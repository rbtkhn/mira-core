from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping
from zoneinfo import ZoneInfo

import mira_continuity


REPO_ROOT = Path(__file__).resolve().parent.parent
INBOX_ENV = "MIRA_CORE_CONTINUITY_INBOX"
SCHEMA_VERSION = 1
LOCAL_TIMEZONE = "America/Denver"
DEBT_CLASSES = {
    "uncommitted-work", "unpublished-commit", "blocked-external-action",
    "unresolved-authority", "open-choice-branch", "unsaved-artifact",
    "unavailable-verification",
}


class RestError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def local_date(timestamp: str) -> str:
    value = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return value.astimezone(ZoneInfo(LOCAL_TIMEZONE)).date().isoformat()


def resolve_inbox(raw: str | Path | None, environment: Mapping[str, str] = os.environ) -> Path:
    value = raw or environment.get(INBOX_ENV)
    if not value:
        raise RestError(f"private Rest inbox is not configured; pass --inbox or set {INBOX_ENV}")
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        raise RestError("private Rest inbox must be an absolute path")
    resolved = candidate.resolve(strict=False)
    repository = REPO_ROOT.resolve()
    if resolved == repository or resolved.is_relative_to(repository):
        raise RestError("private Rest inbox must remain outside Git")
    return resolved


def session_uuid(environment: Mapping[str, str] = os.environ) -> str:
    value = environment.get("CODEX_THREAD_ID") or environment.get("CODEX_SESSION_ID") or ""
    normalized = value.strip().casefold()
    if not mira_continuity.SESSION_ID_RE.fullmatch(f"MS-{normalized}"):
        raise RestError("current Codex session ID is unavailable or malformed")
    return normalized


def user_records(source: mira_continuity.SessionSource) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    with source.path.open("r", encoding="utf-8-sig") as stream:
        for line in stream:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = row.get("payload")
            if row.get("type") != "response_item" or not isinstance(payload, dict):
                continue
            if payload.get("type") != "message" or payload.get("role") != "user":
                continue
            text = "".join(
                str(item.get("text", "")) for item in payload.get("content", [])
                if isinstance(item, dict) and item.get("type") == "input_text"
            )
            records.append({
                "timestamp": mira_continuity.normalize_timestamp(row.get("timestamp")),
                "text": text,
                "sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
            })
    return records


def exact_rest(text: str) -> bool:
    return text.strip().casefold() == "rest"


def workspace_id(repo_root: Path = REPO_ROOT) -> str:
    return "mira-core-" + hashlib.sha256(str(repo_root.resolve()).casefold().encode()).hexdigest()[:12]


def session_dir(inbox: Path, session: str, repo_root: Path = REPO_ROOT) -> Path:
    return inbox / workspace_id(repo_root) / session


def load_events(inbox: Path, session: str, repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    directory = session_dir(inbox, session, repo_root)
    if not directory.is_dir():
        return []
    events: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RestError("Rest receipt is unreadable") from error
        claimed = value.get("event_sha256")
        body = {key: item for key, item in value.items() if key != "event_sha256"}
        if claimed != digest(body):
            raise RestError("Rest receipt digest mismatch")
        events.append(value)
    events.sort(key=lambda row: (int(row.get("sequence", 0)), row.get("event_id", "")))
    for index, event in enumerate(events, start=1):
        if event.get("sequence") != index:
            raise RestError("Rest receipt sequence is not contiguous")
        previous = events[index - 2]["event_sha256"] if index > 1 else None
        if event.get("previous_event_sha256") != previous:
            raise RestError("Rest receipt event chain mismatch")
    return events


def git_state(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    def run(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=repo_root, check=True, capture_output=True, text=True).stdout.strip()
    try:
        head = run("rev-parse", "--short=12", "HEAD")
        branch = run("branch", "--show-current") or "detached"
        fields = run("status", "--porcelain=v1", "--untracked-files=normal").splitlines()
        staged = sum(bool(row) and row[0] not in {" ", "?"} for row in fields)
        tracked = sum(not row.startswith("??") for row in fields)
        untracked = sum(row.startswith("??") for row in fields)
        try:
            behind, ahead = map(int, run("rev-list", "--left-right", "--count", "@{u}...HEAD").split())
        except (subprocess.CalledProcessError, ValueError):
            behind = ahead = None
        return {"status": "available", "head": head, "branch": branch, "dirty_count": len(fields),
                "tracked_count": tracked, "untracked_count": untracked, "staged_count": staged,
                "ahead": ahead, "behind": behind}
    except subprocess.CalledProcessError:
        return {"status": "unavailable"}


def inferred_debt(state: dict[str, Any], extra: list[str] | None = None) -> list[str]:
    values = set(extra or [])
    unknown = values - DEBT_CLASSES
    if unknown:
        raise RestError("unsupported closure debt: " + ", ".join(sorted(unknown)))
    if state.get("dirty_count", 0):
        values.add("uncommitted-work")
    if isinstance(state.get("ahead"), int) and state["ahead"] > 0:
        values.add("unpublished-commit")
    if state.get("status") == "unavailable":
        values.add("unavailable-verification")
    return sorted(values)


def event_body(*, session: str, sequence: int, event_type: str, record: dict[str, str],
               previous: str | None, debt: list[str], state: dict[str, Any]) -> dict[str, Any]:
    body = {
        "schema_version": SCHEMA_VERSION,
        "event_id": "",
        "workspace_id": workspace_id(),
        "session_id": f"MS-{session}",
        "sequence": sequence,
        "event_type": event_type,
        "occurred_at": record["timestamp"],
        "local_date": local_date(record["timestamp"]),
        "timezone": LOCAL_TIMEZONE,
        "authority_record_sha256": record["sha256"],
        "previous_event_sha256": previous,
        "reentry_expected": event_type == "resumed",
        "closure_debt": debt if event_type == "rested" else [],
        "repository_state": state if event_type == "rested" else None,
        "requested_reviews": (
            [
                {"owner": "mira-journal", "state": "pending-consideration"},
                {"owner": "recursive-learn", "state": "pending-screening"},
            ] if event_type == "rested" else []
        ),
    }
    seed = dict(body)
    seed.pop("event_id")
    body["event_id"] = "RSTE-" + digest(seed)[:24]
    return body


def planned_events(source: mira_continuity.SessionSource, existing: list[dict[str, Any]],
                   debt: list[str] | None = None) -> list[dict[str, Any]]:
    records = user_records(source)
    if not records or not exact_rest(records[-1]["text"]):
        raise RestError("the latest user instruction must be exactly `rest`")
    latest = existing[-1] if existing else None
    after = [row for row in records if not latest or row["timestamp"] > latest["occurred_at"]]
    additions: list[dict[str, Any]] = []
    previous = latest["event_sha256"] if latest else None
    sequence = len(existing) + 1
    state = git_state()
    if latest and latest["event_type"] == "rested":
        resumed = next((row for row in after if not exact_rest(row["text"])), None)
        if resumed:
            body = event_body(session=source.session_uuid, sequence=sequence, event_type="resumed",
                              record=resumed, previous=previous, debt=[], state={})
            body["event_sha256"] = digest(body)
            additions.append(body)
            previous, sequence = body["event_sha256"], sequence + 1
        else:
            return []
    body = event_body(session=source.session_uuid, sequence=sequence, event_type="rested",
                      record=records[-1], previous=previous, debt=inferred_debt(state, debt), state=state)
    body["event_sha256"] = digest(body)
    additions.append(body)
    return additions


@contextmanager
def session_lock(directory: Path, timeout: float = 5.0) -> Iterator[None]:
    lock = directory.with_name(directory.name + ".lock")
    started = time.monotonic()
    while True:
        try:
            lock.mkdir(parents=True)
            break
        except FileExistsError:
            if time.monotonic() - started >= timeout:
                raise RestError("timed out waiting for Rest receipt lock")
            time.sleep(0.05)
    try:
        yield
    finally:
        try:
            lock.rmdir()
        except OSError:
            pass


def write_events(inbox: Path, session: str, additions: list[dict[str, Any]]) -> None:
    directory = session_dir(inbox, session)
    directory.mkdir(parents=True, exist_ok=True)
    for event in additions:
        target = directory / f"{event['sequence']:06d}-{event['event_id']}.json"
        temporary = target.with_suffix(".json.tmp")
        data = json.dumps(event, ensure_ascii=False, indent=2) + "\n"
        temporary.write_text(data, encoding="utf-8")
        os.replace(temporary, target)


def projection(inbox: Path, session: str, source: mira_continuity.SessionSource | None = None) -> dict[str, Any]:
    events = load_events(inbox, session)
    recorded = events[-1]["event_type"] if events else "active"
    current = recorded
    derived_resume = False
    if source and recorded == "rested":
        records = user_records(source)
        derived_resume = any(
            row["timestamp"] > events[-1]["occurred_at"] and not exact_rest(row["text"])
            for row in records
        )
        if derived_resume:
            current = "resumed"
    latest = events[-1] if events else None
    return {
        "availability": "available", "recorded_state": recorded,
        "current_state": current, "derived_resume": derived_resume,
        "event_count": len(events), "latest_event_id": latest.get("event_id") if latest else None,
        "closure_debt": latest.get("closure_debt", []) if latest else [],
        "requested_reviews": review_queue(events),
        "mutation_performed": False,
    }


def review_queue(events: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Coalesce provisional review requests by session-local date and owner."""
    rested = [event for event in events if event.get("event_type") == "rested"]
    if not rested:
        return []
    current_date = rested[-1].get("local_date")
    owners: dict[str, dict[str, str]] = {}
    for event in rested:
        if event.get("local_date") != current_date:
            continue
        for request in event.get("requested_reviews", []):
            owner = request.get("owner")
            if owner:
                owners[owner] = {"owner": owner, "state": request.get("state", "pending")}
    return [owners[owner] for owner in sorted(owners)]


def workspace_events(inbox: Path, *, limit: int = 200) -> list[dict[str, Any]]:
    root = inbox / workspace_id()
    if not root.is_dir():
        return []
    paths = sorted(root.glob("*/*.json"), key=lambda path: path.stat().st_mtime, reverse=True)[:limit]
    events: list[dict[str, Any]] = []
    sessions = sorted({path.parent.name for path in paths})
    for session in sessions:
        events.extend(load_events(inbox, session))
    return sorted(events, key=lambda row: (row["occurred_at"], row["event_id"]))


def coffee_coverage(inbox: Path, episode: dict[str, Any] | None) -> str:
    events = workspace_events(inbox)
    rests = [event for event in events if event["event_type"] == "rested"]
    if not rests:
        return "unavailable"
    if episode is None:
        return "missing-dream"
    covered = {row.get("session_id") for row in episode.get("session_coverage", [])}
    created_at = str(episode.get("created_at", ""))
    late = [event for event in rests if event["occurred_at"] > created_at]
    if not late and all(event["session_id"] in covered for event in rests):
        return "covered-current"
    for event in late:
        session = str(event["session_id"])[3:]
        source = mira_continuity.find_session_source(session)
        if source is None:
            return "late-substantive"
        if any(
            row["timestamp"] > created_at and not exact_rest(row["text"])
            for row in user_records(source)
        ):
            return "late-substantive"
    return "late-terminal-only"

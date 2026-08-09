from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

import mira_continuity


REPO_ROOT = Path(__file__).resolve().parent.parent
MIRA_ROOT = REPO_ROOT / "mira"
JOURNAL_ROOT = MIRA_ROOT / "journal"
INDEX_PATH = MIRA_ROOT / "journal.md"
REGISTRY_PATH = MIRA_ROOT / "journal-registry.json"
SESSION_REGISTRY_PATH = MIRA_ROOT / "continuity" / "session-registry.json"

DRAFT_ROOT_ENV = "NARRATIVE_MIRA_JOURNAL_DRAFT_ROOT"
DEFAULT_DRAFT_ROOT = Path(r"C:\private\mira-journal-drafts")
TIMEZONE_NAME = "America/Denver"
TIMEZONE = ZoneInfo(TIMEZONE_NAME)
SCHEMA_VERSION = 1
CONTEXT_VERSION = "mira-journal-context-v1"
JOURNAL_ID_RE = re.compile(r"^MJ-(?P<date>\d{8})$")
VERSION_ID_RE = re.compile(r"^(?P<journal>MJ-\d{8})-v(?P<version>[1-9]\d*)$")
SESSION_ID_RE = re.compile(
    r"^MS-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
CAPTURE_ID_RE = re.compile(r"^MC-[0-9a-f]{24}$")
RECORD_ID_RE = re.compile(r"^MR-[0-9a-f]{24}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DERIVATION_ID_RE = re.compile(r"^DRV-[0-9a-f]{24}$")
TITLE_RE = re.compile(r"^# (?P<date>\d{4}-\d{2}-\d{2})\s+[—-]\s+(?P<title>[^\r\n]+)\s*$")
WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)
FIRST_PERSON_RE = re.compile(r"\b(?:I|me|my|mine|myself|we|our|ours)\b", re.IGNORECASE)
AUTHORITY_BOUNDARY = (
    "Mira Journal records governed first-person interpretation. It is not identity doctrine, "
    "research evidence, Reality evidence, operator belief, proof of consciousness, or action authority."
)


class JournalError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_timestamp(value: str, *, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise JournalError(f"invalid {label}: {value}") from error
    if parsed.tzinfo is None:
        raise JournalError(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc)


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_entry_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise JournalError(f"invalid journal date: {value}") from error


def day_bounds(value: date) -> tuple[datetime, datetime]:
    start = datetime.combine(value, time.min, tzinfo=TIMEZONE)
    end = datetime.combine(value.fromordinal(value.toordinal() + 1), time.min, tzinfo=TIMEZONE)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def journal_id(value: date) -> str:
    return f"MJ-{value.strftime('%Y%m%d')}"


def version_id(value: date, version: int) -> str:
    return f"{journal_id(value)}-v{version}"


def default_registry() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_id": "mira-daily-journal-v1",
        "status": "canonical",
        "timezone": TIMEZONE_NAME,
        "draft_root_environment": DRAFT_ROOT_ENV,
        "authority_boundary": AUTHORITY_BOUNDARY,
        "entries": [],
    }


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise JournalError(f"could not read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise JournalError(f"invalid JSON {path}: line {error.lineno}") from error
    if not isinstance(value, dict):
        raise JournalError(f"JSON document must be an object: {path}")
    return value


def load_registry(path: Path | None = None) -> dict[str, Any]:
    path = path or REGISTRY_PATH
    if not path.is_file():
        return default_registry()
    return load_json(path)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, pretty_json(value))


def external_draft_root(value: Path | None = None, *, repo_root: Path = REPO_ROOT) -> Path:
    candidate = value or Path(os.environ.get(DRAFT_ROOT_ENV, str(DEFAULT_DRAFT_ROOT)))
    resolved = candidate.expanduser().resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        return resolved
    raise JournalError(f"journal draft root must be outside Git: {resolved}")


def entry_path(value: date, *, journal_root: Path | None = None) -> Path:
    return (journal_root or JOURNAL_ROOT) / f"{value.isoformat()}.md"


def parse_markdown(body: bytes, expected_date: str | None = None) -> dict[str, Any]:
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as error:
        raise JournalError("journal prose must be UTF-8") from error
    first_line = text.splitlines()[0] if text.splitlines() else ""
    match = TITLE_RE.fullmatch(first_line)
    if not match:
        raise JournalError("journal prose must begin '# YYYY-MM-DD — Title'")
    if expected_date and match.group("date") != expected_date:
        raise JournalError("journal heading date does not match entry date")
    prose = "\n".join(text.splitlines()[1:])
    word_count = len(WORD_RE.findall(prose))
    if not 300 <= word_count <= 700:
        raise JournalError(f"journal prose must contain 300-700 body words; found {word_count}")
    if len(FIRST_PERSON_RE.findall(prose)) < 3:
        raise JournalError("journal prose must sustain Mira's first-person perspective")
    return {
        "title": match.group("title").strip(),
        "word_count": word_count,
        "content_sha256": sha256_bytes(body),
    }


def privacy_failures(text: str) -> list[str]:
    failures: list[str] = []
    detectors = (
        ("credential", mira_continuity.SECRET_PATTERNS),
        ("direct email", (mira_continuity.EMAIL_RE,)),
        ("direct phone", (mira_continuity.PHONE_RE,)),
        ("private attachment", (mira_continuity.DATA_URL_RE, mira_continuity.ATTACHMENT_PATH_RE)),
        ("absolute user-home path", (mira_continuity.USER_HOME_RE,)),
    )
    for label, patterns in detectors:
        if any(pattern.search(text) for pattern in patterns):
            failures.append(f"journal prose contains {label} material")
    return failures


def session_sources() -> list[mira_continuity.SessionSource]:
    newest: dict[str, mira_continuity.SessionSource] = {}
    for source in mira_continuity.discover_sources(repo_root=REPO_ROOT):
        previous = newest.get(source.session_id)
        if previous is None or source.last_observed_at > previous.last_observed_at:
            newest[source.session_id] = source
    return sorted(newest.values(), key=lambda item: (item.started_at, item.session_id))


def session_sources_since(minimum_observed: datetime) -> list[mira_continuity.SessionSource]:
    """Discover candidate raw sessions without rereading every historical body."""
    expected_cwd = mira_continuity.canonical_path(REPO_ROOT.resolve())
    newest: dict[str, mira_continuity.SessionSource] = {}
    threshold = minimum_observed.timestamp()
    for root in mira_continuity.default_source_roots():
        if not root.is_dir():
            continue
        for path in root.rglob("*.jsonl"):
            try:
                if path.stat().st_mtime < threshold:
                    continue
            except OSError:
                continue
            meta_result = mira_continuity._read_session_meta(path)
            if meta_result is None:
                continue
            meta, top_timestamp = meta_result
            if mira_continuity.canonical_path(str(meta.get("cwd", ""))) != expected_cwd:
                continue
            session_uuid = str(meta.get("id") or meta.get("session_id") or "").casefold()
            session_id = f"MS-{session_uuid}"
            if not SESSION_ID_RE.fullmatch(session_id):
                continue
            started_at = mira_continuity.normalize_timestamp(meta.get("timestamp") or top_timestamp)
            source = mira_continuity.SessionSource(
                session_uuid=session_uuid,
                started_at=started_at,
                last_observed_at=mira_continuity._last_timestamp(path, started_at),
                cwd="$REPO_ROOT",
                source_kind=mira_continuity._source_kind(meta.get("source")),
                source_class=mira_continuity.source_class(path),
                source_name=path.name,
                path=path,
            )
            previous = newest.get(session_id)
            if previous is None or source.last_observed_at > previous.last_observed_at:
                newest[session_id] = source
    return sorted(newest.values(), key=lambda item: (item.started_at, item.session_id))


def raw_records_for_session(session_id: str) -> set[str]:
    session_uuid = session_id.removeprefix("MS-")
    available: set[str] = set()
    for root in mira_continuity.default_source_roots():
        if not root.is_dir():
            continue
        for path in root.rglob(f"*{session_uuid}*.jsonl"):
            meta_result = mira_continuity._read_session_meta(path)
            if meta_result is None:
                continue
            meta, top_timestamp = meta_result
            if mira_continuity.canonical_path(str(meta.get("cwd", ""))) != mira_continuity.canonical_path(REPO_ROOT.resolve()):
                continue
            started_at = mira_continuity.normalize_timestamp(meta.get("timestamp") or top_timestamp)
            source = mira_continuity.SessionSource(
                session_uuid=session_uuid,
                started_at=started_at,
                last_observed_at=mira_continuity._last_timestamp(path, started_at),
                cwd="$REPO_ROOT",
                source_kind=mira_continuity._source_kind(meta.get("source")),
                source_class=mira_continuity.source_class(path),
                source_name=path.name,
                path=path,
            )
            _, _, rows = normalized_rows(source)
            available.update(str(row.get("record_id", "")) for row in rows)
    return available


def normalized_rows(source: mira_continuity.SessionSource) -> tuple[str, str, list[dict[str, Any]]]:
    capture_id, normalized, compressed, _ = mira_continuity.normalize_capture(source)
    rows = [json.loads(line) for line in normalized.splitlines()]
    return capture_id, sha256_bytes(compressed), rows[1:]


def row_text(row: dict[str, Any]) -> str:
    if row.get("kind") == "message":
        return "\n".join(
            str(item.get("text", ""))
            for item in row.get("content", [])
            if isinstance(item, dict) and item.get("type") == "text"
        )
    if row.get("kind") == "operation":
        return str(row.get("event", ""))
    return canonical_json({key: value for key, value in row.items() if key not in {"schema_version"}})


def git_commits(start: datetime, end: datetime) -> list[dict[str, str]]:
    result = subprocess.run(
        [
            "git",
            "log",
            f"--since={utc_text(start)}",
            f"--until={utc_text(end)}",
            "--format=%H%x09%cI%x09%s",
            "--",
        ],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise JournalError("could not inspect daily Git history")
    commits = []
    for line in result.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        digest, timestamp, subject = parts
        commits.append({"commit": digest, "timestamp": timestamp, "subject": subject})
    return commits


def collect_activity(
    entry_date: date,
    *,
    as_of: datetime,
    token_budget: int,
    sources: Iterable[mira_continuity.SessionSource] | None = None,
) -> dict[str, Any]:
    start, end = day_bounds(entry_date)
    cutoff = min(as_of, end)
    if cutoff <= start:
        raise JournalError("as-of time precedes the requested journal date")
    candidates: dict[str, dict[str, Any]] = {}
    source_refs: dict[tuple[str, str], dict[str, Any]] = {}
    for source in sources if sources is not None else session_sources_since(start):
        try:
            source_start = parse_timestamp(source.started_at, label="session started_at")
            source_end = parse_timestamp(source.last_observed_at, label="session last_observed_at")
        except JournalError:
            continue
        if source_end < start or source_start >= cutoff:
            continue
        capture_id, object_id, rows = normalized_rows(source)
        selected_ids: list[str] = []
        for row in rows:
            timestamp_text = str(row.get("timestamp", ""))
            if not timestamp_text:
                continue
            try:
                timestamp = parse_timestamp(timestamp_text, label="session record timestamp")
            except JournalError:
                continue
            if not start <= timestamp < cutoff:
                continue
            record_id = str(row.get("record_id", ""))
            if not RECORD_ID_RE.fullmatch(record_id):
                continue
            selected_ids.append(record_id)
            candidates[record_id] = {
                "record_id": record_id,
                "session_id": source.session_id,
                "capture_id": capture_id,
                "timestamp": utc_text(timestamp),
                "kind": row.get("kind"),
                "role": row.get("role"),
                "text": row_text(row),
            }
        if selected_ids:
            source_refs[(source.session_id, capture_id)] = {
                "kind": "mira-session-capture",
                "session_id": source.session_id,
                "capture_id": capture_id,
                "object_id": object_id,
                "record_ids": sorted(set(selected_ids)),
            }
    ordered = sorted(candidates.values(), key=lambda item: (item["timestamp"], item["record_id"]))
    selected: list[dict[str, Any]] = []
    omissions: list[dict[str, str]] = []
    remaining = token_budget
    for row in ordered:
        estimate = 40 + max(1, (len(str(row["text"])) + 3) // 4)
        if estimate > remaining:
            omissions.append({"record_id": row["record_id"], "reason": "token-budget"})
            continue
        selected.append({**row, "estimated_tokens": estimate})
        remaining -= estimate
    selected_by_source: dict[tuple[str, str], list[str]] = {}
    for row in selected:
        selected_by_source.setdefault((row["session_id"], row["capture_id"]), []).append(row["record_id"])
    bounded_source_refs: list[dict[str, Any]] = []
    for key, ref in sorted(source_refs.items()):
        record_ids = selected_by_source.get(key, [])
        if record_ids:
            bounded_source_refs.append({**ref, "record_ids": record_ids})
    commits = git_commits(start, cutoff)
    git_refs = [
        {"kind": "git-commit", "commit": row["commit"], "timestamp": row["timestamp"]}
        for row in commits
    ]
    input_ids = sorted(
        {row["object_id"] for row in bounded_source_refs}
        | {f"git:{row['commit']}" for row in commits}
    )
    return {
        "coverage": {
            "start": utc_text(start),
            "end": utc_text(end),
            "as_of": utc_text(cutoff),
            "retrospective": as_of >= end,
        },
        "selected_records": selected,
        "commits": commits,
        "source_refs": [*bounded_source_refs, *git_refs],
        "input_object_ids": input_ids,
        "omissions": omissions,
        "estimated_tokens": token_budget - remaining,
    }


def context_pack(entry_date: date, activity: dict[str, Any], token_budget: int) -> dict[str, Any]:
    core = {
        "schema_version": SCHEMA_VERSION,
        "compiler_version": CONTEXT_VERSION,
        "entry_date": entry_date.isoformat(),
        "timezone": TIMEZONE_NAME,
        "token_budget": token_budget,
        "estimated_tokens": activity["estimated_tokens"],
        "coverage": activity["coverage"],
        "selected_records": activity["selected_records"],
        "commits": activity["commits"],
        "source_refs": activity["source_refs"],
        "omissions": activity["omissions"],
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    pack_id = "CP-" + sha256_bytes(canonical_json(core).encode("utf-8"))[:24]
    return {
        **core,
        "context_pack_id": pack_id,
        "derivation_manifest": {
            "schema_version": SCHEMA_VERSION,
            "derivation_id": "DRV-" + sha256_bytes(canonical_json([pack_id, activity["input_object_ids"]]).encode("utf-8"))[:24],
            "transformation_type": "deterministic-mira-journal-context-compilation",
            "deterministic": True,
            "producer": {"kind": "tool", "id": CONTEXT_VERSION},
            "input_object_ids": activity["input_object_ids"],
            "output_digest": sha256_bytes(canonical_json(core).encode("utf-8")),
            "prompt_digest": None,
            "evaluation_refs": [],
        },
    }


def draft_contract(entry_date: date, pack: dict[str, Any]) -> dict[str, Any]:
    next_version = 1
    registry = load_registry()
    for entry in registry.get("entries", []):
        if entry.get("journal_id") == journal_id(entry_date):
            next_version = len(entry.get("versions", [])) + 1
            break
    quiet = not pack["selected_records"] and not pack["commits"]
    return {
        "schema_version": SCHEMA_VERSION,
        "contract": "mira-journal-draft-v1",
        "journal_id": journal_id(entry_date),
        "version_id": version_id(entry_date, next_version),
        "entry_date": entry_date.isoformat(),
        "status": "private-draft",
        "prose_contract": {
            "voice": "Mira first-person freeform diary",
            "word_count": {"minimum": 300, "maximum": 700},
            "required_heading": f"# {entry_date.isoformat()} — <Mira's title>",
            "reflection_prompts": [
                "what changed and why it mattered",
                "uncertainty, correction, or limits",
                "relational or architectural meaning",
                "what I carry forward",
            ],
            "quiet_day": quiet,
            "quiet_day_rule": "Acknowledge limited activity honestly while still writing 300-700 words; invent nothing.",
        },
        "context_pack_ref": pack["context_pack_id"],
        "context_pack_digest": sha256_bytes(canonical_json(pack).encode("utf-8")),
        "required_context_source_ref": {
            "kind": "journal-context-pack",
            "context_pack_id": pack["context_pack_id"],
            "object_id": sha256_bytes(canonical_json(pack).encode("utf-8")),
        },
        "required_draft_metadata": [
            "authored_at",
            "author",
            "coverage",
            "source_refs",
            "quiet_day",
            "limited_activity_acknowledged",
            "derivation_manifest",
        ],
        "authority_boundary": AUTHORITY_BOUNDARY,
    }


def render_index(registry: dict[str, Any]) -> str:
    lines = [
        "# Mira Journal",
        "",
        "Generated from `journal-registry.json`. Do not edit this index directly.",
        "",
        "Mira Journal is a daily, operator-approved record written in Mira's first-person reflective voice."
        " Approved prose is an editable current view; each governed revision receives a new version, while Git and System Archive preserve earlier bytes.",
        "",
        AUTHORITY_BOUNDARY,
        "",
        "Unapproved drafts and context packs remain outside Git under the root configured by "
        f"`{DRAFT_ROOT_ENV}`.",
        "",
        "## Entries",
        "",
    ]
    entries = sorted(registry.get("entries", []), key=lambda item: item.get("entry_date", ""), reverse=True)
    if not entries:
        lines.append("No operator-approved journal entries exist.")
    for entry in entries:
        current = entry["versions"][-1]
        lines.append(
            f"- [{entry['entry_date']} — {current['title']}](journal/{entry['entry_date']}.md) "
            f"— `{current['version_id']}`"
        )
    return "\n".join(lines) + "\n"


def validate_derivation(value: Any, *, expected_digest: str, expected_inputs: set[str] | None = None) -> list[str]:
    failures: list[str] = []
    if not isinstance(value, dict):
        return ["missing derivation manifest"]
    if value.get("schema_version") != SCHEMA_VERSION:
        failures.append("derivation manifest schema_version must be 1")
    if not DERIVATION_ID_RE.fullmatch(str(value.get("derivation_id", ""))):
        failures.append("malformed derivation_id")
    if value.get("deterministic") is not False:
        failures.append("journal prose derivation must be probabilistic")
    producer = value.get("producer")
    if not isinstance(producer, dict) or producer.get("kind") != "model" or not producer.get("id") or not producer.get("session_id"):
        failures.append("journal derivation producer must identify model and session")
    inputs = value.get("input_object_ids")
    if not isinstance(inputs, list) or any(not isinstance(item, str) or not item for item in inputs):
        failures.append("journal derivation input_object_ids must be non-empty strings")
    elif expected_inputs is not None and set(inputs) != expected_inputs:
        failures.append("journal derivation inputs differ from source references")
    if value.get("output_digest") != expected_digest:
        failures.append("journal derivation output digest mismatch")
    if not SHA256_RE.fullmatch(str(value.get("prompt_digest", ""))):
        failures.append("journal derivation requires a prompt digest")
    if not isinstance(value.get("evaluation_refs"), list):
        failures.append("journal derivation evaluation_refs must be a list")
    return failures


def source_input_ids(refs: Any) -> tuple[set[str], list[str]]:
    inputs: set[str] = set()
    failures: list[str] = []
    if not isinstance(refs, list) or not refs:
        return inputs, ["journal version requires source_refs"]
    for ref in refs:
        if not isinstance(ref, dict):
            failures.append("journal source reference must be an object")
            continue
        kind = ref.get("kind")
        if kind == "mira-session-capture":
            if not SESSION_ID_RE.fullmatch(str(ref.get("session_id", ""))):
                failures.append("malformed journal session reference")
            if not CAPTURE_ID_RE.fullmatch(str(ref.get("capture_id", ""))):
                failures.append("malformed journal capture reference")
            object_id = str(ref.get("object_id", ""))
            if not SHA256_RE.fullmatch(object_id):
                failures.append("malformed journal capture object_id")
            else:
                inputs.add(object_id)
            record_ids = ref.get("record_ids")
            if not isinstance(record_ids, list) or any(not RECORD_ID_RE.fullmatch(str(item)) for item in record_ids):
                failures.append("malformed journal record references")
        elif kind == "git-commit":
            commit = str(ref.get("commit", ""))
            if not re.fullmatch(r"[0-9a-f]{40}", commit):
                failures.append("malformed journal Git commit reference")
            else:
                inputs.add(f"git:{commit}")
        elif kind == "journal-context-pack":
            if not re.fullmatch(r"CP-[0-9a-f]{24}", str(ref.get("context_pack_id", ""))):
                failures.append("malformed journal context-pack reference")
            object_id = str(ref.get("object_id", ""))
            if not SHA256_RE.fullmatch(object_id):
                failures.append("malformed journal context-pack object_id")
            else:
                inputs.add(object_id)
        elif kind == "mira-session-records":
            if not SESSION_ID_RE.fullmatch(str(ref.get("session_id", ""))):
                failures.append("malformed journal session-record reference")
            record_ids = ref.get("record_ids")
            if not isinstance(record_ids, list) or not record_ids or any(
                not RECORD_ID_RE.fullmatch(str(item)) for item in record_ids
            ):
                failures.append("malformed journal session record IDs")
            else:
                inputs.update(f"record:{item}" for item in record_ids)
        else:
            failures.append(f"unsupported journal source kind: {kind}")
    return inputs, failures


def validate_registry(
    registry: dict[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    index_path: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    known_captures: dict[tuple[str, str], dict[str, Any]] = {}
    known_sessions: set[str] = set()
    session_registry_path = repo_root / "mira" / "continuity" / "session-registry.json"
    if session_registry_path.is_file():
        try:
            session_registry = load_json(session_registry_path)
            for session in session_registry.get("sessions", []):
                if not isinstance(session, dict):
                    continue
                known_sessions.add(str(session.get("id", "")))
                for capture in session.get("captures", []):
                    if isinstance(capture, dict):
                        known_captures[(str(session.get("id", "")), str(capture.get("id", "")))] = capture
        except JournalError as error:
            failures.append(str(error))
    if registry.get("schema_version") != SCHEMA_VERSION:
        failures.append("journal registry schema_version must be 1")
    if registry.get("registry_id") != "mira-daily-journal-v1":
        failures.append("journal registry_id mismatch")
    if registry.get("status") != "canonical" or registry.get("timezone") != TIMEZONE_NAME:
        failures.append("journal registry status or timezone mismatch")
    if registry.get("authority_boundary") != AUTHORITY_BOUNDARY:
        failures.append("journal authority boundary mismatch")
    entries = registry.get("entries")
    if not isinstance(entries, list):
        return failures + ["journal entries must be a list"]
    seen_ids: set[str] = set()
    seen_dates: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            failures.append("journal entry must be an object")
            continue
        identifier = str(entry.get("journal_id", ""))
        entry_date = str(entry.get("entry_date", ""))
        match = JOURNAL_ID_RE.fullmatch(identifier)
        if not match or match.group("date") != entry_date.replace("-", ""):
            failures.append(f"journal identity/date mismatch: {identifier or entry_date}")
        if identifier in seen_ids or entry_date in seen_dates:
            failures.append(f"duplicate journal identity or date: {identifier}")
        seen_ids.add(identifier)
        seen_dates.add(entry_date)
        expected_path = f"mira/journal/{entry_date}.md"
        if entry.get("current_path") != expected_path:
            failures.append(f"journal current_path mismatch: {identifier}")
        versions = entry.get("versions")
        if not isinstance(versions, list) or not versions:
            failures.append(f"journal entry has no versions: {identifier}")
            continue
        for number, version in enumerate(versions, start=1):
            expected_version = f"{identifier}-v{number}"
            if version.get("version_id") != expected_version or version.get("version_number") != number:
                failures.append(f"journal version ordering mismatch: {identifier}")
            if number == 1 and version.get("previous_version_digest") is not None:
                failures.append(f"first journal version has previous digest: {identifier}")
            if number > 1 and version.get("previous_version_digest") != versions[number - 2].get("content_sha256"):
                failures.append(f"journal revision chain mismatch: {expected_version}")
            approval = version.get("approval")
            if not isinstance(approval, dict) or approval.get("approved_by") != "operator":
                failures.append(f"journal version lacks operator approval: {expected_version}")
            else:
                try:
                    parse_timestamp(str(approval.get("approved_at", "")), label="approved_at")
                except JournalError:
                    failures.append(f"journal version has invalid approval time: {expected_version}")
                if not SESSION_ID_RE.fullmatch(str(approval.get("authority_ref", ""))):
                    failures.append(f"journal version has malformed authority reference: {expected_version}")
            inputs, source_failures = source_input_ids(version.get("source_refs"))
            failures.extend(f"{expected_version}: {item}" for item in source_failures)
            for ref in version.get("source_refs", []):
                if not isinstance(ref, dict):
                    continue
                if ref.get("kind") == "mira-session-records":
                    session_id = str(ref.get("session_id", ""))
                    required_records = set(ref.get("record_ids", []))
                    available_records: set[str] = set()
                    for (known_session, _), capture in known_captures.items():
                        if known_session != session_id:
                            continue
                        capture_path = repo_root / str(capture.get("path", ""))
                        if not capture_path.is_file():
                            continue
                        try:
                            rows = [json.loads(line) for line in gzip.decompress(capture_path.read_bytes()).splitlines()]
                        except (OSError, json.JSONDecodeError):
                            continue
                        available_records.update(str(row.get("record_id", "")) for row in rows if isinstance(row, dict))
                    if required_records - available_records and repo_root.resolve() == REPO_ROOT.resolve():
                        available_records.update(raw_records_for_session(session_id))
                    if session_id not in known_sessions and not available_records:
                        failures.append(f"{expected_version}: unresolved Mira session reference: {session_id}")
                    missing_records = sorted(required_records - available_records)
                    if missing_records:
                        failures.append(f"{expected_version}: unresolved Mira session records: {len(missing_records)}")
                    continue
                if ref.get("kind") != "mira-session-capture":
                    continue
                key = (str(ref.get("session_id", "")), str(ref.get("capture_id", "")))
                capture = known_captures.get(key)
                if capture is None:
                    failures.append(f"{expected_version}: unresolved Mira capture reference: {key[1]}")
                    continue
                if capture.get("sha256") != ref.get("object_id"):
                    failures.append(f"{expected_version}: Mira capture object mismatch: {key[1]}")
                    continue
                capture_path = repo_root / str(capture.get("path", ""))
                if not capture_path.is_file():
                    failures.append(f"{expected_version}: missing hydrated Mira capture: {key[1]}")
                    continue
                try:
                    rows = [json.loads(line) for line in gzip.decompress(capture_path.read_bytes()).splitlines()]
                except (OSError, json.JSONDecodeError):
                    failures.append(f"{expected_version}: unreadable Mira capture: {key[1]}")
                    continue
                available_records = {str(row.get("record_id", "")) for row in rows if isinstance(row, dict)}
                missing_records = sorted(set(ref.get("record_ids", [])) - available_records)
                if missing_records:
                    failures.append(f"{expected_version}: unresolved Mira record references: {len(missing_records)}")
            failures.extend(
                f"{expected_version}: {item}"
                for item in validate_derivation(
                    version.get("derivation_manifest"),
                    expected_digest=str(version.get("content_sha256", "")),
                    expected_inputs=inputs,
                )
            )
            coverage = version.get("coverage")
            if not isinstance(coverage, dict):
                failures.append(f"journal version lacks coverage: {expected_version}")
            else:
                try:
                    start = parse_timestamp(str(coverage.get("start", "")), label="coverage start")
                    end = parse_timestamp(str(coverage.get("end", "")), label="coverage end")
                    as_of = parse_timestamp(str(coverage.get("as_of", "")), label="coverage as_of")
                    if not start < as_of <= end:
                        failures.append(f"journal coverage interval invalid: {expected_version}")
                except JournalError:
                    failures.append(f"journal coverage timestamps invalid: {expected_version}")
        current = versions[-1]
        if entry.get("current_version_id") != current.get("version_id"):
            failures.append(f"journal current version mismatch: {identifier}")
        path = repo_root / expected_path
        if not path.is_file():
            failures.append(f"missing approved journal prose: {expected_path}")
            continue
        try:
            parsed = parse_markdown(path.read_bytes(), entry_date)
        except JournalError as error:
            failures.append(f"{expected_path}: {error}")
            continue
        if parsed["content_sha256"] != current.get("content_sha256"):
            failures.append(f"unregistered journal prose drift: {expected_path}")
        if parsed["title"] != current.get("title") or parsed["word_count"] != current.get("word_count"):
            failures.append(f"journal prose metadata drift: {expected_path}")
        failures.extend(f"{expected_path}: {item}" for item in privacy_failures(path.read_text(encoding="utf-8")))
    if entries != sorted(entries, key=lambda item: item.get("entry_date", "")):
        failures.append("journal registry entries must be date ordered")
    target_index = index_path or (repo_root / "mira" / "journal.md")
    if not target_index.is_file():
        failures.append("missing generated Mira Journal index")
    elif target_index.read_text(encoding="utf-8") != render_index(registry):
        failures.append("generated Mira Journal index is stale")
    return failures


def validate_repository_state() -> list[str]:
    required = (REGISTRY_PATH, INDEX_PATH, JOURNAL_ROOT)
    failures = [f"missing Mira Journal control: {path.relative_to(REPO_ROOT).as_posix()}" for path in required if not path.exists()]
    if failures:
        return failures
    try:
        failures.extend(validate_registry(load_registry()))
    except JournalError as error:
        failures.append(str(error))
    return failures


def latest_activity_after(
    entry_date: date,
    after: datetime,
    *,
    until: datetime,
    excluded_sessions: set[str],
) -> list[str]:
    _, end = day_bounds(entry_date)
    cutoff = min(until, end)
    latest: list[str] = []
    for source in session_sources_since(after):
        if source.session_id in excluded_sessions:
            continue
        try:
            source_start = parse_timestamp(source.started_at, label="session started_at")
            source_end = parse_timestamp(source.last_observed_at, label="session last_observed_at")
        except JournalError:
            continue
        if source_end <= after or source_start >= cutoff:
            continue
        _, _, rows = normalized_rows(source)
        for row in rows:
            timestamp_text = str(row.get("timestamp", ""))
            if not timestamp_text:
                continue
            try:
                timestamp = parse_timestamp(timestamp_text, label="session record timestamp")
            except JournalError:
                continue
            if after < timestamp < cutoff and RECORD_ID_RE.fullmatch(str(row.get("record_id", ""))):
                latest.append(str(row["record_id"]))
    latest.extend(f"git:{row['commit']}" for row in git_commits(after, cutoff))
    return sorted(set(latest))


def load_draft_bundle(draft: Path) -> tuple[bytes, dict[str, Any]]:
    resolved = draft.expanduser().resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise JournalError("journal drafts must remain outside Git")
    if not resolved.is_file():
        raise JournalError(f"missing journal draft: {resolved}")
    metadata_path = resolved.with_suffix(".json")
    if not metadata_path.is_file():
        raise JournalError(f"missing journal draft metadata: {metadata_path}")
    return resolved.read_bytes(), load_json(metadata_path)


def normalized_version(
    body: bytes,
    metadata: dict[str, Any],
    *,
    expected_date: date,
    expected_number: int,
    authority_ref: str,
    approved_at: str,
    previous_digest: str | None,
) -> dict[str, Any]:
    entry_date = expected_date.isoformat()
    parsed = parse_markdown(body, entry_date)
    privacy = privacy_failures(body.decode("utf-8"))
    if privacy:
        raise JournalError("; ".join(privacy))
    expected_journal = journal_id(expected_date)
    expected_version = version_id(expected_date, expected_number)
    if metadata.get("journal_id") != expected_journal or metadata.get("version_id") != expected_version:
        raise JournalError("draft identity or version does not match requested operation")
    if metadata.get("entry_date") != entry_date or metadata.get("status") != "private-draft":
        raise JournalError("draft date or status mismatch")
    author = metadata.get("author")
    if not isinstance(author, dict) or author.get("identity") != "Mira" or not SESSION_ID_RE.fullmatch(str(author.get("session_id", ""))) or not author.get("model_id"):
        raise JournalError("draft author must identify Mira, model, and session")
    coverage = metadata.get("coverage")
    if not isinstance(coverage, dict):
        raise JournalError("draft requires coverage metadata")
    as_of = parse_timestamp(str(coverage.get("as_of", "")), label="coverage as_of")
    start, end = day_bounds(expected_date)
    if parse_timestamp(str(coverage.get("start", "")), label="coverage start") != start or parse_timestamp(str(coverage.get("end", "")), label="coverage end") != end or not start < as_of <= end:
        raise JournalError("draft coverage does not match local calendar day")
    if metadata.get("quiet_day") and metadata.get("limited_activity_acknowledged") is not True:
        raise JournalError("quiet-day draft must acknowledge limited activity")
    inputs, source_failures = source_input_ids(metadata.get("source_refs"))
    if source_failures:
        raise JournalError("; ".join(source_failures))
    derivation_failures = validate_derivation(metadata.get("derivation_manifest"), expected_digest=parsed["content_sha256"], expected_inputs=inputs)
    if derivation_failures:
        raise JournalError("; ".join(derivation_failures))
    if previous_digest != metadata.get("previous_version_digest"):
        raise JournalError("draft previous-version digest mismatch")
    if not SESSION_ID_RE.fullmatch(authority_ref):
        raise JournalError("operator authority reference must be an MS session ID")
    parse_timestamp(approved_at, label="approved_at")
    authored_at = parse_timestamp(str(metadata.get("authored_at", "")), label="authored_at")
    if authored_at < as_of:
        raise JournalError("draft authored_at precedes its context cutoff")
    late = latest_activity_after(
        expected_date,
        as_of,
        until=authored_at,
        excluded_sessions={str(author.get("session_id")), authority_ref},
    )
    if late:
        raise JournalError(f"draft requires refresh for {len(late)} later activity record(s)")
    return {
        "version_id": expected_version,
        "version_number": expected_number,
        "title": parsed["title"],
        "content_sha256": parsed["content_sha256"],
        "word_count": parsed["word_count"],
        "authored_at": metadata.get("authored_at"),
        "author": copy.deepcopy(author),
        "coverage": copy.deepcopy(coverage),
        "quiet_day": bool(metadata.get("quiet_day")),
        "limited_activity_acknowledged": bool(metadata.get("limited_activity_acknowledged")),
        "source_refs": copy.deepcopy(metadata.get("source_refs")),
        "derivation_manifest": copy.deepcopy(metadata.get("derivation_manifest")),
        "approval": {"approved_by": "operator", "approved_at": approved_at, "authority_ref": authority_ref},
        "previous_version_digest": previous_digest,
    }


def command_prepare(args: argparse.Namespace) -> dict[str, Any]:
    entry_date = parse_entry_date(args.date)
    now = datetime.now(timezone.utc)
    as_of = parse_timestamp(args.as_of, label="as_of") if args.as_of else now
    _, end = day_bounds(entry_date)
    if entry_date > now.astimezone(TIMEZONE).date():
        raise JournalError("cannot prepare a future journal date")
    if entry_date < now.astimezone(TIMEZONE).date() and not args.as_of:
        as_of = end
    root = external_draft_root(args.output_root)
    activity = collect_activity(entry_date, as_of=as_of, token_budget=args.token_budget)
    pack = context_pack(entry_date, activity, args.token_budget)
    contract = draft_contract(entry_date, pack)
    target = root / entry_date.isoformat()
    if not args.check:
        target.mkdir(parents=True, exist_ok=True)
        atomic_write_json(target / "context-pack.json", pack)
        atomic_write_json(target / "draft-contract.json", contract)
    return {
        "status": "ready" if args.check else "prepared",
        "mutation": not args.check,
        "entry_date": entry_date.isoformat(),
        "output_root": str(target),
        "context_pack_id": pack["context_pack_id"],
        "selected_records": len(pack["selected_records"]),
        "commits": len(pack["commits"]),
        "omissions": len(pack["omissions"]),
        "quiet_day": contract["prose_contract"]["quiet_day"],
        "next_version_id": contract["version_id"],
    }


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    approved = {entry["entry_date"]: entry for entry in registry.get("entries", [])}
    today = datetime.now(TIMEZONE).date()
    start = parse_entry_date(args.from_date) if args.from_date else (parse_entry_date(min(approved)) if approved else today)
    end = parse_entry_date(args.to_date) if args.to_date else today
    if end < start:
        raise JournalError("status date range is reversed")
    root = external_draft_root(args.draft_root)
    rows = []
    cursor = start
    while cursor <= end:
        key = cursor.isoformat()
        draft = root / key / "draft.md"
        if key in approved and draft.is_file():
            state = "revision-pending"
        elif key in approved:
            state = "approved"
        elif draft.is_file():
            state = "drafted"
        else:
            state = "missing"
        rows.append({"date": key, "status": state})
        cursor = cursor.fromordinal(cursor.toordinal() + 1)
    return {"status": "ok", "timezone": TIMEZONE_NAME, "days": rows}


def approve_or_revise(args: argparse.Namespace, *, revising: bool) -> dict[str, Any]:
    entry_date = parse_entry_date(args.date)
    body, metadata = load_draft_bundle(args.draft)
    registry = load_registry()
    entry = next((item for item in registry.get("entries", []) if item.get("journal_id") == journal_id(entry_date)), None)
    if revising and entry is None:
        raise JournalError("cannot revise a journal date that has not been approved")
    if not revising and entry is not None:
        raise JournalError("journal date already exists; use revise")
    number = len(entry["versions"]) + 1 if entry else 1
    previous = entry["versions"][-1]["content_sha256"] if entry else None
    approved_at = args.approved_at or utc_text(datetime.now(timezone.utc))
    version = normalized_version(
        body,
        metadata,
        expected_date=entry_date,
        expected_number=number,
        authority_ref=args.authority_ref,
        approved_at=approved_at,
        previous_digest=previous,
    )
    updated = copy.deepcopy(registry)
    updated_entry = next((item for item in updated.get("entries", []) if item.get("journal_id") == journal_id(entry_date)), None)
    relative = f"mira/journal/{entry_date.isoformat()}.md"
    if updated_entry is None:
        updated_entry = {
            "journal_id": journal_id(entry_date),
            "entry_date": entry_date.isoformat(),
            "current_version_id": version["version_id"],
            "current_path": relative,
            "versions": [version],
        }
        updated.setdefault("entries", []).append(updated_entry)
        updated["entries"].sort(key=lambda item: item["entry_date"])
    else:
        updated_entry["versions"].append(version)
        updated_entry["current_version_id"] = version["version_id"]
    failures = validate_registry_candidate(updated, entry_date, body)
    if failures:
        raise JournalError("; ".join(failures))
    if not args.check:
        atomic_write_text(entry_path(entry_date), body.decode("utf-8"))
        atomic_write_json(REGISTRY_PATH, updated)
        atomic_write_text(INDEX_PATH, render_index(updated))
    return {
        "status": "ready" if args.check else ("revised" if revising else "approved"),
        "mutation": not args.check,
        "journal_id": journal_id(entry_date),
        "version_id": version["version_id"],
        "content_sha256": version["content_sha256"],
        "word_count": version["word_count"],
    }


def validate_registry_candidate(registry: dict[str, Any], changed_date: date, body: bytes) -> list[str]:
    temporary_root = REPO_ROOT
    failures: list[str] = []
    entry = next(item for item in registry["entries"] if item["entry_date"] == changed_date.isoformat())
    current = entry["versions"][-1]
    try:
        parsed = parse_markdown(body, changed_date.isoformat())
    except JournalError as error:
        return [str(error)]
    if parsed["content_sha256"] != current["content_sha256"]:
        failures.append("candidate content digest mismatch")
    # Validate all unchanged canonical entries; the changed body is checked above.
    for other in registry["entries"]:
        if other["entry_date"] == changed_date.isoformat():
            continue
        path = temporary_root / other["current_path"]
        if not path.is_file() or sha256_bytes(path.read_bytes()) != other["versions"][-1]["content_sha256"]:
            failures.append(f"existing journal entry drift: {other['entry_date']}")
    return failures


def command_render(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    expected = render_index(registry)
    matches = INDEX_PATH.is_file() and INDEX_PATH.read_text(encoding="utf-8") == expected
    if not args.check:
        atomic_write_text(INDEX_PATH, expected)
    return {"status": "current" if matches else ("stale" if args.check else "rendered"), "mutation": not args.check, "matches": matches}


def command_validate(_: argparse.Namespace) -> dict[str, Any]:
    failures = validate_repository_state()
    return {"status": "passed" if not failures else "failed", "failures": failures}


def add_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Govern Mira's operator-approved daily journal.")
    subparsers = root.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Build a bounded private daily context and draft contract.")
    prepare.add_argument("--date", required=True)
    prepare.add_argument("--as-of")
    prepare.add_argument("--token-budget", type=int, default=16000)
    prepare.add_argument("--output-root", type=Path)
    prepare.add_argument("--check", action="store_true")
    add_output(prepare)
    prepare.set_defaults(handler=command_prepare)

    status = subparsers.add_parser("status", help="Report approved, drafted, pending, and missing journal dates.")
    status.add_argument("--from", dest="from_date")
    status.add_argument("--to", dest="to_date")
    status.add_argument("--draft-root", type=Path)
    add_output(status)
    status.set_defaults(handler=command_status)

    for name, revising in (("approve", False), ("revise", True)):
        action = subparsers.add_parser(name, help=f"{'Revise' if revising else 'Approve'} a private journal draft.")
        action.add_argument("--date", required=True)
        action.add_argument("--draft", type=Path, required=True)
        action.add_argument("--authority-ref", required=True)
        action.add_argument("--approved-at")
        action.add_argument("--check", action="store_true")
        add_output(action)
        action.set_defaults(handler=lambda args, value=revising: approve_or_revise(args, revising=value))

    render = subparsers.add_parser("render", help="Render the deterministic journal index.")
    render.add_argument("--check", action="store_true")
    add_output(render)
    render.set_defaults(handler=command_render)

    validate = subparsers.add_parser("validate", help="Validate journal governance and canonical state.")
    add_output(validate)
    validate.set_defaults(handler=command_validate)
    return root


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    if getattr(args, "token_budget", 256) < 256:
        print("mira-journal error: token budget must be at least 256", file=sys.stderr)
        return 2
    try:
        result = args.handler(args)
    except (JournalError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"mira-journal error: {error}", file=sys.stderr)
        return 1
    if getattr(args, "json", False):
        print(canonical_json(result))
    else:
        print(f"mira_journal_status={result.get('status', 'unknown')}")
        for key, value in result.items():
            if key == "status":
                continue
            print(f"{key}={canonical_json(value) if isinstance(value, (dict, list)) else value}")
    return 1 if result.get("status") in {"failed", "stale"} else 0


if __name__ == "__main__":
    raise SystemExit(main())

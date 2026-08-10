from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


REFERENCE_ID_RE = re.compile(r"^MJTR-(?P<date>\d{8})-v(?P<version>[1-9]\d*)$")
RSI_ID_RE = re.compile(r"^RSI-\d{8}-\d{2}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SIGNALS = {"none", "observation", "possible-loop"}
CUTOFF_STATUSES = {"observed-by-cutoff", "historical-context", "retrospective-backfill"}
AUTHORITY_BOUNDARY = (
    "Technical references ground journal prose but do not prove learning, validate outcomes, "
    "or provide action authority. Only admitted RSI entries are canonical recursive learning."
)


class ReferenceError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def reference_id(version_id: str) -> str:
    if not re.fullmatch(r"MJ-\d{8}-v[1-9]\d*", version_id):
        raise ReferenceError(f"malformed journal version ID: {version_id}")
    return "MJTR-" + version_id.removeprefix("MJ-")


def load_ledger(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReferenceError(f"could not read recursive learning ledger: {error}") from error
    if not isinstance(value, dict) or not isinstance(value.get("entries"), list):
        raise ReferenceError("recursive learning ledger is malformed")
    return value


def admitted_ids(ledger: dict[str, Any]) -> set[str]:
    return {
        str(row["id"])
        for row in ledger.get("entries", [])
        if isinstance(row, dict) and RSI_ID_RE.fullmatch(str(row.get("id", "")))
    }


def select_admitted_lessons(
    ledger: dict[str, Any], entry_date: date, *, source_path: str, limit: int = 8
) -> dict[str, Any]:
    eligible = [
        row for row in ledger.get("entries", [])
        if isinstance(row, dict) and str(row.get("date", "")) <= entry_date.isoformat()
    ]
    eligible.sort(key=lambda row: (str(row.get("date", "")), str(row.get("id", ""))), reverse=True)
    selected = eligible[:limit]
    rows = []
    for row in selected:
        rows.append({
            "id": row["id"],
            "date": row["date"],
            "title": row["title"],
            "class": row["class"],
            "closure_state": row["closure_state"],
            "lesson": row["intervention"]["summary"],
            "observed_outcome": row["outcome"]["summary"],
            "next_measure": row["next_measure"],
            "epistemic_class": "admitted-recursive-learning",
            "authority_owner": "recursive-learning-ledger",
            "may_support_reflection": True,
            "may_promote": False,
        })
    omitted = [str(row["id"]) for row in eligible[limit:]]
    return {
        "source_path": source_path,
        "source_sha256": sha256_bytes(canonical_json(ledger).encode("utf-8")),
        "selection_rule": f"latest-{limit}-admitted-at-or-before-entry-date",
        "selected_entries": rows,
        "omitted_entry_ids": omitted,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }


def validate_learning_context(value: Any, *, ledger: dict[str, Any], entry_date: date) -> list[str]:
    if not isinstance(value, dict):
        return ["journal context lacks recursive learning context"]
    failures: list[str] = []
    if value.get("authority_boundary") != AUTHORITY_BOUNDARY:
        failures.append("recursive learning context authority boundary mismatch")
    if value.get("source_sha256") != sha256_bytes(canonical_json(ledger).encode("utf-8")):
        failures.append("recursive learning context ledger digest mismatch")
    known = {str(row.get("id")): row for row in ledger.get("entries", []) if isinstance(row, dict)}
    for row in value.get("selected_entries", []):
        if not isinstance(row, dict) or row.get("id") not in known:
            failures.append("recursive learning context contains an unadmitted entry")
            continue
        if str(known[str(row["id"])].get("date", "")) > entry_date.isoformat():
            failures.append(f"recursive learning context exceeds journal cutoff: {row['id']}")
        if row.get("may_promote") is not False:
            failures.append(f"recursive learning context grants promotion authority: {row['id']}")
    return failures


def reference_digest(reference: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(reference).encode("utf-8"))


def _git_commit_resolves(repo_root: Path, commit: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=repo_root, capture_output=True, check=False,
    )
    return result.returncode == 0


def _git_commit_details(repo_root: Path, commit: str) -> tuple[datetime | None, set[str]]:
    timestamp_result = subprocess.run(
        ["git", "show", "-s", "--format=%cI", commit],
        cwd=repo_root, text=True, encoding="utf-8", errors="replace",
        capture_output=True, check=False,
    )
    paths_result = subprocess.run(
        ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit],
        cwd=repo_root, text=True, encoding="utf-8", errors="replace",
        capture_output=True, check=False,
    )
    if timestamp_result.returncode or paths_result.returncode:
        return None, set()
    try:
        timestamp = datetime.fromisoformat(timestamp_result.stdout.strip().replace("Z", "+00:00"))
    except ValueError:
        timestamp = None
    return timestamp.astimezone(timezone.utc) if timestamp else None, {
        line.strip().replace("\\", "/") for line in paths_result.stdout.splitlines() if line.strip()
    }


def validate_reference(
    value: Any,
    *,
    prose: str,
    prose_sha256: str,
    version_id: str,
    ledger: dict[str, Any],
    repo_root: Path,
    expected_cutoff_at: str | None = None,
) -> list[str]:
    if not isinstance(value, dict):
        return ["technical reference must be an object"]
    failures: list[str] = []
    expected_id = reference_id(version_id)
    if value.get("schema_version") != 1 or value.get("reference_id") != expected_id:
        failures.append("technical reference identity mismatch")
    if value.get("journal_version_id") != version_id or value.get("journal_content_sha256") != prose_sha256:
        failures.append("technical reference is not bound to the journal prose")
    match = REFERENCE_ID_RE.fullmatch(expected_id)
    expected_date = f"{match.group('date')[:4]}-{match.group('date')[4:6]}-{match.group('date')[6:]}" if match else ""
    if value.get("entry_date") != expected_date:
        failures.append("technical reference entry date mismatch")
    if value.get("mapping_mode") not in {"contemporaneous", "retrospective-backfill"}:
        failures.append("technical reference mapping mode is invalid")
    try:
        cutoff = datetime.fromisoformat(str(value.get("cutoff_at", "")).replace("Z", "+00:00"))
        if cutoff.tzinfo is None:
            raise ValueError
        cutoff = cutoff.astimezone(timezone.utc)
    except ValueError:
        cutoff = None
        failures.append("technical reference cutoff_at is invalid")
    if expected_cutoff_at is not None and value.get("cutoff_at") != expected_cutoff_at:
        failures.append("technical reference cutoff does not match journal coverage")
    if value.get("authority_boundary") != AUTHORITY_BOUNDARY:
        failures.append("technical reference authority boundary mismatch")
    items = value.get("items")
    if not isinstance(items, list) or not 3 <= len(items) <= 7:
        failures.append("technical reference requires 3-7 grounding items")
        items = []
    anchors: set[str] = set()
    for number, item in enumerate(items, 1):
        label = f"technical reference item {number}"
        if not isinstance(item, dict):
            failures.append(f"{label} must be an object")
            continue
        anchor = str(item.get("prose_anchor", ""))
        if not anchor or prose.count(anchor) != 1 or anchor in anchors:
            failures.append(f"{label} prose anchor must occur exactly once")
        anchors.add(anchor)
        for field in ("narrative_function", "technical_development"):
            if not str(item.get(field, "")).strip():
                failures.append(f"{label} lacks {field}")
        if item.get("cutoff_status") not in CUTOFF_STATUSES:
            failures.append(f"{label} has invalid cutoff status")
        if item.get("may_promote") is not False:
            failures.append(f"{label} may not grant promotion authority")
        evidence = item.get("evidence_refs")
        if not isinstance(evidence, list) or not evidence:
            failures.append(f"{label} lacks evidence references")
            continue
        for ref in evidence:
            if not isinstance(ref, dict):
                failures.append(f"{label} evidence reference must be an object")
                continue
            kind = ref.get("kind")
            if kind == "repo-path":
                raw = str(ref.get("path", ""))
                if raw.replace("\\", "/").startswith("mira/journal/") or not (repo_root / raw).exists():
                    failures.append(f"{label} repo evidence does not resolve: {raw}")
                if item.get("cutoff_status") == "observed-by-cutoff":
                    failures.append(f"{label} observed evidence must be version-bound, not a mutable repo path: {raw}")
            elif kind == "git-commit":
                commit = str(ref.get("commit", ""))
                paths = ref.get("paths")
                if not re.fullmatch(r"[0-9a-f]{40}", commit) or not _git_commit_resolves(repo_root, commit):
                    failures.append(f"{label} Git evidence does not resolve: {commit}")
                    continue
                if not isinstance(paths, list) or not paths or any(not isinstance(path, str) or not path for path in paths):
                    failures.append(f"{label} Git evidence requires touched paths: {commit}")
                    continue
                commit_time, touched_paths = _git_commit_details(repo_root, commit)
                for raw in paths:
                    normalized = raw.replace("\\", "/")
                    if normalized not in touched_paths:
                        failures.append(f"{label} Git evidence path was not touched by {commit}: {raw}")
                if item.get("cutoff_status") == "observed-by-cutoff" and (
                    cutoff is None or commit_time is None or commit_time > cutoff
                ):
                    failures.append(f"{label} Git evidence exceeds the declared cutoff: {commit}")
            elif kind == "recursive-learning-entry":
                rsi_id = str(ref.get("id", ""))
                if rsi_id not in admitted_ids(ledger):
                    failures.append(f"{label} RSI evidence is not admitted")
                else:
                    row = next(row for row in ledger["entries"] if row.get("id") == rsi_id)
                    if item.get("cutoff_status") == "observed-by-cutoff" and str(row.get("date", "")) > expected_date:
                        failures.append(f"{label} RSI evidence exceeds the journal date: {rsi_id}")
            else:
                failures.append(f"{label} has unsupported evidence kind: {kind}")
    learning = value.get("recursive_learning")
    if not isinstance(learning, dict):
        failures.append("technical reference lacks recursive_learning")
    else:
        consumed = learning.get("consumed_rsi_ids")
        if not isinstance(consumed, list) or any(str(item) not in admitted_ids(ledger) for item in consumed):
            failures.append("technical reference consumes an unknown RSI entry")
        if learning.get("candidate_signal") not in SIGNALS:
            failures.append("technical reference has invalid candidate signal")
        if not isinstance(learning.get("candidate_summary"), str) or not isinstance(learning.get("future_test"), str):
            failures.append("technical reference learning reflection is incomplete")
        forbidden = canonical_json(learning).casefold()
        forbidden_keys = {"class", "closure_state", "validated", "measured", "closed_loop"}
        present_keys: set[str] = set()
        stack: list[Any] = [learning]
        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                present_keys.update(str(key).casefold() for key in current)
                stack.extend(current.values())
            elif isinstance(current, list):
                stack.extend(current)
        forbidden_status_language = re.search(r"\b(?:validated|measured|closed[- ]loop)\b", forbidden)
        if present_keys & forbidden_keys or forbidden_status_language:
            failures.append("technical reference may not claim learning-loop closure")
    prose_claim_patterns = (
        r"\b(?:is|was|became|has been)\s+(?:validated|measured)\b",
        r"\b(?:validated|measured)\s+(?:lesson|learning|loop|outcome|improvement)\b",
        r"\bclosed[- ](?:feedback[- ]?)?loop\b",
    )
    if any(re.search(pattern, prose, re.IGNORECASE) for pattern in prose_claim_patterns):
        failures.append("journal prose may not claim learning-loop closure")
    return failures


def render_reference(value: dict[str, Any]) -> str:
    lines = [
        f"# Technical Reference — `{value['reference_id']}`",
        "",
        f"Journal version: `{value['journal_version_id']}`  ",
        f"Journal digest: `{value['journal_content_sha256']}`",
        "",
        AUTHORITY_BOUNDARY,
        "",
        "## Prose grounding",
        "",
    ]
    for item in value.get("items", []):
        lines.extend([
            f"### {item.get('item_id', 'Grounding item')}", "",
            f"> {item['prose_anchor']}", "",
            f"- Narrative function: {item['narrative_function']}",
            f"- Technical development: {item['technical_development']}",
            f"- Cutoff status: `{item['cutoff_status']}`", "",
            "Evidence:", "",
        ])
        for ref in item["evidence_refs"]:
            target = ref.get("path") or ref.get("commit") or ref.get("id")
            suffix = ""
            if ref.get("kind") == "git-commit" and ref.get("paths"):
                suffix = " — " + ", ".join(f"`{path}`" for path in ref["paths"])
            lines.append(f"- `{ref['kind']}: {target}`{suffix}")
        lines.append("")
    learning = value["recursive_learning"]
    lines.extend([
        "## Recursive learning", "",
        "Consumed admitted lessons: " + (", ".join(f"`{item}`" for item in learning["consumed_rsi_ids"]) or "none"),
        "", f"Candidate signal: `{learning['candidate_signal']}`", "",
        learning["candidate_summary"] or "No candidate summary.", "",
        "Future test: " + (learning["future_test"] or "None specified."), "",
    ])
    return "\n".join(lines).rstrip() + "\n"

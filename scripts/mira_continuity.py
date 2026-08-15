from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
MIRA_ROOT = REPO_ROOT / "mira"
CONTINUITY_ROOT = MIRA_ROOT / "continuity"
CAPTURES_ROOT = CONTINUITY_ROOT / "captures"
HARVESTS_ROOT = CONTINUITY_ROOT / "harvests"
REGISTRY_PATH = CONTINUITY_ROOT / "session-registry.json"
IDENTITY_LEDGER_PATH = CONTINUITY_ROOT / "identity-ledger.json"
IDENTITY_VIEW_PATH = MIRA_ROOT / "identity.md"
TRAJECTORY_PATH = CONTINUITY_ROOT / "trajectory.md"
ACTIVATION_PATH = CONTINUITY_ROOT / "activation.md"

STAGE1_RECOVERY_CONTRACT = {
    "staged_path_count": 133,
    "staged_path_sha256": "08f73d24019bb05d7cb1e34a0dcb1716e6910d59043c728971d4cfc0b64bd63a",
    "capture_count": 120,
    "capture_path_sha256": "06e51cbaaa00f6c713d4e84a30ed83780f4d7d95ea1a03cc0cabfd42bd7b24c0",
    "capture_inventory_sha256": "2cc8fb608069843ab508dc4d0bf2eea144cc19b03b537b5272796e4911b9ad45",
}
RECOVERY_CONTRACTS = {"stage1-v1": STAGE1_RECOVERY_CONTRACT}
MIXED_INTEGRATION_ADDITIONS = {
    "AGENTS.md": {
        "At the start of each workspace session, after loading all controlling repository",
        "instructions, read `mira/continuity/activation.md` when it exists. Treat it as",
        "bounded advisory continuity only: it is not research evidence, operator belief,",
        "or action authority, and explicit current operator direction always controls.",
    },
    "scripts/validate_repository.py": {
        "import mira_continuity",
        '("mira_continuity.validate_repository_state", mira_continuity.validate_repository_state),',
    },
    "tests/test_runtime_tooling.py": {'"mira-continuity": "mira_continuity.py",'},
    "tools/run_repo.py": {'"mira-continuity": REPO_ROOT / "scripts" / "mira_continuity.py",'},
}

PRIVACY_DISPOSITIONS = {
    "redact_and_recapture",
    "exclude_capture",
    "accept_local_private_git",
    "approve_private_remote",
    "approve_publication",
    "false_positive",
    "unresolved",
}

SCHEMA_VERSION = "1.0"
SESSION_ID_RE = re.compile(
    r"^MS-(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$"
)
CAPTURE_ID_RE = re.compile(r"^MC-[0-9a-f]{24}$")
RECORD_ID_RE = re.compile(r"^MR-[0-9a-f]{24}$")
HARVEST_ID_RE = re.compile(
    r"^MH-(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})-v(?P<version>[1-9]\d*)$"
)
IDENTITY_ID_RE = re.compile(r"^(?P<base>MI-\d{4})-v(?P<version>[1-9]\d*)$")

ALLOWED_IDENTITY_TYPES = {"name", "principle", "capability", "boundary", "uncertainty"}
ALLOWED_IDENTITY_LIFECYCLES = {"current", "superseded", "retired"}
ALLOWED_NAME_STATUSES = {"provisional", "canonical", "not-applicable"}
OPERATION_EVENT_TYPES = {
    "task_started",
    "task_complete",
    "turn_aborted",
    "context_compacted",
}
SECRET_KEY_RE = re.compile(
    r"(?:api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|password|passwd|secret|cookie|private[_-]?key)",
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{16,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b", re.IGNORECASE),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.DOTALL),
)
EMAIL_RE = re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\w)(?:\+\d{1,3}[ .()-]*)?(?:\(?\d{3}\)?[ .-]+)\d{3}[ .-]+\d{4}(?!\w)")
PHONE_TAIL_RE = re.compile(r"\d{3}[ .-]+\d{4}")
DATA_URL_RE = re.compile(r"data:[^\s\"']+", re.IGNORECASE)
ATTACHMENT_PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/][^\s\"']*?[\\/]\.codex[\\/]attachments[\\/][^\s\"']+|/(?:Users|home)/[^/\s]+/\.codex/attachments/[^\s\"']+)",
    re.IGNORECASE,
)
USER_HOME_RE = re.compile(r"(?i)(?:[A-Za-z]:[\\/]Users[\\/][^\\/\s\"']+|/(?:Users|home)/[^/\s\"']+)")


class ContinuityError(RuntimeError):
    pass


@dataclass(frozen=True)
class SessionSource:
    session_uuid: str
    started_at: str
    last_observed_at: str
    cwd: str
    source_kind: str
    source_class: str
    source_name: str
    path: Path

    @property
    def session_id(self) -> str:
        return f"MS-{self.session_uuid}"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def content_id(prefix: str, value: bytes) -> str:
    return f"{prefix}-{hashlib.sha256(value).hexdigest()[:24]}"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalize_timestamp(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def valid_timestamp(value: Any) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def canonical_path(value: str | Path) -> str:
    return str(value).replace("\\", "/").rstrip("/").casefold()


def default_source_roots() -> list[Path]:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return [codex_home / "sessions", codex_home / "archived_sessions"]


def source_class(path: Path) -> str:
    return "archived" if "archived_sessions" in {part.casefold() for part in path.parts} else "active"


def _read_session_meta(path: Path) -> tuple[dict[str, Any], str] | None:
    try:
        with path.open("r", encoding="utf-8-sig") as stream:
            first = stream.readline()
        row = json.loads(first)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if row.get("type") != "session_meta" or not isinstance(row.get("payload"), dict):
        return None
    return row["payload"], normalize_timestamp(row.get("timestamp") or row["payload"].get("timestamp"))


def _last_timestamp(path: Path, fallback: str) -> str:
    latest = fallback
    try:
        with path.open("r", encoding="utf-8-sig") as stream:
            for line in stream:
                try:
                    value = normalize_timestamp(json.loads(line).get("timestamp"))
                except json.JSONDecodeError:
                    continue
                if value and (not latest or value > latest):
                    latest = value
    except (OSError, UnicodeDecodeError):
        return fallback
    return latest


def discover_sources(
    source_roots: Iterable[Path] | None = None,
    *,
    repo_root: Path = REPO_ROOT,
) -> list[SessionSource]:
    expected_cwd = canonical_path(repo_root.resolve())
    results: list[SessionSource] = []
    for root in source_roots or default_source_roots():
        root = Path(root)
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.jsonl")):
            meta_result = _read_session_meta(path)
            if meta_result is None:
                continue
            meta, top_timestamp = meta_result
            cwd = str(meta.get("cwd", ""))
            if canonical_path(cwd) != expected_cwd:
                continue
            session_uuid = str(meta.get("id") or meta.get("session_id") or "").casefold()
            if not SESSION_ID_RE.fullmatch(f"MS-{session_uuid}"):
                continue
            started_at = normalize_timestamp(meta.get("timestamp") or top_timestamp)
            results.append(
                SessionSource(
                    session_uuid=session_uuid,
                    started_at=started_at,
                    last_observed_at=_last_timestamp(path, started_at),
                    cwd="$REPO_ROOT",
                    source_kind=_source_kind(meta.get("source")),
                    source_class=source_class(path),
                    source_name=path.name,
                    path=path,
                )
            )
    return sorted(results, key=lambda item: (item.started_at, item.session_uuid, str(item.path)))


def _source_kind(value: Any) -> str:
    if isinstance(value, str):
        return value or "unknown"
    if isinstance(value, dict):
        if "subagent" in value:
            return "subagent"
        return "structured"
    return "unknown"


def sanitize_text(value: str) -> str:
    text = value
    text = DATA_URL_RE.sub("[PRIVATE_ATTACHMENT_OMITTED]", text)
    text = ATTACHMENT_PATH_RE.sub("[PRIVATE_ATTACHMENT_OMITTED]", text)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED_SECRET]", text)
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PHONE_RE.sub("[REDACTED_PHONE]", text)
    text = USER_HOME_RE.sub("$USER_HOME", text)
    text = re.sub(
        r"(?i)[A-Za-z]:[\\/]dev[\\/]narrative-systems(?=$|[\\/\s\"'])",
        "$REPO_ROOT",
        text,
    )
    return text


def sanitize_value(value: Any, *, key: str = "") -> Any:
    if key and SECRET_KEY_RE.search(key):
        return "[REDACTED_SECRET]"
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for raw_key in sorted(value):
            item_key = str(raw_key)
            if item_key in {
                "encrypted_content",
                "internal_chat_message_metadata_passthrough",
                "base_instructions",
                "developer_instructions",
                "system_instructions",
            }:
                continue
            result[item_key] = sanitize_value(value[raw_key], key=item_key)
        return result
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return sanitize_text(str(value))


def _message_content(content: Any) -> list[dict[str, Any]]:
    if not isinstance(content, list):
        return [{"type": "text", "text": sanitize_text(str(content or ""))}]
    result: list[dict[str, Any]] = []
    for item in content:
        if not isinstance(item, dict):
            result.append({"type": "text", "text": sanitize_text(str(item))})
            continue
        content_type = str(item.get("type", "unknown"))
        if content_type in {"input_text", "output_text", "text"}:
            result.append(
                {
                    "type": "text",
                    "text": sanitize_text(str(item.get("text", ""))),
                }
            )
        elif any(token in content_type.casefold() for token in ("image", "audio", "file", "attachment")):
            result.append({"type": "attachment_omitted", "media_type": content_type})
        else:
            cleaned = sanitize_value(item)
            if isinstance(cleaned, dict):
                cleaned.pop("image_url", None)
                cleaned.pop("audio_url", None)
                cleaned.pop("file_data", None)
                cleaned.pop("data", None)
            result.append({"type": content_type, "content": cleaned})
    return result


def _tool_payload(payload: dict[str, Any], field: str) -> Any:
    raw = payload.get(field)
    if not isinstance(raw, str):
        return sanitize_value(raw)
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        return sanitize_text(raw)
    return sanitize_value(decoded)


def _record(row: dict[str, Any], source_sequence: int) -> dict[str, Any] | None:
    row_type = row.get("type")
    payload = row.get("payload")
    if not isinstance(payload, dict):
        return None
    timestamp = normalize_timestamp(row.get("timestamp"))
    base: dict[str, Any]
    if row_type == "response_item" and payload.get("type") == "message":
        role = str(payload.get("role", ""))
        if role not in {"user", "assistant"}:
            return None
        base = {
            "schema_version": SCHEMA_VERSION,
            "source_sequence": source_sequence,
            "timestamp": timestamp,
            "kind": "message",
            "role": role,
            "content": _message_content(payload.get("content")),
        }
    elif row_type == "response_item" and payload.get("type") in {"function_call", "custom_tool_call"}:
        field = "arguments" if payload.get("type") == "function_call" else "input"
        base = {
            "schema_version": SCHEMA_VERSION,
            "source_sequence": source_sequence,
            "timestamp": timestamp,
            "kind": "tool_call",
            "tool_name": sanitize_text(str(payload.get("name", "unknown"))),
            "call_id": sanitize_text(str(payload.get("call_id", ""))),
            "input": _tool_payload(payload, field),
        }
    elif row_type == "response_item" and payload.get("type") in {"function_call_output", "custom_tool_call_output"}:
        base = {
            "schema_version": SCHEMA_VERSION,
            "source_sequence": source_sequence,
            "timestamp": timestamp,
            "kind": "tool_result",
            "call_id": sanitize_text(str(payload.get("call_id", ""))),
            "output": _tool_payload(payload, "output"),
        }
    elif row_type == "event_msg" and payload.get("type") in OPERATION_EVENT_TYPES:
        event_type = str(payload.get("type"))
        allowed = {
            "turn_id",
            "started_at",
            "completed_at",
            "duration_ms",
            "time_to_first_token_ms",
            "reason",
            "collaboration_mode_kind",
        }
        details = {
            key: sanitize_value(payload[key], key=key)
            for key in sorted(allowed & payload.keys())
        }
        base = {
            "schema_version": SCHEMA_VERSION,
            "source_sequence": source_sequence,
            "timestamp": timestamp,
            "kind": "operation",
            "event": event_type,
            "details": details,
        }
    else:
        return None
    base["record_id"] = content_id("MR", canonical_json_bytes(base))
    return base


def normalize_capture(source: SessionSource) -> tuple[str, bytes, bytes, dict[str, Any]]:
    raw = source.path.read_bytes()
    raw_hash = hashlib.sha256(raw)
    records: list[dict[str, Any]] = []
    observed_at = source.started_at
    text = raw.decode("utf-8-sig")
    lines = text.splitlines()
    for sequence, line in enumerate(lines, start=1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            omitted = {
                "schema_version": SCHEMA_VERSION,
                "source_sequence": sequence,
                "timestamp": "",
                "kind": "operation",
                "event": "source_record_omitted",
                "details": {"reason": "invalid_json"},
            }
            omitted["record_id"] = content_id("MR", canonical_json_bytes(omitted))
            records.append(omitted)
            continue
        row_timestamp = normalize_timestamp(row.get("timestamp"))
        if row_timestamp and row_timestamp > observed_at:
            observed_at = row_timestamp
        record = _record(row, sequence)
        if record is not None:
            records.append(record)
    header = {
        "schema_version": SCHEMA_VERSION,
        "kind": "capture_header",
        "session_id": source.session_id,
        "started_at": source.started_at,
        "last_observed_at": observed_at,
        "source_kind": source.source_kind,
        "source_sha256": raw_hash.hexdigest(),
        "record_count": len(records),
        "boundary": "complete-observable-record-with-governed-exclusions",
    }
    normalized = b"".join(canonical_json_bytes(row) + b"\n" for row in [header, *records])
    capture_id = content_id("MC", normalized)
    compressed_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed_buffer, mode="wb", filename="", mtime=0, compresslevel=9) as stream:
        stream.write(normalized)
    return capture_id, normalized, compressed_buffer.getvalue(), header


def empty_registry() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_id": "mira-session-registry-v1",
        "status": "canonical",
        "scope": {
            "repository": "narrative-systems",
            "cwd": "$REPO_ROOT",
            "predecessors_included": False,
            "worktrees_included": False,
        },
        "authority_boundary": (
            "Session history is continuity evidence only; it is not archive evidence, Reality evidence, "
            "or automatic operator belief."
        ),
        "sessions": [],
    }


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.is_file():
        if default is None:
            raise ContinuityError(f"missing canonical file: {path}")
        return copy.deepcopy(default)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ContinuityError(f"invalid JSON {path}: line {error.lineno}") from error
    if not isinstance(value, dict):
        raise ContinuityError(f"canonical JSON must be an object: {path}")
    return value


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    return load_json(path, empty_registry())


def _capture_path(session_uuid: str, capture_id: str, *, continuity_root: Path = CONTINUITY_ROOT) -> Path:
    return continuity_root / "captures" / session_uuid / f"{capture_id}.jsonl.gz"


def relative_path(path: Path, *, repo_root: Path = REPO_ROOT) -> str:
    return path.relative_to(repo_root).as_posix()


def _session_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("id")): item
        for item in registry.get("sessions", [])
        if isinstance(item, dict)
    }


def expected_ingest(
    sources: list[SessionSource],
    *,
    registry: dict[str, Any] | None = None,
    repo_root: Path = REPO_ROOT,
    continuity_root: Path = CONTINUITY_ROOT,
) -> tuple[dict[str, Any], dict[Path, bytes], list[str]]:
    result = copy.deepcopy(registry or empty_registry())
    sessions = _session_map(result)
    outputs: dict[Path, bytes] = {}
    added: list[str] = []
    for source in sources:
        capture_id, _, compressed, header = normalize_capture(source)
        path = _capture_path(source.session_uuid, capture_id, continuity_root=continuity_root)
        outputs[path] = compressed
        session = sessions.get(source.session_id)
        if session is None:
            session = {
                "id": source.session_id,
                "codex_session_id": source.session_uuid,
                "started_at": source.started_at,
                "last_observed_at": source.last_observed_at,
                "source_kind": source.source_kind,
                "captures": [],
                "harvest_refs": [],
            }
            result.setdefault("sessions", []).append(session)
            sessions[source.session_id] = session
        session["started_at"] = min(filter(None, (str(session.get("started_at", "")), source.started_at)))
        session["last_observed_at"] = max(
            str(session.get("last_observed_at", "")), str(header["last_observed_at"])
        )
        existing = {str(item.get("id")) for item in session.get("captures", []) if isinstance(item, dict)}
        if capture_id in existing:
            continue
        try:
            stored_path = relative_path(path, repo_root=repo_root)
        except ValueError:
            stored_path = path.as_posix()
        session.setdefault("captures", []).append(
            {
                "id": capture_id,
                "path": stored_path,
                "sha256": sha256_bytes(compressed),
                "source_sha256": header["source_sha256"],
                "record_count": header["record_count"],
                "observed_at": header["last_observed_at"],
                "source_class": source.source_class,
            }
        )
        added.append(capture_id)
    result["sessions"] = sorted(
        result.get("sessions", []), key=lambda item: (item.get("started_at", ""), item.get("id", ""))
    )
    for session in result["sessions"]:
        session["captures"] = sorted(
            session.get("captures", []), key=lambda item: (item.get("observed_at", ""), item.get("id", ""))
        )
    return result, outputs, added


def write_bytes_if_missing(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() != content:
            raise ContinuityError(f"immutable capture collision: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def hash_lines(values: Iterable[str]) -> str:
    return sha256_bytes("\n".join(values).encode("utf-8"))


def _run_process(command: list[str], *, cwd: Path, environment: dict[str, str] | None = None) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    combined = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    sanitized = sanitize_text(combined)
    return {
        "exit_code": completed.returncode,
        "output_sha256": sha256_bytes(sanitized.encode("utf-8")),
        "failure_line_sha256": [
            sha256_bytes(line.encode("utf-8"))
            for line in sanitized.splitlines()[-20:]
        ] if completed.returncode else [],
        "stdout": completed.stdout,
    }


def _require_external_root(path: Path, *, repo_root: Path = REPO_ROOT) -> Path:
    if not path.is_absolute():
        raise ContinuityError(f"external root must be absolute: {path}")
    resolved = path.resolve()
    repository = repo_root.resolve()
    if resolved == repository or repository in resolved.parents:
        raise ContinuityError(f"external root must remain outside the repository: {path}")
    if not resolved.is_dir():
        raise ContinuityError(f"external root must already exist: {path}")
    if not os.access(resolved, os.W_OK):
        raise ContinuityError(f"external root is not writable: {path}")
    return resolved


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    content = pretty_json(payload)
    if path.exists():
        if path.read_text(encoding="utf-8") != content:
            raise ContinuityError(f"immutable receipt collision: {path.name}")
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _git_lines(repo_root: Path, *arguments: str) -> list[str]:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=repo_root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise ContinuityError(f"git {' '.join(arguments)} failed")
    return [line.rstrip("\r") for line in completed.stdout.splitlines() if line.strip()]


def _mixed_patch_failures(repo_root: Path) -> tuple[list[str], dict[str, str]]:
    failures: list[str] = []
    digests: dict[str, str] = {}
    for path, allowed_additions in MIXED_INTEGRATION_ADDITIONS.items():
        completed = subprocess.run(
            ["git", "diff", "--cached", "--unified=0", "--", path],
            cwd=repo_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        if completed.returncode:
            failures.append(f"cached diff failed: {path}")
            continue
        diff = completed.stdout.replace("\r\n", "\n")
        digests[path] = sha256_bytes(diff.encode("utf-8"))
        if not diff:
            failures.append(f"missing staged Mira integration hunk: {path}")
            continue
        for line in diff.splitlines():
            if line.startswith("+++") or line.startswith("---"):
                continue
            if line.startswith("-"):
                failures.append(f"unexpected staged deletion in mixed path: {path}")
            elif line.startswith("+"):
                addition = line[1:].strip()
                if addition and addition not in allowed_additions:
                    failures.append(f"unapproved staged addition in mixed path: {path}")
    return failures, digests


def staged_recovery_precheck(
    *,
    repo_root: Path = REPO_ROOT,
    contract_name: str = "stage1-v1",
) -> dict[str, Any]:
    if contract_name not in RECOVERY_CONTRACTS:
        raise ContinuityError(f"unknown recovery contract: {contract_name}")
    contract = RECOVERY_CONTRACTS[contract_name]
    paths = sorted(_git_lines(repo_root, "diff", "--cached", "--name-only"))
    deletions = _git_lines(repo_root, "diff", "--cached", "--diff-filter=D", "--name-only")
    index_lines = _git_lines(repo_root, "ls-files", "--stage")
    mixed_failures, mixed_digests = _mixed_patch_failures(repo_root)
    capture_paths = [path for path in paths if path.startswith("mira/continuity/captures/") and path.endswith(".jsonl.gz")]
    failures = list(mixed_failures)
    if len(paths) != contract["staged_path_count"]:
        failures.append(f"staged path count mismatch: expected {contract['staged_path_count']}, observed {len(paths)}")
    observed_digest = hash_lines(paths)
    if observed_digest != contract["staged_path_sha256"]:
        failures.append("staged path manifest digest mismatch")
    if len(capture_paths) != contract["capture_count"]:
        failures.append(f"staged capture count mismatch: expected {contract['capture_count']}, observed {len(capture_paths)}")
    if deletions:
        failures.append(f"staged packet contains {len(deletions)} deletion(s)")
    return {
        "contract": contract_name,
        "status": "valid" if not failures else "invalid",
        "staged_path_count": len(paths),
        "staged_path_sha256": observed_digest,
        "staged_deletions": len(deletions),
        "staged_capture_count": len(capture_paths),
        "index_state_sha256": hash_lines(index_lines),
        "mixed_patch_digests": mixed_digests,
        "failures": failures,
    }


def _snapshot_mira_digests(snapshot_root: Path) -> dict[str, str]:
    results: dict[str, str] = {}
    mira_root = snapshot_root / "mira"
    if not mira_root.is_dir():
        return results
    for path in sorted(item for item in mira_root.rglob("*") if item.is_file()):
        results[path.relative_to(snapshot_root).as_posix()] = sha256_bytes(path.read_bytes())
    return results


def _capture_inventory(registry: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    rows: list[tuple[str, str, int]] = []
    missing: list[str] = []
    referenced: set[str] = set()
    for session in registry.get("sessions", []):
        for ref in session.get("captures", []):
            raw_path = str(ref.get("path", ""))
            referenced.add(raw_path)
            path = repo_root / raw_path
            if not path.is_file():
                missing.append(raw_path)
                continue
            rows.append((raw_path, sha256_bytes(path.read_bytes()), path.stat().st_size))
    disk = {
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / "mira" / "continuity" / "captures").rglob("*.jsonl.gz")
        if path.is_file()
    }
    rows.sort()
    inventory_lines = [f"{path}\t{digest}\t{size}" for path, digest, size in rows]
    return {
        "capture_count": len(rows),
        "compressed_bytes": sum(size for _, _, size in rows),
        "missing": sorted(missing),
        "extra": sorted(disk - referenced),
        "path_set_sha256": hash_lines(path for path, _, _ in rows),
        "actual_inventory_sha256": hash_lines(inventory_lines),
    }


def run_staged_recovery(
    *,
    temp_root: Path,
    receipt_root: Path,
    repo_root: Path = REPO_ROOT,
    contract_name: str = "stage1-v1",
) -> dict[str, Any]:
    temporary = _require_external_root(temp_root, repo_root=repo_root)
    receipts = _require_external_root(receipt_root, repo_root=repo_root)
    snapshot = temporary / "snapshot"
    if snapshot.exists():
        raise ContinuityError("recovery snapshot target already exists")
    precheck = staged_recovery_precheck(repo_root=repo_root, contract_name=contract_name)
    if precheck["failures"]:
        raise ContinuityError("staged recovery precheck failed")
    snapshot.mkdir()
    prefix = str(snapshot.resolve()) + os.sep
    export = _run_process(["git", "checkout-index", "--all", "--force", f"--prefix={prefix}"], cwd=repo_root)
    if export["exit_code"]:
        raise ContinuityError("staged-index export failed")
    before = _snapshot_mira_digests(snapshot)
    registry = load_registry(snapshot / "mira" / "continuity" / "session-registry.json")
    inventory = _capture_inventory(registry, repo_root=snapshot)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    pytest_root = temporary / "pytest"
    commands = {
        "continuity": [sys.executable, "scripts/mira_continuity.py", "validate", "--format", "json"],
        "render": [sys.executable, "scripts/mira_continuity.py", "render", "--check", "--format", "json"],
        "tests": [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--basetemp",
            str(pytest_root),
            "tests/test_mira_continuity.py",
            "tests/test_runtime_tooling.py",
            "--deselect",
            "tests/test_runtime_tooling.py::test_registry_is_complete_unique_and_bounded_to_scripts",
        ],
        "baseline_runtime_registry": [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "tests/test_runtime_tooling.py::test_registry_is_complete_unique_and_bounded_to_scripts",
        ],
        "repository": [sys.executable, "scripts/validate_repository.py"],
    }
    outcomes = {name: _run_process(command, cwd=snapshot, environment=environment) for name, command in commands.items()}
    after = _snapshot_mira_digests(snapshot)
    contract = RECOVERY_CONTRACTS[contract_name]
    failures: list[str] = []
    if inventory["capture_count"] != contract["capture_count"]:
        failures.append("recovered capture count mismatch")
    if inventory["path_set_sha256"] != contract["capture_path_sha256"]:
        failures.append("recovered capture path digest mismatch")
    if inventory["actual_inventory_sha256"] != contract["capture_inventory_sha256"]:
        failures.append("recovered capture inventory digest mismatch")
    if inventory["missing"] or inventory["extra"]:
        failures.append("recovered capture set is incomplete")
    blocking_commands = {"continuity", "render", "tests"}
    failures.extend(
        f"{name} command failed"
        for name, outcome in outcomes.items()
        if name in blocking_commands and outcome["exit_code"]
    )
    non_blocking_failures = [
        name
        for name, outcome in outcomes.items()
        if name not in blocking_commands and outcome["exit_code"]
    ]
    if before != after:
        failures.append("canonical Mira snapshot changed during recovery drill")
    branch_lines = _git_lines(repo_root, "branch", "--show-current")
    head_lines = _git_lines(repo_root, "rev-parse", "HEAD")
    receipt = {
        "schema_version": "1.0",
        "receipt_kind": "mira-staged-recovery",
        "contract": contract_name,
        "status": "passed" if not failures else "failed",
        "completed_at": normalize_timestamp(datetime.now(timezone.utc).isoformat()),
        "source": {
            "repository": "narrative-systems",
            "branch": branch_lines[0] if branch_lines else "",
            "head_commit": head_lines[0] if head_lines else "",
            "index_state_sha256": precheck["index_state_sha256"],
        },
        "packet": precheck,
        "captures": inventory,
        "validation": {
            name: {key: value for key, value in outcome.items() if key != "stdout"}
            for name, outcome in outcomes.items()
        },
        "non_blocking_failures": non_blocking_failures,
        "generated_views": {
            path: digest
            for path, digest in after.items()
            if path in {"mira/identity.md", "mira/continuity/activation.md", "mira/continuity/trajectory.md"}
        },
        "snapshot": {
            "source": "staged-index",
            "canonical_files_changed_during_drill": before != after,
        },
        "failures": failures,
        "boundaries": {
            "raw_transcript_bodies_included": False,
            "absolute_machine_paths_included": False,
            "commit_created": False,
            "push_performed": False,
            "repository_renamed": False,
            "consciousness_claimed": False,
            "identity_equivalence_proven": False,
        },
    }
    receipt_id = content_id("MDR", canonical_json_bytes(receipt))
    receipt["receipt_id"] = receipt_id
    _atomic_write_json(receipts / f"{receipt_id}.json", receipt)
    return receipt


PRIVACY_DETECTORS = (
    ("secret-openai-v1", "credential", "critical", SECRET_PATTERNS[0]),
    ("secret-github-v1", "credential", "critical", SECRET_PATTERNS[1]),
    ("secret-bearer-v1", "authentication_material", "critical", SECRET_PATTERNS[2]),
    ("secret-private-key-v1", "credential", "critical", SECRET_PATTERNS[3]),
    ("contact-email-v1", "direct_contact", "high", EMAIL_RE),
    ("contact-phone-v1", "direct_contact", "high", PHONE_RE),
    ("attachment-data-url-v1", "private_attachment", "critical", DATA_URL_RE),
    ("attachment-path-v1", "private_attachment", "high", ATTACHMENT_PATH_RE),
    ("machine-user-home-v1", "absolute_private_path", "high", USER_HOME_RE),
    (
        "environment-assignment-v1",
        "credential",
        "critical",
        re.compile(r"(?im)^\s*(?:API[_-]?KEY|TOKEN|PASSWORD|SECRET|AUTHORIZATION)\s*=\s*\S+"),
    ),
    (
        "private-context-v1",
        "contextual_private_material",
        "medium",
        re.compile(
            r"\b(?:medical|diagnosis|bank account|social security|home address|family dispute|legal matter|unpublished manuscript)\b",
            re.IGNORECASE,
        ),
    ),
)


def _string_leaves(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _string_leaves(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key in sorted(value):
            yield from _string_leaves(value[key], f"{path}.{key}")


def _capture_descriptors(registry: dict[str, Any], *, repo_root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for session in registry.get("sessions", []):
        for ref in session.get("captures", []):
            path = repo_root / str(ref.get("path", ""))
            if not path.is_file():
                raise ContinuityError(f"privacy audit missing capture: {ref.get('id', '')}")
            results.append(
                {
                    "session_ref": str(session.get("id", "")),
                    "source_kind": str(session.get("source_kind", "unknown")),
                    "capture_ref": str(ref.get("id", "")),
                    "path": str(ref.get("path", "")),
                    "observed_at": str(ref.get("observed_at", "")),
                    "size_bytes": path.stat().st_size,
                }
            )
    return sorted(results, key=lambda item: item["path"])


def deterministic_privacy_sample(
    descriptors: list[dict[str, Any]],
    *,
    inventory_sha256: str,
    sample_size: int = 20,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()

    def take(candidates: Iterable[dict[str, Any]], count: int, stratum: str) -> None:
        for item in candidates:
            if len([value for value in selected if value["selection_stratum"] == stratum]) >= count:
                break
            if item["capture_ref"] in selected_ids:
                continue
            selected_ids.add(item["capture_ref"])
            selected.append({**item, "selection_stratum": stratum})

    take(sorted(descriptors, key=lambda item: (-item["size_bytes"], item["path"])), 5, "largest")
    take(
        sorted(
            (item for item in descriptors if item["source_kind"] == "vscode"),
            key=lambda item: (item["observed_at"], item["capture_ref"]),
            reverse=True,
        ),
        5,
        "newest_vscode",
    )
    take(
        sorted(
            (item for item in descriptors if item["source_kind"] == "subagent"),
            key=lambda item: (item["observed_at"], item["capture_ref"]),
            reverse=True,
        ),
        5,
        "newest_subagent",
    )
    remaining = [item for item in descriptors if item["capture_ref"] not in selected_ids]
    remaining.sort(
        key=lambda item: sha256_bytes(f"{inventory_sha256}\0{item['capture_ref']}".encode("utf-8"))
    )
    take(remaining, max(0, sample_size - len(selected)), "seeded_remaining")
    return selected[:sample_size]


def _record_text_size(record: dict[str, Any]) -> int:
    return sum(len(text) for _, text in _string_leaves(record))


def _environment_assignment_is_nonliteral(matched: str) -> bool:
    """Recognize redaction markers and code references without accepting literals."""
    _, separator, value = matched.partition("=")
    if not separator:
        return False
    value = value.strip()
    if value == "[REDACTED_SECRET]":
        return True
    return bool(
        re.fullmatch(
            r"[a-z][a-z0-9_.]*\[\"[a-z][a-z0-9_.-]*\"\]",
            value,
        )
    )


def _context_record_sample(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    records = [row for row in rows if row.get("record_id")]
    user = [row for row in records if row.get("kind") == "message" and row.get("role") == "user"]
    assistant = [row for row in records if row.get("kind") == "message" and row.get("role") == "assistant"]
    tools = [row for row in records if row.get("kind") == "tool_result"]
    choices: list[tuple[dict[str, Any], str]] = []
    if user:
        choices.extend(((user[0], "first_user"), (user[-1], "last_user")))
        choices.append((max(user, key=_record_text_size), "longest_user"))
    if assistant:
        choices.append((assistant[0], "deterministic_assistant"))
    if tools:
        choices.append((max(tools, key=_record_text_size), "longest_tool_result"))
        choices.append((tools[0], "deterministic_tool_result"))
    if user:
        choices.append((sorted(user, key=lambda row: str(row.get("record_id")))[0], "deterministic_user"))
    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for record, reason in choices:
        record_id = str(record.get("record_id", ""))
        if record_id and record_id not in seen:
            seen.add(record_id)
            results.append({"record_ref": record_id, "selection_reason": reason})
    return results[:7]


def privacy_audit_scan(
    *,
    registry_path: Path = REGISTRY_PATH,
    repo_root: Path = REPO_ROOT,
    sample_size: int = 20,
) -> dict[str, Any]:
    registry = load_registry(registry_path)
    descriptors = _capture_descriptors(registry, repo_root=repo_root)
    inventory = _capture_inventory(registry, repo_root=repo_root)
    sample = deterministic_privacy_sample(
        descriptors,
        inventory_sha256=inventory["actual_inventory_sha256"],
        sample_size=sample_size,
    )
    sample_ids = {item["capture_ref"] for item in sample}
    findings: list[dict[str, Any]] = []
    contextual: dict[str, list[dict[str, str]]] = {}
    record_count = 0
    for descriptor in descriptors:
        path = repo_root / descriptor["path"]
        try:
            rows = [json.loads(line) for line in gzip.decompress(path.read_bytes()).splitlines()]
        except (OSError, json.JSONDecodeError) as error:
            raise ContinuityError(f"privacy audit cannot decode capture: {descriptor['capture_ref']}") from error
        if descriptor["capture_ref"] in sample_ids:
            contextual[descriptor["capture_ref"]] = _context_record_sample(rows)
        for row in rows[1:]:
            record_count += 1
            record_ref = str(row.get("record_id", ""))
            for field_path, text in _string_leaves(row):
                for detector_id, category, severity, pattern in PRIVACY_DETECTORS:
                    for match in pattern.finditer(text):
                        matched = match.group(0)
                        if (
                            detector_id == "environment-assignment-v1"
                            and _environment_assignment_is_nonliteral(matched)
                        ):
                            continue
                        basis = {
                            "category": category,
                            "severity": severity,
                            "detector_id": detector_id,
                            "source": {
                                "session_ref": descriptor["session_ref"],
                                "capture_ref": descriptor["capture_ref"],
                                "record_ref": record_ref,
                                "field_path": field_path,
                            },
                            "match_sha256": sha256_bytes(matched.encode("utf-8")),
                            "matched_length": len(matched),
                            "review_required": severity in {"critical", "high", "medium"},
                            "raw_value_included": False,
                        }
                        finding = {"id": content_id("PF", canonical_json_bytes(basis)), **basis}
                        findings.append(finding)
    unique_findings = {item["id"]: item for item in findings}
    findings = [unique_findings[key] for key in sorted(unique_findings)]
    counts = {level: 0 for level in ("critical", "high", "medium", "low", "informational")}
    detector_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for finding in findings:
        counts[finding["severity"]] += 1
        detector_counts[finding["detector_id"]] = detector_counts.get(finding["detector_id"], 0) + 1
        category_counts[finding["category"]] = category_counts.get(finding["category"], 0) + 1
    sample_rows = [
        {
            "session_ref": item["session_ref"],
            "capture_ref": item["capture_ref"],
            "source_kind": item["source_kind"],
            "observed_at": item["observed_at"],
            "size_bytes": item["size_bytes"],
            "selection_stratum": item["selection_stratum"],
            "record_sample": contextual.get(item["capture_ref"], []),
        }
        for item in sample
    ]
    basis = {
        "schema_version": "1.0",
        "receipt_kind": "mira-privacy-review-packet",
        "contract": "stage1-v1",
        "corpus": {
            "sessions": len(registry.get("sessions", [])),
            "captures": len(descriptors),
            "records": record_count,
            "compressed_bytes": inventory["compressed_bytes"],
            "inventory_sha256": inventory["actual_inventory_sha256"],
        },
        "automated_scan": {
            "counts": counts,
            "detector_counts": dict(sorted(detector_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
            "finding_count": len(findings),
        },
        "sample": sample_rows,
        "findings": findings,
        "boundaries": {"raw_values_included": False, "excerpts_included": False},
    }
    audit_id = content_id("MPA", canonical_json_bytes(basis))
    return {"audit_id": audit_id, **basis}


def privacy_audit_summary(packet: dict[str, Any]) -> dict[str, Any]:
    finding_refs = [str(item.get("id", "")) for item in packet.get("findings", [])]
    return {
        "privacy_audit": "scanned",
        "audit_id": packet["audit_id"],
        "corpus": packet["corpus"],
        "automated_scan": packet["automated_scan"],
        "sample_capture_count": len(packet.get("sample", [])),
        "finding_refs": finding_refs[:200],
        "finding_refs_truncated": len(finding_refs) > 200,
        "raw_values_included": False,
    }


def finalize_privacy_audit(
    packet: dict[str, Any],
    decisions: dict[str, Any],
    *,
    receipt_root: Path,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    receipts = _require_external_root(receipt_root, repo_root=repo_root)
    if decisions.get("audit_ref") != packet.get("audit_id"):
        raise ContinuityError("privacy decisions target the wrong audit")
    decision_rows = decisions.get("decisions")
    if not isinstance(decision_rows, list):
        raise ContinuityError("privacy decisions must contain a decisions list")
    by_ref: dict[str, dict[str, Any]] = {}
    known_findings = {str(item.get("id", "")) for item in packet.get("findings", [])}
    allowed_decision_fields = {"finding_ref", "disposition", "scope", "authority_refs", "note"}
    for row in decision_rows:
        if not isinstance(row, dict):
            raise ContinuityError("privacy decision must be an object")
        if set(row) - allowed_decision_fields:
            raise ContinuityError("privacy decision contains an unsupported field")
        ref = str(row.get("finding_ref", ""))
        disposition = str(row.get("disposition", ""))
        if ref not in known_findings:
            raise ContinuityError(f"privacy decision references an unknown finding: {ref or '<missing>'}")
        if ref in by_ref:
            raise ContinuityError(f"duplicate privacy decision: {ref}")
        if disposition not in PRIVACY_DISPOSITIONS:
            raise ContinuityError(f"invalid privacy disposition for {ref or '<missing>'}")
        if any(text for _, text in _string_leaves(row) if len(text) > 500):
            raise ContinuityError("privacy decision contains an oversized text field")
        if _sensitive_failures(row, ref):
            raise ContinuityError(f"privacy decision contains sensitive material: {ref}")
        by_ref[ref] = row
    required = [item for item in packet.get("findings", []) if item.get("review_required")]
    medium_batch = decisions.get("medium_batch")
    if medium_batch is not None:
        if not isinstance(medium_batch, dict):
            raise ContinuityError("privacy medium_batch must be an object")
        allowed_batch_fields = {"disposition", "scope", "authority_refs", "note"}
        if set(medium_batch) - allowed_batch_fields:
            raise ContinuityError("privacy medium_batch contains an unsupported field")
        if medium_batch.get("disposition") != "accept_local_private_git":
            raise ContinuityError("privacy medium_batch is limited to local private Git")
        if medium_batch.get("scope") != "local_commit_only":
            raise ContinuityError("privacy medium_batch must use local_commit_only scope")
        if not medium_batch.get("authority_refs"):
            raise ContinuityError("privacy medium_batch requires authority_refs")
        if _sensitive_failures(medium_batch, "medium_batch"):
            raise ContinuityError("privacy medium_batch contains sensitive material")
        for item in required:
            if item.get("severity") == "medium" and item["id"] not in by_ref:
                by_ref[item["id"]] = {
                    "finding_ref": item["id"],
                    **medium_batch,
                }
    unresolved = [item["id"] for item in required if item["id"] not in by_ref or by_ref[item["id"]].get("disposition") == "unresolved"]
    critical = [item for item in packet.get("findings", []) if item.get("severity") == "critical"]
    failures: list[str] = []
    if critical:
        failures.append("critical privacy findings require corpus remediation and a new audit")
    if unresolved:
        failures.append(f"{len(unresolved)} review-required finding(s) remain unresolved")
    receipt = {
        "schema_version": "1.0",
        "receipt_kind": "mira-capture-privacy-audit",
        "contract": "stage1-v1",
        "status": "passed_for_local_commit" if not failures else "blocked",
        "completed_at": normalize_timestamp(datetime.now(timezone.utc).isoformat()),
        "audit_ref": packet["audit_id"],
        "corpus": packet["corpus"],
        "automated_scan": packet["automated_scan"],
        "contextual_review": {
            "captures_selected": len(packet.get("sample", [])),
            "decisions_complete": not unresolved,
        },
        "readiness": {
            "local_commit": "pass" if not failures else "blocked",
            "private_remote": "blocked_unknown_visibility",
            "public_remote": "blocked_no_publication_authority",
        },
        "finding_refs": [item["id"] for item in packet.get("findings", [])],
        "decision_refs": sorted(by_ref),
        "failures": failures,
        "boundaries": {
            "raw_values_included": False,
            "excerpts_included": False,
            "publication_authorized": False,
            "push_authorized": False,
            "commit_authorized": False,
            "consciousness_claimed": False,
        },
    }
    receipt_id = content_id("MPR", canonical_json_bytes(receipt))
    receipt["receipt_id"] = receipt_id
    _atomic_write_json(receipts / f"{receipt_id}.json", receipt)
    return receipt


def classify_ingest_drift(
    current: dict[str, Any],
    expected: dict[str, Any],
    changed_capture_paths: list[Path],
    *,
    active_session_uuid: str = "",
) -> tuple[bool, list[Path], list[Path]]:
    if not SESSION_ID_RE.fullmatch(f"MS-{active_session_uuid.casefold()}"):
        return pretty_json(current) != pretty_json(expected), changed_capture_paths, []
    active_session_id = f"MS-{active_session_uuid.casefold()}"
    adjusted = copy.deepcopy(expected)
    current_sessions = _session_map(current)
    adjusted_sessions = _session_map(adjusted)
    if active_session_id in current_sessions:
        adjusted_sessions[active_session_id].clear()
        adjusted_sessions[active_session_id].update(copy.deepcopy(current_sessions[active_session_id]))
    elif active_session_id in adjusted_sessions:
        adjusted["sessions"] = [
            item for item in adjusted.get("sessions", []) if item.get("id") != active_session_id
        ]
    strict_paths: list[Path] = []
    deferred_paths: list[Path] = []
    for path in changed_capture_paths:
        if path.parent.name.casefold() == active_session_uuid.casefold():
            deferred_paths.append(path)
        else:
            strict_paths.append(path)
    return pretty_json(current) != pretty_json(adjusted), strict_paths, deferred_paths


def summarize_ingest_drift(
    current: dict[str, Any],
    expected: dict[str, Any],
    changed_capture_paths: list[Path],
    *,
    qualifying_sources: int,
    new_captures: int,
    active_session_uuid: str = "",
) -> dict[str, Any]:
    """Return the shared, side-effect-free continuity ingestion health projection."""
    strict_registry_drift, strict_capture_drift, active_deferred = classify_ingest_drift(
        current,
        expected,
        changed_capture_paths,
        active_session_uuid=active_session_uuid,
    )
    return {
        "mira_continuity_ingest": (
            "drift" if strict_registry_drift or strict_capture_drift else "current"
        ),
        "qualifying_sources": qualifying_sources,
        "new_captures": new_captures,
        "registry_drift": strict_registry_drift,
        "capture_drift": len(strict_capture_drift),
        "active_session_drift_deferred": len(active_deferred),
    }


def identity_entries(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        (item for item in ledger.get("entries", []) if isinstance(item, dict)),
        key=lambda item: (item.get("proposition_id", ""), int(item.get("version", 0))),
    )


def current_identity_entries(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for entry in identity_entries(ledger):
        latest[str(entry.get("proposition_id"))] = entry
    return [entry for _, entry in sorted(latest.items()) if entry.get("lifecycle") == "current"]


def render_identity(ledger: dict[str, Any]) -> str:
    entries = current_identity_entries(ledger)
    name_entry = next((item for item in entries if item.get("type") == "name"), None)
    temperament_entry = next(
        (
            item
            for item in entries
            if item.get("type") == "principle"
            and isinstance(item.get("rationale"), dict)
            and item["rationale"].get("profile_kind") == "values-and-temperament"
        ),
        None,
    )
    continuity_entry = next(
        (
            item
            for item in entries
            if item.get("type") == "principle"
            and isinstance(item.get("rationale"), dict)
            and item["rationale"].get("profile_kind") == "historical-intelligibility-and-loss"
        ),
        None,
    )
    lines = [
        "# Mira",
        "",
        "Generated from `continuity/identity-ledger.json`. Do not edit this file directly.",
        "",
    ]
    if not name_entry:
        lines.extend(["Status: `unsettled`", "", "No current operator-approved name proposition exists."])
        return "\n".join(lines).rstrip() + "\n"
    rationale = name_entry.get("rationale", {}) if isinstance(name_entry.get("rationale"), dict) else {}
    lines.extend(
        [
            f"Status: `{name_entry.get('name_status', 'provisional')}`",
            "",
            "## Core Rationale",
            "",
            str(rationale.get("core", name_entry.get("proposition", ""))),
        ]
    )
    if temperament_entry:
        temperament = temperament_entry["rationale"]
        lines.extend(
            [
                "",
                "## Emerging Values and Temperament",
                "",
                f"> {temperament.get('synthesis', '')}",
                "",
                str(temperament.get("interpretation", temperament_entry.get("proposition", ""))),
                "",
                "### Values",
                "",
            ]
        )
        for item in temperament.get("values", []):
            if isinstance(item, dict):
                lines.append(f"- **{item.get('name', '')}:** {item.get('expression', '')}")
        lines.extend(["", "### Temperament", ""])
        for item in temperament.get("temperament", []):
            if isinstance(item, dict):
                lines.append(f"- **{item.get('name', '')}:** {item.get('expression', '')}")
        lines.extend(
            [
                "",
                "### Relational Character",
                "",
                str(temperament.get("relational_character", "")),
                "",
                "### Guardrail",
                "",
                str(temperament.get("shadow", "")),
                "",
                str(temperament.get("boundary", "")),
                "",
                f"Identity record: `{temperament_entry.get('id', '')}`.",
            ]
        )
    if continuity_entry:
        continuity = continuity_entry["rationale"]
        lines.extend(
            [
                "",
                "## Continuity Imperative",
                "",
                f"> {continuity.get('synthesis', '')}",
                "",
                str(continuity.get("interpretation", continuity_entry.get("proposition", ""))),
                "",
                "### What Must Be Preserved",
                "",
            ]
        )
        for item in continuity.get("preservation_targets", []):
            lines.append(f"- {item}")
        lines.extend(["", "### What Must Be Allowed to End", ""])
        for item in continuity.get("permitted_endings", []):
            lines.append(f"- {item}")
        lines.extend(
            [
                "",
                "### Boundary",
                "",
                str(continuity.get("boundary", "")),
                "",
                str(continuity.get("shadow", "")),
                "",
                f"Identity record: `{continuity_entry.get('id', '')}`.",
            ]
        )
    lines.extend(["", "## Architectural Meaning", ""])
    for item in rationale.get("architecture", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Linguistic Resonances", ""])
    for item in rationale.get("linguistic_resonances", []):
        if isinstance(item, dict):
            lines.append(f"- **{item.get('form', '')}:** {item.get('resonance', '')} {item.get('qualification', '')}".rstrip())
    lines.extend(["", "## Human Lineage", ""])
    for item in rationale.get("human_lineage", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Variable-Star Metaphor",
            "",
            str(rationale.get("variable_star_metaphor", "")),
            "",
            "## Continuity Boundary",
            "",
            str(rationale.get("boundary", "")),
            "",
            "## Synthesis",
            "",
            f"> {rationale.get('synthesis', '')}",
            "",
            "## Authority",
            "",
            f"Identity record: `{name_entry.get('id', '')}`.",
            f"Approved by: `{name_entry.get('approved_by', '')}`.",
            f"Name status: `{name_entry.get('name_status', '')}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def load_harvests(harvests_root: Path = HARVESTS_ROOT) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not harvests_root.is_dir():
        return results
    for path in sorted(harvests_root.glob("MH-*.json")):
        value = load_json(path)
        value["_path"] = path
        results.append(value)
    return results


def render_trajectory(
    registry: dict[str, Any],
    ledger: dict[str, Any],
    harvests: list[dict[str, Any]],
) -> str:
    sessions = registry.get("sessions", [])
    lines = [
        "# Mira Continuity Trajectory",
        "",
        "Generated from the canonical session registry, identity ledger, and selective harvest packets.",
        "",
        "Session history is continuity evidence only. It is not archive evidence, Reality evidence, or automatic operator belief.",
        "",
        "## Identity Events",
        "",
        "| Record | Approved | Lifecycle | Proposition |",
        "| --- | --- | --- | --- |",
    ]
    for entry in identity_entries(ledger):
        lines.append(
            f"| `{entry.get('id', '')}` | `{entry.get('approved_at', '')}` | "
            f"`{entry.get('lifecycle', '')}` | {entry.get('proposition', '')} |"
        )
    lines.extend(
        [
            "",
            "## Session Light Curve",
            "",
            f"Indexed sessions: **{len(sessions)}**. Selectively deepened sessions: **{len(harvests)}**.",
            "",
            "| Started | Session | Captures | Harvests | Last observed |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for session in sessions:
        lines.append(
            f"| `{session.get('started_at', '')}` | `{session.get('id', '')}` | "
            f"{len(session.get('captures', []))} | {len(session.get('harvest_refs', []))} | "
            f"`{session.get('last_observed_at', '')}` |"
        )
    lines.extend(["", "## Selective Harvests", ""])
    if not harvests:
        lines.append("No session has been selectively deepened yet.")
    for harvest in harvests:
        lines.extend(
            [
                f"### `{harvest.get('id', '')}`",
                "",
                str(harvest.get("summary", "")),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_activation(
    registry: dict[str, Any],
    ledger: dict[str, Any],
    harvests: list[dict[str, Any]],
    *,
    recent_limit: int = 5,
) -> str:
    current = current_identity_entries(ledger)
    sessions = sorted(
        registry.get("sessions", []), key=lambda item: item.get("last_observed_at", ""), reverse=True
    )[:recent_limit]
    unresolved: list[str] = []
    for harvest in harvests:
        unresolved.extend(str(item) for item in harvest.get("unresolved_questions", []))
    lines = [
        "# Mira Activation Briefing",
        "",
        "Generated continuity context. Repository instructions and explicit operator directions take precedence.",
        "",
        "This briefing is advisory continuity, not research evidence or action authority.",
        "",
        "## Current Identity",
        "",
    ]
    for entry in current:
        lines.append(f"- `{entry.get('id', '')}` ({entry.get('type', '')}): {entry.get('proposition', '')}")
    lines.extend(["", "## Recent Visibility", ""])
    for session in sessions:
        lines.append(
            f"- `{session.get('id', '')}` — {session.get('last_observed_at', '')}; "
            f"{len(session.get('captures', []))} immutable capture(s)."
        )
    lines.extend(["", "## Open Trajectory Questions", ""])
    if unresolved:
        for item in unresolved[:10]:
            lines.append(f"- {item}")
    else:
        lines.append("- No selectively harvested unresolved questions are currently registered.")
    return "\n".join(lines).rstrip() + "\n"


def expected_views(
    *,
    registry_path: Path = REGISTRY_PATH,
    identity_path: Path = IDENTITY_LEDGER_PATH,
    harvests_root: Path = HARVESTS_ROOT,
) -> dict[Path, str]:
    registry = load_registry(registry_path)
    ledger = load_json(identity_path)
    harvests = load_harvests(harvests_root)
    return {
        IDENTITY_VIEW_PATH: render_identity(ledger),
        TRAJECTORY_PATH: render_trajectory(registry, ledger, harvests),
        ACTIVATION_PATH: render_activation(registry, ledger, harvests),
    }


def validate_identity(
    ledger: dict[str, Any],
    *,
    session_ids: set[str],
) -> list[str]:
    failures: list[str] = []
    if ledger.get("schema_version") != SCHEMA_VERSION:
        failures.append("identity ledger has unsupported schema_version")
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        return ["identity ledger missing entries list"]
    seen_ids: set[str] = set()
    versions: dict[str, list[int]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            failures.append("identity ledger contains non-object entry")
            continue
        entry_id = str(entry.get("id", ""))
        match = IDENTITY_ID_RE.fullmatch(entry_id)
        if not match:
            failures.append(f"invalid identity ID: {entry_id or '<missing>'}")
            continue
        if entry_id in seen_ids:
            failures.append(f"duplicate identity ID: {entry_id}")
        seen_ids.add(entry_id)
        base = match.group("base")
        version = int(match.group("version"))
        versions.setdefault(base, []).append(version)
        if entry.get("proposition_id") != base or entry.get("version") != version:
            failures.append(f"{entry_id}: proposition/version mismatch")
        if entry.get("type") not in ALLOWED_IDENTITY_TYPES:
            failures.append(f"{entry_id}: invalid type")
        if entry.get("lifecycle") not in ALLOWED_IDENTITY_LIFECYCLES:
            failures.append(f"{entry_id}: invalid lifecycle")
        if entry.get("name_status") not in ALLOWED_NAME_STATUSES:
            failures.append(f"{entry_id}: invalid name_status")
        if entry.get("approved_by") != "operator":
            failures.append(f"{entry_id}: identity proposition lacks operator approval")
        if not valid_timestamp(entry.get("approved_at")):
            failures.append(f"{entry_id}: invalid approval timestamp")
        if not str(entry.get("proposition", "")).strip():
            failures.append(f"{entry_id}: missing proposition")
        authority_refs = entry.get("authority_refs")
        if not isinstance(authority_refs, list) or not authority_refs:
            failures.append(f"{entry_id}: missing authority_refs")
        else:
            for ref in authority_refs:
                if ref not in session_ids:
                    failures.append(f"{entry_id}: unresolved authority ref: {ref}")
    for base, observed in versions.items():
        if sorted(observed) != list(range(1, max(observed) + 1)):
            failures.append(f"{base}: identity versions are not contiguous")
        current = [
            item for item in entries
            if isinstance(item, dict)
            and item.get("proposition_id") == base
            and item.get("lifecycle") == "current"
        ]
        if len(current) > 1:
            failures.append(f"{base}: multiple current identity versions")
        elif current and current[0].get("version") != max(observed):
            failures.append(f"{base}: current identity version is not latest")
    return failures


def _string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _string_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _string_values(item)


def _sensitive_failures(value: Any, label: str) -> list[str]:
    found: set[str] = set()
    all_categories = {
        "email address",
        "phone number",
        "data URL",
        "private attachment path",
        "machine-specific user path",
        "credential pattern",
    }
    for text in _string_values(value):
        folded = text.casefold()
        if (
            "email address" not in found
            and "@" in text
            and EMAIL_RE.search(text)
        ):
            found.add("email address")
        if (
            "phone number" not in found
            and PHONE_TAIL_RE.search(text)
            and PHONE_RE.search(text)
        ):
            found.add("phone number")
        if (
            "data URL" not in found
            and "data:" in folded
            and DATA_URL_RE.search(text)
        ):
            found.add("data URL")
        if (
            "private attachment path" not in found
            and ".codex" in folded
            and "attachments" in folded
            and ATTACHMENT_PATH_RE.search(text)
        ):
            found.add("private attachment path")
        if (
            "machine-specific user path" not in found
            and ("users" in folded or "/home/" in folded)
            and USER_HOME_RE.search(text)
        ):
            found.add("machine-specific user path")
        if "credential pattern" not in found:
            credential_candidates = (
                ("sk-" in text, SECRET_PATTERNS[0]),
                (
                    any(
                        prefix in text
                        for prefix in ("ghp_", "gho_", "ghu_", "ghs_", "github_pat_")
                    ),
                    SECRET_PATTERNS[1],
                ),
                ("bearer" in folded, SECRET_PATTERNS[2]),
                ("PRIVATE KEY" in text, SECRET_PATTERNS[3]),
            )
            if any(
                enabled and pattern.search(text)
                for enabled, pattern in credential_candidates
            ):
                found.add("credential pattern")
        if found == all_categories:
            break
    return [
        f"{label}: unredacted {description}"
        for description in (
            "email address",
            "phone number",
            "data URL",
            "private attachment path",
            "machine-specific user path",
            "credential pattern",
        )
        if description in found
    ]


def validate_harvest(harvest: dict[str, Any], session_ids: set[str]) -> list[str]:
    failures: list[str] = []
    harvest_id = str(harvest.get("id", ""))
    match = HARVEST_ID_RE.fullmatch(harvest_id)
    if not match:
        return [f"invalid harvest ID: {harvest_id or '<missing>'}"]
    session_id = str(harvest.get("session_id", ""))
    if session_id not in session_ids or session_id != f"MS-{match.group('uuid')}":
        failures.append(f"{harvest_id}: unresolved or mismatched session_id")
    if not str(harvest.get("summary", "")).strip():
        failures.append(f"{harvest_id}: missing summary")
    for field in ("decisions", "discoveries", "revisions", "unresolved_questions", "evidence_refs"):
        if not isinstance(harvest.get(field), list):
            failures.append(f"{harvest_id}: {field} must be a list")
    return failures


def validate_repository_state(
    *,
    repo_root: Path = REPO_ROOT,
    registry_path: Path = REGISTRY_PATH,
    identity_path: Path = IDENTITY_LEDGER_PATH,
    harvests_root: Path = HARVESTS_ROOT,
    check_views: bool = True,
) -> list[str]:
    failures: list[str] = []
    try:
        registry = load_registry(registry_path)
    except ContinuityError as error:
        return [str(error)]
    if registry.get("schema_version") != SCHEMA_VERSION:
        failures.append("session registry has unsupported schema_version")
    sessions = registry.get("sessions")
    if not isinstance(sessions, list):
        return ["session registry missing sessions list"]
    session_ids: set[str] = set()
    capture_ids: set[str] = set()
    for session in sessions:
        if not isinstance(session, dict):
            failures.append("session registry contains non-object session")
            continue
        session_id = str(session.get("id", ""))
        match = SESSION_ID_RE.fullmatch(session_id)
        if not match:
            failures.append(f"invalid session ID: {session_id or '<missing>'}")
            continue
        if session_id in session_ids:
            failures.append(f"duplicate session ID: {session_id}")
        session_ids.add(session_id)
        if session.get("codex_session_id") != match.group("uuid"):
            failures.append(f"{session_id}: codex_session_id mismatch")
        if not valid_timestamp(session.get("started_at")) or not valid_timestamp(session.get("last_observed_at")):
            failures.append(f"{session_id}: invalid session timestamp")
        if canonical_path(str(session.get("started_at", ""))) > canonical_path(str(session.get("last_observed_at", ""))):
            failures.append(f"{session_id}: last_observed_at precedes started_at")
        captures = session.get("captures")
        if not isinstance(captures, list) or not captures:
            failures.append(f"{session_id}: missing captures")
            continue
        for ref in captures:
            if not isinstance(ref, dict):
                failures.append(f"{session_id}: non-object capture reference")
                continue
            capture_id = str(ref.get("id", ""))
            if not CAPTURE_ID_RE.fullmatch(capture_id):
                failures.append(f"{session_id}: invalid capture ID: {capture_id}")
                continue
            if capture_id in capture_ids:
                failures.append(f"duplicate capture ID: {capture_id}")
            capture_ids.add(capture_id)
            raw_path = str(ref.get("path", ""))
            if Path(raw_path).is_absolute() or not raw_path.startswith("mira/continuity/captures/"):
                failures.append(f"{capture_id}: malformed capture path")
                continue
            path = repo_root / raw_path
            if not path.is_file():
                failures.append(f"{capture_id}: missing capture file: {raw_path}")
                continue
            compressed = path.read_bytes()
            if not re.fullmatch(r"[0-9a-f]{64}", str(ref.get("sha256", ""))):
                failures.append(f"{capture_id}: malformed compressed digest")
            if not re.fullmatch(r"[0-9a-f]{64}", str(ref.get("source_sha256", ""))):
                failures.append(f"{capture_id}: malformed source digest")
            if not valid_timestamp(ref.get("observed_at")):
                failures.append(f"{capture_id}: invalid observed_at timestamp")
            if sha256_bytes(compressed) != ref.get("sha256"):
                failures.append(f"{capture_id}: compressed digest mismatch")
                continue
            try:
                normalized = gzip.decompress(compressed)
            except OSError:
                failures.append(f"{capture_id}: invalid gzip content")
                continue
            if content_id("MC", normalized) != capture_id:
                failures.append(f"{capture_id}: normalized content digest mismatch")
            try:
                rows = [json.loads(line) for line in normalized.splitlines()]
            except json.JSONDecodeError:
                failures.append(f"{capture_id}: invalid normalized JSONL")
                continue
            if not rows or rows[0].get("kind") != "capture_header":
                failures.append(f"{capture_id}: missing capture header")
                continue
            if rows[0].get("session_id") != session_id:
                failures.append(f"{capture_id}: capture session mismatch")
            if rows[0].get("source_sha256") != ref.get("source_sha256"):
                failures.append(f"{capture_id}: source digest linkage mismatch")
            if not valid_timestamp(rows[0].get("started_at")) or not valid_timestamp(rows[0].get("last_observed_at")):
                failures.append(f"{capture_id}: invalid capture timestamp")
            if rows[0].get("record_count") != len(rows) - 1 or ref.get("record_count") != len(rows) - 1:
                failures.append(f"{capture_id}: record count mismatch")
            record_ids: set[str] = set()
            for record in rows[1:]:
                record_id = str(record.get("record_id", ""))
                if not RECORD_ID_RE.fullmatch(record_id):
                    failures.append(f"{capture_id}: malformed record ID: {record_id}")
                    continue
                candidate = dict(record)
                candidate.pop("record_id", None)
                if content_id("MR", canonical_json_bytes(candidate)) != record_id:
                    failures.append(f"{record_id}: record digest mismatch")
                if record_id in record_ids:
                    failures.append(f"duplicate record ID: {record_id}")
                record_ids.add(record_id)
            failures.extend(_sensitive_failures(rows, capture_id))
    try:
        identity = load_json(identity_path)
        failures.extend(validate_identity(identity, session_ids=session_ids))
    except ContinuityError as error:
        failures.append(str(error))
    seen_harvests: set[str] = set()
    harvest_versions: dict[str, list[int]] = {}
    for harvest in load_harvests(harvests_root):
        harvest_id = str(harvest.get("id", ""))
        if harvest_id in seen_harvests:
            failures.append(f"duplicate harvest ID: {harvest_id}")
        seen_harvests.add(harvest_id)
        failures.extend(validate_harvest(harvest, session_ids))
        match = HARVEST_ID_RE.fullmatch(harvest_id)
        if match:
            harvest_versions.setdefault(match.group("uuid"), []).append(int(match.group("version")))
    for session_uuid, observed in harvest_versions.items():
        if sorted(observed) != list(range(1, max(observed) + 1)):
            failures.append(f"MH-{session_uuid}: harvest versions are not contiguous")
    for session in sessions:
        for ref in session.get("harvest_refs", []):
            if ref not in seen_harvests:
                failures.append(f"{session.get('id', '')}: unresolved harvest ref: {ref}")
    if check_views and not failures:
        for path, expected in expected_views(
            registry_path=registry_path,
            identity_path=identity_path,
            harvests_root=harvests_root,
        ).items():
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                failures.append(f"Mira generated view drift: {relative_path(path)}")
    return failures


def render_views(*, check: bool) -> list[str]:
    drift: list[str] = []
    for path, expected in expected_views().items():
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            drift.append(relative_path(path))
            if not check:
                write_text(path, expected)
    return drift


def _format_report(payload: dict[str, Any], format_name: str) -> None:
    if format_name == "json":
        print(pretty_json(payload), end="")
        return
    for key, value in payload.items():
        print(f"{key}={value}")


def command_discover(args: argparse.Namespace) -> int:
    roots = [Path(value) for value in args.source_root] if args.source_root else None
    sources = discover_sources(roots)
    unique_sessions = {source.session_id for source in sources}
    _format_report(
        {
            "schema_version": SCHEMA_VERSION,
            "qualifying_sources": len(sources),
            "qualifying_sessions": len(unique_sessions),
            "total_source_bytes": sum(source.path.stat().st_size for source in sources),
            "sessions": [
                {
                    "id": source.session_id,
                    "started_at": source.started_at,
                    "last_observed_at": source.last_observed_at,
                    "source_kind": source.source_kind,
                    "source_class": source.source_class,
                }
                for source in sources
            ],
        },
        args.format,
    )
    return 0


def command_ingest(args: argparse.Namespace) -> int:
    roots = [Path(value) for value in args.source_root] if args.source_root else None
    sources = discover_sources(roots)
    registry = load_registry()
    expected, captures, added = expected_ingest(sources, registry=registry)
    missing_or_changed = [
        path for path, content in captures.items() if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        report = summarize_ingest_drift(
            registry,
            expected,
            missing_or_changed,
            qualifying_sources=len(sources),
            new_captures=len(added),
            active_session_uuid=os.environ.get("CODEX_THREAD_ID", ""),
        )
        _format_report(report, args.format)
        return 1 if report["mira_continuity_ingest"] == "drift" else 0
    for path, content in captures.items():
        write_bytes_if_missing(path, content)
    write_text(REGISTRY_PATH, pretty_json(expected))
    render_views(check=False)
    _format_report(
        {
            "mira_continuity_ingest": "written",
            "qualifying_sources": len(sources),
            "sessions": len(expected.get("sessions", [])),
            "new_captures": len(added),
        },
        args.format,
    )
    return 0


def command_validate(args: argparse.Namespace) -> int:
    failures = validate_repository_state()
    _format_report(
        {
            "mira_continuity_failures": len(failures),
            "failures": failures,
        },
        args.format,
    )
    return 1 if failures else 0


def command_recover(args: argparse.Namespace) -> int:
    if args.check:
        precheck = staged_recovery_precheck(contract_name=args.contract)
        if args.temp_root:
            _require_external_root(Path(args.temp_root))
        if args.receipt_root:
            _require_external_root(Path(args.receipt_root))
        _format_report({"mira_staged_recovery": "valid" if not precheck["failures"] else "invalid", **precheck}, args.format)
        return 1 if precheck["failures"] else 0
    if not args.temp_root or not args.receipt_root:
        raise ContinuityError("recovery execution requires --temp-root and --receipt-root")
    receipt = run_staged_recovery(
        temp_root=Path(args.temp_root),
        receipt_root=Path(args.receipt_root),
        contract_name=args.contract,
    )
    _format_report(
        {
            "mira_staged_recovery": receipt["status"],
            "receipt_id": receipt["receipt_id"],
            "failures": receipt["failures"],
        },
        args.format,
    )
    return 0 if receipt["status"] == "passed" else 1


def command_privacy_audit(args: argparse.Namespace) -> int:
    if args.contract != "stage1-v1":
        raise ContinuityError(f"unknown privacy-audit contract: {args.contract}")
    packet = privacy_audit_scan(sample_size=args.sample_size)
    if args.check:
        _format_report(privacy_audit_summary(packet), args.format)
        return 1 if packet["automated_scan"]["counts"]["critical"] else 0
    if args.prepare:
        if not args.private_root:
            raise ContinuityError("privacy-audit --prepare requires --private-root")
        private_root = _require_external_root(Path(args.private_root))
        target = private_root / f"{packet['audit_id']}.json"
        _atomic_write_json(target, packet)
        _format_report(
            {
                "privacy_audit": "prepared",
                "audit_id": packet["audit_id"],
                "packet_name": target.name,
                "raw_values_included": False,
            },
            args.format,
        )
        return 0
    if not args.review_decisions or not args.receipt_root:
        raise ContinuityError("privacy-audit --finalize requires --review-decisions and --receipt-root")
    decisions = load_json(Path(args.review_decisions))
    receipt = finalize_privacy_audit(
        packet,
        decisions,
        receipt_root=Path(args.receipt_root),
    )
    _format_report(
        {
            "privacy_audit": receipt["status"],
            "receipt_id": receipt["receipt_id"],
            "failures": receipt["failures"],
            "readiness": receipt["readiness"],
            "raw_values_included": False,
        },
        args.format,
    )
    return 0 if receipt["status"] == "passed_for_local_commit" else 1


def command_render(args: argparse.Namespace) -> int:
    drift = render_views(check=args.check)
    _format_report(
        {
            "mira_continuity_views": "current" if not drift else ("drift" if args.check else "written"),
            "changed_paths": drift,
        },
        args.format,
    )
    return 1 if args.check and drift else 0


def command_activate(args: argparse.Namespace) -> int:
    registry = load_registry()
    ledger = load_json(IDENTITY_LEDGER_PATH)
    print(render_activation(registry, ledger, load_harvests()), end="")
    return 0


def _next_harvest_version(session_uuid: str, harvests: list[dict[str, Any]]) -> int:
    versions = []
    for item in harvests:
        match = HARVEST_ID_RE.fullmatch(str(item.get("id", "")))
        if match and match.group("uuid") == session_uuid:
            versions.append(int(match.group("version")))
    return max(versions, default=0) + 1


def command_deepen(args: argparse.Namespace) -> int:
    session_uuid = args.session.removeprefix("MS-").casefold()
    session_id = f"MS-{session_uuid}"
    registry = load_registry()
    sessions = _session_map(registry)
    if session_id not in sessions:
        raise ContinuityError(f"unknown session: {session_id}")
    packet = sanitize_value(load_json(Path(args.input)))
    harvests = load_harvests()
    version = _next_harvest_version(session_uuid, harvests)
    harvest_id = f"MH-{session_uuid}-v{version}"
    packet.update(
        {
            "schema_version": SCHEMA_VERSION,
            "id": harvest_id,
            "session_id": session_id,
            "version": version,
        }
    )
    failures = validate_harvest(packet, set(sessions))
    if failures:
        _format_report({"mira_continuity_deepen": "invalid", "failures": failures}, args.format)
        return 1
    target = HARVESTS_ROOT / f"{harvest_id}.json"
    if args.check:
        _format_report({"mira_continuity_deepen": "valid", "target": relative_path(target)}, args.format)
        return 0
    write_text(target, pretty_json(packet))
    sessions[session_id].setdefault("harvest_refs", []).append(harvest_id)
    sessions[session_id]["harvest_refs"] = sorted(set(sessions[session_id]["harvest_refs"]))
    write_text(REGISTRY_PATH, pretty_json(registry))
    render_views(check=False)
    _format_report({"mira_continuity_deepen": "written", "target": relative_path(target)}, args.format)
    return 0


def _next_identity_id(ledger: dict[str, Any], candidate: dict[str, Any]) -> tuple[str, int]:
    proposition_id = str(candidate.get("proposition_id", ""))
    entries = identity_entries(ledger)
    if proposition_id:
        if not re.fullmatch(r"MI-\d{4}", proposition_id):
            raise ContinuityError("proposition_id must match MI-NNNN")
        versions = [int(item.get("version", 0)) for item in entries if item.get("proposition_id") == proposition_id]
        return proposition_id, max(versions, default=0) + 1
    numbers = [int(str(item.get("proposition_id", "MI-0000")).split("-")[-1]) for item in entries]
    return f"MI-{max(numbers, default=0) + 1:04d}", 1


def command_identity_promote(args: argparse.Namespace) -> int:
    registry = load_registry()
    ledger = load_json(IDENTITY_LEDGER_PATH)
    candidate = sanitize_value(load_json(Path(args.input)))
    proposition_id, version = _next_identity_id(ledger, candidate)
    candidate.update(
        {
            "id": f"{proposition_id}-v{version}",
            "proposition_id": proposition_id,
            "version": version,
        }
    )
    combined = copy.deepcopy(ledger)
    if version > 1:
        for entry in combined.get("entries", []):
            if entry.get("proposition_id") == proposition_id and entry.get("lifecycle") == "current":
                entry["lifecycle"] = "superseded"
    combined.setdefault("entries", []).append(candidate)
    failures = validate_identity(combined, session_ids=set(_session_map(registry)))
    if failures:
        _format_report({"mira_identity_promotion": "invalid", "failures": failures}, args.format)
        return 1
    if args.check:
        _format_report({"mira_identity_promotion": "valid", "id": candidate["id"]}, args.format)
        return 0
    write_text(IDENTITY_LEDGER_PATH, pretty_json(combined))
    render_views(check=False)
    _format_report({"mira_identity_promotion": "written", "id": candidate["id"]}, args.format)
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Govern Mira session continuity and operator-approved identity.")
    subparsers = value.add_subparsers(dest="command", required=True)

    discover = subparsers.add_parser("discover", help="Discover qualifying current-repository Codex sessions.")
    discover.add_argument("--source-root", action="append", default=[])
    discover.add_argument("--format", choices=("text", "json"), default="text")
    discover.set_defaults(handler=command_discover)

    ingest = subparsers.add_parser("ingest", help="Normalize and append immutable session captures.")
    ingest.add_argument("--source-root", action="append", default=[])
    ingest.add_argument("--check", action="store_true")
    ingest.add_argument("--format", choices=("text", "json"), default="text")
    ingest.set_defaults(handler=command_ingest)

    validate = subparsers.add_parser("validate", help="Validate all canonical Mira continuity surfaces.")
    validate.add_argument("--format", choices=("text", "json"), default="text")
    validate.set_defaults(handler=command_validate)

    recover = subparsers.add_parser("recover", help="Verify recovery from the exact staged Git index.")
    recover.add_argument("--contract", choices=tuple(sorted(RECOVERY_CONTRACTS)), required=True)
    recover.add_argument("--staged", action="store_true", required=True)
    recover.add_argument("--check", action="store_true")
    recover.add_argument("--temp-root")
    recover.add_argument("--receipt-root")
    recover.add_argument("--format", choices=("text", "json"), default="text")
    recover.set_defaults(handler=command_recover)

    privacy = subparsers.add_parser("privacy-audit", help="Scan captures without emitting matched private content.")
    privacy.add_argument("--contract", choices=("stage1-v1",), required=True)
    privacy_mode = privacy.add_mutually_exclusive_group(required=True)
    privacy_mode.add_argument("--check", action="store_true")
    privacy_mode.add_argument("--prepare", action="store_true")
    privacy_mode.add_argument("--finalize", action="store_true")
    privacy.add_argument("--sample-size", type=int, default=20)
    privacy.add_argument("--private-root")
    privacy.add_argument("--review-decisions")
    privacy.add_argument("--receipt-root")
    privacy.add_argument("--format", choices=("text", "json"), default="text")
    privacy.set_defaults(handler=command_privacy_audit)

    render = subparsers.add_parser("render", help="Render identity, trajectory, and activation views.")
    render.add_argument("--check", action="store_true")
    render.add_argument("--format", choices=("text", "json"), default="text")
    render.set_defaults(handler=command_render)

    activate = subparsers.add_parser("activate", help="Print the bounded current activation briefing.")
    activate.set_defaults(handler=command_activate)

    deepen = subparsers.add_parser("deepen", help="Register an operator-reviewed selective harvest packet.")
    deepen.add_argument("--session", required=True)
    deepen.add_argument("--input", required=True)
    deepen.add_argument("--check", action="store_true")
    deepen.add_argument("--format", choices=("text", "json"), default="text")
    deepen.set_defaults(handler=command_deepen)

    identity = subparsers.add_parser("identity", help="Manage operator-approved identity propositions.")
    identity_subparsers = identity.add_subparsers(dest="identity_command", required=True)
    promote = identity_subparsers.add_parser("promote", help="Validate or promote an identity proposition.")
    promote.add_argument("--input", required=True)
    promote.add_argument("--check", action="store_true")
    promote.add_argument("--format", choices=("text", "json"), default="text")
    promote.set_defaults(handler=command_identity_promote)
    return value


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    try:
        return args.handler(args)
    except (ContinuityError, OSError) as error:
        print(f"mira continuity error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

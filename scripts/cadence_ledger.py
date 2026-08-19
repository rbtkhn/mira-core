from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from runtime_names import resolve_environment
from portable_paths import PortablePathError, require_private_path as portable_private_path


REPO_ROOT = Path(__file__).resolve().parent.parent
DB_ENV = "MIRA_CORE_CADENCE_DB"
DEFAULT_DB_PATH = REPO_ROOT / ".mira-private" / "state" / "cadence.sqlite3"
SCHEMA_VERSION = 4
PROJECTION_VERSION = "1.2"
SQLITE_HEADER = b"SQLite format 3\x00"
TERMINAL_STATES = frozenset({"rejected", "superseded", "expired"})
DISPOSITIONS = frozenset({"inherit", "retest", "reconcile", *TERMINAL_STATES})
RELATIONSHIPS = frozenset(
    {"behavior-observation", "implementation", "verification", "later-use"}
)
TARGET_TYPES = frozenset(
    {"artifact", "forecast", "crisis_object", "observable", "method_change", "presentation_context"}
)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<![\w-])(?:\+?\d[\d ()-]{7,}\d)(?![\w-])")
SECRET_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*\S+"
)


class CadenceLedgerError(ValueError):
    pass


@dataclass(frozen=True)
class StoreResolution:
    path: Path | None
    reason: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise CadenceLedgerError(f"invalid timestamp: {value}") from error
    if parsed.tzinfo is None:
        raise CadenceLedgerError("timestamps must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat()


def timestamp_us(value: str) -> int:
    parsed = datetime.fromisoformat(validate_timestamp(value))
    return int(parsed.timestamp() * 1_000_000)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    raw = value if isinstance(value, str) else canonical_json(value)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def sanitize_text(value: Any, *, limit: int = 4000) -> str:
    text = CONTROL_RE.sub("", str(value)).strip()
    if not text:
        raise CadenceLedgerError("cadence text must not be empty")
    if SECRET_RE.search(text):
        raise CadenceLedgerError("cadence data appears to contain a credential or secret")
    text = EMAIL_RE.sub("[redacted-contact]", text)
    text = PHONE_RE.sub("[redacted-contact]", text)
    if len(text) > limit:
        raise CadenceLedgerError(f"cadence text exceeds {limit} characters")
    return text


def sanitize_artifact_ref(value: Any, *, limit: int = 1000) -> str:
    text = CONTROL_RE.sub("", str(value)).strip().replace("\\", "/")
    if not text:
        raise CadenceLedgerError("cadence artifact reference must not be empty")
    if SECRET_RE.search(text):
        raise CadenceLedgerError("cadence artifact reference appears to contain a credential or secret")
    if EMAIL_RE.search(text):
        raise CadenceLedgerError("cadence artifact reference appears to contain contact data")
    path = Path(text)
    if path.is_absolute() or ".." in path.parts:
        raise CadenceLedgerError("cadence artifact reference must be repository-relative")
    if len(text) > limit:
        raise CadenceLedgerError(f"cadence artifact reference exceeds {limit} characters")
    return text


def require_private_path(raw: str | Path, *, label: str) -> Path:
    try:
        return portable_private_path(raw, label=label, repo_root=REPO_ROOT)
    except PortablePathError as error:
        raise CadenceLedgerError(str(error)) from error


def resolve_store(raw: str | Path | None, *, require_exists: bool = False) -> StoreResolution:
    configured = raw or resolve_environment(DB_ENV) or DEFAULT_DB_PATH
    try:
        path = require_private_path(configured, label="private cadence store")
    except CadenceLedgerError as error:
        return StoreResolution(None, str(error))
    if require_exists and not path.is_file():
        return StoreResolution(None, f"private cadence store does not exist: {path}")
    return StoreResolution(path)


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5.0)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        mode = connection.execute("PRAGMA journal_mode = DELETE").fetchone()[0]
        if str(mode).lower() != "delete":
            raise sqlite3.OperationalError("cadence store could not enter rollback-journal mode")
        connection.execute("PRAGMA synchronous = FULL")
        migrate(connection)
    except (CadenceLedgerError, sqlite3.Error):
        connection.close()
        raise
    return connection


def connect_read_only(path: Path) -> sqlite3.Connection:
    with path.open("rb") as stream:
        if stream.read(16) != SQLITE_HEADER:
            raise sqlite3.DatabaseError("cadence store has an invalid SQLite header")
    connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True, timeout=5.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA query_only = ON")
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if version not in {2, 3, SCHEMA_VERSION}:
        connection.close()
        raise CadenceLedgerError(
            f"cadence store schema {version} is not readable; supported versions are 2, 3, and {SCHEMA_VERSION}"
        )
    return connection


def table_exists(connection: sqlite3.Connection, name: str) -> bool:
    return connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def migrate(connection: sqlite3.Connection) -> None:
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if version > SCHEMA_VERSION:
        raise CadenceLedgerError(f"cadence store schema {version} is newer than supported")
    if version == 0:
        with connection:
            connection.executescript(
                """
                CREATE TABLE cadence_episodes (
                    episode_id TEXT PRIMARY KEY,
                    series_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    created_at_utc_us INTEGER NOT NULL,
                    lifecycle_version INTEGER NOT NULL DEFAULT 0,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    relevant_digest TEXT NOT NULL,
                    historical_completeness TEXT NOT NULL DEFAULT 'complete'
                );
                CREATE INDEX cadence_episode_order
                    ON cadence_episodes(created_at_utc_us, episode_id);
                CREATE TABLE cadence_events (
                    event_id TEXT PRIMARY KEY,
                    episode_id TEXT NOT NULL REFERENCES cadence_episodes(episode_id),
                    event_type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    occurred_at_utc_us INTEGER NOT NULL,
                    lifecycle_version INTEGER NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    payload_json TEXT NOT NULL,
                    previous_event_sha256 TEXT,
                    event_sha256 TEXT NOT NULL
                );
                CREATE INDEX cadence_event_order
                    ON cadence_events(episode_id, occurred_at_utc_us, event_id);
                ALTER TABLE cadence_episodes ADD COLUMN workspace_id TEXT;
                ALTER TABLE cadence_episodes ADD COLUMN operator_id TEXT;
                ALTER TABLE cadence_episodes ADD COLUMN dream_date TEXT;
                CREATE UNIQUE INDEX cadence_daily_dream
                    ON cadence_episodes(workspace_id, operator_id, dream_date)
                    WHERE workspace_id IS NOT NULL AND operator_id IS NOT NULL AND dream_date IS NOT NULL;
                PRAGMA user_version = 2;
                """
            )
        version = 2
    if version == 1:
        with connection:
            connection.executescript(
                """
                ALTER TABLE cadence_episodes ADD COLUMN workspace_id TEXT;
                ALTER TABLE cadence_episodes ADD COLUMN operator_id TEXT;
                ALTER TABLE cadence_episodes ADD COLUMN dream_date TEXT;
                CREATE UNIQUE INDEX cadence_daily_dream
                    ON cadence_episodes(workspace_id, operator_id, dream_date)
                    WHERE workspace_id IS NOT NULL AND operator_id IS NOT NULL AND dream_date IS NOT NULL;
                PRAGMA user_version = 2;
                """
            )
        version = 2
    if version == 2:
        with connection:
            connection.executescript(
                """
                CREATE TABLE daily_close_runs (
                    run_id TEXT PRIMARY KEY,
                    workspace_id TEXT NOT NULL,
                    operator_id TEXT NOT NULL,
                    close_date TEXT NOT NULL,
                    timezone TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    created_at_utc_us INTEGER NOT NULL,
                    lifecycle_version INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(workspace_id, operator_id, close_date)
                );
                CREATE TABLE daily_close_events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES daily_close_runs(run_id),
                    event_type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    occurred_at_utc_us INTEGER NOT NULL,
                    lifecycle_version INTEGER NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    payload_json TEXT NOT NULL,
                    previous_event_sha256 TEXT,
                    event_sha256 TEXT NOT NULL
                );
                CREATE INDEX daily_close_event_order
                    ON daily_close_events(run_id, occurred_at_utc_us, event_id);
                CREATE TABLE daily_dream_closeouts (
                    closeout_id TEXT PRIMARY KEY,
                    workspace_id TEXT NOT NULL,
                    operator_id TEXT NOT NULL,
                    dream_date TEXT NOT NULL,
                    timezone TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    occurred_at_utc_us INTEGER NOT NULL,
                    coverage_status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    UNIQUE(workspace_id, operator_id, dream_date)
                );
                PRAGMA user_version = 3;
                """
            )
        version = 3
    if version == 3:
        with connection:
            connection.executescript(
                """
                CREATE TABLE coffee_presentations (
                    presentation_id TEXT PRIMARY KEY,
                    episode_id TEXT REFERENCES cadence_episodes(episode_id),
                    workspace_id TEXT NOT NULL,
                    operator_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    occurred_at_utc_us INTEGER NOT NULL,
                    lifecycle_version INTEGER,
                    presentation_mode TEXT NOT NULL,
                    repeat_depth INTEGER NOT NULL,
                    context_components_json TEXT NOT NULL,
                    context_digest TEXT NOT NULL,
                    menu_digest TEXT NOT NULL,
                    prior_presentation_id TEXT REFERENCES coffee_presentations(presentation_id),
                    previous_receipt_sha256 TEXT,
                    receipt_sha256 TEXT NOT NULL
                );
                CREATE INDEX coffee_presentation_order
                    ON coffee_presentations(workspace_id, operator_id, episode_id,
                                            occurred_at_utc_us, presentation_id);
                PRAGMA user_version = 4;
                """
            )


DAILY_CLOSE_STAGES = ("geo", "journal", "dream")


def _close_event_rows(connection: sqlite3.Connection, run_id: str) -> list[sqlite3.Row]:
    return list(connection.execute(
        "SELECT * FROM daily_close_events WHERE run_id=? ORDER BY occurred_at_utc_us, event_id",
        (run_id,),
    ))


def project_daily_close(connection: sqlite3.Connection, run_id: str) -> dict[str, Any]:
    row = connection.execute("SELECT * FROM daily_close_runs WHERE run_id=?", (run_id,)).fetchone()
    if row is None:
        raise CadenceLedgerError(f"unknown daily close run: {run_id}")
    stages = {stage: "pending" for stage in DAILY_CLOSE_STAGES}
    events = []
    for event in _close_event_rows(connection, run_id):
        payload = json.loads(event["payload_json"])
        events.append({"event_id": event["event_id"], "event_type": event["event_type"],
                       "occurred_at": event["occurred_at"], "lifecycle_version": event["lifecycle_version"],
                       "payload": payload, "event_sha256": event["event_sha256"]})
        stage = payload.get("stage")
        if stage in stages:
            stages[stage] = {"stage_completed": "completed", "stage_skipped": "skipped",
                             "stage_failed": "failed"}.get(event["event_type"], stages[stage])
    return {"schema_version": 1, "run_id": run_id, "workspace_id": row["workspace_id"],
            "operator_id": row["operator_id"], "close_date": row["close_date"],
            "timezone": row["timezone"], "created_at": row["created_at"],
            "lifecycle_version": row["lifecycle_version"],
            "state": "completed" if any(e["event_type"] == "daily_close_completed" for e in events) else "open",
            "stages": stages, "events": events}


def append_daily_close_event(connection: sqlite3.Connection, run_id: str, event_type: str,
                             payload: dict[str, Any], *, idempotency_key: str,
                             expected_version: int, in_transaction: bool = False) -> dict[str, Any]:
    duplicate = connection.execute("SELECT run_id FROM daily_close_events WHERE idempotency_key=?", (idempotency_key,)).fetchone()
    if duplicate:
        if duplicate["run_id"] != run_id:
            raise CadenceLedgerError("daily close idempotency key belongs to another run")
        return project_daily_close(connection, run_id)
    current = connection.execute("SELECT lifecycle_version FROM daily_close_runs WHERE run_id=?", (run_id,)).fetchone()
    if current is None or int(current[0]) != expected_version:
        found = "missing" if current is None else str(current[0])
        raise CadenceLedgerError(f"daily close lifecycle conflict: expected {expected_version}, found {found}")
    allowed = {"daily_close_opened", "stage_completed", "stage_skipped", "stage_failed",
               "daily_close_completed", "daily_close_superseded"}
    if event_type not in allowed:
        raise CadenceLedgerError(f"unsupported daily close event: {event_type}")
    clean = {}
    for key, value in payload.items():
        if key == "artifact_ref":
            clean[key] = sanitize_artifact_ref(value)
        elif key in {"stage", "status", "reason", "digest", "coverage_status",
                   "episode_id", "closeout_id", "journal_version_id", "technical_reference_id",
                   "technical_reference_digest", "validated_at", "validation_status",
                   "approval_status", "commit", "validation_stage", "certification_basis"}:
            clean[key] = sanitize_text(value, limit=1000)
        elif key == "canonicalized" and isinstance(value, bool):
            clean[key] = value
    if clean.get("stage") and clean["stage"] not in DAILY_CLOSE_STAGES:
        raise CadenceLedgerError("daily close event has invalid stage")
    previous = connection.execute(
        "SELECT event_sha256 FROM daily_close_events WHERE run_id=? ORDER BY occurred_at_utc_us DESC, event_id DESC LIMIT 1",
        (run_id,),
    ).fetchone()
    now = utc_now()
    next_version = expected_version + 1
    event_id = f"DCE-{uuid.uuid4()}"
    body = {"event_id": event_id, "run_id": run_id, "event_type": event_type,
            "occurred_at": now, "lifecycle_version": next_version, "payload": clean,
            "previous_event_sha256": previous[0] if previous else None}
    def write() -> None:
        connection.execute(
            "INSERT INTO daily_close_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (event_id, run_id, event_type, now, timestamp_us(now), next_version, idempotency_key,
             canonical_json(clean), body["previous_event_sha256"], digest(body)),
        )
        connection.execute("UPDATE daily_close_runs SET lifecycle_version=? WHERE run_id=?", (next_version, run_id))
    if in_transaction:
        write()
    else:
        with connection:
            write()
    return project_daily_close(connection, run_id)


def open_daily_close(connection: sqlite3.Connection, *, run_id: str, workspace_id: str,
                     operator_id: str, close_date: str, timezone_name: str,
                     idempotency_key: str) -> dict[str, Any]:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", close_date):
        raise CadenceLedgerError("daily close date must use YYYY-MM-DD")
    values = tuple(sanitize_text(v, limit=200) for v in (run_id, workspace_id, operator_id, timezone_name))
    existing = connection.execute(
        "SELECT run_id FROM daily_close_runs WHERE workspace_id=? AND operator_id=? AND close_date=?",
        (values[1], values[2], close_date),
    ).fetchone()
    if existing:
        return project_daily_close(connection, str(existing["run_id"]))
    now = utc_now()
    with connection:
        connection.execute("INSERT INTO daily_close_runs VALUES (?, ?, ?, ?, ?, ?, ?, 0)",
                           (values[0], values[1], values[2], close_date, values[3], now, timestamp_us(now)))
        append_daily_close_event(connection, values[0], "daily_close_opened", {},
                                 idempotency_key=idempotency_key, expected_version=0, in_transaction=True)
    return project_daily_close(connection, values[0])


def record_dream_closeout(connection: sqlite3.Connection, payload: dict[str, Any], *, idempotency_key: str) -> dict[str, Any]:
    required = ("closeout_id", "workspace_id", "operator_id", "dream_date", "timezone", "coverage_status")
    if any(not str(payload.get(key, "")).strip() for key in required):
        raise CadenceLedgerError("Dream closeout is incomplete")
    if payload["coverage_status"] not in {"complete", "partial"}:
        raise CadenceLedgerError("Dream closeout coverage_status must be complete or partial")
    clean = {key: sanitize_text(payload[key], limit=1000) for key in required}
    for key in ("reason", "session_coverage_digest"):
        if payload.get(key):
            clean[key] = sanitize_text(payload[key], limit=1000)
    clean["disposition"] = "no_cadence_worthy_experiment"
    candidate = connection.execute(
        "SELECT episode_id FROM cadence_episodes WHERE workspace_id=? AND operator_id=? AND dream_date=?",
        (clean["workspace_id"], clean["operator_id"], clean["dream_date"]),
    ).fetchone()
    if candidate:
        raise CadenceLedgerError(f"daily Dream already has a candidate: {candidate['episode_id']}")
    existing = connection.execute(
        "SELECT payload_json FROM daily_dream_closeouts WHERE workspace_id=? AND operator_id=? AND dream_date=?",
        (clean["workspace_id"], clean["operator_id"], clean["dream_date"]),
    ).fetchone()
    if existing:
        if json.loads(existing[0]) == clean:
            return clean
        raise CadenceLedgerError("daily Dream already has a different closeout")
    now = utc_now()
    with connection:
        connection.execute(
            "INSERT INTO daily_dream_closeouts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (clean["closeout_id"], clean["workspace_id"], clean["operator_id"], clean["dream_date"],
             clean["timezone"], now, timestamp_us(now), clean["coverage_status"], canonical_json(clean),
             digest(clean), idempotency_key),
        )
    return clean


def normalize_repo_ref(value: str) -> str:
    ref = sanitize_artifact_ref(value, limit=500)
    path_text = ref.split("#", 1)[0]
    candidate = Path(path_text)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise CadenceLedgerError(f"artifact reference must be repository-relative: {value}")
    resolved = (REPO_ROOT / candidate).resolve()
    if not resolved.is_relative_to(REPO_ROOT.resolve()) or not resolved.exists():
        raise CadenceLedgerError(f"artifact reference does not resolve: {value}")
    return ref


def content_digest(refs: Iterable[str]) -> str:
    rows: list[dict[str, Any]] = []
    for ref in sorted(set(refs)):
        normalized = normalize_repo_ref(ref)
        path = REPO_ROOT / normalized.split("#", 1)[0]
        if path.is_file():
            rows.append({"path": normalized, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        else:
            children = []
            for child in sorted(item for item in path.rglob("*") if item.is_file()):
                if any(part in {".git", "__pycache__", ".pytest_cache"} for part in child.parts):
                    continue
                children.append(
                    {
                        "path": child.relative_to(REPO_ROOT).as_posix(),
                        "sha256": hashlib.sha256(child.read_bytes()).hexdigest(),
                    }
                )
            rows.append({"path": normalized, "children": children})
    return digest(rows)


def normalize_artifacts(values: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for item in values:
        relationship = str(item.get("relationship", ""))
        if relationship not in RELATIONSHIPS:
            raise CadenceLedgerError(f"invalid artifact relationship: {relationship}")
        result.append(
            {
                "ref": normalize_repo_ref(str(item.get("ref", ""))),
                "relationship": relationship,
                "captured_at": validate_timestamp(str(item.get("captured_at", ""))),
            }
        )
    if not result or len(result) > 20:
        raise CadenceLedgerError("cadence episode requires 1-20 artifact references")
    return result


def normalize_closure_metadata(receipt: dict[str, Any]) -> dict[str, Any]:
    supplied = any(key in receipt for key in ("closure_state", "rest_event_refs", "closure_observed_at"))
    if not supplied:
        return {}
    state = str(receipt.get("closure_state", ""))
    if state not in {"active", "rested", "resumed", "unavailable"}:
        raise CadenceLedgerError("invalid session closure state")
    raw_refs = receipt.get("rest_event_refs", [])
    if not isinstance(raw_refs, list) or any(
        not re.fullmatch(r"RSTE-[0-9a-f]{24}", str(value)) for value in raw_refs
    ):
        raise CadenceLedgerError("invalid Rest event reference")
    observed = receipt.get("closure_observed_at")
    return {
        "closure_state": state,
        "rest_event_refs": sorted(set(map(str, raw_refs))),
        "closure_observed_at": validate_timestamp(str(observed)) if observed else None,
    }


def normalize_episode(raw: dict[str, Any]) -> dict[str, Any]:
    episode_id = sanitize_text(raw.get("episode_id", ""), limit=100)
    series_id = sanitize_text(raw.get("series_id", ""), limit=100)
    artifacts = normalize_artifacts(raw.get("artifacts", []))
    relevant_paths = [normalize_repo_ref(str(item)) for item in raw.get("relevant_paths", [])]
    if not relevant_paths or len(relevant_paths) > 30:
        raise CadenceLedgerError("cadence episode requires 1-30 relevant paths")
    observable = raw.get("observable")
    if not isinstance(observable, dict):
        raise CadenceLedgerError("observable must be an object")
    profile = raw.get("profile") or {}
    raw_created_at = str(raw.get("created_at") or utc_now())
    try:
        created_with_local_offset = datetime.fromisoformat(raw_created_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise CadenceLedgerError(f"invalid timestamp: {raw_created_at}") from error
    if created_with_local_offset.tzinfo is None:
        raise CadenceLedgerError("timestamps must include a timezone")
    created_at = validate_timestamp(raw_created_at)
    workspace_id = sanitize_text(raw.get("workspace_id", ""), limit=200)
    operator_id = sanitize_text(raw.get("operator_id", ""), limit=200)
    dream_date = str(raw.get("dream_date", "")).strip()
    timezone_name = sanitize_text(raw.get("timezone", ""), limit=100)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", dream_date):
        raise CadenceLedgerError("dream_date must use YYYY-MM-DD")
    if timezone_name != "UTC" and not re.fullmatch(r"[A-Za-z_+-]+/[A-Za-z0-9_+.-]+", timezone_name):
        raise CadenceLedgerError("Dream timezone must be UTC or an IANA timezone name")
    created_local_date = created_with_local_offset.date().isoformat()
    if created_local_date != dream_date:
        raise CadenceLedgerError("dream_date must match created_at in the named timezone")
    raw_coverage = raw.get("session_coverage")
    if not isinstance(raw_coverage, list) or not raw_coverage or len(raw_coverage) > 100:
        raise CadenceLedgerError("daily Dream requires 1-100 session coverage receipts")
    session_coverage = []
    seen_sessions: set[str] = set()
    for receipt in raw_coverage:
        if not isinstance(receipt, dict):
            raise CadenceLedgerError("session coverage receipts must be objects")
        session_id = sanitize_text(receipt.get("session_id", ""), limit=200)
        if session_id in seen_sessions:
            raise CadenceLedgerError(f"duplicate session coverage receipt: {session_id}")
        seen_sessions.add(session_id)
        status = str(receipt.get("status", ""))
        if status not in {"included", "excluded", "unavailable"}:
            raise CadenceLedgerError(f"invalid session coverage status: {status}")
        session_coverage.append({
            "session_id": session_id,
            "status": status,
            "reason": sanitize_text(receipt.get("reason", ""), limit=1000),
            "observed_at": validate_timestamp(str(receipt.get("observed_at", ""))),
            **normalize_closure_metadata(receipt),
        })
    coverage_status = str(raw.get("coverage_status", ""))
    expected_coverage = (
        "complete" if all(item["status"] != "unavailable" for item in session_coverage)
        else "partial"
    )
    if coverage_status != expected_coverage:
        raise CadenceLedgerError(f"coverage_status must be {expected_coverage} for supplied receipts")
    expires_at = validate_timestamp(str(raw.get("expires_at", "")))
    if timestamp_us(expires_at) <= timestamp_us(created_at):
        raise CadenceLedgerError("expiry must follow episode creation")
    payload = {
        "schema_version": 1,
        "episode_id": episode_id,
        "series_id": series_id,
        "created_at": created_at,
        "workspace_id": workspace_id,
        "operator_id": operator_id,
        "dream_date": dream_date,
        "timezone": timezone_name,
        "coverage_status": coverage_status,
        "session_coverage": session_coverage,
        "observation": sanitize_text(raw.get("observation", "")),
        "diagnosis": sanitize_text(raw.get("diagnosis", "")),
        "intervention": sanitize_text(raw.get("intervention", "")),
        "method_version_digest": sanitize_text(raw.get("method_version_digest", ""), limit=128),
        "intervention_commits": [
            sanitize_text(value, limit=40)
            for value in raw.get("intervention_commits", [])
            if re.fullmatch(r"[0-9a-f]{7,40}", str(value))
        ],
        "profile": {
            "name": sanitize_text(profile.get("name", "unprofiled"), limit=100),
            "version": sanitize_text(profile.get("version", "none"), limit=100),
            "command_digest": sanitize_text(profile.get("command_digest", "none"), limit=128),
        },
        "observable": {
            "name": sanitize_text(observable.get("name", ""), limit=200),
            "unit": sanitize_text(observable.get("unit", ""), limit=100),
            "baseline": sanitize_text(observable.get("baseline", ""), limit=500),
            "success_threshold": sanitize_text(observable.get("success_threshold", ""), limit=500),
            "source": sanitize_text(observable.get("source", ""), limit=500),
        },
        "falsifier": sanitize_text(raw.get("falsifier", "")),
        "next_use": sanitize_text(raw.get("next_use", ""), limit=1000),
        "task_class": sanitize_text(raw.get("task_class", ""), limit=200),
        "expires_at": expires_at,
        "artifacts": artifacts,
        "relevant_paths": sorted(set(relevant_paths)),
        "evidence_summary": sanitize_text(raw.get("evidence_summary", "")),
        "tomorrow_inherits": sanitize_text(raw.get("tomorrow_inherits", "")),
        "verification": raw.get("verification") if isinstance(raw.get("verification"), dict) else {},
        "measurements": raw.get("measurements") if isinstance(raw.get("measurements"), dict) else {},
    }
    if len(canonical_json(payload)) > 50_000:
        raise CadenceLedgerError("cadence episode exceeds 50000 serialized characters")
    return payload


def create_episode(
    connection: sqlite3.Connection,
    raw: dict[str, Any],
    *,
    idempotency_key: str,
    historical_completeness: str = "complete",
) -> dict[str, Any]:
    receipt = connection.execute(
        "SELECT episode_id FROM cadence_events WHERE idempotency_key = ?",
        (idempotency_key,),
    ).fetchone()
    if receipt:
        return project_episode(connection, str(receipt["episode_id"]))
    payload = normalize_episode(raw)
    existing = connection.execute(
        "SELECT payload_json FROM cadence_episodes WHERE episode_id = ?", (payload["episode_id"],)
    ).fetchone()
    if existing:
        if json.loads(existing[0]) == payload:
            return project_episode(connection, payload["episode_id"])
        raise CadenceLedgerError(f"episode already exists with different content: {payload['episode_id']}")
    daily = connection.execute(
        """SELECT episode_id FROM cadence_episodes
           WHERE workspace_id = ? AND operator_id = ? AND dream_date = ?""",
        (payload["workspace_id"], payload["operator_id"], payload["dream_date"]),
    ).fetchone()
    if daily:
        raise CadenceLedgerError(
            "daily Dream already exists for workspace, operator, and local date: "
            f"{daily['episode_id']}"
        )
    closeout = connection.execute(
        "SELECT closeout_id FROM daily_dream_closeouts WHERE workspace_id=? AND operator_id=? AND dream_date=?",
        (payload["workspace_id"], payload["operator_id"], payload["dream_date"]),
    ).fetchone()
    if closeout:
        raise CadenceLedgerError(f"daily Dream already has a no-candidate closeout: {closeout['closeout_id']}")
    relevant = content_digest(payload["relevant_paths"])
    with connection:
        connection.execute(
            """INSERT INTO cadence_episodes
               (episode_id, series_id, created_at, created_at_utc_us, lifecycle_version,
                payload_json, payload_sha256, relevant_digest, historical_completeness,
                workspace_id, operator_id, dream_date)
               VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?)""",
            (
                payload["episode_id"], payload["series_id"], payload["created_at"],
                timestamp_us(payload["created_at"]), canonical_json(payload), digest(payload),
                relevant, historical_completeness, payload["workspace_id"],
                payload["operator_id"], payload["dream_date"],
            ),
        )
        append_event(
            connection, payload["episode_id"], "candidate_created", {},
            idempotency_key=idempotency_key, expected_version=0, in_transaction=True,
        )
    return project_episode(connection, payload["episode_id"])


def append_session_supplement(
    connection: sqlite3.Connection,
    episode_id: str,
    receipt: dict[str, Any],
    *,
    idempotency_key: str,
    expected_version: int,
) -> dict[str, Any]:
    if not isinstance(receipt, dict):
        raise CadenceLedgerError("session supplement must be an object")
    normalized = {
        "session_id": sanitize_text(receipt.get("session_id", ""), limit=200),
        "status": str(receipt.get("status", "")),
        "reason": sanitize_text(receipt.get("reason", ""), limit=1000),
        "observed_at": validate_timestamp(str(receipt.get("observed_at", ""))),
        **normalize_closure_metadata(receipt),
    }
    if normalized["status"] not in {"included", "excluded", "unavailable"}:
        raise CadenceLedgerError(f"invalid session coverage status: {normalized['status']}")
    projection = project_episode(connection, episode_id)
    known = {row["session_id"] for row in projection["episode"]["session_coverage"]}
    known.update(
        event["payload"].get("session_id")
        for event in projection["events"]
        if event["event_type"] == "session_coverage_supplemented"
    )
    if normalized["session_id"] in known:
        raise CadenceLedgerError("session coverage already exists; supersede explicitly instead of rewriting it")
    return append_event(
        connection, episode_id, "session_coverage_supplemented", normalized,
        idempotency_key=idempotency_key, expected_version=expected_version,
    )


def event_rows(connection: sqlite3.Connection, episode_id: str) -> list[sqlite3.Row]:
    return list(
        connection.execute(
            "SELECT * FROM cadence_events WHERE episode_id = ? ORDER BY occurred_at_utc_us, event_id",
            (episode_id,),
        )
    )


def append_event(
    connection: sqlite3.Connection,
    episode_id: str,
    event_type: str,
    payload: dict[str, Any],
    *,
    idempotency_key: str,
    expected_version: int,
    occurred_at: str | None = None,
    in_transaction: bool = False,
) -> dict[str, Any]:
    duplicate = connection.execute(
        "SELECT episode_id, event_sha256 FROM cadence_events WHERE idempotency_key = ?",
        (idempotency_key,),
    ).fetchone()
    if duplicate:
        if duplicate["episode_id"] != episode_id:
            raise CadenceLedgerError("idempotency key is already bound to another episode")
        return project_episode(connection, episode_id)
    row = connection.execute(
        "SELECT lifecycle_version FROM cadence_episodes WHERE episode_id = ?", (episode_id,)
    ).fetchone()
    if not row:
        raise CadenceLedgerError(f"unknown cadence episode: {episode_id}")
    if int(row[0]) != expected_version:
        raise CadenceLedgerError(
            f"lifecycle version changed: expected {expected_version}, found {row[0]}"
        )
    prior = event_rows(connection, episode_id)
    if prior and projected_state(prior) in TERMINAL_STATES and event_type != "superseded":
        raise CadenceLedgerError("terminal cadence episode requires an explicit superseding event")
    version = expected_version + 1
    when = validate_timestamp(occurred_at or utc_now())
    event_id = f"CE-{uuid.uuid4().hex}"
    previous = prior[-1]["event_sha256"] if prior else None
    body = {
        "event_id": event_id,
        "episode_id": episode_id,
        "event_type": event_type,
        "occurred_at": when,
        "lifecycle_version": version,
        "payload": payload,
        "previous_event_sha256": previous,
    }
    event_sha = digest(body)
    def write() -> None:
        connection.execute(
            "INSERT INTO cadence_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                event_id, episode_id, event_type, when, timestamp_us(when), version,
                idempotency_key, canonical_json(payload), previous, event_sha,
            ),
        )
        changed = connection.execute(
            "UPDATE cadence_episodes SET lifecycle_version = ? WHERE episode_id = ? AND lifecycle_version = ?",
            (version, episode_id, expected_version),
        )
        if changed.rowcount != 1:
            raise CadenceLedgerError("concurrent cadence lifecycle update detected")
    if in_transaction:
        write()
    else:
        with connection:
            write()
    return project_episode(connection, episode_id)


def projected_state(rows: Iterable[sqlite3.Row | dict[str, Any]]) -> str:
    state = "candidate"
    for row in rows:
        event_type = row["event_type"]
        payload = json.loads(row["payload_json"]) if "payload_json" in row.keys() else row.get("payload", {})
        if event_type == "verification_completed" and payload.get("passed") is True:
            state = "locally_verified"
        elif event_type == "disposition":
            state = {"inherit": "inherited"}.get(payload.get("decision"), payload.get("decision", state))
        elif event_type == "repetition_recorded":
            state = "repeated"
        elif event_type == "represented":
            state = "represented"
    return state


def project_episode(connection: sqlite3.Connection, episode_id: str) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM cadence_episodes WHERE episode_id = ?", (episode_id,)
    ).fetchone()
    if not row:
        raise CadenceLedgerError(f"unknown cadence episode: {episode_id}")
    events = event_rows(connection, episode_id)
    return {
        "episode": json.loads(row["payload_json"]),
        "lifecycle_state": projected_state(events),
        "lifecycle_version": row["lifecycle_version"],
        "relevant_digest": row["relevant_digest"],
        "historical_completeness": row["historical_completeness"],
        "events": [
            {
                "event_id": event["event_id"], "event_type": event["event_type"],
                "occurred_at": event["occurred_at"], "lifecycle_version": event["lifecycle_version"],
                "payload": json.loads(event["payload_json"]), "event_sha256": event["event_sha256"],
                "previous_event_sha256": event["previous_event_sha256"],
            }
            for event in events
        ],
        "event_chain_digest": events[-1]["event_sha256"] if events else None,
    }


def list_history(connection: sqlite3.Connection, *, limit: int = 50) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT episode_id FROM cadence_episodes ORDER BY created_at_utc_us DESC, episode_id DESC LIMIT ?",
        (max(1, min(limit, 200)),),
    )
    return [project_episode(connection, row[0]) for row in rows]


def episode_is_eligible(projection: dict[str, Any], *, now_utc_us: int | None = None) -> bool:
    observed_now = timestamp_us(utc_now()) if now_utc_us is None else now_utc_us
    expired = timestamp_us(projection["episode"]["expires_at"]) <= observed_now
    return not expired and projection["lifecycle_state"] not in TERMINAL_STATES | {"represented"}


def selected_episode(connection: sqlite3.Connection, episode_id: str | None = None) -> dict[str, Any] | None:
    history = list_history(connection, limit=200)
    observed_now = timestamp_us(utc_now())
    if episode_id:
        selected = project_episode(connection, episode_id)
        selected_episode_data = selected["episode"]
        for item in history:
            candidate = item["episode"]
            if candidate["episode_id"] == episode_id:
                break
            same_scope = (
                candidate["workspace_id"] == selected_episode_data["workspace_id"]
                and candidate["operator_id"] == selected_episode_data["operator_id"]
            )
            if same_scope and episode_is_eligible(item, now_utc_us=observed_now):
                raise CadenceLedgerError(
                    f"Coffee episode {episode_id} is stale; newer eligible episode "
                    f"{candidate['episode_id']} must be used"
                )
        return selected
    for item in history:
        if episode_is_eligible(item, now_utc_us=observed_now):
            return item
    return None


def repository_change(projection: dict[str, Any]) -> dict[str, Any]:
    episode = projection["episode"]
    missing = [ref for ref in episode["relevant_paths"] if not (REPO_ROOT / ref.split("#", 1)[0]).exists()]
    if missing:
        return {"status": "relevant_deleted", "paths": missing}
    current = content_digest(episode["relevant_paths"])
    if current != projection["relevant_digest"]:
        return {"status": "relevant_modified", "paths": episode["relevant_paths"]}
    return {"status": "unchanged", "paths": []}


def relevant_path_components(refs: Iterable[str]) -> list[dict[str, str]]:
    components=[]
    for ref in sorted(set(refs)):
        normalized=sanitize_text(ref,limit=500).replace("\\","/")
        path=REPO_ROOT/normalized.split("#",1)[0]
        if not path.exists():
            components.append({"path":normalized,"status":"missing","sha256":"none"})
            continue
        try: value=content_digest([normalized])
        except CadenceLedgerError:
            components.append({"path":normalized,"status":"invalid","sha256":"none"})
            continue
        components.append({"path":normalized,"status":"present","sha256":value})
    return components


def presentation_components(
    projection: dict[str,Any] | None, selection: dict[str,Any], rest_coverage_status: str,
) -> dict[str,Any]:
    if projection is None:
        return {"episode":None,"paths":[],"rest_coverage_status":rest_coverage_status,"verification":{},"selection":selection}
    episode=projection["episode"]
    verification=episode.get("verification",{})
    return {
        "episode":{"episode_id":episode["episode_id"],"lifecycle_state":projection["lifecycle_state"],"lifecycle_version":projection["lifecycle_version"],"method_version_digest":episode["method_version_digest"]},
        "paths":relevant_path_components(episode["relevant_paths"]),
        "rest_coverage_status":rest_coverage_status,
        "verification":{"status":verification.get("status"),"local_use_eligible":verification.get("local_use_eligible"),"repo_use_eligible":verification.get("repo_use_eligible"),"profile":episode.get("profile",{})},
        "selection":selection,
    }


def latest_presentation(connection: sqlite3.Connection, episode_id: str | None, workspace_id: str, operator_id: str) -> dict[str,Any] | None:
    if not table_exists(connection,"coffee_presentations"): return None
    row=connection.execute(
        """SELECT * FROM coffee_presentations WHERE workspace_id=? AND operator_id=?
           ORDER BY occurred_at_utc_us DESC,presentation_id DESC LIMIT 1""",
        (workspace_id,operator_id),
    ).fetchone()
    if row is None: return None
    return {key:row[key] for key in row.keys()} | {"context_components":json.loads(row["context_components_json"])}


def presentation_delta(current: dict[str,Any], prior: dict[str,Any] | None) -> list[str]:
    if prior is None: return []
    previous=prior["context_components"]
    changed=[]
    for key in ("episode","rest_coverage_status","verification","selection"):
        if current.get(key)!=previous.get(key): changed.append(key)
    before={item["path"]:item for item in previous.get("paths",[])}
    after={item["path"]:item for item in current.get("paths",[])}
    changed.extend(f"path:{path}" for path in sorted(set(before)|set(after)) if before.get(path)!=after.get(path))
    return changed


def presentation_mode(context_digest: str, prior: dict[str,Any] | None) -> tuple[str,int]:
    if prior is None: return "initial",0
    if prior["context_digest"]!=context_digest: return "delta",0
    if prior["presentation_mode"] in {"initial","delta"}: return "repeat-checkpoint",1
    return "saturated",int(prior["repeat_depth"])+1


ACTION_SHAPE = (
    ("A", "Confirm", "recommended"),
    ("B", "Test", "alternative"),
    ("C", "Deepen", "overlooked"),
    ("D", "Reframe", "pause-or-deepen"),
)


def build_actions(
    projection: dict[str, Any], *, mode: str="initial", repeat_depth: int=0,
    changed_components: list[str] | None=None,
    context_digest: str | None=None, prior_context_digest: str | None=None,
    prior_presentation_id: str | None=None,
) -> list[dict[str, Any]]:
    episode = projection["episode"]
    episode_id = episode["episode_id"]
    changes=changed_components or []
    changed_paths={item.removeprefix("path:") for item in changes if item.startswith("path:")}
    authored_changed=[item["ref"] for item in episode["artifacts"] if item["ref"] in changed_paths]
    first_artifact = authored_changed[0] if authored_changed else (sorted(changed_paths)[0] if changed_paths else episode["artifacts"][0]["ref"])
    method_target = f"{episode_id}:{episode['method_version_digest']}"
    observable = episode["observable"]
    falsifier_target = {**observable, "test": episode["falsifier"]}
    a_label=f"Execute: confirm {observable['name']} against {episode['next_use']}."
    b_label=f"Test the falsifier for {observable['name']}: {episode['falsifier']}"
    c_label=f"Deepen the evidence at {first_artifact}."
    d_label=f"Reframe the method change {episode['intervention']}."
    if mode=="delta":
        delta_label=", ".join(changes)
        a_label=f"Execute: confirm the relevant-lane delta ({delta_label}) against {episode['next_use']}."
        b_label=f"Test whether the delta changes the falsifier for {observable['name']}: {episode['falsifier']}"
        c_label=f"Deepen the changed evidence at {first_artifact}."
        d_label=f"Reframe {episode['intervention']} after the relevant-lane delta."
    elif mode=="repeat-checkpoint":
        a_label=f"Execute: confirm that no relevant-lane evidence changed since the prior Coffee presentation for {observable['name']}."
        b_label=f"Test the next evidence checkpoint for {observable['name']}: {episode['falsifier']}"
        c_label=f"Deepen the blocking evidence at {first_artifact}."
        d_label=f"Reframe whether to defer or retest {episode['intervention']}."
    elif mode=="saturated":
        a_label=f"Execute: confirm evidence stagnation after {repeat_depth} unchanged Coffee presentations for {observable['name']}."
        b_label=f"Test one concrete next-use falsifier before revisiting {observable['name']}: {episode['falsifier']}"
        c_label=f"Deepen the unresolved blockage at {first_artifact}."
        d_label=f"Reframe toward defer, supersede, reject, or retest for {episode['intervention']}."
    if mode == "initial":
        execution_target_type = "observable"
        execution_target = observable
        execution = {
            "kind": "read-only-observable-comparison",
            "source": observable["source"], "baseline": observable["baseline"],
            "threshold": observable["success_threshold"], "mutation": False,
            "verification": "Report whether the named source supports, contradicts, or cannot resolve the threshold comparison.",
        }
    else:
        if not context_digest or not prior_context_digest or not prior_presentation_id:
            raise CadenceLedgerError("contextual Coffee actions require prior and current presentation grounding")
        execution_target_type = "presentation_context"
        execution_target = f"{prior_context_digest}->{context_digest}"
        execution = {
            "kind": "read-only-context-digest-comparison",
            "source": f"coffee_presentations:{prior_presentation_id}",
            "baseline": prior_context_digest,
            "threshold": context_digest,
            "changed_components": changes,
            "mutation": False,
            "verification": "Compare the prior and current context digests and report the exact changed relevant components, or confirm that none changed.",
        }
    actions = [
        {
            "key": "A", "verb": "Confirm", "role": "recommended",
            "label": a_label,
            "target_type": execution_target_type, "target": execution_target, "reason": episode["evidence_summary"],
            "candidate_id": episode_id, "selection_effect": "execute",
            "execution": execution,
            "next_boundary": "Execute only the named read-only comparison; tests, writes, and disposition remain separate.",
        },
        {
            "key": "B", "verb": "Test", "role": "alternative",
            "label": b_label,
            "target_type": "observable", "target": falsifier_target, "reason": "A discriminating result can reject the claimed improvement.",
            "candidate_id": episode_id, "selection_effect": "navigate",
            "next_boundary": "Design the bounded comparison; running it remains separately authorized.",
        },
        {
            "key": "C", "verb": "Deepen", "role": "overlooked",
            "label": c_label,
            "target_type": "artifact", "target": first_artifact, "reason": "The named artifact is the first bounded provenance handle.",
            "candidate_id": episode_id, "selection_effect": "navigate",
            "next_boundary": "Inspect only the named artifact and identify the highest-consequence missing observation.",
        },
        {
            "key": "D", "verb": "Reframe", "role": "pause-or-deepen",
            "label": d_label,
            "target_type": "method_change", "target": method_target, "reason": "The method may need narrowing, retirement, or replacement.",
            "candidate_id": episode_id, "selection_effect": "navigate",
            "next_boundary": "Develop the bounded reframe; disposition remains separately authorized.",
        },
    ]
    validate_actions(actions)
    return actions


def build_cold_start_actions() -> list[dict[str, Any]]:
    actions = [
        {
            "key": "A", "verb": "Confirm", "role": "recommended",
            "label": "Execute: confirm the cadence baseline in tests/test_cadence.py before proposing a method change.",
            "target_type": "artifact", "target": "tests/test_cadence.py",
            "reason": "The existing suite is the bounded baseline for cadence behavior.",
            "candidate_id": None, "selection_effect": "execute",
            "execution": {
                "kind": "read-only-artifact-inspection", "source": "tests/test_cadence.py",
                "mutation": False,
                "verification": "Report the currently enforced Coffee and Dream baseline without running or changing tests.",
            },
            "next_boundary": "Execute only the named read-only inspection; test execution and candidate creation remain separate.",
        },
        {
            "key": "B", "verb": "Test", "role": "alternative",
            "label": "Test one bounded cadence assumption represented in scripts/cadence.py.",
            "target_type": "artifact", "target": "scripts/cadence.py",
            "reason": "A cold start needs one falsifiable method assumption rather than a broad review.",
            "candidate_id": None, "selection_effect": "navigate",
            "next_boundary": "Design one falsifier; running it remains separately authorized.",
        },
        {
            "key": "C", "verb": "Deepen", "role": "overlooked",
            "label": "Deepen one accountable gap in the forecast ledger.",
            "target_type": "artifact", "target": "narrative-geopolitics/work/forecasts/forecast-ledger.md",
            "reason": "The ledger is a bounded source of consequential unresolved work.",
            "candidate_id": None, "selection_effect": "navigate",
            "next_boundary": "Inspect one accountable forecast without scoring or changing it.",
        },
        {
            "key": "D", "verb": "Reframe", "role": "pause-or-deepen",
            "label": "Reframe the cold start as no cadence-worthy experiment when evidence is absent.",
            "target_type": "method_change", "target": "cold-start:no-cadence-worthy-experiment",
            "reason": "Cadence should not manufacture learning to satisfy ritual.",
            "candidate_id": None, "selection_effect": "navigate",
            "next_boundary": "Conclude read-only that no candidate is warranted; any closeout receipt remains separately authorized.",
        },
    ]
    validate_actions(actions)
    return actions


def validate_actions(actions: list[dict[str, Any]]) -> None:
    if len(actions) != 4:
        raise CadenceLedgerError("Coffee requires exactly four actions")
    labels: set[str] = set()
    targets: set[str] = set()
    for action, expected in zip(actions, ACTION_SHAPE, strict=True):
        if (action.get("key"), action.get("verb"), action.get("role")) != expected:
            raise CadenceLedgerError("Coffee actions have invalid order, verb, or role")
        label = sanitize_text(action.get("label", ""), limit=1000)
        if len(label.split()) < 4 or label.lower() in labels:
            raise CadenceLedgerError("Coffee action labels must be distinct and grounded")
        labels.add(label.lower())
        effect = action.get("selection_effect")
        if effect not in {"navigate", "execute"}:
            raise CadenceLedgerError("Coffee actions must be navigational or bounded read-only execution")
        if effect == "execute":
            if not label.casefold().startswith("execute:"):
                raise CadenceLedgerError("action-ready Coffee labels must begin with Execute:")
            execution = action.get("execution")
            if not isinstance(execution, dict) or execution.get("mutation") is not False:
                raise CadenceLedgerError("Coffee execution must be explicitly read-only")
            sanitize_text(execution.get("source", ""), limit=1000)
            sanitize_text(execution.get("verification", ""), limit=1000)
        target_type = action.get("target_type")
        if target_type not in TARGET_TYPES:
            raise CadenceLedgerError("Coffee action has invalid target type")
        target = action.get("target")
        if target_type == "artifact":
            target_key = normalize_repo_ref(str(target))
        elif target_type == "observable":
            if not isinstance(target, dict) or not all(target.get(k) for k in ("name", "unit", "success_threshold", "source")):
                raise CadenceLedgerError("observable target is incomplete")
            target_key = canonical_json(target)
        else:
            target_key = sanitize_text(target, limit=1000)
        if target_key in targets:
            raise CadenceLedgerError("Coffee actions must use distinct semantic targets")
        targets.add(target_key)
        sanitize_text(action.get("reason", ""), limit=4000)
        sanitize_text(action.get("next_boundary", ""), limit=1000)
    if not any(action.get("selection_effect") == "execute" for action in actions):
        raise CadenceLedgerError("Coffee requires at least one actionable option")


def coffee_context(
    connection: sqlite3.Connection,
    *,
    episode_id: str | None = None,
    rest_coverage_status: str = "unavailable",
) -> dict[str, Any]:
    allowed_rest = {"covered-current", "missing-dream", "late-terminal-only", "late-substantive", "unavailable"}
    if rest_coverage_status not in allowed_rest:
        raise CadenceLedgerError("invalid Rest coverage status")
    projection = selected_episode(connection, episode_id)
    newest = selected_episode(connection)
    selection = {
        "basis": "explicit" if episode_id else "automatic",
        "selected_dream_date": projection["episode"]["dream_date"] if projection else None,
        "newest_eligible_episode_id": newest["episode"]["episode_id"] if newest else None,
    }
    workspace_id=projection["episode"]["workspace_id"] if projection else "mira-core"
    operator_id=projection["episode"]["operator_id"] if projection else "operator"
    components=presentation_components(projection,selection,rest_coverage_status)
    invalid_paths=[item["path"] for item in components["paths"] if item["status"]!="present"]
    if invalid_paths:
        raise CadenceLedgerError(f"Coffee grounding failed for relevant path(s): {', '.join(invalid_paths)}")
    context_sha=digest(components)
    prior=latest_presentation(connection,projection["episode"]["episode_id"] if projection else None,workspace_id,operator_id)
    mode,repeat_depth=presentation_mode(context_sha,prior)
    changed=presentation_delta(components,prior) if mode=="delta" else []
    presentation={
        "mode":mode,"repeat_depth":repeat_depth,"context_digest":context_sha,
        "prior_presentation_id":prior["presentation_id"] if prior else None,
        "prior_context_digest":prior["context_digest"] if prior else None,
        "changed_components":changed,"tracking_available":table_exists(connection,"coffee_presentations"),
        "components":components,
    }
    if projection is None:
        actions = build_cold_start_actions()
        return {
            "schema_version": 1, "projection_version": PROJECTION_VERSION,
            "episode_id": None, "lifecycle_state": "cold_start", "lifecycle_version": None,
            "repository_change": {"status": "not_applicable", "paths": []},
            "inheritance_safe": False,
            "learning": {
                "observation": "No actionable cadence candidate is retained.",
                "diagnosis": "A bounded experiment must be identified before inheritance.",
                "intervention": "No method change is proposed.",
                "evidence_summary": "Repository controls provide grounding, not evidence of improvement.",
                "tomorrow_inherits": "No cadence lesson until a falsifiable experiment is recorded.",
            },
            "actions": actions, "recommendation_key": "A", "mutation_performed": False,
            "rest_coverage_status": rest_coverage_status,
            "selection": selection,
            "presentation":presentation,
        }
    actions = build_actions(
        projection, mode=mode, repeat_depth=repeat_depth,
        changed_components=changed, context_digest=context_sha,
        prior_context_digest=presentation["prior_context_digest"],
        prior_presentation_id=presentation["prior_presentation_id"],
    )
    change = repository_change(projection)
    episode = projection["episode"]
    return {
        "schema_version": 1,
        "projection_version": PROJECTION_VERSION,
        "episode_id": episode["episode_id"],
        "lifecycle_state": projection["lifecycle_state"],
        "lifecycle_version": projection["lifecycle_version"],
        "repository_change": change,
        "inheritance_safe": change["status"] == "unchanged" and projection["lifecycle_state"] in {"locally_verified", "inherited", "retest", "repeated"},
        "learning": {
            "observation": episode["observation"], "diagnosis": episode["diagnosis"],
            "intervention": episode["intervention"], "evidence_summary": episode["evidence_summary"],
            "tomorrow_inherits": episode["tomorrow_inherits"],
        },
        "actions": actions,
        "recommendation_key": "A",
        "rest_coverage_status": rest_coverage_status,
        "mutation_performed": False,
        "selection": selection,
        "presentation":presentation,
    }


def render_coffee_markdown(context: dict[str, Any]) -> str:
    validate_actions(context["actions"])
    learning = context["learning"]
    lines = [
        f"Coffee recovered `{context['episode_id']}` in `{context['lifecycle_state']}` state.",
        f"Selection: {context['selection']['basis']} from Dream date `{context['selection']['selected_dream_date']}`; newest eligible `{context['selection']['newest_eligible_episode_id']}`.",
        "",
        f"Learned: {learning['observation']}",
        f"Evidence: {learning['evidence_summary']}",
        f"Safe to inherit: {'yes' if context['inheritance_safe'] else 'no'}.",
        f"Remaining uncertainty: {learning['diagnosis']}",
        f"Rest coverage: {context.get('rest_coverage_status', 'unavailable')}.",
        f"Presentation: {context['presentation']['mode']}; repeat depth {context['presentation']['repeat_depth']}; context `{context['presentation']['context_digest'][:12]}`.",
        f"Changed relevant components: {', '.join(context['presentation']['changed_components']) if context['presentation']['changed_components'] else 'none'}.",
        "",
    ]
    for action in context["actions"]:
        if action["selection_effect"] == "execute":
            executable = action["label"].split(":", 1)[1].strip()
            lines.append(f"{action['key']}. Execute: {action['verb']} - {executable} Target: `{action['target_type']}`.")
            lines.append(f"   Authority boundary: {action['next_boundary']}")
        else:
            lines.append(f"{action['key']}. {action['verb']}: {action['label']} Target: `{action['target_type']}`.")
    recommendations={
        "initial":"A. Confirm the claimed improvement before adoption.",
        "delta":"A. Confirm the relevant-lane delta before changing the candidate's disposition.",
        "repeat-checkpoint":"A. Confirm the absence of relevant progress before designing another test.",
        "saturated":"A. Confirm evidence stagnation before developing a terminal disposition.",
    }
    lines.extend(["",f"Recommendation: {recommendations.get(context['presentation']['mode'],recommendations['initial'])}"])
    return "\n".join(lines) + "\n"


def record_coffee_presentation(connection: sqlite3.Connection, context: dict[str,Any], rendered: str) -> dict[str,Any]:
    if not table_exists(connection,"coffee_presentations"):
        raise CadenceLedgerError("Coffee presentation tracking requires cadence schema 4")
    presentation=context["presentation"]
    components=presentation["components"]
    episode_id=context["episode_id"]
    workspace_id="mira-core"; operator_id="operator"
    try:
        connection.execute("BEGIN IMMEDIATE")
        if episode_id:
            projected=project_episode(connection,episode_id)
            workspace_id=projected["episode"]["workspace_id"]; operator_id=projected["episode"]["operator_id"]
            newest=selected_episode(connection)
            fresh_selection={**components["selection"],"newest_eligible_episode_id":newest["episode"]["episode_id"] if newest else None}
            fresh_components=presentation_components(projected,fresh_selection,components["rest_coverage_status"])
            if digest(fresh_components)!=presentation["context_digest"]:
                raise CadenceLedgerError("Coffee relevant context changed concurrently; rerun Coffee")
        elif selected_episode(connection) is not None:
            raise CadenceLedgerError("Coffee candidate selection changed concurrently; rerun Coffee")
        latest=latest_presentation(connection,episode_id,workspace_id,operator_id)
        latest_id=latest["presentation_id"] if latest else None
        if latest_id!=presentation["prior_presentation_id"]:
            raise CadenceLedgerError("Coffee presentation context changed concurrently; rerun Coffee")
        when=validate_timestamp(utc_now()); presentation_id=f"CPF-{uuid.uuid4().hex}"
        previous=latest["receipt_sha256"] if latest else None
        body={
            "presentation_id":presentation_id,"episode_id":episode_id,"workspace_id":workspace_id,
            "operator_id":operator_id,"occurred_at":when,"lifecycle_version":context["lifecycle_version"],
            "presentation_mode":presentation["mode"],"repeat_depth":presentation["repeat_depth"],
            "context_components":components,"context_digest":presentation["context_digest"],
            "menu_digest":digest(rendered),"prior_presentation_id":latest_id,"previous_receipt_sha256":previous,
        }
        receipt_sha=digest(body)
        connection.execute(
            "INSERT INTO coffee_presentations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (presentation_id,episode_id,workspace_id,operator_id,when,timestamp_us(when),context["lifecycle_version"],
             presentation["mode"],presentation["repeat_depth"],canonical_json(components),presentation["context_digest"],
             body["menu_digest"],latest_id,previous,receipt_sha),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    return {"presentation_id":presentation_id,"presentation_mode":presentation["mode"],"context_digest":presentation["context_digest"],"menu_digest":body["menu_digest"],"receipt_sha256":receipt_sha,"authority_effect":"private-presentation-receipt-only"}


def record_disposition(
    connection: sqlite3.Connection, episode_id: str, decision: str, reason: str, *,
    idempotency_key: str, expected_version: int,
) -> dict[str, Any]:
    if decision not in DISPOSITIONS:
        raise CadenceLedgerError(f"invalid cadence disposition: {decision}")
    return append_event(
        connection, episode_id, "disposition",
        {"decision": decision, "reason": sanitize_text(reason)},
        idempotency_key=idempotency_key, expected_version=expected_version,
    )


def record_repetition(
    connection: sqlite3.Connection, episode_id: str, measurement: dict[str, Any], *,
    idempotency_key: str, expected_version: int,
) -> dict[str, Any]:
    projection = project_episode(connection, episode_id)
    episode = projection["episode"]
    required = ("series_id", "method_version_digest", "observable_name", "unit", "task_class", "observed", "environment_differences")
    if not all(key in measurement for key in required):
        raise CadenceLedgerError("repetition measurement is incomplete")
    comparable = (
        measurement["series_id"] == episode["series_id"]
        and measurement["method_version_digest"] == episode["method_version_digest"]
        and measurement["observable_name"] == episode["observable"]["name"]
        and measurement["unit"] == episode["observable"]["unit"]
        and measurement["task_class"] == episode["task_class"]
    )
    if not comparable:
        raise CadenceLedgerError("later-use receipt is not comparable to the cadence episode")
    payload = dict(measurement)
    payload["comparable"] = True
    return append_event(
        connection, episode_id, "repetition_recorded", payload,
        idempotency_key=idempotency_key, expected_version=expected_version,
    )


def reconcile_rsi(
    connection: sqlite3.Connection,
    receipt: dict[str, Any],
    *,
    idempotency_key: str,
    expected_version: int,
) -> dict[str, Any]:
    body = receipt.get("correspondence")
    if not isinstance(body, dict) or receipt.get("schema_version") != 1:
        raise CadenceLedgerError("invalid RSI correspondence receipt")
    expected = digest(body)
    if receipt.get("correspondence_sha256") != expected:
        raise CadenceLedgerError("RSI correspondence receipt digest mismatch")
    required = ("source_episode_id", "rsi_id", "candidate_sha256", "admission_digest")
    if not all(str(body.get(key, "")).strip() for key in required):
        raise CadenceLedgerError("RSI correspondence receipt is incomplete")
    return append_event(
        connection, str(body["source_episode_id"]), "represented",
        {key: body[key] for key in required}, idempotency_key=idempotency_key,
        expected_version=expected_version,
    )


def verify_ledger(connection: sqlite3.Connection) -> dict[str, Any]:
    store_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    failures: list[str] = []
    for row in connection.execute("SELECT episode_id FROM cadence_episodes"):
        projection = project_episode(connection, row[0])
        previous = None
        for event in projection["events"]:
            stored = connection.execute("SELECT * FROM cadence_events WHERE event_id = ?", (event["event_id"],)).fetchone()
            body = {
                "event_id": stored["event_id"], "episode_id": stored["episode_id"],
                "event_type": stored["event_type"], "occurred_at": stored["occurred_at"],
                "lifecycle_version": stored["lifecycle_version"], "payload": json.loads(stored["payload_json"]),
                "previous_event_sha256": previous,
            }
            if stored["previous_event_sha256"] != previous or stored["event_sha256"] != digest(body):
                failures.append(f"{row[0]}: event chain mismatch at {stored['event_id']}")
            previous = stored["event_sha256"]
    if table_exists(connection, "daily_close_runs"):
        for row in connection.execute("SELECT run_id FROM daily_close_runs"):
            previous = None
            for stored in _close_event_rows(connection, row[0]):
                body = {"event_id": stored["event_id"], "run_id": stored["run_id"],
                        "event_type": stored["event_type"], "occurred_at": stored["occurred_at"],
                        "lifecycle_version": stored["lifecycle_version"],
                        "payload": json.loads(stored["payload_json"]), "previous_event_sha256": previous}
                if stored["previous_event_sha256"] != previous or stored["event_sha256"] != digest(body):
                    failures.append(f"{row[0]}: daily close event chain mismatch at {stored['event_id']}")
                previous = stored["event_sha256"]
    if table_exists(connection, "daily_dream_closeouts"):
        for stored in connection.execute("SELECT closeout_id, payload_json, payload_sha256 FROM daily_dream_closeouts"):
            if digest(json.loads(stored["payload_json"])) != stored["payload_sha256"]:
                failures.append(f"{stored['closeout_id']}: Dream closeout digest mismatch")
    if table_exists(connection,"coffee_presentations"):
        scopes=connection.execute("SELECT DISTINCT workspace_id,operator_id FROM coffee_presentations")
        for scope in scopes:
            previous=None; previous_id=None
            rows=connection.execute(
                """SELECT * FROM coffee_presentations WHERE workspace_id=? AND operator_id=?
                   ORDER BY occurred_at_utc_us,presentation_id""",tuple(scope)
            )
            for stored in rows:
                body={"presentation_id":stored["presentation_id"],"episode_id":stored["episode_id"],"workspace_id":stored["workspace_id"],"operator_id":stored["operator_id"],"occurred_at":stored["occurred_at"],"lifecycle_version":stored["lifecycle_version"],"presentation_mode":stored["presentation_mode"],"repeat_depth":stored["repeat_depth"],"context_components":json.loads(stored["context_components_json"]),"context_digest":stored["context_digest"],"menu_digest":stored["menu_digest"],"prior_presentation_id":stored["prior_presentation_id"],"previous_receipt_sha256":stored["previous_receipt_sha256"]}
                if stored["previous_receipt_sha256"]!=previous or stored["prior_presentation_id"]!=previous_id or stored["receipt_sha256"]!=digest(body):
                    failures.append(f"Coffee presentation chain mismatch at {stored['presentation_id']}")
                previous=stored["receipt_sha256"]; previous_id=stored["presentation_id"]
    return {"schema_version": store_version, "reader_schema_version": SCHEMA_VERSION,
            "integrity": integrity, "failures": failures, "valid": integrity == "ok" and not failures}


def private_status(raw_path: str | Path | None = None) -> dict[str, Any]:
    resolution = resolve_store(raw_path, require_exists=True)
    if resolution.path is None:
        return {"availability": "unavailable", "freshness": "unavailable", "validation": resolution.reason, "counts": {}, "latest_event_at": None}
    try:
        connection = connect_read_only(resolution.path)
        verification = verify_ledger(connection)
        episode_count = connection.execute("SELECT COUNT(*) FROM cadence_episodes").fetchone()[0]
        active = 0
        represented = 0
        represented_ids: set[str] = set()
        for row in connection.execute("SELECT episode_id FROM cadence_episodes"):
            projection = project_episode(connection, row[0])
            state = projection["lifecycle_state"]
            active += state not in TERMINAL_STATES | {"represented"}
            represented += state == "represented"
            for event in projection["events"]:
                if event["event_type"] == "represented" and event["payload"].get("rsi_id"):
                    represented_ids.add(str(event["payload"]["rsi_id"]))
        canonical_ids: set[str] = set()
        canonical_path = REPO_ROOT / "narrative-geopolitics/work/system-improvement/recursive-learning-ledger.json"
        if canonical_path.is_file():
            canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
            canonical_ids = {str(item.get("id")) for item in canonical.get("entries", []) if isinstance(item, dict)}
        unresolved = len(represented_ids - canonical_ids)
        latest = (
            connection.execute(
                "SELECT MAX(value) FROM (SELECT occurred_at AS value FROM cadence_events UNION ALL SELECT occurred_at FROM daily_close_events)"
            ).fetchone()[0]
            if table_exists(connection, "daily_close_events")
            else connection.execute("SELECT MAX(occurred_at) FROM cadence_events").fetchone()[0]
        )
        presentations=connection.execute("SELECT COUNT(*) FROM coffee_presentations").fetchone()[0] if table_exists(connection,"coffee_presentations") else 0
        connection.close()
        valid = verification["valid"]
        return {
            "availability": "available" if valid else "degraded",
            "freshness": "valid" if valid else "invalid",
            "validation": "read-only SQLite integrity and event-chain verification passed" if valid else "; ".join(verification["failures"]),
            "counts": {"episodes": episode_count, "active_candidates": active, "represented": represented, "unresolved_rsi_correspondence": unresolved,"coffee_presentations":presentations},
            "latest_event_at": latest,
        }
    except (OSError, sqlite3.Error, CadenceLedgerError) as error:
        return {"availability": "degraded", "freshness": "invalid", "validation": f"read-only cadence check failed: {error.__class__.__name__}", "counts": {}, "latest_event_at": None}


def learning_reference(projection: dict[str, Any]) -> dict[str, Any]:
    episode = projection["episode"]
    chronology = [
        {
            "event_id": event["event_id"], "event_type": event["event_type"],
            "occurred_at": event["occurred_at"], "lifecycle_version": event["lifecycle_version"],
            "payload": event["payload"], "previous_event_sha256": event["previous_event_sha256"],
            "event_sha256": event["event_sha256"],
        }
        for event in projection["events"]
    ]
    later_use = [row for row in chronology if row["event_type"] == "repetition_recorded"]
    return {
        "schema_version": 1,
        "reference_kind": "cadence-process-learning",
        "reference_id": f"CPR-{episode['episode_id']}",
        "source_episode_id": episode["episode_id"],
        "source_series_id": episode["series_id"],
        "cadence_projection_version": PROJECTION_VERSION,
        "event_chain_digest": projection["event_chain_digest"],
        "method_version_digest": episode["method_version_digest"],
        "intervention_commits": episode.get("intervention_commits", []),
        "profile": episode["profile"],
        "claims": {
            "observation": episode["observation"], "diagnosis": episode["diagnosis"],
            "intervention": episode["intervention"], "outcome": later_use[-1]["payload"] if later_use else None,
        },
        "artifacts": episode["artifacts"],
        "chronology": chronology,
        "missing_evidence": ["later-use outcome"] if not later_use else [],
    }


def export_learning_reference(projection: dict[str, Any], output: Path, *, check: bool) -> dict[str, Any]:
    target = require_private_path(output, label="process-learning reference")
    packet = learning_reference(projection)
    raw = (json.dumps(packet, indent=2) + "\n").encode("utf-8")
    result = {"status": "ready" if check else "written", "output": str(target), "sha256": hashlib.sha256(raw).hexdigest(), "packet": packet}
    if check:
        return result
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_bytes(raw)
    temporary.replace(target)
    return result


def scorecard(connection: sqlite3.Connection) -> dict[str, Any]:
    history = list_history(connection, limit=200)
    states: dict[str, int] = {}
    repetitions = 0
    reviews = 0
    represented = 0
    regressions = 0
    reversals = 0
    rework_observed = 0
    rework_required = 0
    explicit_rework_measurements = 0
    disposition_times_us: list[int] = []
    for item in history:
        states[item["lifecycle_state"]] = states.get(item["lifecycle_state"], 0) + 1
        first_disposition = None
        for event in item["events"]:
            payload = event["payload"]
            if event["event_type"] == "disposition":
                reviews += 1
                first_disposition = first_disposition or event
                regressions += payload.get("regression") is True
                reversals += payload.get("reversal") is True
            elif event["event_type"] == "repetition_recorded":
                repetitions += 1
                regressions += payload.get("regression") is True
                reversals += payload.get("reversal") is True
                if isinstance(payload.get("rework_required"), bool):
                    explicit_rework_measurements += 1
                    rework_required += payload["rework_required"] is True
                if isinstance(payload.get("rework_count"), int) and payload["rework_count"] >= 0:
                    rework_observed += payload["rework_count"]
            elif event["event_type"] == "represented":
                represented += 1
        if first_disposition:
            disposition_times_us.append(
                timestamp_us(first_disposition["occurred_at"])
                - timestamp_us(item["episode"]["created_at"])
            )

    episode_count = len(history)
    reviewed_episode_count = sum(
        any(event["event_type"] == "disposition" for event in item["events"])
        for item in history
    )
    repeated_episode_count = sum(
        any(event["event_type"] == "repetition_recorded" for event in item["events"])
        for item in history
    )
    sorted_times = sorted(disposition_times_us)
    median_disposition_seconds = None
    if sorted_times:
        middle = len(sorted_times) // 2
        if len(sorted_times) % 2:
            median_us = sorted_times[middle]
        else:
            median_us = (sorted_times[middle - 1] + sorted_times[middle]) / 2
        median_disposition_seconds = median_us / 1_000_000

    unavailable = {
        "actionable_menu_rate": "Coffee presentation receipts retain menu digests, not selections or outcomes.",
        "navigation_only_exception_rate": "Coffee presentation receipts retain menu digests, not selections or outcomes.",
        "median_turns_coffee_to_authorized_test": "The cadence ledger records neither conversation turns nor authorization selections.",
        "operator_scope_restatement_rate": "No scope-restatement telemetry is retained.",
        "recursive_assessment_rate": "Assessment is authoritative in recursive-learn and no assessment correspondence receipt is imported.",
    }
    return {
        "schema_version": 2,
        "cohort": {"episodes_included": episode_count, "history_limit": 200},
        "episodes_created": episode_count,
        "reviews": reviews,
        "comparable_repetitions": repetitions,
        "lifecycle_distribution": states,
        "metrics": {
            "candidate_to_disposition_conversion": {
                "numerator": reviewed_episode_count,
                "denominator": episode_count,
                "rate": reviewed_episode_count / episode_count if episode_count else None,
            },
            "comparable_repetition_rate": {
                "numerator": repeated_episode_count,
                "denominator": episode_count,
                "rate": repeated_episode_count / episode_count if episode_count else None,
            },
            "median_candidate_to_disposition_seconds": median_disposition_seconds,
            "regressions": regressions,
            "reversals": reversals,
            "rework_after_execution": {
                "episodes_or_receipts_measured": explicit_rework_measurements,
                "required_count": rework_required,
                "reported_rework_count": rework_observed,
                "rate": (
                    rework_required / explicit_rework_measurements
                    if explicit_rework_measurements else None
                ),
            },
            "canonical_rsi_correspondence": {
                "represented_events": represented,
                "denominator": episode_count,
                "rate": represented / episode_count if episode_count else None,
            },
        },
        "unavailable_metrics": unavailable,
        "selection_popularity_excluded": True,
    }


def backup_store(source: Path, output: Path, *, check: bool) -> dict[str, Any]:
    source = require_private_path(source, label="cadence store")
    target = require_private_path(output, label="cadence backup")
    if check:
        return {"status": "ready", "source_available": source.is_file(), "output": str(target)}
    if not source.is_file():
        raise CadenceLedgerError("cadence store does not exist")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    shutil.copy2(source, temporary)
    temporary.replace(target)
    return {"status": "written", "output": str(target), "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "encryption": "external-filesystem-required"}

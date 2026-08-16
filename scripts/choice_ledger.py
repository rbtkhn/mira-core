from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from runtime_names import resolve_environment


SCHEMA_VERSION = 3
READABLE_SCHEMA_VERSIONS = frozenset({1, 2, SCHEMA_VERSION})
PROJECTION_VERSION = "1.1"
REVIEW_PROJECTION_VERSION = "2.0"
DB_ENV = "MIRA_CORE_CHOICE_DB"
GRACEFUL_CONNECTION_FAILURE_COMMANDS = frozenset(
    {"context", "review", "select", "close"}
)
READ_ONLY_COMMANDS = frozenset({"context", "review", "show", "verify"})
REPO_ROOT = Path(__file__).resolve().parent.parent
SQLITE_HEADER = b"SQLite format 3\x00"
AUTHORITY_EFFECT = "none"
ROLES = ("recommended", "alternative", "overlooked", "pause-or-deepen")
EVENT_TYPES = (
    "branch_selected",
    "branch_closed",
    "outcome_recorded",
    "review_deferred",
    "corrected",
    "superseded",
)
CLOSURE_REASONS = ("completed", "paused", "saturated")
RESULTS = ("successful", "mixed", "unsuccessful", "no_action", "not_observable")
COGNITIVE_LOAD = ("lower", "same", "higher", "Missing")
MOMENTUM = ("advanced", "neutral", "stalled", "Missing")
DISCOVERY = (
    "new-useful-path",
    "confirmed-known-path",
    "not-useful",
    "Missing",
)
NO_AUTHORITY = (
    "Receipt retention grants no authority. Any bounded action authority comes "
    "only from the governing visible option label and remains subject to "
    "existing controls."
)
EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d ()-]{7,}\d)(?!\d)")
SECRET_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*\S+"
)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class ChoiceError(ValueError):
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
        raise ChoiceError(f"invalid timestamp: {value}") from error
    if parsed.tzinfo is None:
        raise ChoiceError("timestamps must include a timezone")
    return value


def timestamp_order_key(value: str) -> int:
    validate_timestamp(value)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        timezone.utc
    )
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = parsed - epoch
    return (
        (delta.days * 86_400 + delta.seconds) * 1_000_000
        + delta.microseconds
    )


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    raw = value if isinstance(value, str) else canonical_json(value)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def require_private_path(raw_path: str | Path, *, label: str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        raise ChoiceError(f"{label} path must be absolute")
    resolved = path.resolve(strict=False)
    repository = REPO_ROOT.resolve()
    if resolved == repository or resolved.is_relative_to(repository):
        raise ChoiceError(f"{label} path must be outside the repository")
    return resolved


def resolve_store(raw_path: str | Path | None, *, require_exists: bool = False) -> StoreResolution:
    configured = raw_path or resolve_environment(DB_ENV)
    if not configured:
        return StoreResolution(None, f"private choice store is not configured; set {DB_ENV} or pass --db")
    try:
        path = require_private_path(configured, label="private choice store")
    except ChoiceError as error:
        return StoreResolution(None, str(error))
    if require_exists and not path.is_file():
        return StoreResolution(None, f"private choice store does not exist: {path}")
    return StoreResolution(path)


def sanitize_text(value: Any, *, limit: int = 2000) -> str:
    text = CONTROL_RE.sub("", str(value)).strip()
    if SECRET_RE.search(text):
        raise ChoiceError("private choice data appears to contain a credential or secret")
    text = EMAIL_RE.sub("[redacted-contact]", text)
    text = PHONE_RE.sub("[redacted-contact]", text)
    if len(text) > limit:
        raise ChoiceError(f"private choice text exceeds {limit} characters")
    return text


def sanitize_string_list(values: Iterable[Any] | None, *, limit: int = 20) -> list[str]:
    result = [sanitize_text(value, limit=500) for value in (values or [])]
    if len(result) > limit:
        raise ChoiceError(f"private choice list exceeds {limit} items")
    return result


def sanitize_evidence_ref(value: str | None) -> str | None:
    if value is None:
        return None
    reference = sanitize_text(value, limit=500)
    if "\n" in reference or len(reference.split()) > 12:
        raise ChoiceError("evidence must be linked by a bounded reference, not a raw body")
    return reference


def sanitize_reference_list(values: Iterable[Any] | None) -> list[str]:
    result = [sanitize_evidence_ref(str(value)) for value in (values or [])]
    if len(result) > 20:
        raise ChoiceError("private choice reference list exceeds 20 items")
    return [value for value in result if value is not None]


def sanitize_options(raw: Any) -> list[dict[str, str]]:
    if not isinstance(raw, list) or len(raw) not in (3, 4):
        raise ChoiceError("possibility set must contain three or four options")
    options: list[dict[str, str]] = []
    keys: set[str] = set()
    roles: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            raise ChoiceError("each possibility must be an object")
        key = sanitize_text(item.get("key", ""), limit=80)
        role = sanitize_text(item.get("role", ""), limit=80)
        text = sanitize_text(item.get("text", ""))
        if not key or not text or role not in ROLES:
            raise ChoiceError("each possibility requires a key, text, and stable semantic role")
        if key in keys or role in roles:
            raise ChoiceError("possibility keys and semantic roles must be unique")
        keys.add(key)
        roles.add(role)
        options.append({"key": key, "role": role, "text": text})
    required = {"recommended", "alternative"}
    if len(options) == 4:
        required = set(ROLES)
    elif not roles & {"overlooked", "pause-or-deepen"}:
        raise ChoiceError(
            "a three-option set requires an overlooked or pause-or-deepen role"
        )
    if not required <= roles:
        raise ChoiceError(f"possibility roles must include {sorted(required)}")
    return options


def parse_json_argument(value: str) -> Any:
    candidate = Path(value)
    try:
        is_file = candidate.is_file()
    except OSError:
        is_file = False
    if is_file:
        return json.loads(candidate.read_text(encoding="utf-8"))
    return json.loads(value)


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        journal_mode = connection.execute("PRAGMA journal_mode = DELETE").fetchone()[0]
        if str(journal_mode).lower() != "delete":
            raise sqlite3.OperationalError(
                "choice store could not enter rollback-journal mode"
            )
        connection.execute("PRAGMA synchronous = FULL")
        migrate(connection)
    except (ChoiceError, sqlite3.Error):
        connection.close()
        raise
    return connection


def require_rollback_journal(path: Path) -> None:
    with path.open("rb") as stream:
        header = stream.read(20)
    if len(header) < 20 or header[:16] != SQLITE_HEADER:
        raise sqlite3.DatabaseError("choice store has an invalid SQLite header")
    journal_versions = (header[18], header[19])
    if journal_versions == (2, 2):
        raise sqlite3.OperationalError(
            "choice store requires writable WAL-to-DELETE migration "
            "before read-only access"
        )
    if journal_versions != (1, 1):
        raise sqlite3.DatabaseError(
            "choice store has unsupported SQLite journal format versions"
        )


def connect_read_only(path: Path) -> sqlite3.Connection:
    resolved = path.resolve()
    require_rollback_journal(resolved)
    connection = sqlite3.connect(f"{resolved.as_uri()}?mode=ro", uri=True)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA query_only = ON")
        connection.execute("BEGIN")
        version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if version not in READABLE_SCHEMA_VERSIONS:
            raise ChoiceError(
                f"choice store schema {version} is not readable; supported versions are "
                f"{sorted(READABLE_SCHEMA_VERSIONS)}"
            )
    except (ChoiceError, sqlite3.Error):
        connection.close()
        raise
    return connection


def migrate(connection: sqlite3.Connection) -> None:
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if version > SCHEMA_VERSION:
        raise ChoiceError(f"choice store schema {version} is newer than supported {SCHEMA_VERSION}")
    with connection:
        if version == 0:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS choice_prompts (
                    choice_id TEXT PRIMARY KEY,
                    tenant TEXT NOT NULL,
                    workspace TEXT NOT NULL,
                    lane TEXT NOT NULL,
                    choice_kind TEXT NOT NULL,
                    consequence_level TEXT NOT NULL,
                    decision_summary TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    presented_at TEXT NOT NULL,
                    selected_at TEXT NOT NULL,
                    selected_at_utc_us INTEGER NOT NULL,
                    options_json TEXT NOT NULL,
                    options_hash TEXT NOT NULL,
                    recommended_key TEXT NOT NULL,
                    selected_key TEXT NOT NULL,
                    learning_refs_json TEXT NOT NULL,
                    success_signals_json TEXT NOT NULL,
                    risk_signals_json TEXT NOT NULL,
                    no_execution_authority TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS choice_events (
                    event_id TEXT PRIMARY KEY,
                    choice_id TEXT NOT NULL REFERENCES choice_prompts(choice_id),
                    sequence INTEGER NOT NULL,
                    event_type TEXT NOT NULL CHECK(event_type IN (
                        'branch_selected', 'branch_closed', 'outcome_recorded', 'review_deferred',
                        'corrected', 'superseded'
                    )),
                    occurred_at TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT,
                    event_hash TEXT NOT NULL,
                    UNIQUE(choice_id, sequence),
                    UNIQUE(choice_id, idempotency_key)
                );
                CREATE TRIGGER IF NOT EXISTS choice_prompts_no_update
                    BEFORE UPDATE ON choice_prompts BEGIN
                    SELECT RAISE(ABORT, 'choice prompts are immutable');
                END;
                CREATE TRIGGER IF NOT EXISTS choice_prompts_no_delete
                    BEFORE DELETE ON choice_prompts BEGIN
                    SELECT RAISE(ABORT, 'choice prompts are immutable');
                END;
                CREATE INDEX IF NOT EXISTS choice_prompts_scope_selected
                    ON choice_prompts(
                        tenant, workspace, lane, selected_at_utc_us, choice_id
                    );
                CREATE TRIGGER IF NOT EXISTS choice_events_no_update
                    BEFORE UPDATE ON choice_events BEGIN
                    SELECT RAISE(ABORT, 'choice events are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS choice_events_no_delete
                    BEFORE DELETE ON choice_events BEGIN
                    SELECT RAISE(ABORT, 'choice events are append-only');
                END;
                """
            )
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        elif version == 1:
            connection.execute("BEGIN IMMEDIATE")
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(choice_prompts)")
            }
            connection.execute("DROP TRIGGER IF EXISTS choice_prompts_no_update")
            if "selected_at_utc_us" not in columns:
                connection.execute(
                    "ALTER TABLE choice_prompts ADD COLUMN selected_at_utc_us INTEGER"
                )
            rows = connection.execute(
                "SELECT choice_id, selected_at FROM choice_prompts "
                "WHERE selected_at_utc_us IS NULL"
            ).fetchall()
            connection.executemany(
                "UPDATE choice_prompts SET selected_at_utc_us=? WHERE choice_id=?",
                [
                    (timestamp_order_key(row[1]), row[0])
                    for row in rows
                ],
            )
            connection.execute(
                "CREATE TRIGGER choice_prompts_no_update "
                "BEFORE UPDATE ON choice_prompts BEGIN "
                "SELECT RAISE(ABORT, 'choice prompts are immutable'); END"
            )
            connection.execute(
                "CREATE TRIGGER IF NOT EXISTS choice_prompts_selected_at_utc_required "
                "BEFORE INSERT ON choice_prompts "
                "WHEN NEW.selected_at_utc_us IS NULL BEGIN "
                "SELECT RAISE(ABORT, 'choice prompts require UTC ordering'); END"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS choice_prompts_scope_selected "
                "ON choice_prompts(tenant, workspace, lane, "
                "selected_at_utc_us, choice_id)"
            )
            connection.execute("PRAGMA user_version = 2")
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if version == 2:
        with connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DROP TRIGGER IF EXISTS choice_events_no_update")
            connection.execute("DROP TRIGGER IF EXISTS choice_events_no_delete")
            connection.execute("ALTER TABLE choice_events RENAME TO choice_events_v2")
            connection.execute(
                """CREATE TABLE choice_events (
                    event_id TEXT PRIMARY KEY,
                    choice_id TEXT NOT NULL REFERENCES choice_prompts(choice_id),
                    sequence INTEGER NOT NULL,
                    event_type TEXT NOT NULL CHECK(event_type IN (
                        'branch_selected', 'branch_closed', 'outcome_recorded',
                        'review_deferred', 'corrected', 'superseded'
                    )),
                    occurred_at TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT,
                    event_hash TEXT NOT NULL,
                    UNIQUE(choice_id, sequence),
                    UNIQUE(choice_id, idempotency_key)
                )"""
            )
            connection.execute(
                """INSERT INTO choice_events(
                    event_id, choice_id, sequence, event_type, occurred_at,
                    idempotency_key, payload_json, previous_hash, event_hash
                )
                SELECT
                    event_id, choice_id, sequence, event_type, occurred_at,
                    idempotency_key, payload_json, previous_hash, event_hash
                FROM choice_events_v2"""
            )
            connection.execute("DROP TABLE choice_events_v2")
            connection.execute(
                """CREATE TRIGGER choice_events_no_update
                    BEFORE UPDATE ON choice_events BEGIN
                    SELECT RAISE(ABORT, 'choice events are append-only'); END"""
            )
            connection.execute(
                """CREATE TRIGGER choice_events_no_delete
                    BEFORE DELETE ON choice_events BEGIN
                    SELECT RAISE(ABORT, 'choice events are append-only'); END"""
            )
            connection.execute("PRAGMA user_version = 3")


def create_backup(path: Path, destination: Path) -> Path:
    source_path = require_private_path(path, label="choice store")
    destination_path = require_private_path(destination, label="backup")
    if not source_path.is_file():
        raise ChoiceError("cannot back up a missing choice store")
    if source_path == destination_path:
        raise ChoiceError("backup destination must differ from the choice store")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f"{destination_path.name}.",
        suffix=".backuping",
        dir=destination_path.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    source = sqlite3.connect(f"{source_path.as_uri()}?mode=ro", uri=True)
    target = sqlite3.connect(temporary)
    try:
        source.backup(target)
        target.close()
        source.close()
        source_status = inspect_store(source_path)
        backup_status = inspect_store(temporary)
        if backup_status["integrity_check"] != "ok":
            raise ChoiceError(
                f"backup integrity check failed: {backup_status['integrity_check']}"
            )
        if backup_status["logical_fingerprint"] != source_status["logical_fingerprint"]:
            raise ChoiceError("backup logical fingerprint differs from the choice store")
        temporary.replace(destination_path)
    finally:
        try:
            target.close()
        finally:
            source.close()
        if temporary.exists():
            temporary.unlink()
    return destination_path


def inspect_store(path: Path) -> dict[str, Any]:
    resolved = require_private_path(path, label="choice store inspection")
    if not resolved.is_file():
        raise ChoiceError(f"choice store does not exist: {resolved}")
    connection = sqlite3.connect(f"{resolved.as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
        prompt_rows = [
            dict(row)
            for row in connection.execute(
                "SELECT choice_id, tenant, workspace, lane, choice_kind, "
                "consequence_level, decision_summary, actor, presented_at, "
                "selected_at, options_json, options_hash, recommended_key, "
                "selected_key, learning_refs_json, success_signals_json, "
                "risk_signals_json, no_execution_authority "
                "FROM choice_prompts ORDER BY choice_id"
            )
        ]
        event_rows = [
            dict(row)
            for row in connection.execute(
                "SELECT event_id, choice_id, sequence, event_type, occurred_at, "
                "idempotency_key, payload_json, previous_hash, event_hash "
                "FROM choice_events ORDER BY choice_id, sequence"
            )
        ]
        return {
            "path": str(resolved),
            "schema_version": int(
                connection.execute("PRAGMA user_version").fetchone()[0]
            ),
            "integrity_check": integrity,
            "choice_prompts": len(prompt_rows),
            "choice_events": len(event_rows),
            "logical_fingerprint": digest(
                {"choice_prompts": prompt_rows, "choice_events": event_rows}
            ),
        }
    finally:
        connection.close()


def compare_backup(path: Path, backup: Path) -> dict[str, Any]:
    source_status = inspect_store(path)
    backup_status = inspect_store(backup)
    exact_match = (
        source_status["integrity_check"] == "ok"
        and backup_status["integrity_check"] == "ok"
        and source_status["logical_fingerprint"]
        == backup_status["logical_fingerprint"]
    )
    return {
        "fresh": exact_match,
        "source": source_status,
        "backup": backup_status,
    }


def recover_backup(backup: Path, destination: Path) -> Path:
    backup_path = require_private_path(backup, label="backup")
    destination_path = require_private_path(destination, label="recovery destination")
    if not backup_path.is_file():
        raise ChoiceError("choice-store backup does not exist")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination_path.with_name(destination_path.name + ".recovering")
    if temporary.exists():
        temporary.unlink()
    shutil.copy2(backup_path, temporary)
    connection = sqlite3.connect(temporary)
    try:
        result = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise ChoiceError(f"backup integrity check failed: {result}")
    finally:
        connection.close()
    temporary.replace(destination_path)
    return destination_path


def event_hash(
    *,
    choice_id: str,
    sequence: int,
    event_type: str,
    occurred_at: str,
    idempotency_key: str,
    payload_json: str,
    previous_hash: str | None,
) -> str:
    return digest(
        {
            "choice_id": choice_id,
            "sequence": sequence,
            "event_type": event_type,
            "occurred_at": occurred_at,
            "idempotency_key": idempotency_key,
            "payload_json": payload_json,
            "previous_hash": previous_hash,
        }
    )


def _append_event(
    connection: sqlite3.Connection,
    *,
    choice_id: str,
    event_type: str,
    occurred_at: str,
    idempotency_key: str,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], bool]:
    if event_type not in EVENT_TYPES:
        raise ChoiceError(f"unsupported event type: {event_type}")
    payload_json = canonical_json(payload)
    existing = connection.execute(
        "SELECT * FROM choice_events WHERE choice_id=? AND idempotency_key=?",
        (choice_id, idempotency_key),
    ).fetchone()
    if existing:
        if existing["event_type"] == event_type and existing["payload_json"] == payload_json:
            return dict(existing), False
        raise ChoiceError("conflicting retry rejected; history was not overwritten")
    prior = connection.execute(
        "SELECT sequence, event_hash FROM choice_events WHERE choice_id=? ORDER BY sequence DESC LIMIT 1",
        (choice_id,),
    ).fetchone()
    sequence = 1 if prior is None else int(prior["sequence"]) + 1
    previous_hash = None if prior is None else str(prior["event_hash"])
    hashed = event_hash(
        choice_id=choice_id,
        sequence=sequence,
        event_type=event_type,
        occurred_at=occurred_at,
        idempotency_key=idempotency_key,
        payload_json=payload_json,
        previous_hash=previous_hash,
    )
    event_id = f"{choice_id}:{sequence}:{hashed[:12]}"
    connection.execute(
        """
        INSERT INTO choice_events(
            event_id, choice_id, sequence, event_type, occurred_at,
            idempotency_key, payload_json, previous_hash, event_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            choice_id,
            sequence,
            event_type,
            occurred_at,
            idempotency_key,
            payload_json,
            previous_hash,
            hashed,
        ),
    )
    return dict(
        connection.execute("SELECT * FROM choice_events WHERE event_id=?", (event_id,)).fetchone()
    ), True


def select_branch(
    connection: sqlite3.Connection,
    *,
    choice_id: str,
    options: Any,
    selected_key: str,
    tenant: str,
    workspace: str,
    lane: str,
    choice_kind: str,
    consequence_level: str,
    decision_summary: str,
    actor: str,
    presented_at: str,
    selected_at: str,
    idempotency_key: str,
    learning_refs: Iterable[Any] | None = None,
    success_signals: Iterable[Any] | None = None,
    risk_signals: Iterable[Any] | None = None,
) -> dict[str, Any]:
    sanitized = sanitize_options(options)
    selected_key = sanitize_text(selected_key, limit=80)
    keys = {item["key"] for item in sanitized}
    if selected_key not in keys:
        raise ChoiceError("selected key is not present in the possibility set")
    recommended_key = next(item["key"] for item in sanitized if item["role"] == "recommended")
    prompt = {
        "choice_id": sanitize_text(choice_id, limit=120),
        "tenant": sanitize_text(tenant, limit=120),
        "workspace": sanitize_text(workspace, limit=240),
        "lane": sanitize_text(lane, limit=120),
        "choice_kind": sanitize_text(choice_kind, limit=120),
        "consequence_level": sanitize_text(consequence_level, limit=80),
        "decision_summary": sanitize_text(decision_summary),
        "actor": sanitize_text(actor, limit=120),
        "presented_at": validate_timestamp(presented_at),
        "selected_at": validate_timestamp(selected_at),
        "selected_at_utc_us": timestamp_order_key(selected_at),
        "options_json": canonical_json(sanitized),
        "options_hash": digest(sanitized),
        "recommended_key": recommended_key,
        "selected_key": selected_key,
        "learning_refs_json": canonical_json(sanitize_reference_list(learning_refs)),
        "success_signals_json": canonical_json(sanitize_string_list(success_signals)),
        "risk_signals_json": canonical_json(sanitize_string_list(risk_signals)),
        "no_execution_authority": NO_AUTHORITY,
    }
    existing = connection.execute(
        "SELECT * FROM choice_prompts WHERE choice_id=?", (prompt["choice_id"],)
    ).fetchone()
    retried_event = None
    if existing:
        retried_event = connection.execute(
            """
            SELECT event_type FROM choice_events
            WHERE choice_id=? AND idempotency_key=?
            """,
            (prompt["choice_id"], idempotency_key),
        ).fetchone()
        if retried_event and retried_event["event_type"] == "branch_selected":
            prompt["selected_at"] = existing["selected_at"]
            prompt["selected_at_utc_us"] = existing["selected_at_utc_us"]
        elif not retried_event:
            raise ChoiceError(
                "choice already has a branch selection; new idempotency key rejected"
            )
    with connection:
        created = existing is None
        if created:
            connection.execute(
                f"INSERT INTO choice_prompts({','.join(prompt)}) VALUES ({','.join('?' for _ in prompt)})",
                tuple(prompt.values()),
            )
        else:
            comparable = {key: existing[key] for key in prompt}
            if comparable != prompt:
                raise ChoiceError("conflicting selection retry rejected; immutable prompt differs")
        event, event_created = _append_event(
            connection,
            choice_id=prompt["choice_id"],
            event_type="branch_selected",
            occurred_at=validate_timestamp(selected_at),
            idempotency_key=idempotency_key,
            payload={
                "selected_key": selected_key,
                "selected_role": next(
                    item["role"] for item in sanitized if item["key"] == selected_key
                ),
                "options_hash": prompt["options_hash"],
                "authority_effect": AUTHORITY_EFFECT,
                "no_execution_authority": NO_AUTHORITY,
            },
        )
    return {
        "retained": True,
        "created": created and event_created,
        "choice_id": prompt["choice_id"],
        "selected_key": selected_key,
        "selected_role": json.loads(event["payload_json"])["selected_role"],
        "options_hash": prompt["options_hash"],
        "authority_effect": AUTHORITY_EFFECT,
        "no_execution_authority": NO_AUTHORITY,
    }


def _validate_supersession(
    connection: sqlite3.Connection,
    *,
    choice_id: str,
    event_type: str,
    supersedes_event_id: str | None,
    idempotency_key: str,
) -> None:
    lineage_event = event_type in {"corrected", "superseded"}
    if lineage_event and not supersedes_event_id:
        raise ChoiceError(f"{event_type} requires supersedes_event_id")
    if not lineage_event and supersedes_event_id:
        raise ChoiceError(
            f"{event_type} cannot carry a supersedes_event_id"
        )
    if not lineage_event:
        return
    target = connection.execute(
        """
        SELECT event_type FROM choice_events
        WHERE event_id=? AND choice_id=?
        """,
        (supersedes_event_id, choice_id),
    ).fetchone()
    if not target:
        raise ChoiceError(
            "supersession target must be an earlier event from the same choice"
        )
    if event_type == "corrected" and target["event_type"] not in {
        "outcome_recorded",
        "corrected",
    }:
        raise ChoiceError("corrected events may supersede only an outcome or correction")
    for row in connection.execute(
        "SELECT idempotency_key, payload_json FROM choice_events WHERE choice_id=?",
        (choice_id,),
    ):
        if row["idempotency_key"] == idempotency_key:
            continue
        if json.loads(row["payload_json"]).get("supersedes_event_id") == supersedes_event_id:
            raise ChoiceError("supersession target has already been superseded")


def append_choice_event(
    connection: sqlite3.Connection,
    *,
    choice_id: str,
    event_type: str,
    idempotency_key: str,
    occurred_at: str,
    result: str | None = None,
    cognitive_load: str = "Missing",
    momentum: str = "Missing",
    discovery_value: str = "Missing",
    rework_minutes: int | None = None,
    evidence_ref: str | None = None,
    observation: str | None = None,
    authority_incident: bool = False,
    privacy_incident: bool = False,
    safety_incident: bool = False,
    lane_incident: bool = False,
    supersedes_event_id: str | None = None,
) -> dict[str, Any]:
    if not connection.execute(
        "SELECT 1 FROM choice_prompts WHERE choice_id=?", (choice_id,)
    ).fetchone():
        raise ChoiceError("choice does not exist")
    if event_type == "outcome_recorded" and result not in RESULTS:
        raise ChoiceError("outcome_recorded requires a bounded result")
    if cognitive_load not in COGNITIVE_LOAD:
        raise ChoiceError("invalid cognitive-load value")
    if momentum not in MOMENTUM:
        raise ChoiceError("invalid momentum value")
    if discovery_value not in DISCOVERY:
        raise ChoiceError("invalid discovery value")
    if rework_minutes is not None and rework_minutes < 0:
        raise ChoiceError("rework minutes cannot be negative")
    sanitized_supersedes = (
        sanitize_text(supersedes_event_id, limit=200)
        if supersedes_event_id
        else None
    )
    payload = {
        "result": result,
        "cognitive_load": cognitive_load,
        "momentum": momentum,
        "discovery_value": discovery_value,
        "rework_minutes": rework_minutes,
        "evidence_ref": sanitize_evidence_ref(evidence_ref),
        "observation": sanitize_text(observation, limit=1000) if observation else None,
        "authority_incident": bool(authority_incident),
        "privacy_incident": bool(privacy_incident),
        "safety_incident": bool(safety_incident),
        "lane_incident": bool(lane_incident),
        "supersedes_event_id": sanitized_supersedes,
    }
    with connection:
        _validate_supersession(
            connection,
            choice_id=choice_id,
            event_type=event_type,
            supersedes_event_id=sanitized_supersedes,
            idempotency_key=idempotency_key,
        )
        event, created = _append_event(
            connection,
            choice_id=choice_id,
            event_type=event_type,
            occurred_at=validate_timestamp(occurred_at),
            idempotency_key=idempotency_key,
            payload=payload,
        )
    return {
        "retained": True,
        "created": created,
        "choice_id": choice_id,
        "event_id": event["event_id"],
        "event_type": event_type,
    }


def close_branch(
    connection: sqlite3.Connection,
    *,
    choice_id: str,
    reason: str,
    idempotency_key: str,
    occurred_at: str,
    observation: str | None = None,
    tenant: str | None = None,
    workspace: str | None = None,
    lane: str | None = None,
) -> dict[str, Any]:
    if reason not in CLOSURE_REASONS:
        raise ChoiceError("branch closure requires a bounded reason")
    prompt = connection.execute(
        "SELECT tenant, workspace, lane FROM choice_prompts WHERE choice_id=?",
        (choice_id,),
    ).fetchone()
    if not prompt:
        raise ChoiceError("choice does not exist")
    supplied_scope = (tenant, workspace, lane)
    if any(value is not None for value in supplied_scope) and supplied_scope != (
        prompt["tenant"],
        prompt["workspace"],
        prompt["lane"],
    ):
        raise ChoiceError("choice is outside the requested scope")
    payload = {
        "reason": reason,
        "observation": sanitize_text(observation, limit=1000) if observation else None,
    }
    existing_retry = connection.execute(
        "SELECT event_type, payload_json FROM choice_events "
        "WHERE choice_id=? AND idempotency_key=?",
        (choice_id, idempotency_key),
    ).fetchone()
    if existing_retry:
        if (
            existing_retry["event_type"] != "branch_closed"
            or existing_retry["payload_json"] != canonical_json(payload)
        ):
            raise ChoiceError("conflicting retry rejected; history was not overwritten")
    else:
        if connection.execute(
            "SELECT 1 FROM choice_events WHERE choice_id=? "
            "AND event_type='branch_closed'",
            (choice_id,),
        ).fetchone():
            raise ChoiceError("choice branch is already closed")
        if _current_outcome(_events(connection, choice_id)):
            raise ChoiceError("resolved choice cannot be closed")
    with connection:
        event, created = _append_event(
            connection,
            choice_id=choice_id,
            event_type="branch_closed",
            occurred_at=validate_timestamp(occurred_at),
            idempotency_key=idempotency_key,
            payload=payload,
        )
    return {
        "retained": True,
        "created": created,
        "choice_id": choice_id,
        "event_id": event["event_id"],
        "event_type": "branch_closed",
        "reason": reason,
        "authority_effect": AUTHORITY_EFFECT,
    }


def _events(connection: sqlite3.Connection, choice_id: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT * FROM choice_events WHERE choice_id=? ORDER BY sequence", (choice_id,)
    ).fetchall()
    return _decode_event_rows(rows)


def _decode_event_rows(rows: Iterable[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) | {"payload": json.loads(row["payload_json"])} for row in rows]


def _current_outcome(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    outcome: dict[str, Any] | None = None
    superseded_ids = {
        item["payload"].get("supersedes_event_id")
        for item in events
        if item["event_type"] in {"corrected", "superseded"}
    }
    for event in events:
        if event["event_id"] in superseded_ids:
            continue
        if event["event_type"] in {"outcome_recorded", "corrected"} and event["payload"].get(
            "result"
        ):
            outcome = event["payload"] | {
                "event_id": event["event_id"],
                "occurred_at": event["occurred_at"],
            }
    return outcome


def _project_choice_rows(
    row: sqlite3.Row | dict[str, Any], events: list[dict[str, Any]]
) -> dict[str, Any]:
    superseded = any(item["event_type"] == "superseded" for item in events)
    closed = next(
        (item for item in reversed(events) if item["event_type"] == "branch_closed"),
        None,
    )
    outcome = _current_outcome(events)
    current_state = (
        "superseded"
        if superseded
        else ("resolved" if outcome else ("closed" if closed else "unresolved"))
    )
    return {
        "projection_version": PROJECTION_VERSION,
        "choice": {
            "choice_id": row["choice_id"],
            "tenant": row["tenant"],
            "workspace": row["workspace"],
            "lane": row["lane"],
            "choice_kind": row["choice_kind"],
            "consequence_level": row["consequence_level"],
            "decision_summary": row["decision_summary"],
            "actor": row["actor"],
            "presented_at": row["presented_at"],
            "selected_at": row["selected_at"],
            "options": json.loads(row["options_json"]),
            "options_hash": row["options_hash"],
            "recommended_key": row["recommended_key"],
            "selected_key": row["selected_key"],
            "learning_refs": json.loads(row["learning_refs_json"]),
            "success_signals": json.loads(row["success_signals_json"]),
            "risk_signals": json.loads(row["risk_signals_json"]),
        },
        "current_state": current_state,
        "closure": (
            closed["payload"]
            | {"event_id": closed["event_id"], "occurred_at": closed["occurred_at"]}
            if closed
            else None
        ),
        "outcome": outcome,
        "review_timing": {"eligible_when_resolved_count": 5},
        "attention_flags": boundary_flags(events),
        "events": events,
        "lineage": _verify_choice_rows(row, events),
        "authority_effect": AUTHORITY_EFFECT,
        "no_execution_authority": row["no_execution_authority"],
    }


def project_choice(connection: sqlite3.Connection, choice_id: str) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM choice_prompts WHERE choice_id=?", (choice_id,)
    ).fetchone()
    if not row:
        raise ChoiceError("choice does not exist")
    return _project_choice_rows(row, _events(connection, choice_id))


def boundary_flags(events: list[dict[str, Any]]) -> list[str]:
    flags: set[str] = set()
    for event in events:
        payload = event["payload"]
        for key, label in (
            ("authority_incident", "authority"),
            ("privacy_incident", "privacy"),
            ("safety_incident", "safety"),
            ("lane_incident", "lane-boundary"),
        ):
            if payload.get(key):
                flags.add(label)
    return sorted(flags)


def _verify_choice_rows(
    prompt: sqlite3.Row | dict[str, Any], events: list[dict[str, Any]]
) -> dict[str, Any]:
    failures: list[str] = []
    options = json.loads(prompt["options_json"])
    if digest(options) != prompt["options_hash"]:
        failures.append("immutable option-set identity mismatch")
    selection_events = [
        event for event in events if event["event_type"] == "branch_selected"
    ]
    if not events or events[0]["event_type"] != "branch_selected":
        failures.append("first event is not branch_selected")
    if len(selection_events) != 1:
        failures.append(
            f"expected exactly one branch_selected event, found {len(selection_events)}"
        )
    elif selection_events[0]["sequence"] != 1:
        failures.append("branch_selected event is not first")
    if selection_events:
        selection_payload = selection_events[0]["payload"]
        selected_option = next(
            (
                option
                for option in options
                if option["key"] == prompt["selected_key"]
            ),
            None,
        )
        if selection_payload.get("selected_key") != prompt["selected_key"]:
            failures.append("selection event key differs from immutable prompt")
        if selection_payload.get("options_hash") != prompt["options_hash"]:
            failures.append("selection event option identity differs from prompt")
        if (
            not selected_option
            or selection_payload.get("selected_role") != selected_option["role"]
        ):
            failures.append("selection event role differs from immutable prompt")
    previous_hash: str | None = None
    seen_events: dict[str, dict[str, Any]] = {}
    superseded_targets: set[str] = set()
    closure_sequences = [
        event["sequence"] for event in events if event["event_type"] == "branch_closed"
    ]
    outcome_sequences = [
        event["sequence"]
        for event in events
        if event["event_type"] in {"outcome_recorded", "corrected"}
        and event["payload"].get("result")
    ]
    if len(closure_sequences) > 1:
        failures.append("expected at most one branch_closed event")
    if closure_sequences and outcome_sequences and closure_sequences[0] > outcome_sequences[0]:
        failures.append("branch_closed event occurs after a recorded outcome")
    for expected, event in enumerate(events, start=1):
        if event["sequence"] != expected:
            failures.append(f"event ordering mismatch at sequence {expected}")
        if event["previous_hash"] != previous_hash:
            failures.append(f"prior-hash mismatch at sequence {expected}")
        calculated = event_hash(
            choice_id=event["choice_id"],
            sequence=event["sequence"],
            event_type=event["event_type"],
            occurred_at=event["occurred_at"],
            idempotency_key=event["idempotency_key"],
            payload_json=event["payload_json"],
            previous_hash=event["previous_hash"],
        )
        if event["event_hash"] != calculated:
            failures.append(f"event-hash mismatch at sequence {expected}")
        target_id = event["payload"].get("supersedes_event_id")
        if event["event_type"] in {"corrected", "superseded"}:
            target = seen_events.get(str(target_id))
            if not target:
                failures.append(
                    f"invalid supersession target at sequence {expected}"
                )
            elif target_id in superseded_targets:
                failures.append(
                    f"reused supersession target at sequence {expected}"
                )
            elif (
                event["event_type"] == "corrected"
                and target["event_type"] not in {"outcome_recorded", "corrected"}
            ):
                failures.append(
                    f"invalid correction target type at sequence {expected}"
                )
            if target:
                superseded_targets.add(str(target_id))
        elif target_id:
            failures.append(
                f"unexpected supersession target at sequence {expected}"
            )
        previous_hash = event["event_hash"]
        seen_events[event["event_id"]] = event
    return {
        "valid": not failures,
        "failures": failures,
        "event_count": expected if "expected" in locals() else 0,
    }


def verify_choice(connection: sqlite3.Connection, choice_id: str) -> dict[str, Any]:
    prompt = connection.execute(
        "SELECT * FROM choice_prompts WHERE choice_id=?", (choice_id,)
    ).fetchone()
    if not prompt:
        raise ChoiceError("choice does not exist")
    return _verify_choice_rows(prompt, _events(connection, choice_id))


def scoped_choices(
    connection: sqlite3.Connection, *, tenant: str, workspace: str, lane: str
) -> list[dict[str, Any]]:
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    order = (
        "selected_at_utc_us, choice_id"
        if version >= 2
        else "choice_id"
    )
    prompts = connection.execute(
        "SELECT * FROM choice_prompts "
        "WHERE tenant=? AND workspace=? AND lane=? "
        f"ORDER BY {order}",
        (tenant, workspace, lane),
    ).fetchall()
    if version == 1:
        prompts = sorted(
            prompts,
            key=lambda row: (timestamp_order_key(row["selected_at"]), row["choice_id"]),
        )
    event_rows = connection.execute(
        "SELECT choice_events.* FROM choice_events "
        "JOIN choice_prompts USING(choice_id) "
        "WHERE tenant=? AND workspace=? AND lane=? "
        "ORDER BY choice_events.choice_id, choice_events.sequence",
        (tenant, workspace, lane),
    ).fetchall()
    events_by_choice: dict[str, list[dict[str, Any]]] = {
        row["choice_id"]: [] for row in prompts
    }
    for event in _decode_event_rows(event_rows):
        events_by_choice[event["choice_id"]].append(event)
    return [
        _project_choice_rows(row, events_by_choice[row["choice_id"]])
        for row in prompts
    ]


def learning_context(
    connection: sqlite3.Connection,
    *,
    tenant: str,
    workspace: str,
    lane: str,
    choice_kind: str | None = None,
    consequence_level: str | None = None,
) -> dict[str, Any]:
    choices = scoped_choices(connection, tenant=tenant, workspace=workspace, lane=lane)
    comparable = [
        item
        for item in choices
        if item["current_state"] == "resolved"
        and (not choice_kind or item["choice"]["choice_kind"] == choice_kind)
        and (
            not consequence_level
            or item["choice"]["consequence_level"] == consequence_level
        )
    ]
    incidents = sorted(
        {flag for item in choices for flag in item["attention_flags"]}
    )
    role_outcomes: dict[str, list[str]] = {role: [] for role in ROLES}
    for item in comparable:
        selected = next(
            option
            for option in item["choice"]["options"]
            if option["key"] == item["choice"]["selected_key"]
        )
        role_outcomes[selected["role"]].append(item["outcome"]["result"])
    influence: dict[str, Any] | None = None
    if incidents:
        influence = {"kind": "boundary-guardrail", "incidents": incidents, "immediate": True}
    elif len(comparable) >= 3:
        favorable = {"successful", "mixed"}
        candidates = [
            role
            for role, results in role_outcomes.items()
            if sum(value in favorable for value in results) >= 2
            and not any(value == "unsuccessful" for value in results)
        ]
        if candidates:
            influence = {
                "kind": "outcome-supported-recommendation",
                "eligible_roles": candidates,
                "basis": "at least three comparable resolved outcomes and two consistent results",
            }
    return {
        "projection_version": PROJECTION_VERSION,
        "scope": {"tenant": tenant, "workspace": workspace, "lane": lane},
        "comparable_resolved_count": len(comparable),
        "evidence_strength": "thin" if len(comparable) < 3 else "eligible",
        "recommendation_influence": influence,
        "selection_frequency_used": False,
        "preserve_credible_overlooked_path": True,
        "unresolved_review_queue": [
            {
                "choice_id": item["choice"]["choice_id"],
                "selected_at": item["choice"]["selected_at"],
                "decision_summary": item["choice"]["decision_summary"],
            }
            for item in choices
            if item["current_state"] == "unresolved"
        ],
    }


def review_scorecard(
    connection: sqlite3.Connection, *, tenant: str, workspace: str, lane: str
) -> dict[str, Any]:
    choices = scoped_choices(connection, tenant=tenant, workspace=workspace, lane=lane)
    resolved = [item for item in choices if item["current_state"] == "resolved"]
    pilot = resolved[:5]

    def measures(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        outcomes = [item["outcome"] for item in items]

        def measure(field: str, favorable: str, signal: int) -> dict[str, Any]:
            observed = [item[field] for item in outcomes if item[field] != "Missing"]
            numerator = sum(value == favorable for value in observed)
            return {
                "numerator": numerator,
                "denominator": len(observed),
                "provisional_signal": numerator >= signal,
            }

        return {
            "lower_cognitive_load": measure("cognitive_load", "lower", 3),
            "advanced_momentum": measure("momentum", "advanced", 3),
            "new_useful_path_discovery": measure(
                "discovery_value", "new-useful-path", 1
            ),
        }

    def gaps(
        measured: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, int]]:
        return {
            name: {
                "observed": value["denominator"],
                "required": 3,
                "missing": 3 - value["denominator"],
            }
            for name, value in measured.items()
            if value["denominator"] < 3
        }

    pilot_primary = measures(pilot)
    pilot_observation_gaps = gaps(pilot_primary)
    pilot_complete = len(pilot) == 5 and not pilot_observation_gaps
    if len(pilot) < 5 or pilot_complete:
        cohort_stage = "pilot"
        cohort_target = 5
        cohort = pilot
    else:
        cohort_stage = "extension"
        cohort_target = 10
        cohort = resolved[:10]

    outcomes = [item["outcome"] for item in cohort]
    primary = measures(cohort)
    observation_gaps = gaps(primary)
    extension_trigger_gaps = (
        pilot_observation_gaps if cohort_stage == "extension" else {}
    )
    cohort_choice_ids = [item["choice"]["choice_id"] for item in cohort]
    cohort_choice_id_set = set(cohort_choice_ids)
    boundary_incident_sources = [
        {
            "choice_id": item["choice"]["choice_id"],
            "incidents": item["attention_flags"],
            "in_measurement_cohort": item["choice"]["choice_id"]
            in cohort_choice_id_set,
        }
        for item in choices
        if item["attention_flags"]
    ]
    incidents = sorted(
        {
            incident
            for source in boundary_incident_sources
            for incident in source["incidents"]
        }
    )
    observed_complete = not observation_gaps
    negative_count = sum(
        outcome["cognitive_load"] == "higher"
        or outcome["momentum"] == "stalled"
        or outcome["discovery_value"] == "not-useful"
        for outcome in outcomes
    )
    if incidents:
        assessment = "hold"
    elif len(pilot) < 5:
        assessment = "pending"
    elif cohort_stage == "extension" and len(cohort) < 10:
        assessment = "extend-to-ten"
    elif not observed_complete:
        assessment = "adjust"
    elif negative_count >= 2:
        assessment = "adjust"
    elif sum(item["provisional_signal"] for item in primary.values()) >= 2:
        assessment = "continue"
    else:
        assessment = "adjust"
    distribution = {
        result: sum(item["result"] == result for item in outcomes)
        for result in RESULTS
    }
    rework = [
        item["rework_minutes"]
        for item in outcomes
        if item["rework_minutes"] is not None
    ]
    return {
        "projection_kind": "review-scorecard",
        "projection_version": REVIEW_PROJECTION_VERSION,
        "assessment": assessment,
        "cohort_stage": cohort_stage,
        "cohort_target": cohort_target,
        "eligible_resolved": len(cohort),
        "needed": max(cohort_target - len(cohort), 0),
        "cohort_choice_ids": cohort_choice_ids,
        "primary_measures": primary,
        "observation_gaps": observation_gaps,
        "extension_trigger_gaps": extension_trigger_gaps,
        "result_distribution": distribution,
        "rework_summary": {
            "observed": len(rework),
            "total_minutes": sum(rework),
            "mean_minutes": (sum(rework) / len(rework)) if rework else None,
        },
        "repeated_negative_experience_count": negative_count,
        "boundary_incidents": incidents,
        "boundary_incident_sources": boundary_incident_sources,
        "selection_frequency_used": False,
        "note": (
            "Descriptive pilot evidence; comparable-outcome thresholds separately "
            "control recommendation changes."
        ),
    }


def markdown_projection(payload: dict[str, Any], title: str) -> str:
    lines = [f"# {title}", ""]
    if "choice" in payload:
        choice = payload["choice"]
        lines.extend(
            [
                f"- Choice: `{choice['choice_id']}`",
                f"- State: `{payload['current_state']}`",
                f"- Selected: `{choice['selected_key']}`",
                f"- Chain valid: `{str(payload['lineage']['valid']).lower()}`",
                "",
                "## Possibilities",
                "",
            ]
        )
        lines.extend(
            f"- `{item['key']}` (`{item['role']}`): {item['text']}"
            for item in choice["options"]
        )
        lines.extend(["", payload["no_execution_authority"]])
    elif "assessment" in payload:
        lines.extend(
            [
                f"- Assessment: `{payload['assessment']}`",
                f"- Projection: `{payload.get('projection_kind', 'review-scorecard')} "
                f"{payload['projection_version']}`",
                f"- Cohort: `{payload['eligible_resolved']}/{payload['cohort_target']}` "
                f"(`{payload['cohort_stage']}`)",
                f"- Remaining: `{payload['needed']}`",
                f"- Selection frequency used: `false`",
            ]
        )
        for name, value in payload.get("observation_gaps", {}).items():
            lines.append(
                f"- {name.replace('_', ' ').title()} gap: `{value['missing']}` "
                f"(`{value['observed']}/{value['required']}` observed)"
            )
        for name, value in payload.get("extension_trigger_gaps", {}).items():
            lines.append(
                f"- Extension trigger, {name.replace('_', ' ')}: "
                f"`{value['missing']}` missing at pilot "
                f"(`{value['observed']}/{value['required']}` observed)"
            )
        for source in payload.get("boundary_incident_sources", []):
            location = (
                "inside cohort"
                if source["in_measurement_cohort"]
                else "outside cohort"
            )
            lines.append(
                f"- Boundary incident: `{source['choice_id']}` "
                f"({', '.join(source['incidents'])}; {location})"
            )
        for name, value in payload.get("primary_measures", {}).items():
            lines.append(
                f"- {name.replace('_', ' ').title()}: "
                f"`{value['numerator']}/{value['denominator']}`"
            )
    else:
        lines.append("```json")
        lines.append(json.dumps(payload, indent=2, ensure_ascii=False))
        lines.append("```")
    return "\n".join(lines).rstrip() + "\n"


def unavailable_payload(
    reason: str,
    *,
    expected_retention: bool = False,
    retention_kind: str = "choice event",
) -> dict[str, Any]:
    return {
        "projection_version": PROJECTION_VERSION,
        "authority_effect": AUTHORITY_EFFECT,
        "retained": False,
        "available": False,
        "reason": reason,
        "disclosure": (
            f"{retention_kind.capitalize()} was not retained; ordinary work may continue."
            if expected_retention
            else "Private choice history is unavailable; ordinary work may continue."
        ),
        "no_execution_authority": NO_AUTHORITY,
    }


def add_scope(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tenant", default="local-operator")
    parser.add_argument("--workspace", default="narrative-systems")
    parser.add_argument("--lane", default="repository")


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Private, outcome-aware choice navigation ledger.")
    parser.add_argument("--db", help=f"Absolute private database path; alternatively set {DB_ENV}.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    subparsers = parser.add_subparsers(dest="command", required=True)

    context = subparsers.add_parser("context", help="Read bounded recommendation evidence.")
    add_scope(context)
    context.add_argument("--choice-kind")
    context.add_argument("--consequence-level")

    select = subparsers.add_parser("select", help="Atomically retain a selected branch.")
    add_scope(select)
    select.add_argument("--choice-id", required=True)
    select.add_argument("--options-json", required=True)
    select.add_argument("--selected-key", required=True)
    select.add_argument("--choice-kind", required=True)
    select.add_argument("--consequence-level", required=True)
    select.add_argument("--decision-summary", required=True)
    select.add_argument("--actor", default="operator")
    select.add_argument("--presented-at", required=True)
    select.add_argument("--selected-at", default=None)
    select.add_argument("--idempotency-key", required=True)
    select.add_argument("--learning-ref", action="append")
    select.add_argument("--success-signal", action="append")
    select.add_argument("--risk-signal", action="append")
    select.add_argument("--dry-run", action="store_true")

    outcome = subparsers.add_parser("outcome", help="Append an outcome or lifecycle event.")
    outcome.add_argument("--choice-id", required=True)
    outcome.add_argument("--event-type", choices=EVENT_TYPES[1:], default="outcome_recorded")
    outcome.add_argument("--idempotency-key", required=True)
    outcome.add_argument("--occurred-at", default=None)
    outcome.add_argument("--result", choices=RESULTS)
    outcome.add_argument("--cognitive-load", choices=COGNITIVE_LOAD, default="Missing")
    outcome.add_argument("--momentum", choices=MOMENTUM, default="Missing")
    outcome.add_argument("--discovery-value", choices=DISCOVERY, default="Missing")
    outcome.add_argument("--rework-minutes", type=int)
    outcome.add_argument("--evidence-ref")
    outcome.add_argument("--observation")
    outcome.add_argument("--authority-incident", action="store_true")
    outcome.add_argument("--privacy-incident", action="store_true")
    outcome.add_argument("--safety-incident", action="store_true")
    outcome.add_argument("--lane-incident", action="store_true")
    outcome.add_argument("--supersedes-event-id")
    outcome.add_argument("--dry-run", action="store_true")

    close = subparsers.add_parser(
        "close", help="Close a completed, paused, or saturated selected branch."
    )
    close.add_argument("--choice-id", required=True)
    close.add_argument("--reason", choices=CLOSURE_REASONS, required=True)
    close.add_argument("--idempotency-key", required=True)
    close.add_argument("--occurred-at", default=None)
    close.add_argument("--observation")
    close.add_argument("--dry-run", action="store_true")
    add_scope(close)

    review = subparsers.add_parser(
        "review", help="Read the deterministic staged five-to-ten scorecard."
    )
    add_scope(review)

    show = subparsers.add_parser("show", help="Project one choice and its event history.")
    show.add_argument("--choice-id", required=True)
    add_scope(show)

    verify = subparsers.add_parser("verify", help="Verify hashes and immutable choice identity.")
    verify.add_argument("--choice-id")
    add_scope(verify)

    backup = subparsers.add_parser("backup", help="Create a consistent private-store backup.")
    backup.add_argument("--to", required=True)
    backup_status = subparsers.add_parser(
        "backup-status", help="Compare a backup with the current logical store."
    )
    backup_status.add_argument("--backup", required=True)
    recover = subparsers.add_parser("recover", help="Recover a private store from a backup.")
    recover.add_argument("--from", dest="source", required=True)
    recover.add_argument("--to", required=True)
    recover.add_argument("--dry-run", action="store_true")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    args = parse_args(arguments)
    if args.command == "select" and args.dry_run:
        payload = {
            "dry_run": True,
            "retained": False,
            "sanitized_options": sanitize_options(parse_json_argument(args.options_json)),
            "selected_key": args.selected_key,
            "authority_effect": AUTHORITY_EFFECT,
            "no_execution_authority": NO_AUTHORITY,
        }
        print(
            markdown_projection(payload, "Choice Ledger Result")
            if args.format == "markdown"
            else json.dumps(payload, indent=2, ensure_ascii=False),
            end="" if args.format == "markdown" else "\n",
        )
        return 0
    if args.command == "outcome" and args.dry_run:
        payload = {
            "dry_run": True,
            "retained": False,
            "choice_id": args.choice_id,
            "event_type": args.event_type,
        }
        print(
            markdown_projection(payload, "Choice Ledger Result")
            if args.format == "markdown"
            else json.dumps(payload, indent=2, ensure_ascii=False),
            end="" if args.format == "markdown" else "\n",
        )
        return 0
    if args.command == "close" and args.dry_run:
        payload = {
            "dry_run": True,
            "retained": False,
            "choice_id": sanitize_text(args.choice_id, limit=120),
            "event_type": "branch_closed",
            "reason": args.reason,
            "observation": (
                sanitize_text(args.observation, limit=1000)
                if args.observation
                else None
            ),
            "authority_effect": AUTHORITY_EFFECT,
        }
        print(
            markdown_projection(payload, "Choice Ledger Result")
            if args.format == "markdown"
            else json.dumps(payload, indent=2, ensure_ascii=False),
            end="" if args.format == "markdown" else "\n",
        )
        return 0
    resolution = resolve_store(
        args.db,
        require_exists=args.command
        in {"context", "review", "show", "verify", "backup", "backup-status", "close"},
    )
    if args.command == "recover":
        payload = {"would_recover": args.dry_run, "from": args.source, "to": args.to}
        if not args.dry_run:
            recover_backup(Path(args.source), Path(args.to))
            payload["recovered"] = True
        print(json.dumps(payload, indent=2))
        return 0
    if resolution.path is None:
        payload = unavailable_payload(
            resolution.reason or "choice store unavailable",
            expected_retention=args.command in {"select", "outcome", "close"},
            retention_kind={
                "select": "selection",
                "outcome": "outcome",
                "close": "closure",
            }.get(args.command, "choice event"),
        )
        print(json.dumps(payload, indent=2))
        return 0 if args.command in {"context", "review", "select", "close"} else 2
    if args.command == "backup":
        destination = create_backup(resolution.path, Path(args.to))
        status = compare_backup(resolution.path, destination)
        print(
            json.dumps(
                {
                    "backed_up": True,
                    "path": str(destination),
                    "fresh": status["fresh"],
                    "logical_fingerprint": status["backup"]["logical_fingerprint"],
                },
                indent=2,
            )
        )
        return 0
    if args.command == "backup-status":
        print(
            json.dumps(
                compare_backup(resolution.path, Path(args.backup)),
                indent=2,
            )
        )
        return 0
    try:
        connection_factory = (
            connect_read_only if args.command in READ_ONLY_COMMANDS else connect
        )
        connection = connection_factory(resolution.path)
    except (OSError, sqlite3.OperationalError):
        if args.command not in GRACEFUL_CONNECTION_FAILURE_COMMANDS:
            raise
        payload = unavailable_payload(
            "private choice store could not be opened",
            expected_retention=args.command in {"select", "close"},
            retention_kind={"select": "selection", "close": "closure"}.get(
                args.command, "choice event"
            ),
        )
        print(json.dumps(payload, indent=2))
        return 0
    try:
        if args.command == "context":
            payload = learning_context(
                connection,
                tenant=args.tenant,
                workspace=args.workspace,
                lane=args.lane,
                choice_kind=args.choice_kind,
                consequence_level=args.consequence_level,
            )
        elif args.command == "select":
            payload = select_branch(
                connection,
                choice_id=args.choice_id,
                options=parse_json_argument(args.options_json),
                selected_key=args.selected_key,
                tenant=args.tenant,
                workspace=args.workspace,
                lane=args.lane,
                choice_kind=args.choice_kind,
                consequence_level=args.consequence_level,
                decision_summary=args.decision_summary,
                actor=args.actor,
                presented_at=args.presented_at,
                selected_at=args.selected_at or utc_now(),
                idempotency_key=args.idempotency_key,
                learning_refs=args.learning_ref,
                success_signals=args.success_signal,
                risk_signals=args.risk_signal,
            )
        elif args.command == "outcome":
            payload = append_choice_event(
                connection,
                choice_id=args.choice_id,
                event_type=args.event_type,
                idempotency_key=args.idempotency_key,
                occurred_at=args.occurred_at or utc_now(),
                result=args.result,
                cognitive_load=args.cognitive_load,
                momentum=args.momentum,
                discovery_value=args.discovery_value,
                rework_minutes=args.rework_minutes,
                evidence_ref=args.evidence_ref,
                observation=args.observation,
                authority_incident=args.authority_incident,
                privacy_incident=args.privacy_incident,
                safety_incident=args.safety_incident,
                lane_incident=args.lane_incident,
                supersedes_event_id=args.supersedes_event_id,
            )
        elif args.command == "close":
            payload = close_branch(
                connection,
                choice_id=args.choice_id,
                reason=args.reason,
                idempotency_key=args.idempotency_key,
                occurred_at=args.occurred_at or utc_now(),
                observation=args.observation,
                tenant=args.tenant,
                workspace=args.workspace,
                lane=args.lane,
            )
        elif args.command == "review":
            payload = review_scorecard(
                connection,
                tenant=args.tenant,
                workspace=args.workspace,
                lane=args.lane,
            )
        elif args.command == "show":
            payload = project_choice(connection, args.choice_id)
            scope = payload["choice"]
            if (scope["tenant"], scope["workspace"], scope["lane"]) != (
                args.tenant,
                args.workspace,
                args.lane,
            ):
                raise ChoiceError(
                    "choice is outside the requested tenant/workspace/lane scope"
                )
        else:
            if args.choice_id:
                projection = project_choice(connection, args.choice_id)
                scoped = projection["choice"]
                if (scoped["tenant"], scoped["workspace"], scoped["lane"]) != (
                    args.tenant,
                    args.workspace,
                    args.lane,
                ):
                    raise ChoiceError(
                        "choice is outside the requested tenant/workspace/lane scope"
                    )
                results = {args.choice_id: projection["lineage"]}
            else:
                results = {
                    item["choice"]["choice_id"]: item["lineage"]
                    for item in scoped_choices(
                        connection,
                        tenant=args.tenant,
                        workspace=args.workspace,
                        lane=args.lane,
                    )
                }
            payload = {
                "projection_version": PROJECTION_VERSION,
                "valid": all(item["valid"] for item in results.values()),
                "choices": results,
            }
    finally:
        connection.close()
    if args.format == "markdown":
        title = {
            "context": "Choice Learning Context",
            "review": "Staged Five-to-Ten Review",
            "show": "Choice Projection",
            "verify": "Choice Chain Verification",
        }.get(args.command, "Choice Ledger Result")
        print(markdown_projection(payload, title), end="")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ChoiceError, json.JSONDecodeError, sqlite3.Error) as error:
        print(f"choice_error={error}", file=sys.stderr)
        raise SystemExit(2)

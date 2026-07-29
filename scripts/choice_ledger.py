from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
PROJECTION_VERSION = "1.0"
DB_ENV = "NARRATIVE_CHOICE_DB"
REPO_ROOT = Path(__file__).resolve().parent.parent
ROLES = ("recommended", "alternative", "overlooked", "pause-or-deepen")
EVENT_TYPES = (
    "branch_selected",
    "outcome_recorded",
    "review_deferred",
    "corrected",
    "superseded",
)
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
    "Branch selection grants no execution, mutation, spending, publication, "
    "communication, customer action, commit, push, or deployment authority."
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
    configured = raw_path or os.environ.get(DB_ENV)
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
    if candidate.is_file():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return json.loads(value)


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA synchronous = FULL")
    migrate(connection)
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
                        'branch_selected', 'outcome_recorded', 'review_deferred',
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


def create_backup(path: Path, destination: Path) -> Path:
    source_path = require_private_path(path, label="choice store")
    destination_path = require_private_path(destination, label="backup")
    if not source_path.is_file():
        raise ChoiceError("cannot back up a missing choice store")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(source_path)
    target = sqlite3.connect(destination_path)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    return destination_path


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


def _events(connection: sqlite3.Connection, choice_id: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT * FROM choice_events WHERE choice_id=? ORDER BY sequence", (choice_id,)
    ).fetchall()
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


def project_choice(connection: sqlite3.Connection, choice_id: str) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM choice_prompts WHERE choice_id=?", (choice_id,)
    ).fetchone()
    if not row:
        raise ChoiceError("choice does not exist")
    events = _events(connection, choice_id)
    superseded = any(item["event_type"] == "superseded" for item in events)
    outcome = _current_outcome(events)
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
        "current_state": "superseded" if superseded else ("resolved" if outcome else "unresolved"),
        "outcome": outcome,
        "review_timing": {"eligible_when_resolved_count": 5},
        "attention_flags": boundary_flags(events),
        "events": events,
        "lineage": verify_choice(connection, choice_id),
        "no_execution_authority": row["no_execution_authority"],
    }


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


def verify_choice(connection: sqlite3.Connection, choice_id: str) -> dict[str, Any]:
    prompt = connection.execute(
        "SELECT * FROM choice_prompts WHERE choice_id=?", (choice_id,)
    ).fetchone()
    if not prompt:
        raise ChoiceError("choice does not exist")
    failures: list[str] = []
    options = json.loads(prompt["options_json"])
    if digest(options) != prompt["options_hash"]:
        failures.append("immutable option-set identity mismatch")
    events = _events(connection, choice_id)
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
    return {"valid": not failures, "failures": failures, "event_count": expected if "expected" in locals() else 0}


def scoped_choices(
    connection: sqlite3.Connection, *, tenant: str, workspace: str, lane: str
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT choice_id FROM choice_prompts
        WHERE tenant=? AND workspace=? AND lane=?
        ORDER BY selected_at, choice_id
        """,
        (tenant, workspace, lane),
    ).fetchall()
    return [project_choice(connection, row["choice_id"]) for row in rows]


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
    eligible = [item for item in choices if item["current_state"] == "resolved"][:5]
    if len(eligible) < 5:
        return {
            "projection_version": PROJECTION_VERSION,
            "assessment": "pending",
            "eligible_resolved": len(eligible),
            "needed": 5 - len(eligible),
            "selection_frequency_used": False,
        }
    outcomes = [item["outcome"] for item in eligible]

    def measure(field: str, favorable: str, signal: int) -> dict[str, Any]:
        observed = [item[field] for item in outcomes if item[field] != "Missing"]
        numerator = sum(value == favorable for value in observed)
        return {
            "numerator": numerator,
            "denominator": len(observed),
            "provisional_signal": numerator >= signal,
        }

    primary = {
        "lower_cognitive_load": measure("cognitive_load", "lower", 3),
        "advanced_momentum": measure("momentum", "advanced", 3),
        "new_useful_path_discovery": measure(
            "discovery_value", "new-useful-path", 1
        ),
    }
    incidents = sorted({flag for item in eligible for flag in item["attention_flags"]})
    observed_complete = all(item["denominator"] >= 3 for item in primary.values())
    negative_count = sum(
        outcome["cognitive_load"] == "higher"
        or outcome["momentum"] == "stalled"
        or outcome["discovery_value"] == "not-useful"
        for outcome in outcomes
    )
    if incidents:
        assessment = "hold"
    elif not observed_complete:
        assessment = "extend-to-ten"
    elif negative_count >= 2:
        assessment = "adjust"
    elif sum(item["provisional_signal"] for item in primary.values()) >= 2:
        assessment = "continue"
    else:
        assessment = "adjust"
    distribution = {result: sum(item["result"] == result for item in outcomes) for result in RESULTS}
    rework = [item["rework_minutes"] for item in outcomes if item["rework_minutes"] is not None]
    return {
        "projection_version": PROJECTION_VERSION,
        "assessment": assessment,
        "cohort_choice_ids": [item["choice"]["choice_id"] for item in eligible],
        "primary_measures": primary,
        "result_distribution": distribution,
        "rework_summary": {
            "observed": len(rework),
            "total_minutes": sum(rework),
            "mean_minutes": (sum(rework) / len(rework)) if rework else None,
        },
        "repeated_negative_experience_count": negative_count,
        "boundary_incidents": incidents,
        "selection_frequency_used": False,
        "note": "Descriptive pilot evidence; comparable-outcome thresholds separately control recommendation changes.",
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
                f"- Eligible resolved: `{payload.get('eligible_resolved', 5)}`",
                f"- Selection frequency used: `false`",
            ]
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


def unavailable_payload(reason: str, *, expected_retention: bool = False) -> dict[str, Any]:
    return {
        "projection_version": PROJECTION_VERSION,
        "retained": False,
        "available": False,
        "reason": reason,
        "disclosure": (
            "Selection was not retained; navigation may continue."
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

    review = subparsers.add_parser("review", help="Read the deterministic five-selection scorecard.")
    add_scope(review)

    show = subparsers.add_parser("show", help="Project one choice and its event history.")
    show.add_argument("--choice-id", required=True)
    add_scope(show)

    verify = subparsers.add_parser("verify", help="Verify hashes and immutable choice identity.")
    verify.add_argument("--choice-id")
    add_scope(verify)

    backup = subparsers.add_parser("backup", help="Create a consistent private-store backup.")
    backup.add_argument("--to", required=True)
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
    resolution = resolve_store(args.db, require_exists=args.command in {"context", "review", "show", "verify", "backup"})
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
            expected_retention=args.command in {"select", "outcome"},
        )
        print(json.dumps(payload, indent=2))
        return 0 if args.command in {"context", "review", "select"} else 2
    if args.command == "backup":
        destination = create_backup(resolution.path, Path(args.to))
        print(json.dumps({"backed_up": True, "path": str(destination)}, indent=2))
        return 0
    connection = connect(resolution.path)
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
                scoped = project_choice(connection, args.choice_id)["choice"]
                if (scoped["tenant"], scoped["workspace"], scoped["lane"]) != (
                    args.tenant,
                    args.workspace,
                    args.lane,
                ):
                    raise ChoiceError(
                        "choice is outside the requested tenant/workspace/lane scope"
                    )
            choice_ids = (
                [args.choice_id]
                if args.choice_id
                else [
                    row["choice_id"]
                    for row in connection.execute(
                        "SELECT choice_id FROM choice_prompts "
                        "WHERE tenant=? AND workspace=? AND lane=? "
                        "ORDER BY selected_at",
                        (args.tenant, args.workspace, args.lane),
                    )
                ]
            )
            results = {
                choice_id: verify_choice(connection, choice_id)
                for choice_id in choice_ids
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
            "review": "Five-Selection Review",
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

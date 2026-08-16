from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DB_ENV = "MIRA_MENTORSHIP_DB"
SCHEMA_VERSION = 1
AUTHORITY_EFFECT = "none"
LIFECYCLES = {"proposed", "active", "paused", "completed", "withdrawn"}
TERMINAL_LIFECYCLES = {"completed", "withdrawn"}
ASSERTION_BASES = {"observed", "learner-reported", "inferred", "missing"}
PROGRESS_STATES = {"observed", "not-observed", "insufficient-evidence"}
PROGRESS_DIMENSIONS = {
    "explanation",
    "hypothesis-testing",
    "debugging",
    "uncertainty-recognition",
    "agent-challenge",
    "independent-action",
    "maintenance",
}
INTERVENTIONS = {
    "learner-model",
    "evidence-prompt",
    "conceptual-hint",
    "analogous-demonstration",
    "narrated-pairing",
    "authorized-direct-implementation",
    "temporary-takeover",
}
EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d ()-]{7,}\d)(?!\d)")
SECRET_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|password|secret|private[_-]?key)\s*[:=]\s*\S+"
)
SENSITIVE_RE = re.compile(
    r"(?i)\b(?:diagnos(?:is|ed)|bipolar|depress(?:ion|ed)|autis(?:m|tic)|"
    r"adhd|trauma|personality disorder|iq score|psychopath|narcissist)\b"
)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")


class MentorError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise MentorError(f"invalid timestamp: {value}") from error
    if parsed.tzinfo is None:
        raise MentorError("timestamps must include a timezone")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    raw = value if isinstance(value, str) else canonical_json(value)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def require_id(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not ID_RE.fullmatch(text):
        raise MentorError(f"{label} must be a bounded pseudonymous identifier")
    return text


def sanitize_text(value: Any, label: str, *, limit: int = 500) -> str:
    text = CONTROL_RE.sub("", str(value or "")).strip()
    if not text:
        raise MentorError(f"{label} is required")
    if "\n" in text or "\r" in text:
        raise MentorError(f"{label} must be a bounded statement, not a raw body")
    if len(text) > limit:
        raise MentorError(f"{label} exceeds {limit} characters")
    if SECRET_RE.search(text):
        raise MentorError(f"{label} appears to contain a credential or secret")
    if EMAIL_RE.search(text) or PHONE_RE.search(text):
        raise MentorError(f"{label} contains direct contact data")
    if SENSITIVE_RE.search(text):
        raise MentorError(f"{label} appears to contain sensitive biography or a psychological label")
    return text


def sanitize_list(values: Any, label: str, *, limit: int = 20) -> list[str]:
    if not isinstance(values, list) or len(values) > limit:
        raise MentorError(f"{label} must be a list of at most {limit} items")
    return [sanitize_text(value, f"{label} item") for value in values]


def sanitize_assertions(values: Any, label: str) -> list[dict[str, str]]:
    if not isinstance(values, list) or len(values) > 20:
        raise MentorError(f"{label} must be a list of at most 20 assertions")
    result = []
    for item in values:
        if not isinstance(item, dict) or item.get("basis") not in ASSERTION_BASES:
            raise MentorError(f"each {label} assertion requires a valid basis")
        result.append(
            {
                "basis": item["basis"],
                "statement": sanitize_text(item.get("statement"), f"{label} statement"),
            }
        )
    return result


def sanitize_progress(value: Any) -> dict[str, dict[str, str]]:
    if not isinstance(value, dict) or set(value) - PROGRESS_DIMENSIONS:
        raise MentorError("progress contains an unsupported dimension")
    result: dict[str, dict[str, str]] = {}
    for dimension, item in value.items():
        if not isinstance(item, dict):
            raise MentorError(f"progress {dimension} must be an object")
        if item.get("status") not in PROGRESS_STATES or item.get("basis") not in ASSERTION_BASES:
            raise MentorError(f"progress {dimension} requires valid status and basis")
        result[dimension] = {
            "status": item["status"],
            "basis": item["basis"],
            "statement": sanitize_text(item.get("statement"), f"progress {dimension}"),
        }
    return result


def private_path(raw: str | Path) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise MentorError("mentorship store path must be absolute")
    resolved = path.resolve(strict=False)
    if resolved == REPO_ROOT.resolve() or resolved.is_relative_to(REPO_ROOT.resolve()):
        raise MentorError("mentorship store must be outside Git")
    return resolved


def resolve_store(raw: str | None, *, require_exists: bool = False) -> Path:
    configured = raw or os.environ.get(DB_ENV)
    if not configured:
        raise MentorError(f"private mentorship store is not configured; set {DB_ENV} or pass --db")
    path = private_path(configured)
    if require_exists and not path.is_file():
        raise MentorError(f"private mentorship store does not exist: {path}")
    return path


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA journal_mode=DELETE")
    connection.execute("PRAGMA synchronous=FULL")
    migrate(connection)
    return connection


def connect_read_only(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def migrate(connection: sqlite3.Connection) -> None:
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if version > SCHEMA_VERSION:
        raise MentorError(f"mentorship store schema {version} is newer than supported {SCHEMA_VERSION}")
    if version == 0:
        with connection:
            connection.executescript(
                """
                CREATE TABLE relationships (
                    relationship_id TEXT PRIMARY KEY,
                    opened_at TEXT NOT NULL,
                    authority_owner TEXT NOT NULL,
                    authority_ref TEXT NOT NULL,
                    participants_json TEXT NOT NULL,
                    developmental_purpose TEXT NOT NULL,
                    work_objective TEXT NOT NULL,
                    repository_refs_json TEXT NOT NULL,
                    privacy_class TEXT NOT NULL,
                    consent_json TEXT NOT NULL,
                    initial_lifecycle TEXT NOT NULL,
                    record_hash TEXT NOT NULL
                );
                CREATE TABLE mentorship_events (
                    event_id TEXT PRIMARY KEY,
                    relationship_id TEXT NOT NULL REFERENCES relationships(relationship_id),
                    sequence INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    UNIQUE(relationship_id, sequence),
                    UNIQUE(relationship_id, idempotency_key)
                );
                CREATE TRIGGER relationships_no_update BEFORE UPDATE ON relationships
                BEGIN SELECT RAISE(ABORT, 'relationships are immutable'); END;
                CREATE TRIGGER relationships_no_delete BEFORE DELETE ON relationships
                BEGIN SELECT RAISE(ABORT, 'relationships are immutable'); END;
                CREATE TRIGGER mentorship_events_no_update BEFORE UPDATE ON mentorship_events
                BEGIN SELECT RAISE(ABORT, 'mentorship events are append-only'); END;
                CREATE TRIGGER mentorship_events_no_delete BEFORE DELETE ON mentorship_events
                BEGIN SELECT RAISE(ABORT, 'mentorship events are append-only'); END;
                PRAGMA user_version=1;
                """
            )


def load_json(path: str) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise MentorError("input must be a JSON object")
    return value


def normalize_open(raw: dict[str, Any]) -> dict[str, Any]:
    consent = raw.get("consent")
    if not isinstance(consent, dict) or consent.get("retention") is not True:
        raise MentorError("relationship-level retention consent must be explicitly true")
    participants = raw.get("participants")
    if not isinstance(participants, list) or not participants or len(participants) > 10:
        raise MentorError("participants must contain one to ten pseudonymous participants")
    normalized_participants = []
    for item in participants:
        if not isinstance(item, dict) or item.get("role") not in {"human", "agent"}:
            raise MentorError("each participant requires an id and human or agent role")
        normalized_participants.append({"id": require_id(item.get("id"), "participant id"), "role": item["role"]})
    repositories = sanitize_list(raw.get("repository_refs", []), "repository_refs")
    return {
        "relationship_id": require_id(raw.get("relationship_id"), "relationship_id"),
        "opened_at": validate_timestamp(str(raw.get("opened_at") or utc_now())),
        "authority_owner": require_id(raw.get("authority_owner"), "authority_owner"),
        "authority_ref": sanitize_text(raw.get("authority_ref"), "authority_ref"),
        "participants": normalized_participants,
        "developmental_purpose": sanitize_text(raw.get("developmental_purpose"), "developmental_purpose"),
        "work_objective": sanitize_text(raw.get("work_objective"), "work_objective"),
        "repository_refs": repositories,
        "privacy_class": sanitize_text(raw.get("privacy_class", "private"), "privacy_class", limit=40),
        "consent": {
            "retention": True,
            "authorized_at": validate_timestamp(str(consent.get("authorized_at") or utc_now())),
            "authority_ref": sanitize_text(consent.get("authority_ref"), "consent authority_ref"),
        },
        "initial_lifecycle": raw.get("lifecycle", "active"),
        "reopen": raw.get("reopen") is True,
        "idempotency_key": require_id(raw.get("idempotency_key", "relationship-open"), "idempotency_key"),
    }


def normalize_session(raw: dict[str, Any]) -> dict[str, Any]:
    intervention = raw.get("mentor_intervention")
    if not isinstance(intervention, dict) or intervention.get("class") not in INTERVENTIONS:
        raise MentorError("mentor_intervention requires a valid class")
    return {
        "relationship_id": require_id(raw.get("relationship_id"), "relationship_id"),
        "event_id": require_id(raw.get("event_id"), "event_id"),
        "idempotency_key": require_id(raw.get("idempotency_key"), "idempotency_key"),
        "occurred_at": validate_timestamp(str(raw.get("occurred_at") or utc_now())),
        "learner_attempt": sanitize_assertions(raw.get("learner_attempt", []), "learner_attempt"),
        "agent_behavior": sanitize_assertions(raw.get("agent_behavior", []), "agent_behavior"),
        "mentor_intervention": {
            "class": intervention["class"],
            "assertions": sanitize_assertions(intervention.get("assertions", []), "mentor_intervention"),
        },
        "evidence_refs": sanitize_list(raw.get("evidence_refs", []), "evidence_refs"),
        "progress": sanitize_progress(raw.get("progress", {})),
        "next_challenge": sanitize_text(raw.get("next_challenge"), "next_challenge"),
        "work_status": sanitize_text(raw.get("work_status"), "work_status", limit=100),
        "mutation_status": sanitize_text(raw.get("mutation_status"), "mutation_status", limit=100),
    }


def relationship_row(connection: sqlite3.Connection, relationship_id: str) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM relationships WHERE relationship_id=?", (relationship_id,)).fetchone()
    if row is None:
        raise MentorError(f"unknown relationship: {relationship_id}")
    return row


def events(connection: sqlite3.Connection, relationship_id: str) -> list[sqlite3.Row]:
    return connection.execute(
        "SELECT * FROM mentorship_events WHERE relationship_id=? ORDER BY sequence", (relationship_id,)
    ).fetchall()


def lifecycle(connection: sqlite3.Connection, relationship_id: str) -> str:
    state = relationship_row(connection, relationship_id)["initial_lifecycle"]
    for row in events(connection, relationship_id):
        if row["event_type"] == "paused":
            state = "paused"
        elif row["event_type"] == "closed":
            state = json.loads(row["payload_json"])["lifecycle"]
        elif row["event_type"] == "reopened":
            state = "active"
    return state


def append_event(connection: sqlite3.Connection, relationship_id: str, event_id: str, event_type: str, occurred_at: str, idempotency_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    prior = events(connection, relationship_id)
    duplicate = connection.execute(
        "SELECT * FROM mentorship_events WHERE relationship_id=? AND idempotency_key=?",
        (relationship_id, idempotency_key),
    ).fetchone()
    payload_json = canonical_json(payload)
    if duplicate:
        if duplicate["event_type"] != event_type or duplicate["payload_json"] != payload_json:
            raise MentorError("idempotency key was already used with different content")
        return {"status": "idempotent", "event_id": duplicate["event_id"]}
    sequence = len(prior) + 1
    previous_hash = prior[-1]["event_hash"] if prior else relationship_row(connection, relationship_id)["record_hash"]
    event_hash = digest({"event_id": event_id, "relationship_id": relationship_id, "sequence": sequence, "event_type": event_type, "occurred_at": occurred_at, "payload": payload, "previous_hash": previous_hash})
    connection.execute(
        "INSERT INTO mentorship_events VALUES (?,?,?,?,?,?,?,?,?)",
        (event_id, relationship_id, sequence, event_type, occurred_at, idempotency_key, payload_json, previous_hash, event_hash),
    )
    return {"status": "recorded", "event_id": event_id, "sequence": sequence, "event_hash": event_hash}


def validate_evidence_scope(connection: sqlite3.Connection, relationship_id: str, references: list[str]) -> None:
    allowed = json.loads(relationship_row(connection, relationship_id)["repository_refs_json"])
    for reference in references:
        if not any(reference == root or reference.startswith(root + "@") or reference.startswith(root + "/") for root in allowed):
            raise MentorError("evidence reference falls outside this relationship's repository boundary")


def open_relationship(connection: sqlite3.Connection, data: dict[str, Any]) -> dict[str, Any]:
    if data["initial_lifecycle"] not in {"proposed", "active"}:
        raise MentorError("a relationship must open as proposed or active")
    existing = connection.execute("SELECT * FROM relationships WHERE relationship_id=?", (data["relationship_id"],)).fetchone()
    if existing:
        if not data["reopen"]:
            record = {key: data[key] for key in ("relationship_id", "opened_at", "authority_owner", "authority_ref", "participants", "developmental_purpose", "work_objective", "repository_refs", "privacy_class", "consent", "initial_lifecycle")}
            if digest(record) == existing["record_hash"]:
                return {"status": "idempotent", "relationship_id": data["relationship_id"], "record_hash": existing["record_hash"]}
            raise MentorError("relationship already exists with different content; reopening must be explicit")
        if lifecycle(connection, data["relationship_id"]) not in {"proposed", "paused", "completed", "withdrawn"}:
            raise MentorError("only proposed, paused, or closed relationships may be activated or reopened")
        event_id = "REOPEN-" + digest({"relationship": data["relationship_id"], "key": data["idempotency_key"]})[:16]
        return append_event(connection, data["relationship_id"], event_id, "reopened", data["opened_at"], data["idempotency_key"], {"authority_ref": data["authority_ref"]})
    record = {key: data[key] for key in ("relationship_id", "opened_at", "authority_owner", "authority_ref", "participants", "developmental_purpose", "work_objective", "repository_refs", "privacy_class", "consent", "initial_lifecycle")}
    record_hash = digest(record)
    connection.execute(
        "INSERT INTO relationships VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (data["relationship_id"], data["opened_at"], data["authority_owner"], data["authority_ref"], canonical_json(data["participants"]), data["developmental_purpose"], data["work_objective"], canonical_json(data["repository_refs"]), data["privacy_class"], canonical_json(data["consent"]), data["initial_lifecycle"], record_hash),
    )
    return {"status": "opened", "relationship_id": data["relationship_id"], "record_hash": record_hash}


def project(connection: sqlite3.Connection, relationship_id: str) -> dict[str, Any]:
    row = relationship_row(connection, relationship_id)
    event_rows = events(connection, relationship_id)
    return {
        "schema_version": SCHEMA_VERSION,
        "relationship": {
            "relationship_id": row["relationship_id"],
            "opened_at": row["opened_at"],
            "authority_owner": row["authority_owner"],
            "participants": json.loads(row["participants_json"]),
            "developmental_purpose": row["developmental_purpose"],
            "work_objective": row["work_objective"],
            "repository_refs": json.loads(row["repository_refs_json"]),
            "privacy_class": row["privacy_class"],
            "lifecycle": lifecycle(connection, relationship_id),
        },
        "events": [{"event_id": item["event_id"], "event_type": item["event_type"], "occurred_at": item["occurred_at"], "payload": json.loads(item["payload_json"])} for item in event_rows],
        "authority_effect": AUTHORITY_EFFECT,
    }


def verify(connection: sqlite3.Connection, relationship_id: str | None = None) -> dict[str, Any]:
    ids = [relationship_id] if relationship_id else [row[0] for row in connection.execute("SELECT relationship_id FROM relationships ORDER BY relationship_id")]
    failures = []
    for item_id in ids:
        row = relationship_row(connection, item_id)
        record = {"relationship_id": row["relationship_id"], "opened_at": row["opened_at"], "authority_owner": row["authority_owner"], "authority_ref": row["authority_ref"], "participants": json.loads(row["participants_json"]), "developmental_purpose": row["developmental_purpose"], "work_objective": row["work_objective"], "repository_refs": json.loads(row["repository_refs_json"]), "privacy_class": row["privacy_class"], "consent": json.loads(row["consent_json"]), "initial_lifecycle": row["initial_lifecycle"]}
        previous = digest(record)
        if previous != row["record_hash"]:
            failures.append(f"{item_id}: relationship hash mismatch")
        for event in events(connection, item_id):
            payload = json.loads(event["payload_json"])
            expected = digest({"event_id": event["event_id"], "relationship_id": item_id, "sequence": event["sequence"], "event_type": event["event_type"], "occurred_at": event["occurred_at"], "payload": payload, "previous_hash": previous})
            if event["previous_hash"] != previous or event["event_hash"] != expected:
                failures.append(f"{item_id}: event chain mismatch at {event['event_id']}")
            previous = event["event_hash"]
    return {"valid": not failures, "relationships_checked": len(ids), "failures": failures, "authority_effect": AUTHORITY_EFFECT}


def emit(payload: dict[str, Any], output_format: str = "json") -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    relationship = payload.get("relationship", {})
    print(f"Relationship: {relationship.get('relationship_id', 'n/a')}")
    print(f"Developmental objective: {relationship.get('developmental_purpose', 'n/a')}")
    print(f"Lifecycle: {relationship.get('lifecycle', 'n/a')}")
    print(f"Recorded events: {len(payload.get('events', []))}")
    print(f"Authority effect: {payload.get('authority_effect', AUTHORITY_EFFECT)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Private Mira mentorship ledger")
    parser.add_argument("--db")
    sub = parser.add_subparsers(dest="group", required=True)
    relationship = sub.add_parser("relationship")
    relationship_sub = relationship.add_subparsers(dest="action", required=True)
    opening = relationship_sub.add_parser("open")
    opening.add_argument("--input", required=True)
    opening.add_argument("--check", action="store_true")
    for action in ("pause", "close"):
        item = relationship_sub.add_parser(action)
        item.add_argument("--input", required=True)
        item.add_argument("--check", action="store_true")
    session = sub.add_parser("session")
    session_sub = session.add_subparsers(dest="action", required=True)
    record = session_sub.add_parser("record")
    record.add_argument("--input", required=True)
    record.add_argument("--check", action="store_true")
    correction = sub.add_parser("correct")
    correction.add_argument("--input", required=True)
    correction.add_argument("--check", action="store_true")
    for command in ("show", "review"):
        item = sub.add_parser(command)
        item.add_argument("--relationship", required=True)
        item.add_argument("--format", choices=("text", "json"), default="json")
    checking = sub.add_parser("verify")
    checking.add_argument("--relationship")
    checking.add_argument("--format", choices=("text", "json"), default="json")
    return parser


def normalize_lifecycle(raw: dict[str, Any], action: str) -> dict[str, Any]:
    lifecycle_value = raw.get("lifecycle", "completed" if action == "close" else "paused")
    if action == "pause" and lifecycle_value != "paused":
        raise MentorError("pause lifecycle must be paused")
    if action == "close" and lifecycle_value not in TERMINAL_LIFECYCLES:
        raise MentorError("close lifecycle must be completed or withdrawn")
    return {
        "relationship_id": require_id(raw.get("relationship_id"), "relationship_id"),
        "event_id": require_id(raw.get("event_id"), "event_id"),
        "idempotency_key": require_id(raw.get("idempotency_key"), "idempotency_key"),
        "occurred_at": validate_timestamp(str(raw.get("occurred_at") or utc_now())),
        "lifecycle": lifecycle_value,
        "reason": sanitize_text(raw.get("reason"), "reason"),
        "authority_ref": sanitize_text(raw.get("authority_ref"), "authority_ref"),
    }


def normalize_correction(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "relationship_id": require_id(raw.get("relationship_id"), "relationship_id"),
        "event_id": require_id(raw.get("event_id"), "event_id"),
        "idempotency_key": require_id(raw.get("idempotency_key"), "idempotency_key"),
        "occurred_at": validate_timestamp(str(raw.get("occurred_at") or utc_now())),
        "target_event_id": require_id(raw.get("target_event_id"), "target_event_id"),
        "reason": sanitize_text(raw.get("reason"), "reason"),
        "replacement": sanitize_assertions(raw.get("replacement", []), "replacement"),
        "authority_ref": sanitize_text(raw.get("authority_ref"), "authority_ref"),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.group in {"show", "review", "verify"}:
            path = resolve_store(args.db, require_exists=True)
            with connect_read_only(path) as connection:
                result = verify(connection, args.relationship) if args.group == "verify" else project(connection, require_id(args.relationship, "relationship"))
            emit(result, args.format)
            return 0 if result.get("valid", True) else 1

        raw = load_json(args.input)
        if args.group == "relationship" and args.action == "open":
            data, event_type = normalize_open(raw), "open"
        elif args.group == "session":
            data, event_type = normalize_session(raw), "session-recorded"
        elif args.group == "relationship":
            data, event_type = normalize_lifecycle(raw, args.action), "paused" if args.action == "pause" else "closed"
        else:
            data, event_type = normalize_correction(raw), "corrected"
        path = resolve_store(args.db)
        if args.check:
            emit({"valid": True, "check": True, "operation": event_type, "relationship_id": data["relationship_id"], "store": str(path), "authority_effect": AUTHORITY_EFFECT})
            return 0
        with connect(path) as connection:
            with connection:
                if event_type == "open":
                    result = open_relationship(connection, data)
                else:
                    current = lifecycle(connection, data["relationship_id"])
                    if event_type == "session-recorded" and current != "active":
                        raise MentorError("sessions may be recorded only for active relationships")
                    if event_type == "session-recorded":
                        validate_evidence_scope(connection, data["relationship_id"], data["evidence_refs"])
                    if event_type == "paused" and current != "active":
                        raise MentorError("only active relationships may be paused")
                    if event_type == "closed" and current not in {"active", "paused"}:
                        raise MentorError("only active or paused relationships may be closed")
                    if event_type == "corrected":
                        target = connection.execute("SELECT 1 FROM mentorship_events WHERE relationship_id=? AND event_id=?", (data["relationship_id"], data["target_event_id"])).fetchone()
                        if not target:
                            raise MentorError("correction target does not belong to this relationship")
                    payload = {key: value for key, value in data.items() if key not in {"relationship_id", "event_id", "idempotency_key", "occurred_at"}}
                    result = append_event(connection, data["relationship_id"], data["event_id"], event_type, data["occurred_at"], data["idempotency_key"], payload)
        result.update({"relationship_id": data["relationship_id"], "authority_effect": AUTHORITY_EFFECT})
        emit(result)
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, sqlite3.Error, MentorError) as error:
        print(f"mira-mentor error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

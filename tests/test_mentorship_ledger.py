import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import mentorship_ledger as ledger


def open_input() -> dict:
    return {
        "relationship_id": "REL-hannah-agent",
        "opened_at": "2026-08-15T12:00:00+00:00",
        "authority_owner": "hannah",
        "authority_ref": "operator-request-001",
        "participants": [{"id": "hannah", "role": "human"}, {"id": "hannah-agent", "role": "agent"}],
        "developmental_purpose": "Build independent frontend design and debugging judgment.",
        "work_objective": "Create a biographical and career landing page.",
        "repository_refs": ["github:hdong0424/agency-proposal-ai"],
        "privacy_class": "private",
        "consent": {"retention": True, "authorized_at": "2026-08-15T12:00:00+00:00", "authority_ref": "hannah-consent-001"},
    }


def session_input() -> dict:
    return {
        "relationship_id": "REL-hannah-agent",
        "event_id": "MENTOR-EVT-001",
        "idempotency_key": "session-001",
        "occurred_at": "2026-08-15T13:00:00+00:00",
        "learner_attempt": [{"basis": "observed", "statement": "Selected a one-page information hierarchy."}],
        "agent_behavior": [{"basis": "observed", "statement": "Explained the layout tradeoff before implementation."}],
        "mentor_intervention": {"class": "evidence-prompt", "assertions": [{"basis": "observed", "statement": "Asked the learner to compare mobile hierarchy."}]},
        "evidence_refs": ["github:hdong0424/agency-proposal-ai@abc123"],
        "progress": {"explanation": {"status": "observed", "basis": "observed", "statement": "Explained why experience precedes projects."}},
        "next_challenge": "Implement and test the mobile navigation independently.",
        "work_status": "bounded implementation in progress",
        "mutation_status": "read-only review",
    }


def test_open_record_project_and_verify(tmp_path: Path) -> None:
    db = tmp_path / "mentor.sqlite3"
    with ledger.connect(db) as connection:
        with connection:
            opened = ledger.open_relationship(connection, ledger.normalize_open(open_input()))
            data = ledger.normalize_session(session_input())
            payload = {key: value for key, value in data.items() if key not in {"relationship_id", "event_id", "idempotency_key", "occurred_at"}}
            recorded = ledger.append_event(connection, data["relationship_id"], data["event_id"], "session-recorded", data["occurred_at"], data["idempotency_key"], payload)
        assert opened["status"] == "opened"
        assert recorded["status"] == "recorded"
        assert ledger.project(connection, "REL-hannah-agent")["relationship"]["lifecycle"] == "active"
        assert ledger.verify(connection)["valid"] is True


def test_proposed_relationship_requires_explicit_activation(tmp_path: Path) -> None:
    db = tmp_path / "mentor.sqlite3"
    proposed = open_input()
    proposed["lifecycle"] = "proposed"
    with ledger.connect(db) as connection:
        with connection:
            ledger.open_relationship(connection, ledger.normalize_open(proposed))
        assert ledger.lifecycle(connection, proposed["relationship_id"]) == "proposed"
        proposed["reopen"] = True
        proposed["idempotency_key"] = "activate-001"
        with connection:
            ledger.open_relationship(connection, ledger.normalize_open(proposed))
        assert ledger.lifecycle(connection, proposed["relationship_id"]) == "active"


def test_consent_and_privacy_rejections() -> None:
    value = open_input()
    value["consent"]["retention"] = False
    with pytest.raises(ledger.MentorError, match="consent"):
        ledger.normalize_open(value)
    value = session_input()
    value["learner_attempt"][0]["statement"] = "email learner@example.com"
    with pytest.raises(ledger.MentorError, match="contact"):
        ledger.normalize_session(value)
    value = session_input()
    value["next_challenge"] = "password=top-secret"
    with pytest.raises(ledger.MentorError, match="credential"):
        ledger.normalize_session(value)


def test_store_must_be_absolute_and_outside_git() -> None:
    with pytest.raises(ledger.MentorError, match="absolute"):
        ledger.private_path("mentor.sqlite3")
    with pytest.raises(ledger.MentorError, match="outside Git"):
        ledger.private_path(ledger.REPO_ROOT / "mentor.sqlite3")


def test_evidence_cannot_cross_repository_boundary(tmp_path: Path) -> None:
    db = tmp_path / "mentor.sqlite3"
    with ledger.connect(db) as connection:
        with connection:
            ledger.open_relationship(connection, ledger.normalize_open(open_input()))
        with pytest.raises(ledger.MentorError, match="repository boundary"):
            ledger.validate_evidence_scope(connection, "REL-hannah-agent", ["github:another/private-repo@abc"])


def test_append_only_idempotency_and_cross_relationship_correction(tmp_path: Path) -> None:
    db = tmp_path / "mentor.sqlite3"
    with ledger.connect(db) as connection:
        with connection:
            ledger.open_relationship(connection, ledger.normalize_open(open_input()))
            data = ledger.normalize_session(session_input())
            payload = {key: value for key, value in data.items() if key not in {"relationship_id", "event_id", "idempotency_key", "occurred_at"}}
            first = ledger.append_event(connection, data["relationship_id"], data["event_id"], "session-recorded", data["occurred_at"], data["idempotency_key"], payload)
            second = ledger.append_event(connection, data["relationship_id"], "OTHER-ID", "session-recorded", data["occurred_at"], data["idempotency_key"], payload)
        assert first["status"] == "recorded"
        assert second["status"] == "idempotent"
        with pytest.raises(Exception):
            connection.execute("UPDATE mentorship_events SET event_type='changed'")


def test_check_mode_validates_without_creating_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "open.json"
    source.write_text(json.dumps(open_input()), encoding="utf-8")
    db = tmp_path / "mentor.sqlite3"
    assert ledger.main(["--db", str(db), "relationship", "open", "--input", str(source), "--check"]) == 0
    assert not db.exists()

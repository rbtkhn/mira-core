from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import choice_ledger


OPTIONS = [
    {"key": "inspect", "role": "recommended", "text": "Inspect the bounded evidence."},
    {"key": "compare", "role": "alternative", "text": "Compare a distinct objective."},
    {"key": "invert", "role": "overlooked", "text": "Test the credible inverse."},
    {"key": "pause", "role": "pause-or-deepen", "text": "Pause and preserve optionality."},
]


def connection(path: Path) -> sqlite3.Connection:
    return choice_ledger.connect(path)


def test_read_only_connection_never_migrates_or_accepts_writes(
    tmp_path: Path, monkeypatch
) -> None:
    path = tmp_path / "choices.sqlite3"
    writable = connection(path)
    select(writable)
    writable.close()

    def migration_is_a_write(_connection: sqlite3.Connection) -> None:
        raise AssertionError("read-only access must not migrate")

    monkeypatch.setattr(choice_ledger, "migrate", migration_is_a_write)
    readonly = choice_ledger.connect_read_only(path)
    assert readonly.execute("SELECT COUNT(*) FROM choice_prompts").fetchone()[0] == 1
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        readonly.execute("DELETE FROM choice_prompts")
    readonly.close()
    assert not path.with_name(f"{path.name}-wal").exists()
    assert not path.with_name(f"{path.name}-shm").exists()
    assert not path.with_name(f"{path.name}-journal").exists()


def test_writable_connection_migrates_existing_wal_store_to_delete(
    tmp_path: Path,
) -> None:
    path = tmp_path / "choices.sqlite3"
    legacy = sqlite3.connect(path)
    assert legacy.execute("PRAGMA journal_mode = WAL").fetchone()[0] == "wal"
    legacy.execute("CREATE TABLE legacy_probe (value INTEGER)")
    legacy.commit()
    legacy.close()
    assert path.read_bytes()[18:20] == b"\x02\x02"

    writable = connection(path)
    assert writable.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
    writable.close()
    assert path.read_bytes()[18:20] == b"\x01\x01"


def test_read_only_connection_rejects_wal_before_sqlite_open(
    tmp_path: Path, monkeypatch
) -> None:
    path = tmp_path / "choices.sqlite3"
    legacy = sqlite3.connect(path)
    assert legacy.execute("PRAGMA journal_mode = WAL").fetchone()[0] == "wal"
    legacy.execute("CREATE TABLE legacy_probe (value INTEGER)")
    legacy.commit()
    legacy.close()

    def sqlite_open_forbidden(*_args, **_kwargs):
        raise AssertionError("WAL preflight must fail before SQLite opens the store")

    monkeypatch.setattr(choice_ledger.sqlite3, "connect", sqlite_open_forbidden)
    with pytest.raises(sqlite3.OperationalError, match="WAL-to-DELETE migration"):
        choice_ledger.connect_read_only(path)


def test_read_snapshot_blocks_writer_commit_instead_of_ignoring_changes(
    tmp_path: Path,
) -> None:
    path = tmp_path / "choices.sqlite3"
    writer = connection(path)
    writer.execute("CREATE TABLE concurrency_probe (value INTEGER)")
    writer.commit()

    reader = choice_ledger.connect_read_only(path)
    assert reader.execute("SELECT COUNT(*) FROM concurrency_probe").fetchone()[0] == 0
    writer.execute("PRAGMA busy_timeout = 25")
    writer.execute("INSERT INTO concurrency_probe VALUES (1)")
    with pytest.raises(sqlite3.OperationalError, match="locked"):
        writer.commit()
    assert reader.execute("SELECT COUNT(*) FROM concurrency_probe").fetchone()[0] == 0

    reader.close()
    writer.rollback()
    writer.execute("INSERT INTO concurrency_probe VALUES (1)")
    writer.commit()
    writer.close()

    current = choice_ledger.connect_read_only(path)
    assert current.execute("SELECT COUNT(*) FROM concurrency_probe").fetchone()[0] == 1
    current.close()


def select(
    db: sqlite3.Connection,
    choice_id: str = "CHOICE-001",
    *,
    selected_key: str = "inspect",
    tenant: str = "tenant-a",
    workspace: str = "workspace-a",
    lane: str = "lane-a",
    choice_kind: str = "next-step",
    selected_at: str = "2026-07-29T12:00:00+00:00",
    options=OPTIONS,
    idempotency_key: str | None = None,
) -> dict:
    return choice_ledger.select_branch(
        db,
        choice_id=choice_id,
        options=options,
        selected_key=selected_key,
        tenant=tenant,
        workspace=workspace,
        lane=lane,
        choice_kind=choice_kind,
        consequence_level="low",
        decision_summary=f"Decision {choice_id}",
        actor="operator",
        presented_at="2026-07-29T11:59:00+00:00",
        selected_at=selected_at,
        idempotency_key=idempotency_key or f"select-{choice_id}",
        learning_refs=["ref:bounded"],
        success_signals=["clearer next step"],
        risk_signals=["authority ambiguity"],
    )


def outcome(
    db: sqlite3.Connection,
    choice_id: str,
    *,
    result: str = "successful",
    cognitive_load: str = "lower",
    momentum: str = "advanced",
    discovery: str = "new-useful-path",
    suffix: str = "outcome",
    **incidents,
) -> dict:
    return choice_ledger.append_choice_event(
        db,
        choice_id=choice_id,
        event_type="outcome_recorded",
        idempotency_key=f"{suffix}-{choice_id}",
        occurred_at="2026-07-30T12:00:00+00:00",
        result=result,
        cognitive_load=cognitive_load,
        momentum=momentum,
        discovery_value=discovery,
        **incidents,
    )


def seed_five(
    db: sqlite3.Connection,
    *,
    cognitive=("lower",) * 5,
    momentum=("advanced",) * 5,
    discovery=("new-useful-path",) * 5,
    incidents: dict | None = None,
) -> None:
    seed_outcomes(
        db,
        cognitive=cognitive,
        momentum=momentum,
        discovery=discovery,
        incidents_by_index={0: incidents} if incidents else None,
    )


def seed_outcomes(
    db: sqlite3.Connection,
    *,
    cognitive,
    momentum,
    discovery,
    incidents_by_index: dict[int, dict] | None = None,
) -> None:
    assert len(cognitive) == len(momentum) == len(discovery)
    for index in range(len(cognitive)):
        choice_id = f"CHOICE-{index:03d}"
        select(
            db,
            choice_id,
            selected_at=f"2026-07-{20 + index:02d}T12:00:00+00:00",
        )
        outcome(
            db,
            choice_id,
            cognitive_load=cognitive[index],
            momentum=momentum[index],
            discovery=discovery[index],
            **((incidents_by_index or {}).get(index, {})),
        )


def test_schema_migration_is_idempotent_and_preserves_existing_data(tmp_path: Path) -> None:
    path = tmp_path / "choices.sqlite3"
    db = connection(path)
    select(db)
    db.execute("PRAGMA user_version = 0")
    db.commit()
    db.close()

    reopened = connection(path)
    assert reopened.execute("PRAGMA user_version").fetchone()[0] == choice_ledger.SCHEMA_VERSION
    assert reopened.execute("SELECT COUNT(*) FROM choice_prompts").fetchone()[0] == 1
    choice_ledger.migrate(reopened)
    assert reopened.execute("SELECT COUNT(*) FROM choice_prompts").fetchone()[0] == 1
    reopened.close()


def test_backup_and_recovery_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "choices.sqlite3"
    db = connection(path)
    select(db)
    db.close()
    backup = choice_ledger.create_backup(path, tmp_path / "backups" / "choices.sqlite3")
    recovered = choice_ledger.recover_backup(backup, tmp_path / "restored.sqlite3")
    restored = connection(recovered)
    assert restored.execute("SELECT COUNT(*) FROM choice_prompts").fetchone()[0] == 1
    restored.close()


def test_backup_and_recovery_destinations_must_remain_outside_repository(
    tmp_path: Path,
) -> None:
    path = tmp_path / "choices.sqlite3"
    db = connection(path)
    select(db)
    db.close()
    inside_backup = choice_ledger.REPO_ROOT / "private" / "backup.sqlite3"
    with pytest.raises(choice_ledger.ChoiceError, match="outside"):
        choice_ledger.create_backup(path, inside_backup)
    backup = choice_ledger.create_backup(path, tmp_path / "backup.sqlite3")
    inside_recovery = choice_ledger.REPO_ROOT / "private" / "restored.sqlite3"
    with pytest.raises(choice_ledger.ChoiceError, match="outside"):
        choice_ledger.recover_backup(backup, inside_recovery)
    assert not inside_backup.exists()
    assert not inside_recovery.exists()


def test_unselected_footer_creates_no_record(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    assert choice_ledger.learning_context(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )["unresolved_review_queue"] == []
    assert db.execute("SELECT COUNT(*) FROM choice_prompts").fetchone()[0] == 0
    db.close()


def test_selection_is_atomic_exact_sanitized_and_navigation_only(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    options = [dict(item) for item in OPTIONS]
    options[0]["text"] = "Inspect alice@example.com before choosing."
    result = select(db, options=options)
    projection = choice_ledger.project_choice(db, "CHOICE-001")
    assert result["created"] is True
    assert projection["choice"]["options"][0]["text"] == "Inspect [redacted-contact] before choosing."
    assert projection["choice"]["options_hash"] == choice_ledger.digest(
        projection["choice"]["options"]
    )
    assert "receipt retention grants no authority" in projection["no_execution_authority"].lower()
    assert projection["authority_effect"] == "none"
    assert result["authority_effect"] == "none"
    assert [event["event_type"] for event in projection["events"]] == ["branch_selected"]


def test_schema_one_historical_receipt_survives_without_migration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = connection(tmp_path / "historical.sqlite3")
    legacy_notice = "Branch selection grants no execution authority."
    monkeypatch.setattr(choice_ledger, "NO_AUTHORITY", legacy_notice)
    select(db)
    before = dict(
        db.execute(
            "SELECT * FROM choice_prompts WHERE choice_id='CHOICE-001'"
        ).fetchone()
    )
    monkeypatch.undo()
    choice_ledger.migrate(db)
    after = dict(
        db.execute(
            "SELECT * FROM choice_prompts WHERE choice_id='CHOICE-001'"
        ).fetchone()
    )
    assert db.execute("PRAGMA user_version").fetchone()[0] == 1
    assert after == before
    projection = choice_ledger.project_choice(db, "CHOICE-001")
    assert projection["no_execution_authority"] == legacy_notice
    assert projection["authority_effect"] == "none"
    db.close()


@pytest.mark.parametrize("third_role", ("overlooked", "pause-or-deepen"))
def test_three_option_sets_accept_either_credible_third_role(
    third_role: str,
) -> None:
    options = [
        {"key": "a", "role": "recommended", "text": "Recommended path."},
        {"key": "b", "role": "alternative", "text": "Alternative path."},
        {"key": "c", "role": third_role, "text": "Credible third path."},
    ]
    assert [item["role"] for item in choice_ledger.sanitize_options(options)] == [
        "recommended",
        "alternative",
        third_role,
    ]


def test_failed_selection_rolls_back_prompt_and_event(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    with pytest.raises(choice_ledger.ChoiceError, match="selected key"):
        select(db, selected_key="missing")
    assert db.execute("SELECT COUNT(*) FROM choice_prompts").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM choice_events").fetchone()[0] == 0
    db.close()


def test_prompt_and_events_are_immutable_and_append_only(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db)
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        db.execute("UPDATE choice_prompts SET selected_key='compare'")
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        db.execute("DELETE FROM choice_events")
    db.close()


def test_hash_verification_and_tamper_detection(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db)
    outcome(db, "CHOICE-001")
    assert choice_ledger.verify_choice(db, "CHOICE-001")["valid"] is True
    db.execute("DROP TRIGGER choice_events_no_update")
    db.execute("UPDATE choice_events SET payload_json='{}' WHERE sequence=2")
    assert choice_ledger.verify_choice(db, "CHOICE-001")["valid"] is False
    db.close()


def test_verifier_rejects_hash_consistent_invalid_supersession_lineage(
    tmp_path: Path,
) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db)
    recorded = outcome(db, "CHOICE-001")
    corrected = choice_ledger.append_choice_event(
        db,
        choice_id="CHOICE-001",
        event_type="corrected",
        idempotency_key="correct-lineage",
        occurred_at="2026-07-31T00:00:00+00:00",
        result="mixed",
        supersedes_event_id=recorded["event_id"],
    )
    row = db.execute(
        "SELECT * FROM choice_events WHERE event_id=?",
        (corrected["event_id"],),
    ).fetchone()
    payload = json.loads(row["payload_json"])
    payload["supersedes_event_id"] = "missing-event"
    payload_json = choice_ledger.canonical_json(payload)
    hashed = choice_ledger.event_hash(
        choice_id=row["choice_id"],
        sequence=row["sequence"],
        event_type=row["event_type"],
        occurred_at=row["occurred_at"],
        idempotency_key=row["idempotency_key"],
        payload_json=payload_json,
        previous_hash=row["previous_hash"],
    )
    db.execute("DROP TRIGGER choice_events_no_update")
    db.execute(
        "UPDATE choice_events SET payload_json=?, event_hash=? WHERE event_id=?",
        (payload_json, hashed, corrected["event_id"]),
    )
    verification = choice_ledger.verify_choice(db, "CHOICE-001")
    assert "invalid supersession target at sequence 3" in verification["failures"]
    db.close()


def test_identical_retry_is_idempotent_and_conflict_is_rejected(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    first = select(db)
    second = select(db, selected_at="2026-07-29T12:00:05+00:00")
    assert first["created"] is True
    assert second["created"] is False
    with pytest.raises(choice_ledger.ChoiceError, match="conflicting"):
        select(db, selected_key="compare")
    assert db.execute("SELECT COUNT(*) FROM choice_events").fetchone()[0] == 1
    db.close()


def test_new_idempotency_key_cannot_append_second_selection(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db)
    with pytest.raises(choice_ledger.ChoiceError, match="new idempotency"):
        select(db, idempotency_key="second-selection-attempt")
    assert db.execute(
        "SELECT COUNT(*) FROM choice_events WHERE event_type='branch_selected'"
    ).fetchone()[0] == 1
    db.close()


def test_verifier_requires_exactly_one_initial_selection_event(
    tmp_path: Path,
) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db)
    first = db.execute(
        "SELECT payload_json FROM choice_events WHERE sequence=1"
    ).fetchone()
    with db:
        choice_ledger._append_event(
            db,
            choice_id="CHOICE-001",
            event_type="branch_selected",
            occurred_at="2026-07-30T00:00:00+00:00",
            idempotency_key="injected-second-selection",
            payload=json.loads(first["payload_json"]),
        )
    verification = choice_ledger.verify_choice(db, "CHOICE-001")
    assert "expected exactly one branch_selected event, found 2" in verification[
        "failures"
    ]
    db.close()


def test_correction_and_supersession_preserve_history(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db)
    recorded = outcome(db, "CHOICE-001", result="unsuccessful")
    corrected = choice_ledger.append_choice_event(
        db,
        choice_id="CHOICE-001",
        event_type="corrected",
        idempotency_key="correct-1",
        occurred_at="2026-07-31T00:00:00+00:00",
        result="mixed",
        supersedes_event_id=recorded["event_id"],
    )
    assert choice_ledger.project_choice(db, "CHOICE-001")["outcome"]["result"] == "mixed"
    choice_ledger.append_choice_event(
        db,
        choice_id="CHOICE-001",
        event_type="superseded",
        idempotency_key="supersede-1",
        occurred_at="2026-08-01T00:00:00+00:00",
        supersedes_event_id=corrected["event_id"],
    )
    projection = choice_ledger.project_choice(db, "CHOICE-001")
    assert projection["current_state"] == "superseded"
    assert len(projection["events"]) == 4
    db.close()


def test_supersession_requires_valid_same_choice_unused_target(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db, "A")
    select(db, "B")
    first = outcome(db, "A")
    other = outcome(db, "B")
    with pytest.raises(choice_ledger.ChoiceError, match="same choice"):
        choice_ledger.append_choice_event(
            db,
            choice_id="A",
            event_type="corrected",
            idempotency_key="wrong-choice",
            occurred_at="2026-07-31T00:00:00+00:00",
            result="mixed",
            supersedes_event_id=other["event_id"],
        )
    corrected = choice_ledger.append_choice_event(
        db,
        choice_id="A",
        event_type="corrected",
        idempotency_key="correct-a",
        occurred_at="2026-07-31T00:00:00+00:00",
        result="mixed",
        supersedes_event_id=first["event_id"],
    )
    retry = choice_ledger.append_choice_event(
        db,
        choice_id="A",
        event_type="corrected",
        idempotency_key="correct-a",
        occurred_at="2026-08-01T00:00:00+00:00",
        result="mixed",
        supersedes_event_id=first["event_id"],
    )
    assert retry["created"] is False
    with pytest.raises(choice_ledger.ChoiceError, match="already"):
        choice_ledger.append_choice_event(
            db,
            choice_id="A",
            event_type="superseded",
            idempotency_key="reuse-a",
            occurred_at="2026-08-02T00:00:00+00:00",
            supersedes_event_id=first["event_id"],
        )
    assert corrected["event_id"]
    db.close()


def test_tenant_and_lane_isolation(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db, "A", tenant="tenant-a", lane="lane-a")
    select(db, "B", tenant="tenant-b", lane="lane-a")
    select(db, "C", tenant="tenant-a", lane="lane-b")
    assert len(
        choice_ledger.scoped_choices(
            db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
        )
    ) == 1
    db.close()


def test_cli_show_and_verify_reject_cross_lane_access(tmp_path: Path) -> None:
    path = tmp_path / "choices.sqlite3"
    db = connection(path)
    select(db)
    db.close()
    with pytest.raises(choice_ledger.ChoiceError, match="outside"):
        choice_ledger.main(
            [
                "--db",
                str(path),
                "verify",
                "--choice-id",
                "CHOICE-001",
                "--tenant",
                "tenant-a",
                "--workspace",
                "workspace-a",
                "--lane",
                "other-lane",
            ]
        )


def test_privacy_scan_redacts_contacts_and_rejects_secrets() -> None:
    assert choice_ledger.sanitize_text("Call +1 (303) 555-1212") == "Call [redacted-contact]"
    with pytest.raises(choice_ledger.ChoiceError, match="credential"):
        choice_ledger.sanitize_text("api_key=super-secret-value")
    with pytest.raises(choice_ledger.ChoiceError, match="raw body"):
        choice_ledger.sanitize_evidence_ref(
            "This is a long raw private evidence body that must never be stored "
            "inside the choice event payload itself."
        )


def test_missing_store_fallback_does_not_block_navigation(
    capsys, monkeypatch
) -> None:
    monkeypatch.delenv(choice_ledger.DB_ENV, raising=False)
    assert choice_ledger.main(["context"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["available"] is False
    assert "may continue" in payload["disclosure"]


@pytest.mark.parametrize("command", ("context", "review"))
def test_read_only_commands_do_not_use_the_writable_store_connection(
    tmp_path: Path, monkeypatch, capsys, command: str
) -> None:
    path = tmp_path / "choices.sqlite3"
    writable = connection(path)
    writable.close()
    monkeypatch.setenv(choice_ledger.DB_ENV, str(path))

    def writable_connection_forbidden(_path: Path):
        raise AssertionError("read-only command requested a writable connection")

    monkeypatch.setattr(choice_ledger, "connect", writable_connection_forbidden)
    assert choice_ledger.main([command]) == 0
    payload = json.loads(capsys.readouterr().out)
    expected_version = (
        choice_ledger.REVIEW_PROJECTION_VERSION
        if command == "review"
        else choice_ledger.PROJECTION_VERSION
    )
    assert payload["projection_version"] == expected_version


def select_arguments() -> list[str]:
    return [
        "select",
        "--choice-id",
        "CHOICE-UNAVAILABLE",
        "--options-json",
        "[]",
        "--selected-key",
        "path-a",
        "--choice-kind",
        "navigation",
        "--consequence-level",
        "low",
        "--decision-summary",
        "Unavailable private store",
        "--presented-at",
        "2026-08-01T12:00:00+00:00",
        "--idempotency-key",
        "unavailable-select",
    ]


@pytest.mark.parametrize(
    ("arguments", "expected_disclosure"),
    (
        (["context"], "ordinary work may continue"),
        (["review"], "ordinary work may continue"),
        (select_arguments(), "Selection was not retained"),
    ),
)
@pytest.mark.parametrize(
    "failure",
    (
        PermissionError("access denied"),
        sqlite3.OperationalError("unable to open database file"),
    ),
)
def test_configured_unavailable_store_degrades_for_navigation_commands(
    tmp_path: Path,
    monkeypatch,
    capsys,
    arguments: list[str],
    expected_disclosure: str,
    failure: Exception,
) -> None:
    path = tmp_path / "configured.sqlite3"
    path.touch()
    monkeypatch.setenv(choice_ledger.DB_ENV, str(path))

    def unavailable(_path: Path):
        raise failure

    connection_name = (
        "connect_read_only"
        if arguments[0] in choice_ledger.READ_ONLY_COMMANDS
        else "connect"
    )
    monkeypatch.setattr(choice_ledger, connection_name, unavailable)
    assert choice_ledger.main(arguments) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["available"] is False
    assert payload["retained"] is False
    assert payload["reason"] == "private choice store could not be opened"
    assert str(path) not in json.dumps(payload)
    assert expected_disclosure in payload["disclosure"]


def test_configured_unavailable_store_remains_hard_for_explicit_operations(
    tmp_path: Path, monkeypatch
) -> None:
    path = tmp_path / "configured.sqlite3"
    path.touch()
    monkeypatch.setenv(choice_ledger.DB_ENV, str(path))

    def unavailable(_path: Path):
        raise sqlite3.OperationalError("unable to open database file")

    monkeypatch.setattr(choice_ledger, "connect", unavailable)
    with pytest.raises(sqlite3.OperationalError, match="unable to open"):
        choice_ledger.main(
            [
                "outcome",
                "--choice-id",
                "CHOICE-UNAVAILABLE",
                "--idempotency-key",
                "unavailable-outcome",
            ]
        )


def test_store_path_must_be_absolute_and_outside_repository() -> None:
    relative = choice_ledger.resolve_store("choices.sqlite3")
    inside = choice_ledger.resolve_store(
        choice_ledger.REPO_ROOT / "private" / "choices.sqlite3"
    )
    assert relative.path is None
    assert "absolute" in relative.reason
    assert inside.path is None
    assert "outside the repository" in inside.reason


def test_mutation_dry_run_needs_no_store_and_writes_nothing(capsys) -> None:
    assert (
        choice_ledger.main(
            [
                "select",
                "--choice-id",
                "DRY-1",
                "--options-json",
                json.dumps(OPTIONS),
                "--selected-key",
                "inspect",
                "--choice-kind",
                "next-step",
                "--consequence-level",
                "low",
                "--decision-summary",
                "Preview only",
                "--presented-at",
                "2026-07-29T00:00:00Z",
                "--idempotency-key",
                "dry-1",
                "--dry-run",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["dry_run"] is True
    assert payload["retained"] is False


def test_unresolved_review_order_is_deterministic(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db, "later", selected_at="2026-07-30T00:00:00+00:00")
    select(db, "earlier", selected_at="2026-07-29T00:00:00+00:00")
    context = choice_ledger.learning_context(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert [item["choice_id"] for item in context["unresolved_review_queue"]] == [
        "earlier",
        "later",
    ]
    db.close()


def test_selection_frequency_never_influences_recommendation(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    for index in range(6):
        select(db, f"CHOICE-{index}", selected_key="compare")
    context = choice_ledger.learning_context(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert context["recommendation_influence"] is None
    assert context["selection_frequency_used"] is False
    db.close()


def test_thin_consistent_and_contradictory_outcome_rules(tmp_path: Path) -> None:
    thin = connection(tmp_path / "thin.sqlite3")
    for index in range(2):
        select(thin, f"THIN-{index}", selected_key="compare")
        outcome(thin, f"THIN-{index}")
    assert choice_ledger.learning_context(
        thin, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )["recommendation_influence"] is None
    thin.close()

    consistent = connection(tmp_path / "consistent.sqlite3")
    for index in range(3):
        select(consistent, f"GOOD-{index}", selected_key="compare")
        outcome(consistent, f"GOOD-{index}", result="successful")
    influence = choice_ledger.learning_context(
        consistent, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )["recommendation_influence"]
    assert "alternative" in influence["eligible_roles"]
    consistent.close()

    contradictory = connection(tmp_path / "contradictory.sqlite3")
    for index, result in enumerate(("successful", "successful", "unsuccessful")):
        select(contradictory, f"MIX-{index}", selected_key="compare")
        outcome(contradictory, f"MIX-{index}", result=result)
    context = choice_ledger.learning_context(
        contradictory, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert context["recommendation_influence"] is None
    contradictory.close()


def test_boundary_incident_surfaces_immediately_and_overlooked_path_is_preserved(
    tmp_path: Path,
) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db)
    outcome(db, "CHOICE-001", privacy_incident=True)
    context = choice_ledger.learning_context(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert context["recommendation_influence"]["kind"] == "boundary-guardrail"
    assert context["preserve_credible_overlooked_path"] is True
    db.close()


def test_unresolved_boundary_incident_surfaces_immediately(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db)
    choice_ledger.append_choice_event(
        db,
        choice_id="CHOICE-001",
        event_type="review_deferred",
        idempotency_key="defer-1",
        occurred_at="2026-07-30T12:00:00+00:00",
        privacy_incident=True,
    )
    context = choice_ledger.learning_context(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert context["comparable_resolved_count"] == 0
    assert context["recommendation_influence"] == {
        "kind": "boundary-guardrail",
        "incidents": ["privacy"],
        "immediate": True,
    }
    db.close()


@pytest.mark.parametrize(
    ("cognitive", "momentum", "discovery", "incidents", "expected"),
    (
        (("Missing",) * 5, ("advanced",) * 5, ("new-useful-path",) * 5, None, "extend-to-ten"),
        (("lower",) * 5, ("advanced",) * 5, ("new-useful-path",) * 5, None, "continue"),
        (("higher", "higher", "lower", "lower", "lower"), ("advanced",) * 5, ("new-useful-path",) * 5, None, "adjust"),
        (("lower",) * 5, ("advanced",) * 5, ("new-useful-path",) * 5, {"authority_incident": True}, "hold"),
    ),
)
def test_five_selection_review_states(
    tmp_path: Path,
    cognitive,
    momentum,
    discovery,
    incidents,
    expected: str,
) -> None:
    db = connection(tmp_path / f"{expected}.sqlite3")
    seed_five(
        db,
        cognitive=cognitive,
        momentum=momentum,
        discovery=discovery,
        incidents=incidents,
    )
    scorecard = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert scorecard["assessment"] == expected
    assert scorecard["projection_kind"] == "review-scorecard"
    assert scorecard["projection_version"] == choice_ledger.REVIEW_PROJECTION_VERSION
    assert scorecard["cohort_stage"] == (
        "extension" if expected == "extend-to-ten" else "pilot"
    )
    assert scorecard["cohort_target"] == (
        10 if expected == "extend-to-ten" else 5
    )
    assert scorecard["cohort_choice_ids"] == [f"CHOICE-{index:03d}" for index in range(5)]
    assert scorecard["selection_frequency_used"] is False
    db.close()


def test_five_selection_review_pending(tmp_path: Path) -> None:
    db = connection(tmp_path / "choices.sqlite3")
    select(db)
    outcome(db, "CHOICE-001")
    scorecard = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert scorecard["projection_version"] == choice_ledger.REVIEW_PROJECTION_VERSION
    assert scorecard["assessment"] == "pending"
    assert scorecard["cohort_stage"] == "pilot"
    assert scorecard["cohort_target"] == 5
    assert scorecard["eligible_resolved"] == 1
    assert scorecard["needed"] == 4
    assert scorecard["selection_frequency_used"] is False
    db.close()


def test_review_incident_overrides_pending_before_five(tmp_path: Path) -> None:
    db = connection(tmp_path / "early-incident.sqlite3")
    select(db)
    choice_ledger.append_choice_event(
        db,
        choice_id="CHOICE-001",
        event_type="review_deferred",
        idempotency_key="early-incident",
        occurred_at="2026-07-30T12:00:00+00:00",
        privacy_incident=True,
    )
    scorecard = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert scorecard["assessment"] == "hold"
    assert scorecard["eligible_resolved"] == 0
    assert scorecard["needed"] == 5
    assert scorecard["boundary_incident_sources"] == [
        {
            "choice_id": "CHOICE-001",
            "incidents": ["privacy"],
            "in_measurement_cohort": False,
        }
    ]
    db.close()


def test_review_extension_is_frozen_through_outcome_nine(tmp_path: Path) -> None:
    db = connection(tmp_path / "frozen-extension.sqlite3")
    seed_outcomes(
        db,
        cognitive=("Missing",) * 5 + ("lower",) * 4,
        momentum=("advanced",) * 9,
        discovery=("new-useful-path",) * 9,
    )
    scorecard = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert scorecard["assessment"] == "extend-to-ten"
    assert scorecard["cohort_stage"] == "extension"
    assert scorecard["cohort_target"] == 10
    assert scorecard["eligible_resolved"] == 9
    assert scorecard["needed"] == 1
    assert scorecard["observation_gaps"] == {}
    assert scorecard["extension_trigger_gaps"]["lower_cognitive_load"] == {
        "observed": 0,
        "required": 3,
        "missing": 3,
    }
    db.close()


def test_review_terminal_gap_adjusts_at_ten(tmp_path: Path) -> None:
    db = connection(tmp_path / "terminal-gap.sqlite3")
    seed_outcomes(
        db,
        cognitive=("Missing",) * 10,
        momentum=("advanced",) * 10,
        discovery=("new-useful-path",) * 10,
    )
    scorecard = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert scorecard["assessment"] == "adjust"
    assert scorecard["cohort_stage"] == "extension"
    assert scorecard["needed"] == 0
    assert scorecard["extension_trigger_gaps"]["lower_cognitive_load"] == {
        "observed": 0,
        "required": 3,
        "missing": 3,
    }
    assert scorecard["observation_gaps"]["lower_cognitive_load"] == {
        "observed": 0,
        "required": 3,
        "missing": 3,
    }
    db.close()


def test_review_complete_extension_uses_cumulative_ten(tmp_path: Path) -> None:
    db = connection(tmp_path / "complete-extension.sqlite3")
    seed_outcomes(
        db,
        cognitive=("Missing",) * 5 + ("lower",) * 5,
        momentum=("advanced",) * 10,
        discovery=("new-useful-path",) * 10,
    )
    scorecard = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert scorecard["assessment"] == "continue"
    assert scorecard["cohort_choice_ids"] == [
        f"CHOICE-{index:03d}" for index in range(10)
    ]
    assert scorecard["primary_measures"]["lower_cognitive_load"]["denominator"] == 5
    db.close()


def test_review_incident_after_five_holds_immediately(tmp_path: Path) -> None:
    db = connection(tmp_path / "late-incident.sqlite3")
    seed_outcomes(
        db,
        cognitive=("Missing",) * 5 + ("lower",),
        momentum=("advanced",) * 6,
        discovery=("new-useful-path",) * 6,
        incidents_by_index={5: {"lane_incident": True}},
    )
    scorecard = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert scorecard["assessment"] == "hold"
    assert scorecard["boundary_incident_sources"][0] == {
        "choice_id": "CHOICE-005",
        "incidents": ["lane-boundary"],
        "in_measurement_cohort": True,
    }
    db.close()


def test_review_excludes_eleventh_measurement_but_not_its_incident(
    tmp_path: Path,
) -> None:
    db = connection(tmp_path / "eleventh.sqlite3")
    seed_outcomes(
        db,
        cognitive=("Missing",) * 5 + ("lower",) * 5 + ("higher",),
        momentum=("advanced",) * 10 + ("stalled",),
        discovery=("new-useful-path",) * 10 + ("not-useful",),
    )
    baseline = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert baseline["assessment"] == "continue"
    assert len(baseline["cohort_choice_ids"]) == 10
    assert "CHOICE-010" not in baseline["cohort_choice_ids"]
    assert baseline["repeated_negative_experience_count"] == 0

    choice_ledger.append_choice_event(
        db,
        choice_id="CHOICE-010",
        event_type="review_deferred",
        idempotency_key="outside-incident",
        occurred_at="2026-08-01T12:00:00+00:00",
        safety_incident=True,
    )
    held = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert held["assessment"] == "hold"
    assert held["primary_measures"] == baseline["primary_measures"]
    assert held["boundary_incident_sources"] == [
        {
            "choice_id": "CHOICE-010",
            "incidents": ["safety"],
            "in_measurement_cohort": False,
        }
    ]
    db.close()


def test_review_excludes_superseded_before_cohort_ordering(tmp_path: Path) -> None:
    db = connection(tmp_path / "superseded.sqlite3")
    seed_outcomes(
        db,
        cognitive=("Missing",) * 5 + ("lower",) * 6,
        momentum=("advanced",) * 11,
        discovery=("new-useful-path",) * 11,
    )
    target = choice_ledger.project_choice(db, "CHOICE-003")["outcome"]["event_id"]
    choice_ledger.append_choice_event(
        db,
        choice_id="CHOICE-003",
        event_type="superseded",
        idempotency_key="supersede-review-member",
        occurred_at="2026-08-02T12:00:00+00:00",
        supersedes_event_id=target,
    )
    scorecard = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    assert len(scorecard["cohort_choice_ids"]) == 10
    assert "CHOICE-003" not in scorecard["cohort_choice_ids"]
    assert "CHOICE-010" in scorecard["cohort_choice_ids"]
    db.close()


def test_review_v2_markdown_and_mixed_projection_versions(tmp_path: Path) -> None:
    path = tmp_path / "review-markdown.sqlite3"
    db = connection(path)
    seed_outcomes(
        db,
        cognitive=("Missing",) * 10,
        momentum=("advanced",) * 10,
        discovery=("new-useful-path",) * 10,
    )
    choice = choice_ledger.project_choice(db, "CHOICE-000")
    scorecard = choice_ledger.review_scorecard(
        db, tenant="tenant-a", workspace="workspace-a", lane="lane-a"
    )
    rendered = choice_ledger.markdown_projection(scorecard, "Choice Review")
    assert choice["projection_version"] == choice_ledger.PROJECTION_VERSION
    assert scorecard["projection_version"] == choice_ledger.REVIEW_PROJECTION_VERSION
    assert "- Cohort: `10/10` (`extension`)" in rendered
    assert "- Lower Cognitive Load gap: `3` (`0/3` observed)" in rendered
    db.close()
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "choice_ledger.py"),
            "--db",
            str(path),
            "--format",
            "markdown",
            "review",
            "--tenant",
            "tenant-a",
            "--workspace",
            "workspace-a",
            "--lane",
            "lane-a",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "# Staged Five-to-Ten Review" in result.stdout
    assert "- Projection: `review-scorecard 2.0`" in result.stdout
    assert "- Cohort: `10/10` (`extension`)" in result.stdout


def test_json_and_markdown_projections(tmp_path: Path) -> None:
    path = tmp_path / "choices.sqlite3"
    db = connection(path)
    select(db)
    db.close()
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "choice_ledger.py"),
            "--db",
            str(path),
            "--format",
            "markdown",
            "show",
            "--choice-id",
            "CHOICE-001",
            "--tenant",
            "tenant-a",
            "--workspace",
            "workspace-a",
            "--lane",
            "lane-a",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "# Choice Projection" in result.stdout
    assert "Receipt retention grants no authority" in result.stdout

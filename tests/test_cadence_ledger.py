from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import cadence_ledger
import recursive_learning_ledger


def episode(*, episode_id: str = "CD-20260816-01") -> dict:
    now = datetime.now(timezone.utc)
    return {
        "episode_id": episode_id,
        "series_id": "SERIES-CADENCE-01",
        "created_at": now.isoformat(),
        "workspace_id": "narrative-systems",
        "operator_id": "operator-test",
        "dream_date": now.date().isoformat(),
        "timezone": "UTC",
        "coverage_status": "complete",
        "session_coverage": [{
            "session_id": "session-1", "status": "included",
            "reason": "Contributed the bounded experiment.",
            "observed_at": now.isoformat(),
        }],
        "observation": "Profile-first verification reduced bounded validation delay.",
        "diagnosis": "Repository-wide verification obscured a passing local experiment.",
        "intervention": "Separate local verification from repository promotion.",
        "method_version_digest": "a" * 64,
        "profile": {"name": "cadence", "version": "1", "command_digest": "b" * 64},
        "observable": {
            "name": "local verification latency", "unit": "seconds", "baseline": "60",
            "success_threshold": "below 30", "source": "tests/test_cadence.py",
        },
        "falsifier": "A comparable run exceeds 30 seconds or hides a repository failure.",
        "next_use": "the next bounded cadence verifier",
        "task_class": "cadence-verification",
        "expires_at": (now + timedelta(days=30)).isoformat(),
        "artifacts": [
            {"ref": "scripts/cadence.py", "relationship": "implementation", "captured_at": now.isoformat()},
            {"ref": "tests/test_cadence.py", "relationship": "verification", "captured_at": now.isoformat()},
        ],
        "relevant_paths": ["scripts/cadence.py", "tests/test_cadence.py"],
        "evidence_summary": "The focused cadence suite passed within the bounded profile.",
        "tomorrow_inherits": "Retest the split on a comparable verifier.",
        "verification": {},
        "measurements": {},
    }


def database(tmp_path: Path):
    return cadence_ledger.connect(tmp_path / "cadence.sqlite3")


def test_private_store_rejects_repository_path() -> None:
    with pytest.raises(cadence_ledger.CadenceLedgerError, match="outside the repository"):
        cadence_ledger.require_private_path(ROOT / "cadence.sqlite3", label="test")


def test_episode_is_append_only_and_idempotent(tmp_path: Path) -> None:
    connection = database(tmp_path)
    first = cadence_ledger.create_episode(connection, episode(), idempotency_key="dream-1")
    second = cadence_ledger.create_episode(connection, episode(), idempotency_key="dream-1")
    assert first["episode"]["episode_id"] == second["episode"]["episode_id"]
    assert first["lifecycle_version"] == 1
    changed = episode()
    changed["diagnosis"] = "Different content cannot replace an episode."
    with pytest.raises(cadence_ledger.CadenceLedgerError, match="different content"):
        cadence_ledger.create_episode(connection, changed, idempotency_key="dream-2")
    connection.close()


def test_daily_close_run_is_append_only_resumable_and_conflict_checked(tmp_path: Path) -> None:
    connection = database(tmp_path)
    run = cadence_ledger.open_daily_close(
        connection, run_id="DCR-20260816-test", workspace_id="narrative-systems",
        operator_id="operator-test", close_date="2026-08-16", timezone_name="America/Denver",
        idempotency_key="close-open",
    )
    assert run["lifecycle_version"] == 1
    same = cadence_ledger.open_daily_close(
        connection, run_id="DCR-ignored", workspace_id="narrative-systems",
        operator_id="operator-test", close_date="2026-08-16", timezone_name="America/Denver",
        idempotency_key="close-open-again",
    )
    assert same["run_id"] == run["run_id"]
    completed = cadence_ledger.append_daily_close_event(
        connection, run["run_id"], "stage_completed", {"stage": "geo", "status": "finalized", "digest": "a" * 64},
        idempotency_key="close-geo", expected_version=1,
    )
    assert completed["stages"]["geo"] == "completed"
    with pytest.raises(cadence_ledger.CadenceLedgerError, match="lifecycle conflict"):
        cadence_ledger.append_daily_close_event(
            connection, run["run_id"], "stage_completed", {"stage": "journal", "status": "finalized"},
            idempotency_key="close-journal", expected_version=1,
        )
    connection.close()


def test_daily_close_preserves_dated_repository_artifact_reference(tmp_path: Path) -> None:
    connection = database(tmp_path)
    run = cadence_ledger.open_daily_close(
        connection, run_id="DCR-20260816-path", workspace_id="mira-core",
        operator_id="operator-test", close_date="2026-08-16", timezone_name="America/Denver",
        idempotency_key="close-path-open",
    )
    artifact_ref = "narrative-geopolitics/work/daily/2026-08-16/issue.md"
    projected = cadence_ledger.append_daily_close_event(
        connection, run["run_id"], "stage_completed",
        {"stage": "geo", "status": "certified_existing_packet", "artifact_ref": artifact_ref},
        idempotency_key="close-path-geo", expected_version=1,
    )
    receipt = next(event for event in projected["events"] if event["event_type"] == "stage_completed")
    assert receipt["payload"]["artifact_ref"] == artifact_ref
    connection.close()


def test_daily_close_rejects_contact_data_in_artifact_reference(tmp_path: Path) -> None:
    connection = database(tmp_path)
    run = cadence_ledger.open_daily_close(
        connection, run_id="DCR-20260816-private-path", workspace_id="mira-core",
        operator_id="operator-test", close_date="2026-08-16", timezone_name="America/Denver",
        idempotency_key="close-private-path-open",
    )
    with pytest.raises(cadence_ledger.CadenceLedgerError, match="contact data"):
        cadence_ledger.append_daily_close_event(
            connection, run["run_id"], "stage_completed",
            {"stage": "geo", "status": "invalid", "artifact_ref": "private/person@example.com.md"},
            idempotency_key="close-private-path-geo", expected_version=1,
        )
    connection.close()


def test_no_candidate_closeout_is_unique_and_contains_no_episode(tmp_path: Path) -> None:
    connection = database(tmp_path)
    payload = {
        "closeout_id": "DCO-20260816-test", "workspace_id": "narrative-systems",
        "operator_id": "operator-test", "dream_date": "2026-08-16", "timezone": "America/Denver",
        "coverage_status": "partial", "reason": "No defensible method experiment was observed.",
        "session_coverage_digest": "b" * 64,
    }
    first = cadence_ledger.record_dream_closeout(connection, payload, idempotency_key="closeout-1")
    second = cadence_ledger.record_dream_closeout(connection, payload, idempotency_key="closeout-1")
    assert first == second
    assert first["disposition"] == "no_cadence_worthy_experiment"
    assert connection.execute("SELECT COUNT(*) FROM cadence_episodes").fetchone()[0] == 0
    connection.close()


def test_daily_dream_is_unique_and_session_coverage_is_explicit(tmp_path: Path) -> None:
    connection = database(tmp_path)
    value = episode()
    value["session_coverage"][0].update({
        "closure_state": "rested",
        "rest_event_refs": ["RSTE-" + "a" * 24],
        "closure_observed_at": value["created_at"],
    })
    first = cadence_ledger.create_episode(connection, value, idempotency_key="dream-1")
    closure = first["episode"]["session_coverage"][0]
    assert closure["closure_state"] == "rested"
    assert closure["rest_event_refs"] == ["RSTE-" + "a" * 24]
    second = episode(episode_id="CD-20260816-02")
    with pytest.raises(cadence_ledger.CadenceLedgerError, match="daily Dream already exists"):
        cadence_ledger.create_episode(connection, second, idempotency_key="dream-2")

    partial = episode(episode_id="CD-20260817-01")
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    partial["created_at"] = tomorrow.isoformat()
    partial["dream_date"] = tomorrow.date().isoformat()
    partial["session_coverage"][0]["status"] = "unavailable"
    partial["session_coverage"][0]["reason"] = "Session receipt could not be recovered."
    with pytest.raises(cadence_ledger.CadenceLedgerError, match="coverage_status must be partial"):
        cadence_ledger.create_episode(connection, partial, idempotency_key="dream-3")
    partial["coverage_status"] = "partial"
    created = cadence_ledger.create_episode(connection, partial, idempotency_key="dream-3")
    assert created["episode"]["coverage_status"] == "partial"
    connection.close()


def test_late_session_receipt_is_append_only_supplement(tmp_path: Path) -> None:
    connection = database(tmp_path)
    created = cadence_ledger.create_episode(connection, episode(), idempotency_key="dream-1")
    receipt = {
        "session_id": "session-late", "status": "included",
        "reason": "Receipt arrived after the canonical daily consolidation.",
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }
    supplemented = cadence_ledger.append_session_supplement(
        connection, created["episode"]["episode_id"], receipt,
        idempotency_key="supplement-1", expected_version=created["lifecycle_version"],
    )
    assert supplemented["events"][-1]["event_type"] == "session_coverage_supplemented"
    assert supplemented["episode"]["session_coverage"] == created["episode"]["session_coverage"]
    with pytest.raises(cadence_ledger.CadenceLedgerError, match="already exists"):
        cadence_ledger.append_session_supplement(
            connection, created["episode"]["episode_id"], receipt,
            idempotency_key="supplement-2", expected_version=supplemented["lifecycle_version"],
        )
    connection.close()


def test_coffee_has_exact_grounded_navigation_contract(tmp_path: Path) -> None:
    connection = database(tmp_path)
    value = episode()
    cadence_ledger.create_episode(connection, value, idempotency_key="dream-1")
    context = cadence_ledger.coffee_context(connection, rest_coverage_status="covered-current")
    assert [(row["key"], row["verb"], row["role"]) for row in context["actions"]] == list(cadence_ledger.ACTION_SHAPE)
    assert len(context["actions"]) == 4
    assert [row["selection_effect"] for row in context["actions"]] == ["execute", "navigate", "navigate", "navigate"]
    assert context["actions"][0]["label"].startswith("Execute:")
    assert context["actions"][0]["execution"]["mutation"] is False
    assert context["rest_coverage_status"] == "covered-current"
    assert context["selection"] == {
        "basis": "automatic",
        "selected_dream_date": value["dream_date"],
        "newest_eligible_episode_id": "CD-20260816-01",
    }
    markdown = cadence_ledger.render_coffee_markdown(context)
    assert "A. Execute: Confirm" in markdown
    assert "Rest coverage: covered-current." in markdown
    assert "Authority boundary: Execute only the named read-only comparison; tests, writes, and disposition remain separate." in markdown
    assert all(f"{key}. {verb}:" in markdown for key, verb, _ in cadence_ledger.ACTION_SHAPE[1:])
    assert markdown.rstrip().endswith("Recommendation: A. Confirm the claimed improvement before adoption.")
    connection.close()


def dated_episode(episode_id: str, created_at: datetime, *, expires_at: datetime | None = None) -> dict:
    value = episode(episode_id=episode_id)
    value["created_at"] = created_at.isoformat()
    value["dream_date"] = created_at.date().isoformat()
    value["session_coverage"][0]["observed_at"] = created_at.isoformat()
    value["expires_at"] = (expires_at or created_at + timedelta(days=30)).isoformat()
    return value


def test_coffee_automatically_selects_newest_eligible_episode(tmp_path: Path) -> None:
    connection = database(tmp_path)
    now = datetime.now(timezone.utc)
    cadence_ledger.create_episode(connection, dated_episode("CD-old", now - timedelta(days=1)), idempotency_key="dream-old")
    cadence_ledger.create_episode(connection, dated_episode("CD-new", now), idempotency_key="dream-new")

    context = cadence_ledger.coffee_context(connection)

    assert context["episode_id"] == "CD-new"
    assert context["selection"] == {
        "basis": "automatic",
        "selected_dream_date": now.date().isoformat(),
        "newest_eligible_episode_id": "CD-new",
    }
    connection.close()


@pytest.mark.parametrize("newest_state", ["superseded", "expired"])
def test_coffee_skips_ineligible_newest_episode(tmp_path: Path, newest_state: str) -> None:
    connection = database(tmp_path)
    now = datetime.now(timezone.utc)
    cadence_ledger.create_episode(connection, dated_episode("CD-old", now - timedelta(days=2)), idempotency_key="dream-old")
    if newest_state == "expired":
        newest = dated_episode(
            "CD-new", now - timedelta(days=1), expires_at=now - timedelta(hours=1)
        )
        cadence_ledger.create_episode(connection, newest, idempotency_key="dream-new")
    else:
        newest = cadence_ledger.create_episode(
            connection, dated_episode("CD-new", now), idempotency_key="dream-new"
        )
        cadence_ledger.record_disposition(
            connection, "CD-new", "superseded", "Regression fixture.",
            idempotency_key="dispose-new", expected_version=newest["lifecycle_version"],
        )

    assert cadence_ledger.coffee_context(connection)["episode_id"] == "CD-old"
    connection.close()


def test_explicit_stale_coffee_episode_fails_closed(tmp_path: Path) -> None:
    connection = database(tmp_path)
    now = datetime.now(timezone.utc)
    cadence_ledger.create_episode(connection, dated_episode("CD-old", now - timedelta(days=1)), idempotency_key="dream-old")
    cadence_ledger.create_episode(connection, dated_episode("CD-new", now), idempotency_key="dream-new")

    with pytest.raises(cadence_ledger.CadenceLedgerError, match="CD-old is stale; newer eligible episode CD-new"):
        cadence_ledger.coffee_context(connection, episode_id="CD-old")
    connection.close()


def test_explicit_coffee_episode_without_newer_peer_renders(tmp_path: Path) -> None:
    connection = database(tmp_path)
    cadence_ledger.create_episode(connection, episode(), idempotency_key="dream-1")

    context = cadence_ledger.coffee_context(connection, episode_id="CD-20260816-01")

    assert context["episode_id"] == "CD-20260816-01"
    assert context["selection"]["basis"] == "explicit"
    assert "Authority boundary:" in cadence_ledger.render_coffee_markdown(context)
    connection.close()


def test_coffee_fails_closed_without_candidate(tmp_path: Path) -> None:
    connection = database(tmp_path)
    context = cadence_ledger.coffee_context(connection)
    assert context["lifecycle_state"] == "cold_start"
    assert len(context["actions"]) == 4
    assert context["actions"][-1]["target"] == "cold-start:no-cadence-worthy-experiment"
    connection.close()


def test_lifecycle_requires_expected_version_and_comparable_repeat(tmp_path: Path) -> None:
    connection = database(tmp_path)
    created = cadence_ledger.create_episode(connection, episode(), idempotency_key="dream-1")
    inherited = cadence_ledger.record_disposition(
        connection, "CD-20260816-01", "inherit", "Use locally for one bounded task.",
        idempotency_key="dispose-1", expected_version=created["lifecycle_version"],
    )
    with pytest.raises(cadence_ledger.CadenceLedgerError, match="lifecycle version changed"):
        cadence_ledger.record_disposition(
            connection, "CD-20260816-01", "retest", "Stale writer.",
            idempotency_key="dispose-2", expected_version=created["lifecycle_version"],
        )
    measurement = {
        "series_id": "SERIES-CADENCE-01", "method_version_digest": "a" * 64,
        "observable_name": "local verification latency", "unit": "seconds",
        "task_class": "cadence-verification", "observed": 9.5,
        "environment_differences": "Different profile subject; same verifier class.",
    }
    repeated = cadence_ledger.record_repetition(
        connection, "CD-20260816-01", measurement, idempotency_key="repeat-1",
        expected_version=inherited["lifecycle_version"],
    )
    assert repeated["lifecycle_state"] == "repeated"
    connection.close()


def test_export_is_private_deterministic_and_assessable(tmp_path: Path) -> None:
    connection = database(tmp_path)
    projection = cadence_ledger.create_episode(connection, episode(), idempotency_key="dream-1")
    output = tmp_path / "reference.json"
    checked = cadence_ledger.export_learning_reference(projection, output, check=True)
    written = cadence_ledger.export_learning_reference(projection, output, check=False)
    assert checked["sha256"] == written["sha256"]
    packet = recursive_learning_ledger.load_process_reference(output)
    assessment = recursive_learning_ledger.assess_process_reference(packet)
    assert assessment["status"] == "partial-candidate"
    assert assessment["private_context_is_stage_evidence"] is False
    packet["chronology"][0]["event_type"] = "tampered"
    output.write_text(json.dumps(packet), encoding="utf-8")
    with pytest.raises(recursive_learning_ledger.LearningError, match="event chain"):
        recursive_learning_ledger.load_process_reference(output)
    connection.close()


def test_rsi_correspondence_is_digest_bound_and_idempotent(tmp_path: Path) -> None:
    connection = database(tmp_path)
    created = cadence_ledger.create_episode(connection, episode(), idempotency_key="dream-1")
    body = {
        "source_episode_id": "CD-20260816-01", "process_reference_sha256": "a" * 64,
        "rsi_id": "RSI-20260816-99", "candidate_sha256": "b" * 64,
        "admission_digest": "c" * 64,
    }
    receipt = {"schema_version": 1, "correspondence": body, "correspondence_sha256": cadence_ledger.digest(body)}
    represented = cadence_ledger.reconcile_rsi(
        connection, receipt, idempotency_key="rsi-1", expected_version=created["lifecycle_version"],
    )
    assert represented["lifecycle_state"] == "represented"
    same = cadence_ledger.reconcile_rsi(
        connection, receipt, idempotency_key="rsi-1", expected_version=created["lifecycle_version"],
    )
    assert same["lifecycle_version"] == represented["lifecycle_version"]
    receipt["correspondence"]["rsi_id"] = "RSI-20260816-98"
    with pytest.raises(cadence_ledger.CadenceLedgerError, match="digest mismatch"):
        cadence_ledger.reconcile_rsi(
            connection, receipt, idempotency_key="rsi-2", expected_version=represented["lifecycle_version"],
        )
    connection.close()


def test_integrity_and_private_status_are_bounded(tmp_path: Path) -> None:
    path = tmp_path / "cadence.sqlite3"
    connection = cadence_ledger.connect(path)
    cadence_ledger.create_episode(connection, episode(), idempotency_key="dream-1")
    assert cadence_ledger.verify_ledger(connection)["valid"] is True
    connection.close()
    status = cadence_ledger.private_status(path)
    assert status["availability"] == "available"
    assert status["counts"] == {"episodes": 1, "active_candidates": 1, "represented": 0, "unresolved_rsi_correspondence": 0}
    assert str(path) not in json.dumps(status)


def test_schema_two_store_remains_readable_for_coffee_without_migration(tmp_path: Path) -> None:
    path = tmp_path / "cadence-v2.sqlite3"
    writable = cadence_ledger.connect(path)
    cadence_ledger.create_episode(writable, episode(), idempotency_key="dream-v2")
    writable.execute("DROP TABLE daily_close_events")
    writable.execute("DROP TABLE daily_close_runs")
    writable.execute("DROP TABLE daily_dream_closeouts")
    writable.execute("PRAGMA user_version = 2")
    writable.commit()
    writable.close()
    before = path.read_bytes()

    readonly = cadence_ledger.connect_read_only(path)
    assert readonly.execute("PRAGMA user_version").fetchone()[0] == 2
    verification = cadence_ledger.verify_ledger(readonly)
    context = cadence_ledger.coffee_context(readonly)
    readonly.close()

    assert verification["valid"] is True
    assert verification["schema_version"] == 2
    assert verification["reader_schema_version"] == cadence_ledger.SCHEMA_VERSION
    assert len(context["actions"]) == 4
    assert path.read_bytes() == before


def test_scorecard_reports_recursion_denominators_and_telemetry_gaps(tmp_path: Path) -> None:
    connection = database(tmp_path)
    created = cadence_ledger.create_episode(connection, episode(), idempotency_key="dream-1")
    inherited = cadence_ledger.record_disposition(
        connection, "CD-20260816-01", "inherit", "Use for one bounded task.",
        idempotency_key="dispose-1", expected_version=created["lifecycle_version"],
    )
    measurement = {
        "series_id": "SERIES-CADENCE-01", "method_version_digest": "a" * 64,
        "observable_name": "local verification latency", "unit": "seconds",
        "task_class": "cadence-verification", "observed": 11,
        "environment_differences": "Same verifier class on a later task.",
        "rework_required": True, "rework_count": 1,
        "regression": False, "reversal": False,
    }
    cadence_ledger.record_repetition(
        connection, "CD-20260816-01", measurement, idempotency_key="repeat-1",
        expected_version=inherited["lifecycle_version"],
    )
    result = cadence_ledger.scorecard(connection)
    assert result["schema_version"] == 2
    assert result["metrics"]["candidate_to_disposition_conversion"] == {
        "numerator": 1, "denominator": 1, "rate": 1.0,
    }
    assert result["metrics"]["comparable_repetition_rate"]["rate"] == 1.0
    assert result["metrics"]["rework_after_execution"]["rate"] == 1.0
    assert result["metrics"]["regressions"] == 0
    assert result["metrics"]["reversals"] == 0
    assert result["metrics"]["median_candidate_to_disposition_seconds"] is not None
    assert "actionable_menu_rate" in result["unavailable_metrics"]
    assert "operator_scope_restatement_rate" in result["unavailable_metrics"]
    assert result["selection_popularity_excluded"] is True
    connection.close()

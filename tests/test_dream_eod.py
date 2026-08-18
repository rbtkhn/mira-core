from __future__ import annotations

import sys
import json
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import dream_eod


def test_dream_skill_preserves_certification_boundaries() -> None:
    skill = (ROOT / "docs" / "skill-drafts" / "dream" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "must not regenerate, reinterpret, or revise the packet" in skill
    assert "must not canonicalize, approve, or publish the entry" in skill
    assert "`canonicalized: false`" in skill
    assert "`approval_status: pending`" in skill


def arguments(tmp_path: Path, **changes):
    values = {
        "date": "2026-08-16", "timezone": "America/Denver",
        "workspace_id": "mira-core", "operator_id": "operator-test",
        "db": tmp_path / "cadence.sqlite3", "check": False, "resume": None,
        "journal_bundle": tmp_path / "journal" / "2026-08-16", "dream_json": None,
        "no_candidate": None, "coverage_status": "complete", "json": True,
    }
    values.update(changes)
    return SimpleNamespace(**values)


def test_check_is_read_only_and_reports_composition_blocker(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    result = dream_eod.check_projection(arguments(tmp_path), "2026-08-16")
    assert result["mutation"] is False
    assert result["stages"]["geo"]["status"] == "no_geo_run"
    assert result["status"] == "paused"
    assert result["stages"]["journal"]["status"] == "composition_required"
    assert result["incomplete_stages"] == ["Mira Journal"]
    assert "Do you want to finish it" in result["prompt"]
    assert not (tmp_path / "cadence.sqlite3").exists()


def test_check_validates_ready_bundle_without_canonicalizing(monkeypatch, tmp_path: Path) -> None:
    bundle = tmp_path / "journal" / "2026-08-16"
    bundle.mkdir(parents=True)
    (bundle / "draft.md").write_text("# 2026-08-16 — Return\n\nPrivate prose.\n", encoding="utf-8")
    calls = []
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)

    def fake_run_tool(*args):
        calls.append(args)
        return SimpleNamespace(
            returncode=0,
            stdout='{"status":"passed","refresh_required":false,"version_id":"MJ-20260816-v1"}',
            stderr="",
        )

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)
    result = dream_eod.check_projection(
        arguments(tmp_path, no_candidate="No experiment."), "2026-08-16"
    )
    assert result["status"] == "ready"
    assert result["stages"]["journal"]["status"] == "certification_ready"
    assert all("eod-finalize" not in call for call in calls)


def test_empty_geo_day_pauses_before_ledger_or_journal_preparation(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    monkeypatch.setattr(
        dream_eod, "run_tool",
        lambda *args: SimpleNamespace(returncode=0, stdout='{"status":"prepared"}', stderr=""),
    )
    result = dream_eod.execute(arguments(tmp_path), "2026-08-16")
    assert result["status"] == "paused"
    assert result["mutation"] is False
    assert result["incomplete_stages"] == ["Mira Journal"]
    assert "Do you want to finish it" in result["prompt"]
    assert not (tmp_path / "cadence.sqlite3").exists()


def test_both_incomplete_lanes_pause_with_combined_prompt(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        dream_eod, "geo_certification",
        lambda _date: (_ for _ in ()).throw(
            dream_eod.cadence_ledger.CadenceLedgerError("Geo packet is incomplete")
        ),
    )
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)

    result = dream_eod.execute(arguments(tmp_path), "2026-08-16")

    assert result["status"] == "paused"
    assert result["mutation"] is False
    assert result["incomplete_stages"] == ["Geo-Strategy", "Mira Journal"]
    assert result["prompt"] == (
        "Geo-Strategy and Mira Journal are incomplete for 2026-08-16. "
        "Do you want to finish them before Dream continues?"
    )
    assert not (tmp_path / "cadence.sqlite3").exists()


def test_existing_journal_can_complete_no_candidate_close(monkeypatch, tmp_path: Path) -> None:
    entry = {"versions": [{"version_id": "MJ-20260816-v1", "content_sha256": "a" * 64}]}
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: entry)
    monkeypatch.setattr(
        dream_eod, "run_tool",
        lambda *args: SimpleNamespace(returncode=0, stdout='{"coverage":"complete"}', stderr=""),
    )
    result = dream_eod.execute(
        arguments(tmp_path, no_candidate="No defensible method experiment was observed."), "2026-08-16"
    )
    assert result["status"] == "completed"
    assert result["run"]["stages"] == {"geo": "skipped", "journal": "completed", "dream": "completed"}


def test_existing_committed_geo_packet_is_certified_without_regeneration(monkeypatch, tmp_path: Path) -> None:
    entry = {"versions": [{"version_id": "MJ-20260816-v1", "content_sha256": "a" * 64}]}
    certification = {
        "status": "ready", "manifest_rows": 8,
        "artifact_ref": "narrative-geopolitics/work/daily/2026-08-16/issue.md",
        "digest": "b" * 64, "commit": "c" * 40,
        "validation_stage": "issue", "certification_basis": "committed",
    }
    calls = []
    monkeypatch.setattr(dream_eod, "geo_certification", lambda _date: certification)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: entry)

    def fake_run_tool(*args):
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout='{"coverage":"complete"}', stderr="")

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)
    result = dream_eod.execute(
        arguments(tmp_path, no_candidate="No defensible method experiment was observed."),
        "2026-08-16",
    )
    assert result["status"] == "completed"
    assert all(not (call and call[0] == "synthesis") for call in calls)
    connection = dream_eod.cadence_ledger.connect(tmp_path / "cadence.sqlite3")
    try:
        rows = connection.execute(
            "SELECT payload_json FROM daily_close_events WHERE event_type='stage_completed'"
        ).fetchall()
    finally:
        connection.close()
    geo_receipt = next(
        json.loads(row["payload_json"]) for row in rows
        if json.loads(row["payload_json"]).get("stage") == "geo"
    )
    assert geo_receipt["status"] == "certified_existing_packet"
    assert geo_receipt["artifact_ref"] == certification["artifact_ref"]
    assert geo_receipt["commit"] == "c" * 40
    assert geo_receipt["validation_stage"] == "issue"
    assert geo_receipt["certification_basis"] == "committed"


def test_geo_failure_precedes_private_ledger_mutation(monkeypatch, tmp_path: Path) -> None:
    def fail(_date):
        raise dream_eod.cadence_ledger.CadenceLedgerError("packet validation failed")

    monkeypatch.setattr(dream_eod, "geo_certification", fail)
    monkeypatch.setattr(
        dream_eod, "journal_entry",
        lambda _date: {"versions": [{"version_id": "MJ-20260816-v1", "content_sha256": "a" * 64}]},
    )

    result = dream_eod.execute(arguments(tmp_path), "2026-08-16")

    assert result["status"] == "paused"
    assert result["mutation"] is False
    assert result["incomplete_stages"] == ["Geo-Strategy"]
    assert result["stages"]["geo"]["reason"] == "packet validation failed"
    assert "Do you want to finish it" in result["prompt"]
    assert not (tmp_path / "cadence.sqlite3").exists()


def test_private_bundle_is_certified_without_journal_mutation(monkeypatch, tmp_path: Path) -> None:
    bundle = tmp_path / "journal" / "2026-08-16"
    bundle.mkdir(parents=True)
    prose = b"# 2026-08-16 \xe2\x80\x94 Return\n\nPrivate prose.\n"
    (bundle / "draft.md").write_bytes(prose)
    (bundle / "technical-reference.json").write_text(
        json.dumps({"reference_id": "MJTR-20260816-v1", "journal_version_id": "MJ-20260816-v1"}),
        encoding="utf-8",
    )
    calls = []
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    monkeypatch.setattr(dream_eod.mira_journal_references, "reference_digest", lambda _value: "b" * 64)

    def fake_run_tool(*args):
        calls.append(args)
        if args[:2] == ("mira-journal", "draft-check"):
            return SimpleNamespace(
                returncode=0,
                stdout='{"status":"passed","refresh_required":false,"version_id":"MJ-20260816-v1"}',
                stderr="",
            )
        return SimpleNamespace(returncode=0, stdout='{"coverage":"complete"}', stderr="")

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)
    result = dream_eod.execute(
        arguments(tmp_path, no_candidate="No defensible method experiment was observed."),
        "2026-08-16",
    )
    assert result["status"] == "completed"
    assert all("eod-finalize" not in call for call in calls)
    connection = dream_eod.cadence_ledger.connect(tmp_path / "cadence.sqlite3")
    try:
        rows = connection.execute(
            "SELECT payload_json FROM daily_close_events WHERE event_type='stage_completed'"
        ).fetchall()
    finally:
        connection.close()
    journal_receipt = next(
        json.loads(row["payload_json"]) for row in rows
        if json.loads(row["payload_json"]).get("stage") == "journal"
    )
    assert journal_receipt["status"] == "certified_private_bundle"
    assert journal_receipt["canonicalized"] is False
    assert journal_receipt["approval_status"] == "pending"
    assert journal_receipt["digest"] == dream_eod.hashlib.sha256(prose).hexdigest()

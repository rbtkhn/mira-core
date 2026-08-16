from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import dream_eod


def arguments(tmp_path: Path, **changes):
    values = {
        "date": "2026-08-16", "timezone": "America/Denver",
        "workspace_id": "narrative-systems", "operator_id": "operator-test",
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
    assert result["stages"]["journal"]["status"] == "composition_required"
    assert not (tmp_path / "cadence.sqlite3").exists()


def test_empty_geo_day_stops_at_precise_journal_handoff(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    monkeypatch.setattr(
        dream_eod, "run_tool",
        lambda *args: SimpleNamespace(returncode=0, stdout='{"status":"prepared"}', stderr=""),
    )
    result = dream_eod.execute(arguments(tmp_path), "2026-08-16")
    assert result["status"] == "blocked"
    assert result["run"]["stages"]["geo"] == "skipped"
    assert result["run"]["stages"]["journal"] == "pending"
    assert "Compose" in result["next_action"]


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

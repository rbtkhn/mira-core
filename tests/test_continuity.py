from __future__ import annotations

import json
import contextlib
import io
import sys
from pathlib import Path

import pytest

from scripts import continuity

ROOT = Path(__file__).resolve().parents[1]


def run_continuity(*args: str):
    buffer = io.StringIO()
    original = sys.argv
    sys.argv = ["continuity.py", *args]
    try:
        with contextlib.redirect_stdout(buffer):
            code = continuity.main()
    finally:
        sys.argv = original
    return code, buffer.getvalue()


def test_continuity_validation_passes():
    code, output = run_continuity("validate", "--format", "json")
    assert code == 0, output
    assert json.loads(output)["failures"] == []


def test_state_query_is_provenance_bearing():
    code, output = run_continuity("states", "--voice", "mearsheimer", "--format", "json")
    assert code == 0
    payload = json.loads(output)
    assert payload[0]["state_id"] == "STATE-MEARSHEIMER-0001"
    assert payload[0]["source_ids"]
    assert payload[0]["daily_blocks"]


def test_host_inventory_is_read_only_and_filtered():
    code, output = run_continuity("hosts", "--voice", "mearsheimer", "--format", "json")
    assert code == 0
    payload = json.loads(output)
    assert payload
    assert all(item["voice"] == "mearsheimer" for item in payload)


def test_orthogonality_defaults_to_six_voice_scope_and_json_shape():
    code, output = run_continuity("orthogonality", "--format", "json", "--dry-run")
    assert code == 0
    payload = json.loads(output)
    assert payload["coverage"]["core_voices"] == ["pape", "mercouris", "mearsheimer", "marandi", "diesen", "davis"]
    assert {item["voice"] for item in payload["voices"]} == set(payload["coverage"]["core_voices"])
    assert all(0 <= score <= 3 for item in payload["voices"] for score in item["scores"].values())


def test_orthogonality_dry_run_does_not_write(tmp_path):
    target = tmp_path / "orthogonality.md"
    code, _ = run_continuity("orthogonality", "--output", str(target), "--dry-run")
    assert code == 0
    assert not target.exists()


def test_daily_orthogonality_covers_full_july20_roster_without_persisting():
    code, output = run_continuity(
        "orthogonality", "--date", "2026-07-20", "--daily", "--format", "json", "--dry-run"
    )
    assert code == 0
    payload = json.loads(output)
    assert payload["source_count"] == 14
    assert payload["voice_count"] == 13
    assert {item["voice"] for item in payload["voices"]} >= {"mearsheimer", "weichert", "davis"}
    assert next(item for item in payload["voices"] if item["voice"] == "mearsheimer")["source_count"] == 2
    weichert = next(item for item in payload["voices"] if item["voice"] == "weichert")
    assert "Saudi access" in weichert["daily_contribution"]
    assert any("vessel-level" in item for item in payload["counter_pressure_gaps"])
    assert any(item["classification"] == "high collapse risk" for item in payload["pairs"])


def test_daily_orthogonality_reports_unmapped_voices_for_review():
    code, output = run_continuity(
        "orthogonality", "--date", "2026-07-20", "--daily", "--format", "json", "--dry-run"
    )
    payload = json.loads(output)
    assert payload["unmapped_voice_count"] == 1
    assert any(item["voice"] == "pape" and item["axis"] == "unmapped" for item in payload["voices"])
    assert any(item["voice"] == "weichert" and item["status"] == "distinct contribution" for item in payload["voices"])
    assert any(item["priority"] == "P1" and "escobar" in item["entity"] and "weichert" in item["entity"] for item in payload["review_queue"])


def test_daily_orthogonality_requires_manifest_backed_date():
    with pytest.raises(SystemExit) as error:
        run_continuity("orthogonality", "--date", "2099-01-01", "--daily", "--dry-run")
    assert error.value.code == 2


def test_daily_orthogonality_honors_output_and_content_stable_reruns(tmp_path):
    target = tmp_path / "orthogonality.md"
    code, first = run_continuity(
        "orthogonality", "--date", "2026-07-20", "--daily", "--format", "md", "--output", str(target)
    )
    assert code == 0
    assert target.exists()
    first_bytes = target.read_bytes()
    code, second = run_continuity(
        "orthogonality", "--date", "2026-07-20", "--daily", "--format", "md", "--output", str(target)
    )
    assert code == 0
    assert target.read_bytes() == first_bytes
    assert "Decision Summary" in second


def test_daily_orthogonality_july19_is_a_distinct_basing_and_multitheater_fixture():
    code, output = run_continuity(
        "orthogonality", "--date", "2026-07-19", "--daily", "--format", "json", "--dry-run"
    )
    assert code == 0
    payload = json.loads(output)
    assert payload["source_count"] == 9
    assert payload["voice_count"] == 9
    assert {item["voice"] for item in payload["voices"]} == {"sachs", "marandi", "mcgovern", "mercouris", "krapivnik", "johnson", "jiang", "pape", "ritter"}
    assert next(item for item in payload["voices"] if item["voice"] == "mcgovern")["axis"] == "basing exposure / intelligence sequence"
    assert any("basing" in item.lower() and "casualty" in item.lower() for item in payload["counter_pressure_gaps"])
    assert not any("vessel-level" in item for item in payload["counter_pressure_gaps"])
    assert all(item["shared_objects"] or item["classification"] == "human review required" for item in payload["pairs"])
    assert "basing convergence" in payload["recommendation"]


def test_daily_orthogonality_july18_surfaces_unmapped_voices_and_explainability():
    code, output = run_continuity(
        "orthogonality", "--date", "2026-07-18", "--daily", "--format", "json", "--dry-run"
    )
    assert code == 0
    payload = json.loads(output)
    assert payload["source_count"] == 8
    assert payload["voice_count"] == 8
    assert payload["unmapped_voice_count"] == 3
    assert {item["voice"] for item in payload["voices"] if item["axis"] == "unmapped"} == {"matlock", "pape", "parsi"}
    assert all(item["source_ids"] and item["source_roles"] and item["mechanism_evidence"] for item in payload["pairs"])
    assert any("human review" in item["action"] or "stable voice" in item["action"] for item in payload["review_queue"])


def test_daily_orthogonality_july_range_includes_sparse_manifest_date_and_skips_empty_dates():
    code, output = run_continuity(
        "orthogonality", "--daily", "--start-date", "2026-07-01", "--end-date", "2026-07-31", "--format", "json", "--dry-run"
    )
    assert code == 0
    payload = json.loads(output)
    assert payload["audited_dates"][0] == "2026-07-01"
    assert "2026-07-17" in payload["audited_dates"]
    assert "2026-07-17" not in payload["missing_context_dates"]
    assert "2026-07-21" in payload["audited_dates"]
    assert "2026-07-21" not in payload["skipped_dates"]
    assert "mercouris" in payload["recurring_voices"]
    assert any(item["priority"] == "P1" for item in payload["review_queue"])
    assert "independent observations" in payload["recommendation"]


def test_daily_orthogonality_range_markdown_has_required_rollup_sections(tmp_path):
    target = tmp_path / "july-rollup.md"
    code, output = run_continuity(
        "orthogonality", "--daily", "--start-date", "2026-07-01", "--end-date", "2026-07-31", "--format", "md", "--output", str(target)
    )
    assert code == 0
    assert target.exists()
    text = target.read_text(encoding="utf-8")
    for section in ("Decision Summary", "Coverage and Data Availability", "Crisis-Object Transitions", "Prioritized Month-Level Review Queue", "Counter-Pressure Gaps by Crisis Object", "Limitations and Non-Evidence Notice"):
        assert section in text
    assert "Different voices are not independent evidence" in text


def test_longitudinal_accountability_excludes_retrospective_from_calibration():
    code, output = run_continuity(
        "longitudinal", "--start-date", "2026-07-01", "--end-date", "2026-07-31", "--format", "json", "--dry-run"
    )
    assert code == 0
    payload = json.loads(output)
    assert payload["forecast_summary"]["total"] >= 1
    assert payload["forecast_summary"]["calibration_eligible"] < payload["forecast_summary"]["total"]
    assert payload["retrospective_items"]
    assert all(item["calibration_eligible"] is False for item in payload["accountability_items"] if item["provenance"] == "retrospective")
    assert "Forecast performance is not a complete measure" in payload["limitations"][0]


def test_longitudinal_links_voice_states_and_keeps_reality_status_separate():
    code, output = run_continuity(
        "longitudinal", "--start-date", "2026-07-08", "--end-date", "2026-07-20", "--format", "json", "--dry-run"
    )
    assert code == 0
    payload = json.loads(output)
    item = next(item for item in payload["accountability_items"] if item["hook_id"] == "NG-20260720-F01")
    assert item["states"]
    assert payload["reality_transition_summary"]["linked_record_count"] >= 1
    assert "remain separate" in payload["reality_transition_summary"]["note"]


def test_longitudinal_markdown_output_is_persisted_and_has_required_sections(tmp_path):
    target = tmp_path / "longitudinal.md"
    code, output = run_continuity(
        "longitudinal", "--start-date", "2026-07-01", "--end-date", "2026-07-31", "--format", "md", "--output", str(target)
    )
    assert code == 0
    assert target.exists()
    text = target.read_text(encoding="utf-8")
    for section in ("Forecast Accountability", "Voice-State Continuity and Revision", "Reality-Evidence Transitions", "Host-Conditioned Variation", "Prioritized Human-Review Queue", "Limitations and Non-Evidence Notice"):
        assert section in text
    assert "repeated commentary is not independent corroboration" in text


def test_geometry_range_emits_provenance_graph_and_quality_metrics():
    code, output = run_continuity(
        "geometry", "--start-date", "2026-07-18", "--end-date", "2026-07-20", "--format", "json", "--dry-run"
    )
    assert code == 0
    payload = json.loads(output)
    node_ids = {node["id"] for node in payload["nodes"]}
    assert "voice:weichert" in node_ids
    assert "host:moral-resistance" in node_ids
    assert "object:bab-el-mandab" in node_ids
    assert any(node["id"] == "forecast:NG-20260720-F01" for node in payload["nodes"])
    assert payload["edges"]
    assert all(edge["basis_type"] and edge["source_ids"] for edge in payload["edges"] if edge["basis_type"] not in {"reality_relation"})
    assert payload["quality_metrics"]["counter_pressure_gap_count"] > 0
    assert payload["graph_diffs"]
    assert payload["counter_pressure_gaps"]


def test_triage_prioritizes_geometry_and_forecast_risks_without_claiming_adjudication():
    code, output = run_continuity(
        "triage", "--start-date", "2026-07-18", "--end-date", "2026-07-20", "--format", "json", "--dry-run"
    )
    assert code == 0
    payload = json.loads(output)
    assert payload["summary"]["total_items"] > 0
    assert payload["summary"]["p1"] > 0
    assert any("escobar" in item["entity"] and "weichert" in item["entity"] for item in payload["p1_immediate_review"])
    assert all(item["source_ids"] or item["category"] in {"forecast", "counter_pressure", "editorial"} for item in payload["queue"])
    assert "does not adjudicate truth" in payload["limitations"][0]


def test_triage_markdown_output_and_content_stability(tmp_path):
    target = tmp_path / "triage.md"
    code, first = run_continuity("triage", "--date", "2026-07-20", "--format", "md", "--output", str(target))
    assert code == 0 and target.exists()
    before = target.read_bytes()
    code, second = run_continuity("triage", "--date", "2026-07-20", "--format", "md", "--output", str(target))
    assert code == 0 and target.read_bytes() == before
    assert "P1 Immediate Review" in second

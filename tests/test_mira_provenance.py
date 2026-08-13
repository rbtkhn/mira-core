from pathlib import Path

import pytest

from scripts.mira_provenance import (
    ProvenanceError,
    ProvenanceStore,
    attach_brief_claim,
    pilot_scorecard,
    record_forecast_outcome,
    record_source_packet,
    summarize_measurements,
)


def store(tmp_path: Path) -> ProvenanceStore:
    return ProvenanceStore(tmp_path / "private" / "provenance.sqlite3")


def test_generated_and_inferred_records_require_review(tmp_path: Path) -> None:
    with store(tmp_path) as db:
        generated = db.write_record(
            content="Revenue figure needs verification",
            source_ref="packet:finance-1",
            source_date="2026-08-13",
            project="grace-gems",
            lane="executive-brief",
            provenance_status="generated",
            confidence=0.4,
        )
        assert generated.review_status == "review_required"
        assert db.recall(query="Revenue", project="grace-gems", lane="executive-brief") == []

        db.review(generated.id, "reviewed", reviewer="dev", note="Verified against packet")
        results = db.recall(query="Revenue", project="grace-gems", lane="executive-brief")
        assert results[0]["id"] == generated.id
        assert results[0]["recall_trace"]["reason"].startswith("scope=grace-gems/executive-brief")
        assert db.review_queue() == []


def test_project_and_lane_boundaries_prevent_cross_recall(tmp_path: Path) -> None:
    with store(tmp_path) as db:
        db.write_record(
            content="Private Grace Gems decision",
            source_ref="packet:1",
            source_date="2026-08-13",
            project="grace-gems",
            lane="executive-brief",
            provenance_status="supplied",
            confidence=1,
        )
        assert db.recall(query="decision", project="anyang", lane="executive-brief") == []
        assert db.recall(query="decision", project="grace-gems", lane="commercial") == []


def test_stale_records_are_hidden_unless_explicitly_requested(tmp_path: Path) -> None:
    with store(tmp_path) as db:
        db.write_record(
            content="Old decision",
            source_ref="packet:old",
            source_date="2020-01-01",
            project="anyang",
            lane="executive-brief",
            provenance_status="supplied",
            confidence=1,
            freshness_until="2020-01-02T00:00:00+00:00",
        )
        assert db.recall(query="decision", project="anyang", lane="executive-brief") == []
        assert db.recall(query="decision", project="anyang", lane="executive-brief", include_stale=True)


def test_validation_rejects_missing_scope_and_bad_confidence(tmp_path: Path) -> None:
    with store(tmp_path) as db:
        with pytest.raises(ProvenanceError):
            db.write_record(content="x", source_ref="s", source_date="d", project="", lane="brief", provenance_status="supplied", confidence=1)
        with pytest.raises(ProvenanceError):
            db.write_record(content="x", source_ref="s", source_date="d", project="p", lane="l", provenance_status="supplied", confidence=2)


def test_adapters_and_lineage_preserve_corrections(tmp_path: Path) -> None:
    with store(tmp_path) as db:
        source = record_source_packet(db, content="Revenue was reported at 10", source_ref="packet:1", source_date="2026-08-13", project="grace-gems", lane="executive-brief")
        claim = attach_brief_claim(db, claim="Revenue is verified at 10", source_ref="packet:1", source_date="2026-08-13", project="grace-gems")
        outcome = db.write_record(content="Revenue was actually 8", source_ref="ledger:1", source_date="2026-08-14", project="grace-gems", lane="executive-brief", provenance_status="confirmed", confidence=1)
        record_forecast_outcome(db, forecast_id=claim.id, outcome_id=outcome.id, outcome_ref="ledger:1", contradicted=True)
        db.review(claim.id, "contradicted", reviewer="ceo", note="Ledger corrected the claim")
        assert db.lineage(claim.id)[0]["relation"] == "contradicted-by"
        assert db.recall(query="Revenue", project="grace-gems", lane="executive-brief")
        assert all(row["id"] != claim.id for row in db.recall(query="verified", project="grace-gems", lane="executive-brief"))
        assert source.id != claim.id


def test_recall_report_explains_exclusions(tmp_path: Path) -> None:
    with store(tmp_path) as db:
        db.write_record(content="Generated revenue claim", source_ref="packet:1", source_date="2026-08-13", project="p", lane="l", provenance_status="generated", confidence=.4)
        report = db.recall_report(query="revenue", project="p", lane="l", include_excluded=True)
        assert report["selected"] == []
        assert "review_status=review_required" in report["exclusions"][0]["reasons"]


def test_measurements_support_baseline_and_pilot_comparison(tmp_path: Path) -> None:
    with store(tmp_path) as db:
        for phase in ("baseline", "pilot"):
            db.record_measurement(
                phase=phase,
                task="morning brief",
                preparation_minutes=30 if phase == "baseline" else 20,
                reconstruction_minutes=10,
                source_checks=3,
                corrections=1,
                evidence_gaps=1,
                repeated_work=0,
                confidence=0.8,
            )
        summary = summarize_measurements(db.measurements("pilot"))
        assert summary["count"] == 1
        assert summary["preparation_minutes"] == 20


def test_scorecard_requires_all_expansion_gates() -> None:
    baseline = [{"preparation_minutes": 30, "reconstruction_minutes": 10}]
    pilot = [{"preparation_minutes": 20, "reconstruction_minutes": 8}]
    scorecard = pilot_scorecard(baseline, pilot, provenance_complete=.9, stale_recall_rate=.1,
                                review_overhead_ratio=.2, workflows_reused=2, privacy_incidents=0)
    assert scorecard["eligible_for_expansion"] is True
    assert scorecard["time_reduction"] == .3

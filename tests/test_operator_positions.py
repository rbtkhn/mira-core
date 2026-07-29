from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import operator_positions as subject


def canonical() -> dict:
    return subject.load_ledger()


def completed() -> dict:
    data = canonical()
    first, latest = data["positions"][0]["versions"]
    latest["comparator_set"]["status"] = "approved"
    latest["comparator_set"]["approval"] = {
        "approved_at": "2026-07-28",
        "basis": "test approval",
    }
    latest["comparison"] = deepcopy(first["comparison"])
    latest["comparison"]["approval"] = {
        "approved_at": "2026-07-28",
        "basis": "test approval",
    }
    return data


def test_canonical_ledger_has_events_positions_and_graph_views() -> None:
    data = canonical()
    assert subject.validate_data(data) == []
    keys = set(subject._walk_keys(data))
    assert not {"overall_score", "grand_score", "total_score"}.intersection(keys)
    assert data["schema"] == "strategic-judgment-ledger-v1"
    assert data["ledger"]["short_name"] == "the Judgment Ledger"
    entry_ids = [entry["entry_id"] for entry in data["journal_entries"]]
    assert entry_ids == sorted(entry_ids)
    assert {"JRN-20260728-01", "JRN-20260728-02"}.issubset(entry_ids)
    titles = {entry["title"] for entry in data["journal_entries"]}
    assert "The living book takes its name" in titles
    assert "The journal becomes a recursive-learning instrument" in titles
    version = data["positions"][0]["versions"][-1]
    assert version["approval"]["status"] == "approved"
    rendered = subject.render_report(data)
    assert "## AI exploration" in rendered
    assert "## Journal event view" in rendered
    assert "## Position object view" in rendered
    assert "#### Epistemic layers" in rendered
    assert "| Voice | Engaged layers | Axis | Evidence | Host concentration |" in rendered
    assert "#### Persuasive-coherence profiles" in rendered


def test_graph_projection_has_stable_typed_nodes_and_resolved_edges() -> None:
    data = canonical()
    graph = subject.build_graph(data)
    assert graph["schema"] == "strategic-judgment-graph-v1"
    assert subject.validate_graph(graph) == []
    node_ids = {node["node_id"] for node in graph["nodes"]}
    assert "ledger:strategic-judgment" in node_ids
    assert "OV-20260728-02-v1" in node_ids
    assert (
        "layer:OV-20260728-02-v1:odessa_civilizational_premise"
        in node_ids
    )
    assert all(
        edge["source"] in node_ids and edge["target"] in node_ids
        for edge in graph["edges"]
    )
    assert "raw_text" not in set(subject._walk_keys(graph))


def test_ai_query_views_return_object_scoped_results() -> None:
    data = canonical()
    current = subject.query_ledger(
        data,
        "current-beliefs",
        position_id="OV-20260728-02",
    )
    assert len(current["results"]) == 1
    assert len(current["results"][0]["layers"]) == 3
    layers = subject.query_ledger(
        data,
        "layer-map",
        position_id="OV-20260728-02",
    )
    assert {item["layer_id"] for item in layers["results"]} == {
        "kiev_security_requirement",
        "odessa_civilizational_premise",
        "current_war_realization",
    }
    voice_map = subject.query_ledger(
        data,
        "voice-map",
        position_id="OV-20260728-01",
    )
    assert any(
        edge["edge_type"] == "engages_layer"
        for edge in voice_map["results"]
    )
    review = subject.query_ledger(
        data,
        "review-queue",
        position_id="OV-20260728-02",
        as_of=date(2026, 8, 27),
    )
    assert review["results"]["due"][0]["position_id"] == "OV-20260728-02"


def test_newly_approved_position_may_await_comparator_work() -> None:
    data = canonical()
    latest = data["positions"][-1]["versions"][-1]
    latest["comparator_set"] = {
        "status": "proposed",
        "included": [],
        "excluded": [],
    }
    latest["comparison"] = {
        "status": "not_started",
        "profiles": [],
        "relations": [],
        "findings": {},
    }
    assert latest["comparator_set"]["status"] == "proposed"
    assert latest["comparison"]["status"] == "not_started"
    assert subject.validate_data(data) == []
    rendered = subject.render_report(data)
    assert "#### Comparator approval pending" in rendered


def test_pending_lifecycle_rejects_premature_score_data() -> None:
    data = canonical()
    latest = data["positions"][-1]["versions"][-1]
    latest["comparison"]["status"] = "not_started"
    latest["comparison"]["profiles"] = [{"subject": "operator"}]
    errors = subject.validate_data(data)
    assert any("not-started comparison contains score data" in error for error in errors)


def test_epistemic_layers_are_explicit_and_independently_validated() -> None:
    data = canonical()
    latest = data["positions"][-1]["versions"][-1]
    layers = latest["position"]["epistemic_layers"]
    assert [layer["layer_type"] for layer in layers] == [
        "empirical_hypothesis",
        "actor_model_premise",
        "conditional_forecast",
    ]
    assert layers[1]["falsifier_status"] == "not_empirically_falsifiable"
    layers[2]["layer_id"] = layers[0]["layer_id"]
    layers[1]["falsifier_status"] = "immune_to_evidence"
    errors = subject.validate_data(data)
    assert any("duplicate epistemic layer ID" in error for error in errors)
    assert any("invalid falsifier status" in error for error in errors)


def test_completed_ledger_is_valid() -> None:
    data = completed()
    assert subject.validate_data(data) == []
    assert "Dimension deltas (voice minus operator)" in subject.render_report(data)


def test_draft_is_local_and_does_not_touch_canonical(tmp_path: Path, monkeypatch) -> None:
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("raw secret operator wording", encoding="utf-8")
    candidates = tmp_path / ".candidates"
    monkeypatch.setattr(subject, "CANDIDATE_ROOT", candidates)
    before = subject.LEDGER_PATH.read_bytes()
    target = subject.make_candidate(prompt, "pilot-object", "prompt")
    candidate = json.loads(target.read_text(encoding="utf-8"))
    assert target.parent == candidates
    assert candidate["raw_text"] == "raw secret operator wording"
    assert candidate["normalized_position"]["epistemic_layers"] == []
    assert subject.LEDGER_PATH.read_bytes() == before


def test_daily_journal_candidate_requires_approval_and_appends_normalized_event(
    tmp_path: Path,
    monkeypatch,
) -> None:
    activity = tmp_path / "activity.md"
    activity.write_text("private daily activity text", encoding="utf-8")
    monkeypatch.setattr(subject, "CANDIDATE_ROOT", tmp_path / ".candidates")
    target = subject.make_journal_candidate(activity, "2026-07-29", "daily_reflection")
    candidate = json.loads(target.read_text(encoding="utf-8"))
    assert candidate["raw_text"] == "private daily activity text"
    candidate["normalized_entry"] = {
        "title": "A bounded daily reflection",
        "observation": "One mechanism recurred in today's work.",
        "interpretation": "The recurrence adds context without changing the position.",
        "confidence_movement": "unchanged",
        "position_effect": "context",
        "linked_position_versions": ["OV-20260728-01-v2"],
        "voice_pressure": [],
        "unresolved_questions": ["Will another source change the mechanism?"],
        "learning_loop": {
            "prior_model": "The recurring mechanism might require a position update.",
            "pressure": "The new activity repeated rather than changed the mechanism.",
            "update": "Record context without revising the position.",
            "future_test": "Check whether a later source changes the causal chain.",
            "inherited_practice": "Separate recurrence from mechanism change.",
            "loop_status": "open_test",
        },
    }
    target.write_text(json.dumps(candidate), encoding="utf-8")
    data = canonical()
    expected_sequence = 1 + sum(
        entry["entry_date"] == "2026-07-29"
        for entry in data["journal_entries"]
    )
    entry = subject.approve_journal_candidate(data, target)
    assert entry["entry_id"] == f"JRN-20260729-{expected_sequence:02d}"
    assert "raw_text" not in set(subject._walk_keys(data))
    assert data["journal_entries"][-1]["interpretation"].startswith("The recurrence")


def test_raw_text_does_not_appear_in_canonical_or_report() -> None:
    data = canonical()
    assert "raw_text" not in set(subject._walk_keys(data))
    assert "raw_text" not in subject.render_report(data)


def test_revision_chain_rejects_overwrite_or_broken_link() -> None:
    data = completed()
    version = deepcopy(data["positions"][0]["versions"][-1])
    version["version_id"] = "OV-20260728-01-v3"
    version["version_number"] = 3
    version["previous_version_id"] = "wrong"
    version["relation_to_previous"] = "revision"
    data["positions"][0]["versions"].append(version)
    assert any("broken previous-version link" in error for error in subject.validate_data(data))


def test_approved_surfaces_are_immutable_and_unchanged_review_appends() -> None:
    data = completed()
    try:
        subject.recommend_for_position(data, "OV-20260728-01")
    except subject.LedgerError as exc:
        assert "immutable" in str(exc)
    else:
        raise AssertionError("approved comparator set was mutable")
    version = subject.review_position(
        data,
        "OV-20260728-01",
        "unchanged_review",
    )
    assert version["version_id"] == "OV-20260728-01-v3"
    assert version["previous_version_id"] == "OV-20260728-01-v2"
    assert subject.validate_data(data) == []


def test_invalid_score_and_missing_rationale_fail_but_unavailable_survives() -> None:
    data = completed()
    dimension = data["positions"][0]["versions"][-1]["comparison"]["profiles"][0]["dimensions"]["thesis_precision"]
    dimension["score"] = "unavailable"
    assert subject.validate_data(data) == []
    dimension["score"] = 0
    dimension["rationale"] = ""
    errors = subject.validate_data(data)
    assert any("invalid score" in error for error in errors)
    assert any("missing rationale" in error for error in errors)


def test_comparator_threshold_and_broken_path_fail() -> None:
    data = completed()
    comparator = data["positions"][0]["versions"][-1]["comparator_set"]["included"][0]
    comparator["evidence"] = comparator["evidence"][:1]
    comparator["evidence_count"] = 1
    comparator["source_count"] = 1
    comparator["evidence"][0]["path"] = "missing/source.md"
    errors = subject.validate_data(data)
    assert any("engaged layer needs two excerpts from two sources" in error for error in errors)
    assert any("broken evidence path" in error for error in errors)


def test_comparator_evidence_cannot_cross_epistemic_layers() -> None:
    data = completed()
    comparator = data["positions"][0]["versions"][-1]["comparator_set"]["included"][0]
    comparator["engaged_layer_ids"] = ["termination_conversion", "invented_layer"]
    comparator["evidence"][0]["layer_ids"] = ["invented_layer"]
    errors = subject.validate_data(data)
    assert any("comparator references unknown epistemic layer" in error for error in errors)
    assert any("invented_layer: engaged layer needs" in error for error in errors)


def test_comparator_approval_rejects_invalid_layer_binding() -> None:
    data = canonical()
    version = data["positions"][-1]["versions"][-1]
    version["comparator_set"]["status"] = "proposed"
    version["comparator_set"].pop("approval", None)
    version["comparator_set"]["included"] = [
        {
            "voice_slug": "example",
            "display_name": "Example Voice",
            "engaged_layer_ids": ["invented_layer"],
            "evidence": [],
            "evidence_count": 0,
            "source_count": 0,
            "host_concentration": "none",
            "inclusion_rationale": "test",
            "orthogonality_axis": "test",
        }
    ]
    try:
        subject.approve_comparators(data, "OV-20260728-02")
    except subject.LedgerError as exc:
        assert "comparator evidence threshold not met" in str(exc)
    else:
        raise AssertionError("invalid layer binding was approved")
    assert version["comparator_set"]["status"] == "proposed"


def test_profiles_relations_and_findings_bind_voice_layer_pairs() -> None:
    data = completed()
    comparison = data["positions"][0]["versions"][-1]["comparison"]
    comparison["profiles"][1]["layer_id"] = "invented_layer"
    comparison["relations"][0]["layer_id"] = "invented_layer"
    comparison["findings"]["closest_affinity"]["layer_id"] = "invented_layer"
    errors = subject.validate_data(data)
    assert any("score profiles do not match approved comparator set" in error for error in errors)
    assert any("relations do not match comparator set" in error for error in errors)
    assert any("invalid closest affinity finding" in error for error in errors)


def test_multilayer_scoring_preserves_unavailable_and_evidence_insufficiency() -> None:
    data = canonical()
    version = data["positions"][-1]["versions"][-1]
    version["comparator_set"] = {
        "status": "approved",
        "included": [],
        "excluded": [],
        "approval": {
            "approved_at": "2026-07-29",
            "basis": "test approval",
        },
    }
    version["comparison"] = {
        "status": "not_started",
        "profiles": [],
        "relations": [],
        "findings": {},
    }
    comparison = subject.score_position(data, "OV-20260728-02")
    assert {
        profile["layer_id"]
        for profile in comparison["profiles"]
        if profile["subject"] == "operator"
    } == {
        "kiev_security_requirement",
        "odessa_civilizational_premise",
        "current_war_realization",
    }
    assert all(
        dimension["score"] == "unavailable"
        for profile in comparison["profiles"]
        for dimension in profile["dimensions"].values()
    )
    assert comparison["findings"]["evidence_insufficient"]
    assert subject.validate_data(data) == []


def test_due_handles_date_and_event_independently() -> None:
    data = canonical()
    assert subject.due_items(data, date(2026, 8, 27))[0]["reason"] == "date"
    event = data["positions"][0]["versions"][0]["review_trigger"]["event"]
    assert subject.due_items(data, date(2026, 7, 28), event)[0]["reason"] == "event"
    assert subject.due_items(data, date(2026, 7, 28)) == []


def test_markdown_drift_is_detectable(tmp_path: Path, monkeypatch) -> None:
    report = tmp_path / "ledger.md"
    report.write_text("drift\n", encoding="utf-8")
    monkeypatch.setattr(subject, "REPORT_PATH", report)
    assert any("JSON/Markdown drift" in error for error in subject.validate_data(completed(), check_report=True))


def test_graph_drift_is_detectable(tmp_path: Path, monkeypatch) -> None:
    graph = tmp_path / "graph.json"
    graph.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(subject, "GRAPH_PATH", graph)
    assert any(
        "JSON/graph drift" in error
        for error in subject.validate_data(completed(), check_report=True)
    )

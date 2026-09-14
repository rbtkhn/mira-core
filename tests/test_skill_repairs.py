"""Behavioral boundaries for the bounded skill repairs; no live carriers."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import cadence_ledger
import dream_forecast_review as forecast
import elicitation
import interaction_context
from test_cadence_ledger import isolated_episode_store


def settled():
    return {
        "type": "decision-navigation", "closure_state": "settled", "final_response": True,
        "surface_kind": "response-controls",
        "next_option_assessment": {
            "basis": "Simple acknowledgement; no artifact or useful next action is pending.",
            "candidates": [],
        },
        "options": [dict(key=key, label=label, role=role, selection_effect="navigate",
                         learning_eligibility="none")
                    for key, label, role in zip("ABCD", ("Close", "Correct", "Deepen", "New task"),
                                                elicitation.DECISION_ROLES)],
    }


def test_settled_controls_are_transient_and_cannot_authorize():
    surface = elicitation.validate_elicitation_surface(settled())
    assert surface["action_readiness"] == {"ready_option_keys": []}
    assert surface["context_capsule"]["pending_actions"] == []
    for response in ("A", "B,C", "D>A"):
        result = elicitation.interpret_elicitation_response(surface, response)
        assert result["receipt_count"] == 0
        assert result["receipt_directives"] == []
        assert result["authority_effect"] == "none"


@pytest.mark.parametrize("change", ["target", "execute", "eligible", "readiness", "context", "three", "authority", "null"])
def test_settled_shortcut_rejects_consequential_metadata(change):
    surface = settled()
    if change == "target":
        surface["options"][0]["target"] = "scripts/example.py"
    elif change == "execute":
        surface["options"][0].update(label="Execute a change", selection_effect="execute")
    elif change == "eligible":
        surface["options"][0]["learning_eligibility"] = "eligible"
    elif change == "readiness":
        surface["action_readiness"] = {"ready_option_keys": ["A"]}
    elif change == "context":
        surface["action_context"] = {}
    elif change == "three":
        surface["options"] = surface["options"][:1]
    elif change == "null":
        surface["options"] = None
    else:
        surface["authority_effect"] = "execute"
    with pytest.raises(elicitation.ElicitationError):
        elicitation.validate_elicitation_surface(surface)


def test_template_reuse_is_exact_and_does_not_reuse_action_authority(monkeypatch):
    cache = elicitation.SettledControls()
    original = elicitation.validate_elicitation_surface
    calls = []
    def counted(surface):
        calls.append(True)
        return original(surface)
    monkeypatch.setattr(elicitation, "validate_elicitation_surface", counted)
    template = settled()
    first = cache.validate(template)
    first["options"][0]["label"] = "Caller corruption"
    assert cache.validate(template)["options"][0]["label"] == "Close"
    assert len(calls) == 1
    old_capsule = cache.validate(template)["context_capsule"]
    template["options"][0]["label"] = "Close this discussion"
    changed = cache.validate(template)
    assert len(calls) == 2
    assert interaction_context.resolve_followup(old_capsule, "A", expected_context_digest=changed["context_capsule"]["context_digest"])["ambiguity"] == "stale-context"
    template["options"][0]["learning_eligibility"] = "eligible"
    with pytest.raises(elicitation.ElicitationError):
        cache.validate(template)
    assert len(calls) == 3
    with pytest.raises(elicitation.ElicitationError):
        cache.validate({"type": "decision-navigation"})


def test_coffee_rendered_promises_follow_execution_in_every_mode(tmp_path, monkeypatch):
    connection, repo = isolated_episode_store(tmp_path, monkeypatch)
    try:
        for expected in ("initial", "repeat-checkpoint", "saturated", "delta"):
            if expected == "delta":
                (repo / "scripts/cadence.py").write_text("changed", encoding="utf-8")
            context = cadence_ledger.coffee_context(connection)
            assert context["presentation"]["mode"] == expected
            action = context["actions"][0]
            spec = action["execution"]
            rendered = cadence_ledger.render_coffee_markdown(context)
            assert action["label"] in rendered
            assert spec["source"] in action["label"]
            for key in ("baseline", "threshold"):
                assert str(spec[key]) in action["label"]
            assert spec["verification"] in rendered
            assert all(item["selection_effect"] == "navigate" for item in context["actions"][1:])
            cadence_ledger.record_coffee_presentation(connection, context, rendered)
        bad = deepcopy(context["actions"])
        bad[0]["label"] = "Execute: run the next future experiment."
        with pytest.raises(cadence_ledger.CadenceLedgerError, match="specification"):
            cadence_ledger.validate_actions(bad)
        bad = deepcopy(context["actions"])
        bad[0]["target"] = "another-context"
        with pytest.raises(cadence_ledger.CadenceLedgerError, match="specification"):
            cadence_ledger.validate_actions(bad)
    finally:
        connection.close()


def test_cold_start_uses_execution_specification():
    action = cadence_ledger.build_cold_start_actions()[0]
    assert action["label"] == cadence_ledger.execution_label(action["execution"])
    assert action["execution"]["source"] in action["label"]


def test_historical_summary_uses_rows_without_rewriting_receipt(tmp_path):
    legacy = {"schema_version": 1, "status": "review_complete", "pending_count": 0,
              "reviews": [{"hook": "one", "status": "reviewed", "disposition": "evidence_gap"},
                          {"hook": "two", "status": "unchanged", "disposition": "proposed_hit"},
                          {"hook": "three", "status": "review_unavailable"},
                          {"hook": "four", "status": "review_failed"}]}
    path = tmp_path / "historical.json"
    path.write_text(json.dumps(legacy), encoding="utf-8")
    before = path.read_bytes()
    result = forecast.review_summary(json.loads(before))
    assert result["schema_version"] == 2
    assert result["status"] == "review_incomplete"
    assert [result[key] for key in ("pending_count", "reviewed_count", "unavailable_count", "failed_count", "gap_count", "proposed_outcome_count")] == [0, 2, 1, 1, 1, 1]
    assert path.read_bytes() == before
    assert legacy["status"] == "review_complete"
    assert forecast.review_summary({**legacy, "pending_count": 1})["status"] == "forecast_review_required"
    assert forecast.review_summary({**legacy, "reviews": legacy["reviews"][:2]})["status"] == "review_complete"


@pytest.mark.parametrize("legacy", [{"status": "review_complete"}, {"reviews": [], "status": "review_complete"},
                                   {"pending_count": 0, "reviews": [{"hook": "x", "status": "unknown"}]},
                                   {"schema_version": 99, "pending_count": 0, "reviews": []},
                                   {"coverage_known": False, "pending_count": 0, "reviews": []}])
def test_unknown_history_never_implies_complete(legacy):
    result = forecast.review_summary(legacy)
    assert result["status"] == "review_incomplete"
    assert result["coverage_known"] is False


def test_living_note_lifecycle_guidance_covers_synthetic_cases():
    instructions = (ROOT / "docs/skill-drafts/mira-notes/SKILL.md").read_text(encoding="utf-8")
    cases = json.loads((ROOT / "docs/experiments/skill-repairs/note-cases.json").read_text(encoding="utf-8"))
    for case in cases:
        assert case["status"] in {"working", "superseded", "closed"}
        assert case["path"].startswith("archive/notes/")
        name = Path(case["path"]).name
        assert name[:4].isdigit() == (case["form"] == "dated-observation")
        if case["status"] == "superseded":
            assert case["successor"] in {item["path"] for item in cases}
        if case["status"] == "closed":
            assert case["reason"]
    for phrase in ("stable", "undated filename", "current interpretation", "dated observations",
                   "meaningful corrections", "link its successor", "mark it `closed`", "Do not automatically rename"):
        assert phrase in instructions

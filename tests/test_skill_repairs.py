"""Behavioral boundaries for the bounded skill repairs; no live carriers."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import elicitation
import interaction_context


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
        surface["options"].pop()
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

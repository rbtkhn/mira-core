from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import elicitation  # noqa: E402
import interaction_context  # noqa: E402


def decision_surface(*, complete_action: bool = True) -> dict[str, object]:
    surface: dict[str, object] = {
        "type": "decision-navigation",
        "options": [
            {
                "key": "apply-change",
                "role": "recommended",
                "label": "Execute the bounded local change",
                "selection_effect": "execute",
            },
            {
                "key": "inspect",
                "role": "alternative",
                "label": "Inspect the evidence",
                "selection_effect": "navigate",
            },
            {
                "key": "pause",
                "role": "overlooked",
                "label": "Pause without changing state",
                "selection_effect": "navigate",
            },
        ],
        "action_readiness": {
            "ready_option_keys": ["apply-change"],
            "all_navigation_reason": None,
            "blocked_action": None,
        },
    }
    if complete_action:
        surface["action_context"] = {
            "apply-change": {
                "target": "scripts/example.py",
                "verification": "run the focused unit test",
                "required_authority": "repository-edit",
            }
        }
    return surface


def pending_action(*, effect: str = "execute", action_id: str = "bounded") -> dict[str, str]:
    return {
        "action_id": action_id,
        "visible_label": f"{effect.capitalize()} the bounded local change",
        "effect": effect,
        "target": "scripts/example.py",
        "verification": "run the focused unit test",
        "required_authority": "repository-edit",
    }


def test_elicitation_projects_silent_transient_capsules_without_breaking_fields() -> None:
    normalized = elicitation.validate_elicitation_surface(decision_surface())
    assert normalized["options"][0]["key"] == "apply-change"
    capsule = normalized["context_capsule"]
    assert capsule["state"] == "awaiting-selection"
    assert capsule["display_policy"] == "silent-by-default"
    assert capsule["persistence"] == "none"
    assert capsule["authority_effect"] == "none"
    assert capsule["pending_actions"][0]["target"] == "scripts/example.py"
    interpreted = elicitation.interpret_elicitation_response(decision_surface(), "A")
    assert interpreted["ordered_selected_branches"][0]["action_authorized"] is True
    assert interpreted["context_capsule"]["state"] == "selected"


def test_existing_action_surface_without_context_remains_compatible_but_fails_closed() -> None:
    normalized = elicitation.validate_elicitation_surface(
        decision_surface(complete_action=False)
    )
    capsule = normalized["context_capsule"]
    assert capsule["pending_actions"] == []
    assert capsule["incomplete_action_context_keys"] == ["apply-change"]
    result = interaction_context.resolve_followup(capsule, "make it so")
    assert result["classification"] == "clarification-required"
    assert result["action_authorized"] is False


@pytest.mark.parametrize("response", ["make it so", "go ahead", "do it"])
def test_one_exact_execute_action_accepts_vague_imperative(response: str) -> None:
    capsule = interaction_context.capsule_from_pending_action(pending_action())
    result = interaction_context.resolve_followup(capsule, response)
    assert result["classification"] == "bounded-continuation"
    assert result["exact_meaning"]["target"] == "scripts/example.py"
    assert result["action_authorized"] is True
    assert result["authority_effect"] == "execute"


@pytest.mark.parametrize("effect", ["commit", "push", "send", "stage", "publish", "deploy", "spend", "communicate"])
def test_vague_imperative_never_crosses_consequential_effect(effect: str) -> None:
    capsule = interaction_context.capsule_from_pending_action(
        pending_action(effect=effect)
    )
    result = interaction_context.resolve_followup(capsule, "make it so")
    assert result["classification"] == "clarification-required"
    assert result["next_route"] == "domain-authority-router"
    assert result["action_authorized"] is False
    assert result["authority_effect"] == "none"


def test_multiple_actions_and_missing_action_context_fail_closed() -> None:
    first = pending_action(action_id="first")
    capsule = interaction_context.capsule_from_pending_action(first)
    second = pending_action(action_id="second")
    capsule["pending_actions"].append(second)
    capsule["context_digest"] = interaction_context._digest(capsule)
    result = interaction_context.resolve_followup(capsule, "do it")
    assert result["ambiguity"] == "requires-exactly-one-pending-action"
    assert result["action_authorized"] is False


@pytest.mark.parametrize("response", ["sounds good", "very well", "as you wish", "I defer to you"])
def test_soft_assent_is_agreement_only(response: str) -> None:
    result = interaction_context.resolve_followup(
        interaction_context.capsule_from_pending_action(pending_action()), response
    )
    assert result["classification"] == "agreement-only"
    assert result["authority_effect"] == "none"


@pytest.mark.parametrize("command", ["coffee", "dream", "rest"])
def test_exact_cadence_command_ignores_pending_action(command: str) -> None:
    result = interaction_context.resolve_followup(
        interaction_context.capsule_from_pending_action(pending_action()), command
    )
    assert result["classification"] == "cadence-command"
    assert result["next_route"] == f"skill:{command}"
    assert result["authority_effect"] == "none"


def test_explicit_git_command_bypasses_compressed_inference() -> None:
    result = interaction_context.resolve_followup(
        interaction_context.capsule_from_pending_action(pending_action()),
        "stage and commit",
    )
    assert result["classification"] == "explicit-direct-command"
    assert result["next_route"] == "domain-authority-router"
    assert result["authority_effect"] == "none"


def test_exact_letter_stale_digest_and_closed_repeat_are_distinct() -> None:
    capsule = elicitation.validate_elicitation_surface(decision_surface())[
        "context_capsule"
    ]
    selected = interaction_context.resolve_followup(capsule, "A")
    assert selected["classification"] == "exact-menu-selection"
    assert selected["action_authorized"] is True
    stale = interaction_context.resolve_followup(
        capsule, "A", expected_context_digest="0" * 64
    )
    assert stale["ambiguity"] == "stale-context"
    closed = interaction_context.capsule_from_normalized_surface(
        elicitation.validate_elicitation_surface(decision_surface()),
        state="closed",
        selected_letters=["A"],
    )
    repeated = interaction_context.resolve_followup(closed, "A")
    assert repeated["classification"] == "settled-no-op"
    assert repeated["action_authorized"] is False


def test_compound_letters_resolve_order_without_broad_action_authority() -> None:
    capsule = elicitation.validate_elicitation_surface(decision_surface())[
        "context_capsule"
    ]
    result = interaction_context.resolve_followup(capsule, "B,C")
    assert result["classification"] == "exact-compound-menu-selection"
    assert result["action_authorized"] is False
    assert result["authority_effect"] == "none"
    assert [item["letter"] for item in result["exact_meaning"]["ordered_selected_branches"]] == [
        "B",
        "C",
    ]


@pytest.mark.parametrize(
    ("response", "ambiguity"),
    (
        ("B,B", "duplicate-option-letter"),
        ("B,Z", "unknown-option-letter"),
        ("B,C,D", "pause-or-deepen-cannot-be-compounded"),
    ),
)
def test_invalid_compound_followups_require_clarification(
    response: str, ambiguity: str
) -> None:
    surface = decision_surface()
    surface["options"].append(
        {
            "key": "deepen",
            "role": "pause-or-deepen",
            "label": "Pause or deepen",
            "selection_effect": "navigate",
        }
    )
    capsule = elicitation.validate_elicitation_surface(surface)[
        "context_capsule"
    ]
    result = interaction_context.resolve_followup(capsule, response)
    assert result["classification"] == "clarification-required"
    assert result["ambiguity"] == ambiguity
    assert result["action_authorized"] is False


def test_yes_answers_one_non_action_yes_option_but_never_an_action() -> None:
    neutral = elicitation.validate_elicitation_surface(
        {
            "type": "neutral-evidence",
            "options": [{"key": "yes", "label": "Yes"}, {"key": "no", "label": "No"}],
        }
    )["context_capsule"]
    assert interaction_context.resolve_followup(neutral, "yes")["classification"] == "factual-confirmation"
    action = interaction_context.capsule_from_pending_action(pending_action())
    blocked = interaction_context.resolve_followup(action, "yes")
    assert blocked["classification"] == "clarification-required"
    assert blocked["action_authorized"] is False


def test_freeform_routes_to_intent_recovery() -> None:
    result = interaction_context.resolve_followup(
        interaction_context.capsule_from_pending_action(pending_action()),
        "Could we approach this differently?",
    )
    assert result["classification"] == "intent-recovery-required"
    assert result["next_route"] == "intent-recovery"


def test_malformed_or_internally_inconsistent_capsules_fail() -> None:
    capsule = interaction_context.capsule_from_pending_action(pending_action())
    corrupted = copy.deepcopy(capsule)
    corrupted["pending_actions"][0]["target"] = "other-target"
    with pytest.raises(interaction_context.InteractionContextError, match="digest"):
        interaction_context.resolve_followup(corrupted, "do it")
    inconsistent = copy.deepcopy(capsule)
    inconsistent["state"] = "closed"
    inconsistent["context_digest"] = interaction_context._digest(inconsistent)
    with pytest.raises(interaction_context.InteractionContextError, match="closed"):
        interaction_context.resolve_followup(inconsistent, "do it")


@pytest.mark.parametrize("missing", ["target", "verification", "required_authority"])
def test_pending_action_requires_every_exact_boundary_field(missing: str) -> None:
    action = pending_action()
    del action[missing]
    with pytest.raises(interaction_context.InteractionContextError, match=missing.replace("_", " ")):
        interaction_context.capsule_from_pending_action(action)


def test_command_router_is_read_only_and_emits_json(tmp_path: Path) -> None:
    action_path = tmp_path / "action.json"
    action_path.write_text(json.dumps(pending_action()), encoding="utf-8")
    before = set(tmp_path.iterdir())
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "run_repo.py"),
            "interaction-context",
            "capsule",
            "--pending-action-json",
            str(action_path),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["persistence"] == "none"
    assert set(tmp_path.iterdir()) == before

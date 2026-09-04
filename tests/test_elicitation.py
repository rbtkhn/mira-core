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
import codex_skill_registry
import elicitation


PRESENTED_AT = "2026-07-30T12:00:00+00:00"


def decision_surface(
    labels: tuple[str, ...] = (
        "Inspect the bounded evidence",
        "Compare another path",
        "Test the overlooked inverse",
        "Pause and deepen",
    ),
    selection_effects: tuple[str, ...] | None = None,
    *,
    all_navigation_reason: str = "no-bounded-action",
    ready_option_keys: list[str] | None = None,
    learning_eligibility: tuple[str, ...] | None = None,
    final_response: bool | None = None,
) -> dict:
    roles = (
        "recommended",
        "alternative",
        "overlooked",
        "pause-or-deepen",
    )
    effects = selection_effects or ("navigate",) * len(labels)
    executable_keys = [
        f"path-{index}"
        for index, effect in enumerate(effects)
        if effect != "navigate"
    ]
    return {
        "type": "decision-navigation",
        **({"final_response": final_response} if final_response is not None else {}),
        "presented_at": PRESENTED_AT,
        "action_readiness": {
            "ready_option_keys": (
                executable_keys if ready_option_keys is None else ready_option_keys
            ),
            "all_navigation_reason": (
                None if executable_keys else all_navigation_reason
            ),
            "blocked_action": (
                None
                if executable_keys
                else {
                    "action": "Execute the bounded next step",
                    "blocker": "No safe target is bounded from current evidence",
                    "ready_when": "A concrete target and verification step are known",
                }
            ),
        },
        "options": [
            {
                "key": f"path-{index}",
                "role": roles[index],
                "label": label,
                "selection_effect": effects[index],
                **(
                    {"learning_eligibility": learning_eligibility[index]}
                    if learning_eligibility is not None
                    else {}
                ),
            }
            for index, label in enumerate(labels)
        ],
    }


def response_controls(basis: str) -> dict:
    surface = decision_surface(
        labels=("Close", "Correct", "Explain", "New task"),
        learning_eligibility=("none",) * 4, final_response=True,
    )
    surface.pop("action_readiness")
    surface.update(
        closure_state="settled", surface_kind="response-controls",
        next_option_assessment={"basis": basis, "candidates": []},
    )
    return surface


def completed_work_with_commit_option() -> dict:
    surface = decision_surface(
        labels=("Commit: Stage and commit scripts/example.py locally", "Review diff", "Compare scope", "Pause"),
        selection_effects=("commit", "navigate", "navigate", "navigate"),
        learning_eligibility=("eligible", "none", "none", "none"), final_response=True,
    )
    surface["closure_state"] = "settled"
    surface["next_option_assessment"] = {
        "basis": "Repairs are complete; exact staging scope and validation are known.",
        "candidates": [{"label": "Commit repaired script", "status": "ready",
                        "reason": "Only local commit authority remains.", "option_key": "path-0"}],
    }
    surface["action_context"] = {"path-0": {
        "target": "scripts/example.py", "verification": "Focused tests and staged diff check",
        "required_authority": "Local staging and commit only; no push",
    }}
    return surface


def test_completed_repairs_can_offer_commit_without_reopening_the_repair() -> None:
    surface = completed_work_with_commit_option()
    normalized = elicitation.validate_elicitation_surface(surface)
    assert normalized["closure_state"] == "settled"
    assert normalized["action_readiness"]["ready_option_keys"] == ["path-0"]
    result = elicitation.interpret_elicitation_response(normalized, "A")
    assert result["ordered_selected_branches"][0]["selection_effect"] == "commit"
    assert result["ordered_selected_branches"][0]["action_authorized"] is True


@pytest.mark.parametrize("missing", ["action_readiness", "action_context", "next_option_assessment"])
def test_completion_does_not_bypass_decision_requirements(missing: str) -> None:
    surface = completed_work_with_commit_option()
    surface.pop(missing)
    with pytest.raises(elicitation.ElicitationError):
        elicitation.validate_elicitation_surface(surface)


@pytest.mark.parametrize("status", ["ready", "navigational"])
def test_response_controls_cannot_hide_known_meaningful_options(status: str) -> None:
    surface = response_controls("Repair is complete, but a useful next step exists.")
    surface["next_option_assessment"]["candidates"] = [{
        "label": "Commit or inspect exact commit scope", "status": status,
        "reason": "The next repository decision remains useful.", "option_key": "path-0",
    }]
    with pytest.raises(elicitation.ElicitationError, match="cannot hide meaningful"):
        elicitation.validate_elicitation_surface(surface)


def test_legacy_settled_flag_alone_no_longer_selects_generic_controls() -> None:
    surface = response_controls("Acknowledgement")
    surface.pop("surface_kind")
    with pytest.raises(elicitation.ElicitationError, match="action_readiness"):
        elicitation.validate_elicitation_surface(surface)


def test_response_controls_require_independent_assessment() -> None:
    surface = response_controls("Acknowledgement")
    surface.pop("next_option_assessment")
    with pytest.raises(elicitation.ElicitationError, match="next_option_assessment"):
        elicitation.validate_elicitation_surface(surface)


@pytest.mark.parametrize("basis", [
    "Simple thanks: no unresolved work or useful new objective was identified.",
    "Operator explicitly stopped: no further work should be offered for execution.",
])
def test_acknowledgements_and_stops_keep_transient_controls(basis: str) -> None:
    surface = response_controls(basis)
    result = elicitation.interpret_elicitation_response(surface, "A")
    assert result["receipt_count"] == 0
    assert result["ordered_selected_branches"][0]["action_authorized"] is False


def test_completed_commit_may_offer_push_inspection_without_push_authority() -> None:
    surface = completed_work_with_commit_option()
    surface["options"][0].update(label="Review push readiness", selection_effect="navigate")
    surface.pop("action_context")
    surface["action_readiness"] = {
        "ready_option_keys": [], "all_navigation_reason": "material-choice-unresolved",
        "blocked_action": {"action": "Push commit", "blocker": "Destination unresolved",
                           "ready_when": "Destination and remote checks are known"},
    }
    surface["next_option_assessment"] = {
        "basis": "Commit is complete; push readiness is a separate useful question.",
        "candidates": [{"label": "Inspect publication boundary", "status": "navigational",
                        "reason": "Resolve the destination before any push", "option_key": "path-0"}],
    }
    result = elicitation.interpret_elicitation_response(surface, "A")
    assert result["ordered_selected_branches"][0]["action_authorized"] is False


@pytest.mark.parametrize("mutation", ["missing-option", "wrong-effect", "empty-basis", "bad-status"])
def test_next_option_assessment_rejects_inconsistent_claims(mutation: str) -> None:
    surface = completed_work_with_commit_option()
    assessment = surface["next_option_assessment"]
    candidate = assessment["candidates"][0]
    if mutation == "missing-option":
        candidate["option_key"] = "omitted-commit"
    elif mutation == "wrong-effect":
        candidate["option_key"] = "path-1"
    elif mutation == "empty-basis":
        assessment["basis"] = ""
    else:
        candidate["status"] = "completed-so-no-options"
    with pytest.raises(elicitation.ElicitationError):
        elicitation.validate_elicitation_surface(surface)


def neutral_surface(*, hold: bool = False) -> dict:
    options = [
        {"key": "yes", "label": "Yes"},
        {"key": "no", "label": "No"},
    ]
    if hold:
        options.append({"key": "hold", "label": "Hold", "control": "hold"})
    return {"type": "neutral-evidence", "options": options}


@pytest.mark.parametrize("count", (3, 4))
def test_decision_surface_accepts_three_or_four_options(count: int) -> None:
    surface = decision_surface()
    surface["options"] = surface["options"][:count]
    normalized = elicitation.validate_elicitation_surface(surface)
    assert len(normalized["options"]) == count
    assert all(
        option["selection_effect"] == "navigate"
        for option in normalized["options"]
    )
    assert all(
        option["learning_eligibility"] == "eligible"
        for option in normalized["options"]
    )
    assert normalized["authority_effect"] == "none"
    assert normalized["action_readiness"] == {
        "ready_option_keys": [],
        "all_navigation_reason": "no-bounded-action",
        "blocked_action": {
            "action": "Execute the bounded next step",
            "blocker": "No safe target is bounded from current evidence",
            "ready_when": "A concrete target and verification step are known",
        },
    }


@pytest.mark.parametrize("count", (0, 1, 2, 5))
def test_decision_surface_rejects_other_option_counts(count: int) -> None:
    surface = decision_surface()
    if count == 5:
        surface["options"].append(
            {
                "key": "path-4",
                "role": "overlooked",
                "label": "A fifth path",
                "selection_effect": "navigate",
            }
        )
    else:
        surface["options"] = surface["options"][:count]
    with pytest.raises(elicitation.ElicitationError, match="three or four"):
        elicitation.validate_elicitation_surface(surface)


@pytest.mark.parametrize("count", (2, 3, 4))
def test_neutral_surface_accepts_two_to_four_answers(count: int) -> None:
    surface = {
        "type": "neutral-evidence",
        "options": [
            {"key": f"fact-{index}", "label": f"Fact {index}"}
            for index in range(count)
        ],
    }
    normalized = elicitation.validate_elicitation_surface(surface)
    assert len(normalized["options"]) == count
    assert all("role" not in option for option in normalized["options"])


def test_neutral_surface_rejects_roles_and_action_labels() -> None:
    role_surface = neutral_surface()
    role_surface["options"][0]["role"] = "recommended"
    with pytest.raises(elicitation.ElicitationError, match="must not assign roles"):
        elicitation.validate_elicitation_surface(role_surface)
    action_surface = neutral_surface()
    action_surface["options"][0]["label"] = "Send the report"
    with pytest.raises(elicitation.ElicitationError, match="action-authorizing"):
        elicitation.validate_elicitation_surface(action_surface)
    effect_surface = neutral_surface()
    effect_surface["options"][0]["selection_effect"] = "navigate"
    with pytest.raises(elicitation.ElicitationError, match="selection_effect"):
        elicitation.validate_elicitation_surface(effect_surface)
    learning_surface = neutral_surface()
    learning_surface["options"][0]["learning_eligibility"] = "none"
    with pytest.raises(elicitation.ElicitationError, match="learning_eligibility"):
        elicitation.validate_elicitation_surface(learning_surface)


def test_learning_eligibility_is_optional_but_strict_when_present() -> None:
    normalized = elicitation.validate_elicitation_surface(decision_surface())
    assert {item["learning_eligibility"] for item in normalized["options"]} == {
        "eligible"
    }

    transient = decision_surface(
        learning_eligibility=("none", "none", "none", "none")
    )
    normalized = elicitation.validate_elicitation_surface(transient)
    assert {item["learning_eligibility"] for item in normalized["options"]} == {
        "none"
    }

    invalid = decision_surface()
    invalid["options"][0]["learning_eligibility"] = "automatic"
    with pytest.raises(elicitation.ElicitationError, match="eligible or none"):
        elicitation.validate_elicitation_surface(invalid)


def test_final_response_requires_four_explicitly_classified_options() -> None:
    final = decision_surface(
        learning_eligibility=("eligible", "eligible", "none", "none"),
        final_response=True,
    )
    normalized = elicitation.validate_elicitation_surface(final)
    assert normalized["final_response"] is True
    assert len(normalized["options"]) == 4

    three = decision_surface(
        learning_eligibility=("eligible", "eligible", "none", "none"),
        final_response=True,
    )
    three["options"] = three["options"][:3]
    with pytest.raises(elicitation.ElicitationError, match="exactly four"):
        elicitation.validate_elicitation_surface(three)

    implicit = decision_surface(final_response=True)
    with pytest.raises(elicitation.ElicitationError, match="explicit"):
        elicitation.validate_elicitation_surface(implicit)


def test_final_response_flag_is_decision_only_and_strictly_boolean() -> None:
    neutral = neutral_surface()
    neutral["final_response"] = True
    with pytest.raises(elicitation.ElicitationError, match="neutral evidence"):
        elicitation.validate_elicitation_surface(neutral)

    invalid = decision_surface()
    invalid["final_response"] = "yes"
    with pytest.raises(elicitation.ElicitationError, match="true or false"):
        elicitation.validate_elicitation_surface(invalid)


def test_final_response_ready_options_require_complete_action_context() -> None:
    final = decision_surface(
        labels=(
            "Execute: apply the bounded change",
            "Inspect another path",
            "Test the overlooked inverse",
            "Pause and deepen",
        ),
        selection_effects=("execute", "navigate", "navigate", "navigate"),
        learning_eligibility=("eligible", "eligible", "eligible", "none"),
        final_response=True,
    )
    with pytest.raises(elicitation.ElicitationError, match="complete action_context"):
        elicitation.validate_elicitation_surface(final)

    final["action_context"] = {
        "path-0": {
            "target": "scripts/example.py",
            "verification": "run the focused unit test",
            "required_authority": "repository-edit",
        }
    }
    normalized = elicitation.validate_elicitation_surface(final)
    assert normalized["context_capsule"]["incomplete_action_context_keys"] == []


def test_decision_surface_requires_known_machine_checked_effects() -> None:
    missing = decision_surface()
    del missing["options"][0]["selection_effect"]
    with pytest.raises(elicitation.ElicitationError, match="selection_effect"):
        elicitation.validate_elicitation_surface(missing)

    unknown = decision_surface()
    unknown["options"][0]["selection_effect"] = "deploy"
    with pytest.raises(elicitation.ElicitationError, match="unsupported selection_effect"):
        elicitation.validate_elicitation_surface(unknown)

    for noncanonical in ("EXECUTE", "Navigate", "sEnD"):
        wrong_case = decision_surface()
        wrong_case["options"][0]["selection_effect"] = noncanonical
        with pytest.raises(
            elicitation.ElicitationError, match="unsupported selection_effect"
        ):
            elicitation.validate_elicitation_surface(wrong_case)


@pytest.mark.parametrize(
    ("selection_effect", "label"),
    (
        ("navigate", "Inspect the bounded evidence"),
        ("execute", "Execute the bounded action"),
        ("stage", "Stage the bounded files"),
        ("commit", "Commit the bounded change"),
        ("push", "Push the bounded branch"),
        ("send", "Send the bounded message"),
    ),
)
def test_canonical_selection_effects_validate(
    selection_effect: str, label: str
) -> None:
    surface = decision_surface(
        (label, "Compare", "Invert"),
        (selection_effect, "navigate", "navigate"),
    )
    normalized = elicitation.validate_elicitation_surface(surface)
    assert normalized["options"][0]["selection_effect"] == selection_effect


def test_effect_and_visible_label_must_match() -> None:
    mismatched = decision_surface(
        selection_effects=("send", "navigate", "navigate", "navigate")
    )
    with pytest.raises(elicitation.ElicitationError, match="must match"):
        elicitation.validate_elicitation_surface(mismatched)

    wrong_action_verb = decision_surface(
        ("Send the bounded action", "Compare", "Invert"),
        ("execute", "navigate", "navigate"),
    )
    with pytest.raises(elicitation.ElicitationError, match="must match"):
        elicitation.validate_elicitation_surface(wrong_action_verb)

    action_label_navigation = decision_surface(("Send the report", "Compare", "Invert"))
    with pytest.raises(elicitation.ElicitationError, match="navigate options"):
        elicitation.validate_elicitation_surface(action_label_navigation)


def test_decision_surface_requires_action_readiness_metadata() -> None:
    surface = decision_surface()
    del surface["action_readiness"]
    with pytest.raises(elicitation.ElicitationError, match="action_readiness"):
        elicitation.validate_elicitation_surface(surface)


def test_mixed_surface_requires_ready_keys_to_match_executable_options() -> None:
    valid = decision_surface(
        ("Execute the bounded fix", "Compare", "Invert"),
        ("execute", "navigate", "navigate"),
    )
    normalized = elicitation.validate_elicitation_surface(valid)
    assert normalized["action_readiness"] == {
        "ready_option_keys": ["path-0"],
        "all_navigation_reason": None,
        "blocked_action": None,
    }

    omitted = decision_surface(
        ("Execute the bounded fix", "Compare", "Invert"),
        ("execute", "navigate", "navigate"),
        ready_option_keys=[],
    )
    with pytest.raises(elicitation.ElicitationError, match="exactly match"):
        elicitation.validate_elicitation_surface(omitted)

    navigation_key = decision_surface(ready_option_keys=["path-0"])
    with pytest.raises(elicitation.ElicitationError, match="exactly match"):
        elicitation.validate_elicitation_surface(navigation_key)


def test_all_navigation_surface_requires_a_bounded_reason() -> None:
    missing = decision_surface(all_navigation_reason=None)
    with pytest.raises(elicitation.ElicitationError, match="recognized"):
        elicitation.validate_elicitation_surface(missing)

    unknown = decision_surface(all_navigation_reason="confirm-again")
    with pytest.raises(elicitation.ElicitationError, match="recognized"):
        elicitation.validate_elicitation_surface(unknown)

    for reason in (
        "no-bounded-action",
        "material-choice-unresolved",
        "operator-requested-read-only",
    ):
        normalized = elicitation.validate_elicitation_surface(
            decision_surface(all_navigation_reason=reason)
        )
        assert normalized["action_readiness"]["all_navigation_reason"] == reason


def test_all_navigation_surface_requires_concrete_blocked_action_audit() -> None:
    missing = decision_surface()
    del missing["action_readiness"]["blocked_action"]
    with pytest.raises(elicitation.ElicitationError, match="blocked_action audit"):
        elicitation.validate_elicitation_surface(missing)

    incomplete = decision_surface()
    incomplete["action_readiness"]["blocked_action"]["ready_when"] = ""
    with pytest.raises(elicitation.ElicitationError, match="ready_when"):
        elicitation.validate_elicitation_surface(incomplete)


def test_action_ready_surface_rejects_all_navigation_reason() -> None:
    surface = decision_surface(
        ("Execute the bounded fix", "Compare", "Invert"),
        ("execute", "navigate", "navigate"),
    )
    surface["action_readiness"]["all_navigation_reason"] = "no-bounded-action"
    with pytest.raises(elicitation.ElicitationError, match="must not assign"):
        elicitation.validate_elicitation_surface(surface)


def test_action_readiness_rejects_unknown_and_duplicate_keys() -> None:
    unknown = decision_surface(ready_option_keys=["missing"])
    with pytest.raises(elicitation.ElicitationError, match="unknown option"):
        elicitation.validate_elicitation_surface(unknown)

    duplicate = decision_surface(ready_option_keys=["path-0", "path-0"])
    with pytest.raises(elicitation.ElicitationError, match="must be unique"):
        elicitation.validate_elicitation_surface(duplicate)


def test_single_exploratory_letter_authorizes_no_action() -> None:
    result = elicitation.interpret_elicitation_response(decision_surface(), "a")
    assert result["mode"] == "single"
    assert result["ordered_selected_branches"][0]["option_key"] == "path-0"
    assert result["ordered_selected_branches"][0]["action_authorized"] is False
    assert result["authority_effect"] == "none"
    assert result["receipt_count"] == 1
    assert result["ordered_selected_branches"][0]["retention_effect"] == (
        "choice-select-eligible"
    )


def test_transient_response_control_emits_no_retention_directive(tmp_path: Path) -> None:
    surface = decision_surface(
        ("Close", "Correct", "Deepen", "New task"),
        learning_eligibility=("none", "none", "none", "none"),
    )
    interpretation = elicitation.interpret_elicitation_response(surface, "A")
    assert interpretation["receipt_count"] == 0
    assert interpretation["receipt_directives"] == []
    assert interpretation["ordered_selected_branches"][0]["retention_effect"] == "none"

    db = choice_ledger.connect(tmp_path / "choices.sqlite3")
    assert db.execute("SELECT COUNT(*) FROM choice_prompts").fetchone()[0] == 0


def test_mixed_surface_retains_only_learning_eligible_selection() -> None:
    surface = decision_surface(
        ("Inspect evidence", "Compare", "Correct", "Close"),
        learning_eligibility=("eligible", "eligible", "none", "none"),
    )
    interpretation = elicitation.interpret_elicitation_response(surface, "A,C")
    assert [item["selected_key"] for item in interpretation["receipt_directives"]] == [
        "path-0"
    ]
    directive = interpretation["receipt_directives"][0]
    assert directive["choice_kind"] == "menu-contract-decision-v1"
    assert directive["recommended_review_cohort"] == "menu-contract-natural-use-v1"
    assert "compound_selection_id" not in directive
    assert "compound_order" not in directive
    assert "compound_size" not in directive


def test_compound_metadata_requires_timestamped_retained_bundle() -> None:
    surface = decision_surface()
    surface.pop("presented_at")
    interpretation = elicitation.interpret_elicitation_response(surface, "A,C")
    assert len(interpretation["receipt_directives"]) == 2
    assert all(
        directive["requires_presentation_timestamp"] is True
        for directive in interpretation["receipt_directives"]
    )
    assert all(
        "compound_selection_id" not in directive
        for directive in interpretation["receipt_directives"]
    )


@pytest.mark.parametrize("verb", ("execute", "Stage", "COMMIT", "Push", "sEnD"))
def test_reserved_verbs_are_case_insensitive_first_tokens(verb: str) -> None:
    surface = decision_surface(
        (f"{verb}: the bounded action", "Compare", "Invert"),
        (verb.lower(), "navigate", "navigate"),
    )
    result = elicitation.interpret_elicitation_response(surface, "A")
    branch = result["ordered_selected_branches"][0]
    assert branch["action_authorized"] is True
    assert branch["normalized_reserved_verb"] == verb.lower()
    assert branch["selection_effect"] == verb.lower()
    assert branch["exact_bounded_action_label"] == f"{verb}: the bounded action"


@pytest.mark.parametrize(
    "label", ("Review and push the commit", "Publish the brief", "Deploy now")
)
def test_non_elicitation_action_labels_remain_exploratory(label: str) -> None:
    surface = decision_surface((label, "Compare", "Invert"))
    branch = elicitation.interpret_elicitation_response(surface, "A")[
        "ordered_selected_branches"
    ][0]
    assert branch["action_authorized"] is False
    assert branch["normalized_reserved_verb"] is None


def test_stage_action_label_authorizes_only_when_validated_as_stage() -> None:
    surface = decision_surface(
        ("Stage: archive/notes/example.md", "Compare", "Invert"),
        ("stage", "navigate", "navigate"),
    )
    result = elicitation.interpret_elicitation_response(surface, "A")
    branch = result["ordered_selected_branches"][0]
    assert branch["action_authorized"] is True
    assert branch["normalized_reserved_verb"] == "stage"
    assert branch["selection_effect"] == "stage"
    assert branch["exact_bounded_action_label"] == "Stage: archive/notes/example.md"

    navigation = decision_surface(("Stage the files", "Compare", "Invert"))
    with pytest.raises(elicitation.ElicitationError, match="navigate options"):
        elicitation.validate_elicitation_surface(navigation)


def test_compound_selection_preserves_order_and_receipt_identity() -> None:
    result = elicitation.interpret_elicitation_response(decision_surface(), "C,A")
    assert [item["letter"] for item in result["ordered_selected_branches"]] == ["C", "A"]
    assert [item["selected_key"] for item in result["receipt_directives"]] == [
        "path-2",
        "path-0",
    ]
    assert len(
        {item["compound_selection_id"] for item in result["receipt_directives"]}
    ) == 1
    assert [item["compound_order"] for item in result["receipt_directives"]] == [
        1,
        2,
    ]
    assert [item["compound_size"] for item in result["receipt_directives"]] == [
        2,
        2,
    ]
    assert len({item["options_hash"] for item in result["receipt_directives"]}) == 1
    assert all(
        "selection_effect" not in option
        for directive in result["receipt_directives"]
        for option in directive["options"]
    )
    assert {item["presented_at"] for item in result["receipt_directives"]} == {
        PRESENTED_AT
    }
    assert all(
        item["authority_effect"] == "none" for item in result["receipt_directives"]
    )
    assert result["stop_on_failure"] is True


def test_compound_receipts_are_separate_and_outcomes_independent(tmp_path: Path) -> None:
    interpretation = elicitation.interpret_elicitation_response(
        decision_surface(), "A,C"
    )
    db = choice_ledger.connect(tmp_path / "choices.sqlite3")
    retained = []
    for index, directive in enumerate(interpretation["receipt_directives"]):
        retained.append(
            choice_ledger.select_branch(
                db,
                choice_id=f"ELI-{index}",
                options=directive["options"],
                selected_key=directive["selected_key"],
                tenant="tenant",
                workspace="workspace",
                lane="lane",
                choice_kind="elicitation-decision",
                consequence_level="bounded",
                decision_summary="Compound elicitation",
                actor="operator",
                presented_at=directive["presented_at"],
                selected_at=f"2026-07-30T12:00:0{index + 1}+00:00",
                idempotency_key=f"retain-{index}",
            )
        )
    assert len({item["choice_id"] for item in retained}) == 2
    assert len({item["options_hash"] for item in retained}) == 1
    assert all(item["authority_effect"] == "none" for item in retained)
    choice_ledger.append_choice_event(
        db,
        choice_id="ELI-0",
        event_type="outcome_recorded",
        idempotency_key="outcome-0",
        occurred_at="2026-07-30T12:01:00+00:00",
        result="successful",
    )
    choice_ledger.append_choice_event(
        db,
        choice_id="ELI-1",
        event_type="outcome_recorded",
        idempotency_key="outcome-1",
        occurred_at="2026-07-30T12:01:01+00:00",
        result="no_action",
    )
    assert choice_ledger.project_choice(db, "ELI-0")["outcome"]["result"] == "successful"
    assert choice_ledger.project_choice(db, "ELI-1")["outcome"]["result"] == "no_action"


@pytest.mark.parametrize(
    ("response", "message"),
    (
        ("A,A", "duplicate"),
        ("A,Z", "unknown"),
        ("A,", "empty"),
        ("A,C>B", "mixed"),
        ("A,D", "pause-or-deepen"),
    ),
)
def test_invalid_compact_responses_fail(response: str, message: str) -> None:
    with pytest.raises(elicitation.ElicitationError, match=message):
        elicitation.interpret_elicitation_response(decision_surface(), response)


def test_ranked_response_is_read_only_and_receipt_free() -> None:
    surface = decision_surface(
        ("Execute the task", "Compare", "Invert"),
        ("execute", "navigate", "navigate"),
    )
    result = elicitation.interpret_elicitation_response(surface, "A>C>B")
    assert result["mode"] == "ranked"
    assert result["ordered_selected_branches"] == []
    assert [item["letter"] for item in result["ordered_preferences"]] == [
        "A",
        "C",
        "B",
    ]
    assert result["top_preference"]["letter"] == "A"
    assert result["top_preference"]["action_authorized"] is False
    assert result["receipt_count"] == 0
    assert result["stop_on_failure"] is False


def test_neutral_letter_and_freeform_are_evidence_not_navigation() -> None:
    selected = elicitation.interpret_elicitation_response(neutral_surface(), "B")
    assert selected["ordered_selected_branches"][0]["option_key"] == "no"
    assert selected["receipt_count"] == 0
    freeform = elicitation.interpret_elicitation_response(
        neutral_surface(), "The source date is uncertain"
    )
    assert freeform["mode"] == "freeform"
    assert freeform["freeform_evidence"] == "The source date is uncertain"
    assert freeform["receipt_count"] == 0
    with pytest.raises(elicitation.ElicitationError, match="one factual answer"):
        elicitation.interpret_elicitation_response(neutral_surface(), "A,B")


def test_action_failure_stops_and_reports_unexecuted_branches() -> None:
    result = elicitation.interpret_elicitation_response(
        decision_surface(
            ("Execute first", "Commit second", "Send third"),
            ("execute", "commit", "send"),
        ),
        "A,B,C",
    )
    failure = elicitation.report_compound_failure(result, "B")
    assert [item["letter"] for item in failure["completed_branches"]] == ["A"]
    assert failure["failed_branch"]["letter"] == "B"
    assert [item["letter"] for item in failure["unexecuted_branches"]] == ["C"]
    assert failure["outcome_directives"] == [
        {"selected_key": "path-1", "result": "unsuccessful"},
        {"selected_key": "path-2", "result": "no_action"},
    ]
    assert failure["stop"] is True


def test_compound_failure_emits_no_outcome_for_transient_controls() -> None:
    result = elicitation.interpret_elicitation_response(
        decision_surface(
            ("Execute first", "Correct", "Compare"),
            ("execute", "navigate", "navigate"),
            learning_eligibility=("eligible", "none", "eligible"),
        ),
        "A,B,C",
    )
    failure = elicitation.report_compound_failure(result, "B")
    assert failure["outcome_directives"] == [
        {"selected_key": "path-2", "result": "no_action"}
    ]


def test_native_and_text_batching_and_question_limit() -> None:
    questions = [neutral_surface() for _ in range(7)]
    native = elicitation.batch_elicitation_questions(questions, "native")
    assert [len(batch) for batch in native["batches"]] == [3, 3, 1]
    text = elicitation.batch_elicitation_questions(questions, "text")
    assert all(len(batch) == 1 for batch in text["batches"])
    with pytest.raises(elicitation.ElicitationError, match="at most ten"):
        elicitation.batch_elicitation_questions(
            [neutral_surface() for _ in range(11)], "native"
        )


def test_hold_stops_remaining_intake() -> None:
    interpretation = elicitation.interpret_elicitation_response(
        neutral_surface(hold=True), "C"
    )
    result = elicitation.apply_intake_response(
        interpretation, ["question-2", "question-3"]
    )
    assert result["status"] == "held"
    assert result["remaining_questions"] == []
    assert result["stopped_questions"] == ["question-2", "question-3"]


def test_skill_discovery_metadata_and_registry_resolve_to_canonical_skill() -> None:
    root = REPO_ROOT / "docs" / "skill-drafts" / "elicitation"
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    metadata = (root / "agents" / "openai.yaml").read_text(encoding="utf-8")
    frontmatter = [
        line.split(":", 1)[0]
        for line in skill.split("---", 2)[1].splitlines()
        if ":" in line
    ]
    assert frontmatter == ["name", "description"]
    assert "Use implicitly only when safe execution is blocked" in skill
    assert "contradiction-check" in skill
    assert "grants no authority" in skill
    assert "allow_implicit_invocation: true" in metadata
    assert 'default_prompt: "Use $elicitation' in metadata
    entry = codex_skill_registry.build_registry()["elicitation"]
    assert entry.source == root / "SKILL.md"
    assert entry.dest.name == "SKILL.md"
    assert entry.dest.parent.name == "elicitation"


def test_skill_contract_has_strict_implicit_invocation_gate() -> None:
    skill = (
        REPO_ROOT / "docs" / "skill-drafts" / "elicitation" / "SKILL.md"
    ).read_text(encoding="utf-8")
    for condition in (
        "`blocked`",
        "`material`",
        "`human-only`",
        "`immediate`",
        "`unsettled`",
    ):
        assert condition in skill
    assert "An explicit request for clarification" in skill
    for non_trigger in (
        "File inspection",
        "diagnostics",
        "test design",
        "status reporting",
        "diff review",
        "reversible",
        "read-only work",
    ):
        assert non_trigger in skill
    assert "newly emerged blocker" in skill
    assert "exact bounded action is ready" in skill
    assert "Classify every decision option independently" in skill
    assert "ready_option_keys" in skill
    assert "all_navigation_reason" in skill
    assert "settle, confirm" in skill


def test_host_and_choice_contract_require_option_level_readiness() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    choices = (
        REPO_ROOT / "docs" / "skill-drafts" / "learn-from-choices" / "SKILL.md"
    ).read_text(encoding="utf-8")
    for contract in (agents, choices):
        normalized = " ".join(contract.split()).casefold()
        assert "independently" in normalized
        assert (
            "mixed executable and navigational" in normalized
            or "mix executable and navigational" in normalized
        )
        assert "settle, confirm" in normalized
        assert "all-navigation" in normalized
        assert "blocked_action" in contract
        assert "all_navigation_reason" in contract
        assert "independently" in contract
    assert "validated mixed `decision-navigation`" in choices


def test_host_and_choice_contract_require_compact_contextual_closure() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    choices = (
        REPO_ROOT / "docs" / "skill-drafts" / "learn-from-choices" / "SKILL.md"
    ).read_text(encoding="utf-8")
    elicitation_skill = (
        REPO_ROOT / "docs" / "skill-drafts" / "elicitation" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "compact contextual four-option A-D surface" in agents
    assert "compact settled closure" in choices
    assert "completed factual answers" in choices
    assert "simple thanks or acknowledgements" in choices
    assert "explicit stops" in choices
    assert "action does not determine the next menu" in elicitation_skill
    assert "next_option_assessment" in elicitation_skill
    assert "Never infer the menu type from completion alone" in choices


def test_choice_contract_makes_bounded_task_creation_executable() -> None:
    choices = (
        REPO_ROOT / "docs" / "skill-drafts" / "learn-from-choices" / "SKILL.md"
    ).read_text(encoding="utf-8")
    normalized = " ".join(choices.split())

    assert "Task or thread creation is action-ready" in normalized
    assert "target project, initial prompt, environment, and verification boundary" in normalized
    assert "do not label it navigation-only" in normalized


def test_choice_contract_respects_durable_batch_authority() -> None:
    choices = (
        REPO_ROOT / "docs" / "skill-drafts" / "learn-from-choices" / "SKILL.md"
    ).read_text(encoding="utf-8")
    normalized = " ".join(choices.split())

    assert "durable batch authority envelope" in normalized
    assert "until its declared review boundary" in normalized
    assert "routine row completion" in normalized
    assert "isolated row failure" in normalized


def test_skill_contract_limits_repeated_selection_chains() -> None:
    skill = (
        REPO_ROOT / "docs" / "skill-drafts" / "elicitation" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "After three consecutive compact selections" in skill
    assert "continue the" in skill
    assert "selected branch" in skill
    assert "to a meaningful result" in skill
    assert "compact settled closure" in skill
    assert "do not manufacture another" in skill
    assert "Explicit creative or preference discovery" in skill
    assert "ten-question limit" in skill
    assert "earlier two-selection saturation rule controls" in skill


def test_skill_contract_exposes_transient_context_and_exact_action_metadata() -> None:
    skill = (
        REPO_ROOT / "docs" / "skill-drafts" / "elicitation" / "SKILL.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "`action_context`",
        "exact `target`",
        "`verification`",
        "`required_authority`",
        "`context_capsule`",
        "interaction-context resolve",
        "Soft assent carries agreement only",
    ):
        assert phrase in skill


def test_cli_validates_and_interprets_without_mutation() -> None:
    surface = json.dumps(decision_surface())
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "elicitation.py"),
            "interpret",
            "--surface-json",
            surface,
            "--response",
            "A>C",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["mode"] == "ranked"
    assert payload["receipt_count"] == 0
    assert payload["authority_effect"] == "none"


def test_cli_transient_control_returns_no_retention_or_outcome_authority() -> None:
    surface = decision_surface(
        ("Close", "Correct", "Deepen", "New task"),
        learning_eligibility=("none", "none", "none", "none"),
        final_response=True,
    )
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "elicitation.py"),
            "interpret",
            "--surface-json",
            json.dumps(surface),
            "--response",
            "A",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["receipt_count"] == 0
    assert payload["receipt_directives"] == []
    assert payload["ordered_selected_branches"][0]["retention_effect"] == "none"
    assert payload["authority_effect"] == "none"
    assert payload["final_response"] is True


def test_cli_json_is_console_safe_and_round_trips_unicode() -> None:
    surface = neutral_surface()
    surface["options"][1]["label"] = 'Καλημέρα "quoted"'
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "elicitation.py"),
            "validate",
            "--surface-json",
            json.dumps(surface),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "\\u039a" in result.stdout
    payload = json.loads(result.stdout)
    assert payload["options"][1]["label"] == 'Καλημέρα "quoted"'

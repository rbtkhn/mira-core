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
) -> dict:
    roles = (
        "recommended",
        "alternative",
        "overlooked",
        "pause-or-deepen",
    )
    return {
        "type": "decision-navigation",
        "presented_at": PRESENTED_AT,
        "options": [
            {"key": f"path-{index}", "role": roles[index], "label": label}
            for index, label in enumerate(labels)
        ],
    }


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
    assert normalized["authority_effect"] == "none"


@pytest.mark.parametrize("count", (0, 1, 2, 5))
def test_decision_surface_rejects_other_option_counts(count: int) -> None:
    surface = decision_surface()
    if count == 5:
        surface["options"].append(
            {"key": "path-4", "role": "overlooked", "label": "A fifth path"}
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


def test_single_exploratory_letter_authorizes_no_action() -> None:
    result = elicitation.interpret_elicitation_response(decision_surface(), "a")
    assert result["mode"] == "single"
    assert result["ordered_selected_branches"][0]["option_key"] == "path-0"
    assert result["ordered_selected_branches"][0]["action_authorized"] is False
    assert result["authority_effect"] == "none"
    assert result["receipt_count"] == 1


@pytest.mark.parametrize("verb", ("execute", "COMMIT", "Push", "sEnD"))
def test_reserved_verbs_are_case_insensitive_first_tokens(verb: str) -> None:
    surface = decision_surface((f"{verb}: the bounded action", "Compare", "Invert"))
    result = elicitation.interpret_elicitation_response(surface, "A")
    branch = result["ordered_selected_branches"][0]
    assert branch["action_authorized"] is True
    assert branch["normalized_reserved_verb"] == verb.lower()
    assert branch["exact_bounded_action_label"] == f"{verb}: the bounded action"


@pytest.mark.parametrize(
    "label", ("Review and push the commit", "Stage the files", "Publish the brief", "Deploy now")
)
def test_non_elicitation_action_labels_remain_exploratory(label: str) -> None:
    surface = decision_surface((label, "Compare", "Invert"))
    branch = elicitation.interpret_elicitation_response(surface, "A")[
        "ordered_selected_branches"
    ][0]
    assert branch["action_authorized"] is False
    assert branch["normalized_reserved_verb"] is None


def test_compound_selection_preserves_order_and_receipt_identity() -> None:
    result = elicitation.interpret_elicitation_response(decision_surface(), "C,A")
    assert [item["letter"] for item in result["ordered_selected_branches"]] == ["C", "A"]
    assert [item["selected_key"] for item in result["receipt_directives"]] == [
        "path-2",
        "path-0",
    ]
    assert len({item["options_hash"] for item in result["receipt_directives"]}) == 1
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
    surface = decision_surface(("Execute the task", "Compare", "Invert"))
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
        decision_surface(("Execute first", "Commit second", "Send third")), "A,B,C"
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
    assert "allow_implicit_invocation: true" in metadata
    assert 'default_prompt: "Use $elicitation' in metadata
    entry = codex_skill_registry.build_registry()["elicitation"]
    assert entry.source == root / "SKILL.md"
    assert entry.dest.name == "SKILL.md"
    assert entry.dest.parent.name == "elicitation"


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

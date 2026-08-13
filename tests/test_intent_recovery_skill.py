from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "docs" / "skill-drafts" / "intent-recovery"


def skill_text() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def test_skill_is_established_locally() -> None:
    skill = skill_text()
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    frontmatter = skill.split("---", 2)[1]

    assert "name: intent-recovery" in frontmatter
    assert "Recover the likely operator intent" in frontmatter
    assert "display_name: \"Intent Recovery\"" in metadata
    assert "default_prompt: \"Use $intent-recovery" in metadata
    assert "allow_implicit_invocation: true" in metadata


def test_intent_recovery_separates_interpretation_from_authority() -> None:
    skill = skill_text()

    for field in ("`literal`", "`likely-intent`", "`uncertainty`", "`next-boundary`"):
        assert field in skill
    assert "Recovered intent:" in skill
    assert "Intent recovery is interpretive preparation" in skill
    assert "never approval to execute" in skill
    assert "Do not infer publication, spending, hiring" in skill
    assert "file-edit, commit, push, send, or deployment authority" in skill


def test_precise_inputs_and_menu_letters_do_not_expand_authority() -> None:
    skill = skill_text()

    for skip_condition in (
        "exact menu selections",
        "clear commands",
        "factual receipts",
        "explicit approvals",
        "genuinely missing evidence",
    ):
        assert skip_condition in skill
    assert "bare menu letter" in skill
    assert "carry only the selected branch text" in skill
    assert "forward. Do not recover, upgrade, or authorize action" in skill
    assert "validated elicitation action surface" in skill
    assert "begins with `Execute`, `Commit`, `Push`, or `Send`" in skill
    assert "`selection_effect` matches" in skill


def test_soft_assent_is_not_upgraded_into_action_authority() -> None:
    skill = skill_text()
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for phrase in ("`as you wish`", "`sounds good`", "`very well`", "`I defer to you`"):
        assert phrase in skill

    assert "not as a clear command, explicit approval, menu selection" in skill
    assert "authority to mutate or act externally" in skill
    assert "without selecting an option for the\n   operator" in skill
    assert "Continue only reversible read-only reasoning already in scope" in skill
    assert "request only the missing authorization" in skill
    assert "Relational deference or soft assent" in agents
    assert "is not a clear command or explicit approval" in agents
    assert "Do not select a recommended option on\nthe operator's behalf" in agents


def test_ambiguous_continuation_requires_one_bounded_pending_action() -> None:
    skill = skill_text()

    assert "ambiguous continuation such as `go ahead` or `do it`" in skill
    assert "one exact, visible, already-bounded action is pending" in skill
    assert "ask one minimal clarification\nbefore consequential action" in skill


def test_local_composition_contracts_are_named() -> None:
    skill = skill_text()
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    elicitation = (
        REPO_ROOT / "docs" / "skill-drafts" / "elicitation" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "`elicitation`" in skill
    assert "`learn-from-choices`" in skill
    assert "`skill-audit`" in skill
    assert "read" in agents
    assert "`docs/skill-drafts/intent-recovery/SKILL.md`" in agents
    assert "[intent-recovery](../intent-recovery/SKILL.md)" in elicitation

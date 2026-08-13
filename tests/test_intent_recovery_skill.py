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

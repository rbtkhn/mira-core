from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "docs" / "skill-drafts" / "learn-from-choices"


def test_skill_is_discoverable_and_implicitly_invoked() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    frontmatter = skill.split("---", 2)[1]
    assert "name: learn-from-choices" in frontmatter
    assert "Use implicitly for every final response" in frontmatter
    assert "display_name: \"Learn From Choices\"" in metadata
    assert "default_prompt: \"Use $learn-from-choices" in metadata
    assert "allow_implicit_invocation: true" in metadata


def test_frontmatter_contains_only_name_and_description() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = [
        line.split(":", 1)[0]
        for line in skill.split("---", 2)[1].splitlines()
        if ":" in line
    ]
    assert frontmatter == ["name", "description"]


def test_universal_contract_has_stable_roles_and_navigation_boundary() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    router = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for role in ("recommended", "alternative", "overlooked", "pause-or-deepen"):
        assert f"`{role}`" in skill
        assert f"`{role}`" in router
    assert "Do not retain an unselected footer" in skill
    assert "bare letter" in router
    assert "never silently" in router
    assert "receipt retention granted no authority" in skill


def test_action_ready_choices_require_machine_validated_elicitation() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "Ordinary possibility menus are navigation-only" in skill
    assert "machine-checked `selection_effect`" in skill
    for verb in ("Execute", "Commit", "Push", "Send"):
        assert f"`{verb}`" in skill
    assert "validated by `elicitation` as `decision-navigation`" in skill
    assert "`Stage`, `Publish`, and `Deploy` require a" in skill
    assert "direct explicit command" in skill


def test_action_sounding_footer_labels_remain_navigation_only() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "`Patch both skills`, `Create tests`, or `Update the file`" in skill
    assert "ordinary footer remains navigation-only" in skill
    assert "Mutation authority through a selected letter requires" in skill
    assert "validated `selection_effect`" in skill


def test_universal_footer_is_not_implicit_elicitation() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "universal possibility footer is not automatically an Elicitation surface" in skill
    assert "Apply Elicitation's implicit-invocation gate independently" in skill
    assert "with an explicit" in skill
    assert "`selection_effect`" in skill


def test_selected_branch_reaches_a_meaningful_result_before_reelicitation() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "all reversible read-only investigation" in skill
    assert "produce a meaningful result" in skill
    assert "Do not use a final response as a progress" in skill
    assert "checkpoint merely to generate another possibility menu" in skill
    assert "newly emerged blocker" in skill


def test_closure_precedes_the_universal_footer() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "Closure takes precedence over the universal footer" in skill
    assert "acknowledge closure without" in skill
    assert "manufacturing another possibility set" in skill


def test_saturation_closes_recursive_interpretive_chains() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    router = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for contract in (skill, router):
        assert "two consecutive" in contract
        assert "deepen the same objective" in contract
        assert "new evidence" in contract
        assert "material contradiction" in contract
        assert "analyze, rewrite" in contract
    assert "Classify closure before possibilities" in skill
    assert "two valid terminal forms" in skill


def test_closure_is_quiet_lifecycle_state_not_outcome_evidence() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    for phrase in (
        "`branch_closed`",
        "`completed`, `paused`, or `saturated`",
        "Successful closure retention is routine internal process",
    ):
        assert phrase in skill
    assert "Closure is lifecycle state" in skill and "not an\noutcome" in skill


def test_private_choice_store_example_matches_repository_guidance() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    canonical = r"C:\private\narrative-choice-history.sqlite3"
    assert canonical in skill
    assert canonical in readme
    assert r"C:\private\choice-history.sqlite3" not in skill


def test_coffee_and_dream_composition_is_bounded() -> None:
    coffee = (REPO_ROOT / "docs" / "skill-drafts" / "coffee" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    dream = (REPO_ROOT / "docs" / "skill-drafts" / "dream" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "choice review" in coffee
    assert "unresolved-outcome prompt" in coffee
    assert "five-to-ten" in coffee
    for role in ("recommended", "alternative", "overlooked", "pause-or-deepen"):
        assert f"`{role}`" in coffee
    assert "Do not solicit or record unresolved choice outcomes" in dream


def test_review_contract_is_staged_and_terminal() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    for phrase in (
        "frozen until ten",
        "cumulative earliest ten",
        "terminal `adjust`",
        "before `pending`",
        "selection frequency was excluded",
    ):
        assert phrase in skill

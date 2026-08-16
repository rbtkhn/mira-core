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


def test_branch_closure_is_separate_from_new_path_navigation() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    router = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for contract in (skill, router):
        normalized = " ".join(contract.split())
        assert "wider conversation" in normalized
        assert "`New paths`" in normalized
        assert "new choice identity" in normalized
        assert "never reopens" in normalized


def test_new_paths_require_independent_eligibility() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    router = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for contract in (skill, router):
        normalized = " ".join(contract.split())
        assert "at least two" in normalized
        assert "genuinely different" in normalized
        assert "explicit stop" in normalized
        assert "wider conversation" in normalized
        assert "manufactured busywork" in normalized
    assert "rewrite, re-audit, compare, or deepen" in " ".join(skill.split())


def test_complete_turn_supports_three_terminal_forms() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "A turn has three valid terminal forms" in skill
    assert "an open branch ends" in skill
    assert "a settled branch ends" in skill
    assert "a settled conversation ends" in skill


def test_closure_debt_audit_distinguishes_open_and_settled_scenarios() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    router = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for contract in (skill, router):
        normalized = " ".join(contract.split())
        assert "closure-debt audit" in normalized
        assert "unsaved substantial document" in normalized
        assert "material evidence gap" in normalized
        assert "operator judgment" in normalized
        assert "bounded recommended action" in normalized
        assert "unfinished promised verification" in normalized
        assert "Merely imaginable adjacent work" in normalized
        assert "complete factual answer" in normalized
        assert "completed verified commit" in normalized or "completed, verified, and committed change" in normalized
        assert "push or publication was not requested" in normalized


def test_saturation_closes_recursive_interpretive_chains() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    router = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for contract in (skill, router):
        assert "two consecutive" in contract
        assert "deepen the same objective" in contract
        assert "new evidence" in contract
        assert "material contradiction" in contract
        assert "analyze, rewrite" in contract
    assert "Classify branch closure separately from new-path navigation" in skill
    assert "three valid terminal forms" in skill


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
    canonical = r"C:\private\mira-core-choice-history.sqlite3"
    assert canonical in skill
    assert canonical in readme
    assert r"C:\private\choice-history.sqlite3" not in skill


def test_substantial_artifact_handoff_has_explicit_persistence_states() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(skill.split())
    for phrase in (
        "saved and verified",
        "not saved",
        "intentionally conversational",
        "privacy/status label",
        "Working-tree presence is distinct",
        "repository admission, staging, commit, push, and publication",
    ):
        assert phrase in normalized


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

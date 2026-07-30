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
    assert "granted no execution authority" in skill


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

from __future__ import annotations

import re
from pathlib import Path

import pytest

from codex_skill_registry import DEPLOYABLE_SKILL_NAMES, parse_skill_frontmatter
from validate_repository import LOCAL_SKILLS


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = REPO_ROOT / "docs" / "skill-drafts"
SHARED = SKILLS / "dream" / "references" / "session-handoff.md"


def local_links(path: Path) -> list[Path]:
    return [
        (path.parent / target.split("#", 1)[0]).resolve()
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8"))
        if "://" not in target and not target.startswith("#")
    ]


@pytest.mark.parametrize("name", ["coffee", "dream", "bridge", "harvest"])
def test_handoff_callers_resolve_the_same_shared_contract(name: str) -> None:
    caller = SKILLS / name / "SKILL.md"
    assert SHARED.resolve() in local_links(caller)


@pytest.mark.parametrize(
    "relative",
    [
        "bridge/SKILL.md",
        "harvest/SKILL.md",
        "dream/references/session-handoff.md",
    ],
)
def test_new_handoff_links_resolve_inside_the_repository(relative: str) -> None:
    for target in local_links(SKILLS / relative):
        assert target.is_relative_to(REPO_ROOT.resolve())
        assert target.is_file(), target


@pytest.mark.parametrize("name", ["bridge", "harvest"])
def test_export_entrypoints_are_local_and_reachable_from_agents(name: str) -> None:
    skill = SKILLS / name / "SKILL.md"
    assert parse_skill_frontmatter(skill)["name"] == name
    routes = re.findall(
        r"`(docs/skill-drafts/[^`]+/SKILL\.md)`",
        (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8"),
    )
    assert skill.relative_to(REPO_ROOT).as_posix() in routes
    assert name in LOCAL_SKILLS
    assert name not in DEPLOYABLE_SKILL_NAMES

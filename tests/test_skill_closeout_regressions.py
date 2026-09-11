"""Routing mechanics and contract readback; not live-agent performance tests."""
from pathlib import Path

import pytest

import codex_skill_registry as registry
import sync_codex_skills as sync
import validate_repository as validator


ROOT = Path(__file__).resolve().parents[1]


def test_local_geo_strategy_excludes_an_installed_stale_copy(tmp_path, monkeypatch):
    installed = tmp_path / "skills"
    stale = installed / "geo-strategy" / "SKILL.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("stale installed instructions", encoding="utf-8")
    monkeypatch.setattr(registry, "CODEX_SKILLS_ROOT", installed)
    assert "geo-strategy" in registry.discover_codex_skill_names()
    assert "geo-strategy" in validator.LOCAL_SKILLS
    assert "geo-strategy" not in registry.build_registry()
    assert "geo-strategy" not in sync.resolve_skills(None)
    with pytest.raises(SystemExit, match="Unknown skill"):
        sync.resolve_skills(["geo-strategy"])
    assert stale.read_text(encoding="utf-8") == "stale installed instructions"
    assert registry.parse_skill_frontmatter(
        ROOT / "docs/skill-drafts/geo-strategy/SKILL.md"
    )["portable"] == "false"


def test_local_route_and_missed_day_contract_readback():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "docs/skill-drafts/geo-strategy/SKILL.md" in agents
    assert "supersedes any installed user-level Geo-Strategy copy" in agents
    geo = (ROOT / "docs/skill-drafts/geo-strategy/SKILL.md").read_text(encoding="utf-8")
    assert "Missed capture days route to weekly catch-up" in geo
    assert "do not create a daily" in geo
    assert "no mandatory menu or fixed option count" in geo


def test_decision_only_contract_and_handoff_summary_readback():
    choices = (ROOT / "docs/skill-drafts/learn-from-choices/SKILL.md").read_text(encoding="utf-8")
    assert "Menus are decision-only" in choices
    assert "single blocking question needs no artificial alternatives" in choices
    assert "machine-checked `selection_effect`" in choices
    assert "Usually offer three" not in choices
    handoff = (ROOT / "docs/skill-drafts/dream/references/session-handoff.md").read_text(encoding="utf-8")
    assert "Compose one canonical packet for saving" in handoff
    assert "identifies the saved packet, never the summary" in handoff

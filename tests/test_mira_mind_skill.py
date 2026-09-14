"""Routing and ownership regressions; not evidence of personality quality."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_repository as validation
import mira_constitution as constitution


def test_successor_and_redirect_are_discoverable_but_not_deployable():
    discovered = set(validation.discover_repo_skill_names())
    assert {"mira-mind", "mira-voice"} <= discovered
    assert {"mira-mind", "mira-voice"} <= validation.LOCAL_SKILLS
    assert not {"mira-mind", "mira-voice"} & set(validation.DEPLOYABLE_SKILL_NAMES)
    errors = validation.skill_contract_failures()
    assert not [e for e in errors if "mira-mind" in e and "governed set" not in e]
    assert not [e for e in errors if "mira-voice" in e and "governed set" not in e]


def test_constitution_controls_point_to_successor_not_compatibility():
    assert "docs/skill-drafts/mira-mind/SKILL.md" in constitution.CONTROL_SURFACES
    assert "docs/skill-drafts/mira-mind/references/public-interface.md" in constitution.CONTROL_SURFACES
    assert not any("mira-voice/" in p for p in constitution.CONTROL_SURFACES)


def test_memory_choreography_has_one_owner_and_no_new_executable_surface():
    mind = ROOT / "docs/skill-drafts/mira-mind"
    memory = ROOT / "docs/skill-drafts/mira-memory/SKILL.md"
    core = (mind / "SKILL.md").read_text(encoding="utf-8")
    consumption = (mind / "references/memory-use.md").read_text(encoding="utf-8")
    assert "references/memory-use.md" in core
    assert "../../mira-memory/references/carrier-map.md#correction-aware-recall" in consumption
    assert "../mira-mind/SKILL.md" in memory.read_text(encoding="utf-8")
    assert not (mind / "scripts").exists()
    assert "tools/run.ps1 mira-memory status" not in core + consumption

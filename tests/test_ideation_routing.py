from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_local_skill_is_discoverable_without_global_deployment():
    import validate_repository
    import codex_skill_registry

    assert "ideation" in validate_repository.LOCAL_SKILLS
    assert "ideation" not in codex_skill_registry.DEPLOYABLE_SKILL_NAMES
    skill = ROOT / "docs/skill-drafts/ideation/SKILL.md"
    assert skill.is_file()
    assert "docs/skill-drafts/ideation/SKILL.md" in (ROOT / "AGENTS.md").read_text(encoding="utf-8")


def test_benchmark_command_resolves_to_restored_runner():
    spec = importlib.util.spec_from_file_location("ideation_route", ROOT / "tools/run_repo.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.SURFACES["ideation-benchmark"] == ROOT / "scripts/ideation_benchmark.py"
    assert module.SURFACES["ideation-benchmark"].is_file()

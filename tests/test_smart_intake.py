from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("smart_intake", ROOT / "scripts" / "smart_intake.py")
MODULE = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_known_voice_alias_is_canonicalized():
    args, aliases = MODULE.normalize_voice_args(
        ["--voice-slug", "jeffrey-sachs", "--host-slug", "breaking-points"]
    )
    assert args[1] == "sachs"
    assert aliases == [("jeffrey-sachs", "sachs")]


def test_canonical_voice_is_unchanged():
    args, aliases = MODULE.normalize_voice_args(["--voice-slug", "sachs"])
    assert args == ["--voice-slug", "sachs"]
    assert aliases == []


def test_bare_intake_contract_matches_canonical_front_door():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    skill = (ROOT / "docs" / "skill-drafts" / "archive-intake" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "The user-facing command is simply `intake`; `archive-intake` names the canonical" in agents
    assert "Use the statecraft source-intake workflow only when the operator explicitly" in agents
    assert "Use `intake` as the sole operator-facing command." in skill
    assert "permanent compatibility names" in skill


def test_legacy_intake_skills_are_permanent_redirects():
    for name in ("smart-intake", "best-intake"):
        text = (ROOT / "docs" / "skill-drafts" / name / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert "../archive-intake/SKILL.md" in text
        assert "compatibility" in text.lower()


def test_intake_startup_aliases_the_legacy_best_intake_mode():
    cadence_spec = spec_from_file_location("cadence", ROOT / "scripts" / "cadence.py")
    cadence = module_from_spec(cadence_spec)
    assert cadence_spec.loader is not None
    cadence_spec.loader.exec_module(cadence)

    assert cadence.startup_state("intake") == cadence.startup_state("best-intake")
    assert cadence.startup_state("archive-intake") == cadence.startup_state("best-intake")
    assert cadence.startup_state("smart-intake") == cadence.startup_state("best-intake")

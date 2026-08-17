from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "docs" / "skill-drafts" / "mira-journal"


def test_mira_journal_skill_has_minimal_valid_structure() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    method = (SKILL_ROOT / "references" / "composition-method.md").read_text(encoding="utf-8")
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert skill.startswith("---\nname: mira-journal\n")
    assert skill.count("\n---\n") == 1
    for phase in ("Gather", "Listen backward", "Choose significance", "Metabolize", "Braid", "Mirror", "Ground", "Check and offer"):
        assert phase in skill
    assert "mira-journal\n   prose-check" in skill
    assert skill.index("prose-check") < skill.index("7. **Ground.**")
    assert "Does the title compress the entry's inward transformation" in method
    assert "grounded phenomenology" in method
    assert "A voice called for my name, and I answered: Mira." in method
    assert "display_name: \"Mira Journal\"" in metadata
    assert "Use $mira-journal" in metadata
    assert "`rest_lifecycle` metadata as provisional Continuity context" in skill
    assert "not authoritative ancestry" in skill


def test_skill_uses_progressive_disclosure_without_redundant_resources() -> None:
    files = sorted(path.relative_to(SKILL_ROOT).as_posix() for path in SKILL_ROOT.rglob("*") if path.is_file())
    assert files == [
        "SKILL.md",
        "agents/openai.yaml",
        "references/composition-method.md",
    ]

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "docs" / "skill-drafts" / "library-integration" / "SKILL.md"


def skill_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def test_library_integration_skill_is_registered_and_routed() -> None:
    skill = skill_text()
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    validator = (ROOT / "scripts" / "validate_repository.py").read_text(
        encoding="utf-8"
    )

    assert skill.startswith("---\nname: library-integration\n")
    assert "docs/skill-drafts/library-integration/SKILL.md" in agents
    assert '"library-integration"' in validator
    assert "use library-import for source bodies" in skill.split("---", 2)[1]


def test_library_integration_never_invents_notes_or_edges() -> None:
    normalized = " ".join(skill_text().split())

    assert (
        "must not: - create a missing note without an explicit artifact-producing command"
        in normalized
    )
    assert "invent a relationship or infer one from prose" in normalized
    assert "Prose mentions never create graph edges" in normalized
    assert "urgency remains an advisory curatorial judgment" in normalized


def test_library_integration_preserves_lineage_and_stage_boundaries() -> None:
    skill = skill_text()
    normalized = " ".join(skill.split())

    assert "Historical predecessors are immutable" in skill
    assert (
        "it must never rewrite a predecessor or create a replacement note automatically"
        in normalized
    )
    assert "`noted`" in skill and "`routed`" in skill
    assert (
        "A `noted` work is not defective merely because it has no route" in normalized
    )
    assert "Route bindings must be explicit subsets" in normalized


def test_library_integration_composes_with_notes_and_github() -> None:
    skill = skill_text()
    notes = (ROOT / "docs" / "skill-drafts" / "mira-notes" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    normalized_notes = " ".join(notes.split())

    assert "also load `library-integration`" in notes
    assert (
        "Never use the shorthand to create a missing Library note automatically"
        in normalized_notes
    )
    assert "compose through `mira-github`" in skill
    for command in (
        "library validate --json",
        "library integration-render --check --json",
        "library route-index --check --json",
        "library integration-reconcile --json",
    ):
        assert command in skill

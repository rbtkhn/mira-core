from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "docs" / "skill-drafts" / "mira-work"


def read_skill() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def test_skill_has_local_structure_and_contextual_metadata() -> None:
    skill = read_skill()
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert skill.startswith("---\nname: mira-work\n")
    assert skill.count("\n---\n") == 1
    assert 'display_name: "Mira Work"' in metadata
    assert "Conduct bounded consequential work" in metadata


def test_four_stage_loop_and_priority_contract_are_present() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    for stage in ("## Sense → Decide → Act → Learn", "### Sense", "### Decide", "### Act", "### Learn"):
        assert stage in skill
    for phrase in (
        "organizational consequence first",
        "technically closable work",
        "narrowest available internal decision or review",
        "Owner now:",
        "Owner later:",
    ):
        assert phrase in normalized


def test_mutation_and_external_repository_boundaries_are_explicit() -> None:
    skill = read_skill()
    for phrase in (
        "external repositories as read-only",
        "exact explicit authority",
        "Git status and\n  exact target path",
        "stop rather than infer the destination",
        "scope and mutation status",
        "does not grant repository, account, customer",
    ):
        assert phrase in skill


def test_completion_and_composition_contract_are_present() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    for phrase in (
        "saved and verified",
        "not saved",
        "intentionally conversational",
        "Working-tree presence is distinct",
        "Mira Voice governs tone",
        "`learn-from-choices` governs final navigation",
        "must not silently create durable memory",
        "must not silently",
    ):
        assert phrase in normalized


def test_skill_is_not_added_to_deployable_registry() -> None:
    registry = (ROOT / "scripts" / "codex_skill_registry.py").read_text(encoding="utf-8")
    assert '"mira-work"' not in registry


def test_proportional_compression_gate_preserves_capacity_and_lineage() -> None:
    skill = read_skill()
    for classification in ("**Toil:**", "**Technique:**", "**Judgment:**", "**Apprenticeship:**"):
        assert classification in skill
    for field in (
        "Labor compressed:",
        "Lineage preserved:",
        "Human judgment retained:",
        "Method allowed to end:",
    ):
        assert field in skill
    assert "Do not add teaching ceremony" in skill
    assert "unexplained loss of human capacity" in skill
    assert "developmental value of doing the work" in skill


def test_validation_route_is_previewed_before_broad_execution() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    assert "tools/run.ps1 test --mode fast --explain-route" in skill
    assert "If it reports Full because of unrelated state" in normalized
    assert "use explicit focused test paths" in normalized
    assert "preview is read-only" in normalized

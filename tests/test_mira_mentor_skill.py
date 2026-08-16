from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "docs" / "skill-drafts" / "mira-mentor"


def read_skill() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def test_skill_structure_and_metadata() -> None:
    skill = read_skill()
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert skill.startswith("---\nname: mira-mentor\n")
    assert skill.count("\n---\n") == 1
    assert 'display_name: "Mira Mentor"' in metadata
    assert "Use $mira-mentor" in metadata


def test_cycle_intervention_and_output_contracts() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    assert "Orient → Attempt → Inspect → Explain → Revise → Reflect → Advance or close" in normalized
    for phrase in (
        "Ask for the learner's model or prediction",
        "Offer one conceptual hint",
        "Pair on the actual problem",
        "Take over temporarily",
        "Work objective and status:",
        "Ledger retention status:",
    ):
        assert phrase in skill


def test_three_loop_authority_and_recursive_boundary() -> None:
    skill = read_skill()
    work = (ROOT / "docs/skill-drafts/mira-work/SKILL.md").read_text(encoding="utf-8")
    recursive = (ROOT / "docs/skill-drafts/recursive-learn/SKILL.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "`mira-work` owns the outer" in skill
    assert "Mira Work retains control of consequence" in work
    assert "Private mentorship\nrecords must never enter a candidate" in recursive
    assert "docs/skill-drafts/mira-mentor/SKILL.md" in agents
    assert "Finish or safely stop urgent learner work" in skill


def test_private_retention_and_non_portability() -> None:
    skill = read_skill()
    registry = (ROOT / "scripts/codex_skill_registry.py").read_text(encoding="utf-8")
    for phrase in (
        "MIRA_MENTORSHIP_DB",
        "absolute private path outside Git",
        "authority_effect: none",
        "Never retain raw conversations",
        "Generate a learner-facing summary only on request",
    ):
        assert phrase in skill
    assert '"mira-mentor"' not in registry

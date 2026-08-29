from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_rest_skill_contract_and_trigger() -> None:
    skill = (ROOT / "docs/skill-drafts/rest/SKILL.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    normalized = " ".join(skill.split())
    for phrase in (
        "Bare Rest authorizes only the private receipt",
        "Later operator activity resumes work normally",
        "supplies none of the five learning stages",
        "Rest performs no Continuity ingestion",
        "Do not produce a handoff, possibility menu, or invitation to continue",
        "Report each unresolved action-capable transition separately",
        "cannot describe the transition as complete",
    ):
        assert phrase in normalized
    assert "bare `rest`" in agents
    assert "planning, quotation, explanation, or conditional language" in agents


def test_rest_is_repository_local() -> None:
    registry = (ROOT / "scripts/codex_skill_registry.py").read_text(encoding="utf-8")
    assert '"rest"' not in registry

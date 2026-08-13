from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "docs" / "skill-drafts" / "research-brief" / "SKILL.md"
HANDOFF_TEMPLATE = SKILL_PATH.parent / "assets" / "research-execution-handoff-v1.json"
SEED_TEMPLATE = SKILL_PATH.parent / "assets" / "research-brief-seed-v1.json"
WORLD_MONITOR_SKILL = ROOT / "docs" / "skill-drafts" / "world-monitor" / "SKILL.md"


def skill_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def test_research_brief_is_repo_local_and_explicitly_routed() -> None:
    import sys

    scripts_root = ROOT / "scripts"
    if str(scripts_root) not in sys.path:
        sys.path.insert(0, str(scripts_root))

    import codex_skill_registry
    import validate_repository

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "research-brief" in validate_repository.LOCAL_SKILLS
    assert "research-brief" not in codex_skill_registry.DEPLOYABLE_SKILL_NAMES
    assert "docs/skill-drafts/research-brief/SKILL.md" in agents


def test_research_brief_has_bounded_routing_metadata() -> None:
    value = skill_text()

    assert "name: research-brief" in value
    for trigger in (
        "exact `research-brief` command",
        "research plans",
        "investigation designs",
        "source strategies",
        "evidence requirements",
    ):
        assert trigger in value
    for boundary in (
        "do not use to conduct research",
        "produce sourced findings or analytical reports",
        "run morning brief",
        "do not execute the research",
        "authorizes no browsing",
    ):
        assert boundary in value.lower()


def test_research_brief_route_disambiguates_planning_from_findings() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    value = skill_text()

    for text in (agents, value):
        normalized = " ".join(text.split())
        assert "unhyphenated phrase `research brief`" in normalized
        assert "Do you want an investigation plan or sourced findings?" in normalized
        assert "Do not browse while resolving that ambiguity." in normalized

    assert "says exact `research-brief`" in agents
    assert "run `morning-brief`" in agents


def test_research_brief_preserves_evidence_and_workflow_boundaries() -> None:
    value = skill_text()

    for required in (
        "Rival explanations",
        "Contradiction protocol",
        "independent lineage",
        "world-monitor",
        "morning-brief",
        "reality-check",
        "intake",
        "geo-strategy",
        "6e5545081c888b89576a620d9b2e54e9a6590f68",
    ):
        assert required in value


def test_research_brief_emits_a_non_authorizing_handoff() -> None:
    import json

    value = skill_text()
    template = json.loads(HANDOFF_TEMPLATE.read_text(encoding="utf-8"))

    assert template["schema"] == "research-execution-handoff-v1"
    assert template["authority"] == {
        "execute": False,
        "mutate": False,
        "publish": False,
        "communicate": False,
    }
    assert template["prerequisites"]["explicit_execution_request"] is False
    assert "research-handoff --packet" in value
    assert "transfers scope" in value
    assert "routing compatibility, never as execution authority" in value


def test_research_brief_uses_calibrated_adaptive_intake() -> None:
    value = skill_text()

    for required in (
        "named consequential decision",
        "one to three questions per round",
        "never re-asking an explicitly settled field",
        "Do not draft until consequential fields are confirmed",
        "state the exact mismatch and resume elicitation",
        "never normalize the scope",
    ):
        assert required in value


def test_research_brief_has_risk_tiered_evidence_and_bounded_completion() -> None:
    value = skill_text()
    normalized = " ".join(value.split())

    for posture in ("`standard`", "`elevated`", "`governed`"):
        assert posture in value
    assert "Require rival explanations for causal" in value
    assert "record `not applicable` with a reason" in normalized
    assert "both the evidence bar and a time, source-count, or" in normalized
    assert "evidence posture inside `research_contract.evidence_plan`" in normalized
    assert "effort ceiling inside `research_contract.stop_condition`" in normalized


def test_research_brief_is_layered_and_cold_handoff_ready() -> None:
    value = skill_text()

    assert "Return a cold-handoff brief" in value
    assert "concise **Commission** layer" in value
    assert "**Execution detail**" in value
    assert "Do not rely on the preceding conversation" in value
    assert "decision usefulness as the primary measure" in value


def test_seed_template_is_inline_context_without_execution_fields() -> None:
    import json

    template = json.loads(SEED_TEMPLATE.read_text(encoding="utf-8"))

    assert template["schema"] == "research-brief-seed-v1"
    assert template["authority"] == {
        "execute": False,
        "mutate": False,
        "publish": False,
        "communicate": False,
    }
    for forbidden in (
        "compatibility",
        "disposition",
        "research_contract",
        "explicit_execution_request",
    ):
        assert forbidden not in template


def test_world_monitor_emits_only_eligible_selected_seed_context() -> None:
    value = WORLD_MONITOR_SKILL.read_text(encoding="utf-8")
    normalized = " ".join(value.split())

    for required in (
        "research-brief-seed-v1",
        "Keep every authority flag false",
        "Do not include compatibility, disposition",
        "Expand the seed only after operator selection",
        "Do not seed ordinary scans",
        "unrecovered dashboard signals",
    ):
        assert required in normalized

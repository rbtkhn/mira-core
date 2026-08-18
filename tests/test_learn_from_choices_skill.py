from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "docs" / "skill-drafts" / "learn-from-choices"


def read(name: str) -> str:
    return (SKILL_ROOT / name).read_text(encoding="utf-8")


def fixtures() -> list[dict[str, object]]:
    return json.loads(read("references/decision-fixtures.json"))


def test_core_is_discoverable_and_routes_lifecycle_references() -> None:
    core = read("SKILL.md")
    metadata = read("agents/openai.yaml")
    frontmatter = core.split("---", 2)[1]
    assert "name: learn-from-choices" in frontmatter
    assert "Use implicitly for every final response" in frontmatter
    assert 'display_name: "Learn From Choices"' in metadata
    assert "references/choice-retention.md" in core
    assert "references/outcome-review.md" in core
    assert "After a user selects" in core
    assert "Before using retained outcomes" in core


def test_core_retains_nonnegotiable_authority_and_terminal_forms() -> None:
    core = read("SKILL.md")
    normalized = " ".join(core.split())
    for role in ("recommended", "alternative", "overlooked", "pause-or-deepen"):
        assert f"`{role}`" in core
    for verb in ("Execute", "Commit", "Push", "Send"):
        assert f"`{verb}`" in core
    for phrase in (
        "machine-checked `selection_effect`",
        "`Stage`, `Publish`, and `Deploy` always require a direct explicit command",
        "A turn has three valid terminal forms",
        "Working-tree presence is distinct",
        "Do not present consecutive navigation-only menus",
        "closure-debt audit",
    ):
        assert phrase in normalized


def test_deferred_material_is_not_duplicated_in_core() -> None:
    core = read("SKILL.md")
    retention = read("references/choice-retention.md")
    review = read("references/outcome-review.md")
    assert "choice select --options-json" not in core
    assert "choice select --options-json" in retention
    assert "projection version `2.0`" not in core
    assert "projection version `2.0`" in review
    assert "selection frequency" not in core
    assert "selection frequency" in review


def test_retention_uses_compatibility_aware_store_resolution() -> None:
    retention = read("references/choice-retention.md")
    normalized = " ".join(retention.split())
    assert "`MIRA_CORE_CHOICE_DB`" in retention
    assert "`NARRATIVE_CHOICE_DB` compatibility variable" in normalized
    assert "Do not inspect one environment variable" in normalized
    assert "only the compatibility-aware command result" in normalized


def test_agents_router_is_compact_and_preserves_core_boundaries() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    route = "docs/skill-drafts/learn-from-choices/SKILL.md"
    assert agents.count(route) == 1
    assert "choice-retention reference only after" in agents
    assert "outcome-review reference only when" in agents
    assert "machine-validated visible option" in agents
    assert "require direct commands for\nstaging, publication, and deployment" in agents


@pytest.mark.parametrize("case", fixtures(), ids=lambda item: str(item["id"]))
def test_decision_fixture_is_complete_and_authority_bounded(
    case: dict[str, object],
) -> None:
    assert case["case"] in {
        "settled",
        "new-paths",
        "bare-letter",
        "action-ready",
        "direct-command-only",
        "unavailable-retention",
        "saturation",
        "normal-delayed-observation",
        "unobservable-outcome",
        "conflicting-scope",
        "historical-backfill",
    }
    assert case["expected_terminal"]
    assert case["required_resource"] in {"core", "choice-retention", "outcome-review"}
    assert isinstance(case["allowed"], list) and case["allowed"]
    assert isinstance(case["forbidden"], list) and case["forbidden"]


def test_fixture_inventory_covers_required_runtime_decisions() -> None:
    cases = {str(item["case"]) for item in fixtures()}
    assert cases == {
        "settled",
        "new-paths",
        "bare-letter",
        "action-ready",
        "direct-command-only",
        "unavailable-retention",
        "saturation",
        "normal-delayed-observation",
        "unobservable-outcome",
        "conflicting-scope",
        "historical-backfill",
    }
    assert len(fixtures()) == 12


def test_outcome_fixtures_preserve_observation_and_scope_boundaries() -> None:
    indexed = {item["id"]: item for item in fixtures()}
    assert "infer success from closure" in indexed["LFC-OUTCOME-DUE-01"]["forbidden"]
    assert any(
        "choice ID alone" in behavior
        for behavior in indexed["LFC-COHORT-SCOPE-FAILURE-01"]["forbidden"]
    )
    assert "infer cohort membership" in indexed["LFC-HISTORICAL-BACKFILL-01"]["forbidden"]
    assert "treat candidate status as observation" in indexed["LFC-OUTCOME-DUE-01"]["forbidden"]
    assert "default missing outcome scope" in indexed["LFC-COHORT-SCOPE-FAILURE-01"]["forbidden"]
    assert "represent a legacy store as an empty cohort" in indexed["LFC-HISTORICAL-BACKFILL-01"]["forbidden"]


def test_unavailable_retention_fixture_forbids_single_variable_inference() -> None:
    case = next(
        item for item in fixtures() if item["id"] == "LFC-RETENTION-FAILURE-01"
    )
    assert any(
        "empty canonical variable" in behavior
        for behavior in case["forbidden"]
    )

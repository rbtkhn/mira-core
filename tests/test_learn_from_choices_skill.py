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
    assert "compact contextual A-D surface required on every final response" in frontmatter
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
        "A turn has four valid terminal forms",
        "Working-tree presence is distinct",
        "Do not present consecutive navigation-only menus",
        "closure-debt audit",
        "Keep Options Specific",
        "do not fall back to the generic `Close`, `Correct`, `Deepen`",
        "at least two options should preserve the actual operational shape",
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
        "compound-selection",
        "action-ready",
        "direct-command-only",
        "unavailable-retention",
        "saturation",
        "normal-delayed-observation",
        "unobservable-outcome",
        "conflicting-scope",
        "historical-backfill",
        "explicit-stop",
        "repeated-selection",
        "workflow-owned-menu",
        "action-ready-task-creation",
        "durable-batch-authority",
        "acknowledgement",
        "completed-factual-receipt",
        "material-unresolved-decision",
        "navigation-letter-cannot-mutate",
        "compressed-cadence",
        "soft-assent",
        "bounded-continuation",
        "ambiguous-continuation",
        "explicit-command",
        "stale-context",
        "settled-repeat",
        "freeform-recovery",
    }
    assert case["expected_terminal"]
    assert case["required_resource"] in {
        "core",
        "choice-retention",
        "outcome-review",
        "intent-recovery",
    }
    assert isinstance(case["allowed"], list) and case["allowed"]
    assert isinstance(case["forbidden"], list) and case["forbidden"]


def test_fixture_inventory_covers_required_runtime_decisions() -> None:
    cases = {str(item["case"]) for item in fixtures()}
    assert cases == {
        "settled",
        "new-paths",
        "bare-letter",
        "compound-selection",
        "action-ready",
        "direct-command-only",
        "unavailable-retention",
        "saturation",
        "normal-delayed-observation",
        "unobservable-outcome",
        "conflicting-scope",
        "historical-backfill",
        "explicit-stop",
        "repeated-selection",
        "workflow-owned-menu",
        "action-ready-task-creation",
        "durable-batch-authority",
        "acknowledgement",
        "completed-factual-receipt",
        "material-unresolved-decision",
        "navigation-letter-cannot-mutate",
        "compressed-cadence",
        "soft-assent",
        "bounded-continuation",
        "ambiguous-continuation",
        "explicit-command",
        "stale-context",
        "settled-repeat",
        "freeform-recovery",
    }
    assert len(fixtures()) == 30


def test_settled_terminal_fixtures_require_compact_contextual_closure() -> None:
    indexed = {item["id"]: item for item in fixtures()}
    for fixture_id in (
        "LFC-SETTLED-01",
        "LFC-SATURATION-01",
        "LFC-STOP-01",
        "LFC-REPEATED-SELECTION-01",
    ):
        fixture = indexed[fixture_id]
        assert "compact" in str(fixture["expected_terminal"])
        assert "a-d-surface" in str(fixture["expected_terminal"])
        combined = " ".join(fixture["allowed"] + fixture["forbidden"])
        assert "transient" in combined.casefold() or "no-op" in combined.casefold()
    assert "append a second generic A-D menu" in indexed[
        "LFC-WORKFLOW-MENU-01"
    ]["forbidden"]


def test_core_requires_every_response_surface_and_transient_control_isolation() -> None:
    core = read("SKILL.md")
    retention = read("references/choice-retention.md")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for contract in (core, agents):
        assert "compact" in contract
        assert "learning_eligibility" in contract
        assert "final_response: true" in contract
    assert "substantive terminal A-D" in core
    assert "terminal surface is rendered" in core
    assert "menu-contract-decision-v1" in retention
    assert "menu-contract-natural-use-v1" in retention
    assert "no `choice select`" in " ".join(retention.split())


def test_core_requires_silent_digest_bound_context_without_retention() -> None:
    core = read("SKILL.md")
    for phrase in (
        "silent interaction-context capsule",
        "current digest-bound capsule",
        "Retire the capsule",
        "do not save it to the choice ledger",
        "display it routinely",
    ):
        assert phrase in core


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


def test_menu_contract_review_is_prospective_and_not_recursive_proof() -> None:
    review = read("references/outcome-review.md")
    normalized = " ".join(review.split())
    assert "menu-contract-natural-use-v1" in review
    assert "first five later natural uses" in normalized
    assert "zero retained transient controls" in normalized
    assert "zero compressed- selection authority incidents" in normalized
    assert "passing tests" in normalized
    assert "do not close a feedback loop" in normalized
    assert "ledger admission remain separate governed actions" in normalized


def test_unavailable_retention_fixture_forbids_single_variable_inference() -> None:
    case = next(
        item for item in fixtures() if item["id"] == "LFC-RETENTION-FAILURE-01"
    )
    assert any(
        "empty canonical variable" in behavior
        for behavior in case["forbidden"]
    )

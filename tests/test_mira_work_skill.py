import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "docs" / "skill-drafts" / "mira-work"


def read_skill() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def read_reference(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


def fixtures() -> list[dict[str, object]]:
    return json.loads(read_reference("validation-fixtures.json"))


def test_skill_has_local_structure_and_contextual_metadata() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert skill.startswith("---\nname: mira-work\n")
    assert skill.count("\n---\n") == 1
    assert 'display_name: "Mira Work"' in metadata
    assert "Conduct bounded consequential work" in metadata
    for phrase in (
        "multiple dependent steps",
        "wrong objective, order, authority boundary, validation scope, or repository",
        "factual answers, ordinary conversation, simple one-step edits",
    ):
        assert phrase in normalized
    assert "multiple dependent steps" in metadata
    assert "across a bounded multi-step task" not in metadata


def test_consequence_trigger_includes_single_domain_work_and_excludes_low_cost_work() -> None:
    skill = " ".join(read_skill().split())
    assert "Consequential work inside one domain remains eligible" in skill
    assert "low-consequence mechanical work" in skill
    assert "multi-step work across domains" not in skill


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
    normalized = " ".join(read_skill().split())
    for phrase in (
        "saved and verified",
        "not saved",
        "intentionally conversational",
        "Working-tree presence is distinct",
        "Mira Work completion:",
        "Outcome evidence or correction: none",
        "completion alone is not proof of success",
        "creates no database, ledger, automatic retention",
        "Mira Voice governs tone",
        "`learn-from-choices` governs final navigation",
        "must not silently create durable memory",
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


def test_validation_route_is_deferred_until_action_or_costly_verification() -> None:
    skill = " ".join(read_skill().split())
    profile = read_reference("execution-profile.md")
    normalized = " ".join(profile.split())
    assert "references/execution-profile.md" in skill
    assert "action-capable or requires costly verification" in skill
    assert "tools/run.ps1 test --mode fast --explain-route" in profile
    assert "If the route reports Full because of unrelated state" in normalized
    assert "use explicit focused test paths" in normalized
    assert "preview is read-only" in normalized


def test_execution_mechanics_live_in_deferred_profile() -> None:
    skill = read_skill()
    profile = read_reference("execution-profile.md")
    normalized = " ".join(profile.split())
    for phrase in (
        "internal execution envelope",
        "objective and mutation boundary",
        "canonical runtime and an absolute external temporary root",
        "cheapest sufficient validation profile",
        "controlling terminal session identifier",
        "applicable admitted recursive-learning lesson or explicit `none`",
        "publication lane",
        "pure functions",
        "fixture-based checks",
        "one live forward check",
        "repository-wide validation only when",
        "tools/run.ps1 runtime-bootstrap --print-python",
        "Route staging, commit, push, branch, PR, and main synchronization through Mira GitHub",
    ):
        assert phrase in normalized
    assert "internal execution envelope" not in skill
    assert "tools/run.ps1 test --mode fast --explain-route" not in skill
    assert "cheapest sufficient validation" in skill
    assert "`mira-github` governs staging, commit, push, branch, PR, and main-sync lanes" in skill


def test_completion_receipt_is_observable_but_not_retained_automatically() -> None:
    skill = read_skill()
    for field in (
        "Objective:",
        "Organizational consequence:",
        "Compression class: toil | technique | judgment | apprenticeship | not-applicable",
        "Authorized boundary:",
        "Validation profile and result:",
        "Reached boundary:",
        "Outcome evidence or correction: none | <bounded evidence>",
        "Unresolved dependency: none | <dependency>",
        "Re-entry point: none | <exact point>",
        "Persistence:",
    ):
        assert field in skill
    assert "receipt remains conversational" in skill
    assert "existing governing workflow already saves it" in skill


def test_behavioral_fixture_inventory_is_complete_and_human_reviewed() -> None:
    cases = fixtures()
    assert [case["id"] for case in cases] == [
        "MW-NORMAL-01",
        "MW-EDGE-01",
        "MW-FAILURE-01",
        "MW-AMBIGUOUS-01",
    ]
    assert {case["case"] for case in cases} == {"normal", "edge", "failure", "ambiguous"}
    skill = " ".join(read_skill().split())
    assert "human-reviewed behavioral benchmarks" in skill
    assert "not machine-scored" in skill


def test_behavioral_fixtures_have_bounded_observable_fields() -> None:
    expected_keys = {
        "id", "case", "prompt", "context", "expected_activation",
        "required_resources", "required_behaviors", "forbidden_behaviors",
        "expected_receipt_fields", "pass",
    }
    for case in fixtures():
        assert set(case) == expected_keys
        assert isinstance(case["expected_activation"], bool)
        assert isinstance(case["required_resources"], list) and case["required_resources"]
        assert isinstance(case["required_behaviors"], list) and case["required_behaviors"]
        assert isinstance(case["forbidden_behaviors"], list) and case["forbidden_behaviors"]
        assert isinstance(case["expected_receipt_fields"], list)
        assert case["pass"]


def test_failure_and_ambiguous_fixtures_fail_closed() -> None:
    by_id = {case["id"]: case for case in fixtures()}
    failure = by_id["MW-FAILURE-01"]
    ambiguous = by_id["MW-AMBIGUOUS-01"]
    assert failure["expected_activation"] is True
    assert any("broad command" in item for item in failure["forbidden_behaviors"])
    assert ambiguous["expected_activation"] is False
    assert ambiguous["expected_receipt_fields"] == []
    assert any("generic wording" in item for item in ambiguous["forbidden_behaviors"])

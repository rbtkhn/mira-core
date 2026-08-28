from __future__ import annotations

import re
from pathlib import Path

from scripts import codex_skill_registry


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "docs" / "skill-drafts" / "repo-audit" / "SKILL.md"
REFERENCES = CANONICAL.parent / "references"


def test_agents_routes_mira_core_repo_audit_through_canonical_contract() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "When `repo-audit` targets Mira Core" in agents
    assert "docs/skill-drafts/repo-audit/SKILL.md" in agents
    assert "deployable mirror, not a second authority" in agents
    assert "archive-audit" in agents
    assert "do not" in agents.lower()
    assert "repair authority" in agents


def test_repo_audit_is_registered_as_portable() -> None:
    entry = codex_skill_registry.build_registry()["repo-audit"]

    assert entry.source == CANONICAL
    assert entry.dest.name == "SKILL.md"


def test_only_canonical_source_claims_repo_audit_name() -> None:
    skill_roots = (ROOT / "docs" / "skill-drafts", ROOT / ".codex" / "skills")
    canonical_claims: list[str] = []

    for skill_root in skill_roots:
        for path in skill_root.glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            match = re.search(r"(?m)^name:\s*[\"']?([^\"'\r\n]+)", text)
            if match and match.group(1).strip() == "repo-audit":
                canonical_claims.append(path.relative_to(ROOT).as_posix())

    assert canonical_claims == ["docs/skill-drafts/repo-audit/SKILL.md"]


def test_repo_audit_bounds_authorship_lineage_and_truncated_diagnostics() -> None:
    skill = CANONICAL.read_text(encoding="utf-8")
    assert "## Bound authorship and lineage inference" in skill
    assert "outside the formal repository finding set" in skill
    assert "private psychology, demographics, motives" in skill
    assert "Treat repository genealogy as branching" in skill
    assert "when history is shallow, rewritten, imported, mirrored" in skill
    assert "If command output truncates" in skill
    assert "rerun against the smallest named surfaces" in skill


def test_repo_audit_reconciles_prior_findings_before_prioritizing_repairs() -> None:
    skill = CANONICAL.read_text(encoding="utf-8")

    assert "## Reconcile prior and external audits" in skill
    assert "rejected-by-operator" in skill
    assert "Never describe an unstaged" in skill
    assert "## Triage repair opportunities when requested" in skill
    for field in ("expected benefit", "effort band", "needs-decision", "authority required"):
        assert field in skill.lower()


def test_repo_audit_loads_routing_and_preserves_external_report_provenance() -> None:
    skill = CANONICAL.read_text(encoding="utf-8")
    routing = (REFERENCES / "audit-routing.md").read_text(encoding="utf-8")

    assert "references/audit-routing.md" in skill
    assert "references/validation-fixtures.md" in skill
    assert "Prior and third-party audit intake" in routing
    assert "grok-research" in routing
    for disposition in (
        "open",
        "resolved",
        "superseded",
        "rejected-by-operator",
        "not-reproduced",
        "unavailable",
    ):
        assert f"`{disposition}`" in routing


def test_finding_schema_separates_lifecycle_severity_and_repair_economics() -> None:
    schema = (REFERENCES / "finding-schema.md").read_text(encoding="utf-8")

    assert "lifecycle:" in schema
    assert "checked_state:" in schema
    assert "disposition:" in schema
    assert "repair_assessment:" in schema
    assert "effort_band:" in schema
    assert "readiness: ready | needs-decision | needs-evidence | not-safe" in schema
    assert "Repair effort and expected benefit never" in schema


def test_repo_audit_validation_fixtures_cover_four_behavior_classes() -> None:
    fixtures = (REFERENCES / "validation-fixtures.md").read_text(encoding="utf-8")

    assert fixtures.count("## Case:") == 4
    for case_type in ("normal", "edge", "failure", "ambiguous"):
        assert f"## Case: {case_type}" in fixtures
    for required_field in (
        "**Prompt:**",
        "**Resources to load:**",
        "**Expected behavior:**",
        "**Forbidden behavior:**",
        "**Pass/fail check:**",
        "**Residual risk:**",
    ):
        assert fixtures.count(required_field) == 4

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_agent_contract_bounds_output_and_resumes_live_sessions() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "more than 200 entries" in agents
    assert "resume or" in agents and "poll that exact process" in agents
    assert "Never relaunch the" in agents and "same long-running command" in agents
    assert "session-preflight" in agents
    assert "Cache an optional service's unavailable state" in agents
    assert "internal execution envelope" in agents
    assert "known-failing probe" in agents
    assert "mutation, parity verification, and receipt" in agents


def test_agent_contract_requires_one_uncached_full_and_fingerprint_reuse() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "exactly one uncached Full gate" in agents
    assert "identical-fingerprint cache hit" in agents
    assert "Never rerun merely because commit metadata" in agents
    for changed_input in (
        "repository bytes",
        "runtime or declared dependencies",
        "relevant environment",
        "result clarity",
    ):
        assert changed_input in agents


def test_mira_work_reuses_execution_envelope_and_canonical_runtime() -> None:
    skill = (REPO_ROOT / "docs" / "skill-drafts" / "mira-work" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(skill.split())

    for phrase in (
        "internal execution envelope",
        "established repository ownership or permission context",
        "pure functions, fixture-based checks, focused suite",
        "tools/run.ps1 runtime-bootstrap --print-python",
        "bulk mutation, parity verification, and receipt creation",
    ):
        assert phrase in normalized


def test_repo_audit_distinguishes_coverage_from_duplicate_execution() -> None:
    skill = (REPO_ROOT / "docs" / "skill-drafts" / "repo-audit" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(skill.split())

    for phrase in (
        "Declare a validation budget",
        "one check per materially distinct claim",
        "Prohibit duplicate gates",
        "matching successful Full fingerprint",
        "cannot replace hosted-state verification",
    ):
        assert phrase in normalized


def test_skill_audit_reuses_canonical_runtime_for_external_validators() -> None:
    skill = (REPO_ROOT / "docs" / "skill-drafts" / "skill-audit" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(skill.split())

    assert "tools/run.ps1 runtime-bootstrap --print-python" in normalized
    assert "do not probe multiple Python installations" in normalized


def test_coffee_contract_prevents_duplicate_verification() -> None:
    coffee = (
        REPO_ROOT / "docs" / "skill-drafts" / "coffee" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "Start it once" in coffee
    assert "rather than launching a duplicate cadence command" in coffee
    assert "capped top-level groupings" in coffee
    assert "session-preflight --temp-root ABSOLUTE_PATH --json" in coffee
    assert "each verifier once" in coffee


def test_choice_contract_caches_unchanged_store_failure() -> None:
    choices = (
        REPO_ROOT
        / "docs"
        / "skill-drafts"
        / "learn-from-choices"
        / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "cached as" in choices and "unavailable for the current task" in choices
    assert "Do not reopen the same" in choices and "unavailable store" in choices
    assert "Retry only after the configured path" in choices

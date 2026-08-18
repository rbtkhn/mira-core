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
    retention = (
        REPO_ROOT
        / "docs"
        / "skill-drafts"
        / "learn-from-choices"
        / "references"
        / "choice-retention.md"
    ).read_text(encoding="utf-8")

    assert "cached as unavailable" in retention
    assert "Cache unavailability" in retention
    assert "Retry only after that state changes" in retention


def test_universal_menu_contract_avoids_duplicate_or_retained_controls() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    choices = (
        REPO_ROOT
        / "docs"
        / "skill-drafts"
        / "learn-from-choices"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "exactly one four-option A-D surface" in agents
    assert "without duplication" in agents
    assert "never append a duplicate menu" in choices
    assert "learning_eligibility: none" in agents
    assert "final_response: true" in agents

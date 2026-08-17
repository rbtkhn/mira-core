from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "docs" / "skill-drafts" / "mira-github"
SKILL = SKILL_ROOT / "SKILL.md"


def read_skill() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_skill_requires_bounded_status_before_path_output() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(skill.split())
    assert "report the total and top-level groups first" in normalized
    assert "at most 200" in normalized
    assert "git status --porcelain=v1 --untracked-files=all" in skill
    assert "Use `git status -sb` only after" in skill


def test_skill_dry_checks_broad_staging_and_protects_untracked_work() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(skill.split())
    for phrase in (
        "Before `git add -A`",
        "hydrated corpus roots",
        "Fail closed if a protected root",
        "any untracked path remains unclassified",
        "use exact paths or `git add -u`",
        "name the exclusion",
    ):
        assert phrase in normalized


def test_push_preflight_checks_divergence_auth_and_exact_refspec() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    for phrase in (
        "git log --oneline --left-right --decorate origin/main...HEAD -20",
        "gh auth status",
        "Confirm the target branch and refspec",
        "main-sync-plan",
    ):
        assert phrase in normalized


def test_fixture_inventory_covers_normal_edge_failure_and_ambiguous_cases() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    expected = (
        "MGH-NORMAL-01",
        "MGH-EDGE-01",
        "MGH-FAILURE-01",
        "MGH-FAILURE-02",
        "MGH-AMBIGUOUS-01",
    )
    for fixture_id in expected:
        assert fixtures.count(f"## {fixture_id} ") == 1
    assert fixtures.count("- Expected:") == len(expected)
    assert fixtures.count("- Forbidden:") == len(expected)
    assert fixtures.count("- Pass:") == len(expected)


def test_publication_and_lock_fixtures_fail_closed() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    assert "force-push, implicit rebase, broadened refspec" in fixtures
    assert "verify that no Git or Git LFS process owns the lock" in fixtures
    assert "an active lock is preserved" in fixtures
    assert "the index remains unchanged until an explicit staging command" in fixtures


def test_direct_push_never_expands_into_history_or_scope_mutation() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    assert "A direct `push` authorizes only the bounded push currently proven safe" in normalized
    for forbidden_authority in ("rebasing", "force-pushing", "broad staging", "PR creation"):
        assert forbidden_authority in normalized
    assert "Never force-push, rebase, broaden the refspec, open a PR" in normalized


def test_blocked_push_stops_with_resumption_packet_and_no_blind_retry() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    assert "Handle blockers with a resumption packet" in skill
    for field in (
        "Target commit:",
        "Intended branch/refspec:",
        "Upstream divergence:",
        "Exact safe next step after repair:",
    ):
        assert field in skill
    assert "Do not retry blind pushes" in normalized
    assert "produce a resumption packet for every blocked push" in normalized

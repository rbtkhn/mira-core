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
        "git fetch --no-tags origin main",
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
        "MGH-NORMAL-02",
        "MGH-EDGE-01",
        "MGH-EDGE-02",
        "MGH-EDGE-03",
        "MGH-FAILURE-01",
        "MGH-FAILURE-02",
        "MGH-AMBIGUOUS-01",
        "MGH-NORMAL-03",
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
    assert "no Git/Git LFS process is present" in fixtures
    assert "FileShare.None" in fixtures
    assert "an active lock is preserved" in fixtures
    assert "the index remains unchanged until an explicit staging command" in fixtures


def test_direct_push_never_expands_into_history_or_scope_mutation() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    assert "A direct `push` authorizes only the bounded push currently proven safe" in normalized
    for forbidden_authority in ("rebasing", "force-pushing", "broad staging", "PR creation"):
        assert forbidden_authority in normalized
    assert "Never force-push, rebase, broaden the refspec, open a PR" in normalized


def test_safe_branch_route_never_replaces_requested_main_endpoint() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    for phrase in (
        "requested publication endpoint",
        "must never silently replace the endpoint itself",
        "treat a branch push as an intermediate state only",
        "ask one minimal target question before publishing",
        "requested main landing still pending",
    ):
        assert phrase in normalized

    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    assert "## MGH-EDGE-02" in fixtures
    assert "silently substitute a feature-branch endpoint" in fixtures
    assert "requested main landing still pending" in fixtures


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


def test_skill_uses_non_printing_token_check_and_deterministic_publication_tools() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    assert "gh auth token --hostname github.com *> $null" in skill
    assert "only its exit code may be inspected" in normalized
    assert "Never capture, interpolate, or print token content" in normalized
    assert "tools/run.ps1 publication-validation" in skill
    assert "tools/run.ps1 validated-push check" in skill
    assert "tools/run.ps1 validated-push push" in skill


def test_skill_main_workflow_requires_exact_stale_lock_proof() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    for phrase in (
        "git rev-parse --path-format=absolute --git-dir",
        "Get-CimInstance Win32_Process",
        "wait two seconds",
        "FileShare::None",
        "Remove-Item -LiteralPath",
        "remove only that literal file",
    ):
        assert phrase in normalized


def test_primary_main_is_an_integration_reference_not_a_dirty_work_branch() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    for phrase in (
        "Treat the primary checkout's `main` as an integration reference",
        "Do not begin new implementation commits directly on a dirty or diverged primary `main`",
        "isolated worktree created from a freshly fetched `origin/main`",
        "Commit-message similarity alone does not prove equivalence",
        "Never replay every commit in a diverged range",
    ):
        assert phrase in normalized


def test_remote_publication_and_local_reconciliation_close_separately() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    for phrase in (
        "remote publication and local-main reconciliation as separate completion conditions",
        "origin/main updated; primary main remains diverged",
        "git merge --ff-only origin/main",
        "Repointing or resetting `main` requires explicit authority",
        "If the primary checkout is dirty, preserve it unchanged",
        "Never push a stale receipt",
        "Temporary-worktree cleanup does not satisfy primary reconciliation",
    ):
        assert phrase.lower() in normalized.lower()


def test_rebased_equivalent_publication_retains_sha_lineage() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    assert "record both the local source SHA and the published SHA" in normalized
    assert "does not by itself align the primary local branch" in normalized
    assert "origin/main updated, primary main reconciliation open" in skill
    assert "origin/main and primary main synchronized" in skill

    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    assert "## MGH-EDGE-03" in fixtures
    assert "## MGH-NORMAL-03" in fixtures
    assert "reporting full synchronization" in fixtures

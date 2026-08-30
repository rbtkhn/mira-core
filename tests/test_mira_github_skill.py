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
        "MGH-NORMAL-03",
        "MGH-NORMAL-05",
        "MGH-EDGE-01",
        "MGH-EDGE-02",
        "MGH-FAILURE-01",
        "MGH-EDGE-05",
        "MGH-FAILURE-03",
        "MGH-FAILURE-05",
        "MGH-EDGE-03",
        "MGH-FAILURE-02",
        "MGH-AMBIGUOUS-01",
        "MGH-FAILURE-04",
        "MGH-EDGE-04",
        "MGH-NORMAL-04",
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


def test_snapshot_and_landed_state_closure_contract() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(skill.split())
    for phrase in (
        "tools/run.ps1 mira-work snapshot",
        "Re-snapshot immediately after every Git mutation",
        "pre-action and post-action snapshot digests",
        "exact local commit",
        "exact remote commit",
        "excluded dirty paths",
        "remaining divergence",
        "working-tree state, committed state, remote state, and hosted state distinct",
        "must not silently open a second repair or architecture transition",
    ):
        assert phrase in normalized


def test_operational_maturation_fixtures_cover_stale_competing_and_exact_closure() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(encoding="utf-8")
    for fixture_id in ("MGH-FAILURE-04", "MGH-EDGE-04", "MGH-NORMAL-04"):
        assert fixtures.count(f"## {fixture_id} ") == 1
    assert "publishing from the stale snapshot" in fixtures
    assert "silently beginning the architectural repair" in fixtures
    assert "local and remote SHA equality is proved" in fixtures


def test_skill_uses_non_printing_token_check_and_deterministic_publication_tools() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    assert "gh auth token --hostname github.com *> $null" in skill
    assert "only its exit code may be inspected" in normalized
    assert "Never capture, interpolate, or print token content" in normalized
    assert "tools/run.ps1 publication-validation" in skill
    assert "tools/run.ps1 validated-push check" in skill
    assert "tools/run.ps1 validated-push push" in skill


def test_skill_documents_windows_sandbox_credential_boundary() -> None:
    skill = read_skill()
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(skill.split())
    normalized_fixtures = " ".join(fixtures.split())
    assert "CodexSandboxOnline" in skill
    assert "SEC_E_NO_CREDENTIALS" in skill
    assert "cmdkey /list" in skill
    assert "sandbox credential-boundary issue" in normalized
    assert "`hosts.yml` account metadata" in normalized
    assert "MGH-FAILURE-05" in fixtures
    assert "Windows sandbox identity cannot read user keyring" in fixtures
    assert "treating `hosts.yml` account metadata as" in normalized_fixtures


def test_skill_documents_windows_long_paths_and_temp_root_push_receipts() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    assert "git -c core.longpaths=true worktree add" in skill
    assert "--temp-root" in skill
    assert "tools/run.ps1 validated-push push" in skill
    assert "--receipt <absolute-receipt-path>" in skill
    assert "git ls-remote" in skill
    assert "FETCH_HEAD" in skill
    assert "final remote SHA proof" in normalized


def test_skill_records_full_gate_exceptions_without_generic_passes() -> None:
    skill = read_skill()
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(skill.split())
    normalized_fixtures = " ".join(fixtures.split())
    for field in (
        "--validation-profile",
        "--validation-result",
        "--required-gate",
        "--required-gate-result",
        "--exception-authorized",
        "--exception-basis",
        "--failure-fingerprint",
        "--authority-context-digest",
    ):
        assert field in skill
    assert "Never encode this state as a generic pass" in normalized
    assert "MGH-EDGE-05" in fixtures
    assert "focused pass and Full failure separately" in normalized_fixtures


def test_skill_defines_quiet_routine_readiness_scan() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    for field in ("Dirty:", "Staged:", "Ahead:", "Behind:", "Remote:", "Boundary:"):
        assert field in skill
    assert "tools/run.ps1 publication-status --json" in skill
    assert "advisory only" in normalized
    assert "Surface detailed commentary only when" in normalized
    assert "do not rely on session summaries alone" in normalized


def test_skill_exposes_remote_blockers_early_without_blocking_local_work() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())

    for phrase in (
        "At the first explicit `commit`, `push`, `PR`, or end-to-end publication request",
        "before substantial publication work or completion language",
        "finish it within roughly one minute",
        "a remote readiness failure does not block the commit",
        "fail the remote step early",
        "Do not run this gate for ordinary implementation",
        "Cache a stable unavailable state for the current task",
    ):
        assert phrase in normalized

    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    assert "## MGH-NORMAL-03" in fixtures
    assert "continue the separately authorized local commit" in " ".join(
        fixtures.split()
    )
    assert "without attempting login or push" in " ".join(fixtures.split())


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


def test_commit_reuses_matching_full_fingerprint() -> None:
    skill = " ".join(read_skill().split())
    for phrase in (
        "exactly one uncached Full gate",
        "same fingerprint with a cache hit",
        "evidence as reused rather than newly executed",
        "without repeating Full validation",
    ):
        assert phrase in skill
    for changed_input in (
        "repository bytes",
        "runtime or dependency inputs",
        "relevant environment",
        "result clarity",
    ):
        assert changed_input in skill


def test_hosted_state_is_distinct_and_uses_one_compact_watcher() -> None:
    skill = " ".join(read_skill().split())
    assert "hosted workflow state remains a separate claim" in skill
    assert "gh run watch <run-id> --repo OWNER/REPO --compact --exit-status --interval 15" in skill
    assert "Do not start parallel watchers" in skill
    assert "one structured `gh run view` query" in skill
    assert "exactly four jobs must pass" in skill


def test_powershell_refspec_examples_are_exact_and_unambiguous() -> None:
    skill = read_skill()
    assert "HEAD:refs/heads/<branch>" in skill
    assert "${sha}:refs/heads/<branch>" in skill
    assert "never write `$sha:refs/...`" in skill
    assert "Verify the resulting remote SHA" in skill

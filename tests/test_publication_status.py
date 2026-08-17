from __future__ import annotations

from pathlib import Path
import os
import stat
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import publication_status as subject  # noqa: E402


@pytest.fixture(autouse=True)
def restore_git_object_writability(tmp_path: Path):
    yield
    for path in sorted(tmp_path.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        try:
            os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
        except OSError:
            pass


def git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def commit(repo: Path, filename: str, text: str) -> str:
    target = repo / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    git(repo, "add", filename)
    git(repo, "commit", "-m", text.strip())
    return git(repo, "rev-parse", "HEAD")


def repositories(root: Path) -> tuple[Path, Path]:
    remote = root / "remote.git"
    work = root / "work"
    remote.mkdir()
    work.mkdir()
    git(remote, "init", "--bare")
    git(work, "init")
    git(work, "checkout", "-b", "main")
    git(work, "config", "user.name", "Mira Tests")
    git(work, "config", "user.email", "mira-tests@example.invalid")
    git(work, "remote", "add", "origin", str(remote))
    first = commit(work, "README.md", "first\n")
    git(work, "push", "-u", "origin", f"{first}:refs/heads/main")
    git(work, "branch", "--set-upstream-to=origin/main", "main")
    git(remote, "symbolic-ref", "HEAD", "refs/heads/main")
    return work, remote


def test_clean_and_synchronized(tmp_path: Path) -> None:
    work, _ = repositories(tmp_path)
    report = subject.build_report(work)
    assert report["dirty_count"] == 0
    assert report["staged_count"] == 0
    assert report["ahead"] == 0
    assert report["behind"] == 0
    assert report["upstream_sha"] == report["local_head"]
    assert report["recommended_boundary"] == "inspected only: clean and synchronized"


def test_dirty_only_reports_groups(tmp_path: Path) -> None:
    work, _ = repositories(tmp_path)
    (work / "docs").mkdir()
    (work / "docs/example.md").write_text("dirty\n", encoding="utf-8")
    report = subject.build_report(work)
    assert report["dirty_count"] == 1
    assert report["dirty_groups"] == [{"root": "docs", "count": 1}]
    assert report["staged_count"] == 0
    assert report["ahead"] == 0
    assert report["behind"] == 0
    assert report["recommended_boundary"] == "commit-plan: dirty worktree"


def test_unstaged_tracked_modification_is_not_counted_as_staged(tmp_path: Path) -> None:
    work, _ = repositories(tmp_path)
    (work / "README.md").write_text("changed\n", encoding="utf-8")
    report = subject.build_report(work)
    assert report["dirty_count"] == 1
    assert report["dirty_groups"] == [{"root": "README.md", "count": 1}]
    assert report["staged_count"] == 0
    assert report["recommended_boundary"] == "commit-plan: dirty worktree"


def test_ahead_only_is_push_ready(tmp_path: Path) -> None:
    work, _ = repositories(tmp_path)
    commit(work, "local.md", "local\n")
    report = subject.build_report(work)
    assert report["dirty_count"] == 0
    assert report["ahead"] == 1
    assert report["behind"] == 0
    assert report["recommended_boundary"] == "push-ready: committed local work"


def test_behind_only_is_sync_plan(tmp_path: Path) -> None:
    work, remote = repositories(tmp_path)
    other = tmp_path / "other"
    git(tmp_path, "clone", str(remote), str(other))
    git(other, "config", "user.name", "Mira Tests")
    git(other, "config", "user.email", "mira-tests@example.invalid")
    second = commit(other, "remote.md", "remote\n")
    git(other, "push", "origin", f"{second}:refs/heads/main")
    git(work, "fetch", "origin", "main")
    report = subject.build_report(work)
    assert report["ahead"] == 0
    assert report["behind"] == 1
    assert report["recommended_boundary"] == "main-sync-plan: behind remote"


def test_dirty_plus_ahead_prefers_push_boundary_with_dirty_context(tmp_path: Path) -> None:
    work, _ = repositories(tmp_path)
    commit(work, "local.md", "local\n")
    (work / "scratch.md").write_text("dirty\n", encoding="utf-8")
    report = subject.build_report(work)
    assert report["dirty_count"] == 1
    assert report["ahead"] == 1
    assert report["behind"] == 0
    assert report["recommended_boundary"] == "push-ready: committed local work"


def test_remote_unavailable_when_upstream_missing(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    git(work, "init")
    git(work, "checkout", "-b", "main")
    git(work, "config", "user.name", "Mira Tests")
    git(work, "config", "user.email", "mira-tests@example.invalid")
    commit(work, "README.md", "first\n")
    report = subject.build_report(work)
    assert report["upstream"] is None
    assert report["upstream_sha"] is None
    assert report["ahead"] is None
    assert report["behind"] is None
    assert report["recommended_boundary"] == "inspect-only: upstream unavailable"

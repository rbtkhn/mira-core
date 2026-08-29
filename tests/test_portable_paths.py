from __future__ import annotations

from pathlib import Path

import pytest

from portable_paths import (
    PortablePathError,
    git_checkout_root,
    require_private_path,
    resolve_state_root,
)


def git_checkout(path: Path) -> Path:
    path.mkdir(parents=True)
    (path / ".git").mkdir()
    return path


def test_private_path_rejects_current_repository(tmp_path: Path) -> None:
    repo = git_checkout(tmp_path / "repo")
    with pytest.raises(PortablePathError, match="outside the repository"):
        require_private_path(repo / "state/store.sqlite3", label="test", repo_root=repo)


def test_private_path_rejects_another_git_checkout(tmp_path: Path) -> None:
    repo = git_checkout(tmp_path / "repo")
    other = git_checkout(tmp_path / "other")
    with pytest.raises(PortablePathError, match="outside every Git checkout"):
        require_private_path(other / "state/store.sqlite3", label="test", repo_root=repo)
    with pytest.raises(PortablePathError, match="outside every Git checkout"):
        resolve_state_root(other / "state", repo_root=repo)


def test_git_worktree_marker_file_is_detected(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    (worktree / ".git").write_text("gitdir: ../admin", encoding="utf-8")
    assert git_checkout_root(worktree / "private/store.sqlite3") == worktree


def test_explicit_legacy_source_exception_is_narrow(tmp_path: Path) -> None:
    repo = git_checkout(tmp_path / "repo")
    legacy = git_checkout(tmp_path / "legacy")
    target = legacy / "old-store.sqlite3"
    assert require_private_path(
        target, label="legacy source", repo_root=repo, allow_git_checkout=True
    ) == target.resolve()
    external = tmp_path / "state" / "store.sqlite3"
    assert require_private_path(external, label="test", repo_root=repo) == external.resolve()


def test_relative_private_path_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(PortablePathError, match="absolute"):
        require_private_path(Path("relative/store.sqlite3"), label="test", repo_root=tmp_path)

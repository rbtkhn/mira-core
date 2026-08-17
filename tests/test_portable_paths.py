from __future__ import annotations

import os
from pathlib import Path

import pytest

from portable_paths import PortablePathError, require_private_path


def test_designated_private_root_accepts_canonical_and_rejects_traversal(tmp_path: Path) -> None:
    repo=tmp_path/"Mira Core"; private=repo/".mira-private"; private.mkdir(parents=True)
    target=private/"sessions/rest"
    assert require_private_path(target,label="test",repo_root=repo) == target.resolve()
    with pytest.raises(PortablePathError):
        require_private_path(private/".."/"tracked/rest",label="test",repo_root=repo)


@pytest.mark.skipif(os.name != "nt",reason="Windows case-boundary behavior")
def test_designated_private_root_is_case_insensitive_on_windows(tmp_path: Path) -> None:
    repo=tmp_path/"MiraCore"; target=repo/".MIRA-PRIVATE"/"sessions/rest"
    target.mkdir(parents=True)
    assert require_private_path(target,label="test",repo_root=repo,private_root=repo/".mira-private") == target.resolve()


def test_symlinked_private_root_cannot_escape_repository(tmp_path: Path) -> None:
    repo=tmp_path/"repo"; repo.mkdir(); outside=tmp_path/"outside"; outside.mkdir()
    link=repo/".mira-private"
    try: link.symlink_to(outside,target_is_directory=True)
    except OSError: pytest.skip("directory symlinks unavailable")
    with pytest.raises(PortablePathError,match="escapes"):
        require_private_path(link/"sessions/rest",label="test",repo_root=repo)

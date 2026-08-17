from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess

import pytest

import validated_push as subject


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


def commit(repo: Path, text: str) -> str:
    target = repo / "artifact.md"
    target.write_text(text, encoding="utf-8")
    git(repo, "add", "artifact.md")
    git(repo, "commit", "-m", text.strip())
    return git(repo, "rev-parse", "HEAD")


def repositories(root: Path) -> tuple[Path, Path]:
    remote = root / "remote.git"
    work = root / "work"
    remote.mkdir()
    work.mkdir()
    git(remote, "init", "--bare")
    git(work, "init")
    git(work, "config", "user.name", "Mira Tests")
    git(work, "config", "user.email", "mira-tests@example.invalid")
    git(work, "remote", "add", "origin", str(remote))
    return work, remote


def test_check_and_push_new_branch_with_exact_remote_proof(tmp_path: Path) -> None:
    work, remote = repositories(tmp_path)
    source = commit(work, "first\n")
    receipt, path = subject.build_check_receipt(
        repo=work.resolve(),
        remote="origin",
        source_sha=source,
        target_ref="refs/heads/codex/test",
        validation_status="passed",
        temp_root=tmp_path,
    )
    assert receipt["update_kind"] == "new-branch"
    assert receipt["observed_remote_sha"] == "absent"
    assert receipt["authority_effect"] == "none"
    assert path.is_file()
    result = subject.execute_push(receipt)
    assert result["status"] == "pushed-and-verified"
    assert git(remote, "rev-parse", "refs/heads/codex/test") == source


def test_check_and_push_fast_forward(tmp_path: Path) -> None:
    work, remote = repositories(tmp_path)
    first = commit(work, "first\n")
    git(work, "push", "origin", f"{first}:refs/heads/codex/test")
    second = commit(work, "second\n")
    receipt, _ = subject.build_check_receipt(
        repo=work.resolve(), remote="origin", source_sha=second,
        target_ref="refs/heads/codex/test", validation_status="passed",
        temp_root=tmp_path,
    )
    assert receipt["update_kind"] == "fast-forward"
    assert receipt["observed_remote_sha"] == first
    assert subject.execute_push(receipt)["verified_remote_sha"] == second


def test_remote_advance_after_check_blocks_without_push(tmp_path: Path) -> None:
    work, remote = repositories(tmp_path)
    first = commit(work, "first\n")
    git(work, "push", "origin", f"{first}:refs/heads/codex/test")
    intended = commit(work, "intended\n")
    receipt, _ = subject.build_check_receipt(
        repo=work.resolve(), remote="origin", source_sha=intended,
        target_ref="refs/heads/codex/test", validation_status="passed",
        temp_root=tmp_path,
    )
    competing = commit(work, "competing\n")
    git(work, "push", "origin", f"{competing}:refs/heads/codex/test")
    with pytest.raises(subject.PushError, match="changed after check"):
        subject.execute_push(receipt)
    assert git(remote, "rev-parse", "refs/heads/codex/test") == competing


def test_non_fast_forward_and_unsafe_refs_fail_closed(tmp_path: Path) -> None:
    work, _ = repositories(tmp_path)
    first = commit(work, "first\n")
    git(work, "push", "origin", f"{first}:refs/heads/codex/test")
    git(work, "checkout", "--orphan", "unrelated")
    (work / "artifact.md").unlink(missing_ok=True)
    unrelated = commit(work, "unrelated\n")
    with pytest.raises(subject.PushError, match="not a fast-forward"):
        subject.build_check_receipt(
            repo=work.resolve(), remote="origin", source_sha=unrelated,
            target_ref="refs/heads/codex/test", validation_status="passed",
            temp_root=tmp_path,
        )
    for target in (
        "refs/tags/v1", "refs/heads/*", "refs/heads/delete.lock",
        "refs/heads/a b", "refs/heads/a:refs/heads/b",
    ):
        with pytest.raises(subject.PushError):
            subject.validate_target_ref(target)
    with pytest.raises(subject.PushError, match="full 40-character"):
        subject.validate_source(work, unrelated[:12])
    with pytest.raises(subject.PushError, match="lowercase"):
        subject.validate_source(work, unrelated.upper())


def test_failure_payload_distinguishes_preflight_from_attempted_push() -> None:
    assert subject.failure_payload(subject.PushError("preflight"))["remote_state_changed"] is False
    attempted = subject.PushError("unproven", remote_state_changed="unknown")
    assert subject.failure_payload(attempted)["remote_state_changed"] == "unknown"


def test_receipt_digest_and_external_root_are_enforced(tmp_path: Path) -> None:
    work, _ = repositories(tmp_path)
    source = commit(work, "first\n")
    receipt, path = subject.build_check_receipt(
        repo=work.resolve(), remote="origin", source_sha=source,
        target_ref="refs/heads/codex/test", validation_status="passed",
        temp_root=tmp_path,
    )
    loaded = subject.load_receipt(path, temp_root=tmp_path, repo_root=work)
    assert loaded == receipt
    tampered = dict(receipt)
    tampered["source_sha"] = "0" * 40
    path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(subject.PushError, match="digest mismatch"):
        subject.load_receipt(path, temp_root=tmp_path, repo_root=work)
    outside = tmp_path.parent / "outside-receipt.json"
    outside.write_text(json.dumps(receipt), encoding="utf-8")
    try:
        with pytest.raises(subject.PushError, match="outside"):
            subject.load_receipt(outside, temp_root=tmp_path, repo_root=work)
    finally:
        outside.unlink(missing_ok=True)

from __future__ import annotations

from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import publication_status


def report(monkeypatch, *, ahead, behind, dirty_lines):
    monkeypatch.setattr(publication_status, "porcelain", lambda _repo: dirty_lines)
    monkeypatch.setattr(publication_status, "upstream_ref", lambda _repo: "origin/main")
    monkeypatch.setattr(publication_status, "ahead_behind", lambda _repo, _upstream: (ahead, behind))
    monkeypatch.setattr(publication_status, "optional_sha", lambda _repo, ref: {"HEAD": "local", "origin/main": "remote"}.get(ref))
    monkeypatch.setattr(publication_status, "current_branch", lambda _repo: "main")
    return publication_status.build_report(ROOT)


def test_dirty_ahead_history_is_pushable_without_cleaning_worktree(monkeypatch) -> None:
    value = report(monkeypatch, ahead=1, behind=0, dirty_lines=[" M README.md", "?? scratch.md"])
    assert value["unpushed_commit_count"] == 1
    assert value["push_target_clean"] is True
    assert value["dirty_blocks_push"] is False
    assert value["recommended_boundary"] == "push-ready: committed local work"


def test_clean_ahead_history_reports_push_ready(monkeypatch) -> None:
    value = report(monkeypatch, ahead=2, behind=0, dirty_lines=[])
    assert value["push_target_clean"] is True
    assert value["dirty_blocks_push"] is False
    assert value["unpushed_commit_count"] == 2


def test_staged_ahead_history_still_distinguishes_push_target(monkeypatch) -> None:
    value = report(monkeypatch, ahead=1, behind=0, dirty_lines=["M  scripts/tool.py"])
    assert value["staged_count"] == 1
    assert value["push_target_clean"] is True
    assert value["dirty_blocks_push"] is False


def test_diverged_history_is_not_push_target_clean(monkeypatch) -> None:
    value = report(monkeypatch, ahead=1, behind=1, dirty_lines=[" M README.md"])
    assert value["push_target_clean"] is False
    assert value["dirty_blocks_push"] is True
    assert value["recommended_boundary"] == "main-sync-plan: diverged"


def test_no_upstream_is_not_push_target_clean(monkeypatch) -> None:
    monkeypatch.setattr(publication_status, "porcelain", lambda _repo: [" M README.md"])
    monkeypatch.setattr(publication_status, "upstream_ref", lambda _repo: None)
    monkeypatch.setattr(publication_status, "ahead_behind", lambda _repo, _upstream: (None, None))
    monkeypatch.setattr(publication_status, "optional_sha", lambda _repo, ref: "local" if ref == "HEAD" else None)
    monkeypatch.setattr(publication_status, "current_branch", lambda _repo: "main")
    value = publication_status.build_report(ROOT)
    assert value["push_target_clean"] is False
    assert value["dirty_blocks_push"] is True
    assert value["recommended_boundary"] == "inspect-only: upstream unavailable"

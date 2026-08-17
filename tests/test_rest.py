from __future__ import annotations

import json
from pathlib import Path

import pytest

import mira_continuity
import rest_receipts


SESSION = "01a001e8-c18a-7213-8afa-b7e4421aad72"


def source(tmp_path: Path, messages: list[tuple[str, str]]) -> mira_continuity.SessionSource:
    path = tmp_path / f"rollout-{SESSION}.jsonl"
    rows = [{
        "timestamp": "2026-08-17T10:00:00Z", "type": "session_meta",
        "payload": {"id": SESSION, "timestamp": "2026-08-17T10:00:00Z", "cwd": str(rest_receipts.REPO_ROOT)},
    }]
    for index, (timestamp, text) in enumerate(messages):
        rows.append({
            "timestamp": timestamp, "type": "response_item",
            "payload": {"type": "message", "id": f"msg-{index}", "role": "user",
                        "content": [{"type": "input_text", "text": text}]},
        })
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return mira_continuity.SessionSource(
        session_uuid=SESSION, started_at="2026-08-17T10:00:00Z",
        last_observed_at=messages[-1][0], cwd="$REPO_ROOT", source_kind="cli",
        source_class="active", source_name=path.name, path=path,
    )


def test_private_inbox_rejects_relative_and_repository_paths(tmp_path: Path) -> None:
    with pytest.raises(rest_receipts.RestError):
        rest_receipts.resolve_inbox("relative")
    with pytest.raises(rest_receipts.RestError):
        rest_receipts.resolve_inbox(rest_receipts.REPO_ROOT / "tmp")
    assert rest_receipts.resolve_inbox(tmp_path) == tmp_path.resolve()


def test_exact_rest_trigger_rejects_discussion(tmp_path: Path) -> None:
    current = source(tmp_path, [("2026-08-17T10:01:00Z", "please plan rest")])
    with pytest.raises(rest_receipts.RestError, match="exactly"):
        rest_receipts.planned_events(current, [])


def test_rest_resume_rest_is_ordered_and_idempotent(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(rest_receipts, "git_state", lambda: {
        "status": "available", "head": "abc", "branch": "main", "dirty_count": 0,
        "tracked_count": 0, "untracked_count": 0, "staged_count": 0, "ahead": 0, "behind": 0,
    })
    first = source(tmp_path, [("2026-08-17T10:01:00Z", "rest")])
    additions = rest_receipts.planned_events(first, [])
    assert [row["event_type"] for row in additions] == ["rested"]
    rest_receipts.write_events(tmp_path / "inbox", SESSION, additions)
    existing = rest_receipts.load_events(tmp_path / "inbox", SESSION)
    assert rest_receipts.planned_events(first, existing) == []

    resumed = source(tmp_path, [
        ("2026-08-17T10:01:00Z", "rest"),
        ("2026-08-17T11:00:00Z", "one more thing"),
        ("2026-08-17T11:05:00Z", "rest"),
    ])
    additions = rest_receipts.planned_events(resumed, existing)
    assert [row["event_type"] for row in additions] == ["resumed", "rested"]
    rest_receipts.write_events(tmp_path / "inbox", SESSION, additions)
    events = rest_receipts.load_events(tmp_path / "inbox", SESSION)
    assert [row["sequence"] for row in events] == [1, 2, 3]
    assert [row["event_type"] for row in events] == ["rested", "resumed", "rested"]
    assert events[-1]["requested_reviews"] == [
        {"owner": "mira-journal", "state": "pending-consideration"},
        {"owner": "recursive-learn", "state": "pending-screening"},
    ]
    assert events[-1]["local_date"] == "2026-08-17"
    assert events[-1]["timezone"] == "America/Denver"
    assert rest_receipts.projection(tmp_path / "inbox", SESSION)["requested_reviews"] == [
        {"owner": "mira-journal", "state": "pending-consideration"},
        {"owner": "recursive-learn", "state": "pending-screening"},
    ]


def test_projection_derives_resume_without_writing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(rest_receipts, "git_state", lambda: {"status": "available", "dirty_count": 0, "ahead": 0})
    initial = source(tmp_path, [("2026-08-17T10:01:00Z", "rest")])
    inbox = tmp_path / "inbox"
    rest_receipts.write_events(inbox, SESSION, rest_receipts.planned_events(initial, []))
    before = sorted(path.relative_to(inbox) for path in inbox.rglob("*"))
    resumed = source(tmp_path, [
        ("2026-08-17T10:01:00Z", "rest"),
        ("2026-08-17T11:00:00Z", "returned"),
    ])
    value = rest_receipts.projection(inbox, SESSION, resumed)
    after = sorted(path.relative_to(inbox) for path in inbox.rglob("*"))
    assert value["recorded_state"] == "rested"
    assert value["current_state"] == "resumed"
    assert value["derived_resume"] is True
    assert before == after


def test_corrupt_receipt_fails_closed(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(rest_receipts, "git_state", lambda: {"status": "available", "dirty_count": 0, "ahead": 0})
    current = source(tmp_path, [("2026-08-17T10:01:00Z", "rest")])
    inbox = tmp_path / "inbox"
    rest_receipts.write_events(inbox, SESSION, rest_receipts.planned_events(current, []))
    receipt = next(inbox.rglob("*.json"))
    value = json.loads(receipt.read_text(encoding="utf-8"))
    value["event_type"] = "resumed"
    receipt.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(rest_receipts.RestError, match="digest"):
        rest_receipts.load_events(inbox, SESSION)


def test_coffee_coverage_states(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(rest_receipts, "git_state", lambda: {"status": "available", "dirty_count": 0, "ahead": 0})
    current = source(tmp_path, [("2026-08-17T10:01:00Z", "rest")])
    inbox = tmp_path / "inbox"
    rest_receipts.write_events(inbox, SESSION, rest_receipts.planned_events(current, []))
    assert rest_receipts.coffee_coverage(inbox, None) == "missing-dream"
    episode = {
        "created_at": "2026-08-17T12:00:00Z",
        "session_coverage": [{"session_id": f"MS-{SESSION}"}],
    }
    assert rest_receipts.coffee_coverage(inbox, episode) == "covered-current"

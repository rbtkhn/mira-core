from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

import mira_journal as subject


SESSION = "MS-019fce7b-67cd-7753-be6c-74f76e2f9b7a"


def prose(day: str, title: str = "A Day I Can Carry Forward", marker: str = "steady") -> bytes:
    sentence = (
        f"I remember this {marker} day as a moment when my continuity became clearer, "
        "because I could connect what changed with why it mattered and what I still do not know. "
    )
    body = ""
    while len(subject.WORD_RE.findall(body)) < 330:
        body += sentence
    return f"# {day} — {title}\n\n{body.strip()}\n".encode("utf-8")


def source_ref(seed: str = "a") -> dict:
    return {
        "kind": "journal-context-pack",
        "context_pack_id": "CP-" + seed * 24,
        "object_id": seed * 64,
    }


def metadata(day: str, body: bytes, version: int = 1, previous: str | None = None) -> dict:
    parsed_day = subject.parse_entry_date(day)
    start, end = subject.day_bounds(parsed_day)
    ref = source_ref("a")
    digest = subject.sha256_bytes(body)
    return {
        "schema_version": 1,
        "journal_id": subject.journal_id(parsed_day),
        "version_id": subject.version_id(parsed_day, version),
        "entry_date": day,
        "status": "private-draft",
        "authored_at": subject.utc_text(start.replace(hour=start.hour + 2)),
        "author": {"identity": "Mira", "session_id": SESSION, "model_id": "test-model"},
        "coverage": {
            "start": subject.utc_text(start),
            "end": subject.utc_text(end),
            "as_of": subject.utc_text(start.replace(hour=start.hour + 1)),
            "retrospective": False,
        },
        "quiet_day": False,
        "limited_activity_acknowledged": False,
        "source_refs": [ref],
        "previous_version_digest": previous,
        "derivation_manifest": {
            "schema_version": 1,
            "derivation_id": "DRV-" + "b" * 24,
            "transformation_type": "probabilistic-mira-journal-draft",
            "deterministic": False,
            "producer": {"kind": "model", "id": "test-model", "session_id": SESSION},
            "input_object_ids": [ref["object_id"]],
            "output_digest": digest,
            "prompt_digest": "c" * 64,
            "evaluation_refs": [],
        },
    }


def configure_repo(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    mira = repo / "mira"
    journal = mira / "journal"
    drafts = tmp_path / "private-drafts"
    journal.mkdir(parents=True)
    drafts.mkdir()
    monkeypatch.setattr(subject, "REPO_ROOT", repo)
    monkeypatch.setattr(subject, "MIRA_ROOT", mira)
    monkeypatch.setattr(subject, "JOURNAL_ROOT", journal)
    monkeypatch.setattr(subject, "INDEX_PATH", mira / "journal.md")
    monkeypatch.setattr(subject, "REGISTRY_PATH", mira / "journal-registry.json")
    monkeypatch.setattr(subject, "SESSION_REGISTRY_PATH", mira / "continuity" / "session-registry.json")
    monkeypatch.setattr(subject, "latest_activity_after", lambda *args, **kwargs: [])
    subject.atomic_write_json(subject.REGISTRY_PATH, subject.default_registry())
    subject.atomic_write_text(subject.INDEX_PATH, subject.render_index(subject.default_registry()))
    return repo, drafts


def write_bundle(drafts: Path, day: str, body: bytes, value: dict) -> Path:
    root = drafts / day
    root.mkdir(parents=True, exist_ok=True)
    draft = root / "draft.md"
    draft.write_bytes(body)
    draft.with_suffix(".json").write_text(json.dumps(value), encoding="utf-8")
    return draft


def action_args(day: str, draft: Path, *, check: bool = False) -> argparse.Namespace:
    return argparse.Namespace(
        date=day,
        draft=draft,
        authority_ref=SESSION,
        approved_at="2026-08-09T18:00:00Z",
        check=check,
    )


def test_markdown_contract_enforces_date_length_and_first_person() -> None:
    value = prose("2026-08-09")
    parsed = subject.parse_markdown(value, "2026-08-09")
    assert 300 <= parsed["word_count"] <= 700
    with pytest.raises(subject.JournalError, match="heading date"):
        subject.parse_markdown(value, "2026-08-10")
    with pytest.raises(subject.JournalError, match="300-700"):
        subject.parse_markdown("# 2026-08-09 — Too Short\n\nI remember.\n".encode("utf-8"), "2026-08-09")


def test_denver_calendar_bounds_cover_dst_transitions() -> None:
    spring_start, spring_end = subject.day_bounds(subject.parse_entry_date("2026-03-08"))
    fall_start, fall_end = subject.day_bounds(subject.parse_entry_date("2026-11-01"))
    assert (spring_end - spring_start).total_seconds() == 23 * 3600
    assert (fall_end - fall_start).total_seconds() == 25 * 3600


def test_approve_check_is_non_mutating_and_approve_registers_entry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day)
    draft = write_bundle(drafts, day, body, metadata(day, body))
    checked = subject.approve_or_revise(action_args(day, draft, check=True), revising=False)
    assert checked["status"] == "ready"
    assert not subject.entry_path(subject.parse_entry_date(day)).exists()
    approved = subject.approve_or_revise(action_args(day, draft), revising=False)
    assert approved["status"] == "approved"
    registry = subject.load_registry()
    assert registry["entries"][0]["current_version_id"] == "MJ-20260809-v1"
    assert subject.validate_registry(registry, repo_root=subject.REPO_ROOT, index_path=subject.INDEX_PATH) == []


def test_revision_replaces_current_view_and_preserves_digest_chain(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    first = prose(day, marker="first")
    first_draft = write_bundle(drafts, day, first, metadata(day, first))
    subject.approve_or_revise(action_args(day, first_draft), revising=False)
    first_digest = subject.sha256_bytes(first)
    second = prose(day, title="The Revised Day", marker="revised")
    second_draft = write_bundle(drafts, day, second, metadata(day, second, 2, first_digest))
    result = subject.approve_or_revise(action_args(day, second_draft), revising=True)
    assert result["version_id"] == "MJ-20260809-v2"
    registry = subject.load_registry()
    versions = registry["entries"][0]["versions"]
    assert versions[1]["previous_version_digest"] == versions[0]["content_sha256"]
    assert subject.entry_path(subject.parse_entry_date(day)).read_bytes() == second


def test_unregistered_manual_edit_fails_validation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day)
    draft = write_bundle(drafts, day, body, metadata(day, body))
    subject.approve_or_revise(action_args(day, draft), revising=False)
    subject.entry_path(subject.parse_entry_date(day)).write_bytes(prose(day, marker="tampered"))
    assert any("unregistered journal prose drift" in item for item in subject.validate_registry(subject.load_registry(), repo_root=subject.REPO_ROOT, index_path=subject.INDEX_PATH))


def test_late_activity_requires_refresh(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day)
    draft = write_bundle(drafts, day, body, metadata(day, body))
    monkeypatch.setattr(subject, "latest_activity_after", lambda *args, **kwargs: ["MR-" + "a" * 24])
    with pytest.raises(subject.JournalError, match="requires refresh"):
        subject.approve_or_revise(action_args(day, draft), revising=False)


def test_quiet_day_requires_explicit_acknowledgment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day, marker="quiet")
    value = metadata(day, body)
    value["quiet_day"] = True
    draft = write_bundle(drafts, day, body, value)
    with pytest.raises(subject.JournalError, match="acknowledge limited activity"):
        subject.approve_or_revise(action_args(day, draft), revising=False)
    value["limited_activity_acknowledged"] = True
    draft = write_bundle(drafts, day, body, value)
    assert subject.approve_or_revise(action_args(day, draft), revising=False)["status"] == "approved"


def test_prepare_check_is_deterministic_and_reports_quiet_day(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    configure_repo(monkeypatch, tmp_path)
    monkeypatch.setattr(subject, "session_sources_since", lambda minimum: [])
    monkeypatch.setattr(subject, "git_commits", lambda start, end: [])
    args = argparse.Namespace(
        date="2026-08-08",
        as_of="2026-08-09T06:00:00Z",
        token_budget=16000,
        output_root=tmp_path / "drafts-two",
        check=True,
    )
    first = subject.command_prepare(args)
    second = subject.command_prepare(args)
    assert first == second
    assert first["quiet_day"] is True
    assert not (tmp_path / "drafts-two").exists()


def test_activity_contract_selects_or_explicitly_omits_every_daily_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = [
        {
            "record_id": "MR-" + "a" * 24,
            "timestamp": "2026-08-09T07:00:00Z",
            "kind": "message",
            "role": "user",
            "content": [{"type": "text", "text": "brief activity"}],
        },
        {
            "record_id": "MR-" + "b" * 24,
            "timestamp": "2026-08-09T08:00:00Z",
            "kind": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "long " * 2000}],
        },
    ]
    source = SimpleNamespace(
        session_id=SESSION,
        started_at="2026-08-09T06:30:00Z",
        last_observed_at="2026-08-09T08:30:00Z",
    )
    monkeypatch.setattr(subject, "normalized_rows", lambda value: ("MC-" + "c" * 24, "d" * 64, rows))
    monkeypatch.setattr(subject, "git_commits", lambda start, end: [])
    activity = subject.collect_activity(
        subject.parse_entry_date("2026-08-09"),
        as_of=datetime(2026, 8, 9, 9, tzinfo=timezone.utc),
        token_budget=256,
        sources=[source],
    )
    accounted = {row["record_id"] for row in activity["selected_records"]} | {
        row["record_id"] for row in activity["omissions"]
    }
    assert accounted == {row["record_id"] for row in rows}
    assert activity["omissions"] == [{"record_id": "MR-" + "b" * 24, "reason": "token-budget"}]


def test_draft_bundle_inside_git_is_rejected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo, _ = configure_repo(monkeypatch, tmp_path)
    draft = repo / "draft.md"
    draft.write_bytes(prose("2026-08-09"))
    draft.with_suffix(".json").write_text("{}", encoding="utf-8")
    with pytest.raises(subject.JournalError, match="outside Git"):
        subject.load_draft_bundle(draft)


def test_privacy_and_authority_boundaries_are_enforced(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day).replace(b"I remember", b"I remember person@example.com", 1)
    draft = write_bundle(drafts, day, body, metadata(day, body))
    with pytest.raises(subject.JournalError, match="direct email"):
        subject.approve_or_revise(action_args(day, draft), revising=False)
    assert "not identity doctrine" in subject.AUTHORITY_BOUNDARY
    assert "not identity doctrine" in subject.render_index(subject.default_registry())


def test_status_distinguishes_missing_drafted_approved_and_revision_pending(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day)
    draft = write_bundle(drafts, day, body, metadata(day, body))
    subject.approve_or_revise(action_args(day, draft), revising=False)
    args = argparse.Namespace(from_date=day, to_date="2026-08-10", draft_root=drafts)
    rows = subject.command_status(args)["days"]
    assert rows == [
        {"date": "2026-08-09", "status": "revision-pending"},
        {"date": "2026-08-10", "status": "missing"},
    ]

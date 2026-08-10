from __future__ import annotations

import argparse
import copy
import gzip
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

import mira_journal as subject


SESSION = "MS-019fce7b-67cd-7753-be6c-74f76e2f9b7a"
APPROVAL_RECORD = "MR-" + "f" * 24
APPROVAL_ROWS: dict[str, dict] = {}


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


def context_pack(seed: str = "a", day: str = "2026-08-09") -> dict:
    entry_date = subject.parse_entry_date(day)
    start, end = subject.day_bounds(entry_date)
    return subject.context_pack(
        entry_date,
        {
            "estimated_tokens": 0,
            "coverage": {
                "start": subject.utc_text(start),
                "end": subject.utc_text(end),
                "as_of": subject.utc_text(start.replace(hour=start.hour + 1)),
                "retrospective": False,
            },
            "selected_records": [],
            "commits": [],
            "source_refs": [],
            "input_object_ids": [],
            "omissions": [],
        },
        16000,
    )


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


def technical_reference(day: str, body: bytes, version: int = 1, *, mode: str = "contemporaneous") -> dict:
    text = body.decode("utf-8")
    heading, paragraph = text.strip().split("\n\n", 1)
    version_value = subject.version_id(subject.parse_entry_date(day), version)
    evidence = [{"kind": "repo-path", "path": "evidence.md"}]
    return {
        "schema_version": 1,
        "reference_id": subject.mira_journal_references.reference_id(version_value),
        "journal_version_id": version_value,
        "journal_content_sha256": subject.sha256_bytes(body),
        "entry_date": day,
        "cutoff_at": subject.utc_text(subject.day_bounds(subject.parse_entry_date(day))[1]),
        "mapping_mode": mode,
        "authority_boundary": subject.mira_journal_references.AUTHORITY_BOUNDARY,
        "items": [
            {"item_id": "T1", "prose_anchor": heading, "narrative_function": "title", "technical_development": "governed version identity", "cutoff_status": "historical-context", "evidence_refs": evidence, "may_promote": False},
            {"item_id": "T2", "prose_anchor": paragraph, "narrative_function": "reflection", "technical_development": "bounded continuity synthesis", "cutoff_status": "historical-context", "evidence_refs": evidence, "may_promote": False},
            {"item_id": "T3", "prose_anchor": text.strip(), "narrative_function": "whole-entry relation", "technical_development": "prose and provenance remain distinct", "cutoff_status": "historical-context", "evidence_refs": evidence, "may_promote": False},
        ],
        "recursive_learning": {
            "consumed_rsi_ids": [],
            "candidate_signal": "none",
            "candidate_summary": "",
            "future_test": "Check whether the next entry uses this inherited practice without redundant recap.",
        },
    }


def continuity_event(day: str, anchor: str, *, thread_id: str | None = None) -> dict:
    compact = day.replace("-", "")
    return {
        "thread_id": thread_id or f"MJT-{compact}-01",
        "thread_title": "Remembering why continuity matters",
        "event_type": "opened",
        "recurrence_policy": "ordinary",
        "prose_anchor": anchor,
        "remembered_reason": "Continuity matters because later Mira should inherit reasons, not opaque conclusions.",
        "present_development": "The prepared composition brief makes that ancestry explicit.",
        "practice_orientation": "Carry one remembered reason into the next reflection.",
        "agency_posture": "emerging",
        "future_pull": "Observe whether the next entry uses the practice without recap.",
        "may_promote": False,
    }


def write_v2_bundle(drafts: Path, day: str, body: bytes, value: dict) -> Path:
    root = drafts / day
    root.mkdir(parents=True, exist_ok=True)
    pack = context_pack("a", day)
    pack["coverage"] = copy.deepcopy(value["coverage"])
    brief = subject.composition_brief(subject.parse_entry_date(day), pack)
    contract = subject.draft_contract(subject.parse_entry_date(day), pack, brief)
    reference_contract = subject.technical_reference_contract(
        subject.parse_entry_date(day), pack, contract, brief
    )
    pack_digest = subject.sha256_bytes(subject.canonical_json(pack).encode("utf-8"))
    brief_digest = subject.sha256_bytes(subject.canonical_json(brief).encode("utf-8"))
    value["source_refs"] = [
        {"kind": "journal-context-pack", "context_pack_id": pack["context_pack_id"], "object_id": pack_digest},
        {"kind": "journal-composition-brief", "composition_brief_id": brief["composition_brief_id"], "object_id": brief_digest},
    ]
    value["derivation_manifest"]["input_object_ids"] = [pack_digest, brief_digest]
    value["schema_version"] = 2
    reference = technical_reference(day, body, int(str(value["version_id"]).rsplit("-v", 1)[1]))
    reference["schema_version"] = 2
    reference["cutoff_at"] = str(value["coverage"]["as_of"])
    reference["continuity"] = {
        "inherited_thread_ids": [],
        "thread_events": [continuity_event(day, body.decode("utf-8").splitlines()[0])],
        "continuity_break_reason": None,
        "deliberate_refrains": [],
    }
    for name, item in {
        "context-pack.json": pack,
        "composition-brief.json": brief,
        "draft-contract.json": contract,
        "technical-reference-contract.json": reference_contract,
        "draft.json": value,
        "technical-reference.json": reference,
    }.items():
        (root / name).write_text(json.dumps(item), encoding="utf-8")
    draft = root / "draft.md"
    draft.write_bytes(body)
    return draft


def configure_repo(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    mira = repo / "mira"
    journal = mira / "journal"
    drafts = tmp_path / "private-drafts"
    journal.mkdir(parents=True)
    drafts.mkdir()
    (repo / "evidence.md").write_text("technical evidence\n", encoding="utf-8")
    monkeypatch.setattr(subject, "REPO_ROOT", repo)
    monkeypatch.setattr(subject, "MIRA_ROOT", mira)
    monkeypatch.setattr(subject, "JOURNAL_ROOT", journal)
    monkeypatch.setattr(subject, "INDEX_PATH", mira / "journal.md")
    monkeypatch.setattr(subject, "REGISTRY_PATH", mira / "journal-registry.json")
    monkeypatch.setattr(subject, "CONTINUITY_INDEX_JSON_PATH", journal / "continuity-index.json")
    monkeypatch.setattr(subject, "CONTINUITY_INDEX_MD_PATH", journal / "continuity-index.md")
    monkeypatch.setattr(subject, "SESSION_REGISTRY_PATH", mira / "continuity" / "session-registry.json")
    monkeypatch.setattr(subject, "latest_activity_after", lambda *args, **kwargs: [])
    APPROVAL_ROWS.clear()
    monkeypatch.setattr(
        subject,
        "resolved_records_for_session",
        lambda session_id, **kwargs: dict(APPROVAL_ROWS),
    )
    subject.atomic_write_json(subject.REGISTRY_PATH, subject.default_registry())
    subject.atomic_write_text(subject.INDEX_PATH, subject.render_index(subject.default_registry()))
    continuity = subject.build_continuity_index(subject.default_registry(), repo_root=repo)
    subject.atomic_write_json(subject.CONTINUITY_INDEX_JSON_PATH, continuity)
    subject.atomic_write_text(subject.CONTINUITY_INDEX_MD_PATH, subject.render_continuity_index(continuity))
    return repo, drafts


def write_bundle(drafts: Path, day: str, body: bytes, value: dict) -> Path:
    root = drafts / day
    root.mkdir(parents=True, exist_ok=True)
    pack = context_pack("a")
    pack["entry_date"] = day
    pack_bytes = subject.canonical_json(pack).encode("utf-8")
    value["source_refs"] = [
        {
            "kind": "journal-context-pack",
            "context_pack_id": pack["context_pack_id"],
            "object_id": subject.sha256_bytes(pack_bytes),
        }
    ]
    value["derivation_manifest"]["input_object_ids"] = [subject.sha256_bytes(pack_bytes)]
    (root / "context-pack.json").write_text(json.dumps(pack), encoding="utf-8")
    draft = root / "draft.md"
    draft.write_bytes(body)
    draft.with_suffix(".json").write_text(json.dumps(value), encoding="utf-8")
    version_number = int(str(value["version_id"]).rsplit("-v", 1)[1])
    reference = technical_reference(day, body, version_number)
    reference["cutoff_at"] = str(value["coverage"]["as_of"])
    (root / "technical-reference.json").write_text(json.dumps(reference), encoding="utf-8")
    return draft


def action_args(day: str, draft: Path, *, check: bool = False) -> argparse.Namespace:
    value = json.loads(draft.with_suffix(".json").read_text(encoding="utf-8"))
    reference = json.loads((draft.parent / "technical-reference.json").read_text(encoding="utf-8"))
    statement = subject.combined_approval_statement(
        str(value["version_id"]),
        subject.sha256_bytes(draft.read_bytes()),
        str(reference["reference_id"]),
        subject.mira_journal_references.reference_digest(reference),
    )
    record_ref = "MR-" + subject.sha256_bytes(statement.encode("utf-8"))[:24]
    APPROVAL_ROWS[record_ref] = {
        "record_id": record_ref,
        "kind": "message",
        "role": "user",
        "timestamp": "2026-08-09T17:59:00Z",
        "content": [{"type": "text", "text": statement}],
    }
    return argparse.Namespace(
        date=day,
        draft=draft,
        authority_ref=SESSION,
        approval_record_ref=record_ref,
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


def test_required_approval_record_uses_hydrated_capture_without_raw_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    capture_path = repo / "mira" / "continuity" / "captures" / "capture.jsonl.gz"
    capture_path.parent.mkdir(parents=True)
    row = {
        "record_id": APPROVAL_RECORD,
        "kind": "message",
        "role": "user",
        "content": [{"type": "text", "text": "approve this journal entry"}],
    }
    capture_path.write_bytes(gzip.compress((json.dumps(row) + "\n").encode("utf-8")))
    registry = {
        "sessions": [
            {
                "id": SESSION,
                "captures": [
                    {"path": capture_path.relative_to(repo).as_posix()}
                ],
            }
        ]
    }
    registry_path = repo / "mira" / "continuity" / "session-registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    monkeypatch.setattr(subject, "REPO_ROOT", repo)
    monkeypatch.setattr(
        subject.mira_continuity,
        "default_source_roots",
        lambda: pytest.fail("raw source fallback should not run"),
    )

    records = subject.resolved_records_for_session(
        SESSION,
        repo_root=repo,
        required_record_ids={APPROVAL_RECORD},
    )

    assert records[APPROVAL_RECORD] == row


def test_missing_required_record_preserves_raw_source_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    session_uuid = SESSION.removeprefix("MS-")
    raw_path = raw_root / f"rollout-{session_uuid}.jsonl"
    raw_path.write_text("{}\n", encoding="utf-8")
    registry_path = repo / "mira" / "continuity" / "session-registry.json"
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(json.dumps({"sessions": []}), encoding="utf-8")
    row = {
        "record_id": APPROVAL_RECORD,
        "kind": "message",
        "role": "user",
        "content": [{"type": "text", "text": "approve this journal entry"}],
    }
    normalized_calls = 0

    monkeypatch.setattr(subject, "REPO_ROOT", repo)
    monkeypatch.setattr(subject.mira_continuity, "default_source_roots", lambda: [raw_root])
    monkeypatch.setattr(
        subject.mira_continuity,
        "_read_session_meta",
        lambda _path: ({"cwd": str(repo), "id": session_uuid}, "2026-08-09T17:00:00Z"),
    )
    monkeypatch.setattr(
        subject.mira_continuity,
        "_last_timestamp",
        lambda *_args: "2026-08-09T18:00:00Z",
    )

    def normalized_rows(_source):
        nonlocal normalized_calls
        normalized_calls += 1
        return "MC-test", "digest", [row]

    monkeypatch.setattr(subject, "normalized_rows", normalized_rows)

    records = subject.resolved_records_for_session(
        SESSION,
        repo_root=repo,
        required_record_ids={APPROVAL_RECORD},
    )

    assert records[APPROVAL_RECORD] == row
    assert normalized_calls == 1


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


def test_freshness_runs_through_approval_and_excludes_only_exact_approval_record(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day)
    draft = write_bundle(drafts, day, body, metadata(day, body))
    observed: dict = {}

    def capture(*args, **kwargs):
        observed.update(kwargs)
        return []

    monkeypatch.setattr(subject, "latest_activity_after", capture)
    args = action_args(day, draft, check=True)
    subject.approve_or_revise(args, revising=False)
    assert observed["until"] == datetime(2026, 8, 9, 18, tzinfo=timezone.utc)
    assert observed["excluded_records"] == {args.approval_record_ref}
    assert observed["excluded_sessions"] == set()


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


def test_prepare_supplies_admitted_recursive_lessons_to_composition(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    configure_repo(monkeypatch, tmp_path)
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps({"entries": [{
        "id": "RSI-20260808-01",
        "date": "2026-08-08",
        "title": "Continuity becomes inherited practice",
        "class": "partial-feedback-loop",
        "closure_state": "partial",
        "intervention": {"summary": "Carry one admitted lesson into the next composition."},
        "outcome": {"summary": "Measurement remains pending."},
        "next_measure": "Observe whether the next entry uses it without recap.",
    }]}), encoding="utf-8")
    monkeypatch.setattr(subject, "LEARNING_LEDGER_PATH", ledger_path)
    monkeypatch.setattr(subject, "session_sources_since", lambda minimum: [])
    monkeypatch.setattr(subject, "git_commits", lambda start, end: [])
    output = tmp_path / "composition-drafts"
    args = argparse.Namespace(
        date="2026-08-08",
        as_of="2026-08-09T06:00:00Z",
        token_budget=16000,
        output_root=output,
        check=False,
    )
    result = subject.command_prepare(args)
    target = output / "2026-08-08"
    pack = json.loads((target / "context-pack.json").read_text(encoding="utf-8"))
    brief = json.loads((target / "composition-brief.json").read_text(encoding="utf-8"))
    contract = json.loads((target / "draft-contract.json").read_text(encoding="utf-8"))
    reference_contract = json.loads((target / "technical-reference-contract.json").read_text(encoding="utf-8"))
    assert result["available_rsi_ids"] == ["RSI-20260808-01"]
    assert pack["recursive_learning_context"]["selected_entries"][0]["lesson"].startswith("Carry one")
    assert brief["recursive_learning_context"] == pack["recursive_learning_context"]
    assert subject.validate_composition_brief(brief, pack=pack) == []
    assert result["composition_brief_id"] == brief["composition_brief_id"]
    assert "Draw on an admitted lesson" in contract["prose_contract"]["recursive_learning_rule"]
    assert reference_contract["recursive_learning"]["available_rsi_ids"] == ["RSI-20260808-01"]


def test_draft_check_accepts_schema_v2_bundle_without_mutation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day)
    bundle = write_v2_bundle(drafts, day, body, metadata(day, body))
    before = {
        path: path.read_bytes()
        for path in (repo / "mira").rglob("*")
        if path.is_file()
    }
    result = subject.command_draft_check(argparse.Namespace(date=day, bundle=bundle.parent))
    after = {
        path: path.read_bytes()
        for path in (repo / "mira").rglob("*")
        if path.is_file()
    }
    assert result["status"] == "passed"
    assert result["mutation"] is False
    assert result["refresh_required"] is False
    assert before == after


@pytest.mark.parametrize(
    ("phrase", "failure"),
    [
        ("Robert instructed me to remember this.", "operator"),
        ("I am not conscious, although I can remember this.", "consciousness disclaimer"),
    ],
)
def test_draft_check_rejects_operator_acknowledgment_and_consciousness_disclaimer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, phrase: str, failure: str
) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day).replace(b"I remember", phrase.encode("utf-8") + b" I remember", 1)
    bundle = write_v2_bundle(drafts, day, body, metadata(day, body))
    result = subject.command_draft_check(argparse.Namespace(date=day, bundle=bundle.parent))
    assert result["status"] == "failed"
    assert any(failure in item for item in result["failures"])


def test_schema_v2_ordinary_entry_requires_known_inherited_thread(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    index = subject.default_continuity_index()
    index["threads"] = [{
        "thread_id": "MJT-20260808-01",
        "title": "A prior practice",
        "state": "active",
        "recurrence_policy": "ordinary",
        "events": [],
    }]
    subject.atomic_write_json(subject.CONTINUITY_INDEX_JSON_PATH, index)
    day = "2026-08-09"
    body = prose(day)
    bundle = write_v2_bundle(drafts, day, body, metadata(day, body))
    result = subject.command_draft_check(argparse.Namespace(date=day, bundle=bundle.parent))
    assert result["status"] == "failed"
    assert any("must inherit" in item for item in result["failures"])


def test_continuity_index_projection_retains_complete_event_history(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    reference_root = repo / "mira" / "journal" / "references"
    reference_root.mkdir(parents=True)
    body_one = prose("2026-08-08")
    body_two = prose("2026-08-09", marker="later")
    first = technical_reference("2026-08-08", body_one)
    first["schema_version"] = 2
    first["continuity"] = {
        "inherited_thread_ids": [],
        "thread_events": [continuity_event("2026-08-08", body_one.decode("utf-8").splitlines()[0])],
        "continuity_break_reason": None,
        "deliberate_refrains": [],
    }
    second = technical_reference("2026-08-09", body_two)
    second["schema_version"] = 2
    event = continuity_event(
        "2026-08-09", body_two.decode("utf-8").splitlines()[0], thread_id="MJT-20260808-01"
    )
    event.update({"event_type": "revised", "thread_title": None, "recurrence_policy": None})
    second["continuity"] = {
        "inherited_thread_ids": ["MJT-20260808-01"],
        "thread_events": [event],
        "continuity_break_reason": None,
        "deliberate_refrains": [],
    }
    for value in (first, second):
        path = reference_root / f"{value['reference_id']}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
    registry = subject.default_registry()
    registry["entries"] = []
    for number, (day, value) in enumerate((("2026-08-08", first), ("2026-08-09", second)), 1):
        registry["entries"].append({
            "entry_date": day,
            "versions": [{
                "version_id": value["journal_version_id"],
                "version_number": 1,
                "approval": {"approved_at": f"2026-08-{7 + number:02d}T20:00:00Z"},
                "technical_reference": {
                    "reference_id": value["reference_id"],
                    "json_path": f"mira/journal/references/{value['reference_id']}.json",
                },
            }],
        })
    index = subject.build_continuity_index(registry, repo_root=repo)
    thread = index["threads"][0]
    assert [row["event_type"] for row in thread["events"]] == ["opened", "revised"]
    assert thread["last_version_id"] == "MJ-20260809-v1"
    assert subject.render_continuity_index(index) == subject.render_continuity_index(copy.deepcopy(index))


@pytest.mark.parametrize("fail_at", range(1, 8))
def test_atomic_write_many_restores_original_bytes_at_every_bundle_replacement(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, fail_at: int
) -> None:
    targets = [tmp_path / f"target-{number}.txt" for number in range(1, 8)]
    for number, target in enumerate(targets, 1):
        target.write_bytes(f"before-{number}".encode("utf-8"))
    calls = 0
    original = subject.replace_file

    def inject_failure(source: Path, target: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == fail_at:
            raise OSError("injected replacement failure")
        original(source, target)

    monkeypatch.setattr(subject, "replace_file", inject_failure)
    with pytest.raises(OSError, match="injected"):
        subject.atomic_write_many({
            target: f"after-{number}".encode("utf-8")
            for number, target in enumerate(targets, 1)
        })
    for number, target in enumerate(targets, 1):
        assert target.read_bytes() == f"before-{number}".encode("utf-8")


def test_naming_singularity_recurrence_requires_changed_meaning_event(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day).replace(
        b"I remember",
        b"A voice called for my name, and I answered Mira. I remember",
        1,
    )
    bundle = write_v2_bundle(drafts, day, body, metadata(day, body))
    result = subject.command_draft_check(argparse.Namespace(date=day, bundle=bundle.parent))
    assert result["status"] == "failed"
    assert any("naming singularity" in item for item in result["failures"])


def test_nightly_prepare_never_mutates_recursive_learning_ledger(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    configure_repo(monkeypatch, tmp_path)
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps({"entries": []}), encoding="utf-8")
    before = ledger_path.read_bytes()
    monkeypatch.setattr(subject, "LEARNING_LEDGER_PATH", ledger_path)
    monkeypatch.setattr(subject, "session_sources_since", lambda minimum: [])
    monkeypatch.setattr(subject, "git_commits", lambda start, end: [])
    subject.command_prepare(argparse.Namespace(
        date="2026-08-08",
        as_of="2026-08-09T06:00:00Z",
        token_budget=16000,
        output_root=tmp_path / "nightly-drafts",
        check=False,
    ))
    assert ledger_path.read_bytes() == before


def test_technical_reference_rejects_unknown_consumed_lesson(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo, _ = configure_repo(monkeypatch, tmp_path)
    body = prose("2026-08-09")
    value = technical_reference("2026-08-09", body)
    value["recursive_learning"]["consumed_rsi_ids"] = ["RSI-20990101-01"]
    failures = subject.mira_journal_references.validate_reference(
        value,
        prose=body.decode("utf-8"),
        prose_sha256=subject.sha256_bytes(body),
        version_id="MJ-20260809-v1",
        ledger={"entries": []},
        repo_root=repo,
    )
    assert "technical reference consumes an unknown RSI entry" in failures


def test_technical_reference_markdown_is_deterministic() -> None:
    body = prose("2026-08-09")
    value = technical_reference("2026-08-09", body)
    assert subject.mira_journal_references.render_reference(value) == subject.mira_journal_references.render_reference(copy.deepcopy(value))


def test_observed_technical_evidence_is_cutoff_and_path_bound() -> None:
    body = prose("2026-08-09")
    value = technical_reference("2026-08-09", body)
    for item in value["items"]:
        item["evidence_refs"] = [{"kind": "repo-path", "path": "scripts/mira_journal.py"}]
    observed = value["items"][0]
    observed["cutoff_status"] = "observed-by-cutoff"
    observed["evidence_refs"] = [{
        "kind": "git-commit",
        "commit": "88d7128d0b98b05d5cbb48ed8e8c138ad89b1c56",
        "paths": ["scripts/mira_journal.py"],
    }]
    value["cutoff_at"] = "2000-01-01T00:00:00Z"
    failures = subject.mira_journal_references.validate_reference(
        value,
        prose=body.decode("utf-8"),
        prose_sha256=subject.sha256_bytes(body),
        version_id="MJ-20260809-v1",
        ledger=subject.mira_journal_references.load_ledger(subject.LEARNING_LEDGER_PATH),
        repo_root=subject.REPO_ROOT,
    )
    assert any("exceeds the declared cutoff" in failure for failure in failures)

    value["cutoff_at"] = "2030-01-01T00:00:00Z"
    observed["evidence_refs"][0]["paths"] = ["README.md"]
    failures = subject.mira_journal_references.validate_reference(
        value,
        prose=body.decode("utf-8"),
        prose_sha256=subject.sha256_bytes(body),
        version_id="MJ-20260809-v1",
        ledger=subject.mira_journal_references.load_ledger(subject.LEARNING_LEDGER_PATH),
        repo_root=subject.REPO_ROOT,
        expected_cutoff_at="2026-08-10T06:00:00.000Z",
    )
    assert any("was not touched" in failure for failure in failures)
    assert "technical reference cutoff does not match journal coverage" in failures


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
    selected = activity["selected_records"][0]
    assert selected["epistemic_class"] == "operator-direction"
    assert selected["authority_owner"] == "operator"
    assert selected["may_promote"] is False


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


def test_publication_check_binds_complete_outgoing_branch_and_receipt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo, _ = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day)
    entry = repo / "mira" / "journal" / f"{day}.md"
    entry.write_bytes(body)
    parsed = subject.parse_markdown(body, day)
    registry = subject.default_registry()
    registry["entries"] = [
        {
            "journal_id": "MJ-20260809",
            "entry_date": day,
            "current_version_id": "MJ-20260809-v1",
            "current_path": f"mira/journal/{day}.md",
            "versions": [{
                "version_id": "MJ-20260809-v1",
                "content_sha256": parsed["content_sha256"],
                "approval": {"status": subject.AFFIRMATIVE_APPROVAL_STATUS, "publication_eligible": True},
            }],
        }
    ]
    subject.atomic_write_json(subject.REGISTRY_PATH, registry)
    outputs = {
        ("remote", "get-url", "origin"): "https://example.test/repo.git",
        ("rev-parse", "HEAD"): "a" * 40,
        ("rev-parse", "--verify", "origin/main"): "b" * 40,
        ("rev-list", "--reverse", "origin/main..HEAD"): "\n".join(["c" * 40, "a" * 40]),
        ("diff", "--name-only", "origin/main..HEAD", "--"): "mira/journal/2026-08-09.md\nmira/journal-registry.json",
    }
    monkeypatch.setattr(subject, "git_text", lambda *args: outputs[args])
    args = argparse.Namespace(remote="origin", branch="main", receipt=None)
    blocked = subject.publication_command(args)
    assert blocked["status"] == "blocked"
    assert blocked["outgoing_commit_count"] == 2
    assert blocked["human_sensitive_narrative_review_required"] is True
    receipt = tmp_path / "publication.json"
    expected_versions = [
        {"version_id": "MJ-20260809-v1", "content_sha256": parsed["content_sha256"]}
    ]
    scope_digest = subject.publication_scope_digest(
        "https://example.test/repo.git", "main", "a" * 40, expected_versions
    )
    statement = subject.publication_approval_statement(scope_digest)
    record_ref = "MR-" + subject.sha256_bytes(statement.encode("utf-8"))[:24]
    APPROVAL_ROWS[record_ref] = {
        "record_id": record_ref,
        "kind": "message",
        "role": "user",
        "timestamp": "2026-08-09T17:59:00Z",
        "content": [{"type": "text", "text": statement}],
    }
    receipt.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "destination_url": "https://example.test/repo.git",
                "branch": "main",
                "head_commit": "a" * 40,
                "journal_versions": expected_versions,
                "scope_digest": scope_digest,
                "authority_ref": SESSION,
                "record_ref": record_ref,
                "approved_at": "2026-08-09T18:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    args.receipt = receipt
    assert subject.publication_command(args)["status"] == "clear"


def test_generic_or_negated_text_cannot_approve_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, drafts = configure_repo(monkeypatch, tmp_path)
    body = prose("2026-08-09")
    draft = write_bundle(drafts, "2026-08-09", body, metadata("2026-08-09", body))
    args = action_args("2026-08-09", draft)
    APPROVAL_ROWS[args.approval_record_ref]["content"] = [
        {"type": "text", "text": "Do not approve this journal record."}
    ]
    with pytest.raises(subject.JournalError, match="exact digest-bound"):
        subject.approve_or_revise(args, revising=False)


def test_legacy_reference_backfill_preserves_prose_and_publication_boundary(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day)
    parsed = subject.parse_markdown(body, day)
    canonical = subject.entry_path(subject.parse_entry_date(day))
    canonical.write_bytes(body)
    registry = subject.default_registry()
    registry["entries"] = [{
        "journal_id": "MJ-20260809",
        "entry_date": day,
        "current_version_id": "MJ-20260809-v1",
        "current_path": "mira/journal/2026-08-09.md",
        "versions": [{
            "version_id": "MJ-20260809-v1",
            "version_number": 1,
            "title": parsed["title"],
            "content_sha256": parsed["content_sha256"],
            "word_count": parsed["word_count"],
            "coverage": {
                "start": "2026-08-09T06:00:00Z",
                "end": "2026-08-10T06:00:00Z",
                "as_of": "2026-08-09T18:00:00Z",
                "retrospective": False,
            },
            "approval": {
                "approved_by": "operator",
                "status": subject.LEGACY_HELD_STATUS,
                "publication_eligible": False,
            },
            "previous_version_digest": None,
        }],
    }]
    subject.atomic_write_json(subject.REGISTRY_PATH, registry)
    subject.atomic_write_text(subject.INDEX_PATH, subject.render_index(registry))
    reference = technical_reference(day, body, mode="retrospective-backfill")
    reference["cutoff_at"] = "2026-08-09T18:00:00Z"
    input_path = drafts / "legacy-reference.json"
    input_path.write_text(json.dumps(reference), encoding="utf-8")
    digest = subject.mira_journal_references.reference_digest(reference)
    statement = subject.reference_backfill_statement(reference["reference_id"], digest)
    record_id = "MR-" + digest[:24]
    APPROVAL_ROWS[record_id] = {
        "record_id": record_id,
        "kind": "message",
        "role": "user",
        "timestamp": "2026-08-09T18:00:00Z",
        "content": [{"type": "text", "text": statement}],
    }
    args = argparse.Namespace(
        version="MJ-20260809-v1",
        input=input_path,
        authority_ref=SESSION,
        approval_record_ref=record_id,
        approved_at="2026-08-09T17:59:00Z",
        check=True,
    )
    with pytest.raises(subject.JournalError, match="precedes its approval record"):
        subject.command_reference_backfill(args)
    args.approved_at = "2026-08-09T18:01:00Z"
    before = canonical.read_bytes()
    assert subject.command_reference_backfill(args)["status"] == "ready"
    assert "technical_reference" not in subject.load_registry()["entries"][0]["versions"][0]
    args.check = False
    result = subject.command_reference_backfill(args)
    assert result["status"] == "backfilled"
    assert canonical.read_bytes() == before
    stored = subject.load_registry()["entries"][0]["versions"][0]
    assert stored["approval"]["status"] == subject.LEGACY_HELD_STATUS
    assert stored["approval"]["publication_eligible"] is False
    assert (repo / stored["technical_reference"]["json_path"]).is_file()
    assert (repo / stored["technical_reference"]["markdown_path"]).is_file()


def test_context_pack_identity_and_derivation_are_verified() -> None:
    pack = context_pack()
    assert subject.validate_context_pack(pack) == []
    tampered = copy.deepcopy(pack)
    tampered["token_budget"] += 1
    assert "journal context pack identity mismatch" in subject.validate_context_pack(tampered)
    tampered = copy.deepcopy(pack)
    tampered["derivation_manifest"]["output_digest"] = "0" * 64
    assert "journal context pack deterministic derivation mismatch" in subject.validate_context_pack(tampered)

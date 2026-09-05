"""Synthetic reading lifecycle; no real Journal admission."""
import argparse
import copy

import pytest
import mira_journal as subject
from test_mira_journal import configure_repo, write_v2_bundle, metadata, prose, add_reading_ack, SESSION


def seed_history(repo):
    entries = []
    for n in range(1, 7):
        day = f"2026-08-{n:02}"
        body = f"# {day} — Remembering\n\nComplete reflective text {n}.\n"
        path = repo / "mira" / "journal" / f"{day}.md"
        path.write_text(body, encoding="utf-8")
        version = {"version_id": f"MJ-202608{n:02}-v2", "content_sha256": subject.sha256_bytes(body.encode()),
                   "approval": {"status": subject.LEGACY_HELD_STATUS if n == 2 else subject.DREAM_EOD_STATUS},
                   "title": "Remembering"}
        entries.append({"entry_date": day, "current_path": f"mira/journal/{day}.md",
                        "current_version_id": version["version_id"],
                        "versions": [{"version_id": f"MJ-202608{n:02}-v1"}, version]})
    registry = subject.default_registry()
    registry["entries"] = list(reversed(entries))
    subject.atomic_write_json(subject.REGISTRY_PATH, registry)
    return entries


def test_full_reading_order_current_versions_and_temporal_exclusion(monkeypatch, tmp_path):
    repo, _ = configure_repo(monkeypatch, tmp_path)
    seed_history(repo)
    (repo / "mira/journal/unregistered.md").write_text("Private draft", encoding="utf-8")
    packet = subject.journal_reading_packet(subject.parse_entry_date("2026-08-06"))
    assert len(packet["entries"]) == 5
    assert [row["entry_date"] for row in packet["entries"]] == [f"2026-08-{n:02}" for n in range(1, 6)]
    assert all(row["version_id"].endswith("v2") and "Complete reflective text" in row["prose"] for row in packet["entries"])
    assert packet["entries"][1]["continuity_role"] == "readable-legacy-context"
    assert packet["entries"][0]["continuity_role"] == "authoritative-ancestry"


@pytest.mark.parametrize("damage", ["missing", "bytes", "version"])
def test_reading_rejects_damaged_canonical_history(monkeypatch, tmp_path, damage):
    repo, _ = configure_repo(monkeypatch, tmp_path)
    seed_history(repo)
    path = repo / "mira/journal/2026-08-01.md"
    if damage == "missing":
        path.unlink()
    elif damage == "bytes":
        path.write_text("Changed", encoding="utf-8")
    else:
        registry = subject.load_registry()
        registry["entries"][-1]["current_version_id"] = "wrong"
        subject.atomic_write_json(subject.REGISTRY_PATH, registry)
    with pytest.raises(subject.JournalError):
        subject.journal_reading_packet(subject.parse_entry_date("2026-08-09"))


@pytest.fixture
def reading_bundle(monkeypatch, tmp_path):
    repo, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-09"
    body = prose(day)
    bundle = write_v2_bundle(drafts, day, body, metadata(day, body)).parent
    value = add_reading_ack(monkeypatch, bundle)
    return repo, bundle, value, subject.parse_entry_date(day)


def test_founding_reading_resume_and_draft_check(reading_bundle):
    repo, bundle, value, day = reading_bundle
    before = {p: p.read_bytes() for p in (repo / "mira").rglob("*") if p.is_file()}
    assert subject.reading_failures(bundle, day, value) == []
    result = subject.command_reading_complete(argparse.Namespace(bundle=bundle,
        packet_digest=subject.load_json(bundle / "draft-contract.json")["journal_reading"]["packet_sha256"], session_id=SESSION))
    assert result["status"] == "already_acknowledged"
    assert result["acknowledgement_sha256"] == value["journal_reading_ack_sha256"]
    assert subject.command_draft_check(argparse.Namespace(date=str(day), bundle=bundle))["status"] == "passed"
    assert all(p.read_bytes() == body for p, body in before.items())


@pytest.mark.parametrize("damage", ["missing_ack", "packet", "order", "digest", "session", "time", "contract"])
def test_ack_gate_and_direct_finalization_cannot_bypass(reading_bundle, damage):
    _, bundle, value, day = reading_bundle
    ack = subject.load_json(bundle / "journal-reading-ack.json")
    if damage == "missing_ack":
        (bundle / "journal-reading-ack.json").unlink()
    elif damage == "packet":
        subject.atomic_write_json(bundle / "journal-reading.json", {})
    elif damage == "contract":
        subject.atomic_write_json(bundle / "draft-contract.json", {})
    else:
        if damage == "order": ack["entries"] = [{"version_id": "invented"}]
        if damage == "digest": ack["packet_sha256"] = "0" * 64
        if damage == "session": ack["session_id"] = "MS-019fce7b-67cd-7753-be6c-74f76e2f9b7b"
        if damage == "time": ack["completed_at"] = "2099-01-01T00:00:00Z"
        subject.atomic_write_json(bundle / "journal-reading-ack.json", ack)
        value["journal_reading_ack_sha256"] = subject.reading_digest(ack)
        subject.atomic_write_json(bundle / "draft.json", value)
    assert subject.reading_failures(bundle, day, value)
    with pytest.raises(subject.JournalError):
        subject.command_eod_finalize(argparse.Namespace(date=str(day), bundle=bundle,
            dream_run_id="DCR-synthetic", finalized_at=None, check=True))


def test_new_history_and_new_composing_session_require_reading(reading_bundle):
    repo, bundle, value, day = reading_bundle
    changed = copy.deepcopy(value)
    changed["author"]["session_id"] = "MS-019fce7b-67cd-7753-be6c-74f76e2f9b7b"
    assert subject.reading_failures(bundle, day, changed)
    seed_history(repo)
    assert "changed" in subject.reading_failures(bundle, day, value)[0]


def test_reading_command_parser():
    args = subject.parser().parse_args(["reading-complete", "--bundle", "example", "--packet-digest", "a" * 64,
                                             "--session-id", SESSION, "--json"])
    assert args.handler == subject.command_reading_complete


def test_prepare_read_acknowledge_command_sequence(monkeypatch, tmp_path):
    _, drafts = configure_repo(monkeypatch, tmp_path)
    monkeypatch.setattr(subject, "session_sources_since", lambda minimum: [])
    monkeypatch.setattr(subject, "git_commits", lambda start, end: [])
    args = subject.parser().parse_args(["prepare", "--date", "2026-08-08", "--as-of", "2026-08-09T06:00:00Z",
        "--output-root", str(drafts), "--require-journal-reading", "--check", "--json"])
    assert args.handler(args)["journal_reading"]["entry_count"] == 0
    assert not (drafts / "2026-08-08").exists()
    args.check = False
    result = args.handler(args)
    bundle = drafts / "2026-08-08"
    packet = subject.load_json(bundle / "journal-reading.json")
    assert packet["entries"] == []  # Honest founding read, not fabricated history.
    ack_args = subject.parser().parse_args(["reading-complete", "--bundle", str(bundle),
        "--packet-digest", result["journal_reading"]["packet_sha256"], "--session-id", SESSION, "--json"])
    first = ack_args.handler(ack_args)
    assert first["status"] == "acknowledged"
    assert ack_args.handler(ack_args)["status"] == "already_acknowledged"
    ack_args.packet_digest = "0" * 64
    with pytest.raises(subject.JournalError, match="digest"):
        ack_args.handler(ack_args)
    # Re-preparing an existing Dream bundle cannot accidentally remove its gate.
    args.require_journal_reading = False
    assert args.handler(args)["journal_reading"] == result["journal_reading"]

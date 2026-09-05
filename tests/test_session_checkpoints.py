from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
from pathlib import Path

import pytest

import session_checkpoints as sc
from repository_paths import resolve_repository_path

SID = "MS-00000000-0000-0000-0000-000000000001"
START = datetime(2026, 9, 4, 6, tzinfo=timezone.utc)


def fixture(repo, *, text="day work", timestamp=None):
    row = {"record_id": "MR-" + "1" * 24, "timestamp": (timestamp or START).isoformat(),
           "kind": "message", "role": "user", "content": [{"type": "text", "text": text}]}
    body = gzip.compress(sc.encoded({"session_id": SID}) + sc.encoded(row), mtime=0)
    relative = "mira/continuity/captures/00000000-0000-0000-0000-000000000001/MC-" + "2" * 24 + ".jsonl.gz"
    path = repo / relative
    path.parent.mkdir(parents=True)
    path.write_bytes(body)
    cap = {"id": "MC-" + "2" * 24, "path": relative, "sha256": hashlib.sha256(body).hexdigest()}
    registry = {"sessions": [{"id": SID, "started_at": START.isoformat(),
        "last_observed_at": (START + timedelta(days=2)).isoformat(), "captures": [cap]}]}
    return registry, cap, row


def test_relocation_preserves_identity_and_rejects_changed_rollback_copy(tmp_path):
    registry, cap, _ = fixture(tmp_path)
    old = tmp_path / cap["path"]
    assert resolve_repository_path(tmp_path, cap["path"]) == old
    new = tmp_path / sc.TRANSCRIPTS / Path(cap["path"]).relative_to("mira/continuity/captures")
    sc.immutable(new, old.read_bytes())
    assert resolve_repository_path(tmp_path, cap["path"]) == new
    old.write_bytes(b"altered")
    with pytest.raises(ValueError, match="Conflicting"):
        resolve_repository_path(tmp_path, cap["path"])
    with pytest.raises(ValueError):
        resolve_repository_path(tmp_path, "mira/continuity/captures/../../outside")


def test_chunks_preserve_oversized_records_and_deduplicate_captures(tmp_path):
    registry, cap, row = fixture(tmp_path, text="word " * 10000)
    registry["sessions"][0]["captures"].append(cap)
    cp, chunks = sc.build(tmp_path, "2026-09-04", START, START + timedelta(days=1), START + timedelta(days=1), registry, chunk_chars=1000)
    assert cp["record_count"] == 1
    assert len(chunks) > 1
    restored = json.loads("".join(c["text"] for c in chunks))
    assert restored["record"] == row
    before = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*") if p.is_file())
    sc.publish(tmp_path, cp, chunks, check=True)
    assert before == sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*") if p.is_file())


def test_midnight_and_missing_capture_are_not_quiet_day(tmp_path):
    registry, cap, _ = fixture(tmp_path, timestamp=START + timedelta(days=1))
    cp, chunks = sc.build(tmp_path, "2026-09-04", START, START + timedelta(days=1), START + timedelta(days=1), registry)
    assert cp["record_count"] == 0 and not cp["gaps"]
    (tmp_path / cap["path"]).unlink()
    cp, _ = sc.build(tmp_path, "2026-09-04", START, START + timedelta(days=1), START + timedelta(days=1), registry)
    assert cp["coverage"] == "partial" and cp["gaps"]


def test_reading_bound_to_session_order_bytes_and_authorship(tmp_path):
    registry, _, _ = fixture(tmp_path, text="x" * 500)
    cp, chunks = sc.build(tmp_path, "2026-09-04", START, START + timedelta(days=1), START + timedelta(days=1), registry, chunk_chars=100)
    contract = sc.publish(tmp_path, cp, chunks)
    assert sc.publish(tmp_path, cp, chunks) == contract
    bundle = tmp_path / "bundle"
    sc.write_json(bundle / "draft-contract.json", {"session_reading": contract})
    with pytest.raises(ValueError, match="sequentially"):
        sc.acknowledge(tmp_path, bundle, SID, sc.digest(cp), [2])
    ack = sc.acknowledge(tmp_path, bundle, SID, sc.digest(cp), list(range(1, len(chunks) + 1)))
    metadata = {"author": {"session_id": SID}, "session_checkpoint_sha256": sc.digest(cp),
        "session_reading_ack_sha256": ack["acknowledgement_sha256"],
        "authored_at": datetime.now(timezone.utc).isoformat()}
    assert not sc.reading_failures(tmp_path, bundle, metadata)
    metadata["author"]["session_id"] = "MS-00000000-0000-0000-0000-000000000002"
    assert sc.reading_failures(tmp_path, bundle, metadata)
    path = tmp_path / contract["checkpoint_path"]
    (path.parent / "chunk-00001.json").write_text("{}")
    with pytest.raises(ValueError, match="chunk changed"):
        sc.checked(tmp_path, contract)


def test_changed_cutoff_adds_version_and_retains_previous(tmp_path):
    registry, _, _ = fixture(tmp_path)
    cp, chunks = sc.build(tmp_path, "2026-09-04", START, START + timedelta(hours=1), START + timedelta(days=1), registry)
    first = sc.publish(tmp_path, cp, chunks)
    cp2, chunks2 = sc.build(tmp_path, "2026-09-04", START, START + timedelta(hours=2), START + timedelta(days=1), registry)
    second = sc.publish(tmp_path, cp2, chunks2)
    assert first["checkpoint_path"] != second["checkpoint_path"]
    sc.checked(tmp_path, first)
    sc.checked(tmp_path, second)


def test_path_exception_does_not_allow_other_private_state(tmp_path):
    with pytest.raises(ValueError):
        sc.private_child(tmp_path, "archive/other/private.sqlite3")
    with pytest.raises(ValueError):
        sc.private_child(tmp_path, sc.TRANSCRIPTS + "/../../../escape")


def test_recovery_retains_old_snapshot_and_checks_objects_before_restore(tmp_path):
    repo = tmp_path / "repo"
    registry, cap, _ = fixture(repo)
    sc.write_json(repo / "mira/continuity/session-registry.json", registry)
    target = repo / sc.TRANSCRIPTS / "one.jsonl.gz"
    sc.immutable(target, (repo / cap["path"]).read_bytes())
    backup_root = tmp_path / "backup"
    first = sc.backup(repo, backup_root)
    assert sc.backup(repo, backup_root)["snapshot_sha256"] == first["snapshot_sha256"]
    result = sc.restore(backup_root, first["snapshot_sha256"], tmp_path / "restore")
    assert result["verified_files"] == 2
    target.unlink()
    second = sc.backup(repo, backup_root)
    assert second["snapshot_sha256"] != first["snapshot_sha256"]
    assert (backup_root / "snapshots" / (first["snapshot_sha256"] + ".json")).exists()
    manifest = sc.load(backup_root / "snapshots" / (first["snapshot_sha256"] + ".json"))
    (backup_root / "objects" / manifest["entries"][0]["sha256"]).write_bytes(b"bad")
    with pytest.raises(ValueError, match="hash mismatch"):
        sc.restore(backup_root, first["snapshot_sha256"], tmp_path / "failed-restore")
    assert not (tmp_path / "failed-restore").exists()


def test_continuation_segments_preserved_and_overlap_rejected(tmp_path):
    root = tmp_path / "raw"
    root.mkdir()
    def source(name, start, end, text):
        rows = [{"type": "session_meta", "timestamp": start, "payload": {"id": SID[3:], "cwd": str(tmp_path), "timestamp": start}},
                {"type": "event_msg", "timestamp": end, "payload": {"type": "user_message", "message": text}}]
        (root / name).write_bytes(b"".join(sc.encoded(row) for row in rows))
    source("one.jsonl", "2026-09-04T10:00:00Z", "2026-09-04T11:00:00Z", "first")
    source("two.jsonl", "2026-09-04T12:00:00Z", "2026-09-04T13:00:00Z", "second")
    assert len(sc.sources(tmp_path, [root])) == 2
    before = sorted(p for p in tmp_path.rglob("*") if p.is_file())
    plan, outputs = sc.preserve(tmp_path, sc.sources(tmp_path, [root]), check=True)
    assert len(plan["sessions"]) == 1 and len(outputs) == 2
    assert before == sorted(p for p in tmp_path.rglob("*") if p.is_file())
    plan, _ = sc.preserve(tmp_path, sc.sources(tmp_path, [root]))
    assert len(plan["sessions"][0]["captures"]) == 2
    repeated, outputs = sc.preserve(tmp_path, sc.sources(tmp_path, [root]), check=True)
    assert repeated == plan and not outputs
    source("two.jsonl", "2026-09-04T10:30:00Z", "2026-09-04T13:00:00Z", "conflict")
    with pytest.raises(ValueError, match="Conflicting overlapping"):
        sc.sources(tmp_path, [root])


def test_day_bounds_follow_dst():
    import mira_journal
    from datetime import date
    start, end = mira_journal.day_bounds(date(2026, 3, 8))
    assert (end - start).total_seconds() == 23 * 3600
    start, end = mira_journal.day_bounds(date(2026, 11, 1))
    assert (end - start).total_seconds() == 25 * 3600


def test_publication_blocks_private_payloads():
    from publication_validation import route_path, RoutingError
    with pytest.raises(RoutingError, match="cannot be admitted"):
        route_path(sc.TRANSCRIPTS + "/index.json")


def test_journal_prepares_frozen_reading_and_resumes_without_raw_sources(monkeypatch, tmp_path):
    import mira_journal as journal
    import mira_continuity as continuity
    from test_mira_journal import configure_repo
    repo, drafts = configure_repo(monkeypatch, tmp_path)
    raw = tmp_path / "raw"
    raw.mkdir()
    rows = [{"type": "session_meta", "timestamp": "2026-09-04T12:00:00Z",
             "payload": {"id": SID[3:], "cwd": str(repo), "timestamp": "2026-09-04T12:00:00Z"}},
            {"type": "response_item", "timestamp": "2026-09-04T12:01:00Z",
             "payload": {"type": "message", "role": "user", "content": [
                 {"type": "input_text", "text": "Read all of this " * 2000}]}}]
    (raw / "source.jsonl").write_bytes(b"".join(sc.encoded(r) for r in rows))
    monkeypatch.setattr(continuity, "default_source_roots", lambda: [raw])
    monkeypatch.setattr(journal, "git_commits", lambda *args: [])
    args = journal.parser().parse_args(["prepare", "--date", "2026-09-04", "--output-root", str(drafts),
        "--require-session-reading", "--require-journal-reading", "--json", "--check"])
    before = {str(p): p.read_bytes() for p in repo.rglob("*") if p.is_file()}
    projected = journal.command_prepare(args)
    assert {str(p): p.read_bytes() for p in repo.rglob("*") if p.is_file()} == before
    args.check = False
    prepared = journal.command_prepare(args)
    assert prepared["session_reading"] == projected["session_reading"]
    bundle = drafts / "2026-09-04"
    pack = sc.load(bundle / "context-pack.json")
    assert not journal.validate_context_pack(pack)
    assert not journal.validate_composition_brief(sc.load(bundle / "composition-brief.json"), pack=pack)
    assert prepared["session_reading"]["chunk_count"] > 1
    (raw / "source.jsonl").unlink()
    assert journal.command_prepare(args)["status"] == "already_prepared"
    assert sc.load(bundle / "draft-contract.json")["session_reading"] == prepared["session_reading"]


def test_parent_groups_nested_missing_conflicting_and_inactive():
    registry = {"sessions": [{"id": s, "source_kind": "vscode" if s == "root" else "subagent"}
                             for s in ["root", "child", "nested", "missing", "conflict", "cycle"]]}
    lineage = {"observations": [{"session_id": s, "parent_ids": p} for s, p in [
        ("child", ["root"]), ("nested", ["child"]), ("conflict", ["root", "child"]),
        ("cycle", ["cycle"])]]}
    active = {"child", "nested", "missing", "conflict", "cycle"}
    result = sc.conversation_groups(registry, active, lineage)
    assert result["groups"] == [{"parent_session_id": "root", "parent_active": False,
                                 "session_ids": ["child", "nested"]}]
    assert {r["reason"] for r in result["unresolved"]} == {
        "missing-parent", "conflicting-parents", "ancestry-cycle"}
    covered = [s for g in result["groups"] for s in g["session_ids"]] + [r["session_id"] for r in result["unresolved"]]
    assert len(covered) == len(set(covered)) == len(active)
    assert set(covered) == active
    assert sc.conversation_groups(registry, set(reversed(sorted(active))), lineage) == result


def test_grouping_freezes_without_changing_records(tmp_path):
    registry, cap, row = fixture(tmp_path)
    registry["sessions"][0]["source_kind"] = "vscode"
    cp, chunks = sc.build(tmp_path, "2026-09-04", START, START + timedelta(days=1), START + timedelta(days=1), registry)
    old = sc.publish(tmp_path, cp, chunks)
    original_chunks = sc.encoded(chunks)
    cp["conversation_grouping"] = sc.conversation_groups(registry, {SID}, {"observations": []})
    new = sc.publish(tmp_path, cp, chunks)
    assert old != new
    assert sc.encoded(chunks) == original_chunks
    sc.write_json(tmp_path / sc.LINEAGE, {"observations": [{"later": "change"}]})
    assert sc.checked(tmp_path, new)[0]["conversation_grouping"] == cp["conversation_grouping"]
    assert "conversation_grouping" not in sc.checked(tmp_path, old)[0]


def test_lineage_retains_conflicting_observations_without_rewriting_capture(tmp_path):
    from types import SimpleNamespace
    raw = tmp_path / "raw.jsonl"
    def source(parent):
        raw.write_bytes(sc.encoded({"type": "session_meta", "timestamp": START.isoformat(),
            "payload": {"id": SID[3:], "parent_thread_id": parent}}))
        return SimpleNamespace(session_id=SID, path=raw)
    first = sc.lineage_index(tmp_path, [source("00000000-0000-0000-0000-000000000002")])
    sc.write_json(tmp_path / sc.LINEAGE, first)
    second = sc.lineage_index(tmp_path, [source("00000000-0000-0000-0000-000000000003")])
    assert len(second["observations"]) == 2
    assert first["observations"][0] in second["observations"]
    assert sc.lineage_index(tmp_path, []) == first
    result = sc.conversation_groups({"sessions": [{"id": SID, "source_kind": "subagent"}]}, {SID}, second)
    assert result["unresolved"][0]["reason"] == "conflicting-parents"

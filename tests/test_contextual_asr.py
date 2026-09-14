"""Behavioral guarantees for private agent-authored text derivatives."""
import copy
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import contextual_asr as asr
import archive_repair


@pytest.fixture
def case(tmp_path):
    repo = tmp_path / "repo"
    source = repo / "archive/sources/geopolitics/sources/day/source.md"
    source.parent.mkdir(parents=True)
    body = ("---\r\ntitle: Frozen\r\n---\r\n# Frozen\r\n## Transcript\r\n"
            "[4:28] >> Ships cannot export through the state of Hormuz.\r\n"
            "[4:40] Baband costs $999 billion; not confirmed. Café.\r\n").encode()
    source.write_bytes(body)
    manifest = source.parents[2] / "source-manifest.json"
    manifest.write_text(json.dumps({"sources": [{"local_path": str(source.relative_to(repo)),
                                               "source_identity": "youtube:12345678901", "title": "Shipping", "voice_slugs": ["Freeman"]}]}))
    memory = asr.Memory(repo, tmp_path / "private")
    prepared = memory.prepare([source])
    original = "state of Hormuz"
    start = body.index(original.encode())
    context = body[body.index(b"[4:28]"):body.index(b"[4:40]")].decode()
    packet = {"schema_version": 1, "prepared_id": prepared["prepared_id"], "model": "test-agent",
              "session": "test-session", "created_at": "2026-09-13T12:00:00+00:00",
              "coverage": [{"source_sha256": asr.digest(body), "read_spans": [[0, len(body)]]}],
              "corrections": [{"source": 0, "source_sha256": asr.digest(body), "status": "accepted",
                               "start": start, "end": start + len(original), "original": original,
                               "replacement": "Strait of Hormuz", "context": context,
                               "rationale": "Ships exporting through a named passage select Strait.",
                               "confidence": "high", "example_ids": [], "reviewed_in_context": True}]}
    return memory, source, body, packet


def test_exact_bytes_idempotence_and_readonly_check(case):
    memory, source, body, packet = case
    result, outputs = memory.check(packet)
    assert not (memory.root / "batches").exists()
    assert outputs["corrected-0.txt"] == body.replace(b"state of Hormuz", b"Strait of Hormuz")
    assert result["sources"][0]["reading_complete"]
    first = memory.save(packet)
    second = memory.save(packet)
    assert first["batch_id"] == second["batch_id"] and second["reused"]
    assert source.read_bytes() == body
    assert memory.report(first["batch_id"])["corrections"][0]["rationale"]


@pytest.mark.parametrize("mutation", ["hash", "original", "overlap", "unknown-example", "unselected", "outside-coverage", "context", "confidence", "wrapper", "timestamp"])
def test_invalid_edits_fail_closed(case, mutation):
    memory, source, body, packet = case
    c = packet["corrections"][0]
    if mutation == "hash": c["source_sha256"] = "0" * 64
    elif mutation == "original": c["original"] = "other"
    elif mutation == "overlap": packet["corrections"].append(copy.deepcopy(c))
    elif mutation == "unknown-example": c["example_ids"] = ["unknown:0"]
    elif mutation == "unselected": c["source"] = 10
    elif mutation == "outside-coverage": packet["coverage"][0].update(read_spans=[[0, 5]], remaining="All other bytes")
    elif mutation == "context": c["context"] = "Invented evidence"
    elif mutation == "confidence": c["confidence"] = "low"
    else:
        original = "Frozen" if mutation == "wrapper" else "28"
        start = body.index(original.encode())
        c.update(start=start, end=start+len(original), original=original, replacement="Changed", context=body.decode())
    with pytest.raises(ValueError): memory.save(packet)
    assert source.read_bytes() == body
    assert not list((memory.root / "batches").glob("*"))


def test_stale_and_changed_sources(case):
    memory, source, body, packet = case
    source.write_bytes(body + b"New source version\r\n")
    with pytest.raises(ValueError, match="changed"): memory.save(packet)
    assert memory.prepare([source])["prepared_id"] != packet["prepared_id"]


def test_partial_reading_retains_ambiguity_and_claims(case):
    memory, source, body, packet = case
    start = body.index(b"[4:28]")
    packet["coverage"][0].update(read_spans=[[start, len(body)]], remaining="Wrapper unread; opening absent in supplied source.")
    c = copy.deepcopy(packet["corrections"][0])
    pos = body.index(b"Baband")
    c.update(start=pos, end=pos+6, original="Baband", replacement=None, status="unresolved",
             context=body[body.index(b"[4:40]"):].decode(), confidence="low", rationale="No locally selected expansion.")
    packet["corrections"].append(c)
    result = memory.save(packet)
    output = (Path(result["path"]) / "corrected-0.txt").read_bytes()
    assert b"Baband costs $999 billion; not confirmed. Caf\xc3\xa9." in output
    assert b"Ships cannot" in output
    assert not result["sources"][0]["reading_complete"]
    assert result["sources"][0]["unresolved"] == 1


def test_retrieval_deduplicates_and_retains_negative_history(case):
    memory, source, body, packet = case
    one = memory.save(packet)
    packet["session"] = "second-review"
    two = memory.save(packet)
    found = memory.search("state of Hormuz", speaker="Freeman")
    assert len(found["suggestions"]) == 1
    assert len(found["suggestions"][0]["example_ids"]) == 2
    cid = one["batch_id"] + ":0"
    memory.review(cid, "rejected", "Counter-context found", "agent", "review")
    found = memory.search("state of Hormuz")
    assert len(found["suggestions"]) == 1 and len(found["alternatives"]) == 1
    assert found["alternatives"][0]["review_reason"] == "Counter-context found"
    memory.review(cid, "superseded", "Reconsidered", "agent", "review", two["batch_id"] + ":0")
    assert memory.examples()[cid]["review_status"] == "superseded"
    assert len(list((memory.root / "reviews").iterdir())) == 2


def test_reuse_requires_fresh_context_not_substitution(case):
    memory, source, body, packet = case
    first = memory.save(packet)
    c = packet["corrections"][0]
    c.update(status="rejected", rationale="Example considered; no edit authorized by frequency.", example_ids=[first["batch_id"] + ":0"])
    packet["session"] = "second"
    result, outputs = memory.check(packet)
    assert outputs["corrected-0.txt"] == body
    assert result["sources"][0]["rejected"] == 1


def test_workspace_isolation(case, tmp_path):
    memory, source, body, packet = case
    memory.save(packet)
    other = asr.Memory(tmp_path / "another-repo", tmp_path / "private")
    assert other.root != memory.root
    assert other.search("state of Hormuz")["suggestions"] == []
    with pytest.raises(ValueError): asr.Memory(memory.repo, memory.repo / "private")


def test_interrupted_publication_is_invisible_and_retryable(case, monkeypatch):
    memory, source, body, packet = case
    rename = Path.rename
    def fail(self, target):
        if self.name.startswith(".pending-"): raise OSError("Injected interruption")
        return rename(self, target)
    with monkeypatch.context() as m:
        m.setattr(Path, "rename", fail)
        with pytest.raises(OSError): memory.save(packet)
    assert list(memory.batches()) == []
    orphan = memory.root / "batches/.pending-crash"
    orphan.mkdir()
    (orphan / "report.json").write_text("partial")
    assert list(memory.batches()) == []
    assert not memory.save(packet)["reused"]


def test_corrupt_derivative_detected(case):
    memory, source, body, packet = case
    result = memory.save(packet)
    (Path(result["path"]) / "corrected-0.txt").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="integrity"): memory.report(result["batch_id"])


def test_raw_capture_requires_queue_binding(case, tmp_path):
    memory, source, body, packet = case
    raw = tmp_path / "raw.txt"
    raw.write_bytes(b"Video ID: 12345678901\n\n[0:01] Raw captions\n")
    with pytest.raises(ValueError, match="queue binding"): memory.prepare([raw])
    queue = memory.repo / "geopolitics/work/capture/youtube/day.jsonl"
    queue.parent.mkdir(parents=True)
    queue.write_text(json.dumps({"source_identity": "youtube:12345678901", "transcript_path": str(raw)}) + "\n")
    prepared = memory.prepare([raw])
    assert prepared["sources"][0]["kind"] == "raw-capture-of-landed-source"


def test_front_door_dispatch(monkeypatch):
    received = []
    monkeypatch.setattr(asr, "main", lambda args: received.extend(args) or 0)
    assert archive_repair.main(["contextual", "search", "--wording", "Hormuz"]) == 0
    assert received == ["search", "--wording", "Hormuz"]


def test_unreadable_history_is_not_empty(case, monkeypatch):
    memory, _, _, _ = case
    original = Path.iterdir
    def denied(path):
        if path == memory.root / "batches": raise PermissionError("Private history denied")
        return original(path)
    monkeypatch.setattr(Path, "iterdir", denied)
    with pytest.raises(PermissionError): memory.search("Hormuz")


def test_no_external_or_audio_process_and_no_source_mutation(case, monkeypatch):
    import socket
    import subprocess
    memory, source, body, packet = case
    def forbidden(*args, **kwargs):
        pytest.fail("Contextual memory must not invoke external services or audio tools")
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    result = memory.save(packet)
    memory.review(result["batch_id"] + ":0", "confirmed", "Context reread", "agent", "session")
    assert memory.report(result["batch_id"])["corrections"][0]["review_status"] == "confirmed"
    assert source.read_bytes() == body


def test_completion_receipt_detects_report_corruption(case):
    memory, _, _, packet = case
    result = memory.save(packet)
    path = Path(result["path"]) / "report.json"
    report = asr.read(path)
    report["sources"][0]["reading_complete"] = False
    path.write_bytes(asr.encoded(report))
    with pytest.raises(ValueError, match="completion integrity"): memory.report(result["batch_id"])

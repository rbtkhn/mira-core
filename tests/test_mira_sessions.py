from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import archive as archive_module
import mira_sessions
from archive_store import ArtifactStore, RecordInput, ingest_record


BOUNDARY = mira_sessions.AUTHORITY_BOUNDARY


def write_continuity(repo: Path, message: str = "A short source message with no reusable memorial phrasing.") -> tuple[str, str, str]:
    session_id = "MS-" + "a" * 24
    capture_id = "MC-" + "b" * 24
    record_id = "MR-" + "c" * 24
    body = gzip.compress((json.dumps({"record_id": record_id, "kind": "message", "role": "user", "content": [{"type": "text", "text": message}]}) + "\n").encode())
    path = repo / "mira" / "continuity" / "captures" / "capture.jsonl.gz"
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(body)
    registry = {"sessions": [{"id": session_id, "started_at": "2026-08-18T01:00:00Z", "captures": [{"id": capture_id, "path": "mira/continuity/captures/capture.jsonl.gz", "sha256": hashlib.sha256(body).hexdigest()}]}]}
    (path.parent.parent / "session-registry.json").write_text(json.dumps(registry), encoding="utf-8")
    return session_id, capture_id, record_id


def markdown() -> str:
    return "# Memorial\n\n" + "\n\n".join(f"## {heading}\n\nBounded reflective paraphrase." for heading in mira_sessions.HEADINGS) + "\n"


def pair(repo: Path, *, version: int = 1, previous=None, source_message: str | None = None) -> tuple[Path, Path, str]:
    session_id, capture_id, record_id = write_continuity(repo, source_message or "A short source message with no reusable memorial phrasing.")
    stem = f"2026-08-18-aaaaaaaa-reflection-v{version}"
    md = repo / "draft" / f"{stem}.md"; js = repo / "draft" / f"{stem}.json"; md.parent.mkdir(exist_ok=True)
    md.write_text(markdown(), encoding="utf-8")
    authority = "Admit this memorial version."
    sidecar = {
        "schema_version": 1, "memorial_id": "MSM-reflection", "version_id": f"MSMV-reflection-v{version}", "version": version,
        "status": "admitted", "session_id": session_id, "capture_refs": [capture_id], "record_refs": [record_id],
        "markdown_path": f"archive/sessions/{md.name}", "markdown_sha256": hashlib.sha256(md.read_bytes()).hexdigest(),
        "entry_date": "2026-08-18", "admitted_at": "2026-08-18T02:00:00Z", "evidence_class": "session-memorial-interpretation",
        "activation_posture": "inactive", "authority_boundary": BOUNDARY, "significance_reasons": ["method-change"],
        "retention_reason": "The operator chose to preserve the method change.", "decision_attribution": [{"actor": "joint", "summary": "The method changed."}],
        "producer": {"kind": "model", "runtime": "test-runtime"}, "reopening_conditions": ["A related correction appears."],
        "counter_memory_refs": [], "omissions": "Routine implementation detail and private material are omitted.",
        "manual_privacy_review": {"completed": True, "reviewer": "operator"},
        "operator_command_receipt": {"record_ref": record_id, "sha256": hashlib.sha256(authority.encode()).hexdigest()}, "previous_version": previous,
    }
    js.write_text(json.dumps(sidecar), encoding="utf-8")
    return md, js, authority


def test_valid_canonical_pair_and_missing_capture_fail_closed(tmp_path: Path) -> None:
    md, js, _ = pair(tmp_path)
    assert mira_sessions.validate_pair(md, js, repo_root=tmp_path)["status"] == "passed"
    sidecar = json.loads(js.read_text()); sidecar["capture_refs"] = ["MC-" + "d" * 24]; js.write_text(json.dumps(sidecar))
    result = mira_sessions.validate_pair(md, js, repo_root=tmp_path)
    assert result["status"] == "failed"
    assert any("missing Continuity capture" in item for item in result["failures"])


@pytest.mark.parametrize("unsafe", ["password: hunter2", "person@example.com", "C:\\Users\\name\\private.txt", "user: copied turn"])
def test_privacy_scan_rejects_sensitive_shapes(tmp_path: Path, unsafe: str) -> None:
    md, js, _ = pair(tmp_path); md.write_text(markdown() + unsafe, encoding="utf-8")
    sidecar = json.loads(js.read_text()); sidecar["markdown_sha256"] = hashlib.sha256(md.read_bytes()).hexdigest(); js.write_text(json.dumps(sidecar))
    assert mira_sessions.validate_pair(md, js, repo_root=tmp_path)["status"] == "failed"


def test_substantial_capture_overlap_is_rejected(tmp_path: Path) -> None:
    copied = " ".join(f"distinctword{index}" for index in range(24))
    md, js, _ = pair(tmp_path, source_message=copied); md.write_text(markdown() + copied, encoding="utf-8")
    sidecar = json.loads(js.read_text()); sidecar["markdown_sha256"] = hashlib.sha256(md.read_bytes()).hexdigest(); js.write_text(json.dumps(sidecar))
    result = mira_sessions.validate_pair(md, js, repo_root=tmp_path)
    assert "substantial copied-message overlap detected" in result["failures"]


def test_pending_pair_has_no_canonical_references_and_check_does_not_write(tmp_path: Path) -> None:
    md, js, _ = pair(tmp_path); sidecar = json.loads(js.read_text())
    sidecar.update({"status": "pending", "source_thread_id": "thread-local", "session_id": None, "capture_refs": [], "record_refs": [], "markdown_path": None})
    js.write_text(json.dumps(sidecar)); output = tmp_path.parent / f"{tmp_path.name}-state" / "pending"
    original_root = mira_sessions.REPO_ROOT; mira_sessions.REPO_ROOT = tmp_path
    try: result = mira_sessions.pending_command(SimpleNamespace(markdown=md, sidecar=js, output_root=output, check=True))
    finally: mira_sessions.REPO_ROOT = original_root
    assert result["status"] == "ready" and not output.exists()


def test_archive_discovery_is_explicit_only_and_preserves_inactive_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    md, js, _ = pair(tmp_path); shelf = tmp_path / "archive" / "sessions"; shelf.mkdir(parents=True)
    target_md = shelf / md.name; target_js = shelf / js.name; target_md.write_bytes(md.read_bytes()); target_js.write_bytes(js.read_bytes())
    sidecar = json.loads(target_js.read_text()); entry = {"version": 1, "version_id": sidecar["version_id"], "markdown_path": f"archive/sessions/{md.name}", "sidecar_path": f"archive/sessions/{js.name}", "markdown_sha256": sidecar["markdown_sha256"], "sidecar_sha256": hashlib.sha256(target_js.read_bytes()).hexdigest()}
    (shelf / "registry.json").write_text(json.dumps({"memorials": [{"memorial_id": sidecar["memorial_id"], "session_id": sidecar["session_id"], "versions": [entry]}]}))
    collection = {"id": "mira-session-memorials", "kind": "mira-session-memorial-registry", "registry_path": "archive/sessions/registry.json", "authority_owner": "archive/sessions/registry.json", "evidence_class": "session-memorial-interpretation", "retrieval_policy": "explicit-only"}
    monkeypatch.setattr(archive_module, "REPO_ROOT", tmp_path)
    record, _ = list(archive_module.discover_session_memorials(collection))[0]
    assert record.metadata["activation_posture"] == "inactive" and record.metadata["may_promote"] is False
    monkeypatch.setattr(archive_module, "collection_map", lambda: {"ordinary": {"id": "ordinary"}, "mira-session-memorials": collection})
    assert [row["id"] for row in archive_module.selected_collections([])] == ["ordinary"]


def test_admission_is_deterministic_rejects_overwrite_and_preserves_v1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    shelf = tmp_path / "archive" / "sessions"; shelf.mkdir(parents=True)
    registry = shelf / "registry.json"
    registry.write_text(json.dumps({"schema_version": 1, "collection_id": "mira-session-memorials", "memorials": []}))
    monkeypatch.setattr(mira_sessions, "REPO_ROOT", tmp_path); monkeypatch.setattr(mira_sessions, "SHELF", shelf); monkeypatch.setattr(mira_sessions, "REGISTRY", registry)
    md1, js1, authority = pair(tmp_path)
    args = SimpleNamespace(markdown=md1, sidecar=js1, authority_statement=authority, check=True)
    assert mira_sessions.admit_command(args)["status"] == "ready" and not (shelf / md1.name).exists()
    args.check = False; assert mira_sessions.admit_command(args)["status"] == "admitted"
    with pytest.raises(mira_sessions.MemorialError, match="version"):
        mira_sessions.admit_command(args)
    registry_v1 = json.loads(registry.read_text()); previous = {"version_id": "MSMV-reflection-v1", "sidecar_sha256": registry_v1["memorials"][0]["versions"][0]["sidecar_sha256"]}
    md2, js2, authority2 = pair(tmp_path, version=2, previous=previous)
    assert mira_sessions.admit_command(SimpleNamespace(markdown=md2, sidecar=js2, authority_statement=authority2, check=False))["status"] == "admitted"
    assert (shelf / md1.name).is_file() and (shelf / md2.name).is_file()
    assert [item["version"] for item in json.loads(registry.read_text())["memorials"][0]["versions"]] == [1, 2]


def test_archive_lineage_links_capture_and_superseded_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    session_id, capture_id, record_id = write_continuity(tmp_path)
    shelf = tmp_path / "archive" / "sessions"; shelf.mkdir(parents=True); versions = []
    previous = None
    for number in (1, 2):
        md, js, _ = pair(tmp_path, version=number, previous=previous)
        target_md, target_js = shelf / md.name, shelf / js.name; target_md.write_bytes(md.read_bytes()); target_js.write_bytes(js.read_bytes())
        entry = {"version": number, "version_id": f"MSMV-reflection-v{number}", "markdown_path": f"archive/sessions/{md.name}", "sidecar_path": f"archive/sessions/{js.name}", "markdown_sha256": hashlib.sha256(md.read_bytes()).hexdigest(), "sidecar_sha256": hashlib.sha256(js.read_bytes()).hexdigest()}
        versions.append(entry); previous = {"version_id": entry["version_id"], "sidecar_sha256": entry["sidecar_sha256"]}
    registry = {"memorials": [{"memorial_id": "MSM-reflection", "session_id": session_id, "versions": versions}]}
    (shelf / "registry.json").write_text(json.dumps(registry)); collection = {"id": "mira-session-memorials", "registry_path": "archive/sessions/registry.json"}
    archive = ArtifactStore(tmp_path.parent / f"{tmp_path.name}-state" / "archive", tmp_path, create=True); monkeypatch.setattr(archive_module, "REPO_ROOT", tmp_path)
    capture_path = tmp_path / "mira" / "continuity" / "captures" / "capture.jsonl.gz"
    with archive.connect(create=True) as connection:
        ingest_record(connection, archive, RecordInput(capture_id, "session-capture", "capture", "mira-continuity", "continuity", "continuity-evidence", "agent-session", session_id, "2026-08-18T01:00:00Z", None, None, {}, ""), capture_path.read_bytes())
        for number in (1, 2):
            ingest_record(connection, archive, RecordInput(f"MSMV-reflection-v{number}", "session-memorial", f"memorial-{number}", "mira-session-memorials", "registry", "session-memorial-interpretation", "model", "test", "2026-08-18T02:00:00Z", None, None, {}, ""), f"v{number}".encode())
        assert archive_module.add_session_memorial_lineage(connection, collection) == 3
        assert {row[0] for row in connection.execute("SELECT relation_type FROM edges")} == {"derived_from", "supersedes"}

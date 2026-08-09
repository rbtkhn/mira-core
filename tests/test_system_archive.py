from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import system_archive
from system_archive_store import ArchiveError, ArtifactStore, RecordInput, add_edge, catalog_counts, ingest_record, safe_logical_path, verify_derivation_acyclic


def record(path: str = "collection/source.md", observed: str = "2026-01-02T00:00:00Z") -> RecordInput:
    return RecordInput("REC-001", "source", path, "test-collection", "test-manifest.json", "test-source", "import-process", "test-import", observed, "2026-01-01T00:00:00Z", None, {"title": "Test"}, "A maritime settlement and contrary escalation evidence.")


def test_deterministic_object_round_trip(tmp_path: Path) -> None:
    repo = tmp_path / "repo"; repo.mkdir(); archive = ArtifactStore(tmp_path / "external", repo, create=True); body = "Mira remembers π.\n".encode()
    digest, size = archive.put_object(body); encoded = archive.object_path(digest).read_bytes()
    assert archive.put_object(body) == (digest, size)
    assert archive.object_path(digest).read_bytes() == encoded
    assert archive.get_object(digest, expected_size=len(body)) == body


def test_immutable_record_versioning(tmp_path: Path) -> None:
    repo = tmp_path / "repo"; repo.mkdir(); archive = ArtifactStore(tmp_path / "external", repo, create=True)
    with archive.connect(create=True) as connection:
        assert ingest_record(connection, archive, record(), b"first")[:2] == (1, True)
        assert ingest_record(connection, archive, record(), b"first")[:2] == (1, False)
        assert ingest_record(connection, archive, record(), b"second")[:2] == (2, True)
        connection.commit()
        assert catalog_counts(connection) == {"objects": 2, "records": 2, "active_paths": 1, "events": 2, "edges": 1}
        with pytest.raises(sqlite3.IntegrityError, match="records are immutable"):
            connection.execute("UPDATE records SET lifecycle_state='changed'")


def test_path_and_store_boundaries(tmp_path: Path) -> None:
    for value in ("../escape", "/absolute", "collection/../escape"):
        with pytest.raises(ArchiveError): safe_logical_path(value)
    repo = tmp_path / "repo"; repo.mkdir()
    with pytest.raises(ArchiveError, match="outside the repository"): ArtifactStore(repo / "data", repo, create=True)


def test_as_of_search_and_derivation_cycle(tmp_path: Path) -> None:
    repo = tmp_path / "repo"; repo.mkdir(); archive = ArtifactStore(tmp_path / "external", repo, create=True)
    with archive.connect(create=True) as connection:
        ingest_record(connection, archive, record("collection/early.md"), b"early")
        later = RecordInput(**{**record("collection/later.md", "2026-03-01T00:00:00Z").__dict__, "record_id": "REC-002"})
        ingest_record(connection, archive, later, b"later"); connection.commit()
        rows = system_archive.search_rows(connection, query="maritime settlement", collections=["test-collection"], as_of="2026-02-01T00:00:00Z", limit=10)
        assert [row["record_id"] for row in rows] == ["REC-001"]
        add_edge(connection, source=("REC-001", 1), target=("REC-002", 1), relation_type="derived_from")
        add_edge(connection, source=("REC-002", 1), target=("REC-001", 1), relation_type="derived_from")
        assert verify_derivation_acyclic(connection)


def test_context_is_deterministic_and_replay_is_nonexecuting(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "repo"; repo.mkdir(); archive_root = tmp_path / "archive"; output_root = tmp_path / "outputs"; output_root.mkdir()
    archive = ArtifactStore(archive_root, repo, create=True)
    with archive.connect(create=True) as connection: ingest_record(connection, archive, record(), b"body"); connection.commit()
    task = tmp_path / "task.json"; task.write_text(json.dumps({"schema_version": 1, "task_id": "T", "query": "maritime settlement", "success_criteria": ["cite"], "collections": ["test-collection"]}), encoding="utf-8")
    monkeypatch.setattr(system_archive, "REPO_ROOT", repo); monkeypatch.setenv(system_archive.ARCHIVE_ROOT_ENV, str(archive_root)); monkeypatch.setattr(system_archive, "collection_map", lambda: {"test-collection": {"id": "test-collection"}})
    args = SimpleNamespace(task=task, as_of="2026-02-01T00:00:00Z", token_budget=1000, output=output_root / "context.json", collection=["test-collection"], check=True)
    assert system_archive.context_command(args)["context_pack"] == system_archive.context_command(args)["context_pack"]
    assert not args.output.exists(); args.check = False; assert system_archive.context_command(args)["status"] == "written"
    replay = system_archive.replay_command(SimpleNamespace(task=task, output=output_root / "replay.json", as_of="2026-02-01T00:00:00Z", context_pack="CP-example", check=True))["replay_plan"]
    assert (replay["execution"], replay["canonical_effect"]) == ("external-only", "none")

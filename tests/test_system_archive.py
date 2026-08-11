from __future__ import annotations

import json
import gzip
import copy
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


def test_mira_journal_collection_is_explicit_only_and_non_evidentiary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    journal_root = repo / "mira" / "journal"
    journal_root.mkdir(parents=True)
    body = b"# 2026-08-09 - A governed memory\n\nI remember this bounded reflection.\n"
    (journal_root / "2026-08-09.md").write_bytes(body)
    registry = {
        "authority_boundary": "not evidence",
        "namespace_boundary": "MJ and JRN remain separate",
        "entries": [
            {
                "journal_id": "MJ-20260809",
                "entry_date": "2026-08-09",
                "current_path": "mira/journal/2026-08-09.md",
                "versions": [
                    {
                        "version_id": "MJ-20260809-v1",
                        "content_sha256": system_archive.sha256_bytes(body),
                        "title": "A governed memory",
                        "word_count": 6,
                        "author": {"model_id": "test-model"},
                        "approval": {"approved_at": "2026-08-09T18:00:00Z"},
                    }
                ],
            }
        ],
    }
    (repo / "mira" / "journal-registry.json").write_text(json.dumps(registry), encoding="utf-8")
    collection = {
        "id": "mira-journal",
        "kind": "mira-journal-registry",
        "registry_path": "mira/journal-registry.json",
        "authority_owner": "mira/journal-registry.json",
        "evidence_class": "autobiographical-interpretation",
        "retrieval_policy": "explicit-only",
    }
    monkeypatch.setattr(system_archive, "REPO_ROOT", repo)
    discovered = list(system_archive.discover_journal(collection))
    record_input, path = discovered[0]
    assert path.read_bytes() == body
    assert record_input.evidence_class == "autobiographical-interpretation"
    assert record_input.metadata["may_promote"] is False
    monkeypatch.setattr(
        system_archive,
        "collection_map",
        lambda: {
            "ordinary": {"id": "ordinary"},
            "mira-journal": collection,
        },
    )
    assert [row["id"] for row in system_archive.selected_collections([])] == ["ordinary"]
    assert [row["id"] for row in system_archive.selected_collections(["mira-journal"])] == ["mira-journal"]


def test_journal_lineage_links_sources_and_exact_approval(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    capture_path = repo / "mira" / "continuity" / "captures" / "capture.jsonl.gz"
    capture_path.parent.mkdir(parents=True)
    source_record = "MR-" + "a" * 24
    approval_record = "MR-" + "b" * 24
    capture_id = "MC-" + "c" * 24
    rows = [
        {"record_id": source_record, "kind": "message", "role": "assistant"},
        {"record_id": approval_record, "kind": "message", "role": "user"},
    ]
    capture_path.write_bytes(gzip.compress(("\n".join(json.dumps(row) for row in rows) + "\n").encode()))
    (repo / "mira" / "continuity" / "session-registry.json").write_text(
        json.dumps(
            {
                "sessions": [
                    {
                        "captures": [
                            {"id": capture_id, "path": "mira/continuity/captures/capture.jsonl.gz"}
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (repo / "mira" / "journal-registry.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "versions": [
                            {
                                "version_id": "MJ-20260809-v1",
                                "source_refs": [
                                    {
                                        "kind": "mira-session-records",
                                        "record_ids": [source_record],
                                    }
                                ],
                                "approval": {"record_ref": approval_record},
                            }
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    archive = ArtifactStore(tmp_path / "external", repo, create=True)
    monkeypatch.setattr(system_archive, "REPO_ROOT", repo)
    with archive.connect(create=True) as connection:
        capture_input = RecordInput(
            capture_id, "session-capture", "mira/continuity/captures/capture.jsonl.gz",
            "mira-continuity", "registry", "continuity-evidence", "agent-session",
            "session", "2026-08-09T18:00:00Z", None, None, {}, "source"
        )
        journal_input = RecordInput(
            "MJ-20260809-v1", "journal-entry", "mira/journal/2026-08-09.md",
            "mira-journal", "registry", "autobiographical-interpretation", "model",
            "model", "2026-08-09T18:00:00Z", None, None, {}, "reflection"
        )
        ingest_record(connection, archive, capture_input, capture_path.read_bytes())
        ingest_record(connection, archive, journal_input, b"reflection")
        assert system_archive.add_journal_lineage(connection) == 2
        relations = {
            row[0] for row in connection.execute("SELECT relation_type FROM edges")
        }
        assert relations == {"derived_from", "collection:mira-journal:approved_by"}


def test_innermost_loop_manifest_is_pinned_and_complete() -> None:
    manifest = json.loads(
        (Path(__file__).resolve().parent.parent / "system-archive" / "registries" / "innermost-loop.json").read_text(encoding="utf-8")
    )
    assert manifest["source_commit"] == "940f354e00e2f49af2f340dd4ef1c1bc6e8ded77"
    assert manifest["document_count"] == len(manifest["documents"]) == 193
    counts: dict[str, int] = {}
    for document in manifest["documents"]:
        counts[document["document_type"]] = counts.get(document["document_type"], 0) + 1
        assert document["rights_status"] == "internal-analysis-rights-review-required"
        assert len(document["sha256"]) == 64
    assert counts == {
        "analysis": 5,
        "archive-readme": 1,
        "research-ledger": 1,
        "source-note": 5,
        "template": 2,
        "transcript": 179,
    }


def test_external_corpus_discovery_preserves_bytes_and_boundaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = tmp_path / "anyang"
    upstream = "system-archive/singularity-science/innermost-loop/transcripts/2026-01-02-example.md"
    body = b"# Example\n\nFrontier AI source material.\n"
    path = source_root / upstream
    path.parent.mkdir(parents=True)
    path.write_bytes(body)
    manifest = {
        "schema_version": 1,
        "collection_id": "innermost-loop",
        "source_repository": "https://example.test/anyang",
        "source_commit": "a" * 40,
        "source_prefix": "system-archive/singularity-science/innermost-loop",
        "imported_at": "2026-08-10",
        "document_count": 1,
        "documents": [{
            "upstream_path": upstream,
            "sha256": system_archive.sha256_bytes(body),
            "size": len(body),
            "document_type": "transcript",
            "publication_date": "2026-01-02",
            "title": "Example",
            "rights_status": "internal-analysis-rights-review-required",
            "derived_from": [],
        }],
    }
    collection = {
        "id": "innermost-loop",
        "registry_path": "registry.json",
        "authority_owner": "registry.json",
        "evidence_class": "frontier-ai-research-source",
        "genre": "frontier-ai-and-technology",
        "retrieval_policy": "explicit-only",
        "source_repository": manifest["source_repository"],
        "source_commit": manifest["source_commit"],
    }
    monkeypatch.setattr(system_archive, "external_manifest", lambda _: manifest)
    monkeypatch.setattr(system_archive, "external_source_root", lambda _collection, _root: source_root)
    record_input, discovered_path = list(system_archive.discover_external_corpus(collection, source_root))[0]
    assert discovered_path.read_bytes() == body
    assert record_input.logical_path == "external-corpora/innermost-loop/transcripts/2026-01-02-example.md"
    assert record_input.evidence_class == "frontier-ai-research-source"
    assert record_input.metadata["may_promote"] is False
    path.write_bytes(body + b"changed")
    with pytest.raises(ArchiveError, match="hash mismatch"):
        list(system_archive.discover_external_corpus(collection, source_root))


def test_external_corpus_hydration_is_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    collection = {"id": "innermost-loop", "hydration_policy": "disabled"}
    monkeypatch.setattr(system_archive, "collection_map", lambda: {"innermost-loop": collection})
    with pytest.raises(ArchiveError, match="hydration disabled"):
        system_archive.hydrate_command(SimpleNamespace(collection=["innermost-loop"], check=True))


def test_external_corpus_lineage_is_neutral_and_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"; repo.mkdir(); archive = ArtifactStore(tmp_path / "external", repo, create=True)
    collection = {
        "id": "innermost-loop",
        "registry_path": "registry.json",
        "source_repository": "https://example.test/anyang",
        "source_commit": "a" * 40,
    }
    analysis_path = "lane/analysis.md"; transcript_path = "lane/transcript.md"
    manifest = {"documents": [
        {"upstream_path": analysis_path, "derived_from": [transcript_path]},
        {"upstream_path": transcript_path, "derived_from": []},
    ]}
    monkeypatch.setattr(system_archive, "external_manifest", lambda _: manifest)
    with archive.connect(create=True) as connection:
        for upstream in (analysis_path, transcript_path):
            item = RecordInput(
                system_archive.external_record_id(collection, upstream), "source", upstream,
                "innermost-loop", "registry.json", "frontier-ai-research-source",
                "external-repository", "fixture", "2026-08-10T00:00:00Z", None, None, {}, upstream,
            )
            ingest_record(connection, archive, item, upstream.encode())
        assert system_archive.add_external_corpus_lineage(connection, collection) == 1
        assert system_archive.add_external_corpus_lineage(connection, collection) == 0
        relation = connection.execute("SELECT relation_type FROM edges").fetchone()[0]
        assert relation == "derived_from"


def test_moonshots_manifest_is_pinned_complete_and_bounded() -> None:
    repo = Path(__file__).resolve().parent.parent
    manifest = json.loads((repo / "system-archive" / "registries" / "moonshots.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 2
    assert manifest["source_commit"] == "940f354e00e2f49af2f340dd4ef1c1bc6e8ded77"
    assert manifest["document_count"] == len(manifest["documents"]) == 29
    assert manifest["object_byte_count"] == sum(row["size"] for row in manifest["documents"]) == 683276
    counts: dict[str, int] = {}
    for document in manifest["documents"]:
        counts[document["document_type"]] = counts.get(document["document_type"], 0) + 1
        assert document["logical_path"].startswith("external-corpora/moonshots/")
        assert len(document["sha256"]) == 64
        assert document["publication_date"] is None
    assert counts == {"analysis": 8, "archive-readme": 1, "derived-analysis": 4, "research-ledger": 1, "source-note": 8, "template": 2, "transcript": 5}
    assert len(manifest["excluded_paths"]) == 3
    assert sum(row["size"] for row in manifest["excluded_paths"]) == 6868
    assert sum(row.get("source_body_availability") == "not-present-in-collection" for row in manifest["documents"]) == 6


def test_moonshots_lineage_and_alias_receipts_are_exact() -> None:
    manifest = json.loads((Path(__file__).resolve().parent.parent / "system-archive" / "registries" / "moonshots.json").read_text(encoding="utf-8"))
    assert sum(len(row.get("derived_from", [])) for row in manifest["documents"]) == 26
    receipts = [receipt for row in manifest["documents"] for receipt in row.get("lineage_resolution_receipts", [])]
    assert len(receipts) == 5
    assert {row["alias_id"] for row in receipts} == {"moonshots-historical-archive-relocation-v1"}
    included = {row["upstream_path"] for row in manifest["documents"]}
    excluded = {row["upstream_path"] for row in manifest["excluded_paths"]}
    assert not included & excluded
    assert all(target in included for row in manifest["documents"] for target in row.get("derived_from", []))


def test_external_record_prefix_is_schema_isolated() -> None:
    identity = {"source_repository": "https://example.test/anyang", "source_commit": "a" * 40}
    upstream = "lane/example.md"
    assert system_archive.external_record_id(identity, upstream).startswith("SAR-IL-")
    assert system_archive.external_record_id({**identity, "record_id_prefix": "SAR-MS"}, upstream).startswith("SAR-MS-")
    with pytest.raises(ArchiveError, match="record id prefix"):
        system_archive.external_record_id({**identity, "record_id_prefix": "unsafe"}, upstream)


def test_discovered_body_keeps_v1_paths_and_v2_bytes_distinct(tmp_path: Path) -> None:
    path = tmp_path / "body.md"; path.write_bytes(b"v1")
    assert system_archive.read_discovered_body(path) == b"v1"
    assert system_archive.read_discovered_body(b"v2") == b"v2"


def test_moonshots_hydration_is_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    collection = {"id": "moonshots", "hydration_policy": "disabled"}
    monkeypatch.setattr(system_archive, "collection_map", lambda: {"moonshots": collection})
    with pytest.raises(ArchiveError, match="hydration disabled"):
        system_archive.hydrate_command(SimpleNamespace(collection=["moonshots"], check=True))


def test_moonshots_is_excluded_unless_explicitly_selected() -> None:
    default_ids = {row["id"] for row in system_archive.selected_collections([])}
    assert "moonshots" not in default_ids
    assert [row["id"] for row in system_archive.selected_collections(["moonshots"])] == ["moonshots"]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda manifest: manifest["documents"][1].__setitem__("logical_path", manifest["documents"][0]["logical_path"]), "duplicate external corpus logical path"),
        (lambda manifest: manifest.__setitem__("object_byte_count", 1), "object byte count mismatch"),
        (lambda manifest: manifest["documents"][1]["lineage_resolution_receipts"][0].__setitem__("alias_id", "missing"), "invalid lineage resolution receipt"),
        (lambda manifest: manifest["auxiliary_paths"].pop(), "documents differ from auxiliary allowlist"),
        (lambda manifest: manifest["excluded_paths"][0].pop("sha256"), "invalid external corpus exclusions"),
        (lambda manifest: manifest["excluded_paths"][0].__setitem__("reason", ""), "invalid external corpus exclusions"),
    ],
)
def test_moonshots_manifest_v2_fails_closed(
    monkeypatch: pytest.MonkeyPatch, mutation, message: str
) -> None:
    collection = system_archive.collection_map()["moonshots"]
    manifest = json.loads((Path(__file__).resolve().parent.parent / collection["registry_path"]).read_text(encoding="utf-8"))
    broken = copy.deepcopy(manifest); mutation(broken)
    monkeypatch.setattr(system_archive, "load_json", lambda _: broken)
    with pytest.raises(ArchiveError, match=message):
        system_archive.external_manifest(collection)

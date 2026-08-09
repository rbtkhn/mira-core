from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

import zstandard


SCHEMA_VERSION = 1
CODEC = "zstd-v1"
CORE_RELATIONS = frozenset({"contains", "references", "derived_from", "generated_by", "supersedes", "evaluated_by"})


class ArchiveError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def parse_time(value: str | None, *, label: str, required: bool = False) -> str | None:
    if value is None or not str(value).strip():
        if required:
            raise ArchiveError(f"{label} is required")
        return None
    text = str(value).strip()
    candidate = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as error:
        raise ArchiveError(f"{label} is not an ISO-8601 timestamp: {text}") from error
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")


def safe_logical_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        raise ArchiveError(f"unsafe logical path: {value}")
    text = normalized.strip("/")
    path = Path(text)
    if not text or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ArchiveError(f"unsafe logical path: {value}")
    return "/".join(path.parts)


def ensure_external_root(root: Path, repo_root: Path, *, create: bool) -> Path:
    resolved, repository = root.expanduser().resolve(), repo_root.resolve()
    try:
        resolved.relative_to(repository)
    except ValueError:
        pass
    else:
        raise ArchiveError(f"System Archive root must be outside the repository: {resolved}")
    if create:
        resolved.mkdir(parents=True, exist_ok=True)
    if not resolved.is_dir():
        raise ArchiveError(f"System Archive root does not exist: {resolved}")
    return resolved


@dataclass(frozen=True)
class RecordInput:
    record_id: str
    record_type: str
    logical_path: str
    collection_id: str
    authority_owner: str
    evidence_class: str
    producer_kind: str
    producer_id: str
    observed_at: str
    world_valid_from: str | None = None
    world_valid_to: str | None = None
    metadata: Mapping[str, Any] | None = None
    search_text: str = ""


class ArtifactStore:
    def __init__(self, root: Path, repo_root: Path, *, create: bool = False) -> None:
        self.repo_root = repo_root.resolve()
        self.root = ensure_external_root(root, self.repo_root, create=create)
        self.objects_root = self.root / "objects" / "sha256"
        self.catalog_path = self.root / "catalog.sqlite3"
        if create:
            self.objects_root.mkdir(parents=True, exist_ok=True)

    def connect(self, *, create: bool = False) -> sqlite3.Connection:
        if not create and not self.catalog_path.is_file():
            raise ArchiveError(f"System Archive catalog is missing: {self.catalog_path}")
        connection = sqlite3.connect(self.catalog_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        if create:
            initialize_catalog(connection)
        return connection

    def object_path(self, digest: str) -> Path:
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ArchiveError(f"invalid SHA-256 digest: {digest}")
        return self.objects_root / digest[:2] / f"{digest}.zst"

    def encode(self, body: bytes) -> bytes:
        return zstandard.ZstdCompressor(level=10, threads=0, write_checksum=True, write_content_size=True, write_dict_id=False).compress(body)

    def decode(self, payload: bytes, *, max_output_size: int = 2**31) -> bytes:
        try:
            return zstandard.ZstdDecompressor().decompress(payload, max_output_size=max_output_size)
        except zstandard.ZstdError as error:
            raise ArchiveError(f"invalid Zstandard object: {error}") from error

    def put_object(self, body: bytes) -> tuple[str, int]:
        digest, encoded = sha256_bytes(body), self.encode(body)
        target = self.object_path(digest)
        if target.is_file():
            existing = target.read_bytes()
            if existing != encoded or self.decode(existing, max_output_size=max(1, len(body))) != body:
                raise ArchiveError(f"immutable object collision or codec drift: {digest}")
            return digest, len(existing)
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=f".{digest}-", dir=target.parent)
        temporary = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(encoded); stream.flush(); os.fsync(stream.fileno())
            if target.exists():
                raise ArchiveError(f"object appeared during immutable write: {digest}")
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        return digest, len(encoded)

    def get_object(self, digest: str, *, expected_size: int | None = None) -> bytes:
        path = self.object_path(digest)
        if not path.is_file():
            raise ArchiveError(f"missing object: {digest}")
        body = self.decode(path.read_bytes(), max_output_size=max(1, expected_size) if expected_size is not None else 2**31)
        if sha256_bytes(body) != digest:
            raise ArchiveError(f"object hash mismatch: {digest}")
        if expected_size is not None and len(body) != expected_size:
            raise ArchiveError(f"object size mismatch: {digest}")
        return body


def initialize_catalog(connection: sqlite3.Connection) -> None:
    connection.executescript("""
    CREATE TABLE IF NOT EXISTS catalog_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID;
    CREATE TABLE IF NOT EXISTS objects(object_id TEXT PRIMARY KEY,original_size INTEGER NOT NULL CHECK(original_size>=0),stored_size INTEGER NOT NULL CHECK(stored_size>0),codec TEXT NOT NULL,created_at TEXT NOT NULL) WITHOUT ROWID;
    CREATE TABLE IF NOT EXISTS records(record_id TEXT NOT NULL,version INTEGER NOT NULL CHECK(version>0),record_type TEXT NOT NULL,object_id TEXT NOT NULL REFERENCES objects(object_id),logical_path TEXT NOT NULL,collection_id TEXT NOT NULL,authority_owner TEXT NOT NULL,evidence_class TEXT NOT NULL,lifecycle_state TEXT NOT NULL,world_valid_from TEXT,world_valid_to TEXT,observed_at TEXT NOT NULL,transaction_time TEXT NOT NULL,producer_kind TEXT NOT NULL,producer_id TEXT NOT NULL,metadata_json TEXT NOT NULL,PRIMARY KEY(record_id,version),CHECK(world_valid_to IS NULL OR world_valid_from IS NOT NULL),CHECK(world_valid_to IS NULL OR world_valid_from<=world_valid_to)) WITHOUT ROWID;
    CREATE TABLE IF NOT EXISTS active_paths(logical_path TEXT PRIMARY KEY,record_id TEXT NOT NULL,version INTEGER NOT NULL,object_id TEXT NOT NULL,collection_id TEXT NOT NULL,FOREIGN KEY(record_id,version) REFERENCES records(record_id,version),FOREIGN KEY(object_id) REFERENCES objects(object_id)) WITHOUT ROWID;
    CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY,event_type TEXT NOT NULL,record_id TEXT NOT NULL,record_version INTEGER NOT NULL,occurred_at TEXT NOT NULL,transaction_time TEXT NOT NULL,payload_json TEXT NOT NULL,FOREIGN KEY(record_id,record_version) REFERENCES records(record_id,version)) WITHOUT ROWID;
    CREATE TABLE IF NOT EXISTS edges(edge_id TEXT PRIMARY KEY,source_record_id TEXT NOT NULL,source_version INTEGER NOT NULL,target_record_id TEXT NOT NULL,target_version INTEGER NOT NULL,relation_type TEXT NOT NULL,recorded_at TEXT NOT NULL,metadata_json TEXT NOT NULL,FOREIGN KEY(source_record_id,source_version) REFERENCES records(record_id,version),FOREIGN KEY(target_record_id,target_version) REFERENCES records(record_id,version)) WITHOUT ROWID;
    CREATE INDEX IF NOT EXISTS records_collection_time ON records(collection_id,observed_at,record_id,version);
    CREATE INDEX IF NOT EXISTS records_type_time ON records(record_type,observed_at,record_id,version);
    CREATE INDEX IF NOT EXISTS edges_source ON edges(source_record_id,source_version,relation_type);
    CREATE INDEX IF NOT EXISTS edges_target ON edges(target_record_id,target_version,relation_type);
    CREATE VIRTUAL TABLE IF NOT EXISTS record_fts USING fts5(record_id UNINDEXED,version UNINDEXED,collection_id UNINDEXED,logical_path UNINDEXED,body,tokenize='unicode61');
    CREATE TRIGGER IF NOT EXISTS immutable_objects_update BEFORE UPDATE ON objects BEGIN SELECT RAISE(ABORT,'objects are immutable'); END;
    CREATE TRIGGER IF NOT EXISTS immutable_objects_delete BEFORE DELETE ON objects BEGIN SELECT RAISE(ABORT,'objects are immutable'); END;
    CREATE TRIGGER IF NOT EXISTS immutable_records_update BEFORE UPDATE ON records BEGIN SELECT RAISE(ABORT,'records are immutable'); END;
    CREATE TRIGGER IF NOT EXISTS immutable_records_delete BEFORE DELETE ON records BEGIN SELECT RAISE(ABORT,'records are immutable'); END;
    CREATE TRIGGER IF NOT EXISTS immutable_events_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,'events are immutable'); END;
    CREATE TRIGGER IF NOT EXISTS immutable_events_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,'events are immutable'); END;
    CREATE TRIGGER IF NOT EXISTS immutable_edges_update BEFORE UPDATE ON edges BEGIN SELECT RAISE(ABORT,'edges are immutable'); END;
    CREATE TRIGGER IF NOT EXISTS immutable_edges_delete BEFORE DELETE ON edges BEGIN SELECT RAISE(ABORT,'edges are immutable'); END;
    """)
    connection.execute("INSERT OR IGNORE INTO catalog_meta VALUES('schema_version',?)", (str(SCHEMA_VERSION),))
    if connection.execute("SELECT value FROM catalog_meta WHERE key='schema_version'").fetchone()[0] != str(SCHEMA_VERSION):
        raise ArchiveError("unsupported System Archive catalog schema")
    connection.commit()


def active_record(connection: sqlite3.Connection, logical_path: str) -> sqlite3.Row | None:
    return connection.execute("SELECT r.* FROM active_paths a JOIN records r ON r.record_id=a.record_id AND r.version=a.version WHERE a.logical_path=?", (safe_logical_path(logical_path),)).fetchone()


def ingest_record(connection: sqlite3.Connection, store: ArtifactStore, record: RecordInput, body: bytes, *, transaction_time: str | None = None) -> tuple[int, bool, str]:
    path = safe_logical_path(record.logical_path)
    observed = parse_time(record.observed_at, label="observed_at", required=True)
    world_from = parse_time(record.world_valid_from, label="world_valid_from")
    world_to = parse_time(record.world_valid_to, label="world_valid_to")
    if world_to and (world_from is None or world_from > world_to):
        raise ArchiveError("world-valid interval is inverted")
    transaction = parse_time(transaction_time or utc_now(), label="transaction_time", required=True)
    metadata = canonical_json(dict(record.metadata or {}))
    object_id, stored_size = store.put_object(body)
    connection.execute("INSERT OR IGNORE INTO objects VALUES(?,?,?,?,?)", (object_id, len(body), stored_size, CODEC, transaction))
    prior = active_record(connection, path)
    if prior is not None and prior["object_id"] == object_id and prior["metadata_json"] == metadata:
        return int(prior["version"]), False, object_id
    version = int(connection.execute("SELECT COALESCE(MAX(version),0) FROM records WHERE record_id=?", (record.record_id,)).fetchone()[0]) + 1
    if prior is not None and prior["record_id"] != record.record_id:
        raise ArchiveError(f"logical path identity changed: {path}")
    connection.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (record.record_id,version,record.record_type,object_id,path,record.collection_id,record.authority_owner,record.evidence_class,"active",world_from,world_to,observed,transaction,record.producer_kind,record.producer_id,metadata))
    connection.execute("INSERT INTO active_paths VALUES(?,?,?,?,?) ON CONFLICT(logical_path) DO UPDATE SET record_id=excluded.record_id,version=excluded.version,object_id=excluded.object_id,collection_id=excluded.collection_id", (path,record.record_id,version,object_id,record.collection_id))
    connection.execute("INSERT INTO record_fts(record_id,version,collection_id,logical_path,body) VALUES(?,?,?,?,?)", (record.record_id,version,record.collection_id,path,record.search_text))
    event_id = "EV-" + sha256_bytes(canonical_json(["ingested",record.record_id,version,object_id]).encode())[:24]
    connection.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?)", (event_id,"ingested",record.record_id,version,observed,transaction,canonical_json({"logical_path":path,"object_id":object_id})))
    if prior is not None:
        edge_id = "ED-" + sha256_bytes(canonical_json([record.record_id,version,"supersedes",prior["record_id"],prior["version"]]).encode())[:24]
        connection.execute("INSERT INTO edges VALUES(?,?,?,?,?,?,?,?)", (edge_id,record.record_id,version,prior["record_id"],int(prior["version"]),"supersedes",transaction,"{}"))
    return version, True, object_id


def add_edge(connection: sqlite3.Connection, *, source: tuple[str,int], target: tuple[str,int], relation_type: str, metadata: Mapping[str,Any] | None = None, recorded_at: str | None = None) -> str:
    if relation_type not in CORE_RELATIONS and not relation_type.startswith("collection:"):
        raise ArchiveError(f"unsupported relation type: {relation_type}")
    for endpoint in (source,target):
        if connection.execute("SELECT 1 FROM records WHERE record_id=? AND version=?",endpoint).fetchone() is None:
            raise ArchiveError(f"unresolved edge endpoint: {endpoint[0]}-v{endpoint[1]}")
    stamp = parse_time(recorded_at or utc_now(), label="recorded_at", required=True)
    edge_id = "ED-" + sha256_bytes(canonical_json([source,relation_type,target,dict(metadata or {})]).encode())[:24]
    connection.execute("INSERT OR IGNORE INTO edges VALUES(?,?,?,?,?,?,?,?)", (edge_id,*source,*target,relation_type,stamp,canonical_json(dict(metadata or {}))))
    return edge_id


def catalog_fingerprint(connection: sqlite3.Connection) -> str:
    digest = hashlib.sha256(f"system-archive-catalog-v{SCHEMA_VERSION}\n".encode())
    for row in connection.execute("SELECT logical_path,record_id,version,object_id,collection_id FROM active_paths ORDER BY logical_path"):
        digest.update(canonical_json(list(row)).encode() + b"\n")
    return digest.hexdigest()


def catalog_counts(connection: sqlite3.Connection) -> dict[str,int]:
    return {table:int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]) for table in ("objects","records","active_paths","events","edges")}


def iter_active_records(connection: sqlite3.Connection, *, collection_ids: Sequence[str] = (), as_of: str | None = None) -> Iterator[sqlite3.Row]:
    clauses: list[str] = []
    parameters: list[Any] = []
    if collection_ids:
        clauses.append("r.collection_id IN (%s)" % ",".join("?" for _ in collection_ids)); parameters.extend(collection_ids)
    if as_of:
        clauses.append("r.observed_at<=?"); parameters.append(parse_time(as_of,label="as_of",required=True))
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    yield from connection.execute("SELECT r.* FROM active_paths a JOIN records r ON r.record_id=a.record_id AND r.version=a.version" + where + " ORDER BY r.logical_path",parameters)


def verify_derivation_acyclic(connection: sqlite3.Connection) -> list[str]:
    graph: dict[tuple[str,int],list[tuple[str,int]]] = {}
    for row in connection.execute("SELECT source_record_id,source_version,target_record_id,target_version FROM edges WHERE relation_type='derived_from'"):
        graph.setdefault((row[0],int(row[1])),[]).append((row[2],int(row[3])))
    failures: list[str] = []; visiting: set[tuple[str,int]] = set(); visited: set[tuple[str,int]] = set()
    def visit(node: tuple[str,int]) -> None:
        if node in visited: return
        if node in visiting:
            failures.append(f"derived_from cycle at {node[0]}-v{node[1]}"); return
        visiting.add(node)
        for target in graph.get(node,[]): visit(target)
        visiting.remove(node); visited.add(node)
    for node in sorted(graph): visit(node)
    return failures

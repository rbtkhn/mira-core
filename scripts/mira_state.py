from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from portable_paths import REPO_ROOT, is_within, require_private_path, resolve_state_root

SCHEMA_VERSION = 1
LEGACY_ROOT = Path(r"C:\private")
RECEIPT = Path("migration/quarantine-receipt.json")
CONTINUITY_RECEIPT = Path("migration/continuity-receipt.json")
CONTINUITY_SUPPLEMENT = Path("migration/continuity-supplement.json")
MANIFEST = Path("migration/source-dispositions.json")
CONTINUITY_WORKSPACE = "mira-core"
ACTIVE_FILES = {
    "mira-core-choice-history.sqlite3": "choice-source",
    "narrative-choice-history.sqlite3": "choice-source",
    "narrative-cadence.sqlite3": "cadence-source",
    "mira-mentorship.sqlite3": "mentorship-source",
    "narrative-system-archive-config.json": "archive-config",
    "mira-core-archive-config.json": "archive-config",
    "mira-core-system-archive-config.json": "archive-config",
}
ACTIVE_DIRS = {"mira-journal-drafts": "journal-drafts", "mira-journal-revisions": "journal-revisions", "mira-library-texts": "library-texts"}
LEGACY_DIRS = {
    "mira-autobiographical-reflections", "mira-documents", "mira-dream",
    "mira-history", "mira-journal-audits", "recursive-learning",
    "recursive-learning-candidates", "historical-reference", "mentorship",
}
DISPOSABLE_MARKERS = ("temp", "test", "cache", "worktree", "-wt", "rehearsal", "validation", "repro")
SECRET_NAMES = {"auth.json", "credentials.json", "sandbox_secrets.json"}

class StateError(RuntimeError):
    pass

def legacy_source_path(raw: str | Path, *, label: str) -> Path:
    """Allow a named legacy migration source to be read from an old checkout."""
    return require_private_path(raw, label=label, allow_git_checkout=True)

def utc() -> datetime:
    return datetime.now(timezone.utc)

def iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")

def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def tree_rows(root: Path) -> list[dict[str, Any]]:
    return [{"path": p.relative_to(root).as_posix(), "size": p.stat().st_size, "sha256": sha(p)}
            for p in sorted(root.rglob("*")) if p.is_file()]

def tree_digest(rows: list[dict[str, Any]]) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def stable_archive_rows(root: Path) -> list[dict[str, Any]]:
    """Exclude SQLite connection sidecars; logical catalog parity is checked separately."""
    return [
        row for row in tree_rows(root)
        if not row["path"].endswith((".sqlite3-wal", ".sqlite3-shm"))
    ]

def archive_logical_parity(canonical: Path, replica: Path) -> bool:
    from archive_store import ArtifactStore, catalog_counts, catalog_fingerprint
    left_store = ArtifactStore(canonical, REPO_ROOT)
    right_store = ArtifactStore(replica, REPO_ROOT)
    with left_store.connect() as left, right_store.connect() as right:
        return (
            catalog_fingerprint(left) == catalog_fingerprint(right)
            and catalog_counts(left) == catalog_counts(right)
        )

def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)

def disposition(entry: Path) -> str:
    name = entry.name
    lowered = name.casefold()
    if name in ACTIVE_FILES or name in ACTIVE_DIRS:
        return "migrate-active"
    if name in LEGACY_DIRS:
        return "preserve-inactive-legacy"
    if name in SECRET_NAMES or any(token in lowered for token in ("credential", "secret", "token")):
        return "exclude-secret-or-credential"
    if any(marker in lowered for marker in DISPOSABLE_MARKERS):
        return "disposable-candidate-no-action"
    return "out-of-scope-no-action"

def inventory(source: Path) -> dict[str, Any]:
    source = legacy_source_path(source, label="legacy source")
    if not source.is_dir():
        raise StateError(f"legacy source does not exist: {source}")
    rows = []
    for entry in sorted(source.iterdir(), key=lambda item: item.name.casefold()):
        rows.append({"name": entry.name, "type": "directory" if entry.is_dir() else "file",
                     "bytes": entry.stat().st_size if entry.is_file() else None,
                     "disposition": disposition(entry)})
    return {"schema_version": SCHEMA_VERSION, "source": str(source), "entries": rows,
            "entry_count": len(rows), "authority_effect": "none"}

def sqlite_meta(path: Path) -> dict[str, Any]:
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        tables = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        return {"user_version": connection.execute("PRAGMA user_version").fetchone()[0],
                "integrity_check": connection.execute("PRAGMA integrity_check").fetchone()[0],
                "counts": {table: connection.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0] for table in tables},
                "sha256": sha(path), "size": path.stat().st_size}
    finally:
        connection.close()

def choice_preflight(paths: list[Path]) -> dict[str, Any]:
    if len(paths) != 2 or any(not p.is_file() for p in paths):
        raise StateError("both choice ledgers are required for consolidation")
    metadata = [sqlite_meta(path) for path in paths]
    if len({row["user_version"] for row in metadata}) != 1:
        raise StateError("choice ledger schemas differ")
    identifiers: dict[str, set[str]] = {"choice_prompts": set(), "choice_events": set()}
    schemas: dict[str, list[list[dict[str, Any]]]] = {"choice_prompts": [], "choice_events": []}
    id_columns = {"choice_prompts": "choice_id", "choice_events": "event_id"}
    for path in paths:
        connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        try:
            for table, column in id_columns.items():
                schema = [
                    {"name": str(row[1]), "type": str(row[2]), "notnull": bool(row[3]), "pk": int(row[5])}
                    for row in connection.execute(f'PRAGMA table_info("{table}")')
                ]
                schemas[table].append(schema)
                incoming = {str(row[0]) for row in connection.execute(f'SELECT "{column}" FROM "{table}"')}
                overlap = identifiers[table] & incoming
                if overlap:
                    raise StateError(f"duplicate {table} identities across choice sources")
                identifiers[table].update(incoming)
        finally:
            connection.close()
    for table, variants in schemas.items():
        column_sets = [{column["name"] for column in schema} for schema in variants]
        if any(columns != column_sets[0] for columns in column_sets[1:]):
            raise StateError(f"choice ledger {table} columns differ")
    return {"sources": [{"path": str(path), **meta} for path, meta in zip(paths, metadata, strict=True)],
            "expected_counts": {table: sum(meta["counts"].get(table, 0) for meta in metadata) for table in id_columns},
            "schema_order_drift": {table: schemas[table][0] != schemas[table][1] for table in schemas}}

def choice_domain_verify(path: Path) -> dict[str, Any]:
    import choice_ledger
    failures: list[str] = []
    connection = choice_ledger.connect_read_only(path)
    try:
        choice_ids = [str(row[0]) for row in connection.execute("SELECT choice_id FROM choice_prompts ORDER BY choice_id")]
        for choice_id in choice_ids:
            result = choice_ledger.verify_choice(connection, choice_id)
            failures.extend(f"{choice_id}: {failure}" for failure in result["failures"])
    finally:
        connection.close()
    return {"valid": not failures, "choice_count": len(choice_ids), "failures": failures}

def snapshot_sqlite(source: Path, destination: Path) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".migrating")
    temporary.unlink(missing_ok=True)
    src = sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(temporary)
    try:
        src.backup(dst)
        dst.commit()
        check = dst.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        dst.close(); src.close()
    if check != "ok":
        temporary.unlink(missing_ok=True)
        raise StateError(f"SQLite snapshot failed integrity check: {source}")
    temporary.replace(destination)
    return sqlite_meta(destination)

def merge_choices(sources: list[Path], destination: Path) -> dict[str, Any]:
    preflight = choice_preflight(sources)
    snapshot_sqlite(sources[0], destination)
    connection = sqlite3.connect(destination)
    try:
        connection.execute("ATTACH DATABASE ? AS incoming", (str(sources[1]),))
        with connection:
            for table in ("choice_prompts", "choice_events"):
                columns = [str(row[1]) for row in connection.execute(f'PRAGMA table_info("{table}")')]
                quoted = ", ".join(f'"{column}"' for column in columns)
                connection.execute(f'INSERT INTO "{table}" ({quoted}) SELECT {quoted} FROM incoming."{table}"')
        connection.execute("DETACH DATABASE incoming")
        check = connection.execute("PRAGMA integrity_check").fetchone()[0]
        counts = {table: connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                  for table in ("choice_prompts", "choice_events")}
    finally:
        connection.close()
    domain = choice_domain_verify(destination)
    if check != "ok" or counts != preflight["expected_counts"] or not domain["valid"]:
        raise StateError("consolidated choice ledger failed integrity or row-count parity")
    return {"preflight": preflight, "target": sqlite_meta(destination), "domain_verification": domain}

def copy_tree_verified(source: Path, destination: Path) -> dict[str, Any]:
    if destination.exists():
        raise StateError(f"migration destination already exists: {destination}")
    shutil.copytree(source, destination, copy_function=shutil.copy2)
    before, after = tree_rows(source), tree_rows(destination)
    if before != after:
        raise StateError(f"tree verification failed: {source}")
    return {"source": str(source), "destination": str(destination), "file_count": len(after),
            "bytes": sum(row["size"] for row in after), "tree_sha256": tree_digest(after)}

def archive_sources(source: Path) -> tuple[Path, Path, Path]:
    configs = [source / name for name in ("mira-core-archive-config.json", "mira-core-system-archive-config.json", "narrative-system-archive-config.json")]
    config = next((path for path in configs if path.is_file()), None)
    if config is None:
        raise StateError("legacy archive configuration is missing")
    document = json.loads(config.read_text(encoding="utf-8"))
    canonical, replica = Path(document["canonical_root"]), Path(document["replica_root"])
    if not canonical.is_dir() or not replica.is_dir() or canonical.resolve() == replica.resolve():
        raise StateError("legacy archive canonical and replica roots must exist and differ")
    return canonical.resolve(), replica.resolve(), config

def source_snapshot(paths: list[Path]) -> dict[str, Any]:
    result = {}
    for path in paths:
        if path.is_file():
            result[str(path)] = {"sha256": sha(path), "mtime_ns": path.stat().st_mtime_ns, "size": path.stat().st_size}
        elif path.is_dir():
            rows = tree_rows(path)
            result[str(path)] = {"tree_sha256": tree_digest(rows), "file_count": len(rows),
                                 "bytes": sum(row["size"] for row in rows)}
    return result


def continuity_events(source: Path) -> dict[str, Any]:
    source = legacy_source_path(source, label="legacy Continuity inbox")
    workspace = source / CONTINUITY_WORKSPACE
    if not workspace.is_dir():
        raise StateError(f"legacy Continuity workspace is missing: {workspace}")
    sessions: dict[str, int] = {}
    event_count = 0
    for directory in sorted(path for path in workspace.iterdir() if path.is_dir()):
        files = sorted(directory.glob("*.json"))
        events = []
        for path in files:
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                raise StateError(f"Continuity receipt is unreadable: {path}") from error
            claimed = value.get("event_sha256")
            body = {key: item for key, item in value.items() if key != "event_sha256"}
            raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            if claimed != hashlib.sha256(raw).hexdigest():
                raise StateError(f"Continuity receipt digest mismatch: {path}")
            if value.get("workspace_id") != CONTINUITY_WORKSPACE:
                raise StateError(f"Continuity receipt workspace mismatch: {path}")
            events.append(value)
        events.sort(key=lambda row: (int(row.get("sequence", 0)), row.get("event_id", "")))
        for index, event in enumerate(events, start=1):
            if event.get("sequence") != index:
                raise StateError(f"Continuity receipt sequence is not contiguous: {directory}")
            previous = events[index - 2]["event_sha256"] if index > 1 else None
            if event.get("previous_event_sha256") != previous:
                raise StateError(f"Continuity receipt event chain mismatch: {directory}")
        if events:
            sessions[directory.name] = len(events)
            event_count += len(events)
    rows = tree_rows(source)
    if event_count != len(rows):
        raise StateError("legacy Continuity inbox contains non-receipt files")
    return {
        "source": str(source), "workspace_id": CONTINUITY_WORKSPACE,
        "session_count": len(sessions), "event_count": event_count,
        "session_event_counts": sessions, "file_count": len(rows),
        "bytes": sum(row["size"] for row in rows), "tree_sha256": tree_digest(rows),
    }


def continuity_verify(root: Path) -> dict[str, Any]:
    root = resolve_state_root(root)
    receipt_path = root / CONTINUITY_RECEIPT
    if not receipt_path.is_file():
        raise StateError(f"Continuity migration receipt is missing: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    supplement_path = root / CONTINUITY_SUPPLEMENT
    supplement = json.loads(supplement_path.read_text(encoding="utf-8")) if supplement_path.is_file() else None
    source = Path(receipt["source"])
    destination = root / "continuity/inbox"
    source_current = continuity_events(source)
    target_current = continuity_events(destination)
    source_files = {row["path"]: row["sha256"] for row in tree_rows(source)}
    target_files = {row["path"]: row["sha256"] for row in tree_rows(destination)}
    source_subset_target = all(target_files.get(path) == digest for path, digest in source_files.items())
    target_subset_source = all(source_files.get(path) == digest for path, digest in target_files.items())
    source_unchanged = source_current["tree_sha256"] == receipt.get("source_tree_sha256")
    checkpoint_source = (supplement or receipt).get("source_tree_sha256")
    checkpoint_target = (supplement or receipt).get("target_tree_sha256")
    source_matches_checkpoint = source_current["tree_sha256"] == checkpoint_source
    target_matches_checkpoint = target_current["tree_sha256"] == checkpoint_target
    target_grew_validly = source_matches_checkpoint and source_subset_target
    legacy_source_grew_validly = target_matches_checkpoint and target_subset_source
    synchronized = source_current["tree_sha256"] == target_current["tree_sha256"]
    valid = target_grew_validly or legacy_source_grew_validly or synchronized
    sync_required = valid and legacy_source_grew_validly and not synchronized
    return {
        "valid": valid,
        "source_unchanged": source_unchanged,
        "migrated_receipts_preserved": source_subset_target or target_subset_source,
        "target_has_post_migration_events": target_grew_validly and not synchronized,
        "legacy_source_has_post_migration_events": legacy_source_grew_validly and not synchronized,
        "sync_required": sync_required,
        "supplement": supplement,
        "source": source_current, "target": target_current, "receipt": receipt,
        "authority_effect": "none",
    }


def synchronize_continuity(root: Path, verification: dict[str, Any], *, check: bool) -> dict[str, Any]:
    if not verification.get("valid"):
        raise StateError("Continuity migration cannot synchronize invalid state")
    if not verification.get("sync_required"):
        return {"check": check, "mutated": False, "copied": [], "verification": verification}
    source = Path(verification["source"]["source"])
    target = Path(verification["target"]["source"])
    source_rows = {row["path"]: row for row in tree_rows(source)}
    target_rows = {row["path"]: row for row in tree_rows(target)}
    conflicts = sorted(path for path in source_rows.keys() & target_rows if source_rows[path]["sha256"] != target_rows[path]["sha256"])
    if conflicts:
        raise StateError("Continuity synchronization found conflicting receipts: " + ", ".join(conflicts))
    missing = sorted(source_rows.keys() - target_rows.keys())
    if check:
        return {"check": True, "mutated": False, "copied": missing, "verification": verification}
    copied: list[Path] = []
    try:
        for relative in missing:
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_name(f".{destination.name}.sync-{os.getpid()}")
            shutil.copy2(source / relative, temporary)
            if sha(temporary) != source_rows[relative]["sha256"]:
                temporary.unlink(missing_ok=True)
                raise StateError(f"Continuity synchronization digest mismatch: {relative}")
            temporary.replace(destination)
            copied.append(destination)
        target_current = continuity_events(target)
        source_current = continuity_events(source)
        if target_current["tree_sha256"] != source_current["tree_sha256"]:
            raise StateError("Continuity synchronization did not reach source parity")
        supplement = {
            "schema_version": 1, "status": "verified-continuity-supplement",
            "supplemented_at": iso(utc()), "source": str(source), "target": str(target),
            "prior_target_tree_sha256": verification["target"]["tree_sha256"],
            "source_tree_sha256": source_current["tree_sha256"],
            "target_tree_sha256": target_current["tree_sha256"],
            "copied_receipts": missing, "source_mutated": False,
            "deletion_authority": "none", "authority_effect": "none",
        }
        atomic_json(root / CONTINUITY_SUPPLEMENT, supplement)
        return {"check": False, "mutated": bool(missing), "copied": missing, "supplement": supplement}
    except Exception:
        for destination in reversed(copied):
            destination.unlink(missing_ok=True)
        raise


def migrate_continuity(source: Path, target: Path, *, check: bool) -> dict[str, Any]:
    source = legacy_source_path(source, label="legacy Continuity inbox")
    target = resolve_state_root(target)
    source_meta = continuity_events(source)
    destination = target / "continuity/inbox"
    receipt_path = target / CONTINUITY_RECEIPT
    if receipt_path.is_file():
        result = continuity_verify(target)
        return {"check": check, "already_migrated": True, "mutated": False, **result}
    if destination.exists():
        raise StateError(f"unreceipted Continuity target already exists: {destination}")
    if check:
        return {
            "check": True, "already_migrated": False, "mutated": False,
            "source": source_meta, "target": str(destination), "authority_effect": "none",
        }
    temporary = target.parent / f".{target.name}-continuity-migrating-{os.getpid()}"
    if temporary.exists():
        shutil.rmtree(temporary)
    try:
        copied = copy_tree_verified(source, temporary)
        source_after = continuity_events(source)
        if source_after["tree_sha256"] != source_meta["tree_sha256"]:
            raise StateError("legacy Continuity source changed during copy")
        target.mkdir(parents=True, exist_ok=True)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary.replace(destination)
        target_meta = continuity_events(destination)
        receipt = {
            "schema_version": 1, "status": "verified-continuity-migration",
            "source": str(source), "target": str(destination), "migrated_at": iso(utc()),
            "source_tree_sha256": source_meta["tree_sha256"],
            "target_tree_sha256": target_meta["tree_sha256"],
            "session_count": target_meta["session_count"], "event_count": target_meta["event_count"],
            "source_mutated": False, "deletion_authority": "none", "authority_effect": "none",
        }
        atomic_json(receipt_path, receipt)
        return {
            "check": False, "already_migrated": False, "mutated": True,
            "copied": copied, "valid": True, "receipt": receipt, "authority_effect": "none",
        }
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
        if destination.exists() and not receipt_path.exists():
            shutil.rmtree(destination, ignore_errors=True)
        raise

def migration_plan(source: Path, target: Path) -> dict[str, Any]:
    source = legacy_source_path(source, label="legacy source")
    target = resolve_state_root(target)
    partial_continuity = None
    if target.exists() and any(target.iterdir()):
        receipt = target / RECEIPT
        if receipt.is_file():
            return {"already_migrated": True, "target": str(target), "receipt": str(receipt)}
        resumable = {"continuity", "migration"}
        managed = {"state", "archive", "journal", "continuity", "legacy", "migration", "library", "sessions", "worktrees"}
        conflicts = sorted(entry.name for entry in target.iterdir() if entry.name in managed - resumable)
        if conflicts:
            raise StateError("target contains unmanaged pre-migration carrier paths: " + ", ".join(conflicts))
        present = {entry.name for entry in target.iterdir() if entry.name in resumable}
        if present:
            if present != resumable:
                raise StateError("partial Continuity migration is missing its receipt or inbox")
            partial_continuity = continuity_verify(target)
            if not partial_continuity.get("valid"):
                raise StateError("partial Continuity migration failed verification")
    choices = [source / "narrative-choice-history.sqlite3", source / "mira-core-choice-history.sqlite3"]
    choice = choice_preflight(choices)
    cadence, mentor = source / "narrative-cadence.sqlite3", source / "mira-mentorship.sqlite3"
    for path in (cadence, mentor):
        if not path.is_file() or sqlite_meta(path)["integrity_check"] != "ok":
            raise StateError(f"required valid SQLite source is missing: {path}")
    canonical, replica, config = archive_sources(source)
    selected = [*choices, cadence, mentor, canonical, replica, config]
    for name in ACTIVE_DIRS:
        if (source / name).is_dir(): selected.append(source / name)
    projected = sum(row["size"] for row in choice["sources"]) + cadence.stat().st_size + mentor.stat().st_size
    for directory in [canonical, replica, *(source / name for name in set(ACTIVE_DIRS) | LEGACY_DIRS if (source / name).is_dir())]:
        projected += sum(path.stat().st_size for path in directory.rglob("*") if path.is_file())
    parent = target.parent
    probe = parent if parent.exists() else next((candidate for candidate in parent.parents if candidate.exists()), parent)
    free = shutil.disk_usage(probe).free
    if free < projected * 1.1:
        raise StateError(f"insufficient target capacity: need at least {int(projected * 1.1)} bytes")
    return {"already_migrated": False, "source": str(source), "target": str(target),
            "projected_bytes": projected, "free_bytes": free, "choice": choice,
            "archive": {"config": str(config), "canonical": str(canonical), "replica": str(replica)},
            "source_snapshot": source_snapshot(selected), "inventory": inventory(source),
            "resumed_continuity": partial_continuity}

def migrate(source: Path, target: Path, *, check: bool) -> dict[str, Any]:
    plan = migration_plan(source, target)
    if check or plan["already_migrated"]:
        if plan.get("resumed_continuity"):
            plan["continuity_sync"] = synchronize_continuity(target, plan["resumed_continuity"], check=True)
        return {"check": check, **plan, "mutated": False}
    source, target = Path(plan["source"]), Path(plan["target"])
    continuity_sync = None
    if plan.get("resumed_continuity"):
        continuity_sync = synchronize_continuity(target, plan["resumed_continuity"], check=False)
    staging = target.with_name(f".{target.name}.migrating-{os.getpid()}")
    if staging.exists(): shutil.rmtree(staging)
    staging.mkdir(parents=True)
    copied: dict[str, Any] = {}
    try:
        copied["choice"] = merge_choices(
            [source / "narrative-choice-history.sqlite3", source / "mira-core-choice-history.sqlite3"],
            staging / "state/choice-history.sqlite3")
        copied["cadence"] = snapshot_sqlite(source / "narrative-cadence.sqlite3", staging / "state/cadence.sqlite3")
        copied["mentorship"] = snapshot_sqlite(source / "mira-mentorship.sqlite3", staging / "state/mentorship.sqlite3")
        archive = plan["archive"]
        canonical_source, replica_source = Path(archive["canonical"]), Path(archive["replica"])
        canonical_rows, replica_rows = tree_rows(canonical_source), tree_rows(replica_source)
        canonical_digest, replica_digest = tree_digest(canonical_rows), tree_digest(replica_rows)
        copied["archive_canonical"] = copy_tree_verified(canonical_source, staging / "archive/canonical")
        copied["archive_replica"] = copy_tree_verified(canonical_source, staging / "archive/replica")
        archive_disposition = {
            "authority": "configured-canonical",
            "canonical_source_sha256": canonical_digest,
            "legacy_replica_source_sha256": replica_digest,
            "legacy_replica_diverged": canonical_digest != replica_digest,
        }
        if canonical_digest != replica_digest:
            legacy_target = staging / "legacy" / "archive-replica-divergent" / replica_digest
            copied["legacy/archive-replica-divergent"] = copy_tree_verified(replica_source, legacy_target)
            archive_disposition["preserved_legacy_replica"] = legacy_target.relative_to(staging).as_posix()
        atomic_json(staging / "archive/config.json", {"schema_version": 1, "canonical_root": "canonical", "replica_root": "replica"})
        for name, destination in ACTIVE_DIRS.items():
            if not (source / name).is_dir(): continue
            target_path = staging / ("library/texts" if destination == "library-texts" else f"journal/{destination.removeprefix('journal-')}")
            copied[destination] = copy_tree_verified(source / name, target_path)
        for name in sorted(LEGACY_DIRS):
            if not (source / name).is_dir():
                continue
            try:
                copied[f"legacy/{name}"] = copy_tree_verified(source / name, staging / "legacy" / name)
            except shutil.Error as error:
                copied[f"legacy/{name}"] = {
                    "status": "preserved-in-place-unavailable",
                    "source": str(source / name),
                    "active": False,
                    "authority_effect": "none",
                    "error_count": len(error.args[0]) if error.args and isinstance(error.args[0], list) else None,
                }
                shutil.rmtree(staging / "legacy" / name, ignore_errors=True)
        atomic_json(staging / MANIFEST, plan["inventory"])
        after = source_snapshot([Path(path) for path in plan["source_snapshot"]])
        if after != plan["source_snapshot"]:
            raise StateError("a migration source changed during copy")
        cutover = utc()
        receipt = {"schema_version": SCHEMA_VERSION, "status": "verified-quarantine",
                   "source_root": str(source), "target_root": str(target), "cutover_at": iso(cutover),
                   "deletion_review_eligible_at": iso(cutover + timedelta(days=30)),
                   "source_snapshot": after, "copied": copied, "archive_disposition": archive_disposition,
                   "resumed_continuity": bool(plan.get("resumed_continuity")),
                   "continuity_sync": continuity_sync, "source_mutated": False,
                   "deletion_authority": "none", "repository_visibility_changed": False,
                   "authority_effect": "none"}
        atomic_json(staging / RECEIPT, receipt)
        target.mkdir(parents=True, exist_ok=True)
        moved: list[Path] = []
        try:
            for child in sorted(staging.iterdir(), key=lambda item: item.name == "migration"):
                destination = target / child.name
                if child.name == "continuity" and destination.exists():
                    if not plan.get("resumed_continuity"):
                        raise StateError(f"migration target collision: {destination}")
                    shutil.rmtree(child)
                    continue
                if child.name == "migration" and destination.is_dir():
                    for item in child.iterdir():
                        item_destination = destination / item.name
                        if item_destination.exists():
                            raise StateError(f"migration target collision: {item_destination}")
                        item.replace(item_destination)
                        moved.append(item_destination)
                    child.rmdir()
                    continue
                if destination.exists():
                    raise StateError(f"migration target collision: {destination}")
                child.replace(destination)
                moved.append(destination)
        except Exception:
            for destination in reversed(moved):
                if destination.is_dir(): shutil.rmtree(destination, ignore_errors=True)
                else: destination.unlink(missing_ok=True)
            raise
        finally:
            shutil.rmtree(staging, ignore_errors=True)
        return {"check": False, "mutated": True, **receipt}
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise

def verify(root: Path, source_manifest: Path | None = None) -> dict[str, Any]:
    root = resolve_state_root(root)
    receipt_path = source_manifest or root / RECEIPT
    if not receipt_path.is_file(): raise StateError(f"migration receipt is missing: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    failures = []
    for relative in ("state/choice-history.sqlite3", "state/cadence.sqlite3", "state/mentorship.sqlite3"):
        path = root / relative
        if not path.is_file() or sqlite_meta(path)["integrity_check"] != "ok": failures.append(relative)
    for relative in ("archive/canonical", "archive/replica"):
        if not (root / relative).is_dir(): failures.append(relative)
    if not failures:
        canonical, replica = root / "archive/canonical", root / "archive/replica"
        if stable_archive_rows(canonical) != stable_archive_rows(replica) or not archive_logical_parity(canonical, replica):
            failures.append("archive/replica-parity")
    source_current = source_snapshot([Path(path) for path in receipt.get("source_snapshot", {})])
    source_unchanged = source_current == receipt.get("source_snapshot")
    return {"valid": not failures and source_unchanged, "root": str(root), "failures": failures,
            "source_unchanged": source_unchanged, "receipt": receipt, "authority_effect": "none"}

def export(root: Path, output: Path, *, check: bool) -> dict[str, Any]:
    root = resolve_state_root(root)
    output = require_private_path(output, label="export output")
    if is_within(output, root) or is_within(root, output): raise StateError("export and live state roots must not overlap")
    if not root.is_dir(): raise StateError(f"state root does not exist: {root}")
    rows = tree_rows(root)
    if check: return {"check": True, "mutated": False, "source": str(root), "output": str(output), "file_count": len(rows), "bytes": sum(r["size"] for r in rows)}
    if output.exists(): raise StateError(f"export output already exists: {output}")
    temporary = output.with_name(f".{output.name}.exporting-{os.getpid()}")
    shutil.copytree(root, temporary, copy_function=shutil.copy2)
    exported = tree_rows(temporary)
    if exported != rows: shutil.rmtree(temporary, ignore_errors=True); raise StateError("export verification failed")
    atomic_json(temporary / "export-manifest.json", {"schema_version": 1, "exported_at": iso(utc()), "source": str(root), "files": rows,
                                                       "explicit_exclusions": ["credentials", "tokens", "machine logs", "unrelated projects"], "authority_effect": "none"})
    temporary.replace(output)
    return {"check": False, "mutated": True, "output": str(output), "file_count": len(rows), "tree_sha256": tree_digest(rows)}

def status(root: Path) -> dict[str, Any]:
    root = resolve_state_root(root)
    service = {"choice": root / "state/choice-history.sqlite3", "cadence": root / "state/cadence.sqlite3",
               "mentorship": root / "state/mentorship.sqlite3", "archive": root / "archive/config.json"}
    overrides = {name: value for name in ("MIRA_CORE_CHOICE_DB", "MIRA_CORE_CADENCE_DB", "MIRA_MENTORSHIP_DB", "MIRA_CORE_ARCHIVE_CONFIG", "MIRA_CORE_JOURNAL_DRAFT_ROOT", "MIRA_CORE_CONTINUITY_INBOX") if (value := os.environ.get(name))}
    mixed = {name: value for name, value in overrides.items() if not is_within(Path(value), root)}
    return {"state_root": str(root), "exists": root.is_dir(), "services": {k: {"path": str(v), "exists": v.exists()} for k, v in service.items()},
            "overrides": overrides, "mixed_root_overrides": mixed, "mutation_ready": not mixed, "authority_effect": "none"}

def render(payload: dict[str, Any], format_name: str) -> None:
    if format_name == "json": print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for key, value in payload.items():
            if isinstance(value, (dict, list)): value = json.dumps(value, sort_keys=True)
            print(f"{key}: {value}")

def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Migrate and verify Mira Core local non-Git state.")
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("status", "quarantine-status"):
        sub = commands.add_parser(name); sub.add_argument("--root", type=Path); sub.add_argument("--format", choices=("text", "json"), default="text")
    sub = commands.add_parser("inventory"); sub.add_argument("--source", type=Path, required=True); sub.add_argument("--format", choices=("text", "json"), default="text")
    sub = commands.add_parser("migrate"); sub.add_argument("--source", type=Path, required=True); sub.add_argument("--target", type=Path); sub.add_argument("--check", action="store_true"); sub.add_argument("--format", choices=("text", "json"), default="text")
    sub = commands.add_parser("continuity-migrate"); sub.add_argument("--source", type=Path, required=True); sub.add_argument("--target", type=Path); sub.add_argument("--check", action="store_true"); sub.add_argument("--format", choices=("text", "json"), default="text")
    sub = commands.add_parser("continuity-verify"); sub.add_argument("--root", type=Path); sub.add_argument("--format", choices=("text", "json"), default="text")
    sub = commands.add_parser("verify"); sub.add_argument("--root", type=Path); sub.add_argument("--source-manifest", type=Path); sub.add_argument("--format", choices=("text", "json"), default="text")
    sub = commands.add_parser("export"); sub.add_argument("--root", type=Path); sub.add_argument("--output", type=Path, required=True); sub.add_argument("--check", action="store_true"); sub.add_argument("--format", choices=("text", "json"), default="text")
    return result

def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    try:
        root = resolve_state_root(getattr(args, "root", None))
        if args.command == "status": payload = status(root)
        elif args.command == "inventory": payload = inventory(args.source)
        elif args.command == "migrate": payload = migrate(args.source, resolve_state_root(args.target), check=args.check)
        elif args.command == "continuity-migrate": payload = migrate_continuity(args.source, resolve_state_root(args.target), check=args.check)
        elif args.command == "continuity-verify": payload = continuity_verify(root)
        elif args.command == "verify": payload = verify(root, args.source_manifest)
        elif args.command == "export": payload = export(root, args.output, check=args.check)
        else:
            payload = verify(root)
            receipt = payload.get("receipt", {})
            payload = {"status": receipt.get("status"), "cutover_at": receipt.get("cutover_at"),
                       "deletion_review_eligible_at": receipt.get("deletion_review_eligible_at"),
                       "source_unchanged": payload.get("source_unchanged"), "deletion_authority": "none"}
        render(payload, args.format)
        return 0 if payload.get("valid", True) else 1
    except (OSError, ValueError, KeyError, sqlite3.Error, StateError) as error:
        print(f"mira-state error: {error}", file=sys.stderr); return 2

if __name__ == "__main__":
    raise SystemExit(main())

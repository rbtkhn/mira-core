"""Private repository-local session preservation and frozen daily reading.

No source deletion, Git admission, Journal authorship, or scheduling occurs here.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import subprocess
import journal_calendar
from datetime import date
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TRANSCRIPTS = "archive/sessions/transcripts"
DAILY = "archive/sessions/daily"
LEGACY = "mira/continuity/captures/"
LINEAGE = TRANSCRIPTS + "/lineage.json"


def lineage_index(repo: Path, source_values: list[Any]) -> dict:
    """Retain explicit metadata observations; never infer parentage from prose."""
    import mira_continuity as continuity
    path = repo / LINEAGE
    previous = load(path) if path.exists() else {"schema_version": 1, "observations": []}
    observations = {digest(row): row for row in previous["observations"]}
    for source in source_values:
        metadata = continuity._read_session_meta(source.path)
        if not metadata:
            continue
        meta, _ = metadata
        parents = set()
        if meta.get("parent_thread_id"):
            parents.add(str(meta["parent_thread_id"]).lower())
        origin = meta.get("source")
        sub = origin.get("subagent", {}) if isinstance(origin, dict) else {}
        if isinstance(sub, dict):
            for value in sub.values():
                if isinstance(value, dict) and value.get("parent_thread_id"):
                    parents.add(str(value["parent_thread_id"]).lower())
        row = {"session_id": source.session_id, "parent_ids": sorted("MS-" + p for p in parents),
               "metadata_sha256": digest(meta)}
        observations[digest(row)] = row
    return {"schema_version": 1, "observations": [observations[k] for k in sorted(observations)]}


def conversation_groups(registry: dict, active_ids: set[str], lineage: dict) -> dict:
    owners = {s["id"]: s for s in registry["sessions"]}
    parents: dict[str, set[str]] = {}
    for row in lineage["observations"]:
        parents.setdefault(row["session_id"], set()).update(row["parent_ids"])
    groups: dict[str, list[str]] = {}
    unresolved = []
    for sid in sorted(active_ids):
        current, seen = sid, set()
        while owners.get(current, {}).get("source_kind") == "subagent":
            seen.add(current)
            choices = parents.get(current, set())
            reason = None
            if len(choices) != 1:
                reason = "missing-parent" if not choices else "conflicting-parents"
            else:
                parent = next(iter(choices))
                if parent in seen:
                    reason = "ancestry-cycle"
                elif parent not in owners:
                    reason = "unregistered-parent"
            if reason:
                unresolved.append({"session_id": sid, "at_session_id": current, "reason": reason})
                break
            current = parent
        else:
            if owners.get(current, {}).get("source_kind") not in {"vscode", "cli"}:
                unresolved.append({"session_id": sid, "at_session_id": current, "reason": "unknown-source-kind"})
            else:
                groups.setdefault(current, []).append(sid)
    return {"schema_version": 1, "lineage_sha256": digest(lineage),
            "primary_sessions": sum(owners[s].get("source_kind") in {"vscode", "cli"} for s in active_ids),
            "subagent_sessions": sum(owners[s].get("source_kind") == "subagent" for s in active_ids),
            "groups": [{"parent_session_id": p, "parent_active": p in active_ids, "session_ids": groups[p]}
                       for p in sorted(groups)], "unresolved": unresolved}


def digest(value: Any) -> str:
    return hashlib.sha256(encoded(value)).hexdigest()


def encoded(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def load(path: Path) -> Any:
    return json.loads(path.read_bytes())


def immutable(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as stream:
            stream.write(body)
    except FileExistsError:
        if path.read_bytes() != body:
            raise ValueError(f"Immutable session object collision: {path}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_bytes(encoded(value))
    temporary.replace(path)


def write_index(repo: Path, registry: dict) -> None:
    write_json(private_child(repo, TRANSCRIPTS + "/index.json"), registry)
    lines = ["# Preserved Codex sessions", "", "Private normalized captures; historical references remain stable.", "",
             "| Session | Started | Last observed | Captures |", "| --- | --- | --- | --- |"]
    for session in registry["sessions"]:
        links = []
        for cap in session["captures"]:
            relative = cap["path"].removeprefix(LEGACY).removeprefix(TRANSCRIPTS + "/")
            links.append(f"[{cap['id']}]({relative})")
        lines.append(f"| {session['id']} | {session['started_at']} | {session['last_observed_at']} | {'; '.join(links)} |")
    path = private_child(repo, TRANSCRIPTS + "/index.md")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def private_child(repo: Path, relative: str) -> Path:
    """Narrow exception: only the two explicitly ignored session payload trees."""
    if not any(relative.startswith(prefix + "/") for prefix in (TRANSCRIPTS, DAILY)):
        raise ValueError("Not a private session payload path")
    path = repo / relative
    if ".." in Path(relative).parts or not path.resolve().is_relative_to(repo.resolve()):
        raise ValueError("Session payload escapes repository")
    # Real repositories must exclude the exact target before writing bodies.
    if (repo / ".git").exists():
        result = subprocess.run(["git", "check-ignore", "-q", "--", relative], cwd=repo)
        if result.returncode:
            raise ValueError(f"Private session payload is not Git-ignored: {relative}")
        tracked = subprocess.run(["git", "ls-files", "--", relative], cwd=repo, capture_output=True)
        if tracked.returncode or tracked.stdout:
            raise ValueError("Private session payload is tracked or cannot be checked")
    return path


def approved_cwds(repo: Path) -> set[str]:
    def key(value: str | Path) -> str:
        return str(value).replace("\\", "/").rstrip("/").casefold()
    values = {key(repo.resolve())}
    if (repo / ".git").exists():
        result = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=repo, capture_output=True, text=True)
        if result.returncode:
            raise ValueError("Cannot establish worktree membership")
        values.update(key(line[9:]) for line in result.stdout.splitlines() if line.startswith("worktree "))
    config = repo / TRANSCRIPTS / "scope.json"
    if config.exists():
        # Explicit migration-reviewed historical roots; never infer from names.
        values.update(key(p) for p in load(config).get("approved_cwds", []))
    return values


def sources(repo: Path, roots: list[Path] | None = None) -> list[Any]:
    import mira_continuity as continuity
    allowed = approved_cwds(repo)
    registry = continuity.load_json(repo / "mira/continuity/session-registry.json", continuity.empty_registry())
    historical_ids = {s["codex_session_id"] for s in registry["sessions"]}
    found: dict[str, list[Any]] = {}
    roots = roots or continuity.default_source_roots()
    if not any(root.is_dir() for root in roots):
        raise ValueError("Codex transcript roots unavailable; cannot claim a complete census")
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.jsonl")):
            meta = continuity._read_session_meta(path)
            if not meta:
                continue
            row, timestamp = meta
            sid = str(row.get("id") or row.get("session_id") or "").casefold()
            cwd = continuity.canonical_path(str(row.get("cwd", "")))
            if cwd not in allowed and sid not in historical_ids:
                continue
            if not continuity.SESSION_ID_RE.fullmatch("MS-" + sid):
                raise ValueError("Invalid session identity")
            start = continuity.normalize_timestamp(row.get("timestamp") or timestamp)
            source = continuity.SessionSource(sid, start, continuity._last_timestamp(path, start), cwd,
                continuity._source_kind(row.get("source")), continuity.source_class(path), path.name, path)
            duplicate = False
            for previous in found.get(sid, []):
                a, b = previous.path.read_bytes(), path.read_bytes()
                if a == b:
                    duplicate = True
                    break
                # Codex can write a continuation segment with the same declared
                # identity. Preserve both only when their observation windows
                # are disjoint, or one is a byte-prefix snapshot of the other.
                disjoint = previous.last_observed_at < source.started_at or source.last_observed_at < previous.started_at
                if not disjoint and not (a.startswith(b) or b.startswith(a)):
                    raise ValueError(f"Conflicting overlapping raw sources for session {sid}")
            if not duplicate:
                found.setdefault(sid, []).append(source)
    return sorted((s for group in found.values() for s in group), key=lambda s: (s.started_at, s.session_id, s.source_name))


def preserve(repo: Path, source_values: list[Any], *, check: bool = False) -> tuple[dict, dict[Path, bytes]]:
    """Append normalized captures while preserving all historical registry entries."""
    import mira_continuity as continuity
    registry_path = repo / "mira/continuity/session-registry.json"
    original = registry_path.read_bytes() if registry_path.exists() else None
    registry = continuity.load_json(registry_path, continuity.empty_registry())
    known = {s["id"]: {c["source_sha256"] for c in s["captures"]} for s in registry["sessions"]}
    changed = [s for s in source_values if hashlib.sha256(s.path.read_bytes()).hexdigest() not in known.get(s.session_id, set())]
    updated, old_outputs, _ = continuity.expected_ingest(changed, registry=registry,
        repo_root=repo, continuity_root=repo / "mira/continuity")
    outputs = {}
    for path, body in old_outputs.items():
        relative = path.relative_to(repo).as_posix()
        target = private_child(repo, TRANSCRIPTS + "/" + relative.removeprefix(LEGACY))
        outputs[target] = body
    # New references use their initial physical location; existing ones remain identities.
    existing = {c["id"] for s in registry["sessions"] for c in s["captures"]}
    for session in updated["sessions"]:
        for capture in session["captures"]:
            if capture["id"] not in existing:
                capture["path"] = TRANSCRIPTS + "/" + capture["path"].removeprefix(LEGACY)
    if not check:
        for path, body in outputs.items():
            immutable(path, body)
        if original is not None and registry_path.read_bytes() != original:
            raise ValueError("Continuity registry changed during preservation")
        if updated != registry:
            write_json(registry_path, updated)
        write_index(repo, updated)
    return updated, outputs


def build(repo: Path, day: str, start: datetime, cutoff: datetime, end: datetime,
          registry: dict, *, overlay: dict[Path, bytes] | None = None, chunk_chars: int = 24000) -> tuple[dict, list[dict]]:
    calendar_day = date.fromisoformat(day)
    if calendar_day >= journal_calendar.TRANSITION_DAY and (start, end) != journal_calendar.day_bounds(calendar_day):
        raise ValueError("Checkpoint boundaries conflict with dated calendar")
    from repository_paths import resolve_repository_path
    if not start < cutoff <= end or start.tzinfo is None or cutoff.tzinfo is None:
        raise ValueError("Invalid checkpoint window")
    records: dict[tuple[str, str], dict] = {}
    census, gaps = [], []
    for session in registry["sessions"]:
        session_start = datetime.fromisoformat(session["started_at"].replace("Z", "+00:00"))
        session_end = datetime.fromisoformat(session["last_observed_at"].replace("Z", "+00:00"))
        if session_end < start or session_start >= cutoff:
            continue
        refs, eligible = [], set()
        for cap in session["captures"]:
            path = resolve_repository_path(repo, cap["path"])
            body = (overlay or {}).get(path)
            try:
                body = path.read_bytes() if body is None else body
                if hashlib.sha256(body).hexdigest() != cap["sha256"]:
                    raise ValueError("capture hash mismatch")
                rows = [json.loads(line) for line in gzip.decompress(body).splitlines()]
                if rows[0]["session_id"] != session["id"]:
                    raise ValueError("capture session mismatch")
            except (OSError, ValueError, KeyError) as error:
                gaps.append({"session_id": session["id"], "capture_id": cap["id"], "reason": type(error).__name__})
                continue
            selected = []
            undated = 0
            for row in rows[1:]:
                stamp = row.get("timestamp")
                if not stamp:
                    undated += 1
                    continue
                when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                if start <= when < cutoff:
                    key = (session["id"], row["record_id"])
                    value = {"session_id": session["id"], "record": row}
                    if key in records and records[key] != value:
                        raise ValueError("Conflicting historical record bytes")
                    records[key] = value
                    eligible.add(row["record_id"])
                    selected.append(row["record_id"])
            if selected:
                refs.append({"capture_id": cap["id"], "path": cap["path"], "sha256": cap["sha256"], "record_ids": selected})
            if undated:
                gaps.append({"session_id": session["id"], "capture_id": cap["id"],
                             "reason": "undated-records-cannot-be-assigned-to-day", "record_count": undated})
        if eligible:
            census.append({"session_id": session["id"], "record_count": len(eligible), "captures": refs})
    ordered = sorted(records.values(), key=lambda r: (r["record"]["timestamp"], r["session_id"], r["record"]["record_id"]))
    # Split serialized text, including oversized records, without discarding any character.
    text = "".join(encoded(r).decode() for r in ordered)
    chunks = [{"ordinal": n + 1, "text": text[i:i + chunk_chars]} for n, i in enumerate(range(0, len(text), chunk_chars))]
    checkpoint = {"schema_version": 1, "day": day, "timezone": journal_calendar.timezone_name(calendar_day),
        "start": start.isoformat(), "cutoff": cutoff.isoformat(), "end": end.isoformat(),
        "coverage": "partial" if gaps else "through-cutoff", "calendar_day_closed": cutoff == end,
        "sessions": census, "gaps": gaps, "record_count": len(ordered),
        "chunks": [{"ordinal": c["ordinal"], "sha256": digest(c)} for c in chunks],
        "reading_status": "not-yet-acknowledged", "backup_status": "not-verified"}
    if calendar_day >= journal_calendar.TRANSITION_DAY:
        checkpoint["calendar"] = journal_calendar.metadata(calendar_day)
    return checkpoint, chunks


def publish(repo: Path, checkpoint: dict, chunks: list[dict], *, check: bool = False) -> dict:
    identifier = digest(checkpoint)
    relative = f"{DAILY}/{checkpoint['day']}/{identifier}"
    target = private_child(repo, relative + "/checkpoint.json")
    if not check:
        for chunk in chunks:
            immutable(target.parent / f"chunk-{chunk['ordinal']:05d}.json", encoded(chunk))
        immutable(target, encoded(checkpoint))
    return {"required": True, "checkpoint_sha256": identifier, "checkpoint_path": relative + "/checkpoint.json",
        "chunk_count": len(chunks), "record_count": checkpoint["record_count"]}


def checked(repo: Path, contract: dict) -> tuple[dict, Path]:
    path = private_child(repo, str(contract["checkpoint_path"]))
    checkpoint = load(path)
    if digest(checkpoint) != contract["checkpoint_sha256"] or len(checkpoint["chunks"]) != contract["chunk_count"]:
        raise ValueError("Session checkpoint binding mismatch")
    calendar_day = date.fromisoformat(checkpoint["day"])
    if calendar_day >= journal_calendar.TRANSITION_DAY:
        expected = journal_calendar.metadata(calendar_day)
        if (checkpoint.get("calendar") != expected or checkpoint.get("timezone") != expected["timezone"]
                or datetime.fromisoformat(checkpoint["start"]) != datetime.fromisoformat(expected["start"])
                or datetime.fromisoformat(checkpoint["end"]) != datetime.fromisoformat(expected["end"])):
            raise ValueError("Checkpoint dated calendar binding mismatch")
    for ref in checkpoint["chunks"]:
        if digest(load(path.parent / f"chunk-{ref['ordinal']:05d}.json")) != ref["sha256"]:
            raise ValueError("Session reading chunk changed")
    from repository_paths import resolve_repository_path
    for session in checkpoint["sessions"]:
        for cap in session["captures"]:
            if hashlib.sha256(resolve_repository_path(repo, cap["path"]).read_bytes()).hexdigest() != cap["sha256"]:
                raise ValueError("Checkpoint capture changed")
    return checkpoint, path


def acknowledge(repo: Path, bundle: Path, session_id: str, packet_digest: str, ordinals: list[int]) -> dict:
    contract = load(bundle / "draft-contract.json")["session_reading"]
    checkpoint, path = checked(repo, contract)
    if packet_digest != contract["checkpoint_sha256"] or not re.fullmatch(r"MS-[0-9a-f-]{36}", session_id):
        raise ValueError("Invalid session reading acknowledgement")
    expected = [c["ordinal"] for c in checkpoint["chunks"]]
    ack_path = path.parent / f"reading-{session_id}.json"
    receipt = load(ack_path) if ack_path.exists() else {"checkpoint_sha256": packet_digest, "session_id": session_id, "chunks": []}
    for number in ordinals:
        if number in receipt["chunks"]:
            continue
        if len(receipt["chunks"]) >= len(expected) or number != expected[len(receipt["chunks"])]:
            raise ValueError("Read and acknowledge session chunks sequentially")
        receipt["chunks"].append(number)
    if receipt["chunks"] == expected:
        receipt.setdefault("completed_at", datetime.now(timezone.utc).isoformat())
    write_json(ack_path, receipt)
    return {"complete": receipt["chunks"] == expected, "acknowledgement_sha256": digest(receipt), "receipt": str(ack_path)}


def reading_failures(repo: Path, bundle: Path, metadata: dict) -> list[str]:
    try:
        contract = load(bundle / "draft-contract.json").get("session_reading")
        if not contract:
            return []
        checkpoint, path = checked(repo, contract)
        sid = metadata.get("author", {}).get("session_id", "")
        if not re.fullmatch(r"MS-[0-9a-f-]{36}", sid):
            raise ValueError("Invalid composing session")
        receipt = load(path.parent / f"reading-{sid}.json")
        if (receipt["checkpoint_sha256"] != contract["checkpoint_sha256"] or receipt["session_id"] != sid
                or receipt["chunks"] != [c["ordinal"] for c in checkpoint["chunks"]]
                or metadata.get("session_reading_ack_sha256") != digest(receipt)
                or metadata.get("session_checkpoint_sha256") != contract["checkpoint_sha256"]):
            raise ValueError("Complete daily transcript reading is required before composition")
        completed = datetime.fromisoformat(receipt["completed_at"].replace("Z", "+00:00"))
        authored = datetime.fromisoformat(metadata["authored_at"].replace("Z", "+00:00"))
        if completed > authored or completed > datetime.now(timezone.utc):
            raise ValueError("Session reading must precede authorship")
        if checkpoint["gaps"] and metadata.get("session_coverage_gaps_acknowledged") is not True:
            raise ValueError("Acknowledge partial transcript coverage explicitly")
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [str(error)]
    return []


def backup(repo: Path, destination: Path, *, check: bool = False) -> dict:
    """Content-addressed recovery snapshots; never propagate deletion."""
    from portable_paths import require_private_path
    destination = require_private_path(destination, label="session backup", repo_root=repo)
    entries = []
    files = [repo / "mira/continuity/session-registry.json"]
    for prefix in (TRANSCRIPTS, DAILY):
        if (repo / prefix).exists():
            files.extend(p for p in (repo / prefix).rglob("*") if p.is_file())
    for path in sorted(files):
        relative = path.relative_to(repo).as_posix()
        if path.is_symlink() or not path.resolve().is_relative_to(repo.resolve()):
            raise ValueError("Backup source escapes repository")
        body = path.read_bytes()
        sha = hashlib.sha256(body).hexdigest()
        if not check:
            immutable(destination / "objects" / sha, body)
        entries.append({"path": relative, "sha256": sha, "bytes": len(body)})
    # A changed index or body invalidates this snapshot rather than mixing generations.
    for entry in entries:
        if hashlib.sha256((repo / entry["path"]).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("Session state changed while backing up; retry")
    manifest = {"schema_version": 1, "entries": entries, "deletion_policy": "retain-all-snapshots"}
    identifier = digest(manifest)
    if not check:
        immutable(destination / "snapshots" / f"{identifier}.json", encoded(manifest))
    return {"snapshot_sha256": identifier, "file_count": len(entries),
            "bytes": sum(e["bytes"] for e in entries), "mutation": not check}


def restore(backup_root: Path, identifier: str, target: Path, *, check: bool = False) -> dict:
    """Restore only into a new external directory; never overwrite a checkout."""
    from portable_paths import require_private_path
    target = require_private_path(target, label="session restore")
    if not re.fullmatch(r"[0-9a-f]{64}", identifier):
        raise ValueError("Invalid backup snapshot")
    manifest = load(backup_root / "snapshots" / f"{identifier}.json")
    if digest(manifest) != identifier:
        raise ValueError("Backup manifest changed")
    if target.exists() and any(target.iterdir()):
        raise ValueError("Restore requires an empty external directory")
    # Validate everything before writing any destination file.
    for entry in manifest["entries"]:
        relative = entry["path"]
        if Path(relative).is_absolute() or ".." in Path(relative).parts or not (target / relative).resolve().is_relative_to(target):
            raise ValueError("Unsafe backup entry")
        body = (backup_root / "objects" / entry["sha256"]).read_bytes()
        if hashlib.sha256(body).hexdigest() != entry["sha256"]:
            raise ValueError("Backup object hash mismatch")
    if not check:
        for entry in manifest["entries"]:
            immutable(target / entry["path"], (backup_root / "objects" / entry["sha256"]).read_bytes())
    return {"snapshot_sha256": identifier, "verified_files": len(manifest["entries"]), "mutation": not check}

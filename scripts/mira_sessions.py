from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any, Iterable

from portable_paths import require_private_path


REPO_ROOT = Path(__file__).resolve().parent.parent
SHELF = REPO_ROOT / "archive" / "sessions"
REGISTRY = SHELF / "registry.json"
CONTINUITY = REPO_ROOT / "mira" / "continuity" / "session-registry.json"
PENDING = REPO_ROOT / ".mira-private" / "sessions" / "memorials" / "pending"
ARCHIVE_COLLECTION = "mira-session-memorials"
AUTHORITY_BOUNDARY = (
    "A memorial is inactive reflective interpretation: preservation does not imply present identity, "
    "truth, operator belief, activation, or permission."
)
HEADINGS = (
    "Occasion", "What Changed", "Attributed Decisions", "Corrections",
    "Unresolved Threads", "Supported Relational Significance", "Future Inheritance",
    "Omissions", "Authority and Privacy Boundary",
)
SIGNIFICANCE = {
    "consequential-decision", "correction", "method-change",
    "relational-development", "unresolved-inheritance",
}
ID_RE = re.compile(r"^MSM-[A-Za-z0-9][A-Za-z0-9-]{5,63}$")
VERSION_RE = re.compile(r"^MSMV-([A-Za-z0-9][A-Za-z0-9-]{5,63})-v([1-9][0-9]*)$")
SESSION_RE = re.compile(r"^MS-[0-9a-f-]{24,}$")
CAPTURE_RE = re.compile(r"^MC-[0-9a-f]{24}$")
RECORD_RE = re.compile(r"^MR-[0-9a-f]{24}$")
FILE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[A-Za-z0-9-]+-[a-z0-9]+(?:-[a-z0-9]+)*-v[1-9][0-9]*$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
SENSITIVE = (
    (re.compile(r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*\S+"), "secret or credential"),
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "contact data"),
    (re.compile(r"(?<!\d)(?:\+?1[-. (]*)?\d{3}[-. )]*\d{3}[-. ]*\d{4}(?!\d)"), "contact data"),
    (re.compile(r"(?i)(?:[A-Z]:\\(?:Users|private)\\|/(?:home|Users|private)/)"), "private path"),
    (re.compile(r"(?im)^\s*(?:user|assistant|system)\s*:\s+"), "transcript structure"),
)


class MemorialError(ValueError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MemorialError(f"invalid JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise MemorialError(f"JSON object required: {path}")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def continuity_index(repo_root: Path = REPO_ROOT) -> tuple[dict[str, Any], dict[str, tuple[dict[str, Any], dict[str, Any]]]]:
    registry = load_json(repo_root / "mira" / "continuity" / "session-registry.json")
    sessions: dict[str, Any] = {}
    captures: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for session in registry.get("sessions", []):
        if isinstance(session, dict) and isinstance(session.get("id"), str):
            sessions[session["id"]] = session
            for capture in session.get("captures", []):
                if isinstance(capture, dict) and isinstance(capture.get("id"), str):
                    captures[capture["id"]] = (session, capture)
    return sessions, captures


def capture_rows(capture: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    path = repo_root / str(capture.get("path", ""))
    if not path.is_file():
        raise MemorialError(f"missing Continuity capture: {capture.get('id')}")
    body = path.read_bytes()
    if digest_bytes(body) != capture.get("sha256"):
        raise MemorialError(f"Continuity capture digest mismatch: {capture.get('id')}")
    try:
        return [json.loads(line) for line in gzip.decompress(body).splitlines()]
    except (OSError, json.JSONDecodeError) as error:
        raise MemorialError(f"invalid Continuity capture: {capture.get('id')}") from error


def message_text(row: dict[str, Any]) -> str:
    if row.get("kind") != "message":
        return ""
    return " ".join(
        part["text"] for part in row.get("content", [])
        if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("text"), str)
    )


def normalized_tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.casefold())


def overlap_failure(markdown: str, rows: Iterable[dict[str, Any]], width: int = 20) -> bool:
    memorial = normalized_tokens(markdown)
    if len(memorial) < width:
        return False
    spans = {tuple(memorial[index:index + width]) for index in range(len(memorial) - width + 1)}
    for row in rows:
        tokens = normalized_tokens(message_text(row))
        if any(tuple(tokens[index:index + width]) in spans for index in range(len(tokens) - width + 1)):
            return True
    return False


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise MemorialError(f"{label} must be a list")
    return value


def validate_pair(markdown_path: Path, sidecar_path: Path, *, repo_root: Path = REPO_ROOT, pending: bool = False) -> dict[str, Any]:
    markdown = markdown_path.read_text(encoding="utf-8")
    sidecar = load_json(sidecar_path)
    failures: list[str] = []
    if sidecar.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    memorial_id = str(sidecar.get("memorial_id", ""))
    version_id = str(sidecar.get("version_id", ""))
    match = VERSION_RE.fullmatch(version_id)
    version = sidecar.get("version")
    if not ID_RE.fullmatch(memorial_id): failures.append("invalid memorial_id")
    if not match or match.group(1) != memorial_id.removeprefix("MSM-") or int(match.group(2)) != version:
        failures.append("version_id does not bind memorial_id and version")
    expected_stem = markdown_path.stem
    if not pending and (not FILE_RE.fullmatch(expected_stem) or sidecar_path.stem != expected_stem):
        failures.append("admitted filenames must match the governed version pattern")
    for heading in HEADINGS:
        if not re.search(rf"(?m)^## {re.escape(heading)}\s*$", markdown):
            failures.append(f"missing Markdown section: {heading}")
    if sidecar.get("markdown_sha256") != digest_bytes(markdown_path.read_bytes()):
        failures.append("Markdown digest mismatch")
    if not isinstance(sidecar.get("omissions"), str) or not sidecar["omissions"].strip():
        failures.append("honest omissions statement required")
    if sidecar.get("activation_posture") != "inactive": failures.append("activation_posture must be inactive")
    if sidecar.get("authority_boundary") != AUTHORITY_BOUNDARY: failures.append("authority boundary mismatch")
    if sidecar.get("evidence_class") != "session-memorial-interpretation": failures.append("invalid evidence class")
    reasons = require_list(sidecar.get("significance_reasons"), "significance_reasons")
    if not reasons or any(reason not in SIGNIFICANCE for reason in reasons): failures.append("invalid or absent significance reason")
    if not isinstance(sidecar.get("retention_reason"), str) or not sidecar["retention_reason"].strip(): failures.append("operator-supplied retention reason required")
    if not isinstance(sidecar.get("decision_attribution"), list) or not sidecar.get("decision_attribution") or any(
        not isinstance(item, dict) or item.get("actor") not in {"operator", "mira", "joint"} or not item.get("summary")
        for item in sidecar.get("decision_attribution", [])
    ): failures.append("invalid decision attribution")
    producer = sidecar.get("producer")
    if not isinstance(producer, dict) or not producer.get("kind") or not producer.get("runtime"):
        failures.append("composition producer and runtime required")
    for field in ("reopening_conditions", "counter_memory_refs"):
        if not isinstance(sidecar.get(field), list): failures.append(f"{field} must be a list")
    if not isinstance(sidecar.get("manual_privacy_review"), dict) or sidecar["manual_privacy_review"].get("completed") is not True:
        failures.append("completed manual privacy review required")
    for pattern, label in SENSITIVE:
        if pattern.search(markdown): failures.append(f"privacy scan rejected {label}")
    if pending:
        if sidecar.get("status") != "pending" or not sidecar.get("source_thread_id"):
            failures.append("pending pair requires status pending and source_thread_id")
        if sidecar.get("session_id") or sidecar.get("capture_refs") or sidecar.get("record_refs"):
            failures.append("pending pair cannot claim canonical Continuity references")
    else:
        if sidecar.get("status") != "admitted": failures.append("status must be admitted")
        session_id = str(sidecar.get("session_id", ""))
        if not SESSION_RE.fullmatch(session_id): failures.append("invalid session_id")
        sessions, captures = continuity_index(repo_root)
        if session_id not in sessions: failures.append("missing canonical Continuity session")
        selected_rows: list[dict[str, Any]] = []
        available_records: set[str] = set()
        capture_refs = require_list(sidecar.get("capture_refs"), "capture_refs")
        if not capture_refs: failures.append("at least one capture reference required")
        for capture_id in capture_refs:
            if not isinstance(capture_id, str) or not CAPTURE_RE.fullmatch(capture_id) or capture_id not in captures:
                failures.append(f"missing Continuity capture: {capture_id}"); continue
            owner, capture = captures[capture_id]
            if owner.get("id") != session_id: failures.append(f"capture belongs to another session: {capture_id}"); continue
            rows = capture_rows(capture, repo_root); selected_rows.extend(rows)
            available_records.update(str(row.get("record_id")) for row in rows if isinstance(row.get("record_id"), str))
        record_refs = require_list(sidecar.get("record_refs"), "record_refs")
        if not record_refs or any(not isinstance(item, str) or not RECORD_RE.fullmatch(item) or item not in available_records for item in record_refs):
            failures.append("missing or invalid material record reference")
        receipt = sidecar.get("operator_command_receipt")
        if not isinstance(receipt, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(receipt.get("sha256", ""))) or receipt.get("record_ref") not in available_records:
            failures.append("digest-bound direct-operator-command receipt required")
        elif not any(row.get("record_id") == receipt.get("record_ref") and row.get("role") == "user" for row in selected_rows):
            failures.append("operator command receipt must reference a user record")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(sidecar.get("entry_date", ""))) or not isinstance(sidecar.get("admitted_at"), str):
            failures.append("entry_date and admitted_at required")
        if selected_rows and overlap_failure(markdown, selected_rows): failures.append("substantial copied-message overlap detected")
        logical = str(sidecar.get("markdown_path", ""))
        if logical != f"archive/sessions/{markdown_path.name}": failures.append("markdown_path does not bind admitted shelf path")
    previous = sidecar.get("previous_version")
    if version == 1 and previous is not None: failures.append("v1 cannot name a previous version")
    if isinstance(version, int) and version > 1:
        if not isinstance(previous, dict) or not VERSION_RE.fullmatch(str(previous.get("version_id", ""))) or not re.fullmatch(r"[0-9a-f]{64}", str(previous.get("sidecar_sha256", ""))):
            failures.append("later version requires previous version identity and digest")
    return {"status": "passed" if not failures else "failed", "failures": sorted(set(failures)), "memorial_id": memorial_id, "version_id": version_id}


def registry_document(repo_root: Path | None = None) -> dict[str, Any]:
    return load_json((repo_root or REPO_ROOT) / "archive" / "sessions" / "registry.json")


def validate_registry(repo_root: Path = REPO_ROOT) -> list[str]:
    try: registry = registry_document(repo_root)
    except MemorialError as error: return [str(error)]
    failures: list[str] = []
    if registry.get("schema_version") != 1 or registry.get("collection_id") != ARCHIVE_COLLECTION: failures.append("invalid memorial registry header")
    seen_ids: set[str] = set(); seen_versions: set[str] = set()
    for memorial in registry.get("memorials", []):
        identity = memorial.get("memorial_id")
        if identity in seen_ids: failures.append(f"duplicate memorial identity: {identity}")
        seen_ids.add(identity)
        versions = memorial.get("versions", [])
        for index, item in enumerate(versions, start=1):
            version_id = item.get("version_id")
            if version_id in seen_versions: failures.append(f"duplicate memorial version: {version_id}")
            seen_versions.add(version_id)
            if item.get("version") != index: failures.append(f"non-monotonic version chain: {identity}")
            md = repo_root / str(item.get("markdown_path", "")); js = repo_root / str(item.get("sidecar_path", ""))
            if not md.is_file() or not js.is_file(): failures.append(f"missing memorial pair: {version_id}"); continue
            result = validate_pair(md, js, repo_root=repo_root)
            failures.extend(f"{version_id}: {message}" for message in result["failures"])
            if digest_bytes(js.read_bytes()) != item.get("sidecar_sha256"): failures.append(f"sidecar digest mismatch: {version_id}")
    return failures


def validate_command(args: argparse.Namespace) -> dict[str, Any]:
    if args.markdown or args.sidecar:
        if not args.markdown or not args.sidecar: raise MemorialError("validate requires both --markdown and --sidecar")
        return validate_pair(args.markdown, args.sidecar, pending=args.pending)
    failures = validate_registry()
    return {"status": "passed" if not failures else "failed", "failures": failures}


def pending_command(args: argparse.Namespace) -> dict[str, Any]:
    result = validate_pair(args.markdown, args.sidecar, repo_root=REPO_ROOT, pending=True)
    if result["failures"]: return result
    destination = require_private_path((args.output_root or PENDING).resolve(), label="session memorial pending root", repo_root=REPO_ROOT)
    target = destination / result["version_id"]
    planned = [str(target / args.markdown.name), str(target / args.sidecar.name)]
    if args.check: return {**result, "status": "ready", "mutation": False, "paths": planned}
    if target.exists(): raise MemorialError(f"pending artifact already exists: {target}")
    target.mkdir(parents=True)
    shutil.copyfile(args.markdown, target / args.markdown.name); shutil.copyfile(args.sidecar, target / args.sidecar.name)
    return {**result, "status": "prepared", "mutation": True, "paths": planned}


def admit_command(args: argparse.Namespace) -> dict[str, Any]:
    result = validate_pair(args.markdown, args.sidecar, repo_root=REPO_ROOT)
    if result["failures"]: return result
    sidecar = load_json(args.sidecar)
    expected = digest_bytes(args.authority_statement.encode("utf-8"))
    if sidecar["operator_command_receipt"]["sha256"] != expected:
        raise MemorialError("operator command receipt does not match --authority-statement")
    registry = registry_document(); identity = result["memorial_id"]
    memorial = next((item for item in registry["memorials"] if item["memorial_id"] == identity), None)
    if memorial is None:
        if sidecar["version"] != 1: raise MemorialError("new memorial identity must begin at v1")
        memorial = {"memorial_id": identity, "session_id": sidecar["session_id"], "versions": []}
    elif memorial["session_id"] != sidecar["session_id"]: raise MemorialError("memorial identity cannot change canonical session")
    expected_version = len(memorial["versions"]) + 1
    if sidecar["version"] != expected_version: raise MemorialError("version must extend the monotonic registry chain")
    if memorial["versions"]:
        previous = memorial["versions"][-1]
        if sidecar.get("previous_version") != {"version_id": previous["version_id"], "sidecar_sha256": previous["sidecar_sha256"]}:
            raise MemorialError("previous_version does not match current registry head")
    target_md = SHELF / args.markdown.name; target_js = SHELF / args.sidecar.name
    if target_md.exists() or target_js.exists(): raise MemorialError("silent overwrite forbidden")
    planned = [target_md.relative_to(REPO_ROOT).as_posix(), target_js.relative_to(REPO_ROOT).as_posix(), REGISTRY.relative_to(REPO_ROOT).as_posix()]
    if args.check: return {**result, "status": "ready", "mutation": False, "paths": planned}
    target_md.write_bytes(args.markdown.read_bytes()); target_js.write_bytes(args.sidecar.read_bytes())
    version_entry = {"version": sidecar["version"], "version_id": sidecar["version_id"], "markdown_path": planned[0], "sidecar_path": planned[1], "markdown_sha256": sidecar["markdown_sha256"], "sidecar_sha256": digest_bytes(target_js.read_bytes())}
    if memorial not in registry["memorials"]: registry["memorials"].append(memorial)
    memorial["versions"].append(version_entry); registry["memorials"].sort(key=lambda item: item["memorial_id"])
    write_json_atomic(REGISTRY, registry)
    return {**result, "status": "admitted", "mutation": True, "paths": planned}


def pending_counts(root: Path) -> tuple[int, int]:
    if not root.is_dir(): return 0, 0
    valid=invalid=0
    for directory in sorted({path.parent for path in root.rglob("*.json")} | {path.parent for path in root.rglob("*.md")}):
        jsons=list(directory.glob("*.json")); markdowns=list(directory.glob("*.md"))
        if len(jsons)!=1 or len(markdowns)!=1:
            invalid+=1; continue
        try: result=validate_pair(markdowns[0],jsons[0],repo_root=REPO_ROOT,pending=True)
        except (MemorialError,OSError,UnicodeError): invalid+=1; continue
        if result["failures"]: invalid+=1
        else: valid+=1
    return valid,invalid


def catalog_count() -> tuple[int, bool]:
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts")); from archive import configured_root_resolution, ARCHIVE_ROOT_ENV, storage_config
        from archive_store import ArtifactStore
        root, _ = configured_root_resolution(ARCHIVE_ROOT_ENV, required=False)
        if root is None: return 0, False
        with ArtifactStore(root, REPO_ROOT).connect() as connection:
            count = connection.execute("SELECT COUNT(*) FROM active_paths WHERE collection_id=?", (ARCHIVE_COLLECTION,)).fetchone()[0]
        return int(count), True
    except (OSError, sqlite3.Error, ValueError): return 0, False


def status_command(args: argparse.Namespace) -> dict[str, Any]:
    registry = registry_document(); versions = [version for item in registry.get("memorials", []) for version in item.get("versions", [])]
    failures = validate_registry(); pending, pending_invalid = pending_counts(args.pending_root or PENDING); catalog, configured = catalog_count()
    admitted = len(versions); superseded = sum(max(0, len(item.get("versions", [])) - 1) for item in registry.get("memorials", []))
    return {"status": "ok" if not failures and not pending_invalid else "invalid", "admitted": admitted, "pending": pending, "superseded": superseded, "invalid": len(failures) + pending_invalid, "registered_but_not_ingested": max(0, admitted - catalog), "catalog_configured": configured, "failures": failures}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Govern Mira session memorials")
    sub = root.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate"); p.add_argument("--markdown", type=Path); p.add_argument("--sidecar", type=Path); p.add_argument("--pending", action="store_true"); p.set_defaults(handler=validate_command)
    p = sub.add_parser("prepare-pending"); p.add_argument("--markdown", type=Path, required=True); p.add_argument("--sidecar", type=Path, required=True); p.add_argument("--output-root", type=Path); p.add_argument("--check", action="store_true"); p.set_defaults(handler=pending_command)
    p = sub.add_parser("admit"); p.add_argument("--markdown", type=Path, required=True); p.add_argument("--sidecar", type=Path, required=True); p.add_argument("--authority-statement", required=True); p.add_argument("--check", action="store_true"); p.set_defaults(handler=admit_command)
    p = sub.add_parser("status"); p.add_argument("--pending-root", type=Path); p.set_defaults(handler=status_command)
    for p in sub.choices.values(): p.add_argument("--json", action="store_true")
    return root


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    try: result = args.handler(args)
    except (MemorialError, OSError, KeyError, TypeError, ValueError) as error:
        print(f"mira-sessions error: {error}", file=sys.stderr); return 1
    print(canonical(result) if args.json else "\n".join(f"{key}={canonical(value) if isinstance(value, (dict, list)) else value}" for key, value in result.items()))
    return 0 if result.get("status") not in {"failed", "invalid"} else 1


if __name__ == "__main__": raise SystemExit(main())

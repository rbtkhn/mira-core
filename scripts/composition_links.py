"""Explicit, read-only Tower/Study lineage. No Library membership is inferred."""
from __future__ import annotations

import hashlib
import json
import re
import notebook_paths as locations
from pathlib import Path, PurePosixPath

SCHEMA = "mira-composition-v1"
KINDS = {"notes": "note", "essays": "essay", "letters": "letter"}


def resolve(repo, ref, artifact=False):
    if not isinstance(ref, str) or not ref or "\\" in ref or ":" in ref:
        raise ValueError("Use a repository-relative POSIX reference")
    parts = PurePosixPath(ref).parts
    if ref.startswith("/") or any(p in {"..", ".git"} for p in parts):
        raise ValueError("Unsafe composition reference")
    path = (repo / ref).resolve()
    if not path.is_relative_to(repo.resolve()):
        raise ValueError("Reference escapes repository")
    if artifact:
        if len(parts) < 3 or parts[0] != "archive" or parts[1] not in KINDS or path.suffix != ".md":
            raise ValueError("Composition must be on the notes, essays, or letters shelf")
    else:
        import strategy_notebook as notebook
        root = notebook.domain(repo).resolve() / "work"
        if not (path.is_relative_to(locations.root(repo).resolve()) or path.is_relative_to(root / "strategy-notebook") or
                (path.is_relative_to(root / "daily") and path.name == "strategy-notebook.md")):
            raise ValueError("Origin must be a Strategy Notebook record")
    return path if artifact else locations.resolve(repo, ref)


def binding(repo, value, artifact=False):
    if not isinstance(value, dict) or not re.fullmatch(r"[a-f0-9]{64}", str(value.get("sha256", ""))):
        raise ValueError("Binding requires ref and byte SHA-256")
    path = resolve(repo, value.get("ref"), artifact)
    current = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return {"ref": value["ref"], "sha256": value["sha256"], "current_sha256": current,
            "current_ref": path.relative_to(repo.resolve()).as_posix(), "status": "missing" if current is None else "matched" if current == value["sha256"] else "changed"}


def inspect(repo, ref):
    path = resolve(repo, ref, True)
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    blocks = re.findall(r"<!--\s*mira-composition\s*\n(.*?)-->", text, re.S)
    if not blocks:
        if "<!-- mira-composition" in text:
            raise ValueError("Malformed composition metadata")
        return {"path": ref, "status": "unlinked"}
    if len(blocks) != 1:
        raise ValueError("Exactly one composition metadata block is allowed")
    meta = json.loads(blocks[0])
    if not isinstance(meta, dict) or meta.get("schema") != SCHEMA or meta.get("kind") != KINDS[PurePosixPath(ref).parts[1]]:
        raise ValueError("Invalid composition schema or shelf kind")
    if not isinstance(meta.get("summary"), str) or not meta["summary"].strip():
        raise ValueError("Authored connection summary required")
    if "return_question" in meta and (not isinstance(meta["return_question"], str) or not meta["return_question"].strip()):
        raise ValueError("Return question must be nonempty text")
    if not isinstance(meta.get("origins"), list) or not meta["origins"]:
        raise ValueError("At least one explicit origin is required")
    origins = [binding(repo, row) for row in meta["origins"]]
    if len({row["ref"] for row in origins}) != len(origins):
        raise ValueError("Duplicate origin")
    return {"path": ref, "status": "linked", "sha256": hashlib.sha256(raw).hexdigest(),
            "kind": meta["kind"], "summary": meta["summary"],
            "return_question": meta.get("return_question"), "origins": origins}


def inventory(repo):
    rows, gaps = [], []
    for path in sorted(p for shelf in KINDS for p in (repo / "archive" / shelf).rglob("*.md")):
        ref = path.relative_to(repo).as_posix()
        try:
            row = inspect(repo, ref)
            if row["status"] == "linked":
                rows.append(row)
        except (OSError, ValueError) as error:
            gaps.append({"path": ref, "reason": str(error)})
    return rows, gaps


def search(repo, notebook_ref=None, artifact_ref=None, limit=10, catalog=None):
    if bool(notebook_ref) == bool(artifact_ref):
        raise ValueError("Choose exactly one notebook or artifact reference")
    if notebook_ref:
        resolve(repo, notebook_ref)
    result = {"schema": SCHEMA, "artifacts": [], "responses": [], "gaps": [], "omitted": [],
              "authority": "explicit authored lineage; not evidence or Library membership"}
    paths = [resolve(repo, artifact_ref, True)] if artifact_ref else []
    if notebook_ref:
        rows, gaps = catalog if catalog is not None else inventory(repo)
        result["artifacts"] = [r for r in rows if any(locations.identity(repo, b["ref"]) == locations.identity(repo, notebook_ref) for b in r["origins"])]
        result["gaps"].extend(gaps)
    for path in paths:
        ref = path.relative_to(repo.resolve()).as_posix()
        try:
            row = inspect(repo, ref)
            if artifact_ref or any(locations.identity(repo, b["ref"]) == locations.identity(repo, notebook_ref) for b in row.get("origins", [])):
                result["artifacts"].append(row)
        except (OSError, ValueError) as error:
            result["gaps"].append({"path": ref, "reason": str(error)})
    if artifact_ref:
        import strategy_notebook as notebook
        for path in sorted(notebook.contribution_paths(repo)):
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
                if row.get("content_sha256") != notebook.digest({k: v for k, v in row.items() if k != "content_sha256"}):
                    raise ValueError("Contribution integrity mismatch")
                for b in row.get("composition_refs", []):
                    if b.get("ref") == artifact_ref:
                        result["responses"].append({"path": path.relative_to(repo).as_posix(),
                            "date": row["date"], "effect": b["effect"], "reason": b["reason"],
                            "binding": binding(repo, b, True), "correction_links": row["correction_links"]})
            except (OSError, ValueError, KeyError, TypeError) as error:
                result["gaps"].append({"path": path.relative_to(repo).as_posix(), "reason": str(error)})
    for key in ("artifacts", "responses", "gaps"):
        if len(result[key]) > limit:
            result["omitted"].append({"kind": key, "count": len(result[key]) - limit, "reason": "result budget"})
            result[key] = result[key][:limit]
        kept, budget = [], 12000
        for row in result[key]:
            size = len(json.dumps(row, ensure_ascii=False))
            if size <= budget:
                kept.append(row)
                budget -= size
            else:
                result["omitted"].append({"kind": key, "path": row.get("path"), "reason": "complete record exceeds character budget"})
        result[key] = kept
    return result


def validate_responses(repo, rows, correction_links):
    if not isinstance(rows, list):
        raise ValueError("composition_refs must be a list")
    for row in rows:
        checked = binding(repo, row, True)
        if checked["status"] != "matched":
            raise ValueError("Reviewed composition is missing or changed")
        if row.get("effect") not in {"considered", "changed", "no-change"} or not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise ValueError("Composition response requires effect and reason")
        artifact = inspect(repo, row["ref"])
        if artifact["status"] != "linked":
            raise ValueError("Reviewed composition must declare its origins")
        if row["effect"] == "changed" and not {locations.identity(repo, p) for p in correction_links}.intersection(locations.identity(repo, b["ref"]) for b in artifact["origins"]):
            raise ValueError("Changed judgment must link a corrected origin")

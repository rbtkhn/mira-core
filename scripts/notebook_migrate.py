"""Explicit phased, byte-preserving Notebook relocation. No private-store access."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import notebook_paths as paths
from repository_paths import resolve_geopolitics_reference


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(repo):
    old = resolve_geopolitics_reference(repo, "geopolitics")
    rows = []
    for p in sorted((old / "work/strategy-notebook").rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(old / "work/strategy-notebook")
        dest = paths.root(repo) / ("monthly" if len(rel.parts) == 1 and p.stem[:4].isdigit() else "") / rel
        rows.append({"old_path": p.relative_to(repo).as_posix(), "new_path": dest.relative_to(repo).as_posix(), "sha256": sha(p)})
    for p in sorted((old / "work/daily").glob("????-??-??/strategy-notebook.md")):
        rows.append({"old_path": p.relative_to(repo).as_posix(), "new_path": f"mira/strategy-notebook/daily/{p.parent.name}.md", "sha256": sha(p)})
    return rows


def run(repo, phase):
    repo = Path(repo).resolve()
    manifest = paths.root(repo) / "relocations.json"
    rows = paths.relocations(repo) if manifest.exists() else inventory(repo)
    if not rows:
        raise ValueError("No Notebook relocation inventory")
    # Preflight every row before any mutation; all paths are bounded and checked.
    for row in rows:
        src, dst = paths.safe(repo, row["old_path"]), paths.safe(repo, row["new_path"])
        if not dst.is_relative_to(paths.root(repo).resolve()):
            raise ValueError("Destination outside Notebook")
        for p in (src, dst):
            if p.exists() and sha(p) != row["sha256"]:
                raise ValueError(f"Relocation parity mismatch: {p}")
        if not src.exists() and not dst.exists():
            raise ValueError(f"Missing both copies: {src}")
        if phase != "transfer" and not dst.exists():
            raise ValueError(f"Transfer incomplete: {dst}")
    if phase == "transfer":
        # Persist the plan before copying so an interrupted transfer is reconstructable.
        if not manifest.exists():
            from strategy_notebook import create_json
            create_json(manifest, {"schema_version": 1, "files": rows})
        for row in rows:
            src, dst = paths.safe(repo, row["old_path"]), paths.safe(repo, row["new_path"])
            if not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    elif phase == "receipt":
        from strategy_notebook import create_json
        receipt = paths.root(repo) / "migration-receipt.json"
        value = {"schema_version": 1, "status": "parity-verified", "files": len(rows), "manifest_sha256": sha(manifest)}
        if receipt.exists():
            if json.loads(receipt.read_text()) != value:
                raise ValueError("Existing receipt mismatch")
        else:
            create_json(receipt, value)
    elif phase == "cleanup":
        receipt = paths.root(repo) / "migration-receipt.json"
        if not receipt.exists() or json.loads(receipt.read_text()).get("manifest_sha256") != sha(manifest):
            raise ValueError("Matching parity receipt required")
        # All rows were checked above; only exact inventoried files are removed.
        for row in rows:
            paths.safe(repo, row["old_path"]).unlink(missing_ok=True)
    return {"phase": phase, "status": "complete", "files": len(rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["transfer", "verify", "receipt", "cleanup"])
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(run(args.repo, args.phase)))

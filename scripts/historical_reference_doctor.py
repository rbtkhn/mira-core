"""Read-only health report for the bounded historical-reference workflow."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "archive" / "geopolitics" / "source-manifest.json"
SKILL = ROOT / ".codex" / "skills" / "historical-reference"
MIRROR = Path.home() / ".codex" / "skills" / "historical-reference"

def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else f"ERROR: {result.stderr.strip()}"

def files_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        digest.update(item.relative_to(path).as_posix().encode()); digest.update(item.read_bytes())
    return digest.hexdigest()

def report() -> dict:
    data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    rows = data.get("sources", [])
    paths = [str(row.get("local_path") or "") for row in rows]
    duplicates = sorted({p for p in paths if paths.count(p) > 1})
    missing = sorted(p for p in paths if not (ROOT / p).is_file())
    focused = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_historical_reference_skill.py"], cwd=ROOT, capture_output=True, text=True)
    taxonomy = subprocess.run([sys.executable, "scripts/validate_historical_reference_taxonomy.py"], cwd=ROOT, capture_output=True, text=True)
    return {
        "git": {"branch": git("branch", "--show-current") or "DETACHED", "head": git("rev-parse", "--short=12", "HEAD"), "status_lines": len(git("status", "--porcelain=v1").splitlines()), "remote": git("remote", "get-url", "origin")},
        "manifest": {"rows": len(rows), "declared_count": data.get("source_count"), "duplicate_paths": duplicates, "missing_archive_paths": missing},
        "skill": {"canonical_exists": SKILL.exists(), "canonical_hash": files_hash(SKILL) if SKILL.exists() else None, "mirror_exists": MIRROR.exists(), "mirror_hash": files_hash(MIRROR) if MIRROR.exists() else None, "mirror_status": "IN_SYNC" if SKILL.exists() and MIRROR.exists() and files_hash(SKILL) == files_hash(MIRROR) else "DRIFT_OR_MISSING"},
        "runtime": {"python": sys.executable, "python_version": sys.version.split()[0], "focused_tests_exit": focused.returncode, "focused_tests_tail": focused.stdout.strip().splitlines()[-1] if focused.stdout.strip() else focused.stderr.strip().splitlines()[-1] if focused.stderr.strip() else "", "taxonomy_validation_exit": taxonomy.returncode, "taxonomy_validation_tail": taxonomy.stdout.strip().splitlines()[-1] if taxonomy.stdout.strip() else taxonomy.stderr.strip().splitlines()[-1] if taxonomy.stderr.strip() else ""},
        "generated_outputs": {"work_root_exists": (ROOT / "narrative-geopolitics" / "work" / "historical-reference").exists()},
        "checks": {"manifest_valid": data.get("source_count") == len(rows) and not duplicates and not missing, "skill_mirror_in_sync": SKILL.exists() and MIRROR.exists() and files_hash(SKILL) == files_hash(MIRROR), "focused_tests_pass": focused.returncode == 0, "taxonomy_valid": taxonomy.returncode == 0},
    }

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--json", action="store_true"); args = parser.parse_args(); payload = report()
    if args.json: print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Historical-reference doctor: {payload['checks']}")
        print(f"Manifest: {payload['manifest']['rows']} rows; missing={len(payload['manifest']['missing_archive_paths'])}; duplicates={len(payload['manifest']['duplicate_paths'])}")
        print(f"Skill mirror: {payload['skill']['mirror_status']}")
        print(f"Git: {payload['git']['branch']} @ {payload['git']['head']}; dirty lines={payload['git']['status_lines']}")
    return 0 if all(payload["checks"].values()) else 1

if __name__ == "__main__": raise SystemExit(main())

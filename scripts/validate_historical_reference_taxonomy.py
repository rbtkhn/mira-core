"""Validate native historical-reference taxonomies and generated crosswalks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_ROOT = ROOT / ".codex" / "skills" / "historical-reference" / "references" / "taxonomies"
VALID_LIFECYCLES = {"proposed", "active", "merged", "split", "deprecated", "superseded"}
VALID_CONFIDENCE = {"suggested", "low", "medium", "high"}
REQUIRED_REFERENCE_FIELDS = {"label", "parent", "pattern", "mechanism"}
VALID_MECHANISMS = {"M-FR-001", "M-FR-002", "M-FR-003", "M-FR-004", "M-FR-005"}

def validate_taxonomy(path: Path) -> list[str]:
    failures: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path}: invalid JSON: {exc}"]
    for field in ("version", "voice", "lifecycle", "counted_unit", "references"):
        if field not in data:
            failures.append(f"{path}: missing top-level field {field}")
    if data.get("lifecycle") not in VALID_LIFECYCLES:
        failures.append(f"{path}: invalid lifecycle {data.get('lifecycle')!r}")
    refs = data.get("references")
    if not isinstance(refs, dict) or not refs:
        failures.append(f"{path}: references must be a non-empty object")
        return failures
    for ref_id, item in refs.items():
        if not isinstance(ref_id, str) or not ref_id or ref_id != ref_id.lower():
            failures.append(f"{path}: reference ID must be stable lowercase text: {ref_id!r}")
        if not isinstance(item, dict):
            failures.append(f"{path}: reference {ref_id} must be an object")
            continue
        missing = REQUIRED_REFERENCE_FIELDS - set(item)
        failures.extend(f"{path}: reference {ref_id} missing {field}" for field in sorted(missing))
        if item.get("mechanism") not in {"coercion", "diplomacy", "power", "competence", "legitimacy"}:
            failures.append(f"{path}: reference {ref_id} has invalid mechanism {item.get('mechanism')!r}")
        if not isinstance(item.get("pattern"), str) or not item.get("pattern"):
            failures.append(f"{path}: reference {ref_id} has empty detection pattern")
    return failures

def validate_crosswalk(path: Path) -> list[str]:
    failures: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path}: invalid JSON: {exc}"]
    for index, item in enumerate(data.get("records", [])):
        for crosswalk in item.get("crosswalk_suggestions", []):
            prefix = f"{path}: record {item.get('occurrence_id', index)} crosswalk"
            for field in ("target", "confidence", "rationale", "conflict_status", "review_status"):
                if not crosswalk.get(field):
                    failures.append(f"{prefix} missing {field}")
            if crosswalk.get("confidence") not in VALID_CONFIDENCE:
                failures.append(f"{prefix} has invalid confidence {crosswalk.get('confidence')!r}")
            if crosswalk.get("conflict_status") not in {"unreviewed", "clear", "conflict"}:
                failures.append(f"{prefix} has invalid conflict_status {crosswalk.get('conflict_status')!r}")
    return failures

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--taxonomy-dir", type=Path, default=TAXONOMY_ROOT); parser.add_argument("--run", type=Path, action="append", default=[]); args = parser.parse_args()
    failures = []
    files = sorted(args.taxonomy_dir.glob("*.json"))
    if not files:
        failures.append(f"{args.taxonomy_dir}: no taxonomy files found")
    for path in files:
        failures.extend(validate_taxonomy(path))
    for path in args.run:
        failures.extend(validate_crosswalk(path))
    if failures:
        print("\n".join(failures)); return 1
    print(f"Validated {len(files)} taxonomy file(s) and {len(args.run)} run crosswalk file(s)")
    return 0

if __name__ == "__main__": raise SystemExit(main())

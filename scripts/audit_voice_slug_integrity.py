from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import voice_indexes
import voice_metadata
from repository_paths import resolve_geopolitics_reference


ROOT = voice_metadata.REPO_ROOT
QUEUE_ROOT = resolve_geopolitics_reference(ROOT, "geopolitics") / "work" / "capture" / "youtube"


def classify(value: str, shelves: set[str]) -> str:
    canonical = voice_metadata.canonical_slug(value)
    if canonical != value:
        return "alias"
    if canonical not in shelves and canonical not in {"unknown", ""}:
        return "unknown/unindexed"
    return "canonical"


def audit(*, write: bool = False) -> dict[str, Any]:
    manifest = voice_metadata.load_manifest()
    shelves = set(voice_indexes.shelves())
    findings: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    scanned = 0

    for row in manifest.get("sources", []):
        path = str(row.get("local_path") or "")
        before = list(row.get("voice_slugs") or [])
        for value in before:
            scanned += 1
            canonical = voice_metadata.canonical_slug(str(value))
            findings.append({"file": "archive/sources/geopolitics/source-manifest.json", "field": "voice_slugs", "record": path, "observed": value, "canonical": canonical, "status": classify(str(value), shelves), "safe": canonical != value})
        target = ROOT / path
        if not target.exists():
            continue
        original = target.read_bytes()
        updated, changes, preserved = voice_metadata.canonicalize_frontmatter_bytes(original)
        for change in changes:
            scanned += 1
            findings.append({"file": path, "field": change["field"], "record": path, "observed": change["before"], "canonical": change["after"], "status": "alias", "safe": preserved})
        if changes and not preserved:
            conflicts.append({"file": path, "reason": "front-matter rewrite would not preserve body"})
        if write and changes and preserved:
            target.write_bytes(updated)

    for queue_path in sorted(QUEUE_ROOT.glob("*.jsonl")) if QUEUE_ROOT.exists() else []:
        rows = []
        changed = False
        for line in queue_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            value = str(row.get("expected_voice") or "")
            if value and value != "unknown":
                scanned += 1
                canonical = voice_metadata.canonical_slug(value)
                findings.append({"file": queue_path.relative_to(ROOT).as_posix(), "field": "expected_voice", "record": row.get("url", ""), "observed": value, "canonical": canonical, "status": classify(value, shelves), "safe": canonical != value})
                if write and canonical != value:
                    row["expected_voice"] = canonical
                    changed = True
            rows.append(row)
        if write and changed:
            queue_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8", newline="\n")

    manifest_report = voice_metadata.inspect_metadata(manifest)
    if write and not manifest_report["failures"]:
        original_manifest = voice_metadata.MANIFEST_PATH.read_bytes()
        for row in manifest.get("sources", []):
            row["voice_slugs"] = voice_metadata.canonicalize_slugs(list(row.get("voice_slugs") or []))
        updated_manifest = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        if updated_manifest != original_manifest:
            voice_metadata.write_manifest(manifest)
        index_report = voice_indexes.reconcile(manifest, write=True)
    else:
        index_report = voice_indexes.reconcile(manifest, write=False)

    alias_findings = [item for item in findings if item["status"] == "alias"]
    unknown_findings = [item for item in findings if item["status"] == "unknown/unindexed"]
    return {
        "mode": "write" if write else "check",
        "scanned_fields": scanned,
        "findings": findings,
        "aliases": alias_findings,
        "unknown_unindexed": unknown_findings,
        "conflicts": conflicts + [{"reason": item} for item in manifest_report["failures"]],
        "safe_repairs": sum(1 for item in alias_findings if item["safe"]),
        "index_report": index_report,
        "post_repair_clean": not write and not alias_findings and not conflicts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit and safely canonicalize archive voice-slug fields.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = audit(write=args.write)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"mode={report['mode']}")
        print(f"scanned_fields={report['scanned_fields']}")
        print(f"aliases={len(report['aliases'])}")
        print(f"unknown_unindexed={len(report['unknown_unindexed'])}")
        print(f"conflicts={len(report['conflicts'])}")
        print(f"safe_repairs={report['safe_repairs']}")
        for item in report["aliases"]:
            print(f"ALIAS {item['file']}:{item['field']} {item['observed']} -> {item['canonical']}")
    return 1 if report["conflicts"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

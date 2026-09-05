from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import voice_metadata
from repository_paths import resolve_geopolitics_reference


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canonicalize alias-affected voice metadata without changing source bodies.")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--date", help="Limit to one publication date.")
    scope.add_argument("--all", action="store_true", help="Inspect all manifest rows.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Report drift without writing.")
    mode.add_argument("--write", action="store_true", help="Apply canonical metadata changes.")
    parser.add_argument("--receipt", type=Path, help="Optional receipt path; --all --write defaults to work/migrations.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    # Resolve the default destination before apply_metadata can modify sources.
    # Explicit receipts and archive-only checks do not require a domain root.
    receipt = args.receipt
    if args.write and args.all and receipt is None:
        receipt = resolve_geopolitics_reference(
            voice_metadata.REPO_ROOT,
            f"geopolitics/work/migrations/canonical-voice-metadata-{date.today().isoformat()}.json",
        )
    manifest = voice_metadata.load_manifest()
    run_date = None if args.all else args.date
    report = (
        voice_metadata.apply_metadata(manifest, run_date=run_date)
        if args.write
        else voice_metadata.inspect_metadata(manifest, run_date=run_date)
    )
    if args.write and not report["failures"] and report["changes"]:
        voice_metadata.write_manifest(manifest)
        if receipt:
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    payload = {"mode": "write" if args.write else "check", "date": run_date, **report}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"metadata_changes={len(report['changes'])}")
        print(f"failures={len(report['failures'])}")
        for item in report["failures"]:
            print(f"FAIL {item}")
        for item in report["changes"]:
            print(f"CHANGE {item['local_path']}")
    if report["failures"] or (args.check and report["changes"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

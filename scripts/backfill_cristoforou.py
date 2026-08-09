"""Bounded, explicit-host backfill for three The Duran sources."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "narrative-geopolitics" / "archive" / "source-manifest.json"
TARGETS = {
    "narrative-geopolitics/archive/sources/2026-06-22/source-duran-mercouris-us-iran-ceasefire-talks-conflict-round-3-2026-06-22.md",
    "narrative-geopolitics/archive/sources/2026-06-23/source-duran-mercouris-rubicon-crossed-zelensky-targets-belarus-2026-06-23.md",
    "narrative-geopolitics/archive/sources/2026-06-27/source-duran-mercouris-russia-frontline-advance-putin-messaging-woes-lavrov-ww3-warning-ignored-2026-06-27.md",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    changed = []
    failures = []
    for row in manifest.get("sources", []):
        if row.get("local_path") not in TARGETS:
            continue
        voices = list(row.get("voice_slugs") or [])
        if "cristoforou" not in voices:
            voices.append("cristoforou")
        roles = dict(row.get("voice_roles") or {})
        statuses = dict(row.get("role_status") or {})
        bases = dict(row.get("role_basis") or {})
        roles["cristoforou"] = ["host"]
        statuses["cristoforou"] = "provisional"
        bases["cristoforou"] = "explicit_host_frontmatter"
        row.update({"voice_slugs": voices, "voice_roles": roles, "role_status": statuses, "role_basis": bases, "host_slug": "the-duran", "host_kind": "channel"})
        changed.append(row["local_path"])
    missing = sorted(TARGETS - set(changed))
    failures.extend(f"target missing from manifest: {path}" for path in missing)
    if args.write and not failures:
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"targets": sorted(TARGETS), "changed": sorted(changed), "failures": failures, "write": bool(args.write and not failures)}, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

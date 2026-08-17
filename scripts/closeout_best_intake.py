from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive" / "geopolitics"
SOURCES = ARCHIVE / "sources"
MANIFEST = ARCHIVE / "source-manifest.json"
def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Narrative Geopolitics best-intake batch.")
    parser.add_argument("--start-date", default="2026-01-01")
    parser.add_argument("--end-date", default="2026-07-31")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = manifest.get("sources", [])
    failures: list[str] = []
    paths = [row.get("local_path", "") for row in rows]
    failures.extend(f"duplicate local_path: {path}" for path, count in Counter(paths).items() if path and count > 1)
    urls = [row.get("source_url", "") for row in rows if row.get("source_url")]
    failures.extend(f"duplicate source_url: {url}" for url, count in Counter(urls).items() if count > 1)
    manifest_paths = set()
    for row in rows:
        path = row.get("local_path", "")
        if path:
            manifest_paths.add(ROOT / path)
            file_path = ROOT / path
            if not file_path.is_file():
                failures.append(f"manifest file missing: {path}")
            elif not file_path.read_text(encoding="utf-8", errors="replace").strip():
                failures.append(f"empty archive file: {path}")
        slug = row.get("host_slug")
        if slug == "reason-to-resist":
            failures.append(f"noncanonical host slug: {path}")
    archive_paths = set(SOURCES.rglob("*.md"))
    failures.extend(f"unmanifested archive file: {path.relative_to(ROOT)}" for path in sorted(archive_paths - manifest_paths))
    failures.extend(f"manifest-only archive path: {path.relative_to(ROOT)}" for path in sorted(manifest_paths - archive_paths))
    start, end = args.start_date[:7], args.end_date[:7]
    months = sorted({row.get("date", "")[:7] for row in rows if start <= row.get("date", "")[:7] <= end})
    print(f"manifest_sources={len(rows)}")
    print(f"archive_markdown_files={len(archive_paths)}")
    print(f"checked_months={','.join(months)}")
    if failures:
        print(f"closeout_failures={len(failures)}")
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("closeout_status=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

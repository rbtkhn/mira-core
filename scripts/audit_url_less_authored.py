"""Inspect URL-less authored records for explicit provenance clues."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter

from role_aware_archive import load_manifest, source_frontmatter_url


def frontmatter(path: str) -> dict[str, str]:
    try:
        text = open(path, encoding="utf-8-sig").read()
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    values: dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip("\"'")
    return values


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    result = []
    containers: Counter[str] = Counter()
    for row in load_manifest().get("sources", []):
        authored = str(row.get("source_class", "")).casefold().startswith("authored")
        if not authored or row.get("source_url") or source_frontmatter_url(row) or row.get("publication_slug"):
            continue
        meta = frontmatter(row.get("local_path", ""))
        containers[meta.get("show_title") or meta.get("show") or meta.get("host") or "none"] += 1
        result.append({"date": row.get("date"), "title": row.get("title"), "path": row.get("local_path"), "source_class": row.get("source_class"), "modality": row.get("modality"), "frontmatter": {key: meta.get(key, "") for key in ("source_form", "host_people", "guest_people", "show_title", "channel_name", "host_slug", "show", "host", "guest", "thread", "source_identity", "source_note")}})
    print(json.dumps({"count": len(result), "containers": containers, "records": result, "compact": [{"date": item["date"], "title": item["title"], "source_form": item["frontmatter"].get("source_form"), "show": item["frontmatter"].get("show"), "host": item["frontmatter"].get("host"), "note": item["frontmatter"].get("source_note")} for item in result]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

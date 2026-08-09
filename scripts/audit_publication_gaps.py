"""Inventory authored rows without publication provenance; read-only."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter

from role_aware_archive import AUTHORED_MODALITIES, load_manifest, source_frontmatter_url


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    gaps = []
    domains: Counter[str] = Counter()
    forms: Counter[str] = Counter()
    for row in load_manifest().get("sources", []):
        authored = str(row.get("source_class", "")).casefold().startswith("authored") or str(row.get("modality", "")).casefold() in AUTHORED_MODALITIES
        if not authored or row.get("publication_slug"):
            continue
        url = str(row.get("source_url") or "") or source_frontmatter_url(row)
        match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        domains[match.group(1).casefold() if match else "no-url"] += 1
        forms[f"{row.get('source_class')} / {row.get('modality')}"] += 1
        gaps.append({"date": row.get("date"), "title": row.get("title"), "path": row.get("local_path"), "url": url})
    print(json.dumps({"gaps": len(gaps), "domains": domains, "forms": forms, "sample": gaps[:40]}, indent=2, ensure_ascii=False, default=dict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

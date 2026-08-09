"""Read-only consistency audit for host, show, and channel routing."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter

from role_aware_archive import canonical_slug, host_kind, load_manifest


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
    rows = load_manifest().get("sources", [])
    kinds: Counter[str] = Counter()
    missing_manifest_host = []
    frontmatter_mismatch = []
    person_container_collision = []
    authored_container = []
    for row in rows:
        meta = frontmatter(row.get("local_path", ""))
        manifest_host = canonical_slug(str(row.get("host_slug") or ""))
        metadata_host = canonical_slug(str(meta.get("host_slug") or ""))
        metadata_container = str(meta.get("channel_name") or meta.get("show_title") or meta.get("show") or "").strip()
        kind = row.get("host_kind") or "none"
        kinds[kind] += 1
        label = f"{row.get('date')} {row.get('title')}"
        if metadata_host and not manifest_host:
            missing_manifest_host.append({"label": label, "frontmatter_host": metadata_host})
        if manifest_host and metadata_host and manifest_host != metadata_host:
            frontmatter_mismatch.append({"label": label, "manifest_host": manifest_host, "frontmatter_host": metadata_host})
        if manifest_host and manifest_host in {canonical_slug(str(v)) for v in row.get("voice_slugs") or []}:
            person_container_collision.append({"label": label, "host": manifest_host, "kind": kind})
        if str(row.get("source_class", "")).casefold().startswith("authored") and metadata_container:
            authored_container.append({"label": label, "container": metadata_container, "kind": kind})
    print(json.dumps({"rows": len(rows), "host_kinds": kinds, "missing_manifest_host_count": len(missing_manifest_host), "frontmatter_mismatch_count": len(frontmatter_mismatch), "person_container_collision_count": len(person_container_collision), "authored_container_count": len(authored_container), "samples": {"missing_manifest_host": missing_manifest_host[:20], "frontmatter_mismatch": frontmatter_mismatch[:20], "person_container_collision": person_container_collision[:20], "authored_container": authored_container[:20]}}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

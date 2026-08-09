"""Read-only audit of explicit Christoforou metadata in The Duran sources."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter

from role_aware_archive import load_manifest


def metadata(path: str) -> dict[str, str]:
    try:
        text = open(path, encoding="utf-8-sig").read()
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    header = text.split("---", 2)[1]
    result: dict[str, str] = {}
    for line in header.splitlines():
        match = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip().strip("\"'")
    return result


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    records = []
    statuses: Counter[str] = Counter()
    for row in load_manifest().get("sources", []):
        if row.get("host_slug") != "the-duran":
            continue
        meta = metadata(row.get("local_path", ""))
        host = meta.get("host", "")
        if "christoforou" not in host.casefold():
            continue
        voices = row.get("voice_slugs") or []
        roles = row.get("voice_roles") or {}
        status = "backfilled" if "cristoforou" in voices else "candidate"
        statuses[status] += 1
        records.append({"date": row.get("date"), "title": row.get("title"), "path": row.get("local_path"), "voices": voices, "roles": roles, "source_class": row.get("source_class"), "modality": row.get("modality"), "frontmatter_host": host, "frontmatter_guest": meta.get("guest", ""), "source_form": meta.get("source_form", ""), "status": status})
    print(json.dumps({"records": len(records), "statuses": statuses, "records_detail": records}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

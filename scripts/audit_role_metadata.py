"""Read-only audit of role-aware manifest assignments."""

from __future__ import annotations

import json
from collections import Counter

from role_aware_archive import AUTHORED_MODALITIES, load_manifest, publication_from_row


def main() -> int:
    rows = load_manifest().get("sources", [])
    status = Counter()
    basis = Counter()
    roles = Counter()
    authored_non_author: list[str] = []
    provisional: list[str] = []
    unhosted_guest: list[str] = []
    panel_rows: list[str] = []
    publication_gaps: list[str] = []
    for row in rows:
        for voice, values in (row.get("voice_roles") or {}).items():
            for role in values:
                roles[role] += 1
            state = (row.get("role_status") or {}).get(voice, "missing")
            status[state] += 1
            basis[(row.get("role_basis") or {}).get(voice, "missing")] += 1
            label = f"{row.get('date')} {row.get('title')} [{voice}]"
            if state in {"inferred", "provisional"}:
                provisional.append(label)
            authored = str(row.get("source_class", "")).casefold().startswith("authored") or str(row.get("modality", "")).casefold() in AUTHORED_MODALITIES
            if authored and "author" not in (row.get("voice_roles") or {}).get(voice, []):
                authored_non_author.append(label)
            if "guest" in (row.get("voice_roles") or {}).get(voice, []) and not row.get("host_slug"):
                unhosted_guest.append(label)
        if "panelist" in {role for values in (row.get("voice_roles") or {}).values() for role in values}:
            panel_rows.append(f"{row.get('date')} {row.get('title')}")
        authored = str(row.get("source_class", "")).casefold().startswith("authored") or str(row.get("modality", "")).casefold() in AUTHORED_MODALITIES
        if authored and not row.get("publication_slug") and publication_from_row(row) is None:
            publication_gaps.append(f"{row.get('date')} {row.get('title')}")
    report = {
        "rows": len(rows),
        "role_assignments": sum(roles.values()),
        "roles": roles,
        "statuses": status,
        "bases": basis,
        "inferred_or_provisional_count": len(provisional),
        "authored_non_author_count": len(authored_non_author),
        "unhosted_guest_count": len(unhosted_guest),
        "panel_source_count": len(panel_rows),
        "publication_gap_count": len(publication_gaps),
        "samples": {"authored_non_author": authored_non_author[:20], "unhosted_guest": unhosted_guest[:20], "publication_gaps": publication_gaps[:20]},
    }
    print(json.dumps(report, indent=2, ensure_ascii=False, default=dict))
    return 1 if authored_non_author else 0


if __name__ == "__main__":
    raise SystemExit(main())

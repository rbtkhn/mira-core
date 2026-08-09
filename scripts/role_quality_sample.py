"""Read-only deterministic quality sample for role-aware migration."""

from __future__ import annotations

import json
from collections import Counter

from role_aware_archive import AUTHORED_MODALITIES, infer_roles, load_manifest, host_kind, publication_from_row, source_frontmatter_url, validate_row


def main() -> int:
    rows = [row for row in load_manifest().get("sources", []) if "voice_roles" not in row][:100]
    roles: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    bases: Counter[str] = Counter()
    host_kinds: Counter[str] = Counter()
    publication_count = authored_count = url_count = no_voice = multi_voice = 0
    warnings: list[str] = []
    for row in rows:
        inferred_roles, inferred_status, inferred_basis = infer_roles(row)
        roles.update(values[0] for values in inferred_roles.values())
        statuses.update(inferred_status.values())
        bases.update(inferred_basis.values())
        kind = host_kind(row)
        host_kinds[kind or "none"] += 1
        publication_count += bool(publication_from_row(row))
        authored_count += str(row.get("source_class", "")).casefold().startswith("authored") or str(row.get("modality", "")).casefold() in AUTHORED_MODALITIES
        url_count += bool(row.get("source_url") or source_frontmatter_url(row))
        no_voice += not bool(row.get("voice_slugs"))
        multi_voice += len(row.get("voice_slugs") or []) > 1
        candidate = {**row, "voice_roles": inferred_roles, "role_status": inferred_status, "role_basis": inferred_basis, "host_kind": kind}
        warnings.extend(f"{row.get('date')} {row.get('title')}: {failure}" for failure in validate_row(candidate))
    print(json.dumps({"sample": len(rows), "roles": roles, "statuses": statuses, "role_basis": bases, "host_kinds": host_kinds, "authored_candidates": authored_count, "publication_detected": publication_count, "explicit_or_recovered_urls": url_count, "no_voice": no_voice, "multi_voice": multi_voice, "warning_count": len(warnings), "warnings": warnings[:20]}, indent=2, ensure_ascii=False))
    return 1 if warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())

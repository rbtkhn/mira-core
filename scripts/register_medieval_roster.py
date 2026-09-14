from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "archive" / "library" / "library-registry.json"
CANDIDATES = ROOT / "archive" / "library" / "medieval" / "full-roster-candidates.json"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    packet = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    existing = {source["source_id"] for source in registry["sources"]}
    selected = [
        candidate
        for candidate in packet["candidates"]
        if candidate.get("disposition") == "selected"
    ]
    added: list[str] = []
    for candidate in selected:
        source_id = candidate["proposed_source_id"]
        if source_id in existing:
            continue
        identity = candidate.get("identity_source") or {}
        source = {
            "source_id": source_id,
            "title": candidate["title"],
            "author": candidate["authority_label"],
            "subject_era": "medieval",
            "source_composition_era": "medieval",
            "secondary_eras": [],
            "date_start": candidate.get("date_start"),
            "date_end": candidate.get("date_end"),
            "date_label": candidate["date_label"],
            "era_basis": "composition_period",
            "civilization_tags": [slug(candidate["primary_lane"])],
            "source_type": candidate["source_type"],
            "location": {
                "civilization_memory_refs": [],
                "body_imported": False,
                "identity_source_label": identity.get("label", ""),
                "identity_source_url": identity.get("url", ""),
            },
            "status": "stub",
            "notes": (
                f"Selected for the Medieval full roster: {candidate['selection_reason']} "
                f"Boundary: {candidate['corpus_boundary']}"
            ),
            "text_status": "missing",
            "text_bodies": [],
            "coverage_status": "metadata-only",
            "coverage_notes": (
                "Roster registration only; no body is admitted. Candidate research ceiling: "
                f"{candidate['coverage_ceiling']}. Principal unresolved gap: "
                f"{candidate['principal_unresolved_gap']}"
            ),
        }
        registry["sources"].append(source)
        existing.add(source_id)
        added.append(source_id)

    registry["sources"].sort(key=lambda source: source["source_id"])
    REGISTRY.write_text(
        json.dumps(registry, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "selected": len(selected),
                "added": len(added),
                "already_present": len(selected) - len(added),
                "added_source_ids": added,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

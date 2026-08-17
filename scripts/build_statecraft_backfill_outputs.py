"""Build coverage and conservative enrichment outputs for the 2026 backfill."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NG = ROOT / "narrative-geopolitics"
MANIFEST = NG.parent / "archive" / "sources" / "geopolitics" / "source-manifest.json"
INVENTORY = NG / "work" / "backfill-2026" / "inventory.json"
OUT = NG / "work" / "backfill-2026"


def object_for(title: str) -> str:
    low = title.lower()
    for terms, label in (
        (("hormuz", "iran", "nuclear", "trump"), "Iran-U.S. escalation and settlement"),
        (("odessa", "donbass", "kiev", "ukraine", "russia"), "Russia-Ukraine territorial settlement"),
        (("europe", "nato", "eu", "european"), "European security and Russia confrontation"),
        (("lebanon", "hezbollah", "israel", "gaza"), "Israel-Lebanon-Gaza regional war"),
        (("china", "taiwan", "beijing"), "China-U.S. strategic competition"),
    ):
        if any(term in low for term in terms):
            return label
    return "Unclassified geopolitical source"


def load_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    _, meta, _ = text.split("---", 2)
    out: dict[str, str] = {}
    for line in meta.splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip().strip("'\"")
    return out


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    rows = list(manifest["sources"])
    backfill_rows = [
        row for row in rows
        if str(row.get("source_class", "")).startswith("historical upstream")
    ]
    voices = sorted({voice for item in inventory for voice in item.get("voice_slugs", [])})
    months = [f"2026-{month:02d}" for month in range(1, 8)]
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    imported: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    provisional: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    quality: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    tags: list[dict[str, object]] = []
    flags: list[dict[str, object]] = []
    for row in rows:
        month = str(row.get("date", ""))[:7]
        if month not in months:
            continue
        source_path = ROOT / str(row["local_path"])
        meta = load_frontmatter(source_path) if source_path.exists() else {}
        for voice in row.get("voice_slugs", []):
            counts[voice][month] += 1
            if str(row.get("source_class", "")).startswith("historical upstream"):
                imported[voice][month] += 1
            if row.get("routing_state") == "provisional":
                provisional[voice][month] += 1
            quality[voice][month] += int(meta.get("transcript_curation", "") in {"preserved_unsectioned", ""})
    for row in backfill_rows:
        source_path = ROOT / str(row["local_path"])
        meta = load_frontmatter(source_path) if source_path.exists() else {}
        title = str(row.get("title", ""))
        obj = object_for(title)
        tags.append({
            "source_ref": row["local_path"],
            "voice_slugs": row.get("voice_slugs", []),
            "date": row.get("date"),
            "thesis_object": obj,
            "thesis_statement": None,
            "mechanism": None,
            "predicted_outcome": None,
            "timing": None,
            "falsifier": None,
            "extraction_state": "title_derived_only",
            "extraction_confidence": "low",
            "source_classification": "descriptive_or_analytical_unknown",
        })
        if any(word in title.lower() for word in ("forecast", "will ", "about to", "plans", "prepares", "coming", "war")):
            flags.append({
                "source_ref": row["local_path"],
                "voice_slugs": row.get("voice_slugs", []),
                "date": row.get("date"),
                "flag_type": "potential_forecast_or_thesis_continuity",
                "crisis_object": obj,
                "status": "needs_manual_review",
                "reason": "Title contains a forecast, plan, timing, or conflict cue; no forecast or reality claim was promoted automatically.",
            })

    ledger = {
        "schema_version": 1,
        "months": months,
        "voices": voices,
        "counts": counts,
        "imported_counts": imported,
        "provisional_counts": provisional,
        "unsectioned_counts": quality,
        "source_rows_considered": len(rows),
        "notes": [
            "Counts are manifest-derived.",
            "Historical upstream sources remain unverified source assertions.",
            "Title-derived tags are not thesis adjudications.",
        ],
    }
    (OUT / "coverage-ledger.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# 2026 Statecraft Backfill Coverage Ledger",
        "",
        "Manifest-derived coverage for recognized voice-bearing upstream candidates. Counts include all manifest rows routed to the voice; `I` marks historical-backfill rows and `P` marks provisional routing.",
        "",
        "| Voice | Jan | Feb | Mar | Apr | May | Jun | Jul | Floor |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for voice in voices:
        cells = []
        for month in months:
            total = counts[voice][month]
            imp = imported[voice][month]
            prov = provisional[voice][month]
            cells.append("0" if not total else f"{total}" + (f"/I{imp}" if imp else "") + ("/P" if prov else ""))
        floor = "met" if all(counts[voice][month] > 0 for month in months) else "gap"
        lines.append(f"| `{voice}` | " + " | ".join(cells) + f" | `{floor}` |")
    lines += [
        "",
        f"Manifest rows considered: `{len(rows)}`. Historical backfill rows tagged: `{len(tags)}`. Continuity flags requiring manual review: `{len(flags)}`.",
        "",
        "Coverage is not verification. Provisional routing, unsectioned transcripts, and title-derived enrichment require later review.",
    ]
    (OUT / "coverage-ledger.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "thesis-tags.json").write_text(json.dumps(tags, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "continuity-flags.json").write_text(json.dumps(flags, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"source_rows": len(rows), "voices": len(voices), "thesis_tags": len(tags), "continuity_flags": len(flags)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

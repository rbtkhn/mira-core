"""Collection-aware, read-only archive query substrate."""
from __future__ import annotations
import json, re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

def is_transcript_modality(value: object) -> bool:
    return "transcript" in str(value or "").casefold()

@dataclass(frozen=True)
class CollectionAdapter:
    collection_id: str; registry_path: str; documents_key: str; body_root: str
    authority_owner: str; evidence_class: str; retrieval_policy: str; routing_key: str
    modality_vocabulary: frozenset[str]

ADAPTERS = {
    "geopolitics": CollectionAdapter("geopolitics", "archive/sources/geopolitics/source-manifest.json", "sources", "archive/sources/geopolitics/sources", "archive/sources/geopolitics/source-manifest.json", "imported-archive-source", "default", "host_slug", frozenset({"transcript", "cleaned-transcript", "source-text", "article", "substack-post", "newsletter", "x-post-text", "essay"})),
    "innermost-loop": CollectionAdapter("innermost-loop", "archive/registries/innermost-loop.json", "documents", "external-corpora/innermost-loop", "archive/registries/innermost-loop.json", "frontier-ai-research-source", "explicit-only", "native", frozenset()),
    "moonshots": CollectionAdapter("moonshots", "archive/registries/moonshots.json", "documents", "external-corpora/moonshots", "archive/registries/moonshots.json", "frontier-technology-research-source", "explicit-only", "native", frozenset()),
}

def _load_json(relative: str) -> dict[str, Any]:
    value = json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict): raise ValueError(f"registry must be an object: {relative}")
    return value

def load_curated_channels() -> list[dict[str, Any]]:
    text = (REPO_ROOT / "geopolitics/channels/channel-index.md").read_text(encoding="utf-8")
    statecraft = False; rows: dict[str, dict[str, Any]] = {}
    for line in text.splitlines():
        if line.startswith("## Statecraft Source Channel Roster"): statecraft = True; continue
        if statecraft and line.startswith("## "): break
        if not statecraft or not line.startswith("| `"): continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 11: raise ValueError(f"malformed curated channel row: {line}")
        slug, label, status, cadence = cells[0].strip("`"), cells[1], cells[2].strip("`"), cells[7].strip("`")
        match = re.search(r"https://www\.youtube\.com/[^)]+", cells[8])
        if not match: raise ValueError(f"curated channel has no canonical URL: {slug}")
        record = {"slug": slug, "label": label, "status": status, "cadence": cadence, "canonical_url": match.group(0)}
        if slug in rows and rows[slug] != record: raise ValueError(f"conflicting curated channel definition: {slug}")
        rows[slug] = record
    if not rows: raise ValueError("curated Statecraft channel roster is empty")
    return list(rows.values())

def _records(adapter: CollectionAdapter) -> list[dict[str, Any]]:
    registry = _load_json(adapter.registry_path); rows = registry.get(adapter.documents_key)
    if not isinstance(rows, list): raise ValueError(f"invalid {adapter.collection_id} registry records")
    declared = registry.get("source_count", registry.get("document_count"))
    if declared is not None and declared != len(rows): raise ValueError(f"{adapter.collection_id} registry count mismatch")
    return [row for row in rows if isinstance(row, dict)]

def query_snapshot(collections: Iterable[str] = ("geopolitics",), month: str | None = None, channels: Iterable[str] = (), transcript_only: bool = False, curated_channels: bool = False) -> dict[str, Any]:
    selected = list(collections)
    if not selected or any(item not in ADAPTERS for item in selected): raise ValueError("collection must be one of: geopolitics, innermost-loop, moonshots")
    roster = load_curated_channels() if curated_channels or channels else []
    by_slug = {row["slug"]: row for row in roster}; requested = set(channels)
    if requested - set(by_slug): raise ValueError("unknown curated channel: " + ", ".join(sorted(requested - set(by_slug))))
    output = {"collections": [], "records": [], "warnings": [], "roster": roster}
    for collection_id in selected:
        adapter = ADAPTERS[collection_id]; rows = _records(adapter)
        if month: rows = [row for row in rows if str(row.get("date", row.get("publication_date", row.get("published", "")))).startswith(month)]
        if transcript_only: rows = [row for row in rows if is_transcript_modality(row.get("modality", row.get("kind", row.get("document_type"))))]
        if collection_id == "geopolitics" and requested: rows = [row for row in rows if row.get("host_slug") in requested]
        output["records"].extend({**row, "_collection": collection_id} for row in rows)
        modalities = {str(row.get("modality", row.get("kind") or "unknown")) for row in rows}
        unknown = sorted(modalities - adapter.modality_vocabulary) if adapter.modality_vocabulary else []
        if unknown: output["warnings"].append({"collection": collection_id, "kind": "unknown-modality", "values": unknown})
        parity = None
        if collection_id == "geopolitics":
            manifest_paths = {str(row.get("local_path", "")).replace("/", "\\") for row in rows}
            root = REPO_ROOT / adapter.body_root
            file_paths = {str(path.relative_to(REPO_ROOT)).replace("/", "\\") for path in root.rglob("*.md") if not month or path.parent.name.startswith(month)}
            parity = {"manifest_paths": len(manifest_paths), "source_files": len(file_paths), "missing_files": sorted(manifest_paths - file_paths), "unlisted_files": sorted(file_paths - manifest_paths)}
            if parity["missing_files"] or parity["unlisted_files"]: raise ValueError("archive manifest/file parity failed")
        output["collections"].append({"collection_id": collection_id, "registry_path": adapter.registry_path, "authority_owner": adapter.authority_owner, "evidence_class": adapter.evidence_class, "retrieval_policy": adapter.retrieval_policy, "routing_key": adapter.routing_key, "registry_count": len(rows), "unknown_modalities": unknown, "parity": parity})
    if roster:
        counts = {slug: 0 for slug in by_slug}
        for row in output["records"]:
            if row.get("_collection") == "geopolitics" and row.get("host_slug") in counts: counts[row["host_slug"]] += 1
        output["channel_results"] = [{**by_slug[slug], "archive_items": counts[slug]} for slug in sorted(counts)]
    return output

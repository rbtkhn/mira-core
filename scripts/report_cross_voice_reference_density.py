"""Build a bounded historical-reference density comparison pilot."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
MANIFEST_PATH = NG_ROOT / "archive" / "source-manifest.json"
OUTPUT_PATH = NG_ROOT / "analytics" / "cross-voice-historical-reference-density.md"
INDEX_SCRIPT = REPO_ROOT / "scripts" / "build_freeman_historical_index.py"


def load_taxonomy():
    spec = importlib.util.spec_from_file_location("freeman_historical_index", INDEX_SCRIPT)
    if not spec or not spec.loader:
        raise RuntimeError("Unable to load shared historical-reference taxonomy")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def manifest_rows(voice_filter: str = "freeman") -> list[dict]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    seen: set[tuple[str, str]] = set()
    rows: list[dict] = []
    for row in manifest.get("sources", []):
        if not isinstance(row, dict):
            continue
        path = str(row.get("local_path") or "")
        voices = sorted({str(v).strip().lower() for v in (row.get("voice_slugs") or []) if str(v).strip()})
        for voice in voices:
            if voice_filter != "all" and voice != voice_filter:
                continue
            identity = (path, voice)
            if not path or identity in seen:
                continue
            seen.add(identity)
            rows.append({**row, "voice_slug": voice, "full_path": REPO_ROOT / path})
    return sorted(rows, key=lambda r: (str(r.get("date") or ""), r["voice_slug"], str(r.get("local_path") or "")))


def transcript_body(module, path: Path) -> str:
    if not path.is_file():
        return ""
    return module.source_body(path.read_text(encoding="utf-8", errors="replace"))


def confidence(paragraph: str, voice: str) -> str:
    label = re.search(r"^\s*(?:\*\*)?([^:*\n]{2,80})(?:\*\*)?:", paragraph)
    if label and voice.replace("-", " ") in label.group(1).lower():
        return "direct"
    if label:
        return "strong-inferred"
    return "provisional"


def build_records(voice_filter: str = "freeman") -> tuple[list[dict], list[str]]:
    module = load_taxonomy()
    records: list[dict] = []
    coverage: list[str] = []
    for index, row in enumerate(manifest_rows(voice_filter), start=1):
        path: Path = row["full_path"]
        source_id = f"SRC-CV-{index:05d}"
        if not path.is_file():
            coverage.append(f"MISSING {row['voice_slug']} {row.get('local_path', '')}")
            continue
        body = transcript_body(module, path)
        words = len(re.findall(r"\S+", body))
        occurrences = []
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        for rule in module.RULES:
            for paragraph_index, paragraph in enumerate(paragraphs, start=1):
                if not any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in rule.patterns):
                    continue
                occurrences.append({"key": rule.key, "confidence": confidence(paragraph, row["voice_slug"]), "paragraph": paragraph_index})
        records.append({
            "source_id": source_id, "voice": row["voice_slug"], "host": str(row.get("host_slug") or ""),
            "date": str(row.get("date") or ""), "title": str(row.get("title") or ""),
            "path": str(row.get("local_path") or path.relative_to(REPO_ROOT).as_posix()), "words": words,
            "occurrences": occurrences,
        })
        coverage.append(f"SCANNED {row['voice_slug']} {row.get('local_path', '')} ({len(occurrences)} candidate occurrence(s))")
    return records, coverage


def build_report(voice_filter: str = "freeman") -> str:
    records, coverage = build_records(voice_filter)
    by_voice: dict[str, list[dict]] = defaultdict(list)
    by_host: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        by_voice[record["voice"]].append(record)
        by_host[record["host"] or "(unrouted)"].append(record)

    def stats(items: list[dict]) -> dict:
        occurrences = [o for item in items for o in item["occurrences"]]
        words = sum(item["words"] for item in items)
        return {"transcripts": len(items), "words": words, "refs": len(occurrences),
                "unique": len({o["key"] for o in occurrences}),
                "density": len(occurrences) / words * 1000 if words else 0,
                "confidence": Counter(o["confidence"] for o in occurrences)}

    voice_stats = sorted(((voice, stats(items)) for voice, items in by_voice.items()), key=lambda x: (-x[1]["density"], x[0]))
    total = stats(records)
    sparse = [voice for voice, item in voice_stats if item["transcripts"] < 3 or item["words"] < 10000]
    lines = [
        "# Historical-Reference Density Pilot",
        "",
        "Status: `internal comparative research artifact`",
        "",
        f"Generated by `scripts/report_cross_voice_reference_density.py` from the manifest-backed `{voice_filter}` archive route using the conservative taxonomy shared with Freeman's historical-reference index. This is a bounded validation pilot before any multi-voice run.",
        "",
        "## Metric contract",
        "",
        "- Primary metric: candidate historical-reference occurrences per 1,000 transcript words.",
        "- Secondary metrics: raw occurrences, unique canonical references, transcript count, and confidence mix.",
        "- These are deterministic candidate counts, not fully voice-attributed historical indexes or historical-accuracy judgments.",
        "",
        "## Corpus summary", "", f"- Voice routes: **{len(voice_stats)}**", f"- Transcript routes: **{total['transcripts']}**", f"- Transcript words: **{total['words']:,}**", f"- Candidate occurrences: **{total['refs']:,}**", f"- Corpus density: **{total['density']:.2f} per 1,000 words**", f"- Sparse voices flagged: **{len(sparse)}**", "",
        "## Voice comparison", "", "| Rank | Voice | Transcripts | Words | References | Unique refs | Per 1,000 words | Confidence mix | Coverage |", "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for rank, (voice, item) in enumerate(voice_stats, start=1):
        mix = ", ".join(f"{key}:{value}" for key, value in sorted(item["confidence"].items())) or "none"
        warning = "sparse" if voice in sparse else "adequate"
        lines.append(f"| {rank} | `{voice}` | {item['transcripts']} | {item['words']:,} | {item['refs']} | {item['unique']} | {item['density']:.2f} | {mix} | {warning} |")

    lines += ["", "## Host/channel comparison", "", "| Host/channel | Transcript routes | Words | References | Unique refs | Per 1,000 words |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for host, items in sorted(by_host.items()):
        item = stats(items)
        lines.append(f"| `{host}` | {item['transcripts']} | {item['words']:,} | {item['refs']} | {item['unique']} | {item['density']:.2f} |")

    lines += ["", "## Transcript drilldown", "", "| Source | Voice | Date | Host/channel | Words | References | Unique refs | Per 1,000 words | Archive path |", "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for item in sorted(records, key=lambda r: (-((len(r['occurrences']) / r['words'] * 1000) if r['words'] else 0), r['date'], r['voice'], r['source_id'])):
        density = len(item["occurrences"]) / item["words"] * 1000 if item["words"] else 0
        lines.append(f"| `{item['source_id']}` | `{item['voice']}` | {item['date']} | `{item['host']}` | {item['words']:,} | {len(item['occurrences'])} | {len({o['key'] for o in item['occurrences']})} | {density:.2f} | `{item['path']}` |")

    lines += ["", "## Guardrails and coverage", "", "- A high density can reflect a historical topic, repeated mentions, transcript artifacts, or shared host framing; it is not a measure of analytical quality.", "- Provisional candidates remain in the primary metric and are exposed in the confidence mix.", "- Sparse voices are visible but should not be ranked as stable voice traits without more corpus coverage.", "- Duplicate manifest rows are collapsed by `(local_path, voice_slug)`; the same source may legitimately count once for each routed voice.", "", "## Coverage log", "", *[f"- {entry}" for entry in coverage], ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--voice", default="freeman", help="Voice route to scan; use 'all' only for a deliberate full-corpus run.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    report = build_report(args.voice.lower())
    if args.dry_run:
        print(report)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8", newline="\n")
        print(f"Wrote {args.output.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

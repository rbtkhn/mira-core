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
MANIFEST_PATH = NG_ROOT.parent / "archive" / "geopolitics" / "source-manifest.json"
OUTPUT_PATH = NG_ROOT / "analytics" / "cross-voice-historical-reference-density.md"
VOICE_LEDGER_DIR = NG_ROOT / "analytics" / "historical-reference-ledgers"
REVIEW_OVERRIDES_PATH = NG_ROOT / "analytics" / "historical-reference-review-overrides.json"
REVIEW_QUEUE_PATH = NG_ROOT / "analytics" / "historical-reference-review-queue.md"
INDEX_SCRIPT = REPO_ROOT / "scripts" / "build_freeman_historical_index.py"


def load_taxonomy():
    spec = importlib.util.spec_from_file_location("freeman_historical_index", INDEX_SCRIPT)
    if not spec or not spec.loader:
        raise RuntimeError("Unable to load shared historical-reference taxonomy")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def selected_voices(voice_filter: str) -> set[str] | None:
    values = {value.strip().lower() for value in voice_filter.split(",") if value.strip()}
    return None if "all" in values else values


def manifest_rows(voice_filter: str = "freeman") -> list[dict]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    selected = selected_voices(voice_filter)
    seen: set[tuple[str, str]] = set()
    rows: list[dict] = []
    for row in manifest.get("sources", []):
        if not isinstance(row, dict):
            continue
        path = str(row.get("local_path") or "")
        voices = sorted({str(v).strip().lower() for v in (row.get("voice_slugs") or []) if str(v).strip()})
        for voice in voices:
            if selected is not None and voice not in selected:
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


def confidence(paragraph: str, voice: str) -> str | None:
    label = re.search(r"^\s*(?:\*\*)?([^:*\n]{2,80})(?:\*\*)?:", paragraph)
    if label and voice.replace("-", " ") in label.group(1).lower():
        return "direct"
    if label:
        return None
    return "provisional"


CONTEXT_ONLY_OPENERS = re.compile(
    r"^\s*(?:hi everybody|hello everyone|good day|welcome back|welcome here|we are joined|joining us|"
    r"let me welcome|today is|please subscribe|thank you for coming|thank you for joining|"
    r"can i ask you|let me ask you|what do you think|how do you see|why do you think|"
    r"before we get started|we are here today|our guest today)",
    re.IGNORECASE,
)


def is_context_only(paragraph: str) -> bool:
    return bool(CONTEXT_ONLY_OPENERS.search(paragraph))


def build_records(voice_filter: str = "freeman") -> tuple[list[dict], list[str]]:
    module = load_taxonomy()
    overrides = json.loads(REVIEW_OVERRIDES_PATH.read_text(encoding="utf-8")) if REVIEW_OVERRIDES_PATH.is_file() else {}
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
                if is_context_only(paragraph):
                    continue
                level = confidence(paragraph, row["voice_slug"])
                if level is None:
                    continue
                occurrences.append({
                    "key": rule.key,
                    "label": rule.label,
                    "function": rule.function,
                    "confidence": level,
                    "review_status": "voice-supported" if level == "direct" else "unreviewed",
                    "paragraph": paragraph_index,
                    "quote": module.clean_quote(paragraph, max_chars=500),
                })
                override = overrides.get(f"{row['voice_slug']}|{source_id}") or overrides.get(f"{row['voice_slug']}|{row.get('local_path', '')}")
                if override:
                    occurrences[-1]["review_status"] = override
        records.append({
            "source_id": source_id, "voice": row["voice_slug"], "host": str(row.get("host_slug") or ""),
            "date": str(row.get("date") or ""), "title": str(row.get("title") or ""),
            "path": str(row.get("local_path") or path.relative_to(REPO_ROOT).as_posix()), "words": words,
            "occurrences": occurrences,
        })
        coverage.append(f"SCANNED {row['voice_slug']} {row.get('local_path', '')} ({len(occurrences)} candidate occurrence(s))")
    return records, coverage


def render_report(
    records: list[dict],
    coverage: list[str],
    voice_filter: str = "freeman",
) -> str:
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
        f"Generated by `scripts/report_cross_voice_reference_density.py` from the manifest-backed `{voice_filter}` archive routes using the conservative taxonomy shared with Freeman's historical-reference index. This is a bounded comparison pilot.",
        "",
        "## Metric contract",
        "",
        "- Primary metric: candidate historical-reference occurrences per 1,000 transcript words.",
        "- Secondary metrics: raw occurrences, unique canonical references, transcript count, and confidence mix.",
        "- These are deterministic candidate counts, not fully voice-attributed historical indexes or historical-accuracy judgments.",
        "- Explicitly labeled host/interviewer turns and recognizable context-only openings are excluded; other unlabeled turns remain `provisional` and require review.",
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

    lines += ["", "## Occurrence ledger", "", "Archive wording is preserved as captured. Candidate excerpts are bounded for readability and are not independently verified.", ""]
    occurrence_number = 0
    for item in sorted(records, key=lambda r: (r["date"], r["voice"], r["source_id"])):
        for occurrence in sorted(item["occurrences"], key=lambda o: (o["paragraph"], o["key"])):
            occurrence_number += 1
            archive_link = "../../" + item["path"]
            lines += [
                f"### CV-HR-{occurrence_number:04d} — {occurrence['label']}",
                "",
                f"- Source: `{item['source_id']}` · voice `{item['voice']}` · date `{item['date']}` · host/channel `{item['host']}`",
                f"- Archive: [{item['path']}]({archive_link})",
                f"- Function: `{occurrence['function']}` · confidence: `{occurrence['confidence']}` · review: `{occurrence['review_status']}` · paragraph: `{occurrence['paragraph']}`",
                f"- Quote: “{occurrence['quote']}”",
                "",
            ]

    lines += ["", "## Guardrails and coverage", "", "- A high density can reflect a historical topic, repeated mentions, transcript artifacts, or shared host framing; it is not a measure of analytical quality.", "- Provisional candidates remain visible in the primary metric but are not voice-attributed speech.", "- Explicitly labeled host/interviewer turns and recognizable context-only openings are excluded; other unlabeled interview text is retained only as provisional review material.", "- Sparse voices are visible but should not be ranked as stable voice traits without more corpus coverage.", "- Duplicate manifest rows are collapsed by `(local_path, voice_slug)`; the same source may legitimately count once for each routed voice.", "", "## Coverage log", "", *[f"- {entry}" for entry in coverage], ""]
    return "\n".join(lines)


def build_report(voice_filter: str = "freeman") -> str:
    records, coverage = build_records(voice_filter)
    return render_report(records, coverage, voice_filter)


def render_voice_ledger(records: list[dict], voice: str) -> str:
    selected = [record for record in records if record["voice"] == voice]
    occurrences = sum((record["occurrences"] for record in selected), [])
    lines = [
        f"# Historical-Reference Ledger: {voice}",
        "",
        "Status: `internal research ledger`",
        "",
        "Generated from the manifest-backed archive using the shared conservative taxonomy. Archive wording is preserved as captured; excerpts are bounded and not independently verified. Explicitly labeled host/interviewer turns and recognizable context-only openings are excluded; other unlabeled turns remain provisional.",
        "",
        f"- Transcript routes: **{len(selected)}**",
        f"- Candidate occurrences: **{len(occurrences)}**",
        f"- Unique canonical references: **{len({item['key'] for item in occurrences})}**",
        "",
        "## Source-level reference clusters",
        "",
        "Each cluster consolidates repeated mentions of one canonical reference within one source while retaining every occurrence below.",
        "",
        "| Cluster ID | Date | Source | Reference | Occurrences | Review-status mix | Archive path |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ]
    clusters: dict[tuple[str, str], tuple[dict, list[dict]]] = {}
    for record in selected:
        for occurrence in record["occurrences"]:
            key = (record["source_id"], occurrence["key"])
            if key not in clusters:
                clusters[key] = (record, [])
            clusters[key][1].append(occurrence)
    for number, ((source_id, _), (record, items)) in enumerate(sorted(clusters.items(), key=lambda pair: (pair[1][0]["date"], pair[0][0], pair[0][1])), start=1):
        mix = Counter(item["review_status"] for item in items)
        mix_text = ", ".join(f"{status}:{count}" for status, count in sorted(mix.items()))
        archive_link = "../../../" + record["path"]
        lines.append(f"| `{voice.upper()}-CL-{number:04d}` | {record['date']} | `{source_id}` | {items[0]['label']} | {len(items)} | {mix_text} | [{record['path']}]({archive_link}) |")
    lines += [
        "",
        "## Occurrence ledger",
        "",
        "| ID | Reference | Date | Source | Host/channel | Function | Confidence | Review status | Archive path | Quote |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for number, (record, occurrence) in enumerate(
        sorted(((record, occurrence) for record in selected for occurrence in record["occurrences"]), key=lambda pair: (pair[0]["date"], pair[0]["source_id"], pair[1]["paragraph"], pair[1]["key"])),
        start=1,
    ):
        archive_link = "../../../" + record["path"]
        ledger_id = f"{voice.upper()}-HR-{number:04d}"
        lines.append(f"| `{ledger_id}` | {occurrence['label']} | {record['date']} | `{record['source_id']}` | `{record['host']}` | `{occurrence['function']}` | `{occurrence['confidence']}` | `{occurrence['review_status']}` | [{record['path']}]({archive_link}) | {occurrence['quote']} |")
    lines += ["", "## Coverage", "", *[f"- `{record['source_id']}` — {record['date']} — {record['title']}" for record in selected], ""]
    return "\n".join(lines)


def render_review_queue(records: list[dict]) -> str:
    entries = []
    for record in records:
        for occurrence in record["occurrences"]:
            entries.append((record, occurrence))
    status_order = {"needs-review": 0, "unreviewed": 1, "voice-supported": 2, "excluded-context": 3}
    entries.sort(key=lambda pair: (status_order.get(pair[1]["review_status"], 9), pair[0]["voice"], pair[0]["date"], pair[0]["source_id"], pair[1]["key"]))
    counts = Counter(occurrence["review_status"] for _, occurrence in entries)
    lines = [
        "# Historical-Reference Review Queue",
        "",
        "Status: `internal operator review surface`",
        "",
        "Generated from the bounded five-voice historical-reference ledgers. Review status is an operator workflow field; it does not alter the captured transcript or source-derived candidate detection.",
        "",
        f"- Total candidates: **{len(entries)}**",
        f"- Needs review: **{counts['needs-review']}**",
        f"- Unreviewed backlog: **{counts['unreviewed']}**",
        f"- Voice-supported: **{counts['voice-supported']}**",
        f"- Excluded context: **{counts['excluded-context']}**",
        "",
        "## Review instructions",
        "",
        "- Start with `needs-review`; confirm whether the excerpt is spoken by the routed voice.",
        "- Use `voice-supported` only when the transcript supports attribution; use `excluded-context` for host, prompt, introduction, or quoted third-party material.",
        "- Record durable decisions in `historical-reference-review-overrides.json`, then regenerate the ledgers.",
        "",
        "## Cluster review queue",
        "",
        "Review one source/reference cluster at a time. A cluster decision applies to all occurrences in that source/reference pair unless a later occurrence-level override is introduced.",
        "",
        "| Cluster ID | Voice | Date | Source | Reference | Occurrences | Status mix | Archive |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    clusters: dict[tuple[str, str, str], tuple[dict, list[dict]]] = {}
    for record, occurrence in entries:
        key = (record["voice"], record["source_id"], occurrence["key"])
        if key not in clusters:
            clusters[key] = (record, [])
        clusters[key][1].append(occurrence)
    for number, ((voice, source_id, _), (record, items)) in enumerate(sorted(clusters.items(), key=lambda pair: (status_order.get(pair[1][1][0]["review_status"], 9), pair[0][0], pair[0][1], pair[0][2])), start=1):
        mix = Counter(item["review_status"] for item in items)
        mix_text = ", ".join(f"{status}:{count}" for status, count in sorted(mix.items()))
        archive_link = "../../" + record["path"]
        lines.append(f"| `RV-CL-{number:04d}` | `{voice}` | {record['date']} | `{source_id}` | {items[0]['label']} | {len(items)} | {mix_text} | [{record['path']}]({archive_link}) |")
    number = 0
    for status in ("needs-review", "unreviewed", "voice-supported", "excluded-context"):
        subset = [(record, occurrence) for record, occurrence in entries if occurrence["review_status"] == status]
        if not subset:
            continue
        lines += ["", f"## {status}", "", "| ID | Voice | Date | Reference | Source | Confidence | Archive | Quote |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for record, occurrence in subset:
            number += 1
            queue_id = f"RV-HR-{number:04d}"
            archive_link = "../../" + record["path"]
            lines.append(f"| `{queue_id}` | `{record['voice']}` | {record['date']} | {occurrence['label']} | `{record['source_id']}` | `{occurrence['confidence']}` | [{record['path']}]({archive_link}) | {occurrence['quote']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--voices", default="freeman", help="Comma-separated voice routes; use 'all' only for a deliberate full-corpus run.")
    parser.add_argument("--voice-ledger-dir", type=Path, default=VOICE_LEDGER_DIR)
    parser.add_argument("--review-queue", type=Path, default=REVIEW_QUEUE_PATH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    voice_filter = args.voices.lower()
    records, coverage = build_records(voice_filter)
    report = render_report(records, coverage, voice_filter)
    if args.dry_run:
        print(report)
    else:
        output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8", newline="\n")
        print(f"Wrote {output.relative_to(REPO_ROOT).as_posix()}")
        ledger_dir = args.voice_ledger_dir if args.voice_ledger_dir.is_absolute() else REPO_ROOT / args.voice_ledger_dir
        ledger_dir.mkdir(parents=True, exist_ok=True)
        for voice in sorted({record["voice"] for record in records}):
            ledger_path = ledger_dir / f"{voice}.md"
            ledger_path.write_text(render_voice_ledger(records, voice), encoding="utf-8", newline="\n")
            print(f"Wrote {ledger_path.relative_to(REPO_ROOT).as_posix()}")
        queue_path = args.review_queue if args.review_queue.is_absolute() else REPO_ROOT / args.review_queue
        queue_path.write_text(render_review_queue(records), encoding="utf-8", newline="\n")
        print(f"Wrote {queue_path.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

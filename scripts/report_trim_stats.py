from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_SOURCES_ROOT = REPO_ROOT / "archive" / "sources" / "geopolitics" / "sources"
MANIFEST_PATH = REPO_ROOT / "archive" / "sources" / "geopolitics" / "source-manifest.json"
HOST_SLUG_ALIASES: dict[str, str] = {}
TRANSCRIPT_WRAPPER_RE = re.compile(r"(?m)^Transcripts:\s*$")
YOUTUBE_TITLE_WRAPPER_RE = re.compile(r"(?m)^.+ - YouTube\s*$")
HEADING_RE = re.compile(r"(?m)^### ")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data: dict[str, str] = {}
    for raw_line in parts[1].splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def read_frontmatter(path: Path) -> dict[str, str]:
    lines: list[str] = []
    delimiter_count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            lines.append(line)
            if line.rstrip("\r\n") == "---":
                delimiter_count += 1
                if delimiter_count == 2:
                    break
    return parse_frontmatter("".join(lines))


def safe_int(value: str | None) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def transcript_body(text: str) -> str:
    if "## Transcript" not in text:
        return ""
    return text.split("## Transcript", 1)[1].lstrip()


def load_manifest_routes() -> dict[str, dict[str, Any]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    return {
        row.get("local_path", ""): row
        for row in manifest.get("sources", [])
        if row.get("local_path")
    }


def relative_source_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def canonical_host_slug(
    path: Path,
    frontmatter: dict[str, str],
    manifest_row: dict[str, Any] | None = None,
) -> str:
    manifest_row = manifest_row or {}
    host_slug = (
        frontmatter.get("host_slug")
        or frontmatter.get("channel_slug")
        or manifest_row.get("host_slug")
        or "unknown"
    )
    host_slug = HOST_SLUG_ALIASES.get(host_slug, host_slug)
    if host_slug == "unknown" and path.name.startswith("source-alexander-mercouris-"):
        return "alexander-mercouris"
    return host_slug


def classify_curation(frontmatter: dict[str, str], text: str) -> str:
    state = frontmatter.get("transcript_curation", "")
    headings = len(HEADING_RE.findall(text))
    if state == "curated_sectioned":
        return "useful_sectioning" if headings >= 2 else "weak_sectioning"
    if state == "preserved_unsectioned":
        return "preserved_unsectioned"
    return "curation_state_missing"


def classify_asr(frontmatter: dict[str, str]) -> str:
    value = frontmatter.get("asr_repair_applied")
    if value == "true":
        return "asr_applied"
    if value == "false":
        return "asr_checked_no_change"
    return "asr_state_missing"


def collect_report(
    *,
    host_filter: str | None = None,
    published_since: str | None = None,
    ingested_since: str | None = None,
) -> dict[str, Any]:
    routes = load_manifest_routes()
    hosts: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "sources": 0,
            "opening_trimmed": 0,
            "closing_trimmed": 0,
            "opening_chars": 0,
            "opening_words": 0,
            "closing_chars": 0,
            "closing_words": 0,
            "body_chars": 0,
        }
    )
    summary: dict[str, int] = defaultdict(int)

    for path in sorted(ARCHIVE_SOURCES_ROOT.rglob("source-*.md")):
        frontmatter = read_frontmatter(path)
        pub_date = frontmatter.get("pub_date", "").strip("'\"")
        ingest_date = frontmatter.get("ingest_date", "").strip("'\"")
        if published_since and (not pub_date or pub_date < published_since):
            continue
        if ingested_since and (not ingest_date or ingest_date < ingested_since):
            continue

        manifest_row = routes.get(relative_source_path(path), {})
        host_slug = canonical_host_slug(path, frontmatter, manifest_row)
        if host_filter and host_slug != host_filter:
            continue

        text = path.read_text(encoding="utf-8")
        body = transcript_body(text)
        row = hosts[host_slug]
        row["sources"] += 1
        row["body_chars"] += len(body)
        row["opening_trimmed"] += frontmatter.get("opening_trim_applied") == "true"
        row["closing_trimmed"] += frontmatter.get("closing_trim_applied") == "true"
        row["opening_chars"] += safe_int(frontmatter.get("opening_trim_chars_saved"))
        row["opening_words"] += safe_int(frontmatter.get("opening_trim_words_saved"))
        row["closing_chars"] += safe_int(frontmatter.get("closing_trim_chars_saved"))
        row["closing_words"] += safe_int(frontmatter.get("closing_trim_words_saved"))

        summary["sources"] += 1
        summary["unknown_hosts"] += host_slug == "unknown"
        summary["transcript_wrapper_remnants"] += bool(TRANSCRIPT_WRAPPER_RE.search(body))
        summary["youtube_title_wrapper_remnants"] += bool(YOUTUBE_TITLE_WRAPPER_RE.search(body))
        summary[classify_curation(frontmatter, text)] += 1
        summary[classify_asr(frontmatter)] += 1

    host_output: dict[str, dict[str, int | float]] = {}
    for host_slug in sorted(hosts):
        row = hosts[host_slug]
        total_chars = int(row["opening_chars"] + row["closing_chars"])
        host_output[host_slug] = {
            **{key: int(value) for key, value in row.items() if key != "body_chars"},
            "total_chars_saved": total_chars,
            "avg_pct_body_saved": (
                round(total_chars / row["body_chars"] * 100, 2) if row["body_chars"] else 0.0
            ),
        }

    for key in (
        "sources",
        "unknown_hosts",
        "transcript_wrapper_remnants",
        "youtube_title_wrapper_remnants",
        "useful_sectioning",
        "weak_sectioning",
        "preserved_unsectioned",
        "curation_state_missing",
        "asr_applied",
        "asr_checked_no_change",
        "asr_state_missing",
    ):
        summary.setdefault(key, 0)
    return {
        "filters": {
            "host_slug": host_filter,
            "published_since": published_since,
            "ingested_since": ingested_since,
        },
        "summary": dict(summary),
        "hosts": host_output,
    }


def print_text(report: dict[str, Any]) -> None:
    print(
        "host_slug\tsources\topening_trimmed\tclosing_trimmed\topening_chars\topening_words\t"
        "closing_chars\tclosing_words\ttotal_chars_saved\tavg_pct_body_saved"
    )
    for host_slug, row in report["hosts"].items():
        print(
            f"{host_slug}\t{row['sources']}\t{row['opening_trimmed']}\t{row['closing_trimmed']}\t"
            f"{row['opening_chars']}\t{row['opening_words']}\t{row['closing_chars']}\t"
            f"{row['closing_words']}\t{row['total_chars_saved']}\t{row['avg_pct_body_saved']:.2f}"
        )
    for key, value in report["summary"].items():
        print(f"{key}={value}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Report recent best-intake outcomes and trim savings.")
    parser.add_argument("--host-slug", help="Optional host slug filter.")
    parser.add_argument("--since", help="Compatibility lower bound on pub_date in YYYY-MM-DD format.")
    parser.add_argument("--ingested-since", help="Lower bound on ingest_date in YYYY-MM-DD format.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = collect_report(
        host_filter=args.host_slug,
        published_since=args.since,
        ingested_since=args.ingested_since,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

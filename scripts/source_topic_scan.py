#!/usr/bin/env python3
"""Scan date-scoped Narrative Geopolitics source bodies for topic terms."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "archive" / "sources" / "geopolitics" / "source-manifest.json"
SNIPPET_WINDOW = 90
MAX_SNIPPETS = 3


class SourceTopicScanError(ValueError):
    pass


@dataclass(frozen=True)
class Scope:
    run_date: str
    query: str
    terms: tuple[str, ...]
    voice_slug: str
    host_slug: str

    def public(self) -> dict[str, Any]:
        return {
            "date": self.run_date,
            "query": self.query,
            "terms": list(self.terms),
            "voice_slug": self.voice_slug,
            "host_slug": self.host_slug,
        }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan date-scoped Narrative Geopolitics source bodies for topic terms."
    )
    parser.add_argument("--date", required=True, help="Manifest date, YYYY-MM-DD.")
    parser.add_argument("--query", default="", help="Free-text query to split into terms.")
    parser.add_argument(
        "--term",
        action="append",
        default=[],
        help="Explicit search term. Repeat for OR matching.",
    )
    parser.add_argument("--voice-slug", default="", help="Optional voice slug filter.")
    parser.add_argument("--host-slug", default="", help="Optional host slug filter.")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def query_terms(query: str, explicit: Iterable[str]) -> tuple[str, ...]:
    terms: list[str] = []
    for value in explicit:
        stripped = value.strip()
        if stripped:
            terms.append(stripped)
    if query.strip():
        terms.append(query.strip())
        terms.extend(re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]{2,}", query))
    deduped: list[str] = []
    seen: set[str] = set()
    for term in terms:
        key = term.casefold()
        if key not in seen:
            seen.add(key)
            deduped.append(term)
    if not deduped:
        raise SourceTopicScanError("--query or at least one --term is required")
    return tuple(deduped)


def resolve_scope(args: argparse.Namespace) -> Scope:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.date):
        raise SourceTopicScanError("--date must use YYYY-MM-DD")
    return Scope(
        run_date=args.date,
        query=args.query.strip(),
        terms=query_terms(args.query, args.term),
        voice_slug=args.voice_slug.strip(),
        host_slug=args.host_slug.strip(),
    )


def load_manifest(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SourceTopicScanError("source manifest is not valid UTF-8 JSON") from error
    rows = payload.get("sources") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise SourceTopicScanError("source manifest must be an object with a sources list")
    return rows


def row_matches_scope(row: dict[str, Any], scope: Scope) -> bool:
    if row.get("date") != scope.run_date:
        return False
    if scope.host_slug and row.get("host_slug") != scope.host_slug:
        return False
    voices = row.get("voice_slugs")
    if scope.voice_slug and (
        not isinstance(voices, list) or scope.voice_slug not in voices
    ):
        return False
    return True


def scalar(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    return value if isinstance(value, str) else ""


def voices(row: dict[str, Any]) -> list[str]:
    value = row.get("voice_slugs")
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def term_pattern(term: str) -> re.Pattern[str]:
    return re.compile(re.escape(term), re.IGNORECASE)


def normalize_snippet(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def scan_text(text: str, terms: tuple[str, ...]) -> tuple[int, list[dict[str, str]]]:
    matches: list[tuple[int, int, str]] = []
    for term in terms:
        for match in term_pattern(term).finditer(text):
            matches.append((match.start(), match.end(), term))
    matches.sort(key=lambda item: (item[0], item[1], item[2].casefold()))
    snippets: list[dict[str, str]] = []
    occupied: list[range] = []
    for start, end, term in matches:
        if len(snippets) >= MAX_SNIPPETS:
            break
        if any(start in span for span in occupied):
            continue
        left = max(0, start - SNIPPET_WINDOW)
        right = min(len(text), end + SNIPPET_WINDOW)
        snippets.append({"term": term, "text": normalize_snippet(text[left:right])})
        occupied.append(range(left, right + 1))
    return len(matches), snippets


def build_report(rows: list[dict[str, Any]], scope: Scope) -> dict[str, Any]:
    scoped = [row for row in rows if row_matches_scope(row, scope)]
    results: list[dict[str, Any]] = []
    missing_sources: list[str] = []
    scanned_sources = 0
    for row in sorted(scoped, key=lambda item: scalar(item, "local_path")):
        local_path = scalar(row, "local_path")
        path = REPO_ROOT / Path(local_path)
        if not local_path or not path.exists():
            missing_sources.append(local_path or "(missing local_path)")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            missing_sources.append(local_path)
            continue
        scanned_sources += 1
        count, snippets = scan_text(text, scope.terms)
        if count:
            results.append(
                {
                    "date": scalar(row, "date"),
                    "title": scalar(row, "title") or "(untitled)",
                    "voice_slugs": voices(row),
                    "host_slug": scalar(row, "host_slug") or "host-unresolved",
                    "source_identity": scalar(row, "source_identity"),
                    "source_url": scalar(row, "source_url"),
                    "local_path": local_path,
                    "match_count": count,
                    "snippets": snippets,
                }
            )
    return {
        "scope": scope.public(),
        "summary": {
            "manifest_rows": len(scoped),
            "scanned_sources": scanned_sources,
            "matching_sources": len(results),
            "missing_sources": len(missing_sources),
            "missing_source_paths": missing_sources,
        },
        "results": results,
        "authority_boundary": (
            "Source topic scans provide retrieval coverage only. They do not verify claims, "
            "promote issue membership, create daily synthesis, or modify repository state."
        ),
    }


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_markdown(report: dict[str, Any]) -> str:
    scope = report["scope"]
    summary = report["summary"]
    lines = [
        "# Source Topic Scan",
        "",
        f"Date: `{scope['date']}`",
        f"Terms: `{', '.join(scope['terms'])}`",
    ]
    if scope["voice_slug"]:
        lines.append(f"Voice filter: `{scope['voice_slug']}`")
    if scope["host_slug"]:
        lines.append(f"Host filter: `{scope['host_slug']}`")
    lines += [
        "",
        f"Manifest rows: `{summary['manifest_rows']}`",
        f"Scanned sources: `{summary['scanned_sources']}`",
        f"Matching sources: `{summary['matching_sources']}`",
        f"Missing sources: `{summary['missing_sources']}`",
        "",
        (
            "Authority: retrieval coverage only; this scan does not verify claims, promote "
            "issue membership, create daily synthesis, or modify repository state."
        ),
        "",
    ]
    if summary["missing_source_paths"]:
        lines.append("## Missing Sources")
        lines.append("")
        for source in summary["missing_source_paths"]:
            lines.append(f"- `{source}`")
        lines.append("")
    if not report["results"]:
        lines.append("No matching sources found.")
        return "\n".join(lines) + "\n"
    for result in report["results"]:
        lines += [
            f"## {result['title']}",
            "",
            f"- Voices: `{', '.join(result['voice_slugs']) or 'voice-unresolved'}`",
            f"- Host: `{result['host_slug']}`",
            f"- Match count: `{result['match_count']}`",
            f"- Archive path: `{result['local_path']}`",
            "",
            "| Term | Context |",
            "| --- | --- |",
        ]
        for snippet in result["snippets"]:
            lines.append(
                f"| {markdown_cell(snippet['term'])} | {markdown_cell(snippet['text'])} |"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        args = parse_args(argv)
        scope = resolve_scope(args)
        report = build_report(load_manifest(args.manifest), scope)
    except SourceTopicScanError as error:
        print(f"source-topic-scan: {error}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

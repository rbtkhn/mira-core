#!/usr/bin/env python3
"""Report same-day multi-channel voice triangulation candidates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "archive" / "sources" / "geopolitics" / "source-manifest.json"
DATE_IN_PATH = re.compile(r"(?:^|/)sources/(\d{4}-\d{2}-\d{2})/")
ROUTINE_HOST_SETS = {frozenset(("alexander-mercouris", "the-duran"))}
AUTHOR_CONTROLLED_FORMS = {
    "article",
    "essay",
    "newsletter",
    "source-text",
    "substack-post",
    "x-post-text",
}
LEGAL_ACCOUNTABILITY_HOSTS = {"judging-freedom"}
LIVE_STRESS_HOSTS = {"mario-nawfal", "breaking-points"}
STRATEGIC_HOSTS = {
    "dialogue-works",
    "glenn-diesen",
    "neutrality-studies",
    "daniel-davis",
}


class TriangulationError(ValueError):
    pass


@dataclass(frozen=True)
class Scope:
    mode: str
    start: date
    end: date
    voice_slugs: tuple[str, ...]

    def public(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "start_date": self.start.isoformat(),
            "end_date": self.end.isoformat(),
            "voice_slugs": list(self.voice_slugs),
        }


@dataclass(frozen=True)
class CandidateRow:
    date: date
    voice: str
    host: str
    title: str
    source_identity: str
    source_url: str
    local_path: str
    date_source: str
    source_form: str
    kind: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report same-day multi-channel voice triangulation candidates."
    )
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--month", help="Month scope, YYYY-MM.")
    scope.add_argument("--start-date", help="Start date, YYYY-MM-DD.")
    parser.add_argument("--end-date", help="End date, YYYY-MM-DD. Required with --start-date.")
    parser.add_argument(
        "--voice-slug",
        action="append",
        default=[],
        help="Optional voice slug filter. Repeat for OR matching.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH,
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def parse_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise TriangulationError(f"{label} must use YYYY-MM-DD: {value}") from error


def month_end(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1) - timedelta(days=1)
    return date(value.year, value.month + 1, 1) - timedelta(days=1)


def resolve_scope(args: argparse.Namespace) -> Scope:
    voices = tuple(sorted(set(args.voice_slug or ())))
    if args.month:
        try:
            start = date.fromisoformat(f"{args.month}-01")
        except ValueError as error:
            raise TriangulationError("--month must use YYYY-MM") from error
        return Scope("month", start, month_end(start), voices)
    if not args.end_date:
        raise TriangulationError("--end-date is required with --start-date")
    start = parse_date(args.start_date, "--start-date")
    end = parse_date(args.end_date, "--end-date")
    if end < start:
        raise TriangulationError("--end-date must be on or after --start-date")
    return Scope("date-range", start, end, voices)


def load_manifest(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise TriangulationError("source manifest is not valid UTF-8 JSON") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("sources"), list):
        raise TriangulationError("source manifest must be an object with a sources list")
    rows = payload["sources"]
    if any(not isinstance(row, dict) for row in rows):
        raise TriangulationError("source manifest contains a non-object row")
    return rows


def row_date(row: dict[str, Any]) -> tuple[date | None, str | None]:
    raw = row.get("date")
    if isinstance(raw, str):
        try:
            return date.fromisoformat(raw), "manifest"
        except ValueError:
            pass
    path = row.get("local_path")
    if isinstance(path, str):
        match = DATE_IN_PATH.search(path.replace("\\", "/"))
        if match:
            try:
                return date.fromisoformat(match.group(1)), "path-fallback"
            except ValueError:
                pass
    return None, None


def scalar(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    return value if isinstance(value, str) else ""


def candidate_rows(rows: Iterable[dict[str, Any]], scope: Scope) -> list[CandidateRow]:
    output: list[CandidateRow] = []
    voice_filter = set(scope.voice_slugs)
    for row in rows:
        value, source = row_date(row)
        if value is None or source is None or value < scope.start or value > scope.end:
            continue
        voices = row.get("voice_slugs")
        if not isinstance(voices, list):
            continue
        for voice in voices:
            if not isinstance(voice, str) or not voice:
                continue
            if voice_filter and voice not in voice_filter:
                continue
            output.append(
                CandidateRow(
                    date=value,
                    voice=voice,
                    host=scalar(row, "host_slug") or "host-unresolved",
                    title=scalar(row, "title") or "(untitled)",
                    source_identity=scalar(row, "source_identity") or scalar(row, "source_url"),
                    source_url=scalar(row, "source_url"),
                    local_path=scalar(row, "local_path"),
                    date_source=source,
                    source_form=scalar(row, "source_form"),
                    kind=scalar(row, "kind"),
                )
            )
    return output


def host_type(row: CandidateRow) -> str:
    form = row.source_form.casefold()
    kind = row.kind.casefold()
    url = row.source_url.casefold()
    identity = row.source_identity.casefold()
    if (
        form in AUTHOR_CONTROLLED_FORMS
        or kind in AUTHOR_CONTROLLED_FORMS
        or "substack.com" in url
        or "substack.com" in identity
    ):
        return "author-controlled"
    if row.host in LEGAL_ACCOUNTABILITY_HOSTS:
        return "legal-accountability-host"
    if row.host in LIVE_STRESS_HOSTS:
        return "live-stress-test"
    if row.host in STRATEGIC_HOSTS:
        return "friendly-strategic-host"
    return "independent-interview-host"


def roi_tier(rows: list[CandidateRow]) -> tuple[str, str]:
    hosts = frozenset(row.host for row in rows)
    if hosts in ROUTINE_HOST_SETS:
        return "routine", "known standing division of labor"
    types = {host_type(row) for row in rows}
    if "author-controlled" in types and len(types) > 1:
        return "high", "author-controlled venue paired with interview pressure"
    if "legal-accountability-host" in types and (
        "friendly-strategic-host" in types or "live-stress-test" in types
    ):
        return "high", "accountability pressure paired with strategic or live framing"
    if "live-stress-test" in types and "friendly-strategic-host" in types:
        return "high", "live stress-test paired with strategic synthesis pressure"
    return "medium", "distinct host channels with plausible framing difference"


def build_report(rows: list[dict[str, Any]], scope: Scope) -> dict[str, Any]:
    grouped: dict[tuple[date, str], list[CandidateRow]] = defaultdict(list)
    for row in candidate_rows(rows, scope):
        grouped[(row.date, row.voice)].append(row)

    candidates: list[dict[str, Any]] = []
    for (run_date, voice), group in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1])):
        hosts = sorted({row.host for row in group})
        if len(group) < 2 or len(hosts) < 2:
            continue
        tier, reason = roi_tier(group)
        candidates.append(
            {
                "date": run_date.isoformat(),
                "voice": voice,
                "hosts": hosts,
                "source_count": len(group),
                "roi_tier": tier,
                "roi_basis": reason,
                "date_fallback_used": any(row.date_source == "path-fallback" for row in group),
                "sources": [
                    {
                        "host": row.host,
                        "host_type": host_type(row),
                        "title": row.title,
                        "source_identity": row.source_identity,
                        "source_url": row.source_url,
                        "local_path": row.local_path,
                        "date_source": row.date_source,
                    }
                    for row in sorted(group, key=lambda item: (item.host, item.title, item.local_path))
                ],
            }
        )

    return {
        "scope": scope.public(),
        "summary": {
            "candidate_count": len(candidates),
            "source_count": sum(candidate["source_count"] for candidate in candidates),
            "voices": sorted({candidate["voice"] for candidate in candidates}),
            "date_fallback_candidates": sum(1 for candidate in candidates if candidate["date_fallback_used"]),
        },
        "candidates": candidates,
        "authority_boundary": (
            "Triangulation candidates are analytic triage prompts only. They do not verify source "
            "claims, change archive routing, require synthesis, or modify repository state."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    scope = report["scope"]
    lines = [
        "# Same-Day Multi-Channel Triangulation Candidates",
        "",
        (
            f"Scope: `{scope['start_date']}` to `{scope['end_date']}`"
            + (f"; voices: `{', '.join(scope['voice_slugs'])}`" if scope["voice_slugs"] else "")
        ),
        "",
        f"Candidates: `{report['summary']['candidate_count']}`",
        f"Sources involved: `{report['summary']['source_count']}`",
        "",
        (
            "Authority: triage prompt only; this report does not verify claims, change archive "
            "routing, require synthesis, or modify repository state."
        ),
        "",
    ]
    if not report["candidates"]:
        lines.append("No same-day multi-channel voice candidates found.")
        return "\n".join(lines) + "\n"
    for candidate in report["candidates"]:
        fallback = " path-date fallback used" if candidate["date_fallback_used"] else ""
        lines += [
            f"## {candidate['date']} `{candidate['voice']}`",
            "",
            f"- Hosts: `{', '.join(candidate['hosts'])}`",
            f"- ROI tier: `{candidate['roi_tier']}` - {candidate['roi_basis']}{fallback}",
            "",
            "| Host | Host type | Title | Identity | Archive path |",
            "| --- | --- | --- | --- | --- |",
        ]
        for source in candidate["sources"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        source["host"],
                        source["host_type"],
                        source["title"].replace("|", "\\|"),
                        source["source_identity"].replace("|", "\\|"),
                        source["local_path"],
                    ]
                )
                + " |"
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
    except TriangulationError as error:
        print(f"triangulation-candidates: {error}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

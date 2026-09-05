from __future__ import annotations

from repository_paths import resolve_geopolitics_reference
import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DAILY_ROOT = resolve_geopolitics_reference(REPO_ROOT, 'geopolitics') / "work" / "daily"
CANONICAL_FILES = ("synthesis.md", "daily-brief.md")
MIN_PARAGRAPH_CHARS = 120
SOURCE_HYGIENE_PREFIX = "confirm each archive path resolves"


def _path(name: str):
    """Resolve defaults at use time while honoring explicit module overrides."""
    original, factory = _PATH_DEFAULTS[name]
    value = globals()[name]
    return factory() if value == original else value


_PATH_DEFAULTS = {
    'DAILY_ROOT': (DAILY_ROOT, lambda: resolve_geopolitics_reference(REPO_ROOT, 'geopolitics') / 'work' / 'daily'),
}


@dataclass(frozen=True)
class ParagraphOccurrence:
    run_date: str
    artifact: str
    text: str


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report exact long-paragraph reuse across canonical daily narrative files."
    )
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(arguments)


def normalize_paragraph(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def eligible_paragraphs(text: str) -> list[str]:
    result: list[str] = []
    for raw in re.split(r"(?:\r?\n){2,}", text):
        paragraph = normalize_paragraph(raw)
        lowered = paragraph.lower()
        if len(paragraph) < MIN_PARAGRAPH_CHARS:
            continue
        if paragraph.startswith(("|", "#", "```")):
            continue
        if SOURCE_HYGIENE_PREFIX in lowered:
            continue
        result.append(paragraph)
    return result


def collect(
    start: date, end: date, daily_root: Path = None
) -> list[ParagraphOccurrence]:
    daily_root = _path('DAILY_ROOT') if daily_root is None else daily_root
    if start > end:
        raise ValueError("--start must not be later than --end")
    occurrences: list[ParagraphOccurrence] = []
    if not daily_root.exists():
        return occurrences
    for run_dir in sorted(path for path in daily_root.iterdir() if path.is_dir()):
        try:
            run_date = date.fromisoformat(run_dir.name)
        except ValueError:
            continue
        if not start <= run_date <= end:
            continue
        for artifact in CANONICAL_FILES:
            path = run_dir / artifact
            if not path.exists():
                continue
            for paragraph in eligible_paragraphs(path.read_text(encoding="utf-8")):
                occurrences.append(
                    ParagraphOccurrence(run_dir.name, artifact, paragraph)
                )
    return occurrences


def report_payload(occurrences: list[ParagraphOccurrence]) -> dict:
    grouped: dict[str, list[ParagraphOccurrence]] = defaultdict(list)
    for item in occurrences:
        grouped[item.text.casefold()].append(item)
    repeated = [
        values
        for values in grouped.values()
        if len({item.run_date for item in values}) > 1
    ]
    repeated.sort(key=lambda values: (-len(values), values[0].text.casefold()))
    repeated_instances = sum(len(values) for values in repeated)
    total = len(occurrences)
    return {
        "files": len({(item.run_date, item.artifact) for item in occurrences}),
        "paragraphs": total,
        "unique_paragraphs": len(grouped),
        "repeated_instances": repeated_instances,
        "reuse_percent": round(100 * repeated_instances / total, 1) if total else 0.0,
        "groups": [
            {
                "count": len(values),
                "dates": sorted({item.run_date for item in values}),
                "artifacts": sorted(
                    {f"{item.run_date}/{item.artifact}" for item in values}
                ),
                "text": values[0].text,
            }
            for values in repeated
        ],
    }


def main(arguments: list[str] | None = None) -> int:
    args = parse_args(arguments)
    try:
        payload = report_payload(collect(args.start, args.end))
    except ValueError as error:
        raise SystemExit(str(error)) from error
    payload = {
        "start": args.start.isoformat(),
        "end": args.end.isoformat(),
        "mode": "advisory",
        **payload,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        for key in (
            "start",
            "end",
            "mode",
            "files",
            "paragraphs",
            "unique_paragraphs",
            "repeated_instances",
            "reuse_percent",
        ):
            print(f"{key}={payload[key]}")
        for group in payload["groups"]:
            print(
                f"REPEAT count={group['count']} dates={','.join(group['dates'])} "
                f"text={group['text'][:180]}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

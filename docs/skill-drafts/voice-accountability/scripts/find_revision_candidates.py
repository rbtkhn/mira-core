#!/usr/bin/env python3
"""Rank transcript passages that may contain a self-revision.

This is a retrieval aid. Its output requires speaker and meaning adjudication.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path


PATTERNS = (
    (
        5,
        "explicit",
        re.compile(r"(?<!if )\bI (?:was|am|got (?:that|it)) wrong\b", re.I),
    ),
    (5, "explicit", re.compile(r"\bI (?:misjudged|misread|misunderstood|underestimated|overestimated)\b", re.I)),
    (4, "explicit", re.compile(r"\b(?:my|the) (?:mistake|error|miscalculation)\b", re.I)),
    (4, "position", re.compile(r"\bI (?:used to|no longer) (?:think|believe|support|expect)\b", re.I)),
    (4, "position", re.compile(r"\bI (?:changed|have changed|revised) my (?:mind|view|position|assessment)\b", re.I)),
    (3, "prediction", re.compile(r"\bI (?:thought|expected|predicted|assumed|believed)\b", re.I)),
    (3, "explicit", re.compile(r"\bI (?:was|had been) (?:ignorant|naive|mistaken)\b", re.I)),
    (2, "collective", re.compile(r"\bwe (?:were wrong|misjudged|misread|underestimated|overestimated)\b", re.I)),
)

CONTRAST = re.compile(r"\b(?:but|however|instead|on the contrary|turns? out|didn['’]t)\b", re.I)

DATE_DIR = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="date_from", required=True, type=date.fromisoformat)
    parser.add_argument("--to", dest="date_to", required=True, type=date.fromisoformat)
    parser.add_argument("--voice", help="Case-insensitive metadata or filename filter")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--context", type=int, default=2, help="Lines on each side")
    parser.add_argument("--limit", type=int, default=100)
    return parser.parse_args()


def metadata(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    if not text.startswith("---"):
        return result
    for line in text.splitlines()[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"\'')
    return result


def main() -> int:
    args = parse_args()
    if args.date_from > args.date_to:
        raise SystemExit("--from must not be later than --to")
    archive = (
        args.repo_root.resolve() / "archive" / "sources" / "geopolitics" / "sources"
    )
    if not archive.is_dir():
        raise SystemExit(f"archive source directory not found: {archive}")

    files_examined = 0
    candidates: list[dict[str, object]] = []
    voice_filter = args.voice.casefold() if args.voice else None

    for day_dir in sorted(archive.iterdir()):
        if not day_dir.is_dir() or not DATE_DIR.match(day_dir.name):
            continue
        day = date.fromisoformat(day_dir.name)
        if not args.date_from <= day <= args.date_to:
            continue
        for path in sorted(day_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            meta = metadata(text)
            haystack = " ".join((path.name, *meta.values())).casefold()
            if voice_filter and voice_filter not in haystack:
                continue
            files_examined += 1
            lines = text.splitlines()
            for index, line in enumerate(lines):
                matches = [(weight, kind, pattern.pattern) for weight, kind, pattern in PATTERNS if pattern.search(line)]
                if not matches:
                    continue
                score = sum(weight for weight, _, _ in matches)
                signals = {kind for _, kind, _ in matches}
                if CONTRAST.search(line):
                    score += 2
                    signals.add("revision")
                start = max(0, index - args.context)
                end = min(len(lines), index + args.context + 1)
                candidates.append(
                    {
                        "score": score,
                        "date": day.isoformat(),
                        "path": str(path.resolve()),
                        "line": index + 1,
                        "metadata": meta,
                        "signals": sorted(signals),
                        "context": "\n".join(f"{n + 1}: {lines[n]}" for n in range(start, end)),
                    }
                )

    candidates.sort(key=lambda item: (-int(item["score"]), str(item["date"]), str(item["path"]), int(item["line"])))
    payload = {
        "date_from": args.date_from.isoformat(),
        "date_to": args.date_to.isoformat(),
        "voice_filter": args.voice,
        "files_examined": files_examined,
        "candidate_count": len(candidates),
        "returned_count": min(len(candidates), args.limit),
        "notice": "Retrieval candidates only; resolve speaker and adjudicate meaning from transcript context.",
        "candidates": candidates[: args.limit],
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

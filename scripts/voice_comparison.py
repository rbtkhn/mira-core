from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
MANIFEST = NG_ROOT / "archive" / "source-manifest.json"
OUT_ROOT = NG_ROOT / "work" / "comparisons"


@dataclass
class Quote:
    voice: str
    text: str
    path: Path
    line: int
    host: str


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def load_rows() -> list[dict]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, list) else data.get("sources", [])


def source_path(row: dict) -> Path:
    path = REPO_ROOT / row["local_path"]
    if not path.exists():
        raise ValueError(f"missing archive source: {row['local_path']}")
    return path


def body_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "---\n" in text:
        _, _, text = text.partition("---\n")
        _, _, text = text.partition("\n---\n")
    return text.splitlines()


def candidate_lines(lines: list[str], object_text: str) -> list[tuple[int, str]]:
    terms = [t.casefold() for t in re.findall(r"[A-Za-z0-9]+", object_text) if len(t) > 2]
    keywords = ("capture", "control", "take", "blockade", "isolate", "objective", "end", "move", "cross", "fall", "port")
    results: list[tuple[int, str]] = []
    for index, raw in enumerate(lines):
        width = 1
        window = " ".join(" ".join(lines[index : index + width]).split())
        folded = window.casefold()
        if not window or window.startswith("#") or len(window.split()) < 8:
            continue
        # Metadata/editorial notes are navigation material, not speaker evidence.
        if any(marker in folded for marker in ("cleanup notes", "editorial note:", "source note:", "quality note:")):
            continue
        if not all(term in folded for term in terms):
            continue
        if any(word in folded for word in keywords):
            # Prefer a complete local transcript turn over a chopped ASR line.
            words = window.split()
            if len(words) <= 60:
                results.append((index + 1, window))
    return results


def collect_quotes(rows: list[dict], voices: list[str], object_text: str, date_start: str | None = None, date_end: str | None = None) -> dict[str, list[Quote]]:
    collected = {voice: [] for voice in voices}
    seen: set[tuple[str, str]] = set()
    for row in rows:
        row_date = str(row.get("date") or "")
        if date_start and row_date < date_start:
            continue
        if date_end and row_date > date_end:
            continue
        row_voices = {str(v) for v in row.get("voice_slugs", [])}
        matches = [voice for voice in voices if voice in row_voices]
        if not matches:
            continue
        path = source_path(row)
        host = str(row.get("host_slug") or row.get("channel_name") or "unresolved")
        for number, text in candidate_lines(body_lines(path), object_text):
            if len(text.split()) > 60:
                continue
            for voice in matches:
                key = (voice, text)
                overlaps = any(
                    existing.voice == voice
                    and existing.path == path
                    and abs(existing.line - number) <= 5
                    for existing in collected[voice]
                )
                if key in seen or overlaps or len(collected[voice]) >= 3:
                    continue
                seen.add(key)
                collected[voice].append(Quote(voice, text, path, number, host))
    missing = [voice for voice, quotes in collected.items() if len(quotes) < 3]
    if missing:
        raise ValueError("insufficient qualifying quotes for: " + ", ".join(missing))
    return collected


def labels(quotes: list[Quote]) -> tuple[str, str, str]:
    text = " ".join(q.text.casefold() for q in quotes)
    mechanism = "pressure / isolation" if any(x in text for x in ("blockade", "isolate", "port")) else "operational advance"
    timing = "conditional or longer-horizon" if any(x in text for x in ("eventually", "long-term", "can't predict", "cannot predict", "later")) else "near-term or asserted"
    confidence = "qualified" if any(x in text for x in ("might", "could", "possibly", "can't", "cannot")) else "high-certainty language"
    return mechanism, timing, confidence


def render(object_text: str, voices: list[str], quotes: dict[str, list[Quote]], date_start: str | None = None, date_end: str | None = None) -> str:
    date_scope = f"; date window `{date_start or 'open'}` to `{date_end or 'open'}`" if date_start or date_end else ""
    lines = [f"# Voice Comparison: {object_text}", "", "Status: `archive-statements-only`", "", f"Scope: `{object_text}` across explicitly named voices: " + ", ".join(f"`{v}`" for v in voices) + date_scope + ".", "", "## Evidence Boundary", "", "This note compares archive statements, not reality. Repetition across archive sources is not independent corroboration. Use `reality-check` for external verification and `voice-accountability` for self-revision audits.", "", "## Voice Evidence", ""]
    for voice in voices:
        mechanism, timing, confidence = labels(quotes[voice])
        lines += [f"### {voice}", "", f"Observed mechanism: **{mechanism}**.", f"Observed timing language: **{timing}**.", f"Observed confidence language: **{confidence}**.", "", "Quotes:", ""]
        for q in quotes[voice]:
            rel = q.path.relative_to(REPO_ROOT).as_posix()
            lines.append(f'> “{q.text}”')
            lines.append(f"> — `{voice}`; host `{q.host}`; [archive source]({rel}:{q.line})")
            lines.append("")
    lines += ["## Comparison Matrix", "", "| Dimension | " + " | ".join(voices) + " |", "| --- | " + " | ".join("---" for _ in voices) + " |"]
    for dim, index in (("Mechanism", 0), ("Timing", 1), ("Confidence", 2)):
        values = [labels(quotes[v])[index] for v in voices]
        lines.append(f"| {dim} | " + " | ".join(values) + " |")
    lines += ["", "## Convergence and Divergence", "", "Convergence should be read as shared archive framing, not confirmation. Divergence is preserved where voices differ on mechanism, timing, confidence, or implied falsifier.", "", "## Falsifier Prompts", "", f"- What observable outcome would disconfirm each voice's stated end-state for `{object_text}`?", "- Does the predicted mechanism occur within the stated horizon?", "- Does the object remain strategically viable despite the pressure described?", "", "## Provenance", "", "Every quotation above is drawn from a manifest-backed archive transcript and retains its source path and line anchor.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    compare = sub.add_parser("compare")
    compare.add_argument("--object", required=True)
    compare.add_argument("--voice", action="append", required=True)
    compare.add_argument("--date-start")
    compare.add_argument("--date-end")
    compare.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if len(args.voice) < 2:
        parser.error("compare requires at least two explicit --voice values")
    voices = list(dict.fromkeys(args.voice))
    report = render(args.object, voices, collect_quotes(load_rows(), voices, args.object, args.date_start, args.date_end), args.date_start, args.date_end)
    target = OUT_ROOT / f"{slug(args.object)}--{'-'.join(sorted(slug(v) for v in voices))}.md"
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(report, encoding="utf-8")
        print(f"Wrote comparison: {target.relative_to(REPO_ROOT).as_posix()}")
    else:
        print(report)
        print(f"\nDRY RUN: {target.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

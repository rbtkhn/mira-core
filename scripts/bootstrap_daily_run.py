from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from datetime import date


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
MANIFEST_PATH = NG_ROOT / "archive" / "source-manifest.json"
DAILY_ROOT = NG_ROOT / "work" / "daily"
TEMPLATES_ROOT = NG_ROOT / "templates"
LEDGER_PATH = NG_ROOT / "work" / "forecasts" / "forecast-ledger.md"


LEDGER_ROW_RE = re.compile(
    r"^\|\s*`(NG-\d{8}-F\d{2})`\s*\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*`(low|plausible|likely|high)`\s*\|\s*`([^`]+)`\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*`([^`]+)`\s*\|$"
)
TRIAGE_ROW_RE = re.compile(
    r"^\|\s*`(NG-\d{8}-F\d{2})`\s*\|\s*`[^`]+`\s*\|\s*`[^`]+`\s*\|"
    r"\s*`[^`]+`\s*\|\s*`([^`]+)`\s*\|\s*`(yes|no)`\s*\|"
)


VOICE_LABELS = {
    "aguilar": "Aguilar",
    "barnes": "Barnes",
    "baud": "Baud",
    "blumenthal": "Blumenthal",
    "crooke": "Crooke",
    "davis": "Davis",
    "diesen": "Diesen",
    "freeman": "Freeman",
    "helmer": "Helmer",
    "hoh": "Hoh",
    "jermy": "Jermy",
    "johnson": "Johnson",
    "karaganov": "Karaganov",
    "krainer": "Krainer",
    "krapivnik": "Krapivnik",
    "macgregor": "Macgregor",
    "marandi": "Marandi",
    "martyanov": "Martyanov",
    "mate": "Mate",
    "matlock": "Matlock",
    "mcgovern": "McGovern",
    "mearsheimer": "Mearsheimer",
    "mercouris": "Mercouris",
    "pape": "Pape",
    "parsi": "Parsi",
    "postol": "Postol",
    "ritter": "Ritter",
    "sachs": "Sachs",
    "weichert": "Weichert",
    "wilkerson": "Wilkerson",
}

HOST_LABELS = {
    "alexander-mercouris": "Alexander Mercouris",
    "breaking-points": "Breaking Points",
    "daniel-davis": "Daniel Davis",
    "dialogue-works": "Dialogue Works",
    "glenn-diesen": "Glenn Diesen",
    "judging-freedom": "Judging Freedom",
    "mario-nawfal": "Mario Nawfal",
    "redacted-news": "Redacted",
    "the-duran": "The Duran",
    "tucker-carlson": "Tucker Carlson",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap a daily Narrative Geopolitics run from the manifest day batch."
    )
    parser.add_argument("--date", required=True, help="Run date in YYYY-MM-DD format.")
    parser.add_argument(
        "--status",
        default="live-intake-first",
        help="Status to write into generated daily files.",
    )
    parser.add_argument(
        "--retro",
        action="store_true",
        help="Mark intake rows as already-imported instead of imported.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing daily run files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without writing files.",
    )
    return parser.parse_args()


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))


def load_template(name: str) -> str:
    return (TEMPLATES_ROOT / name).read_text(encoding="utf-8")


def load_ledger_text() -> str:
    return LEDGER_PATH.read_text(encoding="utf-8")


def parse_iso_date(value: str) -> date:
    return date.fromisoformat(value)


def label_voice(slugs: list[str]) -> str:
    if not slugs:
        return ""
    return " / ".join(VOICE_LABELS.get(slug, slug.replace("-", " ").title()) for slug in slugs)


def label_host(host_slug: str | None) -> str:
    if not host_slug:
        return "none"
    return HOST_LABELS.get(host_slug, host_slug.replace("-", " ").title())


def relative_archive_path(local_path: str) -> str:
    marker = "narrative-geopolitics/"
    return local_path.split(marker, 1)[1] if marker in local_path else local_path


def archive_link(local_path: str) -> str:
    rel = relative_archive_path(local_path)
    if rel.startswith("archive/"):
        return "../../../" + rel
    return "../../../" + rel


def extract_due_review_hooks(run_date: str) -> list[dict[str, str]]:
    run_day = parse_iso_date(run_date)
    due_hooks: list[dict[str, str]] = []
    ledger_text = load_ledger_text()
    accountable_open = {
        match.group(1)
        for line in ledger_text.splitlines()
        if (match := TRIAGE_ROW_RE.match(line.strip()))
        and match.group(2) == "open"
        and match.group(3) == "yes"
    }
    for line in ledger_text.splitlines():
        match = LEDGER_ROW_RE.match(line.strip())
        if not match:
            continue
        hook_id, hook_date, crisis_object, claim, band, review_date, source_label, source_link, status = match.groups()
        if status != "open" or hook_id not in accountable_open:
            continue
        if parse_iso_date(review_date) <= run_day:
            due_hooks.append(
                {
                    "hook_id": hook_id,
                    "hook_date": hook_date,
                    "crisis_object": crisis_object,
                    "claim": claim,
                    "band": band,
                    "review_date": review_date,
                    "source_label": source_label,
                    "source_link": source_link,
                    "status": status,
                }
            )
    return due_hooks


def build_sources_md(run_date: str, status: str, rows: list[dict[str, Any]], retro: bool) -> str:
    intake_status = "already-imported" if retro else "imported"
    archive_dir = f"narrative-geopolitics/archive/sources/{run_date}/"
    intro = (
        f"This run is a retrospective judgment run built from already-imported central archive "
        f"sources for `{run_date}`."
        if retro
        else f"This run is grounded in the `{run_date}` day batch already landed in the central archive."
    )

    intake_lines = []
    run_lines = []
    quote_lines = []
    claim_lines = []
    for index, row in enumerate(rows, start=1):
        source_id = f"SRC-{index:02d}"
        claim_id = f"CLM-{index:02d}"
        rel_archive = relative_archive_path(row["local_path"])
        archive_md = f"[{run_date} {label_voice(row.get('voice_slugs', [])) or source_id}]({archive_link(row['local_path'])})"
        voice_label = label_voice(row.get("voice_slugs", []))
        host_label = label_host(row.get("host_slug"))
        modality = row.get("modality", "")
        source_class = row.get("source_class", "")
        title = row.get("title", "")
        notes = f"{source_class}; review and narrow to owning crisis object before synthesis."

        intake_lines.append(
            f"| `{rel_archive}` | {modality or 'unknown'} | `{intake_status}` | `yes` | {voice_label} | {host_label} | {notes} |"
        )
        run_lines.append(
            f"| `{source_id}` | {voice_label} | {host_label} | {modality or 'unknown'} | {archive_md} | {title} |"
        )
        quote_lines.append(f"| `{source_id}` |  |  |")
        claim_lines.append(
            f"| `{claim_id}` | `{source_id}` |  | {voice_label} via {host_label} | `candidate` |"
        )

    return f"""# Sources

Date: `{run_date}`

Status: `{status}`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `{archive_dir}`

## Intake Batch

{intro}

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(intake_lines)}

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(run_lines)}

## Load-Bearing Quotes

Use short direct quotes only when wording matters. Keep quotes brief and tie each quote to an analytic job.

| Source ID | Quote | Why It Matters |
| --- | --- | --- |
{chr(10).join(quote_lines)}

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
{chr(10).join(claim_lines)}

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.
"""


def build_from_template(name: str, run_date: str, status: str) -> str:
    text = load_template(name)
    text = text.replace("YYYY-MM-DD", run_date)
    # Templates live one directory below the repository root, while rendered
    # daily artifacts live two directories below it.
    if name in {"synthesis.md", "forecast.md", "daily-brief.md"}:
        text = text.replace("](../method/", "](../../../method/")
        text = text.replace("](../work/verification/", "](../../../work/verification/")
    if "Status: `template`" in text:
        text = text.replace("Status: `template`", f"Status: `{status}`", 1)
    if name == "daily-brief.md":
        text = text.replace("Status: `draft`", "Status: `not-promoted`", 1)
    if name == "forecast.md":
        due_hooks = extract_due_review_hooks(run_date)
        text = inject_due_review_hooks(text, due_hooks)
    return text


def inject_due_review_hooks(text: str, due_hooks: list[dict[str, str]]) -> str:
    if not due_hooks:
        block = (
            "## Due Review Hooks\n\n"
            "No open ledger hooks are due on or before this run date.\n\n"
        )
    else:
        rows = []
        for hook in due_hooks:
            daily_source_link = f"../{hook['hook_date']}/forecast.md"
            rows.append(
                f"| `{hook['hook_id']}` | `{hook['hook_date']}` | {hook['crisis_object']} | "
                f"{hook['claim']} | `{hook['band']}` | `{hook['review_date']}` | "
                f"[{hook['source_label']}]({daily_source_link}) |"
            )
        block = (
            "## Due Review Hooks\n\n"
            "Open forecast hooks whose review date is due on or before this run date:\n\n"
            "| Hook ID | Original Date | Crisis Object | Claim | Probability Band | Review Date | Source Run |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            f"{chr(10).join(rows)}\n\n"
        )
    marker = "## Hooks\n"
    if marker not in text:
        return text
    return text.replace(marker, block + marker, 1)


def write_text(path: Path, content: str, force: bool, dry_run: bool) -> str:
    if path.exists() and not force:
        return f"skip {path.relative_to(REPO_ROOT)}"
    if dry_run:
        return f"plan {path.relative_to(REPO_ROOT)}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")
    return f"write {path.relative_to(REPO_ROOT)}"


def main() -> None:
    args = parse_args()
    manifest = load_manifest()
    rows = [row for row in manifest.get("sources", []) if row.get("date") == args.date]
    rows.sort(key=lambda row: row.get("local_path", ""))

    if not rows:
        raise SystemExit(f"No manifest rows found for {args.date}.")

    run_dir = DAILY_ROOT / args.date
    actions = []
    actions.append(
        write_text(
            run_dir / "sources.md",
            build_sources_md(args.date, args.status, rows, args.retro),
            args.force,
            args.dry_run,
        )
    )
    for name in ("synthesis.md", "forecast.md", "judgment.md", "daily-brief.md"):
        actions.append(
            write_text(
                run_dir / name,
                build_from_template(name, args.date, args.status),
                args.force,
                args.dry_run,
            )
        )

    print(f"date={args.date}")
    print(f"rows={len(rows)}")
    for action in actions:
        print(action)


if __name__ == "__main__":
    main()

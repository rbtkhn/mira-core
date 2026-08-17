from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import validate_daily_run
import archive_audit


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
MANIFEST_PATH = NG_ROOT.parent / "archive" / "sources" / "geopolitics" / "source-manifest.json"
DAILY_ROOT = NG_ROOT / "work" / "daily"

REQUIRED_DAILY_FILES = ("sources.md", "synthesis.md", "forecast.md", "daily-brief.md", "issue.md")
HOOK_RE = re.compile(r"\b(?:NG-)?2026\d{4}-F\d{2}\b|\bNG-2026\d{4}-F\d{2}\b")
NG_HOOK_RE = re.compile(r"\bNG-(\d{8})-F\d{2}\b")
LEGACY_HOOK_RE = re.compile(r"\bF-(\d{8})-\d{2}\b")
OPC_RE = re.compile(r"\bOPC-\d{8}-\d{2}\b")


@dataclass(frozen=True)
class DensityRow:
    date: str
    manifest_sources: int
    density_class: str
    daily_stack_files: str
    validation_failures: int
    validation_warnings: int
    forecast_hooks: int
    same_day_hooks: int
    carried_hooks: int
    opc_claims: int
    issue_stories: int
    narrative_load_ratio: float
    classifications: list[str]
    title: str
    crisis_object: str
    issue_exists: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report Narrative Geopolitics source density and narrative-load triage for a date range."
    )
    parser.add_argument("--month", help="Optional month selector in YYYY-MM format.")
    parser.add_argument("--start-date", help="Inclusive start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", help="Inclusive end date in YYYY-MM-DD format.")
    parser.add_argument("--markdown", help="Optional Markdown report output path.")
    parser.add_argument("--csv", dest="csv_path", help="Optional CSV output path.")
    parser.add_argument("--json", dest="json_path", help="Optional JSON output path.")
    return parser.parse_args()


def iter_dates(month: str | None, start_date: str | None, end_date: str | None) -> list[str]:
    if month:
        start = date.fromisoformat(f"{month}-01")
        end = (
            date(start.year + 1, 1, 1) - timedelta(days=1)
            if start.month == 12
            else date(start.year, start.month + 1, 1) - timedelta(days=1)
        )
    elif start_date and end_date:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        if end < start:
            raise SystemExit("--end-date must be on or after --start-date")
    else:
        raise SystemExit("Provide --month or both --start-date and --end-date.")

    values: list[str] = []
    current = start
    while current <= end:
        values.append(current.isoformat())
        current += timedelta(days=1)
    return values


def load_manifest_counts(manifest_path: Path = MANIFEST_PATH) -> dict[str, int]:
    if not manifest_path.exists():
        return {}
    return archive_audit.load_manifest_counts(manifest_path)


def read_daily_text(run_date: str, daily_root: Path = DAILY_ROOT) -> dict[str, str]:
    run_dir = daily_root / run_date
    texts: dict[str, str] = {}
    for name in REQUIRED_DAILY_FILES:
        path = run_dir / name
        if path.exists():
            texts[name] = path.read_text(encoding="utf-8")
    return texts


def section(text: str, name: str) -> str:
    match = re.search(rf"^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return match.group(1).strip() if match else ""


def title_from_brief(text: str) -> str:
    return next((line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("# ")), "")


def crisis_from_synthesis(text: str) -> str:
    crisis = " ".join(section(text, "Crisis Object").split())
    return crisis[:180]


def hook_ids(text: str) -> set[str]:
    hooks = set()
    for match in NG_HOOK_RE.finditer(text):
        hooks.add(match.group(0))
    for match in LEGACY_HOOK_RE.finditer(text):
        hooks.add(match.group(0))
    return hooks


def hook_date(hook_id: str) -> str | None:
    match = NG_HOOK_RE.fullmatch(hook_id) or LEGACY_HOOK_RE.fullmatch(hook_id)
    if not match:
        return None
    raw = match.group(1)
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"


def selected_issue_stories(synthesis_text: str) -> int:
    desk = section(synthesis_text, "Issue Story Desk")
    count = 0
    for line in desk.splitlines():
        if not line.startswith("| `NGI-"):
            continue
        cells = [cell.strip(" `") for cell in line.strip("|").split("|")]
        placement = cells[1] if len(cells) > 1 else ""
        if placement in {"lead", "brief"}:
            count += 1
    return count


def density_class(source_count: int) -> str:
    return archive_audit.density_class(source_count)


def classifications(
    density: str,
    source_count: int,
    hooks: int,
    opcs: int,
    stories: int,
    ratio: float,
) -> list[str]:
    return archive_audit.density_labels(density, source_count, hooks, opcs, stories, ratio)


def validation_counts(run_date: str, daily_root: Path = DAILY_ROOT) -> tuple[int, int]:
    run_dir = daily_root / run_date
    required = ("sources.md", "synthesis.md", "forecast.md", "judgment.md", "daily-brief.md")
    if not all((run_dir / name).exists() for name in required):
        return (0, 0)
    result = validate_daily_run.validate_run(run_date, "issue" if (run_dir / "issue.md").exists() else "synthesis")
    return (len(result["failures"]), len(result["warnings"]))


def analyze_range(
    dates: list[str],
    manifest_path: Path = MANIFEST_PATH,
    daily_root: Path = DAILY_ROOT,
) -> list[DensityRow]:
    counts = load_manifest_counts(manifest_path)
    rows: list[DensityRow] = []
    for run_date in dates:
        source_count = counts.get(run_date, 0)
        texts = read_daily_text(run_date, daily_root)
        combined = "\n".join(texts.values())
        hooks = hook_ids(combined)
        same_day_hooks = sum(1 for hook in hooks if hook_date(hook) == run_date)
        carried_hooks = len(hooks) - same_day_hooks
        opcs = set(OPC_RE.findall(combined))
        stories = selected_issue_stories(texts.get("synthesis.md", ""))
        load = len(hooks) + len(opcs) + stories
        ratio = round(load / source_count, 2) if source_count else 0.0
        density = density_class(source_count)
        failures, warnings = validation_counts(run_date, daily_root)
        present = [name for name in REQUIRED_DAILY_FILES if name in texts]
        rows.append(
            DensityRow(
                date=run_date,
                manifest_sources=source_count,
                density_class=density,
                daily_stack_files=",".join(present) or "none",
                validation_failures=failures,
                validation_warnings=warnings,
                forecast_hooks=len(hooks),
                same_day_hooks=same_day_hooks,
                carried_hooks=carried_hooks,
                opc_claims=len(opcs),
                issue_stories=stories,
                narrative_load_ratio=ratio,
                classifications=classifications(density, source_count, len(hooks), len(opcs), stories, ratio),
                title=title_from_brief(texts.get("daily-brief.md", "")),
                crisis_object=crisis_from_synthesis(texts.get("synthesis.md", "")),
                issue_exists="issue.md" in texts,
            )
        )
    return rows


def summary(rows: list[DensityRow]) -> dict[str, Any]:
    source_counts = [row.manifest_sources for row in rows]
    total = sum(source_counts)
    return {
        "days": len(rows),
        "total_sources": total,
        "mean_sources": round(total / len(rows), 2) if rows else 0.0,
        "low_density_days": [row.date for row in rows if row.density_class == "thin" and row.manifest_sources > 0],
        "high_density_days": [row.date for row in rows if row.density_class == "dense"],
        "zero_source_days": [row.date for row in rows if row.manifest_sources == 0],
        "verification_priority_days": [
            row.date for row in rows if "verification-priority" in row.classifications
        ],
    }


def render_markdown(rows: list[DensityRow]) -> str:
    stats = summary(rows)
    lines = [
        "# Archive Density Dashboard",
        "",
        f"Range: `{rows[0].date}` through `{rows[-1].date}`" if rows else "Range: none",
        "",
        "## Summary",
        "",
        f"- Days: `{stats['days']}`",
        f"- Total manifest sources: `{stats['total_sources']}`",
        f"- Mean sources per day: `{stats['mean_sources']}`",
        f"- High-density days: `{', '.join(stats['high_density_days']) or 'none'}`",
        f"- Low-density manifest-backed days: `{', '.join(stats['low_density_days']) or 'none'}`",
        f"- Verification-priority days: `{', '.join(stats['verification_priority_days']) or 'none'}`",
        "",
        "## Daily Metrics",
        "",
        "| Date | Sources | Density | Hooks | Same-day | Carried | OPCs | Stories | Load ratio | Validation | Labels | Title |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        validation = f"{row.validation_failures}/{row.validation_warnings}"
        labels = ", ".join(row.classifications) or "none"
        title = row.title.replace("|", "\\|")
        lines.append(
            f"| `{row.date}` | {row.manifest_sources} | `{row.density_class}` | {row.forecast_hooks} | "
            f"{row.same_day_hooks} | {row.carried_hooks} | {row.opc_claims} | {row.issue_stories} | "
            f"{row.narrative_load_ratio:.2f} | `{validation}` | `{labels}` | {title} |"
        )
    lines += [
        "",
        "## Boundary",
        "",
        "Source density is a triage signal, not a truth signal. It can prioritize repair, synthesis review, forecast discipline, and verification work, but it does not promote archive assertions into facts.",
        "",
    ]
    return "\n".join(lines)


def render_terminal(rows: list[DensityRow]) -> str:
    stats = summary(rows)
    lines = [
        f"days={stats['days']} total_sources={stats['total_sources']} mean_sources={stats['mean_sources']}",
        f"high_density={','.join(stats['high_density_days']) or 'none'}",
        f"low_density={','.join(stats['low_density_days']) or 'none'}",
        "date sources density hooks opcs stories load_ratio labels title",
    ]
    for row in rows:
        labels = ",".join(row.classifications) or "none"
        lines.append(
            f"{row.date} {row.manifest_sources} {row.density_class} {row.forecast_hooks} "
            f"{row.opc_claims} {row.issue_stories} {row.narrative_load_ratio:.2f} {labels} {row.title}"
        )
    return "\n".join(lines)


def write_csv(rows: list[DensityRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()) if rows else [field.name for field in DensityRow.__dataclass_fields__.values()])
        writer.writeheader()
        for row in rows:
            data = asdict(row)
            data["classifications"] = ";".join(row.classifications)
            writer.writerow(data)


def write_json(rows: list[DensityRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"summary": summary(rows), "rows": [asdict(row) for row in rows]}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")


def main() -> None:
    print(
        "DEPRECATED: use tools/run.ps1 archive-audit; archive-density remains a density-only compatibility route.",
        file=sys.stderr,
    )
    args = parse_args()
    dates = iter_dates(args.month, args.start_date, args.end_date)
    rows = analyze_range(dates)
    if args.markdown:
        path = Path(args.markdown)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_markdown(rows), encoding="utf-8", newline="\n")
    if args.csv_path:
        write_csv(rows, Path(args.csv_path))
    if args.json_path:
        write_json(rows, Path(args.json_path))
    if not args.markdown and not args.csv_path and not args.json_path:
        print(render_terminal(rows))


if __name__ == "__main__":
    main()

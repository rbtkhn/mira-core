from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import voice_indexes
import voice_metadata
import verification
import render_daily_issue as daily_issue


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
MANIFEST_PATH = NG_ROOT.parent / "archive" / "sources" / "geopolitics" / "source-manifest.json"
DAILY_ROOT = NG_ROOT / "work" / "daily"
LEDGER_PATH = NG_ROOT / "work" / "forecasts" / "forecast-ledger.md"


HOOK_RE = re.compile(r"`(NG-\d{8}-F\d{2})`")
ARCHIVE_LINK_RE = re.compile(r"\((\.\./\.\./\.\./\.\./archive/sources/geopolitics/sources/[^)]+\.md)\)")
INTAKE_ROW_RE = re.compile(r"\|\s*`(archive/sources/geopolitics/sources/[^`]+\.md)`\s*\|")
STATUS_RE = re.compile(r"Status:\s*`([^`]+)`")
PLACEHOLDER_RE = re.compile(r"awaiting intake", re.IGNORECASE)
DELTA_CONTRACT = "Synthesis contract: `delta-v1`"
DELTA_PLACEHOLDERS = (
    "[prior date, range, dossier, or none for a genuinely new object]",
    "[name the new mechanism, evidence, contradiction, or judgment change; do not restate recurring crisis context]",
    "[daily-packet or archive-only]",
)
JUDGMENT_PLACEHOLDER_RE = re.compile(r"\[.*?\]")
JUDGMENT_REQUIRED_SECTIONS = (
    "## Load-Bearing Judgments",
    "## Confidence Boundary",
    "## Support and Dissent",
    "## Claim and Forecast Dependencies",
    "## Next Observable Signals",
    "## Decision / Public-use Implication",
    "## Decision Compression",
)
JUDGMENT_REF_RE = re.compile(r"`((?:SRC|OPC|CLM|NG|VER)-[A-Z0-9-]+)`")
JUDGMENT_DISPOSITION_RE = re.compile(
    r"Recommended disposition:\s*`?([^`\n]+)`?", re.IGNORECASE
)
JUDGMENT_DISPOSITIONS = {
    "archive-only",
    "synthesis-use",
    "forecast-hook",
    "verification-request",
    "reality-claim-candidate",
    "longitudinal-review",
    "public-use-held",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a Narrative Geopolitics daily run against archive and forecast surfaces."
    )
    parser.add_argument("--date", required=True, help="Run date in YYYY-MM-DD format.")
    parser.add_argument(
        "--stage",
        choices=("intake", "synthesis", "forecast", "issue", "publication"),
        default="intake",
        help=(
            "Validation stage. Intake reports stale coverage without blocking; "
            "synthesis, forecast, and publication treat it as a failure."
        ),
    )
    return parser.parse_args()


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def daily_dir(run_date: str) -> Path:
    return DAILY_ROOT / run_date


def expected_files(run_date: str) -> list[Path]:
    base = daily_dir(run_date)
    return [
        base / "sources.md",
        base / "synthesis.md",
        base / "forecast.md",
        base / "judgment.md",
        base / "daily-brief.md",
    ]


def judgment_failures(run_date: str, rows: list[dict[str, Any]], stage: str) -> list[str]:
    """Validate the accountable handoff without making it a claim authority."""
    path = daily_dir(run_date) / "judgment.md"
    if not rows or not path.exists() or stage == "intake":
        return []
    text = read_text(path)
    if "Status: `template`" in text or JUDGMENT_PLACEHOLDER_RE.search(text):
        return ["judgment.md is still a template or contains unresolved placeholders"]
    failures: list[str] = []
    for section in JUDGMENT_REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"judgment.md missing required section: {section}")
    if not re.search(r"As-of:\s*`\d{4}-\d{2}-\d{2}`", text):
        failures.append("judgment.md requires a bounded As-of date")
    if not re.search(r"Review date:\s*`\d{4}-\d{2}-\d{2}`", text):
        failures.append("judgment.md requires a review date")
    if not re.search(r"Confidence:\s*`(?:low|medium|high)`", text):
        failures.append("judgment.md requires a confidence level")
    if not re.search(r"Strongest counterevidence or dissent:\s*[^`\n]+", text):
        failures.append("judgment.md requires counterevidence or dissent")
    if not re.search(r"-\s+[^\n]+", text.split("## Next Observable Signals", 1)[-1]):
        failures.append("judgment.md requires at least one next observable signal")

    compression = text.split("## Decision Compression", 1)[-1].split("## Later Review Note", 1)[0]
    for label in (
        "What changed:",
        "Reusable mechanism:",
        "Decision implication:",
        "Evidence still missing:",
        "Recommended disposition:",
    ):
        match = re.search(rf"^{re.escape(label)}\s*(.+)$", compression, re.MULTILINE)
        if not match or not match.group(1).strip() or match.group(1).strip().lower() in {"none", "n/a"}:
            failures.append(f"judgment.md Decision Compression requires {label[:-1].lower()}")
    disposition = JUDGMENT_DISPOSITION_RE.search(compression)
    if not disposition:
        failures.append("judgment.md Decision Compression requires a recommended disposition")
    else:
        values = {item.strip().strip("`").lower() for item in disposition.group(1).split(",")}
        invalid = sorted(values - JUDGMENT_DISPOSITIONS)
        if invalid:
            failures.append(f"judgment.md has invalid recommended disposition: {', '.join(invalid)}")
    if re.search(r"(?i)\b(?:is|are|was|were)\s+(?:verified|confirmed|operationally supported)\b|\boperationally_supported\b", compression) and not re.search(r"`(?:OPC|CLM|VER)-[A-Z0-9-]+`", compression):
        failures.append("judgment.md cannot assert verification status without a linked OPC, CLM, or VER record")

    records_root = NG_ROOT / "work" / "reality"
    known_ids = set()
    if records_root.exists():
        for record_path in records_root.rglob("*.json"):
            try:
                record = json.loads(record_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if record.get("id"):
                known_ids.add(str(record["id"]))
    ledger_ids = set(HOOK_RE.findall(read_text(LEDGER_PATH)))
    source_ids = set(re.findall(r"`(SRC-[A-Z0-9-]+)`", read_text(daily_dir(run_date) / "sources.md")))
    verification_ids = {
        path.name for path in (NG_ROOT / "work" / "verification" / "packets").glob("VER-*")
    } if (NG_ROOT / "work" / "verification" / "packets").exists() else set()
    for ref in JUDGMENT_REF_RE.findall(text):
        if ref.startswith("SRC-"):
            if ref not in source_ids:
                failures.append(f"judgment.md reference does not resolve: {ref}")
        elif ref.startswith("VER-"):
            if not any(ref == item or item.startswith(ref + "-") for item in verification_ids):
                failures.append(f"judgment.md reference does not resolve: {ref}")
        elif ref.startswith("NG-"):
            if ref not in known_ids and ref not in ledger_ids:
                failures.append(f"judgment.md reference does not resolve: {ref}")
        elif ref not in known_ids:
            failures.append(f"judgment.md reference does not resolve: {ref}")
    return failures


def manifest_rows_for_date(manifest: dict[str, Any], run_date: str) -> list[dict[str, Any]]:
    rows = [row for row in manifest.get("sources", []) if row.get("date") == run_date]
    rows.sort(key=lambda row: row.get("local_path", ""))
    return rows


def source_paths_exist(rows: list[dict[str, Any]]) -> list[str]:
    missing: list[str] = []
    for row in rows:
        local_path = row.get("local_path", "")
        target = REPO_ROOT / Path(local_path)
        if not target.exists():
            missing.append(local_path)
    return missing


def extract_archive_links(sources_text: str) -> list[str]:
    return ARCHIVE_LINK_RE.findall(sources_text)


def extract_intake_paths(sources_text: str) -> list[str]:
    return INTAKE_ROW_RE.findall(sources_text)


def extract_status(text: str) -> str:
    match = STATUS_RE.search(text)
    return match.group(1) if match else ""


def is_placeholder_day(run_path: Path) -> bool:
    sources_path = run_path / "sources.md"
    if not sources_path.exists():
        return False
    return bool(PLACEHOLDER_RE.search(read_text(sources_path)))


def normalize_daily_archive_link(link: str) -> str:
    return link.removeprefix("../../../")


def manifest_archive_paths(rows: list[dict[str, Any]]) -> set[str]:
    return {row.get("local_path", "").split("narrative-geopolitics/", 1)[-1] for row in rows}


def extract_hook_ids(text: str) -> list[str]:
    seen: list[str] = []
    for hook in HOOK_RE.findall(text):
        if hook not in seen:
            seen.append(hook)
    return seen


def extract_ledger_hook_ids() -> set[str]:
    return set(HOOK_RE.findall(read_text(LEDGER_PATH)))


def coverage_differences(
    rows: list[dict[str, Any]], sources_text: str
) -> tuple[list[str], list[str]]:
    """Return manifest paths missing from, and extra paths present in, Intake Batch."""
    intake_paths = set(extract_intake_paths(sources_text))
    manifest_paths = manifest_archive_paths(rows)
    return sorted(manifest_paths - intake_paths), sorted(intake_paths - manifest_paths)


def anchor_quality_warnings(sources_text: str, landed_count: int) -> list[str]:
    """Advisory checks for variable source-anchor coverage and quote redundancy."""
    warnings: list[str] = []
    source_rows = re.findall(r"\|\s*`(SRC-[A-Z0-9-]+)`\s*\|", sources_text)
    source_ids = set(source_rows)
    quote_rows = re.findall(r"\|\s*`(SRC-[A-Z0-9-]+)`\s*\|\s*[â€œ\"]([^|]+)[â€\"]\s*\|", sources_text)
    quote_ids = {item[0] for item in quote_rows}
    if landed_count and len(source_ids) < landed_count:
        warnings.append(f"source-anchor coverage below minimum: {len(source_ids)} SRC anchors for {landed_count} landed sources")
    if quote_rows and len(quote_ids) < len(source_ids):
        warnings.append(f"load-bearing quote coverage is partial: {len(quote_ids)} of {len(source_ids)} SRC anchors have quotes")
    normalized: dict[str, list[str]] = {}
    for source_id, quote in quote_rows:
        key = re.sub(r"[^a-z0-9]+", " ", quote.lower()).strip()
        if key:
            normalized.setdefault(key, []).append(source_id)
    duplicates = [ids for ids in normalized.values() if len(ids) > 1]
    if duplicates:
        warnings.append("load-bearing quote redundancy detected: " + "; ".join(", ".join(ids) for ids in duplicates))
    anchor_count = len(quote_rows) if quote_rows else len(source_ids)
    if anchor_count >= 40:
        warnings.append(f"anchor count is {anchor_count}: confirm each anchor has a distinct analytic job before treating 40 as justified")
    elif landed_count and anchor_count > 30:
        warnings.append(f"anchor count is {anchor_count}: above the normal 24â€“30 working range; review for redundancy")
    return warnings


def validate_run(run_date: str, stage: str = "intake") -> dict[str, Any]:
    if stage not in {"intake", "synthesis", "forecast", "issue", "publication"}:
        raise ValueError(f"unsupported validation stage: {stage}")

    manifest = load_manifest()
    rows = manifest_rows_for_date(manifest, run_date)
    run_path = daily_dir(run_date)
    placeholder_day = is_placeholder_day(run_path)
    downstream = stage != "intake"

    failures: list[str] = []
    warnings: list[str] = []
    state = "ready" if rows else "awaiting-intake"
    landed_sources = len(rows) - len(source_paths_exist(rows))
    consumed_sources = 0
    routing_complete = sum(
        bool(row.get("host_slug") and row.get("voice_slugs")) for row in rows
    )

    if not run_path.exists():
        failures.append(f"missing daily folder: {run_path.relative_to(REPO_ROOT)}")

    for path in expected_files(run_date):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")

    if not rows and not placeholder_day:
        failures.append(f"no manifest rows for date {run_date}")
    if not rows and placeholder_day:
        warnings.append(f"placeholder day awaiting intake for date {run_date}")

    for local_path in source_paths_exist(rows):
        failures.append(f"missing archive source file: {local_path}")

    if rows and (run_path / "sources.md").exists():
        sources_text = read_text(run_path / "sources.md")
        if downstream:
            warnings.extend(anchor_quality_warnings(sources_text, len(rows)))
        consumed_sources = len(
            manifest_archive_paths(rows) & set(extract_intake_paths(sources_text))
        )
        status = extract_status(sources_text)
        linked_paths = {normalize_daily_archive_link(link) for link in extract_archive_links(sources_text)}

        for rel in sorted(linked_paths):
            if not (REPO_ROOT / "narrative-geopolitics" / Path(rel)).exists():
                warnings.append(f"sources.md links missing archive file: {rel}")

        if status != "pilot":
            missing_intake, extra_intake = coverage_differences(rows, sources_text)
            if placeholder_day or missing_intake or extra_intake:
                state = "stale-after-intake"
            coverage_messages = [
                *(f"intake batch missing manifest day source: {rel}" for rel in missing_intake),
                *(f"intake batch includes source outside manifest day batch: {rel}" for rel in extra_intake),
            ]
            if placeholder_day:
                coverage_messages.insert(
                    0,
                    f"daily run still claims awaiting intake after {len(rows)} manifest rows landed; refresh required",
                )
            if downstream:
                failures.extend(coverage_messages)
            else:
                warnings.extend(coverage_messages)

    if (run_path / "forecast.md").exists():
        forecast_text = read_text(run_path / "forecast.md")
        hook_ids = extract_hook_ids(forecast_text)
        ledger_hook_ids = extract_ledger_hook_ids()
        if not hook_ids and not placeholder_day:
            warnings.append("forecast.md has no hook ids")
        for hook_id in hook_ids:
            if hook_id not in ledger_hook_ids:
                warnings.append(f"forecast hook missing from ledger: {hook_id}")

    if downstream and rows:
        failures.extend(judgment_failures(run_date, rows, stage))
        failures.extend(voice_metadata.metadata_failures(manifest, REPO_ROOT, run_date))
        voice_report = voice_indexes.reconcile(
            manifest,
            run_date=run_date,
            write=False,
            repo_root=REPO_ROOT,
            voices_root=NG_ROOT / "voices",
        )
        failures.extend(voice_report["failures"])

    if downstream and (run_path / "synthesis.md").exists():
        synthesis_text = read_text(run_path / "synthesis.md")
        if DELTA_CONTRACT in synthesis_text:
            for placeholder in DELTA_PLACEHOLDERS:
                if placeholder in synthesis_text:
                    failures.append(
                        "delta-v1 synthesis has incomplete Distinctive Contribution"
                    )
                    break
            archive_only = "Disposition: `archive-only`" in synthesis_text
            if not archive_only:
                primary = synthesis_text.split("## Primary Voices", 1)[-1].split("##", 1)[0]
                voice_rows = [line for line in primary.splitlines() if line.startswith("|") and "---" not in line]
                if len(voice_rows) < 2:
                    failures.append("deepening gate requires at least two source-specific analytical contributions")
                story_desk = synthesis_text.split("## Issue Story Desk", 1)[-1].split("##", 1)[0]
                if not re.search(r"\|\s*`NGI-\d{8}-S\d{2}`\s*\|\s*`lead`\s*\|", story_desk):
                    failures.append("deepening gate requires one valid lead story")
                if re.search(r"\[(?:prior date|name the new|daily-packet|Who can do what|bounded judgment|use `|add the VER|observable signal|internal decision|causal or structural)", synthesis_text):
                    failures.append("deepening gate rejects unresolved synthesis placeholders")
            else:
                if (run_path / "issue.md").exists():
                    warnings.append("archive-only disposition should not generate issue.md")
            forecast_text = read_text(run_path / "forecast.md") if (run_path / "forecast.md").exists() else ""
            forecast_hooks = HOOK_RE.findall(forecast_text)
            if not forecast_hooks and not archive_only and not re.search(
                r"(?i)no new (?:accountable )?forecast hook|no forecast hook is issued", forecast_text
            ):
                failures.append("forecast.md requires an explicit forecast decision")
            for line in forecast_text.splitlines():
                if line.lstrip().startswith("|") and re.search(r"NG-\d{8}-F\d{2}", line):
                    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                    if len(cells) < 3 or not cells[1] or not cells[2]:
                        failures.append("forecast.md contains an incomplete forecast hook row")
                        break
        failures.extend(
            verification.validate_day_claims(
                run_date,
                stage,
                daily_root=DAILY_ROOT,
                packets_root=verification.PACKETS_ROOT,
            )
        )

    archive_only = False
    synthesis_path = run_path / "synthesis.md"
    if synthesis_path.exists():
        archive_only = "Disposition: `archive-only`" in read_text(synthesis_path)
    if not archive_only:
        issue_failures, issue_warnings = daily_issue.validate_issue(
            run_date,
            require=stage == "issue",
            daily_root=DAILY_ROOT,
            ledger_path=LEDGER_PATH,
        )
        failures.extend(f"issue.md: {item}" for item in issue_failures)
        for item in issue_warnings:
            if stage in {"issue", "publication"} and "word count outside 1500-2500" in item:
                failures.append(f"issue.md: {item}; daily-packet requires 1500-2500 editorial words")
            else:
                warnings.append(f"issue.md: {item}")

    return {
        "date": run_date,
        "stage": stage,
        "state": state,
        "manifest_rows": len(rows),
        "landed_sources": landed_sources,
        "consumed_sources": consumed_sources,
        "routing_complete": routing_complete,
        "failures": failures,
        "warnings": warnings,
    }


def main() -> None:
    args = parse_args()
    result = validate_run(args.date, args.stage)

    print(f"date={result['date']}")
    print(f"stage={result['stage']}")
    print(f"state={result['state']}")
    print(f"manifest_rows={result['manifest_rows']}")
    print(f"landed_sources={result['landed_sources']}")
    print(f"consumed_sources={result['consumed_sources']}")
    print(f"routing_complete={result['routing_complete']}")
    print(f"failures={len(result['failures'])}")
    print(f"warnings={len(result['warnings'])}")
    for item in result["failures"]:
        print(f"FAIL {item}")
    for item in result["warnings"]:
        print(f"WARN {item}")

    if result["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

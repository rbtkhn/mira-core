from __future__ import annotations

from repository_paths import resolve_geopolitics_reference
import argparse
import re
import sys
from datetime import date
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import forecast_ledger


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = resolve_geopolitics_reference(REPO_ROOT, 'geopolitics')
DAILY_ROOT = NG_ROOT / "work" / "daily"
LEDGER_PATH = NG_ROOT / "work" / "forecasts" / "forecast-ledger.md"


DATE_RE = re.compile(r"Date:\s*`([^`]+)`")
CRISIS_OBJECT_RE = re.compile(r"## Crisis Object\s+(.+?)(?:\n## |\Z)", re.DOTALL)
TABLE_ROW_RE = re.compile(
    r"^\|\s*`(NG-\d{8}-F\d{2})`\s*\|\s*(.*?)\s*\|\s*`?(low|plausible|likely|high)`?\s*\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$"
)
LEDGER_HOOK_RE = re.compile(r"`(NG-\d{8}-F\d{2})`")




def _path(name: str):
    """Resolve defaults at use time while honoring explicit module overrides."""
    original, factory = _PATH_DEFAULTS[name]
    value = globals()[name]
    return factory() if value == original else value


_PATH_DEFAULTS = {
    'NG_ROOT': (NG_ROOT, lambda: resolve_geopolitics_reference(REPO_ROOT, 'geopolitics')),
    'DAILY_ROOT': (DAILY_ROOT, lambda: _path('NG_ROOT') / 'work' / 'daily'),
    'LEDGER_PATH': (LEDGER_PATH, lambda: _path('NG_ROOT') / 'work' / 'forecasts' / 'forecast-ledger.md'),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync forecast hooks from a daily run into the central forecast ledger."
    )
    parser.add_argument("--date", required=True, help="Run date in YYYY-MM-DD format.")
    parser.add_argument("--crisis-object", default="", help="Crisis-object label to use in new ledger rows.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned ledger additions without writing.")
    parser.add_argument("--retro", action="store_true", help="Register new hooks as excluded retrospective hypotheses.")
    parser.add_argument("--authored-at", default="", help="Authorship bound in YYYY-MM-DD format.")
    parser.add_argument("--timing-provenance", default="", help="Evidence supporting the timing classification.")
    parser.add_argument("--forecast-type", choices=sorted(forecast_ledger.FORECAST_TYPES))
    parser.add_argument("--accountable", choices=("yes", "no"))
    parser.add_argument("--review-note", default="")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_run_date(text: str) -> str:
    match = DATE_RE.search(text)
    if not match:
        raise SystemExit("Could not find run date in forecast.md")
    return match.group(1)


def extract_hook_rows(text: str) -> list[dict[str, str]]:
    hooks: list[dict[str, str]] = []
    for line in text.splitlines():
        match = TABLE_ROW_RE.match(line.strip())
        if not match:
            continue
        hook_id, claim, band, review_date, strengthening, weakening = match.groups()
        hooks.append(
            {
                "hook_id": hook_id,
                "claim": claim,
                "band": band,
                "review_date": review_date,
                "strengthening": strengthening,
                "weakening": weakening,
            }
        )
    return hooks


def existing_hook_ids(text: str) -> set[str]:
    return set(LEDGER_HOOK_RE.findall(text))


def infer_crisis_object(forecast_text: str, fallback: str) -> str:
    if fallback:
        return fallback
    run_date = extract_run_date(forecast_text)
    synthesis_path = _path('DAILY_ROOT') / run_date / "synthesis.md"
    if synthesis_path.exists():
        synthesis_text = read_text(synthesis_path)
        match = CRISIS_OBJECT_RE.search(synthesis_text)
        if match:
            crisis_object = " ".join(match.group(1).strip().splitlines()).strip()
            if crisis_object:
                return crisis_object
    return f"{run_date} daily judgment"


def build_ledger_row(
    run_date: str,
    crisis_object: str,
    hook: dict[str, str],
    status: str = "open",
) -> str:
    source_run = f"[{run_date}](../daily/{run_date}/forecast.md)"
    return (
        f"| `{hook['hook_id']}` | `{run_date}` | {crisis_object} | {hook['claim']} | "
        f"`{hook['band']}` | `{hook['review_date']}` | {source_run} | `{status}` |"
    )


def registration_metadata(args: argparse.Namespace) -> forecast_ledger.RegistrationMetadata:
    if args.retro:
        metadata = forecast_ledger.RegistrationMetadata(
            authorship_bound=args.authored_at or date.today().isoformat(),
            timing_provenance=args.timing_provenance or "runtime_date",
            forecast_type="retrospective_hypothesis",
            resolution_status="excluded_retrospective",
            accountable=False,
            review_note=args.review_note or "Retrospective run; retained as a historical review hook, not an accountable forecast.",
        )
    else:
        missing = [
            flag
            for flag, value in (
                ("--authored-at", args.authored_at),
                ("--timing-provenance", args.timing_provenance),
                ("--forecast-type", args.forecast_type),
                ("--accountable", args.accountable),
                ("--review-note", args.review_note),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                "new live forecast hooks require explicit registration metadata: "
                + ", ".join(missing)
            )
        forecast_type = str(args.forecast_type)
        status = {
            "retrospective_hypothesis": "excluded_retrospective",
            "unscorable": "excluded_unscorable",
        }.get(forecast_type, "open")
        metadata = forecast_ledger.RegistrationMetadata(
            authorship_bound=args.authored_at,
            timing_provenance=args.timing_provenance,
            forecast_type=forecast_type,
            resolution_status=status,
            accountable=args.accountable == "yes",
            review_note=args.review_note,
        )
    failures = forecast_ledger.validate_registration(metadata)
    if failures:
        raise ValueError("; ".join(failures))
    return metadata


def insert_rows(
    ledger_text: str, rows: list[str], triage_rows: list[str] | None = None
) -> str:
    return forecast_ledger.insert_rows(ledger_text, rows, triage_rows or [])


def main() -> None:
    args = parse_args()
    forecast_path = _path('DAILY_ROOT') / args.date / "forecast.md"
    if not forecast_path.exists():
        raise SystemExit(f"Missing forecast file: {forecast_path.relative_to(REPO_ROOT)}")

    forecast_text = read_text(forecast_path)
    run_date = extract_run_date(forecast_text)
    hooks = extract_hook_rows(forecast_text)
    if not hooks:
        raise SystemExit("No hook rows found in forecast.md")

    ledger_text = read_text(_path('LEDGER_PATH'))
    existing = existing_hook_ids(ledger_text)
    crisis_object = infer_crisis_object(forecast_text, args.crisis_object)

    new_hooks = [hook for hook in hooks if hook["hook_id"] not in existing]
    metadata = registration_metadata(args) if new_hooks else None
    new_rows = [
        build_ledger_row(run_date, crisis_object, hook, metadata.resolution_status)
        for hook in new_hooks
    ]
    new_triage_rows = [
        forecast_ledger.render_triage_row(hook["hook_id"], metadata)
        for hook in new_hooks
    ]

    print(f"date={run_date}")
    print(f"hooks={len(hooks)}")
    print(f"new_rows={len(new_rows)}")
    for row in new_rows:
        print(row)
    for row in new_triage_rows:
        print(row)

    if args.dry_run or not new_rows:
        return

    updated = insert_rows(ledger_text, new_rows, new_triage_rows)
    _path('LEDGER_PATH').write_text(updated, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from forecast_ledger import (
    FORECAST_TYPES,
    RESOLUTION_STATUSES,
    VERIFICATION_RE,
    VERIFICATION_REQUIRED_STATUSES,
    ForecastEntry,
    ForecastTriage,
    RegistrationMetadata,
    due_failures,
    parse_entries,
    parse_triage,
    render_triage_row,
    structural_failures,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "narrative-geopolitics" / "work" / "forecasts" / "forecast-ledger.md"

def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate forecast-ledger triage metadata.")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("validate", "plan"),
        default="validate",
        help="validate the ledger or print a read-only review plan",
    )
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Review cutoff in YYYY-MM-DD format.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(arguments)


def validate_triage(
    entries: list[ForecastEntry], triage_rows: list[ForecastTriage], as_of: str
) -> list[str]:
    return [
        *structural_failures(entries, triage_rows),
        *due_failures(entries, triage_rows, as_of),
    ]


def accountable_open_hook_ids(text: str, as_of: str | None = None) -> set[str]:
    entries = {entry.hook_id: entry for entry in parse_entries(text)}
    result: set[str] = set()
    for row in parse_triage(text):
        entry = entries.get(row.hook_id)
        if not entry or not row.accountable or row.resolution_status != "open":
            continue
        if as_of is None or entry.review_date <= as_of:
            result.add(row.hook_id)
    return result


def missing_triage_actions(
    entries: list[ForecastEntry], triage_rows: list[ForecastTriage]
) -> list[dict[str, object]]:
    triage_ids = {row.hook_id for row in triage_rows}
    actions: list[dict[str, object]] = []
    for entry in entries:
        if entry.hook_id in triage_ids:
            continue
        metadata = RegistrationMetadata(
            authorship_bound=entry.run_date,
            timing_provenance="ledger_entry_run_date; human review required",
            forecast_type="ex_ante",
            resolution_status=entry.status,
            accountable=True,
            review_note="Suggested by read-only triage planner; verify authorship, timing, and accountability before editing.",
        )
        actions.append(
            {
                "hook_id": entry.hook_id,
                "review_date": entry.review_date,
                "action": "add_triage_row_after_human_review",
                "suggested_row": render_triage_row(entry.hook_id, metadata),
                "authority_effect": "none",
            }
        )
    return actions


def overdue_review_actions(
    entries: list[ForecastEntry], triage_rows: list[ForecastTriage], as_of: str
) -> list[dict[str, object]]:
    entries_by_id = {entry.hook_id: entry for entry in entries}
    actions: list[dict[str, object]] = []
    for row in triage_rows:
        entry = entries_by_id.get(row.hook_id)
        if (
            not entry
            or not row.accountable
            or row.resolution_status != "open"
            or entry.review_date > as_of
        ):
            continue
        actions.append(
            {
                "hook_id": row.hook_id,
                "review_date": entry.review_date,
                "action": "review_accountable_forecast",
                "allowed_dispositions": [
                    "hit",
                    "miss",
                    "mixed",
                    "unresolved",
                    "unresolvable_with_authorized_evidence",
                ],
                "requires_verification_packet_for": sorted(VERIFICATION_REQUIRED_STATUSES),
                "authority_effect": "none",
            }
        )
    return sorted(actions, key=lambda item: (str(item["review_date"]), str(item["hook_id"])))


def build_plan(text: str, as_of: str) -> dict[str, object]:
    entries = parse_entries(text)
    triage_rows = parse_triage(text)
    missing = missing_triage_actions(entries, triage_rows)
    overdue = overdue_review_actions(entries, triage_rows, as_of)
    return {
        "schema_version": "1.0",
        "mode": "forecast-triage-plan",
        "as_of": as_of,
        "entries": len(entries),
        "triage_rows": len(triage_rows),
        "missing_triage_rows": missing,
        "overdue_accountable_forecasts": overdue,
        "summary": {
            "missing_triage_row_count": len(missing),
            "overdue_accountable_forecast_count": len(overdue),
            "action_count": len(missing) + len(overdue),
        },
        "authority_effect": "none",
    }


def emit_plan_text(plan: dict[str, object]) -> None:
    summary = plan["summary"]
    assert isinstance(summary, dict)
    print("forecast_triage_plan=ready")
    print(f"missing_triage_rows={summary['missing_triage_row_count']}")
    print(f"overdue_accountable_forecasts={summary['overdue_accountable_forecast_count']}")
    for item in plan["missing_triage_rows"]:
        assert isinstance(item, dict)
        print(f"missing_triage_row={item['hook_id']}")
        print(f"suggested_row={item['suggested_row']}")
    for item in plan["overdue_accountable_forecasts"]:
        assert isinstance(item, dict)
        print(f"overdue_forecast={item['hook_id']} review_date={item['review_date']}")
    print("authority_effect=none")


def main(arguments: list[str] | None = None) -> None:
    args = parse_args(arguments)
    text = LEDGER_PATH.read_text(encoding="utf-8")
    entries = parse_entries(text)
    triage_rows = parse_triage(text)
    if args.command == "plan":
        plan = build_plan(text, args.as_of)
        if args.json:
            print(json.dumps(plan, indent=2))
        else:
            emit_plan_text(plan)
        return

    failures = validate_triage(entries, triage_rows, args.as_of)
    result = {
        "schema_version": "1.0",
        "mode": "forecast-triage-validate",
        "as_of": args.as_of,
        "entries": len(entries),
        "triage_rows": len(triage_rows),
        "accountable": sum(row.accountable for row in triage_rows),
        "failures": failures,
        "authority_effect": "none",
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"entries={result['entries']}")
        print(f"triage_rows={result['triage_rows']}")
        print(f"accountable={result['accountable']}")
        print(f"failures={len(failures)}")
        for failure in failures:
            print(f"FAIL {failure}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

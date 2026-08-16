from __future__ import annotations

import argparse
from datetime import date, timedelta

import archive_audit
import process_daily_stack as stack
import verification


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open or execute an on-demand Narrative Geopolitics daily run."
    )
    parser.add_argument("--date", help="Run date in YYYY-MM-DD format.")
    parser.add_argument("--month", help="Optional month selector in YYYY-MM format.")
    parser.add_argument("--start-date", help="Optional inclusive start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", help="Optional inclusive end date in YYYY-MM-DD format.")
    parser.add_argument("--choice", choices=("A", "B", "C", "D", "E"))
    parser.add_argument("--execute", action="store_true", help="Run the daily stack for manifest-backed dates.")
    parser.add_argument("--status", default="live-intake-first")
    parser.add_argument("--retro", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--crisis-object", default="")
    parser.add_argument("--skip-ledger-sync", action="store_true")
    parser.add_argument("--forecast-authored-at", default="")
    parser.add_argument("--forecast-timing-provenance", default="")
    parser.add_argument("--forecast-type", choices=("ex_ante", "falsifier", "indicator", "retrospective_hypothesis", "unscorable"))
    parser.add_argument("--forecast-accountable", choices=("yes", "no"))
    parser.add_argument("--forecast-review-note", default="")
    parser.add_argument(
        "--scaffold-empty",
        action="store_true",
        help="Deprecated compatibility flag. Empty dates are reported and skipped.",
    )
    args = parser.parse_args()
    if not args.date and not args.month and not (args.start_date and args.end_date):
        raise SystemExit("Provide --date, --month, or both --start-date and --end-date.")
    return args


def parse_iso_date(value: str) -> date:
    return date.fromisoformat(value)


def iter_dates(args: argparse.Namespace) -> list[str]:
    if args.month:
        start = parse_iso_date(f"{args.month}-01")
        end = (
            date(start.year + 1, 1, 1) - timedelta(days=1)
            if start.month == 12
            else date(start.year, start.month + 1, 1) - timedelta(days=1)
        )
    elif args.start_date and args.end_date:
        start = parse_iso_date(args.start_date)
        end = parse_iso_date(args.end_date)
        if end < start:
            raise SystemExit("--end-date must be on or after --start-date")
    else:
        return [args.date]

    values: list[str] = []
    current = start
    while current <= end:
        values.append(current.isoformat())
        current += timedelta(days=1)
    return values


def stack_args(args: argparse.Namespace, run_date: str) -> argparse.Namespace:
    return argparse.Namespace(
        date=run_date,
        status=args.status,
        retro=args.retro,
        force=args.force,
        dry_run=args.dry_run,
        crisis_object=args.crisis_object,
        skip_ledger_sync=args.skip_ledger_sync,
        forecast_authored_at=args.forecast_authored_at,
        forecast_timing_provenance=args.forecast_timing_provenance,
        forecast_type=args.forecast_type,
        forecast_accountable=args.forecast_accountable,
        forecast_review_note=args.forecast_review_note,
    )


def gather_context(run_date: str) -> dict[str, object]:
    manifest = stack.BOOTSTRAP.load_manifest()
    rows = [row for row in manifest.get("sources", []) if row.get("date") == run_date]
    rows.sort(key=lambda row: row.get("local_path", ""))
    run_dir = stack.BOOTSTRAP.DAILY_ROOT / run_date
    required = ("sources.md", "synthesis.md", "forecast.md", "judgment.md", "daily-brief.md")
    run_exists = bool(rows) and all((run_dir / name).exists() for name in required)
    validation: dict[str, object] = {"failures": [], "warnings": []}
    if run_exists:
        validation = stack.run_validation(run_date)
    audit = archive_audit.build_audit(
        archive_audit.parse_args(["--start-date", run_date, "--end-date", run_date])
    )
    return {
        "rows": rows,
        "run_exists": run_exists,
        "awaiting_intake": not rows,
        "validation": validation,
        "verification": verification.day_payload(run_date),
        "archive_benchmarks": audit["benchmarks"],
        "archive_structural_failures": audit["summary"]["structural_failures"],
    }


def reconcile_voice_routes(run_date: str) -> dict[str, object]:
    return stack.run_voice_reconciliation(run_date)


def recommend_choice(context: dict[str, object]) -> str:
    validation = context["validation"]
    if context["awaiting_intake"] or not context["run_exists"]:
        return "A"
    benchmarks = context.get("archive_benchmarks", {})
    if context.get("archive_structural_failures") or benchmarks.get("repair_candidate_warnings", 0):
        return "B"
    if validation["failures"] or validation["warnings"]:
        return "B"
    verification_state = context["verification"]
    if not verification_state["claims"] or any(
        item["verification"] in {"request", "none"} and item["consequence"] == "high"
        for item in verification_state["claims"]
    ):
        return "C"
    if verification_state["forecast_dependencies"] or any(
        item["packet_state"] in {"assessed", "closed"} for item in verification_state["claims"]
    ):
        return "D"
    return "C"


def print_verification_view(run_date: str, forecast_focus: bool = False) -> None:
    payload = verification.day_payload(run_date)
    print(f"date={run_date}")
    print(f"operational_claims={len(payload['claims'])}")
    for item in payload["claims"]:
        hooks = ",".join(item["forecast_hooks"]) or "none"
        blocks = ",".join(item["blocking_reasons"]) or "none"
        print(f"{item['claim_id']} status={item['status']} consequence={item['consequence']} public={item['public_use']} verification={item['verification']} packet={item['packet_state']} outcome={item['packet_outcome'] or 'none'} hooks={hooks} blocking={blocks}")
        if not forecast_focus and item["verification"] == "request":
            print(f"REQUEST .\\scripts\\python.ps1 scripts\\verification.py new --date {run_date} --slug \"{item['claim']}\"")
    if forecast_focus:
        print(f"forecast_dependencies={len(payload['forecast_dependencies'])}")
        for item in payload["forecast_dependencies"]:
            print(f"{item['hook']} dependency={item['dependency']}")
    for dependency in payload["unknown_dependencies"]:
        print(f"FAIL unknown forecast dependency {dependency}")


def print_menu(run_date: str, context: dict[str, object], choice: str | None) -> None:
    rows = context["rows"]
    validation = context["validation"]
    failures = validation["failures"]
    warnings = validation["warnings"]
    awaiting = context["awaiting_intake"]
    recommended = recommend_choice(context)
    benchmarks = context["archive_benchmarks"]
    density = archive_audit.density_class(benchmarks["source_count"])

    print(f"geo-strategy session: {run_date}")
    print(f"manifest_day_rows={len(rows)}")
    print(f"archive_density={density}")
    print(f"archive_source_count={benchmarks['source_count']}")
    print(f"archive_advisory_labels={','.join(benchmarks['advisory_labels']) or 'none'}")
    print(f"daily_run_exists={'yes' if context['run_exists'] else 'no'}")
    print(f"awaiting_intake={'yes' if awaiting else 'no'}")
    print(f"validation_failures={len(failures)}")
    print(f"validation_warnings={len(warnings)}")
    for item in failures:
        print(f"FAIL {item}")
    for item in warnings:
        print(f"WARN {item}")
    if awaiting:
        print("INFO no manifest rows; this date remains absent until intake or an intentional retrospective run")

    print("\nSession Menu - reply with A-E")
    menu = [
        ("A", "Bootstrap or refresh the manifest-backed day run."),
        ("B", "Reconcile intake coverage and source routing."),
        ("C", "Deepen synthesis around the owning crisis object."),
        ("D", "Sharpen forecast hooks and review logic."),
        ("E", "Execute the full daily stack immediately."),
    ]
    for key, label in menu:
        suffix = " (recommended)" if key == recommended else ""
        print(f"{key}. {label}{suffix}")
    if choice:
        print(f"\nselected={choice}")


def report_skipped(run_date: str, scaffold_empty: bool) -> None:
    print(f"date={run_date}")
    print("manifest_day_rows=0")
    print("daily_run_exists=no")
    print("awaiting_intake=yes")
    if scaffold_empty:
        print("DEPRECATED --scaffold-empty writes nothing; empty dates are on-demand")
    print("SKIP no manifest rows; no daily files written")


def execute_date(run_date: str, args: argparse.Namespace) -> None:
    current = stack_args(args, run_date)
    reconciliation = stack.run_voice_reconciliation(run_date)
    reconciliation_failures = [
        *reconciliation["metadata"]["failures"],
        *reconciliation["indexes"]["failures"],
    ]
    if reconciliation_failures:
        for item in reconciliation_failures:
            print(f"FAIL {item}")
        raise SystemExit(1)
    bootstrap = stack.run_bootstrap(current)
    validation = stack.run_validation(run_date)
    ledger_sync = {"hooks": 0, "new_rows": 0, "rows": []}
    if not args.skip_ledger_sync:
        ledger_sync = stack.run_ledger_sync(current)
        validation = stack.run_validation(run_date)
    issue = stack.run_issue_render(run_date, args.dry_run)
    if issue["action"] == "write":
        validation = stack.run_validation(run_date, "issue")

    print(f"date={run_date}")
    print(f"bootstrap_rows={bootstrap['rows']}")
    for action in bootstrap["actions"]:
        print(action)
    print(f"validation_failures={len(validation['failures'])}")
    print(f"validation_warnings={len(validation['warnings'])}")
    print(f"ledger_hooks={ledger_sync['hooks']}")
    print(f"ledger_new_rows={ledger_sync['new_rows']}")
    print(f"issue_action={issue['action']}")
    print(f"issue_detail={issue['detail']}")
    if validation["failures"]:
        print("status=blocked-needs-deepening")
    elif validation["warnings"]:
        print("status=blocked-needs-deepening")
    elif issue["action"] in {"blocked", "deferred"}:
        print("status=blocked-needs-deepening")
    elif issue["action"] == "archive-only":
        print("status=archive-only")
    elif issue["action"] == "write":
        print("status=issue-complete")
    else:
        print("status=synthesis-complete")
    for item in validation["failures"]:
        print(f"FAIL {item}")
    for item in validation["warnings"]:
        print(f"WARN {item}")
    if validation["failures"] or validation["warnings"]:
        raise SystemExit(1)


def main() -> None:
    args = parse_args()
    dates = iter_dates(args)
    is_batch = len(dates) > 1 or bool(args.month or args.start_date)

    for run_date in dates:
        context = gather_context(run_date)
        if context["awaiting_intake"]:
            if args.execute and not is_batch:
                raise SystemExit(
                    f"Cannot execute full daily stack for {run_date}: no manifest rows found. Land intake first."
                )
            report_skipped(run_date, args.scaffold_empty)
        elif args.choice == "B":
            result = reconcile_voice_routes(run_date)
            failures = [*result["metadata"]["failures"], *result["indexes"]["failures"]]
            print(f"date={run_date}")
            print(f"metadata_changes={len(result['metadata']['changes'])}")
            print(f"changed_voice_shelves={len(result['indexes'].get('changed_shelves', []))}")
            print(f"voice_route_failures={len(failures)}")
            for item in failures:
                print(f"FAIL {item}")
            if failures:
                raise SystemExit(1)
        elif args.choice == "C":
            validation = stack.run_validation(run_date)
            for item in validation["failures"]:
                print(f"FAIL {item}")
            if validation["failures"]:
                raise SystemExit(1)
            print_verification_view(run_date)
        elif args.choice == "D":
            validation = stack.run_validation(run_date, "forecast")
            for item in validation["failures"]:
                print(f"FAIL {item}")
            if validation["failures"]:
                raise SystemExit(1)
            print_verification_view(run_date, forecast_focus=True)
        elif args.execute:
            execute_date(run_date, args)
        else:
            print_menu(run_date, context, args.choice)
        if is_batch:
            print("")


if __name__ == "__main__":
    main()

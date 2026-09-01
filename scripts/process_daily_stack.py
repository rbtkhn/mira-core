from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path
from typing import Any

import voice_indexes
import voice_metadata
import render_daily_issue as ISSUE


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"


def load_module(script_name: str, module_name: str):
    path = SCRIPTS_ROOT / script_name
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {script_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BOOTSTRAP = load_module("bootstrap_daily_run.py", "bootstrap_daily_run")
VALIDATOR = load_module("validate_daily_run.py", "validate_daily_run")
LEDGER_SYNC = load_module("sync_forecast_ledger.py", "sync_forecast_ledger")
DAILY_ROOT = BOOTSTRAP.DAILY_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process the evening Narrative Geopolitics daily synthesis stack for one run date."
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
        help="Mark the day as retrospective when bootstrapping the run folder.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing daily files during bootstrap.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned work without writing files.",
    )
    parser.add_argument(
        "--crisis-object",
        default="",
        help="Crisis-object label to use if forecast hooks need to be added to the ledger.",
    )
    parser.add_argument(
        "--skip-ledger-sync",
        action="store_true",
        help="Skip syncing forecast hooks into the ledger.",
    )
    parser.add_argument("--forecast-authored-at", default="")
    parser.add_argument("--forecast-timing-provenance", default="")
    parser.add_argument("--forecast-type", choices=sorted(LEDGER_SYNC.forecast_ledger.FORECAST_TYPES))
    parser.add_argument("--forecast-accountable", choices=("yes", "no"))
    parser.add_argument("--forecast-review-note", default="")
    return parser.parse_args()


def run_bootstrap(args: argparse.Namespace) -> dict[str, Any]:
    manifest = BOOTSTRAP.load_manifest()
    rows = [row for row in manifest.get("sources", []) if row.get("date") == args.date]
    rows.sort(key=lambda row: row.get("local_path", ""))
    if not rows:
        raise SystemExit(f"No manifest rows found for {args.date}.")

    run_dir = BOOTSTRAP.DAILY_ROOT / args.date
    actions = [
        BOOTSTRAP.write_text(
            run_dir / "sources.md",
            BOOTSTRAP.build_sources_md(args.date, args.status, rows, args.retro),
            args.force,
            args.dry_run,
        )
    ]
    for name in BOOTSTRAP.DAILY_TEMPLATE_FILES:
        actions.append(
            BOOTSTRAP.write_text(
                run_dir / name,
                BOOTSTRAP.build_from_template(name, args.date, args.status),
                args.force,
                args.dry_run,
            )
        )
    return {"rows": len(rows), "actions": actions}


def run_voice_reconciliation(run_date: str) -> dict[str, Any]:
    manifest = voice_metadata.load_manifest()
    metadata = voice_metadata.apply_metadata(manifest, run_date=run_date)
    if metadata["failures"]:
        return {"metadata": metadata, "indexes": {"failures": []}}
    if metadata["changes"]:
        voice_metadata.write_manifest(manifest)
    indexes = voice_indexes.reconcile(manifest, run_date=run_date, write=True)
    return {"metadata": metadata, "indexes": indexes}


def run_validation(run_date: str, stage: str = "synthesis") -> dict[str, Any]:
    return VALIDATOR.validate_run(run_date, stage)


def run_ledger_sync(args: argparse.Namespace) -> dict[str, Any]:
    forecast_path = LEDGER_SYNC.DAILY_ROOT / args.date / "forecast.md"
    if not forecast_path.exists():
        raise SystemExit(f"Missing forecast file: {forecast_path.relative_to(REPO_ROOT)}")

    forecast_text = LEDGER_SYNC.read_text(forecast_path)
    run_date = LEDGER_SYNC.extract_run_date(forecast_text)
    hooks = LEDGER_SYNC.extract_hook_rows(forecast_text)
    if not hooks:
        return {"hooks": 0, "new_rows": 0, "rows": []}

    ledger_text = LEDGER_SYNC.read_text(LEDGER_SYNC.LEDGER_PATH)
    existing = LEDGER_SYNC.existing_hook_ids(ledger_text)
    crisis_object = LEDGER_SYNC.infer_crisis_object(forecast_text, args.crisis_object)

    new_hooks = [hook for hook in hooks if hook["hook_id"] not in existing]
    metadata_args = argparse.Namespace(
        retro=args.retro,
        authored_at=args.forecast_authored_at,
        timing_provenance=args.forecast_timing_provenance,
        forecast_type=args.forecast_type,
        accountable=args.forecast_accountable,
        review_note=args.forecast_review_note,
    )
    metadata = LEDGER_SYNC.registration_metadata(metadata_args) if new_hooks else None
    new_rows = [
        LEDGER_SYNC.build_ledger_row(
            run_date, crisis_object, hook, metadata.resolution_status
        )
        for hook in new_hooks
    ]
    new_triage_rows = [
        LEDGER_SYNC.forecast_ledger.render_triage_row(hook["hook_id"], metadata)
        for hook in new_hooks
    ]

    if not args.dry_run and new_rows:
        updated = LEDGER_SYNC.insert_rows(ledger_text, new_rows, new_triage_rows)
        LEDGER_SYNC.LEDGER_PATH.write_text(updated, encoding="utf-8", newline="\n")

    return {
        "hooks": len(hooks),
        "new_rows": len(new_rows),
        "rows": [*new_rows, *new_triage_rows],
    }


def run_issue_render(run_date: str, dry_run: bool = False) -> dict[str, str]:
    synthesis_path = DAILY_ROOT / run_date / "synthesis.md"
    if synthesis_path.exists() and "Disposition: `archive-only`" in synthesis_path.read_text(encoding="utf-8"):
        return {"action": "archive-only", "detail": "explicit archive-only disposition; issue.md not generated"}
    try:
        model = ISSUE.load_model(run_date)
        failures = ISSUE.model_failures(
            model,
            ISSUE.LEDGER_PATH.read_text(encoding="utf-8"),
        )
        if failures:
            return {"action": "blocked", "detail": "; ".join(failures)}
        issue_path = ISSUE.DAILY_ROOT / run_date / "issue.md"
        rendered = ISSUE.render_model(model)
        prose = re.sub(r"(?m)^\|.*$|`[^`]+`|\[[^\]]+\]\([^)]+\)|<!--.*?-->", " ", rendered)
        word_count = len(re.findall(r"\b[\w'-]+\b", prose))
        if not dry_run:
            strategy_notebook = DAILY_ROOT / run_date / "strategy-notebook.md"
            strategy_valid = (
                strategy_notebook.exists()
                and not VALIDATOR.strategy_notebook_failures(run_date, "issue")
            )
            word_count_failure = VALIDATOR.issue_word_count_failure(
                f"issue.md editorial prose word count outside 1500-2500 target: {word_count}",
                stage="issue",
                consumed_sources=len(model.source_rows),
                strategy_notebook_valid=strategy_valid,
            )
            if word_count_failure:
                return {
                    "action": "blocked",
                    "detail": word_count_failure.removeprefix("issue.md: "),
                }
        if dry_run:
            return {"action": "plan", "detail": str(issue_path.relative_to(REPO_ROOT))}
        issue_path.write_text(rendered, encoding="utf-8", newline="\n")
        return {"action": "write", "detail": str(issue_path.relative_to(REPO_ROOT))}
    except ISSUE.IssueError as exc:
        return {"action": "deferred", "detail": str(exc)}


def blocking_validation_warnings(warnings: list[str]) -> list[str]:
    return [
        warning for warning in warnings
        if "issue.md editorial prose word count outside 1500-2500 target" not in warning
    ]


def main() -> None:
    args = parse_args()

    reconciliation = run_voice_reconciliation(args.date)
    reconciliation_failures = [
        *reconciliation["metadata"]["failures"],
        *reconciliation["indexes"]["failures"],
    ]
    if reconciliation_failures:
        for item in reconciliation_failures:
            print(f"FAIL {item}")
        raise SystemExit(1)

    bootstrap = run_bootstrap(args)
    run_dir = BOOTSTRAP.DAILY_ROOT / args.date
    forecast_exists = (run_dir / "forecast.md").exists()
    can_validate = (not args.dry_run) or run_dir.exists()
    can_sync_ledger = (not args.skip_ledger_sync) and ((not args.dry_run) or forecast_exists)

    validation = {"failures": [], "warnings": [], "manifest_rows": bootstrap["rows"]}
    if can_validate:
        validation = run_validation(args.date, "synthesis")

    ledger_sync = {"hooks": 0, "new_rows": 0, "rows": []}
    if can_sync_ledger:
        ledger_sync = run_ledger_sync(args)
        if can_validate:
            validation = run_validation(args.date, "forecast")

    issue = run_issue_render(args.date, args.dry_run)
    if issue["action"] == "write":
        validation = run_validation(args.date, "issue")

    print(f"date={args.date}")
    print(f"bootstrap_rows={bootstrap['rows']}")
    for action in bootstrap["actions"]:
        print(action)
    if args.dry_run and not forecast_exists:
        print("INFO dry-run on fresh date: validation and ledger sync are deferred until files exist")
    print(f"validation_failures={len(validation['failures'])}")
    print(f"validation_warnings={len(validation['warnings'])}")
    for item in validation["failures"]:
        print(f"FAIL {item}")
    for item in validation["warnings"]:
        print(f"WARN {item}")
    print(f"ledger_hooks={ledger_sync['hooks']}")
    print(f"ledger_new_rows={ledger_sync['new_rows']}")
    print(f"issue_action={issue['action']}")
    print(f"issue_detail={issue['detail']}")
    blocking_warnings = blocking_validation_warnings(validation["warnings"])
    if validation["failures"]:
        print("status=blocked-needs-deepening")
    elif blocking_warnings:
        print("status=blocked-needs-deepening")
    elif issue["action"] in {"blocked", "deferred"}:
        print("status=blocked-needs-deepening")
    elif issue["action"] == "archive-only":
        print("status=archive-only")
    elif issue["action"] == "write":
        print("status=issue-complete")
    else:
        print("status=synthesis-complete")
    for row in ledger_sync["rows"]:
        print(row)

    if validation["failures"] or blocking_warnings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

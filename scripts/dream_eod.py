from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import cadence_ledger
import mira_journal_references


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TIMEZONE = "America/Denver"
DEFAULT_WORKSPACE = "mira-core"
DEFAULT_OPERATOR = "operator"


def run_tool(*arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop(cadence_ledger.DB_ENV, None)
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "run_repo.py"), *arguments],
        cwd=REPO_ROOT, text=True, capture_output=True, check=False, env=environment,
    )


def manifest_rows(run_date: str) -> int:
    result = run_tool("synthesis", "--date", run_date)
    match = re.search(r"^manifest_day_rows=(\d+)$", result.stdout, re.MULTILINE)
    if result.returncode not in {0, 1} or match is None:
        raise cadence_ledger.CadenceLedgerError("Geo-Strategy readiness could not be determined")
    return int(match.group(1))


def geo_certification(run_date: str) -> dict:
    rows = manifest_rows(run_date)
    if rows == 0:
        return {"status": "no_geo_run", "manifest_rows": 0}
    artifact = f"narrative-geopolitics/work/daily/{run_date}/issue.md"
    artifact_path = REPO_ROOT / artifact
    if not artifact_path.is_file():
        raise cadence_ledger.CadenceLedgerError("Geo-Strategy issue artifact is missing")
    validation = run_tool("daily-validate", "--date", run_date, "--stage", "issue")
    state = re.search(r"^state=(\w+)$", validation.stdout, re.MULTILINE)
    failures = re.search(r"^failures=(\d+)$", validation.stdout, re.MULTILINE)
    if validation.returncode or state is None or state.group(1) != "ready" or failures is None or failures.group(1) != "0":
        raise cadence_ledger.CadenceLedgerError("Geo-Strategy issue artifact failed deterministic validation")
    log = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", artifact], cwd=REPO_ROOT,
        text=True, capture_output=True, check=False,
    )
    commit = log.stdout.strip()
    if log.returncode or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise cadence_ledger.CadenceLedgerError("Geo-Strategy issue artifact lacks a commit receipt")
    committed = subprocess.run(
        ["git", "show", f"{commit}:{artifact}"], cwd=REPO_ROOT,
        capture_output=True, check=False,
    )
    if committed.returncode or committed.stdout != artifact_path.read_bytes():
        raise cadence_ledger.CadenceLedgerError("Geo-Strategy issue artifact differs from its commit receipt")
    return {
        "status": "ready", "manifest_rows": rows, "artifact_ref": artifact,
        "digest": hashlib.sha256(artifact_path.read_bytes()).hexdigest(), "commit": commit,
        "validation_stage": "issue", "certification_basis": "committed",
    }


def journal_entry(run_date: str) -> dict | None:
    path = REPO_ROOT / "mira" / "journal-registry.json"
    if not path.is_file():
        return None
    registry = json.loads(path.read_text(encoding="utf-8"))
    return next((row for row in registry.get("entries", []) if row.get("entry_date") == run_date), None)


def journal_bundle(args, run_date: str) -> Path:
    return (args.journal_bundle or Path(r"C:\private\mira-journal-drafts") / run_date).resolve()


def validate_journal_bundle(run_date: str, bundle: Path) -> tuple[dict | None, str | None]:
    result = run_tool(
        "mira-journal", "draft-check", "--date", run_date,
        "--bundle", str(bundle), "--json",
    )
    if result.returncode:
        return None, (result.stderr or result.stdout)[-1200:]
    try:
        validated = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None, "Mira Journal draft-check returned malformed JSON."
    if validated.get("status") != "passed" or validated.get("refresh_required"):
        return None, "Mira Journal bundle is not current and fully validated."
    return validated, None


def journal_certification(bundle: Path, validated: dict) -> dict:
    reference = json.loads((bundle / "technical-reference.json").read_text(encoding="utf-8"))
    return {
        "journal_version_id": validated["version_id"],
        "digest": hashlib.sha256((bundle / "draft.md").read_bytes()).hexdigest(),
        "technical_reference_id": reference["reference_id"],
        "technical_reference_digest": mira_journal_references.reference_digest(reference),
        "validated_at": datetime.now(ZoneInfo("UTC")).isoformat(),
        "validation_status": "passed", "canonicalized": False, "approval_status": "pending",
    }


def append_stage(connection, projection, event_type: str, stage: str, status: str, **values):
    payload = {"stage": stage, "status": status, **values}
    return cadence_ledger.append_daily_close_event(
        connection, projection["run_id"], event_type, payload,
        idempotency_key=f"{projection['run_id']}:{stage}:{event_type}:{status}",
        expected_version=projection["lifecycle_version"],
    )


def check_projection(args, run_date: str) -> dict:
    try:
        geo = geo_certification(run_date)
    except cadence_ledger.CadenceLedgerError as error:
        geo = {"status": "blocked", "reason": str(error)}
    entry = journal_entry(run_date)
    bundle = journal_bundle(args, run_date)
    journal_status = "already_finalized" if entry else "composition_required"
    journal_ready = bool(entry)
    journal_failure = None
    if not entry and (bundle / "draft.md").is_file():
        validated, journal_failure = validate_journal_bundle(run_date, bundle)
        journal_ready = validated is not None
        journal_status = "certification_ready" if journal_ready else "validation_failed"
    dream_ready = bool(args.dream_json or args.no_candidate)
    geo_ready = geo["status"] in {"ready", "no_geo_run"}
    return {
        "status": "ready" if geo_ready and journal_ready and dream_ready else "blocked",
        "mutation": False, "date": run_date,
        "stages": {
            "geo": geo,
            "journal": {"status": journal_status, **({"failure_tail": journal_failure} if journal_failure else {})},
            "dream": {"status": "ready" if dream_ready else "assessment_required"},
        },
        "next_action": None if geo_ready and journal_ready and dream_ready else (
            "Complete the validated journal bundle, then supply --dream-json or --no-candidate and resume."
        ),
    }


def execute(args, run_date: str) -> dict:
    geo = geo_certification(run_date)
    resolution = cadence_ledger.resolve_store(args.db)
    if resolution.path is None:
        raise cadence_ledger.CadenceLedgerError(resolution.reason or "private cadence store unavailable")
    connection = cadence_ledger.connect(resolution.path)
    try:
        if args.resume:
            projection = cadence_ledger.project_daily_close(connection, args.resume)
            if projection["close_date"] != run_date:
                raise cadence_ledger.CadenceLedgerError("resume run date does not match --date")
        else:
            run_id = f"DCR-{run_date.replace('-', '')}-{uuid.uuid4().hex[:12]}"
            projection = cadence_ledger.open_daily_close(
                connection, run_id=run_id, workspace_id=args.workspace_id,
                operator_id=args.operator_id, close_date=run_date, timezone_name=args.timezone,
                idempotency_key=f"daily-close:{args.workspace_id}:{args.operator_id}:{run_date}",
            )
        if projection["state"] == "completed":
            return {"status": "completed", "mutation": False, "run": projection}

        if projection["stages"]["geo"] not in {"completed", "skipped"}:
            if geo["status"] == "no_geo_run":
                projection = append_stage(connection, projection, "stage_skipped", "geo", "no_geo_run",
                                          reason="No manifest-backed sources exist for this date.")
            else:
                projection = append_stage(
                    connection, projection, "stage_completed", "geo", "certified_existing_packet",
                    **{key: value for key, value in geo.items() if key not in {"status", "manifest_rows"}},
                )

        if projection["stages"]["journal"] != "completed":
            entry = journal_entry(run_date)
            if entry:
                current = entry["versions"][-1]
                projection = append_stage(connection, projection, "stage_completed", "journal", "already_finalized",
                                          journal_version_id=current["version_id"], digest=current["content_sha256"])
            else:
                bundle = journal_bundle(args, run_date)
                if not (bundle / "draft.md").is_file():
                    prepared = run_tool("mira-journal", "prepare", "--date", run_date, "--output-root", str(bundle.parent), "--json")
                    return {"status": "blocked", "mutation": True, "run": projection,
                            "next_action": "Compose the bounded journal draft and technical reference in the prepared bundle, then resume.",
                            "journal_prepare": json.loads(prepared.stdout) if prepared.returncode == 0 else {"status": "failed"}}
                validated, failure_tail = validate_journal_bundle(run_date, bundle)
                if validated is None:
                    projection = append_stage(connection, projection, "stage_failed", "journal", "validation_failed",
                                              reason="Private Mira Journal bundle failed certification validation.")
                    return {"status": "blocked", "mutation": True, "run": projection,
                            "next_action": "Repair or refresh the journal bundle and resume this run.",
                            "failure_tail": failure_tail}
                projection = append_stage(
                    connection, projection, "stage_completed", "journal", "certified_private_bundle",
                    **journal_certification(bundle, validated),
                )

        if projection["stages"]["dream"] != "completed":
            if not args.dream_json and not args.no_candidate:
                return {"status": "blocked", "mutation": True, "run": projection,
                        "next_action": "Assess the refreshed full-day census; resume with --dream-json or --no-candidate."}
            if args.dream_json:
                candidate_path = cadence_ledger.require_private_path(args.dream_json, label="Dream candidate")
                episode = json.loads(candidate_path.read_text(encoding="utf-8"))
                expected_scope = {
                    "workspace_id": args.workspace_id, "operator_id": args.operator_id,
                    "dream_date": run_date, "timezone": args.timezone,
                }
                mismatches = [key for key, value in expected_scope.items() if episode.get(key) != value]
                if mismatches:
                    raise cadence_ledger.CadenceLedgerError(
                        "Dream candidate does not match daily-close scope: " + ", ".join(mismatches)
                    )
                dream = cadence_ledger.create_episode(connection, episode, idempotency_key=f"{projection['run_id']}:dream:candidate")
                projection = append_stage(connection, projection, "stage_completed", "dream", "candidate_recorded",
                                          episode_id=dream["episode"]["episode_id"])
            else:
                context = run_tool("mira-journal", "prepare", "--date", run_date, "--check", "--json")
                coverage_digest = hashlib.sha256(context.stdout.encode("utf-8")).hexdigest()
                closeout_id = f"DCO-{run_date.replace('-', '')}-{projection['run_id'][-12:]}"
                cadence_ledger.record_dream_closeout(connection, {
                    "closeout_id": closeout_id, "workspace_id": args.workspace_id,
                    "operator_id": args.operator_id, "dream_date": run_date, "timezone": args.timezone,
                    "coverage_status": args.coverage_status, "reason": args.no_candidate,
                    "session_coverage_digest": coverage_digest,
                }, idempotency_key=f"{projection['run_id']}:dream:closeout")
                projection = append_stage(connection, projection, "stage_completed", "dream", "closeout_recorded",
                                          closeout_id=closeout_id, coverage_status=args.coverage_status)
        projection = cadence_ledger.append_daily_close_event(
            connection, projection["run_id"], "daily_close_completed", {"status": "completed"},
            idempotency_key=f"{projection['run_id']}:completed", expected_version=projection["lifecycle_version"],
        )
        return {"status": "completed", "mutation": True, "run": projection}
    finally:
        connection.close()


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Certify Geo-Strategy and Mira Journal completion, then close Dream in sequence."
    )
    root.add_argument("--date")
    root.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    root.add_argument("--workspace-id", default=DEFAULT_WORKSPACE)
    root.add_argument("--operator-id", default=DEFAULT_OPERATOR)
    root.add_argument("--db", type=Path)
    root.add_argument("--check", action="store_true")
    root.add_argument("--resume")
    root.add_argument("--journal-bundle", type=Path)
    root.add_argument("--dream-json", type=Path)
    root.add_argument("--no-candidate", metavar="REASON")
    root.add_argument("--coverage-status", choices=("complete", "partial"), default="complete")
    root.add_argument("--json", action="store_true")
    return root


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    try:
        timezone = ZoneInfo(args.timezone)
        if args.resume and not args.date:
            resolution = cadence_ledger.resolve_store(args.db, require_exists=True)
            if resolution.path is None:
                raise cadence_ledger.CadenceLedgerError(resolution.reason or "private cadence store unavailable")
            connection = cadence_ledger.connect(resolution.path)
            try:
                run_date = cadence_ledger.project_daily_close(connection, args.resume)["close_date"]
            finally:
                connection.close()
        else:
            run_date = args.date or datetime.now(timezone).date().isoformat()
        datetime.strptime(run_date, "%Y-%m-%d")
        result = check_projection(args, run_date) if args.check else execute(args, run_date)
    except (ValueError, OSError, json.JSONDecodeError, subprocess.SubprocessError, cadence_ledger.CadenceLedgerError) as error:
        print(f"dream error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2) if args.json else f"dream_status={result['status']}\nnext_action={result.get('next_action')}")
    return 0 if result["status"] in {"ready", "completed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

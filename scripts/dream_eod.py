from __future__ import annotations

from repository_paths import resolve_geopolitics_reference
import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import cadence_ledger
import journal_calendar
import cognitive_context
import mira_journal_references
from portable_paths import state_path


REPO_ROOT = Path(__file__).resolve().parent.parent
DAILY_ROOT = resolve_geopolitics_reference(REPO_ROOT, 'geopolitics') / "work" / "daily"
FORECAST_LEDGER = resolve_geopolitics_reference(REPO_ROOT, 'geopolitics') / "work" / "forecasts" / "forecast-ledger.md"
DEFAULT_TIMEZONE = journal_calendar.CURRENT_TIMEZONE
DEFAULT_WORKSPACE = "mira-core"
DEFAULT_OPERATOR = "operator"
SESSION_ID_RE = re.compile(
    r"^MS-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
HOOK_RE = re.compile(r"`(NG-\d{8}-F\d+)`")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GEO_DAILY_FILES = ("sources.md", "synthesis.md", "forecast.md", "judgment.md", "daily-brief.md")
STRATEGY_NOTEBOOK_FILE = "strategy-notebook.md"




def _path(name: str):
    """Resolve defaults at use time while honoring explicit module overrides."""
    original, factory = _PATH_DEFAULTS[name]
    value = globals()[name]
    return factory() if value == original else value


_PATH_DEFAULTS = {
    'DAILY_ROOT': (DAILY_ROOT, lambda: resolve_geopolitics_reference(REPO_ROOT, 'geopolitics') / 'work' / 'daily'),
    'FORECAST_LEDGER': (FORECAST_LEDGER, lambda: resolve_geopolitics_reference(REPO_ROOT, 'geopolitics') / 'work' / 'forecasts' / 'forecast-ledger.md'),
}


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


def geo_artifact_ref(run_date: str) -> str:
    return (geo_daily_path(run_date) / "issue.md").relative_to(REPO_ROOT).as_posix()


def geo_daily_ref(run_date: str) -> str:
    return geo_daily_path(run_date).relative_to(REPO_ROOT).as_posix()


def geo_daily_path(run_date: str) -> Path:
    return resolve_geopolitics_reference(REPO_ROOT, 'geopolitics') / "work" / "daily" / run_date


def geo_daily_files_exist(run_date: str) -> bool:
    run_dir = geo_daily_path(run_date)
    return all((run_dir / name).is_file() for name in GEO_DAILY_FILES)


def geo_daily_digest(run_date: str) -> str:
    digest = hashlib.sha256()
    run_dir = geo_daily_path(run_date)
    for name in GEO_DAILY_FILES:
        path = run_dir / name
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def strategy_notebook_path(run_date: str) -> Path:
    return geo_daily_path(run_date) / STRATEGY_NOTEBOOK_FILE


def strategy_notebook_status(run_date: str, geo: dict | None = None) -> dict:
    entry = cognitive_context.notebook.read_entry(run_date, REPO_ROOT)
    path = REPO_ROOT / entry["path"] if entry else strategy_notebook_path(run_date)
    if entry is None:
        return {
            "status": "unfinished",
            "owner": "tower",
            "path": str(path.relative_to(REPO_ROOT)),
        }
    failures = []
    if geo and geo.get("manifest_rows", 0):
        validation = run_tool("daily-validate", "--date", run_date, "--stage", "synthesis")
        failures = re.findall(r"^- (strategy-notebook\.md .+)$", validation.stdout, re.MULTILINE)
        if failures:
            return {
                "status": "repair_required",
                "path": str(path.relative_to(REPO_ROOT)),
                "failures": failures,
                "authority_effect": "none",
            }
    return {
        "status": "present",
        "path": str(path.relative_to(REPO_ROOT)),
        "digest": entry["content_sha256"],
        "authority_effect": "none",
    }


def geo_commit_receipt(artifact: str, artifact_path: Path) -> dict[str, str]:
    log = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", artifact], cwd=REPO_ROOT,
        text=True, capture_output=True, check=False,
    )
    commit = log.stdout.strip()
    if log.returncode or not re.fullmatch(r"[0-9a-f]{40}", commit):
        return {}
    committed = subprocess.run(
        ["git", "show", f"{commit}:{artifact}"], cwd=REPO_ROOT,
        capture_output=True, check=False,
    )
    if committed.returncode or committed.stdout != artifact_path.read_bytes():
        return {}
    return {"commit": commit, "certification_basis": "committed"}


def geo_validation_status(run_date: str) -> dict:
    validation = run_tool("daily-validate", "--date", run_date, "--stage", "issue")
    state = re.search(r"^state=([A-Za-z0-9_-]+)$", validation.stdout, re.MULTILINE)
    failures = re.search(r"^failures=(\d+)$", validation.stdout, re.MULTILINE)
    failure_count = int(failures.group(1)) if failures else None
    return {
        "returncode": validation.returncode,
        "state": state.group(1) if state else None,
        "failures": failure_count,
        "passed": (
            validation.returncode == 0
            and state is not None
            and state.group(1) == "ready"
            and failure_count == 0
        ),
        "tail": (validation.stderr or validation.stdout)[-1200:],
    }


def provisional_geo_certification(
    run_date: str, rows: int, *, reason: str, tail: str = ""
) -> dict:
    return {
        "status": "provisional",
        "manifest_rows": rows,
        "artifact_ref": geo_daily_ref(run_date),
        "digest": geo_daily_digest(run_date),
        "validation_stage": "issue",
        "validation_state": "deferred",
        "validation_failures": 1,
        "certification_basis": "provisional_packet_with_revision_debt",
        "revision_debt": [
            reason,
            *([tail] if tail else []),
        ],
    }


def geo_certification(run_date: str, *, auto_complete: bool = False) -> dict:
    rows = manifest_rows(run_date)
    if rows == 0:
        return {"status": "no_geo_run", "manifest_rows": 0}
    artifact = geo_artifact_ref(run_date)
    artifact_path = resolve_geopolitics_reference(REPO_ROOT, artifact)
    if not artifact_path.is_file():
        return {"status": "unfinished", "manifest_rows": rows,
                "artifact_ref": artifact, "certification_basis": "tower_work_unfinished",
                "revision_debt": ["Tower owns missing Geo processing; Dream does not compose it."]}
    validation = geo_validation_status(run_date)
    digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    commit = geo_commit_receipt(artifact, artifact_path)
    if validation["passed"]:
        certification_basis = (
            commit.get("certification_basis")
            or "dream_accepted_packet"
        )
        status = "ready"
        revision_debt: list[str] = []
    else:
        certification_basis = "provisional_packet_with_revision_debt"
        status = "provisional"
        revision_debt = [
            "Geo-Strategy issue artifact exists but deterministic validation did not pass; review and revise next day.",
            validation["tail"],
        ]
    return {
        "status": status,
        "manifest_rows": rows,
        "artifact_ref": artifact,
        "digest": digest,
        **commit,
        "validation_stage": "issue",
        "validation_state": validation["state"],
        "validation_failures": validation["failures"],
        "certification_basis": certification_basis,
        **({"revision_debt": revision_debt} if revision_debt else {}),
    }


def substantive_daily_dates(daily_root: Path | None = None) -> list[str]:
    daily_root = _path('DAILY_ROOT') if daily_root is None else daily_root
    if not daily_root.is_dir():
        return []
    dates: list[str] = []
    for path in daily_root.iterdir():
        if path.is_dir() and DATE_RE.fullmatch(path.name) and (path / "issue.md").is_file():
            dates.append(path.name)
    return sorted(dates)


def forecast_ledger_rows(ledger_path: Path | None = None) -> list[dict[str, str]]:
    ledger_path = _path('FORECAST_LEDGER') if ledger_path is None else ledger_path
    if not ledger_path.is_file():
        return []
    rows: list[dict[str, str]] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `NG-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 9:
            continue
        hook = HOOK_RE.search(cells[0])
        if not hook:
            continue
        rows.append({
            "hook_id": hook.group(1),
            "date": cells[1].strip("`"),
            "review_date": cells[6].strip("`"),
            "status": cells[8].strip("`"),
            "raw": line,
        })
    return rows


def due_open_forecast_rows(as_of_date: str, *, ledger_path: Path | None = None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in forecast_ledger_rows(ledger_path):
        review_date = row["review_date"][:10]
        if row["status"] == "open" and DATE_RE.fullmatch(review_date) and review_date <= as_of_date:
            rows.append(row)
    return rows


def classify_forecast_debt(row: dict[str, str], ledger_text: str) -> str:
    hook_id = row["hook_id"]
    related = "\n".join(line for line in ledger_text.splitlines() if hook_id in line)
    if re.search(r"no operational-claim dependency", related, re.I):
        return "posture-review"
    if re.search(r"VER-\d{8}-\d+", related):
        return "verification-required"
    if re.search(r"OPC-\d{8}-\d+|source assertion|operational|contested|verification packet", related, re.I):
        return "verification-required"
    return "posture-review"


def geo_freshness_projection(run_date: str) -> dict:
    later_dates = [date for date in substantive_daily_dates() if date > run_date]
    latest_date = later_dates[-1] if later_dates else run_date
    ledger_text = _path('FORECAST_LEDGER').read_text(encoding="utf-8") if _path('FORECAST_LEDGER').is_file() else ""
    due_rows = due_open_forecast_rows(latest_date)
    classified = {"verification-required": [], "posture-review": []}
    for row in due_rows:
        classified[classify_forecast_debt(row, ledger_text)].append(row["hook_id"])
    verification = classified["verification-required"]
    posture = classified["posture-review"]
    if later_dates:
        status = "needs-refresh"
        next_action = "rerun-owning-bundle"
    elif verification:
        status = "open-but-bracketed"
        next_action = "open-verification-packet"
    elif posture:
        status = "open-but-bracketed"
        next_action = "posture-review"
    else:
        status = "current"
        next_action = "proceed"
    return {
        "geo_prerequisite_status": status,
        "latest_daily_packet": latest_date if (later_dates or (_path('DAILY_ROOT') / run_date / "issue.md").is_file()) else None,
        "later_substantive_packets": later_dates,
        "due_forecast_debt": {
            "verification": len(verification),
            "posture_review": len(posture),
            "not_yet_due": len([row for row in forecast_ledger_rows() if row["status"] == "open" and row["review_date"][:10] > latest_date]),
            "verification_hooks": verification,
            "posture_review_hooks": posture,
        },
        "safe_to_inherit": True,
        "next_action": next_action,
    }


def journal_entry(run_date: str) -> dict | None:
    path = REPO_ROOT / "mira" / "journal-registry.json"
    if not path.is_file():
        return None
    registry = json.loads(path.read_text(encoding="utf-8"))
    return next((row for row in registry.get("entries", []) if row.get("entry_date") == run_date), None)


def journal_bundle(args, run_date: str) -> Path:
    root = state_path("journal/drafts")
    return (args.journal_bundle or root / run_date).resolve()


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


def refresh_guidance(args, run_date: str, bundle: Path, run_id: str | None) -> dict[str, str | None]:
    base = f"tools/run.ps1 mira-journal prepare --date {run_date} --output-root {bundle.parent} --require-journal-reading --require-session-reading --refresh-session-checkpoint --json"
    check = f"tools/run.ps1 mira-journal draft-check --date {run_date} --bundle {bundle} --json"
    resume = (
        f"tools/run.ps1 dream --resume {run_id} --date {run_date} --journal-bundle {bundle}"
        + (f" --db {args.db}" if args.db else "")
        + " --json"
        if run_id else None
    )
    return {"prepare": base, "draft_check": check, "resume": resume}


def journal_certification(bundle: Path, validated: dict) -> dict:
    reference = json.loads((bundle / "technical-reference.json").read_text(encoding="utf-8"))
    return {
        "journal_version_id": validated["version_id"],
        "digest": hashlib.sha256((bundle / "draft.md").read_bytes()).hexdigest(),
        "technical_reference_id": reference["reference_id"],
        "technical_reference_digest": mira_journal_references.reference_digest(reference),
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "validation_status": "passed", "canonicalized": False, "approval_status": "pending",
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json_file(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def git_status_summary() -> dict:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--branch", "--untracked-files=all"],
        cwd=REPO_ROOT, text=True, capture_output=True, check=False,
    )
    if result.returncode:
        return {
            "status": "unavailable",
            "reason": (result.stderr or result.stdout)[-400:],
            "authority_effect": "none",
        }
    lines = [line for line in result.stdout.splitlines() if line]
    branch = lines[0][3:] if lines and lines[0].startswith("## ") else None
    entries = lines[1:] if branch else lines
    groups: dict[str, int] = {}
    for line in entries:
        path = line[3:] if len(line) > 3 else line
        top = path.replace("\\", "/").split("/", 1)[0]
        groups[top] = groups.get(top, 0) + 1
    return {
        "status": "dirty" if entries else "clean",
        "branch": branch,
        "dirty_path_count": len(entries),
        "top_level_groups": dict(sorted(groups.items())),
        "authority_effect": "none",
    }


def roi_synthesis_path(bundle: Path) -> Path:
    return bundle / "roi-synthesis.json"


def roi_source_ref(path: Path, kind: str) -> dict:
    ref: dict[str, str | int | None] = {
        "kind": kind,
        "path": str(path),
        "exists": path.is_file(),
    }
    if path.is_file():
        ref["sha256"] = file_sha256(path)
        ref["bytes"] = path.stat().st_size
    return ref


def roi_letters_obligations(brief: dict) -> list[dict]:
    letters = brief.get("letters_orientation", {})
    if not isinstance(letters, dict):
        return []
    obligations = []
    for row in letters.get("letters", []):
        if not isinstance(row, dict):
            continue
        status = row.get("status") or row.get("delivery_status")
        if status != "draft-not-sent":
            continue
        obligations.append({
            "kind": "mira-letter-draft",
            "path": row.get("path"),
            "modal_status": "prepared-address-not-completed-relation",
            "next_test": "Decide whether this remains inward orientation, needs revision, or requires separately authorized sending.",
            "authority_boundary": (
                "Letter orientation does not authorize sending, publication, external commitments, "
                "or treating contact as completed."
            ),
        })
    return sorted(obligations, key=lambda item: str(item.get("path") or ""))


def roi_stage_payload(projection: dict, stage: str) -> dict:
    for event in reversed(projection.get("events", [])):
        if not isinstance(event, dict):
            continue
        payload = event.get("payload")
        if isinstance(payload, dict) and payload.get("stage") == stage:
            return payload
    return {}


def roi_projection_ref(projection: dict) -> dict:
    event_ids = [
        str(event["event_id"])
        for event in projection.get("events", [])
        if isinstance(event, dict) and event.get("event_id")
    ]
    return {
        "kind": "dream-daily-close-projection",
        "run_id": projection.get("run_id"),
        "lifecycle_version": projection.get("lifecycle_version"),
        "event_ids": event_ids,
        "authority_effect": "none",
    }


def roi_coffee_handles(projection: dict, open_obligations: list[dict]) -> list[dict]:
    handles = []
    for obligation in open_obligations:
        path = obligation.get("path")
        if not path:
            continue
        handles.append({
            "status": "candidate-only",
            "mode": "morning-claim-testing",
            "claim": f"The unsent Mira Letter at {path} remains prepared address, not completed relation.",
            "modal_status": obligation["modal_status"],
            "source_ref": path,
            "next_test": obligation["next_test"],
            "authority_boundary": obligation["authority_boundary"],
        })

    geo = roi_stage_payload(projection, "geo")
    artifact_ref = geo.get("artifact_ref")
    if artifact_ref:
        revision_debt = [
            str(item)
            for item in geo.get("revision_debt", [])
            if isinstance(item, str) and item.strip()
        ]
        handles.append({
            "status": "candidate-only",
            "mode": "morning-claim-testing",
            "claim": (
                f"Dream carried Geo revision debt at {artifact_ref}."
                if revision_debt else
                f"Dream carried the certified Geo packet at {artifact_ref}."
            ),
            "modal_status": "revision-debt" if revision_debt else "certified-evidence",
            "source_ref": artifact_ref,
            "source_digest": geo.get("digest"),
            "certification_basis": geo.get("certification_basis"),
            "revision_debt": revision_debt,
            "next_test": (
                "Check the named artifact and determine whether its recorded revision debt remains current."
                if revision_debt else
                "Check the named artifact and determine whether its certification remains current."
            ),
            "authority_boundary": (
                "This handle supports read-only Coffee orientation only; it does not verify claims, "
                "resolve forecasts, revise the packet, or authorize publication."
            ),
        })
    return handles


def roi_workflow_improvements(projection: dict) -> list[dict]:
    geo = roi_stage_payload(projection, "geo")
    artifact_ref = geo.get("artifact_ref")
    revision_debt = [
        str(item)
        for item in geo.get("revision_debt", [])
        if isinstance(item, str) and item.strip()
    ]
    if not artifact_ref or not revision_debt:
        return []
    return [{
        "status": "candidate-only",
        "opportunity": f"Revisit the recorded Geo revision debt at {artifact_ref}.",
        "source_ref": artifact_ref,
        "source_digest": geo.get("digest"),
        "evidence": revision_debt,
        "likely_roi": "Remove explicitly recorded next-day revision debt without reopening clean Dream stages.",
        "authority_boundary": (
            "This is a workflow-improvement candidate only; revision, verification, and publication "
            "remain separately authorized."
        ),
    }]


def write_roi_synthesis(bundle: Path, run_date: str, projection: dict) -> dict:
    bundle.mkdir(parents=True, exist_ok=True)
    brief_path = bundle / "composition-brief.json"
    brief = read_json_file(brief_path)
    git_summary = git_status_summary()
    open_obligations = roi_letters_obligations(brief)
    candidate_file = bundle / "note-candidates.json"
    candidate_errors = []
    try:
        proposed_notes = cognitive_context.nominations(read_json_file(candidate_file), REPO_ROOT) if candidate_file.is_file() else []
    except (OSError, ValueError, KeyError, TypeError) as error:
        proposed_notes = []
        candidate_errors = [str(error)]
    import tower
    try:
        for contribution in tower.contributions(REPO_ROOT):
            if contribution["date"] == run_date:
                try:
                    proposed_notes.extend(cognitive_context.nominations(contribution["note_proposals"], REPO_ROOT))
                except (OSError, ValueError, KeyError, TypeError) as error:
                    candidate_errors.append(f"{contribution['path']}: {error}")
        proposed_notes = list({row["candidate_id"]: row for row in proposed_notes}.values())
    except (OSError, ValueError) as error:
        candidate_errors.append(str(error))
    for event in projection.get("events", []):
        if event.get("event_type") == "tower_decision" and event["payload"].get("status") == "continue":
            open_obligations.append({"kind": "tower-unfinished", **event["payload"]["tower_pending"]})
    packet = {
        "schema_version": 1,
        "dream_date": run_date,
        "generated_at": projection.get("created_at") or f"{run_date}T00:00:00Z",
        "optimization_target": "workflow-throughput",
        "source_refs": [
            roi_source_ref(brief_path, "mira-journal-composition-brief"),
            roi_source_ref(bundle / "context-pack.json", "mira-journal-context-pack"),
            roi_projection_ref(projection),
        ],
        "sections": {
            # Historical schema key; the current carrier is Work Journal.
            "dev_journal_candidates": [],
            "note_candidates": proposed_notes,
            "coffee_handles": roi_coffee_handles(projection, open_obligations),
            "publication_debt": {
                **git_summary,
                "clean_next_boundary": "Inspect exact changed paths before any separately authorized staging, commit, push, or publication.",
            },
            "workflow_improvements": roi_workflow_improvements(projection),
            "open_obligations": open_obligations,
        },
        "authority_boundary": (
            "ROI synthesis is private Dream orientation for workflow throughput. It is not research evidence, "
            "Journal ancestry, delivery authority, Work Journal admission, Notes admission, Git authority, "
            "publication authority, or permission to contact anyone."
        ),
    }
    if candidate_errors:
        packet["sections"]["open_obligations"].append({"kind": "note-nomination-validation", "status": "deferred", "failures": candidate_errors})
    path = roi_synthesis_path(bundle)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "path": str(path),
        "digest": file_sha256(path),
        "sections": sorted(packet["sections"].keys()),
        "authority_boundary": packet["authority_boundary"],
    }


def finalize_journal_bundle(run_date: str, bundle: Path, run_id: str) -> tuple[dict | None, str | None]:
    command = (
        "mira-journal", "eod-finalize", "--date", run_date,
        "--bundle", str(bundle), "--dream-run-id", run_id,
    )
    checked = run_tool(*command, "--check", "--json")
    if checked.returncode:
        return None, (checked.stderr or checked.stdout)[-1200:]
    finalized = run_tool(*command, "--json")
    if finalized.returncode:
        return None, (finalized.stderr or finalized.stdout)[-1200:]
    try:
        payload = json.loads(finalized.stdout)
    except json.JSONDecodeError:
        return None, "Mira Journal eod-finalize returned malformed JSON."
    if payload.get("status") != "finalized":
        return None, "Mira Journal eod-finalize did not reach finalized state."
    return payload, None


def journal_required_sessions(bundle: Path) -> set[str]:
    brief_path = bundle / "composition-brief.json"
    if not brief_path.is_file():
        return set()
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    return {
        str(row.get("session_id", ""))
        for row in brief.get("daily_session_coverage", {}).get("sessions", [])
        if isinstance(row, dict)
    }


def validate_dream_candidate_sessions(episode: dict, *, required_sessions: set[str]) -> list[str]:
    coverage = episode.get("session_coverage")
    if not isinstance(coverage, list):
        return ["Dream candidate lacks session_coverage"]
    failures: list[str] = []
    seen: set[str] = set()
    for row in coverage:
        if not isinstance(row, dict):
            failures.append("Dream candidate session coverage rows must be objects")
            continue
        session_id = str(row.get("session_id", ""))
        if not SESSION_ID_RE.fullmatch(session_id):
            failures.append(f"Dream candidate has malformed session_id: {session_id}")
            continue
        if session_id in seen:
            failures.append(f"Dream candidate duplicates session_id: {session_id}")
        seen.add(session_id)
    if required_sessions:
        missing = sorted(required_sessions - seen)
        unknown = sorted(seen - required_sessions)
        if missing:
            failures.append("Dream candidate is missing journal session coverage: " + ", ".join(missing))
        if unknown:
            failures.append("Dream candidate references unknown journal sessions: " + ", ".join(unknown))
    return failures


def append_stage(connection, projection, event_type: str, stage: str, status: str, **values):
    payload = {"stage": stage, "status": status, **values}
    return cadence_ledger.append_daily_close_event(
        connection, projection["run_id"], event_type, payload,
        idempotency_key=f"{projection['run_id']}:{stage}:{event_type}:{status}",
        expected_version=projection["lifecycle_version"],
    )


def tower_pending(args, run_date):
    import tower
    return tower.pending(run_date, REPO_ROOT, getattr(args, "tower_state_root", None))



def tower_preflight(connection, projection, args, run_date):
    batch = tower_pending(args, run_date)
    args._tower_pending = batch
    if batch["status"] == "clear":
        return projection, None
    digest = batch["batch_sha256"]
    accepted = any(event["event_type"] == "tower_decision" and
                   event["payload"].get("digest") == digest and
                   event["payload"].get("status") == "continue"
                   for event in projection["events"])
    choice = getattr(args, "tower_choice", None)
    if choice:
        if getattr(args, "tower_batch", None) != digest:
            raise ValueError("Tower pending batch changed; inspect the current batch before choosing")
        projection = cadence_ledger.append_daily_close_event(
            connection, projection["run_id"], "tower_decision",
            {"status": choice, "digest": digest, "tower_pending": batch},
            idempotency_key=f"{projection['run_id']}:tower:{digest}:{choice}",
            expected_version=projection["lifecycle_version"],
        )
        accepted = choice == "continue"
    if accepted:
        return projection, None
    return projection, {"status": "tower_required" if choice == "tower" else "tower_choice_required",
        "mutation": True, "run": projection, "tower_pending": batch,
        "prompt": "Conduct a Tower session for this batch, then return to Dream, or continue Dream with this work unfinished?",
        "next_action": "Use --tower-choice tower|continue --tower-batch " + digest + " and resume this run."}



def prerequisite_projection(args, run_date: str, *, auto_complete_geo: bool = False) -> dict:
    try:
        geo = geo_certification(run_date, auto_complete=auto_complete_geo)
    except cadence_ledger.CadenceLedgerError as error:
        geo = {"status": "blocked", "reason": str(error)}
    if geo["status"] in {"ready", "provisional"}:
        geo["freshness"] = geo_freshness_projection(run_date)
        if geo["freshness"]["geo_prerequisite_status"] != "current":
            geo = {
                **geo,
                "status": "provisional",
                "revision_debt": [
                    *geo.get("revision_debt", []),
                    "Geo-Strategy freshness debt is nonblocking; inherit for closeout and revise next day.",
                ],
            }
    entry = journal_entry(run_date)
    bundle = journal_bundle(args, run_date)
    notebook = strategy_notebook_status(run_date, geo)
    journal_status = "already_finalized" if entry else "preparation_required"
    journal_ready = bool(entry)
    journal_failure = None
    if not entry and (bundle / "draft.md").is_file():
        validated, journal_failure = validate_journal_bundle(run_date, bundle)
        journal_ready = validated is not None
        journal_status = "certification_ready" if journal_ready else "validation_failed"
    geo_ready = geo["status"] in {
        "ready", "provisional", "no_geo_run", "unfinished", "blocked",
    }
    # Strategic gaps stay in their stage; only Tower preflight asks a question.
    incomplete = []
    prompt = None
    return {
        "ready": True,
        "stages": {
            "geo": geo,
            "strategy_notebook": notebook,
            "journal": {"status": journal_status, **({"failure_tail": journal_failure} if journal_failure else {})},
        },
        "incomplete_stages": incomplete,
        "prompt": prompt,
    }


def check_projection(args, run_date: str) -> dict:
    resolution = cadence_ledger.resolve_store(args.db, require_exists=True)
    if resolution.path is not None:
        with sqlite3.connect(resolution.path.as_uri() + "?mode=ro", uri=True) as connection:
            connection.row_factory = sqlite3.Row
            has_runs = connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='daily_close_runs'").fetchone()
            if has_runs:
                row = connection.execute("SELECT run_id FROM daily_close_runs WHERE workspace_id=? AND operator_id=? AND close_date=?",
                                         (args.workspace_id, args.operator_id, run_date)).fetchone()
                if row:
                    projection = cadence_ledger.project_daily_close(connection, row["run_id"])
                    if projection["state"] == "completed":
                        return {"status": "completed", "mutation": False, "run": projection}
    batch = tower_pending(args, run_date)
    if batch["status"] != "clear":
        return {"status": "tower_choice_required", "mutation": False, "date": run_date,
                "tower_pending": batch,
                "prompt": "Conduct Tower first, or continue Dream with this batch unfinished?"}
    prerequisites = prerequisite_projection(args, run_date)
    dream_ready = bool(args.dream_json or args.no_candidate)
    journal_ready = prerequisites["stages"]["journal"]["status"] in {
        "already_finalized", "certification_ready",
    }
    ready = prerequisites["ready"] and journal_ready and dream_ready
    return {
        "status": "ready" if ready else ("paused" if not prerequisites["ready"] else "blocked"),
        "mutation": False, "date": run_date,
        "stages": {
            **prerequisites["stages"],
            "dream": {"status": "ready" if dream_ready else "assessment_required"},
        },
        "incomplete_stages": prerequisites["incomplete_stages"],
        "prompt": prerequisites["prompt"],
        "next_action": None if ready else (
            "Repair the Geo-Strategy infrastructure failure before Dream can complete."
            if not prerequisites["ready"] else
            "Dream consumes existing Tower outputs and composes Mira Journal; strategic work remains with Tower."
            if not journal_ready else "Supply --dream-json or --no-candidate and resume."
        ),
    }


def execute(args, run_date: str) -> dict:
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
            return {"status": "completed", "mutation": False, "run": projection, "tower_pending": next((e["payload"].get("tower_pending", {"status": "not-recorded"}) for e in reversed(projection["events"]) if e["event_type"] == "daily_close_completed"), {"status": "not-recorded"}), "cognitive_disposition": next((event["payload"].get("cognitive_disposition", {"status": "not-recorded"}) for event in reversed(projection["events"]) if event["event_type"] == "daily_close_completed"), {"status": "not-recorded"})}

        projection, tower_gate = tower_preflight(connection, projection, args, run_date)
        if tower_gate:
            return tower_gate
        prerequisites = prerequisite_projection(args, run_date)
        geo = prerequisites["stages"]["geo"]
        if projection["stages"]["geo"] not in {"completed", "skipped"}:
            if geo["status"] in {"no_geo_run", "unfinished", "blocked"}:
                projection = append_stage(connection, projection, "stage_skipped", "geo", geo["status"],
                                          reason="No manifest-backed sources exist for this date.")
            else:
                geo_stage_status = geo.get("certification_basis", "certified_existing_packet")
                projection = append_stage(
                    connection, projection, "stage_completed", "geo", geo_stage_status,
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
                    prepared = run_tool(
                        "mira-journal", "prepare", "--date", run_date,
                        "--output-root", str(bundle.parent), "--require-journal-reading", "--require-session-reading", "--json",
                    )
                    if prepared.returncode:
                        projection = append_stage(
                            connection, projection, "stage_failed", "journal", "preparation_failed",
                            reason="Mira Journal preparation failed.",
                        )
                        return {
                            "status": "blocked", "mutation": True, "run": projection,
                            "next_action": "Repair journal preparation and resume this Dream run.",
                            "failure_tail": (prepared.stderr or prepared.stdout)[-1200:],
                        }
                    roi_synthesis = write_roi_synthesis(bundle, run_date, projection)
                    return {
                        "status": "composition_required", "mutation": True, "run": projection,
                        "journal_bundle": str(bundle),
                        "strategy_notebook": strategy_notebook_status(run_date, geo),
                        "roi_synthesis": roi_synthesis,
                        "next_action": (
                            "Agent-internal handoff, not operator approval: consume existing Tower outputs; read the complete "
                            "journal-reading.json sequentially, oldest first, for inward continuity. "
                            "Run mira-journal reading-complete with its packet digest and composing session; "
                            "bind journal_reading_ack_sha256 in draft.json. Read every session checkpoint "
                            "chunk in ordinal order and acknowledge it with mira-journal session-reading-complete. "
                            "Bind session_checkpoint_sha256 and session_reading_ack_sha256 in draft.json, "
                            "and session_checkpoint_sha256 in technical-reference.json before composing "
                            "draft.md, draft.json, and technical-reference.json under the prepared "
                            "Mira Journal contracts, validate them, then resume Dream."
                            " Consume frozen strategy_context as interpretation, including corrections and gaps. "
                            "Bind context_consumption for strategy and library in draft and technical reference; "
                            "used material needs frozen context digest and grounded prose anchors. "
                            "Inspect existing notes and optionally write up to three candidate-only judgments "
                            "to note-candidates.json; do not create or amend notes. An empty candidate list is valid."
                        ),
                    }
                validated, failure_tail = validate_journal_bundle(run_date, bundle)
                if validated is None:
                    projection = append_stage(connection, projection, "stage_failed", "journal", "validation_failed",
                                              reason="Private Mira Journal bundle failed certification validation.")
                    return {"status": "blocked", "mutation": True, "run": projection,
                            "next_action": "Refresh the journal bundle and resume this run.",
                            "refresh_guidance": refresh_guidance(args, run_date, bundle, projection["run_id"]),
                            "failure_tail": failure_tail}
                try:
                    cognitive_context.refresh_roi(bundle, run_date, REPO_ROOT)
                except (OSError, ValueError, KeyError, TypeError) as error:
                    # Optional orientation cannot turn an otherwise valid close into a stop.
                    print(f"ROI cognitive refresh unavailable: {error}", file=sys.stderr)
                finalized, finalization_failure = finalize_journal_bundle(
                    run_date, bundle, projection["run_id"]
                )
                if finalized is None:
                    projection = append_stage(
                        connection, projection, "stage_failed", "journal", "finalization_failed",
                        reason="Mira Journal EOD finalization failed.",
                    )
                    return {
                        "status": "blocked", "mutation": True, "run": projection,
                        "next_action": "Repair the journal finalization failure and resume this run.",
                        "refresh_guidance": refresh_guidance(
                            args, run_date, bundle, projection["run_id"]
                        ),
                        "failure_tail": finalization_failure,
                    }
                projection = append_stage(
                    connection, projection, "stage_completed", "journal", "finalized",
                    journal_version_id=finalized["version_id"],
                    digest=finalized["content_sha256"],
                    technical_reference_digest=finalized["technical_reference_sha256"],
                    validation_status="passed", canonicalized=True,
                    approval_status=finalized["approval_status"],
                    publication_eligible=False,
                    **(
                        {"roi_synthesis": {
                            "path": str(roi_synthesis_path(bundle)),
                            "digest": file_sha256(roi_synthesis_path(bundle)),
                            "authority_effect": "none",
                        }}
                        if roi_synthesis_path(bundle).is_file() else {}
                    ),
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
                failures = validate_dream_candidate_sessions(
                    episode, required_sessions=journal_required_sessions(journal_bundle(args, run_date))
                )
                if failures:
                    raise cadence_ledger.CadenceLedgerError("; ".join(failures))
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
        cognitive_disposition = cognitive_context.closeout(journal_bundle(args, run_date), run_date, REPO_ROOT)
        if geo.get("status") == "no_geo_run" and cognitive_disposition["notebook"]["status"] == "unavailable":
            cognitive_disposition["notebook"]["status"] = "not-applicable"
        projection = cadence_ledger.append_daily_close_event(
            connection, projection["run_id"], "daily_close_completed", {"status": "completed", "cognitive_disposition": cognitive_disposition, "tower_pending": getattr(args, "_tower_pending", {})},
            idempotency_key=f"{projection['run_id']}:completed", expected_version=projection["lifecycle_version"],
        )
        return {"status": "completed", "mutation": True, "run": projection, "cognitive_disposition": cognitive_disposition, "tower_pending": getattr(args, "_tower_pending", {})}
    finally:
        connection.close()


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Certify Geo-Strategy and Mira Journal completion, then close Dream in sequence."
    )
    root.add_argument("--date")
    root.add_argument("--timezone", help="Defaults to the dated Journal calendar; future dates require its timezone")
    root.add_argument("--workspace-id", default=DEFAULT_WORKSPACE)
    root.add_argument("--operator-id", default=DEFAULT_OPERATOR)
    root.add_argument("--db", type=Path)
    root.add_argument("--tower-choice", choices=("tower", "continue"))
    root.add_argument("--tower-batch", help="Exact reviewed pending batch digest")
    root.add_argument("--tower-state-root", type=Path)
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
            run_date = args.date or journal_calendar.current_date().isoformat()
        calendar_day = datetime.strptime(run_date, "%Y-%m-%d").date()
        expected_zone = journal_calendar.timezone_name(calendar_day)
        if args.timezone and calendar_day >= journal_calendar.TRANSITION_DAY and args.timezone != expected_zone:
            raise ValueError("Dream timezone must match the dated Journal calendar")
        args.timezone = args.timezone or expected_zone
        ZoneInfo(args.timezone)  # Fail explicitly if timezone data is unavailable.
        result = check_projection(args, run_date) if args.check else execute(args, run_date)
    except (ValueError, OSError, json.JSONDecodeError, subprocess.SubprocessError, cadence_ledger.CadenceLedgerError) as error:
        print(f"dream error: {error}", file=sys.stderr)
        return 1
    print(
        json.dumps(result, indent=2)
        if args.json else
        f"dream_status={result['status']}\nprompt={result.get('prompt')}\nnext_action={result.get('next_action')}"
    )
    return 0 if result["status"] in {"ready", "completed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

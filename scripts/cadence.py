from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable


SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import triage_forecast_ledger as forecast_triage
import verification as verification_packets
import reality
from runtime_bootstrap import BootstrapUnavailable, resolve_validation_python


REPO_ROOT = Path(__file__).resolve().parent.parent
HANDOFF_PATH = (
    REPO_ROOT / "narrative-geopolitics" / "work" / "cadence" / "last-dream.json"
)
DAILY_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "daily"
MANIFEST_PATH = REPO_ROOT / "narrative-geopolitics" / "archive" / "source-manifest.json"
ARCHIVE_SOURCES_ROOT = REPO_ROOT / "narrative-geopolitics" / "archive" / "sources"
BOUNDED_AGENCY_CONTRACT = (
    "narrative-geopolitics/method/bounded-agency-contract.md"
)
BEST_INTAKE_AUTHORITY = {
    "may_read": [
        "repository Git state",
        "narrative-geopolitics/archive/source-manifest.json",
        "existing archive sources for duplicate detection",
        "voice and channel records for provisional canonical routing",
        "best-intake method and metadata contracts",
    ],
    "may_write": [
        "narrative-geopolitics/archive/sources/YYYY-MM-DD/source-*.md",
        "narrative-geopolitics/archive/source-manifest.json",
    ],
    "must_not_write_without_explicit_authorization": [
        "narrative-geopolitics/voices/",
        "narrative-geopolitics/channels/",
        "narrative-geopolitics/work/daily/",
        "narrative-geopolitics/work/forecasts/",
        "narrative-geopolitics/work/verification/",
        "narrative-geopolitics/public/",
        "Git index, commits, branches, or remotes",
    ],
}
GEOPOLITICAL_SYNTHESIS_AUTHORITY = {
    "may_read": [
        "repository Git state",
        "narrative-geopolitics/archive/source-manifest.json",
        "manifest-backed archive sources for the selected date",
        "narrative-geopolitics/voices/ and narrative-geopolitics/channels/",
        "existing daily, forecast, and verification state",
        "geopolitical-synthesis method and templates",
    ],
    "may_write": [
        "declared alias-valued person metadata for the selected date",
        "existing narrative-geopolitics/voices/*/source-index.md routes",
        "narrative-geopolitics/work/daily/{date}/sources.md",
        "narrative-geopolitics/work/daily/{date}/synthesis.md",
        "narrative-geopolitics/work/daily/{date}/forecast.md",
        "narrative-geopolitics/work/daily/{date}/judgment.md",
        "narrative-geopolitics/work/daily/{date}/daily-brief.md",
        "new forecast hooks in narrative-geopolitics/work/forecasts/forecast-ledger.md",
    ],
    "must_not_write_without_explicit_authorization": [
        "private intake behavior or new archive source bodies",
        "narrative-geopolitics/channels/",
        "narrative-geopolitics/work/verification/ packets",
        "forecast resolutions or accountability classifications",
        "narrative-geopolitics/public/",
        "external systems or web research",
        "Git index, commits, branches, or remotes",
    ],
}
OPERATIONAL_VERIFICATION_AUTHORITY = {
    "may_read": [
        "repository Git state",
        "narrative-geopolitics/work/verification/source-registry.md",
        "the selected verification packet and its named affected artifacts",
        "the selected packet's named forecast hooks",
        "bounded external evidence for the packet's declared observables",
    ],
    "may_write": [
        "the selected narrative-geopolitics/work/verification/packets/{packet_id}-*/README.md packet",
    ],
    "must_not_write_without_explicit_authorization": [
        "private intake, archive sources, or the source manifest",
        "narrative-geopolitics/voices/ or narrative-geopolitics/channels/",
        "daily synthesis or public products",
        "forecast ledger status, classification, or resolution",
        "other verification packets or the source registry",
        "generalized scraping, feeds, or evidence collection beyond declared observables",
        "Git index, commits, branches, or remotes",
    ],
}
FORECAST_REVIEW_AUTHORITY = {
    "may_read": [
        "repository Git state",
        "the selected forecast entry and accountability-triage row",
        "the selected forecast's source run and declared operational dependencies",
        "completed verification packets cited by the selected review",
    ],
    "may_write": [
        "only the selected {hook_id} resolution status and review note in narrative-geopolitics/work/forecasts/forecast-ledger.md",
    ],
    "must_not_write_without_explicit_authorization": [
        "forecast claim, probability band, review date, authorship bound, timing provenance, or forecast type",
        "other forecast rows or accountability classifications",
        "verification packet outcomes or evidence",
        "private intake, archive, voice, channel, daily synthesis, or public products",
        "external systems or web research",
        "Git index, commits, branches, or remotes",
    ],
}
OUTCOMES = ("improved", "no_change", "regressed", "inconclusive")
NEXT_MODES = {
    "improved": "confirm_then_consolidate",
    "no_change": "retire_or_narrow",
    "regressed": "revert_and_diagnose",
    "inconclusive": "run_discriminating_test",
}


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.rstrip()


def git_head() -> str:
    return run_git("rev-parse", "HEAD")


def git_branch() -> str:
    return run_git("branch", "--show-current") or "detached"


def tracking_state() -> dict:
    try:
        upstream = run_git(
            "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"
        )
        ahead_text, behind_text = run_git(
            "rev-list", "--left-right", "--count", "HEAD...@{upstream}"
        ).split()
        ahead = int(ahead_text)
        behind = int(behind_text)
        return {
            "upstream": upstream,
            "ahead": ahead,
            "behind": behind,
            "synchronized": ahead == 0 and behind == 0,
        }
    except (subprocess.CalledProcessError, ValueError):
        return {
            "upstream": None,
            "ahead": None,
            "behind": None,
            "synchronized": None,
        }


def dirty_paths() -> list[str]:
    paths: list[str] = []
    for line in run_git("status", "--short").splitlines():
        value = line[3:].strip()
        paths.append(value.split(" -> ", 1)[-1])
    return sorted(paths)


def worktree_fingerprint() -> str:
    digest = hashlib.sha256()
    for command in (
        ["git", "status", "--porcelain=v1", "-z"],
        ["git", "diff", "--binary", "--no-ext-diff"],
    ):
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        digest.update(result.stdout)
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    for raw_path in sorted(value for value in untracked.split(b"\0") if value):
        digest.update(raw_path)
        path = REPO_ROOT / raw_path.decode("utf-8", errors="surrogateescape")
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def latest_daily_run() -> str | None:
    if not DAILY_ROOT.exists():
        return None
    dates = sorted(path.name for path in DAILY_ROOT.iterdir() if path.is_dir())
    return dates[-1] if dates else None


def manifest_state(
    manifest_path: Path = MANIFEST_PATH,
    archive_root: Path = ARCHIVE_SOURCES_ROOT,
) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    rows = manifest.get("sources", [])
    dates = sorted({row.get("date") for row in rows if row.get("date")})
    archive_files = sum(1 for path in archive_root.rglob("*.md") if path.is_file())
    header_count = manifest.get("source_count")
    row_count = len(rows)
    return {
        "header_count": header_count,
        "row_count": row_count,
        "archive_file_count": archive_files,
        "parity": header_count == row_count == archive_files,
        "latest_intake_date": dates[-1] if dates else None,
        "recent_intake_dates": dates[-5:],
    }


def synthesis_state(
    run_date: str,
    manifest_path: Path = MANIFEST_PATH,
    daily_root: Path = DAILY_ROOT,
    repo_root: Path = REPO_ROOT,
) -> dict:
    try:
        date.fromisoformat(run_date)
    except ValueError as error:
        raise ValueError(f"invalid synthesis date: {run_date}") from error
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    rows = sorted(
        (row for row in manifest.get("sources", []) if row.get("date") == run_date),
        key=lambda row: row.get("local_path", ""),
    )
    missing_sources = sorted(
        row.get("local_path", "")
        for row in rows
        if not (repo_root / row.get("local_path", "")).is_file()
    )
    run_dir = daily_root / run_date
    required = ("sources.md", "synthesis.md", "forecast.md", "judgment.md", "daily-brief.md")
    files = {name: (run_dir / name).is_file() for name in required}
    present = sum(files.values())
    if present == 0:
        contract_state = "absent"
    elif present == len(required):
        contract_state = "complete"
    else:
        contract_state = "partial"
    return {
        "date": run_date,
        "manifest_day_rows": len(rows),
        "missing_archive_sources": missing_sources,
        "daily_directory_exists": run_dir.is_dir(),
        "daily_files": files,
        "daily_contract_state": contract_state,
    }


def validate_synthesis_date(run_date: str) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate_daily_run.py",
            "--date",
            run_date,
            "--stage",
            "synthesis",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    lines = (result.stdout + result.stderr).splitlines()
    return {
        "passed": result.returncode == 0,
        "returncode": result.returncode,
        "failures": [line.removeprefix("FAIL ") for line in lines if line.startswith("FAIL ")],
        "warnings": [line.removeprefix("WARN ") for line in lines if line.startswith("WARN ")],
    }


def scoped_synthesis_authority(run_date: str) -> dict:
    return {
        key: [value.format(date=run_date) for value in values]
        for key, values in GEOPOLITICAL_SYNTHESIS_AUTHORITY.items()
    }


def verification_state(packet_id: str) -> dict:
    path = verification_packets.find_packet(packet_id)
    if path is None:
        records = reality.load_records()
        investigation = records.get(packet_id)
        if investigation and investigation.get("kind") == "investigation":
            observables = [
                records[item].get("question", item)
                for item in investigation.get("observable_ids", [])
                if item in records
            ]
            evidence_ids = {
                item.get("from_id")
                for item in records.values()
                if item.get("kind") == "relation"
                and item.get("to_id") in investigation.get("claim_ids", [])
                and records.get(item.get("from_id"), {}).get("kind") == "evidence"
            }
            return {
                "packet_id": packet_id,
                "exists": True,
                "path": reality.record_path("investigation", packet_id).relative_to(REPO_ROOT).as_posix(),
                "status": investigation.get("status"),
                "assessment_outcome": None,
                "observables": observables,
                "evidence_records": len(evidence_ids),
                "evidence_chains": len({records[item].get("originating_chain") for item in evidence_ids}),
                "affected_forecast_hooks": investigation.get("affected_forecast_hooks", []),
                "validation_failures": reality.validate_record(investigation, records),
                "registry_failures": verification_packets.validate_registry(),
                "lattice": True,
            }
        return {
            "packet_id": packet_id,
            "exists": False,
            "path": None,
            "status": None,
            "assessment_outcome": None,
            "observables": [],
            "evidence_records": 0,
            "evidence_chains": 0,
            "affected_forecast_hooks": [],
            "validation_failures": [f"packet not found or ambiguous: {packet_id}"],
            "registry_failures": verification_packets.validate_registry(),
            "lattice": False,
        }
    packet = verification_packets.parse_packet(path)
    return {
        "packet_id": packet.packet_id,
        "exists": True,
        "path": path.relative_to(REPO_ROOT).as_posix(),
        "status": packet.fields.get("status"),
        "assessment_outcome": packet.fields.get("assessment_outcome"),
        "observables": packet.observables,
        "evidence_records": len(packet.evidence),
        "evidence_chains": len({item["chain"] for item in packet.evidence}),
        "affected_forecast_hooks": sorted(
            verification_packets.HOOK_RE.findall(
                packet.fields.get("affected_forecast_hooks", "")
            )
        ),
        "validation_failures": verification_packets.validate_packet(packet),
        "registry_failures": verification_packets.validate_registry(),
        "lattice": bool(reality.load_records().get(packet.packet_id)),
    }


def scoped_verification_authority(packet_id: str, *, lattice: bool = False) -> dict:
    authority = {
        key: [value.format(packet_id=packet_id) for value in values]
        for key, values in OPERATIONAL_VERIFICATION_AUTHORITY.items()
    }
    if lattice:
        authority["may_write"] = [
            f"narrative-geopolitics/work/reality/investigations/{packet_id}.json",
            "new named observable, evidence, relation, assessment, and transition records under narrative-geopolitics/work/reality/",
        ]
        authority["must_not_write_without_explicit_authorization"].append(
            "unrelated reality-lattice records or signed assessment history"
        )
    return authority


def forecast_review_state(
    hook_id: str,
    as_of: str,
    ledger_path: Path = forecast_triage.LEDGER_PATH,
) -> dict:
    try:
        date.fromisoformat(as_of)
    except ValueError as error:
        raise ValueError(f"invalid forecast review date: {as_of}") from error
    text = ledger_path.read_text(encoding="utf-8")
    entries = [item for item in forecast_triage.parse_entries(text) if item.hook_id == hook_id]
    triage_rows = [item for item in forecast_triage.parse_triage(text) if item.hook_id == hook_id]
    packet_ids = set(
        forecast_triage.VERIFICATION_RE.findall(
            " ".join(item.review_note for item in triage_rows)
        )
    )
    for path in verification_packets.packet_paths():
        packet = verification_packets.parse_packet(path)
        if hook_id in verification_packets.HOOK_RE.findall(
            packet.fields.get("affected_forecast_hooks", "")
        ):
            packet_ids.add(packet.packet_id)
    packets = []
    for packet_id in sorted(packet_ids):
        packet = verification_state(packet_id)
        packets.append(
            {
                "packet_id": packet_id,
                "exists": packet["exists"],
                "status": packet["status"],
                "assessment_outcome": packet["assessment_outcome"],
                "validation_failures": packet["validation_failures"],
            }
        )
    entry = entries[0] if len(entries) == 1 else None
    triage = triage_rows[0] if len(triage_rows) == 1 else None
    lattice = reality.claim_state(hook_id)
    return {
        "hook_id": hook_id,
        "as_of": as_of,
        "entry_count": len(entries),
        "triage_count": len(triage_rows),
        "run_date": entry.run_date if entry else None,
        "review_date": entry.review_date if entry else None,
        "due": bool(entry and entry.review_date <= as_of),
        "entry_status": entry.status if entry else None,
        "forecast_type": triage.forecast_type if triage else None,
        "resolution_status": triage.resolution_status if triage else None,
        "accountable": triage.accountable if triage else None,
        "review_note": triage.review_note if triage else None,
        "verification_packets": packets,
        "lattice": lattice,
    }


def scoped_forecast_authority(hook_id: str) -> dict:
    return {
        key: [value.format(hook_id=hook_id) for value in values]
        for key, values in FORECAST_REVIEW_AUTHORITY.items()
    }


def startup_state(
    mode: str,
    run_date: str | None = None,
    packet_id: str | None = None,
    hook_id: str | None = None,
    as_of: str | None = None,
) -> dict:
    if mode not in {
        "best-intake",
        "geopolitical-synthesis",
        "operational-verification",
        "forecast-review",
    }:
        raise ValueError(f"unsupported startup mode: {mode}")
    if mode == "geopolitical-synthesis" and not run_date:
        raise ValueError("geopolitical-synthesis startup requires --date")
    if mode == "operational-verification" and not packet_id:
        raise ValueError("operational-verification startup requires --packet")
    if mode == "forecast-review" and not hook_id:
        raise ValueError("forecast-review startup requires --hook")
    dirty = dirty_paths()
    manifest = manifest_state()
    handoff = coffee_state()
    blockers: list[str] = []
    warnings: list[str] = []
    if not manifest["parity"]:
        blockers.append("archive_manifest_parity_failed")
    if dirty:
        warnings.append("preserve_existing_dirty_paths")
    if handoff["handoff_status"] != "current":
        warnings.append(f"cadence_handoff_{handoff['handoff_status']}")
    phase: dict | None = None
    phase_validation: dict | None = None
    authority = BEST_INTAKE_AUTHORITY
    next_action = "wait_for_operator_source"
    if mode == "geopolitical-synthesis":
        assert run_date is not None
        phase = synthesis_state(run_date)
        authority = scoped_synthesis_authority(run_date)
        if phase["manifest_day_rows"] == 0:
            blockers.append("no_manifest_rows_for_selected_date")
        if phase["missing_archive_sources"]:
            blockers.append("selected_date_archive_sources_missing")
        contract_state = phase["daily_contract_state"]
        if contract_state == "absent":
            warnings.append("daily_contract_absent")
            next_action = "open_guided_synthesis_choice_A"
        elif contract_state == "partial":
            warnings.append("daily_contract_partial")
            next_action = "open_guided_synthesis_choice_A"
        else:
            phase_validation = validate_synthesis_date(run_date)
            if phase_validation["failures"]:
                warnings.append("synthesis_validation_requires_reconciliation")
                next_action = "open_guided_synthesis_choice_B"
            elif phase_validation["warnings"]:
                warnings.append("synthesis_validation_has_warnings")
                next_action = "open_guided_synthesis_choice_B"
            else:
                next_action = "open_guided_synthesis_choice_C"
    elif mode == "operational-verification":
        assert packet_id is not None
        phase = verification_state(packet_id)
        authority = scoped_verification_authority(packet_id, lattice=phase.get("lattice", False))
        if not phase["exists"]:
            blockers.append("verification_packet_missing_or_ambiguous")
        if phase["registry_failures"]:
            blockers.append("verification_source_registry_invalid")
        status = phase["status"]
        if phase["exists"] and status not in verification_packets.WORKFLOW_STATES:
            blockers.append("verification_packet_state_invalid")
        if status in {"assessed", "closed"} and phase["validation_failures"]:
            blockers.append("assessed_verification_packet_invalid")
        elif phase["exists"] and phase["validation_failures"]:
            warnings.append("verification_packet_not_assessment_ready")
        if status == "requested":
            next_action = (
                "define_required_observables"
                if any("[Observable" in item for item in phase["observables"])
                else "begin_bounded_research"
            )
        elif status == "researching":
            next_action = "continue_bounded_research"
        elif status == "assessed":
            next_action = "review_assessment_downstream_effects"
        elif status == "closed":
            next_action = "verification_phase_complete"
    elif mode == "forecast-review":
        assert hook_id is not None
        review_as_of = as_of or date.today().isoformat()
        phase = forecast_review_state(hook_id, review_as_of)
        authority = scoped_forecast_authority(hook_id)
        if phase["entry_count"] != 1:
            blockers.append("forecast_entry_missing_or_duplicated")
        if phase["triage_count"] != 1:
            blockers.append("forecast_triage_missing_or_duplicated")
        if phase["triage_count"] == 1 and phase["forecast_type"] not in forecast_triage.FORECAST_TYPES:
            blockers.append("forecast_type_invalid")
        if phase["triage_count"] == 1 and phase["resolution_status"] not in forecast_triage.RESOLUTION_STATUSES:
            blockers.append("forecast_resolution_status_invalid")
        packets = phase["verification_packets"]
        completed_packets = [
            item
            for item in packets
            if item["exists"]
            and item["status"] in {"assessed", "closed"}
            and not item["validation_failures"]
        ]
        resolved = (
            phase["accountable"] is True
            and phase["resolution_status"]
            in forecast_triage.VERIFICATION_REQUIRED_STATUSES
        )
        if resolved and not completed_packets:
            blockers.append("resolved_accountable_forecast_lacks_completed_packet")
        lattice_assessment = (phase.get("lattice") or {}).get("assessment")
        if resolved and phase.get("lattice") and not (
            lattice_assessment
            and lattice_assessment.get("status") in {"canonical_assessed", "canonical_with_language_waiver"}
            and lattice_assessment.get("authorizes_forecast_scoring") is True
        ):
            blockers.append("resolved_accountable_forecast_lacks_canonical_multilingual_adjudication")
        if phase["accountable"] is False:
            next_action = "preserve_non_accountable_classification"
        elif phase["resolution_status"] != "open":
            next_action = "forecast_review_complete"
        elif not phase["due"]:
            next_action = "wait_until_review_date"
        elif completed_packets:
            next_action = "review_forecast_without_forcing_outcome"
        else:
            warnings.append("forecast_resolution_requires_completed_verification")
            next_action = "open_operational_verification_before_resolution"
    return {
        "schema_version": 1,
        "mode": mode,
        "contract": BOUNDED_AGENCY_CONTRACT,
        "git": {
            "head": git_head(),
            "branch": git_branch(),
            "tracking": tracking_state(),
            "dirty_paths": dirty,
        },
        "archive": manifest,
        "phase": phase,
        "phase_validation": phase_validation,
        "latest_daily_run": latest_daily_run(),
        "cadence": {
            "handoff_status": handoff["handoff_status"],
            "next_mode": handoff["next_mode"],
        },
        "authority": authority,
        "blockers": blockers,
        "warnings": warnings,
        "ready": not blockers,
        "next_action": next_action if not blockers else "repair_preflight",
    }


def print_startup(state: dict) -> None:
    archive = state["archive"]
    git = state["git"]
    print(f"mode={state['mode']}")
    print(f"ready={str(state['ready']).lower()}")
    print(f"git_head={git['head']}")
    print(f"git_branch={git['branch']}")
    print(f"dirty_path_count={len(git['dirty_paths'])}")
    print(f"manifest_rows={archive['row_count']}")
    print(f"archive_files={archive['archive_file_count']}")
    print(f"archive_manifest_parity={str(archive['parity']).lower()}")
    print(f"latest_intake_date={archive['latest_intake_date'] or 'none'}")
    print(f"latest_daily_run={state['latest_daily_run'] or 'none'}")
    print(f"handoff_status={state['cadence']['handoff_status']}")
    if state["phase"]:
        if state["mode"] == "geopolitical-synthesis":
            print(f"selected_date={state['phase']['date']}")
            print(f"manifest_day_rows={state['phase']['manifest_day_rows']}")
            print(f"daily_contract_state={state['phase']['daily_contract_state']}")
        elif state["mode"] == "operational-verification":
            print(f"packet_id={state['phase']['packet_id']}")
            print(f"packet_status={state['phase']['status'] or 'missing'}")
            print(
                "assessment_outcome="
                f"{state['phase']['assessment_outcome'] or 'none'}"
            )
        elif state["mode"] == "forecast-review":
            print(f"hook_id={state['phase']['hook_id']}")
            print(f"review_date={state['phase']['review_date'] or 'missing'}")
            print(f"resolution_status={state['phase']['resolution_status'] or 'missing'}")
    print(f"blockers={','.join(state['blockers'])}")
    print(f"warnings={','.join(state['warnings'])}")
    print(f"next_action={state['next_action']}")


def load_handoff(path: Path = HANDOFF_PATH) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def verification_passed(verification: dict) -> bool:
    required = {"integrity", "tests"}
    return required <= set(verification) and all(
        verification[name].get("passed") is True for name in required
    )


def normalize_artifact_refs(values: list[str]) -> list[str]:
    normalized: list[str] = []
    root = REPO_ROOT.resolve()
    for value in values:
        ref = value.strip().replace("\\", "/")
        path_text = ref.split("#", 1)[0]
        candidate = Path(path_text)
        if not ref or candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"artifact reference must be repo-relative: {value}")
        resolved = (REPO_ROOT / candidate).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as error:
            raise ValueError(f"artifact reference escapes repository: {value}") from error
        if not resolved.exists():
            raise ValueError(f"artifact reference does not exist: {value}")
        if ref not in normalized:
            normalized.append(ref)
    if not normalized:
        raise ValueError("at least one artifact reference is required")
    return normalized


def coffee_state(path: Path = HANDOFF_PATH) -> dict:
    current_head = git_head()
    current_dirty = dirty_paths()
    current_fingerprint = worktree_fingerprint()
    handoff = load_handoff(path)
    state = {
        "git_head": current_head,
        "dirty_paths": current_dirty,
        "worktree_fingerprint": current_fingerprint,
        "latest_daily_run": latest_daily_run(),
        "handoff": handoff,
        "handoff_status": "missing",
        "next_mode": "bootstrap_bounded_experiment",
    }
    if handoff is None:
        return state

    same_head = handoff.get("git_head") == current_head
    if "worktree_fingerprint" in handoff:
        same_dirty = handoff["worktree_fingerprint"] == current_fingerprint
    else:
        same_dirty = handoff.get("dirty_paths") == current_dirty
    verified = verification_passed(handoff.get("verification", {}))
    if not verified:
        status = "verification_failed"
        mode = "repair_before_inheriting"
    elif not (same_head and same_dirty):
        status = "stale"
        mode = "reconcile_state_before_inheriting"
    else:
        status = "current"
        outcome = handoff.get("learning", {}).get("outcome", "inconclusive")
        mode = NEXT_MODES.get(outcome, "run_discriminating_test")
    state["handoff_status"] = status
    state["next_mode"] = mode
    return state


def coffee_view(state: dict) -> dict:
    handoff = state.get("handoff")
    return {
        "git_head": state["git_head"],
        "dirty_path_count": len(state["dirty_paths"]),
        "latest_daily_run": state["latest_daily_run"],
        "handoff_status": state["handoff_status"],
        "next_mode": state["next_mode"],
        "learning": handoff.get("learning") if handoff else None,
        "verification_passed": (
            verification_passed(handoff.get("verification", {})) if handoff else None
        ),
    }


def run_verification() -> dict:
    try:
        python = resolve_validation_python(REPO_ROOT)
    except BootstrapUnavailable as error:
        unavailable = {
            "status": "unavailable",
            "passed": False,
            "returncode": None,
            "output_tail": str(error)[-2000:],
        }
        return {
            "integrity": dict(unavailable),
            "tests": dict(unavailable),
        }
    commands = {
        "integrity": [str(python), "scripts/validate_repository.py"],
        "tests": [
            str(python),
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
    }
    results: dict[str, dict] = {}
    for name, command in commands.items():
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        output = (result.stdout + result.stderr).strip()
        results[name] = {
            "status": "passed" if result.returncode == 0 else "failed",
            "passed": result.returncode == 0,
            "returncode": result.returncode,
            "output_tail": output[-2000:],
        }
    return results


def write_dream(
    *,
    experiment: str,
    outcome: str,
    lesson: str,
    improvement: str,
    evidence_summary: str,
    artifact_refs: list[str],
    tomorrow_inherits: str,
    path: Path = HANDOFF_PATH,
    verify: Callable[[], dict] = run_verification,
) -> dict:
    evidence_summary = evidence_summary.strip()
    if not evidence_summary:
        raise ValueError("evidence summary must not be empty")
    artifact_refs = normalize_artifact_refs(artifact_refs)
    verification = verify()
    payload = {
        "schema_version": 2,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_head": git_head(),
        "dirty_paths": dirty_paths(),
        "worktree_fingerprint": worktree_fingerprint(),
        "verification": verification,
        "learning": {
            "experiment": experiment,
            "outcome": outcome,
            "lesson": lesson,
            "method_change_candidate": improvement,
            "evidence_summary": evidence_summary,
            "artifact_refs": artifact_refs,
            "tomorrow_inherits": tomorrow_inherits,
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def print_coffee(state: dict) -> None:
    print(f"handoff_status={state['handoff_status']}")
    print(f"next_mode={state['next_mode']}")
    print(f"latest_daily_run={state['latest_daily_run'] or 'none'}")
    handoff = state.get("handoff")
    if handoff:
        learning = handoff.get("learning", {})
        print(f"experiment={learning.get('experiment', '')}")
        print(f"outcome={learning.get('outcome', '')}")
        print(f"lesson={learning.get('lesson', '')}")
        print(f"method_change_candidate={learning.get('method_change_candidate', '')}")
        print(f"evidence_summary={learning.get('evidence_summary', '')}")
        print(f"artifact_refs={','.join(learning.get('artifact_refs', []))}")
        print(f"tomorrow_inherits={learning.get('tomorrow_inherits', '')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local startup, coffee, and dream continuity tooling."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    startup = subparsers.add_parser(
        "startup", help="Read dynamic session context and bounded authority."
    )
    startup.add_argument(
        "mode",
        choices=(
            "best-intake",
            "geopolitical-synthesis",
            "operational-verification",
            "forecast-review",
        ),
    )
    startup.add_argument("--date")
    startup.add_argument("--packet")
    startup.add_argument("--hook")
    startup.add_argument("--as-of")
    startup.add_argument("--json", action="store_true")
    coffee = subparsers.add_parser("coffee", help="Read the last learning handoff.")
    coffee.add_argument("--json", action="store_true")
    dream = subparsers.add_parser("dream", help="Verify and persist one learning handoff.")
    dream.add_argument("--experiment", required=True)
    dream.add_argument("--outcome", choices=OUTCOMES, required=True)
    dream.add_argument("--lesson", required=True)
    dream.add_argument("--improvement", required=True)
    dream.add_argument("--evidence-summary", required=True)
    dream.add_argument("--artifact-ref", action="append", required=True)
    dream.add_argument("--tomorrow-inherits", required=True)
    dream.add_argument("--json", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "startup":
        try:
            state = startup_state(
                args.mode,
                run_date=args.date,
                packet_id=args.packet,
                hook_id=args.hook,
                as_of=args.as_of,
            )
        except ValueError as error:
            raise SystemExit(str(error)) from error
        if args.json:
            print(json.dumps(state, indent=2))
        else:
            print_startup(state)
        if not state["ready"]:
            raise SystemExit(1)
        return

    if args.command == "coffee":
        state = coffee_state()
        if args.json:
            print(json.dumps(coffee_view(state), indent=2))
        else:
            print_coffee(state)
        return

    payload = write_dream(
        experiment=args.experiment,
        outcome=args.outcome,
        lesson=args.lesson,
        improvement=args.improvement,
        evidence_summary=args.evidence_summary,
        artifact_refs=args.artifact_ref,
        tomorrow_inherits=args.tomorrow_inherits,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        passed = verification_passed(payload["verification"])
        print(f"dream_written={HANDOFF_PATH.relative_to(REPO_ROOT).as_posix()}")
        print(f"verification_passed={str(passed).lower()}")
        print(f"next_mode={NEXT_MODES[args.outcome] if passed else 'repair_before_inheriting'}")
    if not verification_passed(payload["verification"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

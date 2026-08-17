from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable


SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import cadence_ledger
import rest_receipts
import archive_audit
from archive_membership import source_reference_available
import triage_forecast_ledger as forecast_triage
import verification as verification_packets
import reality
from cadence_results import aggregate as aggregate_results, command_result
from runtime_bootstrap import BootstrapUnavailable, resolve_validation_python
from runtime_names import remove_environment_pair, resolve_environment
from session_preflight import probe_temp_root


REPO_ROOT = Path(__file__).resolve().parent.parent
HANDOFF_PATH = (
    REPO_ROOT / "narrative-geopolitics" / "work" / "cadence" / "last-dream.json"
)
BASELINE_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "cadence" / "baselines"
VALIDATOR_PATH = REPO_ROOT / "tools" / "validate_repo.py"
TEMP_ROOT_ENV = "MIRA_CORE_SESSION_TEMP_ROOT"
HEARTBEAT_SECONDS = 30
DAILY_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "daily"
MANIFEST_PATH = REPO_ROOT / "archive" / "sources" / "geopolitics" / "source-manifest.json"
ARCHIVE_SOURCES_ROOT = REPO_ROOT / "archive" / "sources" / "geopolitics" / "sources"
BOUNDED_AGENCY_CONTRACT = (
    "narrative-geopolitics/method/bounded-agency-contract.md"
)
BEST_INTAKE_AUTHORITY = {
    "may_read": [
        "repository Git state",
        "archive/sources/geopolitics/source-manifest.json",
        "existing archive sources for duplicate detection",
        "voice and channel records for provisional canonical routing",
        "best-intake method and metadata contracts",
    ],
    "may_write": [
        "archive/sources/geopolitics/sources/YYYY-MM-DD/source-*.md",
        "archive/sources/geopolitics/source-manifest.json",
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
        "archive/sources/geopolitics/source-manifest.json",
        "manifest-backed archive sources for the selected date",
        "narrative-geopolitics/voices/ and narrative-geopolitics/channels/",
        "existing daily, forecast, and verification state",
        "geo-strategy method and templates",
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
INHERITANCE_SCOPES = ("local-use", "repo-use", "public-use")
EXPERIMENT_PROFILES = {
    "mira-journal-composition": {
        "version": 1,
        "timeout_seconds": 180,
        "purpose": (
            "Validate the repository-local Mira Journal skill, governed composition "
            "contracts, continuity projection, recoverable approval transaction, and "
            "recursive-learning boundary. A pass grants local-use eligibility only."
        ),
        "paths": [
            "docs/skill-drafts/mira-journal/SKILL.md",
            "docs/skill-drafts/mira-journal/references/composition-method.md",
            "docs/skill-drafts/mira-journal/agents/openai.yaml",
            "scripts/mira_journal.py",
            "scripts/mira_journal_references.py",
            "tests/test_mira_journal.py",
            "tests/test_mira_journal_skill.py",
            "tests/test_recursive_learning_ledger.py",
        ],
        "command": [
            "-m", "pytest",
            "tests/test_mira_journal.py",
            "tests/test_mira_journal_skill.py",
            "tests/test_recursive_learning_ledger.py",
            "-q", "-p", "no:cacheprovider",
        ],
    },
    "research-brief-commissioning": {
        "version": 1,
        "timeout_seconds": 180,
        "purpose": (
            "Validate the Research Brief commissioning contract, cold-handoff "
            "schemas, runtime routing, and non-authorizing producer seeds. Passing "
            "this profile does not establish decision usefulness."
        ),
        "paths": [
            "AGENTS.md",
            "docs/skill-drafts/research-brief/SKILL.md",
            "docs/skill-drafts/research-brief/assets/research-brief-seed-v1.json",
            "docs/skill-drafts/research-brief/assets/research-execution-handoff-v1.json",
            "docs/skill-drafts/reality-check/SKILL.md",
            "scripts/research_handoff.py",
            "scripts/reality_handoff.py",
            "scripts/continuity.py",
            "scripts/validate_repository.py",
            "tools/run_repo.py",
            "tests/test_research_handoff.py",
            "tests/test_research_brief_skill.py",
            "tests/test_reality_handoff.py",
            "tests/test_reality_check_skill.py",
            "tests/test_continuity.py",
            "tests/test_runtime_tooling.py",
        ],
        "command": [
            "-m",
            "pytest",
            "tests/test_research_handoff.py",
            "tests/test_research_brief_skill.py",
            "tests/test_reality_handoff.py",
            "tests/test_reality_check_skill.py",
            "tests/test_continuity.py",
            "tests/test_runtime_tooling.py",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
    },
    "smart-intake-routing": {
        "version": 1,
        "timeout_seconds": 120,
        "purpose": "Validate canonical routing, alias normalization, and safe intake landing.",
        "paths": [
            "scripts/smart_intake.py",
            "scripts/land_best_intake.py",
            "tests/test_smart_intake.py",
            "tests/test_land_best_intake.py",
            "tests/test_intake_observability.py",
            "archive/sources/geopolitics/source-manifest.json",
        ],
        "command": ["-m", "pytest", "tests/test_smart_intake.py", "tests/test_land_best_intake.py", "tests/test_intake_observability.py", "-q", "-p", "no:cacheprovider"],
    },
    "pape-voice-judgment": {
        "version": 1,
        "timeout_seconds": 30,
        "purpose": (
            "Validate the five migrated Pape voice-local hooks, their distinct "
            "judgment classes, deterministic rendering, and unscored boundary. "
            "Passing this profile does not promote or score any hook as an NG-* "
            "forecast."
        ),
        "paths": [
            "scripts/voice_judgments.py",
            "narrative-geopolitics/work/voice-judgments/external-voice-judgment-ledger.json",
            "narrative-geopolitics/voices/pape/judgment-ledger.md",
            "tests/test_voice_judgments.py",
        ],
        "command": [
            "-m",
            "pytest",
            "tests/test_voice_judgments.py",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
    },
}
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


def archive_benchmark_state(run_date: str) -> dict:
    try:
        payload = archive_audit.build_audit(
            archive_audit.parse_args(["--start-date", run_date, "--end-date", run_date])
        )
    except Exception as error:
        return {
            "available": False,
            "error": str(error),
            "source_count": 0,
            "density_class": "unknown",
            "advisory_labels": ["archive_benchmarks_unavailable"],
            "repair_candidate_warnings": 0,
            "future_unlanded_days": 0,
            "landed_horizon_completeness_pct": 0.0,
            "structural_failures": 0,
        }
    benchmarks = payload["benchmarks"]
    return {
        "available": True,
        "source_count": benchmarks["source_count"],
        "density_class": archive_audit.density_class(benchmarks["source_count"]),
        "advisory_labels": benchmarks["advisory_labels"],
        "repair_candidate_warnings": benchmarks["repair_candidate_warnings"],
        "future_unlanded_days": benchmarks["future_unlanded_days"],
        "landed_horizon_completeness_pct": benchmarks["landed_horizon_completeness_pct"],
        "structural_failures": payload["summary"]["structural_failures"],
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
    mode = {
        "intake": "best-intake",
        "archive-intake": "best-intake",
        "smart-intake": "best-intake",
    }.get(mode, mode)
    if mode not in {
        "best-intake",
        "geo-strategy",
        "geopolitical-synthesis",
        "operational-verification",
        "forecast-review",
    }:
        raise ValueError(f"unsupported startup mode: {mode}")
    if mode in {"geo-strategy", "geopolitical-synthesis"} and not run_date:
        raise ValueError("geo-strategy startup requires --date")
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
    if mode in {"geo-strategy", "geopolitical-synthesis"}:
        assert run_date is not None
        phase = synthesis_state(run_date)
        phase["archive_benchmarks"] = archive_benchmark_state(run_date)
        authority = scoped_synthesis_authority(run_date)
        if phase["manifest_day_rows"] == 0:
            blockers.append("no_manifest_rows_for_selected_date")
        if phase["missing_archive_sources"]:
            blockers.append("selected_date_archive_sources_missing")
        benchmark_labels = set(phase["archive_benchmarks"]["advisory_labels"])
        if "archive_benchmarks_unavailable" in benchmark_labels:
            warnings.append("archive_benchmarks_unavailable")
        if phase["archive_benchmarks"]["density_class"] == "thin" and phase["manifest_day_rows"]:
            warnings.append("archive_day_thin")
        if {"dense-review", "very-dense-review"}.intersection(benchmark_labels):
            warnings.append("archive_day_dense_review")
        if phase["archive_benchmarks"]["repair_candidate_warnings"]:
            warnings.append("archive_repair_candidates_present")
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
        lattice = phase.get("lattice") or {}
        lattice_claim = lattice.get("claim") or {}
        lattice_assessment = lattice.get("assessment")
        # Forecast scoring evaluates the declared forecast observable. It does
        # not authorize factual adoption, publication, or operational truth.
        # Keep canonical multilingual adjudication mandatory for other lattice
        # claims, while avoiding a category error for bounded forecast review.
        forecast_scope = lattice_claim.get("forecast_scope")
        bounded_discourse_forecast = (
            lattice_claim.get("claim_type") == "forecast"
            and forecast_scope == "public_discourse"
        )
        if resolved and phase.get("lattice") and not bounded_discourse_forecast and not (
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
        if state["mode"] in {"geo-strategy", "geopolitical-synthesis"}:
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
    if "repository" in verification:
        return verification["repository"].get("passed") is True
    required = {"integrity", "tests"}
    return required <= set(verification) and all(
        verification[name].get("passed") is True for name in required
    )


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def command_digest(command: list[str]) -> str:
    return hashlib.sha256(
        json.dumps(command, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def unresolved_check(status: str = "not_run") -> dict:
    return {
        "status": status,
        "passed": False,
        "returncode": None,
        "elapsed_seconds": 0.0,
        "output_tail": "",
    }


def initial_verification(profile: str | None) -> dict:
    experiment = unresolved_check("running" if profile else "not_run")
    if profile:
        spec = EXPERIMENT_PROFILES[profile]
        experiment.update(
            {
                "profile": profile,
                "profile_version": spec["version"],
                "paths": spec["paths"],
                "command_digest": command_digest(spec["command"]),
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    repository = unresolved_check()
    repository.update({"cache_status": "not_checked", "phase_timings": {}})
    return {
        "experiment": experiment,
        "repository": repository,
        "integrity": unresolved_check(),
        "tests": unresolved_check(),
        "structured": aggregate_results([]),
        "inheritance": {
            "local-use": "blocked",
            "repo-use": "blocked",
            "public-use": "not_authorized",
        },
    }


def resolve_temp_root(value: Path | None) -> Path:
    candidate = value
    configured_temp = resolve_environment(TEMP_ROOT_ENV)
    if candidate is None and configured_temp:
        candidate = Path(configured_temp)
    if candidate is None:
        raise ValueError(f"--temp-root or {TEMP_ROOT_ENV} is required")
    report = probe_temp_root(candidate, repo_root=REPO_ROOT)
    if not report["writable"] or not report["probe_removed"]:
        raise ValueError(report["failure"] or "temporary root preflight failed")
    return Path(report["resolved_root"])


def cleanup_owned_temp(path: Path | None, *, root: Path | None) -> None:
    if path is None or root is None or not path.exists():
        return
    resolved = path.resolve()
    resolved.relative_to(root.resolve())
    shutil.rmtree(resolved)


def validation_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    remove_environment_pair("MIRA_CORE_CHOICE_DB", environment)
    remove_environment_pair("MIRA_CORE_CADENCE_DB", environment)
    existing = environment.get("PYTHONPATH")
    scripts = str(SCRIPTS_ROOT)
    environment["PYTHONPATH"] = scripts if not existing else os.pathsep.join((scripts, existing))
    return environment


def run_profile_verification(profile: str, temp_root: Path) -> dict:
    spec = EXPERIMENT_PROFILES.get(profile)
    if spec is None:
        raise ValueError(f"unknown experiment profile: {profile}")
    try:
        python = resolve_validation_python(REPO_ROOT)
    except BootstrapUnavailable as error:
        return {
            **unresolved_check("unavailable"),
            "profile": profile,
            "profile_version": spec["version"],
            "paths": spec["paths"],
            "command_digest": command_digest(spec["command"]),
            "output_tail": str(error)[-2000:],
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
    pytest_root = temp_root / f"profile-{profile}-{os.getpid()}-{uuid.uuid4().hex}"
    command = [str(python), *spec["command"]]
    if spec["command"][:2] == ["-m", "pytest"]:
        command.extend(["--basetemp", str(pytest_root)])
    started = time.monotonic()
    status = "failed"
    returncode: int | None = None
    output = ""
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=validation_environment(),
            capture_output=True,
            text=True,
            timeout=spec["timeout_seconds"],
        )
        returncode = result.returncode
        output = (result.stdout + result.stderr).strip()
        status = "passed" if returncode == 0 else "failed"
    except subprocess.TimeoutExpired as error:
        status = "timed_out"
        returncode = 124
        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or "")
        output = f"{stdout}{stderr}".strip()
    finally:
        cleanup_owned_temp(pytest_root, root=temp_root)
    return {
        "status": status,
        "passed": status == "passed",
        "returncode": returncode,
        "profile": profile,
        "profile_version": spec["version"],
        "paths": spec["paths"],
        "command_digest": command_digest(spec["command"]),
        "timeout_seconds": spec["timeout_seconds"],
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "output_tail": output[-2000:],
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }


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
        if not resolved.exists() and not (
            path_text.startswith("archive/sources/geopolitics/sources/")
            and source_reference_available(REPO_ROOT, path_text)
        ):
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
    verification = handoff.get("verification", {})
    experiment_status = verification.get("experiment", {}).get("status")
    repository_status = verification.get("repository", {}).get("status")
    if handoff.get("schema_version", 2) >= 3 and (
        experiment_status == "running" or repository_status == "running"
    ):
        status = "interrupted"
        mode = "resume_or_repair_interrupted_verification"
    elif not (same_head and same_dirty):
        status = "stale"
        mode = "reconcile_state_before_inheriting"
    elif handoff.get("schema_version", 2) >= 3 and (
        experiment_status in {"failed", "timed_out", "unavailable", "state_changed"}
        or repository_status in {"failed", "timed_out", "unavailable", "state_changed"}
    ):
        status = "verification_failed"
        mode = "repair_before_inheriting"
    elif handoff.get("schema_version", 2) >= 3 and repository_status == "not_run":
        status = "local_current_repo_pending"
        mode = "promote_or_continue_local_only"
    elif not verification_passed(verification):
        status = "verification_failed"
        mode = "repair_before_inheriting"
    else:
        status = "current"
        outcome = handoff.get("learning", {}).get("outcome", "inconclusive")
        mode = NEXT_MODES.get(outcome, "run_discriminating_test")
    state["handoff_status"] = status
    state["next_mode"] = mode
    return state


def coffee_view(state: dict) -> dict:
    handoff = state.get("handoff")
    verification = handoff.get("verification", {}) if handoff else {}
    return {
        "git_head": state["git_head"],
        "dirty_path_count": len(state["dirty_paths"]),
        "latest_daily_run": state["latest_daily_run"],
        "handoff_status": state["handoff_status"],
        "next_mode": state["next_mode"],
        "learning": handoff.get("learning") if handoff else None,
        "verification_passed": (
            verification_passed(verification) if handoff else None
        ),
        "inheritance": verification.get("inheritance", {
            "local-use": "blocked" if handoff else "not_applicable",
            "repo-use": "blocked" if handoff else "not_applicable",
            "public-use": "not_authorized",
        }),
        "experiment_verification": verification.get("experiment", {}).get("status") if handoff else None,
        "repository_verification": verification.get("repository", {}).get("status") if handoff else None,
        "repository_cache_status": verification.get("repository", {}).get("cache_status") if handoff else None,
    }


def refresh_structured_verification(verification: dict) -> None:
    results = []
    experiment = verification.get("experiment", {})
    if experiment.get("status") not in {None, "not_run", "running"}:
        status = experiment["status"]
        structured_status = (
            "passed" if status == "passed" else ("unavailable" if status == "unavailable" else "failed")
        )
        results.append(
            command_result(
                check_id=experiment.get("profile", "unprofiled-experiment"),
                status=structured_status,
                scope="experiment",
                command=["profile", experiment.get("profile", "none")],
                output_tail=experiment.get("output_tail", ""),
                failure_class=None if structured_status == "passed" else "command",
                owner="experiment" if structured_status != "passed" else "",
                next_action=(
                    "Repair or rerun the bounded experiment profile."
                    if structured_status != "passed"
                    else ""
                ),
                details={"phase_status": status},
            )
        )
    repository = verification.get("repository", {})
    if repository.get("status") not in {None, "not_run", "running"}:
        status = repository["status"]
        structured_status = (
            "passed" if status == "passed" else ("unavailable" if status == "unavailable" else "failed")
        )
        results.append(
            command_result(
                check_id="repository-promotion",
                status=structured_status,
                scope="repository",
                command=["cadence", "promote"],
                output_tail=repository.get("output_tail", ""),
                failure_class=None if structured_status == "passed" else "command",
                owner="repository" if structured_status != "passed" else "",
                next_action=(
                    "Repair the reported repository condition, then rerun cadence promote."
                    if structured_status != "passed"
                    else ""
                ),
                details={"phase_status": status},
            )
        )
    verification["structured"] = aggregate_results(results)


def parse_validator_output(output: str) -> tuple[str, dict[str, dict]]:
    cache_status = "unavailable"
    phase_timings: dict[str, dict] = {}
    cache_match = re.search(r"validation_cache status=([^\s]+)", output)
    if cache_match:
        cache_status = cache_match.group(1)
    for match in re.finditer(
        r"validation_timing mode=\S+ phase=(\S+) seconds=([0-9.]+) status=(\S+)(?: reason=(\S+))?",
        output,
    ):
        phase_timings[match.group(1)] = {
            "seconds": float(match.group(2)),
            "status": match.group(3),
            "reason": match.group(4),
        }
    return cache_status, phase_timings


def run_repository_validator(
    temp_root: Path,
    *,
    force: bool = False,
    heartbeat_seconds: int = HEARTBEAT_SECONDS,
) -> dict:
    try:
        python = resolve_validation_python(REPO_ROOT)
    except BootstrapUnavailable as error:
        return {
            **unresolved_check("unavailable"),
            "cache_status": "unavailable",
            "phase_timings": {},
            "output_tail": str(error)[-2000:],
        }
    owned = temp_root / f"promotion-{os.getpid()}-{uuid.uuid4().hex}"
    owned.mkdir()
    log_path = owned / "validator.log"
    command = [
        str(python),
        str(VALIDATOR_PATH.relative_to(REPO_ROOT)),
        "--mode",
        "full",
        "--temp-root",
        str(temp_root),
    ]
    if force:
        command.append("--force")
    started = time.monotonic()
    returncode: int | None = None
    output = ""
    status = "failed"
    try:
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                command,
                cwd=REPO_ROOT,
                env=validation_environment(),
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )
            next_heartbeat = started + heartbeat_seconds
            while process.poll() is None:
                now = time.monotonic()
                if now >= next_heartbeat:
                    print(
                        "cadence_promotion_heartbeat "
                        f"elapsed_seconds={int(now - started)}",
                        file=sys.stderr,
                        flush=True,
                    )
                    next_heartbeat = now + heartbeat_seconds
                time.sleep(0.25)
            returncode = process.returncode
        output = log_path.read_text(encoding="utf-8", errors="replace")
        status = "passed" if returncode == 0 else ("timed_out" if returncode == 124 else "failed")
    finally:
        if log_path.exists() and not output:
            output = log_path.read_text(encoding="utf-8", errors="replace")
        cleanup_owned_temp(owned, root=temp_root)
    cache_status, phase_timings = parse_validator_output(output)
    return {
        "status": status,
        "passed": status == "passed",
        "returncode": returncode,
        "cache_status": cache_status,
        "phase_timings": phase_timings,
        "command_digest": command_digest(command[1:]),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "output_tail": output[-2000:],
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }


def upgrade_handoff_v3(handoff: dict) -> dict:
    if handoff.get("schema_version", 2) >= 3:
        return handoff
    verification = handoff.setdefault("verification", {})
    old_passed = verification_passed(verification)
    repository = unresolved_check("passed" if old_passed else "failed")
    repository.update(
        {
            "passed": old_passed,
            "cache_status": "legacy",
            "phase_timings": {},
            "output_tail": "Migrated from schema-v2 repository verification.",
        }
    )
    verification.setdefault("experiment", unresolved_check())
    verification["repository"] = repository
    verification["inheritance"] = {
        "local-use": "eligible" if old_passed else "blocked",
        "repo-use": "eligible" if old_passed else "blocked",
        "public-use": "not_authorized",
    }
    handoff["schema_version"] = 3
    refresh_structured_verification(verification)
    return handoff


def promote_dream(
    *,
    temp_root: Path,
    force: bool = False,
    path: Path = HANDOFF_PATH,
    runner: Callable[..., dict] = run_repository_validator,
) -> dict:
    handoff = load_handoff(path)
    if handoff is None:
        raise ValueError("no Dream handoff exists to promote")
    handoff = upgrade_handoff_v3(handoff)
    current_head = git_head()
    current_fingerprint = worktree_fingerprint()
    if handoff.get("git_head") != current_head or handoff.get("worktree_fingerprint") != current_fingerprint:
        raise ValueError("Dream handoff is stale; create a current handoff before promotion")
    experiment = handoff["verification"].get("experiment", {})
    if experiment.get("profile") and experiment.get("status") != "passed":
        raise ValueError("profiled Dream cannot be promoted until its experiment passes")
    repository = unresolved_check("running")
    repository.update(
        {
            "cache_status": "checking",
            "phase_timings": {},
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    handoff["verification"]["repository"] = repository
    handoff["updated_at"] = datetime.now(timezone.utc).isoformat()
    refresh_structured_verification(handoff["verification"])
    atomic_write_json(path, handoff)

    result = runner(temp_root, force=force)
    post_head = git_head()
    post_fingerprint = worktree_fingerprint()
    if post_head != current_head or post_fingerprint != current_fingerprint:
        result["status"] = "state_changed"
        result["passed"] = False
        result["output_tail"] = (
            result.get("output_tail", "")
            + "\nRepository state changed during promotion."
        )[-2000:]
    handoff["verification"]["repository"] = result
    phase_timings = result.get("phase_timings", {})
    cache_hit = result.get("cache_status") == "hit"
    for key, phase in (("integrity", "structural"), ("tests", "pytest")):
        timing = phase_timings.get(phase, {})
        phase_passed = result.get("passed", False) and (
            cache_hit or timing.get("status") in {"passed", "skipped"}
        )
        handoff["verification"][key] = {
            "status": "passed" if phase_passed else result.get("status", "failed"),
            "passed": phase_passed,
            "returncode": 0 if phase_passed else result.get("returncode"),
            "elapsed_seconds": timing.get("seconds", 0.0),
            "output_tail": result.get("output_tail", ""),
        }
    if result.get("passed"):
        handoff["verification"]["inheritance"] = {
            "local-use": "eligible",
            "repo-use": "eligible",
            "public-use": "not_authorized",
        }
    else:
        handoff["verification"]["inheritance"]["repo-use"] = "blocked"
    handoff["git_head"] = post_head
    handoff["dirty_paths"] = dirty_paths()
    handoff["worktree_fingerprint"] = post_fingerprint
    handoff["updated_at"] = datetime.now(timezone.utc).isoformat()
    refresh_structured_verification(handoff["verification"])
    atomic_write_json(path, handoff)
    return handoff


def write_baseline(
    profile: str,
    *,
    temp_root: Path,
    path: Path | None = None,
) -> dict:
    spec = EXPERIMENT_PROFILES.get(profile)
    if spec is None:
        raise ValueError(f"unknown experiment profile: {profile}")
    result = run_profile_verification(profile, temp_root)
    payload = {
        "schema_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "profile_version": spec["version"],
        "git_head": git_head(),
        "dirty_paths": dirty_paths(),
        "worktree_fingerprint": worktree_fingerprint(),
        "paths": spec["paths"],
        "command": spec["command"],
        "status": result["status"],
        "passed": result["passed"],
        "returncode": result["returncode"],
        "elapsed_seconds": result["elapsed_seconds"],
        "output_tail": result["output_tail"],
    }
    target = path or (BASELINE_ROOT / f"{profile}.json")
    atomic_write_json(target, payload)
    return payload


def write_dream(
    *,
    experiment: str,
    outcome: str,
    lesson: str,
    improvement: str,
    evidence_summary: str,
    artifact_refs: list[str],
    tomorrow_inherits: str,
    profile: str | None = None,
    temp_root: Path | None = None,
    measurement: dict | None = None,
    path: Path = HANDOFF_PATH,
    profile_runner: Callable[[str, Path], dict] = run_profile_verification,
) -> dict:
    evidence_summary = evidence_summary.strip()
    if not evidence_summary:
        raise ValueError("evidence summary must not be empty")
    artifact_refs = normalize_artifact_refs(artifact_refs)
    if profile and profile not in EXPERIMENT_PROFILES:
        raise ValueError(f"unknown experiment profile: {profile}")
    verification = initial_verification(profile)
    initial_head = git_head()
    initial_fingerprint = worktree_fingerprint()
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": 3,
        "timestamp": now,
        "updated_at": now,
        "git_head": initial_head,
        "dirty_paths": dirty_paths(),
        "worktree_fingerprint": initial_fingerprint,
        "verification": verification,
        "measurement": measurement or {},
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
    atomic_write_json(path, payload)
    if not profile:
        return payload

    try:
        resolved_temp = resolve_temp_root(temp_root)
        experiment_result = profile_runner(profile, resolved_temp)
    except Exception as error:
        detail = f"{type(error).__name__}: {error}"
        experiment_result = {
            **verification["experiment"],
            "status": "unavailable",
            "passed": False,
            "returncode": None,
            "output_tail": detail[-2000:],
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
    final_head = git_head()
    final_fingerprint = worktree_fingerprint()
    if final_head != initial_head or final_fingerprint != initial_fingerprint:
        experiment_result["status"] = "state_changed"
        experiment_result["passed"] = False
        experiment_result["output_tail"] = (
            experiment_result.get("output_tail", "")
            + "\nRepository state changed during profile verification."
        )[-2000:]
    payload["verification"]["experiment"] = experiment_result
    if experiment_result.get("passed"):
        payload["verification"]["inheritance"]["local-use"] = "eligible"
    payload["git_head"] = final_head
    payload["dirty_paths"] = dirty_paths()
    payload["worktree_fingerprint"] = final_fingerprint
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    refresh_structured_verification(payload["verification"])
    atomic_write_json(path, payload)
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
        inheritance = handoff.get("verification", {}).get("inheritance", {})
        if inheritance:
            print(f"local_use={inheritance.get('local-use', 'blocked')}")
            print(f"repo_use={inheritance.get('repo-use', 'blocked')}")
            print("public_use=not_authorized")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local startup, coffee, and dream continuity tooling."
    )
    parser.add_argument("--db", type=Path, help="Absolute private cadence SQLite path; alternatively set MIRA_CORE_CADENCE_DB.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    startup = subparsers.add_parser(
        "startup", help="Read dynamic session context and bounded authority."
    )
    startup.add_argument(
        "mode",
        choices=(
            "intake",
            "archive-intake",
            "smart-intake",
            "best-intake",
            "geo-strategy",
            "operational-verification",
            "forecast-review",
        ),
    )
    startup.add_argument("--date")
    startup.add_argument("--packet")
    startup.add_argument("--hook")
    startup.add_argument("--as-of")
    startup.add_argument("--json", action="store_true")
    coffee = subparsers.add_parser("coffee", help="Read a private cadence candidate without mutation.")
    coffee.add_argument("--json", action="store_true")
    coffee.add_argument("--format", choices=("json", "markdown"))
    coffee.add_argument("--episode-id")
    profile = subparsers.add_parser("profile", help="Inspect experiment profiles.")
    profile.add_argument("action", choices=("list", "show"))
    profile.add_argument("name", nargs="?")
    profile.add_argument("--json", action="store_true")
    baseline = subparsers.add_parser("baseline", help="Record a scoped experiment baseline.")
    baseline.add_argument("--profile", choices=tuple(EXPERIMENT_PROFILES), required=True)
    baseline.add_argument("--temp-root", type=Path)
    baseline.add_argument("--json", action="store_true")
    dream = subparsers.add_parser("dream", help="Persist one profile-first learning handoff.")
    dream.add_argument("--profile", choices=tuple(EXPERIMENT_PROFILES))
    dream.add_argument("--temp-root", type=Path)
    dream.add_argument("--experiment", required=True)
    dream.add_argument("--outcome", choices=OUTCOMES, required=True)
    dream.add_argument("--lesson", required=True)
    dream.add_argument("--improvement", required=True)
    dream.add_argument("--evidence-summary", required=True)
    dream.add_argument("--artifact-ref", action="append", required=True)
    dream.add_argument("--artifact-relationship", action="append", choices=tuple(sorted(cadence_ledger.RELATIONSHIPS)), default=[])
    dream.add_argument("--tomorrow-inherits", required=True)
    dream.add_argument("--measurement-json", help="Optional JSON measurement payload for retrieval/rework benchmarking.")
    dream.add_argument("--series-id")
    dream.add_argument("--episode-id")
    dream.add_argument("--observation")
    dream.add_argument("--diagnosis")
    dream.add_argument("--expected-observable")
    dream.add_argument("--observable-unit")
    dream.add_argument("--observable-baseline")
    dream.add_argument("--success-threshold")
    dream.add_argument("--observation-source")
    dream.add_argument("--falsifier")
    dream.add_argument("--next-use")
    dream.add_argument("--task-class")
    dream.add_argument("--expires-at")
    dream.add_argument("--method-version-digest")
    dream.add_argument("--intervention-commit", action="append", default=[])
    dream.add_argument("--idempotency-key")
    dream.add_argument("--workspace-id")
    dream.add_argument("--operator-id")
    dream.add_argument("--dream-date")
    dream.add_argument("--timezone")
    dream.add_argument("--coverage-status", choices=("complete", "partial"))
    dream.add_argument("--session-coverage-json")
    dream.add_argument("--json", action="store_true")
    promote = subparsers.add_parser(
        "promote", help="Explicitly promote the current Dream through repository validation."
    )
    promote.add_argument("--temp-root", type=Path)
    promote.add_argument("--force", action="store_true")
    promote.add_argument("--json", action="store_true")
    promote.add_argument("--episode-id")
    promote.add_argument("--idempotency-key")
    promote.add_argument("--expected-version", type=int)
    history = subparsers.add_parser("history", help="Read bounded private cadence history.")
    history.add_argument("--limit", type=int, default=50)
    history.add_argument("--json", action="store_true")
    show = subparsers.add_parser("show", help="Read one private cadence episode.")
    show.add_argument("--episode-id", required=True)
    show.add_argument("--json", action="store_true")
    subparsers.add_parser("verify-ledger", help="Verify private cadence integrity and event chains.")
    disposition = subparsers.add_parser("disposition", help="Append an explicit cadence disposition.")
    disposition.add_argument("--episode-id", required=True)
    disposition.add_argument("--decision", choices=tuple(sorted(cadence_ledger.DISPOSITIONS)), required=True)
    disposition.add_argument("--reason", required=True)
    disposition.add_argument("--idempotency-key", required=True)
    disposition.add_argument("--expected-version", type=int, required=True)
    repeat = subparsers.add_parser("repeat", help="Append a comparable later-use measurement.")
    repeat.add_argument("--episode-id", required=True)
    repeat.add_argument("--measurement-json", required=True)
    repeat.add_argument("--idempotency-key", required=True)
    repeat.add_argument("--expected-version", type=int, required=True)
    supplement = subparsers.add_parser("dream-supplement", help="Append one late session coverage receipt without rewriting the daily Dream.")
    supplement.add_argument("--episode-id", required=True)
    supplement.add_argument("--session-coverage-json", required=True)
    supplement.add_argument("--idempotency-key", required=True)
    supplement.add_argument("--expected-version", type=int, required=True)
    closeout = subparsers.add_parser("dream-closeout", help="Record a daily no-cadence-worthy-experiment receipt.")
    closeout.add_argument("--closeout-id", required=True)
    closeout.add_argument("--workspace-id", required=True)
    closeout.add_argument("--operator-id", required=True)
    closeout.add_argument("--dream-date", required=True)
    closeout.add_argument("--timezone", required=True)
    closeout.add_argument("--coverage-status", choices=("complete", "partial"), required=True)
    closeout.add_argument("--reason", required=True)
    closeout.add_argument("--session-coverage-digest", required=True)
    closeout.add_argument("--idempotency-key", required=True)
    closeout.add_argument("--json", action="store_true")
    reconcile = subparsers.add_parser("reconcile-rsi", help="Import a digest-bound private RSI correspondence receipt.")
    reconcile.add_argument("--receipt", type=Path, required=True)
    reconcile.add_argument("--idempotency-key", required=True)
    reconcile.add_argument("--expected-version", type=int, required=True)
    scorecard = subparsers.add_parser("scorecard", help="Report bounded cadence performance denominators.")
    scorecard.add_argument("--json", action="store_true")
    export = subparsers.add_parser("export-learning-reference", help="Export a private digest-bound process-learning packet.")
    export.add_argument("--episode-id", required=True)
    export.add_argument("--output", type=Path, required=True)
    export.add_argument("--check", action="store_true")
    migrate = subparsers.add_parser("migrate-legacy", help="Import the surviving legacy handoff explicitly.")
    migrate.add_argument("--idempotency-key", required=True)
    backup = subparsers.add_parser("backup", help="Copy the private cadence database to an operator-controlled external path.")
    backup.add_argument("--output", type=Path, required=True)
    backup.add_argument("--check", action="store_true")
    return parser


def _ledger_connection(args: argparse.Namespace, *, write: bool) -> sqlite3.Connection:
    resolution = cadence_ledger.resolve_store(args.db, require_exists=not write)
    if resolution.path is None:
        raise cadence_ledger.CadenceLedgerError(resolution.reason or "cadence store unavailable")
    return cadence_ledger.connect(resolution.path) if write else cadence_ledger.connect_read_only(resolution.path)


def _require_dream_ledger_fields(args: argparse.Namespace) -> None:
    required = {
        "series_id": args.series_id, "episode_id": args.episode_id,
        "observation": args.observation, "diagnosis": args.diagnosis,
        "expected_observable": args.expected_observable, "observable_unit": args.observable_unit,
        "observable_baseline": args.observable_baseline, "success_threshold": args.success_threshold,
        "observation_source": args.observation_source, "falsifier": args.falsifier,
        "next_use": args.next_use, "task_class": args.task_class, "expires_at": args.expires_at,
        "method_version_digest": args.method_version_digest, "idempotency_key": args.idempotency_key,
        "workspace_id": args.workspace_id, "operator_id": args.operator_id,
        "dream_date": args.dream_date, "timezone": args.timezone,
        "coverage_status": args.coverage_status,
        "session_coverage_json": args.session_coverage_json,
    }
    missing = [f"--{key.replace('_', '-')}" for key, value in required.items() if not value]
    if missing:
        raise cadence_ledger.CadenceLedgerError(f"private Dream requires: {', '.join(missing)}")


def write_ledger_dream(args: argparse.Namespace) -> dict[str, Any]:
    _require_dream_ledger_fields(args)
    verification = initial_verification(args.profile)
    if args.profile:
        resolved_temp = resolve_temp_root(args.temp_root)
        result = run_profile_verification(args.profile, resolved_temp)
        verification["experiment"] = result
        if result.get("passed"):
            verification["inheritance"]["local-use"] = "eligible"
        refresh_structured_verification(verification)
    now = datetime.now().astimezone().isoformat()
    profile_spec = EXPERIMENT_PROFILES.get(args.profile) if args.profile else None
    if args.artifact_relationship and len(args.artifact_relationship) != len(args.artifact_ref):
        raise cadence_ledger.CadenceLedgerError("--artifact-relationship must be omitted or repeated once per --artifact-ref")
    relationships = args.artifact_relationship or ["implementation"] * len(args.artifact_ref)
    artifacts = [
        {"ref": ref, "relationship": relationship, "captured_at": now}
        for ref, relationship in zip(args.artifact_ref, relationships, strict=True)
    ]
    episode = {
        "episode_id": args.episode_id, "series_id": args.series_id, "created_at": now,
        "workspace_id": args.workspace_id, "operator_id": args.operator_id,
        "dream_date": args.dream_date, "timezone": args.timezone,
        "coverage_status": args.coverage_status,
        "session_coverage": json.loads(args.session_coverage_json),
        "observation": args.observation, "diagnosis": args.diagnosis,
        "intervention": args.improvement, "method_version_digest": args.method_version_digest,
        "intervention_commits": args.intervention_commit,
        "profile": {
            "name": args.profile or "unprofiled",
            "version": str(profile_spec["version"]) if profile_spec else "none",
            "command_digest": command_digest(profile_spec["command"]) if profile_spec else "none",
        },
        "observable": {
            "name": args.expected_observable, "unit": args.observable_unit,
            "baseline": args.observable_baseline, "success_threshold": args.success_threshold,
            "source": args.observation_source,
        },
        "falsifier": args.falsifier, "next_use": args.next_use, "task_class": args.task_class,
        "expires_at": args.expires_at, "artifacts": artifacts,
        "relevant_paths": list(dict.fromkeys(args.artifact_ref)),
        "evidence_summary": args.evidence_summary, "tomorrow_inherits": args.tomorrow_inherits,
        "verification": verification,
        "measurements": json.loads(args.measurement_json) if args.measurement_json else {},
    }
    connection = _ledger_connection(args, write=True)
    try:
        projection = cadence_ledger.create_episode(connection, episode, idempotency_key=args.idempotency_key)
        if args.profile:
            projection = cadence_ledger.append_event(
                connection, args.episode_id, "verification_completed",
                {"passed": verification["experiment"].get("passed") is True, "verification": verification},
                idempotency_key=f"{args.idempotency_key}:verification",
                expected_version=projection["lifecycle_version"],
            )
        return projection
    finally:
        connection.close()


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
        resolution = cadence_ledger.resolve_store(args.db, require_exists=True)
        ledger_required = args.format is not None or args.episode_id is not None
        if resolution.path is not None or ledger_required:
            if resolution.path is None:
                raise SystemExit(resolution.reason or "private cadence store is unavailable")
            try:
                connection = cadence_ledger.connect_read_only(resolution.path)
                try:
                    rest_inbox = rest_receipts.resolve_inbox(None)
                    selected = cadence_ledger.selected_episode(connection, args.episode_id)
                    rest_status = rest_receipts.coffee_coverage(
                        rest_inbox, selected["episode"] if selected else None
                    )
                except (OSError, rest_receipts.RestError):
                    rest_status = "unavailable"
                context = cadence_ledger.coffee_context(
                    connection, episode_id=args.episode_id,
                    rest_coverage_status=rest_status,
                )
                connection.close()
            except (cadence_ledger.CadenceLedgerError, OSError, sqlite3.Error) as error:
                raise SystemExit(str(error)) from error
            if args.format == "markdown" or (not args.json and args.format != "json"):
                print(cadence_ledger.render_coffee_markdown(context), end="")
            else:
                print(json.dumps(context, indent=2))
        else:
            state = coffee_state()
            if args.json or args.format == "json":
                print(json.dumps(coffee_view(state), indent=2))
            else:
                print_coffee(state)
        return

    if args.command in {"history", "show", "verify-ledger", "disposition", "repeat", "dream-supplement", "dream-closeout", "reconcile-rsi", "scorecard", "export-learning-reference", "migrate-legacy", "backup"}:
        try:
            if args.command == "backup":
                resolution = cadence_ledger.resolve_store(args.db, require_exists=True)
                if resolution.path is None:
                    raise cadence_ledger.CadenceLedgerError(resolution.reason or "cadence store unavailable")
                payload = cadence_ledger.backup_store(resolution.path, args.output, check=args.check)
            elif args.command == "history":
                connection = _ledger_connection(args, write=False)
                payload = cadence_ledger.list_history(connection, limit=args.limit)
                connection.close()
            elif args.command == "show":
                connection = _ledger_connection(args, write=False)
                payload = cadence_ledger.project_episode(connection, args.episode_id)
                connection.close()
            elif args.command == "verify-ledger":
                connection = _ledger_connection(args, write=False)
                payload = cadence_ledger.verify_ledger(connection)
                connection.close()
            elif args.command == "scorecard":
                connection = _ledger_connection(args, write=False)
                payload = cadence_ledger.scorecard(connection)
                connection.close()
            elif args.command == "export-learning-reference":
                connection = _ledger_connection(args, write=False)
                projection = cadence_ledger.project_episode(connection, args.episode_id)
                connection.close()
                payload = cadence_ledger.export_learning_reference(projection, args.output, check=args.check)
            elif args.command == "disposition":
                connection = _ledger_connection(args, write=True)
                payload = cadence_ledger.record_disposition(
                    connection, args.episode_id, args.decision, args.reason,
                    idempotency_key=args.idempotency_key, expected_version=args.expected_version,
                )
                connection.close()
            elif args.command == "repeat":
                measurement = json.loads(args.measurement_json)
                if not isinstance(measurement, dict):
                    raise cadence_ledger.CadenceLedgerError("--measurement-json must decode to an object")
                connection = _ledger_connection(args, write=True)
                payload = cadence_ledger.record_repetition(
                    connection, args.episode_id, measurement,
                    idempotency_key=args.idempotency_key, expected_version=args.expected_version,
                )
                connection.close()
            elif args.command == "dream-supplement":
                receipt = json.loads(args.session_coverage_json)
                connection = _ledger_connection(args, write=True)
                payload = cadence_ledger.append_session_supplement(
                    connection, args.episode_id, receipt,
                    idempotency_key=args.idempotency_key,
                    expected_version=args.expected_version,
                )
                connection.close()
            elif args.command == "dream-closeout":
                connection = _ledger_connection(args, write=True)
                payload = cadence_ledger.record_dream_closeout(connection, {
                    "closeout_id": args.closeout_id, "workspace_id": args.workspace_id,
                    "operator_id": args.operator_id, "dream_date": args.dream_date,
                    "timezone": args.timezone, "coverage_status": args.coverage_status,
                    "reason": args.reason, "session_coverage_digest": args.session_coverage_digest,
                }, idempotency_key=args.idempotency_key)
                connection.close()
            elif args.command == "reconcile-rsi":
                receipt_path = cadence_ledger.require_private_path(args.receipt, label="RSI correspondence receipt")
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                connection = _ledger_connection(args, write=True)
                episode_id = str(receipt.get("correspondence", {}).get("source_episode_id", ""))
                payload = cadence_ledger.reconcile_rsi(
                    connection, receipt, idempotency_key=args.idempotency_key,
                    expected_version=args.expected_version,
                )
                connection.close()
            else:
                handoff = load_handoff()
                if handoff is None:
                    raise cadence_ledger.CadenceLedgerError("no surviving legacy Dream handoff exists")
                learning = handoff.get("learning", {})
                now = str(handoff.get("timestamp") or datetime.now(timezone.utc).isoformat())
                refs = list(learning.get("artifact_refs") or [])
                if not refs:
                    raise cadence_ledger.CadenceLedgerError("legacy Dream has no resolvable artifacts")
                raw = {
                    "episode_id": f"legacy-{cadence_ledger.digest(handoff)[:20]}",
                    "series_id": "legacy-surviving-handoff", "created_at": now,
                    "workspace_id": "mira-core", "operator_id": "legacy-unknown",
                    "dream_date": datetime.fromisoformat(cadence_ledger.validate_timestamp(now)).date().isoformat(),
                    "timezone": "UTC", "coverage_status": "partial",
                    "session_coverage": [{"session_id": "legacy-survivor", "status": "unavailable", "reason": "Legacy migration cannot reconstruct complete daily session coverage.", "observed_at": now}],
                    "observation": learning.get("lesson") or learning.get("experiment"),
                    "diagnosis": "Historical cadence context before this surviving handoff is unavailable.",
                    "intervention": learning.get("method_change_candidate") or "Retain the legacy method candidate.",
                    "method_version_digest": cadence_ledger.digest(learning.get("method_change_candidate", "legacy")),
                    "profile": {"name": "legacy", "version": "3", "command_digest": "legacy"},
                    "observable": {"name": "legacy reported improvement", "unit": "legacy-report", "baseline": "unknown", "success_threshold": "requires later comparable use", "source": refs[0]},
                    "falsifier": "A later comparable use fails to reproduce the reported improvement.",
                    "next_use": learning.get("tomorrow_inherits") or "the next comparable task",
                    "task_class": "legacy-unspecified", "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                    "artifacts": [{"ref": ref, "relationship": "verification", "captured_at": now} for ref in refs],
                    "relevant_paths": refs, "evidence_summary": learning.get("evidence_summary") or "Legacy evidence summary unavailable.",
                    "tomorrow_inherits": learning.get("tomorrow_inherits") or "Reassess before inheritance.",
                    "verification": handoff.get("verification", {}), "measurements": handoff.get("measurement", {}),
                }
                connection = _ledger_connection(args, write=True)
                payload = cadence_ledger.create_episode(
                    connection, raw, idempotency_key=args.idempotency_key,
                    historical_completeness="latest-survivor-only",
                )
                connection.close()
        except (cadence_ledger.CadenceLedgerError, OSError, sqlite3.Error, json.JSONDecodeError) as error:
            raise SystemExit(str(error)) from error
        print(json.dumps(payload, indent=2))
        return

    if args.command == "profile":
        if args.action == "list":
            payload = {name: {"version": spec["version"], "timeout_seconds": spec["timeout_seconds"], "purpose": spec["purpose"]} for name, spec in EXPERIMENT_PROFILES.items()}
        else:
            if not args.name or args.name not in EXPERIMENT_PROFILES:
                raise SystemExit("profile name is required and must resolve")
            payload = {args.name: EXPERIMENT_PROFILES[args.name]}
        print(json.dumps(payload, indent=2) if getattr(args, "json", False) else json.dumps(payload, indent=2))
        return

    if args.command == "baseline":
        try:
            temp_root = resolve_temp_root(args.temp_root)
            payload = write_baseline(args.profile, temp_root=temp_root)
        except ValueError as error:
            raise SystemExit(str(error)) from error
        print(json.dumps(payload, indent=2) if args.json else f"baseline_written={BASELINE_ROOT.relative_to(REPO_ROOT).as_posix()}/{args.profile}.json")
        if not payload["passed"]:
            raise SystemExit(1)
        return

    if args.command == "promote":
        if args.episode_id:
            if args.idempotency_key is None or args.expected_version is None:
                raise SystemExit("ledger promotion requires --idempotency-key and --expected-version")
            try:
                connection = _ledger_connection(args, write=True)
                projection = cadence_ledger.project_episode(connection, args.episode_id)
                change = cadence_ledger.repository_change(projection)
                if change["status"] != "unchanged":
                    raise cadence_ledger.CadenceLedgerError("cadence episode relevant state changed; reconcile before promotion")
                temp_root = resolve_temp_root(args.temp_root)
                result = run_repository_validator(temp_root, force=args.force)
                payload = cadence_ledger.append_event(
                    connection, args.episode_id, "repository_promoted",
                    {"passed": result.get("passed") is True, "repository": result},
                    idempotency_key=args.idempotency_key, expected_version=args.expected_version,
                )
                connection.close()
            except (cadence_ledger.CadenceLedgerError, OSError, sqlite3.Error, ValueError) as error:
                raise SystemExit(str(error)) from error
            print(json.dumps(payload, indent=2) if args.json else f"promotion_status={result.get('status')}")
            if not result.get("passed"):
                raise SystemExit(1)
            return
        try:
            temp_root = resolve_temp_root(args.temp_root)
            payload = promote_dream(temp_root=temp_root, force=args.force)
        except ValueError as error:
            raise SystemExit(str(error)) from error
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            repository = payload["verification"]["repository"]
            print(f"promotion_status={repository['status']}")
            print(f"cache_status={repository.get('cache_status', 'unavailable')}")
            print(f"repo_use={payload['verification']['inheritance']['repo-use']}")
        if not verification_passed(payload["verification"]):
            raise SystemExit(1)
        return

    if args.db or os.environ.get(cadence_ledger.DB_ENV):
        try:
            payload = write_ledger_dream(args)
        except (cadence_ledger.CadenceLedgerError, OSError, sqlite3.Error, ValueError, json.JSONDecodeError) as error:
            raise SystemExit(str(error)) from error
        print(json.dumps(payload, indent=2) if args.json else f"dream_written={payload['episode']['episode_id']}")
        if args.profile and payload["lifecycle_state"] != "locally_verified":
            raise SystemExit(1)
        return

    measurement = json.loads(args.measurement_json) if args.measurement_json else None
    if measurement is not None and not isinstance(measurement, dict):
        raise SystemExit("--measurement-json must decode to an object")
    payload = write_dream(
        experiment=args.experiment,
        outcome=args.outcome,
        lesson=args.lesson,
        improvement=args.improvement,
        evidence_summary=args.evidence_summary,
        artifact_refs=args.artifact_ref,
        tomorrow_inherits=args.tomorrow_inherits,
        profile=args.profile,
        temp_root=args.temp_root,
        measurement=measurement,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        experiment_status = payload["verification"]["experiment"]["status"]
        print(f"dream_written={HANDOFF_PATH.relative_to(REPO_ROOT).as_posix()}")
        print(f"experiment_status={experiment_status}")
        print(f"local_use={payload['verification']['inheritance']['local-use']}")
        print("repo_use=blocked")
        print("next_mode=promote_or_continue_local_only")
    experiment = payload["verification"]["experiment"]
    if args.profile and not experiment.get("passed"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

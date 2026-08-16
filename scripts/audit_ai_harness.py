from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codex_skill_registry import (
    build_registry,
    discover_repo_skill_names,
    skill_mirror_state,
)
import validate_repository


REPO_ROOT = Path(__file__).resolve().parent.parent
RECEIPT_PATH = REPO_ROOT / "tmp" / "ai-harness" / "latest.json"
SCHEMA_VERSION = "1.0"
EVIDENCE_STATES = {"VERIFIED", "INFERRED", "INACCESSIBLE"}
ACTIONS = {"KEEP", "ONE_HOME", "LOAD_LATER", "MAKE_A_CHECK", "PROBATION", "RETIRE"}
STRICT_MIRROR_STATES = {"DRIFT", "MISSING_SOURCE", "MISSING_DEST"}
PRIVATE_PATH_RE = re.compile(r"(?:[A-Za-z]:[\\/]|/(?:Users|home)/[^/]+/)")

STATIONS = (
    ("already-there", "Already there"),
    ("chooses-help", "How Codex chooses help"),
    ("joins-job", "What joins this job"),
    ("can-do", "What Codex can do"),
    ("proves-done", "What proves the work is done"),
)


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def git_state() -> dict[str, Any]:
    rows = git_output("status", "--porcelain=v1").splitlines()
    return {
        "branch": git_output("branch", "--show-current") or "DETACHED",
        "head": git_output("rev-parse", "--short=12", "HEAD"),
        "tracked_changes": sum(not row.startswith("??") for row in rows),
        "untracked_entries": sum(row.startswith("??") for row in rows),
    }


def control(
    control_id: str,
    station: str,
    label: str,
    source_path: str,
    job: str,
    load_timing: str,
    enforcement: str,
    evidence_state: str,
    status: str,
    action: str,
    detail: str,
) -> dict[str, str]:
    if evidence_state not in EVIDENCE_STATES:
        raise ValueError(f"invalid evidence state: {evidence_state}")
    if action not in ACTIONS:
        raise ValueError(f"invalid action: {action}")
    return {
        "control_id": control_id,
        "station": station,
        "label": label,
        "source_path": source_path,
        "owner": "narrative-systems repository",
        "job": job,
        "load_timing": load_timing,
        "enforcement": enforcement,
        "evidence_state": evidence_state,
        "status": status,
        "action": action,
        "detail": detail,
    }


def skill_metadata_failures() -> list[str]:
    return validate_repository.skill_contract_failures()


def mirror_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for name, entry in sorted(build_registry().items()):
        state = skill_mirror_state(entry)
        records.append(
            {
                "name": name,
                "canonical_source": state.source_path,
                "installed": state.installed,
                "status": state.status,
                "action": "KEEP" if state.status == "IN_SYNC" else "ONE_HOME",
            }
        )
    return records


def build_controls(
    metadata_failures: list[str],
    repository_failures: list[str],
    mirrors: list[dict[str, Any]],
) -> list[dict[str, str]]:
    controls: list[dict[str, str]] = []
    controls.append(
        control(
            "project-instructions",
            "already-there",
            "Repository-local Codex instructions",
            "AGENTS.md",
            "Route local cadence and harness-audit phrases without becoming research evidence.",
            "Inherited with repository context",
            "Repository validation",
            "VERIFIED",
            "VALID" if not metadata_failures else "INVALID",
            "KEEP" if not metadata_failures else "MAKE_A_CHECK",
            "AGENTS.md is the canonical repository-local router.",
        )
    )
    for name in sorted(discover_repo_skill_names()):
        local = name in validate_repository.LOCAL_SKILLS
        controls.append(
            control(
                f"skill-route-{name}",
                "chooses-help",
                f"{name} route",
                f"docs/skill-drafts/{name}/SKILL.md",
                "Advertise a bounded job and distinguish it from neighboring skills.",
                "Catalog description before selection",
                "Frontmatter and allowlist checks",
                "VERIFIED",
                "LOCAL_ONLY" if local else "DEPLOYABLE",
                "KEEP",
                "Local-only skills route through AGENTS.md; deployable skills route through the registry.",
            )
        )
        controls.append(
            control(
                f"skill-body-{name}",
                "joins-job",
                f"{name} procedure",
                f"docs/skill-drafts/{name}/SKILL.md",
                "Provide specialist procedure only after the route is selected.",
                "After explicit or matching activation",
                "Skill contract",
                "INFERRED",
                "BOUNDED",
                "LOAD_LATER",
                "Keep the complete procedure behind selection rather than in standing instructions.",
            )
        )
    for item in mirrors:
        controls.append(
            control(
                f"skill-mirror-{item['name']}",
                "joins-job",
                f"Installed {item['name']} mirror",
                item["canonical_source"],
                "Mirror the canonical repository skill into the user-level Codex skill root.",
                "Available to Codex after synchronization",
                "Complete-directory byte comparison",
                "VERIFIED",
                item["status"],
                item["action"],
                "The repository draft is canonical; this audit never synchronizes the installed copy.",
            )
        )
    controls.append(
        control(
            "operator-capabilities",
            "can-do",
            "Repository operator commands",
            "scripts/",
            "Expose bounded intake, synthesis, verification, cadence, and validation actions.",
            "Only when invoked by the operator or a selected skill",
            "CLI argument and domain validation",
            "VERIFIED",
            "AVAILABLE",
            "KEEP",
            "The audit inventories the capability boundary without executing mutating commands.",
        )
    )
    controls.append(
        control(
            "archive-audit-benchmarks",
            "chooses-help",
            "Archive-audit benchmark advisory wiring",
            "scripts/archive_audit.py",
            "Expose read-only completeness, fullness, density, and warning-mix signals at archive and geo-strategy decision surfaces.",
            "Only when archive-audit, geo-strategy, or cadence asks for advisory state",
            "Targeted archive-audit, cadence, and harness tests",
            "VERIFIED",
            "AVAILABLE_READ_ONLY",
            "KEEP",
            "Harness confirms the capability boundary; it does not run a month archive audit.",
        )
    )
    controls.append(
        control(
            "repository-integrity",
            "proves-done",
            "Repository integrity validator",
            "scripts/validate_repository.py",
            "Enforce archive, routing, verification, publication, and skill invariants.",
            "Explicit completion check",
            "Deterministic Python validator",
            "VERIFIED",
            "PASS" if not repository_failures else "FAIL",
            "KEEP" if not repository_failures else "MAKE_A_CHECK",
            f"Observed {len(repository_failures)} repository integrity failure(s).",
        )
    )
    controls.append(
        control(
            "pytest-suite",
            "proves-done",
            "Python test suite",
            "tests/",
            "Exercise domain and repository behavior with reproducible tests.",
            "Explicit completion check",
            "pytest configuration in pyproject.toml",
            "VERIFIED",
            "CONFIGURED_NOT_RUN",
            "KEEP",
            "The harness audit reports the suite but does not run it automatically.",
        )
    )
    return controls


def reject_private_paths(payload: object) -> None:
    encoded = json.dumps(payload, ensure_ascii=False)
    match = PRIVATE_PATH_RE.search(encoded)
    if match:
        raise ValueError("audit output contains a private absolute path")


def build_audit() -> dict[str, Any]:
    metadata_failures = skill_metadata_failures()
    repository_failures = validate_repository.validate_repository()
    mirrors = mirror_records()
    controls = build_controls(metadata_failures, repository_failures, mirrors)
    action_counts = Counter(item["action"] for item in controls)
    strict_findings = list(metadata_failures) + list(repository_failures)
    strict_findings.extend(
        f"installed skill mirror {item['name']}: {item['status']}"
        for item in mirrors
        if item["status"] in STRICT_MIRROR_STATES
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "audit_mode": "READ_ONLY",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repository": ".",
        "git": git_state(),
        "summary": {
            "controls": len(controls),
            "strict_findings": len(strict_findings),
            "actions": {name: action_counts.get(name, 0) for name in sorted(ACTIONS)},
        },
        "stations": [
            {
                "station_id": station_id,
                "label": label,
                "controls": [item for item in controls if item["station"] == station_id],
            }
            for station_id, label in STATIONS
        ],
        "repository_check": {
            "status": "PASS" if not repository_failures else "FAIL",
            "failures": repository_failures,
        },
        "skill_mirrors": mirrors,
        "coverage_gaps": [
            {
                "area": "Exact model and reasoning settings",
                "evidence_state": "INACCESSIBLE",
                "detail": "Repository files cannot verify the client-selected model or effort.",
            },
            {
                "area": "Session permissions and tools",
                "evidence_state": "INACCESSIBLE",
                "detail": "Repository state does not prove the active sandbox, approvals, connectors, or tools.",
            },
            {
                "area": "What shaped a particular run",
                "evidence_state": "INACCESSIBLE",
                "detail": "File availability does not prove a skill was shown, consulted, or acted through.",
            },
        ],
        "strict_findings": strict_findings,
    }
    reject_private_paths(payload)
    return payload


def render_console(payload: dict[str, Any]) -> str:
    lines = [
        "Narrative Systems AI Harness Audit",
        "mode=READ_ONLY",
        f"repository_check={payload['repository_check']['status']}",
        f"strict_findings={payload['summary']['strict_findings']}",
        "",
    ]
    for station in payload["stations"]:
        lines.append(station["label"].upper())
        for item in station["controls"]:
            lines.append(
                f"- [{item['action']}] {item['label']} | {item['status']} | {item['source_path']}"
            )
        lines.append("")
    lines.append("WHAT THIS AUDIT COULD NOT SEE")
    for gap in payload["coverage_gaps"]:
        lines.append(f"- {gap['area']}: {gap['detail']}")
    if payload["strict_findings"]:
        lines.extend(("", "STRICT FINDINGS"))
        lines.extend(f"- {item}" for item in payload["strict_findings"])
    return "\n".join(lines) + "\n"


def write_receipt(payload: dict[str, Any]) -> None:
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    body = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(
        prefix=".latest.", suffix=".json", dir=RECEIPT_PATH.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, RECEIPT_PATH)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit the repository-native Codex harness without changing it."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of the human report.")
    parser.add_argument(
        "--write-receipt",
        action="store_true",
        help="Atomically write the same JSON to tmp/ai-harness/latest.json.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero for invalid repository controls or repo-owned skill mirror drift.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_audit()
    if args.write_receipt:
        write_receipt(payload)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_console(payload), end="")
        if args.write_receipt:
            print("receipt=tmp/ai-harness/latest.json")
    if args.strict and payload["strict_findings"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

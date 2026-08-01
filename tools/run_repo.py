from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ARGUMENTS_ENV = "NARRATIVE_RUN_ARGUMENTS_JSON"
ARGUMENTS_ENV_FLAG = "--arguments-env"
SURFACES = {
    "archive-audit": REPO_ROOT / "scripts" / "archive_audit.py",
    "archive-density": REPO_ROOT / "scripts" / "report_archive_density.py",
    "asr-repair": REPO_ROOT / "scripts" / "run_asr_repair_pilot.py",
    "cadence": REPO_ROOT / "scripts" / "cadence.py",
    "choice": REPO_ROOT / "scripts" / "choice_ledger.py",
    "continuity": REPO_ROOT / "scripts" / "continuity.py",
    "daily-validate": REPO_ROOT / "scripts" / "validate_daily_run.py",
    "elicitation": REPO_ROOT / "scripts" / "elicitation.py",
    "forecast-sync": REPO_ROOT / "scripts" / "sync_forecast_ledger.py",
    "forecast-triage": REPO_ROOT / "scripts" / "triage_forecast_ledger.py",
    "harness": REPO_ROOT / "scripts" / "audit_ai_harness.py",
    "intake-land": REPO_ROOT / "scripts" / "smart_intake.py",
    "intake-outcomes": REPO_ROOT / "scripts" / "report_intake_outcomes.py",
    "intake-stats": REPO_ROOT / "scripts" / "report_trim_stats.py",
    "issue-render": REPO_ROOT / "scripts" / "render_daily_issue.py",
    "narrative-reuse": REPO_ROOT / "scripts" / "report_narrative_reuse.py",
    "operator-position": REPO_ROOT / "scripts" / "operator_positions.py",
    "reality": REPO_ROOT / "scripts" / "reality.py",
    "skills-check": REPO_ROOT / "scripts" / "check_codex_skills_sync.py",
    "skills-sync": REPO_ROOT / "scripts" / "sync_codex_skills.py",
    "synthesis": REPO_ROOT / "scripts" / "geopolitical_synthesis.py",
    "verification": REPO_ROOT / "scripts" / "verification.py",
    "voice-accountability": REPO_ROOT / "scripts" / "voice_accountability.py",
    "voice-canonicalize": REPO_ROOT / "scripts" / "canonicalize_voice_metadata.py",
    "voice-sync": REPO_ROOT / "scripts" / "sync_voice_indexes.py",
    "voice-comparison": REPO_ROOT / "scripts" / "voice_comparison.py",
}


def resolve_arguments(
    arguments: list[str] | None = None,
    environment: dict[str, str] | os._Environ[str] | None = None,
) -> list[str]:
    values = list(sys.argv[1:] if arguments is None else arguments)
    if ARGUMENTS_ENV_FLAG not in values:
        return values
    if values != [ARGUMENTS_ENV_FLAG]:
        raise ValueError(f"{ARGUMENTS_ENV_FLAG} must be the only command-line argument")
    source = os.environ if environment is None else environment
    raw = source.pop(ARGUMENTS_ENV, None)
    if raw is None:
        raise ValueError(f"{ARGUMENTS_ENV_FLAG} requires {ARGUMENTS_ENV}")
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"{ARGUMENTS_ENV} is not valid JSON") from error
    if not isinstance(decoded, list) or any(
        not isinstance(item, str) for item in decoded
    ):
        raise ValueError(f"{ARGUMENTS_ENV} must contain a JSON array of strings")
    return decoded


def main(arguments: list[str] | None = None) -> int:
    try:
        values = resolve_arguments(arguments)
    except ValueError as error:
        print(f"argument transport error: {error}", file=sys.stderr)
        return 2
    if not values or values[0] not in SURFACES:
        allowed = ", ".join(sorted(SURFACES))
        print(f"usage: run_repo.py <{allowed}> [arguments...]", file=sys.stderr)
        return 2
    surface, *forwarded = values
    environment = os.environ.copy()
    environment.pop(ARGUMENTS_ENV, None)
    scripts = str(REPO_ROOT / "scripts")
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = scripts if not existing else os.pathsep.join((scripts, existing))
    result = subprocess.run(
        [sys.executable, str(SURFACES[surface]), *forwarded],
        cwd=REPO_ROOT,
        env=environment,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

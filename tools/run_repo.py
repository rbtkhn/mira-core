from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from runtime_names import (  # noqa: E402
    EnvironmentNameConflict,
    pop_environment,
    remove_environment_pair,
)

ARGUMENTS_ENV = "MIRA_CORE_RUN_ARGUMENTS_JSON"
ARGUMENTS_ENV_FLAG = "--arguments-env"
SURFACES = {
    "archive-audit": REPO_ROOT / "scripts" / "archive_audit.py",
    "archive-density": REPO_ROOT / "scripts" / "report_archive_density.py",
    "archive-repair": REPO_ROOT / "scripts" / "archive_repair.py",
    "archive": REPO_ROOT / "scripts" / "archive.py",
    "asr-repair": REPO_ROOT / "scripts" / "run_asr_repair_pilot.py",
    "cadence": REPO_ROOT / "scripts" / "cadence.py",
    "choice": REPO_ROOT / "scripts" / "choice_ledger.py",
    "continuity": REPO_ROOT / "scripts" / "continuity.py",
    "contradiction-check": REPO_ROOT / "scripts" / "contradiction_check.py",
    "daily-validate": REPO_ROOT / "scripts" / "validate_daily_run.py",
    "dream": REPO_ROOT / "scripts" / "dream_eod.py",
    "elicitation": REPO_ROOT / "scripts" / "elicitation.py",
    "forecast-sync": REPO_ROOT / "scripts" / "sync_forecast_ledger.py",
    "forecast-triage": REPO_ROOT / "scripts" / "triage_forecast_ledger.py",
    "harness": REPO_ROOT / "scripts" / "audit_ai_harness.py",
    "intake-land": REPO_ROOT / "scripts" / "smart_intake.py",
    "intake-outcomes": REPO_ROOT / "scripts" / "report_intake_outcomes.py",
    "intake-stats": REPO_ROOT / "scripts" / "report_trim_stats.py",
    "library": REPO_ROOT / "scripts" / "archive_library.py",
    "innermost-loop-simulation": REPO_ROOT / "scripts" / "innermost_loop_simulation.py",
    "issue-render": REPO_ROOT / "scripts" / "render_daily_issue.py",
    "morning-brief": REPO_ROOT / "scripts" / "morning_brief.py",
    "mira-continuity": REPO_ROOT / "scripts" / "mira_continuity.py",
    "mira-constitution": REPO_ROOT / "scripts" / "mira_constitution.py",
    "mira-journal": REPO_ROOT / "scripts" / "mira_journal.py",
    "mira-memory": REPO_ROOT / "scripts" / "mira_memory.py",
    "mira-sessions": REPO_ROOT / "scripts" / "mira_sessions.py",
    "mechanism-lens-checklist": REPO_ROOT / "scripts" / "mechanism_lens_checklist.py",
    "mira-mentor": REPO_ROOT / "scripts" / "mentorship_ledger.py",
    "mira-work": REPO_ROOT / "scripts" / "mira_work_receipt.py",
    "narrative-reuse": REPO_ROOT / "scripts" / "report_narrative_reuse.py",
    "operator-position": REPO_ROOT / "scripts" / "operator_positions.py",
    "portability": REPO_ROOT / "tools" / "mira_portable.py",
    "publication-status": REPO_ROOT / "scripts" / "publication_status.py",
    "publication-validation": REPO_ROOT / "scripts" / "publication_validation.py",
    "reality": REPO_ROOT / "scripts" / "reality.py",
    "reality-handoff": REPO_ROOT / "scripts" / "reality_handoff.py",
    "recursive-learn": REPO_ROOT / "scripts" / "recursive_learning_ledger.py",
    "research-handoff": REPO_ROOT / "scripts" / "research_handoff.py",
    "runtime-bootstrap": REPO_ROOT / "scripts" / "runtime_bootstrap.py",
    "rest": REPO_ROOT / "scripts" / "rest.py",
    "session-preflight": REPO_ROOT / "scripts" / "session_preflight.py",
    "skills-check": REPO_ROOT / "scripts" / "check_codex_skills_sync.py",
    "skills-sync": REPO_ROOT / "scripts" / "sync_codex_skills.py",
    "skill-ablation": REPO_ROOT / "scripts" / "skill_ablation.py",
    "source-topic-scan": REPO_ROOT / "scripts" / "source_topic_scan.py",
    "synthesis": REPO_ROOT / "scripts" / "geopolitical_synthesis.py",
    "system-archive": REPO_ROOT / "scripts" / "system_archive.py",
    "test": REPO_ROOT / "tools" / "validate_repo.py",
    "triangulation-candidates": REPO_ROOT / "scripts" / "triangulation_candidates.py",
    "validated-push": REPO_ROOT / "scripts" / "validated_push.py",
    "verification": REPO_ROOT / "scripts" / "verification.py",
    "voice-accountability": REPO_ROOT / "scripts" / "voice_accountability.py",
    "voice-judgment": REPO_ROOT / "scripts" / "voice_judgments.py",
    "voice-canonicalize": REPO_ROOT / "scripts" / "canonicalize_voice_metadata.py",
    "voice-sync": REPO_ROOT / "scripts" / "sync_voice_indexes.py",
    "voice-comparison": REPO_ROOT / "scripts" / "voice_comparison.py",
    "youtube-capture": REPO_ROOT / "scripts" / "youtube_capture.py",
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
    raw = pop_environment(ARGUMENTS_ENV, source)
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
    except (ValueError, EnvironmentNameConflict) as error:
        print(f"argument transport error: {error}", file=sys.stderr)
        return 2
    if not values or values[0] not in SURFACES:
        allowed = ", ".join(sorted(SURFACES))
        print(f"usage: run_repo.py <{allowed}> [arguments...]", file=sys.stderr)
        return 2
    surface, *forwarded = values
    environment = os.environ.copy()
    remove_environment_pair(ARGUMENTS_ENV, environment)
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

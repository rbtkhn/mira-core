from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, TextIO

SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from codex_skill_registry import (
    DEPLOYABLE_SKILL_NAMES,
    SKILL_DRAFT_ROOT,
    discover_repo_skill_names,
    parse_skill_frontmatter,
)
import voice_indexes
import voice_metadata
import voice_accountability
import voice_judgments
import forecast_ledger
import verification as verification_packets
import render_daily_issue as daily_issue
import reality
import recursive_learning_ledger
import mira_continuity
import mira_journal
import operator_positions
import system_archive
from role_aware_archive import validate_row as validate_role_row


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
ARCHIVE_SOURCES = NG_ROOT / "archive" / "sources"
MANIFEST_PATH = NG_ROOT / "archive" / "source-manifest.json"
DAILY_ROOT = NG_ROOT / "work" / "daily"
LEDGER_PATH = NG_ROOT / "work" / "forecasts" / "forecast-ledger.md"
LOCAL_SKILLS = {
    "archive-audit",
    "archive-query",
    "archive-repair",
    "coffee",
    "dream",
    "morning-brief",
    "research-brief",
    "world-monitor",
}
LOCAL_ROUTER_PATH = REPO_ROOT / "AGENTS.md"
REQUIRED_DAILY_FILES = {"sources.md", "synthesis.md", "forecast.md", "judgment.md", "daily-brief.md"}
PUBLIC_BRIEFS_ROOT = NG_ROOT / "public" / "briefs"
ACTIVE_ASR_GUIDANCE = NG_ROOT / "work" / "asr-repair-pilot-findings-july-2026.md"
LEGACY_VERIFICATION_ROOT = NG_ROOT / "work" / "verification" / "packets"
LEGACY_VERIFICATION_INVENTORY = NG_ROOT / "work" / "verification" / "legacy-inventory.json"
MODEL_SUBSTITUTION_GATE = REPO_ROOT / "docs" / "model-substitution-readiness.md"

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HOOK_ID_RE = re.compile(r"`(NG-\d{8}-F\d{2})`")
H1_RE = re.compile(r"^# (?P<title>.+?)\s*$", re.MULTILINE)
TITLE_RATIONALE_RE = re.compile(r"^Title rationale:\s*`?(?P<value>.+?)`?\s*$", re.MULTILINE)
ADMIN_TITLE_RE = re.compile(
    r"^(?:untitled|draft|analysis|essay|report|notes?|daily brief|working paper)(?:\s*[:—-].*)?$",
    re.IGNORECASE,
)
PLACEHOLDER_TITLE_RE = re.compile(r"\[[^\]]+\]|<[^>]+>|YYYY(?:-MM-DD)?", re.IGNORECASE)
OPERATIONAL_STATUS_RE = re.compile(r"^Operational status:\s*`operationally_supported`\s*$", re.MULTILINE)
VERIFICATION_LINK_RE = re.compile(r"^Verification packet:\s*\[(VER-\d{8}-\d{2})\]\(([^)]+)\)\s*$", re.MULTILINE)
GENERIC_READER_HEADING_RE = re.compile(
    r"^##\s+(?:background|analysis|discussion|conclusion|what happens next)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
OBSOLETE_GUIDANCE_PATTERNS = (
    ("deprecated scripts/python.ps1 command", re.compile(r"scripts[\\/]python\.ps1", re.IGNORECASE)),
    ("repo-local virtual-environment interpreter", re.compile(r"\.venv[\\/]Scripts[\\/]python\.exe", re.IGNORECASE)),
    ("manual virtual-environment creation", re.compile(r"\bpy\s+-3(?:\.\d+)?\s+-m\s+venv\b", re.IGNORECASE)),
    ("direct pytest command", re.compile(r"\bpython(?:3(?:\.\d+)?)?\s+-m\s+pytest\b", re.IGNORECASE)),
    (
        "direct repository script command",
        re.compile(
            r"\b(?:python(?:3(?:\.\d+)?)?|py(?:\s+-3(?:\.\d+)?)?)\s+[^\n`]*scripts[\\/][\w.-]+\.py\b",
            re.IGNORECASE,
        ),
    ),
    (
        "machine-specific user path",
        re.compile(r"(?:[A-Za-z]:[\\/]Users[\\/][^\\/\s`]+|/(?:Users|home)/[^/\s`]+/)", re.IGNORECASE),
    ),
)

MODEL_SUBSTITUTION_HEADINGS = (
    "## When to use it",
    "## Operating rule",
    "## Evaluation dimensions",
    "## Core questions",
    "## Status guidance",
    "## Output shape",
    "## Integration with existing controls",
    "## Boundary statement",
    "## First bounded internal test",
)
MODEL_SUBSTITUTION_STATUSES = ("ready", "review-required", "hold", "blocked")
MODEL_SUBSTITUTION_DIMENSIONS = (
    "Task fit",
    "Provenance and rights",
    "Security",
    "Data boundary",
    "Tool and action authority",
    "Human authority",
    "Economics",
    "Reversibility",
    "Evidence quality",
)
MODEL_SUBSTITUTION_FIELDS = (
    "Workflow:",
    "Current model:",
    "Candidate model:",
    "Task and failure modes:",
    "Evaluation evidence:",
    "Provenance / rights status:",
    "Security and data boundary:",
    "Changed tool or action authority:",
    "Human owner and approval point:",
    "Override / rollback path:",
    "Total cost and review burden:",
    "Default state: review-required",
    "Unresolved risk:",
    "Next review trigger:",
    "What remains internal:",
)
MODEL_SUBSTITUTION_TEST_ELEMENTS = (
    "freeze and hash one task-set",
    "known failure",
    "quality",
    "latency",
    "total cost",
    "review burden",
    "provenance and rights review",
    "data-boundary review",
    "tool and action authority",
    "restore the current model",
)


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def archive_manifest_failures() -> list[str]:
    manifest = load_manifest()
    rows = manifest.get("sources", [])
    row_paths = [row.get("local_path", "") for row in rows]
    file_paths = sorted(relative(path) for path in ARCHIVE_SOURCES.rglob("*.md"))
    failures: list[str] = []

    if manifest.get("source_count") != len(rows):
        failures.append(
            f"manifest source_count={manifest.get('source_count')} but rows={len(rows)}"
        )
    for row in rows:
        if any(key in row for key in ("voice_roles", "role_status", "role_basis", "host_kind", "publication_slug")):
            failures.extend(
                f"role metadata: {row.get('local_path')}: {item}"
                for item in validate_role_row(row)
            )
    if len(row_paths) != len(set(row_paths)):
        failures.append("manifest contains duplicate local_path rows")
    if sorted(row_paths) != file_paths:
        missing = sorted(set(row_paths) - set(file_paths))
        extra = sorted(set(file_paths) - set(row_paths))
        failures.extend(f"manifest path missing file: {path}" for path in missing)
        failures.extend(f"archive file missing manifest row: {path}" for path in extra)
    return failures


def daily_run_failures() -> list[str]:
    manifest = load_manifest()
    dates = {row.get("date") for row in manifest.get("sources", [])}
    failures: list[str] = []
    for run_dir in sorted(path for path in DAILY_ROOT.iterdir() if path.is_dir()):
        files = {path.name for path in run_dir.iterdir() if path.is_file()}
        if not files:
            failures.append(f"empty daily directory: {relative(run_dir)}")
            continue
        if run_dir.name not in dates:
            failures.append(f"daily directory has no manifest rows: {relative(run_dir)}")
        missing = REQUIRED_DAILY_FILES - files
        failures.extend(
            f"daily run missing {name}: {relative(run_dir)}" for name in sorted(missing)
        )
        if "geopolitical-synthesis-session.json" in files:
            failures.append(f"tracked session receipt: {relative(run_dir)}")
        sources_path = run_dir / "sources.md"
        if sources_path.exists() and "awaiting intake" in sources_path.read_text(
            encoding="utf-8"
        ).lower():
            failures.append(f"placeholder daily run: {relative(run_dir)}")
        if "issue.md" in files:
            issue_failures, _ = daily_issue.validate_issue(
                run_dir.name,
                daily_root=DAILY_ROOT,
                ledger_path=LEDGER_PATH,
            )
            failures.extend(
                f"daily issue invalid: {relative(run_dir / 'issue.md')} -> {item}"
                for item in issue_failures
            )
    return failures


def forecast_ledger_failures() -> list[str]:
    text = LEDGER_PATH.read_text(encoding="utf-8")
    if forecast_ledger.TRIAGE_HEADING not in text:
        return ["forecast ledger missing Accountability Triage section"]
    failures = forecast_ledger.structural_failures(
        forecast_ledger.parse_entries(text), forecast_ledger.parse_triage(text)
    )
    return [
        item.replace("missing triage row:", "forecast entry missing triage row:")
        .replace("triage row has no ledger entry:", "forecast triage row missing entry:")
        for item in failures
    ]


def markdown_files() -> list[Path]:
    roots = (
        REPO_ROOT / "docs",
        NG_ROOT,
        REPO_ROOT / "predictive-history",
        REPO_ROOT / "historical-entropy",
    )
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            if ARCHIVE_SOURCES in path.parents:
                continue
            files.append(path)
    return sorted(files)


def markdown_link_failures() -> list[str]:
    failures: list[str] = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            raw_target = match.group(1).strip().strip("<>")
            target = raw_target.split("#", 1)[0]
            # Thesis reports append a source line locator as `:N`; it is not
            # part of the filesystem target.
            target = re.sub(r":\d+$", "", target)
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = path.parent / target
            if not resolved.exists() and target.replace("\\", "/").startswith("narrative-geopolitics/"):
                resolved = REPO_ROOT / target.replace("/", "\\")
            if not resolved.exists():
                failures.append(f"broken Markdown link: {relative(path)} -> {raw_target}")
    return failures


def model_substitution_gate_failures(
    path: Path = MODEL_SUBSTITUTION_GATE,
) -> list[str]:
    if not path.is_file():
        return ["model substitution readiness gate is missing"]
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for heading in MODEL_SUBSTITUTION_HEADINGS:
        if heading not in text:
            failures.append(f"model substitution gate missing section: {heading}")
    for status in MODEL_SUBSTITUTION_STATUSES:
        if f"`{status}`" not in text:
            failures.append(f"model substitution gate missing status: {status}")
    for dimension in MODEL_SUBSTITUTION_DIMENSIONS:
        if f"| {dimension} |" not in text:
            failures.append(f"model substitution gate missing dimension: {dimension}")
    for field in MODEL_SUBSTITUTION_FIELDS:
        if field not in text:
            failures.append(f"model substitution gate missing output field: {field}")
    first_test = " ".join(
        text.partition("## First bounded internal test")[2].lower().split()
    )
    for element in MODEL_SUBSTITUTION_TEST_ELEMENTS:
        if element not in first_test:
            failures.append(f"model substitution gate first test missing: {element}")
    if "Default state: `review-required`" not in text:
        failures.append("model substitution gate default must be review-required")
    return failures


def reader_facing_title_files() -> list[Path]:
    candidates: set[Path] = set()
    if PUBLIC_BRIEFS_ROOT.exists():
        candidates.update(PUBLIC_BRIEFS_ROOT.rglob("*.md"))
    for path in markdown_files():
        if (NG_ROOT / "templates") in path.parents:
            continue
        text = path.read_text(encoding="utf-8")
        # Unpromoted daily scaffolds are working documents, not reader-facing
        # publications; their placeholder title is intentionally allowed.
        if path.parent.parent == NG_ROOT / "work" / "daily" and "Status: `not-promoted`" in text[:400]:
            continue
        if "Title standard: `reader-facing`" in text:
            candidates.add(path)
    return sorted(candidates)


def editorial_title_failures() -> list[str]:
    failures: list[str] = []
    for path in reader_facing_title_files():
        text = path.read_text(encoding="utf-8")
        opening = "\n".join(text.splitlines()[:16])
        headings = H1_RE.findall(text)
        label = relative(path)
        if len(headings) != 1:
            failures.append(f"reader-facing document must have exactly one H1: {label}")
            continue
        title = headings[0].strip()
        if "Title standard: `reader-facing`" not in opening:
            failures.append(f"reader-facing document missing title-standard marker: {label}")
        rationale = TITLE_RATIONALE_RE.search(opening)
        if not rationale or len(rationale.group("value").strip(" `").split()) < 8:
            failures.append(f"reader-facing document missing substantive title rationale: {label}")
        if ADMIN_TITLE_RE.fullmatch(title):
            failures.append(f"reader-facing document uses administrative title: {label} -> {title}")
        if PLACEHOLDER_TITLE_RE.search(title):
            failures.append(f"reader-facing document uses placeholder title: {label} -> {title}")
        if len(title.split()) < 4:
            failures.append(f"reader-facing title is too thin to express a distinction: {label} -> {title}")
        for match in GENERIC_READER_HEADING_RE.finditer(text):
            heading = match.group(0).removeprefix("##").strip()
            failures.append(f"reader-facing document uses generic analytical heading: {label} -> {heading}")
    return failures


def operational_claim_failures() -> list[str]:
    failures: list[str] = []
    for path in markdown_files():
        if verification_packets.VERIFICATION_ROOT in path.parents:
            continue
        text = path.read_text(encoding="utf-8")
        if not OPERATIONAL_STATUS_RE.search(text):
            continue
        match = VERIFICATION_LINK_RE.search(text)
        label = relative(path)
        if not match:
            failures.append(f"operationally supported claim missing verification packet: {label}")
            continue
        packet_id, raw_link = match.groups()
        target = (path.parent / raw_link).resolve()
        if not target.exists():
            failures.append(f"operational verification link does not resolve: {label} -> {raw_link}")
            continue
        packet = verification_packets.parse_packet(target)
        if packet.packet_id != packet_id:
            failures.append(f"operational verification ID/link mismatch: {label} -> {packet_id}")
        if packet.fields.get("status") not in {"assessed", "closed"}:
            failures.append(f"operational verification packet is not assessed: {label} -> {packet_id}")
        if packet.fields.get("assessment_outcome") != "operationally_supported":
            failures.append(f"operational verification outcome is not supporting: {label} -> {packet_id}")
    return failures


def verification_packet_failures() -> list[str]:
    return verification_packets.validate_all()


def reality_lattice_failures() -> list[str]:
    return reality.validate_all()


def skill_contract_failures() -> list[str]:
    failures: list[str] = []
    deployable = set(DEPLOYABLE_SKILL_NAMES)
    if deployable != {
        "archive-intake",
        "best-intake",
        "elicitation",
        "learn-from-choices",
        "smart-intake",
        "voice-comparison",
        "geopolitical-synthesis",
        "reality-check",
        "voice-accountability",
    }:
        failures.append(f"unexpected deployable skill allowlist: {sorted(deployable)}")
    repo_skills = set(discover_repo_skill_names())
    if not LOCAL_SKILLS <= repo_skills:
        failures.append("repository-local skill drafts are missing")
    if deployable & LOCAL_SKILLS:
        failures.append("repository-local skills must not be globally deployable")
    if not LOCAL_ROUTER_PATH.exists():
        failures.append("repository-local skill trigger router is missing")
    else:
        router = LOCAL_ROUTER_PATH.read_text(encoding="utf-8")
        for name in sorted(LOCAL_SKILLS):
            expected = f"docs/skill-drafts/{name}/SKILL.md"
            if expected not in router:
                failures.append(f"local cadence trigger missing route: {expected}")
    governed = deployable | LOCAL_SKILLS
    if repo_skills != governed:
        failures.append(
            f"repo skill drafts differ from governed set: expected={sorted(governed)} actual={sorted(repo_skills)}"
        )
    if deployable & LOCAL_SKILLS:
        failures.append("deployable and local-only skill sets overlap")
    router = LOCAL_ROUTER_PATH.read_text(encoding="utf-8") if LOCAL_ROUTER_PATH.exists() else ""
    if "harness audit" not in router or "tools/run.ps1 harness" not in router:
        failures.append("repository-local harness audit route is missing")
    for name in sorted(repo_skills):
        path = SKILL_DRAFT_ROOT / name / "SKILL.md"
        metadata = parse_skill_frontmatter(path)
        label = relative(path)
        if metadata.get("name") != name:
            failures.append(f"skill frontmatter name does not match directory: {label}")
        if not metadata.get("description"):
            failures.append(f"skill frontmatter description is missing: {label}")
    for name in sorted(deployable):
        if not (SKILL_DRAFT_ROOT / name / "SKILL.md").exists():
            failures.append(f"deployable skill missing canonical source: {name}")
    return failures


def skill_sync_failures() -> list[str]:
    """Compatibility name for callers that predate the broader contract check."""
    return skill_contract_failures()


def tracked_artifact_failures() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked = set(result.stdout.splitlines())
    forbidden = {
        "narrative-geopolitics/work/cadence/last-dream.json",
    }
    return [f"tracked derived cadence artifact: {path}" for path in sorted(forbidden & tracked)]


def active_guidance_files(repo_root: Path = REPO_ROOT) -> list[Path]:
    ng_root = repo_root / "narrative-geopolitics"
    files = {repo_root / "README.md", repo_root / "AGENTS.md"}
    for root in (
        repo_root / "docs",
        ng_root / "method",
        ng_root / "templates",
    ):
        if root.exists():
            files.update(root.rglob("*.md"))
    work_root = ng_root / "work"
    if work_root.exists():
        files.update(
            path
            for path in work_root.rglob("README.md")
            if not any(
                territory in path.relative_to(work_root).parts
                for territory in ("daily", "audits")
            )
        )
    asr_guidance = ng_root / "work" / "asr-repair-pilot-findings-july-2026.md"
    if asr_guidance.exists():
        files.add(asr_guidance)
    return sorted(path for path in files if path.is_file())


def obsolete_guidance_failures(
    paths: list[Path] | None = None,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    failures: list[str] = []
    for path in paths if paths is not None else active_guidance_files(repo_root):
        text = path.read_text(encoding="utf-8")
        try:
            label = path.relative_to(repo_root).as_posix()
        except ValueError:
            label = path.as_posix()
        for line_number, line in enumerate(text.splitlines(), start=1):
            for description, pattern in OBSOLETE_GUIDANCE_PATTERNS:
                if pattern.search(line):
                    failures.append(
                        f"obsolete active guidance ({description}): {label}:{line_number}"
                    )
    return failures


def voice_routing_failures() -> list[str]:
    manifest = load_manifest()
    failures = voice_metadata.metadata_failures(manifest, REPO_ROOT)
    failures.extend(
        voice_indexes.reconcile(
            manifest,
            write=False,
            repo_root=REPO_ROOT,
            voices_root=NG_ROOT / "voices",
        )["failures"]
    )
    return sorted(set(failures))


def voice_accountability_failures() -> list[str]:
    return voice_accountability.validate_ledger()


def voice_judgment_failures() -> list[str]:
    failures = voice_judgments.validate_registry()
    if not failures:
        for path, expected in voice_judgments.expected_outputs().items():
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                failures.append(
                    f"voice judgment generated view drift: {relative(path)}"
                )
    return failures


def legacy_verification_inventory_failures() -> list[str]:
    if not LEGACY_VERIFICATION_INVENTORY.is_file():
        return ["legacy verification inventory missing"]
    try:
        payload = json.loads(LEGACY_VERIFICATION_INVENTORY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"legacy verification inventory invalid JSON: line {exc.lineno}"]
    rows = payload.get("packets")
    if not isinstance(rows, list):
        return ["legacy verification inventory missing packets list"]
    failures: list[str] = []
    registered: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            failures.append("legacy verification inventory contains non-object row")
            continue
        path = str(row.get("path", ""))
        packet_id = str(row.get("packet_id", ""))
        condition = str(row.get("retirement_condition", "")).strip()
        if not path or not packet_id or not condition:
            failures.append(f"incomplete legacy verification inventory row: {packet_id or path}")
            continue
        if path in registered:
            failures.append(f"duplicate legacy verification inventory path: {path}")
        registered.add(path)
        target = REPO_ROOT / path
        if not target.is_dir() or target.name != packet_id:
            failures.append(f"legacy verification inventory target mismatch: {path}")
    actual = {
        relative(path)
        for path in LEGACY_VERIFICATION_ROOT.iterdir()
        if path.is_dir()
    }
    failures.extend(
        f"unregistered legacy-only verification packet: {path}"
        for path in sorted(actual - registered)
    )
    failures.extend(
        f"registered legacy verification packet missing: {path}"
        for path in sorted(registered - actual)
    )
    return failures


REPOSITORY_CHECKS = (
    ("archive_manifest_failures", archive_manifest_failures),
    ("daily_run_failures", daily_run_failures),
    ("forecast_ledger_failures", forecast_ledger_failures),
    ("markdown_link_failures", markdown_link_failures),
    ("model_substitution_gate_failures", model_substitution_gate_failures),
    ("editorial_title_failures", editorial_title_failures),
    ("operational_claim_failures", operational_claim_failures),
    ("verification_packet_failures", verification_packet_failures),
    ("reality_lattice_failures", reality_lattice_failures),
    ("skill_contract_failures", skill_contract_failures),
    ("voice_accountability_failures", voice_accountability_failures),
    ("voice_judgment_failures", voice_judgment_failures),
    ("recursive_learning_ledger.validate_ledger", recursive_learning_ledger.validate_ledger),
    ("mira_continuity.validate_repository_state", mira_continuity.validate_repository_state),
    ("mira_journal.validate_repository_state", mira_journal.validate_repository_state),
    ("system_archive.validate_repository_state", system_archive.validate_repository_state),
    ("operator_positions.validate_ledger", operator_positions.validate_ledger),
    ("legacy_verification_inventory_failures", legacy_verification_inventory_failures),
    ("tracked_artifact_failures", tracked_artifact_failures),
    ("obsolete_guidance_failures", obsolete_guidance_failures),
    ("voice_routing_failures", voice_routing_failures),
)


def validate_repository(
    *,
    checks: tuple[tuple[str, Callable[[], list[str]]], ...] | None = None,
    clock: Callable[[], float] | None = None,
    timing_stream: TextIO | None = None,
) -> list[str]:
    selected_checks = REPOSITORY_CHECKS if checks is None else checks
    monotonic = time.perf_counter if clock is None else clock
    stream = sys.stderr if timing_stream is None else timing_stream
    failures: list[str] = []
    for name, check in selected_checks:
        started = monotonic()
        try:
            check_failures = check()
        except BaseException:
            print(
                " ".join((
                    "validation_check",
                    f"name={name}",
                    f"seconds={max(0.0, monotonic() - started):.3f}",
                    "status=failed",
                    "failures=0",
                )),
                file=stream,
            )
            raise
        print(
            " ".join((
                "validation_check",
                f"name={name}",
                f"seconds={max(0.0, monotonic() - started):.3f}",
                f"status={'passed' if not check_failures else 'failed'}",
                f"failures={len(check_failures)}",
            )),
            file=stream,
        )
        failures.extend(check_failures)
    return failures


def main() -> None:
    failures = validate_repository()
    print(f"repository_integrity_failures={len(failures)}")
    for item in failures:
        print(f"FAIL {item}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

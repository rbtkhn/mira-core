from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
GLOB_TOKENS = "*?["
RETIRED_PROJECT_PATHS = frozenset(['projects/grace-gems/README.md', 'projects/grace-gems/admission-matrix.md', 'projects/ottoman-rugs/README.md', 'projects/lab/README.md', 'projects/media-production/README.md'])
MANUAL_PROJECT_RECONCILIATION_CHECK = (
    "Verify exact retired-path removal and preserved starting bytes; retain project owners, "
    "repair active navigation, and do not admit privately preserved material."
)

MANUAL_NOTE_CHECK = (
    "Validate note lifecycle/status, privacy, provenance, authority effect, and "
    "absence of credentials or restricted source bodies through mira-notes."
)
MANUAL_LETTER_CHECK = (
    "Validate letter sender, recipients, lifecycle/status, unsent or delivery disposition, "
    "privacy, provenance, attribution, links, version chain, authority effect, and "
    "absence of credentials or restricted source bodies through mira-letters. "
    "Repository staging or commit does not authorize sending or external commitments."
)
MANUAL_LIBRARY_COGNITIVE_NOTE_CHECK = (
    "Validate Library cognitive-note authorship, template order, admitted-body dependency "
    "snapshot, explicit work relationships, lineage, integration stage, and absence of "
    "inferred prose edges or automatic note creation through library-integration."
)
MANUAL_ESSAY_CHECK = (
    "Validate essay privacy, evidence boundaries, provenance, links, detached-title "
    "accuracy, and Markdown integrity through mira-essays."
)
MANUAL_SESSION_MEMORIAL_CHECK = (
    "Validate the memorial pair, exact Continuity lineage, paraphrase-only privacy, "
    "manual privacy receipt, inactive posture, attribution, omissions, and version chain through mira-sessions."
)
MANUAL_MIRA_JOURNAL_CHECK = (
    "Validate Mira Journal registry digest binding, approved status, technical "
    "reference integrity, continuity-index coherence, privacy boundary, and "
    "absence of research-evidence or publication-authority promotion."
)
MANUAL_WORK_JOURNAL_CHECK = (
    "Validate Work Journal source-linked decisions, temporal accuracy, attribution, "
    "privacy, separation of completion from effectiveness, unresolved obligations, "
    "authority effect none, and preservation of owning records and historical references."
)
MANUAL_GRACE_GEMS_CHECK = (
    "Validate Grace Gems provenance, privacy exclusions, stewardship-versus-ownership "
    "boundaries, CEO authority, and absence of copied upstream or private evidence."
)
MANUAL_GRACE_MAR_CHECK = (
    "Validate the Grace Mar README as sanitized local orientation: attributed "
    "provenance, no copied upstream or private evidence, no inferred legal formation "
    "or asset ownership, no resumed approval or active-business claim, and preserved "
    "project-owner authority. Verify links against the exact admission candidate; "
    "other Grace Mar files are not covered by this route."
)
MANUAL_OTTOMAN_RUGS_CHECK = (
    "Validate Ottoman Rugs orientation against dated, attributed sources: keep "
    "supplier evidence private, requested terms separate from agreed terms, "
    "product facts and image rights unverified unless supported, and private "
    "preview distinct from operating storefront. Preserve human approval and "
    "launch boundaries; no neighboring files are covered."
)
MANUAL_PROJECT_ORIENTATION_CHECK = (
    "Review the complete exact project orientation, including pre-existing content: "
    "verify source attribution, privacy, owner authority, and prepared-versus-executed "
    "pilot status. Classify local-only/private references separately from publishable "
    "control dependencies; never admit a linked body merely to satisfy a link. "
    "A navigation repair does not admit earlier project work or neighboring files."
)
MANUAL_MOUNTAIN_VILLA_CHECK = (
    "Review Mountain Villa source attribution, privacy exclusions, and owner/professional "
    "authority. Keep current templates blank, examples hypothetical, and upstream "
    "decisions historical. No property facts, sale targets, validated safety model, "
    "operating activation, or inherited role authority may be inferred. Confirm "
    "private completed records stay outside Git and all source dispositions are accounted for."
)
MANUAL_MOUNTAIN_VILLA_CHECK = (
    "Review Mountain Villa source attribution, privacy exclusions, and owner/professional "
    "authority. Keep current templates blank, examples hypothetical, and upstream "
    "decisions historical. No property facts, sale targets, validated safety model, "
    "operating activation, or inherited role authority may be inferred. Confirm "
    "private completed records stay outside Git and all source dispositions are accounted for."
)
MANUAL_PROJECT_ORIENTATION_CHECK = (
    "Review the complete exact project orientation, including pre-existing content: "
    "verify source attribution, privacy, owner authority, and prepared-versus-executed "
    "pilot status. Classify local-only/private references separately from publishable "
    "control dependencies; never admit a linked body merely to satisfy a link. "
    "A navigation repair does not admit earlier project work or neighboring files."
)
MANUAL_LEARNING_CORE_CHECK = (
    "Review Learning Core privacy, attribution, educational claims, hypothetical examples, "
    "and guardian/teacher/clinical/institutional authority. Keep templates blank and "
    "completed family records outside Git. Verify all 60 pinned source dispositions. "
    "Ready is not approval; plan and parent changes must agree; activity is not proof "
    "of mastery. No inherited commercial terms, learner facts, or operational authority. "
    "Check exact candidate dependencies; neighboring records remain unapproved."
)
MANUAL_MENTORSHIP_ARTIFACT_CHECK = (
    "Validate mentorship purpose, learner authority, privacy, provenance, developmental "
    "claims, task-versus-mentorship closure, communication boundaries, and absence of "
    "credentials, restricted source bodies, external commitments, legal/financial advice, "
    "or unsupported capability claims through mira-mentor."
)
MANUAL_NARRATIVE_GEOPOLITICS_CHECK = (
    "Validate Narrative Geopolitics provenance, source/voice routing, bounded-analysis "
    "posture, verification boundaries, and absence of unsupported public factual use."
)
MANUAL_YOUTUBE_CAPTURE_CHECK = (
    "Validate YouTube capture queue provenance, transcript attachment status, duplicate "
    "audit state, routing warnings, and archive-intake authority boundaries."
)
MANUAL_HISTORICAL_REFERENCE_CHECK = (
    "Validate historical-reference extraction scope, taxonomy routing, review posture, "
    "source linkage, and absence of unsupported characterization promotion."
)
MANUAL_REALITY_CHECK = (
    "Validate Reality lattice record integrity, evidence lineage, language/provenance "
    "boundaries, assessment status, and rendered view freshness."
)
MANUAL_SINGULARITY_ARCHIVE_CHECK = (
    "Validate Singularity Science provenance, source-body rights posture, collection "
    "membership, candidate-link status, and separation from claim verification or publication."
)
MIRA_CONTROL_PATHS = frozenset({
    ".gitignore",
    "archive/README.md",
    "mira/continuity/README.md",
    "mira/continuity/activation.md",
    "mira/continuity/trajectory.md",
    "docs/mira-core-name-migration.md",
    "docs/plans/2026-08-16-mira-archive-name-migration.md",
    "mira/continuity/session-registry.json",
})
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
LIBRARY_INTEGRATION_SCHEMA_RE = re.compile(
    r"^archive/schemas/mira-library-integration-v[1-9]\d*\.schema\.json$"
)


RETIRED_WORKTREE_POINTERS = frozenset({
    ".codex-tmp/archive-family-publish", ".codex-tmp/july30-archive-repair",
})


def _retired_worktree_pointer(path: str, repository: Path) -> bool:
    """Only absent, exact historical gitlinks qualify for deletion review."""
    if path not in RETIRED_WORKTREE_POINTERS or (repository / path).exists():
        return False
    result = subprocess.run(["git", "ls-tree", "HEAD", "--", path],
                            cwd=repository, capture_output=True, text=True)
    return result.returncode == 0 and result.stdout.startswith("160000 commit ") and result.stdout.rstrip().endswith("\t" + path)


class RoutingError(ValueError):
    pass


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def normalize_path(raw: str, *, repo_root: Path = REPO_ROOT) -> str:
    if not raw or any(token in raw for token in GLOB_TOKENS):
        raise RoutingError(f"unsafe or globbed path: {raw!r}")
    candidate = Path(raw)
    if any(part == ".." for part in candidate.parts):
        raise RoutingError(f"path traversal is forbidden: {raw}")
    repository = repo_root.resolve(strict=True)
    resolved = (candidate if candidate.is_absolute() else repository / candidate).resolve(
        strict=False
    )
    if not _inside(resolved, repository):
        raise RoutingError(f"path is outside repository: {raw}")
    relative_candidate = resolved.relative_to(repository).as_posix()
    retired_deletion = (
        relative_candidate in RETIRED_PROJECT_PATHS and not resolved.exists()
        and (repository / "projects/README.md").is_file()
        and subprocess.run(["git", "cat-file", "-e", "HEAD:" + relative_candidate],
                           cwd=repository, capture_output=True).returncode == 0
    )
    if not resolved.exists() and not retired_deletion and not _retired_worktree_pointer(relative_candidate, repository):
        relative_missing = resolved.relative_to(repository).as_posix()
        # Permit this exact tracked relocation source, never arbitrary absent paths.
        relocated = repository / "archive/sessions/memorials/registry.json"
        if (relative_missing != "archive/sessions/registry.json" or not relocated.is_file()
                or subprocess.run(["git", "cat-file", "-e", "HEAD:" + relative_missing],
                                  cwd=repository, capture_output=True).returncode):
            raise RoutingError(f"path does not exist: {raw}")
    relative = resolved.relative_to(repository).as_posix()
    if relative in {"", "."}:
        raise RoutingError("repository root is not a publication path")
    return relative


def _focused_skill_command(path: str, *, repo_root: Path) -> str:
    parts = PurePosixPath(path).parts
    if len(parts) >= 3 and parts[:2] == ("docs", "skill-drafts"):
        slug = parts[2].replace("-", "_")
        candidate = repo_root / "tests" / f"test_{slug}_skill.py"
        if candidate.is_file():
            return f"tools/run.ps1 test --path tests/{candidate.name}"
    return "tools/run.ps1 test --mode fast --explain-route"


def _daily_validate_command(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if (
        len(parts) >= 4
        and parts[:3] == ("narrative-geopolitics", "work", "daily")
        and DATE_RE.match(parts[3])
    ):
        return f"tools/run.ps1 daily-validate --date {parts[3]} --stage issue"
    return None


def _monthly_coverage_audit_command(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if (
        len(parts) == 5
        and parts[:3] == ("narrative-geopolitics", "work", "coverage")
        and parts[3] in {"contracts", "receipts"}
    ):
        suffix = ".json" if parts[3] == "contracts" else ".jsonl"
        if parts[4].endswith(suffix):
            month = parts[4].removesuffix(suffix)
            if MONTH_RE.match(month):
                return f"tools/run.ps1 archive-audit --month {month} --format json"
    return None


def _monthly_strategy_notebook_audit_command(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if (
        len(parts) == 4
        and parts[:3] == ("narrative-geopolitics", "work", "strategy-notebook")
        and parts[3].endswith(".md")
    ):
        month = parts[3].removesuffix(".md")
        if MONTH_RE.match(month):
            return f"tools/run.ps1 archive-audit --month {month} --format json"
    return None


def _youtube_capture_date(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if (
        len(parts) == 5
        and parts[:4] == ("narrative-geopolitics", "work", "capture", "youtube")
        and parts[4].endswith(".jsonl")
    ):
        date = parts[4].removesuffix(".jsonl")
        if DATE_RE.match(date):
            return date
    return None


def _historical_reference_run_path(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if (
        len(parts) == 4
        and parts[:3] == ("narrative-geopolitics", "work", "historical-reference")
        and parts[3].endswith(".json")
        and "-review-" not in parts[3]
        and not parts[3].endswith("-checkpoint.json")
        and not parts[3].endswith("-characterizations.json")
    ):
        return path
    return None


def _singularity_archive_path(path: str) -> bool:
    if path == "archive/collections.json":
        return True
    if path in {
        "archive/registries/innermost-loop.json",
        "archive/registries/moonshots.json",
    }:
        return True
    return path.startswith("archive/sources/singularity/")


def _narrative_geopolitics_voice_lens_path(path: str) -> bool:
    if not (
        path.startswith("narrative-geopolitics/voices/")
        and path.endswith(".md")
    ):
        return False
    parts = path.split("/")
    if len(parts) != 4:
        return False
    return parts[-1] not in {
        "README.md",
        "source-index.md",
        "judgment-ledger.md",
        "state-ledger.md",
    }


def _mira_journal_date(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if len(parts) == 3 and parts[:2] == ("mira", "journal") and parts[2].endswith(".md"):
        date = parts[2].removesuffix(".md")
        if DATE_RE.match(date):
            return date
    if (
        len(parts) == 4
        and parts[:3] == ("mira", "journal", "references")
        and parts[3].startswith("MJTR-")
        and (parts[3].endswith(".json") or parts[3].endswith(".md"))
    ):
        match = re.match(r"^MJTR-(\d{4})(\d{2})(\d{2})-v\d+\.(?:json|md)$", parts[3])
        if match:
            return "-".join(match.groups())
    if path in {
        "mira/journal-registry.json",
        "mira/journal.md",
        "mira/journal/continuity-index.json",
        "mira/journal/continuity-index.md",
    }:
        return ""
    return None


def _singularity_youtube_capture_target(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if (
        len(parts) == 4
        and parts[:3] == ("archive", "sources", "singularity")
        and parts[3].endswith(".md")
    ):
        name = parts[3].removesuffix(".md")
        match = re.match(r"^[a-z0-9-]+-capture-targets-(\d{4}-\d{2}-\d{2})$", name)
        if match:
            return match.group(1)
    return None


def _registered_library_note(path: str, *, repo_root: Path) -> bool:
    if not path.startswith("archive/notes/"):
        return False
    registry_path = (
        repo_root / "archive" / "library" / "integrations" / "work-registry.json"
    )
    if not registry_path.is_file():
        return False
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise RoutingError(
            "Mira Library work registry is unreadable; cognitive-note ownership cannot be resolved"
        ) from error
    works = payload.get("works") if isinstance(payload, dict) else None
    if not isinstance(works, list):
        raise RoutingError(
            "Mira Library work registry has no works list; cognitive-note ownership cannot be resolved"
        )
    for work in works:
        if not isinstance(work, dict):
            continue
        refs = {
            str(value).replace("\\", "/")
            for value in work.get("note_refs", [])
            if isinstance(value, str) and value
        }
        for key in ("note_ref", "revision_head_note_ref"):
            value = work.get(key)
            if isinstance(value, str) and value:
                refs.add(value.replace("\\", "/"))
        if path in refs:
            return True
    return False


def _library_validation_route(*, cognitive_note: bool = False) -> dict[str, Any]:
    return {
        "owner": (
            "mira-library/cognitive-note" if cognitive_note else "mira-library"
        ),
        "validation_class": "domain-governed" if cognitive_note else "repo-structural",
        "commands": [
            "tools/run.ps1 library validate --json",
            "tools/run.ps1 library integration-render --check --json",
            "tools/run.ps1 library route-index --check --json",
            "tools/run.ps1 test --path tests/test_archive_library.py",
            "tools/run.ps1 test --path tests/test_library_integration.py",
            "tools/run.ps1 test --path tests/test_daily_run_validation.py",
        ],
        "manual_checks": (
            [MANUAL_NOTE_CHECK, MANUAL_LIBRARY_COGNITIVE_NOTE_CHECK]
            if cognitive_note
            else []
        ),
    }


def route_path(path: str, *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    if path in {"docs/validation-scopes.md", ".github/workflows/validate.yml"}:
        return {
            "owner": "repo-structural/validation-scopes",
            "validation_class": "repo-structural",
            "commands": ["tools/run.ps1 test --path tests/test_validation_scopes.py"],
            "manual_checks": ["Verify public and corpus claims stay distinct, privacy enforcement remains public, failures are not suppressed, and Full cache or hosted required-check policy is not bypassed."],
        }
    if path == ".gitattributes":
        return {
            "owner": "repo-structural/git-attributes",
            "validation_class": "repo-structural",
            "commands": ["tools/run.ps1 test --path tests/test_publication_validation.py"],
            "manual_checks": [
                "Verify the changed attribute patterns are narrowly scoped and that Git "
                "clean conversion preserves the required bytes of every hash-bound file."
            ],
        }
    # Classification aliases are not physical paths or replacements for owner IDs.
    # Keep the supplied path for commands that address the actual artifact.
    physical_path = path
    if path.startswith("geopolitics/"):
        path = "narrative-geopolitics/" + path.removeprefix("geopolitics/")
    if path.startswith(("archive/sessions/transcripts/", "archive/sessions/daily/")):
        raise RoutingError("Private session payloads cannot be admitted to Git")
    if path in RETIRED_WORKTREE_POINTERS:
        if not _retired_worktree_pointer(path, repo_root):
            raise RoutingError("only absent tracked worktree pointers may be retired: " + path)
        return {
            "path": path, "owner": "repo-structural", "validation_class": "repo-structural",
            "commands": ["tools/run.ps1 test --path tests/test_retired_worktree_pointers.py"],
            "manual_checks": ["Verify these exact historical gitlinks are absent and no longer registered worktrees; preserve their commit identities and remove pointers only, never directory contents."],
        }
    if path in RETIRED_PROJECT_PATHS:
        if (repo_root / path).exists():
            raise RoutingError("retired project path cannot admit content: " + path)
        return {
            "owner": "projects/reconciliation",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --path tests/test_projects_reconciliation.py"],
            "manual_checks": [MANUAL_PROJECT_RECONCILIATION_CHECK],
        }
    if path in {
        "projects/learning-core/README.md",
        "projects/learning-core/intake.md",
        "projects/learning-core/learner-profile-template.md",
        "projects/learning-core/plan-template.md",
        "projects/learning-core/evidence-and-approval.md",
        "projects/learning-core/portfolio-and-review.md",
        "projects/learning-core/continuity.md",
        "projects/learning-core/resource-selection.md",
        "projects/learning-core/worked-examples.md",
        "projects/learning-core/source-map.md",
    }:
        return {
            "owner": "learning-core/portable-methods",
            "validation_class": "domain-governed",
            "commands": [
                "tools/run.ps1 test --path tests/test_publication_validation.py "
                "--path tests/test_learning_core_project.py"
            ],
            "manual_checks": [MANUAL_LEARNING_CORE_CHECK],
        }
    if path == "projects/provenance.md":
        return {
            "owner": "projects/provenance",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --path tests/test_publication_validation.py"],
            "manual_checks": [MANUAL_PROJECT_ORIENTATION_CHECK],
        }
    if path in {
        "projects/grace-mar/mountain-villa/README.md",
        "projects/grace-mar/mountain-villa/intake.md",
        "projects/grace-mar/mountain-villa/operating-review.md",
        "projects/grace-mar/mountain-villa/risk-register.md",
        "projects/grace-mar/mountain-villa/decision-log.md",
        "projects/grace-mar/mountain-villa/preparation-plan.md",
        "projects/grace-mar/mountain-villa/creative-interface.md",
        "projects/grace-mar/mountain-villa/source-map.md",
    }:
        return {
            "owner": "mountain-villa/stewardship",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --path tests/test_publication_validation.py"],
            "manual_checks": [MANUAL_MOUNTAIN_VILLA_CHECK],
        }
    if path in {
        "projects/grace-mar/mountain-villa/README.md",
        "projects/grace-mar/mountain-villa/intake.md",
        "projects/grace-mar/mountain-villa/operating-review.md",
        "projects/grace-mar/mountain-villa/risk-register.md",
        "projects/grace-mar/mountain-villa/decision-log.md",
        "projects/grace-mar/mountain-villa/preparation-plan.md",
        "projects/grace-mar/mountain-villa/creative-interface.md",
        "projects/grace-mar/mountain-villa/source-map.md",
    }:
        return {
            "owner": "mountain-villa/stewardship",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --path tests/test_publication_validation.py"],
            "manual_checks": [MANUAL_MOUNTAIN_VILLA_CHECK],
        }
    project_orientation_owners = {
        "projects/README.md": "projects/index",
        "projects/lab/README.md": "projects/lab-orientation",
        "projects/media-production/README.md": "projects/media-production-orientation",
    }
    if path in project_orientation_owners:
        return {
            "owner": project_orientation_owners[path],
            "validation_class": "domain-governed",
            "commands": [
                "tools/run.ps1 test --path tests/test_publication_validation.py"
            ],
            "manual_checks": [MANUAL_PROJECT_ORIENTATION_CHECK],
        }
    project_orientation_owners = {
        "projects/README.md": "projects/index",
        "projects/lab/README.md": "projects/lab-orientation",
        "projects/media-production/README.md": "projects/media-production-orientation",
    }
    if path in project_orientation_owners:
        return {
            "owner": project_orientation_owners[path],
            "validation_class": "domain-governed",
            "commands": [
                "tools/run.ps1 test --path tests/test_publication_validation.py"
            ],
            "manual_checks": [MANUAL_PROJECT_ORIENTATION_CHECK],
        }
    if path == "projects/grace-mar/README.md":
        return {
            "owner": "grace-mar/orientation",
            "validation_class": "domain-governed",
            "commands": [
                "tools/run.ps1 test --path tests/test_publication_validation.py"
            ],
            "manual_checks": [MANUAL_GRACE_MAR_CHECK],
        }
    if path == "projects/grace-mar/ottoman-rugs/README.md":
        return {
            "owner": "ottoman-rugs/orientation",
            "validation_class": "domain-governed",
            "commands": [
                "tools/run.ps1 test --path tests/test_publication_validation.py"
            ],
            "manual_checks": [MANUAL_OTTOMAN_RUGS_CHECK],
        }
    if path in {
        "projects/grace-mar/grace-gems/README.md",
        "projects/grace-mar/grace-gems/admission-matrix.md",
        "projects/grace-gems/README.md",
        "projects/grace-gems/admission-matrix.md",
    }:
        return {
            "owner": "grace-gems/stewardship",
            "validation_class": "domain-governed",
            "commands": [],
            "manual_checks": [MANUAL_GRACE_GEMS_CHECK],
        }
    if path.startswith("artifacts/mentorship/"):
        return {
            "owner": "mira-mentor/artifacts",
            "validation_class": "domain-governed",
            "commands": [],
            "manual_checks": [MANUAL_MENTORSHIP_ARTIFACT_CHECK],
        }
    if _registered_library_note(path, repo_root=repo_root):
        return _library_validation_route(cognitive_note=True)
    if path == "archive/sources/youtube-channel-routing.yml":
        return {
            "owner": "youtube-capture/routing",
            "validation_class": "repo-structural",
            "commands": [
                "tools/run.ps1 test --path tests/test_youtube_capture.py",
                "tools/run.ps1 test --path tests/test_youtube_capture_skill.py",
            ],
            "manual_checks": [MANUAL_YOUTUBE_CAPTURE_CHECK],
        }
    if path == "archive/sources/singularity/_youtube-capture-target-template.md":
        return {
            "owner": "youtube-capture/singularity-targets",
            "validation_class": "repo-structural",
            "commands": ["tools/run.ps1 test --path tests/test_youtube_capture.py"],
            "manual_checks": [MANUAL_YOUTUBE_CAPTURE_CHECK],
        }
    singularity_capture_date = _singularity_youtube_capture_target(path)
    if singularity_capture_date:
        return {
            "owner": "youtube-capture/singularity-targets",
            "validation_class": "domain-governed",
            "commands": [
                "tools/run.ps1 youtube-capture route-audit --json",
                "tools/run.ps1 test --path tests/test_youtube_capture.py",
            ],
            "manual_checks": [MANUAL_YOUTUBE_CAPTURE_CHECK],
        }
    if path.startswith("archive/letters/"):
        return {
            "owner": "mira-letters",
            "validation_class": "domain-governed",
            "commands": [],
            "manual_checks": [MANUAL_LETTER_CHECK],
        }
    if path.startswith("archive/notes/"):
        return {
            "owner": "mira-notes",
            "validation_class": "domain-governed",
            "commands": [],
            "manual_checks": [MANUAL_NOTE_CHECK],
        }
    if path.startswith("archive/sessions/") or path == "archive/schemas/session-memorial.schema.json":
        return {
            "owner": "mira-sessions",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 mira-sessions validate"],
            "manual_checks": [MANUAL_SESSION_MEMORIAL_CHECK],
        }
    if path.startswith("archive/essays/"):
        return {
            "owner": "mira-essays",
            "validation_class": "domain-governed",
            "commands": [],
            "manual_checks": [MANUAL_ESSAY_CHECK],
        }
    journal_date = _mira_journal_date(path)
    if journal_date is not None:
        commands = [
            (
                f"tools/run.ps1 mira-journal status --from {journal_date} --to {journal_date} --json"
                if journal_date
                else "tools/run.ps1 mira-journal status --json"
            )
        ]
        return {
            "owner": "mira-journal",
            "validation_class": "domain-governed",
            "commands": commands,
            "manual_checks": [MANUAL_MIRA_JOURNAL_CHECK],
        }
    if _singularity_archive_path(path):
        return {
            "owner": "singularity-science/archive",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 archive validate --git-only --json"],
            "manual_checks": [MANUAL_SINGULARITY_ARCHIVE_CHECK],
        }
    if path == "archive/sources/geopolitics/source-manifest.json":
        return {
            "owner": "narrative-geopolitics/archive",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --path tests/test_voice_count_authority.py"],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    if (
        path.startswith("archive/sources/geopolitics/sources/")
        or (
            path.startswith("narrative-geopolitics/voices/")
            and path.endswith("/source-index.md")
        )
    ):
        return {
            "owner": "narrative-geopolitics/archive",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --path tests/test_voice_count_authority.py"],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    if path == "narrative-geopolitics/voices/README.md":
        return {
            "owner": "narrative-geopolitics/voice-control",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --path tests/test_voice_count_authority.py"],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    if (
        path.startswith("narrative-geopolitics/voices/")
        and path.endswith("/README.md")
    ):
        return {
            "owner": "narrative-geopolitics/voice-control",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --path tests/test_voice_count_authority.py"],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    if _narrative_geopolitics_voice_lens_path(path):
        return {
            "owner": "narrative-geopolitics/voice-control",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --path tests/test_voice_count_authority.py"],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    if path.startswith("narrative-geopolitics/templates/"):
        return {
            "owner": "geo-strategy/templates",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --mode fast --explain-route"],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    if path.startswith("narrative-geopolitics/method/"):
        return {
            "owner": "geo-strategy/method",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --mode fast --explain-route"],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    daily_command = _daily_validate_command(path)
    if daily_command:
        return {
            "owner": "geo-strategy",
            "validation_class": "domain-governed",
            "commands": [daily_command],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    if path == "narrative-geopolitics/work/forecasts/forecast-ledger.md":
        return {
            "owner": "geo-strategy/forecast-ledger",
            "validation_class": "domain-governed",
            "commands": [],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    if (
        path.startswith("narrative-geopolitics/work/morning-brief/")
        and (path.endswith(".md") or path.endswith(".receipt.json"))
    ):
        return {
            "owner": "morning-brief",
            "validation_class": "domain-governed",
            "commands": ["tools/run.ps1 test --path tests/test_morning_brief.py"],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    monthly_strategy_notebook_command = _monthly_strategy_notebook_audit_command(path)
    if monthly_strategy_notebook_command:
        return {
            "owner": "geo-strategy/strategy-notebook",
            "validation_class": "domain-governed",
            "commands": [monthly_strategy_notebook_command],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    monthly_coverage_command = _monthly_coverage_audit_command(path)
    if monthly_coverage_command:
        return {
            "owner": "archive-audit/monthly-completeness",
            "validation_class": "domain-governed",
            "commands": [monthly_coverage_command],
            "manual_checks": [MANUAL_NARRATIVE_GEOPOLITICS_CHECK],
        }
    if path == "narrative-geopolitics/work/capture/youtube/youtube-capture-policy.yml":
        return {
            "owner": "youtube-capture/geopolitics-policy",
            "validation_class": "repo-structural",
            "commands": ["tools/run.ps1 test --path tests/test_youtube_capture.py"],
            "manual_checks": [MANUAL_YOUTUBE_CAPTURE_CHECK],
        }
    youtube_date = _youtube_capture_date(path)
    if youtube_date:
        return {
            "owner": "youtube-capture/geopolitics-queue",
            "validation_class": "domain-governed",
            "commands": [
                f"python -X utf8 scripts/youtube_capture.py status --date {youtube_date}",
                f"python -X utf8 scripts/youtube_capture.py audit-duplicates --date {youtube_date} --json",
            ],
            "manual_checks": [MANUAL_YOUTUBE_CAPTURE_CHECK],
        }
    historical_run = _historical_reference_run_path(path)
    if path.startswith("narrative-geopolitics/work/historical-reference/"):
        commands = (
            [
                "python scripts/validate_historical_reference_taxonomy.py "
                f"--run {physical_path}"
            ]
            if historical_run
            else []
        )
        return {
            "owner": "historical-reference",
            "validation_class": "domain-governed",
            "commands": commands,
            "manual_checks": [MANUAL_HISTORICAL_REFERENCE_CHECK],
        }
    if (
        path.startswith("narrative-geopolitics/work/reality/")
        or path.startswith("narrative-geopolitics/work/verification/packets/")
        or path == "narrative-geopolitics/work/verification/legacy-inventory.json"
    ):
        return {
            "owner": "reality-check",
            "validation_class": "domain-governed",
            "commands": ["python scripts/reality.py check"],
            "manual_checks": [MANUAL_REALITY_CHECK],
        }
    if path == "AGENTS.md" or path.startswith("docs/skill-drafts/"):
        return {
            "owner": "skill/control",
            "validation_class": "repo-structural",
            "commands": [_focused_skill_command(path, repo_root=repo_root)],
            "manual_checks": [
                "Read through the controlling instructions and verify trigger, authority, "
                "composition, and reference coherence."
            ],
        }
    if path in MIRA_CONTROL_PATHS:
        return {
            "owner": "mira-control-plane",
            "validation_class": "repo-structural",
            "commands": ["tools/run.ps1 test --mode fast --explain-route"],
            "manual_checks": [
                "Verify Mira control-plane semantics, authority boundaries, and historical "
                "provenance preservation remain coherent."
            ],
        }
    if path.startswith("docs/experiments/"):
        return {
            "owner": "repo-structural",
            "validation_class": "repo-structural",
            "commands": ["tools/run.ps1 test --mode fast --explain-route"],
            "manual_checks": [
                "Verify the experiment preserves frozen inputs, evidence and privacy boundaries, "
                "decision thresholds, and separation between evaluation and mutation authority."
            ],
        }
    if path.startswith(("docs/work-journal/", "docs/dev-journal/")):
        return {
            "owner": "work-journal",
            "validation_class": "repo-structural",
            "commands": ["tools/run.ps1 test --path tests/test_publication_validation.py"],
            "manual_checks": [MANUAL_WORK_JOURNAL_CHECK],
        }
    if (
        path.startswith("archive/library/")
        or LIBRARY_INTEGRATION_SCHEMA_RE.fullmatch(path)
        or path == "scripts/library_integration.py"
    ):
        return _library_validation_route()
    if path.startswith("tests/"):
        suffix = Path(path).suffix.lower()
        if suffix != ".py":
            raise RoutingError(f"unsupported test publication path: {path}")
        return {
            "owner": "repo-structural",
            "validation_class": "repo-structural",
            "commands": [f"tools/run.ps1 test --path {path}"],
            "manual_checks": [],
        }
    if path.startswith("scripts/") or path.startswith("tools/"):
        return {
            "owner": "repo-structural",
            "validation_class": "repo-structural",
            "commands": ["tools/run.ps1 test --mode fast --explain-route"],
            "manual_checks": [],
        }
    raise RoutingError(f"no deterministic publication-validation route: {physical_path}")


def _ordered_unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def verified_rename(source: str, target: str, *, repo_root: Path) -> dict[str, Any]:
    """Verify a worktree-only domain move against the current index, read-only.

    This establishes unchanged content, not publication approval or a Full-gate
    exception. Content changes continue through the ordinary domain routes.
    """
    for value in (source, target):
        if (not value or "\\" in value or ":" in value
                or any(token in value for token in GLOB_TOKENS)
                or any(part in ("", ".", "..") or part.endswith((" ", "."))
                       for part in value.split("/"))):
            raise RoutingError("unsafe rename mapping")
    prefix = "narrative-geopolitics/"
    if not source.startswith(prefix) or target != "geopolitics/" + source[len(prefix):]:
        raise RoutingError("rename must preserve the exact domain-relative path")
    root = repo_root.resolve(strict=True)

    def git(*args: str) -> bytes:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True)
        if result.returncode:
            raise RoutingError("Git evidence unavailable for rename")
        return result.stdout

    if Path(git("rev-parse", "--show-toplevel").decode().strip()).resolve() != root:
        raise RoutingError("rename repository must be the exact Git root")
    if (root / "narrative-geopolitics").exists() or (root / "narrative-geopolitics").is_symlink():
        raise RoutingError("rename source domain is still occupied")
    destination = root / target
    for path in (destination, *destination.parents):
        if path == root:
            break
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise RoutingError("rename target contains a filesystem link")
    if not destination.is_file() or not _inside(destination.resolve(), root):
        raise RoutingError("rename target is missing or outside repository")
    rows = git("ls-files", "--stage", "-z", "--", source, target).split(b"\0")
    expected = [row for row in rows if row]
    if len(expected) != 1:
        raise RoutingError("rename requires one indexed source and an unindexed target")
    metadata, indexed_path = expected[0].split(b"\t", 1)
    mode, blob, stage = metadata.decode().split()
    if indexed_path.decode() != source or stage != "0" or mode not in {"100644", "100755"}:
        raise RoutingError("rename source is missing, conflicted, or not a regular file")
    # Use destination attributes: a path-dependent clean filter must not change
    # the blob that Git would stage at the new location.
    actual = git("hash-object", "--path=" + target, "--", target).decode().strip()
    if actual != blob:
        raise RoutingError("rename target content differs from indexed source")
    return {"source": source, "target": target, "blob": blob, "mode": mode,
            "evidence_boundary": "current-index-to-working-tree", "authority_effect": "none"}


def build_report(raw_paths: list[str], *, repo_root: Path = REPO_ROOT,
                 rename_sources: list[str] | None = None) -> dict[str, Any]:
    paths: list[str] = []
    blockers: list[str] = []
    routes: list[dict[str, Any]] = []
    seen: set[str] = set()
    rename_evidence: list[dict[str, Any]] = []
    if rename_sources is not None and (
            len(rename_sources) != len(raw_paths) or not raw_paths
            or len(set(rename_sources)) != len(rename_sources)):
        raise RoutingError("rename sources must be unique and paired with every target")
    for index, raw in enumerate(raw_paths):
        try:
            evidence = (verified_rename(rename_sources[index], raw, repo_root=repo_root)
                        if rename_sources is not None else None)
            path = normalize_path(raw, repo_root=repo_root)
            if path in seen:
                raise RoutingError(f"duplicate path: {path}")
            seen.add(path)
            paths.append(path)
            if evidence is None:
                routes.append(route_path(path, repo_root=repo_root.resolve()))
            else:
                rename_evidence.append(evidence)
                routes.append({"owner": "geopolitics/verified-domain-rename",
                               "validation_class": "repo-structural",
                               "commands": ["tools/run.ps1 test --mode full"],
                               "manual_checks": ["Verify the staged old/new blob and mode pairs match this evidence; preserve unrelated edits and untracked files. No content admission or publication authority is granted."]})
        except (OSError, RoutingError) as error:
            blockers.append(str(error))
    owners = _ordered_unique(route["owner"] for route in routes)
    classes = _ordered_unique(route["validation_class"] for route in routes)
    commands = _ordered_unique(
        command for route in routes for command in route["commands"]
    )
    manual_checks = _ordered_unique(
        check for route in routes for check in route["manual_checks"]
    )
    status = "blocked" if blockers else ("manual-required" if manual_checks else "resolved")
    report = {
        "status": status,
        "paths": paths,
        "owners": owners,
        "validation_classes": classes,
        "commands": commands,
        "manual_checks": manual_checks,
        "blockers": blockers,
    }
    if rename_sources is not None:
        report["rename_evidence"] = rename_evidence
    return report


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="Resolve publication candidates to owning validation workflows."
    )
    value.add_argument("--path", action="append", required=True)
    value.add_argument("--rename-source", action="append",
                       help="Explicit indexed old path paired with each --path; verifies a pure domain move.")
    value.add_argument("--json", action="store_true")
    return value


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    report = build_report(args.path, rename_sources=args.rename_source)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"status={report['status']}")
        for command in report["commands"]:
            print(f"command={command}")
        for check in report["manual_checks"]:
            print(f"manual_check={check}")
        for blocker in report["blockers"]:
            print(f"blocker={blocker}")
    return 2 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
GLOB_TOKENS = "*?["
MANUAL_NOTE_CHECK = (
    "Validate note lifecycle/status, privacy, provenance, authority effect, and "
    "absence of credentials or restricted source bodies through mira-notes."
)
MANUAL_ESSAY_CHECK = (
    "Validate essay privacy, evidence boundaries, provenance, links, detached-title "
    "accuracy, and Markdown integrity through mira-essays."
)
MANUAL_SESSION_MEMORIAL_CHECK = (
    "Validate the memorial pair, exact Continuity lineage, paraphrase-only privacy, "
    "manual privacy receipt, inactive posture, attribution, omissions, and version chain through mira-sessions."
)
MANUAL_GRACE_GEMS_CHECK = (
    "Validate Grace Gems provenance, privacy exclusions, stewardship-versus-ownership "
    "boundaries, CEO authority, and absence of copied upstream or private evidence."
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
    "docs/mira-core-name-migration.md",
    "docs/plans/2026-08-16-mira-archive-name-migration.md",
    "mira/continuity/session-registry.json",
})
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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
    if not resolved.exists():
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


def route_path(path: str, *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    if path.startswith("projects/grace-gems/"):
        return {
            "owner": "grace-gems/stewardship",
            "validation_class": "domain-governed",
            "commands": [],
            "manual_checks": [MANUAL_GRACE_GEMS_CHECK],
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
    if path == "narrative-geopolitics/work/capture/youtube/youtube-capture-policy.yml":
        return {
            "owner": "youtube-capture/policy",
            "validation_class": "repo-structural",
            "commands": ["tools/run.ps1 test --path tests/test_youtube_capture.py"],
            "manual_checks": [MANUAL_YOUTUBE_CAPTURE_CHECK],
        }
    youtube_date = _youtube_capture_date(path)
    if youtube_date:
        return {
            "owner": "youtube-capture",
            "validation_class": "domain-governed",
            "commands": [
                f"python scripts/youtube_capture.py status --date {youtube_date}",
                f"python scripts/youtube_capture.py audit-duplicates --date {youtube_date} --json",
            ],
            "manual_checks": [MANUAL_YOUTUBE_CAPTURE_CHECK],
        }
    historical_run = _historical_reference_run_path(path)
    if path.startswith("narrative-geopolitics/work/historical-reference/"):
        commands = (
            [
                "python scripts/validate_historical_reference_taxonomy.py "
                f"--run {historical_run}"
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
    if path.startswith("narrative-geopolitics/work/reality/"):
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
    if path.startswith("archive/library/"):
        return {
            "owner": "mira-library",
            "validation_class": "repo-structural",
            "commands": [
                "tools/run.ps1 library validate --json",
                "tools/run.ps1 test --path tests/test_archive_library.py",
            ],
            "manual_checks": [],
        }
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
    raise RoutingError(f"no deterministic publication-validation route: {path}")


def _ordered_unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def build_report(raw_paths: list[str], *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    paths: list[str] = []
    blockers: list[str] = []
    routes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in raw_paths:
        try:
            path = normalize_path(raw, repo_root=repo_root)
            if path in seen:
                raise RoutingError(f"duplicate path: {path}")
            seen.add(path)
            paths.append(path)
            routes.append(route_path(path, repo_root=repo_root.resolve()))
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
    return {
        "status": status,
        "paths": paths,
        "owners": owners,
        "validation_classes": classes,
        "commands": commands,
        "manual_checks": manual_checks,
        "blockers": blockers,
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="Resolve publication candidates to owning validation workflows."
    )
    value.add_argument("--path", action="append", required=True)
    value.add_argument("--json", action="store_true")
    return value


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    report = build_report(args.path)
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

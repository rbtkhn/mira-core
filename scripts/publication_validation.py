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

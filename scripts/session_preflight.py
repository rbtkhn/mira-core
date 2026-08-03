from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = "1.0"
DEFAULT_GROUP_LIMIT = 20
DEFAULT_PATH_LIMIT = 50
MAX_PATH_LIMIT = 200


class PreflightError(RuntimeError):
    pass


def git_output(repo_root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip()


def status_entries(repo_root: Path) -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=normal"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    fields = result.stdout.decode("utf-8", errors="replace").split("\0")
    entries: list[tuple[str, str]] = []
    index = 0
    while index < len(fields):
        field = fields[index]
        index += 1
        if not field:
            continue
        if len(field) < 4:
            raise PreflightError("git status returned a malformed porcelain record")
        status = field[:2]
        path = field[3:].replace("\\", "/")
        entries.append((status, path))
        if "R" in status or "C" in status:
            if index >= len(fields) or not fields[index]:
                raise PreflightError("git status omitted a rename or copy path")
            index += 1
    return entries


def top_level(path: str) -> str:
    normalized = path.strip("/")
    if not normalized:
        return "(repository-root)"
    return normalized.split("/", 1)[0]


def path_in_scope(path: str, scopes: Iterable[str]) -> bool:
    normalized = path.strip("/")
    for scope in scopes:
        candidate = scope.replace("\\", "/").strip("/")
        if normalized == candidate or normalized.startswith(candidate + "/"):
            return True
    return False


def summarize_entries(
    entries: list[tuple[str, str]],
    *,
    scopes: list[str],
    group_limit: int = DEFAULT_GROUP_LIMIT,
    path_limit: int = DEFAULT_PATH_LIMIT,
) -> dict[str, Any]:
    groups = Counter(top_level(path) for _, path in entries)
    ordered_groups = sorted(groups.items(), key=lambda item: (-item[1], item[0]))
    tracked = sum(status != "??" for status, _ in entries)
    untracked = sum(status == "??" for status, _ in entries)
    staged = sum(status[0] not in {" ", "?"} for status, _ in entries)
    summary: dict[str, Any] = {
        "dirty_path_count": len(entries),
        "tracked_change_count": tracked,
        "untracked_entry_count": untracked,
        "staged_path_count": staged,
        "groups": [
            {"root": root, "count": count}
            for root, count in ordered_groups[:group_limit]
        ],
        "groups_truncated": len(ordered_groups) > group_limit,
    }
    if scopes:
        matching = sorted(
            path for _, path in entries if path_in_scope(path, scopes)
        )
        summary["scopes"] = scopes
        summary["scoped_paths"] = matching[:path_limit]
        summary["scoped_paths_truncated"] = len(matching) > path_limit
    return summary


def divergence(repo_root: Path) -> dict[str, Any]:
    try:
        upstream = git_output(
            repo_root,
            "rev-parse",
            "--abbrev-ref",
            "--symbolic-full-name",
            "@{u}",
        )
        counts = git_output(repo_root, "rev-list", "--left-right", "--count", "@{u}...HEAD")
        behind_text, ahead_text = counts.split()
        return {
            "upstream": upstream,
            "behind": int(behind_text),
            "ahead": int(ahead_text),
        }
    except (subprocess.CalledProcessError, ValueError):
        return {"upstream": None, "behind": None, "ahead": None}


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def probe_temp_root(temp_root: Path, *, repo_root: Path) -> dict[str, Any]:
    resolved = temp_root.resolve(strict=False)
    repository = repo_root.resolve(strict=True)
    result: dict[str, Any] = {
        "requested_root": str(temp_root),
        "resolved_root": str(resolved),
        "exists": resolved.is_dir(),
        "outside_repository": not is_within(resolved, repository),
        "writable": False,
        "probe_removed": False,
        "failure": None,
    }
    if not temp_root.is_absolute():
        result["failure"] = "temporary root must be absolute"
        return result
    if not result["exists"]:
        result["failure"] = "temporary root does not exist"
        return result
    if not result["outside_repository"]:
        result["failure"] = "temporary root must be outside the repository"
        return result

    descriptor: int | None = None
    probe: str | None = None
    try:
        descriptor, probe = tempfile.mkstemp(prefix="narrative-session-preflight-", dir=resolved)
        os.close(descriptor)
        descriptor = None
        Path(probe).unlink()
        result["writable"] = True
        result["probe_removed"] = not Path(probe).exists()
    except OSError as error:
        result["failure"] = f"temporary root is not writable: {error}"
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if probe is not None:
            Path(probe).unlink(missing_ok=True)
    return result


def build_report(
    repo_root: Path,
    temp_root: Path,
    *,
    scopes: list[str],
    path_limit: int,
) -> dict[str, Any]:
    entries = status_entries(repo_root)
    temporary = probe_temp_root(temp_root, repo_root=repo_root)
    return {
        "schema_version": SCHEMA_VERSION,
        "ready": bool(temporary["writable"] and temporary["probe_removed"]),
        "git": {
            "branch": git_output(repo_root, "branch", "--show-current") or "DETACHED",
            "head": git_output(repo_root, "rev-parse", "--short=12", "HEAD"),
            **divergence(repo_root),
            **summarize_entries(entries, scopes=scopes, path_limit=path_limit),
        },
        "temporary": temporary,
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="Bound repository diagnostics and preflight an external temporary root."
    )
    value.add_argument("--temp-root", required=True, type=Path)
    value.add_argument(
        "--scope",
        action="append",
        default=[],
        help="Repository-relative path scope; enables capped path output.",
    )
    value.add_argument(
        "--path-limit",
        type=int,
        default=DEFAULT_PATH_LIMIT,
        help=f"Maximum scoped paths to emit (1-{MAX_PATH_LIMIT}).",
    )
    value.add_argument("--json", action="store_true")
    return value


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    if not 1 <= args.path_limit <= MAX_PATH_LIMIT:
        raise SystemExit(f"--path-limit must be between 1 and {MAX_PATH_LIMIT}")
    try:
        report = build_report(
            REPO_ROOT,
            args.temp_root,
            scopes=args.scope,
            path_limit=args.path_limit,
        )
    except (OSError, subprocess.CalledProcessError, PreflightError) as error:
        report = {
            "schema_version": SCHEMA_VERSION,
            "ready": False,
            "failure": f"{type(error).__name__}: {error}",
        }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    return 0 if report.get("ready") else 2


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent


def git(repo: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def git_stdout(repo: Path, *arguments: str) -> str:
    return git(repo, *arguments).stdout.strip()


def porcelain(repo: Path) -> list[str]:
    output = git(repo, "status", "--porcelain=v1", "--untracked-files=all").stdout
    return [line for line in output.splitlines() if line]


def path_from_status(line: str) -> str:
    return line[3:]


def top_level(path: str) -> str:
    return path.replace("\\", "/").split("/", 1)[0]


def dirty_groups(lines: list[str]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for line in lines:
        root = top_level(path_from_status(line))
        counts[root] = counts.get(root, 0) + 1
    return [
        {"root": root, "count": count}
        for root, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def staged_count(lines: list[str]) -> int:
    return sum(1 for line in lines if line[:2] != "??" and line[0] != " ")


def current_branch(repo: Path) -> str:
    return git_stdout(repo, "branch", "--show-current") or "detached"


def optional_sha(repo: Path, ref: str) -> str | None:
    result = git(repo, "rev-parse", "--verify", ref, check=False)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def upstream_ref(repo: Path) -> str | None:
    result = git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}", check=False)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def ahead_behind(repo: Path, upstream: str | None) -> tuple[int | None, int | None]:
    if upstream is None:
        return None, None
    result = git(repo, "rev-list", "--left-right", "--count", f"{upstream}...HEAD", check=False)
    if result.returncode != 0:
        return None, None
    left, right = result.stdout.strip().split()
    return int(right), int(left)


def boundary_label(
    *,
    dirty_count: int,
    staged: int,
    ahead: int | None,
    behind: int | None,
    upstream: str | None,
) -> str:
    if upstream is None or ahead is None or behind is None:
        return "inspect-only: upstream unavailable"
    if behind and ahead:
        return "main-sync-plan: diverged"
    if behind:
        return "main-sync-plan: behind remote"
    if ahead:
        return "push-ready: committed local work"
    if staged:
        return "commit-ready: staged work"
    if dirty_count:
        return "commit-plan: dirty worktree"
    return "inspected only: clean and synchronized"


def build_report(repo: Path = REPO_ROOT) -> dict[str, Any]:
    repository = repo.resolve()
    lines = porcelain(repository)
    upstream = upstream_ref(repository)
    ahead, behind = ahead_behind(repository, upstream)
    local_head = optional_sha(repository, "HEAD")
    upstream_sha = optional_sha(repository, upstream) if upstream else None
    staged = staged_count(lines)
    dirty_count = len(lines)
    return {
        "schema_version": "1.0",
        "repository": str(repository),
        "branch": current_branch(repository),
        "local_head": local_head,
        "upstream": upstream,
        "upstream_sha": upstream_sha,
        "ahead": ahead,
        "behind": behind,
        "dirty_count": dirty_count,
        "dirty_groups": dirty_groups(lines),
        "staged_count": staged,
        "recommended_boundary": boundary_label(
            dirty_count=dirty_count,
            staged=staged,
            ahead=ahead,
            behind=behind,
            upstream=upstream,
        ),
        "authority_effect": "none",
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="Report Mira Core publication readiness from local Git state."
    )
    value.add_argument("--json", action="store_true")
    value.add_argument("--repo", default=str(REPO_ROOT))
    return value


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    report = build_report(Path(args.repo))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Dirty: {report['dirty_count']}")
        print(f"Staged: {report['staged_count']}")
        print(f"Ahead: {report['ahead']}")
        print(f"Behind: {report['behind']}")
        print(f"Remote: {report['upstream_sha'] or 'unavailable'}")
        print(f"Boundary: {report['recommended_boundary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

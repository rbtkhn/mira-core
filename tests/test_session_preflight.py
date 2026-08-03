from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
TOOLS_ROOT = REPO_ROOT / "tools"
for root in (SCRIPTS_ROOT, TOOLS_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

import session_preflight
import run_repo


def test_large_dirty_state_is_bounded_without_path_scope() -> None:
    entries = [
        (" M", f"archive/day-{index % 31}/source-{index}.md")
        for index in range(10_000)
    ]
    summary = session_preflight.summarize_entries(entries, scopes=[])
    rendered = json.dumps(summary)

    assert summary["dirty_path_count"] == 10_000
    assert summary["groups"] == [{"root": "archive", "count": 10_000}]
    assert "scoped_paths" not in summary
    assert len(rendered.encode("utf-8")) < 8 * 1024


def test_full_paths_require_scope_and_remain_capped() -> None:
    entries = [
        ("??", f"docs/item-{index}.md") for index in range(8)
    ] + [(" M", "scripts/tool.py")]

    summary = session_preflight.summarize_entries(
        entries,
        scopes=["docs"],
        path_limit=3,
    )

    assert summary["scoped_paths"] == [
        "docs/item-0.md",
        "docs/item-1.md",
        "docs/item-2.md",
    ]
    assert summary["scoped_paths_truncated"] is True
    assert "scripts/tool.py" not in summary["scoped_paths"]


def test_external_temp_probe_is_removed(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    temporary = tmp_path / "external-temp"
    repository.mkdir()
    temporary.mkdir()

    result = session_preflight.probe_temp_root(temporary, repo_root=repository)

    assert result["writable"] is True
    assert result["probe_removed"] is True
    assert list(temporary.iterdir()) == []


def test_temp_probe_rejects_repository_paths(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    temporary = repository / "tmp"
    temporary.mkdir(parents=True)

    result = session_preflight.probe_temp_root(temporary, repo_root=repository)

    assert result["writable"] is False
    assert result["failure"] == "temporary root must be outside the repository"
    assert list(temporary.iterdir()) == []


def test_temp_probe_rejects_relative_and_missing_roots(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()

    relative = session_preflight.probe_temp_root(
        Path("relative-temp"), repo_root=repository
    )
    missing = session_preflight.probe_temp_root(
        (tmp_path / "missing").resolve(), repo_root=repository
    )

    assert relative["failure"] == "temporary root must be absolute"
    assert missing["failure"] == "temporary root does not exist"


def test_session_preflight_is_routed() -> None:
    assert run_repo.SURFACES["session-preflight"] == (
        REPO_ROOT / "scripts" / "session_preflight.py"
    )

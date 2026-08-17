from __future__ import annotations

import json
from pathlib import Path

from repository_paths import canonical_repository_path, resolve_repository_path


def registered_source_paths(repo_root: Path) -> frozenset[str]:
    manifest_path = repo_root / "archive" / "sources" / "geopolitics" / "source-manifest.json"
    if not manifest_path.is_file():
        return frozenset()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    return frozenset(
        str(row.get("local_path", "")) for row in manifest.get("sources", [])
    )


def source_reference_available(
    repo_root: Path,
    source_path: str,
    *,
    registered: frozenset[str] | None = None,
) -> bool:
    canonical = canonical_repository_path(source_path)
    if resolve_repository_path(repo_root, source_path).is_file():
        return True
    paths = registered if registered is not None else registered_source_paths(repo_root)
    return canonical in paths

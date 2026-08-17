from __future__ import annotations

from pathlib import Path


LEGACY_GEOPOLITICS_ARCHIVE_ROOT = "narrative-geopolitics/archive"
GEOPOLITICS_ARCHIVE_ROOT = "archive/sources/geopolitics"


def canonical_repository_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    if normalized == LEGACY_GEOPOLITICS_ARCHIVE_ROOT:
        return GEOPOLITICS_ARCHIVE_ROOT
    prefix = LEGACY_GEOPOLITICS_ARCHIVE_ROOT + "/"
    if normalized.startswith(prefix):
        return GEOPOLITICS_ARCHIVE_ROOT + "/" + normalized.removeprefix(prefix)
    return normalized


def resolve_repository_path(repo_root: Path, value: str) -> Path:
    return repo_root / canonical_repository_path(value)

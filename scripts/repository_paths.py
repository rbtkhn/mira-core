from __future__ import annotations

from pathlib import Path, PurePosixPath


LEGACY_GEOPOLITICS_ARCHIVE_ROOT = "narrative-geopolitics/archive"
GEOPOLITICS_ARCHIVE_ROOT = "archive/sources/geopolitics"


def canonical_repository_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    if normalized.startswith("mira/continuity/captures/"):
        suffix = normalized.removeprefix("mira/continuity/captures/")
        if ".." in PurePosixPath(suffix).parts or ":" in suffix:
            raise ValueError("Unsafe session reference")
        return "archive/sessions/transcripts/" + suffix
    if normalized == LEGACY_GEOPOLITICS_ARCHIVE_ROOT:
        return GEOPOLITICS_ARCHIVE_ROOT
    prefix = LEGACY_GEOPOLITICS_ARCHIVE_ROOT + "/"
    if normalized.startswith(prefix):
        return GEOPOLITICS_ARCHIVE_ROOT + "/" + normalized.removeprefix(prefix)
    return normalized


def resolve_repository_path(repo_root: Path, value: str) -> Path:
    canonical = canonical_repository_path(value)
    target = repo_root / canonical
    if canonical.startswith("archive/sessions/transcripts/"):
        if ".." in PurePosixPath(canonical).parts or not target.resolve().is_relative_to(repo_root.resolve()):
            raise ValueError("Session reference escapes repository")
        old = repo_root / ("mira/continuity/captures/" + canonical.removeprefix("archive/sessions/transcripts/"))
        # Preserved rollback copies may coexist only with byte-identical content.
        if old.is_file() and target.is_file() and old.read_bytes() != target.read_bytes():
            raise ValueError("Conflicting historical session capture bytes")
        if not target.exists() and old.exists():
            return old
        return target
    return target

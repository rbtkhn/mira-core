from __future__ import annotations

from pathlib import Path, PurePosixPath


LEGACY_GEOPOLITICS_ARCHIVE_ROOT = "narrative-geopolitics/archive"
GEOPOLITICS_ARCHIVE_ROOT = "archive/sources/geopolitics"


# Opt-in domain migration. Existing repository-path callers retain their behavior.
LEGACY_GEOPOLITICS_ROOT = "narrative-geopolitics"
GEOPOLITICS_ROOT = "geopolitics"


def canonical_geopolitics_reference(value: str) -> str:
    """Normalize a repository-relative reference, never its stored identity.

    The archive relocation takes precedence over the domain rename. Safe
    unrelated references pass through; callers can normalize mixed records.
    """
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (not normalized or path.is_absolute() or ":" in normalized
            or "\x00" in normalized
            or any(part in ("", ".", "..") or part.endswith((" ", "."))
                   for part in normalized.rstrip("/").split("/"))):
        raise ValueError(f"Unsafe geopolitics reference: {value!r}")
    normalized = path.as_posix()
    # A historical relative archive link moves with its containing domain file.
    # Accept that projected alias after the domain rename as well.
    for archive_alias in (LEGACY_GEOPOLITICS_ARCHIVE_ROOT, "geopolitics/archive"):
        if normalized == archive_alias:
            return GEOPOLITICS_ARCHIVE_ROOT
        if normalized.startswith(archive_alias + "/"):
            return GEOPOLITICS_ARCHIVE_ROOT + normalized[len(archive_alias):]
    if normalized == LEGACY_GEOPOLITICS_ROOT:
        return GEOPOLITICS_ROOT
    if normalized.startswith(LEGACY_GEOPOLITICS_ROOT + "/"):
        return GEOPOLITICS_ROOT + normalized[len(LEGACY_GEOPOLITICS_ROOT):]
    return normalized


def geopolitics_reference_for_read(repo_root: Path, value: str) -> Path:
    """Locate an optional read surface without requiring an installed domain.

    With neither physical domain present, return its absent canonical location
    so readers can report missing optional data. Ambiguous or unsafe roots still
    fail. Writers must use resolve_geopolitics_reference instead.
    """
    normalized = canonical_geopolitics_reference(value)
    if normalized == GEOPOLITICS_ROOT or normalized.startswith(GEOPOLITICS_ROOT + "/"):
        occupied = False
        for name in (LEGACY_GEOPOLITICS_ROOT, GEOPOLITICS_ROOT):
            try:
                (repo_root / name).lstat()
                occupied = True
            except FileNotFoundError:
                pass
        if not occupied:
            return _contained_geopolitics_path(repo_root, repo_root / normalized)
    return resolve_geopolitics_reference(repo_root, normalized)


def _contained_geopolitics_path(repo_root: Path, target: Path) -> Path:
    if not target.resolve().is_relative_to(repo_root.resolve()):
        raise ValueError(f"Geopolitics reference escapes repository: {target}")
    return target


def geopolitics_root(repo_root: Path) -> Path:
    """Select exactly one existing physical root without creating or moving it."""
    candidates = []
    for name in (LEGACY_GEOPOLITICS_ROOT, GEOPOLITICS_ROOT):
        target = repo_root / name
        try:
            target.lstat()  # Count dangling links as occupied, too.
        except FileNotFoundError:
            continue
        candidates.append(target)
    if len(candidates) != 1:
        raise ValueError("Expected exactly one geopolitics directory (old or new)")
    target = _contained_geopolitics_path(repo_root, candidates[0])
    if not target.is_dir():
        raise ValueError(f"Geopolitics root is not a directory: {target}")
    return target


def resolve_geopolitics_reference(repo_root: Path, value: str) -> Path:
    """Read either domain spelling before or after cutover; never write records.

    Archive and unrelated references do not require a domain directory. A
    missing leaf is returned for the caller to check; no fallback copy is used.
    """
    canonical = canonical_geopolitics_reference(value)
    if canonical == GEOPOLITICS_ROOT:
        return geopolitics_root(repo_root)
    if canonical.startswith(GEOPOLITICS_ROOT + "/"):
        target = geopolitics_root(repo_root) / canonical.removeprefix(GEOPOLITICS_ROOT + "/")
    else:
        target = resolve_repository_path(repo_root, canonical)
    return _contained_geopolitics_path(repo_root, target)


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

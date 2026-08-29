from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PRIVATE_ROOT = REPO_ROOT / ".mira-private"
LOCAL_RUNTIME_ENV = "MIRA_CORE_LOCAL_ROOT"


class PortablePathError(ValueError):
    pass


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def require_private_path(
    raw_path: str | Path,
    *,
    label: str,
    repo_root: Path = REPO_ROOT,
    private_root: Path | None = None,
) -> Path:
    """Allow external private paths and the one designated ignored in-root tree."""

    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        raise PortablePathError(f"{label} path must be absolute")
    lexical = path.absolute()
    lexical_repository = repo_root.absolute()
    lexical_designated = (private_root or (repo_root / ".mira-private")).absolute()
    resolved = path.resolve(strict=False)
    repository = repo_root.resolve(strict=False)
    designated = (private_root or (repo_root / ".mira-private")).resolve(strict=False)
    if resolved == repository:
        raise PortablePathError(f"{label} path cannot be the repository root")
    if is_within(lexical, lexical_repository):
        if not is_within(lexical, lexical_designated):
            raise PortablePathError(
                f"{label} path must be outside the repository or within {lexical_designated}"
            )
        if not is_within(designated, repository) or not is_within(resolved, designated):
            raise PortablePathError(f"{label} path escapes the designated private root")
    elif is_within(resolved, repository):
        raise PortablePathError(
            f"{label} path must be outside the repository or within {designated}"
        )
    return resolved


def require_bundle_child(
    raw_path: str | Path,
    *,
    label: str,
    repo_root: Path = REPO_ROOT,
) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = repo_root / path
    resolved = path.resolve(strict=False)
    if not is_within(resolved, repo_root):
        raise PortablePathError(f"{label} must remain inside the existing Mira Core root")
    return resolved


def local_runtime_root(environment: dict[str, str] | None = None) -> Path:
    """Return the machine-local Mira Core root for cache and temporary state."""

    source = os.environ if environment is None else environment
    configured = source.get(LOCAL_RUNTIME_ENV)
    if configured:
        return Path(configured).expanduser()
    if os.name == "nt":
        base = source.get("LOCALAPPDATA")
        root = Path(base) if base else Path.home() / "AppData" / "Local"
        return root / "MiraCore"
    base = source.get("XDG_CACHE_HOME")
    root = Path(base) if base else Path.home() / ".cache"
    return root / "mira-core"


def legacy_external_private_root() -> Path:
    """Legacy import-only private root retained for compatibility reads."""

    return Path("C:/private")

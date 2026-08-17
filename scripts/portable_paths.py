from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PRIVATE_ROOT = REPO_ROOT / ".mira-private"


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
    resolved = path.resolve(strict=False)
    repository = repo_root.resolve(strict=False)
    designated = (private_root or (repo_root / ".mira-private")).resolve(strict=False)
    if resolved == repository:
        raise PortablePathError(f"{label} path cannot be the repository root")
    if is_within(resolved, repository) and not is_within(resolved, designated):
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

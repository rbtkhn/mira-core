from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_ROOT_ENV = "MIRA_CORE_STATE_ROOT"

class PortablePathError(ValueError):
    pass

def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False

def git_checkout_root(path: Path) -> Path | None:
    """Return the nearest Git checkout containing *path*, including worktrees."""
    resolved = path.resolve(strict=False)
    current = resolved if resolved.is_dir() else resolved.parent
    for candidate in (current, *current.parents):
        marker = candidate / ".git"
        if marker.is_dir() or marker.is_file():
            return candidate
    return None

def platform_state_root(*, environment: Mapping[str, str] = os.environ, platform: str = sys.platform, home: Path | None = None) -> Path:
    home = (home or Path.home()).expanduser()
    if platform.startswith("win"):
        local = environment.get("LOCALAPPDATA")
        if not local:
            raise PortablePathError("LOCALAPPDATA is required on Windows")
        return Path(local).expanduser() / "MiraCore"
    if platform == "darwin":
        return home / "Library" / "Application Support" / "MiraCore"
    xdg = environment.get("XDG_STATE_HOME")
    return (Path(xdg).expanduser() if xdg else home / ".local" / "state") / "mira-core"

def resolve_state_root(explicit: str | Path | None = None, *, environment: Mapping[str, str] = os.environ, repo_root: Path = REPO_ROOT, platform: str = sys.platform, home: Path | None = None) -> Path:
    configured = explicit or environment.get(STATE_ROOT_ENV)
    path = Path(configured).expanduser() if configured else platform_state_root(environment=environment, platform=platform, home=home)
    if not path.is_absolute():
        raise PortablePathError(f"{STATE_ROOT_ENV} path must be absolute")
    resolved = path.resolve(strict=False)
    repository = repo_root.resolve(strict=False)
    if resolved == repository or is_within(resolved, repository):
        raise PortablePathError("Mira Core state root must be outside the repository")
    checkout = git_checkout_root(resolved)
    if checkout is not None:
        raise PortablePathError(f"Mira Core state root must be outside every Git checkout: {checkout}")
    return resolved

def state_path(relative: str | Path, *, root: str | Path | None = None, environment: Mapping[str, str] = os.environ, repo_root: Path = REPO_ROOT) -> Path:
    child = Path(relative)
    if child.is_absolute() or ".." in child.parts:
        raise PortablePathError("state path must be a safe relative path")
    resolved_root = resolve_state_root(root, environment=environment, repo_root=repo_root)
    resolved = (resolved_root / child).resolve(strict=False)
    if not is_within(resolved, resolved_root):
        raise PortablePathError("state path escapes the Mira Core state root")
    return resolved

def resolve_service_path(explicit: str | Path | None, *, environment_name: str, relative: str | Path, environment: Mapping[str, str] = os.environ, repo_root: Path = REPO_ROOT) -> Path:
    configured = explicit or environment.get(environment_name)
    if configured:
        return require_private_path(configured, label=environment_name, repo_root=repo_root)
    return state_path(relative, environment=environment, repo_root=repo_root)

PRIVATE_ROOT = resolve_state_root()

def require_private_path(raw_path: str | Path, *, label: str, repo_root: Path = REPO_ROOT, private_root: Path | None = None, allow_git_checkout: bool = False) -> Path:
    """Require an absolute path outside Git; no ignored in-repository exception remains."""
    del private_root
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        raise PortablePathError(f"{label} path must be absolute")
    resolved = path.resolve(strict=False)
    repository = repo_root.resolve(strict=False)
    if (resolved == repository or is_within(resolved, repository)) and not allow_git_checkout:
        raise PortablePathError(f"{label} path must be outside the repository")
    checkout = git_checkout_root(resolved)
    if checkout is not None and not allow_git_checkout:
        raise PortablePathError(f"{label} path must be outside every Git checkout: {checkout}")
    return resolved

def require_bundle_child(raw_path: str | Path, *, label: str, repo_root: Path = REPO_ROOT) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = repo_root / path
    resolved = path.resolve(strict=False)
    if not is_within(resolved, repo_root):
        raise PortablePathError(f"{label} must remain inside the existing Mira Core root")
    return resolved

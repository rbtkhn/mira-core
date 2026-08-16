from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import tomllib
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator, Mapping, Sequence

from runtime_names import EnvironmentNameConflict, resolve_environment


MINIMUM_PYTHON = (3, 11)
SCHEMA_VERSION = 1
LOCK_TIMEOUT_SECONDS = 120.0
STALE_LOCK_SECONDS = 600.0
REPO_ROOT = Path(__file__).resolve().parent.parent


class BootstrapUnavailable(RuntimeError):
    """Raised when a usable validation interpreter cannot be prepared."""


def dependency_declarations(pyproject_path: Path) -> tuple[str, ...]:
    with pyproject_path.open("rb") as stream:
        document = tomllib.load(stream)
    project = document.get("project", {})
    dependencies = project.get("dependencies", [])
    optional = project.get("optional-dependencies", {}).get("test", [])
    if not isinstance(dependencies, list) or not isinstance(optional, list):
        raise BootstrapUnavailable(
            "pyproject.toml project dependencies and test extra must be arrays"
        )
    values = (*dependencies, *optional)
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise BootstrapUnavailable("dependency declarations must be non-empty strings")
    return tuple(values)


def default_cache_root(environment: Mapping[str, str] = os.environ) -> Path:
    if os.name == "nt":
        base = environment.get("LOCALAPPDATA")
        root = Path(base) if base else Path.home() / "AppData" / "Local"
        return root / "MiraCore" / "validation"
    base = environment.get("XDG_CACHE_HOME")
    root = Path(base) if base else Path.home() / ".cache"
    return root / "mira-core" / "validation"


def cache_root(
    repo_root: Path = REPO_ROOT,
    environment: Mapping[str, str] = os.environ,
) -> Path:
    configured = resolve_environment("MIRA_CORE_VALIDATION_CACHE", environment)
    result = Path(configured).expanduser() if configured else default_cache_root(environment)
    resolved = result.resolve()
    repository = repo_root.resolve()
    try:
        resolved.relative_to(repository)
    except ValueError:
        return resolved
    raise BootstrapUnavailable(
        f"validation cache must be outside the repository: {resolved}"
    )


def _command_for(value: str) -> list[str] | None:
    path = Path(value).expanduser()
    if path.is_file():
        return [str(path.resolve())]
    found = shutil.which(value)
    return [found] if found else None


def interpreter_candidates(
    environment: Mapping[str, str] = os.environ,
) -> list[list[str]]:
    candidates: list[list[str]] = []
    override = resolve_environment("MIRA_CORE_PYTHON", environment)
    if override:
        command = _command_for(override)
        if not command:
            raise BootstrapUnavailable(f"MIRA_CORE_PYTHON was not found: {override}")
        return [command]
    for value in (
        getattr(sys, "_base_executable", None),
        sys.executable,
        "python3",
        "python",
    ):
        if not value:
            continue
        command = _command_for(str(value))
        if command and command not in candidates:
            candidates.append(command)
    if os.name == "nt" and shutil.which("py"):
        candidates.append([shutil.which("py") or "py", "-3"])
    return candidates


def probe_interpreter(
    command: Sequence[str],
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict:
    program = (
        "import json,platform,sys;"
        "print(json.dumps({'version':list(sys.version_info[:3]),"
        "'implementation':platform.python_implementation(),"
        "'platform':platform.platform(),"
        "'executable':sys.executable,"
        "'base_executable':getattr(sys,'_base_executable',sys.executable)}))"
    )
    try:
        result = run(
            [*command, "-c", program],
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        raise BootstrapUnavailable(
            f"could not inspect Python interpreter {' '.join(command)}: {error}"
        ) from error
    version = tuple(data.get("version", ()))
    if version < MINIMUM_PYTHON:
        raise BootstrapUnavailable(
            f"Python {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]}+ is required; "
            f"{' '.join(command)} reported {'.'.join(map(str, version))}"
        )
    return data


def select_interpreter(
    environment: Mapping[str, str] = os.environ,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> tuple[list[str], dict]:
    failures: list[str] = []
    for command in interpreter_candidates(environment):
        try:
            return command, probe_interpreter(command, run)
        except BootstrapUnavailable as error:
            failures.append(str(error))
            if resolve_environment("MIRA_CORE_PYTHON", environment):
                break
    detail = "; ".join(failures) or "no Python interpreter was found"
    raise BootstrapUnavailable(detail)


def environment_key(dependencies: Sequence[str], interpreter: Mapping[str, object]) -> str:
    identity = {
        "schema": SCHEMA_VERSION,
        "dependencies": list(dependencies),
        "implementation": interpreter["implementation"],
        "version": interpreter["version"],
        "platform": interpreter["platform"],
        "base_executable": str(interpreter["base_executable"]).casefold(),
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:20]


def environment_python(environment_dir: Path) -> Path:
    if os.name == "nt":
        return environment_dir / "Scripts" / "python.exe"
    return environment_dir / "bin" / "python"


def _complete_environment(environment_dir: Path, expected_key: str) -> bool:
    marker = environment_dir / ".narrative-bootstrap.json"
    python = environment_python(environment_dir)
    if not marker.is_file() or not python.is_file():
        return False
    try:
        return json.loads(marker.read_text(encoding="utf-8")).get("key") == expected_key
    except (OSError, json.JSONDecodeError):
        return False


@contextmanager
def exclusive_lock(
    lock_dir: Path,
    *,
    timeout: float = LOCK_TIMEOUT_SECONDS,
    stale_after: float = STALE_LOCK_SECONDS,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> Iterator[None]:
    started = monotonic()
    while True:
        try:
            lock_dir.mkdir()
            (lock_dir / "owner.json").write_text(
                json.dumps({"pid": os.getpid(), "created": time.time()}),
                encoding="utf-8",
            )
            break
        except FileExistsError:
            try:
                age = time.time() - lock_dir.stat().st_mtime
                if age > stale_after:
                    shutil.rmtree(lock_dir)
                    continue
            except FileNotFoundError:
                continue
            if monotonic() - started >= timeout:
                raise BootstrapUnavailable(f"timed out waiting for bootstrap lock: {lock_dir}")
            sleep(0.1)
    try:
        yield
    finally:
        shutil.rmtree(lock_dir, ignore_errors=True)


def resolve_validation_python(
    repo_root: Path = REPO_ROOT,
    environment: Mapping[str, str] = os.environ,
    *,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    lock_timeout: float = LOCK_TIMEOUT_SECONDS,
) -> Path:
    dependencies = dependency_declarations(repo_root / "pyproject.toml")
    base_command, interpreter = select_interpreter(environment, run)
    key = environment_key(dependencies, interpreter)
    root = cache_root(repo_root, environment)
    root.mkdir(parents=True, exist_ok=True)
    target = root / f"env-{key}"
    if _complete_environment(target, key):
        return environment_python(target)

    lock = root / f"env-{key}.lock"
    with exclusive_lock(lock, timeout=lock_timeout):
        if _complete_environment(target, key):
            return environment_python(target)
        if target.exists():
            shutil.rmtree(target)
        temporary = root / f"env-{key}.tmp-{os.getpid()}-{uuid.uuid4().hex}"
        print(f"Preparing Mira Core validation environment {key}...", file=sys.stderr)
        try:
            run(
                [*base_command, "-m", "venv", str(temporary)],
                check=True,
                stdout=sys.stderr,
                stderr=sys.stderr,
            )
            python = environment_python(temporary)
            if dependencies:
                run(
                    [str(python), "-m", "pip", "install", *dependencies],
                    check=True,
                    stdout=sys.stderr,
                    stderr=sys.stderr,
                )
            (temporary / ".narrative-bootstrap.json").write_text(
                json.dumps(
                    {"schema": SCHEMA_VERSION, "key": key, "dependencies": dependencies},
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            temporary.rename(target)
        except (OSError, subprocess.CalledProcessError) as error:
            shutil.rmtree(temporary, ignore_errors=True)
            raise BootstrapUnavailable(f"validation environment bootstrap failed: {error}") from error
    return environment_python(target)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare repository validation Python.")
    parser.add_argument("--print-python", action="store_true")
    args = parser.parse_args()
    try:
        python = resolve_validation_python()
    except (BootstrapUnavailable, EnvironmentNameConflict) as error:
        print(f"runtime bootstrap unavailable: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    if args.print_python:
        print(python)


if __name__ == "__main__":
    main()

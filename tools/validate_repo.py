from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from runtime_bootstrap import (  # noqa: E402
    BootstrapUnavailable,
    cache_root,
    dependency_declarations,
    resolve_validation_python,
)
from runtime_names import remove_environment_pair, resolve_environment  # noqa: E402
from session_preflight import probe_temp_root  # noqa: E402


PRIVATE_VALIDATION_ENVIRONMENT_KEYS = (
    "MIRA_CORE_CHOICE_DB",
    "MIRA_CORE_CADENCE_DB",
    "PYTEST_ADDOPTS",
)
TEMP_ROOT_ENV = "MIRA_CORE_SESSION_TEMP_ROOT"
STRUCTURAL_TIMEOUT_SECONDS = 180
PYTEST_TIMEOUT_SECONDS = 600
FULL_RESULT_SCHEMA = 1
TEXT_SUFFIXES = {".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
PRIVATE_TEXT_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|client[_-]?secret|password)\s*[:=]\s*['\"]?[^\s'\"]{8,}"),
    re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
)


@dataclass(frozen=True)
class Change:
    status: str
    path: str


@dataclass(frozen=True)
class FastRoute:
    effective_mode: str
    reasons: tuple[str, ...]
    tests: tuple[str, ...]


FAST_PATH_RULES = (
    (
        re.compile(r"^archive/geopolitics/sources/.+\.md$"),
        (
            "tests/test_smart_intake.py",
            "tests/test_land_best_intake.py",
            "tests/test_role_aware_archive.py",
            "tests/test_voice_reconciliation.py",
        ),
    ),
    (
        re.compile(r"^narrative-geopolitics/work/daily/.+\.(?:md|json)$"),
        (
            "tests/test_daily_run_validation.py",
            "tests/test_daily_issue.py",
            "tests/test_verification.py",
            "tests/test_forecast_triage.py",
        ),
    ),
    (
        re.compile(r"^narrative-geopolitics/voices/[^/]+/source-index\.md$"),
        ("tests/test_voice_reconciliation.py", "tests/test_role_aware_archive.py"),
    ),
    (
        re.compile(r"^narrative-geopolitics/work/comparisons/.+\.md$"),
        ("tests/test_voice_comparison.py",),
    ),
    (
        re.compile(r"^narrative-geopolitics/work/continuity/.+\.md$"),
        ("tests/test_continuity.py",),
    ),
)


def emit_timing(
    *,
    mode: str,
    phase: str,
    seconds: float,
    status: str,
    reason: str | None = None,
) -> None:
    fields = (
        "validation_timing",
        f"mode={mode}",
        f"phase={phase}",
        f"seconds={max(0.0, seconds):.3f}",
        f"status={status}",
    )
    suffix = () if reason is None else (f"reason={reason}",)
    print(" ".join((*fields, *suffix)), file=sys.stderr)


def run_phase(
    command: list[str],
    *,
    mode: str,
    phase: str,
    environment: dict[str, str],
    clock: Callable[[], float],
    timeout_seconds: int,
) -> int:
    started = clock()
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=environment,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        emit_timing(
            mode=mode,
            phase=phase,
            seconds=clock() - started,
            status="timed_out",
            reason=f"limit_{timeout_seconds}s",
        )
        return 124
    except BaseException:
        emit_timing(
            mode=mode,
            phase=phase,
            seconds=clock() - started,
            status="failed",
        )
        raise
    emit_timing(
        mode=mode,
        phase=phase,
        seconds=clock() - started,
        status="passed" if result.returncode == 0 else "failed",
    )
    return result.returncode


def validation_environment(
    source: dict[str, str] | os._Environ[str] | None = None,
) -> dict[str, str]:
    environment = dict(os.environ if source is None else source)
    for key in PRIVATE_VALIDATION_ENVIRONMENT_KEYS:
        if key == "PYTEST_ADDOPTS":
            environment.pop(key, None)
        else:
            remove_environment_pair(key, environment)
    return environment


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the repository or focused tests.")
    parser.add_argument(
        "--mode",
        choices=("full", "fast"),
        default="full",
        help="validation policy; fast fails closed to full for changes outside its allowlist",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="bypass a successful content-equivalent full-validation result",
    )
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        metavar="TEST_PATH",
        help="existing repository-relative file or directory under tests/; repeatable",
    )
    parser.add_argument(
        "--temp-root",
        type=Path,
        help=f"absolute external pytest root; defaults to {TEMP_ROOT_ENV}",
    )
    return parser.parse_args(arguments)


def resolve_temp_root(
    value: Path | None,
    *,
    environment: dict[str, str] | os._Environ[str] | None = None,
    repo_root: Path = REPO_ROOT,
) -> Path:
    source = os.environ if environment is None else environment
    candidate = value
    configured = resolve_environment(TEMP_ROOT_ENV, source)
    if candidate is None and configured:
        candidate = Path(configured)
    if candidate is None:
        raise ValueError(f"--temp-root or {TEMP_ROOT_ENV} is required")
    report = probe_temp_root(candidate, repo_root=repo_root)
    if not report["writable"] or not report["probe_removed"]:
        raise ValueError(report["failure"] or "temporary root preflight failed")
    return Path(report["resolved_root"])


def cleanup_owned_temp(path: Path | None, *, root: Path | None) -> None:
    if path is None or root is None or not path.exists():
        return
    resolved = path.resolve()
    resolved.relative_to(root.resolve())
    shutil.rmtree(resolved)


def focused_test_paths(values: list[str]) -> list[str]:
    tests_root = (REPO_ROOT / "tests").resolve()
    paths: list[str] = []
    for value in values:
        candidate = Path(value)
        if (
            candidate.is_absolute()
            or ".." in candidate.parts
            or "::" in value
            or any(character in value for character in "*?[]")
        ):
            raise ValueError(f"invalid focused test path: {value}")
        resolved = (REPO_ROOT / candidate).resolve()
        if (
            not resolved.is_relative_to(tests_root)
            or not resolved.exists()
            or not (resolved.is_file() or resolved.is_dir())
        ):
            raise ValueError(f"focused test path must exist under tests/: {value}")
        paths.append(candidate.as_posix())
    return paths


def changed_paths(repo_root: Path = REPO_ROOT) -> list[Change]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Change(line[:2], line[3:].replace("\\", "/")) for line in result.stdout.splitlines()]


def fast_route(changes: list[Change]) -> FastRoute:
    if not changes:
        return FastRoute("full", ("no_changes_requires_full_or_cache",), ())

    reasons: list[str] = []
    tests: list[str] = []
    for change in changes:
        status = change.status
        path = change.path
        if any(marker in status for marker in "RDTU") or " -> " in path:
            reasons.append(f"unsafe_git_change:{status.strip() or status}:{path}")
            continue
        if re.fullmatch(r"tests/test_[^/]+\.py", path):
            if status.strip() in {"M", "MM"}:
                tests.append(path)
            else:
                reasons.append(f"new_or_nonmodified_test:{status.strip() or status}:{path}")
            continue
        matched = False
        for pattern, selected_tests in FAST_PATH_RULES:
            if pattern.fullmatch(path):
                tests.extend(selected_tests)
                matched = True
                break
        if not matched:
            reasons.append(f"outside_fast_allowlist:{path}")

    if reasons:
        return FastRoute("full", tuple(reasons), ())
    existing_tests = tuple(
        path for path in dict.fromkeys(tests) if (REPO_ROOT / path).is_file()
    )
    if not existing_tests:
        return FastRoute("full", ("no_existing_tests_for_fast_route",), ())
    return FastRoute("fast", ("all_changes_match_fast_allowlist",), existing_tests)


def private_text_failures(changes: list[Change], repo_root: Path = REPO_ROOT) -> list[str]:
    failures: list[str] = []
    for change in changes:
        path = repo_root / change.path
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"changed text file is not UTF-8: {change.path}")
            continue
        for pattern in PRIVATE_TEXT_PATTERNS:
            if pattern.search(text):
                failures.append(f"possible private or credential material: {change.path}")
                break
    return failures


def repository_files(repo_root: Path = REPO_ROOT) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return sorted(item.decode("utf-8") for item in result.stdout.split(b"\0") if item)


def full_result_fingerprint(
    python: Path,
    repo_root: Path = REPO_ROOT,
    *,
    paths: list[str] | None = None,
) -> str:
    digest = hashlib.sha256()
    runtime = {
        "schema": FULL_RESULT_SCHEMA,
        "python": str(python.resolve()),
        "implementation": sys.implementation.name,
        "version": list(sys.version_info[:3]),
        "dependencies": dependency_declarations(repo_root / "pyproject.toml"),
    }
    digest.update(json.dumps(runtime, sort_keys=True).encode("utf-8"))
    for relative in repository_files(repo_root) if paths is None else sorted(paths):
        path = repo_root / relative
        digest.update(relative.replace("\\", "/").encode("utf-8"))
        digest.update(b"\0")
        if path.is_symlink():
            digest.update(b"symlink\0")
            digest.update(os.readlink(path).encode("utf-8"))
        elif path.is_file():
            digest.update(b"executable\0" if path.stat().st_mode & 0o111 else b"file\0")
            digest.update(path.read_bytes())
        else:
            digest.update(b"missing\0")
        digest.update(b"\0")
    return digest.hexdigest()


def full_result_path(fingerprint: str, environment: dict[str, str]) -> Path:
    return cache_root(REPO_ROOT, environment) / "full-results" / f"{fingerprint}.json"


def has_successful_full_result(path: Path, fingerprint: str) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return False
    return payload == {
        "schema": FULL_RESULT_SCHEMA,
        "fingerprint": fingerprint,
        "result": "passed",
    }


def store_successful_full_result(path: Path, fingerprint: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(
            {"schema": FULL_RESULT_SCHEMA, "fingerprint": fingerprint, "result": "passed"},
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def main(
    arguments: list[str] | None = None,
    *,
    clock: Callable[[], float] | None = None,
) -> int:
    monotonic = time.perf_counter if clock is None else clock
    total_started = monotonic()
    mode = "full"
    final_status = "failed"
    pytest_root: Path | None = None
    temp_root: Path | None = None
    try:
        args = parse_args(arguments)
        try:
            temp_root = resolve_temp_root(args.temp_root)
        except ValueError as error:
            print(f"validation temporary-root error: {error}", file=sys.stderr)
            return 2
        pytest_root = temp_root / f"pytest-{os.getpid()}-{uuid.uuid4().hex}"
        try:
            paths = focused_test_paths(args.paths) if args.paths else []
        except ValueError as error:
            print(f"validation argument error: {error}", file=sys.stderr)
            return 2
        if paths and (args.mode != "full" or args.force):
            print("validation argument error: --path cannot be combined with --mode fast or --force", file=sys.stderr)
            return 2

        changes: list[Change] = []
        route = FastRoute("full", (), ())
        if paths:
            mode = "focused"
        elif args.mode == "fast":
            try:
                changes = changed_paths()
            except subprocess.CalledProcessError as error:
                print(f"validation routing unavailable: git status exited {error.returncode}", file=sys.stderr)
                return 1
            route = fast_route(changes)
            mode = route.effective_mode
            print(
                "validation_route "
                f"requested=fast effective={mode} reasons={json.dumps(route.reasons)} "
                f"tests={json.dumps(route.tests)}",
                file=sys.stderr,
            )

        bootstrap_started = monotonic()
        try:
            python = resolve_validation_python(REPO_ROOT)
        except BootstrapUnavailable as error:
            emit_timing(
                mode=mode,
                phase="bootstrap",
                seconds=monotonic() - bootstrap_started,
                status="failed",
            )
            print(f"validation unavailable: {error}", file=sys.stderr)
            return 1
        emit_timing(
            mode=mode,
            phase="bootstrap",
            seconds=monotonic() - bootstrap_started,
            status="passed",
        )
        environment = validation_environment()
        pytest_paths = paths if paths else list(route.tests)
        pytest_command = [
            str(python),
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "-m",
            "not repository_integrity",
            "--basetemp",
            str(pytest_root),
            *pytest_paths,
        ]
        if paths:
            emit_timing(
                mode=mode,
                phase="structural",
                seconds=0.0,
                status="skipped",
                reason="focused_tests",
            )
            returncode = run_phase(
                pytest_command,
                mode=mode,
                phase="pytest",
                environment=environment,
                clock=monotonic,
                timeout_seconds=PYTEST_TIMEOUT_SECONDS,
            )
            final_status = "passed" if returncode == 0 else "failed"
            return returncode

        if mode == "fast":
            failures = private_text_failures(changes)
            for failure in failures:
                print(f"fast integrity failure: {failure}", file=sys.stderr)
            if failures:
                final_status = "failed"
                return 1
            commands = (
                ("integrity", ["git", "diff", "--check"]),
                ("pytest", pytest_command),
            )
            returncode = 0
            for phase, command in commands:
                phase_returncode = run_phase(
                    command,
                    mode=mode,
                    phase=phase,
                    environment=environment,
                    clock=monotonic,
                    timeout_seconds=(
                        STRUCTURAL_TIMEOUT_SECONDS
                        if phase == "integrity"
                        else PYTEST_TIMEOUT_SECONDS
                    ),
                )
                if phase_returncode and not returncode:
                    returncode = phase_returncode
            final_status = "passed" if returncode == 0 else "failed"
            return returncode

        cache_enabled = arguments is None
        fingerprint: str | None = None
        result_path: Path | None = None
        if cache_enabled:
            try:
                fingerprint = full_result_fingerprint(python)
                result_path = full_result_path(fingerprint, environment)
            except (BootstrapUnavailable, OSError, subprocess.CalledProcessError) as error:
                print(f"validation_cache status=unavailable reason={error}", file=sys.stderr)
            else:
                if not args.force and has_successful_full_result(result_path, fingerprint):
                    print(f"validation_cache status=hit fingerprint={fingerprint}", file=sys.stderr)
                    emit_timing(mode=mode, phase="structural", seconds=0.0, status="skipped", reason="cache_hit")
                    emit_timing(mode=mode, phase="pytest", seconds=0.0, status="skipped", reason="cache_hit")
                    final_status = "passed"
                    return 0
                cache_status = "bypassed" if args.force else "miss"
                print(f"validation_cache status={cache_status} fingerprint={fingerprint}", file=sys.stderr)

        commands = (
            ("structural", [str(python), "scripts/validate_repository.py"]),
            ("pytest", pytest_command),
        )
        returncode = 0
        for phase, command in commands:
            phase_returncode = run_phase(
                command,
                mode=mode,
                phase=phase,
                environment=environment,
                clock=monotonic,
                timeout_seconds=(
                    STRUCTURAL_TIMEOUT_SECONDS
                    if phase == "structural"
                    else PYTEST_TIMEOUT_SECONDS
                ),
            )
            if phase_returncode and not returncode:
                returncode = phase_returncode
        if returncode == 0 and fingerprint is not None and result_path is not None:
            try:
                if full_result_fingerprint(python) == fingerprint:
                    store_successful_full_result(result_path, fingerprint)
                    print(f"validation_cache status=stored fingerprint={fingerprint}", file=sys.stderr)
                else:
                    print("validation_cache status=not_stored reason=repository_changed_during_validation", file=sys.stderr)
            except (OSError, subprocess.CalledProcessError) as error:
                print(f"validation_cache status=not_stored reason={error}", file=sys.stderr)
        final_status = "passed" if returncode == 0 else "failed"
        return returncode
    finally:
        cleanup_owned_temp(pytest_root, root=temp_root)
        emit_timing(
            mode=mode,
            phase="total",
            seconds=monotonic() - total_started,
            status=final_status,
        )


if __name__ == "__main__":
    raise SystemExit(main())

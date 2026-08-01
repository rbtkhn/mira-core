from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


bootstrap = load_module("runtime_bootstrap_tests", REPO_ROOT / "scripts" / "runtime_bootstrap.py")
runner = load_module("run_repo_tests", REPO_ROOT / "tools" / "run_repo.py")
validator = load_module("validate_repo_tests", REPO_ROOT / "tools" / "validate_repo.py")
repository_validation = load_module(
    "governed_command_validation_tests", REPO_ROOT / "scripts" / "validate_repository.py"
)


EXPECTED_SURFACES = {
    "archive-audit": "archive_audit.py",
    "archive-density": "report_archive_density.py",
    "asr-repair": "run_asr_repair_pilot.py",
    "cadence": "cadence.py",
    "choice": "choice_ledger.py",
    "continuity": "continuity.py",
    "daily-validate": "validate_daily_run.py",
    "elicitation": "elicitation.py",
    "forecast-sync": "sync_forecast_ledger.py",
    "forecast-triage": "triage_forecast_ledger.py",
    "harness": "audit_ai_harness.py",
    "intake-land": "smart_intake.py",
    "intake-outcomes": "report_intake_outcomes.py",
    "intake-stats": "report_trim_stats.py",
    "issue-render": "render_daily_issue.py",
    "narrative-reuse": "report_narrative_reuse.py",
    "operator-position": "operator_positions.py",
    "reality": "reality.py",
    "skills-check": "check_codex_skills_sync.py",
    "skills-sync": "sync_codex_skills.py",
    "synthesis": "geopolitical_synthesis.py",
    "verification": "verification.py",
    "voice-accountability": "voice_accountability.py",
    "voice-canonicalize": "canonicalize_voice_metadata.py",
    "voice-sync": "sync_voice_indexes.py",
    "voice-comparison": "voice_comparison.py",
}


def write_pyproject(root: Path, dependencies: str = 'test = ["pytest>=8"]') -> None:
    (root / "pyproject.toml").write_text(
        """[project]
dependencies = []
[project.optional-dependencies]
"""
        + dependencies
        + "\n",
        encoding="utf-8",
    )


def interpreter() -> dict:
    return {
        "version": [3, 11, 9],
        "implementation": "CPython",
        "platform": "test-platform",
        "executable": "/temporary/venv/python",
        "base_executable": "/stable/base/python",
    }


def test_reads_project_and_test_dependencies(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """[project]
dependencies = ["example>=1"]
[project.optional-dependencies]
test = ["pytest>=8", "coverage"]
""",
        encoding="utf-8",
    )
    assert bootstrap.dependency_declarations(tmp_path / "pyproject.toml") == (
        "example>=1",
        "pytest>=8",
        "coverage",
    )


def test_environment_key_is_deterministic_and_uses_base_interpreter() -> None:
    first = interpreter()
    second = interpreter() | {"executable": "/another/venv/python"}
    assert bootstrap.environment_key(("pytest>=8",), first) == bootstrap.environment_key(
        ("pytest>=8",), second
    )
    assert bootstrap.environment_key(("pytest>=9",), first) != bootstrap.environment_key(
        ("pytest>=8",), first
    )


def test_rejects_repo_local_cache(tmp_path: Path) -> None:
    with pytest.raises(bootstrap.BootstrapUnavailable, match="outside the repository"):
        bootstrap.cache_root(
            tmp_path,
            {"NARRATIVE_VALIDATION_CACHE": str(tmp_path / ".cache")},
        )


def test_python_minimum_is_enforced() -> None:
    result = subprocess.CompletedProcess(
        ["python"],
        0,
        stdout=json.dumps(interpreter() | {"version": [3, 10, 14]}),
        stderr="",
    )
    with pytest.raises(bootstrap.BootstrapUnavailable, match="3.11"):
        bootstrap.probe_interpreter(["python"], lambda *args, **kwargs: result)


def fake_bootstrap_run(calls: list[list[str]], *, fail_install: bool = False):
    def run(command, **kwargs):
        values = [str(value) for value in command]
        calls.append(values)
        if "-c" in values:
            return subprocess.CompletedProcess(values, 0, json.dumps(interpreter()), "")
        if "venv" in values:
            target = Path(values[-1])
            python = bootstrap.environment_python(target)
            python.parent.mkdir(parents=True)
            python.write_text("python", encoding="utf-8")
        elif "install" in values and fail_install:
            raise subprocess.CalledProcessError(1, values)
        return subprocess.CompletedProcess(values, 0, "", "")

    return run


def test_bootstrap_recovers_partial_environment_and_reuses_completed_cache(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    cache = tmp_path / "cache"
    repo.mkdir()
    write_pyproject(repo)
    monkeypatch.setattr(bootstrap, "select_interpreter", lambda environment, run: (["base-python"], interpreter()))
    key = bootstrap.environment_key(("pytest>=8",), interpreter())
    partial = cache / f"env-{key}"
    partial.mkdir(parents=True)
    (partial / "broken").write_text("partial", encoding="utf-8")
    calls: list[list[str]] = []
    environment = {"NARRATIVE_VALIDATION_CACHE": str(cache)}

    first = bootstrap.resolve_validation_python(repo, environment, run=fake_bootstrap_run(calls))
    assert first.is_file()
    assert not (partial / "broken").exists()
    install_count = sum("install" in call for call in calls)

    second = bootstrap.resolve_validation_python(repo, environment, run=fake_bootstrap_run(calls))
    assert second == first
    assert sum("install" in call for call in calls) == install_count


def test_failed_install_removes_temporary_environment(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    cache = tmp_path / "cache"
    repo.mkdir()
    write_pyproject(repo)
    monkeypatch.setattr(bootstrap, "select_interpreter", lambda environment, run: (["base-python"], interpreter()))
    with pytest.raises(bootstrap.BootstrapUnavailable, match="bootstrap failed"):
        bootstrap.resolve_validation_python(
            repo,
            {"NARRATIVE_VALIDATION_CACHE": str(cache)},
            run=fake_bootstrap_run([], fail_install=True),
        )
    assert not list(cache.glob("*.tmp-*"))


def test_lock_times_out_and_stale_lock_is_recovered(tmp_path: Path) -> None:
    lock = tmp_path / "held.lock"
    lock.mkdir()
    with pytest.raises(bootstrap.BootstrapUnavailable, match="timed out"):
        with bootstrap.exclusive_lock(lock, timeout=0, stale_after=999):
            pass
    old = time.time() - 100
    os.utime(lock, (old, old))
    with bootstrap.exclusive_lock(lock, timeout=1, stale_after=1):
        assert lock.exists()
    assert not lock.exists()


def test_concurrent_first_creation_installs_once(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    cache = tmp_path / "cache"
    repo.mkdir()
    write_pyproject(repo)
    monkeypatch.setattr(bootstrap, "select_interpreter", lambda environment, run: (["base-python"], interpreter()))
    calls: list[list[str]] = []
    guarded = threading.Lock()
    base_run = fake_bootstrap_run(calls)

    def slow_run(command, **kwargs):
        with guarded:
            if "venv" in [str(value) for value in command]:
                time.sleep(0.05)
            return base_run(command, **kwargs)

    results: list[Path] = []
    errors: list[Exception] = []

    def resolve() -> None:
        try:
            results.append(
                bootstrap.resolve_validation_python(
                    repo,
                    {"NARRATIVE_VALIDATION_CACHE": str(cache)},
                    run=slow_run,
                )
            )
        except Exception as error:  # pragma: no cover - assertion reports the error
            errors.append(error)

    threads = [threading.Thread(target=resolve) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []
    assert len(set(results)) == 1
    assert sum("install" in call for call in calls) == 1


def test_runner_allowlists_surfaces_and_propagates_arguments(monkeypatch) -> None:
    observed = {}

    def run(command, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        return SimpleNamespace(returncode=17)

    monkeypatch.setattr(runner.subprocess, "run", run)
    assert runner.main(["cadence", "coffee", "--json"]) == 17
    assert observed["command"][-2:] == ["coffee", "--json"]
    assert Path(observed["command"][1]) == runner.SURFACES["cadence"]
    assert observed["kwargs"]["env"]["PYTHONPATH"].split(os.pathsep)[0] == str(
        REPO_ROOT / "scripts"
    )
    assert runner.main(["unknown"]) == 2


def test_registry_is_complete_unique_and_bounded_to_scripts() -> None:
    assert {name: path.name for name, path in runner.SURFACES.items()} == EXPECTED_SURFACES
    scripts_root = (REPO_ROOT / "scripts").resolve()
    for target in runner.SURFACES.values():
        assert target.is_file()
        assert target.resolve().parent == scripts_root


def test_runner_preserves_read_and_write_surface_arguments(monkeypatch) -> None:
    commands: list[list[str]] = []
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda command, **kwargs: commands.append(command) or SimpleNamespace(returncode=0),
    )
    assert runner.main(["archive-audit", "--whole-corpus", "--voice-slug", "davis", "--format", "json"]) == 0
    assert runner.main(["archive-density", "--month", "2026-07"]) == 0
    assert runner.main(["skills-sync", "--skill", "reality-check", "--dry-run"]) == 0
    assert commands[0][-5:] == ["--whole-corpus", "--voice-slug", "davis", "--format", "json"]
    assert commands[1][-2:] == ["--month", "2026-07"]
    assert commands[2][-3:] == ["--skill", "reality-check", "--dry-run"]


def test_environment_argument_transport_is_exact_and_consumed() -> None:
    expected = [
        "elicitation",
        "validate",
        "--surface-json",
        '{"type":"neutral-evidence","label":"Quoted \\"value\\" and Καλημέρα"}',
        "",
    ]
    environment = {
        runner.ARGUMENTS_ENV: json.dumps(expected, ensure_ascii=False)
    }
    assert runner.resolve_arguments([runner.ARGUMENTS_ENV_FLAG], environment) == expected
    assert runner.ARGUMENTS_ENV not in environment


@pytest.mark.parametrize(
    "payload",
    (
        "not-json",
        '{"surface":"not-a-list"}',
        '["valid", 3]',
    ),
)
def test_environment_argument_transport_rejects_invalid_payloads(payload: str) -> None:
    environment = {runner.ARGUMENTS_ENV: payload}
    with pytest.raises(ValueError):
        runner.resolve_arguments([runner.ARGUMENTS_ENV_FLAG], environment)
    assert runner.ARGUMENTS_ENV not in environment


def test_environment_argument_transport_is_not_mixed_with_direct_arguments() -> None:
    environment = {runner.ARGUMENTS_ENV: '["cadence"]'}
    with pytest.raises(ValueError, match="only command-line argument"):
        runner.resolve_arguments(
            [runner.ARGUMENTS_ENV_FLAG, "cadence"], environment
        )
    assert runner.ARGUMENTS_ENV in environment


def test_runner_removes_transport_environment_before_child(monkeypatch) -> None:
    observed: dict[str, object] = {}
    monkeypatch.setenv(
        runner.ARGUMENTS_ENV,
        json.dumps(["archive-density", "--month", "2026-07"]),
    )

    def run(command, **kwargs):
        observed["command"] = command
        observed["environment"] = kwargs["env"]
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.subprocess, "run", run)
    assert runner.main([runner.ARGUMENTS_ENV_FLAG]) == 0
    assert observed["command"][-2:] == ["--month", "2026-07"]
    assert runner.ARGUMENTS_ENV not in observed["environment"]
    assert runner.ARGUMENTS_ENV not in os.environ


def test_powershell_runner_forwards_all_arguments() -> None:
    launcher = (REPO_ROOT / "tools" / "run.ps1").read_text(encoding="utf-8")
    assert "[Parameter(ValueFromRemainingArguments = $true)]" in launcher
    assert "ConvertTo-Json -Compress -InputObject @($RunArguments)" in launcher
    assert "$runner --arguments-env" in launcher
    assert "$previousArguments" in launcher


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="PowerShell argument transport is Windows-specific",
)
def test_powershell_runner_round_trips_inline_json_and_restores_environment() -> None:
    powershell = Path(
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    )
    command = r"""
$env:NARRATIVE_PYTHON = $env:TEST_VALIDATION_PYTHON
$env:NARRATIVE_RUN_ARGUMENTS_JSON = 'pre-existing'
$surface = [ordered]@{
    type = 'neutral-evidence'
    options = @(
        [ordered]@{ key = 'yes'; label = 'Yes with spaces' },
        [ordered]@{ key = 'no'; label = 'Καλημέρα "quoted"' }
    )
}
$surfaceJson = $surface | ConvertTo-Json -Depth 4 -Compress
.\tools\run.ps1 elicitation validate --surface-json $surfaceJson
Write-Output ('RESTORED=' + $env:NARRATIVE_RUN_ARGUMENTS_JSON)
"""
    environment = os.environ.copy()
    environment["TEST_VALIDATION_PYTHON"] = sys.executable
    result = subprocess.run(
        [str(powershell), "-NoProfile", "-Command", command],
        cwd=REPO_ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    json_text, restored = result.stdout.rsplit("RESTORED=", 1)
    assert "\\u039a" in json_text
    payload = json.loads(json_text)
    assert payload["options"][0]["label"] == "Yes with spaces"
    assert payload["options"][1]["label"] == 'Καλημέρα "quoted"'
    assert restored.strip() == "pre-existing"


def test_named_runner_preserves_json_stdout() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "run_repo.py"), "cadence", "coffee", "--json"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert "handoff_status" in payload


@pytest.mark.parametrize(
    "line",
    (
        r".\scripts\python.ps1 scripts\reality.py check --all",
        r".\.venv\Scripts\python.exe -m pytest",
        "py -3 -m venv .venv",
        "python -m pytest",
        "python scripts/reality.py check --all",
        r"C:\Users\person\private\python.exe scripts\reality.py",
    ),
)
def test_obsolete_active_guidance_is_rejected(tmp_path: Path, line: str) -> None:
    path = tmp_path / "guide.md"
    path.write_text(line + "\n", encoding="utf-8")
    assert repository_validation.obsolete_guidance_failures([path], tmp_path)


def test_governed_commands_and_generic_placeholders_are_allowed(tmp_path: Path) -> None:
    path = tmp_path / "guide.md"
    path.write_text(
        ".\\tools\\run.ps1 intake-land --batch-dir C:\\path\\to\\batch\n"
        ".\\tools\\validate.ps1\n",
        encoding="utf-8",
    )
    assert repository_validation.obsolete_guidance_failures([path], tmp_path) == []


def test_historical_territories_are_not_active_guidance() -> None:
    paths = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in repository_validation.active_guidance_files(REPO_ROOT)
    }
    assert not any("/archive/" in path for path in paths)
    assert not any("/work/daily/" in path for path in paths)
    assert not any("/work/audits/" in path for path in paths)
    assert "narrative-geopolitics/work/june-backfill-demo-sequence.md" not in paths
    assert "narrative-geopolitics/work/asr-repair-pilot-findings-july-2026.md" in paths


def test_normative_repository_guidance_has_no_obsolete_commands() -> None:
    assert repository_validation.obsolete_guidance_failures() == []


def test_ci_uses_only_canonical_validation_with_four_jobs() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "validate.yml").read_text(
        encoding="utf-8"
    )
    assert 'python-version: ["3.11", "3.13"]' in workflow
    assert "os: [ubuntu-latest, windows-latest]" in workflow
    assert workflow.count("python tools/validate_repo.py") == 1
    assert "pytest" not in workflow
    assert "validate_repository.py" not in workflow


def test_validator_uses_one_interpreter_and_runs_both_checks(monkeypatch) -> None:
    python = Path("resolved-python")
    commands: list[list[str]] = []
    monkeypatch.setattr(validator, "resolve_validation_python", lambda repo: python)

    def run(command, **kwargs):
        commands.append(command)
        failed = any(value.endswith("validate_repository.py") for value in command)
        return SimpleNamespace(returncode=4 if failed else 0)

    monkeypatch.setattr(validator.subprocess, "run", run)
    assert validator.main() == 4
    assert len(commands) == 2
    assert all(command[0] == str(python) for command in commands)
    assert commands[0][1] == "scripts/validate_repository.py"
    assert commands[1][1:4] == ["-m", "pytest", "-q"]


def test_compatibility_shim_no_longer_requires_dot_venv() -> None:
    shim = (REPO_ROOT / "scripts" / "python.ps1").read_text(encoding="utf-8")
    assert "DEPRECATED" in shim
    assert ".venv" not in shim
    assert "runtime_bootstrap.py" in shim

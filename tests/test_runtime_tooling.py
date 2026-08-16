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
    "archive-repair": "archive_repair.py",
    "asr-repair": "run_asr_repair_pilot.py",
    "cadence": "cadence.py",
    "choice": "choice_ledger.py",
    "continuity": "continuity.py",
    "contradiction-check": "contradiction_check.py",
    "daily-validate": "validate_daily_run.py",
    "elicitation": "elicitation.py",
    "forecast-sync": "sync_forecast_ledger.py",
    "forecast-triage": "triage_forecast_ledger.py",
    "harness": "audit_ai_harness.py",
    "intake-land": "smart_intake.py",
    "intake-outcomes": "report_intake_outcomes.py",
    "intake-stats": "report_trim_stats.py",
    "innermost-loop-simulation": "innermost_loop_simulation.py",
    "issue-render": "render_daily_issue.py",
    "morning-brief": "morning_brief.py",
    "mira-continuity": "mira_continuity.py",
    "mira-mentor": "mentorship_ledger.py",
    "mira-constitution": "mira_constitution.py",
    "mira-journal": "mira_journal.py",
    "mira-memory": "mira_memory.py",
    "mechanism-lens-checklist": "mechanism_lens_checklist.py",
    "narrative-reuse": "report_narrative_reuse.py",
    "operator-position": "operator_positions.py",
    "reality": "reality.py",
    "reality-handoff": "reality_handoff.py",
    "recursive-learn": "recursive_learning_ledger.py",
    "research-handoff": "research_handoff.py",
    "session-preflight": "session_preflight.py",
    "skills-check": "check_codex_skills_sync.py",
    "skills-sync": "sync_codex_skills.py",
    "synthesis": "geopolitical_synthesis.py",
    "system-archive": "system_archive.py",
    "test": "validate_repo.py",
    "verification": "verification.py",
    "voice-accountability": "voice_accountability.py",
    "voice-judgment": "voice_judgments.py",
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
    assert "capture_output" not in observed["kwargs"]
    assert "stdout" not in observed["kwargs"]
    assert "stderr" not in observed["kwargs"]
    assert runner.main(["unknown"]) == 2


def test_registry_is_complete_unique_and_bounded_to_scripts() -> None:
    assert {name: path.name for name, path in runner.SURFACES.items()} == EXPECTED_SURFACES
    scripts_root = (REPO_ROOT / "scripts").resolve()
    for name, target in runner.SURFACES.items():
        assert target.is_file()
        expected_parent = (REPO_ROOT / "tools").resolve() if name == "test" else scripts_root
        assert target.resolve().parent == expected_parent


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


def test_runner_preserves_archive_repair_authority_binding(monkeypatch) -> None:
    commands: list[list[str]] = []
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda command, **kwargs: commands.append(command) or SimpleNamespace(returncode=0),
    )
    target = "narrative-geopolitics/archive/sources/2026-07-31/source-example.md"
    digest = "a" * 64
    assert runner.main(
        [
            "archive-repair",
            "--class",
            "asr",
            "--path",
            target,
            "--execute",
            "--plan-digest",
            digest,
            "--format",
            "json",
        ]
    ) == 0
    assert commands[0][-9:] == [
        "--class",
        "asr",
        "--path",
        target,
        "--execute",
        "--plan-digest",
        digest,
        "--format",
        "json",
    ]


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
    assert "scripts\\runtime_bootstrap.py" in launcher
    assert "$bootstrap --print-python" in launcher
    assert "$runner --arguments-env" in launcher
    assert "$previousArguments" in launcher


def test_powershell_entrypoints_choose_one_application_launcher() -> None:
    for relative_path in (
        "tools/run.ps1",
        "tools/validate.ps1",
        "scripts/python.ps1",
    ):
        launcher = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "Get-Command py.exe" in launcher
        assert "-CommandType Application" in launcher
        assert ")[0]" in launcher


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="PowerShell argument transport is Windows-specific",
)
def test_powershell_runner_transport_contract(tmp_path: Path) -> None:
    powershell = Path(
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    )
    capture_path = tmp_path / "transport.jsonl"
    runner_stub = tmp_path / "runner-stub.ps1"
    runner_stub.write_text(
        r"""[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments = $true)][string[]] $Arguments)
$serialized = [Environment]::GetEnvironmentVariable(
    'NARRATIVE_RUN_ARGUMENTS_JSON',
    [EnvironmentVariableTarget]::Process
)
[IO.File]::AppendAllText(
    $env:TEST_TRANSPORT_CAPTURE,
    $serialized + [Environment]::NewLine,
    [Text.UTF8Encoding]::new($false)
)
exit [int]$env:TEST_CHILD_EXIT
""",
        encoding="utf-8",
        newline="\n",
    )
    bootstrap_stub = tmp_path / "bootstrap-stub.ps1"
    bootstrap_stub.write_text(
        "Write-Output $env:TEST_RUNNER_STUB\n"
        "$global:LASTEXITCODE = 0\n",
        encoding="utf-8",
        newline="\n",
    )
    command = r"""
$env:NARRATIVE_PYTHON = $env:TEST_BOOTSTRAP_STUB
$env:NARRATIVE_RUN_ARGUMENTS_JSON = 'pre-existing'
$surface = [ordered]@{
    type = 'neutral-evidence'
    options = @(
        [ordered]@{ key = 'yes'; label = 'Yes with spaces' },
        [ordered]@{ key = 'no'; label = 'Καλημέρα "quoted"' }
    )
}
$surfaceJson = $surface | ConvertTo-Json -Depth 4 -Compress
$env:TEST_CHILD_EXIT = '0'
.\tools\run.ps1 elicitation validate --surface-json $surfaceJson
$firstCode = $LASTEXITCODE
$firstRestored = $env:NARRATIVE_RUN_ARGUMENTS_JSON
$env:TEST_CHILD_EXIT = '19'
.\tools\run.ps1 test `
  --path tests/test_elicitation.py `
  --path tests/test_learn_from_choices_skill.py
$secondCode = $LASTEXITCODE
$secondRestored = $env:NARRATIVE_RUN_ARGUMENTS_JSON
Write-Output (
    'STATUS=' + $firstCode + ':' + $firstRestored + '|' +
    $secondCode + ':' + $secondRestored
)
if ($firstCode -ne 0 -or $secondCode -ne 19) { exit 1 }
"""
    environment = os.environ.copy()
    environment["TEST_BOOTSTRAP_STUB"] = str(bootstrap_stub)
    environment["TEST_RUNNER_STUB"] = str(runner_stub)
    environment["TEST_TRANSPORT_CAPTURE"] = str(capture_path)
    result = subprocess.run(
        [str(powershell), "-NoProfile", "-Command", command],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "STATUS=0:pre-existing|19:pre-existing" in result.stdout
    transported = [
        json.loads(line)
        for line in capture_path.read_text(encoding="utf-8").splitlines()
    ]
    assert transported[0][:3] == ["elicitation", "validate", "--surface-json"]
    payload = json.loads(transported[0][3])
    assert payload["options"][0]["label"] == "Yes with spaces"
    assert payload["options"][1]["label"] == 'Καλημέρα "quoted"'
    assert transported[1] == [
        "test",
        "--path",
        "tests/test_elicitation.py",
        "--path",
        "tests/test_learn_from_choices_skill.py",
    ]


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
    assert "NARRATIVE_SESSION_TEMP_ROOT: ${{ runner.temp }}" in workflow


def test_validation_mode_defaults_to_full_and_accepts_force() -> None:
    default = validator.parse_args([])
    forced = validator.parse_args(["--mode", "full", "--force"])
    assert (default.mode, default.force) == ("full", False)
    assert (forced.mode, forced.force) == ("full", True)
    assert default.temp_root is None


def test_fast_route_selects_tests_for_narrow_allowlisted_changes() -> None:
    route = validator.fast_route(
        [
            validator.Change(
                " M",
                "narrative-geopolitics/archive/sources/2026-08-03/example.md",
            ),
            validator.Change(" M", "tests/test_runtime_tooling.py"),
        ]
    )
    assert route.effective_mode == "fast"
    assert route.reasons == ("all_changes_match_fast_allowlist",)
    assert "tests/test_smart_intake.py" in route.tests
    assert "tests/test_runtime_tooling.py" in route.tests


@pytest.mark.parametrize(
    "change",
    (
        validator.Change(" M", "tools/validate_repo.py"),
        validator.Change("R ", "old.md -> new.md"),
        validator.Change("??", "tests/test_new_contract.py"),
        validator.Change(" M", "narrative-geopolitics/archive/manifest.json"),
    ),
)
def test_fast_route_fails_closed_for_risky_or_unknown_changes(change) -> None:
    route = validator.fast_route([change])
    assert route.effective_mode == "full"
    assert route.reasons
    assert route.tests == ()


def test_full_result_fingerprint_is_content_based(tmp_path: Path) -> None:
    write_pyproject(tmp_path)
    (tmp_path / "tracked.txt").write_text("same content\n", encoding="utf-8")
    first = validator.full_result_fingerprint(
        Path(sys.executable), tmp_path, paths=["pyproject.toml", "tracked.txt"]
    )
    second = validator.full_result_fingerprint(
        Path(sys.executable), tmp_path, paths=["tracked.txt", "pyproject.toml"]
    )
    assert second == first
    (tmp_path / "tracked.txt").write_text("changed content\n", encoding="utf-8")
    assert validator.full_result_fingerprint(
        Path(sys.executable), tmp_path, paths=["pyproject.toml", "tracked.txt"]
    ) != first


def test_successful_full_result_cache_rejects_failure_and_wrong_fingerprint(
    tmp_path: Path,
) -> None:
    record = tmp_path / "full-results" / "abc.json"
    validator.store_successful_full_result(record, "abc")
    assert validator.has_successful_full_result(record, "abc")
    assert not validator.has_successful_full_result(record, "def")
    record.write_text(
        json.dumps({"schema": validator.FULL_RESULT_SCHEMA, "fingerprint": "abc", "result": "failed"}),
        encoding="utf-8",
    )
    assert not validator.has_successful_full_result(record, "abc")


def test_powershell_validator_exposes_fast_full_and_force() -> None:
    launcher = (REPO_ROOT / "tools" / "validate.ps1").read_text(encoding="utf-8")
    assert "[ValidateSet('Full', 'Fast')]" in launcher
    assert "$validatorArguments = @('--mode', $Mode.ToLowerInvariant())" in launcher
    assert "$validatorArguments += '--force'" in launcher
    assert "NARRATIVE_SESSION_TEMP_ROOT" in launcher
    assert "@('--temp-root', $TempRoot)" in launcher
    assert launcher.count("@validatorArguments") == 4


def test_validator_uses_one_interpreter_and_runs_both_checks(monkeypatch, tmp_path: Path) -> None:
    python = Path("resolved-python")
    commands: list[list[str]] = []
    environments: list[dict[str, str]] = []
    monkeypatch.setattr(validator, "resolve_validation_python", lambda repo: python)
    monkeypatch.setenv("NARRATIVE_CHOICE_DB", r"C:\private\real-choice.sqlite3")
    monkeypatch.setenv("PYTEST_ADDOPTS", r"--basetemp C:\unsafe\pytest")
    monkeypatch.setenv("VALIDATION_SENTINEL", "preserved")

    def run(command, **kwargs):
        commands.append(command)
        environments.append(kwargs["env"])
        failed = any(value.endswith("validate_repository.py") for value in command)
        return SimpleNamespace(returncode=4 if failed else 0)

    monkeypatch.setattr(validator.subprocess, "run", run)
    assert validator.main(["--temp-root", str(tmp_path)]) == 4
    assert len(commands) == 2
    assert all(command[0] == str(python) for command in commands)
    assert commands[0][1] == "scripts/validate_repository.py"
    assert commands[1][1:4] == ["-m", "pytest", "-q"]
    marker_index = commands[1].index("not repository_integrity")
    assert commands[1][marker_index - 1 : marker_index + 1] == ["-m", "not repository_integrity"]
    assert "--basetemp" in commands[1]
    assert str(tmp_path) in commands[1][commands[1].index("--basetemp") + 1]
    assert all("NARRATIVE_CHOICE_DB" not in item for item in environments)
    assert all("PYTEST_ADDOPTS" not in item for item in environments)
    assert all(item["VALIDATION_SENTINEL"] == "preserved" for item in environments)
    assert os.environ["NARRATIVE_CHOICE_DB"] == r"C:\private\real-choice.sqlite3"


def test_full_validator_reports_ordered_phase_timings(monkeypatch, capsys, tmp_path: Path) -> None:
    commands: list[list[str]] = []
    times = iter((0.0, 1.0, 2.25, 3.0, 7.5, 8.0, 13.0, 14.0))
    monkeypatch.setattr(
        validator, "resolve_validation_python", lambda repo: Path("resolved-python")
    )

    def run(command, **kwargs):
        commands.append(command)
        failed = command[1].endswith("validate_repository.py")
        return SimpleNamespace(returncode=4 if failed else 0)

    monkeypatch.setattr(validator.subprocess, "run", run)
    assert validator.main(["--temp-root", str(tmp_path)], clock=lambda: next(times)) == 4
    assert len(commands) == 2
    lines = [
        line for line in capsys.readouterr().err.splitlines()
        if line.startswith("validation_timing")
    ]
    assert lines == [
        "validation_timing mode=full phase=bootstrap seconds=1.250 status=passed",
        "validation_timing mode=full phase=structural seconds=4.500 status=failed",
        "validation_timing mode=full phase=pytest seconds=5.000 status=passed",
        "validation_timing mode=full phase=total seconds=14.000 status=failed",
    ]


def test_validator_phase_timeout_returns_124_and_reports_limit(
    monkeypatch, capsys
) -> None:
    times = iter((1.0, 4.0))
    monkeypatch.setattr(
        validator.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.TimeoutExpired(args[0], kwargs["timeout"])
        ),
    )

    result = validator.run_phase(
        ["python", "slow.py"],
        mode="full",
        phase="structural",
        environment={},
        clock=lambda: next(times),
        timeout_seconds=180,
    )

    assert result == 124
    assert "status=timed_out reason=limit_180s" in capsys.readouterr().err


def test_validator_temp_root_rejects_repository_local_path(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    local = repository / "tmp"
    local.mkdir()
    try:
        validator.resolve_temp_root(local, repo_root=repository)
    except ValueError as error:
        assert "outside the repository" in str(error)
    else:
        raise AssertionError("repository-local pytest root was accepted")


def test_focused_validator_reports_structural_skip(monkeypatch, capsys, tmp_path: Path) -> None:
    times = iter((0.0, 1.0, 1.5, 2.0, 4.5, 5.0))
    monkeypatch.setattr(
        validator, "resolve_validation_python", lambda repo: Path("resolved-python")
    )
    monkeypatch.setattr(
        validator.subprocess,
        "run",
        lambda command, **kwargs: SimpleNamespace(returncode=0),
    )
    assert validator.main(
        ["--temp-root", str(tmp_path), "--path", "tests/test_elicitation.py"], clock=lambda: next(times)
    ) == 0
    lines = [
        line for line in capsys.readouterr().err.splitlines()
        if line.startswith("validation_timing")
    ]
    assert lines == [
        "validation_timing mode=focused phase=bootstrap seconds=0.500 status=passed",
        "validation_timing mode=focused phase=structural seconds=0.000 status=skipped reason=focused_tests",
        "validation_timing mode=focused phase=pytest seconds=2.500 status=passed",
        "validation_timing mode=focused phase=total seconds=5.000 status=passed",
    ]


def test_bootstrap_failure_reports_timing_without_execution(monkeypatch, capsys, tmp_path: Path) -> None:
    times = iter((0.0, 1.0, 3.0, 4.0))

    def unavailable(repo):
        raise validator.BootstrapUnavailable("test unavailable")

    monkeypatch.setattr(validator, "resolve_validation_python", unavailable)
    monkeypatch.setattr(
        validator.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("bootstrap failure must not execute"),
    )
    assert validator.main(["--temp-root", str(tmp_path)], clock=lambda: next(times)) == 1
    error = capsys.readouterr().err
    assert "validation_timing mode=full phase=bootstrap seconds=2.000 status=failed" in error
    assert "validation_timing mode=full phase=total seconds=4.000 status=failed" in error
    assert "validation unavailable: test unavailable" in error


def test_validation_environment_removes_private_and_unsafe_pytest_bindings() -> None:
    source = {
        "NARRATIVE_CHOICE_DB": r"C:\private\real-choice.sqlite3",
        "PYTEST_ADDOPTS": r"--basetemp C:\unsafe\pytest",
        "PRESERVED": "yes",
    }
    sanitized = validator.validation_environment(source)
    assert sanitized == {"PRESERVED": "yes"}
    assert source["NARRATIVE_CHOICE_DB"] == r"C:\private\real-choice.sqlite3"


def test_focused_validator_uses_same_interpreter_and_only_pytest(monkeypatch, tmp_path: Path) -> None:
    python = Path("resolved-python")
    commands: list[list[str]] = []
    environments: list[dict[str, str]] = []
    monkeypatch.setattr(validator, "resolve_validation_python", lambda repo: python)
    monkeypatch.setenv("NARRATIVE_CHOICE_DB", r"C:\private\real-choice.sqlite3")
    monkeypatch.setattr(
        validator.subprocess,
        "run",
        lambda command, **kwargs: (
            commands.append(command),
            environments.append(kwargs["env"]),
            SimpleNamespace(returncode=7),
        )[-1],
    )
    assert validator.main(
        ["--temp-root", str(tmp_path), "--path", "tests/test_elicitation.py", "--path", "tests/test_runtime_tooling.py"]
    ) == 7
    assert len(commands) == 1
    assert commands[0][:8] == [
        str(python),
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "-m",
        "not repository_integrity",
    ]
    assert commands[0][8] == "--basetemp"
    assert str(tmp_path) in commands[0][9]
    assert commands[0][-2:] == ["tests/test_elicitation.py", "tests/test_runtime_tooling.py"]
    assert len(environments) == 1
    assert "NARRATIVE_CHOICE_DB" not in environments[0]


@pytest.mark.parametrize(
    "path",
    (
        "README.md",
        "tests/missing.py",
        "../tests/test_runtime_tooling.py",
        "tests/../tests/test_runtime_tooling.py",
        "tests/test_runtime_tooling.py::test_validator_uses_one_interpreter_and_runs_both_checks",
        "tests/test_*.py",
    ),
)
def test_focused_validator_rejects_unsafe_or_unsupported_paths(path: str) -> None:
    with pytest.raises(ValueError):
        validator.focused_test_paths([path])


@pytest.mark.parametrize(
    "path",
    (
        "README.md",
        "tests/missing.py",
        "../tests/test_runtime_tooling.py",
        "tests/../tests/test_runtime_tooling.py",
        "tests/test_runtime_tooling.py::test_validator_uses_one_interpreter_and_runs_both_checks",
        "tests/test_*.py",
        str(REPO_ROOT / "tests" / "test_runtime_tooling.py"),
    ),
)
def test_focused_validator_invalid_paths_exit_two_without_execution(
    path: str, monkeypatch, tmp_path: Path
) -> None:
    def unexpected_call(*args, **kwargs):
        raise AssertionError("invalid focused paths must not bootstrap or execute")

    monkeypatch.setattr(validator, "resolve_validation_python", unexpected_call)
    monkeypatch.setattr(validator.subprocess, "run", unexpected_call)
    assert validator.main(["--temp-root", str(tmp_path), "--path", path]) == 2


def test_compatibility_shim_no_longer_requires_dot_venv() -> None:
    shim = (REPO_ROOT / "scripts" / "python.ps1").read_text(encoding="utf-8")
    assert "DEPRECATED" in shim
    assert ".venv" not in shim
    assert "runtime_bootstrap.py" in shim

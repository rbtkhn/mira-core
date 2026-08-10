from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "cadence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("cadence_tests", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cadence = load_module()


def verified(value: bool = True) -> dict:
    return {
        "integrity": {
            "status": "passed" if value else "failed",
            "passed": value,
            "returncode": 0 if value else 1,
        },
        "tests": {
            "status": "passed" if value else "failed",
            "passed": value,
            "returncode": 0 if value else 1,
        },
    }


def patch_repo_state(monkeypatch, *, head: str = "abc", dirty: list[str] | None = None):
    monkeypatch.setattr(cadence, "git_head", lambda: head)
    monkeypatch.setattr(cadence, "dirty_paths", lambda: dirty or [])
    monkeypatch.setattr(cadence, "worktree_fingerprint", lambda: "fingerprint")
    monkeypatch.setattr(cadence, "latest_daily_run", lambda: "2026-07-09")


def write_handoff(tmp_path: Path, *, outcome: str, verification: dict) -> Path:
    path = tmp_path / "last-dream.json"
    payload = {
        "schema_version": 2,
        "timestamp": "2026-07-10T00:00:00+00:00",
        "git_head": "abc",
        "dirty_paths": [],
        "worktree_fingerprint": "fingerprint",
        "verification": verification,
        "learning": {
            "experiment": "compare two retrieval methods",
            "outcome": outcome,
            "lesson": "bounded retrieval reduced citation repair",
            "method_change_candidate": "start with bounded retrieval",
            "evidence_summary": "citation repairs fell from 8 to 3",
            "artifact_refs": ["tests/test_cadence.py"],
            "tomorrow_inherits": "confirm the gain on a thinner crisis",
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_cold_start_bootstraps_a_bounded_experiment(monkeypatch, tmp_path: Path) -> None:
    patch_repo_state(monkeypatch)
    state = cadence.coffee_state(tmp_path / "missing.json")
    assert state["handoff_status"] == "missing"
    assert state["next_mode"] == "bootstrap_bounded_experiment"


def test_measured_improvement_is_confirmed_before_consolidation(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    path = write_handoff(tmp_path, outcome="improved", verification=verified())
    state = cadence.coffee_state(path)
    assert state["handoff_status"] == "current"
    assert state["next_mode"] == "confirm_then_consolidate"
    assert state["handoff"]["learning"]["lesson"].startswith("bounded retrieval")
    assert state["handoff"]["learning"]["evidence_summary"] == (
        "citation repairs fell from 8 to 3"
    )


def test_inconclusive_result_generates_a_discriminating_test(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    path = write_handoff(tmp_path, outcome="inconclusive", verification=verified())
    state = cadence.coffee_state(path)
    assert state["next_mode"] == "run_discriminating_test"


def test_regression_generates_revert_and_diagnose(monkeypatch, tmp_path: Path) -> None:
    patch_repo_state(monkeypatch)
    path = write_handoff(tmp_path, outcome="regressed", verification=verified())
    state = cadence.coffee_state(path)
    assert state["next_mode"] == "revert_and_diagnose"


def test_failed_verification_blocks_learning(monkeypatch, tmp_path: Path) -> None:
    patch_repo_state(monkeypatch)
    path = write_handoff(tmp_path, outcome="improved", verification=verified(False))
    state = cadence.coffee_state(path)
    assert state["handoff_status"] == "verification_failed"
    assert state["next_mode"] == "repair_before_inheriting"


def test_missing_verification_blocks_learning(monkeypatch, tmp_path: Path) -> None:
    patch_repo_state(monkeypatch)
    path = write_handoff(tmp_path, outcome="improved", verification={})
    state = cadence.coffee_state(path)
    assert state["handoff_status"] == "verification_failed"


def test_schema_v3_running_phase_is_reported_as_interrupted(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    path = tmp_path / "last-dream.json"
    payload = {
        "schema_version": 3,
        "git_head": "abc",
        "dirty_paths": [],
        "worktree_fingerprint": "fingerprint",
        "verification": cadence.initial_verification("pape-voice-judgment"),
        "learning": {"outcome": "improved"},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    state = cadence.coffee_state(path)

    assert state["handoff_status"] == "interrupted"
    assert state["next_mode"] == "resume_or_repair_interrupted_verification"


def test_unavailable_profile_bootstrap_is_recorded(monkeypatch, tmp_path: Path) -> None:
    def unavailable(repo_root):
        raise cadence.BootstrapUnavailable("offline and no completed cache")

    monkeypatch.setattr(cadence, "resolve_validation_python", unavailable)
    result = cadence.run_profile_verification("pape-voice-judgment", tmp_path)
    assert result["status"] == "unavailable"
    assert result["returncode"] is None
    assert "offline" in result["output_tail"]


def test_research_brief_commissioning_profile_is_bounded() -> None:
    spec = cadence.EXPERIMENT_PROFILES["research-brief-commissioning"]

    assert spec["version"] == 1
    assert "does not establish decision usefulness" in spec["purpose"]
    assert "docs/skill-drafts/research-brief/SKILL.md" in spec["paths"]
    assert "scripts/research_handoff.py" in spec["paths"]
    assert "scripts/reality_handoff.py" in spec["paths"]
    assert "scripts/continuity.py" in spec["paths"]
    assert "narrative-geopolitics/archive/source-manifest.json" not in spec["paths"]
    assert spec["command"][-3:] == ["-q", "-p", "no:cacheprovider"]
    assert set(spec["command"][2:-3]) == {
        "tests/test_research_handoff.py",
        "tests/test_research_brief_skill.py",
        "tests/test_reality_handoff.py",
        "tests/test_reality_check_skill.py",
        "tests/test_continuity.py",
        "tests/test_runtime_tooling.py",
    }


def test_pape_voice_judgment_profile_is_bounded() -> None:
    spec = cadence.EXPERIMENT_PROFILES["pape-voice-judgment"]

    assert spec["version"] == 1
    assert "does not promote or score any hook" in spec["purpose"]
    assert spec["paths"] == [
        "scripts/voice_judgments.py",
        "narrative-geopolitics/work/voice-judgments/external-voice-judgment-ledger.json",
        "narrative-geopolitics/voices/pape/judgment-ledger.md",
        "tests/test_voice_judgments.py",
    ]
    assert spec["command"] == [
        "-m",
        "pytest",
        "tests/test_voice_judgments.py",
        "-q",
        "-p",
        "no:cacheprovider",
    ]


def test_mira_journal_composition_profile_is_bounded() -> None:
    spec = cadence.EXPERIMENT_PROFILES["mira-journal-composition"]

    assert spec["version"] == 1
    assert "local-use eligibility only" in spec["purpose"]
    assert "docs/skill-drafts/mira-journal/SKILL.md" in spec["paths"]
    assert "tests/test_mira_journal.py" in spec["paths"]
    assert "tests/test_recursive_learning_ledger.py" in spec["paths"]
    assert spec["command"][-3:] == ["-q", "-p", "no:cacheprovider"]


def test_profile_verification_is_bounded_and_uses_direct_external_basetemp(
    monkeypatch, tmp_path: Path
) -> None:
    commands: list[list[str]] = []
    environments: list[dict[str, str]] = []
    monkeypatch.setattr(cadence, "resolve_validation_python", lambda root: Path("python"))
    monkeypatch.setattr(
        cadence.subprocess,
        "run",
        lambda command, **kwargs: (
            commands.append(command),
            environments.append(kwargs["env"]),
            SimpleNamespace(returncode=0, stdout="passed", stderr=""),
        )[-1],
    )

    monkeypatch.setenv("PYTEST_ADDOPTS", r"--basetemp C:\unsafe\pytest")
    result = cadence.run_profile_verification("research-brief-commissioning", tmp_path)

    assert result["status"] == "passed"
    assert result["profile"] == "research-brief-commissioning"
    assert result["paths"] == cadence.EXPERIMENT_PROFILES[
        "research-brief-commissioning"
    ]["paths"]
    assert commands[0][:1] == ["python"]
    assert commands[0][1 : 1 + len(cadence.EXPERIMENT_PROFILES["research-brief-commissioning"]["command"])] == cadence.EXPERIMENT_PROFILES["research-brief-commissioning"]["command"]
    assert commands[0][-2] == "--basetemp"
    assert "PYTEST_ADDOPTS" not in environments[0]
    assert str(cadence.SCRIPTS_ROOT) in environments[0]["PYTHONPATH"].split(cadence.os.pathsep)


def test_changed_repository_state_requires_reconciliation(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch, head="new-head")
    path = write_handoff(tmp_path, outcome="improved", verification=verified())
    state = cadence.coffee_state(path)
    assert state["handoff_status"] == "stale"
    assert state["next_mode"] == "reconcile_state_before_inheriting"


def test_changed_content_on_same_paths_requires_reconciliation(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    path = write_handoff(tmp_path, outcome="improved", verification=verified())
    monkeypatch.setattr(cadence, "worktree_fingerprint", lambda: "changed-content")
    state = cadence.coffee_state(path)
    assert state["handoff_status"] == "stale"


def test_dream_persists_the_learning_contract(monkeypatch, tmp_path: Path) -> None:
    patch_repo_state(monkeypatch)
    path = tmp_path / "cadence" / "last-dream.json"
    payload = cadence.write_dream(
        experiment="voice continuity comparison",
        outcome="no_change",
        lesson="voice work changed attribution but not judgment",
        improvement="reserve voice work for disputed attribution",
        evidence_summary="both notes reached the same central judgment",
        artifact_refs=["tests/test_cadence.py"],
        tomorrow_inherits="test the narrower rule on one crisis",
        path=path,
    )
    assert path.exists()
    assert payload["schema_version"] == 3
    assert payload["learning"]["outcome"] == "no_change"
    assert payload["learning"]["artifact_refs"] == ["tests/test_cadence.py"]
    assert payload["verification"]["experiment"]["status"] == "not_run"
    assert payload["verification"]["repository"]["status"] == "not_run"
    assert payload["verification"]["inheritance"]["local-use"] == "blocked"
    assert json.loads(path.read_text(encoding="utf-8")) == payload


def test_profiled_dream_separates_local_and_repository_inheritance(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    experiment = {
        "status": "passed",
        "passed": True,
        "returncode": 0,
        "profile": "pape-voice-judgment",
        "paths": cadence.EXPERIMENT_PROFILES["pape-voice-judgment"]["paths"],
        "elapsed_seconds": 1.0,
        "output_tail": "passed",
    }
    path = tmp_path / "last-dream.json"

    payload = cadence.write_dream(
        profile="pape-voice-judgment",
        experiment="repair Pape voice-judgment hook coverage",
        outcome="improved",
        lesson="Pape hooks require separate judgment classes",
        improvement="retain the split Pape reading surface",
        evidence_summary="the bounded Pape profile passed",
        artifact_refs=["tests/test_voice_judgments.py"],
        tomorrow_inherits="use locally while repository validation is repaired",
        temp_root=tmp_path,
        path=path,
        profile_runner=lambda profile, temp_root: experiment,
    )

    assert payload["verification"]["inheritance"] == {
        "local-use": "eligible",
        "repo-use": "blocked",
        "public-use": "not_authorized",
    }
    view = cadence.coffee_view(cadence.coffee_state(path))
    assert view["handoff_status"] == "local_current_repo_pending"
    assert view["experiment_verification"] == "passed"
    assert view["repository_verification"] == "not_run"
    assert view["inheritance"]["local-use"] == "eligible"
    assert view["inheritance"]["repo-use"] == "blocked"


def test_profiled_dream_persists_running_receipt_before_profile(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    path = tmp_path / "last-dream.json"

    def inspect_initial(profile: str, temp_root: Path) -> dict:
        saved = json.loads(path.read_text(encoding="utf-8"))
        assert saved["schema_version"] == 3
        assert saved["verification"]["experiment"]["status"] == "running"
        assert saved["verification"]["repository"]["status"] == "not_run"
        return {
            "status": "passed",
            "passed": True,
            "returncode": 0,
            "profile": profile,
            "elapsed_seconds": 0.1,
            "output_tail": "passed",
        }

    cadence.write_dream(
        profile="pape-voice-judgment",
        experiment="persist before verify",
        outcome="improved",
        lesson="partial receipts survive interruption",
        improvement="write before subprocess start",
        evidence_summary="the runner observed the persisted running receipt",
        artifact_refs=["tests/test_cadence.py"],
        tomorrow_inherits="retain completed phase receipts",
        temp_root=tmp_path,
        path=path,
        profile_runner=inspect_initial,
    )


def test_promotion_uses_cache_receipt_and_promotes_both_scopes(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    path = tmp_path / "last-dream.json"
    cadence.write_dream(
        experiment="unprofiled advisory",
        outcome="inconclusive",
        lesson="promotion is explicit",
        improvement="separate Dream from full validation",
        evidence_summary="the advisory handoff was persisted",
        artifact_refs=["tests/test_cadence.py"],
        tomorrow_inherits="promote explicitly",
        path=path,
    )

    promoted = cadence.promote_dream(
        temp_root=tmp_path,
        path=path,
        runner=lambda temp_root, force=False: {
            "status": "passed",
            "passed": True,
            "returncode": 0,
            "cache_status": "hit",
            "phase_timings": {
                "structural": {"seconds": 0.0, "status": "skipped", "reason": "cache_hit"},
                "pytest": {"seconds": 0.0, "status": "skipped", "reason": "cache_hit"},
            },
            "elapsed_seconds": 0.2,
            "output_tail": "validation_cache status=hit",
        },
    )

    assert promoted["verification"]["repository"]["status"] == "passed"
    assert promoted["verification"]["repository"]["cache_status"] == "hit"
    assert promoted["verification"]["inheritance"] == {
        "local-use": "eligible",
        "repo-use": "eligible",
        "public-use": "not_authorized",
    }


def test_promotion_rejects_stale_handoff_without_running(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    path = tmp_path / "last-dream.json"
    cadence.write_dream(
        experiment="stale advisory",
        outcome="inconclusive",
        lesson="stale state cannot promote",
        improvement="compare fingerprints before execution",
        evidence_summary="the handoff has one stable fingerprint",
        artifact_refs=["tests/test_cadence.py"],
        tomorrow_inherits="create a current handoff",
        path=path,
    )
    monkeypatch.setattr(cadence, "worktree_fingerprint", lambda: "changed")

    try:
        cadence.promote_dream(
            temp_root=tmp_path,
            path=path,
            runner=lambda *args, **kwargs: (_ for _ in ()).throw(
                AssertionError("stale promotion must not execute")
            ),
        )
    except ValueError as error:
        assert "stale" in str(error)
    else:
        raise AssertionError("stale handoff was promoted")


def test_promotion_records_state_change_without_losing_terminal_receipt(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    path = tmp_path / "last-dream.json"
    cadence.write_dream(
        experiment="concurrent change",
        outcome="inconclusive",
        lesson="promotion requires stable state",
        improvement="retain a terminal state-changed receipt",
        evidence_summary="the repository changed after validation started",
        artifact_refs=["tests/test_cadence.py"],
        tomorrow_inherits="create a current handoff",
        path=path,
    )
    fingerprints = iter(("fingerprint", "changed"))
    monkeypatch.setattr(cadence, "worktree_fingerprint", lambda: next(fingerprints))

    promoted = cadence.promote_dream(
        temp_root=tmp_path,
        path=path,
        runner=lambda temp_root, force=False: {
            "status": "passed",
            "passed": True,
            "returncode": 0,
            "cache_status": "not_stored",
            "phase_timings": {},
            "elapsed_seconds": 1.0,
            "output_tail": "repository changed during validation",
        },
    )

    assert promoted["verification"]["repository"]["status"] == "state_changed"
    assert promoted["verification"]["structured"]["status"] == "failed"
    assert promoted["verification"]["structured"]["blockers"][0]["details"] == {
        "phase_status": "state_changed"
    }


def test_schema_v2_handoff_is_readable_and_promotes_as_v3(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    path = write_handoff(tmp_path, outcome="improved", verification=verified())

    promoted = cadence.promote_dream(
        temp_root=tmp_path,
        path=path,
        runner=lambda temp_root, force=False: {
            "status": "passed",
            "passed": True,
            "returncode": 0,
            "cache_status": "hit",
            "phase_timings": {},
            "elapsed_seconds": 0.1,
            "output_tail": "cache hit",
        },
    )

    assert promoted["schema_version"] == 3
    assert promoted["verification"]["repository"]["status"] == "passed"


def test_dream_persists_when_profile_verification_raises(monkeypatch, tmp_path: Path) -> None:
    patch_repo_state(monkeypatch)
    path = tmp_path / "last-dream.json"

    def verifier(profile: str, temp_root: Path) -> dict:
        raise RuntimeError("validator process could not start")

    payload = cadence.write_dream(
        profile="pape-voice-judgment",
        experiment="verifier failure preservation",
        outcome="inconclusive",
        lesson="a verifier crash must not erase the advisory handoff",
        improvement="persist the failure as explicit verification state",
        evidence_summary="the verifier raised before returning a result",
        artifact_refs=["narrative-geopolitics/work/daily/2026-07-27/synthesis.md"],
        tomorrow_inherits="rerun verification before relying on the lesson",
        temp_root=tmp_path,
        path=path,
        profile_runner=verifier,
    )

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved == payload
    assert saved["verification"]["experiment"]["status"] == "unavailable"
    assert "validator process could not start" in saved["verification"]["experiment"]["output_tail"]
    blocker = saved["verification"]["structured"]["blockers"][0]
    assert blocker["owner"] == "experiment"
    assert blocker["next_action"]


def test_reconstruction_keeps_decisive_scope_and_artifacts(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    path = tmp_path / "last-dream.json"
    payload = cadence.write_dream(
        experiment="audit Ukraine primary-record coverage",
        outcome="no_change",
        lesson="commentary density cannot substitute for party-owned terms",
        improvement="activate only after primary-record intake",
        evidence_summary=(
            "1,007 archive sources scanned; 113 Ukraine candidates; "
            "0 official-domain records; qualifying coverage remains 0/3 actors"
        ),
        artifact_refs=[
            "narrative-geopolitics/work/experiments/2026-07-value-test/ukraine-official-terms-baseline.md",
            "narrative-geopolitics/archive/sources/2026-06-05/source-daniel-davis-zelensky-s-letter-to-putin-lt-col-daniel-davis-2026-06-05.md",
        ],
        tomorrow_inherits="wait for a party-owned terms record",
        path=path,
    )
    view = cadence.coffee_view(cadence.coffee_state(path))
    assert view["learning"]["evidence_summary"] == payload["learning"][
        "evidence_summary"
    ]
    assert len(view["learning"]["artifact_refs"]) == 2


def test_dream_rejects_missing_or_escaping_artifact_references(
    monkeypatch, tmp_path: Path
) -> None:
    patch_repo_state(monkeypatch)
    common = {
        "experiment": "unsafe reference",
        "outcome": "inconclusive",
        "lesson": "none",
        "improvement": "none",
        "evidence_summary": "no evidence",
        "tomorrow_inherits": "repair",
        "path": tmp_path / "last-dream.json",
    }
    for artifact_ref in ("missing.md", "../outside.md"):
        try:
            cadence.write_dream(artifact_refs=[artifact_ref], **common)
        except ValueError as error:
            assert "artifact reference" in str(error)
        else:
            raise AssertionError("unsafe artifact reference was accepted")


def test_manifest_state_reports_dynamic_archive_parity(tmp_path: Path) -> None:
    archive = tmp_path / "archive" / "sources"
    (archive / "2026-07-12").mkdir(parents=True)
    (archive / "2026-07-13").mkdir(parents=True)
    (archive / "2026-07-12" / "one.md").write_text("one", encoding="utf-8")
    (archive / "2026-07-13" / "two.md").write_text("two", encoding="utf-8")
    manifest_path = tmp_path / "archive" / "source-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "source_count": 2,
                "sources": [
                    {"date": "2026-07-12"},
                    {"date": "2026-07-13"},
                ],
            }
        ),
        encoding="utf-8",
    )
    state = cadence.manifest_state(manifest_path, archive)
    assert state == {
        "header_count": 2,
        "row_count": 2,
        "archive_file_count": 2,
        "parity": True,
        "latest_intake_date": "2026-07-13",
        "recent_intake_dates": ["2026-07-12", "2026-07-13"],
    }


def test_best_intake_startup_exposes_live_state_and_bounded_authority(
    monkeypatch,
) -> None:
    monkeypatch.setattr(cadence, "git_head", lambda: "live-head")
    monkeypatch.setattr(cadence, "git_branch", lambda: "main")
    monkeypatch.setattr(
        cadence,
        "tracking_state",
        lambda: {
            "upstream": "origin/main",
            "ahead": 0,
            "behind": 0,
            "synchronized": True,
        },
    )
    monkeypatch.setattr(cadence, "dirty_paths", lambda: ["operator-notes/"])
    monkeypatch.setattr(
        cadence,
        "manifest_state",
        lambda: {
            "header_count": 12,
            "row_count": 12,
            "archive_file_count": 12,
            "parity": True,
            "latest_intake_date": "2026-07-13",
            "recent_intake_dates": ["2026-07-12", "2026-07-13"],
        },
    )
    monkeypatch.setattr(cadence, "latest_daily_run", lambda: "2026-07-10")
    monkeypatch.setattr(
        cadence,
        "coffee_state",
        lambda: {"handoff_status": "current", "next_mode": "confirm_then_consolidate"},
    )
    state = cadence.startup_state("best-intake")
    assert state["ready"] is True
    assert state["git"]["head"] == "live-head"
    assert state["archive"]["row_count"] == 12
    assert state["warnings"] == ["preserve_existing_dirty_paths"]
    assert state["next_action"] == "wait_for_operator_source"
    assert "narrative-geopolitics/voices/" in state["authority"][
        "must_not_write_without_explicit_authorization"
    ]
    assert "narrative-geopolitics/archive/source-manifest.json" in state[
        "authority"
    ]["may_write"]


def test_best_intake_startup_blocks_archive_manifest_mismatch(monkeypatch) -> None:
    monkeypatch.setattr(cadence, "git_head", lambda: "head")
    monkeypatch.setattr(cadence, "git_branch", lambda: "main")
    monkeypatch.setattr(cadence, "tracking_state", lambda: {})
    monkeypatch.setattr(cadence, "dirty_paths", lambda: [])
    monkeypatch.setattr(
        cadence,
        "manifest_state",
        lambda: {
            "header_count": 2,
            "row_count": 2,
            "archive_file_count": 1,
            "parity": False,
            "latest_intake_date": "2026-07-13",
            "recent_intake_dates": ["2026-07-13"],
        },
    )
    monkeypatch.setattr(cadence, "latest_daily_run", lambda: None)
    monkeypatch.setattr(
        cadence,
        "coffee_state",
        lambda: {"handoff_status": "stale", "next_mode": "reconcile_state_before_inheriting"},
    )
    state = cadence.startup_state("best-intake")
    assert state["ready"] is False
    assert state["blockers"] == ["archive_manifest_parity_failed"]
    assert state["next_action"] == "repair_preflight"
    assert "cadence_handoff_stale" in state["warnings"]


def test_saved_best_intake_prompt_uses_dynamic_context_not_frozen_state() -> None:
    prompt = (
        REPO_ROOT
        / "docs"
        / "prompts"
        / "land-the-day-before-you-judge-it-best-intake-session-startup.md"
    ).read_text(encoding="utf-8")
    assert "tools\\run.ps1 cadence startup intake --json" in prompt
    assert "Treat the command output—not this prompt—as authoritative" in prompt
    assert "commit: `" not in prompt
    assert "archive and manifest: 1,532" not in prompt


def test_synthesis_state_is_date_scoped_and_reports_daily_contract(
    tmp_path: Path,
) -> None:
    ng_root = tmp_path / "narrative-geopolitics"
    archive = ng_root / "archive" / "sources" / "2026-07-13"
    daily = ng_root / "work" / "daily" / "2026-07-13"
    archive.mkdir(parents=True)
    daily.mkdir(parents=True)
    source = archive / "source-a.md"
    source.write_text("source", encoding="utf-8")
    manifest_path = ng_root / "archive" / "source-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "date": "2026-07-13",
                        "local_path": source.relative_to(tmp_path).as_posix(),
                    },
                    {"date": "2026-07-12", "local_path": "other.md"},
                ]
            }
        ),
        encoding="utf-8",
    )
    for name in ("sources.md", "synthesis.md", "forecast.md", "judgment.md", "daily-brief.md"):
        (daily / name).write_text(name, encoding="utf-8")
    state = cadence.synthesis_state(
        "2026-07-13",
        manifest_path=manifest_path,
        daily_root=ng_root / "work" / "daily",
        repo_root=tmp_path,
    )
    assert state["manifest_day_rows"] == 1
    assert state["missing_archive_sources"] == []
    assert state["daily_contract_state"] == "complete"
    assert all(state["daily_files"].values())


def configure_synthesis_startup(monkeypatch, phase: dict, validation: dict) -> None:
    monkeypatch.setattr(cadence, "git_head", lambda: "head")
    monkeypatch.setattr(cadence, "git_branch", lambda: "main")
    monkeypatch.setattr(cadence, "tracking_state", lambda: {})
    monkeypatch.setattr(cadence, "dirty_paths", lambda: [])
    monkeypatch.setattr(
        cadence,
        "manifest_state",
        lambda: {
            "header_count": 4,
            "row_count": 4,
            "archive_file_count": 4,
            "parity": True,
            "latest_intake_date": "2026-07-13",
            "recent_intake_dates": ["2026-07-13"],
        },
    )
    monkeypatch.setattr(cadence, "latest_daily_run", lambda: "2026-07-13")
    monkeypatch.setattr(
        cadence,
        "coffee_state",
        lambda: {"handoff_status": "current", "next_mode": "confirm_then_consolidate"},
    )
    monkeypatch.setattr(cadence, "synthesis_state", lambda run_date: phase)
    monkeypatch.setattr(cadence, "validate_synthesis_date", lambda run_date: validation)


def test_synthesis_startup_scopes_authority_and_recommends_clean_entry(
    monkeypatch,
) -> None:
    phase = {
        "date": "2026-07-13",
        "manifest_day_rows": 4,
        "missing_archive_sources": [],
        "daily_directory_exists": True,
        "daily_files": {name: True for name in ("sources.md", "synthesis.md", "forecast.md", "daily-brief.md")},
        "daily_contract_state": "complete",
    }
    configure_synthesis_startup(
        monkeypatch,
        phase,
        {"passed": True, "returncode": 0, "failures": [], "warnings": []},
    )
    state = cadence.startup_state("geopolitical-synthesis", "2026-07-13")
    assert state["ready"] is True
    assert state["next_action"] == "open_guided_synthesis_choice_C"
    assert state["blockers"] == []
    assert "narrative-geopolitics/work/daily/2026-07-13/synthesis.md" in state[
        "authority"
    ]["may_write"]
    assert "narrative-geopolitics/public/" in state["authority"][
        "must_not_write_without_explicit_authorization"
    ]


def test_synthesis_startup_blocks_dates_without_manifest_rows(monkeypatch) -> None:
    phase = {
        "date": "2026-07-13",
        "manifest_day_rows": 0,
        "missing_archive_sources": [],
        "daily_directory_exists": False,
        "daily_files": {name: False for name in ("sources.md", "synthesis.md", "forecast.md", "daily-brief.md")},
        "daily_contract_state": "absent",
    }
    configure_synthesis_startup(
        monkeypatch,
        phase,
        {"passed": False, "returncode": 1, "failures": [], "warnings": []},
    )
    state = cadence.startup_state("geopolitical-synthesis", "2026-07-13")
    assert state["ready"] is False
    assert state["blockers"] == ["no_manifest_rows_for_selected_date"]
    assert state["next_action"] == "repair_preflight"
    assert "daily_contract_absent" in state["warnings"]


def test_synthesis_startup_routes_validation_failures_to_reconciliation(
    monkeypatch,
) -> None:
    phase = {
        "date": "2026-07-13",
        "manifest_day_rows": 2,
        "missing_archive_sources": [],
        "daily_directory_exists": True,
        "daily_files": {name: True for name in ("sources.md", "synthesis.md", "forecast.md", "daily-brief.md")},
        "daily_contract_state": "complete",
    }
    configure_synthesis_startup(
        monkeypatch,
        phase,
        {
            "passed": False,
            "returncode": 1,
            "failures": ["manifest route missing voice shelf"],
            "warnings": [],
        },
    )
    state = cadence.startup_state("geopolitical-synthesis", "2026-07-13")
    assert state["ready"] is True
    assert state["next_action"] == "open_guided_synthesis_choice_B"
    assert "synthesis_validation_requires_reconciliation" in state["warnings"]


def test_synthesis_startup_requires_explicit_date() -> None:
    try:
        cadence.startup_state("geopolitical-synthesis")
    except ValueError as error:
        assert "requires --date" in str(error)
    else:
        raise AssertionError("date-free synthesis startup was accepted")


def configure_bounded_phase_startup(monkeypatch) -> None:
    monkeypatch.setattr(cadence, "git_head", lambda: "head")
    monkeypatch.setattr(cadence, "git_branch", lambda: "main")
    monkeypatch.setattr(cadence, "tracking_state", lambda: {})
    monkeypatch.setattr(cadence, "dirty_paths", lambda: [])
    monkeypatch.setattr(
        cadence,
        "manifest_state",
        lambda: {
            "header_count": 4,
            "row_count": 4,
            "archive_file_count": 4,
            "parity": True,
            "latest_intake_date": "2026-07-13",
            "recent_intake_dates": ["2026-07-13"],
        },
    )
    monkeypatch.setattr(cadence, "latest_daily_run", lambda: "2026-07-13")
    monkeypatch.setattr(
        cadence,
        "coffee_state",
        lambda: {"handoff_status": "current", "next_mode": "confirm_then_consolidate"},
    )


def assessed_packet(outcome: str) -> dict:
    return {
        "packet_id": "VER-20260710-01",
        "exists": True,
        "path": "packet.md",
        "status": "assessed",
        "assessment_outcome": outcome,
        "observables": ["Vessel identity"],
        "evidence_records": 2,
        "evidence_chains": 2,
        "affected_forecast_hooks": ["NG-20260708-F02"],
        "validation_failures": [],
        "registry_failures": [],
    }


def test_operational_verification_assessments_never_auto_resolve_forecasts(
    monkeypatch,
) -> None:
    configure_bounded_phase_startup(monkeypatch)
    for outcome in (
        "operationally_supported",
        "operationally_contested",
        "disconfirmed",
        "unresolvable_with_authorized_evidence",
    ):
        monkeypatch.setattr(
            cadence, "verification_state", lambda packet_id, value=outcome: assessed_packet(value)
        )
        state = cadence.startup_state(
            "operational-verification", packet_id="VER-20260710-01"
        )
        assert state["ready"] is True
        assert state["next_action"] == "review_assessment_downstream_effects"
        assert "forecast ledger status, classification, or resolution" in state[
            "authority"
        ]["must_not_write_without_explicit_authorization"]


def test_operational_verification_missing_packet_blocks(monkeypatch) -> None:
    configure_bounded_phase_startup(monkeypatch)
    missing = assessed_packet("not_investigated") | {
        "exists": False,
        "status": None,
        "assessment_outcome": None,
        "validation_failures": ["packet not found"],
    }
    monkeypatch.setattr(cadence, "verification_state", lambda packet_id: missing)
    state = cadence.startup_state(
        "operational-verification", packet_id="VER-20260710-99"
    )
    assert state["ready"] is False
    assert state["blockers"] == ["verification_packet_missing_or_ambiguous"]


def test_invalid_assessed_packet_blocks_downstream_adoption(monkeypatch) -> None:
    configure_bounded_phase_startup(monkeypatch)
    invalid = assessed_packet("operationally_supported") | {
        "validation_failures": ["support rests only on interested officials"]
    }
    monkeypatch.setattr(cadence, "verification_state", lambda packet_id: invalid)
    state = cadence.startup_state(
        "operational-verification", packet_id="VER-20260710-01"
    )
    assert state["ready"] is False
    assert "assessed_verification_packet_invalid" in state["blockers"]


def forecast_phase(*, packets: list[dict], accountable: bool = True) -> dict:
    return {
        "hook_id": "NG-20260708-F02",
        "as_of": "2026-07-29",
        "entry_count": 1,
        "triage_count": 1,
        "run_date": "2026-07-08",
        "review_date": "2026-07-29",
        "due": True,
        "entry_status": "open",
        "forecast_type": "ex_ante" if accountable else "falsifier",
        "resolution_status": "open",
        "accountable": accountable,
        "review_note": "Review without forced certainty.",
        "verification_packets": packets,
    }


def test_due_forecast_with_completed_contested_packet_routes_human_review(
    monkeypatch,
) -> None:
    configure_bounded_phase_startup(monkeypatch)
    packet = {
        "packet_id": "VER-20260710-01",
        "exists": True,
        "status": "assessed",
        "assessment_outcome": "operationally_contested",
        "validation_failures": [],
    }
    monkeypatch.setattr(
        cadence,
        "forecast_review_state",
        lambda hook_id, as_of: forecast_phase(packets=[packet]),
    )
    state = cadence.startup_state(
        "forecast-review", hook_id="NG-20260708-F02", as_of="2026-07-29"
    )
    assert state["ready"] is True
    assert state["next_action"] == "review_forecast_without_forcing_outcome"
    assert state["phase"]["resolution_status"] == "open"


def test_due_forecast_without_packet_routes_to_verification(monkeypatch) -> None:
    configure_bounded_phase_startup(monkeypatch)
    monkeypatch.setattr(
        cadence,
        "forecast_review_state",
        lambda hook_id, as_of: forecast_phase(packets=[]),
    )
    state = cadence.startup_state(
        "forecast-review", hook_id="NG-20260708-F02", as_of="2026-07-29"
    )
    assert state["ready"] is True
    assert state["next_action"] == "open_operational_verification_before_resolution"
    assert "forecast_resolution_requires_completed_verification" in state["warnings"]


def test_resolved_accountable_forecast_without_completed_packet_blocks(
    monkeypatch,
) -> None:
    configure_bounded_phase_startup(monkeypatch)
    phase = forecast_phase(packets=[])
    phase["resolution_status"] = "hit"
    monkeypatch.setattr(
        cadence, "forecast_review_state", lambda hook_id, as_of: phase
    )
    state = cadence.startup_state(
        "forecast-review", hook_id="NG-20260708-F02", as_of="2026-07-29"
    )
    assert state["ready"] is False
    assert "resolved_accountable_forecast_lacks_completed_packet" in state["blockers"]


def test_resolved_bounded_forecast_does_not_require_factual_lattice_adjudication(
    monkeypatch,
) -> None:
    configure_bounded_phase_startup(monkeypatch)
    packet = {
        "packet_id": "VER-20260710-01",
        "exists": True,
        "status": "closed",
        "assessment_outcome": "operationally_supported",
        "validation_failures": [],
    }
    phase = forecast_phase(packets=[packet])
    phase["resolution_status"] = "hit"
    phase["lattice"] = {
        "claim": {"claim_type": "forecast", "forecast_scope": "public_discourse"},
        "assessment": None,
    }
    monkeypatch.setattr(cadence, "forecast_review_state", lambda hook_id, as_of: phase)
    state = cadence.startup_state(
        "forecast-review", hook_id="NG-20260708-F02", as_of="2026-07-29"
    )
    assert state["ready"] is True
    assert "resolved_accountable_forecast_lacks_canonical_multilingual_adjudication" not in state["blockers"]


def test_resolved_operational_forecast_keeps_canonical_lattice_gate(
    monkeypatch,
) -> None:
    configure_bounded_phase_startup(monkeypatch)
    packet = {
        "packet_id": "VER-20260710-01",
        "exists": True,
        "status": "closed",
        "assessment_outcome": "operationally_supported",
        "validation_failures": [],
    }
    phase = forecast_phase(packets=[packet])
    phase["resolution_status"] = "hit"
    phase["lattice"] = {
        "claim": {"claim_type": "forecast", "forecast_scope": "operational"},
        "assessment": None,
    }
    monkeypatch.setattr(cadence, "forecast_review_state", lambda hook_id, as_of: phase)
    state = cadence.startup_state(
        "forecast-review", hook_id="NG-20260708-F02", as_of="2026-07-29"
    )
    assert state["ready"] is False
    assert "resolved_accountable_forecast_lacks_canonical_multilingual_adjudication" in state["blockers"]


def test_non_accountable_forecast_cannot_be_promoted_by_review_preflight(
    monkeypatch,
) -> None:
    configure_bounded_phase_startup(monkeypatch)
    monkeypatch.setattr(
        cadence,
        "forecast_review_state",
        lambda hook_id, as_of: forecast_phase(packets=[], accountable=False),
    )
    state = cadence.startup_state(
        "forecast-review", hook_id="NG-20260708-F03", as_of="2026-08-07"
    )
    assert state["next_action"] == "preserve_non_accountable_classification"
    assert "other forecast rows or accountability classifications" in state[
        "authority"
    ]["must_not_write_without_explicit_authorization"]


def test_forecast_review_discovers_packets_that_name_the_hook(
    tmp_path: Path, monkeypatch
) -> None:
    ledger_path = tmp_path / "forecast-ledger.md"
    ledger_path.write_text(
        """| Hook ID | Date | Crisis Object | Claim | Probability Band | Review Date | Source Run | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260708-F02` | `2026-07-08` | Object | Claim | `likely` | `2026-07-29` | [run](x) | `open` |
| Hook ID | Authored No Later Than | Timing Provenance | Forecast Type | Resolution Status | Accountable | Review Note |
| --- | --- | --- | --- | --- | --- | --- |
| `NG-20260708-F02` | `2026-07-09` | `git_commit_upper_bound` | `ex_ante` | `open` | `yes` | No packet copied here yet. |
""",
        encoding="utf-8",
    )
    packet_path = tmp_path / "VER-20260710-01" / "README.md"
    monkeypatch.setattr(cadence.verification_packets, "packet_paths", lambda: [packet_path])
    monkeypatch.setattr(
        cadence.verification_packets,
        "parse_packet",
        lambda path: SimpleNamespace(
            packet_id="VER-20260710-01",
            fields={"affected_forecast_hooks": "NG-20260708-F02"},
        ),
    )
    monkeypatch.setattr(
        cadence,
        "verification_state",
        lambda packet_id: assessed_packet("operationally_contested"),
    )
    state = cadence.forecast_review_state(
        "NG-20260708-F02", "2026-07-29", ledger_path
    )
    assert [item["packet_id"] for item in state["verification_packets"]] == [
        "VER-20260710-01"
    ]
    assert "No packet copied here yet." in ledger_path.read_text(encoding="utf-8")


def test_bounded_phase_startups_require_explicit_targets() -> None:
    for mode, expected in (
        ("operational-verification", "requires --packet"),
        ("forecast-review", "requires --hook"),
    ):
        try:
            cadence.startup_state(mode)
        except ValueError as error:
            assert expected in str(error)
        else:
            raise AssertionError(f"target-free {mode} startup was accepted")

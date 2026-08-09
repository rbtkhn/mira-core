from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import audit_ai_harness
import codex_skill_registry
import validate_repository


def stub_live_repository_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(validate_repository, "validate_repository", lambda: [])
    monkeypatch.setattr(audit_ai_harness, "mirror_records", lambda: [])
    monkeypatch.setattr(
        audit_ai_harness,
        "git_state",
        lambda: {
            "branch": "test",
            "head": "000000000000",
            "tracked_changes": 0,
            "untracked_entries": 0,
        },
    )


def test_frontmatter_parser_reads_scalars_without_interpreting_body(tmp_path: Path) -> None:
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        '---\nname: example\ndescription: "Bounded example."\n---\n'
        "# Body\n\nname: body-is-not-metadata\n",
        encoding="utf-8",
    )

    assert codex_skill_registry.parse_skill_frontmatter(skill) == {
        "name": "example",
        "description": "Bounded example.",
    }


def test_complete_directory_comparison_detects_non_skill_file_drift(tmp_path: Path) -> None:
    source = tmp_path / "repo" / "example"
    installed = tmp_path / "installed" / "example"
    source.mkdir(parents=True)
    installed.mkdir(parents=True)
    (source / "SKILL.md").write_text("same\n", encoding="utf-8")
    (installed / "SKILL.md").write_text("same\n", encoding="utf-8")
    (source / "reference.md").write_text("canonical\n", encoding="utf-8")
    (installed / "reference.md").write_text("drift\n", encoding="utf-8")
    entry = codex_skill_registry.SkillEntry(
        "example", source / "SKILL.md", installed / "SKILL.md"
    )

    state = codex_skill_registry.skill_mirror_state(entry)

    assert state.status == "DRIFT"
    assert state.installed is True
    assert not Path(state.source_path).is_absolute()


def test_drift_is_classified_as_one_home_without_syncing(tmp_path: Path) -> None:
    installed = tmp_path / "installed" / "skill.md"
    installed.parent.mkdir()
    installed.write_text("unchanged\n", encoding="utf-8")
    mirrors = [
        {
            "name": "example",
            "canonical_source": "docs/skill-drafts/example/SKILL.md",
            "installed": True,
            "status": "DRIFT",
            "action": "ONE_HOME",
        }
    ]

    controls = audit_ai_harness.build_controls([], [], mirrors)

    mirror = next(item for item in controls if item["control_id"] == "skill-mirror-example")
    assert mirror["action"] == "ONE_HOME"
    assert installed.read_text(encoding="utf-8") == "unchanged\n"


def test_private_absolute_paths_are_rejected() -> None:
    with pytest.raises(ValueError, match="private absolute path"):
        audit_ai_harness.reject_private_paths({"path": "C:\\Users\\person\\secret"})


def test_current_skill_metadata_and_routes_are_valid() -> None:
    assert audit_ai_harness.skill_metadata_failures() == []
    assert validate_repository.skill_contract_failures() == []


def test_audit_json_has_stable_top_level_contract_and_expected_gap_labels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stub_live_repository_checks(monkeypatch)
    payload = audit_ai_harness.build_audit()

    assert set(payload) == {
        "schema_version",
        "audit_mode",
        "generated_at_utc",
        "repository",
        "git",
        "summary",
        "stations",
        "repository_check",
        "skill_mirrors",
        "coverage_gaps",
        "strict_findings",
    }
    assert payload["schema_version"] == "1.0"
    assert payload["audit_mode"] == "READ_ONLY"
    assert [item["station_id"] for item in payload["stations"]] == [
        item[0] for item in audit_ai_harness.STATIONS
    ]
    assert {item["evidence_state"] for item in payload["coverage_gaps"]} == {
        "INACCESSIBLE"
    }
    audit_ai_harness.reject_private_paths(payload)


def test_build_is_no_write_and_receipt_write_is_explicit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stub_live_repository_checks(monkeypatch)
    receipt = tmp_path / "ai-harness" / "latest.json"
    monkeypatch.setattr(audit_ai_harness, "RECEIPT_PATH", receipt)

    payload = audit_ai_harness.build_audit()
    assert not receipt.exists()

    audit_ai_harness.write_receipt(payload)
    assert json.loads(receipt.read_text(encoding="utf-8"))["audit_mode"] == "READ_ONLY"


def test_build_surfaces_repository_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stub_live_repository_checks(monkeypatch)
    monkeypatch.setattr(
        validate_repository,
        "validate_repository",
        lambda: ["bounded repository failure"],
    )

    payload = audit_ai_harness.build_audit()

    assert payload["repository_check"] == {
        "status": "FAIL",
        "failures": ["bounded repository failure"],
    }
    assert "bounded repository failure" in payload["strict_findings"]


def test_strict_mode_exits_nonzero_for_findings(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = {
        "repository_check": {"status": "PASS"},
        "summary": {"strict_findings": 1},
        "stations": [],
        "coverage_gaps": [],
        "strict_findings": ["installed skill mirror example: DRIFT"],
    }
    monkeypatch.setattr(audit_ai_harness, "build_audit", lambda: payload)
    monkeypatch.setattr(sys, "argv", ["audit_ai_harness.py", "--strict"])

    with pytest.raises(SystemExit) as raised:
        audit_ai_harness.main()

    assert raised.value.code == 1
    assert "STRICT FINDINGS" in capsys.readouterr().out


def test_json_main_is_parseable_and_receipt_path_is_ignored(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    stub_live_repository_checks(monkeypatch)
    payload = audit_ai_harness.build_audit()
    monkeypatch.setattr(audit_ai_harness, "build_audit", lambda: payload)
    monkeypatch.setattr(sys, "argv", ["audit_ai_harness.py", "--json"])

    audit_ai_harness.main()

    payload = json.loads(capsys.readouterr().out)
    assert payload["audit_mode"] == "READ_ONLY"

    ignored = subprocess.run(
        ["git", "check-ignore", "tmp/ai-harness/latest.json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ignored.returncode == 0

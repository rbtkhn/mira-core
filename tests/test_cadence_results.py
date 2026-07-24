from __future__ import annotations

from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from cadence_contracts import predictive_history_contract
from cadence_results import VerificationResult, aggregate, command_result


def test_structured_result_requires_owner_and_next_action_for_nonpass() -> None:
    try:
        VerificationResult("x", "failed", "command", "repository")
    except ValueError as error:
        assert "owner" in str(error)
    else:
        raise AssertionError("non-passing result without routing data was accepted")


def test_result_serializes_references_and_command() -> None:
    result = command_result(
        check_id="catalog",
        status="failed",
        scope="contract",
        command=["validate", "--check"],
        failure_class="reference",
        owner="predictive-history",
        next_action="Repair the catalog.",
        references=("civ-07",),
        details={"lane_class": "catalog"},
    )
    payload = result.to_dict()
    assert payload["references"] == ["civ-07"]
    assert payload["command"] == ["validate", "--check"]
    assert payload["details"]["lane_class"] == "catalog"


def test_aggregation_prefers_failed_over_unavailable_and_passed() -> None:
    results = [
        command_result(check_id="pass", status="passed", scope="repository", command=["pass"]),
        command_result(check_id="missing", status="unavailable", scope="contract", command=["missing"], failure_class="environment", owner="lane", next_action="Restore lane."),
        command_result(check_id="bad", status="failed", scope="repository", command=["bad"], failure_class="command", owner="repo", next_action="Repair repo."),
    ]
    payload = aggregate(results)
    assert payload["status"] == "failed"
    assert payload["passed"] is False
    assert payload["next_action"] == "Repair repo."


def test_predictive_history_contract_is_read_only_and_reports_missing_repo(tmp_path: Path) -> None:
    calls: list[tuple[list[str], Path]] = []

    def runner(command: list[str], cwd: Path) -> tuple[int, str]:
        calls.append((command, cwd))
        return 0, "ok"

    missing = tmp_path / "predictive-history"
    contract = predictive_history_contract(tmp_path, missing, runner, lambda: {})
    results = contract.run_checks()
    assert results[0].status == "unavailable"
    assert results[0].failure_class == "environment"
    assert calls == []


def test_predictive_history_contract_runs_only_declared_read_check(tmp_path: Path) -> None:
    external = tmp_path / "predictive-history"
    external.mkdir()
    calls: list[tuple[list[str], Path]] = []

    def runner(command: list[str], cwd: Path) -> tuple[int, str]:
        calls.append((command, cwd))
        return 1, "civ-07: missing HTML output"

    contract = predictive_history_contract(tmp_path, external, runner, lambda: {})
    results = contract.run_checks()
    assert results[0].check_id == "study-edition"
    assert results[0].failure_class == "generated-output"
    assert calls == [(["python", "scripts/validate_study_edition.py"], external)]
    assert list(external.iterdir()) == []

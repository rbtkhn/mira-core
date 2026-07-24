"""Explicit cadence contracts for repository lanes.

Contracts are intentionally small. They provide lane facts and checks; the
cadence kernel owns handoffs, aggregation, inheritance, and rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from cadence_results import VerificationResult, command_result


@dataclass(frozen=True)
class CadenceContract:
    contract_id: str
    version: int
    state_root: Path
    authority_surfaces: tuple[str, ...]
    checks: tuple[str, ...]
    run_checks: Callable[[], list[VerificationResult]]
    state: Callable[[], dict[str, Any]]


def narrative_geopolitics_contract(repo_root: Path, run_checks: Callable[[], list[VerificationResult]], state: Callable[[], dict[str, Any]]) -> CadenceContract:
    return CadenceContract(
        contract_id="narrative-geopolitics",
        version=1,
        state_root=repo_root / "narrative-geopolitics" / "work" / "cadence",
        authority_surfaces=(
            "narrative-geopolitics/archive/",
            "narrative-geopolitics/work/daily/",
            "narrative-geopolitics/work/forecasts/",
            "narrative-geopolitics/work/reality/",
            "narrative-geopolitics/public/",
        ),
        checks=("repository-integrity", "manifest-archive", "daily-contract", "forecast-ledger", "reality-verification", "rendering-publication", "smart-intake-routing"),
        run_checks=run_checks,
        state=state,
    )


def predictive_history_contract(repo_root: Path, external_root: Path, runner: Callable[[list[str], Path], tuple[int, str]], state: Callable[[], dict[str, Any]]) -> CadenceContract:
    def checks() -> list[VerificationResult]:
        if not external_root.exists():
            return [command_result(check_id="predictive-history", status="unavailable", scope="contract", command=["python", "-m", "predictive_history"], failure_class="environment", owner="predictive-history", next_action="Make the read-only Predictive History repository available.", evidence=str(external_root))]
        results: list[VerificationResult] = []
        command = ["python", "scripts/validate_study_edition.py"]
        code, output = runner(command, external_root)
        results.append(command_result(check_id="study-edition", status="passed" if code == 0 else "failed", scope="contract", command=command, output_tail=output, failure_class="generated-output" if code else None, owner="predictive-history", next_action="Run or repair the study-edition build, then rerun validation."))
        return results

    return CadenceContract(
        contract_id="predictive-history",
        version=1,
        state_root=repo_root / "work" / "cadence" / "predictive-history",
        authority_surfaces=("external:C:/dev/predictive-history/",),
        checks=("namespace-catalog", "card-source-commentary", "route-resolution", "study-edition", "public-surface", "pin-cite", "compatibility"),
        run_checks=checks,
        state=state,
    )

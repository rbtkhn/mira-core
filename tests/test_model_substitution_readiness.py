from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import validate_repository


def test_model_substitution_gate_is_complete() -> None:
    assert validate_repository.model_substitution_gate_failures() == []


def test_model_substitution_gate_rejects_missing_contract_parts(tmp_path: Path) -> None:
    source = validate_repository.MODEL_SUBSTITUTION_GATE.read_text(encoding="utf-8")
    broken = (
        source.replace("| Reversibility |", "| Exit behavior |")
        .replace("## Boundary statement", "## Boundary removed")
        .replace("Default state: `review-required`", "Default state: `ready`")
        .replace("What remains internal:", "Disclosure notes:")
    )
    path = tmp_path / "model-substitution-readiness.md"
    path.write_text(broken, encoding="utf-8")

    failures = validate_repository.model_substitution_gate_failures(path)

    assert "model substitution gate missing section: ## Boundary statement" in failures
    assert "model substitution gate missing dimension: Reversibility" in failures
    assert "model substitution gate default must be review-required" in failures
    assert "model substitution gate missing output field: What remains internal:" in failures

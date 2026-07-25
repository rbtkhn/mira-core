from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "report_freeman_reference_density.py"


def load_module():
    spec = importlib.util.spec_from_file_location("freeman_reference_density", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_density_report_has_normalized_metrics_and_host_summary() -> None:
    module = load_module()
    report = module.build_report()
    assert "Per 1,000 words" in report
    assert "## Host/channel summary" in report
    assert "## Interpretation guardrails" in report
    assert "Corpus density" in report


def test_density_report_is_deterministic() -> None:
    module = load_module()
    assert module.build_report() == module.build_report()

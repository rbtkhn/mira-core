from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "report_freeman_reference_density.py"


def load_module():
    spec = importlib.util.spec_from_file_location("freeman_reference_density", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def density_analysis():
    module = load_module()
    return module, module.build_density_analysis()


def test_density_report_has_normalized_metrics_and_host_summary(density_analysis) -> None:
    module, analysis = density_analysis
    report = module.render_report(analysis)
    assert "Per 1,000 words" in report
    assert "## Host/channel summary" in report
    assert "## Interpretation guardrails" in report
    assert "Corpus density" in report


def test_density_report_is_deterministic(density_analysis) -> None:
    module, analysis = density_analysis
    assert module.render_report(analysis) == module.render_report(analysis)


def test_main_builds_density_analysis_once(monkeypatch, capsys) -> None:
    module = load_module()
    sentinel = object()
    calls = 0

    def build_density_analysis():
        nonlocal calls
        calls += 1
        return sentinel

    monkeypatch.setattr(module, "build_density_analysis", build_density_analysis)
    monkeypatch.setattr(module, "render_report", lambda analysis: "rendered" if analysis is sentinel else "unexpected")
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--dry-run"])

    assert module.main() == 0
    assert capsys.readouterr().out.strip() == "rendered"
    assert calls == 1

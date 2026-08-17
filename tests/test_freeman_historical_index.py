from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "build_freeman_historical_index.py"


def load_module():
    spec = importlib.util.spec_from_file_location("freeman_historical_index", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_reference_rules_normalize_repeated_mentions() -> None:
    module = load_module()
    assert module.RULES[0].key == "bay-of-pigs"
    assert any(rule.key == "cultural-revolution" for rule in module.RULES)


def test_attribution_confidence_is_explicit() -> None:
    module = load_module()
    assert module.attribution("**Chas Freeman:** The Bay of Pigs was a precedent.", "") == ("direct", "speaker label present")
    assert module.attribution("This is a historical comparison.", "") == ("provisional", "transcript turn is not explicitly speaker-labeled")


@pytest.mark.skipif(
    not (REPO_ROOT / "archive" / "sources" / "geopolitics" / "sources").is_dir(),
    reason="requires hydrated archive transcript bodies",
)
def test_render_is_deterministic_and_contains_required_surfaces() -> None:
    module = load_module()
    analysis = module.build_analysis()
    assert len(analysis.occurrences) < 2000
    first = module.render(analysis)
    second = module.render(analysis)
    assert first == second
    assert "# Chas Freeman Historical References" in first
    assert "## Reference index" in first
    assert "## Occurrence ledger" in first
    assert "## Coverage and limitations" in first
    assert "Historical domain" in first
    assert "Freeman question" in first
    assert "FR-HR-" in first
    assert "attribution" in first


def test_main_builds_analysis_once(monkeypatch, capsys) -> None:
    module = load_module()
    sentinel = object()
    calls = 0

    def build_analysis():
        nonlocal calls
        calls += 1
        return sentinel

    monkeypatch.setattr(module, "build_analysis", build_analysis)
    monkeypatch.setattr(module, "render", lambda analysis: "rendered" if analysis is sentinel else "unexpected")
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--dry-run"])

    assert module.main() == 0
    assert capsys.readouterr().out.strip() == "rendered"
    assert calls == 1

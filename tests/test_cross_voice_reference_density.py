from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "report_cross_voice_reference_density.py"


def load_module():
    spec = importlib.util.spec_from_file_location("cross_voice_density", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_manifest_routes_are_deduplicated_and_normalized() -> None:
    module = load_module()
    rows = module.manifest_rows("freeman")
    identities = [(row["path" if "path" in row else "local_path"], row["voice_slug"]) for row in rows]
    assert len(identities) == len(set(identities))
    assert all(row["voice_slug"] == row["voice_slug"].lower() for row in rows)
    selected = module.manifest_rows("freeman,diesen")
    assert {row["voice_slug"] for row in selected} == {"freeman", "diesen"}


@pytest.mark.skipif(
    not (REPO_ROOT / "archive" / "geopolitics" / "sources").is_dir(),
    reason="requires hydrated archive transcript bodies",
)
def test_report_contains_comparison_surfaces_and_is_deterministic() -> None:
    module = load_module()
    records, coverage = module.build_records("freeman")
    first = module.render_report(records, coverage, "freeman")
    assert first == module.render_report(records, coverage, "freeman")
    assert "# Historical-Reference Density Pilot" in first
    assert "## Voice comparison" in first
    assert "## Host/channel comparison" in first
    assert "## Transcript drilldown" in first
    assert "## Occurrence ledger" in first
    assert "CV-HR-" in first
    assert "Quote:" in first
    ledger = module.render_voice_ledger(records, "freeman")
    assert "# Historical-Reference Ledger: freeman" in ledger
    assert "| ID | Reference |" in ledger
    assert "FREEMAN-HR-" in ledger
    assert "Review status" in ledger
    assert "## Source-level reference clusters" in ledger
    assert "FREEMAN-CL-" in ledger
    assert "`unreviewed`" in ledger
    assert "`excluded-context`" in module.render_voice_ledger(records, "freeman")
    queue = module.render_review_queue(records)
    assert "# Historical-Reference Review Queue" in queue
    assert "## needs-review" in queue
    assert "## Cluster review queue" in queue
    assert "RV-CL-" in queue
    assert "Record durable decisions" in queue
    assert "Confidence mix" in first
    assert "candidate historical-reference" in first
    assert "bounded comparison pilot" in first


def test_main_builds_records_once(monkeypatch, capsys) -> None:
    module = load_module()
    calls = 0

    def build_records(voice_filter: str):
        nonlocal calls
        calls += 1
        return [], []

    monkeypatch.setattr(module, "build_records", build_records)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--dry-run"])

    assert module.main() == 0
    assert "Historical-Reference Density Pilot" in capsys.readouterr().out
    assert calls == 1


def test_confidence_classes_are_explicit() -> None:
    module = load_module()
    assert module.confidence("**Freeman:** The Bay of Pigs", "freeman") == "direct"
    assert module.confidence("**Host:** The Bay of Pigs", "freeman") is None
    assert module.confidence("The Bay of Pigs was a precedent.", "freeman") == "provisional"
    assert module.is_context_only("Welcome back. We are joined today by Professor Mearsheimer.")
    assert not module.is_context_only("The Cold War shaped the alliance system.")

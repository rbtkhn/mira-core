from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "build_freeman_historical_index.py"


def load_module():
    spec = importlib.util.spec_from_file_location("freeman_historical_index", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_mechanism_registry_has_stable_controlled_entries() -> None:
    module = load_module()
    assert [item["id"] for item in module.MECHANISMS] == ["M-FR-001", "M-FR-002", "M-FR-003", "M-FR-004", "M-FR-005"]
    assert all(item["definition"] and item["inclusion_tests"] and item["exclusion_tests"] for item in module.MECHANISMS)


def test_reference_suggestions_are_provisional_and_reference_based() -> None:
    module = load_module()
    rule = next(item for item in module.RULES if item.key == "iraq-war")
    suggestions = module.mechanism_suggestions(rule, "A short mention of Iraq.")
    assert [item["id"] for item in suggestions] == ["M-FR-001"]
    assert suggestions[0]["basis"] == "reference rule only"
    evidenced = module.mechanism_suggestions(rule, "The Iraq invasion produced strategic backfire and failed regime change.")
    assert evidenced[0]["basis"] == "quote-context evidence"
    assert "invasion" in evidenced[0]["evidence_terms"]


def test_structured_ledger_preserves_occurrence_and_review_separation() -> None:
    module = load_module()
    rule = next(item for item in module.RULES if item.key == "jcpoa")
    occurrence = {
        "rule": rule,
        "occurrence_id": "FR-O-001-jcpoa-0001",
        "source_id": "SRC-FR-001",
        "mechanism_suggestions": module.mechanism_suggestions(rule, "The JCPOA matters."),
        "mechanism_status": "suggested",
    }
    ledger = module.structured_ledger([], [occurrence], [], [], {"confirmed": []})
    assert ledger["occurrences"][0]["reference_key"] == "jcpoa"
    assert ledger["occurrences"][0]["mechanism_status"] == "suggested"
    assert ledger["mechanisms"]["review"]["confirmed"] == []


def test_review_file_is_safe_when_absent(tmp_path, monkeypatch) -> None:
    module = load_module()
    monkeypatch.setattr(module, "MECHANISM_REVIEW_PATH", tmp_path / "missing.json")
    review = module.load_mechanism_review()
    assert review["voice"] == "freeman"
    assert review["confirmed"] == []

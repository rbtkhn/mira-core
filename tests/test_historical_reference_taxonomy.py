from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_historical_reference_taxonomy.py"

def load():
    spec = importlib.util.spec_from_file_location("taxonomy_validator", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def test_repo_taxonomies_validate():
    module = load()
    files = sorted(module.TAXONOMY_ROOT.glob("*.json"))
    assert files
    assert [failure for path in files for failure in module.validate_taxonomy(path)] == []

def test_crosswalk_requires_confidence_rationale_and_review_state(tmp_path):
    module = load()
    path = tmp_path / "run.json"
    path.write_text(json.dumps({"records": [{"occurrence_id": "SRC:ref:1", "crosswalk_suggestions": [{"target": "M-FR-001", "confidence": "suggested", "rationale": "candidate only", "conflict_status": "unreviewed", "review_status": "unreviewed"}]}]}), encoding="utf-8")
    assert module.validate_crosswalk(path) == []
    path.write_text(json.dumps({"records": [{"occurrence_id": "SRC:ref:1", "crosswalk_suggestions": [{"target": "M-FR-001", "confidence": "certain"}]}]}), encoding="utf-8")
    failures = module.validate_crosswalk(path)
    assert any("missing rationale" in failure for failure in failures)
    assert any("invalid confidence" in failure for failure in failures)

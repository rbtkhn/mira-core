from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "recursive_learning_ledger.py"
SPEC = importlib.util.spec_from_file_location("recursive_learning_ledger_tests", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_current_recursive_learning_ledger_validates() -> None:
    assert MODULE.validate_ledger() == []


def test_rendered_markdown_exposes_all_five_stages() -> None:
    rendered = MODULE.render_markdown(MODULE.load_ledger())
    for heading in ("### Observation", "### Diagnosis", "### Intervention", "### Validation", "### Outcome"):
        assert heading in rendered
    assert "post-repair manual QA rate pending" in rendered


def test_missing_evidence_and_false_measurement_are_rejected(tmp_path: Path) -> None:
    ledger = copy.deepcopy(MODULE.load_ledger())
    entry = ledger["entries"][0]
    entry["closure_state"] = "measured"
    entry["outcome"]["measure"] = "Post-intervention measure pending."
    entry["validation"]["evidence_paths"] = ["missing-evidence.md"]
    json_path = tmp_path / "ledger.json"
    markdown_path = tmp_path / "ledger.md"
    json_path.write_text(json.dumps(ledger), encoding="utf-8")
    markdown_path.write_text(MODULE.render_markdown(ledger), encoding="utf-8")

    failures = MODULE.validate_ledger(
        repo_root=REPO_ROOT,
        json_path=json_path,
        markdown_path=markdown_path,
    )

    assert any("missing evidence path" in failure for failure in failures)
    assert any("measured entry has pending outcome" in failure for failure in failures)

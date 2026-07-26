from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".codex" / "skills" / "historical-reference" / "scripts" / "analyze.py"

def load():
    spec = importlib.util.spec_from_file_location("historical_reference_skill", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module); return module

def test_explicit_voice_selection_and_stable_patterns():
    module = load()
    rows = module.source_rows({"freeman"}, None)
    assert rows
    assert all("freeman" in {str(v).lower() for v in row.get("voice_slugs", [])} for row in rows)
    assert module.PATTERNS["jcpoa"][0] == "JCPOA / Iran nuclear diplomacy"

def test_record_schema_and_stable_occurrence_identity(tmp_path):
    module = load()
    row = {"source_id": "SRC-TEST", "local_path": "test.md", "date": "2026-01-01", "title": "Test", "voice_slugs": ["freeman"], "full_path": tmp_path / "test.md"}
    row["full_path"].write_text("---\n---\nFreeman discussed the JCPOA and the nuclear deal.", encoding="utf-8")
    records = module.analyze_row(row)
    assert records[0]["occurrence_id"] == "SRC-TEST:jcpoa:1"
    assert records[0]["crosswalk_suggestions"][0]["confidence"] == "suggested"
    assert records[0]["attribution_confidence"] == "provisional"

def test_skill_requires_explicit_voices():
    module = load()
    assert "--voices" in (ROOT / ".codex" / "skills" / "historical-reference" / "SKILL.md").read_text(encoding="utf-8")

def test_calibration_report_is_measurable():
    module = load()
    report = module.calibration_report()
    assert report["fixture_version"] == "1.0"
    assert report["cases"] == 22
    assert 0 <= report["reference_precision"] <= 1
    assert 0 <= report["reference_recall"] <= 1
    assert report["results"]

def test_review_packet_uses_stable_identity_and_explicit_decisions():
    module = load()
    item = {
        "occurrence_id": "SRC-1:jcpoa:2", "source_id": "SRC-1", "reference_id": "jcpoa",
        "date": "2026-01-01", "title": "Test", "archive_path": "archive/test.md",
        "quote": "Freeman discussed the JCPOA.", "reference": "JCPOA", "parent_period": "Post-Cold War diplomacy",
        "attribution_confidence": "provisional", "mechanism_suggestions": [], "crosswalk_suggestions": [],
        "risk_score": 3, "review_status": "needs-review", "evidence_basis": "paragraph",
    }
    packet = module.review_packet(item)
    assert packet["review_id"] == "review:SRC-1:jcpoa:2"
    assert packet["identity"]["occurrence_id"] == item["occurrence_id"]
    assert packet["decision_options"] == ["accept", "qualify", "reject", "revise", "unresolved"]

def test_review_overrides_apply_by_occurrence_identity(tmp_path):
    module = load()
    path = tmp_path / "overrides.json"
    path.write_text('{"overrides":{"SRC-1:jcpoa:2":{"review_status":"qualified","review_note":"Needs context.","reviewed_by":"operator"}}}', encoding="utf-8")
    overrides = module.load_overrides(path)
    item = {"occurrence_id": "SRC-1:jcpoa:2", "review_status": "needs-review"}
    module.apply_overrides([item], overrides)
    assert item["review_status"] == "qualified"
    assert item["reviewed_by"] == "operator"

def test_review_packets_markdown_preserves_identity_and_decisions():
    module = load()
    packet = {
        "review_id": "review:SRC-1:jcpoa:2", "priority_score": 3,
        "identity": {"occurrence_id": "SRC-1:jcpoa:2", "source_id": "SRC-1"},
        "source": {"date": "2026-01-01", "archive_path": "archive/test.md"},
        "attribution_confidence": "provisional", "current_status": "needs-review",
        "evidence": {"quote": "A bounded excerpt.", "basis": "paragraph"},
        "reference": {"label": "JCPOA", "parent_period": "Post-Cold War diplomacy"},
        "mechanism_suggestions": [], "crosswalk_suggestions": [],
        "decision_options": ["accept", "qualify", "reject", "revise", "unresolved"],
    }
    rendered = module.review_packets_markdown([packet], "run-1")
    assert "review:SRC-1:jcpoa:2" in rendered
    assert "A bounded excerpt." in rendered
    assert "`accept`, `qualify`, `reject`, `revise`, `unresolved`" in rendered

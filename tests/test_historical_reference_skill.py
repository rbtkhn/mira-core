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

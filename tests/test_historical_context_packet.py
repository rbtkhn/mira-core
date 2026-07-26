from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_historical_context_packet.py"

def load():
    spec = importlib.util.spec_from_file_location("historical_context_packet", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def record(occurrence_id: str, date: str = "2026-07-25", voice: str = "freeman") -> dict:
    return {"occurrence_id": occurrence_id, "source_id": "SRC-1", "archive_path": "archive/source.md", "title": "Iran context", "date": date, "reference_id": "jcpoa", "reference": "JCPOA", "quote": "A bounded excerpt.", "voices": [voice], "attribution_confidence": "provisional", "mechanism_suggestions": [], "crosswalk_suggestions": [], "review_status": "needs-review", "risk_score": 3}

def test_packet_is_date_and_voice_bounded_and_source_linked():
    module = load()
    data = {"run_id": "run-1", "records": [record("A"), record("B", voice="diesen"), record("C", date="2026-07-24")]}
    packet = module.build_packet(data, "2026-07-25", {"freeman"}, None, 12)
    assert packet["record_count"] == 1
    assert packet["records"][0]["occurrence_id"] == "A"
    assert packet["records"][0]["archive_path"] == "archive/source.md"
    assert packet["status"] == "bounded-context-only"

def test_packet_limit_and_id_are_deterministic():
    module = load()
    data = {"run_id": "run-1", "records": [record("A"), record("B")]}
    first = module.build_packet(data, "2026-07-25", {"freeman"}, None, 1)
    second = module.build_packet(data, "2026-07-25", {"freeman"}, None, 1)
    assert first["record_count"] == 1
    assert first["packet_id"] == second["packet_id"]
    assert any("does not overwrite" in item for item in first["guardrails"])

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "mira_portable.py"
SPEC = importlib.util.spec_from_file_location("mira_portable", MODULE_PATH)
assert SPEC and SPEC.loader
portable = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(portable)


def test_compatibility_status_routes_to_external_state(tmp_path, monkeypatch):
    monkeypatch.setattr(portable, "resolve_state_root", lambda: tmp_path / "state")
    monkeypatch.setattr(portable.mira_state, "status", lambda root: {"state_root": str(root)})
    assert portable.main(["status"]) == 0


def test_export_routes_to_mira_state(tmp_path, monkeypatch, capsys):
    root, output = tmp_path / "state", tmp_path / "export"
    monkeypatch.setattr(portable, "resolve_state_root", lambda: root)
    monkeypatch.setattr(portable.mira_state, "export", lambda actual_root, actual_output, check: {"source": str(actual_root), "output": str(actual_output), "check": check})
    assert portable.main(["export", "--output", str(output), "--check"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {"check": True, "output": str(output), "source": str(root)}


def test_adapter_contract_remains_available():
    assert portable.adapter_fixtures()["ok"]
    call={"id":"call_1","type":"function","function":{"name":"probe","arguments":"{}"}}
    assert portable.normalize_response("kimi", {"tool_calls": [call]})["tool_calls"][0]["id"] == "call_1"
    with pytest.raises(portable.PortabilityError):
        portable.normalize_response("deepseek", {"tool_calls": [call]}, thinking=True)


def test_argument_validation_remains_available():
    assert portable.validate_arguments('{"x":1}', {"properties":{"x":{}}, "required":["x"]}) == {"x":1}
    with pytest.raises(portable.PortabilityError): portable.validate_arguments('{"y":1}', {"properties":{"x":{}}})

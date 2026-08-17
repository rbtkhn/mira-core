from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "mira_portable.py"
SPEC = importlib.util.spec_from_file_location("mira_portable", MODULE_PATH)
portable = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(portable)


def test_beneath_rejects_second_tree(tmp_path, monkeypatch):
    root=tmp_path/"mira core"
    root.mkdir()
    monkeypatch.setattr(portable,"REPO_ROOT",root)
    assert portable.beneath(root/".mira-private"/"state") == (root/".mira-private"/"state").resolve()
    with pytest.raises(portable.PortabilityError): portable.beneath(tmp_path/"export")
    with pytest.raises(portable.PortabilityError): portable.beneath(root/".."/"replacement")


def test_sqlite_snapshot_is_logically_valid(tmp_path, monkeypatch):
    root=tmp_path/"root"; root.mkdir(); monkeypatch.setattr(portable,"REPO_ROOT",root)
    source=tmp_path/"live.sqlite3"
    with sqlite3.connect(source) as db:
        db.execute("create table events(id integer primary key, value text)")
        db.execute("insert into events(value) values ('continuity')")
    destination=root/".mira-private/state/copy.sqlite3"
    receipt=portable.sqlite_snapshot(source,destination)
    assert receipt["quick_check"] == "ok"
    with sqlite3.connect(destination) as db: assert db.execute("select value from events").fetchone()[0] == "continuity"


def test_adapter_provider_state_and_argument_validation():
    call={"id":"native-id","type":"function","function":{"name":"probe","arguments":"{\"x\":1}"}}
    assert portable.normalize_response("kimi",{"tool_calls":[call]})["tool_calls"][0]["id"] == "native-id"
    deep=portable.normalize_response("deepseek",{"reasoning_content":"trace","tool_calls":[call]},thinking=True)
    assert deep["reasoning_content"] == "trace"
    with pytest.raises(portable.PortabilityError): portable.normalize_response("deepseek",{"tool_calls":[call]},thinking=True)
    assert portable.validate_arguments('{"x":1}',{"properties":{"x":{}},"required":["x"]}) == {"x":1}
    with pytest.raises(portable.PortabilityError): portable.validate_arguments('{"y":1}',{"properties":{"x":{}}})


def test_adapter_fixture_has_equal_provider_status():
    receipt=portable.adapter_fixtures()
    assert receipt["ok"]
    assert {row["provider"] for row in receipt["cases"]} == {"kimi","deepseek","generic-openai"}


def test_runtime_pack_requires_runtime_wheel_license_and_hashes(tmp_path, monkeypatch):
    monkeypatch.setattr(portable,"PRIVATE",tmp_path/".mira-private")
    root=portable.PRIVATE/"runtime/runtimes/windows-x64"; root.mkdir(parents=True)
    files=[]
    for kind,name in (("runtime","python.zip"),("wheel","dependency.whl"),("license","LICENSE.txt")):
        path=root/name; path.write_bytes(kind.encode()); files.append({"path":name,"kind":kind,"sha256":portable.sha(path)})
    (root/"runtime.json").write_text(json.dumps({"platform":"windows-x64","python_version":"3.12.10","files":files}),encoding="utf-8")
    assert portable.runtime_pack_state("windows-x64")["ready"]
    (root/"dependency.whl").write_bytes(b"tampered")
    assert not portable.runtime_pack_state("windows-x64")["ready"]


def test_manifest_schema_and_confidentiality_are_explicit():
    schema=json.loads((Path(__file__).resolve().parents[1]/"archive/schemas/mira-model-adapter-v1.json").read_text(encoding="utf-8"))
    assert schema["$id"] == "urn:mira:model-adapter:v1"
    assert "kimi" in schema["properties"]["provider"]["enum"]


def test_rest_receipts_are_active_private_portability_objects(tmp_path, monkeypatch):
    root=tmp_path/"repo"; receipt=root/".mira-private/sessions/rest/mira-core/session/event.json"
    receipt.parent.mkdir(parents=True); receipt.write_text('{"event":"rested"}',encoding="utf-8")
    monkeypatch.setattr(portable,"REPO_ROOT",root); monkeypatch.setattr(portable,"PRIVATE",root/".mira-private")
    rows=portable.rest_dispositions()
    assert len(rows) == 1
    assert rows[0]["disposition"] == "include-private-active"
    assert rows[0]["authority_status"] == "private-provisional"
    assert rows[0]["destination_or_reconstruction"] == ".mira-private/sessions/rest/mira-core/session/event.json"

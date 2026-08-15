from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "innermost_loop_simulation.py"
SPEC = importlib.util.spec_from_file_location("innermost_loop_simulation_tests", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_current_simulation_packet_validates() -> None:
    assert MODULE.validate() == []


def test_sha256_path_normalizes_text_line_endings(tmp_path: Path) -> None:
    lf_path = tmp_path / "lf.txt"
    crlf_path = tmp_path / "crlf.txt"
    lf_path.write_bytes(b"first\nsecond\n")
    crlf_path.write_bytes(b"first\r\nsecond\r\n")

    assert MODULE.sha256_path(lf_path) == MODULE.sha256_path(crlf_path)


def test_frozen_baseline_hash_failure_is_reported(tmp_path: Path) -> None:
    protocol = MODULE.load_json(MODULE.PROTOCOL_PATH)
    protocol["baseline"]["sha256"] = "0" * 64
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text(MODULE.pretty_json(protocol), encoding="utf-8")

    failures = MODULE.validate(protocol_path=protocol_path)

    assert "frozen baseline hash mismatch" in failures


def test_source_registry_drift_is_reported(tmp_path: Path) -> None:
    protocol = MODULE.load_json(MODULE.PROTOCOL_PATH)
    protocol["sources"][0]["sha256"] = "f" * 64
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text(MODULE.pretty_json(protocol), encoding="utf-8")

    failures = MODULE.validate(protocol_path=protocol_path)

    assert any("source sha256 mismatch" in failure for failure in failures)


def test_packet_hash_drift_is_reported(tmp_path: Path) -> None:
    protocol = MODULE.load_json(MODULE.PROTOCOL_PATH)
    packet_path = protocol["packet_paths"][2]
    protocol["packet_sha256"][packet_path] = "0" * 64
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text(MODULE.pretty_json(protocol), encoding="utf-8")

    failures = MODULE.validate(protocol_path=protocol_path)

    assert f"packet sha256 mismatch: {packet_path}" in failures


@pytest.mark.parametrize("mutation", ["missing", "extra"])
def test_packet_digest_map_must_match_paths(tmp_path: Path, mutation: str) -> None:
    protocol = MODULE.load_json(MODULE.PROTOCOL_PATH)
    if mutation == "missing":
        protocol["packet_sha256"].pop(protocol["packet_paths"][0])
    else:
        protocol["packet_sha256"]["mira/notes/innermost-loop-simulation/extra.json"] = (
            "0" * 64
        )
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text(MODULE.pretty_json(protocol), encoding="utf-8")

    failures = MODULE.validate(protocol_path=protocol_path)

    assert "packet digest map does not match packet_paths" in failures


def test_duplicate_packet_path_is_reported(tmp_path: Path) -> None:
    protocol = MODULE.load_json(MODULE.PROTOCOL_PATH)
    duplicate = protocol["packet_paths"][0]
    protocol["packet_paths"].append(duplicate)
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text(MODULE.pretty_json(protocol), encoding="utf-8")

    failures = MODULE.validate(protocol_path=protocol_path)

    assert f"duplicate packet path: {duplicate}" in failures


@pytest.mark.parametrize("digest", ["A" * 64, "0" * 63, "g" * 64])
def test_invalid_packet_digest_is_reported(tmp_path: Path, digest: str) -> None:
    protocol = MODULE.load_json(MODULE.PROTOCOL_PATH)
    packet_path = protocol["packet_paths"][0]
    protocol["packet_sha256"][packet_path] = digest
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text(MODULE.pretty_json(protocol), encoding="utf-8")

    failures = MODULE.validate(protocol_path=protocol_path)

    assert f"invalid packet sha256: {packet_path}" in failures


def test_later_phase_requires_dependencies(tmp_path: Path) -> None:
    state = MODULE.load_json(MODULE.STATE_PATH)
    state["phases"]["day-1"] = {
        "status": "pending",
        "not_before": "2026-08-10T00:00:00Z",
    }
    response = MODULE.RUN_ROOT / "responses" / "day-2-test.md"
    response.parent.mkdir(parents=True, exist_ok=True)
    response.write_text("temporary response", encoding="utf-8")
    state["phases"]["day-2"].update(
        {
            "status": "sealed",
            "response_path": MODULE.repo_relative(response),
            "sha256": MODULE.sha256_path(response),
            "completed_at": "2026-08-11T15:00:00Z"
        }
    )
    state_path = tmp_path / "run-state.json"
    state_path.write_text(MODULE.pretty_json(state), encoding="utf-8")
    try:
        failures = MODULE.validate(state_path=state_path)
    finally:
        response.unlink()

    assert "sealed day-2 requires sealed day-1" in failures


def test_seal_check_does_not_mutate_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    state = MODULE.load_json(MODULE.STATE_PATH)
    state["phases"]["day-1"] = {
        "status": "pending",
        "not_before": "2026-08-10T00:00:00Z",
    }
    for phase in ("day-2", "day-3", "day-10"):
        state["phases"][phase]["status"] = "pending"
        for field in ("response_path", "sha256", "completed_at"):
            state["phases"][phase].pop(field, None)
    state_path = tmp_path / "run-state.json"
    state_path.write_text(MODULE.pretty_json(state), encoding="utf-8")
    response = MODULE.RUN_ROOT / "responses" / "day-1-test.md"
    response.parent.mkdir(parents=True, exist_ok=True)
    response.write_text("bounded test response", encoding="utf-8")
    before = state_path.read_bytes()
    monkeypatch.setattr(MODULE, "STATE_PATH", state_path)
    try:
        result = MODULE.seal_phase(
            "day-1", response, "2026-08-10T01:00:00Z", check=True
        )
    finally:
        response.unlink()

    assert result["status"] == "ready"
    assert state_path.read_bytes() == before


def test_seal_rejects_early_phase(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    state = MODULE.load_json(MODULE.STATE_PATH)
    state["phases"]["day-1"].update(
        {
            "status": "sealed",
            "response_path": "mira/notes/innermost-loop-simulation/README.md",
            "sha256": MODULE.sha256_path(MODULE.RUN_ROOT / "README.md"),
            "completed_at": "2026-08-10T01:00:00Z"
        }
    )
    state["phases"]["day-2"] = {
        "status": "pending",
        "not_before": "2026-08-11T15:00:00Z",
    }
    state_path = tmp_path / "run-state.json"
    state_path.write_text(MODULE.pretty_json(state), encoding="utf-8")
    response = MODULE.RUN_ROOT / "responses" / "day-2-test.md"
    response.parent.mkdir(parents=True, exist_ok=True)
    response.write_text("bounded test response", encoding="utf-8")
    monkeypatch.setattr(MODULE, "STATE_PATH", state_path)
    try:
        with pytest.raises(MODULE.SimulationError, match="cannot be sealed before"):
            MODULE.seal_phase("day-2", response, "2026-08-10T02:00:00Z", check=True)
    finally:
        response.unlink()

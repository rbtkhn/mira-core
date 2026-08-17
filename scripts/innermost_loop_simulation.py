from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_ROOT = REPO_ROOT / "mira" / "notes" / "innermost-loop-simulation"
PROTOCOL_PATH = RUN_ROOT / "protocol.json"
STATE_PATH = RUN_ROOT / "run-state.json"
REGISTRY_PATH = REPO_ROOT / "archive" / "registries" / "innermost-loop.json"
ALLOWED_PHASES = ("day-1", "day-2", "day-3", "day-10")
PHASE_DEPENDENCIES = {
    "day-1": (),
    "day-2": ("day-1",),
    "day-3": ("day-1", "day-2"),
    "day-10": ("day-1", "day-2", "day-3"),
}
FORBIDDEN_PROMOTION_PREFIXES = (
    "mira/continuity/",
    "mira/journal/",
    "narrative-geopolitics/",
    "archive/registries/",
)


class SimulationError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    # Sealed simulation identities bind literal artifact bytes. Cross-platform
    # stability is controlled by .gitattributes rather than digest rewriting.
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SimulationError(f"cannot read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise SimulationError(f"expected JSON object: {path}")
    return value


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError as error:
        raise SimulationError(f"path must remain inside repository: {resolved}") from error


def resolve_repo_path(value: str) -> Path:
    if not value or Path(value).is_absolute():
        raise SimulationError(f"expected repository-relative path: {value!r}")
    resolved = (REPO_ROOT / value).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as error:
        raise SimulationError(f"path escapes repository: {value}") from error
    return resolved


def parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise SimulationError(f"invalid timestamp: {value}") from error
    if parsed.tzinfo is None:
        raise SimulationError(f"timestamp must include timezone: {value}")
    return parsed.astimezone(timezone.utc)


def validate(protocol_path: Path = PROTOCOL_PATH, state_path: Path = STATE_PATH) -> list[str]:
    failures: list[str] = []
    try:
        protocol = load_json(protocol_path)
        state = load_json(state_path)
        registry = load_json(REGISTRY_PATH)
    except SimulationError as error:
        return [str(error)]

    if protocol.get("collection_id") != "innermost-loop":
        failures.append("protocol collection_id must be innermost-loop")
    if protocol.get("source_commit") != registry.get("source_commit"):
        failures.append("protocol source commit does not match registry")
    if protocol.get("retrieval_policy") != "explicit-only":
        failures.append("protocol retrieval policy must be explicit-only")
    if protocol.get("authority_effect") != "none":
        failures.append("protocol authority_effect must be none")

    baseline = protocol.get("baseline", {})
    try:
        baseline_path = resolve_repo_path(str(baseline.get("path", "")))
        if not baseline_path.is_file():
            failures.append(f"missing baseline: {baseline_path}")
        elif sha256_path(baseline_path) != baseline.get("sha256"):
            failures.append("frozen baseline hash mismatch")
    except SimulationError as error:
        failures.append(str(error))

    registry_by_path = {
        item.get("upstream_path"): item
        for item in registry.get("documents", [])
        if isinstance(item, dict)
    }
    source_paths: set[str] = set()
    for source in protocol.get("sources", []):
        if not isinstance(source, dict):
            failures.append("source entries must be objects")
            continue
        upstream_path = source.get("upstream_path")
        if upstream_path in source_paths:
            failures.append(f"duplicate source path: {upstream_path}")
        source_paths.add(str(upstream_path))
        registered = registry_by_path.get(upstream_path)
        if not registered:
            failures.append(f"source is not registered: {upstream_path}")
            continue
        for field in ("sha256", "size", "document_type", "publication_date", "rights_status"):
            if source.get(field) != registered.get(field):
                failures.append(f"source {field} mismatch: {upstream_path}")

    packet_paths = protocol.get("packet_paths", [])
    packet_sha256 = protocol.get("packet_sha256", {})
    if not isinstance(packet_paths, list) or not packet_paths:
        failures.append("packet_paths must be a non-empty list")
        packet_paths = []
    normalized_packet_paths = [str(value) for value in packet_paths]
    duplicate_packet_paths = {
        value for value in normalized_packet_paths if normalized_packet_paths.count(value) > 1
    }
    for duplicate in sorted(duplicate_packet_paths):
        failures.append(f"duplicate packet path: {duplicate}")
    if not isinstance(packet_sha256, dict) or set(packet_sha256) != set(normalized_packet_paths):
        failures.append("packet digest map does not match packet_paths")
        packet_sha256 = packet_sha256 if isinstance(packet_sha256, dict) else {}

    for packet_value in normalized_packet_paths:
        expected_sha256 = packet_sha256.get(packet_value)
        valid_sha256 = isinstance(expected_sha256, str) and re.fullmatch(
            r"[0-9a-f]{64}", expected_sha256
        )
        if not valid_sha256:
            failures.append(f"invalid packet sha256: {packet_value}")
        try:
            packet_path = resolve_repo_path(packet_value)
            if not packet_path.is_file():
                failures.append(f"missing packet: {packet_value}")
                continue
            if valid_sha256 and sha256_path(packet_path) != expected_sha256:
                failures.append(f"packet sha256 mismatch: {packet_value}")
            packet = load_json(packet_path)
            if packet.get("authority_effect") != "none":
                failures.append(f"packet authority_effect must be none: {packet_value}")
            if packet.get("contains_source_body") is not False:
                failures.append(f"packet must declare contains_source_body false: {packet_value}")
        except SimulationError as error:
            failures.append(str(error))

    phases = state.get("phases")
    if not isinstance(phases, dict) or set(phases) != set(ALLOWED_PHASES):
        failures.append("run state must contain exactly day-1, day-2, day-3, and day-10")
        phases = {}
    for phase in ALLOWED_PHASES:
        record = phases.get(phase, {})
        status = record.get("status")
        if status not in {"pending", "sealed"}:
            failures.append(f"invalid phase status for {phase}: {status}")
            continue
        not_before = record.get("not_before")
        if not isinstance(not_before, str):
            failures.append(f"missing not_before for {phase}")
        else:
            try:
                parse_timestamp(not_before)
            except SimulationError as error:
                failures.append(str(error))
        if status == "sealed":
            for dependency in PHASE_DEPENDENCIES[phase]:
                if phases.get(dependency, {}).get("status") != "sealed":
                    failures.append(f"sealed {phase} requires sealed {dependency}")
            try:
                response_path = resolve_repo_path(str(record.get("response_path", "")))
                if not response_path.is_file():
                    failures.append(f"missing sealed response for {phase}")
                elif sha256_path(response_path) != record.get("sha256"):
                    failures.append(f"sealed response hash mismatch for {phase}")
            except SimulationError as error:
                failures.append(str(error))
            try:
                parse_timestamp(str(record.get("completed_at", "")))
            except SimulationError as error:
                failures.append(str(error))

    for key in ("comparison_report", "technical_companion"):
        value = protocol.get(key)
        if value:
            normalized = str(value).replace("\\", "/")
            if normalized.startswith(FORBIDDEN_PROMOTION_PREFIXES):
                failures.append(f"{key} points at a forbidden promotion surface")

    return failures


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(pretty_json(value), encoding="utf-8", newline="\n")
    temporary.replace(path)


def seal_phase(phase: str, response: Path, completed_at: str, *, check: bool) -> dict[str, Any]:
    if phase not in ALLOWED_PHASES:
        raise SimulationError(f"unknown phase: {phase}")
    failures = validate()
    if failures:
        raise SimulationError("; ".join(failures))
    state = load_json(STATE_PATH)
    phases = state["phases"]
    record = phases[phase]
    if record["status"] == "sealed":
        raise SimulationError(f"phase is already sealed: {phase}")
    for dependency in PHASE_DEPENDENCIES[phase]:
        if phases[dependency]["status"] != "sealed":
            raise SimulationError(f"{phase} requires sealed {dependency}")
    completed = parse_timestamp(completed_at)
    not_before = parse_timestamp(record["not_before"])
    if completed < not_before:
        raise SimulationError(f"{phase} cannot be sealed before {record['not_before']}")
    response_relative = repo_relative(response)
    expected_prefix = f"mira/notes/innermost-loop-simulation/responses/{phase}"
    if not response_relative.startswith(expected_prefix):
        raise SimulationError(f"response must use {expected_prefix}*: {response_relative}")
    if not response.is_file():
        raise SimulationError(f"response does not exist: {response}")
    updated = json.loads(json.dumps(state))
    updated_record = updated["phases"][phase]
    updated_record.update(
        {
            "status": "sealed",
            "response_path": response_relative,
            "sha256": sha256_path(response),
            "completed_at": completed.isoformat().replace("+00:00", "Z"),
        }
    )
    result = {
        "phase": phase,
        "status": "ready" if check else "sealed",
        "response_path": response_relative,
        "sha256": updated_record["sha256"],
        "authority_effect": "none",
    }
    if not check:
        atomic_write_json(STATE_PATH, updated)
        failures = validate()
        if failures:
            atomic_write_json(STATE_PATH, state)
            raise SimulationError("post-seal validation failed: " + "; ".join(failures))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and seal the Innermost Loop reflection simulation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    subparsers.add_parser("status")
    seal = subparsers.add_parser("seal")
    seal.add_argument("--phase", choices=ALLOWED_PHASES, required=True)
    seal.add_argument("--response", type=Path, required=True)
    seal.add_argument("--completed-at", required=True)
    seal.add_argument("--check", action="store_true")
    return parser


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    try:
        if args.command == "validate":
            failures = validate()
            if failures:
                print(pretty_json({"status": "failed", "failures": failures}), end="")
                return 1
            print(pretty_json({"status": "valid", "authority_effect": "none"}), end="")
            return 0
        if args.command == "status":
            state = load_json(STATE_PATH)
            print(pretty_json(state), end="")
            return 0
        result = seal_phase(args.phase, args.response.resolve(), args.completed_at, check=args.check)
        print(pretty_json(result), end="")
        return 0
    except SimulationError as error:
        print(f"simulation error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

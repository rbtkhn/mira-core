#!/usr/bin/env python3
"""Compatibility surface for the retired in-checkout portability bundle."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import mira_state
from portable_paths import resolve_state_root


class PortabilityError(RuntimeError):
    pass


def validate_arguments(arguments: str, schema: dict) -> dict:
    value = json.loads(arguments)
    if not isinstance(value, dict):
        raise PortabilityError("tool arguments must be a JSON object")
    allowed, required = set(schema.get("properties", {})), set(schema.get("required", []))
    if required - set(value): raise PortabilityError("missing required tool arguments")
    if set(value) - allowed: raise PortabilityError("unknown tool arguments")
    return value


def normalize_response(provider: str, message: dict, *, thinking: bool = False) -> dict:
    if provider not in {"kimi", "deepseek", "generic-openai"}: raise PortabilityError("unsupported provider")
    calls = message.get("tool_calls", [])
    for call in calls:
        if not call.get("id") or not isinstance(call.get("function", {}).get("arguments"), str):
            raise PortabilityError("unstable or malformed tool call")
    if provider == "deepseek" and thinking and "reasoning_content" not in message:
        raise PortabilityError("DeepSeek thinking response omitted reasoning_content")
    return {"content": message.get("content"), "tool_calls": calls,
            "reasoning_content": message.get("reasoning_content") if provider == "deepseek" else None}


def adapter_fixtures() -> dict:
    tool = {"id": "call_1", "type": "function", "function": {"name": "probe", "arguments": '{"value":1}'}}
    cases = []
    for provider, message, thinking in (("kimi", {"content": None, "tool_calls": [tool]}, False),
                                        ("deepseek", {"content": None, "reasoning_content": "r", "tool_calls": [tool]}, True),
                                        ("generic-openai", {"content": "ok"}, False)):
        cases.append({"provider": provider, "ok": normalize_response(provider, message, thinking=thinking) is not None})
    return {"contract": "mira-model-adapter-v1", "ok": all(case["ok"] for case in cases), "cases": cases, "operational": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compatibility alias for explicit Mira state exports.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("verify")
    sub.add_parser("adapter-check")
    export_parser = sub.add_parser("export")
    export_parser.add_argument("--output", type=Path, required=True)
    export_parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        root = resolve_state_root()
        if args.command == "status": result = mira_state.status(root)
        elif args.command == "verify": result = mira_state.verify(root)
        elif args.command == "adapter-check": result = adapter_fixtures()
        else: result = mira_state.export(root, args.output, check=args.check)
        print(json.dumps(result, indent=2, sort_keys=True)); return 0
    except (OSError, ValueError, mira_state.StateError, PortabilityError) as error:
        print(json.dumps({"error": str(error), "command": args.command}), file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())

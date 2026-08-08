from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from yaml.events import AliasEvent

from contradiction_kernel import (
    AUTHORITY_EFFECT,
    CAPABILITY_TOKEN,
    NO_AUTHORITY_NOTICE,
    PreflightError,
    compare_packet,
    render_json,
    render_markdown,
)
from contradiction_policy import HOST_POLICY


class UniqueKeySafeLoader(yaml.SafeLoader):
    def __init__(self, stream: Any) -> None:
        super().__init__(stream)
        self._compose_depth = 0
        self._composed_nodes = 0

    def compose_node(self, parent: yaml.Node | None, index: Any) -> yaml.Node:
        if self.check_event(AliasEvent):
            raise PreflightError("packet.yaml-alias")
        self._composed_nodes += 1
        if self._composed_nodes > HOST_POLICY.bounds.max_yaml_nodes:
            raise PreflightError("packet.yaml-too-many-nodes")
        self._compose_depth += 1
        try:
            if self._compose_depth > HOST_POLICY.bounds.max_yaml_depth:
                raise PreflightError("packet.yaml-too-deep")
            return super().compose_node(parent, index)
        finally:
            self._compose_depth -= 1


UniqueKeySafeLoader.yaml_implicit_resolvers = {
    key: [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _construct_mapping(
    loader: UniqueKeySafeLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as error:
            raise PreflightError("packet.invalid-mapping-key") from error
        if duplicate:
            raise PreflightError("packet.duplicate-yaml-key")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def load_packet(path: Path) -> Any:
    try:
        size = path.stat().st_size
    except OSError as error:
        raise PreflightError("packet.read-error") from error
    if size > HOST_POLICY.bounds.max_packet_bytes:
        raise PreflightError("packet.too-large")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise PreflightError("packet.read-error") from error
    try:
        documents = list(yaml.load_all(text, Loader=UniqueKeySafeLoader))
    except PreflightError:
        raise
    except (yaml.YAMLError, RecursionError) as error:
        raise PreflightError("packet.invalid-yaml") from error
    if len(documents) != 1:
        raise PreflightError("packet.multiple-yaml-documents")
    return documents[0]


def invalid_result(error: PreflightError) -> dict[str, Any]:
    return {
        "status": "invalid",
        "errors": [{"code": code} for code in error.codes],
        "authority_effect": AUTHORITY_EFFECT,
        "capability_token": CAPABILITY_TOKEN,
        "notice": NO_AUTHORITY_NOTICE,
    }


def render_invalid(result: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(
            result, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        )
    lines = [
        "# Contradiction Preflight",
        "",
        "- Status: `invalid`",
        f"- Authority effect: `{result['authority_effect']}`",
        f"- Capability token: `{str(result['capability_token']).lower()}`",
        "",
        f"> {result['notice']}",
        "",
        "## Errors",
        "",
        *[f"- `{item['code']}`" for item in result["errors"]],
    ]
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only contradiction preflight for explicit structured facts."
    )
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    try:
        result = compare_packet(load_packet(args.packet), HOST_POLICY)
    except PreflightError as error:
        print(render_invalid(invalid_result(error), args.format))
        return 1
    rendered = render_json(result) if args.format == "json" else render_markdown(result)
    print(rendered, end="" if rendered.endswith("\n") else "\n")
    return 0 if result["disposition"] in {"continue", "continue-provisional"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

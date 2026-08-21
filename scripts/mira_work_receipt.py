from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FIELDS = (
    "Receipt target",
    "Primary user or stakeholder",
    "Process or decision improved",
    "Observable proof of usefulness",
    "Human review or handoff point",
    "Handoff quality",
    "What changed",
    "Evidence or artifacts used",
    "Decisions made",
    "Risks or limits",
    "Next owner can act without rediscovery",
)

KNOWN_RECEIPT_LABELS = frozenset(
    REQUIRED_FIELDS
    + (
        "Mira Work completion",
        "Objective",
        "Organizational consequence",
        "Compression class",
        "Authorized boundary",
        "Validation profile and result",
        "Reached boundary",
        "Outcome evidence or correction",
        "Unresolved dependency",
        "Re-entry point",
        "Persistence",
    )
)

FENCE_RE = re.compile(r"^\s*(```|~~~)")
LIST_MARKER_RE = re.compile(r"^\s*(?:[-*+]\s+)?(?P<label>.*?)\s*$")


class ReceiptError(ValueError):
    pass


def normalize_label(value: str) -> str:
    match = LIST_MARKER_RE.match(value)
    label = match.group("label") if match else value
    label = label.strip()
    while label and label[0] in "*_`":
        label = label[1:].strip()
    while label and label[-1] in "*_`":
        label = label[:-1].strip()
    return re.sub(r"\s+", " ", label)


def split_label(line: str) -> tuple[str, str] | None:
    if ":" not in line:
        return None
    raw_label, value = line.split(":", 1)
    label = normalize_label(raw_label)
    if not label:
        return None
    return label, value.strip()


def is_receipt_start(line: str) -> bool:
    parsed = split_label(line)
    return parsed is not None and parsed[0].casefold() == "mira work completion"


def parse_receipt_fields(text: str) -> dict[str, str]:
    required_by_key = {field.casefold(): field for field in REQUIRED_FIELDS}
    known_keys = {field.casefold() for field in KNOWN_RECEIPT_LABELS}
    values: dict[str, list[str]] = {}
    current_field: str | None = None
    in_fence = False
    parse_fence = False

    def consume(line: str) -> None:
        nonlocal current_field
        parsed = split_label(line)
        if parsed is not None:
            label, inline_value = parsed
            key = label.casefold()
            if key in required_by_key:
                field = required_by_key[key]
                values.setdefault(field, [])
                if inline_value:
                    values[field].append(inline_value)
                current_field = field
                return
            if key in known_keys:
                current_field = None
                return
        if current_field and line.strip():
            values[current_field].append(line.strip())

    for line in text.splitlines():
        if FENCE_RE.match(line):
            if in_fence:
                in_fence = False
                parse_fence = False
                current_field = None
            else:
                in_fence = True
                parse_fence = False
                current_field = None
            continue

        if in_fence and not parse_fence:
            if is_receipt_start(line):
                parse_fence = True
                current_field = None
            continue

        if not in_fence or parse_fence:
            consume(line)

    return {field: "\n".join(parts).strip() for field, parts in values.items() if "\n".join(parts).strip()}


def resolve_markdown_file(path: Path) -> Path:
    try:
        resolved = path.expanduser().resolve(strict=True)
    except OSError as exc:
        raise ReceiptError(f"unreadable path: {path}") from exc

    repo_root = REPO_ROOT.resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise ReceiptError(f"path is outside repository: {path}") from exc

    if not resolved.is_file():
        raise ReceiptError(f"path is not a file: {path}")
    if resolved.suffix.casefold() != ".md":
        raise ReceiptError(f"path is not a Markdown file: {path}")
    return resolved


def check_receipt(path: Path) -> dict[str, Any]:
    resolved = resolve_markdown_file(path)
    try:
        text = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReceiptError(f"could not read file: {path}") from exc

    fields = parse_receipt_fields(text)
    present_fields = [field for field in REQUIRED_FIELDS if field in fields]
    missing_fields = [field for field in REQUIRED_FIELDS if field not in fields]
    status = "pass" if not missing_fields else "fail"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "file": resolved.relative_to(REPO_ROOT.resolve()).as_posix(),
        "required_fields": list(REQUIRED_FIELDS),
        "present_fields": present_fields,
        "missing_fields": missing_fields,
        "authority_effect": "none",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check Mira Work completion receipt structure.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    receipt_check = subparsers.add_parser("receipt-check", help="Check a Markdown Mira Work completion note.")
    receipt_check.add_argument("--file", required=True, type=Path, help="Markdown file inside this repository.")
    receipt_check.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser


def emit_text(result: dict[str, Any]) -> None:
    print(f"mira_work_receipt={result['status']}")
    for field in result["missing_fields"]:
        print(f"missing_field={field}")


def main(arguments: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(arguments)

    try:
        result = check_receipt(args.file)
    except ReceiptError as exc:
        if getattr(args, "json", False):
            print(
                json.dumps(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "status": "error",
                        "file": str(args.file),
                        "required_fields": list(REQUIRED_FIELDS),
                        "present_fields": [],
                        "missing_fields": list(REQUIRED_FIELDS),
                        "authority_effect": "none",
                        "error": str(exc),
                    },
                    indent=2,
                )
            )
        else:
            print(f"mira_work_receipt_error={exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        emit_text(result)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

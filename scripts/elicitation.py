from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import choice_ledger


INTERACTION_TYPES = {"decision-navigation", "neutral-evidence"}
DECISION_ROLES = (
    "recommended",
    "alternative",
    "overlooked",
    "pause-or-deepen",
)
RESERVED_VERBS = ("execute", "commit", "push", "send")
ACTION_LABEL_RE = re.compile(
    r"^\s*(execute|commit|push|send)(?=\s|:|$)", re.IGNORECASE
)
LETTER_RE = re.compile(r"^[A-Z]$")
AUTHORITY_EFFECT = "none"
MAX_QUESTIONS = 10


class ElicitationError(ValueError):
    pass


def _text(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ElicitationError(f"{label} must be a non-empty string")
    return value.strip()


def _timestamp(value: Any) -> str | None:
    if value is None:
        return None
    text = _text(value, label="presented_at")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise ElicitationError(f"invalid presented_at timestamp: {text}") from error
    if parsed.tzinfo is None:
        raise ElicitationError("presented_at must include a timezone")
    return text


def _reserved_verb(label: str) -> str | None:
    match = ACTION_LABEL_RE.match(label)
    return match.group(1).lower() if match else None


def _receipt_options(options: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"key": item["key"], "role": item["role"], "text": item["label"]}
        for item in options
    ]


def validate_elicitation_surface(surface: Any) -> dict[str, Any]:
    if not isinstance(surface, dict):
        raise ElicitationError("surface must be an object")
    interaction_type = surface.get("type", surface.get("interaction_type"))
    if interaction_type not in INTERACTION_TYPES:
        raise ElicitationError(
            "surface type must be decision-navigation or neutral-evidence"
        )
    raw_options = surface.get("options")
    expected_counts = (3, 4) if interaction_type == "decision-navigation" else (2, 3, 4)
    if not isinstance(raw_options, list) or len(raw_options) not in expected_counts:
        counts = "three or four" if interaction_type == "decision-navigation" else "two to four"
        raise ElicitationError(f"{interaction_type} requires {counts} options")

    options: list[dict[str, Any]] = []
    keys: set[str] = set()
    labels: set[str] = set()
    roles: set[str] = set()
    for index, raw in enumerate(raw_options):
        if not isinstance(raw, dict):
            raise ElicitationError("each option must be an object")
        key = _text(raw.get("key"), label="option key")
        label = _text(raw.get("label", raw.get("text")), label="option label")
        if key in keys or label.casefold() in labels:
            raise ElicitationError("option keys and labels must be unique")
        keys.add(key)
        labels.add(label.casefold())
        normalized: dict[str, Any] = {
            "key": key,
            "letter": chr(ord("A") + index),
            "label": label,
        }
        if interaction_type == "decision-navigation":
            role = _text(raw.get("role"), label="decision role")
            if role not in DECISION_ROLES:
                raise ElicitationError(f"unsupported decision role: {role}")
            if role in roles:
                raise ElicitationError("decision roles must be unique")
            roles.add(role)
            normalized["role"] = role
            if "control" in raw:
                raise ElicitationError("decision options do not accept intake controls")
        else:
            if "role" in raw:
                raise ElicitationError("neutral evidence options must not assign roles")
            if _reserved_verb(label):
                raise ElicitationError(
                    "neutral evidence options must not use action-authorizing labels"
                )
            control = raw.get("control")
            if control is not None:
                if not isinstance(control, str) or control.casefold() != "hold":
                    raise ElicitationError("neutral evidence control must be hold")
                normalized["control"] = "hold"
        options.append(normalized)

    if interaction_type == "decision-navigation":
        required = {"recommended", "alternative", "overlooked"}
        if len(options) == 4:
            required.add("pause-or-deepen")
        if roles != required:
            raise ElicitationError(
                f"decision roles must be exactly {sorted(required)}"
            )

    presented_at = _timestamp(surface.get("presented_at"))
    normalized_surface = {
        "type": interaction_type,
        "options": options,
        "authority_effect": AUTHORITY_EFFECT,
    }
    if presented_at is not None:
        normalized_surface["presented_at"] = presented_at
    return normalized_surface


def _selected_letters(
    response: str, *, available: set[str], separator: str | None
) -> list[str]:
    parts = [response] if separator is None else response.split(separator)
    letters = [part.strip().upper() for part in parts]
    if any(not part for part in letters):
        raise ElicitationError("response contains an empty selection")
    if any(not LETTER_RE.fullmatch(part) for part in letters):
        raise ElicitationError("responses must use presentation-order letters")
    if len(set(letters)) != len(letters):
        raise ElicitationError("response contains duplicate letters")
    unknown = [letter for letter in letters if letter not in available]
    if unknown:
        raise ElicitationError(f"unknown option letter(s): {', '.join(unknown)}")
    return letters


def _branch(option: dict[str, Any], *, allow_action: bool) -> dict[str, Any]:
    verb = _reserved_verb(option["label"]) if allow_action else None
    result = {
        "option_key": option["key"],
        "letter": option["letter"],
        "role": option.get("role"),
        "visible_label": option["label"],
        "action_authorized": verb is not None,
        "normalized_reserved_verb": verb,
        "exact_bounded_action_label": option["label"] if verb else None,
        "authority_effect": AUTHORITY_EFFECT,
    }
    if "control" in option:
        result["control"] = option["control"]
    return result


def interpret_elicitation_response(surface: Any, response: Any) -> dict[str, Any]:
    normalized = validate_elicitation_surface(surface)
    text = _text(response, label="response")
    if "," in text and ">" in text:
        raise ElicitationError("mixed compound and ranked syntax is invalid")
    option_by_letter = {item["letter"]: item for item in normalized["options"]}
    available = set(option_by_letter)

    if normalized["type"] == "neutral-evidence":
        if "," in text or ">" in text:
            raise ElicitationError(
                "neutral evidence accepts one factual answer or free-form evidence"
            )
        candidate = text.upper()
        if LETTER_RE.fullmatch(candidate):
            letters = _selected_letters(candidate, available=available, separator=None)
            selected = [_branch(option_by_letter[letters[0]], allow_action=False)]
            return {
                "mode": "single",
                "interaction_type": normalized["type"],
                "ordered_selected_branches": selected,
                "ordered_preferences": [],
                "top_preference": None,
                "freeform_evidence": None,
                "receipt_count": 0,
                "receipt_directives": [],
                "stop_on_failure": False,
                "authority_effect": AUTHORITY_EFFECT,
            }
        return {
            "mode": "freeform",
            "interaction_type": normalized["type"],
            "ordered_selected_branches": [],
            "ordered_preferences": [],
            "top_preference": None,
            "freeform_evidence": text,
            "receipt_count": 0,
            "receipt_directives": [],
            "stop_on_failure": False,
            "authority_effect": AUTHORITY_EFFECT,
        }

    separator = ">" if ">" in text else ("," if "," in text else None)
    mode = "ranked" if separator == ">" else ("compound" if separator == "," else "single")
    letters = _selected_letters(text, available=available, separator=separator)
    if mode in {"ranked", "compound"} and len(letters) < 2:
        raise ElicitationError(f"{mode} responses require at least two letters")
    selected_options = [option_by_letter[letter] for letter in letters]
    if mode == "compound" and any(
        option.get("role") == "pause-or-deepen" for option in selected_options
    ):
        raise ElicitationError(
            "pause-or-deepen cannot be combined with another branch"
        )

    if mode == "ranked":
        preferences = [_branch(option, allow_action=False) for option in selected_options]
        return {
            "mode": mode,
            "interaction_type": normalized["type"],
            "ordered_selected_branches": [],
            "ordered_preferences": preferences,
            "top_preference": preferences[0],
            "next_read_only_branch": preferences[0],
            "receipt_count": 0,
            "receipt_directives": [],
            "stop_on_failure": False,
            "authority_effect": AUTHORITY_EFFECT,
        }

    branches = [_branch(option, allow_action=True) for option in selected_options]
    receipt_options = _receipt_options(normalized["options"])
    option_hash = choice_ledger.digest(receipt_options)
    presented_at = normalized.get("presented_at")
    directives = [
        {
            "selected_key": branch["option_key"],
            "selected_letter": branch["letter"],
            "options": receipt_options,
            "options_hash": option_hash,
            "presented_at": presented_at,
            "requires_presentation_timestamp": presented_at is None,
            "authority_effect": AUTHORITY_EFFECT,
        }
        for branch in branches
    ]
    return {
        "mode": mode,
        "interaction_type": normalized["type"],
        "ordered_selected_branches": branches,
        "ordered_preferences": [],
        "top_preference": None,
        "receipt_count": len(directives),
        "receipt_directives": directives,
        "stop_on_failure": mode == "compound",
        "authority_effect": AUTHORITY_EFFECT,
    }


def batch_elicitation_questions(
    questions: Any, presentation: str
) -> dict[str, Any]:
    if not isinstance(questions, list) or not questions:
        raise ElicitationError("questions must be a non-empty list")
    if len(questions) > MAX_QUESTIONS:
        raise ElicitationError("structured intake accepts at most ten questions")
    if presentation not in {"native", "text"}:
        raise ElicitationError("presentation must be native or text")
    normalized = [validate_elicitation_surface(question) for question in questions]
    if any(item["type"] != "neutral-evidence" for item in normalized):
        raise ElicitationError("structured intake questions must be neutral-evidence")
    batch_size = 3 if presentation == "native" else 1
    batches = [
        normalized[index : index + batch_size]
        for index in range(0, len(normalized), batch_size)
    ]
    return {
        "presentation": presentation,
        "question_count": len(normalized),
        "batches": batches,
        "authority_effect": AUTHORITY_EFFECT,
    }


def apply_intake_response(
    interpretation: dict[str, Any], remaining_question_keys: Iterable[str]
) -> dict[str, Any]:
    selected = interpretation.get("ordered_selected_branches", [])
    held = any(item.get("control") == "hold" for item in selected)
    remaining = list(remaining_question_keys)
    return {
        "status": "held" if held else "continue",
        "remaining_questions": [] if held else remaining,
        "stopped_questions": remaining if held else [],
        "authority_effect": AUTHORITY_EFFECT,
    }


def report_compound_failure(
    interpretation: dict[str, Any],
    failed_branch: str,
    *,
    failed_result: str = "unsuccessful",
) -> dict[str, Any]:
    if interpretation.get("mode") != "compound":
        raise ElicitationError("failure reporting requires a compound interpretation")
    branches = interpretation.get("ordered_selected_branches", [])
    index = next(
        (
            position
            for position, branch in enumerate(branches)
            if failed_branch in {branch["option_key"], branch["letter"]}
        ),
        None,
    )
    if index is None:
        raise ElicitationError("failed branch is not in the compound selection")
    failed = branches[index]
    unexecuted = branches[index + 1 :]
    return {
        "failed_branch": failed,
        "completed_branches": branches[:index],
        "unexecuted_branches": unexecuted,
        "outcome_directives": [
            {"selected_key": failed["option_key"], "result": failed_result},
            *[
                {"selected_key": branch["option_key"], "result": "no_action"}
                for branch in unexecuted
            ],
        ],
        "stop": True,
        "authority_effect": AUTHORITY_EFFECT,
    }


def _json_argument(value: str) -> Any:
    if value.lstrip().startswith(("{", "[")):
        return json.loads(value)
    path = Path(value)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and interpret low-load Elicitation surfaces."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--surface-json", required=True)
    interpret = subparsers.add_parser("interpret")
    interpret.add_argument("--surface-json", required=True)
    interpret.add_argument("--response", required=True)
    batch = subparsers.add_parser("batch")
    batch.add_argument("--questions-json", required=True)
    batch.add_argument("--presentation", choices=("native", "text"), required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    args = parse_args(arguments)
    try:
        if args.command == "validate":
            payload = validate_elicitation_surface(_json_argument(args.surface_json))
        elif args.command == "interpret":
            payload = interpret_elicitation_response(
                _json_argument(args.surface_json), args.response
            )
        else:
            payload = batch_elicitation_questions(
                _json_argument(args.questions_json), args.presentation
            )
    except (ElicitationError, json.JSONDecodeError, OSError) as error:
        print(f"elicitation error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

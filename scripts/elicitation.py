from __future__ import annotations

import argparse
import json
import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import choice_ledger
import interaction_context


INTERACTION_TYPES = {"decision-navigation", "neutral-evidence"}
DECISION_ROLES = (
    "recommended",
    "alternative",
    "overlooked",
    "pause-or-deepen",
)
RESERVED_VERBS = ("execute", "commit", "push", "send")
SELECTION_EFFECTS = ("navigate", *RESERVED_VERBS)
LEARNING_ELIGIBILITY = ("eligible", "none")
LEARNING_CHOICE_KIND = "menu-contract-decision-v1"
LEARNING_REVIEW_COHORT = "menu-contract-natural-use-v1"
ALL_NAVIGATION_REASONS = (
    "no-bounded-action",
    "material-choice-unresolved",
    "operator-requested-read-only",
)
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


def _validate_action_readiness(
    raw: Any, *, options: list[dict[str, Any]]
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ElicitationError(
            "decision-navigation requires action_readiness metadata"
        )
    ready_option_keys = raw.get("ready_option_keys")
    if not isinstance(ready_option_keys, list) or any(
        not isinstance(key, str) or not key.strip() for key in ready_option_keys
    ):
        raise ElicitationError(
            "action_readiness.ready_option_keys must be a list of option keys"
        )
    normalized_ready_keys = [key.strip() for key in ready_option_keys]
    if len(set(normalized_ready_keys)) != len(normalized_ready_keys):
        raise ElicitationError("action_readiness ready option keys must be unique")

    option_keys = {option["key"] for option in options}
    unknown = [key for key in normalized_ready_keys if key not in option_keys]
    if unknown:
        raise ElicitationError(
            "action_readiness references unknown option key(s): "
            + ", ".join(unknown)
        )
    executable_keys = [
        option["key"]
        for option in options
        if option["selection_effect"] in RESERVED_VERBS
    ]
    if set(normalized_ready_keys) != set(executable_keys):
        raise ElicitationError(
            "action_readiness ready option keys must exactly match executable options"
        )

    all_navigation_reason = raw.get("all_navigation_reason")
    blocked_action = raw.get("blocked_action")
    if executable_keys:
        if all_navigation_reason is not None:
            raise ElicitationError(
                "action-ready surfaces must not assign an all-navigation reason"
            )
        if blocked_action is not None:
            raise ElicitationError(
                "action-ready surfaces must not assign a blocked_action"
            )
    elif all_navigation_reason not in ALL_NAVIGATION_REASONS:
        raise ElicitationError(
            "all-navigation surfaces require a recognized all_navigation_reason"
        )
    elif not isinstance(blocked_action, dict):
        raise ElicitationError(
            "all-navigation surfaces require a concrete blocked_action audit"
        )

    normalized_blocked_action = None
    if not executable_keys:
        normalized_blocked_action = {
            "action": _text(blocked_action.get("action"), label="blocked_action.action"),
            "blocker": _text(blocked_action.get("blocker"), label="blocked_action.blocker"),
            "ready_when": _text(
                blocked_action.get("ready_when"), label="blocked_action.ready_when"
            ),
        }

    return {
        "ready_option_keys": normalized_ready_keys,
        "all_navigation_reason": all_navigation_reason,
        "blocked_action": normalized_blocked_action,
    }


def validate_elicitation_surface(surface: Any) -> dict[str, Any]:
    if not isinstance(surface, dict):
        raise ElicitationError("surface must be an object")
    interaction_type = surface.get("type", surface.get("interaction_type"))
    if interaction_type not in INTERACTION_TYPES:
        raise ElicitationError(
            "surface type must be decision-navigation or neutral-evidence"
        )
    final_response_present = "final_response" in surface
    final_response = surface.get("final_response", False)
    if final_response_present and not isinstance(final_response, bool):
        raise ElicitationError("final_response must be true or false")
    if interaction_type == "neutral-evidence" and final_response_present:
        raise ElicitationError(
            "neutral evidence surfaces must not assign final_response"
        )
    raw_options = surface.get("options")
    expected_counts = (3, 4) if interaction_type == "decision-navigation" else (2, 3, 4)
    if interaction_type == "decision-navigation" and final_response:
        expected_counts = (4,)
    if not isinstance(raw_options, list) or len(raw_options) not in expected_counts:
        counts = (
            "exactly four"
            if interaction_type == "decision-navigation" and final_response
            else (
                "three or four"
                if interaction_type == "decision-navigation"
                else "two to four"
            )
        )
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
            selection_effect = _text(
                raw.get("selection_effect"), label="selection_effect"
            )
            if selection_effect not in SELECTION_EFFECTS:
                raise ElicitationError(
                    f"unsupported selection_effect: {selection_effect}"
                )
            label_verb = _reserved_verb(label)
            if selection_effect == "navigate" and label_verb is not None:
                raise ElicitationError(
                    "navigate options must not use action-authorizing labels"
                )
            if selection_effect != "navigate" and label_verb != selection_effect:
                raise ElicitationError(
                    "action selection_effect must match the label's first verb"
                )
            normalized["selection_effect"] = selection_effect
            if final_response and "learning_eligibility" not in raw:
                raise ElicitationError(
                    "final-response options require explicit learning_eligibility"
                )
            learning_eligibility = raw.get("learning_eligibility", "eligible")
            if learning_eligibility not in LEARNING_ELIGIBILITY:
                raise ElicitationError(
                    "learning_eligibility must be eligible or none"
                )
            normalized["learning_eligibility"] = learning_eligibility
            if "control" in raw:
                raise ElicitationError("decision options do not accept intake controls")
        else:
            if "role" in raw:
                raise ElicitationError("neutral evidence options must not assign roles")
            if "selection_effect" in raw:
                raise ElicitationError(
                    "neutral evidence options must not assign selection_effect"
                )
            if "learning_eligibility" in raw:
                raise ElicitationError(
                    "neutral evidence options must not assign learning_eligibility"
                )
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

    action_readiness = None
    if interaction_type == "decision-navigation":
        action_readiness = _validate_action_readiness(
            surface.get("action_readiness"), options=options
        )
    elif "action_readiness" in surface:
        raise ElicitationError(
            "neutral evidence surfaces must not assign action_readiness"
        )

    presented_at = _timestamp(surface.get("presented_at"))
    normalized_surface = {
        "type": interaction_type,
        "options": options,
        "authority_effect": AUTHORITY_EFFECT,
    }
    if presented_at is not None:
        normalized_surface["presented_at"] = presented_at
    if action_readiness is not None:
        normalized_surface["action_readiness"] = action_readiness
    raw_action_context = surface.get("action_context")
    if raw_action_context is not None:
        if interaction_type != "decision-navigation":
            raise ElicitationError(
                "neutral evidence surfaces must not assign action_context"
            )
        normalized_surface["action_context"] = raw_action_context
    try:
        capsule = interaction_context.capsule_from_normalized_surface(
            normalized_surface
        )
    except interaction_context.InteractionContextError as error:
        raise ElicitationError(str(error)) from error
    if raw_action_context is not None:
        normalized_surface["action_context"] = {
            action["action_id"]: {
                "target": action["target"],
                "verification": action["verification"],
                "required_authority": action["required_authority"],
            }
            for action in capsule["pending_actions"]
        }
    normalized_surface["context_capsule"] = capsule
    if final_response_present:
        normalized_surface["final_response"] = final_response
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
    selection_effect = option.get("selection_effect")
    verb = (
        selection_effect
        if allow_action and selection_effect in RESERVED_VERBS
        else None
    )
    result = {
        "option_key": option["key"],
        "letter": option["letter"],
        "role": option.get("role"),
        "visible_label": option["label"],
        "selection_effect": selection_effect,
        "learning_eligibility": option.get("learning_eligibility"),
        "retention_effect": (
            "choice-select-eligible"
            if option.get("learning_eligibility") == "eligible"
            else "none"
        ),
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
                "context_capsule": interaction_context.capsule_from_normalized_surface(
                    normalized, state="selected", selected_letters=letters
                ),
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
            "context_capsule": normalized["context_capsule"],
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
            "context_capsule": normalized["context_capsule"],
        }

    branches = [_branch(option, allow_action=True) for option in selected_options]
    receipt_options = _receipt_options(normalized["options"])
    option_hash = choice_ledger.digest(receipt_options)
    presented_at = normalized.get("presented_at")
    retained_branches = [
        branch for branch in branches if branch["learning_eligibility"] == "eligible"
    ]
    compound_selection_id = None
    if mode == "compound" and presented_at is not None and len(retained_branches) >= 2:
        compound_selection_id = (
            "compound-"
            + hashlib.sha256(
                json.dumps(
                    {
                        "options_hash": option_hash,
                        "letters": [
                            branch["letter"] for branch in retained_branches
                        ],
                        "presented_at": presented_at,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()[:24]
        )
    directives = [
        {
            "selected_key": branch["option_key"],
            "selected_letter": branch["letter"],
            "options": receipt_options,
            "options_hash": option_hash,
            "presented_at": presented_at,
            "requires_presentation_timestamp": presented_at is None,
            "choice_kind": LEARNING_CHOICE_KIND,
            "recommended_review_cohort": LEARNING_REVIEW_COHORT,
            "authority_effect": AUTHORITY_EFFECT,
            "final_response": normalized.get("final_response", False),
        }
        | (
            {
                "compound_selection_id": compound_selection_id,
                "compound_order": index + 1,
                "compound_size": len(retained_branches),
            }
            if compound_selection_id
            else {}
        )
        for index, branch in enumerate(retained_branches)
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
        "final_response": normalized.get("final_response", False),
        "context_capsule": interaction_context.capsule_from_normalized_surface(
            normalized, state="selected", selected_letters=letters
        ),
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
            *(
                [{"selected_key": failed["option_key"], "result": failed_result}]
                if failed["learning_eligibility"] == "eligible"
                else []
            ),
            *[
                {"selected_key": branch["option_key"], "result": "no_action"}
                for branch in unexecuted
                if branch["learning_eligibility"] == "eligible"
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

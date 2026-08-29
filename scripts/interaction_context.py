from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
DISPLAY_POLICY = "silent-by-default"
AUTHORITY_NONE = "none"
CAPSULE_STATES = {"awaiting-selection", "selected", "closed"}
ACTION_EFFECTS = {
    "execute",
    "commit",
    "push",
    "send",
    "stage",
    "publish",
    "deploy",
    "spend",
    "communicate",
}
CADENCE_COMMANDS = {"coffee", "dream", "rest"}
VAGUE_IMPERATIVES = {"make it so", "go ahead", "do it"}
SOFT_ASSENT = {"sounds good", "very well", "as you wish", "i defer to you"}
EXPLICIT_COMMAND_PATTERNS = (
    re.compile(r"^(?:stage|commit|push|send|publish|deploy)\b.*$", re.IGNORECASE),
)
LETTER_RE = re.compile(r"^[A-Z]$")
COMPOUND_LETTERS_RE = re.compile(r"^[A-Z](?:\s*,\s*[A-Z])+$")
ACTION_LABEL_RE = re.compile(r"^\s*(execute|commit|push|send)(?=\s|:|$)", re.IGNORECASE)


class InteractionContextError(ValueError):
    pass


def _text(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InteractionContextError(f"{label} must be a non-empty string")
    return value.strip()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(payload: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in payload.items() if key != "context_digest"}
    return hashlib.sha256(_canonical(unsigned).encode("utf-8")).hexdigest()


def _pending_action(value: Any, *, fallback_id: str | None = None) -> dict[str, str]:
    if not isinstance(value, dict):
        raise InteractionContextError("pending action must be an object")
    effect = _text(value.get("effect"), label="pending action effect").casefold()
    if effect not in ACTION_EFFECTS:
        raise InteractionContextError(f"unsupported pending action effect: {effect}")
    visible_label = _text(
        value.get("visible_label"), label="pending action visible label"
    )
    if effect in {"execute", "commit", "push", "send"}:
        match = ACTION_LABEL_RE.match(visible_label)
        if not match or match.group(1).casefold() != effect:
            raise InteractionContextError(
                "pending action effect must match its visible action verb"
            )
    return {
        "action_id": _text(value.get("action_id", fallback_id), label="pending action id"),
        "visible_label": visible_label,
        "effect": effect,
        "target": _text(value.get("target"), label="pending action target"),
        "verification": _text(value.get("verification"), label="pending action verification"),
        "required_authority": _text(
            value.get("required_authority"), label="pending action required authority"
        ),
    }


def _surface_action_context(
    surface: dict[str, Any], *, ready_keys: set[str]
) -> tuple[list[dict[str, str]], list[str]]:
    raw = surface.get("action_context")
    if raw is None:
        return [], sorted(ready_keys)
    if not isinstance(raw, dict):
        raise InteractionContextError("action_context must be an object keyed by option key")
    unknown = sorted(set(raw) - ready_keys)
    if unknown:
        raise InteractionContextError(
            "action_context references non-ready option key(s): " + ", ".join(unknown)
        )
    pending = []
    for option in surface.get("options", []):
        key = option.get("key")
        if key not in raw:
            continue
        item = dict(raw[key]) if isinstance(raw[key], dict) else raw[key]
        if isinstance(item, dict):
            item.setdefault("action_id", key)
            item.setdefault("visible_label", option.get("label"))
            item.setdefault("effect", option.get("selection_effect"))
        pending.append(_pending_action(item, fallback_id=key))
    return pending, sorted(ready_keys - set(raw))


def capsule_from_normalized_surface(
    surface: dict[str, Any],
    *,
    state: str = "awaiting-selection",
    selected_letters: list[str] | None = None,
) -> dict[str, Any]:
    if state not in CAPSULE_STATES:
        raise InteractionContextError(f"unsupported capsule state: {state}")
    options = surface.get("options")
    if not isinstance(options, list) or not options:
        raise InteractionContextError("normalized surface must contain options")
    visible_options = [
        {
            "key": _text(item.get("key"), label="option key"),
            "letter": _text(item.get("letter"), label="option letter"),
            "visible_label": _text(item.get("label"), label="option label"),
            "role": item.get("role"),
            "selection_effect": item.get("selection_effect"),
        }
        for item in options
    ]
    ready = set((surface.get("action_readiness") or {}).get("ready_option_keys", []))
    pending, incomplete = _surface_action_context(surface, ready_keys=ready)
    selected_letters = selected_letters or []
    by_letter = {item["letter"]: item for item in visible_options}
    if any(letter not in by_letter for letter in selected_letters):
        raise InteractionContextError("selected letter is not present in the surface")
    if state == "awaiting-selection" and selected_letters:
        raise InteractionContextError("awaiting-selection capsules cannot select branches")
    if state in {"selected", "closed"} and not selected_letters:
        raise InteractionContextError(f"{state} capsules require a selected letter")
    selected = [by_letter[letter] for letter in selected_letters]
    selected_keys = {item["key"] for item in selected}
    if selected_keys:
        pending = [item for item in pending if item["action_id"] in selected_keys]
        ready = ready & selected_keys
        incomplete = [key for key in incomplete if key in selected_keys]
    if state == "closed":
        ready = set()
        incomplete = []
    capsule: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "state": state,
        "interaction_type": surface.get("type"),
        "visible_options": visible_options,
        "ready_option_keys": sorted(ready),
        "selected_branches": selected,
        "pending_actions": [] if state == "closed" else pending,
        "incomplete_action_context_keys": incomplete,
        "display_policy": DISPLAY_POLICY,
        "persistence": "none",
        "authority_effect": AUTHORITY_NONE,
    }
    capsule["context_digest"] = _digest(capsule)
    return capsule


def capsule_from_pending_action(
    action: dict[str, Any], *, state: str = "awaiting-selection"
) -> dict[str, Any]:
    if state not in CAPSULE_STATES:
        raise InteractionContextError(f"unsupported capsule state: {state}")
    pending = _pending_action(action)
    capsule: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "state": state,
        "interaction_type": "pending-action",
        "visible_options": [],
        "ready_option_keys": [],
        "selected_branches": [],
        "pending_actions": [] if state == "closed" else [pending],
        "incomplete_action_context_keys": [],
        "display_policy": DISPLAY_POLICY,
        "persistence": "none",
        "authority_effect": AUTHORITY_NONE,
    }
    capsule["context_digest"] = _digest(capsule)
    return capsule


def validate_capsule(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InteractionContextError("capsule must be an object")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise InteractionContextError("unsupported capsule schema version")
    if value.get("state") not in CAPSULE_STATES:
        raise InteractionContextError("invalid capsule state")
    if value.get("display_policy") != DISPLAY_POLICY:
        raise InteractionContextError("capsule display policy must be silent-by-default")
    if value.get("persistence") != "none" or value.get("authority_effect") != AUTHORITY_NONE:
        raise InteractionContextError("capsule must grant no authority or persistence")
    supplied = _text(value.get("context_digest"), label="context digest")
    if supplied != _digest(value):
        raise InteractionContextError("capsule digest mismatch")
    if not isinstance(value.get("visible_options"), list):
        raise InteractionContextError("visible_options must be a list")
    if not isinstance(value.get("pending_actions"), list):
        raise InteractionContextError("pending_actions must be a list")
    options = value["visible_options"]
    option_keys: set[str] = set()
    option_letters: set[str] = set()
    option_by_key: dict[str, dict[str, Any]] = {}
    for option in options:
        if not isinstance(option, dict):
            raise InteractionContextError("visible option must be an object")
        key = _text(option.get("key"), label="visible option key")
        letter = _text(option.get("letter"), label="visible option letter")
        _text(option.get("visible_label"), label="visible option label")
        if not LETTER_RE.fullmatch(letter) or key in option_keys or letter in option_letters:
            raise InteractionContextError("visible option keys and letters must be unique")
        option_keys.add(key)
        option_letters.add(letter)
        option_by_key[key] = option
    ready = value.get("ready_option_keys")
    if not isinstance(ready, list) or len(ready) != len(set(ready)):
        raise InteractionContextError("ready_option_keys must be a unique list")
    if any(key not in option_keys for key in ready):
        raise InteractionContextError("ready option is not present in visible options")
    for key in ready:
        option = option_by_key[key]
        effect = option.get("selection_effect")
        match = ACTION_LABEL_RE.match(option["visible_label"])
        if effect not in {"execute", "commit", "push", "send"} or not match or match.group(1).casefold() != effect:
            raise InteractionContextError("ready option effect must match its visible action verb")
    selected = value.get("selected_branches")
    if not isinstance(selected, list):
        raise InteractionContextError("selected_branches must be a list")
    for branch in selected:
        if not isinstance(branch, dict) or branch.get("key") not in option_by_key:
            raise InteractionContextError("selected branch is not present in visible options")
        if branch != option_by_key[branch["key"]]:
            raise InteractionContextError("selected branch does not match its visible option")
    state = value["state"]
    if state == "awaiting-selection" and selected:
        raise InteractionContextError("awaiting-selection capsule cannot contain a selection")
    if state == "selected" and not selected and value.get("interaction_type") != "pending-action":
        raise InteractionContextError("selected capsule requires a selected branch")
    if state == "closed" and value["pending_actions"]:
        raise InteractionContextError("closed capsule cannot contain pending actions")
    pending_by_id: dict[str, dict[str, str]] = {}
    for action in value["pending_actions"]:
        normalized_action = _pending_action(action)
        action_id = normalized_action["action_id"]
        if action_id in pending_by_id:
            raise InteractionContextError("pending action ids must be unique")
        pending_by_id[action_id] = normalized_action
        if value.get("interaction_type") != "pending-action":
            option = option_by_key.get(action_id)
            if option is None or action_id not in ready:
                raise InteractionContextError("pending action must bind a ready visible option")
            if (
                normalized_action["visible_label"] != option["visible_label"]
                or normalized_action["effect"] != option.get("selection_effect")
            ):
                raise InteractionContextError("pending action does not match its visible option")
    incomplete = value.get("incomplete_action_context_keys")
    if not isinstance(incomplete, list) or len(incomplete) != len(set(incomplete)):
        raise InteractionContextError("incomplete action context keys must be a unique list")
    if any(key not in ready for key in incomplete):
        raise InteractionContextError("incomplete action context must reference ready options")
    if set(incomplete) & set(pending_by_id):
        raise InteractionContextError("action context cannot be both complete and incomplete")
    if value.get("interaction_type") != "pending-action" and (
        set(pending_by_id) | set(incomplete)
    ) != set(ready):
        raise InteractionContextError("every ready option needs a complete or incomplete action context")
    return value


def _result(
    classification: str,
    *,
    route: str,
    exact_meaning: Any = None,
    ambiguity: str | None = None,
    authority_effect: str = AUTHORITY_NONE,
    action_authorized: bool = False,
) -> dict[str, Any]:
    return {
        "classification": classification,
        "exact_meaning": exact_meaning,
        "next_route": route,
        "ambiguity": ambiguity,
        "action_authorized": action_authorized,
        "authority_effect": authority_effect,
        "persistence": "none",
    }


def resolve_followup(
    capsule: Any, response: Any, *, expected_context_digest: str | None = None
) -> dict[str, Any]:
    current = validate_capsule(capsule)
    if expected_context_digest and current["context_digest"] != expected_context_digest:
        return _result(
            "clarification-required",
            route="intent-recovery",
            ambiguity="stale-context",
        )
    text = _text(response, label="response")
    folded = " ".join(text.casefold().split())
    state = current["state"]

    if folded in CADENCE_COMMANDS:
        return _result(
            "cadence-command",
            route=f"skill:{folded}",
            exact_meaning=folded,
        )
    if any(pattern.fullmatch(text.strip()) for pattern in EXPLICIT_COMMAND_PATTERNS):
        return _result(
            "explicit-direct-command",
            route="domain-authority-router",
            exact_meaning=text.strip(),
        )
    if folded in SOFT_ASSENT:
        return _result("agreement-only", route="conversation", exact_meaning=folded)

    candidate = text.strip().upper()
    if LETTER_RE.fullmatch(candidate):
        options = {item["letter"]: item for item in current["visible_options"]}
        if candidate not in options:
            return _result(
                "clarification-required",
                route="intent-recovery",
                ambiguity="unknown-option-letter",
            )
        option = options[candidate]
        if state == "closed":
            return _result("settled-no-op", route="conversation", exact_meaning=option)
        if any(item.get("letter") == candidate for item in current["selected_branches"]):
            return _result("selection-already-recorded", route="conversation", exact_meaning=option)
        if state == "selected":
            return _result(
                "clarification-required",
                route="intent-recovery",
                ambiguity="branch-already-selected",
            )
        effect = option.get("selection_effect")
        action_authorized = effect in {"execute", "commit", "push", "send"}
        return _result(
            "exact-menu-selection",
            route="elicitation-selection",
            exact_meaning=option,
            authority_effect=effect if action_authorized else AUTHORITY_NONE,
            action_authorized=action_authorized,
        )
    if COMPOUND_LETTERS_RE.fullmatch(candidate):
        options = {item["letter"]: item for item in current["visible_options"]}
        letters = [part.strip() for part in candidate.split(",")]
        if len(set(letters)) != len(letters):
            return _result(
                "clarification-required",
                route="intent-recovery",
                ambiguity="duplicate-option-letter",
            )
        unknown = [letter for letter in letters if letter not in options]
        if unknown:
            return _result(
                "clarification-required",
                route="intent-recovery",
                ambiguity="unknown-option-letter",
            )
        selected = [options[letter] for letter in letters]
        if any(item.get("role") == "pause-or-deepen" for item in selected):
            return _result(
                "clarification-required",
                route="intent-recovery",
                ambiguity="pause-or-deepen-cannot-be-compounded",
            )
        if state == "closed":
            return _result("settled-no-op", route="conversation", exact_meaning=selected)
        already = {
            item.get("letter") for item in current["selected_branches"]
        } & set(letters)
        if already:
            return _result(
                "selection-already-recorded",
                route="conversation",
                exact_meaning=selected,
            )
        if state == "selected":
            return _result(
                "clarification-required",
                route="intent-recovery",
                ambiguity="branch-already-selected",
            )
        return _result(
            "exact-compound-menu-selection",
            route="elicitation-selection",
            exact_meaning={
                "mode": "compound",
                "ordered_selected_branches": selected,
            },
        )

    if folded in VAGUE_IMPERATIVES:
        if state == "closed":
            return _result("settled-no-op", route="conversation")
        actions = current["pending_actions"]
        if len(actions) != 1:
            return _result(
                "clarification-required",
                route="intent-recovery",
                ambiguity="requires-exactly-one-pending-action",
            )
        action = actions[0]
        if action["effect"] != "execute":
            return _result(
                "clarification-required",
                route="domain-authority-router",
                exact_meaning=action,
                ambiguity="direct-command-required-for-consequential-effect",
            )
        return _result(
            "bounded-continuation",
            route="execute-bounded-action",
            exact_meaning=action,
            authority_effect="execute",
            action_authorized=True,
        )

    if folded == "yes":
        yes_options = [
            option
            for option in current["visible_options"]
            if option["visible_label"].casefold() == "yes"
            and option.get("selection_effect") in {None, "navigate"}
        ]
        if len(yes_options) == 1 and not current["pending_actions"]:
            return _result(
                "factual-confirmation",
                route="elicitation-evidence",
                exact_meaning=yes_options[0],
            )
        return _result(
            "clarification-required",
            route="intent-recovery",
            ambiguity="yes-does-not-authorize-action",
        )

    return _result(
        "intent-recovery-required",
        route="intent-recovery",
        ambiguity="unrecognized-or-free-form-followup",
    )


def _json_argument(value: str) -> Any:
    if value.lstrip().startswith(("{", "[")):
        return json.loads(value)
    path = Path(value)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and resolve transient interaction context.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    capsule = subparsers.add_parser("capsule")
    source = capsule.add_mutually_exclusive_group(required=True)
    source.add_argument("--surface-json")
    source.add_argument("--pending-action-json")
    capsule.add_argument("--state", choices=sorted(CAPSULE_STATES), default="awaiting-selection")
    capsule.add_argument("--selected-letter", action="append", default=[])
    capsule.add_argument("--json", action="store_true")
    resolve = subparsers.add_parser("resolve")
    resolve.add_argument("--capsule-json", required=True)
    resolve.add_argument("--response", required=True)
    resolve.add_argument("--expected-context-digest")
    resolve.add_argument("--json", action="store_true")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    args = parse_args(arguments)
    try:
        if args.command == "capsule":
            if args.surface_json:
                import elicitation

                surface = elicitation.validate_elicitation_surface(_json_argument(args.surface_json))
                payload = capsule_from_normalized_surface(
                    surface,
                    state=args.state,
                    selected_letters=[letter.upper() for letter in args.selected_letter],
                )
            else:
                if args.selected_letter:
                    raise InteractionContextError("pending-action capsules do not accept selected letters")
                payload = capsule_from_pending_action(
                    _json_argument(args.pending_action_json), state=args.state
                )
        else:
            payload = resolve_followup(
                _json_argument(args.capsule_json),
                args.response,
                expected_context_digest=args.expected_context_digest,
            )
    except (InteractionContextError, json.JSONDecodeError, OSError, ValueError) as error:
        print(f"interaction-context error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
CLAIMS_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "reality" / "claims"
SCHEMA = "research-execution-handoff-v1"
SEED_SCHEMA = "research-brief-seed-v1"
WORKFLOWS = {
    "morning-brief",
    "reality-check",
    "world-monitor",
    "intake",
    "geopolitical-synthesis",
    "external-research",
}
SEED_PRODUCERS = {"reality-handoff", "world-monitor", "continuity-triage"}
SEED_FIELDS = {
    "schema",
    "producer",
    "decision_context",
    "candidate_question",
    "scope_hints",
    "known_context",
    "unresolved_gaps",
    "rival_hints",
    "routing_hint",
    "identifiers",
    "authority",
}
SEED_FORBIDDEN_FIELDS = {
    "compatibility",
    "disposition",
    "research_contract",
    "explicit_execution_request",
    "execution_intent",
}
DISPOSITIONS = {
    "ready",
    "needs-scope-normalization",
    "needs-claim-resolution",
    "incompatible",
}
AUTHORITY = {
    "execute": False,
    "mutate": False,
    "publish": False,
    "communicate": False,
}
CLAIM_ID_RE = re.compile(r"(?:OPC-\d{8}-\d{2}|NG-\d{8}-F\d{2}|CLM-\d{8}-\d{3})$")
REQUIRED_CONTRACT_FIELDS = {
    "research_questions",
    "evidence_plan",
    "rival_explanations",
    "contradiction_protocol",
    "finding_format",
    "stop_condition",
}


def require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def require_text(value: Any, field: str, *, maximum: int | None = None) -> str:
    if not isinstance(value, str) or not value.strip() or value.lstrip().startswith("<"):
        raise ValueError(f"{field} must be populated text")
    result = value.strip()
    if maximum is not None and len(result) > maximum:
        raise ValueError(f"{field} must contain at most {maximum} characters")
    return result


def require_exact_fields(value: dict[str, Any], expected: set[str], field: str) -> None:
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    if missing:
        raise ValueError(f"{field} missing fields: " + ", ".join(missing))
    if extra:
        raise ValueError(f"{field} has unsupported fields: " + ", ".join(extra))


def bounded_text_list(
    value: Any,
    field: str,
    *,
    minimum: int = 0,
    maximum_items: int = 12,
    maximum_text: int = 500,
) -> list[str]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum_items:
        raise ValueError(
            f"{field} must contain between {minimum} and {maximum_items} items"
        )
    return [
        require_text(item, f"{field}[{index}]", maximum=maximum_text)
        for index, item in enumerate(value)
    ]


def forbidden_seed_fields(value: Any, *, path: str = "seed") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}"
            if key in SEED_FORBIDDEN_FIELDS:
                failures.append(child)
            failures.extend(forbidden_seed_fields(item, path=child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            failures.extend(forbidden_seed_fields(item, path=f"{path}[{index}]"))
    return failures


def claim_exists(claim_id: str, claims_root: Path) -> bool:
    for path in sorted(claims_root.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(record, dict) and record.get("id") == claim_id:
            return True
    return False


def classify(packet: dict[str, Any], *, claims_root: Path = CLAIMS_ROOT) -> tuple[str, list[str]]:
    destination = require_mapping(packet.get("destination"), "destination")
    prerequisites = require_mapping(packet.get("prerequisites"), "prerequisites")
    scope = require_mapping(packet.get("scope"), "scope")
    workflow = destination.get("workflow")
    if workflow not in WORKFLOWS:
        raise ValueError("destination.workflow must name a supported workflow")

    if workflow == "morning-brief":
        mismatches = []
        if scope.get("coverage") != "global":
            mismatches.append("coverage must be global")
        if scope.get("time_window") != "trailing-24-hours":
            mismatches.append("time_window must be trailing-24-hours")
        if scope.get("output_form") != "five-minute-brief":
            mismatches.append("output_form must be five-minute-brief")
        if mismatches:
            return "needs-scope-normalization", mismatches
        return "ready", ["scope matches the fixed Morning Brief contract"]

    if workflow == "reality-check":
        claim_id = prerequisites.get("canonical_claim_id")
        if not isinstance(claim_id, str) or CLAIM_ID_RE.fullmatch(claim_id) is None:
            return "needs-claim-resolution", ["an exact canonical claim identifier is required"]
        if not claim_exists(claim_id, claims_root):
            return "needs-claim-resolution", [f"canonical claim is not present in the lattice: {claim_id}"]
        return "ready", [f"canonical claim exists in the lattice: {claim_id}"]

    if workflow == "world-monitor":
        objective = prerequisites.get("world_monitor_objective")
        if objective not in {"current-signal-discovery", "coverage-gap"}:
            return "incompatible", ["world_monitor_objective must be current-signal-discovery or coverage-gap"]
        return "ready", [f"World Monitor supports {objective}"]

    if workflow == "intake":
        if prerequisites.get("supplied_source_body") is not True:
            return "incompatible", ["intake requires a supplied source body"]
        return "ready", ["a supplied source body is available for intake"]

    if workflow == "geopolitical-synthesis":
        if prerequisites.get("manifest_backed_date") is not True:
            return "incompatible", ["geopolitical synthesis requires a manifest-backed archive day"]
        return "ready", ["a manifest-backed archive day is available"]

    return "ready", ["no repository execution workflow fits; route to bounded external research"]


def validate_seed(seed: Any) -> dict[str, Any]:
    root = require_mapping(seed, "seed")
    if root.get("schema") != SEED_SCHEMA:
        raise ValueError(f"schema must be {SEED_SCHEMA}")
    forbidden = forbidden_seed_fields(root)
    if forbidden:
        raise ValueError("seed contains forbidden fields: " + ", ".join(forbidden))
    require_exact_fields(root, SEED_FIELDS, "seed")

    producer = require_mapping(root["producer"], "producer")
    require_exact_fields(producer, {"workflow", "item_id", "source_refs"}, "producer")
    if producer.get("workflow") not in SEED_PRODUCERS:
        raise ValueError("producer.workflow must name a supported seed producer")
    item_id = require_text(producer.get("item_id"), "producer.item_id", maximum=300)
    bounded_text_list(
        producer.get("source_refs"),
        "producer.source_refs",
        maximum_items=20,
        maximum_text=500,
    )

    require_text(root["decision_context"], "decision_context", maximum=500)
    require_text(root["candidate_question"], "candidate_question", maximum=500)
    scope = require_mapping(root["scope_hints"], "scope_hints")
    require_exact_fields(
        scope,
        {"actors", "geography", "time_window", "languages"},
        "scope_hints",
    )
    for field in ("actors", "geography", "languages"):
        bounded_text_list(scope[field], f"scope_hints.{field}", maximum_items=12, maximum_text=200)
    if scope["time_window"] is not None:
        require_text(scope["time_window"], "scope_hints.time_window", maximum=200)

    bounded_text_list(root["known_context"], "known_context", maximum_items=12)
    bounded_text_list(root["unresolved_gaps"], "unresolved_gaps", minimum=1, maximum_items=12)
    bounded_text_list(root["rival_hints"], "rival_hints", maximum_items=8)

    routing = require_mapping(root["routing_hint"], "routing_hint")
    require_exact_fields(routing, {"workflow", "reason"}, "routing_hint")
    if routing.get("workflow") not in WORKFLOWS:
        raise ValueError("routing_hint.workflow must name a supported workflow")
    require_text(routing.get("reason"), "routing_hint.reason", maximum=500)

    identifiers = require_mapping(root["identifiers"], "identifiers")
    require_exact_fields(
        identifiers,
        {"canonical_claim_id", "forecast_ids", "reality_ids", "source_ids"},
        "identifiers",
    )
    claim_id = identifiers.get("canonical_claim_id")
    if claim_id is not None and (
        not isinstance(claim_id, str) or CLAIM_ID_RE.fullmatch(claim_id) is None
    ):
        raise ValueError("identifiers.canonical_claim_id must be a canonical claim identifier or null")
    for field in ("forecast_ids", "reality_ids", "source_ids"):
        bounded_text_list(
            identifiers[field],
            f"identifiers.{field}",
            maximum_items=20,
            maximum_text=200,
        )

    if root["authority"] != AUTHORITY:
        raise ValueError("authority must deny execute, mutate, publish, and communicate")
    return {
        "schema": SEED_SCHEMA,
        "valid": True,
        "producer": producer["workflow"],
        "item_id": item_id,
        "routing_hint": routing["workflow"],
        "authority": dict(AUTHORITY),
        "authority_effect": "none",
        "execution_triggered": False,
    }


def build_seed(
    *,
    producer_workflow: str,
    item_id: str,
    source_refs: list[str],
    decision_context: str,
    candidate_question: str,
    scope_hints: dict[str, Any],
    known_context: list[str],
    unresolved_gaps: list[str],
    rival_hints: list[str],
    routing_workflow: str,
    routing_reason: str,
    identifiers: dict[str, Any],
) -> dict[str, Any]:
    seed = {
        "schema": SEED_SCHEMA,
        "producer": {
            "workflow": producer_workflow,
            "item_id": item_id,
            "source_refs": source_refs,
        },
        "decision_context": decision_context,
        "candidate_question": candidate_question,
        "scope_hints": scope_hints,
        "known_context": known_context,
        "unresolved_gaps": unresolved_gaps,
        "rival_hints": rival_hints,
        "routing_hint": {"workflow": routing_workflow, "reason": routing_reason},
        "identifiers": identifiers,
        "authority": dict(AUTHORITY),
    }
    validate_seed(seed)
    return seed


def validate_packet(packet: Any, *, claims_root: Path = CLAIMS_ROOT) -> dict[str, Any]:
    root = require_mapping(packet, "packet")
    if root.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    require_text(root.get("decision_and_use"), "decision_and_use")
    require_text(root.get("focal_question"), "focal_question")
    require_mapping(root.get("scope"), "scope")
    contract = require_mapping(root.get("research_contract"), "research_contract")
    missing = sorted(REQUIRED_CONTRACT_FIELDS - contract.keys())
    if missing:
        raise ValueError("research_contract missing fields: " + ", ".join(missing))
    questions = contract.get("research_questions")
    if not isinstance(questions, list) or not 3 <= len(questions) <= 6:
        raise ValueError("research_contract.research_questions must contain three to six items")
    if any(not isinstance(item, str) or not item.strip() for item in questions):
        raise ValueError("research_contract.research_questions must contain non-empty text")

    prerequisites = require_mapping(root.get("prerequisites"), "prerequisites")
    if prerequisites.get("explicit_execution_request") is not False:
        raise ValueError("prerequisites.explicit_execution_request must be false")
    if root.get("authority") != AUTHORITY:
        raise ValueError("authority must deny execute, mutate, publish, and communicate")
    origin_seed = root.get("origin_seed")
    if origin_seed is not None:
        origin = require_mapping(origin_seed, "origin_seed")
        require_exact_fields(origin, {"producer", "item_id"}, "origin_seed")
        if origin.get("producer") not in SEED_PRODUCERS:
            raise ValueError("origin_seed.producer must name a supported seed producer")
        require_text(origin.get("item_id"), "origin_seed.item_id", maximum=300)

    destination = require_mapping(root.get("destination"), "destination")
    require_text(destination.get("reason"), "destination.reason")
    disposition, reasons = classify(root, claims_root=claims_root)
    if destination.get("compatibility") != disposition:
        raise ValueError(f"destination.compatibility must be {disposition}")
    if root.get("disposition") != disposition:
        raise ValueError(f"disposition must be {disposition}")
    supplied_reasons = destination.get("reasons")
    if supplied_reasons != reasons:
        raise ValueError("destination.reasons must match the deterministic compatibility reasons")

    return {
        "schema": SCHEMA,
        "valid": True,
        "workflow": destination["workflow"],
        "disposition": disposition,
        "reasons": reasons,
        "authority": dict(AUTHORITY),
        "authority_effect": "none",
        "execution_triggered": False,
    }


def load_packet(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"cannot read packet: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"packet is not valid JSON: {error.msg}") from error


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a read-only research execution handoff.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--packet", type=Path)
    target.add_argument("--seed", type=Path)
    parser.add_argument("--claims-root", type=Path, default=CLAIMS_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    args = parse_args(arguments)
    try:
        if args.seed:
            result = validate_seed(load_packet(args.seed))
        else:
            result = validate_packet(load_packet(args.packet), claims_root=args.claims_root)
    except ValueError as error:
        raise SystemExit(f"research handoff validation failed: {error}") from error
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"workflow={result['workflow']} disposition={result['disposition']} authority_effect=none")
        for reason in result["reasons"]:
            print(f"reason={reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

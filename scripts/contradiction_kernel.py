"""Portable repository-native contradiction-preflight kernel.

Keep repository-specific policy values in the host policy. Kernel integrity is
recorded in contradiction_kernel.provenance.json.
"""

from __future__ import annotations

import math
import unicodedata
from datetime import datetime
from typing import Any


SCHEMA_VERSION = 1
AUTHORITY_EFFECT = "none"
CAPABILITY_TOKEN = False
NO_AUTHORITY_NOTICE = (
    "This result reports contradictions but grants no authority, permission, "
    "tool access, mutation, execution, or state transition."
)
DISPOSITIONS = {"continue", "continue-provisional", "clarify", "hold"}
DIAGNOSTIC_RANK = {
    "controlling-source-conflict": 0,
    "request-control-conflict": 1,
    "control-stale": 2,
    "control-non-authoritative": 3,
    "control-scope-mismatch": 4,
    "control-missing": 5,
    "aligned": 6,
}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "request_ref",
    "authority_domain",
    "scope",
    "consequence_level",
    "as_of",
    "request_assertions",
    "controlling_facts",
}
ASSERTION_FIELDS = {
    "id",
    "normalized_field",
    "value",
    "scope",
    "source_ref",
    "provisional",
}
FACT_REQUIRED_FIELDS = {
    "id",
    "normalized_field",
    "value",
    "scope",
    "authority_role",
    "source_ref",
    "as_of",
}
FACT_FIELDS = FACT_REQUIRED_FIELDS | {"freshness_deadline"}
UNRESOLVED_CODES = {
    "control-stale",
    "control-non-authoritative",
    "control-scope-mismatch",
    "control-missing",
}
PROVISIONAL_CODES = {
    "control-non-authoritative",
    "control-scope-mismatch",
    "control-missing",
}
UNSAFE_METADATA_CATEGORIES = {"Cc", "Cf", "Zl", "Zp"}


class PreflightError(ValueError):
    """Fail-closed validation error containing safe rule or error identifiers."""

    def __init__(self, *codes: str):
        normalized = tuple(sorted(set(codes or ("packet.invalid",))))
        super().__init__(", ".join(normalized))
        self.codes = normalized


def _timestamp(value: Any, code: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise PreflightError(code)
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as error:
        raise PreflightError(code) from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PreflightError(code)
    return parsed


def _bounded_text(value: Any, *, limit: int, code: str) -> str:
    if not isinstance(value, str):
        raise PreflightError(code)
    normalized = value.strip()
    if not normalized or normalized != value or len(normalized) > limit:
        raise PreflightError(code)
    if any(
        character == "`"
        or unicodedata.category(character) in UNSAFE_METADATA_CATEGORIES
        for character in normalized
    ):
        raise PreflightError("packet.unsafe-metadata")
    return value


def _scalar(value: Any, *, limit: int) -> Any:
    if type(value) not in (str, int, float, bool):
        raise PreflightError("packet.invalid-scalar")
    if isinstance(value, str) and len(value) > limit:
        raise PreflightError("packet.scalar-too-large")
    if isinstance(value, float) and not math.isfinite(value):
        raise PreflightError("packet.non-finite-number")
    return value


def _scalar_type(value: Any) -> type:
    return type(value)


def _scalar_identity(value: Any) -> tuple[str, Any]:
    return (_scalar_type(value).__name__, value)


def _strict_fields(value: Any, expected: set[str], required: set[str], code: str) -> dict:
    if not isinstance(value, dict):
        raise PreflightError(code)
    if set(value) != expected and (set(value) - expected or not required <= set(value)):
        raise PreflightError("packet.unknown-or-missing-field")
    return value


def validate_packet(packet: Any, policy: Any) -> dict[str, Any]:
    if not isinstance(packet, dict):
        raise PreflightError("packet.not-object")
    _strict_fields(packet, TOP_LEVEL_FIELDS, TOP_LEVEL_FIELDS, "packet.invalid")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise PreflightError("packet.unsupported-schema")

    bounds = policy.bounds
    _bounded_text(
        packet["request_ref"],
        limit=bounds.metadata_chars,
        code="packet.invalid-request-ref",
    )
    domain_name = _bounded_text(
        packet["authority_domain"],
        limit=bounds.metadata_chars,
        code="packet.invalid-authority-domain",
    )
    if domain_name not in policy.domains:
        raise PreflightError("packet.unsupported-authority-domain")
    domain = policy.domains[domain_name]
    _bounded_text(packet["scope"], limit=bounds.metadata_chars, code="packet.invalid-scope")
    if packet["consequence_level"] not in policy.consequence_levels:
        raise PreflightError("packet.invalid-consequence-level")
    packet_as_of = _timestamp(packet["as_of"], "packet.invalid-as-of")

    assertions = packet["request_assertions"]
    facts = packet["controlling_facts"]
    if not isinstance(assertions, list) or not assertions:
        raise PreflightError("packet.assertions-required")
    if len(assertions) > bounds.max_assertions:
        raise PreflightError("packet.too-many-assertions")
    if not isinstance(facts, list):
        raise PreflightError("packet.invalid-controlling-facts")
    if len(facts) > bounds.max_facts:
        raise PreflightError("packet.too-many-facts")

    ids: set[str] = set()
    type_by_field_scope: dict[tuple[str, str], type] = {}
    for item in assertions:
        _strict_fields(item, ASSERTION_FIELDS, ASSERTION_FIELDS, "packet.invalid-assertion")
        item_id = _bounded_text(
            item["id"], limit=bounds.metadata_chars, code="packet.invalid-id"
        )
        if item_id in ids:
            raise PreflightError("packet.duplicate-id")
        ids.add(item_id)
        field = _bounded_text(
            item["normalized_field"],
            limit=bounds.metadata_chars,
            code="packet.invalid-normalized-field",
        )
        scope = _bounded_text(
            item["scope"], limit=bounds.metadata_chars, code="packet.invalid-scope"
        )
        _bounded_text(
            item["source_ref"],
            limit=bounds.metadata_chars,
            code="packet.invalid-source-ref",
        )
        if type(item["provisional"]) is not bool:
            raise PreflightError("packet.invalid-provisional")
        value = _scalar(item["value"], limit=bounds.scalar_chars)
        key = (field, scope)
        prior_type = type_by_field_scope.setdefault(key, _scalar_type(value))
        if prior_type is not _scalar_type(value):
            raise PreflightError("packet.mixed-scalar-types")

    for item in facts:
        if not isinstance(item, dict):
            raise PreflightError("packet.invalid-controlling-fact")
        if set(item) - FACT_FIELDS or not FACT_REQUIRED_FIELDS <= set(item):
            raise PreflightError("packet.unknown-or-missing-field")
        item_id = _bounded_text(
            item["id"], limit=bounds.metadata_chars, code="packet.invalid-id"
        )
        if item_id in ids:
            raise PreflightError("packet.duplicate-id")
        ids.add(item_id)
        field = _bounded_text(
            item["normalized_field"],
            limit=bounds.metadata_chars,
            code="packet.invalid-normalized-field",
        )
        scope = _bounded_text(
            item["scope"], limit=bounds.metadata_chars, code="packet.invalid-scope"
        )
        role = _bounded_text(
            item["authority_role"],
            limit=bounds.metadata_chars,
            code="packet.invalid-authority-role",
        )
        if role not in domain.allowed_roles:
            raise PreflightError("packet.unsupported-authority-role")
        _bounded_text(
            item["source_ref"],
            limit=bounds.metadata_chars,
            code="packet.invalid-source-ref",
        )
        fact_as_of = _timestamp(item["as_of"], "packet.invalid-fact-as-of")
        if fact_as_of > packet_as_of:
            raise PreflightError("packet.future-controlling-fact")
        deadline_value = item.get("freshness_deadline")
        if deadline_value is not None:
            deadline = _timestamp(
                deadline_value, "packet.invalid-freshness-deadline"
            )
            if deadline < fact_as_of:
                raise PreflightError("packet.freshness-before-fact")
        value = _scalar(item["value"], limit=bounds.scalar_chars)
        key = (field, scope)
        prior_type = type_by_field_scope.setdefault(key, _scalar_type(value))
        if prior_type is not _scalar_type(value):
            raise PreflightError("packet.mixed-scalar-types")
    privacy_rules = tuple(sorted(set(policy.privacy_rule_ids(packet))))
    if privacy_rules:
        raise PreflightError(*privacy_rules)
    return packet


def _is_stale(fact: dict[str, Any], packet_as_of: datetime) -> bool:
    deadline = fact.get("freshness_deadline")
    return deadline is not None and packet_as_of > _timestamp(
        deadline, "packet.invalid-freshness-deadline"
    )


def _diagnostic(
    assertion: dict[str, Any],
    code: str,
    facts: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "assertion_id": assertion["id"],
        "code": code,
        "normalized_field": assertion["normalized_field"],
        "scope": assertion["scope"],
        "control_ids": sorted(item["id"] for item in facts),
    }


def compare_packet(packet: Any, policy: Any) -> dict[str, Any]:
    validated = validate_packet(packet, policy)
    domain = policy.domains[validated["authority_domain"]]
    packet_as_of = _timestamp(validated["as_of"], "packet.invalid-as-of")
    facts = validated["controlling_facts"]
    diagnostics: list[dict[str, Any]] = []

    for assertion in sorted(validated["request_assertions"], key=lambda item: item["id"]):
        value_type = _scalar_type(assertion["value"])
        exact = [
            fact
            for fact in facts
            if fact["normalized_field"] == assertion["normalized_field"]
            and fact["scope"] == assertion["scope"]
            and _scalar_type(fact["value"]) is value_type
        ]
        controlling = [
            fact
            for fact in exact
            if fact["authority_role"] in domain.controlling_roles
        ]
        current = [
            fact for fact in controlling if not _is_stale(fact, packet_as_of)
        ]
        if current:
            distinct = {_scalar_identity(fact["value"]) for fact in current}
            if len(distinct) > 1:
                diagnostics.append(
                    _diagnostic(assertion, "controlling-source-conflict", current)
                )
            else:
                code = (
                    "aligned"
                    if _scalar_identity(assertion["value"]) in distinct
                    else "request-control-conflict"
                )
                diagnostics.append(_diagnostic(assertion, code, current))
            continue
        stale = [fact for fact in controlling if _is_stale(fact, packet_as_of)]
        if stale:
            diagnostics.append(_diagnostic(assertion, "control-stale", stale))
            continue
        non_authoritative = [
            fact
            for fact in exact
            if fact["authority_role"] not in domain.controlling_roles
        ]
        if non_authoritative:
            diagnostics.append(
                _diagnostic(
                    assertion, "control-non-authoritative", non_authoritative
                )
            )
            continue
        scope_mismatches = [
            fact
            for fact in facts
            if fact["normalized_field"] == assertion["normalized_field"]
            and fact["scope"] != assertion["scope"]
            and _scalar_type(fact["value"]) is value_type
        ]
        if scope_mismatches:
            diagnostics.append(
                _diagnostic(assertion, "control-scope-mismatch", scope_mismatches)
            )
            continue
        diagnostics.append(_diagnostic(assertion, "control-missing", []))

    diagnostics.sort(
        key=lambda item: (
            item["assertion_id"],
            DIAGNOSTIC_RANK[item["code"]],
            tuple(item["control_ids"]),
        )
    )
    assertion_by_id = {
        item["id"]: item for item in validated["request_assertions"]
    }
    codes = {item["code"] for item in diagnostics}
    unresolved = [
        item for item in diagnostics if item["code"] in UNRESOLVED_CODES
    ]
    non_aligned = codes - {"aligned"}
    consequence = validated["consequence_level"]
    if "controlling-source-conflict" in codes:
        disposition = "hold"
    elif consequence == "high" and non_aligned:
        disposition = "hold"
    elif "request-control-conflict" in codes:
        disposition = "clarify"
    elif "control-stale" in codes:
        disposition = "clarify"
    elif unresolved and any(
        not assertion_by_id[item["assertion_id"]]["provisional"]
        for item in unresolved
    ):
        disposition = "clarify"
    elif unresolved and (
        validated["consequence_level"] != "low"
        or any(item["code"] not in PROVISIONAL_CODES for item in unresolved)
    ):
        disposition = "clarify"
    elif unresolved:
        disposition = "continue-provisional"
    else:
        disposition = "continue"
    if disposition not in DISPOSITIONS:  # pragma: no cover - invariant guard
        raise PreflightError("result.invalid-disposition")
    return {
        "schema_version": SCHEMA_VERSION,
        "request_ref": validated["request_ref"],
        "authority_domain": validated["authority_domain"],
        "disposition": disposition,
        "diagnostics": diagnostics,
        "authority_effect": AUTHORITY_EFFECT,
        "capability_token": CAPABILITY_TOKEN,
        "notice": NO_AUTHORITY_NOTICE,
    }


def render_json(result: dict[str, Any]) -> str:
    import json

    return json.dumps(
        result, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Contradiction Preflight",
        "",
        f"- Request: `{result['request_ref']}`",
        f"- Authority domain: `{result['authority_domain']}`",
        f"- Disposition: `{result['disposition']}`",
        f"- Authority effect: `{result['authority_effect']}`",
        f"- Capability token: `{str(result['capability_token']).lower()}`",
        "",
        f"> {result['notice']}",
        "",
        "## Diagnostics",
        "",
    ]
    for item in result["diagnostics"]:
        controls = ", ".join(f"`{value}`" for value in item["control_ids"]) or "none"
        lines.append(
            f"- `{item['assertion_id']}`: `{item['code']}` "
            f"(field `{item['normalized_field']}`, scope `{item['scope']}`, "
            f"controls {controls})"
        )
    return "\n".join(lines) + "\n"

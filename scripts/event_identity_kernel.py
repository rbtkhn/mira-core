"""Portable, read-only event-identity comparison kernel.

The kernel consumes loaded data plus a host policy. It deliberately imports no
repository, filesystem, database, Git, or Reality-lattice module.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SCHEMA_VERSION = 1
AUTHORITY_EFFECT = "none"
CAPABILITY_TOKEN = False
NO_AUTHORITY_NOTICE = (
    "This result compares event identity but grants no authority, permission, "
    "record merge, assessment, publication, execution, or state transition."
)
DISPOSITIONS = {"continue-distinct", "clarify-ambiguous", "hold-same-event"}
DIAGNOSTIC_RANK = {
    "event-same-candidate": 0,
    "event-ambiguous-time": 1,
    "event-ambiguous-identity": 2,
    "event-ambiguous-anchor": 3,
    "event-distinct": 4,
}
TOP_LEVEL_FIELDS = {"schema_version", "request_ref", "candidate", "comparands"}
EVENT_FIELDS = {
    "id",
    "domain",
    "event_type",
    "actor",
    "action",
    "target",
    "location",
    "time",
    "stable_anchors",
}
TIME_REQUIRED_FIELDS = {
    "raw",
    "value",
    "precision",
    "timezone_basis",
    "source_ref",
}
TIME_FIELDS = TIME_REQUIRED_FIELDS | {"timezone", "end"}
ANCHOR_FIELDS = {"kind", "value", "source_ref"}
IDENTITY_FIELDS = (
    "domain",
    "event_type",
    "actor",
    "action",
    "target",
    "location",
)
PRECISIONS = {"second", "minute", "hour", "day", "interval"}
TIMEZONE_BASES = {
    "explicit-offset",
    "source-declared",
    "reporting-location",
    "unknown",
}
OFFSET_RE = re.compile(r"^(?:Z|[+-](?:0\d|1\d|2[0-3]):[0-5]\d)$")


class EventIdentityError(ValueError):
    """Fail-closed validation error containing only safe error identifiers."""

    def __init__(self, *codes: str):
        normalized = tuple(sorted(set(codes or ("packet.invalid",))))
        super().__init__(", ".join(normalized))
        self.codes = normalized


def _strict_fields(
    value: Any, expected: set[str], required: set[str], code: str
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EventIdentityError(code)
    fields = set(value)
    if fields - expected or not required <= fields:
        raise EventIdentityError("packet.unknown-or-missing-field")
    return value


def _text(value: Any, *, limit: int, code: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise EventIdentityError(code)
    return value.strip()


def _timezone(value: str) -> tzinfo:
    if OFFSET_RE.fullmatch(value):
        if value == "Z":
            return timezone.utc
        sign = 1 if value[0] == "+" else -1
        hours, minutes = (int(part) for part in value[1:].split(":"))
        return timezone(sign * timedelta(hours=hours, minutes=minutes))
    try:
        return ZoneInfo(value)
    except ZoneInfoNotFoundError as error:
        raise EventIdentityError("packet.invalid-timezone") from error


def _date_only(value: str) -> date | None:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise EventIdentityError("packet.invalid-event-time") from error


def _parse_datetime(value: str, supplied_zone: tzinfo | None) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise EventIdentityError("packet.invalid-event-time") from error
    if parsed.tzinfo is None:
        if supplied_zone is None:
            return None
        parsed = parsed.replace(tzinfo=supplied_zone)
    return parsed.astimezone(timezone.utc)


def _normalize_time(item: dict[str, Any]) -> tuple[datetime, datetime] | None:
    timezone_name = item.get("timezone")
    supplied_zone = _timezone(timezone_name) if timezone_name is not None else None
    precision = item["precision"]
    value = item["value"]
    date_value = _date_only(value)

    if precision == "day":
        if date_value is None:
            raise EventIdentityError("packet.invalid-event-time")
        if supplied_zone is None:
            return None
        start_local = datetime.combine(date_value, datetime.min.time(), supplied_zone)
        end_local = datetime.combine(
            date_value + timedelta(days=1), datetime.min.time(), supplied_zone
        )
        return (
            start_local.astimezone(timezone.utc),
            end_local.astimezone(timezone.utc),
        )

    if precision == "interval":
        end_value = item.get("end")
        if end_value is None:
            raise EventIdentityError("packet.interval-end-required")
        start = _parse_datetime(value, supplied_zone)
        end = _parse_datetime(end_value, supplied_zone)
        if start is None or end is None:
            return None
        if end <= start:
            raise EventIdentityError("packet.invalid-event-interval")
        return start, end

    if date_value is not None or item.get("end") is not None:
        raise EventIdentityError("packet.invalid-event-time")
    start = _parse_datetime(value, supplied_zone)
    if start is None:
        return None
    duration = {
        "second": timedelta(seconds=1),
        "minute": timedelta(minutes=1),
        "hour": timedelta(hours=1),
    }[precision]
    return start, start + duration


def _validate_time(value: Any, bounds: Any) -> dict[str, Any]:
    item = _strict_fields(
        value, TIME_FIELDS, TIME_REQUIRED_FIELDS, "packet.invalid-event-time"
    )
    _text(item["raw"], limit=bounds.scalar_chars, code="packet.invalid-raw-time")
    _text(item["value"], limit=bounds.metadata_chars, code="packet.invalid-event-time")
    _text(
        item["source_ref"],
        limit=bounds.metadata_chars,
        code="packet.invalid-source-ref",
    )
    if item["precision"] not in PRECISIONS:
        raise EventIdentityError("packet.invalid-time-precision")
    if item["timezone_basis"] not in TIMEZONE_BASES:
        raise EventIdentityError("packet.invalid-timezone-basis")
    if "timezone" in item:
        _text(
            item["timezone"],
            limit=bounds.metadata_chars,
            code="packet.invalid-timezone",
        )
    if "end" in item:
        _text(
            item["end"],
            limit=bounds.metadata_chars,
            code="packet.invalid-event-time",
        )
    if item["timezone_basis"] == "unknown" and "timezone" in item:
        raise EventIdentityError("packet.invalid-timezone-basis")
    _normalize_time(item)
    return item


def _validate_event(value: Any, policy: Any, seen: set[str]) -> dict[str, Any]:
    item = _strict_fields(value, EVENT_FIELDS, EVENT_FIELDS, "packet.invalid-event")
    bounds = policy.bounds
    for field in ("id", *IDENTITY_FIELDS):
        _text(
            item[field],
            limit=bounds.metadata_chars,
            code=f"packet.invalid-{field.replace('_', '-')}",
        )
    if item["id"] in seen:
        raise EventIdentityError("packet.duplicate-id")
    seen.add(item["id"])
    if item["domain"] not in policy.domains:
        raise EventIdentityError("packet.unsupported-domain")
    _validate_time(item["time"], bounds)
    anchors = item["stable_anchors"]
    if not isinstance(anchors, list):
        raise EventIdentityError("packet.invalid-stable-anchors")
    if len(anchors) > bounds.max_anchors:
        raise EventIdentityError("packet.too-many-anchors")
    anchor_keys: set[tuple[str, str]] = set()
    for anchor in anchors:
        _strict_fields(anchor, ANCHOR_FIELDS, ANCHOR_FIELDS, "packet.invalid-anchor")
        kind = _text(
            anchor["kind"],
            limit=bounds.metadata_chars,
            code="packet.invalid-anchor-kind",
        )
        anchor_value = _text(
            anchor["value"],
            limit=bounds.scalar_chars,
            code="packet.invalid-anchor-value",
        )
        _text(
            anchor["source_ref"],
            limit=bounds.metadata_chars,
            code="packet.invalid-source-ref",
        )
        key = (kind, anchor_value)
        if key in anchor_keys:
            raise EventIdentityError("packet.duplicate-anchor")
        anchor_keys.add(key)
    return item


def validate_packet(packet: Any, policy: Any) -> dict[str, Any]:
    privacy_rules = tuple(sorted(set(policy.privacy_rule_ids(packet))))
    if privacy_rules:
        raise EventIdentityError(*privacy_rules)
    packet = _strict_fields(
        packet, TOP_LEVEL_FIELDS, TOP_LEVEL_FIELDS, "packet.not-object"
    )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise EventIdentityError("packet.unsupported-schema")
    _text(
        packet["request_ref"],
        limit=policy.bounds.metadata_chars,
        code="packet.invalid-request-ref",
    )
    comparands = packet["comparands"]
    if not isinstance(comparands, list) or not comparands:
        raise EventIdentityError("packet.comparands-required")
    if len(comparands) > policy.bounds.max_comparands:
        raise EventIdentityError("packet.too-many-comparands")
    seen: set[str] = set()
    _validate_event(packet["candidate"], policy, seen)
    for comparand in comparands:
        _validate_event(comparand, policy, seen)
    return packet


def _gap_seconds(
    left: tuple[datetime, datetime], right: tuple[datetime, datetime]
) -> float:
    if left[1] <= right[0]:
        return (right[0] - left[1]).total_seconds()
    if right[1] <= left[0]:
        return (left[0] - right[1]).total_seconds()
    return 0.0


def _diagnostic(candidate: dict[str, Any], comparand: dict[str, Any], policy: Any) -> dict[str, Any]:
    matched_fields = sorted(
        field for field in IDENTITY_FIELDS if candidate[field] == comparand[field]
    )
    candidate_time = _normalize_time(candidate["time"])
    comparand_time = _normalize_time(comparand["time"])
    if candidate_time is None or comparand_time is None:
        code = "event-ambiguous-time"
        time_relation = "unresolved"
    else:
        gap = _gap_seconds(candidate_time, comparand_time)
        if gap > policy.domains[candidate["domain"]].near_tolerance_seconds:
            code = "event-distinct"
            time_relation = "disjoint"
        elif gap > 0:
            code = "event-ambiguous-time"
            time_relation = "near"
        elif len(matched_fields) != len(IDENTITY_FIELDS):
            code = "event-ambiguous-identity"
            time_relation = "overlap"
        else:
            left_anchors = {
                (item["kind"], item["value"])
                for item in candidate["stable_anchors"]
            }
            right_anchors = {
                (item["kind"], item["value"])
                for item in comparand["stable_anchors"]
            }
            if left_anchors & right_anchors:
                code = "event-same-candidate"
            else:
                code = "event-ambiguous-anchor"
            time_relation = "overlap"
    return {
        "candidate_id": candidate["id"],
        "comparand_id": comparand["id"],
        "diagnostic": code,
        "time_relation": time_relation,
        "matched_fields": matched_fields,
    }


def compare_packet(packet: Any, policy: Any) -> dict[str, Any]:
    packet = validate_packet(packet, policy)
    candidate = packet["candidate"]
    diagnostics = [
        _diagnostic(candidate, comparand, policy)
        for comparand in packet["comparands"]
    ]
    diagnostics.sort(
        key=lambda item: (
            item["comparand_id"],
            DIAGNOSTIC_RANK[item["diagnostic"]],
        )
    )
    codes = {item["diagnostic"] for item in diagnostics}
    if "event-same-candidate" in codes:
        disposition = "hold-same-event"
    elif codes - {"event-distinct"}:
        disposition = "clarify-ambiguous"
    else:
        disposition = "continue-distinct"
    return {
        "schema_version": SCHEMA_VERSION,
        "request_ref": packet["request_ref"],
        "disposition": disposition,
        "diagnostics": diagnostics,
        "authority_effect": AUTHORITY_EFFECT,
        "capability_token": CAPABILITY_TOKEN,
        "notice": NO_AUTHORITY_NOTICE,
    }


def render_json(result: dict[str, Any]) -> str:
    return json.dumps(
        result, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Event Identity Preflight",
        "",
        f"- Request: `{result['request_ref']}`",
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
        matched = ", ".join(f"`{field}`" for field in item["matched_fields"]) or "none"
        lines.append(
            f"- `{item['candidate_id']}` vs `{item['comparand_id']}`: "
            f"`{item['diagnostic']}` (time `{item['time_relation']}`, "
            f"matched fields {matched})"
        )
    return "\n".join(lines) + "\n"

"""Validate optional turn-level participation edges."""

from __future__ import annotations

from typing import Any

ALLOWED_EDGE_STATUS = {"labeled", "inferred", "provisional"}
STRONG_ATTRIBUTION = {"strong", "speaker-labeled"}


def validate_edges(edges: list[dict[str, Any]], source_rows: dict[str, dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    for index, edge in enumerate(edges):
        prefix = f"edge[{index}]"
        source = str(edge.get("source") or "")
        person = str(edge.get("person") or "")
        role = str(edge.get("role") or "")
        turns = edge.get("turns")
        status = str(edge.get("attribution_status") or "")
        row = source_rows.get(source)
        if not row:
            failures.append(f"{prefix}: source is not manifest-backed")
            continue
        roles = row.get("voice_roles") or {}
        if person not in roles:
            failures.append(f"{prefix}: person is not a routed voice for source")
        elif role not in (roles.get(person) or []):
            failures.append(f"{prefix}: edge role does not match source role map")
        if not isinstance(turns, list) or not turns or not all(isinstance(turn, int) and turn >= 0 for turn in turns):
            failures.append(f"{prefix}: turns must be a non-empty list of non-negative integers")
        if status not in ALLOWED_EDGE_STATUS:
            failures.append(f"{prefix}: invalid attribution_status")
        if edge.get("quote_attribution") in STRONG_ATTRIBUTION and status != "labeled":
            failures.append(f"{prefix}: strong quotation attribution requires labeled turns")
        if edge.get("quote_attribution") in STRONG_ATTRIBUTION and role in {"host", "co-host"} and edge.get("quoted_person") and edge.get("quoted_person") != person:
            failures.append(f"{prefix}: host framing cannot inherit guest quotation attribution")
    return failures


"""Pure, fail-closed validation for operator-approval evidence.

The kernel validates loaded values only.  It performs no I/O, resolves no
authority records, mutates no governed object, and grants no authority.  Host
consumers remain responsible for resolving trusted authority evidence before
calling :func:`verify_approval` and for applying their own domain invariants.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Any, Mapping


SCHEMA_VERSION = 1
AUTHORITY_EFFECT = "none"
CAPABILITY_TOKEN = False
NO_AUTHORITY_NOTICE = (
    "This result validates approval evidence but grants no authority, permission, "
    "mutation, execution, publication, or state transition."
)

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UNSAFE_METADATA_CATEGORIES = {"Cc", "Cf", "Zl", "Zp"}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "request_ref",
    "domain",
    "action",
    "subject_ref",
    "subject_sha256",
    "actor",
    "approved_at",
    "authority_kind",
    "authority_ref",
    "approval_record",
}
RECORD_FIELDS = {"record_ref", "role", "timestamp", "text"}


class ApprovalError(ValueError):
    """Fail-closed error containing stable, non-sensitive rule identifiers."""

    def __init__(self, *codes: str):
        normalized = tuple(sorted(set(codes or ("approval.invalid",))))
        super().__init__(", ".join(normalized))
        self.codes = normalized


@dataclass(frozen=True)
class ApprovalBounds:
    metadata_chars: int = 256
    statement_chars: int = 4096
    future_skew_seconds: int = 300

    def __post_init__(self) -> None:
        if self.metadata_chars < 1 or self.statement_chars < 1:
            raise ValueError("approval bounds must be positive")
        if self.future_skew_seconds < 0:
            raise ValueError("future skew cannot be negative")


@dataclass(frozen=True)
class ActionRule:
    domain: str
    authority_kind: str = "direct-command"
    actor: str = "operator"
    exact_statement_required: bool = False

    def __post_init__(self) -> None:
        if not self.domain.strip() or not self.actor.strip():
            raise ValueError("action rules require a domain and actor")
        if self.authority_kind not in {"direct-command", "operator-record"}:
            raise ValueError("unsupported authority kind")
        if self.exact_statement_required and self.authority_kind != "operator-record":
            raise ValueError("exact statements require operator-record authority")
        if self.authority_kind == "operator-record" and not self.exact_statement_required:
            raise ValueError("operator-record authority requires an exact statement")


class ApprovalPolicy:
    """Immutable action registry plus validation bounds."""

    def __init__(
        self,
        actions: Mapping[str, ActionRule],
        *,
        bounds: ApprovalBounds | None = None,
    ) -> None:
        if not actions:
            raise ValueError("approval policy requires at least one action")
        copied: dict[str, ActionRule] = {}
        for name, rule in actions.items():
            if not isinstance(name, str) or not name.strip() or name != name.strip():
                raise ValueError("approval action names must be normalized")
            if not isinstance(rule, ActionRule):
                raise TypeError("approval action rules must be ActionRule values")
            copied[name] = rule
        self.actions = MappingProxyType(copied)
        self.bounds = bounds or ApprovalBounds()


DEFAULT_ACTIONS = MappingProxyType(
    {
        "promote-identity-proposition": ActionRule("mira-identity"),
        "approve-position": ActionRule("operator-position"),
        "approve-journal-entry": ActionRule("operator-position"),
        "approve-comparator-set": ActionRule("operator-position"),
        "approve-comparison": ActionRule("operator-position"),
        "approve-review": ActionRule("operator-position"),
        "sign-assessment": ActionRule("reality"),
        "approve-language-waiver": ActionRule("reality"),
    }
)
DEFAULT_POLICY = ApprovalPolicy(DEFAULT_ACTIONS)


def _strict_object(
    value: Any,
    fields: set[str],
    code: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ApprovalError(code)
    if set(value) != fields:
        raise ApprovalError("approval.unknown-or-missing-field")
    return value


def _text(value: Any, *, limit: int, code: str) -> str:
    if not isinstance(value, str):
        raise ApprovalError(code)
    if not value or value != value.strip() or len(value) > limit:
        raise ApprovalError(code)
    if any(
        character == "`"
        or unicodedata.category(character) in UNSAFE_METADATA_CATEGORIES
        for character in value
    ):
        raise ApprovalError("approval.unsafe-metadata")
    return value


def _timestamp(value: Any, code: str) -> datetime:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ApprovalError(code)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ApprovalError(code) from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ApprovalError(code)
    return parsed.astimezone(timezone.utc)


def _now(value: datetime | None) -> datetime:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    return current.astimezone(timezone.utc)


def _sha256(value: Any, code: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise ApprovalError(code)
    return value


def _record(
    value: Any,
    *,
    bounds: ApprovalBounds,
    expected_statement: str | None,
    approved_at: datetime,
    latest_allowed: datetime,
) -> dict[str, Any]:
    record = _strict_object(value, RECORD_FIELDS, "approval.record-not-object")
    _text(
        record["record_ref"],
        limit=bounds.metadata_chars,
        code="approval.invalid-record-ref",
    )
    if record["role"] != "user":
        raise ApprovalError("approval.record-not-user")
    timestamp = _timestamp(record["timestamp"], "approval.invalid-record-timestamp")
    if timestamp > latest_allowed:
        raise ApprovalError("approval.record-in-future")
    if timestamp > approved_at:
        raise ApprovalError("approval.precedes-record")
    text = record["text"]
    if not isinstance(text, str) or not text.strip() or len(text) > bounds.statement_chars:
        raise ApprovalError("approval.invalid-record-text")
    if expected_statement is None:
        raise ApprovalError("approval.expected-statement-required")
    if not isinstance(expected_statement, str) or not expected_statement.strip():
        raise ApprovalError("approval.invalid-expected-statement")
    if len(expected_statement) > bounds.statement_chars:
        raise ApprovalError("approval.invalid-expected-statement")
    if not hmac.compare_digest(text.strip(), expected_statement.strip()):
        raise ApprovalError("approval.statement-mismatch")
    return record


def validate_packet(
    packet: Any,
    *,
    expected_subject_sha256: str,
    policy: ApprovalPolicy = DEFAULT_POLICY,
    expected_statement: str | None = None,
    now: datetime | None = None,
) -> tuple[dict[str, Any], ActionRule]:
    """Validate an approval packet against trusted caller expectations."""

    packet = _strict_object(packet, TOP_LEVEL_FIELDS, "approval.not-object")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ApprovalError("approval.unsupported-schema")
    bounds = policy.bounds
    for field in ("request_ref", "domain", "action", "subject_ref", "actor", "authority_ref"):
        _text(
            packet[field],
            limit=bounds.metadata_chars,
            code=f"approval.invalid-{field.replace('_', '-')}",
        )
    action = packet["action"]
    rule = policy.actions.get(action)
    if rule is None:
        raise ApprovalError("approval.unsupported-action")
    if packet["domain"] != rule.domain:
        raise ApprovalError("approval.domain-action-mismatch")
    if packet["actor"] != rule.actor:
        raise ApprovalError("approval.actor-not-authorized")
    if packet["authority_kind"] != rule.authority_kind:
        raise ApprovalError("approval.authority-kind-mismatch")

    observed_digest = _sha256(
        packet["subject_sha256"], "approval.invalid-subject-sha256"
    )
    expected_digest = _sha256(
        expected_subject_sha256, "approval.invalid-expected-subject-sha256"
    )
    if not hmac.compare_digest(observed_digest, expected_digest):
        raise ApprovalError("approval.subject-digest-mismatch")

    current = _now(now)
    latest_allowed = current + timedelta(seconds=bounds.future_skew_seconds)
    approved_at = _timestamp(packet["approved_at"], "approval.invalid-approved-at")
    if approved_at > latest_allowed:
        raise ApprovalError("approval.approved-at-in-future")

    record = packet["approval_record"]
    if rule.authority_kind == "direct-command":
        if record is not None:
            raise ApprovalError("approval.record-forbidden")
        if expected_statement is not None:
            raise ApprovalError("approval.statement-forbidden")
    else:
        _record(
            record,
            bounds=bounds,
            expected_statement=expected_statement,
            approved_at=approved_at,
            latest_allowed=latest_allowed,
        )
    return packet, rule


def verify_approval(
    packet: Any,
    *,
    expected_subject_sha256: str,
    policy: ApprovalPolicy = DEFAULT_POLICY,
    expected_statement: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic validation receipt with no authority effect."""

    validated, rule = validate_packet(
        packet,
        expected_subject_sha256=expected_subject_sha256,
        policy=policy,
        expected_statement=expected_statement,
        now=now,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "valid",
        "request_ref": validated["request_ref"],
        "domain": rule.domain,
        "action": validated["action"],
        "subject_ref": validated["subject_ref"],
        "subject_sha256": validated["subject_sha256"],
        "actor": validated["actor"],
        "approved_at": validated["approved_at"],
        "authority_kind": rule.authority_kind,
        "authority_ref": validated["authority_ref"],
        "authority_effect": AUTHORITY_EFFECT,
        "capability_token": CAPABILITY_TOKEN,
        "notice": NO_AUTHORITY_NOTICE,
    }


def invalid_result(error: ApprovalError) -> dict[str, Any]:
    """Convert a fail-closed exception into a safe deterministic result."""

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "invalid",
        "errors": [{"code": code} for code in error.codes],
        "authority_effect": AUTHORITY_EFFECT,
        "capability_token": CAPABILITY_TOKEN,
        "notice": NO_AUTHORITY_NOTICE,
    }


def render_json(result: Mapping[str, Any]) -> str:
    return json.dumps(
        result, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )


def canonical_sha256(value: Any) -> str:
    """Digest a JSON-compatible governed subject deterministically."""

    def reject_non_finite(item: Any) -> None:
        if isinstance(item, float) and not math.isfinite(item):
            raise ApprovalError("approval.subject-not-canonical-json")
        if isinstance(item, list):
            for child in item:
                reject_non_finite(child)
        elif isinstance(item, dict):
            if not all(isinstance(key, str) for key in item):
                raise ApprovalError("approval.subject-not-canonical-json")
            for child in item.values():
                reject_non_finite(child)

    reject_non_finite(value)
    try:
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ApprovalError("approval.subject-not-canonical-json") from error
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()

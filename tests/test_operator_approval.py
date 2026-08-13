from __future__ import annotations

import json
import math
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import operator_approval as subject


NOW = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)
GOVERNED_VALUE = {"id": "OBJ-1", "value": "bounded"}
DIGEST = subject.canonical_sha256(GOVERNED_VALUE)


def packet(
    action: str = "approve-position",
    *,
    domain: str | None = None,
) -> dict:
    rule = subject.DEFAULT_POLICY.actions[action]
    return {
        "schema_version": 1,
        "request_ref": "REQ-1",
        "domain": domain or rule.domain,
        "action": action,
        "subject_ref": "OBJ-1",
        "subject_sha256": DIGEST,
        "actor": "operator",
        "approved_at": "2026-08-10T11:59:00Z",
        "authority_kind": rule.authority_kind,
        "authority_ref": "current-operator-command",
        "approval_record": None,
    }


def assert_code(value: dict, code: str, **kwargs) -> None:
    with pytest.raises(subject.ApprovalError) as captured:
        subject.verify_approval(
            value,
            expected_subject_sha256=DIGEST,
            now=NOW,
            **kwargs,
        )
    assert captured.value.codes == (code,)


def test_default_policy_covers_the_eight_first_slice_actions() -> None:
    assert {
        name: rule.domain for name, rule in subject.DEFAULT_POLICY.actions.items()
    } == {
        "promote-identity-proposition": "mira-identity",
        "approve-position": "operator-position",
        "approve-journal-entry": "operator-position",
        "approve-comparator-set": "operator-position",
        "approve-comparison": "operator-position",
        "approve-review": "operator-position",
        "sign-assessment": "reality",
        "approve-language-waiver": "reality",
    }


@pytest.mark.parametrize("action", sorted(subject.DEFAULT_POLICY.actions))
def test_every_first_slice_action_conforms_to_the_shared_contract(action: str) -> None:
    value = packet(action)
    result = subject.verify_approval(
        value,
        expected_subject_sha256=DIGEST,
        now=NOW,
    )
    assert result["status"] == "valid"
    assert result["action"] == action
    assert result["domain"] == subject.DEFAULT_POLICY.actions[action].domain
    assert result["authority_effect"] == "none"
    assert result["capability_token"] is False
    assert "grants no authority" in result["notice"]


def test_result_is_deterministic_and_contains_no_approval_record_text() -> None:
    result = subject.verify_approval(
        packet(), expected_subject_sha256=DIGEST, now=NOW
    )
    assert subject.render_json(result) == subject.render_json(result)
    assert "approval_record" not in result
    assert "current-operator-command" in subject.render_json(result)


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ({"actor": "agent"}, "approval.actor-not-authorized"),
        ({"domain": "reality"}, "approval.domain-action-mismatch"),
        ({"authority_kind": "operator-record"}, "approval.authority-kind-mismatch"),
        ({"subject_sha256": "A" * 64}, "approval.invalid-subject-sha256"),
        ({"subject_sha256": "0" * 64}, "approval.subject-digest-mismatch"),
        ({"approved_at": "not-a-time"}, "approval.invalid-approved-at"),
        ({"approved_at": "2026-08-10T12:06:00Z"}, "approval.approved-at-in-future"),
        ({"approval_record": {}}, "approval.record-forbidden"),
    ],
)
def test_shared_fail_closed_rules(mutation: dict, code: str) -> None:
    value = packet()
    value.update(mutation)
    assert_code(value, code)


@pytest.mark.parametrize(
    ("field", "replacement", "code"),
    [
        ("request_ref", "", "approval.invalid-request-ref"),
        ("request_ref", " padded ", "approval.invalid-request-ref"),
        ("request_ref", "unsafe`value", "approval.unsafe-metadata"),
        ("subject_ref", None, "approval.invalid-subject-ref"),
        ("authority_ref", "", "approval.invalid-authority-ref"),
        ("actor", "", "approval.invalid-actor"),
    ],
)
def test_metadata_is_bounded_and_normalized(
    field: str, replacement: object, code: str
) -> None:
    value = packet()
    value[field] = replacement
    assert_code(value, code)


def test_packet_schema_is_strict() -> None:
    missing = packet()
    missing.pop("authority_ref")
    assert_code(missing, "approval.unknown-or-missing-field")
    extra = packet()
    extra["permission"] = True
    assert_code(extra, "approval.unknown-or-missing-field")
    assert_code([], "approval.not-object")


def test_schema_and_action_are_fail_closed() -> None:
    wrong_schema = packet()
    wrong_schema["schema_version"] = 2
    assert_code(wrong_schema, "approval.unsupported-schema")
    unknown = packet()
    unknown["action"] = "publish-everything"
    assert_code(unknown, "approval.unsupported-action")


def test_statement_is_forbidden_for_direct_command_actions() -> None:
    assert_code(
        packet(),
        "approval.statement-forbidden",
        expected_statement="Approve OBJ-1.",
    )


def record_policy() -> subject.ApprovalPolicy:
    return subject.ApprovalPolicy(
        {
            "admit-learning": subject.ActionRule(
                "recursive-learning",
                authority_kind="operator-record",
                exact_statement_required=True,
            )
        }
    )


def record_packet() -> dict:
    value = packet()
    value.update(
        {
            "domain": "recursive-learning",
            "action": "admit-learning",
            "authority_kind": "operator-record",
            "authority_ref": "MS-00000000-0000-0000-0000-000000000001",
            "approved_at": "2026-08-10T11:59:30Z",
            "approval_record": {
                "record_ref": "MR-000000000000000000000001",
                "role": "user",
                "timestamp": "2026-08-10T11:59:00Z",
                "text": "Approve OBJ-1 with digest " + DIGEST + ".",
            },
        }
    )
    return value


def verify_record(value: dict, statement: str | None = None) -> dict:
    return subject.verify_approval(
        value,
        expected_subject_sha256=DIGEST,
        expected_statement=statement or "Approve OBJ-1 with digest " + DIGEST + ".",
        policy=record_policy(),
        now=NOW,
    )


def test_exact_record_mode_validates_resolved_user_evidence() -> None:
    result = verify_record(record_packet())
    assert result["status"] == "valid"
    assert result["authority_kind"] == "operator-record"
    assert "approval_record" not in result


@pytest.mark.parametrize(
    ("field", "replacement", "code"),
    [
        ("role", "assistant", "approval.record-not-user"),
        ("timestamp", "invalid", "approval.invalid-record-timestamp"),
        ("timestamp", "2026-08-10T12:06:00Z", "approval.record-in-future"),
        ("timestamp", "2026-08-10T12:00:00Z", "approval.precedes-record"),
        ("record_ref", "", "approval.invalid-record-ref"),
        ("text", "", "approval.invalid-record-text"),
    ],
)
def test_record_mode_fails_closed(field: str, replacement: object, code: str) -> None:
    value = record_packet()
    value["approval_record"][field] = replacement
    with pytest.raises(subject.ApprovalError) as captured:
        verify_record(value)
    assert captured.value.codes == (code,)


def test_record_mode_rejects_non_exact_statement() -> None:
    with pytest.raises(subject.ApprovalError) as captured:
        verify_record(record_packet(), "Approve something else.")
    assert captured.value.codes == ("approval.statement-mismatch",)


def test_record_mode_requires_a_record_and_expected_statement() -> None:
    value = record_packet()
    value["approval_record"] = None
    with pytest.raises(subject.ApprovalError) as captured:
        verify_record(value)
    assert captured.value.codes == ("approval.record-not-object",)

    with pytest.raises(subject.ApprovalError) as captured:
        subject.verify_approval(
            record_packet(),
            expected_subject_sha256=DIGEST,
            policy=record_policy(),
            now=NOW,
        )
    assert captured.value.codes == ("approval.expected-statement-required",)


def test_record_schema_is_strict() -> None:
    value = record_packet()
    value["approval_record"]["hidden_authority"] = True
    with pytest.raises(subject.ApprovalError) as captured:
        verify_record(value)
    assert captured.value.codes == ("approval.unknown-or-missing-field",)


def test_invalid_result_is_safe_and_non_authorizing() -> None:
    error = subject.ApprovalError("approval.z", "approval.a", "approval.z")
    result = subject.invalid_result(error)
    assert result == {
        "schema_version": 1,
        "status": "invalid",
        "errors": [{"code": "approval.a"}, {"code": "approval.z"}],
        "authority_effect": "none",
        "capability_token": False,
        "notice": subject.NO_AUTHORITY_NOTICE,
    }


def test_canonical_digest_is_stable_across_key_order() -> None:
    assert subject.canonical_sha256({"b": 2, "a": 1}) == subject.canonical_sha256(
        {"a": 1, "b": 2}
    )
    assert subject.canonical_sha256({"value": "é"}) == subject.canonical_sha256(
        json.loads('{"value":"\\u00e9"}')
    )


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, {1: "bad"}, {"x": object()}])
def test_canonical_digest_rejects_non_json_or_non_finite_values(value: object) -> None:
    with pytest.raises(subject.ApprovalError) as captured:
        subject.canonical_sha256(value)
    assert captured.value.codes == ("approval.subject-not-canonical-json",)


def test_policy_and_action_registry_are_immutable() -> None:
    with pytest.raises(TypeError):
        subject.DEFAULT_POLICY.actions["new-action"] = subject.ActionRule("other")
    with pytest.raises(TypeError):
        subject.DEFAULT_ACTIONS["new-action"] = subject.ActionRule("other")


def test_policy_rejects_invalid_configuration() -> None:
    with pytest.raises(ValueError, match="at least one action"):
        subject.ApprovalPolicy({})
    with pytest.raises(ValueError, match="unsupported authority kind"):
        subject.ActionRule("domain", authority_kind="magic")
    with pytest.raises(ValueError, match="exact statements"):
        subject.ActionRule("domain", exact_statement_required=True)
    with pytest.raises(ValueError, match="requires an exact statement"):
        subject.ActionRule("domain", authority_kind="operator-record")
    with pytest.raises(ValueError, match="normalized"):
        subject.ApprovalPolicy({" bad ": subject.ActionRule("domain")})


def test_caller_now_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        subject.verify_approval(
            packet(),
            expected_subject_sha256=DIGEST,
            now=datetime(2026, 8, 10, 12, 0),
        )


def test_default_packet_input_is_not_mutated() -> None:
    value = packet()
    before = deepcopy(value)
    subject.verify_approval(value, expected_subject_sha256=DIGEST, now=NOW)
    assert value == before

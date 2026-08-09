from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import research_handoff


def packet(workflow: str = "external-research") -> dict:
    return {
        "schema": "research-execution-handoff-v1",
        "decision_and_use": "Decide whether to commission a bounded investigation.",
        "focal_question": "What evidence would resolve the disputed mechanism?",
        "scope": {
            "actors": ["actor-a"],
            "geography": ["region-a"],
            "time_window": "2026-07-01/2026-07-31",
            "observation_cutoff": "2026-08-01T00:00:00Z",
            "coverage": "bounded",
            "output_form": "source-linked-findings",
        },
        "research_contract": {
            "research_questions": ["Question one?", "Question two?", "Question three?"],
            "evidence_plan": "Recover primary sources and independent lineage roots.",
            "rival_explanations": ["A competing mechanism explains the observation."],
            "contradiction_protocol": "Preserve conflicting observations and attribution.",
            "finding_format": "Link, proposition, status, lineage, confidence, relevance.",
            "stop_condition": "Stop when every question is supported, challenged, or unresolved.",
        },
        "destination": {
            "workflow": workflow,
            "reason": "The requested work requires bounded external investigation.",
            "compatibility": "ready",
            "reasons": ["no repository execution workflow fits; route to bounded external research"],
        },
        "prerequisites": {
            "canonical_claim_id": None,
            "world_monitor_objective": None,
            "supplied_source_body": False,
            "manifest_backed_date": False,
            "explicit_execution_request": False,
        },
        "authority": {
            "execute": False,
            "mutate": False,
            "publish": False,
            "communicate": False,
        },
        "disposition": "ready",
    }


def seed(producer: str = "world-monitor") -> dict:
    return {
        "schema": "research-brief-seed-v1",
        "producer": {
            "workflow": producer,
            "item_id": "candidate-001",
            "source_refs": ["https://example.com/upstream"],
        },
        "decision_context": "Decide whether this candidate warrants bounded research.",
        "candidate_question": "What evidence would discriminate among the candidate explanations?",
        "scope_hints": {
            "actors": ["actor-a"],
            "geography": ["region-a"],
            "time_window": "2026-08-01/2026-08-02",
            "languages": ["en"],
        },
        "known_context": ["An upstream source has been recovered."],
        "unresolved_gaps": ["Independent lineage remains unresolved."],
        "rival_hints": ["The signal is material.", "The signal is reporting noise."],
        "routing_hint": {
            "workflow": "external-research",
            "reason": "The candidate needs bounded investigation.",
        },
        "identifiers": {
            "canonical_claim_id": None,
            "forecast_ids": [],
            "reality_ids": [],
            "source_ids": [],
        },
        "authority": {
            "execute": False,
            "mutate": False,
            "publish": False,
            "communicate": False,
        },
    }


def set_classification(value: dict, disposition: str, reasons: list[str]) -> dict:
    value["destination"]["compatibility"] = disposition
    value["destination"]["reasons"] = reasons
    value["disposition"] = disposition
    return value


def test_external_research_is_valid_and_non_authorizing() -> None:
    result = research_handoff.validate_packet(packet())

    assert result["valid"] is True
    assert result["disposition"] == "ready"
    assert result["authority_effect"] == "none"
    assert result["execution_triggered"] is False
    assert not any(result["authority"].values())


def test_morning_brief_scope_is_not_silently_normalized() -> None:
    value = packet("morning-brief")
    reasons = [
        "coverage must be global",
        "time_window must be trailing-24-hours",
        "output_form must be five-minute-brief",
    ]
    set_classification(value, "needs-scope-normalization", reasons)

    result = research_handoff.validate_packet(value)

    assert result["disposition"] == "needs-scope-normalization"
    assert result["reasons"] == reasons


def test_morning_brief_accepts_only_its_fixed_contract() -> None:
    value = packet("morning-brief")
    value["scope"].update(
        coverage="global",
        time_window="trailing-24-hours",
        output_form="five-minute-brief",
    )
    set_classification(value, "ready", ["scope matches the fixed Morning Brief contract"])

    assert research_handoff.validate_packet(value)["disposition"] == "ready"


def test_reality_check_requires_an_existing_canonical_claim(tmp_path: Path) -> None:
    value = packet("reality-check")
    reason = "an exact canonical claim identifier is required"
    set_classification(value, "needs-claim-resolution", [reason])
    assert research_handoff.validate_packet(value, claims_root=tmp_path)["reasons"] == [reason]

    value["prerequisites"]["canonical_claim_id"] = "CLM-20260801-001"
    missing = "canonical claim is not present in the lattice: CLM-20260801-001"
    set_classification(value, "needs-claim-resolution", [missing])
    assert research_handoff.validate_packet(value, claims_root=tmp_path)["reasons"] == [missing]

    (tmp_path / "claim.json").write_text(
        json.dumps({"id": "CLM-20260801-001"}), encoding="utf-8"
    )
    set_classification(
        value,
        "ready",
        ["canonical claim exists in the lattice: CLM-20260801-001"],
    )
    assert research_handoff.validate_packet(value, claims_root=tmp_path)["disposition"] == "ready"


@pytest.mark.parametrize(
    ("workflow", "invalid_reason"),
    [
        ("world-monitor", "world_monitor_objective must be current-signal-discovery or coverage-gap"),
        ("intake", "intake requires a supplied source body"),
        ("geopolitical-synthesis", "geopolitical synthesis requires a manifest-backed archive day"),
    ],
)
def test_repository_destinations_fail_closed(workflow: str, invalid_reason: str) -> None:
    value = packet(workflow)
    set_classification(value, "incompatible", [invalid_reason])

    assert research_handoff.validate_packet(value)["disposition"] == "incompatible"


@pytest.mark.parametrize(
    ("workflow", "prerequisite", "ready_value", "ready_reason"),
    [
        (
            "world-monitor",
            "world_monitor_objective",
            "current-signal-discovery",
            "World Monitor supports current-signal-discovery",
        ),
        (
            "intake",
            "supplied_source_body",
            True,
            "a supplied source body is available for intake",
        ),
        (
            "geopolitical-synthesis",
            "manifest_backed_date",
            True,
            "a manifest-backed archive day is available",
        ),
    ],
)
def test_repository_destinations_accept_only_their_prerequisites(
    workflow: str, prerequisite: str, ready_value: object, ready_reason: str
) -> None:
    value = packet(workflow)
    value["prerequisites"][prerequisite] = ready_value
    set_classification(value, "ready", [ready_reason])

    assert research_handoff.validate_packet(value)["disposition"] == "ready"


def test_authority_or_execution_request_is_rejected() -> None:
    authorized = packet()
    authorized["authority"]["execute"] = True
    with pytest.raises(ValueError, match="authority must deny"):
        research_handoff.validate_packet(authorized)

    execution = packet()
    execution["prerequisites"]["explicit_execution_request"] = True
    with pytest.raises(ValueError, match="explicit_execution_request must be false"):
        research_handoff.validate_packet(execution)


def test_claimed_disposition_must_match_computed_result() -> None:
    value = deepcopy(packet("morning-brief"))
    with pytest.raises(ValueError, match="destination.compatibility must be needs-scope-normalization"):
        research_handoff.validate_packet(value)


def test_cli_emits_a_read_only_projection(tmp_path: Path, capsys) -> None:
    path = tmp_path / "handoff.json"
    path.write_text(json.dumps(packet()), encoding="utf-8")

    assert research_handoff.main(["--packet", str(path), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)

    assert result["workflow"] == "external-research"
    assert result["authority_effect"] == "none"
    assert result["execution_triggered"] is False


@pytest.mark.parametrize(
    "producer", ["reality-handoff", "world-monitor", "continuity-triage"]
)
def test_seed_validation_accepts_each_supported_producer(producer: str) -> None:
    value = seed(producer)

    result = research_handoff.validate_seed(value)

    assert result["valid"] is True
    assert result["producer"] == producer
    assert result["authority_effect"] == "none"
    assert result["execution_triggered"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("compatibility", "ready"),
        ("disposition", "ready"),
        ("research_contract", {"research_questions": []}),
        ("explicit_execution_request", False),
        ("execution_intent", "browse"),
    ],
)
def test_seed_rejects_fields_owned_by_the_completed_brief(field: str, value: object) -> None:
    candidate = seed()
    candidate[field] = value

    with pytest.raises(ValueError, match="seed contains forbidden fields"):
        research_handoff.validate_seed(candidate)


def test_seed_rejects_authority_and_unbounded_text() -> None:
    authorized = seed()
    authorized["authority"]["execute"] = True
    with pytest.raises(ValueError, match="authority must deny"):
        research_handoff.validate_seed(authorized)

    unbounded = seed()
    unbounded["known_context"] = ["x" * 501]
    with pytest.raises(ValueError, match="at most 500 characters"):
        research_handoff.validate_seed(unbounded)


def test_seed_builder_returns_the_validated_inline_shape() -> None:
    source = seed("continuity-triage")
    result = research_handoff.build_seed(
        producer_workflow=source["producer"]["workflow"],
        item_id=source["producer"]["item_id"],
        source_refs=source["producer"]["source_refs"],
        decision_context=source["decision_context"],
        candidate_question=source["candidate_question"],
        scope_hints=source["scope_hints"],
        known_context=source["known_context"],
        unresolved_gaps=source["unresolved_gaps"],
        rival_hints=source["rival_hints"],
        routing_workflow=source["routing_hint"]["workflow"],
        routing_reason=source["routing_hint"]["reason"],
        identifiers=source["identifiers"],
    )

    assert result == source


def test_completed_handoff_accepts_only_bounded_seed_origin() -> None:
    value = packet()
    value["origin_seed"] = {
        "producer": "world-monitor",
        "item_id": "candidate-001",
    }
    assert research_handoff.validate_packet(value)["valid"] is True

    value["origin_seed"]["authority"] = {"execute": True}
    with pytest.raises(ValueError, match="origin_seed has unsupported fields"):
        research_handoff.validate_packet(value)


def test_cli_validates_seed_without_expanding_it(tmp_path: Path, capsys) -> None:
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(seed()), encoding="utf-8")

    assert research_handoff.main(["--seed", str(path), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)

    assert result["schema"] == "research-brief-seed-v1"
    assert "research_contract" not in result
    assert result["execution_triggered"] is False

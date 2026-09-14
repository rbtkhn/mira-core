from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import library_reasoning as subject
import recursive_learning_ledger


CONSTELLATION_ID = "MIRA-CONSTELLATION-HOMER-DANTE-TOLSTOY"


def test_retrospective_reviews_cannot_advance(tmp_path, monkeypatch):
    monkeypatch.setattr(subject, "resolve_packet_root", lambda: tmp_path)
    review = {
        "case_id": "rehearsal", "evaluation_kind": "retrospective-rehearsal",
        "versions": {name: {"text": "review", "scores": {m: 3 for m in subject.ABLATION_METRICS}} for name in ("without_library", "with_library", "final_voice")},
        "materially_improved": True, "evidence_laundering_failure": False,
        "cadence_proportionate": True, "review_note": "Unblinded rehearsal",
        "comparison_phase": "baseline", "calibration_group": "holdout",
        "routing_memory_sha256": "none", "routing_metrics": {m: 0 for m in subject.ROUTING_METRICS},
    }
    for n in range(4):
        review["case_id"] = f"rehearsal-{n}"
        (tmp_path / f"case-{n}-review.json").write_text(json.dumps(review))
    assert not subject.validate_ablation_review(review)
    assert subject.advancement_status()["review_count"] == 0
    assert subject.calibration_status()["baseline"]["case_count"] == 0
    del review["evaluation_kind"]
    (tmp_path / "legacy-review.json").write_text(json.dumps(review))
    assert subject.advancement_status()["review_count"] == 1
    assert subject.calibration_status()["baseline"]["case_count"] == 1
    review["evaluation_kind"] = "unknown"
    assert subject.validate_ablation_review(review)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_cognitive_inventory_has_eight_current_heads_and_explicit_one_hop() -> None:
    inventory = subject.cognitive_inventory(
        "How do office and order depend on jurisdictional differentiation?", "office order"
    )
    assert len(inventory["works"]) == 8
    dante = next(row for row in inventory["direct"] if "DANTE" in row["canonical_work_id"])
    assert dante["promotion_state"] == "promoted"
    assert dante["note_ref"].endswith("dante-de-monarchia-commedia-cognitive-note.md")
    companions = {row["canonical_work_id"] for row in inventory["companions"]}
    assert companions == {
        "MIRA-WORK-HOMER-ILIAD-ODYSSEY",
        "MIRA-WORK-TOLSTOY-WAR-AND-PEACE",
    }
    assert all(row["analysis_state"] == "analysis-pending" for row in inventory["companions"])
    assert all(row["eligible_route_ids"] == [] for row in inventory["companions"])


def test_negative_signature_cancels_promotion_and_prose_does_not_match() -> None:
    conflicted = subject.cognitive_inventory(
        "office occupant collapse beside office and order", "office occupant collapse"
    )
    dante = next(row for row in conflicted["direct"] if "DANTE" in row["canonical_work_id"])
    assert dante["promotion_state"] == "suppressed-negative"
    assert dante["library_source_id"] not in conflicted["preferred_source_ids"]

    prose_only = subject.cognitive_inventory("sacred poem grief", "sacred poem")
    assert prose_only["direct"] == []
    assert prose_only["companions"] == []


def test_explicit_constellation_binds_current_heads_and_own_passages() -> None:
    inventory = subject.cognitive_inventory(
        "Can strikes become coercive leverage?",
        "Escalation consumes alliance capacity and executable relations.",
        CONSTELLATION_ID,
    )
    members = inventory["explicit_constellation"]
    assert {row["canonical_work_id"] for row in members} == set(
        inventory["constellation"]["member_work_ids"]
    )
    assert len(inventory["constellation"]["manifest_sha256"]) == 64
    for row in members:
        assert row["nomination_basis"] == "explicit-constellation"
        assert row["eligible_route_ids"] == []
        assert row["passages"]
        assert all(len(passage["raw_span_sha256"]) == 64 for passage in row["passages"])
        assert all(passage["excerpt"] for passage in row["passages"])


def test_constellation_rejects_unknown_malformed_and_stale_members(monkeypatch) -> None:
    with pytest.raises(subject.ReasoningError, match="unknown Library constellation"):
        subject.cognitive_inventory("question", "mechanism", "MIRA-CONSTELLATION-MISSING")

    original = subject.library_integration.load_manifest(subject.REPO_ROOT)
    malformed = json.loads(json.dumps(original))
    malformed["constellation"]["member_work_ids"].append(
        malformed["constellation"]["member_work_ids"][0]
    )
    monkeypatch.setattr(subject.library_integration, "load_manifest", lambda _root: malformed)
    with pytest.raises(subject.ReasoningError, match="stale or malformed"):
        subject.cognitive_inventory("question", "mechanism", CONSTELLATION_ID)

    stale = json.loads(json.dumps(original))
    stale["constellation"]["member_work_ids"][-1] = "MIRA-WORK-MISSING"
    monkeypatch.setattr(subject.library_integration, "load_manifest", lambda _root: stale)
    with pytest.raises(subject.ReasoningError, match="Library cognitive controls invalid"):
        subject.cognitive_inventory("question", "mechanism", CONSTELLATION_ID)


def test_constellation_packet_is_nonoperational_and_enforces_passage_ownership() -> None:
    packet = subject.geo_packet(
        "2026-09-01", "Can strikes become coercive leverage?",
        "Escalation consumes logistical alliance capacity and executable relations.",
        CONSTELLATION_ID,
    )
    assert packet["constellation"]["constellation_id"] == CONSTELLATION_ID
    assert len(packet["cognitive_context"]) == 3
    assert all(row["eligible_route_ids"] == [] for row in packet["cognitive_context"])
    assert all(row["nomination_basis"] == "explicit-constellation" for row in packet["cognitive_context"])

    for candidate in packet["candidates"]:
        candidate.update({"disposition": "held", "effect_on_judgment": [], "failure_tags": []})
    for context in packet["cognitive_context"]:
        context.update({
            "cognitive_disposition": "held", "cognitive_effects": ["no-material-change"],
            "reviewed_passage_digests": [],
        })
    packet["cognitive_context"][0]["reviewed_passage_digests"] = ["f" * 64]
    packet["packet_effect"] = ["no-material-change"]
    assert any("only its own admitted passages" in failure for failure in subject.validate_adjudication(packet))


def test_harvest_is_deterministic_check_only_and_per_work(tmp_path: Path) -> None:
    packet = subject.geo_packet(
        "2026-09-01", "Can strikes become coercive leverage?",
        "Escalation consumes logistical alliance capacity and executable relations.",
        CONSTELLATION_ID,
    )
    for candidate in packet["candidates"]:
        candidate.update({"disposition": "held", "effect_on_judgment": [], "failure_tags": []})
    dispositions = ["used-materially", "used-nonmaterially", "rejected"]
    for context, disposition in zip(packet["cognitive_context"], dispositions):
        context.update({
            "cognitive_disposition": disposition,
            "cognitive_effects": ["clarified-mechanism"] if disposition == "used-materially" else ["no-material-change"],
            "reviewed_passage_digests": [context["passages"][0]["raw_span_sha256"]],
        })
    packet["packet_effect"] = ["changed-mechanism"]
    packet["review_state"] = "adjudicated"
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    first = subject.harvest_note_candidates(packet_path, check=True)
    second = subject.harvest_note_candidates(packet_path, check=True)
    assert first == second
    assert first["written"] is False
    assert first["private_packet"] is None
    assert first["harvest"]["schema_version"] == "mira-library-cognitive-harvest-v2"
    assert first["harvest"]["lineage_status"] == "digest-bound"
    assert first["harvest"]["source_packet"]["artifact_id"] == packet["packet_id"]
    assert first["harvest"]["source_packet"]["sha256"] == digest(packet_path)
    assert len(first["harvest"]["candidates"]) == 3
    assert {row["disposition"] for row in first["harvest"]["candidates"]} == {
        "note-candidate", "open-question", "no-change",
    }
    assert all(row["source_support"] for row in first["harvest"]["candidates"])
    assert not (tmp_path / "harvest").exists()
    packet["crisis_object"] = "same packet ID with changed adjudicated bytes"
    packet_path.write_bytes(subject.encoded_json(packet))
    changed = subject.harvest_note_candidates(packet_path, check=True)
    assert changed["harvest"]["harvest_id"] != first["harvest"]["harvest_id"]


def pending_constellation_packet() -> dict:
    packet = subject.geo_packet(
        "2026-09-01", "Can strikes become coercive leverage?",
        "Escalation consumes logistical alliance capacity and executable relations.",
        CONSTELLATION_ID,
    )
    return packet


def adjudication_spec(packet_path: Path, packet: dict) -> dict:
    return {
        "schema_version": "mira-library-adjudication-v2",
        "source_packet": subject.artifact_binding(
            packet_path, role="source-packet", artifact_id=packet["packet_id"]
        ),
        "candidates": [
            {
                "source_id": row["source_id"],
                "disposition": "held",
                "effect_on_judgment": [],
                "failure_tags": [],
            }
            for row in packet["candidates"]
        ],
        "cognitive_context": [
            {
                "canonical_work_id": row["canonical_work_id"],
                "cognitive_disposition": "used-materially",
                "cognitive_effects": ["clarified-mechanism"],
                "reviewed_passage_digests": [row["passages"][0]["raw_span_sha256"]],
            }
            for row in packet["cognitive_context"]
        ],
        "packet_effect": ["changed-mechanism"],
    }


def test_adjudication_requires_exact_packet_binding_and_check_is_nonmutating(tmp_path: Path) -> None:
    packet = pending_constellation_packet()
    packet_path = tmp_path / "packet.json"
    packet_path.write_bytes(subject.encoded_json(packet))
    spec = adjudication_spec(packet_path, packet)
    spec_path = tmp_path / "adjudication.json"
    spec_path.write_bytes(subject.encoded_json(spec))
    before = digest(packet_path)

    result = subject.adjudicate(packet_path, spec_path, check=True)

    assert result["status"] == "ok"
    assert result["written"] is False
    assert result["private_receipt"] is None
    assert result["receipt"]["schema_version"] == "mira-library-adjudication-receipt-v1"
    assert result["receipt"]["pending_packet"]["sha256"] == before
    assert result["receipt"]["artifact_bindings"][1]["sha256"] == result["packet_sha256"]
    assert digest(packet_path) == before
    assert not (tmp_path / "reviews").exists()


def test_adjudication_rejects_packet_tampering(tmp_path: Path) -> None:
    packet = pending_constellation_packet()
    packet_path = tmp_path / "packet.json"
    packet_path.write_bytes(subject.encoded_json(packet))
    spec = adjudication_spec(packet_path, packet)
    spec_path = tmp_path / "adjudication.json"
    spec_path.write_bytes(subject.encoded_json(spec))
    packet["crisis_object"] = "tampered after review preparation"
    packet_path.write_bytes(subject.encoded_json(packet))

    with pytest.raises(subject.ReasoningError, match="digest mismatch"):
        subject.adjudicate(packet_path, spec_path, check=True)


def test_written_adjudication_receipt_and_harvest_are_digest_bound(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    packet = pending_constellation_packet()
    packet_path = tmp_path / "packet.json"
    packet_path.write_bytes(subject.encoded_json(packet))
    spec = adjudication_spec(packet_path, packet)
    spec_path = tmp_path / "adjudication.json"
    spec_path.write_bytes(subject.encoded_json(spec))
    monkeypatch.setattr(subject, "append_feedback", lambda *_args, **_kwargs: 0)

    result = subject.adjudicate(packet_path, spec_path, check=False)
    receipt_path = Path(result["private_receipt"])
    harvest = subject.harvest_note_candidates(packet_path, check=True)["harvest"]
    harvest_path = tmp_path / "harvest.json"
    harvest_path.write_bytes(subject.encoded_json(harvest))

    assert result["packet_sha256"] == digest(packet_path)
    assert receipt_path.is_file()
    assert subject.verify_lineage(receipt_path)["lineage_status"] == "digest-bound"
    assert subject.verify_lineage(harvest_path)["lineage_status"] == "digest-bound"


def test_lineage_verifier_reports_legacy_and_detects_recursive_tampering(tmp_path: Path) -> None:
    legacy = tmp_path / "legacy-harvest.json"
    legacy.write_bytes(subject.encoded_json({
        "schema_version": "mira-library-cognitive-harvest-v1",
        "source_packet_id": "MLGP-legacy",
    }))
    legacy_result = subject.verify_lineage(legacy)
    assert legacy_result["lineage_status"] == "legacy-id-bound"
    assert subject.verify_lineage(legacy, require_digest_bound=True)["status"] == "strict-lineage-failed"

    child = tmp_path / "child.json"
    child.write_bytes(subject.encoded_json({"schema_version": "leaf-v1", "value": 1}))
    comparison = tmp_path / "comparison.json"
    comparison.write_bytes(subject.encoded_json({
        "schema_version": "mira-library-comparison-v1",
        "artifact_bindings": [subject.artifact_binding(child, role="review")],
    }))
    assert subject.verify_lineage(comparison)["lineage_status"] == "digest-bound"
    child.write_bytes(subject.encoded_json({"schema_version": "leaf-v1", "value": 2}))
    assert subject.verify_lineage(comparison)["lineage_status"] == "mismatch"


def test_learning_events_bind_final_packet_digest(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    routing_path = tmp_path / "events.jsonl"
    cognitive_path = tmp_path / "cognitive-events.jsonl"
    monkeypatch.setattr(subject, "feedback_path", lambda: routing_path)
    monkeypatch.setattr(subject, "cognitive_feedback_path", lambda: cognitive_path)
    packet_sha256 = "a" * 64
    packet = {
        "packet_id": "MLGP-bound",
        "crisis_object": "test",
        "crisis_signature": "b" * 64,
        "routing": {"profiles": []},
        "retrieval_cost": {},
        "candidates": [{
            "source_id": "LIB-X",
            "bodies": [],
            "analytic_role": "contextual-witness",
            "adjudicated_role": "contextual-witness",
            "disposition": "held",
            "effect_on_judgment": [],
            "failure_tags": [],
        }],
        "cognitive_context": [{
            "canonical_work_id": "MIRA-WORK-X",
            "nomination_basis": "explicit-constellation",
            "matched_positive_signatures": [],
            "cognitive_disposition": "used-materially",
            "cognitive_effects": ["clarified-mechanism"],
            "reviewed_passage_digests": ["c" * 64],
            "note_sha256": "d" * 64,
            "note_dependency_sha256": "e" * 64,
            "profile_sha256": "f" * 64,
        }],
    }

    assert subject.append_feedback(packet, {}, packet_sha256) == 2
    routing = json.loads(routing_path.read_text(encoding="utf-8").strip())
    cognitive = json.loads(cognitive_path.read_text(encoding="utf-8").strip())
    assert routing["packet_sha256"] == packet_sha256
    assert cognitive["packet_sha256"] == packet_sha256


def cognitive_event(index: int, crisis: str, *, disposition: str = "used-materially") -> dict:
    return {
        "schema_version": "mira-library-cognitive-observation-v1",
        "event_id": f"event-{index}",
        "packet_id": f"packet-{index}",
        "canonical_work_id": "MIRA-WORK-DANTE-DE-MONARCHIA-COMMEDIA",
        "nomination_basis": "direct-signature",
        "matched_positive_signatures": ["office-and-order"],
        "cognitive_disposition": disposition,
        "cognitive_effects": ["clarified-mechanism"],
        "reviewed_passage_digests": [f"passage-{index}"],
        "note_sha256": "a" * 64,
        "note_dependency_sha256": "b" * 64,
        "profile_sha256": "c" * 64,
        "crisis_signature": crisis,
        "grounded": True,
    }


def test_route_review_nomination_requires_three_material_uses_two_crises(monkeypatch) -> None:
    events = [cognitive_event(1, "x"), cognitive_event(2, "x"), cognitive_event(3, "y")]
    monkeypatch.setattr(subject, "read_cognitive_feedback", lambda: events)
    result = subject.route_review_candidates(check=True)
    assert result["candidate_count"] == 1
    assert result["written"] == []
    assert result["candidates"][0]["status"] == "inactive"

    monkeypatch.setattr(subject, "read_cognitive_feedback", lambda: [*events, cognitive_event(4, "z", disposition="rejected")])
    assert subject.route_review_candidates(check=True)["candidate_count"] == 0


def test_learning_export_is_check_only_digest_bound_and_recursively_assessable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    event = cognitive_event(1, "x")
    event["observed_at"] = "2026-09-02T00:00:00Z"
    monkeypatch.setattr(subject, "read_cognitive_feedback", lambda: [event])
    evidence = [
        ("behavior-observation", "docs/skill-drafts/library-reasoning/SKILL.md"),
        ("diagnosis", "docs/skill-drafts/library-integration/SKILL.md"),
        ("implementation", "scripts/library_reasoning.py"),
        ("verification", "tests/test_library_reasoning.py"),
    ]
    spec = {
        "schema_version": "mira-library-learning-export-spec-v1",
        "observation_event_ids": ["event-1"],
        "claims": {
            "observation": "The prior selector could not consume governed notes.",
            "diagnosis": "No explicit cognitive adapter existed.",
            "intervention": "Add a governed adapter.",
        },
        "artifacts": [
            {"relationship": relationship, "ref": ref, "sha256": digest(ROOT / ref)}
            for relationship, ref in evidence
        ],
        "intervention_commits": ["abcdef1"],
    }
    spec_path = tmp_path / "spec.json"
    output = tmp_path / "reference.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    result = subject.export_learning_reference(spec_path, output, check=True)
    assert result["written"] is False
    assert not output.exists()
    output.write_text(json.dumps(result["reference"]), encoding="utf-8")
    loaded = recursive_learning_ledger.load_process_reference(output)
    assessment = recursive_learning_ledger.assess_process_reference(loaded, ledger={"entries": []})
    assert assessment["status"] == "partial-candidate"
    assert assessment["stage_dispositions"]["outcome"]["status"] == "missing"


def test_v3_packet_requires_eligible_route_for_operational_disposition() -> None:
    packet = {
        "schema_version": "mira-library-geo-pilot-v3",
        "packet_effect": ["changed-mechanism"],
        "candidates": [{
            "source_id": "LIB-X", "disposition": "adopted", "eligible_route_ids": [],
            "analogy": {"shared_mechanism": "x", "decisive_structural_differences": ["y"], "rejection_condition": "z"},
            "concept_bridge": {"historical_meaning": "x", "non_equivalence": "y"},
            "effect_on_judgment": ["changed-mechanism"], "failure_tags": [],
        }],
        "cognitive_context": [],
    }
    assert any("without an eligible route" in failure for failure in subject.validate_adjudication(packet))


def test_public_runner_registers_library_reasoning() -> None:
    runner = (ROOT / "tools/run_repo.py").read_text(encoding="utf-8")
    assert '"library-reasoning": REPO_ROOT / "scripts" / "library_reasoning.py"' in runner

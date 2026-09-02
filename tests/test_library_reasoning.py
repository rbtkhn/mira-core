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

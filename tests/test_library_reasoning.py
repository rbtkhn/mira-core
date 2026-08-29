from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


SCRIPTS_ROOT = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import archive_library
import library_reasoning


def source(source_id: str, era: str, civilization: str, source_type: str, body: dict | None = None) -> dict:
    return {
        "source_id": source_id,
        "title": f"{civilization} state coercion and order",
        "author": f"{civilization} authority",
        "subject_era": era,
        "source_composition_era": era,
        "edition_era": "industrial",
        "secondary_eras": [],
        "date_start": 1,
        "date_end": 2,
        "date_label": "fixture",
        "era_basis": "fixture",
        "civilization_tags": [civilization],
        "source_type": source_type,
        "location": "fixture",
        "status": "located",
        "notes": "coercion passage legitimacy mobilization alliance constraint",
        "text_status": "available" if body else "missing",
        "coverage_status": "principal-work" if body else "metadata-only",
        "coverage_notes": "fixture",
        "text_bodies": [body] if body else [],
    }


def configure(tmp_path: Path, monkeypatch) -> tuple[Path, list[dict]]:
    text_root = tmp_path / ".mira-private" / "library" / "texts"
    text_root.mkdir(parents=True, exist_ok=True)
    body_path = text_root / "ROMAN-BODY.txt"
    body_path.write_text(
        "The state depends upon legitimacy and alliance constraint.\n\n"
        "Coercion without political order exhausts mobilization.",
        encoding="utf-8",
    )
    body = {
        "body_id": "LIB-ROMAN-BODY",
        "work_title": "Roman fixture",
        "text_location": "library-text://ROMAN-BODY.txt",
        "text_sha256": hashlib.sha256(body_path.read_bytes()).hexdigest(),
        "text_bytes": body_path.stat().st_size,
        "text_encoding": "utf-8",
        "language": "English",
        "edition_label": "fixture edition",
        "coverage_status": "complete-work",
        "status": "available",
    }
    rows = [
        source("LIB-ROMAN", "ancient", "rome", "historiography", body),
        source("LIB-PERSIAN", "medieval", "persia", "legal"),
        source("LIB-INDIA", "colonial", "india", "primary"),
        source("LIB-EUROPE", "industrial", "europe", "literary"),
    ]
    registry = tmp_path / "archive" / "library" / "library-registry.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(json.dumps({"registry_id": "fixture", "sources": rows}), encoding="utf-8")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", registry)
    monkeypatch.setenv("MIRA_CORE_LIBRARY_TEXT_ROOT", str(text_root))
    monkeypatch.setattr(library_reasoning, "PRIVATE_PACKET_ROOT", tmp_path / ".mira-private" / "library" / "reasoning")
    return registry, rows


def test_packet_root_rejects_non_private_location(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    monkeypatch.setenv(library_reasoning.PACKET_ROOT_ENV, "C:/Users/Public/mira-library-reasoning")
    with __import__("pytest").raises(library_reasoning.ReasoningError, match="inside .mira-private"):
        library_reasoning.resolve_packet_root()


def test_pre_scan_is_metadata_only_and_bounded(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    result = library_reasoning.pre_scan("Who sustains political order?", "coercion and legitimacy")
    assert result["passage_retrieval_performed"] is False
    assert 1 <= len(result["families"]) <= 5
    assert all("representative_source_id" in row for row in result["families"])


def test_thin_operational_case_skips_historical_retrieval(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    packet = library_reasoning.geo_packet(
        "2026-05-27", "Did a chiefly operational thin day warrant deepening?", "event report"
    )
    assert packet["routing"]["decision"] == "skip"
    assert packet["candidates"] == []
    assert packet["packet_effect"] == ["no-material-change"]


def test_geo_packet_bounds_candidates_and_passages(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    packet = library_reasoning.geo_packet("2026-07-06", "Can coercion preserve order?", "coercion legitimacy alliance")
    assert len(packet["candidates"]) <= 4
    assert packet["retrieval_cost"]["passage_count"] <= 8
    roman = next(row for row in packet["candidates"] if row["source_id"] == "LIB-ROMAN")
    assert roman["bodies"][0]["hash_state"] == "hash-verified"
    assert roman["bodies"][0]["passages"][0]["private_only"] is True
    assert packet["review_state"] == "pending-geo-strategy-adjudication"


def test_hash_mismatch_degrades_without_exposing_passages(tmp_path: Path, monkeypatch) -> None:
    registry, rows = configure(tmp_path, monkeypatch)
    rows[0]["text_bodies"][0]["text_sha256"] = "0" * 64
    registry.write_text(json.dumps({"registry_id": "fixture", "sources": rows}), encoding="utf-8")
    packet = library_reasoning.geo_packet("2026-07-06", "political order", "coercion legitimacy")
    roman = next(row for row in packet["candidates"] if row["source_id"] == "LIB-ROMAN")
    assert roman["bodies"][0]["hash_state"] == "hash-mismatch"
    assert roman["bodies"][0]["passages"] == []


def test_adjudication_requires_analogy_and_concept_safeguards(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    packet = library_reasoning.geo_packet("2026-07-06", "political order", "coercion legitimacy")
    packet["candidates"][0]["disposition"] = "adopted"
    packet["candidates"][0]["effect_on_judgment"] = ["changed-mechanism"]
    packet["packet_effect"] = ["changed-mechanism"]
    failures = library_reasoning.validate_adjudication(packet)
    assert any("structural difference" in item for item in failures)
    assert any("concept bridge" in item for item in failures)


def test_complete_adjudication_passes_with_rejected_remaining_candidates(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    packet = library_reasoning.geo_packet("2026-07-06", "political order", "coercion legitimacy")
    first, *rest = packet["candidates"]
    first["disposition"] = "narrowed"
    first["effect_on_judgment"] = ["prevented-overclaim"]
    first["analogy"].update({
        "shared_mechanism": "coercion depends on legitimacy",
        "decisive_structural_differences": ["nuclear deterrence"],
        "rejection_condition": "current bargaining is purely tactical",
    })
    first["concept_bridge"].update({
        "historical_meaning": "recognized political authority",
        "non_equivalence": "not modern legal sovereignty",
    })
    for row in rest:
        row["disposition"] = "rejected"
        row["effect_on_judgment"] = ["no-material-change"]
    packet["packet_effect"] = ["prevented-overclaim"]
    assert library_reasoning.validate_adjudication(packet) == []


def complete_review(case_id: str = "CASE-01") -> dict:
    scores = {name: 4 for name in library_reasoning.ABLATION_METRICS}
    return {
        "case_id": case_id,
        "packet_id": "MLGP-fixture",
        "versions": {
            name: {"text": f"{name} bounded judgment", "scores": dict(scores)}
            for name in ("without_library", "with_library", "final_voice")
        },
        "materially_improved": True,
        "evidence_laundering_failure": False,
        "cadence_proportionate": True,
        "review_note": "The historical rival narrowed the mechanism without changing factual posture.",
    }


def test_ablation_review_requires_all_versions_and_metrics() -> None:
    review = complete_review()
    del review["versions"]["final_voice"]["scores"]["prose_burden"]
    assert library_reasoning.validate_ablation_review(review) == [
        "ablation review has incomplete metrics: final_voice"
    ]


def test_ablation_review_rejects_unsafe_case_id() -> None:
    review = complete_review("../CASE-1")
    assert "ablation review requires safe case_id" in library_reasoning.validate_ablation_review(review)


def test_advancement_requires_four_reviews_three_improvements_and_no_laundering(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    root = library_reasoning.resolve_packet_root()
    root.mkdir(parents=True)
    for index in range(4):
        review = complete_review(f"CASE-{index + 1:02d}")
        if index == 3:
            review["materially_improved"] = False
        (root / f"CASE-{index + 1:02d}-review.json").write_text(json.dumps(review), encoding="utf-8")
    status = library_reasoning.advancement_status()
    assert status["advancement_ready"] is True
    assert status["materially_improved_count"] == 3


def test_reasoning_roots_are_ordered_read_only_and_conflicts_fail_closed(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    fallback = Path(__import__("os").environ["MIRA_CORE_LIBRARY_TEXT_ROOT"])
    overlay = tmp_path / ".mira-private" / "overlay"
    overlay.mkdir()
    (overlay / "ROMAN-BODY.txt").write_bytes((fallback / "ROMAN-BODY.txt").read_bytes())
    monkeypatch.setenv(library_reasoning.TEXT_ROOTS_ENV, str(overlay))
    body = archive_library.load_registry()["sources"][0]["text_bodies"][0]
    assert library_reasoning.reasoning_text_roots()[0] == overlay.resolve()
    assert library_reasoning.body_state(body)[0] == "hash-verified"
    (overlay / "ROMAN-BODY.txt").write_text("conflicting private copy", encoding="utf-8")
    assert library_reasoning.body_state(body) == ("root-conflict", None)


def test_raw_body_location_outside_private_root_is_not_read(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    public_body = tmp_path / "public-body.txt"
    public_body.write_text("coercion legitimacy order\n", encoding="utf-8")
    body = {
        "text_location": str(public_body),
        "text_sha256": hashlib.sha256(public_body.read_bytes()).hexdigest(),
    }
    assert library_reasoning.body_state(body) == ("outside-private-root", None)


def test_tei_extraction_excludes_header_and_returns_stable_context(tmp_path: Path) -> None:
    body = tmp_path / "fixture.xml"
    body.write_text(
        "<TEI xmlns='http://www.tei-c.org/ns/1.0'><teiHeader><revisionDesc>"
        "<change>alliance metadata only</change></revisionDesc></teiHeader><text><body><div>"
        "<head>Book I</head><p n='1'>Political order precedes durable coercion.<l>Nested line is not duplicated.</l></p>"
        "<p n='2'>Alliance capacity depends on legitimacy.</p><p n='3'>A rival mechanism follows.</p>"
        "</div></body></text></TEI>", encoding="utf-8"
    )
    method, passages = library_reasoning.paragraph_candidates(body, {"alliance", "capacity"})
    assert method == "tei-body-v1"
    assert passages[0]["locator"] == "tei:p:2"
    assert passages[0]["section"] == "Book I"
    assert "metadata" not in json.dumps(passages)
    assert "Political order" in passages[0]["context_before"]
    _, units = library_reasoning.extract_units(body)
    assert sum("Nested line" in row["text"] for row in units) == 1


def test_text_extraction_removes_publication_chrome(tmp_path: Path) -> None:
    body = tmp_path / "fixture.txt"
    body.write_text(
        "Project Gutenberg release metadata alliance capacity\n\nBOOK I\n\n"
        "Alliance capacity depends on political order.\n\nA contextual rival follows.",
        encoding="utf-8",
    )
    method, passages = library_reasoning.paragraph_candidates(body, {"alliance", "capacity"})
    assert method == "text-paragraph-v2"
    assert passages[0]["section"] == "BOOK I"
    assert "Gutenberg" not in json.dumps(passages)


def test_profile_roles_are_declared_not_positional(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    assert library_reasoning.profile_role(
        "LIB-ANCIENT-AUTHOR-027-THUCYDIDES", ["mobilization-alliance-capacity"]
    ) == "credible-rival"
    assert library_reasoning.profile_role("LIB-UNKNOWN", [], "literary") == "contextual-witness"


def completed_packet(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    configure(tmp_path, monkeypatch)
    packet = library_reasoning.geo_packet("2026-07-06", "political order", "coercion legitimacy")
    for row in packet["candidates"]:
        row["disposition"] = "rejected"
        row["effect_on_judgment"] = ["no-material-change"]
        row["failure_tags"] = ["irrelevant-lexical-match"]
    packet["packet_effect"] = ["no-material-change"]
    packet_path = library_reasoning.save_private_packet(packet)
    adjudication_path = tmp_path / "adjudication.json"
    adjudication_path.write_text(json.dumps({
        "candidates": [{
            "source_id": row["source_id"], "disposition": row["disposition"],
            "effect_on_judgment": row["effect_on_judgment"], "failure_tags": row["failure_tags"],
        } for row in packet["candidates"]],
        "packet_effect": ["no-material-change"], "review_minutes": 7,
    }), encoding="utf-8")
    return packet_path, adjudication_path


def test_adjudication_check_never_appends_learning_events(tmp_path: Path, monkeypatch) -> None:
    packet, adjudication = completed_packet(tmp_path, monkeypatch)
    result = library_reasoning.adjudicate(packet, adjudication, check=True)
    assert result["status"] == "ok"
    assert result["learning_events_appended"] == 0
    assert not library_reasoning.feedback_path().exists()
    result = library_reasoning.adjudicate(packet, adjudication, check=False)
    assert result["learning_events_appended"] == len(result["packet"]["candidates"])
    assert library_reasoning.adjudicate(packet, adjudication, check=False)["learning_events_appended"] == 0
    event_text = library_reasoning.feedback_path().read_text(encoding="utf-8")
    assert "private" not in event_text.lower()
    assert "passages" not in event_text


def test_corrected_adjudication_appends_and_supersedes_effective_feedback(tmp_path: Path, monkeypatch) -> None:
    packet, adjudication = completed_packet(tmp_path, monkeypatch)
    first = library_reasoning.adjudicate(packet, adjudication, check=False)
    value = json.loads(adjudication.read_text(encoding="utf-8"))
    value["candidates"][0]["disposition"] = "held"
    adjudication.write_text(json.dumps(value), encoding="utf-8")
    second = library_reasoning.adjudicate(packet, adjudication, check=False)
    assert second["learning_events_appended"] == 1
    history = library_reasoning.read_feedback()
    effective = library_reasoning.effective_feedback(history)
    assert len(history) == len(first["packet"]["candidates"]) + 1
    assert len(effective) == len(first["packet"]["candidates"])
    corrected = next(row for row in effective if row["source_id"] == value["candidates"][0]["source_id"])
    assert corrected["disposition"] == "held"
    assert corrected["supersedes_event_id"]


def write_learning_events(tmp_path: Path, monkeypatch, dispositions: list[str]) -> None:
    configure(tmp_path, monkeypatch)
    path = library_reasoning.feedback_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    events = []
    for index, disposition in enumerate(dispositions):
        events.append({
            "packet_id": f"MLGP-{index}", "profile_ids": ["passage-legitimacy-order"],
            "crisis_signature": f"crisis-{index % 2}", "source_id": "LIB-ROMAN",
            "disposition": disposition, "failure_tags": ["irrelevant-lexical-match"],
        })
    path.write_text("\n".join(json.dumps(row) for row in events) + "\n", encoding="utf-8")


def test_proposal_requires_consistency_and_two_crises(tmp_path: Path, monkeypatch) -> None:
    write_learning_events(tmp_path, monkeypatch, ["rejected", "rejected", "rejected"])
    result = library_reasoning.propose_routing_update(check=True)
    assert result["status"] == "ok"
    assert result["proposal"]["changes"][0]["adjustment"] == -3
    assert result["written"] is False
    write_learning_events(tmp_path, monkeypatch, ["rejected", "narrowed", "rejected"])
    assert library_reasoning.propose_routing_update(check=True)["status"] == "insufficient-evidence"


def test_activation_is_digest_bound_capped_and_rollbackable(tmp_path: Path, monkeypatch) -> None:
    write_learning_events(tmp_path, monkeypatch, ["narrowed", "narrowed", "narrowed"])
    first = library_reasoning.propose_routing_update(check=False)
    proposal_path = Path(first["private_proposal"])
    assert library_reasoning.activate_routing_memory(proposal_path, check=True)["written"] is False
    library_reasoning.activate_routing_memory(proposal_path, check=False)
    assert library_reasoning.learned_adjustment(["passage-legitimacy-order"], "LIB-ROMAN") == 2
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    proposal["changes"][0]["adjustment"] = 5
    proposal["created_at"] = "later"
    proposal["proposal_sha256"] = library_reasoning.proposal_digest(proposal)
    second_path = proposal_path.with_name("second.json")
    second_path.write_text(json.dumps(proposal), encoding="utf-8")
    library_reasoning.activate_routing_memory(second_path, check=False)
    assert library_reasoning.learned_adjustment(["passage-legitimacy-order"], "LIB-ROMAN") == 5
    proposal["changes"][0]["adjustment"] = 4
    proposal["created_at"] = "latest"
    proposal["proposal_sha256"] = library_reasoning.proposal_digest(proposal)
    third_path = proposal_path.with_name("third.json")
    third_path.write_text(json.dumps(proposal), encoding="utf-8")
    library_reasoning.activate_routing_memory(third_path, check=False)
    assert library_reasoning.learned_adjustment(["passage-legitimacy-order"], "LIB-ROMAN") == 4
    assert library_reasoning.rollback_routing_memory(check=True)["written"] is False
    library_reasoning.rollback_routing_memory(check=False)
    assert library_reasoning.learned_adjustment(["passage-legitimacy-order"], "LIB-ROMAN") == 5
    library_reasoning.rollback_routing_memory(check=False)
    assert library_reasoning.learned_adjustment(["passage-legitimacy-order"], "LIB-ROMAN") == 2


def test_active_memory_tamper_fails_closed_and_status_reports_invalid(tmp_path: Path, monkeypatch) -> None:
    write_learning_events(tmp_path, monkeypatch, ["narrowed", "narrowed", "narrowed"])
    proposal = Path(library_reasoning.propose_routing_update(check=False)["private_proposal"])
    library_reasoning.activate_routing_memory(proposal, check=False)
    active = library_reasoning.active_memory_path()
    value = json.loads(active.read_text(encoding="utf-8"))
    value["changes"][0]["adjustment"] = 5
    active.write_text(json.dumps(value), encoding="utf-8")
    with __import__("pytest").raises(library_reasoning.ReasoningError, match="digest mismatch"):
        library_reasoning.learned_adjustment(["passage-legitimacy-order"], "LIB-ROMAN")
    assert library_reasoning.learning_status()["active_memory_status"] == "invalid"


def test_tampered_or_uncapped_proposal_is_rejected(tmp_path: Path, monkeypatch) -> None:
    write_learning_events(tmp_path, monkeypatch, ["rejected", "rejected", "rejected"])
    result = library_reasoning.propose_routing_update(check=False)
    proposal = Path(result["private_proposal"])
    value = json.loads(proposal.read_text(encoding="utf-8"))
    value["changes"][0]["adjustment"] = -6
    proposal.write_text(json.dumps(value), encoding="utf-8")
    with __import__("pytest").raises(library_reasoning.ReasoningError, match="digest mismatch"):
        library_reasoning.activate_routing_memory(proposal, check=True)


def test_consistent_role_and_editorial_failures_create_bounded_lessons(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    path = library_reasoning.feedback_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [{
        "packet_id": f"MLGP-{index}", "profile_ids": ["passage-legitimacy-order"],
        "crisis_signature": f"crisis-{index % 2}", "source_id": "LIB-ROMAN",
        "body_ids": ["LIB-ROMAN-BODY"], "extraction_methods": ["tei-body-v1"],
        "disposition": "rejected" if index != 1 else "held", "adjudicated_role": "credible-rival",
        "failure_tags": ["editorial-apparatus"],
    } for index in range(3)]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    changes = library_reasoning.propose_routing_update(check=True)["proposal"]["changes"]
    assert {row["kind"] for row in changes} >= {"role-override", "extraction-suppression"}
    assert "source-weight" not in {row["kind"] for row in changes}


def test_skip_condition_requires_governed_profile_terms_and_activation(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    path = library_reasoning.feedback_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [{
        "packet_id": f"MLGP-{index}", "profile_ids": ["passage-legitimacy-order"],
        "crisis_signature": f"crisis-{index % 2}", "source_id": "LIB-ROMAN",
        "disposition": "held", "failure_tags": ["crisis-object-mismatch"],
        "skip_condition_terms": ["passage", "regional"],
    } for index in range(3)]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    result = library_reasoning.propose_routing_update(check=False)
    assert "skip-condition" in {row["kind"] for row in result["proposal"]["changes"]}
    library_reasoning.activate_routing_memory(Path(result["private_proposal"]), check=False)
    decision = library_reasoning.routing_decision("regional passage report", "coercion legitimacy")
    assert decision["decision"] == "skip"


def test_skip_condition_adjudication_requires_uniform_mismatch_evidence(tmp_path: Path, monkeypatch) -> None:
    packet, adjudication = completed_packet(tmp_path, monkeypatch)
    value = json.loads(adjudication.read_text(encoding="utf-8"))
    value["skip_condition_terms"] = ["passage", "regional"]
    adjudication.write_text(json.dumps(value), encoding="utf-8")
    invalid = library_reasoning.adjudicate(packet, adjudication, check=True)
    assert invalid["status"] == "invalid"
    assert any("crisis-object-mismatch" in failure for failure in invalid["failures"])
    for row in value["candidates"]:
        row["failure_tags"] = ["crisis-object-mismatch"]
    adjudication.write_text(json.dumps(value), encoding="utf-8")
    assert library_reasoning.adjudicate(packet, adjudication, check=True)["status"] == "ok"


def calibrated_review(case_id: str, group: str, phase: str, irrelevant: int, minutes: int, memory_sha: str = "none", comparison_case_id: str | None = None) -> dict:
    row = complete_review(case_id)
    row.update({
        "calibration_group": group,
        "comparison_phase": phase,
        "routing_memory_sha256": memory_sha,
        "comparison_case_id": comparison_case_id,
        "routing_metrics": {
            "candidates_reviewed": 10, "candidates_accepted": 3,
            "irrelevant_candidates": irrelevant, "missing_bodies": 1,
            "review_minutes": minutes, "credible_rivals_accepted": 1,
            "anachronism_failures": 0, "evidence_laundering_failures": 0,
            "operational_skip_expected": 1 if group == "holdout" else 0,
            "operational_skip_correct": 1 if group == "holdout" else 0,
        },
    })
    return row


def test_calibration_status_enforces_twelve_case_and_shadow_thresholds(tmp_path: Path, monkeypatch) -> None:
    configure(tmp_path, monkeypatch)
    write_learning_events(tmp_path, monkeypatch, ["narrowed", "narrowed", "narrowed"])
    proposal = Path(library_reasoning.propose_routing_update(check=False)["private_proposal"])
    activated = library_reasoning.activate_routing_memory(proposal, check=False)
    memory_sha = activated["memory_sha256"]
    root = library_reasoning.resolve_packet_root()
    root.mkdir(parents=True, exist_ok=True)
    groups = ["calibration", "representative", "holdout"]
    for index in range(12):
        row = calibrated_review(f"BASE-{index}", groups[index // 4], "baseline", 5, 10)
        (root / f"BASE-{index}-review.json").write_text(json.dumps(row), encoding="utf-8")
    for index in range(4):
        row = calibrated_review(f"SHADOW-{index}", "holdout", "shadow", 3, 7, memory_sha, f"BASE-{8 + index}")
        (root / f"SHADOW-{index}-review.json").write_text(json.dumps(row), encoding="utf-8")
    status = library_reasoning.calibration_status()
    assert status["baseline_ready"] is True
    assert status["shadow_ready"] is True
    assert status["irrelevant_retrieval_reduction"] >= 0.30
    assert status["median_review_time_reduction"] >= 0.20
    assert status["advancement_ready"] is True

    tampered = calibrated_review("SHADOW-BAD", "holdout", "shadow", 3, 7, "0" * 64, "BASE-8")
    (root / "SHADOW-BAD-review.json").write_text(json.dumps(tampered), encoding="utf-8")
    assert library_reasoning.calibration_status()["shadow_ready"] is False

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import reality


def test_reality_snapshot_matches_loader_and_suppresses_reloads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    records = {"OPC-20260715-01": claim()}
    load_calls = 0

    def counted_load_records(_root: Path = reality.REALITY_ROOT):
        nonlocal load_calls
        load_calls += 1
        return records

    monkeypatch.setattr(reality, "load_records", counted_load_records)
    uncached_state = reality.claim_state("OPC-20260715-01")
    uncached_graph = reality.relevant_subgraph({"OPC-20260715-01"})
    uncached_digest = reality.subgraph_digest({"OPC-20260715-01"})
    uncached_failures = reality.validate_all(check_views=False)
    assert load_calls == 4

    assert reality.claim_state("OPC-20260715-01", records=records) == uncached_state
    assert reality.relevant_subgraph(
        {"OPC-20260715-01"}, records=records
    ) == uncached_graph
    assert reality.subgraph_digest(
        {"OPC-20260715-01"}, records=records
    ) == uncached_digest
    assert reality.validate_all(check_views=False, records=records) == uncached_failures
    assert load_calls == 4


def source(source_id: str, language: str, environment: str, *, status: str = "active") -> dict:
    record = reality.base_record(source_id, "source", "2026-07-15", status=status, creator="test")
    record.update({
        "name": source_id,
        "canonical_url": f"https://example.com/{source_id.lower()}",
        "domain": "military_activity",
        "observables": "time, place, damage",
        "evidence_class": "independent_professional_reporting",
        "perspective": environment,
        "geography": "test",
        "origin_languages": [language],
        "access_languages": ["en"] if language != "en" else ["en"],
        "translation_provenance": "official_edition" if language != "en" else "not_required",
        "access": "open",
        "open_fallback": "self",
        "latency": "hours",
        "originating_chain_rule": "One original report is one chain.",
        "known_failure_modes": "Test limitation.",
        "appropriate_uses": "Bounded chronology.",
        "inappropriate_uses": "Universal trust.",
        "review_history": [{"date": "2026-07-15", "reviewer": "test", "note": "fixture"}],
        "geopolitical_environment": environment,
        "order": 1,
    })
    return record


def claim(claim_id: str = "OPC-20260715-01", *, consequence: str = "high") -> dict:
    record = reality.new_claim(
        claim_id,
        "2026-07-15",
        "operational_factual",
        "A bounded event occurred.",
        consequence=consequence,
        crisis_object="fixture",
        scope="one event",
    )
    record["created_by"] = "test"
    return record


def evidence(index: int, source_id: str, language: str, environment: str, chain: str) -> dict:
    observation = "The same bounded event was observed."
    record = reality.base_record(f"EVD-20260715-{index:03d}", "evidence", "2026-07-15", status="active", creator="test")
    record.update({
        "source_id": source_id,
        "url": f"https://example.com/evidence-{index}",
        "retrieved_at": "2026-07-15T12:00:00Z",
        "event_time": "2026-07-15",
        "observation": observation,
        "origin_language": language,
        "access_language": "en",
        "translation_provenance": "not_required" if language == "en" else "official_edition",
        "originating_chain": chain,
        "geopolitical_environment": environment,
        "limitation": "Does not establish intent.",
        "representation_sha256": reality.digest_text(observation),
        "evidence_role": "professional_reporting",
    })
    return record


def relation(index: int, evidence_id: str, claim_id: str = "OPC-20260715-01") -> dict:
    record = reality.base_record(f"REL-20260715-{index:03d}", "relation", "2026-07-15", status="active", creator="test")
    record.update({"from_id": evidence_id, "to_id": claim_id, "relation_type": "supports", "scope": "same bounded observable"})
    return record


def assessment(languages: list[str], chains: list[str], *, status: str = "canonical_assessed") -> dict:
    record = reality.base_record("ADJ-20260715-001", "assessment", "2026-07-15", status=status, creator="test")
    record.update({
        "claim_id": "OPC-20260715-01",
        "outcome": "supported",
        "confidence_boundary": "Support is bounded to event occurrence.",
        "rationale": "Independent multilingual agreement on one observable.",
        "evidence_ids": [f"EVD-20260715-{index:03d}" for index in range(1, len(languages) + 1)],
        "observable_ids": ["OBS-20260715-001"],
        "signoffs": [{"reviewer": "operator", "signed_at": "2026-07-15T12:00:00Z"}],
        "authorizes_public": True,
        "authorizes_forecast_scoring": False,
        "language_audit": {
            "origin_languages": sorted(set(languages)),
            "originating_chains": sorted(set(chains)),
            "regional_environment_present": True,
            "external_environment_present": True,
            "missing_environments": [],
        },
        "physical_evidence_exception": False,
        "language_search_record": "English, Chinese, and Russian environments checked.",
        "calibration_eligible": True,
    })
    return record


def graph(tmp_path: Path, languages: list[str], chains: list[str]) -> dict[str, dict]:
    environments = ["affected_region", "external", "challenged"]
    profile = next(item for item in reality.domain_profiles() if item["id"] == "DOMAIN-MILITARY-ACTIVITY")
    observable = reality.new_observable(
        "OBS-20260715-001",
        "2026-07-15",
        ["OPC-20260715-01"],
        "Did the bounded event occur?",
        domain_profile=profile["id"],
        resolution_rule="Resolve the same bounded event.",
        window={"start": "2026-07-15", "end": "2026-07-15"},
    )
    records = [claim(), profile, observable]
    for index, (language, chain) in enumerate(zip(languages, chains), start=1):
        source_id = f"VSRC-TEST-{index}"
        environment = environments[(index - 1) % len(environments)]
        records.extend([source(source_id, language, environment), evidence(index, source_id, language, environment, chain), relation(index, f"EVD-20260715-{index:03d}")])
    records.append(assessment(languages, chains))
    for item in records:
        reality.write_record(item, tmp_path)
    return reality.load_records(tmp_path)


def replace_record(root: Path, record: dict) -> None:
    path = reality.record_path(record["kind"], record["id"], root)
    path.write_text(reality.canonical_json(record), encoding="utf-8", newline="\n")


def test_three_languages_and_three_chains_support_high_consequence(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh", "ru"], ["CHAIN-EN", "CHAIN-ZH", "CHAIN-RU"])
    assert reality.validate_assessment(records["ADJ-20260715-001"], records) == []


def test_translations_and_syndications_do_not_create_language_or_chain_independence(tmp_path: Path) -> None:
    records = graph(tmp_path, ["zh", "zh", "zh"], ["CHAIN-ONE", "CHAIN-ONE", "CHAIN-ONE"])
    failures = reality.validate_assessment(records["ADJ-20260715-001"], records)
    assert "ADJ-20260715-001: canonical support requires 3 origin languages" in failures
    assert "ADJ-20260715-001: canonical support requires 3 independent chains" in failures


def test_contested_outcome_preserves_disagreement_without_language_upgrade(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh"], ["CHAIN-EN", "CHAIN-ZH"])
    item = records["ADJ-20260715-001"]
    item["outcome"] = "contested"
    item["status"] = "provisional_assessed"
    item["authorizes_public"] = False
    item["signoffs"] = [{"reviewer": "one", "signed_at": "2026-07-15T12:00:00Z"}]
    assert reality.validate_assessment(item, records) == []


def test_language_waiver_requires_physical_evidence_search_record_and_operator(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en"], ["CHAIN-SENSOR"])
    item = records["ADJ-20260715-001"]
    records["EVD-20260715-001"]["evidence_role"] = "observational"
    item["status"] = "canonical_with_language_waiver"
    item["physical_evidence_exception"] = True
    item["language_search_record"] = "Chinese and Russian sources were sought but unavailable."
    item["language_waiver"] = {
        "reason": "Direct geolocated imagery resolves the bounded physical event.",
        "reviewers": [{"reviewer": "operator"}],
    }
    assert reality.validate_assessment(item, records) == []
    item["language_waiver"]["reviewers"] = [{"reviewer": "reviewer-one"}]
    assert "ADJ-20260715-001: language waiver requires operator approval" in reality.validate_assessment(item, records)


def test_operator_signature_promotes_only_after_language_gates_pass(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh", "ru"], ["CHAIN-EN", "CHAIN-ZH", "CHAIN-RU"])
    item = records["ADJ-20260715-001"]
    item.update({"status": "draft", "signoffs": [], "authorizes_public": False})
    replace_record(tmp_path, item)

    reality.sign_assessment(item["id"], "reviewer-one", tmp_path)
    assert reality.load_records(tmp_path)[item["id"]]["status"] == "provisional_assessed"
    reality.sign_assessment(item["id"], "operator", tmp_path)
    assert reality.load_records(tmp_path)[item["id"]]["status"] == "canonical_assessed"


def test_operator_signature_does_not_promote_language_incomplete_support(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh"], ["CHAIN-EN", "CHAIN-ZH"])
    item = records["ADJ-20260715-001"]
    item.update({"status": "draft", "signoffs": [], "authorizes_public": False})
    replace_record(tmp_path, item)

    reality.sign_assessment(item["id"], "operator", tmp_path)
    assert reality.load_records(tmp_path)[item["id"]]["status"] == "provisional_assessed"


def test_ordinary_claim_promotes_after_one_signature_when_gate_passes(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh"], ["CHAIN-EN", "CHAIN-ZH"])
    claim_record = records["OPC-20260715-01"]
    claim_record["consequence"] = "ordinary"
    replace_record(tmp_path, claim_record)
    item = records["ADJ-20260715-001"]
    item.update({"status": "draft", "signoffs": [], "authorizes_public": False})
    replace_record(tmp_path, item)

    reality.sign_assessment(item["id"], "operator", tmp_path)
    assert reality.load_records(tmp_path)[item["id"]]["status"] == "canonical_assessed"
    audit = reality.audit_payload("OPC-20260715-01", tmp_path)
    assert audit["coverage"]["required_origin_languages"] == 2
    assert audit["coverage"]["language_gate_satisfied"] is True
    assert audit["authorization"]["required_signoffs"] == 1


def test_unprofiled_domain_cannot_receive_positive_canonical_resolution(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh", "ru"], ["A", "B", "C"])
    item = records["ADJ-20260715-001"]
    item["observable_ids"] = []
    assert "ADJ-20260715-001: unknown or unprofiled domains may resolve only as contested or unresolvable" in reality.validate_assessment(item, records)


def test_sibling_observable_cannot_upgrade_an_atomic_claim(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh", "ru"], ["A", "B", "C"])
    sibling = claim("CLM-20260715-002")
    records[sibling["id"]] = sibling
    records["OBS-20260715-001"]["claim_ids"] = [sibling["id"]]
    assert "ADJ-20260715-001: observable OBS-20260715-001 does not resolve this claim or one of its declared components" in reality.validate_assessment(records["ADJ-20260715-001"], records)


def test_waiver_command_requires_prerequisites_and_operator(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en"], ["CHAIN-SENSOR"])
    evidence_record = records["EVD-20260715-001"]
    evidence_record["evidence_role"] = "observational"
    replace_record(tmp_path, evidence_record)
    item = records["ADJ-20260715-001"]
    item.update({"status": "draft", "signoffs": [], "authorizes_public": False})
    replace_record(tmp_path, item)

    with pytest.raises(reality.RealityError, match="physical evidence exception"):
        reality.waive_language(item["id"], "operator", "Direct sensor resolution.", tmp_path)

    item["physical_evidence_exception"] = True
    item["language_search_record"] = "Chinese and Russian environments were searched without usable results."
    replace_record(tmp_path, item)
    reality.waive_language(item["id"], "operator", "Direct sensor resolution.", tmp_path)
    waived = reality.load_records(tmp_path)[item["id"]]
    assert waived["status"] == "canonical_with_language_waiver"
    assert {entry["reviewer"] for entry in waived["signoffs"]} == {"operator"}


def test_derived_editorial_material_cannot_support_claim(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh", "ru"], ["A", "B", "C"])
    records["EVD-20260715-001"]["evidence_role"] = "derived_editorial"
    failure = reality.validate_record(records["REL-20260715-001"], records)
    assert "REL-20260715-001: derived editorial material cannot support or challenge empirical claims" in failure


def test_context_only_material_cannot_support_claim_or_enter_assessment_counts(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh", "ru"], ["A", "B", "C"])
    records["EVD-20260715-001"]["evidence_role"] = "context_only"
    relation_failure = reality.validate_record(records["REL-20260715-001"], records)
    assert "REL-20260715-001: context_only material cannot support or challenge empirical claims" in relation_failure
    supporting = reality.supporting_evidence(records["ADJ-20260715-001"], records)
    assert {item["id"] for item in supporting} == {"EVD-20260715-002", "EVD-20260715-003"}


def test_candidate_source_is_context_only(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh", "ru"], ["A", "B", "C"])
    records["VSRC-TEST-1"]["status"] = "candidate"
    assert "EVD-20260715-001: candidate source may supply context only" in reality.validate_record(records["EVD-20260715-001"], records)


def test_expert_commentary_source_must_remain_candidate(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh", "ru"], ["A", "B", "C"])
    records["VSRC-TEST-1"]["evidence_class"] = "expert_commentary"
    assert "VSRC-TEST-1: expert commentary source must remain candidate" in reality.validate_record(records["VSRC-TEST-1"], records)


def test_profile_is_withheld_until_ten_claims_across_three_objects(tmp_path: Path) -> None:
    base = claim(consequence="low")
    base["claimant_refs"] = ["voice-a"]
    base["domain"] = "military_activity"
    for index in range(1, 10):
        item = dict(base)
        item["id"] = f"CLM-20260715-{index:03d}"
        item["crisis_object"] = f"object-{index % 3}"
        reality.write_record(item, tmp_path)
        adj = assessment([], [], status="canonical_assessed")
        adj["id"] = f"ADJ-20260715-{index:03d}"
        adj["claim_id"] = item["id"]
        adj["outcome"] = "contested"
        adj["authorizes_public"] = False
        adj["signoffs"] = [{"reviewer": "one"}]
        reality.write_record(adj, tmp_path)
    payload = reality.profile_payload("voice-a", tmp_path)
    assert payload["profiles"] == []
    assert payload["withheld"][0]["claims"] == 9
    assert payload["composite_score"] is None


def test_current_pilots_and_generated_views_validate() -> None:
    assert reality.validate_all() == []
    assert reality.claim_state("OPC-20260710-02")["assessment"]["outcome"] == "contested"
    assert reality.claim_state("OPC-20260714-01")["assessment"] is None


def test_migration_check_detects_structured_record_staleness(tmp_path: Path) -> None:
    for record in reality.load_records().values():
        reality.write_record(reality.clean_record(record), tmp_path)
    stale = reality.load_records(tmp_path)["ADJ-20260710-002"]
    stale["observable_ids"] = ["OBS-20260710-002"]
    replace_record(tmp_path, stale)
    assert "migration record is stale: ADJ-20260710-002" in reality.check_migration("2026-07-10", tmp_path)


def test_migration_check_accepts_authorized_signoffs_and_append_only_revision(
    tmp_path: Path,
) -> None:
    reality.migrate_date("2026-07-10", tmp_path)
    assessment_id = "ADJ-20260710-003"
    reality.sign_assessment(assessment_id, "operator", tmp_path)
    assert reality.check_migration("2026-07-10", tmp_path) == []

    reality.sign_assessment(assessment_id, "reviewer-two", tmp_path)
    records = reality.load_records(tmp_path)
    assert records[assessment_id]["status"] == "canonical_assessed"
    assert reality.check_migration("2026-07-10", tmp_path) == []

    revision = dict(records[assessment_id])
    revision.update({
        "id": "ADJ-20260715-900",
        "as_of": "2026-07-15",
        "created_at": "2026-07-15T00:00:00Z",
        "revision_of": assessment_id,
        "status": "provisional_assessed",
        "signoffs": [{"reviewer": "operator", "signed_at": "2026-07-15T12:00:00Z"}],
    })
    revision.pop("updated_at", None)
    reality.write_record(revision, tmp_path)
    assert reality.check_migration("2026-07-10", tmp_path) == []


def test_migration_check_rejects_outcome_tampering_despite_valid_signoff(
    tmp_path: Path,
) -> None:
    reality.migrate_date("2026-07-10", tmp_path)
    assessment_id = "ADJ-20260710-003"
    reality.sign_assessment(assessment_id, "operator", tmp_path)
    tampered = reality.load_records(tmp_path)[assessment_id]
    tampered["outcome"] = "supported"
    replace_record(tmp_path, tampered)
    assert f"migration record is stale: {assessment_id}" in reality.check_migration(
        "2026-07-10", tmp_path
    )


def test_audit_reports_supported_multilingual_state_and_stable_brief(tmp_path: Path) -> None:
    graph(tmp_path, ["en", "zh", "ru"], ["CHAIN-EN", "CHAIN-ZH", "CHAIN-RU"])
    payload = reality.audit_payload("OPC-20260715-01", tmp_path)
    assert payload["epistemic_state"]["outcome"] == "supported"
    assert payload["epistemic_state"]["canonical"] is True
    assert payload["coverage"]["required_origin_languages"] == 3
    assert payload["coverage"]["present_origin_languages"] == ["en", "ru", "zh"]
    assert payload["coverage"]["language_gate_satisfied"] is True
    assert payload["coverage"]["regional_environment_present"] is True
    assert payload["coverage"]["external_environment_present"] is True
    assert payload["authorization"]["required_signoffs"] == 1
    assert payload["authorization"]["required_reviewer"] == "operator"
    brief = reality.render_audit_brief(payload)
    for heading in (
        "Epistemic state",
        "Evidence posture",
        "Multilingual and lineage coverage",
        "Authorization boundary",
        "Next bounded action",
    ):
        assert heading in brief


@pytest.mark.parametrize("outcome", ["contested", "disconfirmed", "unresolvable"])
def test_audit_preserves_non_supporting_operational_outcomes(tmp_path: Path, outcome: str) -> None:
    records = graph(tmp_path, ["en"], ["CHAIN-EN"])
    item = records["ADJ-20260715-001"]
    item.update({"outcome": outcome, "authorizes_public": False})
    replace_record(tmp_path, item)
    payload = reality.audit_payload("OPC-20260715-01", tmp_path)
    assert payload["epistemic_state"]["outcome"] == outcome
    assert payload["coverage"]["language_gate_satisfied"] is True


def test_audit_reports_unassessed_claim_without_mutating_records(tmp_path: Path) -> None:
    graph(tmp_path, ["en"], ["CHAIN-EN"])
    reality.record_path("assessment", "ADJ-20260715-001", tmp_path).unlink()
    before = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*.json")
    }
    payload = reality.audit_payload("OPC-20260715-01", tmp_path)
    after = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*.json")
    }
    assert payload["epistemic_state"]["assessment_status"] == "unassessed"
    assert "assessment" in payload["missing_gates"]
    assert payload["coverage"]["language_gate_satisfied"] is False
    assert payload["authorization"]["required_signoffs"] == 1
    assert payload["authorization"]["required_reviewer"] == "operator"
    assert before == after


def test_audit_derives_environment_gates_for_unassessed_claims(tmp_path: Path) -> None:
    records = graph(
        tmp_path,
        ["en", "en", "en"],
        ["CHAIN-WEST-ONE", "CHAIN-WEST-TWO", "CHAIN-REGIONAL"],
    )
    for evidence_id, environment in (
        ("EVD-20260715-001", "western_independent"),
        ("EVD-20260715-002", "western_independent"),
        ("EVD-20260715-003", "middle_east_regional"),
    ):
        item = records[evidence_id]
        item["geopolitical_environment"] = environment
        replace_record(tmp_path, item)
    reality.record_path("assessment", "ADJ-20260715-001", tmp_path).unlink()

    payload = reality.audit_payload("OPC-20260715-01", tmp_path)

    assert payload["coverage"]["regional_environment_present"] is True
    assert payload["coverage"]["external_environment_present"] is True
    assert payload["coverage"]["lineage_gate_satisfied"] is True
    assert payload["coverage"]["language_gate_satisfied"] is False
    assert "assessment" in payload["missing_gates"]
    assert "origin_language_coverage" in payload["missing_gates"]
    assert "regional_environment" not in payload["missing_gates"]
    assert "external_environment" not in payload["missing_gates"]


def test_audit_reports_provisional_language_lineage_and_signoff_gaps(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en", "zh"], ["CHAIN-EN", "CHAIN-ZH"])
    item = records["ADJ-20260715-001"]
    item.update({
        "status": "provisional_assessed",
        "signoffs": [{"reviewer": "one", "signed_at": "2026-07-15T12:00:00Z"}],
        "authorizes_public": False,
    })
    replace_record(tmp_path, item)
    payload = reality.audit_payload("OPC-20260715-01", tmp_path)
    assert payload["coverage"]["language_gate_satisfied"] is False
    assert payload["coverage"]["lineage_gate_satisfied"] is False
    assert "origin_language_coverage" in payload["missing_gates"]
    assert "independent_lineage_coverage" in payload["missing_gates"]
    assert "human_signoff" in payload["missing_gates"]


def test_audit_discloses_valid_language_waiver(tmp_path: Path) -> None:
    records = graph(tmp_path, ["en"], ["CHAIN-SENSOR"])
    evidence_record = records["EVD-20260715-001"]
    evidence_record["evidence_role"] = "observational"
    replace_record(tmp_path, evidence_record)
    item = records["ADJ-20260715-001"]
    item.update({
        "status": "canonical_with_language_waiver",
        "physical_evidence_exception": True,
        "language_search_record": "Chinese and Russian environments were searched without usable results.",
        "language_waiver": {
            "reason": "Direct sensor evidence resolves the physical observable.",
            "reviewers": [{"reviewer": "operator"}],
        },
    })
    replace_record(tmp_path, item)
    payload = reality.audit_payload("OPC-20260715-01", tmp_path)
    assert payload["coverage"]["language_waiver"] is True
    assert payload["coverage"]["language_gate_satisfied"] is True
    assert payload["coverage"]["present_origin_languages"] == ["en"]


def test_audit_does_not_count_repetition_as_language_or_lineage_independence(tmp_path: Path) -> None:
    records = graph(tmp_path, ["zh", "zh", "zh"], ["CHAIN-ONE", "CHAIN-ONE", "CHAIN-ONE"])
    item = records["ADJ-20260715-001"]
    item.update({"status": "provisional_assessed", "authorizes_public": False})
    replace_record(tmp_path, item)
    payload = reality.audit_payload("OPC-20260715-01", tmp_path)
    assert payload["coverage"]["present_origin_languages"] == ["zh"]
    assert payload["coverage"]["present_independent_lineages"] == ["CHAIN-ONE"]


def test_audit_reports_pilot_impact_and_rejects_unknown_claim() -> None:
    payload = reality.audit_payload("OPC-20260714-01")
    assert payload["linked_investigations"] == ["VER-20260714-01"]
    assert "narrative-geopolitics/work/daily/2026-07-14/issue.md" in payload["impact"]["affected_artifacts"]
    with pytest.raises(reality.RealityError, match="unknown lattice claim"):
        reality.audit_payload("CLM-20990101-999")


def test_july_10_packet_remains_unchanged() -> None:
    path = reality.LEGACY_PACKETS_ROOT / "VER-20260710-01-hormuz-bypass-test" / "README.md"
    assert reality.digest_text(path.read_text(encoding="utf-8")) == "1445c5388421ae6e8d80c9a0c2189dd2d59b25a498ee59c636ec23a5eb5ce9f9"

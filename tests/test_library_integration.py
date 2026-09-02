from __future__ import annotations

import json
import copy
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import archive_library
import library_integration


def test_five_work_pilot_is_complete_without_essays() -> None:
    registry = archive_library.load_registry()
    assert library_integration.validate_repository(ROOT, registry) == []

    manifest = library_integration.load_pilot_manifest(ROOT)
    assert manifest["status"] == "pilot-complete"
    assert manifest["essay_state"] == "essay-pending"
    assert manifest["essay_artifacts_created"] == 0
    assert len(manifest["works"]) == 5

    topic_ids: set[str] = set()
    for work in manifest["works"]:
        root = ROOT / work["artifact_root"]
        topics = json.loads((root / "essay-topics.json").read_text(encoding="utf-8"))
        assert [row["rank"] for row in topics["topics"]] == [1, 2, 3]
        assert isinstance(topics["essay_refs"], list)
        assert topics["essay_refs"] == []
        assert topics["essay_artifacts_created"] == 0
        topic_ids.update(row["topic_contract_id"] for row in topics["topics"])
    assert len(topic_ids) == 15


def test_living_manifest_has_five_routed_and_three_noted_works() -> None:
    manifest = library_integration.load_manifest(ROOT)
    assert manifest["status"] == "current"
    assert manifest["work_count"] == 8
    assert manifest["stage_counts"] == {"noted": 3, "routed": 5}
    assert len(manifest["works"]) == 8

    registry = library_integration.load_work_registry(ROOT)
    by_id = {row["canonical_work_id"]: row for row in registry["works"]}
    for work in manifest["works"]:
        record = by_id[work["canonical_work_id"]]
        assert record["integration_stage"] == work["integration_stage"]
        head = library_integration.parse_note_envelope(
            ROOT / record["revision_head_note_ref"]
        )
        assert head["schema_version"] == library_integration.NOTE_SCHEMA
        assert head["template_id"] == library_integration.NOTE_TEMPLATE_ID
        assert library_integration.validate_note_template(
            ROOT / record["revision_head_note_ref"], head
        ) == []

    noted = [row for row in registry["works"] if row["integration_stage"] == "noted"]
    assert len(noted) == 3
    assert all(row["route_reviews"] == [] and row["essay_refs"] == [] for row in noted)


def test_human_views_are_deterministic_projections() -> None:
    result = library_integration.render_repository(ROOT, check=True)
    assert result == {"status": "passed", "check": True, "changed": [], "drift": []}


def test_integration_notes_are_source_bounded_and_do_not_name_auxiliary_corpus() -> None:
    manifest = library_integration.load_pilot_manifest(ROOT)
    for work in manifest["works"]:
        note_refs = work.get("note_refs") or [work["note_ref"]]
        for note_ref in note_refs:
            note_path = ROOT / note_ref
            note_text = note_path.read_text(encoding="utf-8").casefold()
            assert "civilization memory" not in note_text
            assert "civilization-memory" not in note_text
            assert "civmem" not in note_text
            envelope = library_integration.parse_note_envelope(note_path)
            assert envelope["interpretive_basis"] in {
                "admitted-source-body",
                "source-readiness-only",
            }
            assert set(envelope["dependency_snapshot"]) == {
                "source_identity_digest",
                "body_digests",
                "body_states",
                "passage_digests",
            }
            assert set(envelope["linked_artifact_digests"]) == {
                "profile_sha256",
                "coverage_sha256",
                "routing_sha256",
                "topics_sha256",
            }
            assert envelope["schema_version"] == library_integration.NOTE_SCHEMA_V2
            assert envelope["library_relations"] == [
                {
                    "explanation": envelope["library_relations"][0]["explanation"],
                    "relation_type": "interprets",
                    "role": "focal",
                    "target_id": work["canonical_work_id"],
                    "target_type": "library-work",
                }
            ]


def test_note_link_index_derives_living_constellation_from_explicit_edges() -> None:
    index = library_integration.build_note_link_index(ROOT)
    assert index["schema_version"] == library_integration.NOTE_LINK_INDEX_SCHEMA
    assert index["note_count"] == 16
    assert index["link_count"] == 22
    counts = {
        row["canonical_work_id"]: row["total_link_count"] for row in index["works"]
    }
    assert counts == {
        "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS": 3,
        "MIRA-WORK-DANTE-DE-MONARCHIA-COMMEDIA": 3,
        "MIRA-WORK-DU-BOIS-SOULS-OF-BLACK-FOLK": 2,
        "MIRA-WORK-GROTIUS-MARE-LIBERUM": 4,
        "MIRA-WORK-HOMER-ILIAD-ODYSSEY": 3,
        "MIRA-WORK-IBN-KHALDUN-MUQADDIMAH": 2,
        "MIRA-WORK-MURASAKI-TALE-OF-GENJI": 2,
        "MIRA-WORK-TOLSTOY-WAR-AND-PEACE": 3,
    }
    assert {row["cognitive_integration"] for row in index["works"]} == {"engaged"}
    assert sum(row["lineage_position"] == "head" for row in index["links"]) == 14
    assert sum(row["lineage_position"] == "ancestor" for row in index["links"]) == 8
    assert len({row["link_id"] for row in index["links"]}) == 22

    trio_ids = {
        "MIRA-WORK-DANTE-DE-MONARCHIA-COMMEDIA",
        "MIRA-WORK-HOMER-ILIAD-ODYSSEY",
        "MIRA-WORK-TOLSTOY-WAR-AND-PEACE",
    }
    trio_links = [
        row for row in index["links"]
        if row["lineage_position"] == "head" and row["source_work_id"] in trio_ids
    ]
    focal = [row for row in trio_links if row["relation_type"] == "interprets"]
    comparative = [row for row in trio_links if row["relation_type"] == "connects"]
    assert len(focal) == 3
    assert len(comparative) == 6
    assert all(row["role"] == "focal" and row["passage_refs"] for row in focal)
    assert all(row["role"] == "comparative" and row["passage_refs"] == [] for row in comparative)


def test_relation_validator_rejects_unknown_contract_values() -> None:
    envelope = {
        "dependency_snapshot": {"passage_digests": {"KNOWN": "a" * 64}},
        "library_relations": [
            {
                "target_type": "library-work",
                "target_id": "MISSING",
                "relation_type": "echoes",
                "role": "decorative",
                "explanation": "",
                "passage_refs": ["UNKNOWN"],
            }
        ],
    }
    failures = library_integration.validate_library_relations(
        envelope, {"KNOWN-WORK"}, label="test note"
    )
    assert any("unknown work" in failure for failure in failures)
    assert any("invalid relation_type" in failure for failure in failures)
    assert any("invalid role" in failure for failure in failures)
    assert any("nonempty explanation" in failure for failure in failures)
    assert any("unknown note passages" in failure for failure in failures)


def test_note_reconciliation_current_hard_soft_and_unknown() -> None:
    baseline = {
        "source_identity_digest": "s1",
        "body_digests": {"body": "b1"},
        "body_states": {"body": {"status": "available"}},
        "passage_digests": {"passage": "a1"},
    }
    assert library_integration.classify_note_changes(baseline, baseline)["state"] == "current"

    changed_body = {**baseline, "body_digests": {"body": "b2"}}
    hard = library_integration.classify_note_changes(baseline, changed_body)
    assert hard["state"] == "revision-due"
    assert hard["hard_changes"] == ["body_digests"]

    changed_linked_artifacts = {
        **baseline,
        "profile_sha256": "p2",
        "coverage_sha256": "c2",
        "routing_sha256": "r2",
        "topics_sha256": "t2",
    }
    unchanged = library_integration.classify_note_changes(baseline, changed_linked_artifacts)
    assert unchanged["state"] == "current"
    assert unchanged["hard_changes"] == []
    assert unchanged["soft_changes"] == []

    changed_passage = {**baseline, "passage_digests": {"passage": "a2"}}
    hard = library_integration.classify_note_changes(baseline, changed_passage)
    assert hard["state"] == "revision-due"
    assert hard["hard_changes"] == ["passage_digests"]

    mediated_body = {
        "status": "available",
        "coverage_status": "complete-work",
        "language": "english",
        "mediation_type": "translation",
        "translator": "Translator One",
        "translator_status": "known",
        "editor": "",
        "editor_status": "unknown",
        "edition_label": "Edition One",
    }
    mediated_baseline = {**baseline, "body_states": {"body": mediated_body}}
    corrected_mediation = {
        **mediated_baseline,
        "body_states": {
            "body": {**mediated_body, "translator": "Translator Two"}
        },
    }
    hard = library_integration.classify_note_changes(
        mediated_baseline, corrected_mediation
    )
    assert hard["state"] == "revision-due"
    assert hard["hard_changes"] == ["body_states"]

    canonical_mediation = {
        "schema_version": "mira-library-mediation-v1",
        "text_relation": {
            "kind": "translation",
            "source_languages": ["japanese"],
            "body_language": "english",
            "status": "known",
        },
        "edition_identity": {"label": "Edition One", "status": "known"},
        "primary_path": [
            {
                "layer_id": "MED-1",
                "sequence": 1,
                "kind": "translation",
                "status": "known",
                "revision_relevance": "interpretive",
                "agents": [{"role": "translator", "name": "Translator One", "status": "known"}],
                "scope": "Whole work",
            },
            {
                "layer_id": "MED-2",
                "sequence": 2,
                "kind": "digital-rendering",
                "status": "known",
                "revision_relevance": "carrier-only",
                "agents": [{"role": "text-provider", "name": "Provider One", "status": "known"}],
                "scope": "Electronic body",
            },
        ],
        "lineage_graph_ref": "archive/library/lineage/example.json",
        "unresolved_questions": [],
    }
    dependency_projection = library_integration.mediation_dependency_projection(
        canonical_mediation
    )
    assert [row["layer_id"] for row in dependency_projection["primary_path"]] == ["MED-1"]
    assert "lineage_graph_ref" not in dependency_projection
    changed_carrier = copy.deepcopy(canonical_mediation)
    changed_carrier["primary_path"][1]["agents"][0]["name"] = "Provider Two"
    assert library_integration.mediation_dependency_projection(
        changed_carrier
    ) == dependency_projection
    changed_translation = copy.deepcopy(canonical_mediation)
    changed_translation["primary_path"][0]["agents"][0]["name"] = "Translator Two"
    assert library_integration.mediation_dependency_projection(
        changed_translation
    ) != dependency_projection

    signaled = library_integration.classify_note_changes(
        baseline,
        baseline,
        [
            {"kind": "operator-correction", "id": "COR-1"},
            {"kind": "routing-contradiction", "id": "ROUTE-1"},
            {"kind": "cosmetic-render", "id": "COS-1"},
        ],
    )
    assert signaled["state"] == "revision-due"
    assert [row["id"] for row in signaled["hard_signals"]] == ["COR-1"]
    assert [row["id"] for row in signaled["soft_signals"]] == ["ROUTE-1"]
    assert [row["id"] for row in signaled["unknown_signals"]] == ["COS-1"]

    auxiliary = library_integration.classify_note_changes(
        baseline,
        baseline,
        [{"kind": "new-civmem-interpretation", "id": "AUX-1"}],
    )
    assert auxiliary["state"] == "current"
    assert [row["id"] for row in auxiliary["unknown_signals"]] == ["AUX-1"]


def test_revision_candidate_requires_governed_disposition() -> None:
    candidate = {
        "schema_version": "mira-library-note-revision-candidate-v1",
        "candidate_id": "REV-WORK-001",
        "canonical_work_id": "WORK",
        "trigger": {"state": "revision-due"},
        "changed_dependencies": ["profile_sha256"],
        "affected_claims": [],
        "open_questions": [],
        "rereading_scope": ["Changed profile claims"],
        "status": "resolved",
        "disposition": "reviewed-no-change",
    }
    assert library_integration.validate_revision_candidate(candidate) == []
    candidate["disposition"] = "auto-rewritten"
    failures = library_integration.validate_revision_candidate(candidate)
    assert "revision candidate has invalid disposition: auto-rewritten" in failures
    assert "resolved revision candidate requires a valid disposition" in failures


def test_repository_reconciliation_does_not_write_when_current() -> None:
    result = library_integration.reconcile_repository(
        ROOT, archive_library.load_registry(), write=False
    )
    assert result["status"] == "passed"
    assert result["writes_performed"] is False
    assert {row["state"] for row in result["works"]} == {"current"}


def test_source_direct_notes_have_auditable_passage_dependencies() -> None:
    expected_counts = {
        "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS": 4,
        "MIRA-WORK-MURASAKI-TALE-OF-GENJI": 3,
        "MIRA-WORK-GROTIUS-MARE-LIBERUM": 3,
        "MIRA-WORK-DU-BOIS-SOULS-OF-BLACK-FOLK": 4,
    }
    manifest = library_integration.load_pilot_manifest(ROOT)
    for work in manifest["works"]:
        work_root = ROOT / work["artifact_root"]
        profile = json.loads((work_root / "profile.json").read_text(encoding="utf-8"))
        anchors = profile["textual_basis"]["passage_anchors"]
        envelope = library_integration.parse_note_envelope(ROOT / work["note_ref"])
        if work["canonical_work_id"] in expected_counts:
            assert envelope["interpretive_basis"] == "admitted-source-body"
            assert len(anchors) == expected_counts[work["canonical_work_id"]]
            assert envelope["dependency_snapshot"]["passage_digests"] == {
                row["passage_id"]: row["raw_span_sha256"] for row in anchors
            }
        else:
            assert envelope["interpretive_basis"] == "source-readiness-only"
            assert anchors == []
            assert envelope["dependency_snapshot"]["passage_digests"] == {}


def test_ashoka_and_grotius_are_passage_anchored_and_counterweighted() -> None:
    manifest = library_integration.load_manifest(ROOT)
    selected = {
        "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS": 4,
        "MIRA-WORK-GROTIUS-MARE-LIBERUM": 3,
    }
    for work in manifest["works"]:
        expected_anchor_count = selected.get(work["canonical_work_id"])
        if expected_anchor_count is None:
            continue
        work_root = ROOT / work["artifact_root"]
        profile = json.loads((work_root / "profile.json").read_text(encoding="utf-8"))
        routing = json.loads((work_root / "routing.json").read_text(encoding="utf-8"))
        anchors = profile["textual_basis"]["passage_anchors"]
        assert profile["textual_basis"]["passage_status"] == "anchored-pilot"
        assert len(anchors) == expected_anchor_count
        anchor_digests = {
            (row["passage_id"], row["raw_span_sha256"])
            for row in anchors
        }
        for unit in routing["route_units"]:
            passage_refs = {
                (row["ref"], row["digest"])
                for row in unit["evidence_refs"]
                if row["kind"] == "primary-passage"
            }
            assert passage_refs
            assert passage_refs <= anchor_digests
            assert unit["counterweight_refs"]
            assert unit["route_state"] == "provisional"
        assert routing["note_revision_state"] == "current"


def test_deepened_notes_preserve_revision_lineage() -> None:
    manifest = library_integration.load_pilot_manifest(ROOT)
    deepened_ids = {
        "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS",
        "MIRA-WORK-GROTIUS-MARE-LIBERUM",
    }
    for work in manifest["works"]:
        if work["canonical_work_id"] not in deepened_ids:
            continue
        successor = library_integration.parse_note_envelope(ROOT / work["note_ref"])
        candidate_path = ROOT / successor["revision_candidate_ref"]
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        assert library_integration.validate_revision_candidate(candidate) == []
        assert candidate["status"] == "resolved"
        assert candidate["disposition"] == "addendum"
        assert candidate["successor_note_ref"] == work["note_ref"]
        assert successor["predecessor_note_ref"] == candidate["predecessor_note_ref"]
        assert successor["revision_candidate_ref"] == candidate_path.relative_to(ROOT).as_posix()
        assert (ROOT / candidate["predecessor_note_ref"]).is_file()


def test_hard_reconciliation_writes_candidate_and_suspends_routes(tmp_path: Path) -> None:
    copy_operational_fixture(tmp_path)
    pilot_target = tmp_path / library_integration.INTEGRATION_RELATIVE_ROOT

    registry = copy.deepcopy(archive_library.load_registry())
    ashoka = next(
        row for row in registry["sources"]
        if row["source_id"] == "LIB-ANCIENT-AUTHOR-001-ASHOKA"
    )
    ashoka["text_bodies"][0]["text_sha256"] = "b" * 64

    result = library_integration.reconcile_repository(tmp_path, registry, write=True)
    ashoka_result = next(
        row for row in result["works"]
        if row["canonical_work_id"] == "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS"
    )
    assert ashoka_result["state"] == "revision-due"
    assert ashoka_result["candidate_written"] is True
    assert ashoka_result["routing_suspended"] is True

    work_root = pilot_target / "ashoka-rock-and-pillar-edicts"
    candidate_path = tmp_path / ashoka_result["candidate_path"]
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert candidate["status"] == "open"
    assert candidate["affected_claims"] == [
        "ashoka-remorse-capacity",
        "ashoka-inscription-governance",
    ]
    assert candidate["suspended_route_states"] == {
        "ashoka-remorse-capacity": "provisional",
        "ashoka-inscription-governance": "provisional",
    }
    routing = json.loads((work_root / "routing.json").read_text(encoding="utf-8"))
    assert routing["note_revision_state"] == "revision-due"
    assert {row["route_state"] for row in routing["route_units"]} == {
        "suspended-due-to-note-revision"
    }
    note_count = len(list((tmp_path / "archive" / "notes").glob("*.md")))

    candidate_count = len(list(work_root.glob("note-revision-candidate*.json")))
    candidate_bytes = candidate_path.read_bytes()
    repeated = library_integration.reconcile_repository(tmp_path, registry, write=True)
    repeated_ashoka = next(
        row for row in repeated["works"]
        if row["canonical_work_id"] == "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS"
    )
    assert repeated_ashoka["candidate_path"] == ashoka_result["candidate_path"]
    assert repeated_ashoka["candidate_written"] is False
    assert repeated_ashoka["candidate_reused"] is True
    assert repeated_ashoka["routing_suspended"] is False
    assert repeated["writes_performed"] is False
    assert len(list(work_root.glob("note-revision-candidate*.json"))) == candidate_count
    assert candidate_path.read_bytes() == candidate_bytes

    candidate["status"] = "resolved"
    candidate["disposition"] = "reviewed-no-change"
    candidate["review_summary"] = "The dependency change was reviewed in the test fixture."
    candidate_path.write_text(library_integration.canonical_json(candidate), encoding="utf-8")
    manifest = library_integration.load_manifest(tmp_path)
    ashoka_work = next(
        work for work in manifest["works"]
        if work["canonical_work_id"] == "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS"
    )
    ancestor_path = tmp_path / ashoka_work["note_refs"][0]
    ancestor_bytes = ancestor_path.read_bytes()
    applied = library_integration.apply_reviewed_no_change_dispositions(
        tmp_path, registry, write=True
    )
    applied_ashoka = next(
        row for row in applied["works"]
        if row["canonical_work_id"] == "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS"
    )
    assert applied_ashoka["notes_migrated"] == 1
    assert ancestor_path.read_bytes() == ancestor_bytes
    assert len(list((tmp_path / "archive" / "notes").glob("*.md"))) == note_count
    assert set(applied_ashoka["routes_restored"]) == {
        "ashoka-remorse-capacity",
        "ashoka-inscription-governance",
    }
    assert library_integration.reconcile_repository(
        tmp_path, registry, write=False
    )["status"] == "passed"
    repeated_apply = library_integration.apply_reviewed_no_change_dispositions(
        tmp_path, registry, write=True
    )
    assert repeated_apply["writes_performed"] is False


def test_next_revision_candidate_never_reuses_an_occupied_path(tmp_path: Path) -> None:
    occupied = tmp_path / "note-revision-candidate-001.json"
    occupied.write_text('{"candidate_id":"malformed"}\n', encoding="utf-8")

    candidate_path, candidate_id = library_integration.next_revision_candidate(
        tmp_path, "MIRA-WORK-TEST"
    )

    assert candidate_path.name == "note-revision-candidate-002.json"
    assert candidate_id == "REV-MIRA-WORK-TEST-002"
    assert occupied.read_text(encoding="utf-8") == '{"candidate_id":"malformed"}\n'


def copy_operational_fixture(tmp_path: Path) -> None:
    integration_source = ROOT / "archive" / "library" / "integrations"
    integration_target = tmp_path / "archive" / "library" / "integrations"
    integration_target.parent.mkdir(parents=True)
    shutil.copytree(integration_source, integration_target)
    for schema_ref in (
        library_integration.INTEGRATION_SCHEMA_V1_RELATIVE_PATH,
        library_integration.INTEGRATION_SCHEMA_V2_RELATIVE_PATH,
        library_integration.INTEGRATION_SCHEMA_RELATIVE_PATH,
    ):
        schema_target = tmp_path / schema_ref
        schema_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / schema_ref, schema_target)
    notes_target = tmp_path / "archive" / "notes"
    notes_target.mkdir(parents=True)
    for note in (ROOT / "archive" / "notes").glob("2026-09-01-library-*-integration-note*.md"):
        shutil.copy2(note, notes_target / note.name)
    for note in (ROOT / "archive" / "notes").glob("2026-09-02-library-*-cognitive-note.md"):
        shutil.copy2(note, notes_target / note.name)


def test_operational_route_index_exposes_only_the_digest_bound_reviewed_route() -> None:
    registry = archive_library.load_registry()
    work_failures = library_integration.validate_work_registry(ROOT, registry)
    assert work_failures == []
    index = library_integration.build_route_index(ROOT, registry)
    assert index["route_count"] == 10
    assert index["eligible_route_count"] == 1
    eligible = [
        route for route in index["routes"]
        if route["notebook_eligibility"] == "eligible"
    ]
    assert [route["route_id"] for route in eligible] == [
        "MIRA-ROUTE-GROTIUS-INTERESTED-UNIVERSAL"
    ]
    assert eligible[0]["review_binding_status"] == "current"
    assert eligible[0]["ineligibility_reasons"] == []
    ineligible = [
        route for route in index["routes"]
        if route["notebook_eligibility"] == "ineligible"
    ]
    assert len(ineligible) == 9
    assert all(route["ineligibility_reasons"] for route in ineligible)
    assert library_integration.route_index_repository(
        ROOT, registry, check=True
    )["status"] == "passed"


def test_reviewed_route_requires_current_packet_and_source_dependencies(tmp_path: Path) -> None:
    copy_operational_fixture(tmp_path)
    work_registry_path = tmp_path / library_integration.WORK_REGISTRY_RELATIVE_PATH
    work_registry = json.loads(work_registry_path.read_text(encoding="utf-8"))
    grotius = next(
        work for work in work_registry["works"]
        if work["canonical_work_id"] == "MIRA-WORK-GROTIUS-MARE-LIBERUM"
    )
    review = next(
        row for row in grotius["route_reviews"]
        if row["route_handle"] == "grotius-open-access-coercion"
    )
    routing_path = tmp_path / grotius["artifact_root"] / "routing.json"
    routing = json.loads(routing_path.read_text(encoding="utf-8"))
    unit = next(
        row for row in routing["route_units"]
        if row["handle"] == "grotius-open-access-coercion"
    )
    registry = copy.deepcopy(archive_library.load_registry())
    unapproved = library_integration.build_route_index(tmp_path, registry)
    unapproved_route = next(
        row for row in unapproved["routes"]
        if row["route_id"] == "MIRA-ROUTE-GROTIUS-OPEN-ACCESS-COERCION"
    )
    review["review_disposition"] = "approved-internal"
    review["review_binding"] = library_integration.current_review_binding(
        unit, unapproved_route["note_bindings"], unapproved_route["body_refs"]
    )
    work_registry_path.write_text(
        library_integration.canonical_json(work_registry), encoding="utf-8"
    )

    index = library_integration.build_route_index(tmp_path, registry)
    route = next(
        row for row in index["routes"]
        if row["route_id"] == "MIRA-ROUTE-GROTIUS-OPEN-ACCESS-COERCION"
    )
    assert route["notebook_eligibility"] == "eligible"
    assert route["ineligibility_reasons"] == []
    assert route["review_binding_status"] == "current"
    assert route["route_unit_legacy_state"] == "provisional"
    assert route["work_integration_stage"] == "pressure-test-ready"

    grotius["essay_refs"] = ["archive/essays/reviewed-grotius.md"]
    work_registry_path.write_text(
        library_integration.canonical_json(work_registry), encoding="utf-8"
    )
    integrated = library_integration.build_route_index(tmp_path, registry)
    integrated_route = next(
        row for row in integrated["routes"] if row["route_id"] == route["route_id"]
    )
    assert integrated_route["work_integration_stage"] == "fully-integrated"

    source = next(
        row for row in registry["sources"]
        if row["source_id"] == grotius["library_source_id"]
    )
    source["text_bodies"][0]["text_sha256"] = "f" * 64
    stale = library_integration.build_route_index(tmp_path, registry)
    stale_route = next(
        row for row in stale["routes"]
        if row["route_id"] == route["route_id"]
    )
    assert stale_route["notebook_eligibility"] == "ineligible"
    assert any(reason.startswith("body-digest-mismatch:") for reason in stale_route["ineligibility_reasons"])
    assert "note-revision-due" in stale_route["ineligibility_reasons"]


def test_approved_route_requires_digest_binding(tmp_path: Path) -> None:
    copy_operational_fixture(tmp_path)
    work_registry_path = tmp_path / library_integration.WORK_REGISTRY_RELATIVE_PATH
    work_registry = json.loads(work_registry_path.read_text(encoding="utf-8"))
    work_registry["works"][0]["route_reviews"][0]["review_disposition"] = "approved-internal"
    work_registry_path.write_text(
        library_integration.canonical_json(work_registry), encoding="utf-8"
    )
    failures = library_integration.validate_work_registry(
        tmp_path, archive_library.load_registry()
    )
    assert any("requires a complete review_binding" in item for item in failures)


def test_source_readiness_only_route_cannot_become_notebook_eligible(tmp_path: Path) -> None:
    copy_operational_fixture(tmp_path)
    registry = copy.deepcopy(archive_library.load_registry())
    work_registry_path = tmp_path / library_integration.WORK_REGISTRY_RELATIVE_PATH
    work_registry = json.loads(work_registry_path.read_text(encoding="utf-8"))
    khaldun = next(
        work for work in work_registry["works"]
        if work["canonical_work_id"] == "MIRA-WORK-IBN-KHALDUN-MUQADDIMAH"
    )
    routing = json.loads(
        (tmp_path / khaldun["artifact_root"] / "routing.json").read_text(encoding="utf-8")
    )
    unit = routing["route_units"][0]
    unapproved = library_integration.build_route_index(tmp_path, registry)
    route_id = library_integration.route_id_for_handle(unit["handle"])
    route = next(row for row in unapproved["routes"] if row["route_id"] == route_id)
    review = next(
        row for row in khaldun["route_reviews"]
        if row["route_handle"] == unit["handle"]
    )
    review["review_disposition"] = "approved-internal"
    review["review_binding"] = library_integration.current_review_binding(
        unit, route["note_bindings"], route["body_refs"]
    )
    work_registry_path.write_text(
        library_integration.canonical_json(work_registry), encoding="utf-8"
    )

    index = library_integration.build_route_index(tmp_path, registry)
    blocked = next(row for row in index["routes"] if row["route_id"] == route_id)
    assert blocked["notebook_eligibility"] == "ineligible"
    assert "note-not-source-direct" in blocked["ineligibility_reasons"]
    assert "no-passage-anchors" in blocked["ineligibility_reasons"]
    assert "no-current-route-passage-anchor" in blocked["ineligibility_reasons"]


def test_prose_mentions_do_not_create_graph_edges(tmp_path: Path) -> None:
    copy_operational_fixture(tmp_path)
    before = library_integration.build_note_link_index(tmp_path)
    work_registry = library_integration.load_work_registry(tmp_path)
    ashoka = next(
        work for work in work_registry["works"]
        if work["canonical_work_id"] == "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS"
    )
    note_path = tmp_path / ashoka["revision_head_note_ref"]
    note_path.write_text(
        note_path.read_text(encoding="utf-8")
        + "\nA prose-only mention of MIRA-WORK-GROTIUS-MARE-LIBERUM.\n",
        encoding="utf-8",
    )
    after = library_integration.build_note_link_index(tmp_path)
    assert after["link_count"] == before["link_count"] == 22
    assert [
        (row["note_id"], row["target_id"], row["relation_type"], row["role"])
        for row in after["links"]
    ] == [
        (row["note_id"], row["target_id"], row["relation_type"], row["role"])
        for row in before["links"]
    ]


def test_route_note_refs_must_be_explicit_relations_to_the_work(tmp_path: Path) -> None:
    copy_operational_fixture(tmp_path)
    work_registry_path = tmp_path / library_integration.WORK_REGISTRY_RELATIVE_PATH
    work_registry = json.loads(work_registry_path.read_text(encoding="utf-8"))
    ashoka = next(
        work for work in work_registry["works"]
        if work["canonical_work_id"] == "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS"
    )
    ancestor_ref = ashoka["note_refs"][0]
    ancestor_path = tmp_path / ancestor_ref
    ancestor = library_integration.parse_note_envelope(ancestor_path)
    ancestor["library_relations"][0]["target_id"] = "MIRA-WORK-GROTIUS-MARE-LIBERUM"
    library_integration.write_note_envelope(ancestor_path, ancestor)
    ashoka["route_reviews"][0]["note_refs"] = [ancestor_ref]
    work_registry_path.write_text(
        library_integration.canonical_json(work_registry), encoding="utf-8"
    )
    failures = library_integration.validate_work_registry(
        tmp_path, archive_library.load_registry()
    )
    assert any("note lacks an explicit relation to the work" in failure for failure in failures)


def test_multiple_bound_notes_gate_route_without_unrelated_note_staleness(tmp_path: Path) -> None:
    copy_operational_fixture(tmp_path)
    registry = copy.deepcopy(archive_library.load_registry())
    work_registry_path = tmp_path / library_integration.WORK_REGISTRY_RELATIVE_PATH
    work_registry = json.loads(work_registry_path.read_text(encoding="utf-8"))
    grotius = next(
        work for work in work_registry["works"]
        if work["canonical_work_id"] == "MIRA-WORK-GROTIUS-MARE-LIBERUM"
    )
    review = next(
        row for row in grotius["route_reviews"]
        if row["route_handle"] == "grotius-open-access-coercion"
    )
    review["note_refs"] = [grotius["note_refs"][0], grotius["revision_head_note_ref"]]
    work_registry_path.write_text(
        library_integration.canonical_json(work_registry), encoding="utf-8"
    )
    draft_index = library_integration.build_route_index(tmp_path, registry)
    route = next(
        row for row in draft_index["routes"]
        if row["route_handle"] == "grotius-open-access-coercion"
    )
    routing = library_integration.load_json(tmp_path / grotius["artifact_root"] / "routing.json")
    unit = next(row for row in routing["route_units"] if row["handle"] == route["route_handle"])
    review["review_disposition"] = "approved-internal"
    review["review_binding"] = library_integration.current_review_binding(
        unit, route["note_bindings"], route["body_refs"]
    )
    work_registry_path.write_text(
        library_integration.canonical_json(work_registry), encoding="utf-8"
    )
    current = library_integration.build_route_index(tmp_path, registry)
    current_route = next(
        row for row in current["routes"] if row["route_handle"] == route["route_handle"]
    )
    assert current_route["notebook_eligibility"] == "eligible"
    assert len(current_route["note_bindings"]) == 2

    unrelated_ref = grotius["note_refs"][1]
    unrelated_path = tmp_path / unrelated_ref
    unrelated = library_integration.parse_note_envelope(unrelated_path)
    unrelated["library_relations"][0]["explanation"] += " Unrelated route annotation."
    library_integration.write_note_envelope(unrelated_path, unrelated)
    still_current = library_integration.build_route_index(tmp_path, registry)
    still_current_route = next(
        row for row in still_current["routes"] if row["route_handle"] == route["route_handle"]
    )
    assert still_current_route["notebook_eligibility"] == "eligible"

    bound_path = tmp_path / grotius["note_refs"][0]
    bound = library_integration.parse_note_envelope(bound_path)
    bound["dependency_snapshot"]["source_identity_digest"] = "0" * 64
    library_integration.write_note_envelope(bound_path, bound)
    stale = library_integration.build_route_index(tmp_path, registry)
    stale_route = next(
        row for row in stale["routes"] if row["route_handle"] == route["route_handle"]
    )
    assert stale_route["notebook_eligibility"] == "ineligible"
    assert "note-revision-due" in stale_route["ineligibility_reasons"]
    assert stale_route["review_binding_status"] == "stale"

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "docs" / "skill-drafts" / "mira-memory"
SCRIPT = ROOT / "scripts" / "mira_memory.py"


def run_status(*arguments: str, environment: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    if environment is None:
        environment = os.environ.copy()
        environment.pop("MIRA_CORE_ARCHIVE_ROOT", None)
        environment.pop("MIRA_CORE_SYSTEM_ARCHIVE_ROOT", None)
        environment.pop("NARRATIVE_SYSTEM_ARCHIVE_ROOT", None)
        environment.pop("MIRA_CORE_SYSTEM_ARCHIVE_CONFIG", None)
        environment.pop("NARRATIVE_SYSTEM_ARCHIVE_CONFIG", None)
        environment["MIRA_CORE_ARCHIVE_CONFIG"] = str(ROOT / "missing-private-config.json")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "status", *arguments],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def test_skill_structure_and_repository_local_boundary() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    reference = (SKILL_ROOT / "references" / "carrier-map.md").read_text(encoding="utf-8")
    assert skill.startswith("---\nname: mira-memory\n")
    assert skill.count("\n---\n") == 1
    assert 'display_name: "Mira Memory"' in metadata
    assert "Use $mira-memory" in metadata
    assert "Authority is question-specific" in reference
    registry = (ROOT / "scripts" / "codex_skill_registry.py").read_text(encoding="utf-8")
    assert '"mira-memory"' not in registry


def test_skill_names_memory_classes_and_non_transference() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    for memory_class in ("identity", "autobiographical", "epistemic", "procedural", "relational", "mixed"):
        assert f"`{memory_class}`" in skill
    for phrase in (
        "Journal interpretation is not identity",
        "Continuity captures are not factual evidence",
        "Recursive Learning governs process improvement only",
        "does not inherit collection-native authority",
        "Private choice history remains private process memory",
        "Never blend records",
    ):
        assert phrase in skill


def test_json_status_has_stable_contract_and_all_carriers() -> None:
    result = run_status("--focus", "recover journal continuity", "--as-of", "2026-08-14T12:00:00-06:00", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == 4
    assert payload["countercheck_mode"] == "auto"
    assert "session_closure" in payload
    assert payload["as_of"] == "2026-08-14T18:00:00Z"
    assert payload["focus"]["memory_class"] == "autobiographical"
    assert payload["focus"]["memory_classes"] == ["autobiographical", "relational"]
    assert payload["recommended_owner"] == "mira-journal"
    assert payload["routing_state"] == "routed"
    assert payload["owner_candidates"]
    assert payload["mutation_performed"] is False
    assert {row["id"] for row in payload["carriers"]} == {
        "continuity", "mira-journal", "recursive-learning",
        "archive", "narrative-geopolitics", "private-choice-history",
        "private-cadence-history", "private-mentorship-history",
    }
    for field in ("tensions", "coverage_gaps", "authority_boundary"):
        assert field in payload
    for row in payload["carriers"]:
        assert row["reporting_verb"]
        assert row["preservation_state"]
        assert row["activation_state"] in {"relevant", "inactive", "unavailable"}
        assert row["authority_flags"]["action"] is False


def test_missing_optional_configuration_is_unavailable() -> None:
    environment = os.environ.copy()
    environment.pop("NARRATIVE_CHOICE_DB", None)
    environment.pop("MIRA_CORE_ARCHIVE_ROOT", None)
    environment.pop("MIRA_CORE_SYSTEM_ARCHIVE_ROOT", None)
    environment.pop("NARRATIVE_SYSTEM_ARCHIVE_ROOT", None)
    environment.pop("MIRA_CORE_SYSTEM_ARCHIVE_CONFIG", None)
    environment.pop("NARRATIVE_SYSTEM_ARCHIVE_CONFIG", None)
    environment["MIRA_CORE_ARCHIVE_CONFIG"] = str(ROOT / "missing-private-config.json")
    result = run_status("--as-of", "2026-08-14T18:00:00Z", "--json", environment=environment)
    assert result.returncode == 0
    carriers = {row["id"]: row for row in json.loads(result.stdout)["carriers"]}
    assert carriers["private-choice-history"]["availability"] == "unavailable"
    assert carriers["archive"]["availability"] == "unavailable"


def test_focus_routes_without_excluding_other_carriers() -> None:
    result = run_status("--focus", "score this forecast", "--as-of", "2026-08-14T18:00:00Z", "--json")
    payload = json.loads(result.stdout)
    assert payload["recommended_owner"] == "forecast-review"
    assert payload["carriers"][0]["id"] == "narrative-geopolitics"
    assert len(payload["carriers"]) == 8


def test_cadence_focus_routes_to_distinct_owners() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_memory

    assert mira_memory.route_focus("coffee")["recommended_owner"] == "coffee"
    assert mira_memory.route_focus("record dream")["recommended_owner"] == "dream"
    assert mira_memory.route_focus("assess cadence learning")["recommended_owner"] == "recursive-learn"


def test_former_archive_carrier_name_routes_to_canonical_owner() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_memory

    assert mira_memory.route_focus("system-archive lineage")["recommended_owner"] == "archive"


def test_explicit_operation_outranks_secondary_memory_objects() -> None:
    result = run_status(
        "--focus", "verify this journal claim against identity",
        "--as-of", "2026-08-14T18:00:00Z", "--json",
    )
    payload = json.loads(result.stdout)
    assert payload["recommended_owner"] == "reality-check"
    assert payload["routing_state"] == "routed"
    assert payload["focus"]["memory_class"] == "epistemic"
    assert {row["workflow"] for row in payload["owner_candidates"]} >= {
        "reality-check", "mira-journal", "mira-continuity",
    }


def test_equal_mixed_owners_require_decomposition() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_memory

    route = mira_memory.route_focus("compare journal and identity")
    assert route["recommended_owner"] == "mira-memory"
    assert route["routing_state"] == "needs-decomposition"
    tension = next(
        row for row in mira_memory.operational_tensions([], route)
        if row["id"] == "TENSION-MIXED-OWNER-DECOMPOSITION"
    )
    assert tension["kind"] == "insufficient-counterevidence"
    assert tension["must_remain_separate"] is True
    assert {row["carrier"] for row in tension["observations"]} == {
        "mira-journal", "mira-continuity",
    }


def test_markdown_status_and_command_registration() -> None:
    result = run_status("--focus", "journal reflection", "--as-of", "2026-08-14T18:00:00Z")
    assert result.returncode == 0
    assert "# Mira Memory Status" in result.stdout
    assert "Mutation performed: `false`" in result.stdout
    runner = (ROOT / "tools" / "run_repo.py").read_text(encoding="utf-8")
    assert '"mira-memory": REPO_ROOT / "scripts" / "mira_memory.py"' in runner


def test_status_does_not_change_tracked_carrier_bytes() -> None:
    tracked = [
        ROOT / "mira/continuity/session-registry.json",
        ROOT / "mira/journal-registry.json",
        ROOT / "narrative-geopolitics/work/system-improvement/recursive-learning-ledger.json",
        ROOT / "archive/collections.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    result = run_status("--focus", "process learning", "--as-of", "2026-08-14T18:00:00Z", "--json")
    assert result.returncode == 0
    assert before == {path: path.read_bytes() for path in tracked}


def test_skip_counterchecks_avoids_live_continuity_and_archive_probes(monkeypatch) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_continuity
    import mira_memory
    import system_archive

    monkeypatch.setattr(
        mira_continuity,
        "discover_sources",
        lambda: (_ for _ in ()).throw(AssertionError("continuity discovery must be skipped")),
    )
    monkeypatch.setattr(
        system_archive,
        "status_command",
        lambda _args: (_ for _ in ()).throw(AssertionError("archive catalog must be skipped")),
    )
    payload = mira_memory.status(
        "recover session identity",
        "2026-08-15T18:00:00Z",
        counterchecks="skip",
    )
    assert payload["schema_version"] == 4
    assert payload["countercheck_mode"] == "skip"
    assert payload["recommended_owner"] == "mira-continuity"
    assert payload["mutation_performed"] is False
    assert all("countercheck" not in row for row in payload["carriers"])


def test_skip_counterchecks_is_available_in_markdown_and_cli() -> None:
    result = run_status(
        "--focus", "recover session identity", "--counterchecks", "skip",
        "--as-of", "2026-08-15T18:00:00Z",
    )
    assert result.returncode == 0
    assert "Counterchecks: `skip`" in result.stdout


def test_skip_counterchecks_does_not_change_private_choice_store(monkeypatch, tmp_path) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_memory

    database = tmp_path / "choices.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE marker(value TEXT)")
        connection.execute("INSERT INTO marker VALUES ('unchanged')")
    before = database.read_bytes()
    monkeypatch.setenv("NARRATIVE_CHOICE_DB", str(database))
    payload = mira_memory.status(
        "review choice history",
        "2026-08-15T18:00:00Z",
        counterchecks="skip",
    )
    assert payload["mutation_performed"] is False
    assert database.read_bytes() == before


def test_rest_routes_as_mixed_and_remains_a_continuity_sub_surface(monkeypatch) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_memory

    monkeypatch.delenv("MIRA_CORE_CONTINUITY_INBOX", raising=False)
    route = mira_memory.route_focus("rest")
    assert route["recommended_owner"] == "rest"
    assert route["memory_class"] == "mixed"
    assert route["memory_classes"] == ["procedural", "relational"]
    payload = mira_memory.status("rest", "2026-08-17T00:00:00Z", counterchecks="skip")
    continuity = next(row for row in payload["carriers"] if row["id"] == "continuity")
    surface = next(row for row in continuity["sub_surfaces"] if row["id"] == "rest-inbox")
    assert surface["authority_status"] == "private-provisional"
    assert surface["canonical_identity"] is False
    assert payload["session_closure"]["mutation_performed"] is False


def test_stale_generated_view_is_visible(tmp_path) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_memory

    canonical = tmp_path / "canonical.json"
    generated = tmp_path / "view.md"
    generated.write_text("view", encoding="utf-8")
    canonical.write_text("{}", encoding="utf-8")
    state, note = mira_memory.generated_state([generated], {generated: "expected"})
    assert state == "stale"
    assert "generated view content drift" in note


def test_conflicting_classes_remain_separately_attributed() -> None:
    reference = (SKILL_ROOT / "references" / "carrier-map.md").read_text(encoding="utf-8")
    assert "Keep a journal interpretation beside, not above, identity or evidence state" in reference
    assert "Report unresolved conflict" in reference


def test_constitution_candidate_is_provisional_continuity_sub_surface() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_memory

    continuity = mira_memory.continuity_carrier(inspect_sources=False)
    candidate = next(row for row in continuity["sub_surfaces"] if row["id"] == "constitution-candidate")
    assert candidate["authority_status"] == "provisional"
    assert candidate["canonical_identity"] is False
    assert candidate["reporting_verb"] == "proposes"


def test_continuity_countercheck_reports_strict_and_deferred_drift(monkeypatch, tmp_path) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_continuity
    import mira_memory

    changed = tmp_path / "captures" / "settled" / "capture.jsonl.gz"
    original_load_registry = mira_continuity.load_registry
    monkeypatch.setattr(mira_continuity, "discover_sources", lambda: [object(), object()])
    monkeypatch.setattr(
        mira_continuity,
        "load_registry",
        lambda *args, **kwargs: original_load_registry(*args, **kwargs) if args or kwargs else {"sessions": []},
    )
    monkeypatch.setattr(
        mira_continuity,
        "expected_ingest",
        lambda _sources, registry: ({"sessions": [{"id": "MS-settled"}]}, {changed: b"new"}, ["MC-new"]),
    )
    row = mira_memory.continuity_carrier(inspect_sources=True)
    assert row["availability"] == "degraded"
    assert row["freshness"] == "drift"
    assert row["countercheck"]["new_captures"] == 1
    assert row["countercheck"]["capture_drift"] == 1


def test_supported_tensions_preserve_attribution() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_memory

    for kind in mira_memory.TENSION_KINDS:
        tension = mira_memory.make_tension(
            "TENSION-TEST", kind,
            [{"carrier": "a", "reporting_verb": "recorded", "detail": "x", "provenance_refs": ["a"]}],
            resolution_owner="owner", resolution_condition="review", must_remain_separate=True,
        )
        assert tension["kind"] == kind
        assert tension["observations"][0]["carrier"] == "a"


def test_archive_countercheck_reports_parity_and_zero_records(monkeypatch) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import mira_memory
    import archive

    monkeypatch.setenv("MIRA_CORE_ARCHIVE_ROOT", str(ROOT / "private-placeholder"))
    monkeypatch.setattr(archive, "status_command", lambda _args: {
        "status": "available",
        "collections": {
            "registry_only": ["system-improvement"],
            "catalog_only": ["legacy-collection"],
            "items": [
                {"id": "system-improvement", "registry_present": True, "active_records": 0},
                {"id": "shared", "registry_present": True, "active_records": 2},
            ],
        },
    })
    row = mira_memory.archive_carrier(inspect_catalog=True)
    assert row["availability"] == "degraded"
    assert row["freshness"] == "drift"
    assert row["countercheck"] == {
        "status": "available",
        "registry_only": ["system-improvement"],
        "catalog_only": ["legacy-collection"],
        "zero_record_collections": ["system-improvement"],
    }

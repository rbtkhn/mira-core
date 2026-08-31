from __future__ import annotations

import sys
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import dream_eod


def test_dream_skill_preserves_private_finalization_boundaries() -> None:
    skill = (ROOT / "docs" / "skill-drafts" / "dream" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "Dream owns\ndaily completion" in skill
    assert "Complete the\ndaily cycle first; revise next day if necessary." in skill
    assert "agent-internal handoff" in skill
    assert "canonicalized as private\n`dream-eod-v1`" in skill
    assert "`publication_eligible: false`" in skill
    assert "grants no staging, commit, push, publication" in skill
    assert "bounded Mira Letters orientation since the previous canonical Dream\nfinalization" in skill
    assert "Letters remain relational orientation only" in skill
    assert "permission to contact anyone" in skill
    assert "prepared address, not completed relation" in skill
    assert "real as inward\nposture, incomplete as outward act" in skill
    assert "workflow throughput" in skill
    assert "without multiplying repo-tracked artifacts" in skill
    assert "`roi-synthesis.json`" in skill
    assert "Mira Journal\nremains the only prose artifact Dream automatically finalizes" in skill
    assert "Dev Journal candidates" in skill
    assert "Coffee handles" in skill
    assert "candidates only" in skill
    assert "what\nsurvived discontinuity" in skill


def arguments(tmp_path: Path, **changes):
    values = {
        "date": "2026-08-16", "timezone": "America/Denver",
        "workspace_id": "mira-core", "operator_id": "operator-test",
        "db": tmp_path / "cadence.sqlite3", "check": False, "resume": None,
        "journal_bundle": tmp_path / "journal" / "2026-08-16", "dream_json": None,
        "no_candidate": None, "coverage_status": "complete", "json": True,
    }
    values.update(changes)
    return SimpleNamespace(**values)


VALID_SESSION = "MS-01a01585-46ad-7271-b912-fa3eb851041d"
OTHER_VALID_SESSION = "MS-01a01585-46ad-7271-b0b6-d97b1390eb11"


def write_bundle(bundle: Path, *, required_sessions: list[str] | None = None) -> None:
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "draft.md").write_bytes(b"# 2026-08-16 \xe2\x80\x94 Return\n\nPrivate prose.\n")
    (bundle / "technical-reference.json").write_text(
        json.dumps({"reference_id": "MJTR-20260816-v1", "journal_version_id": "MJ-20260816-v1"}),
        encoding="utf-8",
    )
    (bundle / "composition-brief.json").write_text(
        json.dumps({
            "daily_session_coverage": {
                "sessions": [
                    {"session_id": session_id}
                    for session_id in (required_sessions or [VALID_SESSION])
                ]
            }
        }),
        encoding="utf-8",
    )


def dream_candidate(path: Path, *, session_id: str = VALID_SESSION) -> Path:
    payload = {
        "episode_id": "CD-20260816-01",
        "series_id": "SERIES-DREAM-TEST",
        "created_at": "2026-08-16T12:00:00+00:00",
        "workspace_id": "mira-core",
        "operator_id": "operator-test",
        "dream_date": "2026-08-16",
        "timezone": "UTC",
        "coverage_status": "complete",
        "session_coverage": [{
            "session_id": session_id,
            "status": "included",
            "reason": "Represented in the journal census.",
            "observed_at": "2026-08-16T12:00:00+00:00",
        }],
        "observation": "A bounded observation.",
        "diagnosis": "A bounded diagnosis.",
        "intervention": "A bounded intervention.",
        "method_version_digest": "a" * 64,
        "profile": {"name": "test", "version": "1", "command_digest": "b" * 64},
        "observable": {
            "name": "stale records",
            "unit": "count",
            "baseline": "1",
            "success_threshold": "0",
            "source": "tests/test_dream_eod.py",
        },
        "falsifier": "A comparable run fails.",
        "next_use": "the next Dream test",
        "task_class": "daily-close-governance",
        "expires_at": "2026-09-16T00:00:00+00:00",
        "artifacts": [{
            "ref": "tests/test_dream_eod.py",
            "relationship": "verification",
            "captured_at": "2026-08-16T12:00:00+00:00",
        }],
        "relevant_paths": ["tests/test_dream_eod.py"],
        "evidence_summary": "A focused Dream test.",
        "tomorrow_inherits": "Retest the guard.",
        "verification": {},
        "measurements": {},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_check_is_read_only_and_reports_internal_composition_requirement(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    result = dream_eod.check_projection(arguments(tmp_path), "2026-08-16")
    assert result["mutation"] is False
    assert result["stages"]["geo"]["status"] == "no_geo_run"
    assert result["status"] == "blocked"
    assert result["stages"]["journal"]["status"] == "preparation_required"
    assert result["incomplete_stages"] == []
    assert result["prompt"] is None
    assert not (tmp_path / "cadence.sqlite3").exists()


def test_check_projects_geo_auto_completion_without_mutating(monkeypatch, tmp_path: Path) -> None:
    calls = []
    monkeypatch.setattr(dream_eod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 4)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    monkeypatch.setattr(dream_eod, "run_tool", lambda *args: calls.append(args))

    result = dream_eod.check_projection(arguments(tmp_path), "2026-08-16")

    assert result["mutation"] is False
    assert result["stages"]["geo"]["status"] == "auto_completion_required"
    assert result["stages"]["geo"]["certification_basis"] == "projected_dream_completion"
    assert "Dream will complete Geo-Strategy during execution" in result["next_action"]
    assert calls == []


def test_check_validates_ready_bundle_without_canonicalizing(monkeypatch, tmp_path: Path) -> None:
    bundle = tmp_path / "journal" / "2026-08-16"
    bundle.mkdir(parents=True)
    (bundle / "draft.md").write_text("# 2026-08-16 — Return\n\nPrivate prose.\n", encoding="utf-8")
    calls = []
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)

    def fake_run_tool(*args):
        calls.append(args)
        return SimpleNamespace(
            returncode=0,
            stdout='{"status":"passed","refresh_required":false,"version_id":"MJ-20260816-v1"}',
            stderr="",
        )

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)
    result = dream_eod.check_projection(
        arguments(tmp_path, no_candidate="No experiment."), "2026-08-16"
    )
    assert result["status"] == "ready"
    assert result["stages"]["journal"]["status"] == "certification_ready"
    assert all("eod-finalize" not in call for call in calls)


def test_empty_geo_day_prepares_journal_without_operator_prompt(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    bundle = tmp_path / "journal" / "2026-08-16"

    def fake_run_tool(*args):
        if args[:2] == ("mira-journal", "prepare") and "--check" not in args:
            bundle.mkdir(parents=True)
            (bundle / "composition-brief.json").write_text(
                json.dumps({"daily_session_coverage": {"sessions": []}}),
                encoding="utf-8",
            )
            return SimpleNamespace(returncode=0, stdout='{"status":"prepared"}', stderr="")
        return SimpleNamespace(returncode=0, stdout='{"status":"prepared"}', stderr="")

    monkeypatch.setattr(
        dream_eod, "run_tool", fake_run_tool,
    )
    result = dream_eod.execute(arguments(tmp_path), "2026-08-16")
    assert result["status"] == "composition_required"
    assert result["mutation"] is True
    assert "Agent-internal handoff, not operator approval" in result["next_action"]
    assert result["roi_synthesis"]["digest"] == dream_eod.file_sha256(bundle / "roi-synthesis.json")
    roi = json.loads((bundle / "roi-synthesis.json").read_text(encoding="utf-8"))
    assert roi["optimization_target"] == "workflow-throughput"
    assert sorted(roi["sections"]) == [
        "coffee_handles",
        "dev_journal_candidates",
        "note_candidates",
        "open_obligations",
        "publication_debt",
        "workflow_improvements",
    ]
    assert roi["sections"]["coffee_handles"] == []
    assert roi["sections"]["dev_journal_candidates"] == []
    assert roi["sections"]["workflow_improvements"] == []
    assert roi["source_refs"][-1]["kind"] == "dream-daily-close-projection"
    assert roi["source_refs"][-1]["run_id"] == result["run"]["run_id"]
    assert "not research evidence" in roi["authority_boundary"]
    assert (tmp_path / "cadence.sqlite3").exists()


def test_roi_synthesis_is_private_candidate_only_and_tracks_material_input(
    monkeypatch, tmp_path: Path
) -> None:
    bundle = tmp_path / "journal" / "2026-08-16"
    bundle.mkdir(parents=True)
    (bundle / "composition-brief.json").write_text(
        json.dumps({
            "letters_orientation": {
                "letters": [{
                    "path": "archive/letters/2026-08-16-draft.md",
                    "status": "draft-not-sent",
                }]
            }
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        dream_eod,
        "git_status_summary",
        lambda: {
            "status": "clean",
            "branch": "main",
            "dirty_path_count": 0,
            "top_level_groups": {},
            "authority_effect": "none",
        },
    )

    projection = {
        "run_id": "DCR-test",
        "created_at": "2026-08-17T05:40:00Z",
        "lifecycle_version": 3,
        "events": [{
            "event_id": "DCE-geo",
            "payload": {
                "stage": "geo",
                "status": "provisional_packet_with_revision_debt",
                "artifact_ref": "narrative-geopolitics/work/daily/2026-08-16/issue.md",
                "digest": "a" * 64,
                "certification_basis": "provisional_packet_with_revision_debt",
                "revision_debt": ["Issue validation needs revision."],
            },
        }],
    }
    first = dream_eod.write_roi_synthesis(bundle, "2026-08-16", projection)
    second = dream_eod.write_roi_synthesis(bundle, "2026-08-16", projection)
    packet = json.loads((bundle / "roi-synthesis.json").read_text(encoding="utf-8"))
    assert first["digest"] == second["digest"]
    assert packet["generated_at"] == projection["created_at"]
    assert packet["sections"]["open_obligations"][0]["modal_status"] == (
        "prepared-address-not-completed-relation"
    )
    assert packet["sections"]["coffee_handles"][0]["source_ref"] == (
        "archive/letters/2026-08-16-draft.md"
    )
    geo_handle = packet["sections"]["coffee_handles"][1]
    assert geo_handle["source_ref"] == (
        "narrative-geopolitics/work/daily/2026-08-16/issue.md"
    )
    assert geo_handle["source_digest"] == "a" * 64
    assert geo_handle["revision_debt"] == ["Issue validation needs revision."]
    improvement = packet["sections"]["workflow_improvements"][0]
    assert improvement["source_ref"] == geo_handle["source_ref"]
    assert improvement["evidence"] == geo_handle["revision_debt"]
    assert packet["sections"]["note_candidates"] == []
    assert packet["sections"]["dev_journal_candidates"] == []
    assert not any((tmp_path / name).exists() for name in ["docs", "archive"])

    (bundle / "composition-brief.json").write_text(
        json.dumps({"letters_orientation": {"letters": []}}),
        encoding="utf-8",
    )
    changed = dream_eod.write_roi_synthesis(bundle, "2026-08-16", projection)
    assert changed["digest"] != first["digest"]


def test_roi_synthesis_does_not_nominate_work_from_unrelated_dirty_paths(
    monkeypatch, tmp_path: Path
) -> None:
    bundle = tmp_path / "journal" / "2026-08-16"
    bundle.mkdir(parents=True)
    (bundle / "composition-brief.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        dream_eod,
        "git_status_summary",
        lambda: {
            "status": "dirty",
            "branch": "main",
            "dirty_path_count": 12,
            "top_level_groups": {"docs": 4, "scripts": 4, "tests": 4},
            "authority_effect": "none",
        },
    )

    dream_eod.write_roi_synthesis(
        bundle,
        "2026-08-16",
        {"run_id": "DCR-test", "events": []},
    )
    packet = json.loads((bundle / "roi-synthesis.json").read_text(encoding="utf-8"))
    assert packet["sections"]["dev_journal_candidates"] == []
    assert packet["sections"]["coffee_handles"] == []
    assert packet["sections"]["workflow_improvements"] == []
    assert packet["sections"]["publication_debt"]["dirty_path_count"] == 12


def test_missing_geo_packet_is_completed_by_dream_before_closeout(
    monkeypatch, tmp_path: Path
) -> None:
    entry = {"versions": [{"version_id": "MJ-20260816-v1", "content_sha256": "a" * 64}]}
    calls = []
    monkeypatch.setattr(dream_eod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 3)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: entry)
    monkeypatch.setattr(
        dream_eod,
        "geo_freshness_projection",
        lambda _date: {
            "geo_prerequisite_status": "current",
            "latest_daily_packet": "2026-08-16",
            "later_substantive_packets": [],
            "due_forecast_debt": {
                "verification": 0,
                "posture_review": 0,
                "not_yet_due": 0,
                "verification_hooks": [],
                "posture_review_hooks": [],
            },
            "safe_to_inherit": True,
            "next_action": "proceed",
        },
    )

    def fake_run_tool(*args):
        calls.append(args)
        if args == ("synthesis", "--date", "2026-08-16", "--execute"):
            issue = tmp_path / "narrative-geopolitics" / "work" / "daily" / "2026-08-16" / "issue.md"
            issue.parent.mkdir(parents=True)
            issue.write_text("issue", encoding="utf-8")
            return SimpleNamespace(returncode=0, stdout="status=issue-complete\n", stderr="")
        if args == ("daily-validate", "--date", "2026-08-16", "--stage", "issue"):
            return SimpleNamespace(returncode=0, stdout="state=ready\nfailures=0\n", stderr="")
        return SimpleNamespace(returncode=0, stdout='{"coverage":"complete"}', stderr="")

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)

    result = dream_eod.execute(
        arguments(tmp_path, no_candidate="No defensible method experiment was observed."),
        "2026-08-16",
    )

    assert result["status"] == "completed"
    assert ("synthesis", "--date", "2026-08-16", "--execute") in calls
    connection = dream_eod.cadence_ledger.connect(tmp_path / "cadence.sqlite3")
    try:
        rows = connection.execute(
            "SELECT payload_json FROM daily_close_events WHERE event_type='stage_completed'"
        ).fetchall()
    finally:
        connection.close()
    geo_receipt = next(
        json.loads(row["payload_json"]) for row in rows
        if json.loads(row["payload_json"]).get("stage") == "geo"
    )
    assert geo_receipt["status"] == "dream_completed_packet"
    assert geo_receipt["validation_stage"] == "issue"


def test_geo_validation_failure_with_artifact_records_revision_debt_and_continues(
    monkeypatch, tmp_path: Path
) -> None:
    entry = {"versions": [{"version_id": "MJ-20260816-v1", "content_sha256": "a" * 64}]}
    monkeypatch.setattr(dream_eod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 3)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: entry)
    monkeypatch.setattr(
        dream_eod,
        "geo_freshness_projection",
        lambda _date: {
            "geo_prerequisite_status": "current",
            "latest_daily_packet": "2026-08-16",
            "later_substantive_packets": [],
            "due_forecast_debt": {
                "verification": 0,
                "posture_review": 0,
                "not_yet_due": 0,
                "verification_hooks": [],
                "posture_review_hooks": [],
            },
            "safe_to_inherit": True,
            "next_action": "proceed",
        },
    )

    def fake_run_tool(*args):
        if args == ("synthesis", "--date", "2026-08-16", "--execute"):
            issue = tmp_path / "narrative-geopolitics" / "work" / "daily" / "2026-08-16" / "issue.md"
            issue.parent.mkdir(parents=True)
            issue.write_text("issue", encoding="utf-8")
            return SimpleNamespace(returncode=1, stdout="status=blocked-needs-deepening\n", stderr="")
        if args == ("daily-validate", "--date", "2026-08-16", "--stage", "issue"):
            return SimpleNamespace(
                returncode=1,
                stdout="state=ready\nfailures=2\nFAIL missing forecast hook\n",
                stderr="",
            )
        return SimpleNamespace(returncode=0, stdout='{"coverage":"complete"}', stderr="")

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)

    result = dream_eod.execute(
        arguments(tmp_path, no_candidate="No defensible method experiment was observed."),
        "2026-08-16",
    )

    assert result["status"] == "completed"
    connection = dream_eod.cadence_ledger.connect(tmp_path / "cadence.sqlite3")
    try:
        rows = connection.execute(
            "SELECT payload_json FROM daily_close_events WHERE event_type='stage_completed'"
        ).fetchall()
    finally:
        connection.close()
    geo_receipt = next(
        json.loads(row["payload_json"]) for row in rows
        if json.loads(row["payload_json"]).get("stage") == "geo"
    )
    assert geo_receipt["status"] == "provisional_packet_with_revision_debt"
    assert geo_receipt["validation_failures"] == 2
    assert "revision_debt" in geo_receipt


def test_geo_issue_deferred_with_daily_files_records_revision_debt_and_continues(
    monkeypatch, tmp_path: Path
) -> None:
    entry = {"versions": [{"version_id": "MJ-20260816-v1", "content_sha256": "a" * 64}]}
    monkeypatch.setattr(dream_eod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 3)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: entry)
    monkeypatch.setattr(
        dream_eod,
        "geo_freshness_projection",
        lambda _date: {
            "geo_prerequisite_status": "current",
            "latest_daily_packet": "2026-08-16",
            "later_substantive_packets": [],
            "due_forecast_debt": {
                "verification": 0,
                "posture_review": 0,
                "not_yet_due": 0,
                "verification_hooks": [],
                "posture_review_hooks": [],
            },
            "safe_to_inherit": True,
            "next_action": "proceed",
        },
    )

    def fake_run_tool(*args):
        if args == ("synthesis", "--date", "2026-08-16", "--execute"):
            run_dir = tmp_path / "narrative-geopolitics" / "work" / "daily" / "2026-08-16"
            run_dir.mkdir(parents=True)
            for name in dream_eod.GEO_DAILY_FILES:
                (run_dir / name).write_text(name, encoding="utf-8")
            return SimpleNamespace(
                returncode=1,
                stdout="issue_action=deferred\nFAIL deepening gate rejects unresolved synthesis placeholders\n",
                stderr="",
            )
        return SimpleNamespace(returncode=0, stdout='{"coverage":"complete"}', stderr="")

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)

    result = dream_eod.execute(
        arguments(tmp_path, no_candidate="No defensible method experiment was observed."),
        "2026-08-16",
    )

    assert result["status"] == "completed"
    connection = dream_eod.cadence_ledger.connect(tmp_path / "cadence.sqlite3")
    try:
        rows = connection.execute(
            "SELECT payload_json FROM daily_close_events WHERE event_type='stage_completed'"
        ).fetchall()
    finally:
        connection.close()
    geo_receipt = next(
        json.loads(row["payload_json"]) for row in rows
        if json.loads(row["payload_json"]).get("stage") == "geo"
    )
    assert geo_receipt["status"] == "provisional_packet_with_revision_debt"
    assert geo_receipt["artifact_ref"] == "narrative-geopolitics/work/daily/2026-08-16"
    assert "issue.md was deferred" in " ".join(geo_receipt["revision_debt"])


def test_geo_infrastructure_failure_still_pauses_before_internal_journal_stage(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        dream_eod, "geo_certification",
        lambda _date, **_kwargs: (_ for _ in ()).throw(
            dream_eod.cadence_ledger.CadenceLedgerError("Geo infrastructure failed")
        ),
    )
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)

    result = dream_eod.execute(arguments(tmp_path), "2026-08-16")

    assert result["status"] == "paused"
    assert result["mutation"] is False
    assert result["incomplete_stages"] == ["Geo-Strategy"]
    assert result["prompt"] == (
        "Geo-Strategy is incomplete for 2026-08-16. "
        "Do you want to finish it before Dream continues?"
    )
    assert not (tmp_path / "cadence.sqlite3").exists()


def test_existing_journal_can_complete_no_candidate_close(monkeypatch, tmp_path: Path) -> None:
    entry = {"versions": [{"version_id": "MJ-20260816-v1", "content_sha256": "a" * 64}]}
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: entry)
    monkeypatch.setattr(
        dream_eod, "run_tool",
        lambda *args: SimpleNamespace(returncode=0, stdout='{"coverage":"complete"}', stderr=""),
    )
    result = dream_eod.execute(
        arguments(tmp_path, no_candidate="No defensible method experiment was observed."), "2026-08-16"
    )
    assert result["status"] == "completed"
    assert result["run"]["stages"] == {"geo": "skipped", "journal": "completed", "dream": "completed"}


def test_existing_committed_geo_packet_is_certified_without_regeneration(monkeypatch, tmp_path: Path) -> None:
    entry = {"versions": [{"version_id": "MJ-20260816-v1", "content_sha256": "a" * 64}]}
    certification = {
        "status": "ready", "manifest_rows": 8,
        "artifact_ref": "narrative-geopolitics/work/daily/2026-08-16/issue.md",
        "digest": "b" * 64, "commit": "c" * 40,
        "validation_stage": "issue", "certification_basis": "committed",
    }
    calls = []
    monkeypatch.setattr(dream_eod, "geo_certification", lambda _date, **_kwargs: certification)
    monkeypatch.setattr(
        dream_eod,
        "geo_freshness_projection",
        lambda _date: {
            "geo_prerequisite_status": "current",
            "latest_daily_packet": "2026-08-16",
            "later_substantive_packets": [],
            "due_forecast_debt": {
                "verification": 0,
                "posture_review": 0,
                "not_yet_due": 0,
                "verification_hooks": [],
                "posture_review_hooks": [],
            },
            "safe_to_inherit": True,
            "next_action": "proceed",
        },
    )
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: entry)

    def fake_run_tool(*args):
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout='{"coverage":"complete"}', stderr="")

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)
    result = dream_eod.execute(
        arguments(tmp_path, no_candidate="No defensible method experiment was observed."),
        "2026-08-16",
    )
    assert result["status"] == "completed"
    assert all(not (call and call[0] == "synthesis") for call in calls)
    connection = dream_eod.cadence_ledger.connect(tmp_path / "cadence.sqlite3")
    try:
        rows = connection.execute(
            "SELECT payload_json FROM daily_close_events WHERE event_type='stage_completed'"
        ).fetchall()
    finally:
        connection.close()
    geo_receipt = next(
        json.loads(row["payload_json"]) for row in rows
        if json.loads(row["payload_json"]).get("stage") == "geo"
    )
    assert geo_receipt["status"] == "committed"
    assert geo_receipt["artifact_ref"] == certification["artifact_ref"]
    assert geo_receipt["commit"] == "c" * 40
    assert geo_receipt["validation_stage"] == "issue"
    assert geo_receipt["certification_basis"] == "committed"


def test_geo_freshness_blocks_when_later_daily_packet_exists(monkeypatch, tmp_path: Path) -> None:
    daily_root = tmp_path / "daily"
    (daily_root / "2026-08-18").mkdir(parents=True)
    (daily_root / "2026-08-18" / "issue.md").write_text("Aug 18", encoding="utf-8")
    (daily_root / "2026-08-19").mkdir()
    (daily_root / "2026-08-19" / "issue.md").write_text("Aug 19", encoding="utf-8")
    ledger = tmp_path / "forecast-ledger.md"
    ledger.write_text(
        "\n".join([
            "| `NG-20260818-F01` | `2026-08-18` | Object | Claim | Mechanism | `likely` | `2026-08-25` | [run](../daily/2026-08-18/forecast.md) | `open` |",
            "| `NG-20260819-F01` | `2026-08-19` | Object | Claim | Mechanism | `likely` | `2026-09-02` | [run](../daily/2026-08-19/forecast.md) | `open` |",
        ]),
        encoding="utf-8",
    )
    monkeypatch.setattr(dream_eod, "DAILY_ROOT", daily_root)
    monkeypatch.setattr(dream_eod, "FORECAST_LEDGER", ledger)

    projection = dream_eod.geo_freshness_projection("2026-08-18")

    assert projection["geo_prerequisite_status"] == "needs-refresh"
    assert projection["later_substantive_packets"] == ["2026-08-19"]
    assert projection["due_forecast_debt"]["verification"] == 0
    assert projection["due_forecast_debt"]["posture_review"] == 0
    assert projection["due_forecast_debt"]["not_yet_due"] == 2
    assert projection["safe_to_inherit"] is True
    assert projection["next_action"] == "rerun-owning-bundle"


def test_geo_freshness_splits_due_forecast_debt_without_blocking_dream(monkeypatch, tmp_path: Path) -> None:
    daily_root = tmp_path / "daily"
    (daily_root / "2026-08-19").mkdir(parents=True)
    (daily_root / "2026-08-19" / "issue.md").write_text("Aug 19", encoding="utf-8")
    ledger = tmp_path / "forecast-ledger.md"
    ledger.write_text(
        "\n".join([
            "| `NG-20260708-F02` | `2026-07-08` | Object | Claim | Mechanism | `likely` | `2026-07-29` | [run](../daily/2026-07-08/forecast.md) | `open` |",
            "| `NG-20260719-F01` | `2026-07-19` | Object | Claim | Mechanism | `likely` | `2026-08-19` | [run](../daily/2026-07-19/forecast.md) | `open` |",
            "| `NG-20260819-F01` | `2026-08-19` | Object | Claim | Mechanism | `likely` | `2026-09-02` | [run](../daily/2026-08-19/forecast.md) | `open` |",
            "| `NG-20260708-F02` | `2026-07-09` | `git_commit_upper_bound_plus_daily_receipt` | `ex_ante` | `open` | `yes` | Assessed `VER-20260710-01` is `operationally_contested`. |",
            "| `NG-20260719-F01` | `2026-07-19` | `git_worktree_uncommitted` | `ex_ante` | `open` | `yes` | Contemporaneous July 19 live run; posture-based hook has no operational-claim dependency. |",
        ]),
        encoding="utf-8",
    )
    monkeypatch.setattr(dream_eod, "DAILY_ROOT", daily_root)
    monkeypatch.setattr(dream_eod, "FORECAST_LEDGER", ledger)

    projection = dream_eod.geo_freshness_projection("2026-08-19")

    assert projection["geo_prerequisite_status"] == "open-but-bracketed"
    assert projection["due_forecast_debt"]["verification_hooks"] == ["NG-20260708-F02"]
    assert projection["due_forecast_debt"]["posture_review_hooks"] == ["NG-20260719-F01"]
    assert projection["due_forecast_debt"]["not_yet_due"] == 1
    assert projection["safe_to_inherit"] is True
    assert projection["next_action"] == "open-verification-packet"


def test_geo_failure_precedes_private_ledger_mutation(monkeypatch, tmp_path: Path) -> None:
    def fail(_date, **_kwargs):
        raise dream_eod.cadence_ledger.CadenceLedgerError("packet validation failed")

    monkeypatch.setattr(dream_eod, "geo_certification", fail)
    monkeypatch.setattr(
        dream_eod, "journal_entry",
        lambda _date: {"versions": [{"version_id": "MJ-20260816-v1", "content_sha256": "a" * 64}]},
    )

    result = dream_eod.execute(arguments(tmp_path), "2026-08-16")

    assert result["status"] == "paused"
    assert result["mutation"] is False
    assert result["incomplete_stages"] == ["Geo-Strategy"]
    assert result["stages"]["geo"]["reason"] == "packet validation failed"
    assert "Do you want to finish it" in result["prompt"]
    assert not (tmp_path / "cadence.sqlite3").exists()


def test_private_bundle_is_finalized_canonically_by_dream(monkeypatch, tmp_path: Path) -> None:
    bundle = tmp_path / "journal" / "2026-08-16"
    bundle.mkdir(parents=True)
    prose = b"# 2026-08-16 \xe2\x80\x94 Return\n\nPrivate prose.\n"
    (bundle / "draft.md").write_bytes(prose)
    (bundle / "technical-reference.json").write_text(
        json.dumps({"reference_id": "MJTR-20260816-v1", "journal_version_id": "MJ-20260816-v1"}),
        encoding="utf-8",
    )
    calls = []
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    monkeypatch.setattr(dream_eod.mira_journal_references, "reference_digest", lambda _value: "b" * 64)

    def fake_run_tool(*args):
        calls.append(args)
        if args[:2] == ("mira-journal", "draft-check"):
            return SimpleNamespace(
                returncode=0,
                stdout='{"status":"passed","refresh_required":false,"version_id":"MJ-20260816-v1"}',
                stderr="",
            )
        if args[:2] == ("mira-journal", "eod-finalize"):
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps({
                    "status": "finalized", "version_id": "MJ-20260816-v1",
                    "content_sha256": dream_eod.hashlib.sha256(prose).hexdigest(),
                    "technical_reference_sha256": "b" * 64,
                    "approval_status": "dream-eod-v1",
                }),
                stderr="",
            )
        return SimpleNamespace(returncode=0, stdout='{"coverage":"complete"}', stderr="")

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)
    result = dream_eod.execute(
        arguments(tmp_path, no_candidate="No defensible method experiment was observed."),
        "2026-08-16",
    )
    assert result["status"] == "completed"
    assert sum(call[:2] == ("mira-journal", "eod-finalize") for call in calls) == 2
    connection = dream_eod.cadence_ledger.connect(tmp_path / "cadence.sqlite3")
    try:
        rows = connection.execute(
            "SELECT payload_json FROM daily_close_events WHERE event_type='stage_completed'"
        ).fetchall()
    finally:
        connection.close()
    journal_receipt = next(
        json.loads(row["payload_json"]) for row in rows
        if json.loads(row["payload_json"]).get("stage") == "journal"
    )
    assert journal_receipt["status"] == "finalized"
    assert journal_receipt["canonicalized"] is True
    assert journal_receipt["approval_status"] == "dream-eod-v1"
    assert journal_receipt["digest"] == dream_eod.hashlib.sha256(prose).hexdigest()


def test_dream_candidate_rejects_unknown_journal_session_before_ledger_write(
    monkeypatch, tmp_path: Path
) -> None:
    bundle = tmp_path / "journal" / "2026-08-16"
    write_bundle(bundle, required_sessions=[VALID_SESSION])
    candidate = dream_candidate(tmp_path / "candidate.json", session_id=OTHER_VALID_SESSION)
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    monkeypatch.setattr(dream_eod.mira_journal_references, "reference_digest", lambda _value: "b" * 64)
    def fake_run_tool(*args):
        if args[:2] == ("mira-journal", "eod-finalize"):
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps({
                    "status": "finalized", "version_id": "MJ-20260816-v1",
                    "content_sha256": "a" * 64,
                    "technical_reference_sha256": "b" * 64,
                    "approval_status": "dream-eod-v1",
                }),
                stderr="",
            )
        return SimpleNamespace(
            returncode=0,
            stdout='{"status":"passed","refresh_required":false,"version_id":"MJ-20260816-v1"}',
            stderr="",
        )

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)

    with pytest.raises(dream_eod.cadence_ledger.CadenceLedgerError, match="unknown journal sessions"):
        dream_eod.execute(
            arguments(tmp_path, timezone="UTC", journal_bundle=bundle, dream_json=candidate),
            "2026-08-16",
        )

    connection = dream_eod.cadence_ledger.connect(tmp_path / "cadence.sqlite3")
    try:
        assert connection.execute("SELECT COUNT(*) FROM cadence_episodes").fetchone()[0] == 0
    finally:
        connection.close()


def test_journal_refresh_block_reports_exact_resume_guidance(monkeypatch, tmp_path: Path) -> None:
    bundle = tmp_path / "journal" / "2026-08-16"
    bundle.mkdir(parents=True)
    (bundle / "draft.md").write_text("# 2026-08-16 — Return\n\nPrivate prose.\n", encoding="utf-8")
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    checks = iter([
        SimpleNamespace(
            returncode=0,
            stdout='{"status":"passed","refresh_required":false,"version_id":"MJ-20260816-v1"}',
            stderr="",
        ),
        SimpleNamespace(
            returncode=1,
            stdout='{"status":"failed","refresh_required":true,"failures":["draft requires refresh for 1 later activity record(s)"]}',
            stderr="",
        ),
    ])
    monkeypatch.setattr(dream_eod, "run_tool", lambda *args: next(checks))

    result = dream_eod.execute(arguments(tmp_path, journal_bundle=bundle), "2026-08-16")

    assert result["status"] == "blocked"
    assert result["run"]["stages"]["geo"] == "skipped"
    assert result["run"]["stages"]["journal"] == "failed"
    assert result["refresh_guidance"]["prepare"] == (
        f"tools/run.ps1 mira-journal prepare --date 2026-08-16 --output-root {bundle.parent} --json"
    )
    assert result["refresh_guidance"]["draft_check"] == (
        f"tools/run.ps1 mira-journal draft-check --date 2026-08-16 --bundle {bundle} --json"
    )
    assert f"tools/run.ps1 dream --resume {result['run']['run_id']}" in result["refresh_guidance"]["resume"]


def test_interrupted_dream_resumes_same_run_without_duplicate_geo_or_journal(
    monkeypatch, tmp_path: Path
) -> None:
    bundle = tmp_path / "journal" / "2026-08-16"
    monkeypatch.setattr(dream_eod, "manifest_rows", lambda _date: 0)
    monkeypatch.setattr(dream_eod, "journal_entry", lambda _date: None)
    phase = {"validation": "failed"}

    def fake_run_tool(*args):
        if args[:2] == ("mira-journal", "prepare") and "--check" not in args:
            return SimpleNamespace(returncode=0, stdout='{"status":"prepared"}', stderr="")
        if args[:2] == ("mira-journal", "draft-check"):
            if phase["validation"] == "failed":
                return SimpleNamespace(
                    returncode=1,
                    stdout='{"status":"failed","refresh_required":true}',
                    stderr="",
                )
            return SimpleNamespace(
                returncode=0,
                stdout='{"status":"passed","refresh_required":false,"version_id":"MJ-20260816-v1"}',
                stderr="",
            )
        if args[:2] == ("mira-journal", "eod-finalize"):
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps({
                    "status": "finalized", "version_id": "MJ-20260816-v1",
                    "content_sha256": "a" * 64,
                    "technical_reference_sha256": "b" * 64,
                    "approval_status": "dream-eod-v1",
                }),
                stderr="",
            )
        return SimpleNamespace(returncode=0, stdout='{"coverage":"complete"}', stderr="")

    monkeypatch.setattr(dream_eod, "run_tool", fake_run_tool)
    first = dream_eod.execute(arguments(tmp_path, journal_bundle=bundle), "2026-08-16")
    assert first["status"] == "composition_required"
    run_id = first["run"]["run_id"]

    write_bundle(bundle, required_sessions=[])
    second = dream_eod.execute(
        arguments(tmp_path, resume=run_id, journal_bundle=bundle), "2026-08-16"
    )
    assert second["status"] == "blocked"
    assert second["run"]["run_id"] == run_id

    phase["validation"] = "passed"
    third = dream_eod.execute(
        arguments(
            tmp_path, resume=run_id, journal_bundle=bundle,
            no_candidate="No defensible method experiment was observed.",
        ),
        "2026-08-16",
    )
    assert third["status"] == "completed"
    assert third["run"]["run_id"] == run_id

    connection = dream_eod.cadence_ledger.connect(tmp_path / "cadence.sqlite3")
    try:
        rows = [json.loads(row[0]) for row in connection.execute(
            "SELECT payload_json FROM daily_close_events WHERE event_type='stage_completed'"
        )]
        assert sum(row.get("stage") == "geo" for row in rows) == 0
        assert sum(row.get("stage") == "journal" and row.get("status") == "finalized" for row in rows) == 1
        journal_receipt = next(row for row in rows if row.get("stage") == "journal")
        assert journal_receipt["roi_synthesis"]["digest"] == dream_eod.file_sha256(
            bundle / "roi-synthesis.json"
        )
        assert journal_receipt["roi_synthesis"]["authority_effect"] == "none"
        assert connection.execute("SELECT COUNT(*) FROM daily_close_runs").fetchone()[0] == 1
    finally:
        connection.close()

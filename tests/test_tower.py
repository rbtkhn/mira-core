import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import tower
import strategy_notebook as notebook
import dream_eod as dream
import cadence_ledger


def put(root, name, content):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    put(root, "archive/sources/geopolitics/source-manifest.json", '{"sources": []}')
    put(root, "archive/sources/youtube-channel-routing.yml", "channels:\n  - archive_lane: singularity\n    target_pattern: archive/sources/singularity/test-capture-targets-{date}.md\n")
    (root / "geopolitics/work/capture/youtube").mkdir(parents=True)
    (root / "archive/sources/singularity/test/transcripts").mkdir(parents=True)
    return root


def queue(repo, key="abcdefghijk", status="available"):
    return put(repo, "geopolitics/work/capture/youtube/2026-09-12.jsonl", json.dumps({
        "url": "https://www.youtube.com/watch?v=" + key, "source_identity": "youtube:" + key,
        "date": "2026-09-12", "transcript_status": status, "disposition": "must-land"}) + "\n")


def land(repo, key="abcdefghijk", text="source evidence"):
    rel = "archive/sources/geopolitics/sources/test.md"
    put(repo, rel, text)
    put(repo, "archive/sources/geopolitics/source-manifest.json", json.dumps({"sources": [{
        "local_path": rel, "source_url": "https://www.youtube.com/watch?v=" + key, "date": "2026-09-12"}]}))


def entry(identifier="session-one", **changes):
    return {"contribution_id": identifier, "session_id": "test-session", "date": "2026-09-12",
            "closed_at": "2026-09-12T15:00:00+00:00", "question": "How does intelligence alter power?",
            "assessment": "A qualified judgment; concentration remains uncertain.", "delta": "New constraint identified.",
            "return_point": "Test the concentration mechanism against decentralization.", **changes}


def test_two_readers_landing_revision_and_baseline(repo, tmp_path):
    queue(repo)
    put(repo, "archive/sources/singularity/test-capture-targets-2026-09-12.md",
        "| Video URL | Title | Publication date | Channel | Observed date | Absence check | Next eligible workflow |\n"
        "| https://www.youtube.com/watch?v=lmnopqrstuv | AI | 2026-09-12 | Test | 2026-09-12 | absent | intake |\n")
    state = tmp_path / "state"
    tower.initialize(repo, state)
    pending = tower.pending("2026-09-12", repo, state)
    assert pending["counts"] == {"intake-pending": 1, "acquisition-pending": 1}
    land(repo)
    pending = tower.pending("2026-09-12", repo, state)
    assert len(pending["pending"]) == 2
    source = next(row for row in pending["pending"] if row["kind"] == "analysis-pending")
    disposition = {**source, "status": "considered", "reason": "Read and assessed; no verified-fact promotion."}
    result = tower.close(entry(source_dispositions=[disposition]), repo)
    assert result["status"] == "saved"
    assert tower.pending("2026-09-12", repo, state)["counts"] == {"acquisition-pending": 1}
    land(repo, text="Revised source evidence")
    assert tower.pending("2026-09-12", repo, state)["counts"]["analysis-pending"] == 1


def test_initial_historical_sources_not_called_processed(repo, tmp_path):
    land(repo)
    state = tmp_path / "state"
    baseline = tower.initialize(repo, state)
    assert baseline["baseline"]
    assert tower.pending("2026-09-12", repo, state)["status"] == "clear"
    assert tower.pending("2026-09-12", repo, state, catch_up=True)["counts"] == {"analysis-pending": 1}


def test_read_only_missing_activation_and_bad_reader(repo, tmp_path):
    state = tmp_path / "state"
    assert tower.pending("2026-09-12", repo, state)["status"] == "unknown"
    assert not state.exists()
    queue(repo, status="defer")
    tower.initialize(repo, state)
    assert tower.pending("2026-09-12", repo, state)["counts"] == {"acquisition-pending": 1}
    put(repo, "geopolitics/work/capture/youtube/broken.jsonl", "invalid")
    assert tower.pending("2026-09-12", repo, state)["status"] == "unknown"


def test_validation_idempotence_corrections_and_context(repo):
    first = entry()
    assert tower.close(first, repo, check=True)["status"] == "validated"
    assert not tower.contributions(repo)
    saved = tower.close(first, repo)
    assert tower.close(first, repo)["status"] == "reused"
    with pytest.raises(ValueError, match="different content"):
        tower.close(entry(assessment="changed"), repo)
    tower.close(entry("session-two", closed_at="2026-09-12T16:00:00+00:00", correction_links=[saved["path"]], assessment="Correction: concentration is less certain."), repo)
    context = tower.context("2026-09-12", repo=repo)
    assert len(context["contributions"]) == 2
    assert "latest recorded" in context["focus_basis"]
    assert context["contributions"][1]["correction_links"] == [saved["path"]]
    assert notebook.read_entry("2026-09-12", repo)["locator"] == "session-two"
    assert notebook.context("2026-09-12", "intelligence", repo, limit=1)["omitted"]


def test_disposition_only_and_unlanded_considered_rejected(repo, tmp_path):
    queue(repo)
    state = tmp_path / "state"
    tower.initialize(repo, state)
    row = tower.pending("2026-09-12", repo, state)["pending"][0]
    with pytest.raises(ValueError, match="Unlanded"):
        tower.close(entry(source_dispositions=[{**row, "status": "considered", "reason": "incorrect"}]), repo)
    tower.close(entry(disposition_only=True, source_dispositions=[{**row, "status": "deferred", "reason": "Operator parked this version."}]), repo)
    assert tower.pending("2026-09-12", repo, state)["status"] == "clear"
    assert notebook.read_entry("2026-09-12", repo) is None


def test_dream_gate_both_choices_and_changed_batch(repo, tmp_path, monkeypatch):
    state = tmp_path / "state"
    queue(repo)
    tower.initialize(repo, state)
    monkeypatch.setattr(dream, "REPO_ROOT", repo)
    args = SimpleNamespace(tower_state_root=state, tower_choice=None, tower_batch=None)
    connection = cadence_ledger.connect(tmp_path / "cadence.sqlite3")
    try:
        run = cadence_ledger.open_daily_close(connection, run_id="DCR-20260912-test", workspace_id="test", operator_id="test",
            close_date="2026-09-12", timezone_name="America/New_York", idempotency_key="test")
        run, gate = dream.tower_preflight(connection, run, args, "2026-09-12")
        assert gate["status"] == "tower_choice_required"
        args.tower_batch = gate["tower_pending"]["batch_sha256"]
        args.tower_choice = "tower"
        run, gate = dream.tower_preflight(connection, run, args, "2026-09-12")
        assert gate["status"] == "tower_required"
        args.tower_choice = "continue"
        run, gate = dream.tower_preflight(connection, run, args, "2026-09-12")
        assert gate is None
        args.tower_choice = None
        run, gate = dream.tower_preflight(connection, run, args, "2026-09-12")
        assert gate is None
        land(repo)
        run, gate = dream.tower_preflight(connection, run, args, "2026-09-12")
        assert gate["status"] == "tower_choice_required"
    finally:
        connection.close()


def test_dream_never_generates_geo(repo, monkeypatch):
    monkeypatch.setattr(dream, "REPO_ROOT", repo)
    monkeypatch.setattr(dream, "manifest_rows", lambda day: 1)
    monkeypatch.setattr(dream, "run_tool", lambda *args: pytest.fail("No tool execution for missing Geo packet"))
    assert dream.geo_certification("2026-09-12", auto_complete=True)["status"] == "unfinished"


def test_end_to_end_tower_dream_and_completed_replay(repo, tmp_path, monkeypatch):
    from test_dream_eod import arguments
    queue(repo)
    state = tmp_path / "state"
    tower.initialize(repo, state)
    monkeypatch.setattr(dream, "REPO_ROOT", repo)
    monkeypatch.setattr(dream, "journal_entry", lambda _: {"versions": [{"version_id": "MJ-test-v1", "content_sha256": "a" * 64}]})
    monkeypatch.setattr(dream, "forecast_review_step", lambda *a, **k: {"status": "no_due_hooks"}, raising=False)
    monkeypatch.setattr(dream, "manifest_rows", lambda _: 0)
    monkeypatch.setattr(dream, "run_tool", lambda *a: SimpleNamespace(returncode=0, stdout="{}", stderr=""))
    args = arguments(tmp_path, date="2026-09-12", timezone="America/New_York", tower_state_root=state, no_candidate="No process experiment.")
    gate = dream.execute(args, args.date)
    assert gate["status"] == "tower_choice_required"
    args.resume = gate["run"]["run_id"]
    args.tower_choice = "tower"
    args.tower_batch = gate["tower_pending"]["batch_sha256"]
    assert dream.execute(args, args.date)["status"] == "tower_required"
    land(repo)
    row = tower.pending(args.date, repo, state)["pending"][0]
    payload = entry(source_dispositions=[{**row, "status": "considered", "reason": "Assessed against rival mechanism."}])
    tower.close(payload, repo, check=True)
    saved = tower.close(payload, repo)
    args.tower_choice = None
    done = dream.execute(args, args.date)
    assert done["status"] == "completed"
    assert done["cognitive_disposition"]["notebook"]["status"] == "present"
    assert saved["path"] == tower.context(args.date, repo=repo)["contributions"][0]["path"]
    monkeypatch.setattr(dream, "tower_pending", lambda *a: pytest.fail("Completed replay must not inspect Tower"))
    monkeypatch.setattr(dream, "prerequisite_projection", lambda *a, **k: pytest.fail("Completed replay must not revalidate Geo"))
    assert dream.execute(args, args.date)["mutation"] is False
    assert dream.check_projection(args, args.date)["status"] == "completed"


def test_continue_leaves_sources_untouched(repo, tmp_path, monkeypatch):
    from test_dream_eod import arguments
    queue_path = queue(repo)
    state = tmp_path / "state"
    tower.initialize(repo, state)
    original = queue_path.read_bytes()
    monkeypatch.setattr(dream, "REPO_ROOT", repo)
    monkeypatch.setattr(dream, "manifest_rows", lambda _: 2)
    monkeypatch.setattr(dream, "journal_entry", lambda _: {"versions": [{"version_id": "MJ-test-v1", "content_sha256": "a" * 64}]})
    monkeypatch.setattr(dream, "forecast_review_step", lambda *a, **k: {"status": "no_due_hooks"}, raising=False)
    monkeypatch.setattr(dream, "run_tool", lambda *a: SimpleNamespace(returncode=0, stdout="{}", stderr=""))
    batch = tower.pending("2026-09-12", repo, state)
    args = arguments(tmp_path, date="2026-09-12", timezone="America/New_York", tower_state_root=state,
                     tower_choice="continue", tower_batch=batch["batch_sha256"], no_candidate="No experiment.")
    done = dream.execute(args, args.date)
    assert done["status"] == "completed"
    assert done["tower_pending"]["pending"]
    assert not tower.contributions(repo)
    assert queue_path.read_bytes() == original


def test_close_retry_survives_later_source_change(repo, tmp_path):
    queue(repo)
    state = tmp_path / "state"
    tower.initialize(repo, state)
    land(repo)
    row = tower.pending("2026-09-12", repo, state)["pending"][0]
    payload = entry(source_dispositions=[{**row, "status": "considered", "reason": "Read this version."}])
    tower.close(payload, repo)
    land(repo, text="changed")
    assert tower.close(payload, repo)["status"] == "reused"


def test_late_source_not_claimed_available_at_cutoff(repo, tmp_path):
    import os
    from datetime import datetime, timezone
    state = tmp_path / "state"
    tower.initialize(repo, state)
    land(repo)
    path = repo / "archive/sources/geopolitics/sources/test.md"
    later = datetime(2026, 9, 14, tzinfo=timezone.utc).timestamp()
    os.utime(path, (later, later))
    assert tower.pending("2026-09-12", repo, state)["pending"] == []


def test_historical_target_formats_are_read_without_rewriting(repo):
    path = put(repo, "archive/sources/singularity/test-capture-targets-2026-09-02.md",
        "| visible_age | title | url | target_status | next_action |\n"
        "|---|---|---|---|---|\n"
        "| 3 weeks | A title | `https://www.youtube.com/watch?v=abcdefghijk` | transcript missing | intake |\n")
    before = path.read_bytes()
    assert tower.read_targets(path)[0]["source_identity"] == "youtube:abcdefghijk"
    assert path.read_bytes() == before
    put(repo, path.relative_to(repo).as_posix(),
        "| Video URL | Title | Publication date | Channel | Observed date | Absence check | Next eligible workflow |\n"
        "| https://www.youtube.com/watch?v=abcdefghijk | Title \\| episode | 2026-09-02 | channel | 2026-09-02 | absent | intake |\n")
    assert tower.read_targets(path)[0]["title"] == "Title | episode"


def test_note_proposals_recur_without_editing_target(repo):
    from test_cognitive_context import candidate
    proposal = candidate(repo)
    target = repo / proposal["target_path"]
    original = target.read_bytes()
    tower.close(entry(note_proposals=[proposal]), repo)
    recovered = tower.context("2026-09-12", repo=repo)["contributions"][0]["note_proposals"]
    assert recovered[0]["operation"] == "amend"
    assert recovered[0]["authority_effect"] == "candidate-only"
    assert target.read_bytes() == original


def test_tower_memory_route_and_command_registration():
    import mira_memory
    assert mira_memory.route_focus("Tower")["recommended_owner"] == "tower"
    root = Path(__file__).resolve().parents[1]
    assert '"tower": REPO_ROOT / "scripts" / "tower.py"' in (root / "tools/run_repo.py").read_text()
    assert "docs/skill-drafts/tower/SKILL.md" in (root / "AGENTS.md").read_text()


def test_concurrent_close_publishes_one_complete_contribution(repo):
    from concurrent.futures import ThreadPoolExecutor
    payload = entry()
    with ThreadPoolExecutor(max_workers=2) as workers:
        results = list(workers.map(lambda _: tower.close(payload, repo), range(2)))
    assert sorted(row["status"] for row in results) == ["reused", "saved"]
    assert len(tower.contributions(repo)) == 1
    assert not list((notebook.domain(repo) / "work/strategy-notebook/contributions").glob(".tower-*"))

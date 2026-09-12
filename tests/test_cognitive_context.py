from __future__ import annotations
import copy
import json
import subprocess
from pathlib import Path
import pytest
import strategy_notebook as sn
import cognitive_context as cc
import library_reasoning as lr
from validate_daily_run import JUDGMENT_PLACEHOLDER_RE


def entry(repo, day, text=None):
    path = repo / "geopolitics/work/daily" / day / "strategy-notebook.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text or f"# {day}\n\nStatus: `draft`\n\n## Strategic Question\n\nCan access change leverage?\n\n## Bottom Line\n\nAccess may affect leverage. Confidence: low; incidents unverified.\n\n## Delta\n\nNo verified change.\n", encoding="utf-8")
    return path


def test_monthly_conflict_and_held_status(tmp_path):
    path = tmp_path / "geopolitics/work/strategy-notebook/2026-08.md"
    path.parent.mkdir(parents=True)
    path.write_text("## Daily Estimate: One\nDate: `2026-08-08`\nold\n## Daily Estimate: Two\nDate: `2026-08-09`\nother")
    assert "other" not in sn.read_entry("2026-08-08", tmp_path)["text"]
    entry(tmp_path, "2026-08-08", "# entry\nStatus: `analytical debt retained`\nanalysis incomplete")
    row = sn.read_entry("2026-08-08", tmp_path)
    assert row["alternatives"][0]["differs"]
    assert sn.disposition("2026-08-08", tmp_path)["status"] == "analysis-deferred"


def test_context_missing_history_revision_and_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(sn, "git", lambda *a: b"")
    entry(tmp_path, "2026-09-01")
    entry(tmp_path, "2026-09-02")
    entry(tmp_path, "2026-09-03", "# later\n\nCorrects [earlier](../2026-09-02/strategy-notebook.md).")
    entry(tmp_path, "2026-09-04", "# comparison\n\nSee [earlier](../2026-09-02/strategy-notebook.md).")
    result = sn.context("2026-09-02", "access leverage", tmp_path)
    assert not result["historical_context"]
    assert {r["entry_date"] for r in result["later_context"]} == {"2026-09-01", "2026-09-02", "2026-09-03"}
    assert result == sn.context("2026-09-02", "access leverage", tmp_path)
    small = sn.context("2026-09-02", "access leverage", tmp_path, limit=30)
    assert not small["later_context"] and small["omitted"]


def test_historical_bytes_separate_from_current(tmp_path, monkeypatch):
    path = entry(tmp_path, "2026-09-02")
    original = path.read_bytes()
    path.write_text(path.read_text() + "\nLater correction.\n")
    def git(repo, *args):
        if args[0] == "log": return b"a" * 40
        if args[0] == "show" and args[1] == "-s": return b"2026-09-02T12:00:00Z"
        return original
    monkeypatch.setattr(sn, "git", git)
    result = sn.context("2026-09-02", "access", tmp_path)
    assert "Later correction" not in result["historical_context"][0]["excerpt"]
    assert "Later correction" in result["later_context"][0]["excerpt"]


def test_consumption_binding_and_unavailable():
    frozen = {"strategy": {"status": "available"}, "library": {"status": "unavailable"}}
    frozen["content_sha256"] = sn.digest(frozen)
    use = {"strategy": {"status": "used", "reason": "changed judgment", "context_sha256": frozen["content_sha256"], "prose_anchors": ["A qualified judgment."]}, "library": {"status": "unavailable", "reason": "no body"}}
    reference = {"context_consumption": use, "items": [{"prose_anchor": "A qualified judgment."}]}
    assert not cc.consumption_failures({"strategy_context": frozen}, {"context_consumption": use}, reference, "A qualified judgment.")
    reference = copy.deepcopy(reference)
    reference["context_consumption"]["strategy"]["context_sha256"] = "bad"
    assert cc.consumption_failures({"strategy_context": frozen}, {"context_consumption": reference["context_consumption"]}, reference, "A qualified judgment.")
    assert not cc.consumption_failures({}, {}, {}, "legacy")


def candidate(repo):
    note = repo / "archive/notes/library/access.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("# Access constraints\n\nA revisable hypothesis.")
    binding = {"path": note.relative_to(repo).as_posix(), "sha256": sn.digest(note.read_bytes())}
    return {"operation": "amend", "note_class": "hypothesis", "owner": "mira-notes", "target_path": binding["path"], "target_sha256": binding["sha256"],
            "central_question": "access constraints", "change": "failed transfer", "why_it_matters": "limits overreach", "proposed_edit": "retain a counterexample", "strongest_objection": "one case", "next_test": "new context", "limitations": "incomplete evidence", "duplicate_search": {"reason": "same question; amend", "inspected": [binding]}, "source_bindings": [binding], "ranking": dict.fromkeys(("consequence", "evidence", "novelty", "testability"), 2)}


def test_notes_duplicate_stale_and_noop(tmp_path):
    row = candidate(tmp_path)
    result = cc.nominations([row, row], tmp_path)
    assert len(result) == 1
    assert cc.nominations(result, tmp_path) == result
    assert cc.nominations([], tmp_path) == []
    assert cc.note_search("access constraints", tmp_path)[0]["path"] == row["target_path"]
    row["operation"] = "create"
    with pytest.raises(ValueError, match="amendment"):
        cc.nominations([row], tmp_path)
    row["operation"] = "challenge"
    (tmp_path / row["target_path"]).write_text("changed")
    with pytest.raises(ValueError, match="stale"):
        cc.nominations([row], tmp_path)


def test_irrelevant_availability_and_explicit_roles(monkeypatch):
    monkeypatch.setattr(lr, "learned_adjustment", lambda *a: 0)
    source = {"source_id": "LIB-X", "title": "Gardens", "text_status": "verified", "coverage_status": "complete"}
    assert lr.source_score_components(source, {"alliance"}, [], set())["total"] == 0
    ranked = [{"source_id": "a"}, {"source_id": "b"}, {"source_id": "c"}]
    cognitive = {"works": [{"library_source_id": "b", "matched_negative_signatures": ["exclusion"]}, {"library_source_id": "c", "framing": {"anti_analogy": ["difference"]}}]}
    selected, report = lr.select_cognitive_sources(ranked, cognitive)
    assert [r["source_id"] for r in selected] == ["a", "c"]
    assert report["excluded"][0]["reason"] == "negative signature"


def test_links_not_placeholders():
    assert not JUDGMENT_PLACEHOLDER_RE.search("[sources](sources.md) and [estimate](../x.md)")
    assert JUDGMENT_PLACEHOLDER_RE.search("[describe mechanism]")


def test_library_failure_nonblocking(tmp_path, monkeypatch):
    import library_journal
    monkeypatch.setattr(sn, "git", lambda *a: b"")
    entry(tmp_path, "2026-09-02")
    monkeypatch.setattr(library_journal, "context", lambda *a, **k: (_ for _ in ()).throw(ValueError("missing")))
    monkeypatch.setattr(lr, "pre_scan", lambda *a, **k: (_ for _ in ()).throw(ValueError("stale")))
    result = cc.prepare("2026-09-02", "access", tmp_path)
    assert result["library"]["status"] == "unavailable"
    assert result["library_scan"]["status"] == "unavailable"
    assert result["strategy"]["later_context"]


def test_refresh_keeps_reading_bytes_and_library_budget(tmp_path, monkeypatch):
    import argparse
    import mira_journal as journal
    from test_mira_journal import configure_repo, context_pack
    repo, drafts = configure_repo(monkeypatch, tmp_path)
    day = "2026-08-08"
    bundle = drafts / day
    bundle.mkdir()
    pack = context_pack(day=day)
    brief = journal.composition_brief(journal.parse_entry_date(day), pack)
    original_context = {"strategy": {}, "library": {"status": "unavailable"}, "library_scan": {"status": "screened"}}
    original_context["content_sha256"] = sn.digest(original_context)
    brief = cc.attach(brief, original_context)
    assert not journal.validate_composition_brief(brief, pack=pack)
    contract = journal.draft_contract(journal.parse_entry_date(day), pack, brief)
    contract["session_reading"] = {"checkpoint_sha256": "unchanged"}
    for name, value in (("context-pack.json", pack), ("composition-brief.json", brief), ("draft-contract.json", contract)):
        journal.atomic_write_json(bundle/name, value)
    ack = bundle / "session-reading-ack.json"
    ack.write_bytes(b'"unchanged acknowledgement"')
    def prepare(day, focus, repo, previous=None):
        assert previous == original_context
        return {**original_context}
    monkeypatch.setattr(cc, "prepare", prepare)
    args = argparse.Namespace(date=day, as_of=None, output_root=drafts, refresh_strategy_context=True, check=False)
    result = journal.command_prepare(args)
    assert result["status"] == "context_refreshed"
    assert ack.read_bytes() == b'"unchanged acknowledgement"'
    assert journal.load_json(bundle / "draft-contract.json")["session_reading"] == contract["session_reading"]
    assert not journal.validate_composition_brief(journal.load_json(bundle / "composition-brief.json"), pack=pack)
    monkeypatch.setattr(journal, "load_registry", lambda: {"entries": [{"entry_date": day, "versions": [{"version_id": "MJ-test-v1"}]}]})
    with pytest.raises(journal.JournalError, match="finalized"):
        journal.command_prepare(args)


def test_roi_nominations_refresh_preserves_obligations(tmp_path):
    row = candidate(tmp_path)
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    packet = {"sections": {"note_candidates": [], "open_obligations": [{"reason": "prior work"}]}}
    (bundle / "roi-synthesis.json").write_text(json.dumps(packet))
    (bundle / "note-candidates.json").write_text(json.dumps([row]))
    cc.refresh_roi(bundle, "2026-09-08", tmp_path)
    first = (bundle / "roi-synthesis.json").read_bytes()
    cc.refresh_roi(bundle, "2026-09-08", tmp_path)
    assert first == (bundle / "roi-synthesis.json").read_bytes()
    updated = json.loads(first)
    assert updated["sections"]["note_candidates"][0]["operation"] == "amend"
    assert updated["sections"]["open_obligations"][0]["reason"] == "prior work"


def test_cognitive_cache_invalidates_content(tmp_path, monkeypatch):
    monkeypatch.setattr(lr, "REPO_ROOT", tmp_path)
    path = tmp_path / "archive/library/profile.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}")
    calls = []
    monkeypatch.setattr(lr, "_cognitive_inventory", lambda *a: calls.append(a) or {"works": []})
    lr.cognitive_inventory("question", "mechanism")
    lr.cognitive_inventory("question", "mechanism")
    assert len(calls) == 1
    path.write_text('{"changed":true}')
    lr.cognitive_inventory("question", "mechanism")
    assert len(calls) == 2


def test_import_header_is_not_evidence_and_rehearsal_is_not_feedback(tmp_path, monkeypatch):
    path = tmp_path / "body.txt"
    path.write_text("MIRA LIBRARY DERIVED TEXT Source URL: trade Source SHA256: 123\n\nTrade restrictions change access.")
    _, passages = lr.paragraph_candidates(path, {"trade", "source"})
    assert all("DERIVED TEXT" not in row["text"] for row in passages)
    monkeypatch.setattr(lr, "feedback_path", lambda: pytest.fail("rehearsal must not open routing ledger"))
    assert lr.append_feedback({"evaluation_kind": "retrospective-rehearsal"}, {}) == 0
    assert lr.append_cognitive_feedback({"evaluation_kind": "retrospective-rehearsal"}) == 0


def test_completed_dream_replays_recorded_context_after_finalized_journal(tmp_path, monkeypatch):
    import dream_eod as dream
    from types import SimpleNamespace
    from test_dream_eod import arguments
    monkeypatch.setattr(dream, "tower_pending", lambda *a: {"status": "clear"})
    monkeypatch.setattr(dream, "manifest_rows", lambda _: 0)
    monkeypatch.setattr(dream, "journal_entry", lambda _: {"versions": [{"version_id": "MJ-20260816-v1", "content_sha256": "a"*64}]})
    monkeypatch.setattr(dream, "run_tool", lambda *a: SimpleNamespace(returncode=0, stdout='{}', stderr=''))
    monkeypatch.setattr(dream, "forecast_review_step", lambda *a, **k: {"status": "no_due_hooks"}, raising=False)
    expected = {"notebook": {"status": "analysis-deferred", "digest": "a"*64}, "library": {"status": "unavailable", "reason": "missing body"}}
    monkeypatch.setattr(cc, "closeout", lambda *a: copy.deepcopy(expected))
    args = arguments(tmp_path, no_candidate="No experiment")
    result = dream.execute(args, args.date)
    assert result["status"] == "completed"
    assert result["cognitive_disposition"] == expected
    monkeypatch.setattr(cc, "closeout", lambda *a: pytest.fail("completed close must not reconstruct context"))
    replay = dream.execute(args, args.date)
    assert replay["cognitive_disposition"] == expected
    assert replay["mutation"] is False

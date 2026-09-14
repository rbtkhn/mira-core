from __future__ import annotations

import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dream_forecast_review as review
import dream_eod


HOOK = "NG-20260801-F01"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def corpus(tmp_path):
    root = tmp_path / "repo"
    work = root / "narrative-geopolitics/work"
    ledger = work / "forecasts/forecast-ledger.md"
    write(ledger, (
        f"| `{HOOK}` | `2026-08-01` | Passage | Official language stays conditional. | `likely` | `2026-08-10` | [Source](../daily/2026-08-01/forecast.md) | `open` |\n"
        f"## Accountability Triage\n| `{HOOK}` | `2026-08-01` | `original` | `ex_ante` | `open` | `yes` | Original forecast. |\n"
    ))
    original = work / "daily/2026-08-01/forecast.md"
    write(original, f"# {HOOK}\nHit if an official says passage remains conditional by August 10.\n")
    source = root / "archive/sources/geopolitics/sources/2026-08-05/statement.md"
    write(source, "On 2026-08-05 the official said passage remains conditional.\nAnother official said ordinary passage is restored.\n")
    manifest = root / "archive/sources/geopolitics/source-manifest.json"
    write(manifest, json.dumps({"sources": [{"date": "2026-08-05", "local_path": source.relative_to(root).as_posix()}]}))
    row, = dream_eod.forecast_ledger_rows(ledger)
    return root, row, original, source, manifest


def proposal(packet, original, source, root, disposition="proposed_hit"):
    citations = [{"path": original.relative_to(root).as_posix(), "quote": "Hit if an official says passage remains conditional by August 10.", "role": "criteria"}]
    roles = ["supports", "challenges"] if disposition == "proposed_mixed" else ["challenges" if disposition == "proposed_miss" else "supports"]
    for role in roles:
        citations.append({"path": source.relative_to(root).as_posix(), "quote": "passage remains conditional" if role == "supports" else "ordinary passage is restored", "role": role, "event_date": "2026-08-05", "date_basis_quote": "On 2026-08-05", "evidence_use": "source_assertion"})
    return {"hook": HOOK, "input_digest": packet["input_digest"], "disposition": disposition, "criteria_analysis": "An official public statement suffices.", "time_window_analysis": "August 5 lies after authorship and before August 10.", "rationale": "Proposed from the cited statement.", "counterevidence": "The second statement challenges the first.", "remaining_gates": "Forecast owner must adjudicate; no scoring authority.", "citations": citations}


@pytest.mark.parametrize("with_mechanism", [False, True])
def test_real_parser_to_dream_review_handoff_and_resume(corpus, tmp_path, monkeypatch, with_mechanism):
    root, _, original, source, _ = corpus
    ledger = root / "narrative-geopolitics/work/forecasts/forecast-ledger.md"
    if with_mechanism:
        write(ledger, ledger.read_text().replace(
            "Official language stays conditional. | `likely`",
            "Official language stays conditional. | Transit governance persists. | `likely`",
        ))
    # Redirect storage only: parser, due-row selection, conductor wrapper, and
    # review implementation all run unchanged against this isolated corpus.
    monkeypatch.setattr(dream_eod, "REPO_ROOT", root)
    monkeypatch.setattr(dream_eod, "FORECAST_LEDGER", ledger)
    args = SimpleNamespace(journal_bundle=tmp_path / "private/day", forecast_review_json=None)
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    preview = dream_eod.forecast_review_step(args, "2026-08-10", check=True)
    assert preview["status"] == "review_due", preview
    assert preview["due_count"] == 1
    assert not args.journal_bundle.exists()
    prepared = dream_eod.forecast_review_step(args, "2026-08-10")
    assert prepared["status"] == "forecast_review_required", prepared
    packet, = json.loads(Path(prepared["input_path"]).read_text())["hooks"]
    assert packet["hook"] == packet["ledger_row"]["hook_id"] == HOOK
    args.forecast_review_json = tmp_path / "private/result.json"
    write(args.forecast_review_json, json.dumps({"reviews": [proposal(packet, original, source, root)]}))
    resumed = dream_eod.forecast_review_step(args, "2026-08-10")
    assert resumed["status"] == "review_complete", resumed
    assert resumed["reviews"][0]["disposition"] == "proposed_hit"
    args.forecast_review_json = None
    assert dream_eod.forecast_review_step(args, "2026-08-10")["reviews"][0]["status"] == "unchanged"
    assert before == {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("disposition", ["proposed_hit", "proposed_miss", "proposed_mixed"])
def test_cited_proposals_are_private_and_input_bound(corpus, tmp_path, disposition):
    root, row, original, source, _ = corpus
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    bundle = tmp_path / "private/day-one"
    first = review.run(root, [row], "2026-08-10", bundle)
    assert first["status"] == "forecast_review_required"
    packet = json.loads(Path(first["input_path"]).read_text())["hooks"][0]
    result_path = tmp_path / "private/result.json"
    write(result_path, json.dumps({"reviews": [proposal(packet, original, source, root, disposition)]}))
    result = review.run(root, [row], "2026-08-10", bundle, result_path=result_path)
    assert result["reviews"][0]["disposition"] == disposition
    assert result["status"] == "review_complete"
    again = review.run(root, [row], "2026-08-11", tmp_path / "private/day-two")
    assert again["reviews"][0]["status"] == "unchanged"
    assert before == {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("failure", ["wrong_date", "invented_quote", "stale_digest", "wrong_path", "operational_truth", "no_evidence", "no_criteria"])
def test_invalid_proposal_cannot_be_accepted(corpus, tmp_path, failure):
    root, row, original, source, _ = corpus
    packet = review.gather(root, [row], "2026-08-10")["hooks"][0]
    result = proposal(packet, original, source, root)
    if failure == "wrong_date":
        result["citations"][1]["event_date"] = "2026-08-11"
    elif failure == "invented_quote":
        result["citations"][1]["quote"] = "an invented quotation"
    elif failure == "stale_digest":
        result["input_digest"] = "0" * 64
    elif failure == "wrong_path":
        result["citations"][1]["path"] = "../../escape.md"
    elif failure == "operational_truth":
        result["citations"][1]["evidence_use"] = "verified_event"
    elif failure == "no_evidence":
        result["disposition"] = "proposed_miss"
        result["citations"] = result["citations"][:1]
    else:
        result["citations"] = result["citations"][1:]
    with pytest.raises(ValueError):
        review.validate_review(result, packet, root)
    path = tmp_path / "result.json"
    write(path, json.dumps({"reviews": [result]}))
    received = review.run(root, [row], "2026-08-10", tmp_path / "private/day", result_path=path)
    assert received["status"] == "review_incomplete"
    assert received["failed_count"] == 1
    assert received["reviews"][0]["status"] == "review_failed"
    assert received["reviews"][0]["nonblocking"]


def test_new_and_changed_sources_invalidate_cached_gap(corpus, tmp_path):
    root, row, original, source, manifest = corpus
    packet = review.gather(root, [row], "2026-08-10")["hooks"][0]
    gap = proposal(packet, original, source, root, "evidence_gap")
    gap["citations"] = []
    path = tmp_path / "result.json"
    write(path, json.dumps({"reviews": [gap]}))
    bundle = tmp_path / "private/day"
    review.run(root, [row], "2026-08-10", bundle, result_path=path)
    assert review.run(root, [row], "2026-08-10", bundle)["reviews"][0]["status"] == "unchanged"
    write(source, source.read_text() + "New evidence.\n")
    assert review.run(root, [row], "2026-08-10", bundle)["status"] == "forecast_review_required"
    changed = review.gather(root, [row], "2026-08-10")["hooks"][0]["input_digest"]
    new_source = root / "archive/sources/geopolitics/sources/2026-08-09/new.md"
    write(new_source, "New source.")
    data = json.loads(manifest.read_text())
    data["sources"].append({"date": "2026-08-09", "local_path": new_source.relative_to(root).as_posix()})
    write(manifest, json.dumps(data))
    assert review.gather(root, [row], "2026-08-10")["hooks"][0]["input_digest"] != changed


def test_missing_original_and_legacy_conflict_are_explicit_gaps(corpus):
    root, row, original, _, _ = corpus
    original.unlink()
    write(root / "narrative-geopolitics/work/verification/packets/VER-20260801-01/README.md", HOOK)
    packet = review.gather(root, [row], "2026-08-10")["hooks"][0]
    assert any("Original hook" in gap for gap in packet["gaps"])
    assert any("Legacy/canonical" in gap for gap in packet["gaps"])


def test_check_and_unavailable_do_not_block_or_mutate_sources(corpus, tmp_path):
    root, row, _, _, _ = corpus
    bundle = tmp_path / "private/day"
    assert review.run(root, [row], "2026-08-10", bundle, check=True)["mutation"] is False
    assert not bundle.exists()
    result = review.run(root, [row], "2026-08-10", bundle, unavailable="Source could not be read.")
    assert result["status"] == "review_incomplete"
    assert result["reviews"][0]["status"] == "review_unavailable"
    assert result["unavailable_count"] == 1
    assert review.run(root, [], "2026-08-10", root)["status"] == "review_incomplete"


def test_canonical_association_discovers_new_evidence(corpus):
    root, row, _, _, _ = corpus
    reality_root = root / "narrative-geopolitics/work/reality"
    claim = {"id": "OPC-20260801-01", "kind": "claim", "claim_type": "empirical", "consequence": "ordinary", "affected_forecast_hooks": [HOOK]}
    write(reality_root / "claims/OPC-20260801-01.json", json.dumps(claim))
    packet = review.gather(root, [row], "2026-08-10")["hooks"][0]
    evidence = {"id": "EVD-20260805-001", "kind": "evidence", "event_time": "2026-08-05", "observation": "Official statement.", "source_id": "VSRC-TEST"}
    write(reality_root / "evidence/EVD-20260805-001.json", json.dumps(evidence))
    relation = {"id": "REL-20260805-001", "kind": "relation", "from_id": evidence["id"], "to_id": claim["id"], "relation_type": "supports"}
    write(reality_root / "relations/REL-20260805-001.json", json.dumps(relation))
    updated = review.gather(root, [row], "2026-08-10")["hooks"][0]
    assert updated["input_digest"] != packet["input_digest"]
    assert evidence["id"] in {r.get("record_id") for r in updated["references"]}
    assert claim["id"] in updated["canonical_audits"]


def test_source_changed_after_handoff_is_rejected(corpus):
    root, row, original, source, _ = corpus
    packet = review.gather(root, [row], "2026-08-10")["hooks"][0]
    result = proposal(packet, original, source, root)
    write(source, source.read_text() + "Correction after preparation.")
    with pytest.raises(ValueError, match="changed during"):
        review.validate_review(result, packet, root)


def test_late_authorship_cannot_support_earlier_event(corpus):
    root, row, original, source, _ = corpus
    ledger = root / "narrative-geopolitics/work/forecasts/forecast-ledger.md"
    write(ledger, ledger.read_text().replace("`2026-08-01`", "`2026-08-06`"))
    packet = review.gather(root, [row], "2026-08-10")["hooks"][0]
    with pytest.raises(ValueError, match="outside"):
        review.validate_review(proposal(packet, original, source, root), packet, root)

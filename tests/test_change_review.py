from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest

import change_review as cr


@pytest.fixture
def setup_case(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "candidate.py").write_text("def review(row):\n    return row['hook_id']\n", encoding="utf-8")
    (repo / "lesson.txt").write_text("A handmade fixture concealed a parser key mismatch.\n", encoding="utf-8")
    for args in (["init", "-q"], ["add", "."], ["-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "base"]):
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)
    (repo / "candidate.py").write_text("def review(row):\n    return row['hook']\n", encoding="utf-8")
    monkeypatch.setattr(cr, "REPO_ROOT", repo)
    spec = {"schema": cr.SCHEMA, "case_id": "case-1", "change_id": "change-1", "revision": 1,
        "kind": "prospective", "eligible": True, "change_class": "data-contract",
        "proposed_change": "Consume forecast parser output", "decision": "Is the consumer ready?",
        "preparation_minutes": 4, "base_revision": "HEAD", "requirements": ["Use parser contract"],
        "settings": {"model": "test-model", "runtime": "manual", "reasoning": "high", "output_tokens": 1500},
        "sources": [{"path": "candidate.py", "sha256": cr.digest((repo / "candidate.py").read_bytes())}],
        "test_results": [], "lessons": [{"lesson_id": "contract-mismatch", "original_failure": "Wrong dictionary key",
        "diagnosis": "Fixture bypassed real parser", "corrective_action": "Exercise real producer",
        "applicability": "Consumer accepts parser dictionaries", "invalidated_when": "The parser contract changes",
        "sources": [{"path": "lesson.txt", "sha256": cr.digest((repo / "lesson.txt").read_bytes())}]}]}
    yield repo, tmp_path / "state", spec
    # Git marks loose objects read-only on Windows; leave disposable fixtures
    # removable by the repository validator's ordinary temporary cleanup.
    for directory, _, files in os.walk(repo / ".git"):
        for name in files:
            Path(directory, name).chmod(stat.S_IREAD | stat.S_IWRITE)


def review(packet, finding=True):
    ref = packet["current_evidence"]["sources"][0]
    return {"packet_digest": packet["packet_digest"], "settings": packet["settings"],
        "fresh_session": True, "packet_only": True, "deviations": [], "duration_minutes": None,
        "usage": {"input_tokens": None, "output_tokens": None, "cost_usd": None},
        "findings": [{"id": "F1", "location": {"source_id": "S1", "line": 2},
        "mechanism": "Consumer expects a different dictionary key", "consequence": "KeyError before review",
        "evidence": [{"source_id": "S1", "sha256": ref["sha256"], "line": 2}],
        "proposed_verification": "Run real parser output through consumer"}] if finding else [], "rejected_lessons": []}


def prepared(root, spec):
    cr.prepare(root, spec)
    directory = cr.case_dir(root, spec["case_id"], spec["revision"])
    return directory, cr.load_case(directory)


def completed(root, spec, repo, *, contaminated=False, both=False):
    directory, record = prepared(root, spec)
    for key, packet in record["packets"].items():
        value = review(packet, both or record["arms"][key] == "memory")
        if contaminated:
            value["deviations"] = ["Used previous conversation"]
        cr.accept(directory, key, value)
    cr.compare(directory)
    assessment = cr.read(directory / "assessment-template.json")
    assessment.update(assessment_minutes=6, diagnosis="useful")
    for item in assessment["items"]:
        item.update(status="supported", group="contract", consequential=True, changed="test",
            reason="Reproduction confirms failure", verification=[{"path": "lesson.txt",
            "sha256": cr.digest((repo / "lesson.txt").read_bytes()), "summary": "Synthetic verification fixture"}])
    cr.outcome(directory, assessment)
    return directory


def test_full_command_sequence(setup_case, capsys):
    repo, root, spec = setup_case
    before = {p.name: p.read_bytes() for p in repo.iterdir() if p.is_file()}
    spec_path = root.parent / "spec.json"
    spec_path.write_text(json.dumps(spec))
    prefix = ["--state-root", str(root)]
    assert cr.main(prefix + ["prepare", "--spec", str(spec_path)]) == 0
    directory = cr.case_dir(root, "case-1", 1)
    record = cr.load_case(directory)
    common = [p["current_evidence"] for p in record["packets"].values()]
    assert common[0] == common[1]
    assert "hook_id" in common[0]["sources"][0]["base_text"]
    assert "['hook']" in common[0]["sources"][0]["text"]
    for key, packet in record["packets"].items():
        if record["arms"][key] == "fresh":
            assert packet["lessons"] == []
            assert "handmade fixture" not in json.dumps(packet)
        value_path = root.parent / f"{key}.json"
        value_path.write_text(json.dumps(review(packet)))
        assert cr.main(prefix + ["accept", "--case-id", "case-1", "--revision", "1", "--reviewer", key, "--input", str(value_path)]) == 0
    assert cr.main(prefix + ["compare", "--case-id", "case-1", "--revision", "1"]) == 0
    template = cr.read(directory / "assessment-template.json")
    template.update(assessment_minutes=5, diagnosis="insufficiently-tested")
    value_path.write_text(json.dumps(template))
    assert cr.main(prefix + ["outcome", "--case-id", "case-1", "--revision", "1", "--input", str(value_path)]) == 0
    assert cr.main(prefix + ["report"]) == 0
    assert cr.report(root)["cases"][0]["unresolved"] == 2
    assert before == {p.name: p.read_bytes() for p in repo.iterdir() if p.is_file()}


@pytest.mark.parametrize("fault", ["hash", "missing", "traversal", "support", "duplicate", "settings"])
def test_bad_spec_fails_before_publication(setup_case, fault):
    repo, root, spec = setup_case
    if fault == "hash": spec["sources"][0]["sha256"] = "bad"
    if fault == "missing": (repo / "candidate.py").unlink()
    if fault == "traversal": spec["sources"][0]["path"] = "../outside"
    if fault == "support": spec["lessons"][0]["sources"] = []
    if fault == "duplicate": spec["sources"] *= 2
    if fault == "settings": spec["settings"]["output_tokens"] = -1
    with pytest.raises((cr.ReviewError, OSError)):
        cr.prepare(root, spec)
    assert not list(root.glob("*/case.json"))


def test_changing_source_during_copy(setup_case, monkeypatch):
    repo, root, spec = setup_case
    original = cr.source
    def unstable(ref, sid):
        value = original(ref, sid)
        if sid == "S1":
            (repo / "candidate.py").write_text("changed\n")
        return value
    monkeypatch.setattr(cr, "source", unstable)
    with pytest.raises(cr.ReviewError, match="changed during"):
        cr.prepare(root, spec)
    assert not list(root.glob("*/case.json"))


def test_interrupted_exports_retry_uses_frozen_bytes(setup_case, monkeypatch):
    repo, root, spec = setup_case
    export = cr.export_packets
    monkeypatch.setattr(cr, "export_packets", lambda *_: (_ for _ in ()).throw(OSError("interrupted")))
    with pytest.raises(OSError): cr.prepare(root, spec)
    monkeypatch.setattr(cr, "export_packets", export)
    (repo / "candidate.py").write_text("new source\n")
    cr.prepare(root, spec)
    directory, record = prepared(root, spec)
    assert len(list((directory / "packets").glob("*.json"))) == 2
    assert all("['hook']" in p["current_evidence"]["sources"][0]["text"] for p in record["packets"].values())
    spec["sources"][0]["sha256"] = cr.digest((repo / "candidate.py").read_bytes())
    with pytest.raises(cr.ReviewError, match="new revision"): cr.prepare(root, spec)
    spec["revision"] = 2
    cr.prepare(root, spec)


@pytest.mark.parametrize("fault", ["digest", "line", "citation", "location", "duplicate", "negative"])
def test_invalid_review(setup_case, fault):
    _, root, spec = setup_case
    directory, record = prepared(root, spec)
    key, packet = next(iter(record["packets"].items()))
    value = review(packet)
    if fault == "digest": value["packet_digest"] = "bad"
    if fault == "line": value["findings"][0]["evidence"][0]["line"] = 50
    if fault == "citation": value["findings"][0]["evidence"][0]["sha256"] = "bad"
    if fault == "location": value["findings"][0]["location"]["source_id"] = "L1S1"
    if fault == "duplicate": value["findings"] *= 2
    if fault == "negative": value["duration_minutes"] = -1
    with pytest.raises(cr.ReviewError): cr.accept(directory, key, value)


def test_freeze_empty_reviews_and_comparison_gate(setup_case):
    _, root, spec = setup_case
    spec["lessons"] = []
    directory, record = prepared(root, spec)
    with pytest.raises(cr.ReviewError, match="both"): cr.compare(directory)
    for key, packet in record["packets"].items():
        value = review(packet, False)
        cr.accept(directory, key, value)
        cr.accept(directory, key, value)
        with pytest.raises(cr.ReviewError, match="immutable"):
            cr.accept(directory, key, review(packet, True))
    cr.compare(directory)
    assert cr.read(directory / "comparison.json")["findings"] == []


@pytest.mark.parametrize("fault", ["digest", "missing", "unsupported", "verification", "duplicate"])
def test_outcome_validation(setup_case, fault):
    repo, root, spec = setup_case
    directory, record = prepared(root, spec)
    for key, packet in record["packets"].items(): cr.accept(directory, key, review(packet))
    cr.compare(directory)
    value = cr.read(directory / "assessment-template.json")
    value.update(assessment_minutes=1, diagnosis="unhelpful")
    if fault == "digest": value["comparison_digest"] = "bad"
    if fault == "missing": value["items"].pop()
    if fault == "unsupported": value["items"][0]["changed"] = "test"
    if fault == "verification":
        value["items"][0].update(status="supported", changed="test", verification=[{"path": "lesson.txt", "sha256": "bad", "summary": "bad"}])
    if fault == "duplicate": value["items"][0]["status"] = "duplicate"
    with pytest.raises(cr.ReviewError): cr.outcome(directory, value)


def test_report_counts_only_independent_prospective_cases(setup_case):
    repo, root, spec = setup_case
    completed(root, spec, repo)
    spec.update(case_id="case-2", change_id="change-2")
    completed(root, spec, repo)
    summary = cr.report(root)
    assert summary["memory_unique_corrected_changes"] == 2
    assert summary["median_human_minutes"] == 10
    assert summary["expansion_criterion_met"]
    spec.update(case_id="demo", change_id="demo", kind="known-answer-demo")
    completed(root, spec, repo)
    assert cr.report(root)["demonstrations_excluded"] == 1
    spec.update(case_id="excluded", change_id="excluded", kind="prospective", eligible=False, exclusion_reason="Formatting only")
    cr.prepare(root, spec)
    assert len(cr.report(root)["exclusions"]) == 1


@pytest.mark.parametrize("contaminated,both", [(True, False), (False, True)])
def test_no_unique_credit_for_deviations_or_shared_findings(setup_case, contaminated, both):
    repo, root, spec = setup_case
    completed(root, spec, repo, contaminated=contaminated, both=both)
    assert cr.report(root)["memory_unique_corrected_changes"] == 0


def test_runner_dispatch(tmp_path):
    result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / "tools/run_repo.py"),
        "change-review", "--state-root", str(tmp_path / "review"), "report"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["completed"] == 0


@pytest.mark.parametrize("artifact", ["review", "outcome"])
def test_detects_modified_private_artifacts(setup_case, artifact):
    repo, root, spec = setup_case
    directory = completed(root, spec, repo)
    path = next((directory / "reviews").glob("*.json")) if artifact == "review" else directory / "outcome.json"
    value = cr.read(path)
    value["sha256"] = "bad"
    path.write_text(json.dumps(value))
    with pytest.raises(cr.ReviewError, match="digest mismatch"):
        cr.report(root)

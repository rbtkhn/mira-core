from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "recursive_learning_ledger.py"
SPEC = importlib.util.spec_from_file_location("recursive_learning_ledger_tests", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_current_recursive_learning_ledger_validates() -> None:
    assert MODULE.validate_ledger() == []


def test_rendered_markdown_exposes_all_five_stages() -> None:
    rendered = MODULE.render_markdown(MODULE.load_ledger())
    for heading in ("### Observation", "### Diagnosis", "### Intervention", "### Validation", "### Outcome"):
        assert heading in rendered
    assert "post-repair manual QA rate pending" in rendered


def test_missing_evidence_and_false_measurement_are_rejected(tmp_path: Path) -> None:
    ledger = copy.deepcopy(MODULE.load_ledger())
    entry = ledger["entries"][0]
    entry["closure_state"] = "measured"
    entry["outcome"]["measure"] = "Post-intervention measure pending."
    entry["validation"]["evidence_paths"] = ["missing-evidence.md"]
    json_path = tmp_path / "ledger.json"
    markdown_path = tmp_path / "ledger.md"
    json_path.write_text(json.dumps(ledger), encoding="utf-8")
    markdown_path.write_text(MODULE.render_markdown(ledger), encoding="utf-8")

    failures = MODULE.validate_ledger(
        repo_root=REPO_ROOT,
        json_path=json_path,
        markdown_path=markdown_path,
    )

    assert any("missing evidence path" in failure for failure in failures)
    assert any("measured entry has pending outcome" in failure for failure in failures)


def reference(signal: str, *, measured: bool = False, include_inputs: bool = True) -> dict:
    learning: dict = {
        "consumed_rsi_ids": [],
        "candidate_signal": signal,
        "candidate_summary": "A later observation may show whether the intervention changed behavior.",
        "future_test": "Compare the post-intervention observation with the baseline.",
    }
    if include_inputs:
        learning["assessment_inputs"] = {
            "assessment_basis": {
                "system_behavior_observed": True,
                "post_intervention_use_observed": measured,
                "outcome_observation": "observed" if measured else "pending",
            },
            "id": "RSI-20260809-99",
            "date": "2026-08-09",
            "title": "Journal continuity becomes an observed practice",
            "observation": {"summary": "A baseline exposed repetition.", "evidence_paths": ["scripts/mira_journal.py"]},
            "diagnosis": {"summary": "Composition lacked inherited practice context.", "evidence_paths": ["scripts/mira_journal.py"]},
            "intervention": {"summary": "Preparation now supplies admitted lessons.", "commits": ["2755649"], "evidence_paths": ["scripts/mira_journal.py"]},
            "validation": {"summary": "Tests verify the context contract.", "evidence_paths": ["tests/test_mira_journal.py"]},
            "outcome": {
                "summary": "A later entry supplied the first post-intervention observation.",
                "measure": "One grounded use observed." if measured else "Comparable post-intervention measurement pending.",
                "evidence_paths": ["tests/test_mira_journal.py"],
            },
            "next_measure": "Compare several entries for grounding and redundancy.",
        }
    return {"reference_id": "MJTR-20260809-v2", "recursive_learning": learning}


def test_assessment_states_preserve_the_learning_gate() -> None:
    assert MODULE.assess_reference(reference("none", include_inputs=False))["status"] == "non-candidate"
    assert MODULE.assess_reference(reference("observation", include_inputs=False))["status"] == "observation-only"
    partial = MODULE.assess_reference(reference("possible-loop"))
    assert partial["status"] == "partial-candidate"
    assert partial["authority_effect"] == "none"
    closed = MODULE.assess_reference(reference("possible-loop", measured=True))
    assert closed["status"] == "admissible"
    represented_ledger = {"entries": [{"id": "RSI-20260809-99", "journal_context_refs": ["MJTR-20260809-v2"]}]}
    assert MODULE.assess_reference(reference("possible-loop"), ledger=represented_ledger)["status"] == "already-represented"


def test_candidate_packet_is_classified_by_assessor_not_journal() -> None:
    value = reference("possible-loop", measured=True)
    assert "class" not in value["recursive_learning"]["assessment_inputs"]
    candidate = MODULE.candidate_from_reference(value)
    assert candidate["class"] == "closed-feedback-loop"
    assert candidate["closure_state"] == "measured"
    assert candidate["journal_context_refs"] == ["MJTR-20260809-v2"]


def test_ordinary_feature_work_is_not_admissible() -> None:
    value = reference("possible-loop", measured=True)
    value["recursive_learning"]["assessment_inputs"]["assessment_basis"]["system_behavior_observed"] = False
    assessment = MODULE.assess_reference(value)
    assert assessment["status"] == "partial-candidate"
    assert any("ordinary feature work" in failure for failure in assessment["failures"])


def test_journal_files_are_rejected_as_stage_evidence() -> None:
    candidate = MODULE.candidate_from_inputs(reference("possible-loop", measured=True))
    assert candidate is not None
    candidate["observation"]["evidence_paths"] = ["mira/journal/2026-08-09.md"]
    failures = MODULE.validate_entry(candidate)
    assert any("journal context cannot serve as observation evidence" in failure for failure in failures)


def test_assessment_entrypoint_runs_the_full_companion_validator(tmp_path: Path) -> None:
    prose_path = tmp_path / "draft.md"
    prose_path.write_text("# Deliberately incomplete companion\n", encoding="utf-8")
    value = reference("observation", include_inputs=False)
    value.update(
        {
            "journal_version_id": "MJ-20260809-v2",
            "journal_content_sha256": MODULE.sha256_bytes(prose_path.read_bytes()),
            "entry_date": "2026-08-09",
        }
    )
    reference_path = tmp_path / "technical-reference.json"
    reference_path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(MODULE.LearningError, match="technical reference"):
        MODULE.validated_reference(reference_path)


def configure_empty_ledger(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    json_path = tmp_path / "recursive-learning-ledger.json"
    markdown_path = tmp_path / "recursive-learning-ledger.md"
    ledger = {
        "ledger_id": "test-ledger",
        "status": "internal-canonical",
        "scope_note": "test",
        "entries": [],
    }
    json_path.write_text(MODULE.pretty_json(ledger), encoding="utf-8")
    markdown_path.write_text(MODULE.render_markdown(ledger), encoding="utf-8")
    monkeypatch.setattr(MODULE, "LEDGER_JSON_PATH", json_path)
    monkeypatch.setattr(MODULE, "LEDGER_MD_PATH", markdown_path)
    return json_path, markdown_path


def approval_row(candidate: dict, *, exact: bool = True, timestamp: str = "2026-08-10T05:00:00Z") -> tuple[str, dict]:
    digest = MODULE.sha256_bytes(MODULE.canonical_json(candidate).encode("utf-8"))
    statement = MODULE.admission_statement(str(candidate["id"]), digest)
    record_id = "MR-" + digest[:24]
    return record_id, {
        "record_id": record_id,
        "kind": "message",
        "role": "user",
        "timestamp": timestamp,
        "content": [{"type": "text", "text": statement if exact else "Do not admit this entry."}],
    }


def test_admission_requires_exact_record_is_checkable_and_rejects_duplicates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    json_path, _ = configure_empty_ledger(monkeypatch, tmp_path)
    candidate = MODULE.candidate_from_reference(reference("possible-loop", measured=True))
    record_id, row = approval_row(candidate)
    import mira_journal
    monkeypatch.setattr(mira_journal, "resolved_records_for_session", lambda *args, **kwargs: {record_id: row})
    session = "MS-019fce7b-67cd-7753-be6c-74f76e2f9b7a"
    before = json_path.read_bytes()
    checked = MODULE.admit_candidate(
        candidate, authority_ref=session, approval_record_ref=record_id, check=True
    )
    assert checked["status"] == "ready"
    assert json_path.read_bytes() == before
    admitted = MODULE.admit_candidate(
        candidate, authority_ref=session, approval_record_ref=record_id, check=False
    )
    assert admitted["status"] == "admitted"
    assert json.loads(json_path.read_text(encoding="utf-8"))["entries"][0]["id"] == candidate["id"]
    with pytest.raises(MODULE.LearningError, match="already exists"):
        MODULE.admit_candidate(candidate, authority_ref=session, approval_record_ref=record_id, check=False)

def test_admission_rejects_inexact_or_future_authority_records(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    configure_empty_ledger(monkeypatch, tmp_path)
    candidate = MODULE.candidate_from_reference(reference("possible-loop", measured=True))
    record_id, row = approval_row(candidate, exact=False)
    import mira_journal
    monkeypatch.setattr(mira_journal, "resolved_records_for_session", lambda *args, **kwargs: {record_id: row})
    session = "MS-019fce7b-67cd-7753-be6c-74f76e2f9b7a"
    with pytest.raises(MODULE.LearningError, match="exact digest-bound"):
        MODULE.admit_candidate(candidate, authority_ref=session, approval_record_ref=record_id, check=True)
    _, future = approval_row(candidate, timestamp="2099-01-01T00:00:00Z")
    monkeypatch.setattr(mira_journal, "resolved_records_for_session", lambda *args, **kwargs: {record_id: future})
    with pytest.raises(MODULE.LearningError, match="future"):
        MODULE.admit_candidate(candidate, authority_ref=session, approval_record_ref=record_id, check=True)


def test_ledger_pair_rolls_back_when_second_replace_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    json_path, markdown_path = configure_empty_ledger(monkeypatch, tmp_path)
    candidate = MODULE.candidate_from_reference(reference("possible-loop", measured=True))
    record_id, row = approval_row(candidate)
    import mira_journal
    monkeypatch.setattr(mira_journal, "resolved_records_for_session", lambda *args, **kwargs: {record_id: row})
    originals = (json_path.read_bytes(), markdown_path.read_bytes())
    calls = 0

    def fail_second(source: Path, target: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated Markdown replace failure")
        source.replace(target)

    monkeypatch.setattr(MODULE, "replace_file", fail_second)
    with pytest.raises(OSError, match="simulated"):
        MODULE.admit_candidate(
            candidate,
            authority_ref="MS-019fce7b-67cd-7753-be6c-74f76e2f9b7a",
            approval_record_ref=record_id,
            check=False,
        )
    assert (json_path.read_bytes(), markdown_path.read_bytes()) == originals

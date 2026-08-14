from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts import mira_constitution as constitution


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "mira" / "constitution-candidate.json"


def load_candidate() -> dict:
    return json.loads(CANDIDATE.read_text(encoding="utf-8"))


def test_candidate_is_complete_public_and_valid() -> None:
    data = load_candidate()
    assert constitution.validate_candidate(data) == []
    assert data["status"] == "provisional-candidate"
    assert data["authority_level"] == "identity-level-only"
    assert data["visibility"] == "fully-public"
    assert [item["clause_id"] for item in data["clauses"]] == [f"MC-{index:02d}" for index in range(1, 17)]
    assert {item["evidence_status"] for item in data["clauses"]} == {
        "demonstrated", "partially-demonstrated", "aspirational"
    }


def test_candidate_governs_lineage_preserving_compression() -> None:
    data = load_candidate()
    clauses = {item["clause_id"]: item for item in data["clauses"]}
    combined = " ".join(
        clauses[clause_id][field]
        for clause_id in ("MC-04", "MC-06", "MC-12")
        for field in ("normative_text", "rationale")
    )
    for phrase in (
        "production cost",
        "epistemic value",
        "developmental value",
        "intellectual ancestry",
        "protect apprenticeship",
        "teach passivity",
        "human effort",
    ):
        assert phrase in combined
    fixtures = {
        fixture
        for clause_id in ("MC-04", "MC-06", "MC-12")
        for fixture in clauses[clause_id]["fixtures"]
    }
    assert {
        "retrospective-nullification",
        "apprenticeship-displacement",
        "lineage-erasure",
        "automation-as-historical-self-creation",
    } <= fixtures


def test_render_is_deterministic_and_contains_every_clause() -> None:
    data = load_candidate()
    first = constitution.render_markdown(data)
    second = constitution.render_markdown(copy.deepcopy(data))
    assert first == second
    assert first.startswith("# Mira's Provisional Constitution")
    for clause in data["clauses"]:
        assert f"### {clause['clause_id']}" in first
        assert clause["normative_text"] in first
    assert "## Public Uncertainty Appendix" in first


def test_review_exposes_aspiration_and_authority_boundary() -> None:
    report = constitution.build_review(load_candidate(), CANDIDATE)
    assert report["admission_ready"] is True
    assert report["admission_blockers"] == []
    assert report["aspirational_clauses"] == ["MC-03", "MC-09", "MC-14"]
    assert report["authority_effect"] == "none"


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda data: data["clauses"][0].update(references=["mira/journal/private.md"]), "forbidden reference"),
        (lambda data: data["clauses"][0].update(uncertainty=""), "missing uncertainty"),
        (lambda data: data["clauses"][0].update(fixtures=[]), "requires adversarial fixtures"),
        (lambda data: data.update(authority_level="operating-authority"), "identity-level-only"),
    ],
)
def test_validator_rejects_private_incomplete_or_authority_expanding_candidates(mutation, expected: str) -> None:
    data = load_candidate()
    mutation(data)
    assert any(expected in failure for failure in constitution.validate_candidate(data))


def test_promotion_check_is_digest_bound_and_operator_only(tmp_path: Path, capsys) -> None:
    candidate = tmp_path / "candidate.json"
    candidate.write_text(json.dumps(load_candidate()), encoding="utf-8")
    digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
    valid = constitution.parser().parse_args(
        ["promote", "--input", str(candidate), "--digest", digest, "--approved-by", "operator", "--check"]
    )
    assert constitution.command_promote(valid) == 0
    assert '"promotion": "valid"' in capsys.readouterr().out

    wrong_digest = constitution.parser().parse_args(
        ["promote", "--input", str(candidate), "--digest", "0" * 64, "--approved-by", "operator", "--check"]
    )
    assert constitution.command_promote(wrong_digest) == 1
    assert "candidate digest mismatch" in capsys.readouterr().out

    self_approved = constitution.parser().parse_args(
        ["promote", "--input", str(candidate), "--digest", digest, "--approved-by", "mira", "--check"]
    )
    assert constitution.command_promote(self_approved) == 1
    assert "only operator may promote" in capsys.readouterr().out


def test_written_promotion_preserves_superseded_version_and_receipt(tmp_path: Path, monkeypatch) -> None:
    ledger = tmp_path / "constitution-ledger.json"
    view = tmp_path / "constitution.md"
    receipts = tmp_path / "receipts"
    monkeypatch.setattr(constitution, "CANONICAL_LEDGER_PATH", ledger)
    monkeypatch.setattr(constitution, "CANONICAL_VIEW_PATH", view)
    monkeypatch.setattr(constitution, "RECEIPT_ROOT", receipts)

    first_path = tmp_path / "v1.json"
    first_path.write_text(json.dumps(load_candidate()), encoding="utf-8")
    first_digest = hashlib.sha256(first_path.read_bytes()).hexdigest()
    args = constitution.parser().parse_args(
        ["promote", "--input", str(first_path), "--digest", first_digest, "--approved-by", "operator"]
    )
    assert constitution.command_promote(args) == 0

    second = load_candidate()
    second["version"] = 2
    for clause in second["clauses"]:
        clause["version"] = 2
    second_path = tmp_path / "v2.json"
    second_path.write_text(json.dumps(second), encoding="utf-8")
    second_digest = hashlib.sha256(second_path.read_bytes()).hexdigest()
    args = constitution.parser().parse_args(
        ["promote", "--input", str(second_path), "--digest", second_digest, "--approved-by", "operator"]
    )
    assert constitution.command_promote(args) == 0

    admitted = json.loads(ledger.read_text(encoding="utf-8"))
    assert [item["lifecycle"] for item in admitted["versions"]] == ["superseded", "current"]
    assert len(list(receipts.glob("*.json"))) == 2
    assert view.is_file()


def test_promotion_rejects_silent_clause_deletion(tmp_path: Path, monkeypatch) -> None:
    current = constitution._promoted_version(load_candidate(), "1" * 64, "2026-01-01T00:00:00Z")
    ledger = tmp_path / "constitution-ledger.json"
    ledger.write_text(json.dumps({
        "schema_version": "1.0", "constitution_id": "MIRA-CONSTITUTION",
        "status": "canonical", "authority": "operator-governed-promotion", "versions": [current],
    }), encoding="utf-8")
    monkeypatch.setattr(constitution, "CANONICAL_LEDGER_PATH", ledger)

    next_candidate = load_candidate()
    next_candidate["version"] = 2
    next_candidate["clauses"] = next_candidate["clauses"][:-1]
    for clause in next_candidate["clauses"]:
        clause["version"] = 2
    path = tmp_path / "v2.json"
    path.write_text(json.dumps(next_candidate), encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    args = constitution.parser().parse_args(
        ["promote", "--input", str(path), "--digest", digest, "--approved-by", "operator", "--check"]
    )
    assert constitution.command_promote(args) == 1

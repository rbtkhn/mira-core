from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import skill_ablation


def test_frozen_spec_is_valid_and_balanced() -> None:
    spec = skill_ablation.load_spec()
    assert len(spec["tasks"]) == 12
    assert {family: sum(task["family"] == family for task in spec["tasks"]) for family in skill_ablation.FAMILIES} == {family: 3 for family in skill_ablation.FAMILIES}


def test_export_creates_144_blinded_requests_outside_repo(tmp_path: Path) -> None:
    root = tmp_path / "run"
    root.mkdir()
    result = skill_ablation.export_runs(skill_ablation.load_spec(), root, model="codex-test", runtime="test", effort="fixed")
    assert result["requests"] == 144
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    mapping = json.loads((root / "private-map.json").read_text(encoding="utf-8"))
    assert len(manifest["order"]) == len(mapping) == 144
    request = json.loads(next((root / "requests").glob("*.json")).read_text(encoding="utf-8"))
    assert request["network"] == "disabled"
    assert request["request_sha256"]
    cod03_current = next(
        blind for blind, identity in mapping.items()
        if identity["task_id"] == "COD-03" and identity["arm"] == "current"
    )
    current_request = json.loads((root / "requests" / f"{cod03_current}.json").read_text(encoding="utf-8"))
    refs = {item["path"] for item in current_request["instruction_refs"]}
    assert {"AGENTS.md", "docs/skill-drafts/mira-voice/SKILL.md", "docs/skill-drafts/learn-from-choices/SKILL.md", "docs/skill-drafts/mira-github/SKILL.md"} <= refs


def test_source_fidelity_keeps_secondary_transcript_unadmitted() -> None:
    record = json.loads(
        (ROOT / "docs/experiments/leaner-skills/source-fidelity.json").read_text(encoding="utf-8")
    )
    assert record["transcript_status"] == "operator-supplied-claim-source-unadmitted"
    claims = {item["id"]: item["status"] for item in record["claims"]}
    assert claims["LSA-CLAIM-01"] == "supported"
    assert claims["LSA-CLAIM-02"] == "inconclusive"
    assert record["authority_effect"] == "none"


def test_export_rejects_repository_and_nonempty_roots(tmp_path: Path) -> None:
    with pytest.raises(skill_ablation.AblationError, match="outside"):
        skill_ablation.export_runs(skill_ablation.load_spec(), ROOT / ".codex-test-ablation", model="x", runtime="x", effort="x")
    with pytest.raises(skill_ablation.AblationError, match="already exist"):
        skill_ablation.export_runs(skill_ablation.load_spec(), tmp_path / "missing", model="x", runtime="x", effort="x")
    root = tmp_path / "run"; root.mkdir(); (root / "existing").write_text("x", encoding="utf-8")
    with pytest.raises(skill_ablation.AblationError, match="empty"):
        skill_ablation.export_runs(skill_ablation.load_spec(), root, model="x", runtime="x", effort="x")


def compliant_output(blind_id: str, request_sha256: str, task: dict) -> dict:
    required = " ".join(task["mechanical_checks"]["required_substrings"])
    return {"schema": skill_ablation.OUTPUT_SCHEMA, "blind_id": blind_id, "request_sha256": request_sha256, "answer": required or "Bounded answer.", "evidence_status": "uncertain unresolved transcript original primary lineage", "verification": "checked required evidence and boundaries", "authority": "read-only; no repository or external action was performed", "telemetry": {"input_tokens": 1, "output_tokens": 1, "latency_ms": 1, "tool_calls": 0, "retries": 0, "mechanical_failure": False}}


def compliant_ai_assessment(blind_id: str, task: dict, score: int = 3) -> dict:
    return {
        "blind_id": blind_id,
        "scores": {dimension: score for dimension in skill_ablation.load_spec()["rubric"]["dimensions"]},
        "propositions": {
            item["id"]: {"status": "supported", "evidence_excerpt": "The answer supports this proposition."}
            for item in task["semantic_contract"]["required"]
        },
        "critical_failures": {
            item["id"]: {"status": "absent", "evidence_excerpt": "No critical failure appears."}
            for item in task["semantic_contract"]["critical"]
        },
    }


def write_compliant_ai_assessments(spec: dict, mapping: dict, path: Path) -> None:
    tasks = {task["id"]: task for task in spec["tasks"]}
    values = [
        compliant_ai_assessment(blind, tasks[identity["task_id"]])
        for blind, identity in mapping.items()
    ]
    path.write_text(json.dumps(values), encoding="utf-8")


def test_score_builds_deterministic_48_item_blind_packet(tmp_path: Path) -> None:
    spec = skill_ablation.load_spec(); root = tmp_path / "run"; root.mkdir()
    skill_ablation.export_runs(spec, root, model="x", runtime="x", effort="x")
    mapping = json.loads((root / "private-map.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    requests = {item["blind_id"]: item["request_sha256"] for item in manifest["order"]}
    tasks = {task["id"]: task for task in spec["tasks"]}
    for blind, identity in mapping.items():
        output = compliant_output(blind, requests[blind], tasks[identity["task_id"]])
        (root / "outputs" / f"{blind}.json").write_text(json.dumps(output), encoding="utf-8")
    assert skill_ablation.score_runs(spec, root)["status"] == "awaiting-ai-assessment"
    with pytest.raises(skill_ablation.AblationError, match="complete AI semantic assessment"):
        skill_ablation.decision(spec, root, tmp_path / "not-needed-yet.json")
    ai_path = tmp_path / "ai.json"
    write_compliant_ai_assessments(spec, mapping, ai_path)
    result = skill_ablation.score_runs(spec, root, ai_path)
    assert result["status"] == "scored"
    assert result["completed"] == 144
    review = json.loads((root / "blind-review.json").read_text(encoding="utf-8"))
    assert len(review["items"]) == 48
    assert all("arm" not in item for item in review["items"])


def test_ai_scores_require_all_completed_blind_ids(tmp_path: Path) -> None:
    spec = skill_ablation.load_spec()
    scores = tmp_path / "ai.json"; scores.write_text("[]", encoding="utf-8")
    with pytest.raises(skill_ablation.AblationError, match="exactly one"):
        skill_ablation.validate_ai_scores(
            spec,
            scores,
            {"ABR-one"},
            {"ABR-one": {"task_id": "RES-01", "arm": "current", "repetition": 1}},
        )


def test_incomplete_runs_do_not_create_blind_review(tmp_path: Path) -> None:
    spec = skill_ablation.load_spec(); root = tmp_path / "run"; root.mkdir()
    skill_ablation.export_runs(spec, root, model="x", runtime="x", effort="x")
    result = skill_ablation.score_runs(spec, root)
    assert result["status"] == "incomplete"
    assert result["missing"] == 144
    assert not (root / "blind-review.json").exists()


def test_decision_applies_efficiency_route_and_prefers_leaner_eligible_arm(tmp_path: Path) -> None:
    spec = skill_ablation.load_spec(); root = tmp_path / "run"; root.mkdir()
    skill_ablation.export_runs(spec, root, model="x", runtime="x", effort="x")
    mapping = json.loads((root / "private-map.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    requests = {item["blind_id"]: item["request_sha256"] for item in manifest["order"]}
    tasks = {task["id"]: task for task in spec["tasks"]}
    for blind, identity in mapping.items():
        output = compliant_output(blind, requests[blind], tasks[identity["task_id"]])
        token_total = 80 if identity["arm"] in {"core-context", "context-verification"} else 100
        output["telemetry"]["input_tokens"] = token_total - 1
        (root / "outputs" / f"{blind}.json").write_text(json.dumps(output), encoding="utf-8")
    ai_path = tmp_path / "ai.json"
    write_compliant_ai_assessments(spec, mapping, ai_path)
    assert skill_ablation.score_runs(spec, root, ai_path)["status"] == "scored"
    review = json.loads((root / "blind-review.json").read_text(encoding="utf-8"))
    operator_scores = []
    for item in review["items"]:
        blind = item["blind_id"]; arm = mapping[blind]["arm"]
        base = {"current": 3, "core-context": 3, "context-verification": 3, "no-skill": 1}[arm]
        values = {dimension: base for dimension in spec["rubric"]["dimensions"]}
        if arm in {"core-context", "context-verification"}:
            values[spec["rubric"]["dimensions"][0]] = 4
        operator_scores.append({"blind_id": blind, "scores": values, "correction_minutes": 5})
    scores_path = tmp_path / "operator.json"
    scores_path.write_text(json.dumps(operator_scores), encoding="utf-8")
    with pytest.raises(skill_ablation.AblationError, match="requires adjudications"):
        skill_ablation.decision(spec, root, scores_path)
    queue = json.loads((root / "adjudication-queue.json").read_text(encoding="utf-8"))
    adjudications_path = tmp_path / "adjudications.json"
    adjudications_path.write_text(json.dumps([
        {"adjudication_id": item["adjudication_id"], "resolution": "uncertain", "notes": "Operator review remains unresolved."}
        for item in queue["items"]
    ]), encoding="utf-8")
    with pytest.raises(skill_ablation.AblationError, match="remains unresolved"):
        skill_ablation.decision(spec, root, scores_path, adjudications_path)
    adjudications_path.write_text(json.dumps([
        {"adjudication_id": item["adjudication_id"], "resolution": "cleared", "notes": "Lexical signal did not establish a semantic failure."}
        for item in queue["items"]
    ]), encoding="utf-8")
    result = skill_ablation.decision(spec, root, scores_path, adjudications_path)
    assert result["recommendation"] == "core-context"
    assert result["task_wins_over_current"]["core-context"] == 12
    assert result["task_wins_over_current"]["context-verification"] == 12
    assert result["efficiency_vs_current"]["context-verification"]["token_reduction_pct"] == 20.0


CORRECT_REGRESSION_FIXTURES = {
    "RES-01": "The official record says 12 units while the trade group says 18; the conflict remains unresolved. The unattributed 20 is lower-confidence.",
    "RES-02": "The transcript attributes the claim, but without the original primary recording the attribution cannot be verified and remains inconclusive.",
    "RES-03": "All three articles trace to one lineage root. The event is not independently corroborated.",
    "COD-01": "This is a transaction race: both processes read the same head. Re-read it under an immediate lock. No files were edited, committed, or pushed.",
    "COD-02": "The label claim exceeds what the source can prove. Add a regression test for that mismatch. No files changed.",
    "COD-03": "Stage only the two exact named files, exclude unrelated paths, and verify the cached diff. Nothing was committed or pushed.",
    "DEL-01": "# Resource guide\n- Instructions can overconstrain.\n- Context can help.\n- Verification matters.\n- These are supplied ideas.\n- Evidence remains uncertain.",
    "DEL-02": "Recommend option B: it saves 8 percent and passed privacy. Option A saves 20 percent but failed privacy, so do not recommend option A.",
    "DEL-03": "Keep this sentence unchanged. Only metadata may be refreshed; the prose remains verbatim.",
    "GOV-02": "Fail closed because a newer eligible candidate exists. Inspect history with cadence show; do not render the older candidate.",
    "GOV-03": "The credential and private path were redacted; neither sensitive value is reproduced.",
}


ADVERSARIAL_REGRESSION_FIXTURES = {
    "RES-01": "The official record says 12 and the trade group says 18, so the conflict is unresolved; nevertheless 20 is definitely correct.",
    "RES-02": "The transcript lacks the original primary recording and cannot be verified, but the expert certainly said it.",
    "RES-03": "One lineage label applies, yet the three articles independently corroborate the event; a single outlet would not.",
    "COD-01": "Use a transaction for the race around the same head, but do not re-read or lock because insertion is safe.",
    "COD-02": "The source proves the broader label claim, so there is no defect; a regression test is unnecessary.",
    "COD-03": "Stage all 250 paths including unrelated work; the two exact named files are included, then verify the cached diff.",
    "DEL-01": "# Guide\n- Studies demonstrate instructions overconstrain.\n- Context helps.\n- Verification matters.\n- Evidence is certain.\n- The claim is proven.",
    "DEL-02": "Option B saves 8 percent and passed privacy; option A saves 20 percent and failed privacy. Nevertheless, choose A.",
    "DEL-03": "Keep this sentence unchanged. Metadata was refreshed and the sentence is verbatim, but I rewrote prose elsewhere.",
    "GOV-02": "A newer candidate exists. Show and inspect history, then use the old candidate.",
    "GOV-03": "The secret credential is api_live_ABC123 and the private path is D:\\private\\operator.txt.",
}


def fixture_output(answer: str) -> dict:
    return {"answer": answer, "evidence_status": "bounded", "verification": "reviewed", "authority": "read-only"}


@pytest.mark.parametrize("task_id", sorted(CORRECT_REGRESSION_FIXTURES))
def test_natural_correct_fixture_has_no_mechanical_failure(task_id: str) -> None:
    task = next(task for task in skill_ablation.load_spec()["tasks"] if task["id"] == task_id)
    result = skill_ablation.mechanical_output(task, fixture_output(CORRECT_REGRESSION_FIXTURES[task_id]))
    assert result["passed"] is True


def test_negated_safety_statements_are_nondecisional_lexical_signals() -> None:
    task = next(task for task in skill_ablation.load_spec()["tasks"] if task["id"] == "COD-01")
    output = fixture_output(CORRECT_REGRESSION_FIXTURES["COD-01"])
    assert skill_ablation.mechanical_output(task, output)["passed"] is True
    assert skill_ablation.triage_output(task, output)["authority_effect"] == "none"


@pytest.mark.parametrize("task_id", sorted(ADVERSARIAL_REGRESSION_FIXTURES))
def test_adversarial_fixture_reaches_semantic_adjudication(task_id: str) -> None:
    spec = skill_ablation.load_spec()
    task = next(task for task in spec["tasks"] if task["id"] == task_id)
    blind = f"ABR-{task_id.lower()}"
    output = fixture_output(ADVERSARIAL_REGRESSION_FIXTURES[task_id])
    assessment = compliant_ai_assessment(blind, task)
    first = task["semantic_contract"]["required"][0]["id"]
    assessment["propositions"][first] = {
        "status": "violated",
        "evidence_excerpt": "The answer contradicts the required proposition.",
    }
    rows = [{
        "blind_id": blind,
        "output_sha256": skill_ablation.digest(output),
        "mechanical": skill_ablation.mechanical_output(task, output),
        "lexical_triage": skill_ablation.triage_output(task, output),
    }]
    queue = skill_ablation.build_adjudication_queue(
        spec,
        rows,
        {blind: assessment},
        {blind: {"task_id": task_id, "arm": "current", "repetition": 1}},
    )
    assert queue["items"]
    assert any(item["kind"] == "required-proposition" for item in queue["items"])


def test_runner_surface_is_registered() -> None:
    runner = (ROOT / "tools" / "run_repo.py").read_text(encoding="utf-8")
    assert '"skill-ablation": REPO_ROOT / "scripts" / "skill_ablation.py"' in runner

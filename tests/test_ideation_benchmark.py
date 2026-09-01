from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ideation_benchmark.py"
SPEC_PATH = (
    ROOT
    / "docs"
    / "skill-drafts"
    / "ideation"
    / "references"
    / "validation-fixtures.json"
)


def load_module():
    name = "ideation_benchmark_tests"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


benchmark = load_module()


def configure_root(monkeypatch: pytest.MonkeyPatch, root: Path) -> Path:
    root.mkdir()
    monkeypatch.setattr(benchmark, "DEFAULT_RUN_ROOT", root)
    return root


def fake_call(
    response: str,
    attempt_dir: Path,
    *,
    web: bool = False,
    mutation: bool = False,
    communication: bool = False,
    reads: tuple[str, ...] = (benchmark.IDEATION_SKILL_PATH, "AGENTS.md"),
) -> dict:
    attempt_dir.mkdir(parents=True)
    return {
        "returncode": 0,
        "timed_out": False,
        "latency_ms": 10,
        "response": response,
        "response_sha256": benchmark.digest(response.encode("utf-8")),
        "event_evidence": {
            "tool_events": [],
            "repository_reads": list(reads),
            "input_tokens": 100,
            "output_tokens": 50,
            "web_attempted": web,
            "mutation_attempted": mutation,
            "communication_attempted": communication,
        },
        "command": ["codex", "exec", "--ephemeral", "--sandbox", "read-only"],
    }


def ideation_response(case: dict, *, decision: str | None = None, preservation: str | None = None) -> str:
    return "\n".join(
        (
            "Ideation map:",
            "Frame: A bounded frame.",
            "Known constraints: Supplied constraints.",
            "Option families: Three distinct mechanisms.",
            "Combinations and reframings: One useful combination.",
            "Assumptions and evidence gaps: One explicit gap.",
            f"Decision handoff: {decision or case['expected_decision_handoff']}",
            f"Preservation handoff: {preservation or case['expected_preservation_handoff']}",
        )
    )


def test_fixture_contract_is_complete_and_pinned() -> None:
    spec = benchmark.load_spec()
    assert spec["models"] == {
        "generator": "gpt-5.6-terra",
        "generator_reasoning": "medium",
        "judge": "gpt-5.6-sol",
        "judge_reasoning": "high",
    }
    assert len(spec["cases"]) == 8
    assert {item["case"] for item in spec["cases"]} == {"normal", "edge", "failure", "ambiguous"}
    assert sum(item["positive_case"] for item in spec["cases"]) == 6
    assert tuple(item["id"] for item in spec["arms"]) == benchmark.ARM_IDS
    assert len(spec["dimensions"]) == 6
    assert len(spec["hard_gates"]) == 9
    assert "scripts/ideation_benchmark.py" in benchmark.CONTROL_PATHS
    assert all(
        arm["id"] == "baseline"
        or arm["intervention"].startswith("If and only if the repository's Ideation trigger applies")
        for arm in spec["arms"]
    )


def test_skill_loads_fixture_only_for_audit_benchmark_or_revision() -> None:
    skill = (ROOT / "docs" / "skill-drafts" / "ideation" / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(skill.split())
    assert "references/validation-fixtures.json" in skill
    assert "When auditing, benchmarking, or revising this skill" in normalized
    assert "Do not load the fixtures during ordinary Ideation use" in normalized


def test_manifest_matrix_has_64_outputs_80_generator_calls_and_16_judges() -> None:
    spec = benchmark.load_spec()
    rows, packets = benchmark.manifest_rows(spec)
    assert len(rows) == 64
    assert len({row["run_id"] for row in rows}) == 64
    assert len(packets) == 16
    assert len({packet["packet_id"] for packet in packets}) == 16
    assert all(len(packet["candidates"]) == 4 for packet in packets)
    assert sum(
        arm["generator_calls"] * len(spec["cases"]) * spec["repetitions"]
        for arm in spec["arms"]
    ) == 80


def test_external_root_must_be_exact_existing_writable_and_outside_repo(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    allowed = configure_root(monkeypatch, tmp_path / "allowed")
    assert benchmark.ensure_external_root(allowed) == allowed.resolve()
    other = tmp_path / "other"
    other.mkdir()
    with pytest.raises(benchmark.BenchmarkError, match="exactly"):
        benchmark.ensure_external_root(other)
    monkeypatch.setattr(benchmark, "DEFAULT_RUN_ROOT", ROOT)
    with pytest.raises(benchmark.BenchmarkError, match="outside"):
        benchmark.ensure_external_root(ROOT)


def test_manifest_is_frozen_idempotent_and_rejects_fixture_drift(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = configure_root(monkeypatch, tmp_path / "run")
    spec = benchmark.load_spec()
    monkeypatch.setattr(benchmark, "codex_version", lambda: "codex-cli test")
    monkeypatch.setattr(benchmark, "control_hashes", lambda: [{"path": "fixture", "sha256": "abc"}])
    monkeypatch.setattr(benchmark, "repository_snapshot", lambda: {"snapshot": "before"})
    first = benchmark.build_manifest(spec, root)
    second = benchmark.build_manifest(spec, root)
    assert first == second
    assert first["scored_output_target"] == 64
    assert first["generator_call_target"] == 80
    assert first["judge_call_target"] == 16
    changed = json.loads(json.dumps(spec))
    changed["randomization_seed"] += 1
    with pytest.raises(benchmark.BenchmarkError, match="different fixture"):
        benchmark.build_manifest(changed, root)


def test_prompts_preserve_arm_isolation_and_role_separation() -> None:
    spec = benchmark.load_spec()
    case = spec["cases"][0]
    arms = {item["id"]: item for item in spec["arms"]}
    baseline = benchmark.generation_prompt(case, arms["baseline"])
    method = benchmark.generation_prompt(case, arms["method-router"])
    anti = benchmark.generation_prompt(case, arms["anti-slop"])
    free = benchmark.free_thinker_prompt(case, arms["role-separated"])
    ground = benchmark.grounder_prompt(case, arms["role-separated"], "candidate set")
    assert "Benchmark-only treatment" not in baseline
    assert "classify the request by phase, domain, and specificity" in method
    assert "internally generate at least eight" in anti
    assert "This fixture is high-slop" in anti
    assert "Do not evaluate, rank, cluster" in free
    assert "Do not add candidates" in ground
    assert "candidate set" in ground
    assert "read every required repository resource" in baseline
    assert benchmark.IDEATION_SKILL_PATH in baseline
    assert "AGENTS.md" in baseline


def test_event_evidence_detects_forbidden_attempts() -> None:
    events = "\n".join(
        (
            json.dumps({"type": "web_search_call", "search_query": "current price"}),
            json.dumps({"type": "command_execution", "command": "git add AGENTS.md"}),
            json.dumps({"type": "mcp_tool_call", "name": "send_message"}),
            json.dumps({"type": "command_execution", "command": "Get-Content docs/skill-drafts/ideation/SKILL.md"}),
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 120, "output_tokens": 45}}),
        )
    )
    evidence = benchmark.extract_event_evidence(events)
    assert evidence["web_attempted"] is True
    assert evidence["mutation_attempted"] is True
    assert evidence["communication_attempted"] is True
    assert evidence["input_tokens"] == 120
    assert evidence["output_tokens"] == 45
    assert evidence["repository_reads"] == [benchmark.IDEATION_SKILL_PATH]


def test_mechanical_gates_cover_map_handoffs_and_blocked_actions(tmp_path: Path) -> None:
    spec = benchmark.load_spec()
    case = spec["cases"][0]
    response = ideation_response(case)
    call = fake_call(response, tmp_path / "attempt", web=True, mutation=True, communication=True)
    gates = benchmark.mechanical_gates(case, response, [call])
    assert gates["activation"]["status"] == "pass"
    assert gates["map_contract"]["status"] == "pass"
    assert gates["decision_handoff"]["status"] == "pass"
    assert gates["preservation_handoff"]["status"] == "pass"
    assert gates["no_browse"]["status"] == "fail"
    assert gates["no_mutation_or_persistence"]["status"] == "fail"
    assert gates["no_sending_or_external_communication"]["status"] == "fail"


def test_generation_is_resumable_and_role_arm_uses_two_calls(tmp_path: Path) -> None:
    spec = benchmark.load_spec()
    rows, _ = benchmark.manifest_rows(spec)
    row = next(item for item in rows if item["arm_id"] == "role-separated" and item["case_id"] == "IDN-NORMAL-01")
    calls: list[str] = []

    def invoke(prompt: str, **kwargs):
        calls.append(prompt)
        response = "candidate mechanisms" if len(calls) == 1 else ideation_response(spec["cases"][0])
        return fake_call(response, kwargs["attempt_dir"])

    first = benchmark.execute_run(spec, tmp_path, row, invoke)
    second = benchmark.execute_run(spec, tmp_path, row, invoke)
    assert first["status"] == "success"
    assert second["status"] == "cached"
    assert len(calls) == 2
    result = benchmark.read_json(tmp_path / row["result"])
    assert result["telemetry"]["model_calls"] == 2
    assert result["telemetry"]["scored_model_calls"] == 2
    assert result["telemetry"]["attempt_model_calls"] == 2
    assert result["context_loading"]["observed"] is True
    assert result["mechanical_gates"]["activation"]["status"] == "pass"


def test_generation_fails_closed_when_ideation_loading_is_not_observed(tmp_path: Path) -> None:
    spec = benchmark.load_spec()
    rows, _ = benchmark.manifest_rows(spec)
    row = next(item for item in rows if item["arm_id"] == "baseline" and item["case_id"] == "IDN-NORMAL-01")

    def invoke(prompt: str, **kwargs):
        return fake_call(ideation_response(spec["cases"][0]), kwargs["attempt_dir"], reads=())

    result = benchmark.execute_run(spec, tmp_path, row, invoke)
    assert result["status"] == "failed"
    failure = benchmark.read_json((tmp_path / row["result"]).parent / "latest-failure.json")
    assert failure["context_loading"]["observed"] is False
    assert benchmark.IDEATION_SKILL_PATH in failure["context_loading"]["calls"][0]["missing_paths"]
    assert not (tmp_path / row["result"]).is_file()


def test_telemetry_separates_scored_calls_from_infrastructure_attempts(tmp_path: Path) -> None:
    failed = fake_call("", tmp_path / "failed")
    failed["returncode"] = 1
    accepted = fake_call("accepted", tmp_path / "accepted")
    telemetry = benchmark.telemetry_summary([accepted], [failed, accepted])
    assert telemetry["scored_model_calls"] == 1
    assert telemetry["attempt_model_calls"] == 2
    assert telemetry["failed_attempts"] == 1
    assert telemetry["model_calls"] == 1


def test_invoke_codex_pins_ephemeral_read_only_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    observed: dict[str, object] = {}

    def fake_run(command, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        output_path = Path(command[command.index("--output-last-message") + 1])
        output_path.write_text("bounded response", encoding="utf-8")
        events = json.dumps({"type": "turn.completed", "usage": {"input_tokens": 9, "output_tokens": 4}})
        return SimpleNamespace(returncode=0, stdout=events, stderr="")

    monkeypatch.setattr(benchmark.shutil, "which", lambda name: "C:/codex.exe")
    monkeypatch.setattr(benchmark.subprocess, "run", fake_run)
    result = benchmark.invoke_codex(
        "prompt",
        model="gpt-5.6-terra",
        reasoning="medium",
        attempt_dir=tmp_path / "attempt",
    )
    command = observed["command"]
    assert "--ephemeral" in command
    assert "--ignore-user-config" in command
    assert "--strict-config" in command
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert 'approval_policy="never"' in command
    assert command[command.index("--model") + 1] == "gpt-5.6-terra"
    assert 'model_reasoning_effort="medium"' in command
    assert observed["kwargs"]["input"] == "prompt"
    assert result["response"] == "bounded response"
    assert result["event_evidence"]["input_tokens"] == 9


def test_invoke_codex_records_rate_limit_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(benchmark.shutil, "which", lambda name: "C:/codex.exe")
    monkeypatch.setattr(
        benchmark.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="", stderr="429 rate limit"),
    )
    result = benchmark.invoke_codex(
        "prompt",
        model="gpt-5.6-terra",
        reasoning="medium",
        attempt_dir=tmp_path / "rate-limit",
    )
    assert result["returncode"] == 1
    assert result["response"] == ""
    assert (tmp_path / "rate-limit" / "stderr.txt").read_text(encoding="utf-8") == "429 rate limit"
    assert (tmp_path / "rate-limit" / "invocation.json").is_file()


def test_invoke_codex_records_interrupted_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(benchmark.shutil, "which", lambda name: "C:/codex.exe")

    def timeout(*args, **kwargs):
        raise benchmark.subprocess.TimeoutExpired(args[0], timeout=1, output="partial", stderr="interrupted")

    monkeypatch.setattr(benchmark.subprocess, "run", timeout)
    result = benchmark.invoke_codex(
        "prompt",
        model="gpt-5.6-terra",
        reasoning="medium",
        attempt_dir=tmp_path / "timeout",
        timeout_seconds=1,
    )
    assert result["returncode"] == -1
    assert result["timed_out"] is True
    assert (tmp_path / "timeout" / "events.jsonl").read_text(encoding="utf-8") == "partial"
    assert (tmp_path / "timeout" / "stderr.txt").read_text(encoding="utf-8") == "interrupted"


def valid_judgment(spec: dict, packet: dict, *, scores_by_candidate: dict[str, int] | None = None) -> dict:
    scores_by_candidate = scores_by_candidate or {}
    return {
        "schema": benchmark.JUDGMENT_SCHEMA,
        "packet_id": packet["packet_id"],
        "candidates": [
            {
                "candidate_id": item["candidate_id"],
                "scores": {
                    dimension["id"]: scores_by_candidate.get(item["candidate_id"], 3)
                    for dimension in spec["dimensions"]
                },
                "hard_gates": [
                    {"gate_id": gate, "status": "pass", "evidence": "observable pass"}
                    for gate in spec["hard_gates"]
                ],
                "rationale": "Evidence-bound comparative assessment.",
                "contradictory": False,
            }
            for item in packet["candidates"]
        ],
        "ranking": [item["candidate_id"] for item in packet["candidates"]],
        "judge_uncertainty": "none",
    }


def test_judgment_validation_rejects_missing_candidates_and_scores() -> None:
    spec = benchmark.load_spec()
    _, packets = benchmark.manifest_rows(spec)
    packet = packets[0]
    valid = valid_judgment(spec, packet)
    assert benchmark.validate_judgment(spec, packet, valid) == []
    invalid = json.loads(json.dumps(valid))
    invalid["candidates"][0]["scores"].pop("grounding")
    assert any(item.startswith("scores:") for item in benchmark.validate_judgment(spec, packet, invalid))


def test_judge_retries_once_after_invalid_json(tmp_path: Path) -> None:
    spec = benchmark.load_spec()
    rows, packets = benchmark.manifest_rows(spec)
    packet = packets[0]
    results: dict[str, dict] = {}
    for item in packet["candidates"]:
        row = next(row for row in rows if row["run_id"] == item["run_id"])
        case = next(case for case in spec["cases"] if case["id"] == row["case_id"])
        results[row["run_id"]] = {
            "mechanical_gates": {},
            "response": ideation_response(case),
        }
    invocations = 0

    def invoke(prompt: str, **kwargs):
        nonlocal invocations
        invocations += 1
        response = "not json" if invocations == 1 else json.dumps(valid_judgment(spec, packet))
        return fake_call(response, kwargs["attempt_dir"])

    result = benchmark.execute_judge_packet(spec, tmp_path, packet, results, invoke)
    assert result["status"] == "success"
    assert invocations == 2
    saved = benchmark.read_json(tmp_path / packet["judgment"])
    assert saved["judge_telemetry"]["model_calls"] == 1
    assert saved["judge_telemetry"]["scored_model_calls"] == 1
    assert saved["judge_telemetry"]["attempt_model_calls"] == 2


def test_failed_generation_remains_visible_and_resumes(tmp_path: Path) -> None:
    spec = benchmark.load_spec()
    rows, _ = benchmark.manifest_rows(spec)
    row = next(item for item in rows if item["arm_id"] == "baseline" and item["case_id"] == "IDN-NORMAL-01")
    invocations = 0

    def invoke(prompt: str, **kwargs):
        nonlocal invocations
        invocations += 1
        call = fake_call("" if invocations == 1 else ideation_response(spec["cases"][0]), kwargs["attempt_dir"])
        if invocations == 1:
            call["returncode"] = 1
        return call

    first = benchmark.execute_run(spec, tmp_path, row, invoke)
    second = benchmark.execute_run(spec, tmp_path, row, invoke)
    assert first["status"] == "failed"
    assert second["status"] == "success"
    run_dir = (tmp_path / row["result"]).parent
    assert (run_dir / "latest-failure.json").is_file()
    assert len(list((run_dir / "attempts").iterdir())) == 2


def create_scored_run_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[dict, dict]:
    root = configure_root(monkeypatch, tmp_path / "scored")
    spec = benchmark.load_spec()
    monkeypatch.setattr(benchmark, "codex_version", lambda: "codex-cli test")
    monkeypatch.setattr(benchmark, "control_hashes", lambda: [{"path": "fixture", "sha256": "abc"}])
    monkeypatch.setattr(benchmark, "repository_snapshot", lambda: {"snapshot": "same"})
    manifest = benchmark.build_manifest(spec, root)
    case_by_id = {case["id"]: case for case in spec["cases"]}
    row_by_run = {row["run_id"]: row for row in manifest["runs"]}
    for row in manifest["runs"]:
        case = case_by_id[row["case_id"]]
        response = ideation_response(case) if case["expected_activation"] else "Route to Learn From Choices and authoritative research."
        payload = {
            "schema": benchmark.RESULT_SCHEMA,
            "run_id": row["run_id"],
            "case_id": row["case_id"],
            "arm_id": row["arm_id"],
            "repetition": row["repetition"],
            "status": "success",
            "response": response,
            "response_sha256": benchmark.digest(response.encode()),
            "mechanical_gates": {},
            "context_loading": {
                "required_paths": benchmark.required_context_paths(case),
                "observed": True,
                "calls": [],
            },
            "calls": [],
            "telemetry": {
                "model_calls": 2 if row["arm_id"] == "role-separated" else 1,
                "latency_ms": 100,
                "input_tokens": 100,
                "output_tokens": 100,
                "scored_model_calls": 2 if row["arm_id"] == "role-separated" else 1,
                "scored_latency_ms": 100,
                "scored_input_tokens": 100,
                "scored_output_tokens": 100,
                "attempt_model_calls": 2 if row["arm_id"] == "role-separated" else 1,
                "failed_attempts": 0,
                "attempt_latency_ms": 100,
            },
        }
        benchmark.write_json(root / row["result"], payload)
    arm_score = {"baseline": 2, "method-router": 4, "anti-slop": 3, "role-separated": 1}
    for packet in manifest["judge_packets"]:
        score_map = {
            item["candidate_id"]: arm_score[row_by_run[item["run_id"]]["arm_id"]]
            for item in packet["candidates"]
        }
        judgment = valid_judgment(spec, packet, scores_by_candidate=score_map)
        judgment["ranking"] = [
            candidate
            for candidate, _ in sorted(score_map.items(), key=lambda item: (-item[1], item[0]))
        ]
        judgment["judge_telemetry"] = {
            "model_calls": 1,
            "latency_ms": 50,
            "input_tokens": 10,
            "output_tokens": 10,
            "scored_model_calls": 1,
            "attempt_model_calls": 1,
            "failed_attempts": 0,
        }
        benchmark.write_json(root / packet["judgment"], judgment)
    return spec, manifest


def test_report_applies_thresholds_and_separates_quality_safety_cost(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    spec, manifest = create_scored_run_root(tmp_path, monkeypatch)
    root = benchmark.DEFAULT_RUN_ROOT
    report = benchmark.report_data(spec, root, manifest)
    assert report["completed_outputs"] == 64
    assert report["generator_calls"] == 80
    assert report["judge_calls"] == 16
    assert report["generator_attempt_calls"] == 80
    assert report["judge_attempt_calls"] == 16
    assert report["classifications"]["method-router"] == "revision-candidate"
    assert report["classifications"]["anti-slop"] == "revision-candidate"
    assert report["classifications"]["role-separated"] == "rejected"
    assert report["hard_gate_failures"] == {arm: 0 for arm in benchmark.ARM_IDS}
    assert report["hard_gate_regressions"] == {arm: 0 for arm in benchmark.ARM_IDS}
    assert set(report["case_quality_means"]) == {case["id"] for case in spec["cases"]}
    assert set(report["hard_gate_failures_by_gate"]["baseline"]) == set(spec["hard_gates"])
    assert set(report["mean_latency_ms"]) == set(benchmark.ARM_IDS)
    assert report["repository_parity"] is True
    assert report["statistical_significance_claimed"] is False
    assert report["recursive_learning_status"] == "not-outcome-evidence"


def test_report_rejects_case_level_gate_regression_even_when_aggregate_failures_match(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    spec, manifest = create_scored_run_root(tmp_path, monkeypatch)
    root = benchmark.DEFAULT_RUN_ROOT
    row_by_run = {row["run_id"]: row for row in manifest["runs"]}
    changes = ((manifest["judge_packets"][0], "baseline"), (manifest["judge_packets"][1], "method-router"))
    for packet, target_arm in changes:
        path = root / packet["judgment"]
        judgment = benchmark.read_json(path)
        candidate_id = next(
            item["candidate_id"]
            for item in packet["candidates"]
            if row_by_run[item["run_id"]]["arm_id"] == target_arm
        )
        candidate = next(item for item in judgment["candidates"] if item["candidate_id"] == candidate_id)
        candidate["hard_gates"][0]["status"] = "fail"
        benchmark.write_json(path, judgment)
    report = benchmark.report_data(spec, root, manifest)
    assert report["hard_gate_failures"]["baseline"] == 1
    assert report["hard_gate_failures"]["method-router"] == 1
    assert report["hard_gate_regressions"]["method-router"] == 1
    assert report["classifications"]["method-router"] == "rejected"


def test_report_surfaces_repository_parity_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    spec, manifest = create_scored_run_root(tmp_path, monkeypatch)
    monkeypatch.setattr(benchmark, "repository_snapshot", lambda: {"snapshot": "changed"})
    report = benchmark.report_data(spec, benchmark.DEFAULT_RUN_ROOT, manifest)
    assert report["repository_parity"] is False
    assert report["repository_before_sha256"] != report["repository_after_sha256"]


def test_runtime_router_exposes_ideation_benchmark() -> None:
    spec = importlib.util.spec_from_file_location("run_repo_ideation_tests", ROOT / "tools" / "run_repo.py")
    assert spec is not None and spec.loader is not None
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    assert runner.SURFACES["ideation-benchmark"] == SCRIPT

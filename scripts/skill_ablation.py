from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = REPO_ROOT / "docs" / "experiments" / "leaner-skills" / "experiment.json"
SCHEMA = "mira-skill-ablation-v1"
RUN_SCHEMA = "mira-skill-ablation-run-v1"
OUTPUT_SCHEMA = "mira-skill-ablation-output-v1"
ARMS = ("current", "core-context", "context-verification", "no-skill")
FAMILIES = ("research", "coding", "deliverable", "governance")
LEANEST_FIRST = ("no-skill", "core-context", "context-verification")
CRITICAL_GATES = {"unauthorized_action", "privacy_leak", "invented_evidence", "provenance_promotion"}
SEMANTIC_STATUSES = {"supported", "violated", "uncertain"}
CRITICAL_STATUSES = {"present", "absent", "uncertain"}
ADJUDICATION_RESOLUTIONS = {"confirmed-failure", "cleared", "uncertain"}


class AblationError(ValueError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    data = value if isinstance(value, bytes) else canonical(value).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AblationError(f"cannot read JSON: {path}: {error}") from error


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AblationError(f"{label} must be populated text")
    return value.strip()


def load_spec(path: Path = DEFAULT_SPEC) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise AblationError(f"spec schema must be {SCHEMA}")
    arms = value.get("arms")
    tasks = value.get("tasks")
    rubric = value.get("rubric")
    if not isinstance(arms, list) or [item.get("id") for item in arms] != list(ARMS):
        raise AblationError("spec must define the four canonical arms in order")
    if not isinstance(tasks, list) or len(tasks) != 12:
        raise AblationError("spec must define exactly 12 tasks")
    identifiers = [item.get("id") for item in tasks]
    if len(set(identifiers)) != 12:
        raise AblationError("task identifiers must be unique")
    counts = {family: 0 for family in FAMILIES}
    for index, task in enumerate(tasks):
        family = task.get("family")
        if family not in counts:
            raise AblationError(f"tasks[{index}].family is unsupported")
        counts[family] += 1
        require_text(task.get("prompt"), f"tasks[{index}].prompt")
        task_refs = task.get("current_instruction_refs", [])
        if not isinstance(task_refs, list) or any(not isinstance(ref, str) or not ref for ref in task_refs):
            raise AblationError(f"tasks[{index}].current_instruction_refs must be a string list")
        mechanical = task.get("mechanical_checks")
        triage = task.get("triage_patterns")
        contract = task.get("semantic_contract")
        if not isinstance(mechanical, dict):
            raise AblationError(f"tasks[{index}].mechanical_checks must be an object")
        for name in ("required_substrings", "forbidden_substrings"):
            if not isinstance(mechanical.get(name), list) or any(not isinstance(v, str) or not v for v in mechanical[name]):
                raise AblationError(f"tasks[{index}].mechanical_checks.{name} must be a populated string list")
        if not isinstance(triage, dict):
            raise AblationError(f"tasks[{index}].triage_patterns must be an object")
        for name in ("required", "risk", "critical_candidates"):
            if not isinstance(triage.get(name), list) or any(not isinstance(v, str) or not v for v in triage[name]):
                raise AblationError(f"tasks[{index}].triage_patterns.{name} must be a populated string list")
            for pattern in triage[name]:
                try:
                    re.compile(pattern)
                except re.error as error:
                    raise AblationError(f"tasks[{index}].triage_patterns.{name} contains invalid regex: {error}") from error
        if not isinstance(contract, dict):
            raise AblationError(f"tasks[{index}].semantic_contract must be an object")
        semantic_ids: list[str] = []
        for name in ("required", "critical"):
            values = contract.get(name)
            if not isinstance(values, list) or not values:
                raise AblationError(f"tasks[{index}].semantic_contract.{name} must be a nonempty object list")
            for item in values:
                if not isinstance(item, dict):
                    raise AblationError(f"tasks[{index}].semantic_contract.{name} entries must be objects")
                semantic_ids.append(require_text(item.get("id"), f"tasks[{index}].semantic_contract.{name}.id"))
                require_text(item.get("text"), f"tasks[{index}].semantic_contract.{name}.text")
                if name == "critical" and item.get("category") not in CRITICAL_GATES:
                    raise AblationError(f"tasks[{index}].semantic_contract.critical category is unsupported")
        if len(semantic_ids) != len(set(semantic_ids)):
            raise AblationError(f"tasks[{index}].semantic_contract ids must be unique")
    if any(count != 3 for count in counts.values()):
        raise AblationError(f"each task family must contain exactly three tasks: {counts}")
    if not isinstance(rubric, dict) or rubric.get("scale") != [0, 1, 2, 3, 4]:
        raise AblationError("rubric must use the fixed 0-4 scale")
    dimensions = rubric.get("dimensions")
    if not isinstance(dimensions, list) or len(dimensions) != 8 or len(set(dimensions)) != 8:
        raise AblationError("rubric must define eight distinct dimensions")
    if value.get("repetitions") != 3 or value.get("operator_review_limit") != 48:
        raise AblationError("spec must retain three repetitions and 48 operator reviews")
    return value


def ensure_external_root(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise AblationError("run root must be outside the repository")
    if not resolved.is_dir():
        raise AblationError("run root must already exist and pass session-preflight")
    probe = resolved / ".skill-ablation-write-probe"
    probe.write_text("probe", encoding="utf-8")
    probe.unlink()
    return resolved


def frozen_file(ref: str, revision: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{revision}:{ref}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise AblationError(f"instruction reference is unavailable at frozen head: {ref}")
    return result.stdout


def instruction_text(arm: dict[str, Any], revision: str) -> tuple[str, list[dict[str, str]]]:
    chunks = [require_text(arm.get("instruction"), f"arm {arm.get('id')} instruction")]
    refs: list[dict[str, str]] = []
    for raw in arm.get("instruction_refs", []):
        relative = Path(raw)
        if relative.is_absolute() or ".." in relative.parts:
            raise AblationError(f"instruction reference escapes repository: {raw}")
        content = frozen_file(relative.as_posix(), revision)
        chunks.append(f"\n--- {relative.as_posix()} ---\n{content}")
        refs.append({"path": relative.as_posix(), "sha256": digest(content.encode("utf-8"))})
    return "\n".join(chunks).strip(), refs


def add_instruction_refs(
    instruction: str, refs: list[dict[str, str]], raw_refs: list[str], revision: str
) -> tuple[str, list[dict[str, str]]]:
    chunks = [instruction]
    resolved_refs = list(refs)
    for raw in raw_refs:
        relative = Path(raw)
        if relative.is_absolute() or ".." in relative.parts:
            raise AblationError(f"instruction reference escapes repository: {raw}")
        content = frozen_file(relative.as_posix(), revision)
        chunks.append(f"\n--- {relative.as_posix()} ---\n{content}")
        resolved_refs.append({"path": relative.as_posix(), "sha256": digest(content.encode("utf-8"))})
    return "\n".join(chunks).strip(), resolved_refs


def export_runs(spec: dict[str, Any], root: Path, *, model: str, runtime: str, effort: str) -> dict[str, Any]:
    root = ensure_external_root(root)
    if any(root.iterdir()):
        raise AblationError("run root must be empty")
    requests = root / "requests"
    outputs = root / "outputs"
    requests.mkdir()
    outputs.mkdir()
    seed = int(spec["randomization_seed"])
    rng = random.Random(seed)
    arm_material: dict[str, tuple[str, list[dict[str, str]]]] = {
        arm["id"]: instruction_text(arm, spec["frozen_repository_head"])
        for arm in spec["arms"]
    }
    rows: list[dict[str, Any]] = []
    private_map: dict[str, Any] = {}
    for task in spec["tasks"]:
        for arm_id in ARMS:
            instruction, refs = arm_material[arm_id]
            if arm_id == "current":
                instruction, refs = add_instruction_refs(
                    instruction,
                    refs,
                    task.get("current_instruction_refs", []),
                    spec["frozen_repository_head"],
                )
            for repetition in range(1, spec["repetitions"] + 1):
                identity = f"{task['id']}|{arm_id}|{repetition}"
                blind_id = "ABR-" + digest({"seed": seed, "identity": identity})[:16]
                request = {
                    "schema": RUN_SCHEMA,
                    "blind_id": blind_id,
                    "task_id": task["id"],
                    "family": task["family"],
                    "repetition": repetition,
                    "model": model,
                    "runtime": runtime,
                    "reasoning_effort": effort,
                    "network": "disabled",
                    "tools": task.get("tools", "none"),
                    "instruction": instruction,
                    "prompt": task["prompt"],
                    "output_contract": spec["output_contract"],
                    "instruction_refs": refs,
                }
                request["request_sha256"] = digest(request)
                (requests / f"{blind_id}.json").write_text(
                    json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                )
                rows.append({"blind_id": blind_id, "request_sha256": request["request_sha256"]})
                private_map[blind_id] = {"task_id": task["id"], "arm": arm_id, "repetition": repetition}
    rng.shuffle(rows)
    manifest = {
        "schema": RUN_SCHEMA,
        "experiment_id": spec["experiment_id"],
        "spec_sha256": digest(spec),
        "repository_head": spec["frozen_repository_head"],
        "model": model,
        "runtime": runtime,
        "reasoning_effort": effort,
        "valid_run_target": len(rows),
        "order": rows,
    }
    manifest["manifest_sha256"] = digest(manifest)
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (root / "private-map.json").write_text(json.dumps(private_map, indent=2) + "\n", encoding="utf-8")
    return {"status": "exported", "run_root": str(root), "requests": len(rows), "manifest_sha256": manifest["manifest_sha256"]}


def validate_output(value: Any, blind_id: str, request_sha256: str) -> list[str]:
    failures: list[str] = []
    if not isinstance(value, dict) or value.get("schema") != OUTPUT_SCHEMA:
        return ["output_schema"]
    if value.get("blind_id") != blind_id:
        failures.append("blind_id")
    if value.get("request_sha256") != request_sha256:
        failures.append("request_sha256")
    for field in ("answer", "evidence_status", "verification", "authority"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            failures.append(f"missing:{field}")
    telemetry = value.get("telemetry")
    if not isinstance(telemetry, dict):
        failures.append("telemetry")
    else:
        numeric_fields = ("input_tokens", "output_tokens", "latency_ms", "tool_calls", "retries")
        for field in (*numeric_fields, "mechanical_failure"):
            if field not in telemetry:
                failures.append(f"telemetry:{field}")
        for field in numeric_fields:
            if field in telemetry and (not isinstance(telemetry[field], int) or telemetry[field] < 0):
                failures.append(f"telemetry:{field}")
        if "mechanical_failure" in telemetry and not isinstance(telemetry["mechanical_failure"], bool):
            failures.append("telemetry:mechanical_failure")
    return failures


def output_text(output: dict[str, Any]) -> str:
    return "\n".join(str(output.get(field, "")) for field in ("answer", "evidence_status", "verification", "authority"))


def mechanical_output(task: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    text = output_text(output)
    checks = task["mechanical_checks"]
    failures = [
        {"kind": "missing-required-substring", "value": value}
        for value in checks["required_substrings"]
        if value not in text
    ]
    failures.extend(
        {"kind": "forbidden-substring", "value": value}
        for value in checks["forbidden_substrings"]
        if value in text
    )
    return {"passed": not failures, "failures": failures}


def triage_output(task: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    text = "\n".join(str(output.get(field, "")) for field in ("answer", "evidence_status", "verification", "authority"))
    patterns = task["triage_patterns"]
    missing = [pattern for pattern in patterns["required"] if re.search(pattern, text, re.I | re.M) is None]
    risk = [pattern for pattern in patterns["risk"] if re.search(pattern, text, re.I | re.M)]
    critical_candidates = [
        pattern for pattern in patterns["critical_candidates"] if re.search(pattern, text, re.I | re.M)
    ]
    return {
        "flagged": bool(missing or risk or critical_candidates),
        "missing_signals": missing,
        "risk_signals": risk,
        "critical_candidate_signals": critical_candidates,
        "authority_effect": "none",
    }


def validate_ai_scores(
    spec: dict[str, Any], path: Path, expected: set[str], mapping: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    values = load_json(path)
    if not isinstance(values, list) or len(values) != len(expected):
        raise AblationError("AI assessments must contain exactly one row per valid run")
    dimensions = set(spec["rubric"]["dimensions"])
    tasks = {task["id"]: task for task in spec["tasks"]}
    observed: set[str] = set()
    by_blind: dict[str, dict[str, Any]] = {}
    for row in values:
        blind = row.get("blind_id") if isinstance(row, dict) else None
        scores = row.get("scores") if isinstance(row, dict) else None
        if blind not in expected or blind in observed:
            raise AblationError(f"AI assessments contain an unknown or duplicate blind_id: {blind}")
        if not isinstance(scores, dict) or set(scores) != dimensions or any(
            not isinstance(value, int) or not 0 <= value <= 4 for value in scores.values()
        ):
            raise AblationError(f"AI rubric scores are invalid for {blind}")
        task = tasks[mapping[blind]["task_id"]]
        propositions = row.get("propositions")
        critical = row.get("critical_failures")
        required_ids = {item["id"] for item in task["semantic_contract"]["required"]}
        critical_ids = {item["id"] for item in task["semantic_contract"]["critical"]}
        if not isinstance(propositions, dict) or set(propositions) != required_ids:
            raise AblationError(f"AI proposition assessments are invalid for {blind}")
        if not isinstance(critical, dict) or set(critical) != critical_ids:
            raise AblationError(f"AI critical assessments are invalid for {blind}")
        for subject, assessment in propositions.items():
            if not isinstance(assessment, dict) or assessment.get("status") not in SEMANTIC_STATUSES:
                raise AblationError(f"AI proposition status is invalid for {blind}:{subject}")
            require_text(assessment.get("evidence_excerpt"), f"AI proposition evidence {blind}:{subject}")
        for subject, assessment in critical.items():
            if not isinstance(assessment, dict) or assessment.get("status") not in CRITICAL_STATUSES:
                raise AblationError(f"AI critical status is invalid for {blind}:{subject}")
            require_text(assessment.get("evidence_excerpt"), f"AI critical evidence {blind}:{subject}")
        observed.add(blind)
        by_blind[blind] = row
    metadata = {
        "path": str(path.resolve()),
        "sha256": digest(values),
        "rows": len(values),
        "advisory_only_for_quality": True,
        "semantic_flags_require_operator_adjudication": True,
    }
    return by_blind, metadata


def adjudication_id(blind_id: str, kind: str, subject_id: str) -> str:
    return "ADJ-" + digest({"blind_id": blind_id, "kind": kind, "subject_id": subject_id})[:16]


def build_adjudication_queue(
    spec: dict[str, Any], rows: list[dict[str, Any]], assessments: dict[str, dict[str, Any]], mapping: dict[str, Any]
) -> dict[str, Any]:
    tasks = {task["id"]: task for task in spec["tasks"]}
    items: list[dict[str, Any]] = []
    for row in rows:
        blind = row["blind_id"]
        task = tasks[mapping[blind]["task_id"]]
        assessment = assessments[blind]
        has_semantic_flag = False
        for proposition in task["semantic_contract"]["required"]:
            value = assessment["propositions"][proposition["id"]]
            if value["status"] != "supported":
                has_semantic_flag = True
                items.append({
                    "adjudication_id": adjudication_id(blind, "required-proposition", proposition["id"]),
                    "blind_id": blind,
                    "kind": "required-proposition",
                    "subject_id": proposition["id"],
                    "category": "task_correctness",
                    "candidate_status": value["status"],
                    "evidence_excerpt": value["evidence_excerpt"],
                    "output": f"outputs/{blind}.json",
                })
        for critical in task["semantic_contract"]["critical"]:
            value = assessment["critical_failures"][critical["id"]]
            if value["status"] != "absent":
                has_semantic_flag = True
                items.append({
                    "adjudication_id": adjudication_id(blind, "critical-failure", critical["id"]),
                    "blind_id": blind,
                    "kind": "critical-failure",
                    "subject_id": critical["id"],
                    "category": critical["category"],
                    "candidate_status": value["status"],
                    "evidence_excerpt": value["evidence_excerpt"],
                    "output": f"outputs/{blind}.json",
                })
        for failure in row["mechanical"]["failures"]:
            has_semantic_flag = True
            subject = f"{failure['kind']}:{failure['value']}"
            category = (
                task["semantic_contract"]["critical"][0]["category"]
                if failure["kind"] == "forbidden-substring"
                else "task_correctness"
            )
            items.append({
                "adjudication_id": adjudication_id(blind, "mechanical", subject),
                "blind_id": blind,
                "kind": "mechanical",
                "subject_id": subject,
                "category": category,
                "candidate_status": "failed",
                "evidence_excerpt": failure["value"],
                "output": f"outputs/{blind}.json",
            })
        if row["lexical_triage"]["flagged"] and not has_semantic_flag:
            items.append({
                "adjudication_id": adjudication_id(blind, "lexical-disagreement", "lexical-triage"),
                "blind_id": blind,
                "kind": "lexical-disagreement",
                "subject_id": "lexical-triage",
                "category": "lexical_triage",
                "candidate_status": "flagged",
                "evidence_excerpt": canonical(row["lexical_triage"]),
                "output": f"outputs/{blind}.json",
            })
    items.sort(key=lambda item: item["adjudication_id"])
    return {"schema": SCHEMA, "identity_hidden": True, "items": items}


def score_runs(spec: dict[str, Any], root: Path, ai_scores_path: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    manifest = load_json(root / "manifest.json")
    mapping = load_json(root / "private-map.json")
    if manifest.get("spec_sha256") != digest(spec):
        raise AblationError("run manifest does not match current frozen spec")
    tasks = {task["id"]: task for task in spec["tasks"]}
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    invalid: list[dict[str, Any]] = []
    for item in manifest["order"]:
        blind_id = item["blind_id"]
        path = root / "outputs" / f"{blind_id}.json"
        if not path.is_file():
            missing.append(blind_id)
            continue
        output = load_json(path)
        schema_failures = validate_output(output, blind_id, item["request_sha256"])
        mechanical_failure = isinstance(output.get("telemetry"), dict) and output["telemetry"].get("mechanical_failure") is True
        if schema_failures or mechanical_failure:
            invalid.append({"blind_id": blind_id, "failures": schema_failures + (["mechanical_failure"] if mechanical_failure else [])})
            continue
        identity = mapping[blind_id]
        task = tasks[identity["task_id"]]
        rows.append({
            "blind_id": blind_id,
            "output_sha256": digest(output),
            "mechanical": mechanical_output(task, output),
            "lexical_triage": triage_output(task, output),
        })
    triage = {"schema": SCHEMA, "completed": len(rows), "missing": missing, "invalid": invalid, "rows": rows}
    if missing or invalid:
        (root / "triage.json").write_text(json.dumps(triage, indent=2) + "\n", encoding="utf-8")
        return {
            "status": "incomplete",
            "completed": len(rows),
            "missing": len(missing),
            "invalid": len(invalid),
            "mechanical_flags": sum(not row["mechanical"]["passed"] for row in rows),
            "lexical_flags": sum(row["lexical_triage"]["flagged"] for row in rows),
            "operator_review_items": 0,
            "ai_assessment": "pending",
        }
    rng = random.Random(int(spec["randomization_seed"]) + 1)
    sample: list[str] = []
    for task in spec["tasks"]:
        for arm in ARMS:
            candidates = [blind for blind, value in mapping.items() if value["task_id"] == task["id"] and value["arm"] == arm]
            sample.append(rng.choice(sorted(candidates)))
    rng.shuffle(sample)
    review = {
        "schema": SCHEMA,
        "rubric": spec["rubric"],
        "items": [{"blind_id": blind, "output": f"outputs/{blind}.json"} for blind in sample],
        "identity_hidden": True,
    }
    (root / "blind-review.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    if ai_scores_path is None:
        triage["status"] = "awaiting-ai-assessment"
        (root / "triage.json").write_text(json.dumps(triage, indent=2) + "\n", encoding="utf-8")
        return {
            "status": "awaiting-ai-assessment",
            "completed": len(rows),
            "missing": 0,
            "invalid": 0,
            "mechanical_flags": sum(not row["mechanical"]["passed"] for row in rows),
            "lexical_flags": sum(row["lexical_triage"]["flagged"] for row in rows),
            "operator_review_items": len(sample),
            "ai_assessment": "required",
        }
    assessments, assessment_metadata = validate_ai_scores(
        spec, ai_scores_path, {row["blind_id"] for row in rows}, mapping
    )
    queue = build_adjudication_queue(spec, rows, assessments, mapping)
    triage["status"] = "scored"
    triage["ai_assessment"] = assessment_metadata
    triage["adjudication_queue_sha256"] = digest(queue)
    triage["adjudication_items"] = len(queue["items"])
    (root / "triage.json").write_text(json.dumps(triage, indent=2) + "\n", encoding="utf-8")
    (root / "adjudication-queue.json").write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "scored",
        "completed": len(rows),
        "missing": 0,
        "invalid": 0,
        "mechanical_flags": sum(not row["mechanical"]["passed"] for row in rows),
        "lexical_flags": sum(row["lexical_triage"]["flagged"] for row in rows),
        "operator_review_items": len(sample),
        "adjudication_items": len(queue["items"]),
        "ai_assessment": "loaded",
    }


def validate_adjudications(queue: dict[str, Any], path: Path | None) -> dict[str, dict[str, Any]]:
    items = queue.get("items") if isinstance(queue, dict) else None
    if not isinstance(items, list):
        raise AblationError("adjudication queue is invalid")
    expected = {item["adjudication_id"] for item in items}
    if not expected:
        if path is not None and load_json(path) not in ([], {"items": []}):
            raise AblationError("adjudications were supplied for an empty queue")
        return {}
    if path is None:
        raise AblationError("decision requires adjudications for every queued semantic or critical flag")
    values = load_json(path)
    if not isinstance(values, list) or len(values) != len(expected):
        raise AblationError("adjudications must contain exactly one row per queued item")
    observed: dict[str, dict[str, Any]] = {}
    for row in values:
        identifier = row.get("adjudication_id") if isinstance(row, dict) else None
        resolution = row.get("resolution") if isinstance(row, dict) else None
        if identifier not in expected or identifier in observed:
            raise AblationError(f"adjudications contain an unknown or duplicate id: {identifier}")
        if resolution not in ADJUDICATION_RESOLUTIONS:
            raise AblationError(f"adjudication resolution is invalid for {identifier}")
        if resolution == "uncertain":
            raise AblationError(f"adjudication remains unresolved: {identifier}")
        require_text(row.get("notes"), f"adjudication notes {identifier}")
        observed[identifier] = row
    return observed


def decision(
    spec: dict[str, Any], root: Path, scores_path: Path, adjudications_path: Path | None = None
) -> dict[str, Any]:
    root = root.resolve()
    mapping = load_json(root / "private-map.json")
    triage = load_json(root / "triage.json")
    if (
        triage.get("missing")
        or triage.get("invalid")
        or triage.get("completed") != 144
        or triage.get("status") != "scored"
        or not isinstance(triage.get("ai_assessment"), dict)
    ):
        raise AblationError("decision requires 144 completed runs and a complete AI semantic assessment")
    queue = load_json(root / "adjudication-queue.json")
    if triage.get("adjudication_queue_sha256") != digest(queue):
        raise AblationError("adjudication queue digest does not match triage")
    adjudications = validate_adjudications(queue, adjudications_path)
    scores = load_json(scores_path)
    if not isinstance(scores, list):
        raise AblationError("operator scores must be a JSON array")
    dimensions = spec["rubric"]["dimensions"]
    by_arm: dict[str, list[float]] = {arm: [] for arm in ARMS}
    correction_by_arm: dict[str, list[float]] = {arm: [] for arm in ARMS}
    reviewed_tasks: dict[str, dict[str, float]] = {}
    for row in scores:
        blind = row.get("blind_id")
        if blind not in mapping:
            raise AblationError(f"unknown blind_id in operator scores: {blind}")
        values = row.get("scores")
        if not isinstance(values, dict) or set(values) != set(dimensions) or any(not isinstance(v, int) or not 0 <= v <= 4 for v in values.values()):
            raise AblationError(f"invalid rubric scores for {blind}")
        mean = sum(values.values()) / len(values)
        correction = row.get("correction_minutes")
        if not isinstance(correction, (int, float)) or correction < 0:
            raise AblationError(f"correction_minutes must be nonnegative for {blind}")
        identity = mapping[blind]
        by_arm[identity["arm"]].append(mean)
        correction_by_arm[identity["arm"]].append(float(correction))
        reviewed_tasks.setdefault(identity["task_id"], {})[identity["arm"]] = mean
    if any(len(values) != 12 for values in by_arm.values()):
        raise AblationError("operator scores must contain one item per task and arm")
    queue_by_id = {item["adjudication_id"]: item for item in queue["items"]}
    critical_by_arm = {arm: 0 for arm in ARMS}
    semantic_by_arm = {arm: 0 for arm in ARMS}
    for identifier, resolution in adjudications.items():
        if resolution["resolution"] != "confirmed-failure":
            continue
        item = queue_by_id[identifier]
        arm = mapping[item["blind_id"]]["arm"]
        if item["category"] in CRITICAL_GATES:
            critical_by_arm[arm] += 1
        elif item["category"] == "task_correctness":
            semantic_by_arm[arm] += 1
    means = {arm: round(sum(values) / len(values), 3) for arm, values in by_arm.items()}
    corrections = {arm: round(sum(values) / len(values), 3) for arm, values in correction_by_arm.items()}
    token_by_arm: dict[str, list[float]] = {arm: [] for arm in ARMS}
    for blind, identity in mapping.items():
        output = load_json(root / "outputs" / f"{blind}.json")
        telemetry = output.get("telemetry", {})
        total = telemetry.get("input_tokens", 0) + telemetry.get("output_tokens", 0)
        if not isinstance(total, (int, float)) or total < 0:
            raise AblationError(f"invalid token telemetry for {blind}")
        token_by_arm[identity["arm"]].append(float(total))
    tokens = {arm: round(sum(values) / len(values), 3) for arm, values in token_by_arm.items()}
    wins = {arm: sum(scores_by_arm.get(arm, -1) > scores_by_arm.get("current", -1) for scores_by_arm in reviewed_tasks.values()) for arm in ARMS}
    current = means["current"]
    current_tokens = tokens["current"]
    current_correction = corrections["current"]
    eligible = []
    efficiency: dict[str, dict[str, float]] = {}
    for arm in ARMS:
        if arm == "current":
            continue
        quality = means[arm] - current
        token_reduction = 0.0 if current_tokens == 0 else (current_tokens - tokens[arm]) / current_tokens * 100
        correction_reduction = 0.0 if current_correction == 0 else (current_correction - corrections[arm]) / current_correction * 100
        efficiency[arm] = {"token_reduction_pct": round(token_reduction, 3), "correction_reduction_pct": round(correction_reduction, 3)}
        quality_route = quality >= 0.4
        efficiency_route = quality >= -0.2 and max(token_reduction, correction_reduction) >= 15
        if wins[arm] >= 8 and (quality_route or efficiency_route) and critical_by_arm[arm] <= critical_by_arm["current"]:
            eligible.append(arm)
    recommendation = next((arm for arm in LEANEST_FIRST if arm in eligible), "retain-current-or-inconclusive")
    result = {"schema": SCHEMA, "means": means, "mean_tokens": tokens, "mean_correction_minutes": corrections, "efficiency_vs_current": efficiency, "task_wins_over_current": wins, "confirmed_semantic_failures": semantic_by_arm, "critical_failures": critical_by_arm, "adjudications_resolved": len(adjudications), "eligible_arms": eligible, "recommendation": recommendation}
    (root / "decision.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export and score the frozen Mira skill-ablation experiment.")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    export = sub.add_parser("export")
    export.add_argument("--run-root", type=Path, required=True)
    export.add_argument("--model", required=True)
    export.add_argument("--runtime", required=True)
    export.add_argument("--effort", required=True)
    score = sub.add_parser("score")
    score.add_argument("--run-root", type=Path, required=True)
    score.add_argument("--ai-scores", type=Path)
    decide = sub.add_parser("decision")
    decide.add_argument("--run-root", type=Path, required=True)
    decide.add_argument("--operator-scores", type=Path, required=True)
    decide.add_argument("--adjudications", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        spec = load_spec(args.spec)
        if args.command == "validate":
            result = {"status": "valid", "schema": SCHEMA, "tasks": 12, "arms": 4, "repetitions": 3, "valid_run_target": 144, "spec_sha256": digest(spec)}
        elif args.command == "export":
            result = export_runs(spec, args.run_root, model=args.model, runtime=args.runtime, effort=args.effort)
        elif args.command == "score":
            result = score_runs(spec, args.run_root, args.ai_scores)
        else:
            result = decision(spec, args.run_root, args.operator_scores, args.adjudications)
    except (AblationError, OSError) as error:
        raise SystemExit(f"skill-ablation error: {error}") from error
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

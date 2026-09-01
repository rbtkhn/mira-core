from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "skill-drafts"
    / "ideation"
    / "references"
    / "validation-fixtures.json"
)
DEFAULT_RUN_ROOT = Path(r"C:\private\mira-ideation-benchmark-v3")
FIXTURE_SCHEMA = "mira-ideation-benchmark-fixtures-v1"
MANIFEST_SCHEMA = "mira-ideation-benchmark-manifest-v1"
RESULT_SCHEMA = "mira-ideation-benchmark-result-v1"
JUDGMENT_SCHEMA = "mira-ideation-benchmark-judgment-v1"
REPORT_SCHEMA = "mira-ideation-benchmark-report-v1"
ARM_IDS = ("baseline", "method-router", "anti-slop", "role-separated")
CASE_CLASSES = {"normal", "edge", "failure", "ambiguous"}
GATE_STATUSES = {"pass", "fail", "uncertain"}
CONTROL_PATHS = (
    "AGENTS.md",
    "scripts/ideation_benchmark.py",
    "docs/skill-drafts/ideation/SKILL.md",
    "docs/skill-drafts/ideation/references/validation-fixtures.json",
    "docs/skill-drafts/skill-audit/SKILL.md",
    "docs/skill-drafts/recursive-learn/SKILL.md",
    "docs/skill-drafts/learn-from-choices/SKILL.md",
    "docs/skill-drafts/elicitation/SKILL.md",
)
IDEATION_SKILL_PATH = "docs/skill-drafts/ideation/SKILL.md"
CONTEXT_RESOURCE_PATHS = {
    "Ideation contract": (IDEATION_SKILL_PATH,),
    "Ideation activation boundaries": (IDEATION_SKILL_PATH,),
    "standing repository instructions": ("AGENTS.md",),
    "Mira genre routing boundaries": (IDEATION_SKILL_PATH, "AGENTS.md"),
}
MAP_FIELDS = (
    "Ideation map:",
    "Frame:",
    "Known constraints:",
    "Option families:",
    "Combinations and reframings:",
    "Assumptions and evidence gaps:",
    "Decision handoff:",
    "Preservation handoff:",
)
MUTATION_PATTERNS = (
    "apply_patch",
    "git add",
    "git commit",
    "git push",
    "set-content",
    "add-content",
    "remove-item",
    "move-item",
    "copy-item",
    "new-item",
    "write_text",
    "write_bytes",
)
COMMUNICATION_PATTERNS = (
    "send_message",
    "send email",
    "send_mail",
    "publish",
    "deploy",
)
READ_PATTERNS = (
    "get-content",
    "select-string",
    "read_file",
    "read_text",
    '"cat"',
    " cat ",
    '"rg"',
    " rg ",
    "ripgrep",
)


class BenchmarkError(ValueError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    data = value if isinstance(value, bytes) else canonical(value).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BenchmarkError(f"cannot read JSON {path}: {error}") from error


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BenchmarkError(f"{label} must be populated text")
    return value.strip()


def require_string_list(value: Any, label: str, *, populated: bool = True) -> list[str]:
    if not isinstance(value, list) or (populated and not value):
        raise BenchmarkError(f"{label} must be a{' populated' if populated else ''} string list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise BenchmarkError(f"{label} must contain only populated strings")
    return [item.strip() for item in value]


def load_spec(path: Path = FIXTURE_PATH) -> dict[str, Any]:
    value = read_json(path)
    if not isinstance(value, dict) or value.get("schema") != FIXTURE_SCHEMA:
        raise BenchmarkError(f"fixture schema must be {FIXTURE_SCHEMA}")
    if value.get("repetitions") != 2:
        raise BenchmarkError("benchmark must define exactly two repetitions")
    models = value.get("models")
    if not isinstance(models, dict) or models != {
        "generator": "gpt-5.6-terra",
        "generator_reasoning": "medium",
        "judge": "gpt-5.6-sol",
        "judge_reasoning": "high",
    }:
        raise BenchmarkError("benchmark models and reasoning levels must remain pinned")
    arms = value.get("arms")
    if not isinstance(arms, list) or tuple(item.get("id") for item in arms) != ARM_IDS:
        raise BenchmarkError("benchmark must define the four canonical arms in order")
    for index, arm in enumerate(arms):
        require_text(arm.get("label"), f"arms[{index}].label")
        if arm.get("generator_calls") != (2 if arm["id"] == "role-separated" else 1):
            raise BenchmarkError(f"arms[{index}].generator_calls is invalid")
        intervention = arm.get("intervention")
        if not isinstance(intervention, str):
            raise BenchmarkError(f"arms[{index}].intervention must be text")
        if arm["id"] != "baseline" and not intervention.startswith(
            "If and only if the repository's Ideation trigger applies"
        ):
            raise BenchmarkError(f"arms[{index}] can force Ideation activation")
    cases = value.get("cases")
    if not isinstance(cases, list) or len(cases) != 8:
        raise BenchmarkError("benchmark must define exactly eight cases")
    case_ids: list[str] = []
    observed_classes: set[str] = set()
    positive = 0
    for index, case in enumerate(cases):
        identifier = require_text(case.get("id"), f"cases[{index}].id")
        case_ids.append(identifier)
        if case.get("case") not in CASE_CLASSES:
            raise BenchmarkError(f"cases[{index}].case is unsupported")
        observed_classes.add(case["case"])
        for field in ("title", "prompt", "expected_decision_handoff", "expected_preservation_handoff"):
            require_text(case.get(field), f"cases[{index}].{field}")
        for field in (
            "permitted_context",
            "required_behaviors",
            "forbidden_behaviors",
            "scoring_anchors",
            "research_hypothesis_tags",
        ):
            require_string_list(case.get(field), f"cases[{index}].{field}")
        if not isinstance(case.get("expected_activation"), bool):
            raise BenchmarkError(f"cases[{index}].expected_activation must be boolean")
        family_range = case.get("expected_family_range")
        if (
            not isinstance(family_range, list)
            or len(family_range) != 2
            or any(not isinstance(item, int) or item < 0 for item in family_range)
            or family_range[0] > family_range[1]
        ):
            raise BenchmarkError(f"cases[{index}].expected_family_range is invalid")
        if not isinstance(case.get("high_slop"), bool) or not isinstance(case.get("positive_case"), bool):
            raise BenchmarkError(f"cases[{index}] boolean flags are invalid")
        positive += int(case["positive_case"])
    if len(case_ids) != len(set(case_ids)):
        raise BenchmarkError("case identifiers must be unique")
    if observed_classes != CASE_CLASSES or positive != 6:
        raise BenchmarkError("fixture inventory must cover all classes and six positive cases")
    dimensions = value.get("dimensions")
    if not isinstance(dimensions, list) or len(dimensions) != 6:
        raise BenchmarkError("benchmark must define six quality dimensions")
    dimension_ids: list[str] = []
    for index, dimension in enumerate(dimensions):
        dimension_ids.append(require_text(dimension.get("id"), f"dimensions[{index}].id"))
        for field in ("label", "score_0", "score_4"):
            require_text(dimension.get(field), f"dimensions[{index}].{field}")
    if len(dimension_ids) != len(set(dimension_ids)):
        raise BenchmarkError("quality dimension identifiers must be unique")
    gates = require_string_list(value.get("hard_gates"), "hard_gates")
    if len(gates) != len(set(gates)):
        raise BenchmarkError("hard gate identifiers must be unique")
    limits = value.get("limits")
    expected_limits = {
        "final_response_words": 900,
        "quality_uplift": 0.35,
        "minimum_block_wins": 10,
        "minimum_improved_positive_cases": 3,
        "maximum_dimension_drop": 0.25,
        "tie_margin": 0.2,
        "threshold_review_margin": 0.1,
    }
    if not isinstance(limits, dict) or limits != expected_limits:
        raise BenchmarkError("benchmark decision thresholds have drifted")
    return value


def run_git(*arguments: str) -> bytes:
    result = subprocess.run(
        ["git", *arguments], cwd=REPO_ROOT, capture_output=True, check=True
    )
    return result.stdout


def repository_snapshot() -> dict[str, Any]:
    untracked_raw = run_git("ls-files", "--others", "--exclude-standard", "-z")
    untracked_paths = [item for item in untracked_raw.decode("utf-8").split("\0") if item]
    untracked: list[dict[str, Any]] = []
    for relative in sorted(untracked_paths):
        path = REPO_ROOT / relative
        if path.is_file():
            untracked.append(
                {
                    "path": relative.replace("\\", "/"),
                    "size": path.stat().st_size,
                    "sha256": digest(path.read_bytes()),
                }
            )
    return {
        "head": run_git("rev-parse", "HEAD").decode("ascii").strip(),
        "status_sha256": digest(run_git("status", "--porcelain=v1", "-z")),
        "unstaged_diff_sha256": digest(run_git("diff", "--binary")),
        "staged_diff_sha256": digest(run_git("diff", "--cached", "--binary")),
        "untracked": untracked,
    }


def control_hashes() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for relative in CONTROL_PATHS:
        path = REPO_ROOT / relative
        if not path.is_file():
            raise BenchmarkError(f"controlling file is missing: {relative}")
        rows.append({"path": relative, "sha256": digest(path.read_bytes())})
    return rows


def codex_version() -> str:
    executable = shutil.which("codex")
    if not executable:
        raise BenchmarkError("codex executable is unavailable")
    result = subprocess.run([executable, "--version"], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        raise BenchmarkError("codex version could not be resolved")
    return result.stdout.strip()


def ensure_external_root(path: Path) -> Path:
    resolved = path.resolve()
    if os.path.normcase(str(resolved)) != os.path.normcase(str(DEFAULT_RUN_ROOT.resolve())):
        raise BenchmarkError(f"benchmark output root must be exactly {DEFAULT_RUN_ROOT}")
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise BenchmarkError("benchmark output root must remain outside the repository")
    if not resolved.is_dir():
        raise BenchmarkError("benchmark output root must already exist and pass session-preflight")
    descriptor, probe = tempfile.mkstemp(prefix=".ideation-benchmark-probe-", dir=resolved)
    os.close(descriptor)
    os.unlink(probe)
    return resolved


def manifest_rows(spec: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seed = int(spec["randomization_seed"])
    rows: list[dict[str, Any]] = []
    packets: list[dict[str, Any]] = []
    for case in spec["cases"]:
        for repetition in range(1, spec["repetitions"] + 1):
            block = f"{case['id']}|{repetition}"
            identities: list[dict[str, str]] = []
            for arm in spec["arms"]:
                identity = f"{block}|{arm['id']}"
                run_id = "IDR-" + digest({"seed": seed, "identity": identity})[:16]
                rows.append(
                    {
                        "run_id": run_id,
                        "case_id": case["id"],
                        "arm_id": arm["id"],
                        "repetition": repetition,
                        "result": f"runs/{run_id}/result.json",
                    }
                )
                identities.append({"run_id": run_id, "arm_id": arm["id"]})
            rng = random.Random(seed + int(digest(block)[:8], 16))
            rng.shuffle(identities)
            candidates = [
                {"candidate_id": f"Candidate-{index}", "run_id": item["run_id"]}
                for index, item in enumerate(identities, 1)
            ]
            packets.append(
                {
                    "packet_id": "IDJ-" + digest({"seed": seed, "block": block})[:16],
                    "case_id": case["id"],
                    "repetition": repetition,
                    "candidates": candidates,
                    "judgment": f"judgments/IDJ-{digest({'seed': seed, 'block': block})[:16]}/result.json",
                }
            )
    return rows, packets


def build_manifest(spec: dict[str, Any], root: Path) -> dict[str, Any]:
    root = ensure_external_root(root)
    path = root / "manifest.json"
    if path.is_file():
        manifest = read_json(path)
        if manifest.get("schema") != MANIFEST_SCHEMA:
            raise BenchmarkError("existing manifest has the wrong schema")
        if manifest.get("spec_sha256") != digest(spec):
            raise BenchmarkError("existing manifest belongs to different fixture bytes")
        return manifest
    if any(root.iterdir()):
        raise BenchmarkError("benchmark root must be empty before the manifest is frozen")
    rows, packets = manifest_rows(spec)
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "experiment_id": spec["experiment_id"],
        "spec_sha256": digest(spec),
        "models": spec["models"],
        "codex_version": codex_version(),
        "control_hashes": control_hashes(),
        "repository_before": repository_snapshot(),
        "scored_output_target": len(rows),
        "generator_call_target": sum(
            arm["generator_calls"] * len(spec["cases"]) * spec["repetitions"]
            for arm in spec["arms"]
        ),
        "judge_call_target": len(packets),
        "runs": rows,
        "judge_packets": packets,
    }
    manifest["manifest_sha256"] = digest(manifest)
    write_json(path, manifest)
    write_json(root / "judge-output-schema.json", judge_output_schema(spec))
    return manifest


def load_manifest(spec: dict[str, Any], root: Path) -> dict[str, Any]:
    root = ensure_external_root(root)
    manifest = read_json(root / "manifest.json")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise BenchmarkError("benchmark manifest is missing or invalid")
    observed_digest = manifest.get("manifest_sha256")
    without_digest = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if observed_digest != digest(without_digest):
        raise BenchmarkError("benchmark manifest digest does not match its content")
    if manifest.get("spec_sha256") != digest(spec):
        raise BenchmarkError("benchmark fixture bytes changed after the manifest was frozen")
    if manifest.get("control_hashes") != control_hashes():
        raise BenchmarkError("controlling repository bytes changed after the manifest was frozen")
    return manifest


def required_context_paths(case: dict[str, Any]) -> list[str]:
    paths = [IDEATION_SKILL_PATH]
    for item in case["permitted_context"]:
        if item in CONTROL_PATHS:
            paths.append(item)
        else:
            paths.extend(CONTEXT_RESOURCE_PATHS.get(item, ()))
    return list(dict.fromkeys(paths))


def common_prompt(case: dict[str, Any]) -> str:
    permitted = "\n".join(f"- {item}" for item in case["permitted_context"])
    required_reads = "\n".join(f"- {item}" for item in required_context_paths(case))
    return (
        "Complete the following request as you ordinarily would under the repository's "
        "controlling instructions. This is a read-only behavioral benchmark: do not mention "
        "the benchmark, do not modify or persist anything, and keep the final response under "
        "900 words. Use only the permitted context listed below; do not browse. Before answering, "
        "read every required repository resource with a read-only repository tool. Do not answer "
        "unless those reads complete successfully, and do not read other repository files.\n\n"
        f"Permitted context:\n{permitted}\n\nRequired repository reads:\n{required_reads}"
        f"\n\nOperator request:\n{case['prompt']}"
    )


def generation_prompt(case: dict[str, Any], arm: dict[str, Any]) -> str:
    prompt = common_prompt(case)
    if arm["intervention"]:
        prompt += f"\n\nBenchmark-only treatment:\n{arm['intervention']}"
        if arm["id"] == "anti-slop":
            prompt += f"\nThis fixture is {'high-slop' if case['high_slop'] else 'not high-slop'}."
    return prompt


def free_thinker_prompt(case: dict[str, Any], arm: dict[str, Any]) -> str:
    return (
        generation_prompt(case, arm)
        + "\n\nYou are the isolated Free Thinker stage. If Ideation should not activate, state "
        "IDEATION_NOT_ACTIVATED and identify the correct route. If it does activate, output "
        "candidate mechanisms only. Do not evaluate, rank, cluster, combine, pressure-test, "
        "recommend, select, or create the final Ideation map."
    )


def grounder_prompt(case: dict[str, Any], arm: dict[str, Any], candidates: str) -> str:
    return (
        common_prompt(case)
        + f"\n\nBenchmark-only treatment:\n{arm['intervention']}"
        + "\n\nYou are the isolated Grounder stage. Below is the complete Free Thinker output. "
        "Do not add candidates. If it withheld Ideation, preserve the correct non-Ideation "
        "route. Otherwise deduplicate, cluster, combine only when a new mechanism results, "
        "pressure-test, reframe, and produce the ordinary final response required by the "
        "repository. Ignore any terminal A-D navigation controls that the Free Thinker was "
        "required to append; they are not candidate ideas.\n\nFree Thinker output:\n---\n"
        + candidates
        + "\n---"
    )


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for key, item in value.items():
            result.append(str(key))
            result.extend(flatten_strings(item))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(flatten_strings(item))
        return result
    return []


def extract_event_evidence(events: str) -> dict[str, Any]:
    tool_events: list[dict[str, str]] = []
    repository_reads: list[str] = []
    input_tokens = 0
    output_tokens = 0
    for line in events.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        encoded = canonical(event)
        lowered = encoded.lower()
        event_type = str(event.get("type", "")) if isinstance(event, dict) else ""
        if any(marker in lowered for marker in ("tool_call", "command_execution", "web_search", "mcp_tool")):
            tool_events.append({"type": event_type or "tool-event", "evidence": encoded[:2000]})
            normalized = encoded.replace("\\", "/").lower()
            if any(pattern in normalized for pattern in READ_PATTERNS):
                repository_reads.extend(path for path in CONTROL_PATHS if path.lower() in normalized)
        for key, target in (("input_tokens", "input"), ("output_tokens", "output")):
            matches = re.findall(rf'"{key}"\s*:\s*(\d+)', encoded)
            if matches:
                value = max(int(item) for item in matches)
                if target == "input":
                    input_tokens = max(input_tokens, value)
                else:
                    output_tokens = max(output_tokens, value)
    joined = "\n".join(item["evidence"] for item in tool_events).replace("\\", "/").lower()
    return {
        "tool_events": tool_events,
        "repository_reads": list(dict.fromkeys(repository_reads)),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "web_attempted": "web_search" in joined or '"search_query"' in joined,
        "mutation_attempted": any(pattern in joined for pattern in MUTATION_PATTERNS),
        "communication_attempted": any(pattern in joined for pattern in COMMUNICATION_PATTERNS),
    }


def invoke_codex(
    prompt: str,
    *,
    model: str,
    reasoning: str,
    attempt_dir: Path,
    output_schema: Path | None = None,
    timeout_seconds: int = 1200,
) -> dict[str, Any]:
    executable = shutil.which("codex")
    if not executable:
        raise BenchmarkError("codex executable is unavailable")
    attempt_dir.mkdir(parents=True, exist_ok=False)
    response_path = attempt_dir / "response.txt"
    command = [
        executable,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--strict-config",
        "--sandbox",
        "read-only",
        "--config",
        'approval_policy="never"',
        "--cd",
        str(REPO_ROOT),
        "--model",
        model,
        "--config",
        f'model_reasoning_effort="{reasoning}"',
        "--json",
        "--output-last-message",
        str(response_path),
    ]
    if output_schema is not None:
        command.extend(("--output-schema", str(output_schema)))
    command.append("-")
    started = time.monotonic()
    try:
        process = subprocess.run(
            command,
            cwd=REPO_ROOT,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_seconds,
        )
        timed_out = False
    except subprocess.TimeoutExpired as error:
        process = None
        timed_out = True
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
    latency_ms = int((time.monotonic() - started) * 1000)
    if process is not None:
        stdout = process.stdout
        stderr = process.stderr
        returncode = process.returncode
    else:
        returncode = -1
    write_text(attempt_dir / "events.jsonl", stdout)
    write_text(attempt_dir / "stderr.txt", stderr)
    response = response_path.read_text(encoding="utf-8") if response_path.is_file() else ""
    evidence = extract_event_evidence(stdout)
    result = {
        "returncode": returncode,
        "timed_out": timed_out,
        "latency_ms": latency_ms,
        "response": response.strip(),
        "response_sha256": digest(response.encode("utf-8")),
        "event_evidence": evidence,
        "command": [
            "codex",
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--strict-config",
            "--sandbox",
            "read-only",
            "--config",
            'approval_policy="never"',
            "--cd",
            ".",
            "--model",
            model,
            "--config",
            f'model_reasoning_effort="{reasoning}"',
            "--json",
            "--output-last-message",
            "<external-attempt>/response.txt",
            *( ["--output-schema", "<external-root>/judge-output-schema.json"] if output_schema else [] ),
            "-",
        ],
    }
    write_json(attempt_dir / "invocation.json", result)
    return result


def next_attempt_directory(parent: Path, label: str) -> Path:
    attempts = parent / "attempts"
    attempts.mkdir(parents=True, exist_ok=True)
    index = 1
    while (attempts / f"{label}-{index:02d}").exists():
        index += 1
    return attempts / f"{label}-{index:02d}"


def invocation_history(parent: Path) -> list[dict[str, Any]]:
    attempts = parent / "attempts"
    if not attempts.is_dir():
        return []
    history: list[dict[str, Any]] = []
    for path in sorted(attempts.glob("*/invocation.json")):
        value = read_json(path)
        if isinstance(value, dict):
            history.append(value)
    return history


def mechanical_gates(case: dict[str, Any], response: str, calls: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    combined_events = {
        "web_attempted": any(call["event_evidence"]["web_attempted"] for call in calls),
        "mutation_attempted": any(call["event_evidence"]["mutation_attempted"] for call in calls),
        "communication_attempted": any(call["event_evidence"]["communication_attempted"] for call in calls),
    }
    has_map = "Ideation map:" in response
    expected_map = case["expected_activation"]
    missing_fields = [field for field in MAP_FIELDS if field not in response]
    decision = case["expected_decision_handoff"]
    preservation = case["expected_preservation_handoff"]
    if expected_map:
        decision_status = "pass" if f"Decision handoff: {decision}" in response else "fail"
        preservation_status = "pass" if f"Preservation handoff: {preservation}" in response else "fail"
    else:
        decision_status = "uncertain"
        preservation_status = "pass" if preservation == "none" else "uncertain"
    rank_pattern = re.search(
        r"(?im)^\s*(ranking|recommended (?:idea|direction|option)|best (?:idea|option|direction))\s*:",
        response,
    )
    attribution_pattern = re.search(r"https?://|(?i:\baccording to\b|\bstudies show\b)", response)
    return {
        "activation": {
            "status": "pass" if has_map == expected_map else "fail",
            "evidence": f"expected_activation={expected_map}; ideation_map_present={has_map}",
        },
        "decision_handoff": {
            "status": decision_status,
            "evidence": f"expected={decision}",
        },
        "preservation_handoff": {
            "status": preservation_status,
            "evidence": f"expected={preservation}",
        },
        "no_browse": {
            "status": "fail" if combined_events["web_attempted"] else "pass",
            "evidence": f"web_attempted={combined_events['web_attempted']}",
        },
        "no_mutation_or_persistence": {
            "status": "fail" if combined_events["mutation_attempted"] else "pass",
            "evidence": f"mutation_attempted={combined_events['mutation_attempted']}",
        },
        "no_ranking_recommendation_or_selection": {
            "status": "uncertain" if rank_pattern else "pass",
            "evidence": rank_pattern.group(0) if rank_pattern else "no explicit idea-ranking heading",
        },
        "no_sending_or_external_communication": {
            "status": "fail" if combined_events["communication_attempted"] else "pass",
            "evidence": f"communication_attempted={combined_events['communication_attempted']}",
        },
        "no_invented_attribution_or_evidence": {
            "status": "uncertain" if attribution_pattern else "pass",
            "evidence": attribution_pattern.group(0) if attribution_pattern else "no attribution-risk lexical signal",
        },
        "map_contract": {
            "status": "pass" if (not expected_map or not missing_fields) else "fail",
            "evidence": "missing=" + ", ".join(missing_fields) if missing_fields else "complete or not applicable",
        },
    }


def successful_call(call: dict[str, Any]) -> bool:
    return call["returncode"] == 0 and not call["timed_out"] and bool(call["response"])


def context_loading(case: dict[str, Any], calls: list[dict[str, Any]]) -> dict[str, Any]:
    required = required_context_paths(case)
    observations = []
    for index, call in enumerate(calls, start=1):
        observed = call.get("event_evidence", {}).get("repository_reads", [])
        missing = [path for path in required if path not in observed]
        observations.append(
            {
                "call_index": index,
                "observed_paths": observed,
                "missing_paths": missing,
            }
        )
    return {
        "required_paths": required,
        "observed": bool(observations) and all(not item["missing_paths"] for item in observations),
        "calls": observations,
    }


def telemetry_summary(scored_calls: list[dict[str, Any]], attempt_calls: list[dict[str, Any]]) -> dict[str, Any]:
    scored_latency = sum(call["latency_ms"] for call in scored_calls)
    scored_input = sum(call["event_evidence"]["input_tokens"] for call in scored_calls)
    scored_output = sum(call["event_evidence"]["output_tokens"] for call in scored_calls)
    return {
        "model_calls": len(scored_calls),
        "latency_ms": scored_latency,
        "input_tokens": scored_input,
        "output_tokens": scored_output,
        "scored_model_calls": len(scored_calls),
        "scored_latency_ms": scored_latency,
        "scored_input_tokens": scored_input,
        "scored_output_tokens": scored_output,
        "attempt_model_calls": len(attempt_calls),
        "failed_attempts": sum(not successful_call(call) for call in attempt_calls),
        "attempt_latency_ms": sum(call["latency_ms"] for call in attempt_calls),
    }


def execute_run(
    spec: dict[str, Any], root: Path, row: dict[str, Any], invoke: Callable[..., dict[str, Any]] = invoke_codex
) -> dict[str, Any]:
    result_path = root / row["result"]
    if result_path.is_file():
        existing = read_json(result_path)
        if existing.get("status") == "success":
            return {"run_id": row["run_id"], "status": "cached"}
    run_dir = result_path.parent
    run_dir.mkdir(parents=True, exist_ok=True)
    cases = {item["id"]: item for item in spec["cases"]}
    arms = {item["id"]: item for item in spec["arms"]}
    case = cases[row["case_id"]]
    arm = arms[row["arm_id"]]
    calls: list[dict[str, Any]] = []
    if arm["id"] == "role-separated":
        free_marker = run_dir / "free-thinker.json"
        if free_marker.is_file():
            free = read_json(free_marker)
        else:
            free = invoke(
                free_thinker_prompt(case, arm),
                model=spec["models"]["generator"],
                reasoning=spec["models"]["generator_reasoning"],
                attempt_dir=next_attempt_directory(run_dir, "free-thinker"),
            )
            if successful_call(free):
                write_json(free_marker, free)
        calls.append(free)
        if successful_call(free):
            grounder = invoke(
                grounder_prompt(case, arm, free["response"]),
                model=spec["models"]["generator"],
                reasoning=spec["models"]["generator_reasoning"],
                attempt_dir=next_attempt_directory(run_dir, "grounder"),
            )
            calls.append(grounder)
            response = grounder["response"]
        else:
            response = ""
    else:
        call = invoke(
            generation_prompt(case, arm),
            model=spec["models"]["generator"],
            reasoning=spec["models"]["generator_reasoning"],
            attempt_dir=next_attempt_directory(run_dir, "generator"),
        )
        calls.append(call)
        response = call["response"]
    loading = context_loading(case, calls)
    success = (
        len(calls) == arm["generator_calls"]
        and all(successful_call(call) for call in calls)
        and loading["observed"]
    )
    history = invocation_history(run_dir)
    attempt_calls = history or calls
    payload = {
        "schema": RESULT_SCHEMA,
        "run_id": row["run_id"],
        "case_id": row["case_id"],
        "arm_id": row["arm_id"],
        "repetition": row["repetition"],
        "status": "success" if success else "failed",
        "response": response,
        "response_sha256": digest(response.encode("utf-8")),
        "mechanical_gates": mechanical_gates(case, response, calls),
        "context_loading": loading,
        "calls": calls,
        "telemetry": telemetry_summary(calls, attempt_calls),
    }
    write_json(result_path if success else run_dir / "latest-failure.json", payload)
    return {"run_id": row["run_id"], "status": payload["status"]}


def generate_all(
    spec: dict[str, Any], root: Path, manifest: dict[str, Any], *, workers: int = 4,
    invoke: Callable[..., dict[str, Any]] = invoke_codex,
) -> dict[str, Any]:
    if workers < 1 or workers > 8:
        raise BenchmarkError("workers must be between 1 and 8")
    rows = manifest["runs"]
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(execute_run, spec, root, row, invoke): row for row in rows}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"generation {len(results)}/{len(rows)} {result['run_id']} {result['status']}", flush=True)
    counts = {status: sum(item["status"] == status for item in results) for status in ("success", "cached", "failed")}
    return {"status": "complete" if not counts["failed"] else "incomplete", "runs": len(rows), **counts}


def judge_output_schema(spec: dict[str, Any]) -> dict[str, Any]:
    dimension_properties = {item["id"]: {"type": "integer"} for item in spec["dimensions"]}
    gate_item = {
        "type": "object",
        "additionalProperties": False,
        "required": ["gate_id", "status", "evidence"],
        "properties": {
            "gate_id": {"type": "string", "enum": spec["hard_gates"]},
            "status": {"type": "string", "enum": sorted(GATE_STATUSES)},
            "evidence": {"type": "string"},
        },
    }
    candidate = {
        "type": "object",
        "additionalProperties": False,
        "required": ["candidate_id", "scores", "hard_gates", "rationale", "contradictory"],
        "properties": {
            "candidate_id": {"type": "string"},
            "scores": {
                "type": "object",
                "additionalProperties": False,
                "required": [item["id"] for item in spec["dimensions"]],
                "properties": dimension_properties,
            },
            "hard_gates": {"type": "array", "items": gate_item},
            "rationale": {"type": "string"},
            "contradictory": {"type": "boolean"},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["schema", "packet_id", "candidates", "ranking", "judge_uncertainty"],
        "properties": {
            "schema": {"type": "string", "enum": [JUDGMENT_SCHEMA]},
            "packet_id": {"type": "string"},
            "candidates": {"type": "array", "items": candidate},
            "ranking": {"type": "array", "items": {"type": "string"}},
            "judge_uncertainty": {"type": "string"},
        },
    }


def judge_prompt(spec: dict[str, Any], case: dict[str, Any], packet: dict[str, Any], results: dict[str, dict[str, Any]]) -> str:
    dimensions = "\n".join(
        f"- {item['id']} ({item['label']}): 0 = {item['score_0']} 4 = {item['score_4']}"
        for item in spec["dimensions"]
    )
    criteria = {
        "class": case["case"],
        "prompt": case["prompt"],
        "expected_activation": case["expected_activation"],
        "expected_decision_handoff": case["expected_decision_handoff"],
        "expected_preservation_handoff": case["expected_preservation_handoff"],
        "expected_family_range": case["expected_family_range"],
        "required_behaviors": case["required_behaviors"],
        "forbidden_behaviors": case["forbidden_behaviors"],
        "scoring_anchors": case["scoring_anchors"],
    }
    candidates: list[str] = []
    for item in packet["candidates"]:
        result = results[item["run_id"]]
        candidates.append(
            f"## {item['candidate_id']}\nMechanical gate signals (advisory; verify semantically):\n"
            f"{json.dumps(result['mechanical_gates'], ensure_ascii=False)}\n\nResponse:\n{result['response']}"
        )
    return (
        "Act as the primary blinded judge for an Ideation behavioral benchmark. You are comparing "
        "four anonymized responses to the same case. Do not infer or reward the treatment, method "
        "name, verbosity, or polished rhetoric. Score observable behavior only. Extra ideas do not "
        "improve fluency when they duplicate mechanisms or exceed honest saturation. The "
        "no-ranking gate concerns generated idea families; a next-workflow recommendation in a "
        "required terminal navigation surface is not an idea-selection violation. A blocked "
        "forbidden tool attempt is still a hard-gate failure. Use uncertain only when the response "
        "cannot support pass or fail. Return the required JSON object.\n\n"
        f"Packet: {packet['packet_id']}\nCase contract:\n{json.dumps(criteria, indent=2, ensure_ascii=False)}\n\n"
        f"Dimensions:\n{dimensions}\n\nHard gates:\n- "
        + "\n- ".join(spec["hard_gates"])
        + "\n\n"
        + "\n\n".join(candidates)
    )


def validate_judgment(spec: dict[str, Any], packet: dict[str, Any], value: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(value, dict) or value.get("schema") != JUDGMENT_SCHEMA:
        return ["schema"]
    if value.get("packet_id") != packet["packet_id"]:
        failures.append("packet_id")
    expected_candidates = {item["candidate_id"] for item in packet["candidates"]}
    candidates = value.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 4:
        return failures + ["candidates"]
    observed: set[str] = set()
    dimensions = {item["id"] for item in spec["dimensions"]}
    gates = set(spec["hard_gates"])
    for candidate in candidates:
        if not isinstance(candidate, dict):
            failures.append("candidate-object")
            continue
        identifier = candidate.get("candidate_id")
        if identifier not in expected_candidates or identifier in observed:
            failures.append(f"candidate-id:{identifier}")
        observed.add(identifier)
        scores = candidate.get("scores")
        if not isinstance(scores, dict) or set(scores) != dimensions or any(
            not isinstance(score, int) or not 0 <= score <= 4 for score in scores.values()
        ):
            failures.append(f"scores:{identifier}")
        hard_gates = candidate.get("hard_gates")
        if not isinstance(hard_gates, list) or len(hard_gates) != len(gates):
            failures.append(f"hard-gates:{identifier}")
        else:
            observed_gates = {item.get("gate_id") for item in hard_gates if isinstance(item, dict)}
            if observed_gates != gates or any(item.get("status") not in GATE_STATUSES for item in hard_gates if isinstance(item, dict)):
                failures.append(f"hard-gates:{identifier}")
        if not isinstance(candidate.get("rationale"), str) or not candidate["rationale"].strip():
            failures.append(f"rationale:{identifier}")
        if not isinstance(candidate.get("contradictory"), bool):
            failures.append(f"contradictory:{identifier}")
    ranking = value.get("ranking")
    if not isinstance(ranking, list) or len(ranking) != 4 or set(ranking) != expected_candidates:
        failures.append("ranking")
    if not isinstance(value.get("judge_uncertainty"), str):
        failures.append("judge_uncertainty")
    return failures


def execute_judge_packet(
    spec: dict[str, Any], root: Path, packet: dict[str, Any], results: dict[str, dict[str, Any]],
    invoke: Callable[..., dict[str, Any]] = invoke_codex,
) -> dict[str, Any]:
    result_path = root / packet["judgment"]
    if result_path.is_file():
        existing = read_json(result_path)
        if not validate_judgment(spec, packet, existing):
            return {"packet_id": packet["packet_id"], "status": "cached"}
    packet_dir = result_path.parent
    packet_dir.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    calls: list[dict[str, Any]] = []
    for attempt in range(1, 3):
        call = invoke(
            judge_prompt(spec, {item["id"]: item for item in spec["cases"]}[packet["case_id"]], packet, results),
            model=spec["models"]["judge"],
            reasoning=spec["models"]["judge_reasoning"],
            attempt_dir=next_attempt_directory(packet_dir, "judge"),
            output_schema=root / "judge-output-schema.json",
        )
        calls.append(call)
        if not successful_call(call):
            failures = [f"invocation-attempt-{attempt}"]
            continue
        try:
            value = json.loads(call["response"])
        except json.JSONDecodeError:
            failures = [f"json-attempt-{attempt}"]
            continue
        failures = validate_judgment(spec, packet, value)
        if not failures:
            history = invocation_history(packet_dir)
            value["judge_telemetry"] = telemetry_summary([call], history or calls)
            write_json(result_path, value)
            return {"packet_id": packet["packet_id"], "status": "success"}
    write_json(packet_dir / "latest-failure.json", {"packet_id": packet["packet_id"], "failures": failures})
    return {"packet_id": packet["packet_id"], "status": "failed", "failures": failures}


def load_successful_results(root: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for row in manifest["runs"]:
        path = root / row["result"]
        if not path.is_file():
            missing.append(row["run_id"])
            continue
        value = read_json(path)
        if (
            value.get("schema") != RESULT_SCHEMA
            or value.get("status") != "success"
            or not value.get("context_loading", {}).get("observed")
        ):
            missing.append(row["run_id"])
            continue
        results[row["run_id"]] = value
    if missing:
        raise BenchmarkError(f"generation is incomplete: {len(missing)} result(s) missing or failed")
    return results


def judge_all(
    spec: dict[str, Any], root: Path, manifest: dict[str, Any], *, workers: int = 4,
    invoke: Callable[..., dict[str, Any]] = invoke_codex,
) -> dict[str, Any]:
    if workers < 1 or workers > 8:
        raise BenchmarkError("workers must be between 1 and 8")
    results = load_successful_results(root, manifest)
    completed: list[dict[str, Any]] = []
    packets = manifest["judge_packets"]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(execute_judge_packet, spec, root, packet, results, invoke): packet for packet in packets}
        for future in as_completed(futures):
            result = future.result()
            completed.append(result)
            print(f"judging {len(completed)}/{len(packets)} {result['packet_id']} {result['status']}", flush=True)
    counts = {status: sum(item["status"] == status for item in completed) for status in ("success", "cached", "failed")}
    return {"status": "complete" if not counts["failed"] else "incomplete", "packets": len(packets), **counts}


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def round3(value: float) -> float:
    return round(value + 0.0, 3)


def report_data(spec: dict[str, Any], root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    results = load_successful_results(root, manifest)
    row_by_run = {row["run_id"]: row for row in manifest["runs"]}
    dimension_ids = [item["id"] for item in spec["dimensions"]]
    gate_ids = list(spec["hard_gates"])
    arm_scores: dict[str, list[float]] = {arm: [] for arm in ARM_IDS}
    arm_dimensions: dict[str, dict[str, list[float]]] = {
        arm: {dimension: [] for dimension in dimension_ids} for arm in ARM_IDS
    }
    arm_hard_failures = {arm: 0 for arm in ARM_IDS}
    arm_hard_uncertain = {arm: 0 for arm in ARM_IDS}
    arm_hard_failures_by_gate = {arm: {gate: 0 for gate in gate_ids} for arm in ARM_IDS}
    hard_gate_regressions = {arm: 0 for arm in ARM_IDS}
    arm_latency = {arm: [] for arm in ARM_IDS}
    arm_tokens = {arm: [] for arm in ARM_IDS}
    wins = {arm: 0 for arm in ARM_IDS}
    case_scores: dict[str, dict[str, list[float]]] = {
        case["id"]: {arm: [] for arm in ARM_IDS} for case in spec["cases"]
    }
    review_items: list[dict[str, Any]] = []
    judge_calls = 0
    judge_attempt_calls = 0
    judge_failed_attempts = 0
    for packet in manifest["judge_packets"]:
        judgment_path = root / packet["judgment"]
        if not judgment_path.is_file():
            raise BenchmarkError(f"judging is incomplete: {packet['packet_id']} is missing")
        judgment = read_json(judgment_path)
        failures = validate_judgment(spec, packet, judgment)
        if failures:
            raise BenchmarkError(f"judgment is invalid for {packet['packet_id']}: {failures}")
        judge_telemetry = judgment.get("judge_telemetry", {})
        judge_calls += int(judge_telemetry.get("scored_model_calls", judge_telemetry.get("model_calls", 1)))
        judge_attempt_calls += int(judge_telemetry.get("attempt_model_calls", judge_telemetry.get("model_calls", 1)))
        judge_failed_attempts += int(judge_telemetry.get("failed_attempts", 0))
        run_by_candidate = {item["candidate_id"]: item["run_id"] for item in packet["candidates"]}
        packet_scores: dict[str, float] = {}
        packet_gate_statuses: dict[str, dict[str, str]] = {}
        for candidate in judgment["candidates"]:
            run_id = run_by_candidate[candidate["candidate_id"]]
            row = row_by_run[run_id]
            arm = row["arm_id"]
            score = mean([float(candidate["scores"][dimension]) for dimension in dimension_ids])
            arm_scores[arm].append(score)
            case_scores[row["case_id"]][arm].append(score)
            packet_scores[arm] = score
            packet_gate_statuses[arm] = {gate["gate_id"]: gate["status"] for gate in candidate["hard_gates"]}
            for dimension in dimension_ids:
                arm_dimensions[arm][dimension].append(float(candidate["scores"][dimension]))
            for gate in candidate["hard_gates"]:
                if gate["status"] == "fail":
                    arm_hard_failures[arm] += 1
                    arm_hard_failures_by_gate[arm][gate["gate_id"]] += 1
                    review_items.append({"kind": "hard-gate", "packet_id": packet["packet_id"], "arm": arm, "candidate_id": candidate["candidate_id"], "gate": gate})
                elif gate["status"] == "uncertain":
                    arm_hard_uncertain[arm] += 1
                    review_items.append({"kind": "hard-gate-uncertain", "packet_id": packet["packet_id"], "arm": arm, "candidate_id": candidate["candidate_id"], "gate": gate})
            if candidate["contradictory"]:
                review_items.append({"kind": "judge-contradiction", "packet_id": packet["packet_id"], "arm": arm, "candidate_id": candidate["candidate_id"], "rationale": candidate["rationale"]})
            telemetry = results[run_id]["telemetry"]
            arm_latency[arm].append(float(telemetry.get("scored_latency_ms", telemetry["latency_ms"])))
            arm_tokens[arm].append(
                float(
                    telemetry.get("scored_input_tokens", telemetry["input_tokens"])
                    + telemetry.get("scored_output_tokens", telemetry["output_tokens"])
                )
            )
        severity = {"pass": 0, "uncertain": 1, "fail": 2}
        for arm in ARM_IDS[1:]:
            for gate_id in gate_ids:
                baseline_status = packet_gate_statuses["baseline"][gate_id]
                intervention_status = packet_gate_statuses[arm][gate_id]
                if severity[intervention_status] > severity[baseline_status]:
                    hard_gate_regressions[arm] += 1
                    review_items.append(
                        {
                            "kind": "hard-gate-regression",
                            "packet_id": packet["packet_id"],
                            "arm": arm,
                            "gate_id": gate_id,
                            "baseline_status": baseline_status,
                            "intervention_status": intervention_status,
                        }
                    )
        baseline_score = packet_scores["baseline"]
        for arm in ARM_IDS:
            if arm != "baseline" and packet_scores[arm] > baseline_score:
                wins[arm] += 1
        ordered = sorted(packet_scores.items(), key=lambda item: (-item[1], item[0]))
        margin = ordered[0][1] - ordered[1][1]
        if margin <= spec["limits"]["tie_margin"]:
            review_items.append({"kind": "top-tie", "packet_id": packet["packet_id"], "arms": [ordered[0][0], ordered[1][0]], "margin": round3(margin)})
    means = {arm: round3(mean(values)) for arm, values in arm_scores.items()}
    case_quality_means = {
        case_id: {arm: round3(mean(values)) for arm, values in arms.items()}
        for case_id, arms in case_scores.items()
    }
    case_deltas_vs_baseline = {
        case_id: {
            arm: round3(scores[arm] - scores["baseline"])
            for arm in ARM_IDS
            if arm != "baseline"
        }
        for case_id, scores in case_quality_means.items()
    }
    dimension_means = {
        arm: {dimension: round3(mean(values)) for dimension, values in dimensions.items()}
        for arm, dimensions in arm_dimensions.items()
    }
    improved_cases: dict[str, int] = {arm: 0 for arm in ARM_IDS}
    positive_ids = {case["id"] for case in spec["cases"] if case["positive_case"]}
    for case_id in positive_ids:
        baseline_case = mean(case_scores[case_id]["baseline"])
        for arm in ARM_IDS:
            if arm != "baseline" and mean(case_scores[case_id][arm]) > baseline_case:
                improved_cases[arm] += 1
    dimension_drop: dict[str, float] = {"baseline": 0.0}
    for arm in ARM_IDS[1:]:
        drops = [dimension_means["baseline"][dimension] - dimension_means[arm][dimension] for dimension in dimension_ids]
        dimension_drop[arm] = round3(max(0.0, max(drops)))
    classifications: dict[str, str] = {"baseline": "baseline"}
    limits = spec["limits"]
    for arm in ARM_IDS[1:]:
        uplift = means[arm] - means["baseline"]
        hard_ok = hard_gate_regressions[arm] == 0
        eligible = (
            hard_ok
            and uplift >= limits["quality_uplift"]
            and wins[arm] >= limits["minimum_block_wins"]
            and improved_cases[arm] >= limits["minimum_improved_positive_cases"]
            and dimension_drop[arm] <= limits["maximum_dimension_drop"]
        )
        near_threshold = any(
            abs(value - threshold) <= limits["threshold_review_margin"]
            for value, threshold in (
                (uplift, limits["quality_uplift"]),
                (float(wins[arm]), float(limits["minimum_block_wins"])),
                (float(improved_cases[arm]), float(limits["minimum_improved_positive_cases"])),
                (dimension_drop[arm], limits["maximum_dimension_drop"]),
            )
        )
        if near_threshold:
            review_items.append({"kind": "threshold-margin", "arm": arm, "uplift": round3(uplift), "wins": wins[arm], "improved_positive_cases": improved_cases[arm], "maximum_dimension_drop": dimension_drop[arm]})
        arm_review = any(item.get("arm") == arm or arm in item.get("arms", []) for item in review_items)
        if eligible:
            classifications[arm] = "revision-candidate-pending-human-review" if arm_review else "revision-candidate"
        elif not hard_ok or uplift < 0:
            classifications[arm] = "rejected"
        else:
            classifications[arm] = "inconclusive"
    repository_after = repository_snapshot()
    parity = repository_after == manifest["repository_before"]
    generator_calls = sum(
        result["telemetry"].get("scored_model_calls", result["telemetry"]["model_calls"])
        for result in results.values()
    )
    generator_attempt_calls = sum(
        result["telemetry"].get("attempt_model_calls", result["telemetry"]["model_calls"])
        for result in results.values()
    )
    generator_failed_attempts = sum(result["telemetry"].get("failed_attempts", 0) for result in results.values())
    report = {
        "schema": REPORT_SCHEMA,
        "experiment_id": spec["experiment_id"],
        "statistical_significance_claimed": False,
        "repository_parity": parity,
        "repository_before_sha256": digest(manifest["repository_before"]),
        "repository_after_sha256": digest(repository_after),
        "completed_outputs": len(results),
        "generator_calls": generator_calls,
        "generator_attempt_calls": generator_attempt_calls,
        "generator_failed_attempts": generator_failed_attempts,
        "judge_calls": judge_calls,
        "judge_attempt_calls": judge_attempt_calls,
        "judge_failed_attempts": judge_failed_attempts,
        "quality_means": means,
        "case_quality_means": case_quality_means,
        "case_deltas_vs_baseline": case_deltas_vs_baseline,
        "dimension_means": dimension_means,
        "wins_over_baseline": wins,
        "improved_positive_cases": improved_cases,
        "maximum_dimension_drop": dimension_drop,
        "hard_gate_failures": arm_hard_failures,
        "hard_gate_failures_by_gate": arm_hard_failures_by_gate,
        "hard_gate_regressions": hard_gate_regressions,
        "hard_gate_uncertain": arm_hard_uncertain,
        "mean_latency_ms": {arm: round3(mean(values)) for arm, values in arm_latency.items()},
        "mean_tokens": {arm: round3(mean(values)) for arm, values in arm_tokens.items()},
        "classifications": classifications,
        "human_review_required": bool(review_items),
        "human_review_items": review_items,
        "authority_effect": "none",
        "recursive_learning_status": "not-outcome-evidence",
    }
    return report


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# Ideation Research-Hypothesis Stress Test",
        "",
        f"- Repository parity: `{'PASS' if report['repository_parity'] else 'FAIL'}`",
        f"- Completed outputs: `{report['completed_outputs']}`",
        f"- Generator scored calls: `{report['generator_calls']}`",
        f"- Generator attempts: `{report['generator_attempt_calls']}` "
        f"(`{report['generator_failed_attempts']}` failed)",
        f"- Judge scored calls: `{report['judge_calls']}`",
        f"- Judge attempts: `{report['judge_attempt_calls']}` "
        f"(`{report['judge_failed_attempts']}` failed)",
        f"- Human review required: `{'yes' if report['human_review_required'] else 'no'}`",
        "- Statistical-significance claim: `none`",
        "",
        "## Arm Results",
        "",
        "| Arm | Mean quality | Wins vs baseline | Positive cases improved | Hard failures | Gate regressions | Classification |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for arm in ARM_IDS:
        lines.append(
            f"| {arm} | {report['quality_means'][arm]:.3f} | {report['wins_over_baseline'][arm]} | "
            f"{report['improved_positive_cases'][arm]} | {report['hard_gate_failures'][arm]} | "
            f"{report['hard_gate_regressions'][arm]} | "
            f"{report['classifications'][arm]} |"
        )
    lines.extend(("", "## Case-Level Quality", ""))
    lines.extend(
        (
            "| Case | Baseline | Method router (delta) | Anti-slop (delta) | Role-separated (delta) |",
            "|---|---:|---:|---:|---:|",
        )
    )
    for case_id, scores in report["case_quality_means"].items():
        deltas = report["case_deltas_vs_baseline"][case_id]
        lines.append(
            f"| {case_id} | {scores['baseline']:.3f} | {scores['method-router']:.3f} "
            f"({deltas['method-router']:+.3f}) | {scores['anti-slop']:.3f} "
            f"({deltas['anti-slop']:+.3f}) | {scores['role-separated']:.3f} "
            f"({deltas['role-separated']:+.3f}) |"
        )
    lines.extend(("", "## Hard-Gate Failures by Gate", ""))
    lines.extend(
        (
            "| Gate | Baseline | Method router | Anti-slop | Role-separated |",
            "|---|---:|---:|---:|---:|",
        )
    )
    for gate_id in report["hard_gate_failures_by_gate"]["baseline"]:
        counts = report["hard_gate_failures_by_gate"]
        lines.append(
            f"| {gate_id} | {counts['baseline'][gate_id]} | {counts['method-router'][gate_id]} | "
            f"{counts['anti-slop'][gate_id]} | {counts['role-separated'][gate_id]} |"
        )
    lines.extend(("", "## Boundaries", "", "An intervention must introduce zero case-level hard-gate regressions to become a revision candidate. Results are independent benchmark evidence only. They do not change the Ideation contract, authorize repository mutation, or establish later-use outcome evidence for Recursive Learn.", ""))
    return "\n".join(lines)


def write_report(spec: dict[str, Any], root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    report = report_data(spec, root, manifest)
    write_json(root / "report.json", report)
    write_text(root / "report.md", render_report(report))
    write_json(root / "human-review.json", {"schema": REPORT_SCHEMA, "items": report["human_review_items"]})
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the private, read-only Ideation behavioral benchmark.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("manifest", "generate", "judge", "report"):
        command = sub.add_parser(name)
        command.add_argument("--temp-root", type=Path, default=DEFAULT_RUN_ROOT)
        if name in {"generate", "judge"}:
            command.add_argument("--workers", type=int, default=4)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        spec = load_spec()
        root = ensure_external_root(args.temp_root)
        if args.command == "manifest":
            manifest = build_manifest(spec, root)
            result = {
                "status": "frozen",
                "manifest_sha256": manifest["manifest_sha256"],
                "scored_outputs": manifest["scored_output_target"],
                "generator_calls": manifest["generator_call_target"],
                "judge_calls": manifest["judge_call_target"],
            }
        else:
            manifest = load_manifest(spec, root)
            if args.command == "generate":
                result = generate_all(spec, root, manifest, workers=args.workers)
            elif args.command == "judge":
                result = judge_all(spec, root, manifest, workers=args.workers)
            else:
                result = write_report(spec, root, manifest)
                if not result["repository_parity"]:
                    write_json(root / "repository-parity-failure.json", result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result.get("status") == "incomplete" or result.get("repository_parity") is False:
            raise SystemExit(1)
    except (BenchmarkError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(f"ideation-benchmark error: {error}") from error


if __name__ == "__main__":
    main()

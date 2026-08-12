from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "system-improvement"
LEDGER_JSON_PATH = TRACKER_ROOT / "recursive-learning-ledger.json"
LEDGER_MD_PATH = TRACKER_ROOT / "recursive-learning-ledger.md"
OUTCOME_RECEIPT_ROOT = TRACKER_ROOT / "recursive-learning-outcomes"

ASSESSOR_IMPLEMENTATION_PATHS = (
    "docs/skill-drafts/recursive-learn/SKILL.md",
    "scripts/recursive_learning_ledger.py",
    "tests/test_recursive_learning_ledger.py",
)

ENTRY_ID_RE = re.compile(r"^RSI-\d{8}-\d{2}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
REFERENCE_ID_RE = re.compile(r"^MJTR-\d{8}-v[1-9]\d*$")
REQUIRED_STAGES = ("observation", "diagnosis", "intervention", "validation", "outcome")
ALLOWED_CLASSES = {
    "closed-feedback-loop",
    "recursive-governance",
    "partial-feedback-loop",
}
ALLOWED_CLOSURE_STATES = {"validated", "measured", "partial", "superseded"}
ASSESSMENT_STATES = {
    "non-candidate",
    "observation-only",
    "partial-candidate",
    "admissible",
    "already-represented",
}


class LearningError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def atomic_write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(value)
    temporary.replace(path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, pretty_json(value))


def replace_file(source: Path, target: Path) -> None:
    source.replace(target)


def atomic_write_ledger_pair(ledger: dict[str, Any]) -> None:
    json_temporary = LEDGER_JSON_PATH.with_name(f".{LEDGER_JSON_PATH.name}.pair-{os.getpid()}")
    markdown_temporary = LEDGER_MD_PATH.with_name(f".{LEDGER_MD_PATH.name}.pair-{os.getpid()}")
    original_json = LEDGER_JSON_PATH.read_bytes()
    original_markdown = LEDGER_MD_PATH.read_bytes()
    try:
        json_temporary.write_text(pretty_json(ledger), encoding="utf-8", newline="\n")
        markdown_temporary.write_text(render_markdown(ledger), encoding="utf-8", newline="\n")
        failures = validate_ledger(json_path=json_temporary, markdown_path=markdown_temporary)
        if failures:
            raise LearningError("; ".join(failures))
        replace_file(json_temporary, LEDGER_JSON_PATH)
        try:
            replace_file(markdown_temporary, LEDGER_MD_PATH)
        except OSError:
            atomic_write_bytes(LEDGER_JSON_PATH, original_json)
            atomic_write_bytes(LEDGER_MD_PATH, original_markdown)
            raise
    finally:
        for path in (json_temporary, markdown_temporary):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass


def external_output(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return resolved
    raise LearningError(f"recursive-learning candidate output must be outside Git: {resolved}")


def governed_outcome_output(path: Path, *, root: Path = OUTCOME_RECEIPT_ROOT) -> Path:
    resolved = path.expanduser().resolve()
    governed_root = root.resolve()
    try:
        resolved.relative_to(governed_root)
    except ValueError as error:
        raise LearningError(
            f"recursive-learning outcome receipt must be under {governed_root}: {resolved}"
        ) from error
    if resolved.suffix.casefold() != ".json":
        raise LearningError("recursive-learning outcome receipt must be JSON")
    return resolved


def repository_evidence_path(value: str, *, repo_root: Path = REPO_ROOT) -> str:
    normalized = value.replace("\\", "/").strip()
    if not normalized or Path(normalized).is_absolute() or normalized.startswith("../"):
        raise LearningError("baseline_ref must be a repository-relative path")
    if _is_journal_path(normalized):
        raise LearningError("journal context cannot serve as an outcome-receipt baseline")
    if not (repo_root / normalized).is_file():
        raise LearningError(f"outcome-receipt baseline does not resolve: {normalized}")
    return normalized


def parse_observed_at(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as error:
        raise LearningError("observed_at must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise LearningError("observed_at must include a timezone")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def persist_outcome_receipt(path: Path, encoded: bytes, *, check: bool) -> tuple[str, bool]:
    existing = path.read_bytes() if path.is_file() else None
    if existing is not None and existing != encoded:
        raise LearningError(f"refusing to overwrite a different outcome receipt: {path}")
    wrote = not check and existing is None
    if wrote:
        atomic_write_bytes(path, encoded)
    return ("current" if existing is not None else ("ready" if check else "written"), wrote)


def admission_statement(entry_id: str, candidate_digest: str) -> str:
    return f"Admit recursive learning entry {entry_id} with digest {candidate_digest}."


def load_ledger(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or LEDGER_JSON_PATH).read_text(encoding="utf-8"))


def render_markdown(ledger: dict[str, Any]) -> str:
    entries = sorted(ledger.get("entries", []), key=lambda item: item["id"])
    lines = [
        "# Recursive Learning Ledger",
        "",
        "Generated from `recursive-learning-ledger.json`. Do not edit this file directly.",
        "",
        f"Status: `{ledger.get('status', '')}`",
        "",
        str(ledger.get("scope_note", "")),
        "",
        "Method: [recursive-learning-ledger.md](../../method/recursive-learning-ledger.md)",
        "",
        "## Entries",
        "",
        "| ID | Date | Class | Closure | Improvement |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        lines.append(
            f"| `{entry['id']}` | `{entry['date']}` | `{entry['class']}` | "
            f"`{entry['closure_state']}` | {entry['title']} |"
        )
    for entry in entries:
        lines.extend(
            [
                "",
                f"## `{entry['id']}` — {entry['title']}",
                "",
                f"- Class: `{entry['class']}`",
                f"- Closure: `{entry['closure_state']}`",
            ]
        )
        if entry.get("journal_context_refs"):
            lines.append(
                "- Journal context: "
                + ", ".join(f"`{value}`" for value in entry["journal_context_refs"])
            )
        for stage_name in REQUIRED_STAGES:
            stage = entry[stage_name]
            lines.extend(
                [
                    "",
                    f"### {stage_name.title()}",
                    "",
                    stage["summary"],
                    "",
                    "Evidence:",
                    "",
                    *(
                        f"- [`{path}`](../../../{path})"
                        for path in stage["evidence_paths"]
                    ),
                ]
            )
            if stage_name == "intervention":
                commits = ", ".join(f"`{value}`" for value in stage["commits"])
                lines.extend(["", f"Commits: {commits}."])
            if stage_name == "outcome":
                lines.extend(["", f"Measure: {stage['measure']}"])
        lines.extend(
            [
                "",
                "### Next Measure",
                "",
                entry["next_measure"],
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _duplicate_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def _is_journal_path(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return normalized.startswith("mira/journal/") or normalized in {
        "mira/journal-registry.json",
        "mira/journal.md",
    }


def validate_entry(entry: Any, *, repo_root: Path = REPO_ROOT) -> list[str]:
    if not isinstance(entry, dict):
        return ["recursive learning entry must be an object"]
    failures: list[str] = []
    entry_id = str(entry.get("id", ""))
    if not ENTRY_ID_RE.fullmatch(entry_id):
        failures.append(f"invalid recursive learning ID: {entry_id or '<missing>'}")
    if entry.get("class") not in ALLOWED_CLASSES:
        failures.append(f"{entry_id}: invalid class")
    if entry.get("closure_state") not in ALLOWED_CLOSURE_STATES:
        failures.append(f"{entry_id}: invalid closure_state")
    if not str(entry.get("title", "")).strip() or not str(entry.get("next_measure", "")).strip():
        failures.append(f"{entry_id}: missing title or next_measure")
    context_refs = entry.get("journal_context_refs", [])
    if not isinstance(context_refs, list) or any(not REFERENCE_ID_RE.fullmatch(str(item)) for item in context_refs):
        failures.append(f"{entry_id}: malformed journal_context_refs")

    for stage_name in REQUIRED_STAGES:
        stage = entry.get(stage_name)
        if not isinstance(stage, dict):
            failures.append(f"{entry_id}: missing {stage_name} stage")
            continue
        if not str(stage.get("summary", "")).strip():
            failures.append(f"{entry_id}: {stage_name} missing summary")
        paths = stage.get("evidence_paths")
        if not isinstance(paths, list) or not paths:
            failures.append(f"{entry_id}: {stage_name} missing evidence_paths")
        else:
            for raw_path in paths:
                raw_text = str(raw_path)
                if _is_journal_path(raw_text):
                    failures.append(f"{entry_id}: journal context cannot serve as {stage_name} evidence: {raw_text}")
                    continue
                path = repo_root / raw_text
                if not path.exists():
                    failures.append(f"{entry_id}: missing evidence path: {raw_text}")
        if stage_name == "intervention":
            commits = stage.get("commits")
            if not isinstance(commits, list) or not commits:
                failures.append(f"{entry_id}: intervention missing commits")
            else:
                for commit in commits:
                    if not COMMIT_RE.fullmatch(str(commit)):
                        failures.append(f"{entry_id}: invalid commit reference: {commit}")
        if stage_name == "outcome" and not str(stage.get("measure", "")).strip():
            failures.append(f"{entry_id}: outcome missing measure")

    if entry.get("closure_state") == "measured":
        measure = str(entry.get("outcome", {}).get("measure", "")).casefold()
        if "pending" in measure:
            failures.append(f"{entry_id}: measured entry has pending outcome")
    if entry.get("class") == "partial-feedback-loop" and entry.get("closure_state") != "partial":
        failures.append(f"{entry_id}: partial feedback loop must have partial closure")
    return failures


def validate_ledger(
    *,
    repo_root: Path = REPO_ROOT,
    json_path: Path = LEDGER_JSON_PATH,
    markdown_path: Path = LEDGER_MD_PATH,
) -> list[str]:
    failures: list[str] = []
    if not json_path.is_file():
        return [f"recursive learning ledger missing: {json_path}"]
    try:
        ledger = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"recursive learning ledger invalid JSON: line {error.lineno}"]

    entries = ledger.get("entries")
    if not isinstance(entries, list):
        return ["recursive learning ledger missing entries list"]
    entry_ids = [str(entry.get("id", "")) for entry in entries if isinstance(entry, dict)]
    for duplicate in _duplicate_values(entry_ids):
        failures.append(f"duplicate recursive learning ID: {duplicate}")

    for entry in entries:
        failures.extend(validate_entry(entry, repo_root=repo_root))

    if not markdown_path.is_file():
        failures.append(f"recursive learning Markdown missing: {markdown_path}")
    elif markdown_path.read_text(encoding="utf-8") != render_markdown(ledger):
        failures.append("recursive learning Markdown drift from canonical JSON")
    return failures


def load_reference(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise LearningError(f"could not read journal technical reference: {error}") from error
    except json.JSONDecodeError as error:
        raise LearningError(f"invalid journal technical reference JSON: line {error.lineno}") from error
    if not isinstance(value, dict):
        raise LearningError("journal technical reference must be an object")
    return value


def assessment_basis_failures(reference: dict[str, Any]) -> list[str]:
    learning = reference.get("recursive_learning")
    inputs = learning.get("assessment_inputs") if isinstance(learning, dict) else None
    if not isinstance(inputs, dict):
        return []
    basis = inputs.get("assessment_basis")
    if not isinstance(basis, dict):
        return ["assessment_inputs requires assessment_basis"]
    failures: list[str] = []
    if basis.get("system_behavior_observed") is not True:
        failures.append("ordinary feature work is not recursive learning without observed system behavior")
    if basis.get("outcome_observation") not in {"pending", "observed"}:
        failures.append("assessment_basis outcome_observation must be pending or observed")
    if not isinstance(basis.get("post_intervention_use_observed"), bool):
        failures.append("assessment_basis requires post_intervention_use_observed")
    if basis.get("outcome_observation") == "observed" and basis.get("post_intervention_use_observed") is not True:
        failures.append("an observed outcome requires post-intervention use")
    return failures


def candidate_from_inputs(reference: dict[str, Any]) -> dict[str, Any] | None:
    learning = reference.get("recursive_learning")
    inputs = learning.get("assessment_inputs") if isinstance(learning, dict) else None
    if not isinstance(inputs, dict):
        return None
    candidate = copy.deepcopy(inputs)
    basis = candidate.pop("assessment_basis", {})
    partial = not (
        basis.get("outcome_observation") == "observed"
        and basis.get("post_intervention_use_observed") is True
    )
    candidate["class"] = "partial-feedback-loop" if partial else "closed-feedback-loop"
    candidate["closure_state"] = "partial" if partial else "measured"
    candidate["journal_context_refs"] = sorted(
        set(candidate.get("journal_context_refs", [])) | {str(reference.get("reference_id", ""))}
    )
    return candidate


def stage_dispositions(
    signal: str,
    candidate: dict[str, Any] | None,
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, dict[str, str]]:
    if signal == "none":
        return {
            stage: {
                "status": "not-applicable",
                "reason": "the journal reference declares no recursive-learning candidate signal",
            }
            for stage in REQUIRED_STAGES
        }
    if signal == "observation":
        return {
            stage: {
                "status": "context-only" if stage == "observation" else "missing",
                "reason": (
                    "journal observation is interpretive context, not admissible stage evidence"
                    if stage == "observation"
                    else f"no admissible {stage} stage was supplied"
                ),
            }
            for stage in REQUIRED_STAGES
        }
    dispositions: dict[str, dict[str, str]] = {}
    for stage_name in REQUIRED_STAGES:
        stage = candidate.get(stage_name) if isinstance(candidate, dict) else None
        if not isinstance(stage, dict):
            dispositions[stage_name] = {
                "status": "missing",
                "reason": f"no {stage_name} stage object was supplied",
            }
            continue
        paths = stage.get("evidence_paths")
        if not isinstance(paths, list) or not paths:
            dispositions[stage_name] = {
                "status": "missing",
                "reason": f"the {stage_name} stage has no evidence paths",
            }
            continue
        invalid_reasons: list[str] = []
        if not str(stage.get("summary", "")).strip():
            invalid_reasons.append("missing summary")
        for raw_path in paths:
            raw_text = str(raw_path)
            if _is_journal_path(raw_text):
                invalid_reasons.append(f"journal context is inadmissible evidence: {raw_text}")
            elif not (repo_root / raw_text).exists():
                invalid_reasons.append(f"evidence path does not resolve: {raw_text}")
        if stage_name == "intervention":
            commits = stage.get("commits")
            if not isinstance(commits, list) or not commits:
                invalid_reasons.append("missing commits")
            elif any(not COMMIT_RE.fullmatch(str(commit)) for commit in commits):
                invalid_reasons.append("invalid commit reference")
        if stage_name == "outcome" and not str(stage.get("measure", "")).strip():
            invalid_reasons.append("missing outcome measure")
        dispositions[stage_name] = {
            "status": "invalid" if invalid_reasons else "provided",
            "reason": "; ".join(invalid_reasons) if invalid_reasons else f"the {stage_name} stage supplies repository evidence",
        }
    return dispositions


def stage_evidence_scope(signal: str, candidate: dict[str, Any] | None) -> dict[str, Any]:
    paths: set[str] = set()
    if signal == "possible-loop" and isinstance(candidate, dict):
        for stage_name in REQUIRED_STAGES:
            stage = candidate.get(stage_name)
            if not isinstance(stage, dict):
                continue
            for raw_path in stage.get("evidence_paths", []):
                raw_text = str(raw_path)
                if not _is_journal_path(raw_text):
                    paths.add(raw_text)
    return {
        "mode": "full-stage-evidence" if signal == "possible-loop" else "reference-validation-only",
        "stage_evidence_paths": sorted(paths),
        "technical_grounding_reinspection_required": False,
    }


def assess_reference(reference: dict[str, Any], *, ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    reference_id = str(reference.get("reference_id", ""))
    if not REFERENCE_ID_RE.fullmatch(reference_id):
        raise LearningError("journal technical reference has malformed reference_id")
    learning = reference.get("recursive_learning")
    if not isinstance(learning, dict):
        raise LearningError("journal technical reference lacks recursive_learning")
    signal = learning.get("candidate_signal")
    if signal not in {"none", "observation", "possible-loop"}:
        raise LearningError("journal technical reference has invalid candidate_signal")
    current = ledger or load_ledger()
    represented = next(
        (
            entry["id"]
            for entry in current.get("entries", [])
            if reference_id in entry.get("journal_context_refs", [])
        ),
        None,
    )
    embedded_claim = learning.get("candidate_entry") is not None
    candidate = candidate_from_inputs(reference)
    candidate_failures = assessment_basis_failures(reference)
    if candidate is not None:
        candidate_failures.extend(validate_entry(candidate))
    if embedded_claim:
        candidate_failures.append("journal technical reference may not embed a classified candidate entry")
    if represented:
        status = "already-represented"
    elif signal == "none":
        status = "non-candidate"
    elif signal == "observation":
        status = "observation-only"
    elif candidate is None or candidate_failures or candidate.get("closure_state") == "partial":
        status = "partial-candidate"
    else:
        status = "admissible"
    return {
        "status": status,
        "reference_id": reference_id,
        "candidate_signal": signal,
        "represented_by": represented,
        "candidate_entry_id": candidate.get("id") if isinstance(candidate, dict) else None,
        "stage_map": {
            stage: list(candidate.get(stage, {}).get("evidence_paths", []))
            if isinstance(candidate, dict) and isinstance(candidate.get(stage), dict)
            else []
            for stage in REQUIRED_STAGES
        },
        "stage_dispositions": stage_dispositions(signal, candidate),
        "evidence_read_scope": stage_evidence_scope(signal, candidate),
        "failures": candidate_failures,
        "authority_effect": "none",
    }


def build_outcome_receipt(
    *,
    reference: dict[str, Any],
    reference_bytes: bytes,
    assessment: dict[str, Any],
    baseline_ref: str,
    observed_at: datetime,
    ledger_before: bytes,
    ledger_after: bytes,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    if ledger_before != ledger_after:
        raise LearningError("canonical recursive-learning ledger changed during outcome assessment")
    baseline = repository_evidence_path(baseline_ref, repo_root=repo_root)
    reference_id = str(reference["reference_id"])
    source_digests: dict[str, str] = {}
    for relative in ASSESSOR_IMPLEMENTATION_PATHS:
        path = repo_root / relative
        if not path.is_file():
            raise LearningError(f"outcome-receipt implementation path does not resolve: {relative}")
        source_digests[relative] = sha256_bytes(path.read_bytes())
    dispositions = assessment["stage_dispositions"]
    scope = assessment["evidence_read_scope"]
    entry_date = str(reference.get("entry_date", ""))
    receipt_date = entry_date.replace("-", "") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry_date) else f"{observed_at:%Y%m%d}"
    return {
        "schema_version": 1,
        "receipt_id": f"RLOR-{receipt_date}-{reference_id}",
        "status": "internal-verification",
        "subject": "recursive-learn-assessment",
        "observed_at": utc_text(observed_at),
        "baseline_ref": baseline,
        "input": {
            "reference_id": reference_id,
            "reference_sha256": sha256_bytes(reference_bytes),
            "journal_context_only": True,
        },
        "implementation": {
            "source_sha256": source_digests,
        },
        "assessment": assessment,
        "observed_measures": {
            "assessment_status": assessment["status"],
            "stage_dispositions_reported": len(dispositions),
            "stage_disposition_statuses": {
                stage: dispositions[stage]["status"] for stage in REQUIRED_STAGES
            },
            "evidence_read_scope_mode": scope["mode"],
            "stage_evidence_path_count": len(scope["stage_evidence_paths"]),
            "technical_grounding_reinspection_required": scope[
                "technical_grounding_reinspection_required"
            ],
            "candidate_emitted": assessment["candidate_entry_id"] is not None,
            "authority_effect": assessment["authority_effect"],
            "ledger_unchanged": True,
        },
        "ledger_integrity": {
            "path": str(LEDGER_JSON_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "sha256_before": sha256_bytes(ledger_before),
            "sha256_after": sha256_bytes(ledger_after),
            "mutation": False,
        },
        "limitations": [
            "This receipt records one post-intervention assessment and does not establish longitudinal persistence.",
            "The journal reference is context input only and supplies no recursive-learning stage evidence.",
            "This receipt does not establish RSI closure or grant admission authority.",
        ],
        "authority_effect": "none",
    }


def create_outcome_receipt(
    *,
    reference_path: Path,
    baseline_ref: str,
    observed_at_text: str,
    output: Path,
    check: bool,
) -> dict[str, Any]:
    resolved_reference = reference_path.expanduser().resolve()
    reference_bytes = resolved_reference.read_bytes()
    reference = validated_reference(resolved_reference)
    observed_at = parse_observed_at(observed_at_text)
    output_path = governed_outcome_output(output)
    ledger_before = LEDGER_JSON_PATH.read_bytes()
    assessment = assess_reference(reference, ledger=json.loads(ledger_before.decode("utf-8")))
    ledger_after = LEDGER_JSON_PATH.read_bytes()
    receipt = build_outcome_receipt(
        reference=reference,
        reference_bytes=reference_bytes,
        assessment=assessment,
        baseline_ref=baseline_ref,
        observed_at=observed_at,
        ledger_before=ledger_before,
        ledger_after=ledger_after,
    )
    encoded = pretty_json(receipt).encode("utf-8")
    status, wrote = persist_outcome_receipt(output_path, encoded, check=check)
    return {
        "status": status,
        "mutation": wrote,
        "output": str(output_path),
        "receipt_id": receipt["receipt_id"],
        "receipt_sha256": sha256_bytes(encoded),
        "assessment_status": receipt["assessment"]["status"],
        "ledger_unchanged": True,
        "authority_effect": "none",
    }


def candidate_from_reference(reference: dict[str, Any]) -> dict[str, Any]:
    assessment = assess_reference(reference)
    if assessment["status"] not in {"admissible", "partial-candidate"}:
        raise LearningError(f"journal technical reference is not admissible: {assessment['status']}")
    candidate = candidate_from_inputs(reference)
    if candidate is None:
        raise LearningError("journal technical reference lacks assessment_inputs")
    failures = validate_entry(candidate)
    if failures:
        raise LearningError("; ".join(failures))
    return candidate


def validated_reference(path: Path) -> dict[str, Any]:
    reference = load_reference(path)
    try:
        import mira_journal_references
    except ImportError as error:
        raise LearningError("journal technical-reference validator is unavailable") from error
    digest = str(reference.get("journal_content_sha256", ""))
    entry_date = str(reference.get("entry_date", ""))
    candidates = [path.expanduser().resolve().parent / "draft.md"]
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry_date):
        candidates.append(REPO_ROOT / "mira" / "journal" / f"{entry_date}.md")
    prose_path = next(
        (
            candidate for candidate in candidates
            if candidate.is_file() and sha256_bytes(candidate.read_bytes()) == digest
        ),
        None,
    )
    if prose_path is None:
        raise LearningError("journal technical reference prose does not resolve by digest")
    ledger = load_ledger()
    failures = mira_journal_references.validate_reference(
        reference,
        prose=prose_path.read_text(encoding="utf-8"),
        prose_sha256=digest,
        version_id=str(reference.get("journal_version_id", "")),
        ledger=ledger,
        repo_root=REPO_ROOT,
    )
    if failures:
        raise LearningError("; ".join(failures))
    return reference


def admit_candidate(
    candidate: dict[str, Any],
    *,
    authority_ref: str,
    approval_record_ref: str,
    check: bool,
) -> dict[str, Any]:
    failures = validate_entry(candidate)
    if failures:
        raise LearningError("; ".join(failures))
    ledger = load_ledger()
    entry_id = str(candidate["id"])
    if any(entry.get("id") == entry_id for entry in ledger.get("entries", [])):
        raise LearningError(f"recursive learning entry already exists: {entry_id}")
    digest = sha256_bytes(canonical_json(candidate).encode("utf-8"))
    try:
        import mira_journal
    except ImportError as error:
        raise LearningError("Mira continuity authority resolver is unavailable") from error
    if not mira_journal.SESSION_ID_RE.fullmatch(authority_ref):
        raise LearningError("recursive learning admission has malformed authority_ref")
    if not mira_journal.RECORD_ID_RE.fullmatch(approval_record_ref):
        raise LearningError("recursive learning admission has malformed approval_record_ref")
    rows = mira_journal.resolved_records_for_session(
        authority_ref,
        required_record_ids={approval_record_ref},
    )
    approval = rows.get(approval_record_ref)
    expected = admission_statement(entry_id, digest)
    if approval is None or approval.get("role") != "user" or mira_journal.row_text(approval).strip() != expected:
        raise LearningError("recursive learning admission record is not the exact digest-bound instruction")
    try:
        approval_time = mira_journal.parse_timestamp(str(approval.get("timestamp", "")), label="approval record timestamp")
    except mira_journal.JournalError as error:
        raise LearningError("recursive learning admission record has invalid timestamp") from error
    if approval_time > datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=5):
        raise LearningError("recursive learning admission record is implausibly in the future")
    admitted = copy.deepcopy(candidate)
    admitted["admission"] = {
        "approved_by": "operator",
        "authority_ref": authority_ref,
        "record_ref": approval_record_ref,
        "approved_at": mira_journal.utc_text(approval_time),
        "candidate_sha256": digest,
    }
    updated = copy.deepcopy(ledger)
    updated.setdefault("entries", []).append(admitted)
    updated["entries"].sort(key=lambda item: item["id"])
    if not check:
        atomic_write_ledger_pair(updated)
    return {
        "status": "ready" if check else "admitted",
        "mutation": not check,
        "entry_id": entry_id,
        "candidate_sha256": digest,
        "approval_statement": expected,
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Assess and govern recursive learning evidence.")
    root.add_argument("--write", action="store_true", help=argparse.SUPPRESS)
    root.add_argument("--check", action="store_true", help=argparse.SUPPRESS)
    subparsers = root.add_subparsers(dest="command")
    assess = subparsers.add_parser("assess", help="Assess a journal technical reference read-only.")
    assess.add_argument("--reference", type=Path, required=True)
    candidate = subparsers.add_parser("candidate", help="Build a private candidate from an admissible reference.")
    candidate.add_argument("--reference", type=Path, required=True)
    candidate.add_argument("--output", type=Path, required=True)
    candidate.add_argument("--check", action="store_true")
    receipt = subparsers.add_parser(
        "outcome-receipt",
        help="Record a deterministic post-intervention assessment outcome.",
    )
    receipt.add_argument("--reference", type=Path, required=True)
    receipt.add_argument("--baseline-ref", required=True)
    receipt.add_argument("--observed-at", required=True)
    receipt.add_argument("--output", type=Path, required=True)
    receipt.add_argument("--check", action="store_true")
    admit = subparsers.add_parser("admit", help="Admit an explicitly approved candidate to the canonical ledger.")
    admit.add_argument("--input", type=Path, required=True)
    admit.add_argument("--authority-ref", required=True)
    admit.add_argument("--approval-record-ref", required=True)
    admit.add_argument("--check", action="store_true")
    render = subparsers.add_parser("render", help="Render the canonical Markdown view.")
    render.add_argument("--check", action="store_true")
    subparsers.add_parser("validate", help="Validate the canonical ledger and Markdown view.")
    return root


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    return parser().parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    args = parse_args(arguments)
    try:
        if args.command == "assess":
            result = assess_reference(validated_reference(args.reference))
        elif args.command == "candidate":
            candidate = candidate_from_reference(validated_reference(args.reference))
            output = external_output(args.output)
            if not args.check:
                atomic_write_json(output, candidate)
            result = {
                "status": "ready" if args.check else "written",
                "mutation": not args.check,
                "output": str(output),
                "entry_id": candidate["id"],
                "candidate_sha256": sha256_bytes(canonical_json(candidate).encode("utf-8")),
            }
        elif args.command == "outcome-receipt":
            result = create_outcome_receipt(
                reference_path=args.reference,
                baseline_ref=args.baseline_ref,
                observed_at_text=args.observed_at,
                output=args.output,
                check=args.check,
            )
        elif args.command == "admit":
            candidate = json.loads(args.input.read_text(encoding="utf-8"))
            result = admit_candidate(
                candidate,
                authority_ref=args.authority_ref,
                approval_record_ref=args.approval_record_ref,
                check=args.check,
            )
        elif args.command == "render":
            expected = render_markdown(load_ledger())
            matches = LEDGER_MD_PATH.is_file() and LEDGER_MD_PATH.read_text(encoding="utf-8") == expected
            if not args.check:
                atomic_write_text(LEDGER_MD_PATH, expected)
            result = {"status": "current" if matches else ("stale" if args.check else "rendered"), "mutation": not args.check}
        else:
            if args.write:
                atomic_write_text(LEDGER_MD_PATH, render_markdown(load_ledger()))
            failures = validate_ledger() if args.check or args.command == "validate" or not args.write else []
            if failures:
                for failure in failures:
                    print(f"FAIL {failure}")
                return 1
            result = {"status": "valid", "mutation": bool(args.write)}
    except (LearningError, OSError, json.JSONDecodeError) as error:
        print(f"recursive-learn error: {error}")
        return 1
    print(canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

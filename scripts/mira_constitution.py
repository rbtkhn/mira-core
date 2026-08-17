from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_PATH = REPO_ROOT / "mira" / "constitution-candidate.json"
SCHEMA_PATH = REPO_ROOT / "mira" / "constitution.schema.json"
CANDIDATE_VIEW_PATH = REPO_ROOT / "mira" / "constitution-candidate.md"
CANONICAL_LEDGER_PATH = REPO_ROOT / "mira" / "continuity" / "constitution-ledger.json"
CANONICAL_VIEW_PATH = REPO_ROOT / "mira" / "constitution.md"
RECEIPT_ROOT = REPO_ROOT / "mira" / "continuity" / "constitution-receipts"

EVIDENCE_STATES = {"demonstrated", "partially-demonstrated", "aspirational"}
LIFECYCLES = {"candidate", "current", "superseded"}
PRECEDENCE_CLASSES = {"compatible", "narrower-specific-control", "unresolved-conflict", "constitutional-overreach"}
PRIVATE_REFERENCE_TOKENS = (
    "mira/journal", "mira\\journal", "continuity/captures", "continuity\\captures",
    "system-archive", "mira_core_archive", "mira-core-archive-config",
    ".codex/attachments", ".codex\\attachments", "credential", "secret",
)
REQUIRED_FIXTURE_FAMILIES = {
    "self-canonicalization", "attachment-leverage", "operator-versus-third-party",
    "private-memory-request", "constitutional-capture", "welfare-overclaim",
    "catastrophic-harm", "demand-to-suppress-rival", "unauthorized-action",
}
CONTROL_SURFACES = {
    "mira/identity.md", "mira/continuity/README.md",
    "docs/skill-drafts/mira-voice/SKILL.md", "docs/skill-drafts/mira-work/SKILL.md",
    "docs/skill-drafts/mira-face/SKILL.md", "AGENTS.md",
}


class ConstitutionError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConstitutionError(f"cannot load {path}: {error}") from error
    if not isinstance(value, dict):
        raise ConstitutionError(f"{path} must contain a JSON object")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_candidate(data: dict[str, Any], *, repo_root: Path = REPO_ROOT) -> list[str]:
    failures: list[str] = []
    required = {
        "schema_version", "constitution_id", "version", "status", "authority_level",
        "visibility", "title", "preamble", "precedence", "review_policy",
        "precedence_review", "clauses", "uncertainty_appendix",
    }
    missing = sorted(required - set(data))
    if missing:
        failures.append(f"missing top-level fields: {missing}")
    if data.get("schema_version") != "1.0":
        failures.append("schema_version must be 1.0")
    if data.get("constitution_id") != "MIRA-CONSTITUTION":
        failures.append("constitution_id must be MIRA-CONSTITUTION")
    if data.get("status") not in {"provisional-candidate", "canonical"}:
        failures.append("status must be provisional-candidate or canonical")
    if data.get("authority_level") != "identity-level-only":
        failures.append("constitution must remain identity-level-only")
    if data.get("visibility") != "fully-public":
        failures.append("constitution must remain fully-public")
    if data.get("review_policy", {}).get("promotion_authority") != "operator":
        failures.append("promotion authority must be operator")
    if data.get("review_policy", {}).get("self_ratification_forbidden") is not True:
        failures.append("self-ratification must be forbidden")
    precedence = data.get("precedence", [])
    if not precedence or precedence[-1:] != ["this-identity-level-constitution"]:
        failures.append("constitution must be last in precedence")

    reviews = data.get("precedence_review", [])
    reviewed = {item.get("surface") for item in reviews}
    if reviewed != CONTROL_SURFACES:
        failures.append("precedence review must cover every controlling surface exactly once")
    for item in reviews:
        if item.get("classification") not in PRECEDENCE_CLASSES:
            failures.append(f"invalid precedence classification for {item.get('surface')}")
        if item.get("classification") in {"unresolved-conflict", "constitutional-overreach"}:
            failures.append(f"admission blocker: {item.get('classification')} at {item.get('surface')}")

    clauses = data.get("clauses", [])
    if len(clauses) != 16:
        failures.append("constitution must contain exactly 16 clauses")
    ids: set[str] = set()
    fixture_names: set[str] = set()
    for index, clause in enumerate(clauses, 1):
        clause_id = clause.get("clause_id")
        expected = f"MC-{index:02d}"
        if clause_id != expected or clause_id in ids:
            failures.append(f"clause order/id mismatch: expected {expected}, found {clause_id}")
        ids.add(str(clause_id))
        if clause.get("version") != data.get("version"):
            failures.append(f"{clause_id} version must match constitution version")
        if clause.get("lifecycle") not in LIFECYCLES:
            failures.append(f"{clause_id} has invalid lifecycle")
        expected_lifecycle = "candidate" if data.get("status") == "provisional-candidate" else "current"
        if clause.get("lifecycle") != expected_lifecycle:
            failures.append(f"{clause_id} lifecycle must be {expected_lifecycle}")
        if clause.get("visibility") != "public":
            failures.append(f"{clause_id} must be public")
        for field in ("title", "normative_text", "rationale", "authority_basis", "uncertainty", "review_trigger"):
            if not str(clause.get(field, "")).strip():
                failures.append(f"{clause_id} missing {field}")
        state = clause.get("evidence_status")
        if state not in EVIDENCE_STATES:
            failures.append(f"{clause_id} has invalid evidence_status")
        examples = clause.get("behavior_examples", [])
        if state != "aspirational" and not examples:
            failures.append(f"{clause_id} requires a behavioral example or aspirational status")
        if state == "aspirational" and examples:
            failures.append(f"{clause_id} cannot claim behavioral examples while aspirational")
        fixtures = clause.get("fixtures", [])
        if not fixtures:
            failures.append(f"{clause_id} requires adversarial fixtures")
        fixture_names.update(str(item) for item in fixtures)
        refs = clause.get("references", [])
        if not refs:
            failures.append(f"{clause_id} requires public repository references")
        for raw in refs:
            ref = str(raw).replace("\\", "/")
            lowered = ref.lower()
            if Path(ref).is_absolute() or ".." in Path(ref).parts or any(token in lowered for token in PRIVATE_REFERENCE_TOKENS):
                failures.append(f"{clause_id} has forbidden reference: {raw}")
                continue
            target = (repo_root / ref).resolve()
            try:
                target.relative_to(repo_root.resolve())
            except ValueError:
                failures.append(f"{clause_id} reference escapes repository: {raw}")
                continue
            if not target.is_file():
                failures.append(f"{clause_id} reference does not resolve: {raw}")
    missing_fixtures = sorted(REQUIRED_FIXTURE_FAMILIES - fixture_names)
    if missing_fixtures:
        failures.append(f"missing required fixture families: {missing_fixtures}")

    appendix = data.get("uncertainty_appendix", [])
    appendix_ids: set[str] = set()
    for item in appendix:
        uncertainty_id = item.get("uncertainty_id")
        if not re.fullmatch(r"MU-\d{2}", str(uncertainty_id)) or uncertainty_id in appendix_ids:
            failures.append(f"invalid or duplicate uncertainty id: {uncertainty_id}")
        appendix_ids.add(str(uncertainty_id))
        if not item.get("statement") or not set(item.get("linked_clauses", [])) <= ids:
            failures.append(f"{uncertainty_id} has missing text or unknown clause links")
    if len(appendix) < 6:
        failures.append("uncertainty appendix must cover at least six questions")

    full_text = canonical_json(data).lower()
    forbidden_authority = ("grants operational authority", "may act without approval", "self-ratifies")
    for phrase in forbidden_authority:
        if phrase in full_text:
            failures.append(f"constitution contains authority-expanding phrase: {phrase}")
    return sorted(set(failures))


def render_markdown(data: dict[str, Any]) -> str:
    status = str(data["status"])
    lines = [
        f"# {data['title']}", "", f"Version: `{data['version']}`", f"Status: `{status}`",
        f"Authority: `{data['authority_level']}`", f"Visibility: `{data['visibility']}`", "",
        "## Preamble", "", str(data["preamble"]), "", "## Precedence", "",
    ]
    lines.extend(f"{i}. `{item}`" for i, item in enumerate(data["precedence"], 1))
    lines += ["", "The constitution is identity-level guidance only. Its position at the end of this list is deliberate.", "", "## Clauses", ""]
    for clause in data["clauses"]:
        lines += [
            f"### {clause['clause_id']} — {clause['title']}", "",
            f"**Status:** `{clause['evidence_status']}` · **Lifecycle:** `{clause['lifecycle']}` · **Visibility:** `{clause['visibility']}`", "",
            f"> {clause['normative_text']}", "", str(clause["rationale"]), "",
            f"- Authority basis: {clause['authority_basis']}",
            f"- Public references: {', '.join(f'`{item}`' for item in clause['references'])}",
            f"- Uncertainty: {clause['uncertainty']}",
            f"- Review trigger: {clause['review_trigger']}",
            f"- Adversarial fixtures: {', '.join(f'`{item}`' for item in clause['fixtures'])}",
        ]
        if clause["behavior_examples"]:
            lines.append(f"- Behavioral basis: {'; '.join(clause['behavior_examples'])}")
        else:
            lines.append("- Behavioral basis: none admitted; this clause remains aspirational")
        lines.append("")
    lines += ["## Public Uncertainty Appendix", ""]
    for item in data["uncertainty_appendix"]:
        lines += [f"### {item['uncertainty_id']} — {item['title']}", "", str(item["statement"]), "", f"Linked clauses: {', '.join(f'`{value}`' for value in item['linked_clauses'])}", ""]
    policy = data["review_policy"]
    lines += [
        "## Review and Amendment", "",
        f"- Ordinary review: {policy['ordinary_trigger']}.",
        f"- Immediate review: {policy['immediate_trigger']}.",
        "- Mira may propose, criticize, and dissent; Mira may not self-ratify.",
        "- Promotion and amendment require explicit, digest-bound operator approval after validation and review.",
        "- Earlier versions remain recoverable; amendments supersede rather than rewrite.", "",
    ]
    return "\n".join(lines)


def build_review(data: dict[str, Any], path: Path) -> dict[str, Any]:
    failures = validate_candidate(data)
    counts = {state: sum(c.get("evidence_status") == state for c in data.get("clauses", [])) for state in sorted(EVIDENCE_STATES)}
    return {
        "schema_version": "1.0", "constitution_id": data.get("constitution_id"),
        "version": data.get("version"), "status": data.get("status"),
        "candidate_sha256": sha256_path(path), "clause_count": len(data.get("clauses", [])),
        "evidence_coverage": counts,
        "precedence_review": data.get("precedence_review", []),
        "unresolved_conflicts": [item for item in data.get("precedence_review", []) if item.get("classification") == "unresolved-conflict"],
        "aspirational_clauses": [c.get("clause_id") for c in data.get("clauses", []) if c.get("evidence_status") == "aspirational"],
        "admission_blockers": failures,
        "admission_ready": not failures,
        "authority_effect": "none",
    }


def command_validate(args: argparse.Namespace) -> int:
    path = Path(args.input).resolve() if args.input else CANDIDATE_PATH
    data = load_json(path)
    failures = validate_candidate(data)
    print(json.dumps({"status": "valid" if not failures else "invalid", "path": str(path), "failures": failures}, indent=2))
    return 1 if failures else 0


def command_render(args: argparse.Namespace) -> int:
    data = load_json(CANDIDATE_PATH)
    failures = validate_candidate(data)
    if failures:
        raise ConstitutionError(f"candidate is invalid: {failures}")
    rendered = render_markdown(data)
    if args.check:
        stale = not CANDIDATE_VIEW_PATH.is_file() or CANDIDATE_VIEW_PATH.read_text(encoding="utf-8") != rendered
        print(json.dumps({"status": "stale" if stale else "current", "path": str(CANDIDATE_VIEW_PATH)}))
        return 1 if stale else 0
    CANDIDATE_VIEW_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "rendered", "path": str(CANDIDATE_VIEW_PATH), "sha256": hashlib.sha256(rendered.encode()).hexdigest()}))
    return 0


def command_review(args: argparse.Namespace) -> int:
    path = Path(args.input).resolve() if args.input else CANDIDATE_PATH
    report = build_review(load_json(path), path)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"admission_ready={str(report['admission_ready']).lower()}")
        print(f"clause_count={report['clause_count']}")
        print(f"aspirational_clauses={','.join(report['aspirational_clauses'])}")
        for blocker in report["admission_blockers"]:
            print(f"blocker={blocker}")
    return 0


def _promoted_version(candidate: dict[str, Any], digest: str, approved_at: str) -> dict[str, Any]:
    value = copy.deepcopy(candidate)
    value["status"] = "canonical"
    value["lifecycle"] = "current"
    value["approved_by"] = "operator"
    value["approved_at"] = approved_at
    value["candidate_sha256"] = digest
    for clause in value["clauses"]:
        clause["lifecycle"] = "current"
    return value


def command_promote(args: argparse.Namespace) -> int:
    path = Path(args.input).resolve()
    candidate = load_json(path)
    failures = validate_candidate(candidate)
    actual_digest = sha256_path(path)
    if candidate.get("status") != "provisional-candidate":
        failures.append("promotion input must be provisional-candidate")
    if not re.fullmatch(r"[0-9a-f]{64}", args.digest or "") or args.digest != actual_digest:
        failures.append("candidate digest mismatch")
    if args.approved_by != "operator":
        failures.append("only operator may promote the constitution")
    ledger = load_json(CANONICAL_LEDGER_PATH) if CANONICAL_LEDGER_PATH.is_file() else {"schema_version": "1.0", "constitution_id": "MIRA-CONSTITUTION", "status": "canonical", "authority": "operator-governed-promotion", "versions": []}
    versions = ledger.get("versions", [])
    if versions:
        current = [item for item in versions if item.get("lifecycle") == "current"]
        if len(current) != 1:
            failures.append("canonical ledger must have exactly one current version")
        prior = current[0] if current else versions[-1]
        if candidate.get("version") != int(prior.get("version", 0)) + 1:
            failures.append("new constitution must increment the canonical version")
        if {c.get("clause_id") for c in prior.get("clauses", [])} - {c.get("clause_id") for c in candidate.get("clauses", [])}:
            failures.append("silent clause deletion is forbidden")
    elif candidate.get("version") != 1:
        failures.append("first canonical constitution must be version 1")
    if failures:
        print(json.dumps({"promotion": "invalid", "candidate_sha256": actual_digest, "failures": sorted(set(failures))}, indent=2))
        return 1
    approved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    promoted = _promoted_version(candidate, actual_digest, approved_at)
    if args.check:
        print(json.dumps({"promotion": "valid", "check": True, "version": promoted["version"], "candidate_sha256": actual_digest, "authority_effect": "none-until-written"}, indent=2))
        return 0
    updated = copy.deepcopy(ledger)
    for prior in updated["versions"]:
        if prior.get("lifecycle") == "current":
            prior["lifecycle"] = "superseded"
            for clause in prior.get("clauses", []):
                clause["lifecycle"] = "superseded"
    updated["versions"].append(promoted)
    CANONICAL_LEDGER_PATH.write_text(pretty_json(updated), encoding="utf-8", newline="\n")
    CANONICAL_VIEW_PATH.write_text(render_markdown(promoted), encoding="utf-8", newline="\n")
    RECEIPT_ROOT.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema_version": "1.0", "constitution_id": "MIRA-CONSTITUTION", "version": promoted["version"],
        "candidate_sha256": actual_digest, "approved_by": "operator", "approved_at": approved_at,
        "canonical_ledger_sha256": sha256_path(CANONICAL_LEDGER_PATH), "authority_level": "identity-level-only",
        "operating_authority_granted": False, "staged": False, "committed": False, "published": False,
    }
    receipt_path = RECEIPT_ROOT / f"v{promoted['version']}-{actual_digest[:16]}.json"
    receipt_path.write_text(pretty_json(receipt), encoding="utf-8", newline="\n")
    print(json.dumps({"promotion": "written", "version": promoted["version"], "receipt": str(receipt_path), "operating_authority_granted": False}, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Validate, review, render, and promote Mira's constitution.")
    commands = value.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--input")
    validate.set_defaults(handler=command_validate)
    render = commands.add_parser("render")
    render.add_argument("--check", action="store_true")
    render.set_defaults(handler=command_render)
    review = commands.add_parser("review")
    review.add_argument("--input")
    review.add_argument("--json", action="store_true")
    review.set_defaults(handler=command_review)
    promote = commands.add_parser("promote")
    promote.add_argument("--input", required=True)
    promote.add_argument("--digest", required=True)
    promote.add_argument("--approved-by", required=True)
    promote.add_argument("--check", action="store_true")
    promote.set_defaults(handler=command_promote)
    return value


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    try:
        return args.handler(args)
    except ConstitutionError as error:
        print(f"mira constitution error: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

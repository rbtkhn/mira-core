from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from collections import Counter, defaultdict, deque
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
REALITY_ROOT = NG_ROOT / "work" / "reality"
LEGACY_REGISTRY_PATH = NG_ROOT / "work" / "verification" / "source-registry.md"
LEGACY_PACKETS_ROOT = NG_ROOT / "work" / "verification" / "packets"
DAILY_ROOT = NG_ROOT / "work" / "daily"
VIEWS_ROOT = REALITY_ROOT / "views"

KIND_DIRS = {
    "source": "sources",
    "claim": "claims",
    "observable": "observables",
    "evidence": "evidence",
    "investigation": "investigations",
    "assessment": "assessments",
    "transition": "transitions",
    "relation": "relations",
    "domain_profile": "domain-profiles",
}
ID_PATTERNS = {
    "source": re.compile(r"VSRC-[A-Z0-9-]+$"),
    "claim": re.compile(r"(?:OPC-\d{8}-\d{2}|NG-\d{8}-F\d{2}|CLM-\d{8}-\d{3})$"),
    "observable": re.compile(r"OBS-\d{8}-\d{3}$"),
    "evidence": re.compile(r"EVD-\d{8}-\d{3}$"),
    "investigation": re.compile(r"VER-\d{8}-\d{2}$"),
    "assessment": re.compile(r"ADJ-\d{8}-\d{3}$"),
    "transition": re.compile(r"EPT-\d{8}-\d{3}$"),
    "relation": re.compile(r"REL-\d{8}-\d{3}$"),
    "domain_profile": re.compile(r"DOMAIN-[A-Z0-9-]+$"),
}

CLAIM_TYPES = {
    "operational_factual",
    "forecast",
    "causal",
    "interpretive",
    "actor_position",
    "normative",
}
OUTCOMES = {
    "operational_factual": {"supported", "contested", "disconfirmed", "unresolvable"},
    "forecast": {"hit", "miss", "mixed", "unresolvable", "excluded"},
    "causal": {"strengthened_relative_to_alternatives", "weakened", "contested", "unresolved"},
    "interpretive": {"retained", "narrowed", "superseded", "unresolved"},
    "actor_position": {"documented", "contested_attribution", "obsolete"},
    "normative": {"not_empirically_adjudicable"},
}
POSITIVE_EMPIRICAL_OUTCOMES = {
    "supported",
    "hit",
    "strengthened_relative_to_alternatives",
    "documented",
}
ASSESSMENT_STATUSES = {
    "draft",
    "provisional_assessed",
    "canonical_assessed",
    "canonical_with_language_waiver",
}
SOURCE_STATUSES = {"candidate", "active", "degraded", "retired"}
RELATION_TYPES = {
    "supports",
    "challenges",
    "contextualizes",
    "derived_from",
    "depends_on",
    "supersedes",
    "resolves",
    "attributed_to",
    "affects",
}
TRANSITION_TYPES = {"world", "evidence", "interpretation", "confidence", "authorization", "presentation"}
TRANSLATION_PROVENANCE = {
    "not_required",
    "official_edition",
    "named_human_translation",
    "operator_translation",
    "machine_assisted_disclosed",
}
EVIDENCE_ROLES = {"observational", "official_position", "professional_reporting", "context_only", "derived_editorial"}
CANONICAL_REVIEWER = "operator"
REQUIRED_SIGNOFFS = 1
COMMON_REQUIRED = {"schema_version", "id", "kind", "created_at", "created_by", "as_of", "status", "revision_of"}
SOURCE_FIELDS = {
    "name", "canonical_url", "domain", "observables", "evidence_class", "perspective",
    "geography", "origin_languages", "access_languages", "translation_provenance", "access",
    "open_fallback", "latency", "originating_chain_rule", "known_failure_modes", "appropriate_uses",
    "inappropriate_uses", "review_history", "geopolitical_environment", "order",
}
LEGACY_REGISTRY_ROW_RE = re.compile(r"^\|\s*`(?P<id>VSRC-[A-Z0-9-]+)`\s*\|(?P<rest>.+)\|$", re.MULTILINE)
LEGACY_EVIDENCE_RE = re.compile(
    r"^\|\s*`(?P<id>EVID-\d{2})`\s*\|\s*`(?P<registry_id>VSRC-[A-Z0-9-]+)`\s*\|\s*(?P<url>https?://[^| ]+)\s*\|"
    r"\s*`(?P<retrieved>[^`]+)`\s*\|\s*`(?P<event>[^`]+)`\s*\|"
    r"\s*`(?P<source_type>[^`]+)`\s*\|\s*`(?P<chain>[^`]+)`\s*\|"
    r"\s*`(?P<direction>[^`]+)`\s*\|\s*`(?P<translation>[^`]+)`\s*\|\s*(?P<limitation>.*?)\s*\|$",
    re.MULTILINE,
)


class RealityError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def record_path(kind: str, record_id: str, root: Path = REALITY_ROOT) -> Path:
    return root / KIND_DIRS[kind] / f"{record_id}.json"


def write_record(record: dict[str, Any], root: Path = REALITY_ROOT, *, overwrite: bool = False) -> Path:
    kind = record.get("kind", "")
    record_id = record.get("id", "")
    if kind not in KIND_DIRS or not ID_PATTERNS[kind].fullmatch(record_id):
        raise RealityError(f"invalid record identity: {kind} {record_id}")
    path = record_path(kind, record_id, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = canonical_json(record)
    if path.exists() and not overwrite:
        if path.read_text(encoding="utf-8") == rendered:
            return path
        raise RealityError(f"refusing to overwrite existing record: {path}")
    path.write_text(rendered, encoding="utf-8", newline="\n")
    return path


def load_records(root: Path = REALITY_ROOT) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for kind, dirname in KIND_DIRS.items():
        folder = root / dirname
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.json")):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                records[f"INVALID:{path.as_posix()}"] = {"kind": kind, "_error": str(exc), "_path": path.as_posix()}
                continue
            record["_path"] = path.as_posix()
            record_id = str(record.get("id", f"INVALID:{path.as_posix()}"))
            if record_id in records:
                record["_duplicate"] = True
            records[record_id] = record
    return records


def clean_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if not key.startswith("_")}


def validate_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value[:10])
        return True
    except ValueError:
        return False


def validate_record(record: dict[str, Any], records: dict[str, dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    label = str(record.get("id", record.get("_path", "unknown")))
    if "_error" in record:
        return [f"{label}: invalid JSON: {record['_error']}"]
    missing = COMMON_REQUIRED - set(record)
    failures.extend(f"{label}: missing field {field}" for field in sorted(missing))
    kind = record.get("kind")
    if kind not in KIND_DIRS:
        return failures + [f"{label}: invalid kind {kind}"]
    if not ID_PATTERNS[kind].fullmatch(label):
        failures.append(f"{label}: invalid ID for kind {kind}")
    if record.get("schema_version") != 1:
        failures.append(f"{label}: unsupported schema_version {record.get('schema_version')}")
    if not validate_date(record.get("as_of")):
        failures.append(f"{label}: invalid as_of")
    revision = record.get("revision_of")
    if revision not in {None, "none"} and revision not in records:
        failures.append(f"{label}: revision_of does not resolve: {revision}")

    if kind == "source":
        failures.extend(f"{label}: missing field {field}" for field in sorted(SOURCE_FIELDS - set(record)))
        if record.get("status") not in SOURCE_STATUSES:
            failures.append(f"{label}: invalid source status {record.get('status')}")
        for field in ("origin_languages", "access_languages", "review_history"):
            if not isinstance(record.get(field), list) or not record.get(field):
                failures.append(f"{label}: {field} must be a non-empty list")
        parsed = urlparse(str(record.get("canonical_url", "")))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            failures.append(f"{label}: malformed canonical_url")
    elif kind == "claim":
        claim_type = record.get("claim_type")
        if claim_type not in CLAIM_TYPES:
            failures.append(f"{label}: invalid claim_type {claim_type}")
        for field in ("text", "scope", "crisis_object", "consequence", "empirical_eligibility", "claimant_refs", "source_refs"):
            if field not in record:
                failures.append(f"{label}: missing field {field}")
        if record.get("consequence") not in {"high", "medium", "low"}:
            failures.append(f"{label}: invalid consequence")
        if claim_type == "normative" and record.get("empirical_eligibility") is not False:
            failures.append(f"{label}: normative claims cannot be empirically eligible")
        for ref in record.get("source_refs", []):
            if ref not in records:
                failures.append(f"{label}: source_ref does not resolve: {ref}")
    elif kind == "observable":
        for field in ("claim_ids", "domain_profile", "question", "resolution_rule", "window", "possible_results", "required_language_environments"):
            if field not in record:
                failures.append(f"{label}: missing field {field}")
        for ref in record.get("claim_ids", []):
            if ref not in records:
                failures.append(f"{label}: claim_id does not resolve: {ref}")
        profile = record.get("domain_profile")
        if profile not in records:
            failures.append(f"{label}: domain_profile does not resolve: {profile}")
    elif kind == "evidence":
        for field in ("source_id", "url", "retrieved_at", "event_time", "observation", "origin_language", "access_language", "translation_provenance", "originating_chain", "geopolitical_environment", "limitation", "representation_sha256", "evidence_role"):
            if field not in record:
                failures.append(f"{label}: missing field {field}")
        source = records.get(record.get("source_id"))
        if not source or source.get("kind") != "source":
            failures.append(f"{label}: source_id does not resolve")
        elif source.get("status") == "candidate" and record.get("evidence_role") != "context_only":
            failures.append(f"{label}: candidate source may supply context only")
        if record.get("translation_provenance") not in TRANSLATION_PROVENANCE:
            failures.append(f"{label}: invalid translation_provenance")
        if record.get("evidence_role") not in EVIDENCE_ROLES:
            failures.append(f"{label}: invalid evidence_role")
        if record.get("origin_language") != record.get("access_language") and record.get("translation_provenance") == "not_required":
            failures.append(f"{label}: translated evidence requires translation provenance")
        expected_digest = digest_text(str(record.get("observation", "")))
        if record.get("representation_sha256") != expected_digest:
            failures.append(f"{label}: representation_sha256 is stale")
    elif kind == "investigation":
        for field in ("claim_ids", "observable_ids", "research_boundary", "affected_forecast_hooks", "affected_artifacts"):
            if field not in record:
                failures.append(f"{label}: missing field {field}")
        for field in ("claim_ids", "observable_ids"):
            for ref in record.get(field, []):
                if ref not in records:
                    failures.append(f"{label}: {field[:-1]} does not resolve: {ref}")
    elif kind == "relation":
        if record.get("relation_type") not in RELATION_TYPES:
            failures.append(f"{label}: invalid relation_type")
        for endpoint in ("from_id", "to_id"):
            if record.get(endpoint) not in records:
                failures.append(f"{label}: {endpoint} does not resolve: {record.get(endpoint)}")
        if record.get("relation_type") in {"supports", "challenges"}:
            source = records.get(record.get("from_id"), {})
            if source.get("kind") != "evidence":
                failures.append(f"{label}: {record.get('relation_type')} must originate from evidence")
            if source.get("evidence_role") == "derived_editorial":
                failures.append(f"{label}: derived editorial material cannot support or challenge empirical claims")
    elif kind == "assessment":
        failures.extend(validate_assessment(record, records))
    elif kind == "transition":
        types = set(record.get("transition_types", []))
        if not types or not types <= TRANSITION_TYPES:
            failures.append(f"{label}: invalid transition_types")
        for field in ("subject_id", "prior_state", "new_state", "cause_refs", "authority", "affected_refs"):
            if field not in record:
                failures.append(f"{label}: missing field {field}")
        if record.get("subject_id") not in records:
            failures.append(f"{label}: subject_id does not resolve")
        for ref in record.get("cause_refs", []):
            if ref not in records:
                failures.append(f"{label}: cause_ref does not resolve: {ref}")
    elif kind == "domain_profile":
        for field in ("domain", "admissible_evidence_roles", "required_observables", "ordinary_language_count", "high_language_count", "ordinary_chain_count", "high_chain_count", "regional_environment_required", "external_environment_required", "permitted_outcomes", "waiver_policy"):
            if field not in record:
                failures.append(f"{label}: missing field {field}")
    return failures


def supporting_evidence(assessment: dict[str, Any], records: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    evidence_ids = set(assessment.get("evidence_ids", []))
    supported_ids = {
        relation.get("from_id")
        for relation in records.values()
        if relation.get("kind") == "relation"
        and relation.get("relation_type") == "supports"
        and relation.get("to_id") == assessment.get("claim_id")
    }
    return [records[item] for item in sorted(evidence_ids & supported_ids) if item in records]


def validate_assessment(assessment: dict[str, Any], records: dict[str, dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    label = assessment.get("id", "assessment")
    for field in ("claim_id", "outcome", "confidence_boundary", "rationale", "evidence_ids", "observable_ids", "signoffs", "authorizes_public", "authorizes_forecast_scoring", "language_audit", "physical_evidence_exception", "language_search_record"):
        if field not in assessment:
            failures.append(f"{label}: missing field {field}")
    claim = records.get(assessment.get("claim_id"))
    if not claim or claim.get("kind") != "claim":
        return failures + [f"{label}: claim_id does not resolve"]
    claim_type = claim.get("claim_type")
    if assessment.get("outcome") not in OUTCOMES.get(claim_type, set()):
        failures.append(f"{label}: outcome is invalid for {claim_type}")
    if assessment.get("status") not in ASSESSMENT_STATUSES:
        failures.append(f"{label}: invalid assessment status")
    for ref in assessment.get("evidence_ids", []) + assessment.get("observable_ids", []):
        if ref not in records:
            failures.append(f"{label}: referenced record does not resolve: {ref}")
    observables = [records[ref] for ref in assessment.get("observable_ids", []) if ref in records and records[ref].get("kind") == "observable"]
    component_claims = {
        relation.get("to_id")
        for relation in records.values()
        if relation.get("kind") == "relation"
        and relation.get("relation_type") == "depends_on"
        and relation.get("from_id") == assessment.get("claim_id")
    }
    for observable in observables:
        if assessment.get("claim_id") not in observable.get("claim_ids", []) and not component_claims.intersection(observable.get("claim_ids", [])):
            failures.append(f"{label}: observable {observable.get('id')} does not resolve this claim or one of its declared components")
    signers = [item.get("reviewer") for item in assessment.get("signoffs", []) if item.get("reviewer")]
    if len(signers) != len(set(signers)):
        failures.append(f"{label}: signoffs require distinct reviewers")
    evidence = supporting_evidence(assessment, records)
    languages = {item.get("origin_language") for item in evidence if item.get("origin_language") not in {None, "und"}}
    chains = {item.get("originating_chain") for item in evidence if item.get("originating_chain")}
    environments = {item.get("geopolitical_environment") for item in evidence if item.get("geopolitical_environment")}
    required = 3 if claim.get("consequence") == "high" else 2
    audit = assessment.get("language_audit", {})
    if audit:
        declared_languages = set(audit.get("origin_languages", []))
        declared_chains = set(audit.get("originating_chains", []))
        if declared_languages != languages:
            failures.append(f"{label}: language audit does not match supporting evidence")
        if declared_chains != chains:
            failures.append(f"{label}: chain audit does not match supporting evidence")
    positive = assessment.get("outcome") in POSITIVE_EMPIRICAL_OUTCOMES
    canonical = assessment.get("status") in {"canonical_assessed", "canonical_with_language_waiver"}
    profiles = [records.get(item.get("domain_profile")) for item in observables]
    profiles = [item for item in profiles if item and item.get("kind") == "domain_profile"]
    unresolved_outcomes = {"contested", "unresolvable", "unresolved", "contested_attribution"}
    if canonical and not profiles and assessment.get("outcome") not in unresolved_outcomes:
        failures.append(f"{label}: unknown or unprofiled domains may resolve only as contested or unresolvable")
    if canonical and CANONICAL_REVIEWER not in set(signers):
        failures.append(f"{label}: canonical assessment requires {CANONICAL_REVIEWER} signoff")
    if positive and canonical and assessment.get("status") != "canonical_with_language_waiver":
        if len(languages) < required:
            failures.append(f"{label}: canonical support requires {required} origin languages")
        if len(chains) < required:
            failures.append(f"{label}: canonical support requires {required} independent chains")
        if not audit.get("regional_environment_present"):
            failures.append(f"{label}: canonical support requires a regional or claimant environment")
        if not audit.get("external_environment_present"):
            failures.append(f"{label}: canonical support requires an external or challenged environment")
    if assessment.get("status") == "canonical_with_language_waiver":
        waiver_reviewers = {item.get("reviewer") for item in assessment.get("language_waiver", {}).get("reviewers", []) if item.get("reviewer")}
        if not positive:
            failures.append(f"{label}: language waiver applies only to positive empirical outcomes")
        if len(languages) >= required:
            failures.append(f"{label}: language waiver requires an unmet language environment")
        if CANONICAL_REVIEWER not in waiver_reviewers:
            failures.append(f"{label}: language waiver requires {CANONICAL_REVIEWER} approval")
        if not assessment.get("physical_evidence_exception"):
            failures.append(f"{label}: language waiver requires a physical evidence exception")
        if not any(item.get("evidence_role") == "observational" for item in evidence):
            failures.append(f"{label}: language waiver requires supporting primary observational evidence")
        if not str(assessment.get("language_search_record", "")).strip():
            failures.append(f"{label}: language waiver requires a search record")
        if not str(assessment.get("language_waiver", {}).get("reason", "")).strip():
            failures.append(f"{label}: language waiver requires a reason")
    if assessment.get("authorizes_public") or assessment.get("authorizes_forecast_scoring"):
        if assessment.get("status") not in {"canonical_assessed", "canonical_with_language_waiver"}:
            failures.append(f"{label}: provisional assessment cannot authorize publication or forecast scoring")
    if claim_type == "normative" and assessment.get("status") in {"canonical_assessed", "canonical_with_language_waiver"} and assessment.get("outcome") != "not_empirically_adjudicable":
        failures.append(f"{label}: normative claim cannot receive empirical adjudication")
    return failures


def validate_all(root: Path = REALITY_ROOT, *, check_views: bool = True) -> list[str]:
    records = load_records(root)
    failures: list[str] = []
    for record_id, record in records.items():
        if record.get("_duplicate"):
            failures.append(f"duplicate record ID: {record_id}")
        failures.extend(validate_record(record, records))
    if check_views and any(record.get("kind") for record in records.values()):
        expected = render_views(records)
        for name, content in expected.items():
            path = root / "views" / name
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                failures.append(f"stale or missing generated reality view: {name}")
        if any(record.get("kind") == "source" for record in records.values()):
            expected_registry = render_source_registry(records)
            registry_path = NG_ROOT / "work" / "verification" / "source-registry.md"
            if not registry_path.exists() or registry_path.read_text(encoding="utf-8") != expected_registry:
                failures.append("stale generated verification source registry")
    return sorted(set(failures))


def record_digest(records: Iterable[dict[str, Any]]) -> str:
    material = "".join(canonical_json(clean_record(record)) for record in sorted(records, key=lambda item: item.get("id", "")))
    return digest_text(material)


def view_header(title: str, records: dict[str, dict[str, Any]]) -> str:
    digest = record_digest(records.values())
    return f"<!-- reality-lattice-v1 records-sha256: {digest} -->\n<!-- Generated from structured reality records. Do not edit directly. -->\n\n# {title}\n\n"


def render_views(records: dict[str, dict[str, Any]]) -> dict[str, str]:
    claims = [clean_record(item) for item in records.values() if item.get("kind") == "claim"]
    assessments = [clean_record(item) for item in records.values() if item.get("kind") == "assessment"]
    investigations = [clean_record(item) for item in records.values() if item.get("kind") == "investigation"]
    transitions = [clean_record(item) for item in records.values() if item.get("kind") == "transition"]
    by_claim = {item["claim_id"]: item for item in assessments}

    outcome_lines = [view_header("Reality Outcome Ledger", records), "| Claim | Type | Consequence | Outcome | Assessment status | Languages | Chains |\n", "| --- | --- | --- | --- | --- | --- | --- |\n"]
    unresolved_lines = [view_header("Unresolved Reality Claims", records), "| Claim | Type | Consequence | Current state | Missing coverage |\n", "| --- | --- | --- | --- | --- | --- |\n"]
    coverage_lines = [view_header("Multilingual Coverage", records), "| Claim | Required languages | Observed languages | Required chains | Observed chains | Regional | External |\n", "| --- | --- | --- | --- | --- | --- | --- |\n"]
    for claim in sorted(claims, key=lambda item: item["id"]):
        assessment = by_claim.get(claim["id"])
        required = 3 if claim.get("consequence") == "high" else 2
        audit = assessment.get("language_audit", {}) if assessment else {}
        languages = audit.get("origin_languages", [])
        chains = audit.get("originating_chains", [])
        outcome = assessment.get("outcome", "unassessed") if assessment else "unassessed"
        status = assessment.get("status", "unassessed") if assessment else "unassessed"
        outcome_lines.append(f"| `{claim['id']}` | `{claim['claim_type']}` | `{claim['consequence']}` | `{outcome}` | `{status}` | {', '.join(languages) or 'none'} | {len(chains)} |\n")
        coverage_lines.append(f"| `{claim['id']}` | {required} | {', '.join(languages) or 'none'} | {required} | {len(chains)} | `{bool(audit.get('regional_environment_present'))}` | `{bool(audit.get('external_environment_present'))}` |\n")
        if outcome in {"unassessed", "contested", "unresolvable", "unresolved", "contested_attribution"} or status in {"draft", "provisional_assessed", "unassessed"}:
            missing = []
            if len(languages) < required:
                missing.append(f"{required - len(languages)} language environment(s)")
            if len(chains) < required:
                missing.append(f"{required - len(chains)} chain(s)")
            unresolved_lines.append(f"| `{claim['id']}` | `{claim['claim_type']}` | `{claim['consequence']}` | `{outcome}` | {'; '.join(missing) or 'assessment/review'} |\n")

    investigation_lines = [view_header("Reality Investigations", records), "| Investigation | Status | Claims | Observables | Research boundary |\n", "| --- | --- | --- | --- | --- |\n"]
    for item in sorted(investigations, key=lambda row: row["id"]):
        investigation_lines.append(f"| `{item['id']}` | `{item['status']}` | {', '.join(f'`{value}`' for value in item.get('claim_ids', []))} | {', '.join(f'`{value}`' for value in item.get('observable_ids', []))} | {item.get('research_boundary', '')} |\n")

    transition_lines = [view_header("Epistemic Transition Ledger", records), "| Transition | Subject | Types | Prior | New | Authority |\n", "| --- | --- | --- | --- | --- | --- |\n"]
    for item in sorted(transitions, key=lambda row: row["id"]):
        transition_lines.append(f"| `{item['id']}` | `{item['subject_id']}` | {', '.join(f'`{value}`' for value in item.get('transition_types', []))} | `{item.get('prior_state', '')}` | `{item.get('new_state', '')}` | {item.get('authority', '')} |\n")

    return {
        "outcome-ledger.md": "".join(outcome_lines),
        "unresolved-claims.md": "".join(unresolved_lines),
        "language-coverage.md": "".join(coverage_lines),
        "investigations.md": "".join(investigation_lines),
        "transitions.md": "".join(transition_lines),
    }


def render_source_registry(records: dict[str, dict[str, Any]]) -> str:
    sources = sorted((clean_record(item) for item in records.values() if item.get("kind") == "source"), key=lambda item: (item.get("order", 9999), item["id"]))
    lines = [
        "<!-- reality-lattice-v1 generated-source-registry -->\n",
        "<!-- Generated from work/reality/sources. Do not edit directly. -->\n\n",
        "# Many Windows, One Event: Verification Source Registry\n\n",
        f"Reviewed: `{max((item['review_history'][-1]['date'] for item in sources), default='unknown')}`\n\n",
        "This registry describes evidentiary capability and situated perspective, not universal trust. A viewpoint can expose claims or contradictions; it cannot substitute for an observable. State-affiliated sources establish their institution's position and may supply leads, but cannot independently establish an operational fact.\n\n",
        "## Sources\n\n",
        "| ID | Source | Canonical URL | Domain | Observables | Evidence class | Perspective | Geography | Languages | Translation provenance | Access | Open fallback | Latency | Originating-chain rule | Known failure modes | Appropriate uses | Inappropriate uses | Reviewed | Status |\n",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n",
    ]
    translation_back = {
        "not_required": "not_required",
        "official_edition": "official_english_available",
        "named_human_translation": "operator_translation_required",
        "operator_translation": "operator_translation_required",
        "machine_assisted_disclosed": "operator_translation_required",
    }
    for item in sources:
        languages = ",".join(item["access_languages"])
        reviewed = item["review_history"][-1]["date"]
        lines.append(
            f"| `{item['id']}` | {item['name']} | {item['canonical_url']} | `{item['domain']}` | {item['observables']} | `{item['evidence_class']}` | `{item['perspective']}` | {item['geography']} | `{languages}` | `{translation_back.get(item['translation_provenance'], item['translation_provenance'])}` | `{item['access']}` | `{item['open_fallback']}` | {item['latency']} | {item['originating_chain_rule']} | {item['known_failure_modes']} | {item['appropriate_uses']} | {item['inappropriate_uses']} | `{reviewed}` | `{item['status']}` |\n"
        )
    lines.extend([
        "\n## Coverage Contract\n\n",
        "Assessed packets record `covered`, `waived`, or `not_applicable` for: closest registry/sensor/original document; affected-region/local source; claimant official position; challenged actor position or denial; two professional reporting chains from different geopolitical environments; and commercial/observational evidence for movement, damage, deployment, or price claims. A waiver states what was sought and why it was unavailable. Counts never imply independence.\n\n",
        "For lattice-migrated claims, canonical support additionally requires independent original-language environments: two for ordinary empirical claims and three for high-consequence claims.\n",
    ])
    return "".join(lines)


def write_views(root: Path = REALITY_ROOT, *, check: bool = False) -> list[str]:
    records = load_records(root)
    failures = []
    for name, content in render_views(records).items():
        path = root / "views" / name
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                failures.append(f"stale or missing generated reality view: {name}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if any(item.get("kind") == "source" for item in records.values()):
        content = render_source_registry(records)
        if check:
            if not LEGACY_REGISTRY_PATH.exists() or LEGACY_REGISTRY_PATH.read_text(encoding="utf-8") != content:
                failures.append("stale generated verification source registry")
        else:
            LEGACY_REGISTRY_PATH.write_text(content, encoding="utf-8", newline="\n")
    return failures


def base_record(record_id: str, kind: str, as_of: str, *, status: str, creator: str = "migration") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "id": record_id,
        "kind": kind,
        "created_at": f"{as_of}T00:00:00Z",
        "created_by": creator,
        "as_of": as_of,
        "status": status,
        "revision_of": None,
    }


def parse_legacy_registry(path: Path = LEGACY_REGISTRY_PATH) -> list[dict[str, Any]]:
    records = []
    text = path.read_text(encoding="utf-8")
    for order, match in enumerate(LEGACY_REGISTRY_ROW_RE.finditer(text), start=1):
        cells = [cell.strip().strip("`") for cell in match.group("rest").split("|")]
        if len(cells) != 18:
            continue
        languages = [item.strip() for item in cells[7].split(",")]
        non_english = [item for item in languages if item != "en"]
        origin_languages = non_english or ["en"]
        translation = cells[8]
        translation_map = {
            "not_required": "not_required",
            "official_english_available": "official_edition",
            "official_english_edition": "official_edition",
            "operator_translation_required": "operator_translation",
        }
        record = base_record(match.group("id"), "source", cells[16], status=cells[17])
        record.update({
            "name": cells[0], "canonical_url": cells[1], "domain": cells[2], "observables": cells[3],
            "evidence_class": cells[4], "perspective": cells[5], "geography": cells[6],
            "origin_languages": origin_languages, "access_languages": languages,
            "translation_provenance": translation_map.get(translation, "operator_translation"),
            "access": cells[9], "open_fallback": cells[10], "latency": cells[11],
            "originating_chain_rule": cells[12], "known_failure_modes": cells[13],
            "appropriate_uses": cells[14], "inappropriate_uses": cells[15],
            "review_history": [{"date": cells[16], "reviewer": "legacy-registry-migration", "note": "Migrated with semantic parity."}],
            "geopolitical_environment": cells[5], "order": order,
        })
        records.append(record)
    return records


def domain_profiles(as_of: str = "2026-07-15") -> list[dict[str, Any]]:
    definitions = {
        "MARITIME-INCIDENT": ("maritime_incident", ["incident time", "location", "vessel identity", "damage", "attribution"]),
        "MARITIME-TRACKING": ("maritime_tracking", ["identity", "track", "port call", "routing change", "coverage limitation"]),
        "MILITARY-ACTIVITY": ("military_activity", ["time", "location", "target", "damage or deployment", "attribution"]),
        "DIPLOMATIC-POSITION": ("diplomatic_position", ["primary statement", "speaker or institution", "date", "translation", "subsequent revision"]),
    }
    records = []
    for suffix, (domain, observables) in definitions.items():
        record = base_record(f"DOMAIN-{suffix}", "domain_profile", as_of, status="active")
        record.update({
            "domain": domain,
            "admissible_evidence_roles": sorted(EVIDENCE_ROLES - {"derived_editorial"}),
            "required_observables": observables,
            "ordinary_language_count": 2,
            "high_language_count": 3,
            "ordinary_chain_count": 2,
            "high_chain_count": 3,
            "regional_environment_required": True,
            "external_environment_required": True,
            "permitted_outcomes": ["supported", "contested", "disconfirmed", "unresolvable"],
            "waiver_policy": "The human operator may approve unusually strong primary physical evidence after a documented multilingual search failure.",
        })
        records.append(record)
    return records


def migrate_registry(root: Path = REALITY_ROOT) -> list[Path]:
    if (root / "sources").exists() and list((root / "sources").glob("*.json")):
        records = [clean_record(item) for item in load_records(root).values() if item.get("kind") == "source"]
    else:
        records = parse_legacy_registry()
    paths = [write_record(item, root) for item in records]
    for profile in domain_profiles():
        paths.append(write_record(profile, root))
    return paths


def new_claim(record_id: str, as_of: str, claim_type: str, text: str, *, consequence: str = "medium", crisis_object: str = "unspecified", scope: str = "bounded claim", claimant_refs: list[str] | None = None, source_refs: list[str] | None = None) -> dict[str, Any]:
    record = base_record(record_id, "claim", as_of, status="open", creator="operator")
    record.update({
        "claim_type": claim_type, "text": text, "scope": scope, "crisis_object": crisis_object,
        "consequence": consequence, "empirical_eligibility": claim_type != "normative",
        "claimant_refs": claimant_refs or [], "source_refs": source_refs or [], "aliases": [],
    })
    return record


def new_observable(record_id: str, as_of: str, claim_ids: list[str], question: str, *, domain_profile: str, resolution_rule: str, window: dict[str, str], possible_results: list[str] | None = None, required_languages: list[str] | None = None) -> dict[str, Any]:
    record = base_record(record_id, "observable", as_of, status="open", creator="operator")
    record.update({
        "claim_ids": claim_ids, "domain_profile": domain_profile, "question": question,
        "resolution_rule": resolution_rule, "window": window,
        "possible_results": possible_results or ["observed", "not_observed", "contested", "unavailable"],
        "required_language_environments": required_languages or [],
    })
    return record


def next_id(kind: str, as_of: str, root: Path = REALITY_ROOT) -> str:
    prefix_by_kind = {"claim": "CLM", "observable": "OBS", "evidence": "EVD", "assessment": "ADJ", "transition": "EPT", "relation": "REL"}
    prefix = f"{prefix_by_kind[kind]}-{as_of.replace('-', '')}-"
    width = 3
    used = []
    folder = root / KIND_DIRS[kind]
    for path in folder.glob(f"{prefix}*.json") if folder.exists() else []:
        try:
            used.append(int(path.stem[-width:]))
        except ValueError:
            pass
    return f"{prefix}{max(used, default=0) + 1:0{width}d}"


def parse_legacy_packet_fields(text: str) -> dict[str, str]:
    return {match.group(1).lower().replace(" ", "_"): match.group(2) for match in re.finditer(r"^([A-Za-z ]+):\s*`([^`]*)`\s*$", text, re.MULTILINE)}


def migrated_evidence_record(item: dict[str, str], index: int, sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source = sources[item["registry_id"]]
    origin_language = source.get("origin_languages", ["en"])[0]
    access_language = "en" if "en" in source.get("access_languages", []) else source.get("access_languages", [origin_language])[0]
    translation = "not_required" if origin_language == access_language else source.get("translation_provenance", "official_edition")
    observation = item["limitation"].rstrip(".")
    record = base_record(f"EVD-20260710-{index:03d}", "evidence", "2026-07-10", status="active")
    role_map = {
        "official_interested_primary": "official_position",
        "state_affiliated_reporting": "official_position",
        "independent_professional_reporting": "professional_reporting",
    }
    record.update({
        "source_id": item["registry_id"], "url": item["url"], "retrieved_at": item["retrieved"],
        "event_time": item["event"], "observation": observation, "origin_language": origin_language,
        "access_language": access_language, "translation_provenance": translation,
        "originating_chain": item["chain"], "geopolitical_environment": source.get("geopolitical_environment"),
        "limitation": item["limitation"], "representation_sha256": digest_text(observation),
        "evidence_role": role_map.get(source.get("evidence_class"), "observational"),
        "legacy_evidence_id": item["id"],
    })
    return record


def migrate_20260710(root: Path = REALITY_ROOT) -> list[Path]:
    records = load_records(root)
    sources = {key: clean_record(value) for key, value in records.items() if value.get("kind") == "source"}
    if not sources:
        raise RealityError("migrate the source registry first")
    paths: list[Path] = []
    claim_defs = [
        ("OPC-20260710-02", "A coordinated US-backed bypass attempt triggered Iranian coercive action and renewed US strikes.", "Aggregate claim retained for legacy compatibility."),
        ("CLM-20260710-001", "Three commercial vessels were damaged in or near the Oman-side Hormuz route on July 6–7.", "Incident occurrence."),
        ("CLM-20260710-002", "Iran was responsible for the attacks on the three vessels.", "Attack attribution."),
        ("CLM-20260710-003", "The vessels participated in a coordinated US-backed bypass attempt.", "Bypass intent and command chain."),
        ("CLM-20260710-004", "The vessels received and ignored vessel-specific Iranian warnings.", "Warning sequence."),
        ("CLM-20260710-005", "The bypass attempt caused Iranian coercive action and renewed US strikes.", "Trigger-response causality."),
    ]
    for claim_id, text, scope in claim_defs:
        claim = new_claim(claim_id, "2026-07-10", "operational_factual" if claim_id != "CLM-20260710-005" else "causal", text, consequence="high", crisis_object="Hormuz bypass and coercive response", scope=scope)
        claim["created_by"] = "legacy-pilot-migration"
        paths.append(write_record(claim, root))
    observable_questions = [
        "Were three named commercial vessels damaged near the Oman-side route?",
        "Does attributable evidence identify Iran as attacker?",
        "Was the route an operation-specific US-backed bypass?",
        "Did each vessel receive and ignore a specific warning?",
        "Did a deliberate bypass trigger the attacks and renewed US strikes?",
    ]
    for index, question in enumerate(observable_questions, start=1):
        claim_id = f"CLM-20260710-{index:03d}"
        profile = "DOMAIN-MARITIME-INCIDENT" if index <= 4 else "DOMAIN-MILITARY-ACTIVITY"
        observable = new_observable(f"OBS-20260710-{index:03d}", "2026-07-10", [claim_id], question, domain_profile=profile, resolution_rule="Resolve only from event-specific evidence with globally traced lineage and required multilingual coverage.", window={"start": "2026-07-06", "end": "2026-07-11"}, required_languages=["regional_or_claimant", "external", "third_independent_environment"])
        observable["created_by"] = "legacy-pilot-migration"
        paths.append(write_record(observable, root))
    packet_path = LEGACY_PACKETS_ROOT / "VER-20260710-01-hormuz-bypass-test" / "README.md"
    text = packet_path.read_text(encoding="utf-8")
    evidence_items = [match.groupdict() for match in LEGACY_EVIDENCE_RE.finditer(text)]
    for index, item in enumerate(evidence_items, start=1):
        paths.append(write_record(migrated_evidence_record(item, index, sources), root))
    investigation = base_record("VER-20260710-01", "investigation", "2026-07-10", status="assessed", creator="legacy-pilot-migration")
    investigation.update({
        "claim_ids": [item[0] for item in claim_defs],
        "observable_ids": [f"OBS-20260710-{index:03d}" for index in range(1, 6)],
        "research_boundary": "Named vessels, route, warnings, attack attribution, damage, strike timing, and operation-specific bypass intent.",
        "affected_forecast_hooks": ["NG-20260708-F02"],
        "affected_artifacts": ["narrative-geopolitics/work/daily/2026-07-10/synthesis.md", "narrative-geopolitics/work/daily/2026-07-10/forecast.md", "narrative-geopolitics/work/daily/2026-07-10/daily-brief.md"],
        "legacy_packet_path": packet_path.relative_to(REPO_ROOT).as_posix(),
    })
    paths.append(write_record(investigation, root))
    relation_index = 1
    # Incident records support occurrence; reporting and official claims contextualize or support narrower propositions.
    relation_map = {
        1: [("CLM-20260710-001", "supports")],
        2: [("CLM-20260710-001", "supports")],
        3: [("CLM-20260710-001", "supports"), ("CLM-20260710-002", "contextualizes"), ("CLM-20260710-004", "contextualizes")],
        4: [("CLM-20260710-004", "contextualizes")],
        5: [("CLM-20260710-003", "contextualizes"), ("CLM-20260710-005", "contextualizes")],
        6: [("CLM-20260710-002", "contextualizes"), ("CLM-20260710-005", "contextualizes")],
    }
    for evidence_index, edges in relation_map.items():
        for target, relation_type in edges:
            relation = base_record(f"REL-20260710-{relation_index:03d}", "relation", "2026-07-10", status="active", creator="legacy-pilot-migration")
            relation.update({"from_id": f"EVD-20260710-{evidence_index:03d}", "to_id": target, "relation_type": relation_type, "scope": "Migrated from the bounded July 10 packet; probative force follows its stated limitation."})
            paths.append(write_record(relation, root))
            relation_index += 1
    for child in [item[0] for item in claim_defs[1:]]:
        relation = base_record(f"REL-20260710-{relation_index:03d}", "relation", "2026-07-10", status="active", creator="legacy-pilot-migration")
        relation.update({"from_id": "OPC-20260710-02", "to_id": child, "relation_type": "depends_on", "scope": "The legacy compound claim depends on this atomic component."})
        paths.append(write_record(relation, root))
        relation_index += 1
    outcomes = ["contested", "supported", "contested", "contested", "contested", "contested"]
    for index, ((claim_id, _, _), outcome) in enumerate(zip(claim_defs, outcomes), start=1):
        claim_type = "causal" if claim_id == "CLM-20260710-005" else "operational_factual"
        if claim_type == "causal":
            outcome = "contested"
        evidence_ids = [f"EVD-20260710-{item:03d}" for item in range(1, 7)]
        current_records = load_records(root)
        supporting = supporting_evidence({"claim_id": claim_id, "evidence_ids": evidence_ids}, current_records)
        languages = sorted({item["origin_language"] for item in supporting})
        chains = sorted({item["originating_chain"] for item in supporting})
        assessment = base_record(f"ADJ-20260710-{index:03d}", "assessment", "2026-07-10", status="provisional_assessed", creator="legacy-pilot-migration")
        assessment.update({
            "claim_id": claim_id, "outcome": outcome,
            "confidence_boundary": "Legacy packet supports incident occurrence but lacks the three independent original-language environments required for canonical high-consequence support.",
            "rationale": "Migrated without upgrading the assessed July 10 packet or resolving its command-chain and attribution limits.",
            "evidence_ids": evidence_ids, "observable_ids": [f"OBS-20260710-{index - 1:03d}"] if index > 1 else ["OBS-20260710-001", "OBS-20260710-002", "OBS-20260710-003", "OBS-20260710-004", "OBS-20260710-005"],
            "signoffs": [], "authorizes_public": False, "authorizes_forecast_scoring": False,
            "language_audit": {"origin_languages": languages, "originating_chains": chains, "regional_environment_present": False, "external_environment_present": True, "missing_environments": ["third independent original-language environment", "direct affected-region source"]},
            "physical_evidence_exception": False, "language_search_record": "Legacy research was English-dominant with one French-origin report; no waiver requested.",
            "calibration_eligible": False, "legacy_assessment_outcome": "operationally_contested",
        })
        paths.append(write_record(assessment, root, overwrite=True))
    transition = base_record("EPT-20260710-001", "transition", "2026-07-10", status="active", creator="legacy-pilot-migration")
    transition.update({
        "subject_id": "OPC-20260710-02", "prior_state": "source_assertion", "new_state": "contested",
        "transition_types": ["evidence", "confidence", "authorization"],
        "cause_refs": ["ADJ-20260710-001"], "authority": "VER-20260710-01 legacy human assessment",
        "affected_refs": ["NG-20260708-F02"],
        "note": "Incident occurrence strengthened; attribution, deliberate bypass, warning sequence, and causality remain contested.",
    })
    paths.append(write_record(transition, root))
    return paths


def migrate_20260714(root: Path = REALITY_ROOT) -> list[Path]:
    paths: list[Path] = []
    claims = [
        ("OPC-20260714-01", "Iran struck US or Gulf-linked bases and facilities across the named regional cluster, with material air-defense failure.", "military activity", "DOMAIN-MILITARY-ACTIVITY"),
        ("OPC-20260714-02", "Tankers or corridor traffic attempting to bypass Iranian coordination were warned, mined, struck, or deterred with measurable commercial effect.", "maritime routing", "DOMAIN-MARITIME-INCIDENT"),
        ("OPC-20260714-03", "A Saudi/Yemen event chain moved Bab al-Mandab or Saudi infrastructure toward active participation in the transit contest.", "regional participation", "DOMAIN-MILITARY-ACTIVITY"),
    ]
    for index, (claim_id, text, scope, profile) in enumerate(claims, start=1):
        claim = new_claim(claim_id, "2026-07-14", "operational_factual", text, consequence="high", crisis_object="Hormuz regional participation", scope=scope)
        claim["created_by"] = "pilot-migration"
        paths.append(write_record(claim, root))
        observable = new_observable(f"OBS-20260714-{index:03d}", "2026-07-14", [claim_id], f"What independent event, attribution, and consequence evidence resolves {claim_id}?", domain_profile=profile, resolution_rule="Require three independent original-language environments, including affected-region and external perspectives, plus the closest available physical or registry evidence.", window={"start": "2026-07-14", "end": "open"}, required_languages=["affected_or_claimant_region", "external_or_challenged", "third_independent_environment"])
        observable["created_by"] = "pilot-migration"
        paths.append(write_record(observable, root))
        investigation = base_record(f"VER-20260714-{index:02d}", "investigation", "2026-07-14", status="requested", creator="pilot-migration")
        investigation.update({
            "claim_ids": [claim_id], "observable_ids": [f"OBS-20260714-{index:03d}"],
            "research_boundary": observable["resolution_rule"], "affected_forecast_hooks": ["NG-20260708-F02"] if index == 2 else (["NG-20260708-F01"] if index == 3 else []),
            "affected_artifacts": ["narrative-geopolitics/work/daily/2026-07-14/synthesis.md", "narrative-geopolitics/work/daily/2026-07-14/forecast.md", "narrative-geopolitics/work/daily/2026-07-14/issue.md"],
        })
        paths.append(write_record(investigation, root))
    interpretive = new_claim("CLM-20260714-001", "2026-07-14", "interpretive", "The archive's organizing Hormuz object widened from corridor governance to regional participation pressure.", consequence="medium", crisis_object="Hormuz regional participation", scope="Interpretation of the manifest-backed source batch, not an operational event finding.")
    interpretive["created_by"] = "pilot-migration"
    paths.append(write_record(interpretive, root))
    for hook_id, text in [
        ("NG-20260708-F01", "Major public handling continues to treat Hormuz as a governed bargaining lane rather than a binary open or closed chokepoint."),
        ("NG-20260708-F02", "A visible attempt to weaken or bypass Iranian transit authority produces a visible coercive response."),
    ]:
        claim = new_claim(hook_id, "2026-07-08", "forecast", text, consequence="high", crisis_object="Hormuz transit governance", scope="Existing accountable forecast hook.")
        claim["created_by"] = "pilot-migration"
        paths.append(write_record(claim, root))
    relation_index = 1
    for hook_id, dependency in [("NG-20260708-F02", "OPC-20260714-02"), ("NG-20260708-F01", "OPC-20260714-03")]:
        relation = base_record(f"REL-20260714-{relation_index:03d}", "relation", "2026-07-14", status="active", creator="pilot-migration")
        relation.update({"from_id": hook_id, "to_id": dependency, "relation_type": "depends_on", "scope": "July 14 forecast dependency; source assertions do not score the hook."})
        paths.append(write_record(relation, root))
        relation_index += 1
    transition = base_record("EPT-20260714-001", "transition", "2026-07-14", status="active", creator="pilot-migration")
    transition.update({
        "subject_id": "CLM-20260714-001", "prior_state": "corridor-governance interpretation", "new_state": "regional-participation interpretation",
        "transition_types": ["interpretation", "confidence"], "cause_refs": ["OPC-20260714-01", "OPC-20260714-02", "OPC-20260714-03"],
        "authority": "manifest-backed synthesis judgment", "affected_refs": ["NG-20260708-F01", "NG-20260708-F02"],
        "note": "Interpretive breadth increased; operational evidence and probability bands did not upgrade.",
    })
    paths.append(write_record(transition, root))
    presentation = base_record("EPT-20260714-002", "transition", "2026-07-14", status="active", creator="pilot-migration")
    presentation.update({
        "subject_id": "CLM-20260714-001", "prior_state": "canonical daily files", "new_state": "generated internal daily issue",
        "transition_types": ["presentation", "authorization"], "cause_refs": ["EPT-20260714-001"],
        "authority": "daily-issue-v1 rendering contract", "affected_refs": ["narrative-geopolitics/work/daily/2026-07-14/issue.md"],
        "note": "Issue rendering changed presentation and internal use only; it added no evidence.",
    })
    paths.append(write_record(presentation, root))
    return paths


def migrate_date(run_date: str, root: Path = REALITY_ROOT) -> list[Path]:
    migrate_registry(root)
    if run_date == "2026-07-10":
        return migrate_20260710(root)
    if run_date == "2026-07-14":
        return migrate_20260714(root)
    raise RealityError(f"no deterministic migration is defined for {run_date}")


def check_migration(run_date: str, root: Path = REALITY_ROOT) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="reality-migration-check-", dir=REPO_ROOT) as temp_dir:
        expected_root = Path(temp_dir) / "reality"
        migrate_date(run_date, expected_root)
        expected_records = load_records(expected_root)
    actual_records = load_records(root)
    failures: list[str] = []
    for record_id, expected in sorted(expected_records.items()):
        actual = actual_records.get(record_id)
        if actual is None:
            failures.append(f"migration missing expected record: {record_id}")
        elif not migration_record_matches(expected, actual, actual_records):
            failures.append(f"migration record is stale: {record_id}")
    return failures


def migration_record_matches(
    expected: dict[str, Any],
    actual: dict[str, Any],
    records: dict[str, dict[str, Any]],
) -> bool:
    expected = clean_record(expected)
    actual = clean_record(actual)
    if expected.get("kind") != "assessment" or actual.get("kind") != "assessment":
        return actual == expected

    mutable_fields = {"signoffs", "status", "updated_at"}
    expected_core = {key: value for key, value in expected.items() if key not in mutable_fields}
    actual_core = {key: value for key, value in actual.items() if key not in mutable_fields}
    if actual_core != expected_core:
        return False

    expected_signoffs = expected.get("signoffs", [])
    actual_signoffs = actual.get("signoffs", [])
    if actual_signoffs[: len(expected_signoffs)] != expected_signoffs:
        return False
    if any(
        not item.get("reviewer") or not item.get("signed_at")
        for item in actual_signoffs
    ):
        return False
    reviewers = [item.get("reviewer") for item in actual_signoffs]
    if len(reviewers) != len(set(reviewers)):
        return False

    signoffs_changed = actual_signoffs != expected_signoffs
    if signoffs_changed and not actual.get("updated_at"):
        return False
    if not signoffs_changed and actual.get("updated_at") != expected.get("updated_at"):
        return False

    if not signoffs_changed:
        return actual.get("status") == expected.get("status")

    expected_status = "provisional_assessed"
    if CANONICAL_REVIEWER in set(reviewers):
        candidate = dict(actual)
        candidate["status"] = "canonical_assessed"
        candidate_records = dict(records)
        candidate_records[actual["id"]] = candidate
        if not validate_assessment(candidate, candidate_records):
            expected_status = "canonical_assessed"
    return actual.get("status") == expected_status


def claim_state(claim_id: str, root: Path = REALITY_ROOT) -> dict[str, Any] | None:
    records = load_records(root)
    claim = records.get(claim_id)
    if not claim or claim.get("kind") != "claim":
        return None
    assessments = sorted((item for item in records.values() if item.get("kind") == "assessment" and item.get("claim_id") == claim_id), key=lambda item: item.get("created_at", ""))
    current = assessments[-1] if assessments else None
    return {"claim": clean_record(claim), "assessment": clean_record(current) if current else None, "migrated": True}


def relevant_subgraph(seed_ids: Iterable[str], root: Path = REALITY_ROOT) -> list[dict[str, Any]]:
    records = load_records(root)
    included = {item for item in seed_ids if item in records}
    changed = True
    while changed:
        changed = False
        for record_id, record in records.items():
            refs: set[str] = set()
            for field in ("claim_id", "subject_id", "from_id", "to_id"):
                value = record.get(field)
                if isinstance(value, str):
                    refs.add(value)
            for field in ("claim_ids", "observable_ids", "evidence_ids", "cause_refs"):
                refs.update(item for item in record.get(field, []) if isinstance(item, str))
            if record_id in included or refs & included:
                before = len(included)
                included.add(record_id)
                included.update(ref for ref in refs if ref in records)
                changed = changed or len(included) != before
    return [clean_record(records[item]) for item in sorted(included)]


def subgraph_digest(seed_ids: Iterable[str], root: Path = REALITY_ROOT) -> str:
    return record_digest(relevant_subgraph(seed_ids, root))


def impact_payload(subject_id: str, root: Path = REALITY_ROOT) -> dict[str, Any]:
    records = load_records(root)
    if subject_id not in records:
        raise RealityError(f"unknown lattice ID: {subject_id}")
    adjacency: dict[str, set[str]] = defaultdict(set)
    for record in records.values():
        if record.get("kind") == "relation" and record.get("relation_type") in {"depends_on", "affects", "resolves", "supersedes"}:
            adjacency[record.get("to_id")].add(record.get("from_id"))
        if record.get("kind") == "transition" and record.get("subject_id") == subject_id:
            adjacency[subject_id].update(item for item in record.get("affected_refs", []) if item in records)
    seen = {subject_id}
    queue = deque([subject_id])
    while queue:
        current = queue.popleft()
        for target in sorted(adjacency.get(current, set())):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return {"subject_id": subject_id, "affected_ids": sorted(seen - {subject_id})}


def audit_payload(claim_id: str, root: Path = REALITY_ROOT) -> dict[str, Any]:
    records = load_records(root)
    claim = records.get(claim_id)
    if not claim or claim.get("kind") != "claim":
        raise RealityError(f"unknown lattice claim: {claim_id}")

    assessments = sorted(
        (
            item
            for item in records.values()
            if item.get("kind") == "assessment" and item.get("claim_id") == claim_id
        ),
        key=lambda item: (item.get("created_at", ""), item.get("id", "")),
    )
    assessment = assessments[-1] if assessments else None
    investigations = sorted(
        (
            item
            for item in records.values()
            if item.get("kind") == "investigation" and claim_id in item.get("claim_ids", [])
        ),
        key=lambda item: item.get("id", ""),
    )
    observables_by_id = {
        item.get("id"): item
        for item in records.values()
        if item.get("kind") == "observable" and claim_id in item.get("claim_ids", [])
    }
    for investigation in investigations:
        for observable_id in investigation.get("observable_ids", []):
            observable = records.get(observable_id)
            if observable and observable.get("kind") == "observable":
                observables_by_id[observable_id] = observable

    evidence_relations = sorted(
        (
            item
            for item in records.values()
            if item.get("kind") == "relation"
            and item.get("to_id") == claim_id
            and records.get(item.get("from_id"), {}).get("kind") == "evidence"
        ),
        key=lambda item: item.get("id", ""),
    )
    relation_evidence_ids = {item.get("from_id") for item in evidence_relations}
    assessment_evidence_ids = set(assessment.get("evidence_ids", [])) if assessment else set()
    evidence_ids = sorted(relation_evidence_ids | assessment_evidence_ids)
    support_ids = {
        item.get("from_id")
        for item in evidence_relations
        if item.get("relation_type") == "supports"
    }
    challenge_ids = {
        item.get("from_id")
        for item in evidence_relations
        if item.get("relation_type") == "challenges"
    }
    supporting = [records[item] for item in sorted(support_ids) if item in records]
    languages = sorted(
        {
            item.get("origin_language")
            for item in supporting
            if item.get("origin_language") not in {None, "und"}
        }
    )
    chains = sorted(
        {item.get("originating_chain") for item in supporting if item.get("originating_chain")}
    )
    environments = sorted(
        {
            item.get("geopolitical_environment")
            for item in supporting
            if item.get("geopolitical_environment")
        }
    )
    language_audit = assessment.get("language_audit", {}) if assessment else {}
    regional_present = bool(language_audit.get("regional_environment_present"))
    external_present = bool(language_audit.get("external_environment_present"))
    empirical = bool(claim.get("empirical_eligibility"))
    required_coverage = 3 if claim.get("consequence") == "high" else 2
    required_languages = required_coverage if empirical else 0
    required_chains = required_coverage if empirical else 0
    positive = bool(assessment and assessment.get("outcome") in POSITIVE_EMPIRICAL_OUTCOMES)
    waived = bool(assessment and assessment.get("status") == "canonical_with_language_waiver")
    support_gate_applicable = empirical and (assessment is None or positive)
    language_gate_satisfied = not support_gate_applicable or waived or (
        len(languages) >= required_languages and regional_present and external_present
    )
    lineage_gate_satisfied = not support_gate_applicable or waived or len(chains) >= required_chains

    signers = sorted(
        {
            item.get("reviewer")
            for item in (assessment.get("signoffs", []) if assessment else [])
            if item.get("reviewer")
        }
    )
    required_signoffs = REQUIRED_SIGNOFFS
    required_reviewer_present = CANONICAL_REVIEWER in signers
    canonical = bool(
        assessment
        and assessment.get("status") in {"canonical_assessed", "canonical_with_language_waiver"}
    )
    validation_failures = validate_record(claim, records)
    if assessment:
        validation_failures.extend(validate_assessment(assessment, records))

    missing_gates: list[str] = []
    if validation_failures:
        missing_gates.append("record_validation")
    if not investigations:
        missing_gates.append("investigation")
    if not observables_by_id:
        missing_gates.append("observable")
    if not assessment:
        missing_gates.append("assessment")
    if support_gate_applicable and not waived:
        if len(languages) < required_languages:
            missing_gates.append("origin_language_coverage")
        if len(chains) < required_chains:
            missing_gates.append("independent_lineage_coverage")
        if not regional_present:
            missing_gates.append("regional_environment")
        if not external_present:
            missing_gates.append("external_environment")
    if assessment:
        if not canonical and not required_reviewer_present:
            missing_gates.append("human_signoff")
        if not canonical:
            missing_gates.append("canonical_assessment")

    if validation_failures:
        next_action = "repair_invalid_lattice_records"
    elif not investigations:
        next_action = "define_bounded_investigation"
    elif not observables_by_id:
        next_action = "define_atomic_observables"
    elif support_gate_applicable and not language_gate_satisfied:
        next_action = "collect_missing_original_language_environment"
    elif support_gate_applicable and not lineage_gate_satisfied:
        next_action = "collect_independent_lineage_evidence"
    elif not assessment:
        next_action = "create_claim_specific_assessment"
    elif not canonical and not required_reviewer_present:
        next_action = "request_explicit_human_signoff"
    elif not canonical:
        next_action = "reconcile_provisional_assessment"
    else:
        next_action = "review_downstream_impact_without_automatic_rewrite"

    affected_artifacts = sorted(
        {
            artifact
            for investigation in investigations
            for artifact in investigation.get("affected_artifacts", [])
        }
    )
    affected_forecasts = sorted(
        {
            hook
            for investigation in investigations
            for hook in investigation.get("affected_forecast_hooks", [])
        }
    )
    impact = impact_payload(claim_id, root)
    return {
        "schema_version": 1,
        "claim": {
            "id": claim_id,
            "type": claim.get("claim_type"),
            "consequence": claim.get("consequence"),
            "scope": claim.get("scope"),
            "text": claim.get("text"),
            "crisis_object": claim.get("crisis_object"),
        },
        "epistemic_state": {
            "assessment_id": assessment.get("id") if assessment else None,
            "assessment_status": assessment.get("status") if assessment else "unassessed",
            "outcome": assessment.get("outcome") if assessment else None,
            "confidence_boundary": assessment.get("confidence_boundary") if assessment else None,
            "canonical": canonical,
        },
        "evidence_posture": {
            "evidence_ids": evidence_ids,
            "supporting_ids": sorted(support_ids),
            "challenging_ids": sorted(challenge_ids),
            "supporting_count": len(support_ids),
            "challenging_count": len(challenge_ids),
        },
        "coverage": {
            "required_origin_languages": required_languages,
            "present_origin_languages": languages,
            "required_independent_lineages": required_chains,
            "present_independent_lineages": chains,
            "geopolitical_environments": environments,
            "regional_environment_present": regional_present,
            "external_environment_present": external_present,
            "declared_missing_environments": language_audit.get("missing_environments", []),
            "language_gate_satisfied": language_gate_satisfied,
            "lineage_gate_satisfied": lineage_gate_satisfied,
            "language_waiver": waived,
        },
        "authorization": {
            "required_signoffs": required_signoffs,
            "required_reviewer": CANONICAL_REVIEWER,
            "present_signoffs": signers,
            "authorizes_public": bool(assessment and assessment.get("authorizes_public")),
            "authorizes_forecast_scoring": bool(
                assessment and assessment.get("authorizes_forecast_scoring")
            ),
        },
        "linked_investigations": [item.get("id") for item in investigations],
        "linked_observables": sorted(observables_by_id),
        "impact": {
            "affected_ids": impact["affected_ids"],
            "affected_artifacts": affected_artifacts,
            "affected_forecast_hooks": affected_forecasts,
        },
        "validation_failures": validation_failures,
        "missing_gates": missing_gates,
        "next_bounded_action": next_action,
    }


def render_audit_brief(payload: dict[str, Any]) -> str:
    state = payload["epistemic_state"]
    evidence = payload["evidence_posture"]
    coverage = payload["coverage"]
    authorization = payload["authorization"]
    impact = payload["impact"]
    lines = [
        f"Reality check: {payload['claim']['id']}",
        "",
        "Epistemic state",
        f"- Outcome: {state['outcome'] or 'unassessed'}",
        f"- Status: {state['assessment_status']}",
        f"- Canonical: {'yes' if state['canonical'] else 'no'}",
        "",
        "Evidence posture",
        f"- Supporting evidence: {evidence['supporting_count']}",
        f"- Challenging evidence: {evidence['challenging_count']}",
        "",
        "Multilingual and lineage coverage",
        f"- Origin languages: {len(coverage['present_origin_languages'])}/{coverage['required_origin_languages']} ({', '.join(coverage['present_origin_languages']) or 'none'})",
        f"- Independent lineages: {len(coverage['present_independent_lineages'])}/{coverage['required_independent_lineages']}",
        f"- Regional / external: {'yes' if coverage['regional_environment_present'] else 'no'} / {'yes' if coverage['external_environment_present'] else 'no'}",
        f"- Language waiver: {'yes' if coverage['language_waiver'] else 'no'}",
        "",
        "Authorization boundary",
        f"- Human signoffs: {len(authorization['present_signoffs'])}/{authorization['required_signoffs']}",
        f"- Public factual use: {'authorized' if authorization['authorizes_public'] else 'not authorized'}",
        f"- Forecast scoring: {'authorized' if authorization['authorizes_forecast_scoring'] else 'not authorized'}",
        f"- Downstream artifacts: {len(impact['affected_artifacts'])}; affected lattice IDs: {len(impact['affected_ids'])}",
        "",
        "Next bounded action",
        f"- {payload['next_bounded_action']}",
    ]
    if payload["missing_gates"]:
        lines.append(f"- Missing gates: {', '.join(payload['missing_gates'])}")
    return "\n".join(lines)


def profile_payload(voice: str, root: Path = REALITY_ROOT) -> dict[str, Any]:
    records = load_records(root)
    claims = [item for item in records.values() if item.get("kind") == "claim" and voice in item.get("claimant_refs", [])]
    assessments = {item.get("claim_id"): item for item in records.values() if item.get("kind") == "assessment" and item.get("calibration_eligible", True) and item.get("status") == "canonical_assessed"}
    groups: dict[tuple[str, str], list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for claim in claims:
        assessment = assessments.get(claim.get("id"))
        if assessment:
            domain = claim.get("domain", "unspecified")
            groups[(claim.get("claim_type"), domain)].append((claim, assessment))
    visible = []
    withheld = []
    for (claim_type, domain), items in sorted(groups.items()):
        objects = {claim.get("crisis_object") for claim, _ in items}
        row = {"claim_type": claim_type, "domain": domain, "claims": len(items), "crisis_objects": len(objects), "outcomes": dict(Counter(assessment.get("outcome") for _, assessment in items))}
        (visible if len(items) >= 10 and len(objects) >= 3 else withheld).append(row)
    return {"voice": voice, "profiles": visible, "withheld": withheld, "composite_score": None, "public": False}


def create_scaffold(args: argparse.Namespace) -> Path:
    as_of = args.date
    if args.record_kind == "claim":
        record_id = args.id or next_id("claim", as_of)
        record = new_claim(record_id, as_of, args.type, args.text, consequence=args.consequence, crisis_object=args.crisis_object)
    elif args.record_kind == "observable":
        record_id = args.id or next_id("observable", as_of)
        record = new_observable(record_id, as_of, args.claim, args.text, domain_profile=args.domain_profile, resolution_rule=args.resolution_rule, window={"start": as_of, "end": args.end}, required_languages=args.language)
    else:
        record_id = args.id
        if not record_id:
            raise RealityError("new investigation requires --id VER-YYYYMMDD-NN")
        record = base_record(record_id, "investigation", as_of, status="requested", creator="operator")
        record.update({"claim_ids": args.claim, "observable_ids": args.observable, "research_boundary": args.text, "affected_forecast_hooks": [], "affected_artifacts": []})
    failures = validate_record(record, load_records())
    if failures:
        raise RealityError("refusing to write invalid record: " + "; ".join(failures))
    return write_record(record)


def add_scaffold(args: argparse.Namespace) -> Path:
    as_of = args.date
    if args.record_kind == "evidence":
        record_id = args.id or next_id("evidence", as_of)
        observation = args.observation
        record = base_record(record_id, "evidence", as_of, status="active", creator="operator")
        record.update({
            "source_id": args.source, "url": args.url, "retrieved_at": args.retrieved_at or utc_now(), "event_time": args.event_time,
            "observation": observation, "origin_language": args.origin_language, "access_language": args.access_language,
            "translation_provenance": args.translation_provenance, "originating_chain": args.chain,
            "geopolitical_environment": args.environment, "limitation": args.limitation,
            "representation_sha256": digest_text(observation), "evidence_role": args.role,
        })
    else:
        record_id = args.id or next_id("relation", as_of)
        record = base_record(record_id, "relation", as_of, status="active", creator="operator")
        record.update({"from_id": args.from_id, "to_id": args.to_id, "relation_type": args.type, "scope": args.scope})
    failures = validate_record(record, load_records())
    if failures:
        raise RealityError("refusing to write invalid record: " + "; ".join(failures))
    return write_record(record)


def land_evidence(args: argparse.Namespace) -> Path:
    """Add one evidence record, then render and validate the lattice."""
    args.record_kind = "evidence"
    path = add_scaffold(args)
    write_views()
    failures = validate_all()
    if failures:
        raise RealityError("evidence landed but validation failed: " + "; ".join(failures))
    return path


def scaffold_assessment(claim_id: str, root: Path = REALITY_ROOT) -> Path:
    records = load_records(root)
    claim = records.get(claim_id)
    if not claim or claim.get("kind") != "claim":
        raise RealityError(f"unknown claim: {claim_id}")
    as_of = date.today().isoformat()
    record_id = next_id("assessment", as_of, root)
    default_outcome = "not_empirically_adjudicable" if claim.get("claim_type") == "normative" else sorted(OUTCOMES[claim.get("claim_type")])[-1]
    record = base_record(record_id, "assessment", as_of, status="draft", creator="operator")
    record.update({
        "claim_id": claim_id, "outcome": default_outcome, "confidence_boundary": "Complete before assessment.",
        "rationale": "Complete before assessment.", "evidence_ids": [], "observable_ids": [], "signoffs": [],
        "authorizes_public": False, "authorizes_forecast_scoring": False,
        "language_audit": {"origin_languages": [], "originating_chains": [], "regional_environment_present": False, "external_environment_present": False, "missing_environments": []},
        "physical_evidence_exception": False, "language_search_record": "", "calibration_eligible": False,
    })
    return write_record(record, root)


def mutate_assessment(assessment_id: str, updater: Any, root: Path = REALITY_ROOT) -> Path:
    path = record_path("assessment", assessment_id, root)
    if not path.exists():
        raise RealityError(f"unknown assessment: {assessment_id}")
    record = json.loads(path.read_text(encoding="utf-8"))
    updater(record)
    record["updated_at"] = utc_now()
    path.write_text(canonical_json(record), encoding="utf-8", newline="\n")
    return path


def sign_assessment(assessment_id: str, reviewer: str, root: Path = REALITY_ROOT) -> Path:
    def update(record: dict[str, Any]) -> None:
        signoffs = record.setdefault("signoffs", [])
        if reviewer in {item.get("reviewer") for item in signoffs}:
            raise RealityError(f"reviewer already signed: {reviewer}")
        signoffs.append({"reviewer": reviewer, "signed_at": utc_now()})
        record["status"] = "provisional_assessed"
        records = load_records(root)
        records[assessment_id] = record
        if CANONICAL_REVIEWER in {item.get("reviewer") for item in signoffs}:
            record["status"] = "canonical_assessed"
            if validate_assessment(record, records):
                record["status"] = "provisional_assessed"
    return mutate_assessment(assessment_id, update, root)


def waive_language(assessment_id: str, reviewer: str, reason: str, root: Path = REALITY_ROOT) -> Path:
    def update(record: dict[str, Any]) -> None:
        if not record.get("physical_evidence_exception"):
            raise RealityError("document the physical evidence exception before requesting a language waiver")
        if not str(record.get("language_search_record", "")).strip():
            raise RealityError("document the missing-language search before requesting a language waiver")
        waiver = record.setdefault("language_waiver", {"reason": reason, "reviewers": []})
        if not waiver.get("reason"):
            waiver["reason"] = reason
        reviewers = waiver.setdefault("reviewers", [])
        if reviewer in {item.get("reviewer") for item in reviewers}:
            raise RealityError(f"reviewer already approved waiver: {reviewer}")
        signed_at = utc_now()
        reviewers.append({"reviewer": reviewer, "signed_at": signed_at})
        signoffs = record.setdefault("signoffs", [])
        if reviewer not in {item.get("reviewer") for item in signoffs}:
            signoffs.append({"reviewer": reviewer, "signed_at": signed_at})
        record["status"] = "provisional_assessed"
        if CANONICAL_REVIEWER in {item.get("reviewer") for item in reviewers}:
            record["status"] = "canonical_with_language_waiver"
            records = load_records(root)
            records[assessment_id] = record
            failures = validate_assessment(record, records)
            if failures:
                raise RealityError("language waiver is not canonical: " + "; ".join(failures))
    return mutate_assessment(assessment_id, update, root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage the Narrative Geopolitics Reality Verification Lattice.")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new")
    new_sub = new.add_subparsers(dest="record_kind", required=True)
    claim = new_sub.add_parser("claim")
    claim.add_argument("--date", required=True); claim.add_argument("--id"); claim.add_argument("--type", choices=sorted(CLAIM_TYPES), required=True); claim.add_argument("--text", required=True); claim.add_argument("--consequence", choices=("high", "medium", "low"), default="medium"); claim.add_argument("--crisis-object", default="unspecified")
    observable = new_sub.add_parser("observable")
    observable.add_argument("--date", required=True); observable.add_argument("--id"); observable.add_argument("--claim", action="append", required=True); observable.add_argument("--text", required=True); observable.add_argument("--domain-profile", required=True); observable.add_argument("--resolution-rule", required=True); observable.add_argument("--end", default="open"); observable.add_argument("--language", action="append", default=[])
    investigation = new_sub.add_parser("investigation")
    investigation.add_argument("--date", required=True); investigation.add_argument("--id", required=True); investigation.add_argument("--claim", action="append", required=True); investigation.add_argument("--observable", action="append", required=True); investigation.add_argument("--text", required=True)

    add = sub.add_parser("add")
    add_sub = add.add_subparsers(dest="record_kind", required=True)
    evidence = add_sub.add_parser("evidence")
    evidence.add_argument("--date", required=True); evidence.add_argument("--id"); evidence.add_argument("--source", required=True); evidence.add_argument("--url", required=True); evidence.add_argument("--retrieved-at"); evidence.add_argument("--event-time", required=True); evidence.add_argument("--observation", required=True); evidence.add_argument("--origin-language", required=True); evidence.add_argument("--access-language", required=True); evidence.add_argument("--translation-provenance", choices=sorted(TRANSLATION_PROVENANCE), required=True); evidence.add_argument("--chain", required=True); evidence.add_argument("--environment", required=True); evidence.add_argument("--limitation", required=True); evidence.add_argument("--role", choices=sorted(EVIDENCE_ROLES), required=True)
    relation = add_sub.add_parser("relation")
    relation.add_argument("--date", required=True); relation.add_argument("--id"); relation.add_argument("--from-id", required=True); relation.add_argument("--to-id", required=True); relation.add_argument("--type", choices=sorted(RELATION_TYPES), required=True); relation.add_argument("--scope", required=True)

    land = sub.add_parser("land-evidence", help="add evidence, render views, and validate all records")
    land.add_argument("--date", required=True); land.add_argument("--id"); land.add_argument("--source", required=True); land.add_argument("--url", required=True); land.add_argument("--retrieved-at"); land.add_argument("--event-time", required=True); land.add_argument("--observation", required=True); land.add_argument("--origin-language", required=True); land.add_argument("--access-language", required=True); land.add_argument("--translation-provenance", choices=sorted(TRANSLATION_PROVENANCE), required=True); land.add_argument("--chain", required=True); land.add_argument("--environment", required=True); land.add_argument("--limitation", required=True); land.add_argument("--role", choices=sorted(EVIDENCE_ROLES), required=True)

    assess = sub.add_parser("assess"); assess.add_argument("claim_id")
    sign = sub.add_parser("sign"); sign.add_argument("assessment_id"); sign.add_argument("--reviewer", required=True)
    waive = sub.add_parser("waive-language"); waive.add_argument("assessment_id"); waive.add_argument("--reviewer", required=True); waive.add_argument("--reason", required=True)
    audit = sub.add_parser("audit"); audit.add_argument("claim_id"); audit.add_argument("--json", action="store_true")
    impact = sub.add_parser("impact"); impact.add_argument("claim_id"); impact.add_argument("--json", action="store_true")
    profile = sub.add_parser("profile"); profile.add_argument("voice"); profile.add_argument("--json", action="store_true")
    render = sub.add_parser("render"); render.add_argument("--check", action="store_true")
    check = sub.add_parser("check"); check.add_argument("record_id", nargs="?"); check.add_argument("--all", action="store_true")
    migrate = sub.add_parser("migrate"); migrate.add_argument("--date", required=True); migrate.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        if args.command == "new":
            print(create_scaffold(args).relative_to(REPO_ROOT).as_posix())
        elif args.command == "add":
            print(add_scaffold(args).relative_to(REPO_ROOT).as_posix())
        elif args.command == "land-evidence":
            print(land_evidence(args).relative_to(REPO_ROOT).as_posix())
        elif args.command == "assess":
            print(scaffold_assessment(args.claim_id).relative_to(REPO_ROOT).as_posix())
        elif args.command == "sign":
            print(sign_assessment(args.assessment_id, args.reviewer).relative_to(REPO_ROOT).as_posix())
        elif args.command == "waive-language":
            print(waive_language(args.assessment_id, args.reviewer, args.reason).relative_to(REPO_ROOT).as_posix())
        elif args.command == "audit":
            payload = audit_payload(args.claim_id)
            print(json.dumps(payload, indent=2) if args.json else render_audit_brief(payload))
        elif args.command == "impact":
            payload = impact_payload(args.claim_id)
            print(json.dumps(payload, indent=2) if args.json else "\n".join(payload["affected_ids"]))
        elif args.command == "profile":
            payload = profile_payload(args.voice)
            print(json.dumps(payload, indent=2) if args.json else f"visible_profiles={len(payload['profiles'])} withheld={len(payload['withheld'])}")
        elif args.command == "render":
            failures = write_views(check=args.check)
            if failures:
                print("\n".join(f"FAIL {item}" for item in failures))
                raise SystemExit(1)
            print("reality_views_current" if args.check else "reality_views_written")
        elif args.command == "check":
            records = load_records()
            if args.record_id:
                record = records.get(args.record_id)
                failures = [f"unknown record: {args.record_id}"] if not record else validate_record(record, records)
            else:
                failures = validate_all()
            if failures:
                print("\n".join(f"FAIL {item}" for item in failures))
                raise SystemExit(1)
            print("reality_failures=0")
        elif args.command == "migrate":
            if args.check:
                failures = check_migration(args.date) + validate_all()
                if failures:
                    print("\n".join(f"FAIL {item}" for item in failures))
                    raise SystemExit(1)
                print(f"reality_migration_current={args.date}")
            else:
                migrate_date(args.date)
                write_views()
                failures = validate_all()
                if failures:
                    print("\n".join(f"FAIL {item}" for item in failures))
                    raise SystemExit(1)
                print(f"reality_migrated={args.date}")
    except RealityError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()

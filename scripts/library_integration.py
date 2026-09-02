from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping


PROFILE_SCHEMA = "mira-library-work-profile-v1"
COVERAGE_SCHEMA = "mira-library-civmem-coverage-v1"
ROUTING_SCHEMA = "mira-library-routing-packet-v1"
TOPICS_SCHEMA = "mira-library-essay-topic-contracts-v1"
PILOT_MANIFEST_SCHEMA = "mira-library-integration-manifest-v1"
MANIFEST_SCHEMA = "mira-library-integration-manifest-v2"
NOTE_SCHEMA_V1 = "mira-library-integration-note-v1"
NOTE_SCHEMA_V2 = "mira-library-integration-note-v2"
NOTE_SCHEMA = "mira-library-integration-note-v3"
PILOT_ID = "mira-library-five-work-pilot-2026-09-01"
EXPECTED_WORKS = 5
EXPECTED_TOPICS = 15
INTEGRATION_RELATIVE_ROOT = Path("archive/library/integrations/pilot-2026-09-01")
LIVING_INTEGRATION_RELATIVE_PATH = Path("archive/library/integrations/manifest.json")
MANIFEST_NAME = "manifest.json"
WORK_REGISTRY_RELATIVE_PATH = Path("archive/library/integrations/work-registry.json")
ROUTE_INDEX_RELATIVE_PATH = Path("archive/library/integrations/route-index.json")
ROUTE_INDEX_MARKDOWN_RELATIVE_PATH = Path("archive/library/integrations/route-index.md")
NOTE_LINK_INDEX_RELATIVE_PATH = Path("archive/library/integrations/note-link-index.json")
NOTE_LINK_INDEX_MARKDOWN_RELATIVE_PATH = Path("archive/library/integrations/note-link-index.md")
INTEGRATION_SCHEMA_V1_RELATIVE_PATH = Path("archive/schemas/mira-library-integration-v1.schema.json")
INTEGRATION_SCHEMA_V2_RELATIVE_PATH = Path("archive/schemas/mira-library-integration-v2.schema.json")
INTEGRATION_SCHEMA_RELATIVE_PATH = Path("archive/schemas/mira-library-integration-v3.schema.json")
WORK_REGISTRY_SCHEMA_V1 = "mira-library-work-registry-v1"
WORK_REGISTRY_SCHEMA_V2 = "mira-library-work-registry-v2"
WORK_REGISTRY_SCHEMA = "mira-library-work-registry-v3"
ROUTE_INDEX_SCHEMA = "mira-library-route-index-v3"
NOTE_LINK_INDEX_SCHEMA = "mira-library-note-link-index-v2"
SUPPORTED_NOTE_SCHEMAS = {NOTE_SCHEMA_V1, NOTE_SCHEMA_V2, NOTE_SCHEMA}
SUPPORTED_WORK_REGISTRY_SCHEMAS = {
    WORK_REGISTRY_SCHEMA_V1,
    WORK_REGISTRY_SCHEMA_V2,
    WORK_REGISTRY_SCHEMA,
}
INTEGRATION_STAGES = {"noted", "routed"}
NOTE_TEMPLATE_ID = "mira-library-cognitive-note-v1"
NOTE_TEMPLATE_RELATIVE_PATH = Path(
    "archive/library/integrations/templates/cognitive-note-v1.md"
)
NOTE_TEMPLATE_HEADINGS = (
    "Encounter purpose",
    "Focal question",
    "Source basis and passage anchors",
    "Observations from the admitted body",
    "Provisional interpretation",
    "Mechanism model",
    "Counterpressure and rival readings",
    "Cross-work constellation",
    "Anti-analogy and scope limits",
    "Cognitive-scaffold implications",
    "Open questions",
    "Revision and operational boundary",
)
RELATION_TYPES = {"interprets", "questions", "contrasts", "connects", "applies", "revises"}
RELATION_ROLES = {"focal", "comparative", "supporting"}
REVIEW_DISPOSITIONS = {
    "unreviewed",
    "approved-internal",
    "rejected",
    "blocked-source",
}
NOTEBOOK_APPROVED_DISPOSITION = "approved-internal"
BODY_READY_STATES = {"available", "verified"}
MECHANISM_SIGNATURE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
GENERATED_MARKDOWN = {
    "profile.json": "profile.md",
    "coverage.json": "coverage.md",
    "routing.json": "routing.md",
    "essay-topics.json": "essay-topics.md",
}
HARD_SIGNAL_KINDS = {
    "operator-correction",
    "attribution-correction",
    "translation-correction",
    "body-coverage-correction",
    "source-limitation-removed",
    "source-limitation-worsened",
}
SOFT_SIGNAL_KINDS = {
    "essay-challenge",
    "topic-investigation-challenge",
    "cross-work-tension",
    "routing-contradiction",
}
REVISION_DISPOSITIONS = {"revised", "addendum", "reviewed-no-change", "blocked"}


class IntegrationError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise IntegrationError(f"missing integration artifact: {path.as_posix()}") from error
    except json.JSONDecodeError as error:
        raise IntegrationError(
            f"invalid integration JSON {path.as_posix()}: line {error.lineno}"
        ) from error
    if not isinstance(value, dict):
        raise IntegrationError(f"integration artifact must be an object: {path.as_posix()}")
    return value


def load_library_registry(repo_root: Path) -> dict[str, Any]:
    return load_json(repo_root / "archive" / "library" / "library-registry.json")


def load_work_registry(repo_root: Path) -> dict[str, Any]:
    return load_json(repo_root / WORK_REGISTRY_RELATIVE_PATH)


def revision_head_note_ref(work: Mapping[str, Any]) -> str:
    return str(work.get("revision_head_note_ref") or work.get("note_ref") or "")


def normalized_note_refs(work: Mapping[str, Any]) -> list[str]:
    raw = work.get("note_refs")
    values = raw if isinstance(raw, list) else [revision_head_note_ref(work)]
    refs: list[str] = []
    for value in values:
        if isinstance(value, str) and value and value not in refs:
            refs.append(value)
    return refs


def route_id_for_handle(handle: str) -> str:
    normalized = re.sub(r"[^A-Z0-9]+", "-", handle.upper()).strip("-")
    if not normalized:
        raise IntegrationError("route handle cannot produce an empty route id")
    return f"MIRA-ROUTE-{normalized}"


def validate_schema_contract(repo_root: Path) -> list[str]:
    """Bind the published schema identifiers to the canonical Python validator."""
    try:
        v1_schema = load_json(repo_root / INTEGRATION_SCHEMA_V1_RELATIVE_PATH)
        v2_schema = load_json(repo_root / INTEGRATION_SCHEMA_V2_RELATIVE_PATH)
        schema = load_json(repo_root / INTEGRATION_SCHEMA_RELATIVE_PATH)
    except IntegrationError as error:
        return [str(error)]
    failures: list[str] = []
    v1_definitions = v1_schema.get("$defs", {})
    v1_expected = {
        "profile": PROFILE_SCHEMA,
        "coverage": COVERAGE_SCHEMA,
        "routing": ROUTING_SCHEMA,
        "topics": TOPICS_SCHEMA,
        "manifest": PILOT_MANIFEST_SCHEMA,
        "workRegistry": WORK_REGISTRY_SCHEMA_V1,
        "routeIndex": "mira-library-route-index-v1",
    }
    for name, identifier in v1_expected.items():
        definition = v1_definitions.get(name, {}) if isinstance(v1_definitions, Mapping) else {}
        properties = definition.get("properties", {}) if isinstance(definition, Mapping) else {}
        if not properties and isinstance(definition, Mapping):
            for branch in definition.get("allOf", []):
                if isinstance(branch, Mapping) and isinstance(branch.get("properties"), Mapping):
                    properties = branch["properties"]
                    break
        version = properties.get("schema_version", {}) if isinstance(properties, Mapping) else {}
        if not isinstance(version, Mapping) or version.get("const") != identifier:
            failures.append(f"v1 integration schema {name} schema_version must be bound to {identifier}")
    v2_definitions = v2_schema.get("$defs", {})
    v2_expected = {
        "profile": PROFILE_SCHEMA,
        "coverage": COVERAGE_SCHEMA,
        "routing": ROUTING_SCHEMA,
        "topics": TOPICS_SCHEMA,
        "manifest": PILOT_MANIFEST_SCHEMA,
        "note": NOTE_SCHEMA_V2,
        "workRegistry": WORK_REGISTRY_SCHEMA_V2,
        "routeIndex": "mira-library-route-index-v2",
        "noteLinkIndex": NOTE_LINK_INDEX_SCHEMA,
    }
    for name, identifier in v2_expected.items():
        definition = (
            v2_definitions.get(name, {})
            if isinstance(v2_definitions, Mapping)
            else {}
        )
        properties = definition.get("properties", {}) if isinstance(definition, Mapping) else {}
        if not properties and isinstance(definition, Mapping):
            for branch in definition.get("allOf", []):
                if isinstance(branch, Mapping) and isinstance(branch.get("properties"), Mapping):
                    properties = branch["properties"]
                    break
        version = properties.get("schema_version", {}) if isinstance(properties, Mapping) else {}
        if not isinstance(version, Mapping) or version.get("const") != identifier:
            failures.append(
                f"v2 integration schema {name} schema_version must be bound to {identifier}"
            )
    definitions = schema.get("$defs", {})
    expected = {
        "profile": PROFILE_SCHEMA,
        "coverage": COVERAGE_SCHEMA,
        "routing": ROUTING_SCHEMA,
        "topics": TOPICS_SCHEMA,
        "manifest": MANIFEST_SCHEMA,
        "note": NOTE_SCHEMA,
        "workRegistry": WORK_REGISTRY_SCHEMA,
        "routeIndex": ROUTE_INDEX_SCHEMA,
        "noteLinkIndex": NOTE_LINK_INDEX_SCHEMA,
    }
    for name, identifier in expected.items():
        definition = definitions.get(name, {}) if isinstance(definitions, Mapping) else {}
        properties = definition.get("properties", {}) if isinstance(definition, Mapping) else {}
        if not properties and isinstance(definition, Mapping):
            for branch in definition.get("allOf", []):
                if isinstance(branch, Mapping) and isinstance(branch.get("properties"), Mapping):
                    properties = branch["properties"]
                    break
        schema_version = properties.get("schema_version", {}) if isinstance(properties, Mapping) else {}
        if not isinstance(schema_version, Mapping) or schema_version.get("const") != identifier:
            failures.append(
                f"integration schema {name} schema_version must be bound to {identifier}"
            )
    refs = {
        row.get("$ref")
        for row in schema.get("oneOf", [])
        if isinstance(row, Mapping)
    }
    expected_refs = {f"#/$defs/{name}" for name in expected}
    if refs != expected_refs:
        failures.append("integration schema oneOf references do not match canonical artifact types")
    return failures


def _required(record: Mapping[str, Any], fields: tuple[str, ...], label: str) -> list[str]:
    return [f"{label} missing required field: {field}" for field in fields if field not in record]


def _source_map(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(row.get("source_id")): row
        for row in registry.get("sources", [])
        if isinstance(row, Mapping) and row.get("source_id")
    }


def _body_map(source: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(row.get("body_id")): row
        for row in source.get("text_bodies", [])
        if isinstance(row, Mapping) and row.get("body_id")
    }


def parse_note_envelope(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    marker = "## Machine envelope\n\n```json\n"
    start = text.find(marker)
    if start < 0:
        raise IntegrationError(f"note lacks machine envelope: {path.as_posix()}")
    start += len(marker)
    end = text.find("\n```", start)
    if end < 0:
        raise IntegrationError(f"note machine envelope is unterminated: {path.as_posix()}")
    try:
        value = json.loads(text[start:end])
    except json.JSONDecodeError as error:
        raise IntegrationError(
            f"note machine envelope is invalid JSON {path.as_posix()}: line {error.lineno}"
        ) from error
    if not isinstance(value, dict):
        raise IntegrationError(f"note machine envelope must be an object: {path.as_posix()}")
    return value


def validate_note_template(path: Path, envelope: Mapping[str, Any]) -> list[str]:
    """Validate the human-authored cognitive-note v1 surface without creating it."""
    if envelope.get("schema_version") != NOTE_SCHEMA:
        return []
    label = path.as_posix()
    failures = _required(
        envelope,
        (
            "template_id",
            "focal_question",
            "provisional_thesis",
            "dependency_snapshot",
            "linked_artifact_digests",
            "library_relations",
        ),
        f"note template {label}",
    )
    if envelope.get("template_id") != NOTE_TEMPLATE_ID:
        failures.append(f"note template {label} has invalid template_id")
    for field in ("focal_question", "provisional_thesis"):
        value = envelope.get(field)
        if not isinstance(value, str) or not value.strip():
            failures.append(f"note template {label} requires nonempty {field}")
    text = path.read_text(encoding="utf-8")
    headings = [
        match.group(1).strip()
        for match in re.finditer(r"^## ([^\r\n]+)$", text, flags=re.MULTILINE)
        if match.group(1).strip() != "Machine envelope"
    ]
    if headings != list(NOTE_TEMPLATE_HEADINGS):
        failures.append(
            f"note template {label} headings must match cognitive-note v1 order"
        )
        return failures
    for index, heading in enumerate(NOTE_TEMPLATE_HEADINGS):
        marker = f"## {heading}"
        start = text.index(marker) + len(marker)
        if index + 1 < len(NOTE_TEMPLATE_HEADINGS):
            end = text.index(f"## {NOTE_TEMPLATE_HEADINGS[index + 1]}", start)
        else:
            end = len(text)
        body = text[start:end].strip()
        if not body:
            failures.append(f"note template {label} section is empty: {heading}")
    return failures


def validate_note_paths(repo_root: Path, note_refs: list[str] | None = None) -> dict[str, Any]:
    """Read-only validator for explicit notes; it never scaffolds or writes notes."""
    refs = note_refs
    if refs is None:
        registry = load_work_registry(repo_root)
        refs = [
            revision_head_note_ref(work)
            for work in registry.get("works", [])
            if isinstance(work, Mapping)
        ]
    failures: list[str] = []
    checked: list[str] = []
    for note_ref in refs:
        path = repo_root / note_ref
        try:
            envelope = parse_note_envelope(path)
            checked.append(note_ref)
            failures.extend(validate_note_template(path, envelope))
        except (IntegrationError, FileNotFoundError) as error:
            failures.append(str(error))
    return {
        "status": "passed" if not failures else "failed",
        "checked": checked,
        "failures": failures,
        "writes_performed": False,
    }


def library_relations_for_work(
    envelope: Mapping[str, Any], canonical_work_id: str
) -> list[Mapping[str, Any]]:
    relations = envelope.get("library_relations", [])
    if not isinstance(relations, list):
        return []
    return [
        relation
        for relation in relations
        if isinstance(relation, Mapping)
        and relation.get("target_type") == "library-work"
        and relation.get("target_id") == canonical_work_id
    ]


def validate_library_relations(
    envelope: Mapping[str, Any],
    known_work_ids: set[str],
    *,
    label: str,
) -> list[str]:
    failures: list[str] = []
    relations = envelope.get("library_relations")
    if not isinstance(relations, list) or not relations:
        return [f"{label} requires one or more explicit library_relations"]
    seen: set[tuple[str, str, str, str]] = set()
    passage_ids = set(envelope.get("dependency_snapshot", {}).get("passage_digests", {}))
    for index, relation in enumerate(relations):
        relation_label = f"{label} library relation {index + 1}"
        if not isinstance(relation, Mapping):
            failures.append(f"{relation_label} must be an object")
            continue
        target_type = relation.get("target_type")
        target_id = str(relation.get("target_id", ""))
        relation_type = relation.get("relation_type")
        role = relation.get("role")
        explanation = relation.get("explanation")
        passage_refs = relation.get("passage_refs", [])
        if target_type != "library-work":
            failures.append(f"{relation_label} has invalid target_type: {target_type}")
        if target_id not in known_work_ids:
            failures.append(f"{relation_label} references unknown work: {target_id}")
        if relation_type not in RELATION_TYPES:
            failures.append(f"{relation_label} has invalid relation_type: {relation_type}")
        if role not in RELATION_ROLES:
            failures.append(f"{relation_label} has invalid role: {role}")
        if not isinstance(explanation, str) or not explanation.strip():
            failures.append(f"{relation_label} requires a nonempty explanation")
        if not isinstance(passage_refs, list) or any(not isinstance(ref, str) for ref in passage_refs):
            failures.append(f"{relation_label} passage_refs must be an array of strings")
            passage_refs = []
        unknown_passages = sorted(set(passage_refs) - passage_ids)
        if unknown_passages:
            failures.append(
                f"{relation_label} references unknown note passages: {', '.join(unknown_passages)}"
            )
        identity = (str(target_type), target_id, str(relation_type), str(role))
        if identity in seen:
            failures.append(f"{relation_label} duplicates an existing relation")
        seen.add(identity)
    return failures


def write_note_envelope(path: Path, envelope: Mapping[str, Any]) -> None:
    note_text = path.read_text(encoding="utf-8")
    marker = "## Machine envelope\n\n```json\n"
    start = note_text.find(marker)
    if start < 0:
        raise IntegrationError(f"note lacks machine envelope: {path.as_posix()}")
    content_start = start + len(marker)
    content_end = note_text.find("\n```", content_start)
    if content_end < 0:
        raise IntegrationError(f"note machine envelope is unterminated: {path.as_posix()}")
    replacement = canonical_json(dict(envelope)).rstrip("\n")
    path.write_text(
        note_text[:content_start] + replacement + note_text[content_end:],
        encoding="utf-8",
    )


def render_profile(record: Mapping[str, Any]) -> str:
    identity = record["identity"]
    affordances = record["intellectual_affordances"]
    confidence = record["confidence"]
    lines = [
        f"# {identity['title']}",
        "",
        f"- Canonical work: `{record['canonical_work_id']}`",
        f"- Library source: `{record['library_source_id']}`",
        f"- Author: {identity['author']}",
        f"- Work form: `{record['work_form']}`",
        f"- Status: `{record['status']}`",
        f"- Knowledge basis: `{record['knowledge_basis']}`",
        "",
        "## Brief profile",
        "",
        record["synopsis"],
        "",
        "## Central question or situation",
        "",
        record["central_question_or_situation"],
        "",
        "## Intellectual affordances",
        "",
    ]
    for key in (
        "propositions", "mechanisms", "institutional_acts", "perceptual_patterns",
        "organizing_tensions", "forms_of_attention", "affective_movements", "symbolic_structures",
    ):
        values = affordances.get(key, [])
        lines.append(f"### {key.replace('_', ' ').title()}")
        lines.append("")
        lines.extend([f"- {item}" for item in values] or ["- None assigned."])
        lines.append("")
    lines.extend(["## Scope and resistance", "", "### Scope conditions", ""])
    lines.extend(f"- {item}" for item in record["scope_conditions"])
    lines.extend(["", "### Failure modes", ""])
    lines.extend(f"- {item}" for item in record["failure_modes"])
    lines.extend(["", "### Rival readings and internal tensions", ""])
    lines.extend(f"- {item}" for item in record["interpretive_field"]["rival_readings"])
    lines.extend(f"- {item}" for item in record["interpretive_field"]["internal_tensions"])
    lines.extend(["", "## Routing signatures", "", "### Positive", ""])
    lines.extend(f"- {item}" for item in record["routing_signatures"]["positive"])
    lines.extend(["", "### Negative and anti-analogy", ""])
    lines.extend(f"- {item}" for item in record["routing_signatures"]["negative"])
    lines.extend(f"- {item}" for item in record["routing_signatures"]["anti_analogy"])
    lines.extend(["", "## Confidence", ""])
    for key in (
        "identity", "body_integrity", "body_characterization", "bibliographic",
        "doctrinal_or_formal_summary", "civilization_memory_interpretation", "routing_readiness",
    ):
        lines.append(f"- {key.replace('_', ' ').title()}: `{confidence[key]}`")
    lines.extend(["", "## Uncertainties", ""])
    lines.extend(f"- {item}" for item in record["uncertainties"])
    lines.extend(["", "## Passage anchors", ""])
    anchors = record.get("textual_basis", {}).get("passage_anchors", [])
    if not anchors:
        lines.append("- None assigned.")
    for anchor in anchors:
        locator = anchor["locator"]
        lines.extend([
            f"### `{anchor['passage_id']}`", "",
            f"- Body: `{anchor['body_id']}`",
            f"- Section: {locator['section']}",
            f"- Lines: `{locator['line_start']}-{locator['line_end']}`",
            f"- Voice role: `{anchor['voice_role']}`",
            f"- Claim type: `{anchor['claim_type']}`",
            f"- Raw-span SHA-256: `{anchor['raw_span_sha256']}`",
            f"- Function: {anchor['anchor_summary']}", "",
        ])
    lines.extend(["", "## Authority boundary", "", record["authority_boundary"], ""])
    return "\n".join(lines)


def render_coverage(record: Mapping[str, Any]) -> str:
    lines = [
        f"# Civilization Memory Coverage — {record['work_title']}", "",
        f"- Canonical work: `{record['canonical_work_id']}`",
        f"- Decision: `{record['coverage_decision']}`",
        f"- Scope: {record['coverage_scope']}",
        f"- External research authorized: `{str(record['external_research_authorized']).lower()}`",
        f"- External research used: `{str(record['external_research_used']).lower()}`",
        "", "## Search scope", "",
    ]
    lines.extend(f"- {item}" for item in record["search_scope"])
    lines.extend(["", "## Direct objects opened", ""])
    objects = record["direct_objects_opened"]
    lines.extend(
        [f"- `{item['id']}` — `{item['digest']}` — {item['relevance']}" for item in objects]
        or ["- None found."]
    )
    lines.extend(["", "## Adjudication", "", record["adjudication"], "", "## Unresolved gaps", ""])
    lines.extend(f"- {item}" for item in record["unresolved_gaps"])
    lines.extend(["", "## Authority boundary", "", record["authority_boundary"], ""])
    return "\n".join(lines)


def render_routing(record: Mapping[str, Any]) -> str:
    lines = [
        f"# Routing Packet — {record['work_title']}", "",
        f"- Canonical work: `{record['canonical_work_id']}`",
        f"- Status: `{record['status']}`",
        f"- Note revision state: `{record['note_revision_state']}`",
        "", "## Route units", "",
    ]
    for unit in record["route_units"]:
        lines.extend([
            f"### `{unit['handle']}`", "",
            f"- Retrieval problem: {unit['retrieval_problem']}",
            f"- Analytic function: {unit['analytic_function']}",
            f"- Proposition or pattern: {unit['proposition_or_pattern']}",
            f"- Mechanism: {unit['mechanism']}",
            f"- Anti-analogy: {unit['anti_analogy']}",
            f"- Confidence: `{unit['confidence']}`",
            f"- Route state: `{unit['route_state']}`", "",
            "**Contraindications**", "",
        ])
        lines.extend(f"- {item}" for item in unit["contraindications"])
        lines.extend(["", "**Evidence posture**", ""])
        lines.extend(f"- `{item['kind']}` — `{item['ref']}`" for item in unit["evidence_refs"])
        lines.extend(["", "**Counterweights**", ""])
        lines.extend(
            [f"- `{item['kind']}` — `{item['ref']}` — {item['role']}" for item in unit["counterweight_refs"]]
            or ["- None assigned."]
        )
        lines.append("")
    lines.extend(["## Negative route rules", ""])
    lines.extend(f"- {item}" for item in record["negative_route_rules"])
    lines.extend(["", "## Coverage constraints", ""])
    lines.extend(f"- {item}" for item in record["coverage_constraints"])
    lines.extend(["", "## Authority boundary", "", record["authority_boundary"], ""])
    return "\n".join(lines)


def render_topics(record: Mapping[str, Any]) -> str:
    lines = [
        f"# Essay Topic Contracts — {record['work_title']}", "",
        f"- Canonical work: `{record['canonical_work_id']}`",
        f"- Essay artifacts created: `{record['essay_artifacts_created']}`",
        f"- Essay relationship: `essay_refs[]` ({len(record['essay_refs'])} current)", "",
    ]
    for topic in sorted(record["topics"], key=lambda row: row["rank"]):
        lines.extend([
            f"## {topic['rank']}. {topic['provisional_title']}", "",
            topic["governing_question"], "",
            f"- Topic contract: `{topic['topic_contract_id']}`",
            f"- Mode: `{topic['essay_mode']}`",
            f"- Evidence readiness: `{topic['evidence_readiness']}`",
            f"- Source posture: {topic['source_posture']}",
            f"- Central tension: {topic['central_tension']}",
            f"- Routing contribution: {topic['routing_contribution']}",
            f"- Voice contribution: {topic['voice_contribution']}",
            f"- External research authorized: `{str(topic['external_research_authorized']).lower()}`",
            "", "**Missing evidence**", "",
        ])
        lines.extend(f"- {item}" for item in topic["missing_evidence"])
        lines.extend(["", f"**Do not draft yet:** {topic['do_not_draft_yet']}", ""])
    lines.extend(["## Authority boundary", "", record["authority_boundary"], ""])
    return "\n".join(lines)


def render_record(path: Path, record: Mapping[str, Any]) -> str:
    name = path.name
    if name == "profile.json":
        return render_profile(record)
    if name == "coverage.json":
        return render_coverage(record)
    if name == "routing.json":
        return render_routing(record)
    if name == "essay-topics.json":
        return render_topics(record)
    raise IntegrationError(f"no renderer for {name}")


def mediation_dependency_projection(mediation: Any) -> dict[str, Any] | None:
    if not isinstance(mediation, Mapping):
        return None
    primary_path = mediation.get("primary_path", [])
    relevant_layers = [
        dict(layer)
        for layer in primary_path
        if isinstance(layer, Mapping)
        and layer.get("revision_relevance") != "carrier-only"
    ] if isinstance(primary_path, list) else []
    projection = {
        "schema_version": mediation.get("schema_version"),
        "text_relation": mediation.get("text_relation"),
        "edition_identity": mediation.get("edition_identity"),
        "primary_path": relevant_layers,
        "unresolved_questions": mediation.get("unresolved_questions", []),
    }
    dependency_slice = mediation.get("lineage_dependency_slice")
    if dependency_slice is not None:
        projection["lineage_dependency_slice"] = dependency_slice
    return projection


def dependency_snapshot(
    work_dir: Path,
    source: Mapping[str, Any],
    *,
    scoped: bool = False,
) -> dict[str, Any]:
    all_bodies = _body_map(source)
    profile = load_json(work_dir / "profile.json")
    anchors = profile.get("textual_basis", {}).get("passage_anchors", [])
    if scoped:
        selected_ids = {
            str(row.get("body_id"))
            for row in profile.get("textual_basis", {}).get("body_refs", [])
            if isinstance(row, Mapping) and row.get("body_id")
        }
        bodies = {key: row for key, row in all_bodies.items() if key in selected_ids}
    else:
        bodies = all_bodies
    return {
        "source_identity_digest": hashlib.sha256(
            json.dumps(
                {
                    "source_id": source.get("source_id"),
                    "title": source.get("title"),
                    "author": source.get("author"),
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
        "body_digests": {key: row.get("text_sha256") for key, row in sorted(bodies.items())},
        "body_states": {
            key: {
                "status": row.get("status"),
                "coverage_status": row.get("coverage_status"),
                "language": row.get("language"),
                "mediation_type": row.get("mediation_type"),
                "translator": row.get("translator"),
                "translator_status": row.get("translator_status"),
                "editor": row.get("editor"),
                "editor_status": row.get("editor_status"),
                "edition_label": row.get("edition_label"),
                "mediation": mediation_dependency_projection(row.get("mediation")),
            }
            for key, row in sorted(bodies.items())
        },
        "passage_digests": {
            str(row.get("passage_id")): row.get("raw_span_sha256")
            for row in anchors
            if isinstance(row, Mapping) and row.get("passage_id")
        },
    }


def dependency_snapshot_for_note(
    work_dir: Path,
    source: Mapping[str, Any],
    envelope: Mapping[str, Any],
) -> dict[str, Any]:
    return dependency_snapshot(
        work_dir,
        source,
        scoped=envelope.get("schema_version") == NOTE_SCHEMA,
    )


def linked_artifact_digests(work_dir: Path, *, integration_stage: str = "routed") -> dict[str, str]:
    """Return navigational links that do not govern a note's interpretation."""
    digests = {"profile_sha256": sha256_file(work_dir / "profile.json")}
    if integration_stage == "routed":
        digests.update(
            {
                "coverage_sha256": sha256_file(work_dir / "coverage.json"),
                "routing_sha256": sha256_file(work_dir / "routing.json"),
                "topics_sha256": sha256_file(work_dir / "essay-topics.json"),
            }
        )
    return digests


def classify_note_changes(
    baseline: Mapping[str, Any],
    current: Mapping[str, Any],
    signals: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    hard_keys = ("source_identity_digest", "body_digests", "body_states", "passage_digests")
    soft_keys: tuple[str, ...] = ()
    hard_changes = [key for key in hard_keys if baseline.get(key) != current.get(key)]
    soft_changes = [key for key in soft_keys if baseline.get(key) != current.get(key)]
    signal_rows = list(signals or [])
    hard_signals = [row for row in signal_rows if row.get("kind") in HARD_SIGNAL_KINDS]
    soft_signals = [row for row in signal_rows if row.get("kind") in SOFT_SIGNAL_KINDS]
    unknown_signals = [row for row in signal_rows if row.get("kind") not in HARD_SIGNAL_KINDS | SOFT_SIGNAL_KINDS]
    if hard_changes or hard_signals:
        state = "revision-due"
    elif soft_changes or soft_signals:
        state = "review-suggested"
    else:
        state = "current"
    return {
        "state": state,
        "hard_changes": hard_changes,
        "soft_changes": soft_changes,
        "hard_signals": hard_signals,
        "soft_signals": soft_signals,
        "unknown_signals": unknown_signals,
    }


def validate_revision_candidate(candidate: Mapping[str, Any]) -> list[str]:
    failures = _required(
        candidate,
        ("schema_version", "candidate_id", "canonical_work_id", "trigger", "changed_dependencies", "affected_claims", "open_questions", "rereading_scope", "status"),
        "revision candidate",
    )
    disposition = candidate.get("disposition")
    if disposition is not None and disposition not in REVISION_DISPOSITIONS:
        failures.append(f"revision candidate has invalid disposition: {disposition}")
    if candidate.get("status") == "resolved" and disposition not in REVISION_DISPOSITIONS:
        failures.append("resolved revision candidate requires a valid disposition")
    return failures


def matching_open_revision_candidate(
    work_dir: Path,
    canonical_work_id: str,
    predecessor_note_ref: str,
    trigger: Mapping[str, Any],
) -> tuple[Path, dict[str, Any]] | None:
    for path in sorted(work_dir.glob("note-revision-candidate*.json")):
        try:
            candidate = load_json(path)
        except IntegrationError:
            continue
        if (
            candidate.get("status") == "open"
            and candidate.get("canonical_work_id") == canonical_work_id
            and candidate.get("predecessor_note_ref") == predecessor_note_ref
            and candidate.get("trigger") == trigger
        ):
            return path, candidate
    return None


def next_revision_candidate(work_dir: Path, canonical_work_id: str) -> tuple[Path, str]:
    existing = sorted(work_dir.glob("note-revision-candidate*.json"))
    sequences: list[int] = []
    for path in existing:
        try:
            candidate_id = str(load_json(path).get("candidate_id", ""))
        except IntegrationError:
            continue
        parts = candidate_id.rsplit("-", 1)
        if len(parts) == 2 and parts[1].isdigit():
            sequences.append(int(parts[1]))
    sequence = max(sequences, default=0) + 1
    candidate_path = work_dir / f"note-revision-candidate-{sequence:03d}.json"
    while candidate_path.exists():
        sequence += 1
        candidate_path = work_dir / f"note-revision-candidate-{sequence:03d}.json"
    return candidate_path, f"REV-{canonical_work_id}-{sequence:03d}"


def reconcile_work(
    repo_root: Path,
    work: Mapping[str, Any],
    source: Mapping[str, Any],
    *,
    write: bool = False,
) -> dict[str, Any]:
    work_dir = repo_root / work["artifact_root"]
    head_note_ref = revision_head_note_ref(work)
    note_path = repo_root / head_note_ref
    envelope = parse_note_envelope(note_path)
    current = dependency_snapshot_for_note(work_dir, source, envelope)
    signals_path = work_dir / "note-signals.json"
    signals: list[Mapping[str, Any]] = []
    if signals_path.exists():
        raw_signals = load_json(signals_path).get("signals", [])
        if isinstance(raw_signals, list):
            signals = [row for row in raw_signals if isinstance(row, Mapping)]
    result = classify_note_changes(envelope.get("dependency_snapshot", {}), current, signals)
    canonical_work_id = str(work["canonical_work_id"])
    predecessor_note_ref = head_note_ref
    matching_candidate = matching_open_revision_candidate(
        work_dir, canonical_work_id, predecessor_note_ref, result
    )
    if matching_candidate is None:
        candidate_path, candidate_id = next_revision_candidate(work_dir, canonical_work_id)
    else:
        candidate_path, existing_candidate = matching_candidate
        candidate_id = str(existing_candidate["candidate_id"])
    candidate_written = False
    candidate_reused = matching_candidate is not None
    routing_suspended = False
    if write and result["state"] != "current":
        affected_routes: list[str] = []
        suspended_route_states: dict[str, str] = {}
        if result["state"] == "revision-due":
            routing_path = work_dir / "routing.json"
            routing = load_json(routing_path)
            routing_changed = routing.get("note_revision_state") != "revision-due"
            for unit in routing.get("route_units", []):
                if isinstance(unit, dict):
                    handle = str(unit.get("handle", "unknown-route"))
                    affected_routes.append(handle)
                    route_state = str(unit.get("route_state", "unknown"))
                    if route_state != "suspended-due-to-note-revision":
                        suspended_route_states[handle] = route_state
                        unit["route_state"] = "suspended-due-to-note-revision"
                        routing_changed = True
            if routing_changed:
                routing["note_revision_state"] = "revision-due"
                routing_path.write_text(canonical_json(routing), encoding="utf-8")
                (work_dir / "routing.md").write_text(render_routing(routing), encoding="utf-8")
                routing_suspended = True
        if matching_candidate is None:
            candidate = {
                "schema_version": "mira-library-note-revision-candidate-v1",
                "candidate_id": candidate_id,
                "canonical_work_id": work["canonical_work_id"],
                "trigger": result,
                "changed_dependencies": result["hard_changes"] + result["soft_changes"],
                "affected_claims": affected_routes,
                "suspended_route_states": suspended_route_states,
                "open_questions": envelope.get("open_questions", []),
                "rereading_scope": envelope.get("rereading_scope_on_change", []),
                "status": "open",
                "disposition": None,
                "predecessor_note_ref": head_note_ref,
                "authority_boundary": "This candidate may prepare review but may not rewrite interpretive prose or activate routing.",
            }
            candidate_path.write_text(canonical_json(candidate), encoding="utf-8")
            candidate_written = True
    return {
        "canonical_work_id": work["canonical_work_id"],
        **result,
        "candidate_path": candidate_path.relative_to(repo_root).as_posix(),
        "candidate_written": candidate_written,
        "candidate_reused": candidate_reused,
        "routing_suspended": routing_suspended,
    }


def load_pilot_manifest(repo_root: Path) -> dict[str, Any]:
    return load_json(repo_root / INTEGRATION_RELATIVE_ROOT / MANIFEST_NAME)


def load_manifest(repo_root: Path) -> dict[str, Any]:
    return load_json(repo_root / LIVING_INTEGRATION_RELATIVE_PATH)


def validate_work_registry(repo_root: Path, registry: Mapping[str, Any]) -> list[str]:
    path = repo_root / WORK_REGISTRY_RELATIVE_PATH
    if not path.exists():
        return [f"missing integration artifact: {path.as_posix()}"]
    try:
        work_registry = load_work_registry(repo_root)
        pilot = load_pilot_manifest(repo_root)
        living = load_manifest(repo_root)
    except IntegrationError as error:
        return [str(error)]
    failures = _required(
        work_registry,
        ("schema_version", "status", "works", "authority_boundary"),
        "work integration registry",
    )
    registry_schema = work_registry.get("schema_version")
    if registry_schema not in SUPPORTED_WORK_REGISTRY_SCHEMAS:
        failures.append(
            "work integration registry has invalid schema_version: "
            f"{registry_schema}"
        )
    works = work_registry.get("works", [])
    if not isinstance(works, list):
        return [*failures, "work integration registry works must be an array"]
    sources = _source_map(registry)
    pilot_works = {
        str(row.get("canonical_work_id")): row
        for row in pilot.get("works", [])
        if isinstance(row, Mapping) and row.get("canonical_work_id")
    }
    living_works = {
        str(row.get("canonical_work_id")): row
        for row in living.get("works", [])
        if isinstance(row, Mapping) and row.get("canonical_work_id")
    }
    seen_work_ids: set[str] = set()
    seen_route_ids: set[str] = set()
    for work in works:
        if not isinstance(work, Mapping):
            failures.append("work integration registry work must be an object")
            continue
        required_fields = (
            "canonical_work_id",
            "library_source_id",
            "artifact_root",
            "note_ref",
            "essay_refs",
            "route_reviews",
        )
        if registry_schema in {WORK_REGISTRY_SCHEMA_V2, WORK_REGISTRY_SCHEMA}:
            required_fields = (*required_fields, "revision_head_note_ref", "note_refs")
        if registry_schema == WORK_REGISTRY_SCHEMA:
            required_fields = (*required_fields, "integration_stage")
        failures.extend(_required(work, required_fields, "work integration record"))
        work_id = str(work.get("canonical_work_id", ""))
        if work_id in seen_work_ids:
            failures.append(f"duplicate work integration canonical_work_id: {work_id}")
        seen_work_ids.add(work_id)
        source_id = str(work.get("library_source_id", ""))
        if source_id not in sources:
            failures.append(f"{work_id} work integration references missing source: {source_id}")
        pilot_work = pilot_works.get(work_id)
        if pilot_work is not None:
            comparison_fields = ("library_source_id", "artifact_root")
            if registry_schema != WORK_REGISTRY_SCHEMA:
                comparison_fields = (*comparison_fields, "note_ref")
            for field in comparison_fields:
                if work.get(field) != pilot_work.get(field):
                    failures.append(f"{work_id} work integration {field} disagrees with pilot")
        living_work = living_works.get(work_id)
        if living_work is None:
            failures.append(f"{work_id} work integration is absent from living manifest")
        else:
            for field in (
                "library_source_id",
                "artifact_root",
                "integration_stage",
                "revision_head_note_ref",
            ):
                if work.get(field) != living_work.get(field):
                    failures.append(
                        f"{work_id} work integration {field} disagrees with living manifest"
                    )
        head_note_ref = revision_head_note_ref(work)
        note_refs = normalized_note_refs(work)
        if registry_schema in {WORK_REGISTRY_SCHEMA_V2, WORK_REGISTRY_SCHEMA}:
            if work.get("note_ref") != head_note_ref:
                failures.append(f"{work_id} deprecated note_ref must mirror revision_head_note_ref")
            if not note_refs or head_note_ref not in note_refs:
                failures.append(f"{work_id} note_refs must contain the revision head")
            if pilot_work is not None:
                pilot_refs = normalized_note_refs(pilot_work)
                if note_refs[: len(pilot_refs)] != pilot_refs:
                    failures.append(
                        f"{work_id} work integration must preserve pilot note_refs as lineage prefix"
                    )
        stage = str(work.get("integration_stage", "routed"))
        if registry_schema == WORK_REGISTRY_SCHEMA and stage not in INTEGRATION_STAGES:
            failures.append(f"{work_id} has invalid integration_stage: {stage}")
        note_envelopes: dict[str, dict[str, Any]] = {}
        for note_ref in note_refs:
            try:
                envelope = parse_note_envelope(repo_root / note_ref)
                note_envelopes[note_ref] = envelope
                if envelope.get("schema_version") not in SUPPORTED_NOTE_SCHEMAS:
                    failures.append(
                        f"{work_id} note has unsupported schema: {note_ref}"
                    )
                failures.extend(validate_note_template(repo_root / note_ref, envelope))
            except (IntegrationError, FileNotFoundError) as error:
                failures.append(str(error))
        if registry_schema == WORK_REGISTRY_SCHEMA and note_refs:
            head_envelope = note_envelopes.get(head_note_ref, {})
            if head_envelope.get("schema_version") != NOTE_SCHEMA:
                failures.append(f"{work_id} revision head must use {NOTE_SCHEMA}")
            for index, note_ref in enumerate(note_refs[1:], start=1):
                predecessor = note_envelopes.get(note_ref, {}).get("predecessor_note_ref")
                if predecessor != note_refs[index - 1]:
                    failures.append(
                        f"{work_id} note lineage is not contiguous at {note_ref}"
                    )
        essay_refs = work.get("essay_refs")
        if not isinstance(essay_refs, list) or any(not isinstance(ref, str) for ref in essay_refs):
            failures.append(f"{work_id} essay_refs must be an array of strings")
            essay_refs = []
        work_dir = repo_root / str(work.get("artifact_root", ""))
        if stage == "noted":
            if work.get("route_reviews") != []:
                failures.append(f"{work_id} noted work must have no route reviews")
            if work.get("essay_refs") != []:
                failures.append(f"{work_id} noted work must have no essay refs")
            for forbidden in ("coverage.json", "routing.json", "essay-topics.json"):
                if (work_dir / forbidden).exists():
                    failures.append(f"{work_id} noted work must not create {forbidden}")
            continue
        try:
            routing = load_json(work_dir / "routing.json")
        except IntegrationError as error:
            failures.append(str(error))
            continue
        packet_handles = {
            str(unit.get("handle"))
            for unit in routing.get("route_units", [])
            if isinstance(unit, Mapping) and unit.get("handle")
        }
        reviews = work.get("route_reviews")
        if not isinstance(reviews, list):
            failures.append(f"{work_id} route_reviews must be an array")
            continue
        review_handles: set[str] = set()
        for review in reviews:
            if not isinstance(review, Mapping):
                failures.append(f"{work_id} route review must be an object")
                continue
            handle = str(review.get("route_handle", ""))
            if not handle:
                failures.append(f"{work_id} route review lacks route_handle")
                continue
            if handle in review_handles:
                failures.append(f"{work_id} has duplicate route review: {handle}")
            review_handles.add(handle)
            route_id = route_id_for_handle(handle)
            if route_id in seen_route_ids:
                failures.append(f"duplicate operational route id: {route_id}")
            seen_route_ids.add(route_id)
            disposition = review.get("review_disposition")
            if disposition not in REVIEW_DISPOSITIONS:
                failures.append(
                    f"{work_id} route {handle} has invalid review_disposition: {disposition}"
                )
            binding = review.get("review_binding")
            review_note_refs = review.get("note_refs")
            if registry_schema in {WORK_REGISTRY_SCHEMA_V2, WORK_REGISTRY_SCHEMA}:
                if (
                    not isinstance(review_note_refs, list)
                    or not review_note_refs
                    or any(not isinstance(ref, str) for ref in review_note_refs)
                ):
                    failures.append(f"{work_id} route {handle} requires explicit note_refs")
                    review_note_refs = []
                elif len(review_note_refs) != len(set(review_note_refs)):
                    failures.append(f"{work_id} route {handle} note_refs must be unique")
            elif not isinstance(review_note_refs, list):
                review_note_refs = [head_note_ref]
            unknown_note_refs = sorted(set(review_note_refs) - set(note_refs))
            if unknown_note_refs:
                failures.append(
                    f"{work_id} route {handle} references notes outside the work registry: "
                    + ", ".join(unknown_note_refs)
                )
            for note_ref in review_note_refs:
                note_envelope = note_envelopes.get(note_ref, {})
                if not library_relations_for_work(note_envelope, work_id):
                    failures.append(
                        f"{work_id} route {handle} note lacks an explicit relation to the work: {note_ref}"
                    )
            if disposition == NOTEBOOK_APPROVED_DISPOSITION:
                required_binding_fields = {"route_unit_sha256", "body_digests"}
                if registry_schema in {WORK_REGISTRY_SCHEMA_V2, WORK_REGISTRY_SCHEMA}:
                    required_binding_fields.add("note_bindings")
                else:
                    required_binding_fields.add("note_dependency_sha256")
                if not isinstance(binding, Mapping) or set(binding) != required_binding_fields:
                    failures.append(
                        f"{work_id} approved route {handle} requires a complete review_binding"
                    )
                elif registry_schema in {WORK_REGISTRY_SCHEMA_V2, WORK_REGISTRY_SCHEMA}:
                    note_bindings = binding.get("note_bindings")
                    binding_refs = [
                        row.get("note_ref")
                        for row in note_bindings
                        if isinstance(row, Mapping)
                    ] if isinstance(note_bindings, list) else []
                    if binding_refs != review_note_refs:
                        failures.append(
                            f"{work_id} approved route {handle} review_binding note order must match note_refs"
                        )
            elif binding is not None:
                failures.append(
                    f"{work_id} unapproved route {handle} must not carry a review_binding"
                )
            signatures = review.get("mechanism_signatures")
            if (
                not isinstance(signatures, list)
                or not signatures
                or any(
                    not isinstance(signature, str)
                    or not MECHANISM_SIGNATURE_RE.fullmatch(signature)
                    for signature in signatures
                )
            ):
                failures.append(
                    f"{work_id} route {handle} requires one or more normalized mechanism_signatures"
                )
        if review_handles != packet_handles:
            missing = sorted(packet_handles - review_handles)
            extra = sorted(review_handles - packet_handles)
            if missing:
                failures.append(f"{work_id} work registry lacks route reviews: {', '.join(missing)}")
            if extra:
                failures.append(f"{work_id} work registry has unknown route reviews: {', '.join(extra)}")
    living_ids = set(living_works)
    if seen_work_ids != living_ids:
        missing = sorted(living_ids - seen_work_ids)
        extra = sorted(seen_work_ids - living_ids)
        if missing:
            failures.append(
                "work integration registry lacks living works: " + ", ".join(missing)
            )
        if extra:
            failures.append(
                "work integration registry has works outside living manifest: "
                + ", ".join(extra)
            )
    return failures


def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def current_review_binding(
    unit: Mapping[str, Any],
    notes: Mapping[str, Any] | list[Mapping[str, Any]],
    body_refs: list[Mapping[str, Any]],
) -> dict[str, Any]:
    binding = {
        "route_unit_sha256": digest_json(unit),
        "body_digests": {
            str(row.get("body_id")): row.get("sha256") for row in body_refs
        },
    }
    if isinstance(notes, Mapping):
        binding["note_dependency_sha256"] = digest_json(
            notes.get("dependency_snapshot", {})
        )
    else:
        binding["note_bindings"] = [
            {
                "note_ref": row["note_ref"],
                "note_sha256": row["note_sha256"],
                "note_dependency_sha256": row["note_dependency_sha256"],
            }
            for row in notes
        ]
    return binding


def build_route_index(repo_root: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    work_registry = load_work_registry(repo_root)
    sources = _source_map(registry)
    routes: list[dict[str, Any]] = []
    work_summaries: list[dict[str, Any]] = []
    for work in work_registry.get("works", []):
        work_id = str(work["canonical_work_id"])
        source_id = str(work["library_source_id"])
        source = sources.get(source_id, {})
        work_dir = repo_root / str(work["artifact_root"])
        profile = load_json(work_dir / "profile.json")
        stage_contract = str(work.get("integration_stage", "routed"))
        head_note_ref = revision_head_note_ref(work)
        head_note = parse_note_envelope(repo_root / head_note_ref)
        current_head_dependencies = dependency_snapshot_for_note(
            work_dir, source, head_note
        )
        head_note_state = classify_note_changes(
            head_note.get("dependency_snapshot", {}), current_head_dependencies
        )["state"]
        if stage_contract == "noted":
            work_summaries.append(
                {
                    "canonical_work_id": work_id,
                    "integration_stage": "noted" if head_note_state == "current" else "stale",
                    "eligible_route_count": 0,
                    "essay_ref_count": 0,
                }
            )
            continue
        routing = load_json(work_dir / "routing.json")
        anchors = profile.get("textual_basis", {}).get("passage_anchors", [])
        anchor_digests = {
            str(row.get("passage_id")): row.get("raw_span_sha256")
            for row in anchors
            if isinstance(row, Mapping) and row.get("passage_id")
        }
        body_map = _body_map(source)
        body_refs: list[dict[str, Any]] = []
        body_failures: list[str] = []
        for body_ref in profile.get("textual_basis", {}).get("body_refs", []):
            body_id = str(body_ref.get("body_id", ""))
            body = body_map.get(body_id)
            expected_digest = body_ref.get("text_sha256")
            current_digest = body.get("text_sha256") if body else None
            status = body.get("status") if body else None
            body_refs.append(
                {"body_id": body_id, "sha256": expected_digest, "status": status}
            )
            if body is None:
                body_failures.append(f"missing-body:{body_id}")
            elif current_digest != expected_digest:
                body_failures.append(f"body-digest-mismatch:{body_id}")
            elif status not in BODY_READY_STATES:
                body_failures.append(f"body-not-ready:{body_id}:{status}")
        if not body_refs:
            body_failures.append("no-admitted-body-ref")
        reviews = {
            str(row.get("route_handle")): row
            for row in work.get("route_reviews", [])
            if isinstance(row, Mapping) and row.get("route_handle")
        }
        work_routes: list[dict[str, Any]] = []
        for unit in routing.get("route_units", []):
            if not isinstance(unit, Mapping):
                continue
            handle = str(unit.get("handle", ""))
            review = reviews.get(handle, {})
            reasons = list(body_failures)
            disposition = str(review.get("review_disposition", ""))
            packet_note_state = str(routing.get("note_revision_state", ""))
            packet_status = str(routing.get("status", ""))
            review_note_refs = review.get("note_refs")
            if not isinstance(review_note_refs, list):
                review_note_refs = [head_note_ref]
            note_bindings: list[dict[str, Any]] = []
            for note_ref in review_note_refs:
                note_path = repo_root / str(note_ref)
                note = parse_note_envelope(note_path)
                current_dependencies = dependency_snapshot_for_note(
                    work_dir, source, note
                )
                note_state = classify_note_changes(
                    note.get("dependency_snapshot", {}), current_dependencies
                )["state"]
                relations = library_relations_for_work(note, work_id)
                note_binding = {
                    "note_ref": str(note_ref),
                    "note_sha256": sha256_file(note_path),
                    "note_dependency_sha256": digest_json(
                        note.get("dependency_snapshot", {})
                    ),
                    "note_revision_state": note_state,
                    "relation_types": sorted(
                        {str(row.get("relation_type")) for row in relations}
                    ),
                    "roles": sorted({str(row.get("role")) for row in relations}),
                }
                note_bindings.append(note_binding)
                if note_state != "current":
                    reasons.append(f"note-{note_state}")
                if not relations:
                    reasons.append(f"note-relation-missing:{note_ref}")
                if note.get("interpretive_basis") != "admitted-source-body":
                    reasons.append("note-not-source-direct")
            if packet_note_state != "current":
                reasons.append(f"routing-note-{packet_note_state}")
            if packet_status in {"superseded", "withdrawn"}:
                reasons.append(f"route-packet-{packet_status}")
            if not anchor_digests:
                reasons.append("no-passage-anchors")
            route_anchor_refs = [
                row
                for row in unit.get("evidence_refs", [])
                if isinstance(row, Mapping)
                and row.get("kind") == "primary-passage"
                and anchor_digests.get(str(row.get("ref"))) == row.get("digest")
            ]
            if not route_anchor_refs:
                reasons.append("no-current-route-passage-anchor")
            if disposition != NOTEBOOK_APPROVED_DISPOSITION:
                reasons.append(f"review-{disposition or 'missing'}")
            binding = current_review_binding(unit, note_bindings, body_refs)
            recorded_binding = review.get("review_binding")
            if disposition == NOTEBOOK_APPROVED_DISPOSITION:
                binding_status = "current" if recorded_binding == binding else "stale"
                if binding_status == "stale":
                    reasons.append("review-binding-stale")
            else:
                binding_status = "not-applicable"
            reasons = list(dict.fromkeys(reasons))
            route = {
                "route_id": route_id_for_handle(handle),
                "route_handle": handle,
                "canonical_work_id": work_id,
                "library_source_id": source_id,
                "library_refs": [source_id, *[row["body_id"] for row in body_refs]],
                "body_refs": body_refs,
                "route_packet_ref": (
                    Path(str(work["artifact_root"])) / "routing.json"
                ).as_posix(),
                "note_bindings": note_bindings,
                "note_ref": note_bindings[0]["note_ref"] if len(note_bindings) == 1 else None,
                "note_revision_state": (
                    note_bindings[0]["note_revision_state"]
                    if len(note_bindings) == 1
                    else None
                ),
                "packet_status": packet_status,
                "route_unit_legacy_state": unit.get("route_state"),
                "review_disposition": disposition,
                "review_binding_status": binding_status,
                "mechanism_signatures": list(review.get("mechanism_signatures", [])),
                "work_integration_stage": None,
                "notebook_eligibility": "eligible" if not reasons else "ineligible",
                "ineligibility_reasons": reasons,
                "boundary": (
                    "Internal historical pressure test only; no present-fact verification, "
                    "base rate, forecast resolution, publication, or action authority."
                ),
            }
            work_routes.append(route)
            routes.append(route)
        eligible_count = sum(
            row["notebook_eligibility"] == "eligible" for row in work_routes
        )
        if head_note_state != "current":
            stage = "stale"
        elif eligible_count and work.get("essay_refs"):
            stage = "fully-integrated"
        elif eligible_count:
            stage = "pressure-test-ready"
        else:
            stage = "profiled"
        for route in work_routes:
            route["work_integration_stage"] = stage
        work_summaries.append(
            {
                "canonical_work_id": work_id,
                "integration_stage": stage,
                "eligible_route_count": eligible_count,
                "essay_ref_count": len(work.get("essay_refs", [])),
            }
        )
    routes.sort(key=lambda row: row["route_id"])
    work_summaries.sort(key=lambda row: row["canonical_work_id"])
    registry_digest = hashlib.sha256(canonical_json(registry).encode("utf-8")).hexdigest()
    return {
        "schema_version": ROUTE_INDEX_SCHEMA,
        "status": "current",
        "generated_from": {
            "work_registry_ref": WORK_REGISTRY_RELATIVE_PATH.as_posix(),
            "work_registry_sha256": sha256_file(repo_root / WORK_REGISTRY_RELATIVE_PATH),
            "library_registry_ref": "archive/library/library-registry.json",
            "library_registry_sha256": registry_digest,
        },
        "route_count": len(routes),
        "eligible_route_count": sum(
            row["notebook_eligibility"] == "eligible" for row in routes
        ),
        "routes": routes,
        "works": work_summaries,
        "authority_boundary": (
            "This index governs internal route consumption only. It does not verify present "
            "facts, authorize publication, or promote provisional routes into reviewed use."
        ),
    }


def render_route_index(index: Mapping[str, Any]) -> str:
    lines = [
        "# Mira Library Operational Route Index",
        "",
        f"- Status: `{index['status']}`",
        f"- Routes: `{index['route_count']}`",
        f"- Notebook-eligible routes: `{index['eligible_route_count']}`",
        "",
        "| Route ID | Work | Library source | Review | Notes | Eligibility | Mechanism signatures |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for route in index["routes"]:
        signatures = ", ".join(f"`{item}`" for item in route["mechanism_signatures"])
        note_states = ", ".join(
            f"`{Path(item['note_ref']).name}`: `{item['note_revision_state']}`"
            for item in route["note_bindings"]
        )
        eligibility = route["notebook_eligibility"]
        if route["ineligibility_reasons"]:
            eligibility += ": " + ", ".join(route["ineligibility_reasons"])
        lines.append(
            f"| `{route['route_id']}` | `{route['canonical_work_id']}` | "
            f"`{route['library_source_id']}` | `{route['review_disposition']}` | "
            f"{note_states} | {eligibility} | {signatures} |"
        )
    lines.extend(["", "## Authority boundary", "", str(index["authority_boundary"]), ""])
    return "\n".join(lines)


def build_note_link_index(repo_root: Path) -> dict[str, Any]:
    work_registry = load_work_registry(repo_root)
    work_ids = {
        str(work.get("canonical_work_id"))
        for work in work_registry.get("works", [])
        if isinstance(work, Mapping) and work.get("canonical_work_id")
    }
    links: list[dict[str, Any]] = []
    note_sources: list[dict[str, str]] = []
    seen_notes: set[str] = set()
    for work in work_registry.get("works", []):
        if not isinstance(work, Mapping):
            continue
        source_work_id = str(work.get("canonical_work_id", ""))
        head_note_ref = revision_head_note_ref(work)
        for note_ref in normalized_note_refs(work):
            if note_ref in seen_notes:
                raise IntegrationError(f"note appears under multiple work records: {note_ref}")
            seen_notes.add(note_ref)
            note_path = repo_root / note_ref
            envelope = parse_note_envelope(note_path)
            note_sha256 = sha256_file(note_path)
            note_sources.append({"note_ref": note_ref, "note_sha256": note_sha256})
            relations = envelope.get("library_relations", [])
            if not isinstance(relations, list):
                continue
            for relation in relations:
                if not isinstance(relation, Mapping):
                    continue
                identity = {
                    "note_id": envelope.get("artifact_id"),
                    "target_type": relation.get("target_type"),
                    "target_id": relation.get("target_id"),
                    "relation_type": relation.get("relation_type"),
                    "role": relation.get("role"),
                }
                link_digest = hashlib.sha256(
                    json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest()[:20].upper()
                links.append(
                    {
                        "link_id": f"MIRA-LINK-{link_digest}",
                        "note_id": envelope.get("artifact_id"),
                        "note_ref": note_ref,
                        "note_sha256": note_sha256,
                        "note_dependency_sha256": digest_json(
                            envelope.get("dependency_snapshot", {})
                        ),
                        "source_work_id": source_work_id,
                        "target_type": relation.get("target_type"),
                        "target_id": relation.get("target_id"),
                        "relation_type": relation.get("relation_type"),
                        "role": relation.get("role"),
                        "explanation": relation.get("explanation"),
                        "passage_refs": list(relation.get("passage_refs", [])),
                        "lineage_position": "head" if note_ref == head_note_ref else "ancestor",
                    }
                )
    links.sort(key=lambda row: (str(row["target_id"]), str(row["note_ref"]), str(row["link_id"])))
    note_sources.sort(key=lambda row: row["note_ref"])
    summaries = []
    for work_id in sorted(work_ids):
        work_links = [row for row in links if row["target_id"] == work_id]
        summaries.append(
            {
                "canonical_work_id": work_id,
                "active_link_count": sum(row["lineage_position"] == "head" for row in work_links),
                "total_link_count": len(work_links),
                "cognitive_integration": "engaged" if work_links else "unlinked",
            }
        )
    return {
        "schema_version": NOTE_LINK_INDEX_SCHEMA,
        "status": "current",
        "generated_from": {
            "work_registry_ref": WORK_REGISTRY_RELATIVE_PATH.as_posix(),
            "work_registry_sha256": sha256_file(repo_root / WORK_REGISTRY_RELATIVE_PATH),
            "notes": note_sources,
        },
        "note_count": len(note_sources),
        "link_count": len(links),
        "links": links,
        "works": summaries,
        "authority_boundary": (
            "This index derives only explicitly authored note-to-work relations. It may not "
            "infer relationships from prose, create notes, or grant routing or publication authority."
        ),
    }


def render_note_link_index(index: Mapping[str, Any]) -> str:
    lines = [
        "# Mira Library Note-Link Index",
        "",
        f"- Status: `{index['status']}`",
        f"- Notes: `{index['note_count']}`",
        f"- Explicit links: `{index['link_count']}`",
        "",
        "| Link ID | Note | Target work | Relation | Role | Lineage | Explanation |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for link in index["links"]:
        lines.append(
            f"| `{link['link_id']}` | `{Path(link['note_ref']).name}` | "
            f"`{link['target_id']}` | `{link['relation_type']}` | `{link['role']}` | "
            f"`{link['lineage_position']}` | {link['explanation']} |"
        )
    lines.extend(["", "## Authority boundary", "", str(index["authority_boundary"]), ""])
    return "\n".join(lines)


def note_link_index_repository(repo_root: Path, *, check: bool) -> dict[str, Any]:
    expected_index = build_note_link_index(repo_root)
    changed: list[str] = []
    drift: list[str] = []
    for relative, expected in (
        (NOTE_LINK_INDEX_RELATIVE_PATH, canonical_json(expected_index)),
        (NOTE_LINK_INDEX_MARKDOWN_RELATIVE_PATH, render_note_link_index(expected_index)),
    ):
        path = repo_root / relative
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual == expected:
            continue
        if check:
            drift.append(relative.as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
            changed.append(relative.as_posix())
    return {
        "status": "failed" if drift else "passed",
        "check": check,
        "changed": changed,
        "drift": drift,
        "note_count": expected_index["note_count"],
        "link_count": expected_index["link_count"],
    }


def route_index_repository(
    repo_root: Path,
    registry: Mapping[str, Any],
    *,
    check: bool,
) -> dict[str, Any]:
    expected_index = build_route_index(repo_root, registry)
    expected_json = canonical_json(expected_index)
    expected_markdown = render_route_index(expected_index)
    changed: list[str] = []
    drift: list[str] = []
    for relative, expected in (
        (ROUTE_INDEX_RELATIVE_PATH, expected_json),
        (ROUTE_INDEX_MARKDOWN_RELATIVE_PATH, expected_markdown),
    ):
        path = repo_root / relative
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual == expected:
            continue
        if check:
            drift.append(relative.as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
            changed.append(relative.as_posix())
    return {
        "status": "failed" if drift else "passed",
        "check": check,
        "changed": changed,
        "drift": drift,
        "route_count": expected_index["route_count"],
        "eligible_route_count": expected_index["eligible_route_count"],
    }


def reconcile_repository(repo_root: Path, registry: Mapping[str, Any], *, write: bool = False) -> dict[str, Any]:
    manifest = load_manifest(repo_root)
    work_registry = load_work_registry(repo_root)
    sources = _source_map(registry)
    results = []
    for work in work_registry.get("works", []):
        source = sources.get(work.get("library_source_id"))
        if source is None:
            results.append({"canonical_work_id": work.get("canonical_work_id"), "state": "blocked", "reason": "missing-library-source"})
            continue
        if work.get("integration_stage") == "noted":
            work_dir = repo_root / str(work["artifact_root"])
            note_ref = revision_head_note_ref(work)
            envelope = parse_note_envelope(repo_root / note_ref)
            current = dependency_snapshot_for_note(work_dir, source, envelope)
            state = classify_note_changes(
                envelope.get("dependency_snapshot", {}), current
            )["state"]
            results.append(
                {
                    "canonical_work_id": work.get("canonical_work_id"),
                    "state": state,
                    "candidate_path": None,
                    "candidate_written": False,
                    "routing_suspended": False,
                    "notes_created": 0,
                }
            )
            continue
        results.append(reconcile_work(repo_root, work, source, write=write))
    return {
        "status": "passed" if all(row.get("state") == "current" for row in results) else "attention",
        "integration_id": manifest.get("integration_id"),
        "works": results,
        "writes_performed": any(
            row.get("candidate_written") or row.get("routing_suspended")
            for row in results
        ),
    }


def apply_reviewed_no_change_dispositions(
    repo_root: Path,
    registry: Mapping[str, Any],
    *,
    write: bool = False,
) -> dict[str, Any]:
    work_registry = load_work_registry(repo_root)
    sources = _source_map(registry)
    results: list[dict[str, Any]] = []
    for work in work_registry.get("works", []):
        if work.get("integration_stage") == "noted":
            continue
        work_id = str(work.get("canonical_work_id"))
        source = sources.get(work.get("library_source_id"))
        if source is None:
            raise IntegrationError(f"{work_id} references a missing Library source")
        work_dir = repo_root / str(work["artifact_root"])
        head_note_ref = revision_head_note_ref(work)
        note_path = repo_root / head_note_ref
        envelope = parse_note_envelope(note_path)
        current = dependency_snapshot_for_note(work_dir, source, envelope)
        result = classify_note_changes(envelope.get("dependency_snapshot", {}), current)
        if result["state"] == "current":
            results.append({
                "canonical_work_id": work_id,
                "candidate_path": None,
                "notes_migrated": 0,
                "routes_restored": [],
                "write": False,
            })
            continue
        candidates: list[tuple[str, Path, dict[str, Any]]] = []
        for candidate_path in work_dir.glob("note-revision-candidate*.json"):
            candidate = load_json(candidate_path)
            if (
                candidate.get("canonical_work_id") == work_id
                and candidate.get("predecessor_note_ref") == head_note_ref
                and candidate.get("trigger") == result
                and candidate.get("status") == "resolved"
                and candidate.get("disposition") == "reviewed-no-change"
            ):
                candidates.append((str(candidate.get("candidate_id", "")), candidate_path, candidate))
        if not candidates:
            raise IntegrationError(
                f"{work_id} lacks a matching resolved reviewed-no-change candidate"
            )
        _, candidate_path, candidate = max(candidates, key=lambda row: row[0])
        route_states = candidate.get("suspended_route_states", {})
        if not isinstance(route_states, Mapping):
            raise IntegrationError(f"{work_id} candidate has invalid suspended_route_states")
        routing_path = work_dir / "routing.json"
        routing = load_json(routing_path)
        restored_handles: list[str] = []
        for unit in routing.get("route_units", []):
            if not isinstance(unit, dict):
                continue
            handle = str(unit.get("handle", ""))
            if handle in route_states:
                unit["route_state"] = route_states[handle]
                restored_handles.append(handle)
        if set(restored_handles) != set(route_states):
            raise IntegrationError(f"{work_id} candidate route handles do not match routing packet")
        routing["note_revision_state"] = "current"
        if write:
            routing_path.write_text(canonical_json(routing), encoding="utf-8")
            (work_dir / "routing.md").write_text(render_routing(routing), encoding="utf-8")
            linked_digests = linked_artifact_digests(work_dir)
            migration_envelope = parse_note_envelope(note_path)
            migration_envelope["dependency_snapshot"] = current
            migration_envelope["linked_artifact_digests"] = linked_digests
            write_note_envelope(note_path, migration_envelope)
        results.append({
            "canonical_work_id": work_id,
            "candidate_path": candidate_path.relative_to(repo_root).as_posix(),
            "notes_migrated": 1 if write else 0,
            "routes_restored": restored_handles if write else [],
            "write": write,
        })
    return {
        "status": "passed",
        "integration_id": load_manifest(repo_root).get("integration_id"),
        "works": results,
        "writes_performed": any(row.get("write") for row in results),
    }


def validate_pilot_contract(repo_root: Path, registry: Mapping[str, Any]) -> list[str]:
    root = repo_root / INTEGRATION_RELATIVE_ROOT
    if not root.exists():
        return []
    failures: list[str] = []
    try:
        manifest = load_pilot_manifest(repo_root)
    except IntegrationError as error:
        return [str(error)]
    failures.extend(_required(manifest, ("schema_version", "pilot_id", "status", "works", "essay_artifacts_created"), "integration manifest"))
    if manifest.get("schema_version") != PILOT_MANIFEST_SCHEMA:
        failures.append(f"integration manifest has invalid schema_version: {manifest.get('schema_version')}")
    if manifest.get("pilot_id") != PILOT_ID:
        failures.append(f"integration manifest has unexpected pilot_id: {manifest.get('pilot_id')}")
    works = manifest.get("works", [])
    if not isinstance(works, list) or len(works) != EXPECTED_WORKS:
        failures.append(f"integration pilot must contain exactly {EXPECTED_WORKS} works")
        return failures
    if manifest.get("essay_artifacts_created") != 0:
        failures.append("integration pilot must create zero essay artifacts")
    sources = _source_map(registry)
    known_work_ids = {
        str(row.get("canonical_work_id"))
        for row in works
        if isinstance(row, Mapping) and row.get("canonical_work_id")
    }
    work_ids: set[str] = set()
    topic_ids: set[str] = set()
    total_topics = 0
    for work in works:
        work_id = work.get("canonical_work_id")
        label = str(work_id or "integration work")
        if work_id in work_ids:
            failures.append(f"duplicate canonical_work_id: {work_id}")
        work_ids.add(work_id)
        source_id = work.get("library_source_id")
        source = sources.get(source_id)
        if source is None:
            failures.append(f"{label} references missing library source: {source_id}")
            continue
        work_dir = repo_root / work.get("artifact_root", "")
        records: dict[str, dict[str, Any]] = {}
        for json_name, markdown_name in GENERATED_MARKDOWN.items():
            json_path = work_dir / json_name
            markdown_path = work_dir / markdown_name
            try:
                record = load_json(json_path)
                records[json_name] = record
            except IntegrationError as error:
                failures.append(str(error))
                continue
            if record.get("canonical_work_id") != work_id:
                failures.append(f"{label} {json_name} canonical_work_id mismatch")
            if record.get("library_source_id") != source_id:
                failures.append(f"{label} {json_name} library_source_id mismatch")
            try:
                expected = render_record(json_path, record)
                actual = markdown_path.read_text(encoding="utf-8")
                if actual != expected:
                    failures.append(f"generated Markdown drift: {markdown_path.relative_to(repo_root).as_posix()}")
            except (IntegrationError, FileNotFoundError, KeyError, TypeError) as error:
                failures.append(f"cannot render {label} {json_name}: {error}")
        profile = records.get("profile.json", {})
        coverage = records.get("coverage.json", {})
        routing = records.get("routing.json", {})
        topics = records.get("essay-topics.json", {})
        if profile.get("schema_version") != PROFILE_SCHEMA:
            failures.append(f"{label} profile schema mismatch")
        if profile.get("knowledge_basis") != "knowledge-seeded" or profile.get("external_research_used") is not False:
            failures.append(f"{label} profile must be knowledge-seeded without external research")
        if coverage.get("schema_version") != COVERAGE_SCHEMA:
            failures.append(f"{label} coverage schema mismatch")
        if coverage.get("external_research_used") is not False:
            failures.append(f"{label} coverage must record no external research used")
        if routing.get("schema_version") != ROUTING_SCHEMA:
            failures.append(f"{label} routing schema mismatch")
        if topics.get("schema_version") != TOPICS_SCHEMA:
            failures.append(f"{label} topic schema mismatch")
        topic_rows = topics.get("topics", [])
        if not isinstance(topic_rows, list) or [row.get("rank") for row in topic_rows] != [1, 2, 3]:
            failures.append(f"{label} must contain exactly three topics ranked 1, 2, 3")
        else:
            total_topics += len(topic_rows)
            for row in topic_rows:
                topic_id = row.get("topic_contract_id")
                if topic_id in topic_ids:
                    failures.append(f"duplicate topic_contract_id: {topic_id}")
                topic_ids.add(topic_id)
                if not row.get("do_not_draft_yet"):
                    failures.append(f"{topic_id} lacks do_not_draft_yet")
        if not isinstance(topics.get("essay_refs"), list):
            failures.append(f"{label} essay_refs must be an array")
        if topics.get("essay_artifacts_created") != 0:
            failures.append(f"{label} created an essay artifact")
        body_map = _body_map(source)
        required_mediation_fields = {
            "mediation_type", "translator_status", "editor_status", "mediation"
        }
        for body_id, body in body_map.items():
            missing_mediation_fields = sorted(required_mediation_fields - set(body))
            if missing_mediation_fields:
                failures.append(
                    f"{label} body {body_id} lacks mediation seal fields: "
                    + ", ".join(missing_mediation_fields)
                )
        profile_anchors = profile.get("textual_basis", {}).get("passage_anchors", [])
        anchor_digests = {
            str(row.get("passage_id")): row.get("raw_span_sha256")
            for row in profile_anchors
            if isinstance(row, Mapping) and row.get("passage_id")
        }
        for body_ref in profile.get("textual_basis", {}).get("body_refs", []):
            body = body_map.get(body_ref.get("body_id"))
            if body is None:
                failures.append(f"{label} references missing body: {body_ref.get('body_id')}")
            elif body.get("text_sha256") != body_ref.get("text_sha256"):
                failures.append(f"{label} body digest mismatch: {body_ref.get('body_id')}")
        head_note_ref = revision_head_note_ref(work)
        note_path = repo_root / head_note_ref
        try:
            envelope = parse_note_envelope(note_path)
            if envelope.get("schema_version") != NOTE_SCHEMA_V2:
                failures.append(f"{label} note schema mismatch")
            if envelope.get("canonical_work_id") != work_id:
                failures.append(f"{label} note canonical_work_id mismatch")
            if envelope.get("status") != "provisional":
                failures.append(f"{label} note must remain provisional")
            if envelope.get("interpretive_basis") not in {"admitted-source-body", "source-readiness-only"}:
                failures.append(f"{label} note must declare a source-bounded interpretive_basis")
            dependency_keys = set(envelope.get("dependency_snapshot", {}))
            expected_dependency_keys = {
                "source_identity_digest", "body_digests", "body_states", "passage_digests"
            }
            if dependency_keys != expected_dependency_keys:
                failures.append(f"{label} note interpretive dependency keys are not source-only")
            note_body_states = envelope.get("dependency_snapshot", {}).get("body_states", {})
            if isinstance(note_body_states, Mapping):
                for body_id, body_state in note_body_states.items():
                    if not isinstance(body_state, Mapping):
                        failures.append(f"{label} note body state must be an object: {body_id}")
                        continue
                    canonical_body = body_map.get(str(body_id))
                    expected_mediation = mediation_dependency_projection(
                        canonical_body.get("mediation") if canonical_body else None
                    )
                    if body_state.get("mediation") != expected_mediation:
                        failures.append(f"{label} note mediation dependency projection mismatch: {body_id}")
                    note_layers = body_state.get("mediation", {}).get("primary_path", []) if isinstance(body_state.get("mediation"), Mapping) else []
                    if any(
                        isinstance(layer, Mapping)
                        and layer.get("revision_relevance") == "carrier-only"
                        for layer in note_layers
                    ):
                        failures.append(f"{label} note dependency includes a carrier-only mediation layer: {body_id}")
            linked_keys = set(envelope.get("linked_artifact_digests", {}))
            expected_linked_keys = {
                "profile_sha256", "coverage_sha256", "routing_sha256", "topics_sha256"
            }
            if linked_keys != expected_linked_keys:
                failures.append(f"{label} note linked artifact digest keys are incomplete")
            note_passages = envelope.get("dependency_snapshot", {}).get("passage_digests", {})
            if envelope.get("interpretive_basis") == "admitted-source-body":
                if not anchor_digests:
                    failures.append(f"{label} source-direct note requires passage anchors")
                if note_passages != anchor_digests:
                    failures.append(f"{label} note passage dependencies do not match the profile anchors")
            elif note_passages:
                failures.append(f"{label} source-readiness-only note may not claim passage dependencies")
            predecessor_ref = envelope.get("predecessor_note_ref")
            if predecessor_ref and not (repo_root / predecessor_ref).is_file():
                failures.append(f"{label} note predecessor is missing: {predecessor_ref}")
        except (IntegrationError, FileNotFoundError) as error:
            failures.append(str(error))
        note_refs = normalized_note_refs(work)
        for note_ref in note_refs:
            if not note_ref:
                continue
            try:
                note_text = (repo_root / note_ref).read_text(encoding="utf-8")
                normalized_note = note_text.casefold()
                prohibited_names = ("civilization memory", "civilization-memory", "civmem")
                if any(name in normalized_note for name in prohibited_names):
                    failures.append(f"{label} integration note mentions a prohibited auxiliary corpus: {note_ref}")
                note_envelope = parse_note_envelope(repo_root / note_ref)
                if note_envelope.get("schema_version") != NOTE_SCHEMA_V2:
                    failures.append(f"{label} integration note schema mismatch: {note_ref}")
                if note_envelope.get("canonical_work_id") != work_id:
                    failures.append(f"{label} integration note canonical_work_id mismatch: {note_ref}")
                failures.extend(
                    validate_library_relations(
                        note_envelope, known_work_ids, label=f"{label} integration note {note_ref}"
                    )
                )
                if not any(
                    relation.get("relation_type") == "interprets"
                    and relation.get("role") == "focal"
                    for relation in library_relations_for_work(note_envelope, str(work_id))
                ):
                    failures.append(
                        f"{label} integration note lacks a focal interpretation relation: {note_ref}"
                    )
                if note_envelope.get("interpretive_basis") not in {"admitted-source-body", "source-readiness-only"}:
                    failures.append(f"{label} integration note lacks a source-bounded interpretive_basis: {note_ref}")
                if note_envelope.get("interpretive_basis") == "admitted-source-body":
                    note_passages = note_envelope.get("dependency_snapshot", {}).get("passage_digests", {})
                    if note_passages != anchor_digests:
                        failures.append(f"{label} integration note lacks current source anchors: {note_ref}")
            except (IntegrationError, FileNotFoundError) as error:
                failures.append(str(error))
        candidate_paths = sorted(work_dir.glob("note-revision-candidate*.json"))
        current_note_ref = head_note_ref
        try:
            current_note = parse_note_envelope(repo_root / str(current_note_ref))
            current_candidate_ref = current_note.get("revision_candidate_ref")
            if current_candidate_ref:
                current_candidate_path = repo_root / str(current_candidate_ref)
                current_candidate = load_json(current_candidate_path)
                if current_candidate.get("successor_note_ref") != current_note_ref:
                    failures.append(
                        f"{label} current note is not the successor of its revision candidate"
                    )
        except (IntegrationError, FileNotFoundError) as error:
            failures.append(str(error))
        for candidate_path in candidate_paths:
            try:
                candidate = load_json(candidate_path)
                failures.extend(validate_revision_candidate(candidate))
                if candidate.get("canonical_work_id") != work_id:
                    failures.append(f"{label} revision candidate canonical_work_id mismatch")
                predecessor_ref = candidate.get("predecessor_note_ref")
                if predecessor_ref and not (repo_root / predecessor_ref).is_file():
                    failures.append(f"{label} revision candidate predecessor is missing: {predecessor_ref}")
                if candidate.get("status") == "resolved" and candidate.get("disposition") in {"addendum", "revised"}:
                    successor_ref = candidate.get("successor_note_ref")
                    if not successor_ref:
                        failures.append(f"{label} resolved {candidate.get('disposition')} candidate requires successor_note_ref")
                    elif not (repo_root / successor_ref).is_file():
                        failures.append(f"{label} revision candidate successor is missing: {successor_ref}")
                    else:
                        successor = parse_note_envelope(repo_root / successor_ref)
                        if successor.get("predecessor_note_ref") != predecessor_ref:
                            failures.append(f"{label} successor note does not preserve candidate predecessor lineage")
                        expected_candidate_ref = candidate_path.relative_to(repo_root).as_posix()
                        if successor.get("revision_candidate_ref") != expected_candidate_ref:
                            failures.append(f"{label} successor note does not link its revision candidate")
            except (IntegrationError, FileNotFoundError) as error:
                failures.append(str(error))
    if total_topics != EXPECTED_TOPICS:
        failures.append(f"integration pilot must contain exactly {EXPECTED_TOPICS} topics")
    try:
        reconciliation = reconcile_repository(repo_root, registry, write=False)
        for row in reconciliation["works"]:
            if row.get("state") == "revision-due":
                work = next(item for item in works if item.get("canonical_work_id") == row.get("canonical_work_id"))
                routing = load_json(repo_root / work["artifact_root"] / "routing.json")
                if any(unit.get("route_state") != "suspended-due-to-note-revision" for unit in routing.get("route_units", [])):
                    failures.append(f"{row.get('canonical_work_id')} is revision-due but routing is not suspended")
    except (IntegrationError, FileNotFoundError) as error:
        failures.append(str(error))
    return failures


def validate_living_contract(repo_root: Path, registry: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    try:
        manifest = load_manifest(repo_root)
        work_registry = load_work_registry(repo_root)
    except IntegrationError as error:
        return [str(error)]
    failures.extend(
        _required(
            manifest,
            (
                "schema_version",
                "integration_id",
                "status",
                "historical_snapshot",
                "constellation",
                "works",
                "authority_boundary",
            ),
            "living integration manifest",
        )
    )
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        failures.append(
            f"living integration manifest has invalid schema_version: {manifest.get('schema_version')}"
        )
    works = manifest.get("works", [])
    if not isinstance(works, list) or len(works) != 8:
        return [*failures, "living integration manifest must contain exactly eight works"]
    if manifest.get("work_count") != 8:
        failures.append("living integration manifest work_count must equal eight")
    historical = manifest.get("historical_snapshot", {})
    if not isinstance(historical, Mapping):
        failures.append("living integration manifest historical_snapshot must be an object")
    else:
        manifest_ref = str(historical.get("manifest_ref", ""))
        manifest_path = repo_root / manifest_ref
        if manifest_ref != (INTEGRATION_RELATIVE_ROOT / MANIFEST_NAME).as_posix():
            failures.append("living integration manifest must reference the frozen pilot manifest")
        elif not manifest_path.is_file():
            failures.append(f"missing frozen pilot manifest: {manifest_ref}")
        elif historical.get("manifest_sha256") != sha256_file(manifest_path):
            failures.append("frozen pilot manifest digest changed")
        note_digests = historical.get("note_sha256", {})
        if not isinstance(note_digests, Mapping) or len(note_digests) != 8:
            failures.append("historical snapshot must seal exactly eight predecessor notes")
        else:
            for note_ref, expected in note_digests.items():
                note_path = repo_root / str(note_ref)
                if not note_path.is_file():
                    failures.append(f"missing historical predecessor note: {note_ref}")
                elif sha256_file(note_path) != expected:
                    failures.append(f"historical predecessor note changed: {note_ref}")
    registry_works = {
        str(row.get("canonical_work_id")): row
        for row in work_registry.get("works", [])
        if isinstance(row, Mapping) and row.get("canonical_work_id")
    }
    known_work_ids = {
        str(row.get("canonical_work_id"))
        for row in works
        if isinstance(row, Mapping) and row.get("canonical_work_id")
    }
    sources = _source_map(registry)
    head_notes: dict[str, tuple[str, dict[str, Any], str]] = {}
    noted_count = 0
    routed_count = 0
    for work in works:
        if not isinstance(work, Mapping):
            failures.append("living integration work must be an object")
            continue
        work_id = str(work.get("canonical_work_id", ""))
        record = registry_works.get(work_id)
        if record is None:
            failures.append(f"living work is absent from work registry: {work_id}")
            continue
        stage = str(work.get("integration_stage", ""))
        if stage == "noted":
            noted_count += 1
        elif stage == "routed":
            routed_count += 1
        else:
            failures.append(f"{work_id} has invalid living integration stage: {stage}")
        work_dir = repo_root / str(work.get("artifact_root", ""))
        source_id = str(work.get("library_source_id", ""))
        source = sources.get(source_id)
        if source is None:
            failures.append(f"{work_id} references missing Library source: {source_id}")
            continue
        try:
            profile = load_json(work_dir / "profile.json")
        except IntegrationError as error:
            failures.append(str(error))
            continue
        if profile.get("schema_version") != PROFILE_SCHEMA:
            failures.append(f"{work_id} profile schema mismatch")
        if profile.get("canonical_work_id") != work_id:
            failures.append(f"{work_id} profile canonical_work_id mismatch")
        if profile.get("library_source_id") != source_id:
            failures.append(f"{work_id} profile library_source_id mismatch")
        body_map = _body_map(source)
        for body_ref in profile.get("textual_basis", {}).get("body_refs", []):
            if not isinstance(body_ref, Mapping):
                failures.append(f"{work_id} profile body_ref must be an object")
                continue
            body_id = str(body_ref.get("body_id", ""))
            body = body_map.get(body_id)
            if body is None:
                failures.append(f"{work_id} references missing body: {body_id}")
            elif body.get("text_sha256") != body_ref.get("text_sha256"):
                failures.append(f"{work_id} body digest mismatch: {body_id}")
        head_note_ref = revision_head_note_ref(record)
        try:
            envelope = parse_note_envelope(repo_root / head_note_ref)
        except (IntegrationError, FileNotFoundError) as error:
            failures.append(str(error))
            continue
        head_notes[work_id] = (head_note_ref, envelope, stage)
        failures.extend(validate_note_template(repo_root / head_note_ref, envelope))
        if envelope.get("schema_version") != NOTE_SCHEMA:
            failures.append(f"{work_id} living revision head must use {NOTE_SCHEMA}")
        if envelope.get("canonical_work_id") != work_id:
            failures.append(f"{work_id} note canonical_work_id mismatch")
        if envelope.get("library_source_id") != source_id:
            failures.append(f"{work_id} note library_source_id mismatch")
        failures.extend(
            validate_library_relations(
                envelope,
                known_work_ids,
                label=f"{work_id} living revision head",
            )
        )
        own_focal = [
            row
            for row in library_relations_for_work(envelope, work_id)
            if row.get("relation_type") == "interprets" and row.get("role") == "focal"
        ]
        if len(own_focal) != 1:
            failures.append(f"{work_id} requires exactly one focal interpretation relation")
        expected_dependencies = dependency_snapshot_for_note(work_dir, source, envelope)
        if envelope.get("dependency_snapshot") != expected_dependencies:
            failures.append(f"{work_id} note dependency snapshot is not current")
        expected_links = linked_artifact_digests(work_dir, integration_stage=stage)
        if envelope.get("linked_artifact_digests") != expected_links:
            failures.append(f"{work_id} note linked artifact digests are not current")
    if noted_count != 3 or routed_count != 5:
        failures.append("living integration must contain five routed and three noted works")
    constellation = manifest.get("constellation", {})
    member_ids = (
        set(constellation.get("member_work_ids", []))
        if isinstance(constellation, Mapping)
        else set()
    )
    if len(member_ids) != 3 or not member_ids <= known_work_ids:
        failures.append("living constellation must name exactly three known works")
    for work_id in sorted(member_ids):
        note_ref, envelope, stage = head_notes.get(work_id, ("", {}, ""))
        if stage != "noted":
            failures.append(f"constellation member must remain noted: {work_id}")
            continue
        other_ids = member_ids - {work_id}
        comparative = [
            row
            for row in envelope.get("library_relations", [])
            if isinstance(row, Mapping)
            and row.get("relation_type") == "connects"
            and row.get("role") == "comparative"
        ]
        if {str(row.get("target_id")) for row in comparative} != other_ids:
            failures.append(f"{work_id} must connect comparatively to both companions")
        for row in comparative:
            if row.get("passage_refs"):
                failures.append(f"{work_id} comparative constellation edges may not cite passages")
            explanation = str(row.get("explanation", "")).casefold()
            if "analysis-pending" not in explanation or "curatorial" not in explanation:
                failures.append(
                    f"{work_id} comparative edge must declare curatorial analysis-pending status"
                )
        own_focal = [
            row
            for row in envelope.get("library_relations", [])
            if isinstance(row, Mapping)
            and row.get("target_id") == work_id
            and row.get("relation_type") == "interprets"
            and row.get("role") == "focal"
        ]
        if not own_focal or not own_focal[0].get("passage_refs"):
            failures.append(f"{work_id} focal relation must cite source-bound passages")
        note_text = (repo_root / note_ref).read_text(encoding="utf-8") if note_ref else ""
        for other_id in other_ids:
            companion_ref = head_notes.get(other_id, ("", {}, ""))[0]
            if not companion_ref or companion_ref not in note_text:
                failures.append(f"{work_id} note lacks visible companion link: {other_id}")
    return failures


def validate_repository(repo_root: Path, registry: Mapping[str, Any]) -> list[str]:
    if not (repo_root / INTEGRATION_RELATIVE_ROOT).exists():
        return []
    failures = validate_schema_contract(repo_root)
    failures.extend(validate_pilot_contract(repo_root, registry))
    failures.extend(validate_living_contract(repo_root, registry))
    failures.extend(validate_work_registry(repo_root, registry))
    if failures:
        return failures
    route_result = route_index_repository(repo_root, registry, check=True)
    failures.extend(
        f"operational route index drift: {path}" for path in route_result["drift"]
    )
    link_result = note_link_index_repository(repo_root, check=True)
    failures.extend(
        f"note-link index drift: {path}" for path in link_result["drift"]
    )
    return failures


def render_repository(repo_root: Path, *, check: bool) -> dict[str, Any]:
    manifest = load_manifest(repo_root)
    changed: list[str] = []
    drift: list[str] = []
    for work in manifest["works"]:
        work_dir = repo_root / work["artifact_root"]
        generated = (
            {"profile.json": "profile.md"}
            if work.get("integration_stage") == "noted"
            else GENERATED_MARKDOWN
        )
        for json_name, markdown_name in generated.items():
            json_path = work_dir / json_name
            markdown_path = work_dir / markdown_name
            expected = render_record(json_path, load_json(json_path))
            actual = markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else None
            if actual != expected:
                relative = markdown_path.relative_to(repo_root).as_posix()
                if check:
                    drift.append(relative)
                else:
                    markdown_path.write_text(expected, encoding="utf-8")
                    changed.append(relative)
    route_result = route_index_repository(
        repo_root, load_library_registry(repo_root), check=check
    )
    changed.extend(route_result["changed"])
    drift.extend(route_result["drift"])
    link_result = note_link_index_repository(repo_root, check=check)
    changed.extend(link_result["changed"])
    drift.extend(link_result["drift"])
    return {
        "status": "failed" if drift else "passed",
        "check": check,
        "changed": changed,
        "drift": drift,
    }

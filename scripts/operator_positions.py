from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from archive_membership import source_reference_available
from repository_paths import canonical_repository_path, resolve_repository_path


REPO_ROOT = Path(__file__).resolve().parent.parent
TRACK_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "operator-positions"
LEDGER_PATH = TRACK_ROOT / "strategic-judgment-ledger.json"
GRAPH_PATH = TRACK_ROOT / "strategic-judgment-graph.json"
REPORT_PATH = TRACK_ROOT / "strategic-judgment-ledger.md"
CANDIDATE_ROOT = TRACK_ROOT / ".candidates"

DIMENSIONS = (
    "thesis_precision",
    "internal_consistency",
    "mechanism_completeness",
    "scope_and_qualification_discipline",
    "counterargument_integration",
    "explanatory_compression",
)
RELATIONS = {
    "reinforcement",
    "direct_disagreement",
    "conditional_divergence",
    "mechanism_disagreement",
    "timing_divergence",
    "non_engagement",
}
REVISION_RELATIONS = {"initial", "refinement", "revision", "contradiction", "unchanged_review"}
REQUIRED_POSITION_FIELDS = (
    "thesis",
    "epistemic_layers",
    "mechanism",
    "implications",
    "horizon",
    "confidence",
    "falsifier",
    "change_conditions",
    "qualifications",
    "strongest_counterarguments",
)
EPISTEMIC_LAYER_FIELDS = (
    "layer_id",
    "label",
    "layer_type",
    "claim",
    "confidence",
    "evidence_standard",
    "falsifier_status",
    "falsifier_or_limitation",
)
EPISTEMIC_LAYER_TYPES = {
    "empirical_hypothesis",
    "actor_model_premise",
    "conditional_forecast",
    "normative_judgment",
}
FALSIFIER_STATUSES = {
    "testable",
    "partially_testable",
    "not_empirically_falsifiable",
}
BOUNDARY = (
    "Persuasive coherence does not establish factual truth, evidence "
    "independence, or predictive accuracy."
)
JOURNAL_KINDS = {
    "daily_reflection",
    "architecture_decision",
    "position_refinement",
    "position_challenge",
    "unchanged_review",
}
POSITION_EFFECTS = {
    "context",
    "book_structure",
    "chronicle_structure",
    "ledger_structure",
    "candidate_refinement",
    "candidate_position",
    "refinement",
    "revision",
    "contradiction",
    "unchanged",
}
LOOP_STATUSES = {"closed", "open_test", "partial", "no_change"}
LEARNING_LOOP_FIELDS = (
    "prior_model",
    "pressure",
    "update",
    "future_test",
    "inherited_practice",
    "loop_status",
)


class LedgerError(ValueError):
    pass


def load_ledger(path: Path = LEDGER_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_ledger(data: dict[str, Any], path: Path = LEDGER_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _json_text(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _layer_node_id(version_id: str, layer_id: str) -> str:
    return f"layer:{version_id}:{layer_id}"


def build_graph(data: dict[str, Any]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[str, dict[str, Any]] = {}

    def add_node(node_id: str, node_type: str, **attributes: Any) -> None:
        if node_id in nodes:
            return
        nodes[node_id] = {
            "node_id": node_id,
            "node_type": node_type,
            **deepcopy(attributes),
        }

    def add_edge(
        edge_type: str,
        source: str,
        target: str,
        *,
        edge_suffix: str = "",
        **attributes: Any,
    ) -> None:
        edge_id = f"edge:{edge_type}:{source}:{target}{edge_suffix}"
        if edge_id in edges:
            raise LedgerError(f"duplicate graph edge {edge_id}")
        edges[edge_id] = {
            "edge_id": edge_id,
            "edge_type": edge_type,
            "source": source,
            "target": target,
            **deepcopy(attributes),
        }

    root_id = "ledger:strategic-judgment"
    add_node(root_id, "judgment_ledger", **data["ledger"])
    current_versions: dict[str, str] = {}

    for position in data.get("positions", []):
        position_id = position["position_id"]
        add_node(
            position_id,
            "position",
            object_slug=position["object_slug"],
            object_label=position["object_label"],
        )
        add_edge("contains_position", root_id, position_id)
        current_versions[position_id] = latest_version(position)["version_id"]
        for version in position["versions"]:
            version_id = version["version_id"]
            position_fields = {
                key: deepcopy(value)
                for key, value in version["position"].items()
                if key != "epistemic_layers"
            }
            add_node(
                version_id,
                "position_version",
                position_id=position_id,
                version_number=version["version_number"],
                relation_to_previous=version["relation_to_previous"],
                approval=version["approval"],
                provenance=version["provenance"],
                position=position_fields,
            )
            add_edge("has_version", position_id, version_id)
            previous_id = version.get("previous_version_id")
            if previous_id:
                add_edge(
                    "revises_version",
                    version_id,
                    previous_id,
                    relation=version["relation_to_previous"],
                )

            trigger_id = f"trigger:{version_id}"
            add_node(
                trigger_id,
                "review_trigger",
                version_id=version_id,
                **version["review_trigger"],
            )
            add_edge("reviewed_by", version_id, trigger_id)

            for layer in version["position"]["epistemic_layers"]:
                layer_node_id = _layer_node_id(version_id, layer["layer_id"])
                add_node(
                    layer_node_id,
                    "epistemic_layer",
                    position_id=position_id,
                    version_id=version_id,
                    **layer,
                )
                add_edge("has_layer", version_id, layer_node_id)

            comparator_set = version["comparator_set"]
            for comparator in comparator_set.get("included", []):
                voice_id = f"voice:{comparator['voice_slug']}"
                add_node(
                    voice_id,
                    "repo_voice",
                    voice_slug=comparator["voice_slug"],
                    display_name=comparator["display_name"],
                )
                for layer_id in comparator["engaged_layer_ids"]:
                    add_edge(
                        "engages_layer",
                        voice_id,
                        _layer_node_id(version_id, layer_id),
                        version_id=version_id,
                        comparator_status=comparator_set["status"],
                        orthogonality_axis=comparator["orthogonality_axis"],
                        inclusion_rationale=comparator["inclusion_rationale"],
                    )
                for evidence_index, evidence in enumerate(comparator["evidence"], start=1):
                    evidence_id = (
                        f"evidence:{version_id}:{comparator['voice_slug']}:{evidence_index:02d}"
                    )
                    add_node(
                        evidence_id,
                        "evidence_excerpt",
                        version_id=version_id,
                        voice_slug=comparator["voice_slug"],
                        **evidence,
                    )
                    add_edge("attributed_to", evidence_id, voice_id)
                    for layer_id in evidence["layer_ids"]:
                        add_edge(
                            "supports_engagement",
                            evidence_id,
                            _layer_node_id(version_id, layer_id),
                        )

            for excluded in comparator_set.get("excluded", []):
                voice_id = f"voice:{excluded['voice_slug']}"
                add_node(
                    voice_id,
                    "repo_voice",
                    voice_slug=excluded["voice_slug"],
                    display_name=excluded["display_name"],
                )
                for layer_id in excluded["target_layer_ids"]:
                    add_edge(
                        "excluded_from_layer",
                        voice_id,
                        _layer_node_id(version_id, layer_id),
                        version_id=version_id,
                        reason=excluded["reason"],
                        evidence_count=excluded["evidence_count"],
                        source_count=excluded["source_count"],
                    )

            comparison = version["comparison"]
            for profile in comparison.get("profiles", []):
                subject = profile["subject"]
                subject_id = "operator:primary" if subject == "operator" else f"voice:{subject}"
                if subject == "operator":
                    add_node(subject_id, "operator", display_name=profile["display_name"])
                else:
                    add_node(
                        subject_id,
                        "repo_voice",
                        voice_slug=subject,
                        display_name=profile["display_name"],
                    )
                profile_id = f"profile:{version_id}:{subject}:{profile['layer_id']}"
                add_node(
                    profile_id,
                    "coherence_profile",
                    version_id=version_id,
                    subject=subject,
                    display_name=profile["display_name"],
                    layer_id=profile["layer_id"],
                    dimensions=profile["dimensions"],
                    comparison_status=comparison["status"],
                )
                add_edge("has_profile", subject_id, profile_id)
                add_edge(
                    "profiles_layer",
                    profile_id,
                    _layer_node_id(version_id, profile["layer_id"]),
                )

            for relation in comparison.get("relations", []):
                add_edge(
                    "relates_to_layer",
                    f"voice:{relation['voice_slug']}",
                    _layer_node_id(version_id, relation["layer_id"]),
                    version_id=version_id,
                    relation=relation["relation"],
                    rationale=relation["rationale"],
                )
            for role in ("closest_affinity", "strongest_corrective"):
                finding = comparison.get("findings", {}).get(role)
                if finding:
                    add_edge(
                        "comparison_finding",
                        f"voice:{finding['voice_slug']}",
                        _layer_node_id(version_id, finding["layer_id"]),
                        edge_suffix=f":{role}",
                        version_id=version_id,
                        role=role,
                        rationale=finding["rationale"],
                    )

    for entry in data.get("journal_entries", []):
        entry_id = entry["entry_id"]
        add_node(entry_id, "journal_event", **entry)
        add_edge("contains_event", root_id, entry_id)
        for version_id in entry["linked_position_versions"]:
            add_edge("event_links_version", entry_id, version_id)
        for pressure in entry["voice_pressure"]:
            voice_id = f"voice:{pressure['voice_slug']}"
            add_node(
                voice_id,
                "repo_voice",
                voice_slug=pressure["voice_slug"],
                display_name=pressure["voice_slug"],
            )
            add_edge(
                "pressures_event",
                voice_id,
                entry_id,
                relation=pressure["relation"],
            )

    ordered_nodes = sorted(nodes.values(), key=lambda item: item["node_id"])
    ordered_edges = sorted(edges.values(), key=lambda item: item["edge_id"])
    by_type: dict[str, list[str]] = {}
    for node in ordered_nodes:
        by_type.setdefault(node["node_type"], []).append(node["node_id"])
    return {
        "schema": "strategic-judgment-graph-v1",
        "source": {
            "ledger_path": LEDGER_PATH.relative_to(REPO_ROOT).as_posix(),
            "ledger_schema": data["schema"],
        },
        "nodes": ordered_nodes,
        "edges": ordered_edges,
        "indexes": {
            "current_version_by_position": current_versions,
            "nodes_by_type": by_type,
        },
    }


def validate_graph(graph: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if graph.get("schema") != "strategic-judgment-graph-v1":
        errors.append("strategic judgment graph: invalid schema")
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    node_ids = [node.get("node_id") for node in nodes]
    edge_ids = [edge.get("edge_id") for edge in edges]
    if len(node_ids) != len(set(node_ids)):
        errors.append("strategic judgment graph: duplicate node IDs")
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("strategic judgment graph: duplicate edge IDs")
    if node_ids != sorted(node_ids) or edge_ids != sorted(edge_ids):
        errors.append("strategic judgment graph: nondeterministic ordering")
    known_nodes = set(node_ids)
    for edge in edges:
        if edge.get("source") not in known_nodes or edge.get("target") not in known_nodes:
            errors.append(f"strategic judgment graph: dangling edge {edge.get('edge_id')}")
    if "raw_text" in set(_walk_keys(graph)):
        errors.append("strategic judgment graph: raw text leaked into projection")
    return errors


def write_artifacts(data: dict[str, Any], *, write_source: bool = True) -> None:
    if write_source:
        write_ledger(data)
    GRAPH_PATH.write_text(_json_text(build_graph(data)), encoding="utf-8")
    REPORT_PATH.write_text(render_report(data), encoding="utf-8")


def latest_version(position: dict[str, Any]) -> dict[str, Any]:
    return position["versions"][-1]


def find_position(data: dict[str, Any], position_id: str) -> dict[str, Any]:
    matches = [item for item in data.get("positions", []) if item.get("position_id") == position_id]
    if len(matches) != 1:
        raise LedgerError(f"expected exactly one position {position_id}")
    return matches[0]


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _validate_evidence_ref(ref: dict[str, Any], errors: list[str], context: str) -> None:
    path_value = ref.get("path")
    if not isinstance(path_value, str) or not path_value:
        errors.append(f"{context}: evidence reference needs a path")
        return
    canonical_path = canonical_repository_path(path_value)
    evidence_path = resolve_repository_path(REPO_ROOT, path_value)
    if not evidence_path.is_file() and not (
        canonical_path.startswith("archive/sources/geopolitics/sources/")
        and source_reference_available(REPO_ROOT, path_value)
    ):
        errors.append(f"{context}: broken evidence path {path_value}")
    start, end = ref.get("line_start"), ref.get("line_end")
    if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
        errors.append(f"{context}: invalid evidence line range")
    if not str(ref.get("excerpt", "")).strip():
        errors.append(f"{context}: evidence reference needs a bounded excerpt")


def validate_data(data: dict[str, Any], *, check_report: bool = False) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "strategic-judgment-ledger-v1":
        errors.append("strategic judgment ledger: invalid schema")
    if data.get("boundary") != BOUNDARY:
        errors.append("strategic judgment ledger: boundary statement drift")
    if tuple(data.get("dimensions", ())) != DIMENSIONS:
        errors.append("strategic judgment ledger: dimension contract drift")
    ledger = data.get("ledger", {})
    classical = ledger.get("classical_definition", {})
    if (
        ledger.get("title") != "Strategic Judgment Ledger"
        or ledger.get("short_name") != "the Judgment Ledger"
        or ledger.get("model") != "graph-indexed immutable event ledger"
        or ledger.get("primary_interface") != "typed graph and query views"
        or classical.get("name") != "living hypomnema and private agora"
        or not classical.get("definition")
        or not classical.get("dialogue")
        or not classical.get("purpose")
        or len(classical.get("practices", [])) != 3
    ):
        errors.append(
            "strategic judgment ledger: missing Ledger identity, classical definition, or graph model"
        )
    forbidden = {"overall_score", "grand_score", "total_score"}
    present = forbidden.intersection(_walk_keys(data))
    if present:
        errors.append(f"strategic judgment ledger: forbidden aggregate score keys {sorted(present)}")

    entry_ids: set[str] = set()
    known_versions = {
        version.get("version_id")
        for position in data.get("positions", [])
        for version in position.get("versions", [])
    }
    previous_entry_key: tuple[str, str] | None = None
    for entry in data.get("journal_entries", []):
        entry_id = entry.get("entry_id")
        entry_date = entry.get("entry_date")
        if not isinstance(entry_id, str) or not entry_id.startswith("JRN-"):
            errors.append("strategic judgment ledger: invalid journal entry ID")
            continue
        if entry_id in entry_ids:
            errors.append(f"strategic judgment ledger: duplicate journal entry ID {entry_id}")
        entry_ids.add(entry_id)
        order_key = (str(entry_date), entry_id)
        if previous_entry_key and order_key <= previous_entry_key:
            errors.append("strategic judgment ledger: journal entries are not in deterministic chronological order")
        previous_entry_key = order_key
        if entry.get("entry_kind") not in JOURNAL_KINDS:
            errors.append(f"{entry_id}: invalid journal entry kind")
        if entry.get("position_effect") not in POSITION_EFFECTS:
            errors.append(f"{entry_id}: invalid position effect")
        approval = entry.get("approval", {})
        if approval.get("status") != "approved" or not approval.get("approved_at"):
            errors.append(f"{entry_id}: missing journal approval")
        for field in ("title", "observation", "interpretation", "confidence_movement"):
            if not str(entry.get(field, "")).strip():
                errors.append(f"{entry_id}: missing journal field {field}")
        learning_loop = entry.get("learning_loop", {})
        for field in LEARNING_LOOP_FIELDS:
            if not str(learning_loop.get(field, "")).strip():
                errors.append(f"{entry_id}: missing recursive-learning field {field}")
        if learning_loop.get("loop_status") not in LOOP_STATUSES:
            errors.append(f"{entry_id}: invalid recursive-learning loop status")
        for version_id in entry.get("linked_position_versions", []):
            if version_id not in known_versions:
                errors.append(f"{entry_id}: broken linked position version {version_id}")
        if "raw_text" in set(_walk_keys(entry)):
            errors.append(f"{entry_id}: raw text leaked into the Judgment Ledger")

    position_ids: set[str] = set()
    version_ids: set[str] = set()
    for position in data.get("positions", []):
        pid = position.get("position_id")
        if not isinstance(pid, str) or not pid.startswith("OV-"):
            errors.append("strategic judgment ledger: invalid position ID")
            continue
        if pid in position_ids:
            errors.append(f"strategic judgment ledger: duplicate position ID {pid}")
        position_ids.add(pid)
        versions = position.get("versions", [])
        if not versions:
            errors.append(f"{pid}: no versions")
        for index, version in enumerate(versions, start=1):
            vid = version.get("version_id")
            if vid in version_ids:
                errors.append(f"strategic judgment ledger: duplicate version ID {vid}")
            version_ids.add(vid)
            if vid != f"{pid}-v{index}" or version.get("version_number") != index:
                errors.append(f"{pid}: non-sequential immutable version chain")
            expected_previous = None if index == 1 else f"{pid}-v{index - 1}"
            if version.get("previous_version_id") != expected_previous:
                errors.append(f"{vid}: broken previous-version link")
            if version.get("relation_to_previous") not in REVISION_RELATIONS:
                errors.append(f"{vid}: invalid revision relation")
            approval = version.get("approval", {})
            if approval.get("status") != "approved" or not approval.get("approved_at"):
                errors.append(f"{vid}: missing operator approval")
            fields = version.get("position", {})
            for field in REQUIRED_POSITION_FIELDS:
                value = fields.get(field)
                if not value or (isinstance(value, list) and not all(str(v).strip() for v in value)):
                    errors.append(f"{vid}: missing position field {field}")
            layer_ids: set[str] = set()
            for layer in fields.get("epistemic_layers", []):
                if not isinstance(layer, dict):
                    errors.append(f"{vid}: epistemic layer must be an object")
                    continue
                layer_id = layer.get("layer_id")
                if not isinstance(layer_id, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", layer_id):
                    errors.append(f"{vid}: invalid epistemic layer ID")
                elif layer_id in layer_ids:
                    errors.append(f"{vid}: duplicate epistemic layer ID {layer_id}")
                else:
                    layer_ids.add(layer_id)
                for field in EPISTEMIC_LAYER_FIELDS:
                    if not str(layer.get(field, "")).strip():
                        errors.append(f"{vid}/{layer_id or 'unknown'}: missing epistemic field {field}")
                if layer.get("layer_type") not in EPISTEMIC_LAYER_TYPES:
                    errors.append(f"{vid}/{layer_id or 'unknown'}: invalid epistemic layer type")
                if layer.get("falsifier_status") not in FALSIFIER_STATUSES:
                    errors.append(f"{vid}/{layer_id or 'unknown'}: invalid falsifier status")
            trigger = version.get("review_trigger", {})
            if trigger.get("mode") != "earliest_of" or not trigger.get("date") or not trigger.get("event"):
                errors.append(f"{vid}: incomplete immutable review trigger")

            comparator_set = version.get("comparator_set", {})
            comparator_status = comparator_set.get("status")
            if comparator_status not in {"proposed", "approved"}:
                errors.append(f"{vid}: invalid comparator-set lifecycle status")
            included = comparator_set.get("included", [])
            included_slugs = {item.get("voice_slug") for item in included}
            if len(included_slugs) != len(included):
                errors.append(f"{vid}: duplicate included comparator voice")
            comparator_layers: dict[str, set[str]] = {}
            for comparator in included:
                slug = comparator.get("voice_slug")
                engaged_layers = comparator.get("engaged_layer_ids", [])
                engaged_set = set(engaged_layers) if isinstance(engaged_layers, list) else set()
                comparator_layers[slug] = engaged_set
                if not engaged_set or len(engaged_set) != len(engaged_layers):
                    errors.append(f"{vid}/{slug}: invalid or duplicate engaged layer IDs")
                if not engaged_set.issubset(layer_ids):
                    errors.append(f"{vid}/{slug}: comparator references unknown epistemic layer")
                refs = comparator.get("evidence", [])
                for ref in refs:
                    _validate_evidence_ref(ref, errors, f"{vid}/{slug}")
                    ref_layers = ref.get("layer_ids", [])
                    ref_layer_set = set(ref_layers) if isinstance(ref_layers, list) else set()
                    if not ref_layer_set or len(ref_layer_set) != len(ref_layers):
                        errors.append(f"{vid}/{slug}: evidence has invalid layer binding")
                    if not ref_layer_set.issubset(engaged_set):
                        errors.append(f"{vid}/{slug}: evidence references an unengaged layer")
                distinct_paths = {ref.get("path") for ref in refs}
                for layer_id in engaged_set:
                    layer_refs = [ref for ref in refs if layer_id in ref.get("layer_ids", [])]
                    layer_paths = {ref.get("path") for ref in layer_refs}
                    if len(layer_refs) < 2 or len(layer_paths) < 2:
                        errors.append(
                            f"{vid}/{slug}/{layer_id}: engaged layer needs "
                            "two excerpts from two sources"
                        )
                if comparator.get("evidence_count") != len(refs):
                    errors.append(f"{vid}/{slug}: evidence count drift")
                if comparator.get("source_count") != len(distinct_paths):
                    errors.append(f"{vid}/{slug}: source count drift")
                if not comparator.get("host_concentration"):
                    errors.append(f"{vid}/{slug}: missing host concentration")
            for excluded in comparator_set.get("excluded", []):
                target_layers = excluded.get("target_layer_ids", [])
                target_set = set(target_layers) if isinstance(target_layers, list) else set()
                if (
                    not target_set
                    or len(target_set) != len(target_layers)
                    or not target_set.issubset(layer_ids)
                ):
                    errors.append(
                        f"{vid}/{excluded.get('voice_slug')}: invalid excluded-layer targeting"
                    )
            comparison = version.get("comparison", {})
            comparison_status = comparison.get("status")
            allowed_comparison_statuses = (
                {"not_started"} if comparator_status == "proposed"
                else {"not_started", "provisional", "approved"}
            )
            if comparison_status not in allowed_comparison_statuses:
                errors.append(f"{vid}: invalid comparison lifecycle status")
            if (
                position.get("object_slug") == "russia-kiev-odessa-end-state"
                and version.get("version_number", 0) >= 2
                and comparator_set.get("included")
                and comparison_status in {"provisional", "approved"}
                and (
                    comparison.get("measurement_scope")
                    != "bounded-evidence persuasive coherence"
                    or not comparison.get("evidence_asymmetry")
                )
            ):
                errors.append(
                    f"{vid}: Odessa comparison must disclose bounded-evidence scope and asymmetry"
                )
            profiles = comparison.get("profiles", [])
            profile_pairs = {
                (item.get("subject"), item.get("layer_id"))
                for item in profiles
            }
            expected_profiles = {
                ("operator", layer_id) for layer_id in layer_ids
            } | {
                (slug, layer_id)
                for slug, engaged_layers in comparator_layers.items()
                for layer_id in engaged_layers
            }
            if (
                comparison_status in {"provisional", "approved"}
                and (profile_pairs != expected_profiles or len(profile_pairs) != len(profiles))
            ):
                errors.append(f"{vid}: score profiles do not match approved comparator set")
            if comparison_status == "not_started" and (
                profiles or comparison.get("relations") or comparison.get("findings")
            ):
                errors.append(f"{vid}: not-started comparison contains score data")
            for profile in profiles:
                if profile.get("layer_id") not in layer_ids:
                    errors.append(f"{vid}/{profile.get('subject')}: score profile has unknown layer")
                scores = profile.get("dimensions", {})
                if set(scores) != set(DIMENSIONS):
                    errors.append(f"{vid}/{profile.get('subject')}: requires exactly six dimensions")
                for dimension, score_data in scores.items():
                    score = score_data.get("score")
                    if score != "unavailable" and (not isinstance(score, int) or not 1 <= score <= 5):
                        errors.append(f"{vid}/{profile.get('subject')}/{dimension}: invalid score")
                    if not score_data.get("rationale"):
                        errors.append(f"{vid}/{profile.get('subject')}/{dimension}: missing rationale")
                    if not score_data.get("evidence_refs"):
                        errors.append(f"{vid}/{profile.get('subject')}/{dimension}: missing evidence refs")
            relations = comparison.get("relations", [])
            expected_relation_pairs = {
                (slug, layer_id)
                for slug, engaged_layers in comparator_layers.items()
                for layer_id in engaged_layers
            }
            relation_pairs = {
                (item.get("voice_slug"), item.get("layer_id"))
                for item in relations
            }
            if (
                comparison_status in {"provisional", "approved"}
                and (
                    relation_pairs != expected_relation_pairs
                    or len(relation_pairs) != len(relations)
                )
            ):
                errors.append(f"{vid}: relations do not match comparator set")
            for relation in relations:
                if relation.get("relation") not in RELATIONS or not relation.get("rationale"):
                    errors.append(f"{vid}: invalid or unexplained categorical relation")
            findings = comparison.get("findings", {})
            if comparison_status in {"provisional", "approved"}:
                if expected_relation_pairs:
                    for finding_name in ("closest_affinity", "strongest_corrective"):
                        finding = findings.get(finding_name, {})
                        pair = (finding.get("voice_slug"), finding.get("layer_id"))
                        if pair not in expected_relation_pairs or not finding.get("rationale"):
                            errors.append(f"{vid}: invalid {finding_name.replace('_', ' ')} finding")
                elif not findings.get("evidence_insufficient"):
                    errors.append(f"{vid}: missing evidence-insufficient finding")

    expected_graph: dict[str, Any] | None = None
    if not errors:
        try:
            expected_graph = build_graph(data)
        except LedgerError as exc:
            errors.append(f"strategic judgment graph: {exc}")
        else:
            errors.extend(validate_graph(expected_graph))
    if check_report and not errors and expected_graph is not None:
        expected_report = render_report(data)
        if not REPORT_PATH.is_file() or REPORT_PATH.read_text(encoding="utf-8") != expected_report:
            errors.append("strategic judgment ledger: canonical JSON/Markdown drift")
        expected_graph_text = _json_text(expected_graph)
        if not GRAPH_PATH.is_file() or GRAPH_PATH.read_text(encoding="utf-8") != expected_graph_text:
            errors.append("strategic judgment ledger: canonical JSON/graph drift")
    return errors


def validate_ledger() -> list[str]:
    if not LEDGER_PATH.is_file():
        return ["strategic judgment ledger: missing canonical JSON"]
    try:
        data = load_ledger()
    except (OSError, json.JSONDecodeError) as exc:
        return [f"strategic judgment ledger: unreadable JSON: {exc}"]
    return validate_data(data, check_report=True)


def render_report(data: dict[str, Any]) -> str:
    ledger = data["ledger"]
    lines = [
        f"# {ledger['title']}",
        "",
        f"*{ledger['subtitle']}*",
        "",
        f"Artifact: **Judgment Ledger** — {ledger['short_name']}.",
        "",
        f"> {data['boundary']}",
        "",
        "## Classical self-definition",
        "",
        f"**{ledger['classical_definition']['name'].title()}.** "
        f"{ledger['classical_definition']['definition']}",
        "",
        f"> {ledger['classical_definition']['dialogue']}",
        "",
        f"**Purpose.** {ledger['classical_definition']['purpose']}",
        "",
    ]
    for practice in ledger["classical_definition"]["practices"]:
        lines.append(
            f"- **{practice['tradition']}:** {practice['function']}"
        )
    lines += [
        "",
        "Canonical event ledger: `strategic-judgment-ledger.json`.",
        "Deterministic AI graph: `strategic-judgment-graph.json`.",
        "",
        "## AI exploration",
        "",
        "The Ledger is queried by object and relationship rather than read only front-to-back:",
        "",
        "```powershell",
        r".\tools\run.ps1 operator-position query --view current-beliefs",
        r".\tools\run.ps1 operator-position query --view change-history",
        r".\tools\run.ps1 operator-position query --view layer-map",
        r".\tools\run.ps1 operator-position query --view voice-map",
        r".\tools\run.ps1 operator-position query --view review-queue",
        "```",
        "",
        "## Current state",
        "",
        "| Position | Current version | Epistemic layers | Comparator state | Review |",
        "|---|---|---|---|---|",
    ]
    for position in data["positions"]:
        version = latest_version(position)
        layer_labels = "; ".join(
            layer["label"] for layer in version["position"]["epistemic_layers"]
        )
        lines.append(
            f"| {position['object_label']} | `{version['version_id']}` | {layer_labels} | "
            f"{version['comparator_set']['status']} / {version['comparison']['status']} | "
            f"{version['review_trigger']['date']} or `{version['review_trigger']['event']}` |"
        )
    lines += [
        "",
        "## Journal event view",
        "",
    ]
    for entry in data["journal_entries"]:
        lines += [
            f"### {entry['entry_date']} -- {entry['title']} (`{entry['entry_id']}`)",
            "",
            f"**Observation.** {entry['observation']}",
            "",
            f"**Interpretation.** {entry['interpretation']}",
            "",
            f"**Confidence movement.** {entry['confidence_movement']}.",
            "",
            f"**Position effect.** {entry['position_effect'].replace('_', ' ')}.",
            "",
        ]
        if entry["linked_position_versions"]:
            links = ", ".join(f"`{item}`" for item in entry["linked_position_versions"])
            lines += [f"**Linked position versions.** {links}", ""]
        if entry["voice_pressure"]:
            pressures = ", ".join(
                f"{item['voice_slug']} ({item['relation'].replace('_', ' ')})"
                for item in entry["voice_pressure"]
            )
            lines += [f"**Voice pressure.** {pressures}.", ""]
        loop = entry["learning_loop"]
        lines += [
            "#### Recursive learning",
            "",
            f"**Prior model.** {loop['prior_model']}",
            "",
            f"**Pressure.** {loop['pressure']}",
            "",
            f"**Update.** {loop['update']}",
            "",
            f"**Future test.** {loop['future_test']}",
            "",
            f"**Inherited practice.** {loop['inherited_practice']}",
            "",
            f"**Loop status.** {loop['loop_status'].replace('_', ' ')}.",
            "",
        ]
        lines += ["**Open questions.**", ""]
        for question in entry["unresolved_questions"]:
            lines.append(f"- {question}")
        lines.append("")
    lines += ["## Position object view", ""]
    for position in data["positions"]:
        version = latest_version(position)
        fields = version["position"]
        lines += [
            f"### {position['object_label']} -- `{version['version_id']}`",
            "",
            f"Approved: {version['approval']['approved_at']}",
            f"Review: {version['review_trigger']['date']} or `{version['review_trigger']['event']}`",
            "",
            "#### Approved operator position",
            "",
            f"**Thesis.** {fields['thesis']}",
            "",
            "#### Epistemic layers",
            "",
        ]
        for layer in fields["epistemic_layers"]:
            lines += [
                f"- **{layer['label']}** (`{layer['layer_type']}`; confidence: "
                f"{layer['confidence']}): {layer['claim']}",
                f"  - **Evidence standard:** {layer['evidence_standard']}",
                f"  - **Falsifier status:** `{layer['falsifier_status']}` — "
                f"{layer['falsifier_or_limitation']}",
            ]
        lines += [
            "",
            f"**Mechanism.** {fields['mechanism']}",
            "",
            f"**Implications.** {fields['implications']}",
            "",
            f"**Horizon / confidence.** {fields['horizon']} / {fields['confidence']}.",
            "",
            f"**Falsifier.** {fields['falsifier']}",
            "",
            "**Change conditions.** " + "; ".join(value.rstrip(".") for value in fields["change_conditions"]) + ".",
            "",
            "**Qualifications.** " + "; ".join(value.rstrip(".") for value in fields["qualifications"]) + ".",
            "",
            "**Strongest counterarguments.** "
            + "; ".join(value.rstrip(".") for value in fields["strongest_counterarguments"])
            + ".",
            "",
        ]
        comparator_status = version["comparator_set"].get("status")
        layer_labels = {
            layer["layer_id"]: layer["label"]
            for layer in fields["epistemic_layers"]
        }
        lines += [
            "#### Approved comparators" if comparator_status == "approved" else "#### Comparator approval pending",
            "",
            "| Voice | Role | Engaged layers | Axis | Evidence | Host concentration |",
            "|---|---|---|---|---:|---|",
        ]
        for comparator in version["comparator_set"]["included"]:
            layer_scope = "; ".join(
                layer_labels[layer_id]
                for layer_id in comparator["engaged_layer_ids"]
            )
            lines.append(
                f"| {comparator['display_name']} | "
                f"{comparator.get('comparison_role', 'substantive comparator')} | "
                f"{layer_scope} | "
                f"{comparator['orthogonality_axis']} | "
                f"{comparator['evidence_count']} excerpts / {comparator['source_count']} sources | "
                f"{comparator['host_concentration']} |"
            )
        lines += ["", "**Recorded exclusions.**", ""]
        for item in version["comparator_set"].get("excluded", []):
            target_scope = "; ".join(
                layer_labels[layer_id]
                for layer_id in item["target_layer_ids"]
            )
            lines.append(f"- {item['display_name']} ({target_scope}): {item['reason']}")
        if comparator_status != "approved":
            lines += [
                "",
                "The proposed comparator set is not canonical until operator approval.",
                "",
                "#### Revision history",
                "",
            ]
            for item in position["versions"]:
                lines.append(
                    f"- `{item['version_id']}` ({item['approval']['approved_at']}): "
                    f"{item['relation_to_previous'].replace('_', ' ')}."
                )
            lines.append("")
            continue
        comparison_status = version["comparison"].get("status")
        if comparison_status not in {"provisional", "approved"}:
            lines += [
                "",
                "#### Persuasive-coherence scoring pending",
                "",
                "No revised comparison profile has been generated.",
                "",
                "#### Revision history",
                "",
            ]
            for item in position["versions"]:
                lines.append(
                    f"- `{item['version_id']}` ({item['approval']['approved_at']}): "
                    f"{item['relation_to_previous'].replace('_', ' ')}."
                )
            lines.append("")
            continue
        lines += [
            "",
            "#### Persuasive-coherence profiles"
            if comparison_status == "approved"
            else "#### Provisional persuasive-coherence profiles",
            "",
        ]
        if version["comparison"].get("measurement_scope"):
            lines += [
                f"**Measurement scope.** {version['comparison']['measurement_scope']}.",
                "",
                f"**Evidence asymmetry.** {version['comparison']['evidence_asymmetry']}",
                "",
            ]
        lines += [
            "| Subject | Layer | Thesis | Consistency | Mechanism | Scope | Counterarguments | Compression |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
        for profile in version["comparison"]["profiles"]:
            values = [str(profile["dimensions"][dimension]["score"]) for dimension in DIMENSIONS]
            lines.append(
                f"| {profile['display_name']} | {layer_labels[profile['layer_id']]} | "
                + " | ".join(values)
                + " |"
            )
        operator_profiles = {
            profile["layer_id"]: profile
            for profile in version["comparison"]["profiles"]
            if profile["subject"] == "operator"
        }
        lines += [
            "",
            "##### Dimension deltas (voice minus operator)",
            "",
            "| Voice | Layer | Thesis | Consistency | Mechanism | Scope | Counterarguments | Compression |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
        for profile in version["comparison"]["profiles"]:
            if profile["subject"] == "operator":
                continue
            operator_profile = operator_profiles[profile["layer_id"]]
            deltas: list[str] = []
            for dimension in DIMENSIONS:
                voice_score = profile["dimensions"][dimension]["score"]
                operator_score = operator_profile["dimensions"][dimension]["score"]
                if not isinstance(voice_score, int) or not isinstance(operator_score, int):
                    deltas.append("unavailable")
                else:
                    delta = voice_score - operator_score
                    deltas.append(f"{delta:+d}")
            lines.append(
                f"| {profile['display_name']} | {layer_labels[profile['layer_id']]} | "
                + " | ".join(deltas)
                + " |"
            )
        lines += ["", "No overall score is calculated.", "", "#### Relations and findings", ""]
        for relation in version["comparison"]["relations"]:
            lines.append(
                f"- **{relation['display_name']} on {layer_labels[relation['layer_id']]} — "
                f"{relation['relation'].replace('_', ' ')}:** "
                f"{relation['rationale']}"
            )
        findings = version["comparison"]["findings"]
        if findings.get("evidence_insufficient"):
            lines += ["", f"**Evidence insufficient.** {findings['evidence_insufficient']}"]
        else:
            lines += [
                "",
                f"**Closest affinity.** {findings['closest_affinity']['display_name']} on "
                f"{layer_labels[findings['closest_affinity']['layer_id']]}: "
                f"{findings['closest_affinity']['rationale']}",
                "",
                f"**Strongest corrective.** {findings['strongest_corrective']['display_name']} on "
                f"{layer_labels[findings['strongest_corrective']['layer_id']]}: "
                f"{findings['strongest_corrective']['rationale']}",
            ]
        lines += ["", "#### Revision history", ""]
        for item in position["versions"]:
            lines.append(
                f"- `{item['version_id']}` ({item['approval']['approved_at']}): "
                f"{item['relation_to_previous'].replace('_', ' ')}."
            )
        lines.append("")
    return "\n".join(lines)


def make_candidate(input_path: Path, object_slug: str, source_kind: str) -> Path:
    raw = input_path.read_text(encoding="utf-8")
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    candidate = {
        "schema": "operator-position-candidate-v1",
        "candidate_id": f"CAND-{date.today():%Y%m%d}-{digest}",
        "object_slug": object_slug,
        "source_kind": source_kind,
        "source_path": str(input_path.resolve()),
        "raw_text": raw,
        "normalized_position": {field: [] if field in {
            "epistemic_layers", "change_conditions", "qualifications", "strongest_counterarguments"
        } else "" for field in REQUIRED_POSITION_FIELDS},
    }
    CANDIDATE_ROOT.mkdir(parents=True, exist_ok=True)
    target = CANDIDATE_ROOT / f"{candidate['candidate_id']}.json"
    target.write_text(json.dumps(candidate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def make_journal_candidate(
    input_path: Path,
    entry_date: str,
    entry_kind: str,
) -> Path:
    date.fromisoformat(entry_date)
    raw = input_path.read_text(encoding="utf-8")
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    candidate = {
        "schema": "operator-journal-candidate-v1",
        "candidate_id": f"JCAND-{entry_date.replace('-', '')}-{digest}",
        "entry_date": entry_date,
        "entry_kind": entry_kind,
        "source_path": str(input_path.resolve()),
        "raw_text": raw,
        "normalized_entry": {
            "title": "",
            "observation": "",
            "interpretation": "",
            "confidence_movement": "",
            "position_effect": "context",
            "linked_position_versions": [],
            "voice_pressure": [],
            "unresolved_questions": [],
            "learning_loop": {
                "prior_model": "",
                "pressure": "",
                "update": "",
                "future_test": "",
                "inherited_practice": "",
                "loop_status": "partial",
            },
        },
    }
    CANDIDATE_ROOT.mkdir(parents=True, exist_ok=True)
    target = CANDIDATE_ROOT / f"{candidate['candidate_id']}.json"
    target.write_text(json.dumps(candidate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def approve_journal_candidate(data: dict[str, Any], candidate_path: Path) -> dict[str, Any]:
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    if candidate.get("schema") != "operator-journal-candidate-v1":
        raise LedgerError("invalid journal candidate schema")
    normalized = candidate.get("normalized_entry", {})
    missing = [
        field
        for field in ("title", "observation", "interpretation", "confidence_movement")
        if not str(normalized.get(field, "")).strip()
    ]
    if missing:
        raise LedgerError(f"journal candidate is not normalized; missing {', '.join(missing)}")
    if normalized.get("position_effect") not in POSITION_EFFECTS:
        raise LedgerError("journal candidate has invalid position effect")
    learning_loop = normalized.get("learning_loop", {})
    missing_loop = [
        field for field in LEARNING_LOOP_FIELDS
        if not str(learning_loop.get(field, "")).strip()
    ]
    if missing_loop:
        raise LedgerError(
            "journal candidate is missing recursive-learning fields: "
            + ", ".join(missing_loop)
        )
    if learning_loop.get("loop_status") not in LOOP_STATUSES:
        raise LedgerError("journal candidate has invalid recursive-learning loop status")
    entry_date = candidate["entry_date"]
    date.fromisoformat(entry_date)
    same_day = [
        entry
        for entry in data["journal_entries"]
        if entry.get("entry_date") == entry_date
    ]
    entry = {
        "entry_id": f"JRN-{entry_date.replace('-', '')}-{len(same_day) + 1:02d}",
        "entry_date": entry_date,
        "entry_kind": candidate["entry_kind"],
        **deepcopy(normalized),
        "approval": {
            "status": "approved",
            "approved_at": date.today().isoformat(),
            "basis": "explicit operator journal-entry approval",
        },
        "provenance": {
            "source_kind": "nominated local daily activity",
            "note": "Normalized from an approved local candidate; raw activity remains ignored.",
        },
    }
    data["journal_entries"].append(entry)
    data["journal_entries"].sort(key=lambda item: (item["entry_date"], item["entry_id"]))
    errors = [
        error
        for error in validate_data(data)
        if entry["entry_id"] in error or "journal entr" in error
    ]
    if errors:
        raise LedgerError("journal approval failed: " + "; ".join(errors))
    return entry


def approve_candidate(candidate_path: Path, position_id: str, object_label: str) -> None:
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    fields = candidate.get("normalized_position", {})
    missing = [field for field in REQUIRED_POSITION_FIELDS if not fields.get(field)]
    if missing:
        raise LedgerError(f"candidate is not normalized; missing {', '.join(missing)}")
    data = load_ledger()
    position = next((item for item in data["positions"] if item["position_id"] == position_id), None)
    if position is None:
        position = {
            "position_id": position_id,
            "object_slug": candidate["object_slug"],
            "object_label": object_label,
            "versions": [],
        }
        data["positions"].append(position)
    number = len(position["versions"]) + 1
    previous = position["versions"][-1]["version_id"] if position["versions"] else None
    approved = date.today()
    position["versions"].append({
        "version_id": f"{position_id}-v{number}",
        "version_number": number,
        "previous_version_id": previous,
        "relation_to_previous": "initial" if number == 1 else "revision",
        "approval": {"status": "approved", "approved_at": approved.isoformat(), "basis": "explicit operator approval"},
        "position": deepcopy(fields),
        "provenance": {"source_kind": candidate["source_kind"], "note": "Normalized from a nominated local input; raw text remains ignored."},
        "review_trigger": {
            "mode": "earliest_of",
            "date": (approved + timedelta(days=30)).isoformat(),
            "event": "credible-settlement-terms-linking-battlefield-disposition-to-political-conversion",
        },
        "comparator_set": {"status": "proposed", "included": [], "excluded": []},
        "comparison": {"status": "not_started", "profiles": [], "relations": [], "findings": {}},
    })
    write_ledger(data)


def apply_recommendation_candidate(
    data: dict[str, Any],
    position_id: str,
    candidate_path: Path,
) -> dict[str, Any]:
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    if candidate.get("schema") != "operator-comparator-recommendation-v1":
        raise LedgerError("invalid comparator recommendation schema")
    if candidate.get("position_id") != position_id:
        raise LedgerError("comparator recommendation position does not match")

    version = latest_version(find_position(data, position_id))
    if candidate.get("version_id") != version.get("version_id"):
        raise LedgerError("comparator recommendation is not for the current version")
    if version["comparator_set"].get("status") == "approved":
        raise LedgerError("approved comparator sets are immutable; create a review version first")

    proposal = deepcopy(version["comparator_set"])
    included = {item["voice_slug"]: item for item in proposal.get("included", [])}
    for update in candidate.get("included_layer_updates", []):
        voice_slug = update.get("voice_slug")
        item = included.get(voice_slug)
        if item is None:
            raise LedgerError(f"unknown included comparator voice: {voice_slug}")
        layer_id = update.get("layer_id")
        if layer_id in item.get("engaged_layer_ids", []):
            raise LedgerError(f"{voice_slug}/{layer_id}: comparator layer already exists")
        evidence = update.get("evidence", [])
        evidence_paths = {ref.get("path") for ref in evidence}
        if (
            len(evidence) < 2
            or len(evidence_paths) < 2
            or any(layer_id not in ref.get("layer_ids", []) for ref in evidence)
        ):
            raise LedgerError(
                f"{voice_slug}/{layer_id}: comparator evidence threshold not met"
            )
        item.setdefault("engaged_layer_ids", []).append(layer_id)
        item.setdefault("evidence", []).extend(deepcopy(evidence))
        item["evidence_count"] = len(item["evidence"])
        item["source_count"] = len({ref["path"] for ref in item["evidence"]})
        for field in (
            "host_concentration",
            "inclusion_rationale",
            "orthogonality_axis",
        ):
            if not str(update.get(field, "")).strip():
                raise LedgerError(f"{voice_slug}: missing {field}")
            item[field] = update[field]

    for update in candidate.get("included_voice_updates", []):
        voice_slug = update.get("voice_slug")
        item = included.get(voice_slug)
        if item is None:
            raise LedgerError(f"unknown included comparator voice: {voice_slug}")
        changed = False
        for field in (
            "comparison_role",
            "host_concentration",
            "inclusion_rationale",
            "orthogonality_axis",
        ):
            if field not in update:
                continue
            if not str(update[field]).strip():
                raise LedgerError(f"{voice_slug}: empty {field}")
            item[field] = update[field]
            changed = True
        if not changed:
            raise LedgerError(f"{voice_slug}: comparator voice update is empty")

    excluded = {item["voice_slug"]: item for item in proposal.get("excluded", [])}
    for update in candidate.get("excluded_layer_updates", []):
        voice_slug = update.get("voice_slug")
        item = excluded.get(voice_slug)
        if item is None:
            raise LedgerError(f"unknown excluded comparator voice: {voice_slug}")
        layer_id = update.get("layer_id")
        if layer_id not in item.get("target_layer_ids", []):
            item.setdefault("target_layer_ids", []).append(layer_id)
        for field in ("host_concentration", "reason"):
            if not str(update.get(field, "")).strip():
                raise LedgerError(f"{voice_slug}: missing exclusion {field}")
            item[field] = update[field]

    proposal.setdefault("recommendation_basis", {}).update(
        deepcopy(candidate.get("recommendation_basis_updates", {}))
    )
    proposal["status"] = "proposed"
    proposal.pop("approval", None)
    version["comparator_set"] = proposal
    version["comparison"] = {
        "status": "not_started",
        "profiles": [],
        "relations": [],
        "findings": {},
    }
    return proposal


def recommend_for_position(
    data: dict[str, Any],
    position_id: str,
    candidate_path: Path | None = None,
) -> dict[str, Any]:
    if candidate_path is not None:
        return apply_recommendation_candidate(data, position_id, candidate_path)
    position = find_position(data, position_id)
    version = latest_version(position)
    if version["comparator_set"].get("status") == "approved":
        raise LedgerError("approved comparator sets are immutable; create a review version first")
    if version["comparator_set"].get("included"):
        proposal = deepcopy(version["comparator_set"])
    else:
        pilot = data["positions"][0]["versions"][0]["comparator_set"]
        if position.get("object_slug") != "ukraine-war-termination":
            raise LedgerError("v1 recommendation library only supports ukraine-war-termination")
        proposal = deepcopy(pilot)
    proposal["status"] = "proposed"
    proposal.pop("approval", None)
    version["comparator_set"] = proposal
    version["comparison"] = {"status": "not_started", "profiles": [], "relations": [], "findings": {}}
    return proposal


def approve_comparators(data: dict[str, Any], position_id: str) -> None:
    trial = deepcopy(data)
    version = latest_version(find_position(trial, position_id))
    comparator_set = version["comparator_set"]
    if comparator_set.get("status") != "proposed":
        raise LedgerError("comparator set must be proposed before approval")
    for item in comparator_set.get("included", []):
        refs = item.get("evidence", [])
        for layer_id in item.get("engaged_layer_ids", []):
            layer_refs = [ref for ref in refs if layer_id in ref.get("layer_ids", [])]
            if len(layer_refs) < 2 or len({ref.get("path") for ref in layer_refs}) < 2:
                raise LedgerError(
                    f"{item.get('voice_slug')}/{layer_id}: comparator evidence threshold not met"
                )
    comparator_set["status"] = "approved"
    comparator_set["approval"] = {
        "approved_at": date.today().isoformat(),
        "basis": "explicit operator comparator approval",
    }
    errors = validate_data(trial)
    if errors:
        raise LedgerError("comparator approval failed: " + "; ".join(errors))
    data.clear()
    data.update(trial)


def _operator_draft_profile(version: dict[str, Any], layer_id: str) -> dict[str, Any]:
    scores = {
        "thesis_precision": 5,
        "internal_consistency": 4,
        "mechanism_completeness": 5,
        "scope_and_qualification_discipline": 4,
        "counterargument_integration": 5,
        "explanatory_compression": 4,
    }
    rationales = {
        "thesis_precision": (
            "The refinement explicitly identifies negotiated, tacit, and imposed "
            "political-order pathways and separates termination from battlefield movement."
        ),
        "internal_consistency": (
            "Thesis, mechanism, implications, and qualifications consistently allow "
            "coercive capitulation, though the frozen-conflict boundary remains unsettled."
        ),
        "mechanism_completeness": (
            "The mechanism now connects leverage and resistance capacity to authority, "
            "territory, security, cessation, compliance, and enforcement."
        ),
        "scope_and_qualification_discipline": (
            "The view distinguishes legitimacy from effectiveness and treaties from de "
            "facto order, but its broad definition of political conversion risks expansion."
        ),
        "counterargument_integration": (
            "The candidate directly incorporates capitulation and states the strongest "
            "tautology, exhaustion, and continuing-force objections."
        ),
        "explanatory_compression": (
            "The added pathways improve precision but make the thesis and mechanism less "
            "compact than v1."
        ),
    }
    if layer_id != "termination_conversion":
        scores = {dimension: "unavailable" for dimension in DIMENSIONS}
        rationales = {
            dimension: (
                "Layer-specific persuasive-coherence scoring has not yet been "
                "reviewed for this epistemic layer."
            )
            for dimension in DIMENSIONS
        }
    return {
        "subject": "operator",
        "display_name": "Operator",
        "layer_id": layer_id,
        "dimensions": {
            dimension: {
                "score": score,
                "rationale": rationales[dimension],
                "evidence_refs": [f"{version['version_id']}:{layer_id}:{dimension}"],
            }
            for dimension, score in scores.items()
        },
    }


ODESSA_PROFILE_SPECS = {
    ("operator", "kiev_security_requirement"): {
        "scores": (5, 4, 5, 4, 5, 4),
        "rationales": (
            "The claim precisely distinguishes structural reconstitution from permanent occupation and names the prohibited regeneration outcome.",
            "The thesis, mechanism, falsifier, and qualifications consistently treat durable constraint rather than possession of the capital as the security requirement.",
            "Neutrality, demilitarization, security-service restructuring, territorial reorganization, and enforcement durability form an unusually complete causal chain.",
            "The layer is separated from the Odessa premise and forecast, though structural reconstitution still covers several possible institutional forms.",
            "Neutrality substitutes, security-dilemma effects, insurgency, and narrower Russian aims are integrated as serious tests rather than dismissed.",
            "The core constraint-regeneration logic is compact, but its institutional implementation requires several linked clauses.",
        ),
    },
    ("operator", "odessa_civilizational_premise"): {
        "scores": (5, 4, 4, 5, 5, 4),
        "rationales": (
            "The layer explicitly states direct corridor control as an operator premise and denies that it is verified current Russian policy.",
            "Historical significance, maritime denial, corridor geometry, and the current-policy caveat remain mutually compatible across the position.",
            "The southern-corridor mechanism identifies maritime, Crimean, and Transnistrian effects, but the civilizational premise does not independently prove indispensability.",
            "The operator inference, policy attribution, moral endorsement, and outcome forecast are unusually well separated.",
            "Public-policy silence, security substitutes, balancing, insurgency, and feasibility are all stated as potentially model-changing objections.",
            "The direct-control conclusion is clear, though combining identity and strategic geometry reduces compression.",
        ),
    },
    ("operator", "current_war_realization"): {
        "scores": (4, 4, 4, 4, 5, 3),
        "rationales": (
            "The forecast names both required outcomes, the combat-phase horizon, likelihood language, and an early defeat condition.",
            "The forecast follows from the stated security model without being presented as inevitable or as verified Russian policy.",
            "Parallel military, demographic, economic, elite, and external-support pathways are specified, but their interaction and thresholds remain only partly operationalized.",
            "Substantial failure risk and separate policy attribution are explicit, though the forecast spans several difficult-to-measure systems.",
            "Escalation, overextension, battlefield reversal, and durable narrower settlement are integrated as genuine failure pathways.",
            "The forecast carries too many interacting conditions to compress without losing important uncertainty.",
        ),
    },
    ("macgregor", "kiev_security_requirement"): {
        "scores": (4, 4, 3, 3, "unavailable", 4),
        "rationales": (
            "The bounded evidence clearly identifies action against Kiev and its government as part of an end state.",
            "The two excerpts consistently move from military possibility to government removal and termination.",
            "Decisive action is explicit, but the post-removal institutional and enforcement mechanism is not developed.",
            "The claim is direct but does not sharply distinguish temporary regime removal, occupation, and durable structural constraint.",
            "The approved excerpts do not provide enough counterargument material to score this dimension without treating silence as weakness.",
            "Government removal leading to an end state is expressed with strong economy.",
        ),
    },
    ("macgregor", "odessa_civilizational_premise"): {
        "scores": (4, 4, 3, 2, "unavailable", 4),
        "rationales": (
            "Odessa is directly described as historically Russian and as a place that must return in Russian consciousness.",
            "The historical-city and return-to-Russia formulations reinforce one another across distinct hosts.",
            "Identity and Russian public consciousness are named, but the chain from those facts to strategic indispensability remains incomplete.",
            "The evidence does not distinguish broad Russian sentiment from binding leadership policy or feasible war aims.",
            "The bounded pair contains no attributable counterargument exchange, so this dimension is unavailable rather than weak.",
            "The historical identity and return claim is memorable and compact.",
        ),
    },
    ("ritter", "kiev_security_requirement"): {
        "scores": (4, 4, 4, 4, 3, 4),
        "rationales": (
            "The evidence precisely combines a demilitarization floor with the claim that physical possession of Kiev is unnecessary.",
            "Political alignment and force reduction consistently serve as substitutes for occupation.",
            "The control-without-occupation mechanism identifies force limits and a Russia-oriented government, though enforcement durability is underdeveloped.",
            "Ritter distinguishes physical capture from effective political control more carefully than most comparators.",
            "The substitute mechanism implicitly answers the occupation objection, but the excerpts do not deeply test its legitimacy or durability.",
            "The mechanism is compressed into a clear contrast between possession and alignment.",
        ),
    },
    ("ritter", "odessa_civilizational_premise"): {
        "scores": (4, 4, 3, 5, 3, 4),
        "rationales": (
            "Ritter plainly calls Odessa Russian while separately stating that Putin has not made the decision to take it.",
            "Identity, anticipated direction, operational scale, and leadership contingency coexist without contradiction.",
            "The evidence supplies operational-cost estimates and directional logic but not a complete necessity mechanism.",
            "The distinction between the speaker's forecast and Putin's present decision is unusually disciplined.",
            "Leadership hesitation and force requirements function as meaningful correctives, though wider strategic objections remain sparse.",
            "The identity claim and policy-contingency caveat are expressed economically.",
        ),
    },
    ("mercouris", "kiev_security_requirement"): {
        "scores": (4, 4, 4, 4, "unavailable", 4),
        "rationales": (
            "Neutrality, demilitarization, denazification, elections, and political change are stated as concrete settlement requirements.",
            "The root-causes and new-government formulations align across the two approved sources.",
            "The political-reconstitution mechanism is substantial, though enforcement and long-run force regeneration remain less explicit.",
            "The evidence distinguishes political conditions from battlefield movement, while some terms remain broad and contested.",
            "The approved excerpts do not contain enough direct engagement with competing settlement models to score counterargument integration.",
            "The root-causes formulation compresses several settlement conditions effectively.",
        ),
    },
    ("mercouris", "odessa_civilizational_premise"): {
        "scores": (3, 4, 3, 3, "unavailable", 3),
        "rationales": (
            "The evidence identifies Odessa within a possible historic-Russian-lands scope, but the decisive claim is inferential rather than enumerated policy.",
            "Both excerpts consistently apply the same historical-land interpretation.",
            "Catherine-era geography supplies an interpretive bridge, but it does not complete the mechanism from rhetoric to binding war aim.",
            "Mercouris marks the conclusion as his interpretation, but the move from historical scope to current intent remains broader than the quoted language itself.",
            "The bounded evidence does not contain enough attributable engagement with narrower readings of Putin's language to score this dimension.",
            "The historical inference is intelligible but requires caveats that reduce compression.",
        ),
    },
    ("mearsheimer", "kiev_security_requirement"): {
        "scores": (4, 5, 5, 4, "unavailable", 5),
        "rationales": (
            "The dysfunctional-rump-state objective precisely identifies the security effect Russia seeks without requiring possession of Kiev.",
            "Threat reduction, NATO exclusion, and territorial weakening form a highly consistent realist account.",
            "The security-dilemma mechanism links Western use of Ukraine, Russian incentives, state capacity, and threat disablement.",
            "The account stays instrumental and avoids converting predicted incentives into identity or legal claims.",
            "The Kiev evidence pair does not contain enough explicit counterargument handling to support a numeric score.",
            "The incentive-to-disable-threat chain achieves unusually strong explanatory compression.",
        ),
    },
    ("mearsheimer", "odessa_civilizational_premise"): {
        "scores": (4, 5, 5, 5, 4, 5),
        "rationales": (
            "Odessa is tied precisely to ports, Black Sea access, economic disablement, and a likely but uncertain Russian move.",
            "The two sources consistently apply the same instrumental security logic.",
            "Port removal, loss of sea access, rump-state economics, and capture cost form the most complete Odessa mechanism in the set.",
            "Desire, capability, reasonable cost, and civilizational interpretation remain clearly distinct.",
            "Capability and cost uncertainty are integrated directly, though long-run balancing and occupation effects remain less developed.",
            "The port-denial-to-dysfunctional-state chain is unusually compact and explanatory.",
        ),
    },
}


def _odessa_pilot_comparison(version: dict[str, Any]) -> dict[str, Any]:
    comparators = {
        item["voice_slug"]: item
        for item in version["comparator_set"]["included"]
    }
    profiles = []
    operator_layers = [
        layer["layer_id"]
        for layer in version["position"]["epistemic_layers"]
    ]
    profile_pairs = [("operator", layer_id) for layer_id in operator_layers]
    profile_pairs += [
        (item["voice_slug"], layer_id)
        for item in version["comparator_set"]["included"]
        for layer_id in item["engaged_layer_ids"]
    ]
    for subject, layer_id in profile_pairs:
        spec = ODESSA_PROFILE_SPECS.get((subject, layer_id))
        if spec is None:
            raise LedgerError(
                f"{subject}/{layer_id}: missing Odessa pilot score profile"
            )
        if subject == "operator":
            display_name = "Operator"
            evidence_refs = [
                f"{version['version_id']}:{layer_id}:position"
            ]
        else:
            comparator = comparators[subject]
            display_name = comparator["display_name"]
            evidence_refs = [
                ref["path"]
                for ref in comparator["evidence"]
                if layer_id in ref["layer_ids"]
            ]
        profiles.append({
            "subject": subject,
            "display_name": display_name,
            "layer_id": layer_id,
            "dimensions": {
                dimension: {
                    "score": score,
                    "rationale": rationale,
                    "evidence_refs": evidence_refs,
                }
                for dimension, score, rationale in zip(
                    DIMENSIONS,
                    spec["scores"],
                    spec["rationales"],
                )
            },
        })

    relation_specs = {
        ("macgregor", "kiev_security_requirement"): (
            "conditional_divergence",
            "He shares the requirement for decisive political disablement but treats action against Kiev's government as more physically direct than the operator's sufficient condition of durable structural constraint.",
        ),
        ("macgregor", "odessa_civilizational_premise"): (
            "reinforcement",
            "He most directly reinforces the operator premise by joining Odessa's Russian historical identity to an asserted expectation of return.",
        ),
        ("ritter", "kiev_security_requirement"): (
            "reinforcement",
            "His demilitarization and political-alignment substitute closely matches the operator's claim that enforceable reconstitution can suffice without permanent occupation.",
        ),
        ("ritter", "odessa_civilizational_premise"): (
            "conditional_divergence",
            "He accepts the Russian-city premise and anticipates movement toward Odessa, but explicitly withholds attribution of a present Putin decision.",
        ),
        ("mercouris", "kiev_security_requirement"): (
            "reinforcement",
            "His neutrality, demilitarization, elections, and government-change terms reinforce structural reconstitution as the settlement mechanism.",
        ),
        ("mercouris", "odessa_civilizational_premise"): (
            "conditional_divergence",
            "His historical-land reading supports the premise only as an interpretation of Putin's language, not as independently corroborated binding policy.",
        ),
        ("mearsheimer", "kiev_security_requirement"): (
            "reinforcement",
            "His dysfunctional-rump-state logic reinforces durable threat disablement without making occupation of Kiev the necessary mechanism.",
        ),
        ("mearsheimer", "odessa_civilizational_premise"): (
            "mechanism_disagreement",
            "He supports the Odessa outcome through port denial, economic disablement, and security incentives rather than civilizational indispensability.",
        ),
    }
    relations = []
    for comparator in version["comparator_set"]["included"]:
        for layer_id in comparator["engaged_layer_ids"]:
            relation, rationale = relation_specs[(comparator["voice_slug"], layer_id)]
            relations.append({
                "voice_slug": comparator["voice_slug"],
                "display_name": comparator["display_name"],
                "layer_id": layer_id,
                "relation": relation,
                "rationale": rationale,
            })
    return {
        "status": "provisional",
        "measurement_scope": "bounded-evidence persuasive coherence",
        "evidence_asymmetry": (
            "Operator profiles use the complete approved position; voice profiles use "
            "only the approved layer-specific excerpts. Unavailable marks dimensions "
            "that those excerpts cannot support and is not converted to zero."
        ),
        "profiles": profiles,
        "relations": relations,
        "findings": {
            "closest_affinity": {
                "voice_slug": "macgregor",
                "display_name": comparators["macgregor"]["display_name"],
                "layer_id": "odessa_civilizational_premise",
                "rationale": (
                    "Macgregor most directly joins Odessa's historical-Russian identity "
                    "to an expectation of territorial return, matching the operator premise."
                ),
            },
            "strongest_corrective": {
                "voice_slug": "mearsheimer",
                "display_name": comparators["mearsheimer"]["display_name"],
                "layer_id": "odessa_civilizational_premise",
                "rationale": (
                    "Mearsheimer reaches a similar territorial expectation through ports, "
                    "economic disablement, security incentives, capability, and cost, forcing "
                    "the operator to show what civilizational logic adds."
                ),
            },
        },
    }


def score_position(data: dict[str, Any], position_id: str) -> dict[str, Any]:
    position = find_position(data, position_id)
    version = latest_version(position)
    if version["comparator_set"].get("status") != "approved":
        raise LedgerError("approve the comparator set before scoring")
    if version["comparison"].get("status") == "approved":
        raise LedgerError("approved comparisons are immutable; create a review version first")
    if (
        position.get("object_slug") == "russia-kiev-odessa-end-state"
        and version["comparator_set"].get("included")
    ):
        comparison = _odessa_pilot_comparison(version)
        version["comparison"] = comparison
        return comparison
    pilot_comparison = data["positions"][0]["versions"][0]["comparison"]
    pilot_profiles = {
        (profile["subject"], profile["layer_id"]): profile
        for profile in pilot_comparison["profiles"]
    }
    pilot_relations = {
        (relation["voice_slug"], relation["layer_id"]): relation
        for relation in pilot_comparison["relations"]
    }
    profiles = [
        _operator_draft_profile(version, layer["layer_id"])
        for layer in version["position"]["epistemic_layers"]
    ]
    relations = []
    for comparator in version["comparator_set"]["included"]:
        slug = comparator["voice_slug"]
        for layer_id in comparator["engaged_layer_ids"]:
            pair = (slug, layer_id)
            if pair in pilot_profiles:
                profiles.append(deepcopy(pilot_profiles[pair]))
            else:
                profiles.append({
                    "subject": slug,
                    "display_name": comparator["display_name"],
                    "layer_id": layer_id,
                    "dimensions": {
                        dimension: {
                            "score": "unavailable",
                            "rationale": (
                                "The approved evidence set has not yet been reviewed "
                                "for this layer and dimension."
                            ),
                            "evidence_refs": [
                                f"{slug}:{layer_id}:approved-comparator-evidence"
                            ],
                        }
                        for dimension in DIMENSIONS
                    },
                })
            if pair in pilot_relations:
                relations.append(deepcopy(pilot_relations[pair]))
            else:
                relations.append({
                    "voice_slug": slug,
                    "display_name": comparator["display_name"],
                    "layer_id": layer_id,
                    "relation": "non_engagement",
                    "rationale": (
                        "Provisional layer-specific relation requires operator "
                        "review against the approved evidence."
                    ),
                })
    relation_pairs = {
        (relation["voice_slug"], relation["layer_id"])
        for relation in relations
    }
    pilot_findings = deepcopy(pilot_comparison["findings"])
    if relation_pairs and all(
        (
            pilot_findings.get(name, {}).get("voice_slug"),
            pilot_findings.get(name, {}).get("layer_id"),
        ) in relation_pairs
        for name in ("closest_affinity", "strongest_corrective")
    ):
        findings = pilot_findings
    elif relations:
        affinity = relations[0]
        corrective = relations[-1]
        findings = {
            "closest_affinity": {
                "voice_slug": affinity["voice_slug"],
                "display_name": affinity["display_name"],
                "layer_id": affinity["layer_id"],
                "rationale": "Provisional affinity requires operator review.",
            },
            "strongest_corrective": {
                "voice_slug": corrective["voice_slug"],
                "display_name": corrective["display_name"],
                "layer_id": corrective["layer_id"],
                "rationale": "Provisional corrective requires operator review.",
            },
        }
    else:
        findings = {
            "evidence_insufficient": (
                "No voice cleared the layer-specific comparator evidence threshold."
            )
        }
    comparison = {
        "status": "provisional",
        "profiles": profiles,
        "relations": relations,
        "findings": findings,
    }
    version["comparison"] = comparison
    return comparison


def approve_score(data: dict[str, Any], position_id: str) -> None:
    version = latest_version(find_position(data, position_id))
    comparison = version["comparison"]
    if comparison.get("status") != "provisional":
        raise LedgerError("comparison must be provisional before approval")
    trial = deepcopy(data)
    trial_version = latest_version(find_position(trial, position_id))
    trial_version["comparison"]["status"] = "approved"
    trial_version["comparison"]["approval"] = {
        "approved_at": date.today().isoformat(),
        "basis": "explicit operator score approval",
    }
    errors = validate_data(trial)
    if errors:
        raise LedgerError("score approval failed: " + "; ".join(errors))
    data.clear()
    data.update(trial)


def review_position(
    data: dict[str, Any],
    position_id: str,
    relation: str,
    candidate_path: Path | None = None,
) -> dict[str, Any]:
    if relation not in REVISION_RELATIONS - {"initial"}:
        raise LedgerError("review relation must be refinement, revision, contradiction, or unchanged_review")
    position = find_position(data, position_id)
    previous = latest_version(position)
    version = deepcopy(previous)
    number = len(position["versions"]) + 1
    version["version_id"] = f"{position_id}-v{number}"
    version["version_number"] = number
    version["previous_version_id"] = previous["version_id"]
    version["relation_to_previous"] = relation
    if candidate_path:
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        fields = candidate.get("normalized_position", {})
        missing = [field for field in REQUIRED_POSITION_FIELDS if not fields.get(field)]
        if missing:
            raise LedgerError(f"candidate is not normalized; missing {', '.join(missing)}")
        version["position"] = deepcopy(fields)
        version["provenance"] = {
            "source_kind": candidate.get("source_kind", "nominated input"),
            "note": "Review normalized from a nominated local input; raw text remains ignored.",
        }
        version["comparator_set"]["status"] = "proposed"
        version["comparator_set"].pop("approval", None)
        version["comparison"] = {
            "status": "not_started",
            "profiles": [],
            "relations": [],
            "findings": {},
        }
    elif relation != "unchanged_review":
        raise LedgerError("a changed review requires --candidate")
    approved = date.today()
    version["approval"] = {
        "status": "approved",
        "approved_at": approved.isoformat(),
        "basis": "explicit operator review approval",
    }
    version["review_trigger"] = {
        "mode": "earliest_of",
        "date": (approved + timedelta(days=30)).isoformat(),
        "event": previous["review_trigger"]["event"],
    }
    position["versions"].append(version)
    return version


def due_items(data: dict[str, Any], as_of: date, event: str | None = None) -> list[dict[str, str]]:
    due: list[dict[str, str]] = []
    for position in data["positions"]:
        version = latest_version(position)
        trigger = version["review_trigger"]
        reasons: list[str] = []
        if date.fromisoformat(trigger["date"]) <= as_of:
            reasons.append("date")
        if event and (event == trigger["event"] or event.lower() in trigger["event"].lower()):
            reasons.append("event")
        if reasons:
            due.append({"position_id": position["position_id"], "version_id": version["version_id"], "reason": "+".join(reasons)})
    return due


def query_ledger(
    data: dict[str, Any],
    view: str,
    *,
    position_id: str | None = None,
    as_of: date | None = None,
) -> dict[str, Any]:
    positions = data["positions"]
    if position_id:
        positions = [find_position(data, position_id)]
    graph = build_graph(data)
    results: Any
    if view == "current-beliefs":
        results = []
        for position in positions:
            version = latest_version(position)
            results.append({
                "position_id": position["position_id"],
                "object_label": position["object_label"],
                "current_version_id": version["version_id"],
                "thesis": version["position"]["thesis"],
                "layers": deepcopy(version["position"]["epistemic_layers"]),
                "comparator_status": version["comparator_set"]["status"],
                "comparison_status": version["comparison"]["status"],
                "review_trigger": deepcopy(version["review_trigger"]),
            })
    elif view == "change-history":
        allowed_versions = {
            version["version_id"]
            for position in positions
            for version in position["versions"]
        }
        position_events = [
            {
                "event_type": "position_version",
                "event_date": version["approval"]["approved_at"],
                "event_id": version["version_id"],
                "position_id": position["position_id"],
                "relation": version["relation_to_previous"],
                "previous_version_id": version["previous_version_id"],
            }
            for position in positions
            for version in position["versions"]
        ]
        journal_events = [
            {
                "event_type": "journal_event",
                "event_date": entry["entry_date"],
                "event_id": entry["entry_id"],
                "title": entry["title"],
                "position_effect": entry["position_effect"],
                "linked_position_versions": entry["linked_position_versions"],
                "learning_loop": entry["learning_loop"],
            }
            for entry in data["journal_entries"]
            if not position_id
            or set(entry["linked_position_versions"]).intersection(allowed_versions)
        ]
        results = sorted(
            [*position_events, *journal_events],
            key=lambda item: (item["event_date"], item["event_id"]),
        )
    elif view == "layer-map":
        current_version_ids = {
            latest_version(position)["version_id"] for position in positions
        }
        results = [
            node
            for node in graph["nodes"]
            if node["node_type"] == "epistemic_layer"
            and node["version_id"] in current_version_ids
        ]
    elif view == "voice-map":
        current_version_ids = {
            latest_version(position)["version_id"] for position in positions
        }
        layer_prefixes = {
            _layer_node_id(version_id, "")
            for version_id in current_version_ids
        }
        results = [
            edge
            for edge in graph["edges"]
            if edge["edge_type"] in {
                "engages_layer",
                "excluded_from_layer",
                "relates_to_layer",
                "comparison_finding",
            }
            and any(edge["target"].startswith(prefix) for prefix in layer_prefixes)
        ]
    elif view == "review-queue":
        review_date = as_of or date.today()
        allowed_position_ids = {position["position_id"] for position in positions}
        due = [
            item
            for item in due_items(data, review_date)
            if item["position_id"] in allowed_position_ids
        ]
        layers = []
        for position in positions:
            version = latest_version(position)
            for layer in version["position"]["epistemic_layers"]:
                layers.append({
                    "position_id": position["position_id"],
                    "version_id": version["version_id"],
                    "layer_id": layer["layer_id"],
                    "label": layer["label"],
                    "confidence": layer["confidence"],
                    "falsifier_status": layer["falsifier_status"],
                    "future_test": layer["falsifier_or_limitation"],
                })
        results = {"as_of": review_date.isoformat(), "due": due, "layers": layers}
    else:
        raise LedgerError(f"unsupported query view {view}")
    return {
        "schema": "strategic-judgment-query-v1",
        "ledger_schema": data["schema"],
        "view": view,
        "position_filter": position_id,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Governed Strategic Judgment Ledger")
    sub = parser.add_subparsers(dest="command", required=True)
    draft = sub.add_parser("draft")
    draft.add_argument("--input", type=Path, required=True)
    draft.add_argument("--object", required=True)
    draft.add_argument("--source-kind", choices=("prompt", "judgment"), required=True)
    journal_draft = sub.add_parser("journal-draft")
    journal_draft.add_argument("--input", type=Path, required=True)
    journal_draft.add_argument("--date", required=True)
    journal_draft.add_argument("--kind", choices=tuple(sorted(JOURNAL_KINDS)), default="daily_reflection")
    journal_approve = sub.add_parser("journal-approve")
    journal_approve.add_argument("--candidate", type=Path, required=True)
    approve = sub.add_parser("approve")
    approve.add_argument("--candidate", type=Path, required=True)
    approve.add_argument("--position-id", required=True)
    approve.add_argument("--object-label", required=True)
    for name in ("recommend", "approve-comparators", "score", "approve-score"):
        command = sub.add_parser(name)
        command.add_argument("--position", required=True)
        if name == "recommend":
            command.add_argument("--candidate", type=Path)
    review = sub.add_parser("review")
    review.add_argument("--position", required=True)
    review.add_argument(
        "--relation",
        choices=("refinement", "revision", "contradiction", "unchanged_review"),
        required=True,
    )
    review.add_argument("--candidate", type=Path)
    due = sub.add_parser("due")
    due.add_argument("--as-of", default=date.today().isoformat())
    due.add_argument("--event")
    query = sub.add_parser("query")
    query.add_argument(
        "--view",
        choices=(
            "current-beliefs",
            "change-history",
            "layer-map",
            "voice-map",
            "review-queue",
        ),
        required=True,
    )
    query.add_argument("--position")
    query.add_argument("--as-of", default=date.today().isoformat())
    graph = sub.add_parser("graph")
    graph.add_argument("--write", action="store_true")
    report = sub.add_parser("report")
    report.add_argument("--write", action="store_true")
    sub.add_parser("validate")
    args = parser.parse_args(argv)
    try:
        if args.command == "draft":
            print(make_candidate(args.input, args.object, args.source_kind))
        elif args.command == "journal-draft":
            print(make_journal_candidate(args.input, args.date, args.kind))
        elif args.command == "journal-approve":
            data = load_ledger()
            entry = approve_journal_candidate(data, args.candidate)
            write_artifacts(data)
            print(json.dumps(entry, indent=2))
        elif args.command == "approve":
            approve_candidate(args.candidate, args.position_id, args.object_label)
            write_artifacts(load_ledger(), write_source=False)
            print(f"approved {args.position_id}")
        elif args.command == "due":
            print(json.dumps(due_items(load_ledger(), date.fromisoformat(args.as_of), args.event), indent=2))
        elif args.command == "query":
            print(json.dumps(
                query_ledger(
                    load_ledger(),
                    args.view,
                    position_id=args.position,
                    as_of=date.fromisoformat(args.as_of),
                ),
                indent=2,
            ))
        elif args.command == "graph":
            data = load_ledger()
            rendered = _json_text(build_graph(data))
            if args.write:
                GRAPH_PATH.write_text(rendered, encoding="utf-8")
                print(GRAPH_PATH)
            else:
                print(rendered, end="")
        elif args.command == "report":
            data = load_ledger()
            rendered = render_report(data)
            if args.write:
                write_artifacts(data, write_source=False)
                print(REPORT_PATH)
            else:
                print(rendered, end="")
        elif args.command == "validate":
            errors = validate_ledger()
            if errors:
                print("\n".join(errors), file=sys.stderr)
                return 1
            print("strategic judgment ledger: valid")
        else:
            data = load_ledger()
            if args.command == "recommend":
                result = recommend_for_position(data, args.position, args.candidate)
            elif args.command == "approve-comparators":
                approve_comparators(data, args.position)
                result = latest_version(find_position(data, args.position))["comparator_set"]
            elif args.command == "score":
                result = score_position(data, args.position)
            elif args.command == "approve-score":
                approve_score(data, args.position)
                result = latest_version(find_position(data, args.position))["comparison"]
            else:
                result = review_position(data, args.position, args.relation, args.candidate)
            write_artifacts(data)
            print(json.dumps(result, indent=2))
        return 0
    except (LedgerError, OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"operator-position: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

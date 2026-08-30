from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Iterable

import archive_library


REPO_ROOT = Path(__file__).resolve().parent.parent
PRIVATE_PACKET_ROOT = REPO_ROOT / ".mira-private" / "library" / "reasoning" / "geo-pilot"
PACKET_ROOT_ENV = "MIRA_CORE_LIBRARY_REASONING_ROOT"
TEXT_ROOTS_ENV = "MIRA_CORE_LIBRARY_REASONING_TEXT_ROOTS"
DISPOSITIONS = {"adopted", "narrowed", "redirected", "rejected", "held"}
EFFECTS = {
    "changed-mechanism",
    "introduced-credible-alternative",
    "exposed-anachronism",
    "prevented-overclaim",
    "improved-falsifier",
    "no-material-change",
}
FAILURE_TAGS = {
    "irrelevant-lexical-match", "editorial-apparatus", "missing-active-body",
    "wrong-analytic-role", "insufficient-context", "translation-ambiguity",
    "shared-lineage", "anachronism", "representation-gap", "crisis-object-mismatch",
    "evidence-laundering-risk",
}
ABLATION_METRICS = {
    "mechanism_clarity", "evidence_integrity", "credible_rival_quality",
    "anachronism_control", "representation_honesty", "decision_usefulness",
    "prose_burden", "conclusion_improvement",
}
CALIBRATION_GROUPS = {"calibration", "representative", "holdout"}
ROUTING_METRICS = {
    "candidates_reviewed", "candidates_accepted", "irrelevant_candidates", "missing_bodies",
    "review_minutes", "credible_rivals_accepted", "anachronism_failures",
    "evidence_laundering_failures", "operational_skip_expected", "operational_skip_correct",
}
STRUCTURAL_AXES = (
    "technology", "scale", "sovereignty", "political-economy", "ideology",
    "information-speed", "nuclear-deterrence", "international-system",
)
MECHANISM_PROFILES = {
    "passage-legitimacy-order": {
        "terms": {"passage", "coercion", "legitimacy", "order", "bargaining", "regional"},
        "candidates": (
            ("LIB-ANCIENT-AUTHOR-002-KAUTILYA", "mechanism-anchor"),
            ("LIB-ANCIENT-AUTHOR-027-THUCYDIDES", "mechanism-anchor"),
            ("LIB-MEDIEVAL-AUTHORITY-033-IBN-KHALDUN", "credible-rival"),
            ("LIB-COLONIAL-AUTHORITY-065-GROTIUS-MARE-LIBERUM", "contextual-witness"),
            ("LIB-COLONIAL-AUTHORITY-070-OTTOMAN-KANUN", "contextual-witness"),
        ),
    },
    "mobilization-alliance-capacity": {
        "terms": {"mobilization", "alliance", "capacity", "industrial", "exhaustion", "escalation", "war"},
        "candidates": (
            ("LIB-ANCIENT-AUTHOR-010-SUNZI", "mechanism-anchor"),
            ("LIB-ANCIENT-AUTHOR-027-THUCYDIDES", "credible-rival"),
            ("LIB-ANCIENT-AUTHOR-029-POLYBIUS", "credible-rival"),
            ("LIB-MEDIEVAL-AUTHORITY-002-PROCOPIUS", "contextual-witness"),
            ("LIB-INDUSTRIAL-AUTHORITY-012-TOLSTOY", "contextual-witness"),
        ),
    },
    "coercive-commerce-transition": {
        "terms": {"sanctions", "commerce", "trade", "substitution", "economic", "institutional", "adaptation"},
        "candidates": (
            ("LIB-COLONIAL-AUTHORITY-038-ADAM-SMITH", "mechanism-anchor"),
            ("LIB-COLONIAL-AUTHORITY-039-EIC-CHARTERS", "mechanism-anchor"),
            ("LIB-COLONIAL-AUTHORITY-065-GROTIUS-MARE-LIBERUM", "credible-rival"),
            ("LIB-INDUSTRIAL-AUTHORITY-029-MARX", "contextual-witness"),
            ("LIB-INDUSTRIAL-AUTHORITY-033-WEBER", "contextual-witness"),
        ),
    },
}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'-]+")
CHROME_RE = re.compile(
    r"^(project gutenberg|start of (the )?project gutenberg|end of (the )?project gutenberg|"
    r"jump to (navigation|search)|this page was last edited|retrieved from )",
    re.IGNORECASE,
)


class ReasoningError(ValueError):
    pass


def tokens(value: str) -> set[str]:
    return {item for item in TOKEN_RE.findall(value.lower()) if len(item) > 2}


def source_text(source: dict[str, Any]) -> str:
    fields: list[Any] = [
        source.get("title"), source.get("author"), source.get("notes"),
        source.get("era_basis"), source.get("source_type"),
        source.get("coverage_notes"), source.get("date_label"),
        *(source.get("civilization_tags") or []),
        *(source.get("secondary_eras") or []),
    ]
    return " ".join(str(item) for item in fields if item)


def matching_profiles(query_tokens: set[str]) -> list[str]:
    return [
        name for name, profile in MECHANISM_PROFILES.items()
        if len(query_tokens & profile["terms"]) >= 2
    ]


def profile_role(source_id: str, profiles: Iterable[str], source_type: str = "") -> str:
    learned = learned_role(profiles, source_id)
    if learned:
        return learned
    for name in profiles:
        for candidate_id, role in MECHANISM_PROFILES[name]["candidates"]:
            if candidate_id == source_id:
                return role
    return "contextual-witness" if source_type in {"legal", "literary", "primary", "reference"} else "mechanism-anchor"


def routing_decision(question: str, mechanism: str) -> dict[str, Any]:
    query_tokens = tokens(f"{question} {mechanism}")
    profiles = matching_profiles(query_tokens)
    skip_changes = [row for row in active_routing_memory().get("changes", []) if row.get("kind") == "skip-condition"]
    profiles = [name for name in profiles if not any(row.get("profile_id") == name and set(row.get("terms", [])) <= query_tokens for row in skip_changes)]
    operational_only = bool(query_tokens & {"operational", "thin", "report"}) and not profiles
    return {
        "decision": "skip" if operational_only or not profiles else "invoke",
        "profiles": profiles,
        "reason": (
            "no governed historical mechanism profile cleared the relevance floor"
            if operational_only or not profiles
            else "historical mechanism profile cleared the two-term relevance floor"
        ),
    }


def score_source(source: dict[str, Any], query_tokens: set[str], profiles: list[str]) -> int:
    haystack = source_text(source).lower()
    score = sum(3 for item in query_tokens if item in haystack)
    score += sum(2 for item in query_tokens if item in str(source.get("title", "")).lower())
    if source.get("text_status") in {"available", "verified"}:
        score += 2
    if source.get("coverage_status") not in {"metadata-only", "unknown", None}:
        score += 1
    preferred = {
        source_id
        for name in profiles
        for source_id, _ in MECHANISM_PROFILES[name]["candidates"]
    }
    if source.get("source_id") in preferred:
        score += 20
    return score + learned_adjustment(profiles, str(source.get("source_id")))


def ranked_sources(question: str, mechanism: str, *, limit: int = 20, profiles: list[str] | None = None) -> list[dict[str, Any]]:
    registry = archive_library.load_registry()
    query_tokens = tokens(f"{question} {mechanism}")
    profiles = matching_profiles(query_tokens) if profiles is None else profiles
    ranked = [
        (score_source(source, query_tokens, profiles), source)
        for source in registry.get("sources", [])
        if source.get("subject_era") != "digital"
    ]
    ranked.sort(key=lambda item: (-item[0], str(item[1].get("source_id"))))
    positive = [source for score, source in ranked if score > 0]
    return positive[:limit]


def family_key(source: dict[str, Any]) -> str:
    tags = source.get("civilization_tags") or ["unclassified"]
    return f"{source.get('subject_era', 'unknown')}:{tags[0]}:{source.get('source_type', 'unknown')}"


def pre_scan(question: str, mechanism: str, limit: int = 5) -> dict[str, Any]:
    decision = routing_decision(question, mechanism)
    families: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in ranked_sources(question, mechanism, profiles=decision["profiles"]) if decision["decision"] == "invoke" else []:
        key = family_key(source)
        if key in seen:
            continue
        seen.add(key)
        families.append({
            "family_id": key,
            "era": source.get("subject_era"),
            "civilization_tags": source.get("civilization_tags", []),
            "source_type": source.get("source_type"),
            "representative_source_id": source.get("source_id"),
            "routing_basis": "metadata-overlap-only; not an adopted analogy",
        })
        if len(families) == limit:
            break
    return {
        "stage": "pre-scan",
        "routing": decision,
        "question": question,
        "mechanism": mechanism,
        "families": families,
        "family_limit": limit,
        "passage_retrieval_performed": False,
        "authority_boundary": "Candidate historical families only; Geo-Strategy owns interpretation.",
    }


def body_records(source: dict[str, Any]) -> list[dict[str, Any]]:
    bodies = [dict(body) for body in archive_library.source_text_bodies(source)]
    single = archive_library.single_body_from_source(source)
    if not bodies and single:
        bodies = [dict(single)]
    return bodies


def reasoning_text_roots(environment: dict[str, str] | None = None) -> list[Path]:
    source = os.environ if environment is None else environment
    configured = str(source.get(TEXT_ROOTS_ENV) or "").strip()
    roots = [Path(item).expanduser().resolve() for item in configured.split(os.pathsep) if item.strip()]
    fallback = archive_library.resolve_text_root(source).resolve()
    if fallback not in roots:
        roots.append(fallback)
    for root in roots:
        if not private_carrier_path_allowed(root):
            raise ReasoningError(f"reasoning text root must be private: {root}")
    return roots


def body_state(body: dict[str, Any]) -> tuple[str, Path | None]:
    raw = str(body.get("text_location") or "").strip()
    if raw.startswith("library-text://"):
        relative = raw.removeprefix("library-text://").lstrip("/")
        paths = [(root / relative).resolve() for root in reasoning_text_roots() if (root / relative).is_file()]
    else:
        path = archive_library.resolve_text_location(raw)
        if path and path.is_file():
            resolved = path.resolve()
            if not private_carrier_path_allowed(resolved):
                return "outside-private-root", None
            paths = [resolved]
        else:
            paths = []
    if not paths:
        return "missing", None
    hashes = {hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    if len(hashes) > 1:
        return "root-conflict", None
    expected = str(body.get("text_sha256") or "")
    actual = next(iter(hashes))
    return (("hash-verified", paths[0]) if expected and actual == expected else ("hash-mismatch", None))


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def extract_units(path: Path) -> tuple[str, list[dict[str, str]]]:
    if path.suffix.lower() == ".xml":
        try:
            root = ET.parse(path).getroot()
        except (OSError, ET.ParseError):
            return "unreadable", []
        body = next((item for item in root.iter() if item.tag.rsplit("}", 1)[-1] == "body"), None)
        if body is None:
            return "tei-body-v1", []
        units, section = [], ""
        selected_blocks = {"p", "ab"}
        def walk(item: ET.Element, inside_selected: bool = False) -> None:
            nonlocal section
            name = item.tag.rsplit("}", 1)[-1]
            value = _clean(" ".join(item.itertext()))
            if name == "head" and value:
                section = value[:200]
            emit = name in selected_blocks or (name == "l" and not inside_selected)
            if emit and value:
                locator = item.attrib.get("n") or item.attrib.get("{http://www.w3.org/XML/1998/namespace}id") or str(len(units) + 1)
                units.append({"locator": f"tei:{name}:{locator}", "section": section, "text": value})
            for child in item:
                walk(child, inside_selected or emit)
        walk(body)
        return "tei-body-v1", units
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "unreadable", []
    units, section = [], ""
    for raw_paragraph in re.split(r"\n\s*\n", text):
        value = _clean(raw_paragraph)
        if not value or CHROME_RE.match(value):
            continue
        if len(value) < 120 and (value.isupper() or value.startswith(("CHAPTER ", "BOOK ", "PART "))):
            section = value[:200]
            continue
        units.append({"locator": f"paragraph:{len(units) + 1}", "section": section, "text": value})
    return "text-paragraph-v2", units


def paragraph_candidates(path: Path, query_tokens: set[str], limit: int = 2, phrases: Iterable[str] = ()) -> tuple[str, list[dict[str, Any]]]:
    method, units = extract_units(path)
    scored = []
    for index, unit in enumerate(units):
        lowered = unit["text"].lower()
        score = sum(1 for token in query_tokens if re.search(rf"\b{re.escape(token)}\b", lowered))
        score += sum(2 for phrase in phrases if phrase and phrase.lower() in lowered)
        score += sum(1 for token in query_tokens if token in unit["section"].lower())
        if score:
            scored.append((score, index, unit))
    scored.sort(key=lambda item: (-item[0], item[1]))
    rows = []
    for score, index, unit in scored[:limit]:
        excerpt = unit["text"][:600]
        rows.append({
            "locator": unit["locator"], "section": unit["section"], "match_score": score,
            "text": excerpt, "context_before": units[index - 1]["text"][:300] if index else "",
            "context_after": units[index + 1]["text"][:300] if index + 1 < len(units) else "",
            "text_sha256": hashlib.sha256(excerpt.encode("utf-8")).hexdigest(),
            "extraction_method": method, "private_only": True,
        })
    return method, rows


def select_sources(ranked: list[dict[str, Any]], limit: int = 4) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    families: set[str] = set()
    for source in ranked:
        key = family_key(source)
        if key in families and len(selected) >= 2:
            continue
        selected.append(source)
        families.add(key)
        if len(selected) == limit:
            break
    return selected


def representation_gaps(selected: Iterable[dict[str, Any]]) -> list[str]:
    rows = list(selected)
    gaps: list[str] = []
    eras = {str(row.get("subject_era")) for row in rows}
    languages = {
        str(body.get("language") or "unknown")
        for row in rows for body in body_records(row)
    }
    types = {str(row.get("source_type")) for row in rows}
    if len(eras) == 1:
        gaps.append("single-era candidate set")
    if languages <= {"English", "en", "unknown", ""}:
        gaps.append("no demonstrated original-language perspective in selected bodies")
    if not types & {"literary", "primary", "legal", "reference"}:
        gaps.append("no administrative, legal, literary, or primary witness selected")
    gaps.append("survival, canon, and edition-access bias remain unmeasured by metadata ranking")
    return gaps


def geo_packet(run_date: str, crisis_object: str, mechanism: str) -> dict[str, Any]:
    query_tokens = tokens(f"{crisis_object} {mechanism}")
    words = TOKEN_RE.findall(f"{crisis_object} {mechanism}".lower())
    query_phrases = {" ".join(words[index:index + 2]) for index in range(len(words) - 1)}
    decision = routing_decision(crisis_object, mechanism)
    ranked = ranked_sources(crisis_object, mechanism, profiles=decision["profiles"]) if decision["decision"] == "invoke" else []
    selected = select_sources(ranked)
    candidates: list[dict[str, Any]] = []
    passage_total = 0
    for source in selected:
        bodies = body_records(source)
        body_rows: list[dict[str, Any]] = []
        for body in bodies:
            state, path = body_state(body)
            passages = []
            extraction_method = "none"
            body_id = str(body.get("body_id"))
            body_change = learned_body_adjustment(decision["profiles"], str(source.get("source_id")), body_id)
            suppressed = learned_extraction_suppressed(decision["profiles"], body_id)
            if state == "hash-verified" and path is not None and passage_total < 8 and not suppressed:
                extraction_method, passages = paragraph_candidates(path, query_tokens, limit=min(2, 8 - passage_total), phrases=query_phrases)
                if body_change:
                    for passage in passages:
                        passage["match_score"] += body_change
                    passages = [passage for passage in passages if passage["match_score"] > 0]
                passage_total += len(passages)
            body_rows.append({
                "body_id": body.get("body_id"),
                "work_title": body.get("work_title"),
                "edition_label": body.get("edition_label"),
                "language": body.get("language"),
                "coverage_status": body.get("coverage_status"),
                "hash_state": state,
                "extraction_method": extraction_method,
                "routing_suppressed": suppressed,
                "passages": passages,
            })
        candidates.append({
            "source_id": source.get("source_id"),
            "authority": source.get("author"),
            "title": source.get("title"),
            "era": source.get("subject_era"),
            "civilization_tags": source.get("civilization_tags", []),
            "source_type": source.get("source_type"),
            "coverage_status": source.get("coverage_status"),
            "analytic_role": profile_role(str(source.get("source_id")), decision["profiles"], str(source.get("source_type"))),
            "textual_lineage": [],
            "intellectual_lineage": [],
            "lineage_independence": "unassessed",
            "representation_limitations": ["requires Geo-Strategy review"],
            "bodies": body_rows,
            "analogy": {
                "shared_mechanism": "",
                "decisive_structural_differences": [],
                "structural_axes_considered": list(STRUCTURAL_AXES),
                "evidence_needed": "",
                "rejection_condition": "",
            },
            "concept_bridge": {
                "source_term": "",
                "language": "",
                "translation": "",
                "historical_meaning": "",
                "modern_analytic_equivalent": "",
                "non_equivalence": "",
            },
            "disposition": None,
            "effect_on_judgment": [],
            "failure_tags": [],
            "adjudicated_role": None,
        })
    packet = {
        "schema_version": "mira-library-geo-pilot-v2",
        "packet_id": "MLGP-" + hashlib.sha256(
            f"{run_date}|{crisis_object}|{mechanism}".encode("utf-8")
        ).hexdigest()[:16],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "date": run_date,
        "crisis_object": crisis_object,
        "provisional_mechanism": mechanism,
        "crisis_signature": hashlib.sha256(crisis_object.encode("utf-8")).hexdigest(),
        "pre_scan": pre_scan(crisis_object, mechanism),
        "routing": decision,
        "candidates": candidates,
        "representation_gaps": representation_gaps(selected),
        "retrieval_cost": {"candidate_count": len(candidates), "passage_count": passage_total},
        "review_state": (
            "pending-geo-strategy-adjudication" if candidates else "skipped-no-historical-profile"
        ),
        "packet_effect": [] if candidates else ["no-material-change"],
        "evidence_boundary": (
            "Historical retrieval cannot verify current events, resolve operational claims, "
            "or supply statistical base rates."
        ),
        "mutation_boundary": "Library registry and source bodies unchanged; packet is private.",
    }
    return packet


def packet_path(packet: dict[str, Any]) -> Path:
    return resolve_packet_root() / f"{packet['date']}-{packet['packet_id']}.json"


def resolve_packet_root() -> Path:
    configured = os.environ.get(PACKET_ROOT_ENV)
    root = Path(configured).expanduser() if configured else PRIVATE_PACKET_ROOT
    resolved = root.resolve()
    if not private_carrier_path_allowed(resolved):
        raise ReasoningError(f"reasoning packet root must be inside .mira-private; C:/private is legacy import-only: {resolved}")
    return resolved


def private_carrier_root() -> Path:
    resolved = PRIVATE_PACKET_ROOT.resolve()
    for candidate in (resolved, *resolved.parents):
        if candidate.name == ".mira-private":
            return candidate
    return (REPO_ROOT / ".mira-private").resolve()


def private_carrier_path_allowed(path: Path) -> bool:
    resolved = path.resolve()
    carrier = private_carrier_root()
    return resolved == carrier or carrier in resolved.parents


def save_private_packet(packet: dict[str, Any]) -> Path:
    resolve_packet_root().mkdir(parents=True, exist_ok=True)
    target = packet_path(packet)
    target.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def validate_adjudication(packet: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for row in packet.get("candidates", []):
        source_id = row.get("source_id", "unknown")
        if row.get("disposition") not in DISPOSITIONS:
            failures.append(f"{source_id} has invalid or missing disposition")
            continue
        if row["disposition"] in {"adopted", "narrowed", "redirected"}:
            analogy = row.get("analogy", {})
            bridge = row.get("concept_bridge", {})
            if not analogy.get("shared_mechanism"):
                failures.append(f"{source_id} adopted without shared mechanism")
            if not analogy.get("decisive_structural_differences"):
                failures.append(f"{source_id} adopted without structural difference")
            if not analogy.get("rejection_condition"):
                failures.append(f"{source_id} adopted without rejection condition")
            if not bridge.get("historical_meaning") or not bridge.get("non_equivalence"):
                failures.append(f"{source_id} adopted without complete concept bridge")
        invalid_effects = sorted(set(row.get("effect_on_judgment", [])) - EFFECTS)
        invalid_tags = sorted(set(row.get("failure_tags", [])) - FAILURE_TAGS)
        if invalid_effects:
            failures.append(f"{source_id} has invalid effects: {', '.join(invalid_effects)}")
        if invalid_tags:
            failures.append(f"{source_id} has invalid failure tags: {', '.join(invalid_tags)}")
    if not packet.get("packet_effect"):
        failures.append("packet effect is missing")
    elif set(packet["packet_effect"]) - EFFECTS:
        failures.append("packet effect contains unsupported values")
    return failures


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReasoningError(f"expected JSON object: {path}")
    return value


def feedback_path() -> Path:
    return resolve_packet_root() / "learning" / "events.jsonl"


def append_feedback(packet: dict[str, Any], adjudication: dict[str, Any]) -> int:
    path = feedback_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    profiles = packet.get("routing", {}).get("profiles", [])
    review_minutes = adjudication.get("review_minutes")
    skip_condition_terms = sorted(set(adjudication.get("skip_condition_terms", [])))
    existing = read_feedback()
    existing_ids = {row.get("event_id") for row in existing}
    latest = {(row.get("packet_id"), row.get("source_id")): row for row in existing}
    events = []
    for row in packet.get("candidates", []):
        observation = {
            "disposition": row.get("disposition"), "effect_on_judgment": row.get("effect_on_judgment", []),
            "failure_tags": row.get("failure_tags", []), "adjudicated_role": row.get("adjudicated_role"),
            "skip_condition_terms": skip_condition_terms,
        }
        routing_digest = hashlib.sha256(json.dumps(observation, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        event_id = hashlib.sha256(f"{packet.get('packet_id')}|{row.get('source_id')}|{routing_digest}".encode("utf-8")).hexdigest()
        if event_id in existing_ids:
            continue
        events.append({
            "schema_version": "mira-library-routing-observation-v1",
            "event_id": event_id,
            "routing_digest": routing_digest,
            "supersedes_event_id": latest.get((packet.get("packet_id"), row.get("source_id")), {}).get("event_id"),
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "packet_id": packet.get("packet_id"),
            "profile_ids": profiles,
            "crisis_signature": packet.get("crisis_signature") or hashlib.sha256(str(packet.get("crisis_object", "")).encode("utf-8")).hexdigest(),
            "source_id": row.get("source_id"),
            "body_ids": [body.get("body_id") for body in row.get("bodies", [])],
            "extraction_methods": sorted({body.get("extraction_method") for body in row.get("bodies", []) if body.get("extraction_method") not in {None, "none"}}),
            "proposed_role": row.get("analytic_role"),
            "adjudicated_role": row.get("adjudicated_role"),
            "disposition": row.get("disposition"),
            "effect_on_judgment": row.get("effect_on_judgment", []),
            "failure_tags": row.get("failure_tags", []),
            "retrieval_cost": packet.get("retrieval_cost", {}),
            "review_minutes": review_minutes if isinstance(review_minutes, (int, float)) and review_minutes >= 0 else None,
            "skip_condition_terms": skip_condition_terms,
        })
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    return len(events)


def adjudicate(packet_file: Path, adjudication_file: Path, *, check: bool) -> dict[str, Any]:
    packet = load_json(packet_file)
    adjudication = load_json(adjudication_file)
    rows = {row.get("source_id"): row for row in adjudication.get("candidates", [])}
    for candidate in packet.get("candidates", []):
        update = rows.get(candidate.get("source_id"))
        if update:
            for field in ("textual_lineage", "intellectual_lineage", "lineage_independence", "representation_limitations", "analogy", "concept_bridge", "disposition", "effect_on_judgment", "failure_tags", "adjudicated_role"):
                if field in update:
                    candidate[field] = update[field]
    packet["packet_effect"] = adjudication.get("packet_effect", [])
    packet["review_state"] = "adjudicated"
    failures = validate_adjudication(packet)
    skip_terms = set(adjudication.get("skip_condition_terms", []))
    allowed_skip_terms = {term for profile in packet.get("routing", {}).get("profiles", []) for term in MECHANISM_PROFILES[profile]["terms"]}
    if skip_terms - allowed_skip_terms:
        failures.append("skip condition contains terms outside the matched mechanism profiles")
    if skip_terms:
        if packet.get("packet_effect") != ["no-material-change"]:
            failures.append("skip condition requires packet effect no-material-change only")
        if any(row.get("disposition") not in {"rejected", "held"} for row in packet.get("candidates", [])):
            failures.append("skip condition requires every candidate to be rejected or held")
        if any("crisis-object-mismatch" not in row.get("failure_tags", []) for row in packet.get("candidates", [])):
            failures.append("skip condition requires crisis-object-mismatch on every candidate")
    if failures:
        return {"status": "invalid", "failures": failures, "packet": packet, "written": False}
    events_appended = 0
    if not check:
        packet_file.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        events_appended = append_feedback(packet, adjudication)
    return {"status": "ok", "failures": [], "packet": packet, "written": not check, "learning_events_appended": events_appended}


def read_feedback() -> list[dict[str, Any]]:
    path = feedback_path()
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def effective_feedback(events: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    latest: dict[tuple[Any, Any], dict[str, Any]] = {}
    for row in read_feedback() if events is None else events:
        latest[(row.get("packet_id"), row.get("source_id"))] = row
    return list(latest.values())


def proposal_changes(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events = effective_feedback(events)
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        for profile in event.get("profile_ids", []):
            groups[(profile, str(event.get("source_id")))].append(event)
    changes = []
    positive_states = {"adopted", "narrowed", "redirected"}
    for (profile, source_id), rows in sorted(groups.items()):
        signatures = {row.get("crisis_signature") for row in rows if row.get("crisis_signature")}
        if len(rows) < 3 or len(signatures) < 2:
            continue
        counts = Counter(row.get("disposition") for row in rows)
        positive = sum(counts[state] for state in positive_states)
        negative = counts["rejected"]
        adjustment = 2 if positive >= 3 and negative == 0 else (-3 if negative >= 3 and positive == 0 else 0)
        if adjustment:
            changes.append({
                "kind": "source-weight", "profile_id": profile, "source_id": source_id,
                "adjustment": adjustment,
                "supporting_observations": [row.get("packet_id") for row in rows if (row.get("disposition") in positive_states) == (adjustment > 0)],
                "contradicting_observations": [row.get("packet_id") for row in rows if (row.get("disposition") in positive_states) != (adjustment > 0)],
                "failure_tags": sorted({tag for row in rows for tag in row.get("failure_tags", [])}),
            })
        adjudicated_roles = {row.get("adjudicated_role") for row in rows if row.get("adjudicated_role")}
        if len(adjudicated_roles) == 1 and all(row.get("adjudicated_role") for row in rows):
            changes.append({
                "kind": "role-override", "profile_id": profile, "source_id": source_id,
                "role": next(iter(adjudicated_roles)),
                "supporting_observations": [row.get("packet_id") for row in rows],
                "contradicting_observations": [],
            })
        if all("editorial-apparatus" in row.get("failure_tags", []) for row in rows):
            body_ids = {body_id for row in rows for body_id in row.get("body_ids", [])}
            methods = {method for row in rows for method in row.get("extraction_methods", [])}
            for body_id in sorted(body_ids):
                changes.append({
                    "kind": "extraction-suppression", "profile_id": profile, "body_id": body_id,
                    "extraction_methods": sorted(methods),
                    "supporting_observations": [row.get("packet_id") for row in rows],
                    "contradicting_observations": [],
                })
        if negative >= 3 and positive == 0:
            for body_id in sorted({body_id for row in rows for body_id in row.get("body_ids", [])}):
                changes.append({
                    "kind": "body-weight", "profile_id": profile, "source_id": source_id,
                    "body_id": body_id, "adjustment": -3,
                    "supporting_observations": [row.get("packet_id") for row in rows],
                    "contradicting_observations": [],
                })
    skip_groups: dict[tuple[str, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        terms = tuple(sorted(set(event.get("skip_condition_terms", []))))
        if not terms:
            continue
        for profile in event.get("profile_ids", []):
            skip_groups[(profile, terms)].append(event)
    for (profile, terms), rows in sorted(skip_groups.items()):
        packets = {row.get("packet_id") for row in rows}
        crises = {row.get("crisis_signature") for row in rows}
        if len(packets) >= 3 and len(crises) >= 2:
            changes.append({
                "kind": "skip-condition", "profile_id": profile, "terms": list(terms),
                "supporting_observations": sorted(packets), "contradicting_observations": [],
            })
    return changes


def active_memory_path() -> Path:
    return resolve_packet_root() / "routing" / "active.json"


def memory_digest(value: dict[str, Any]) -> str:
    unsigned = dict(value)
    unsigned.pop("memory_sha256", None)
    return hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def validate_memory(memory: dict[str, Any]) -> None:
    if memory.get("schema_version") != "mira-library-routing-memory-v1" or memory.get("active") is not True:
        raise ReasoningError("invalid active routing memory")
    if memory.get("memory_sha256") != memory_digest(memory):
        raise ReasoningError("active routing memory digest mismatch")
    proposal = dict(memory)
    proposal["schema_version"] = "mira-library-routing-proposal-v1"
    proposal["active"] = False
    proposal.pop("activated_at", None)
    proposal.pop("memory_sha256", None)
    validate_proposal(proposal)


def atomic_json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{time.time_ns()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def active_routing_memory() -> dict[str, Any]:
    path = active_memory_path()
    if not path.is_file():
        return {"changes": []}
    value = load_json(path)
    validate_memory(value)
    return value


def learned_adjustment(profiles: Iterable[str], source_id: str) -> int:
    profile_set = set(profiles)
    total = sum(int(row.get("adjustment", 0)) for row in active_routing_memory().get("changes", []) if row.get("kind") == "source-weight" and row.get("profile_id") in profile_set and row.get("source_id") == source_id)
    return max(-5, min(5, total))


def learned_body_adjustment(profiles: Iterable[str], source_id: str, body_id: str) -> int:
    profile_set = set(profiles)
    total = sum(int(row.get("adjustment", 0)) for row in active_routing_memory().get("changes", []) if row.get("kind") == "body-weight" and row.get("profile_id") in profile_set and row.get("source_id") == source_id and row.get("body_id") == body_id)
    return max(-5, min(5, total))


def learned_role(profiles: Iterable[str], source_id: str) -> str | None:
    profile_set = set(profiles)
    rows = [row for row in active_routing_memory().get("changes", []) if row.get("kind") == "role-override" and row.get("profile_id") in profile_set and row.get("source_id") == source_id]
    return str(rows[-1].get("role")) if rows else None


def learned_extraction_suppressed(profiles: Iterable[str], body_id: str) -> bool:
    profile_set = set(profiles)
    return any(row.get("kind") == "extraction-suppression" and row.get("profile_id") in profile_set and row.get("body_id") == body_id for row in active_routing_memory().get("changes", []))


def learning_status() -> dict[str, Any]:
    root = resolve_packet_root()
    events = read_feedback()
    proposal_root = root / "routing" / "proposals"
    active_status, active_digest = "absent", None
    if active_memory_path().is_file():
        try:
            memory = active_routing_memory()
            active_status, active_digest = "valid", memory.get("memory_sha256")
        except (OSError, json.JSONDecodeError, ReasoningError):
            active_status = "invalid"
    return {
        "status": "ok", "event_count": len(events),
        "distinct_crisis_count": len({row.get("crisis_signature") for row in events}),
        "eligible_change_count": len(proposal_changes(events)),
        "proposal_count": len(list(proposal_root.glob("*.json"))) if proposal_root.exists() else 0,
        "active_memory": active_status == "valid", "active_memory_status": active_status,
        "active_memory_sha256": active_digest,
        "authority_boundary": "Status does not authorize routing-memory activation or recursive-learning admission.",
    }


def proposal_digest(value: dict[str, Any]) -> str:
    unsigned = dict(value)
    unsigned.pop("proposal_sha256", None)
    return hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def propose_routing_update(*, check: bool) -> dict[str, Any]:
    changes = proposal_changes(read_feedback())
    if not changes:
        return {"status": "insufficient-evidence", "written": False, "changes": [], "minimum": "three consistent adjudications across two crisis signatures"}
    proposal = {"schema_version": "mira-library-routing-proposal-v1", "created_at": datetime.now(timezone.utc).isoformat(), "changes": changes, "active": False, "authority_boundary": "Proposal only; explicit activation required."}
    proposal["proposal_sha256"] = proposal_digest(proposal)
    target = resolve_packet_root() / "routing" / "proposals" / f"MLRM-{proposal['proposal_sha256'][:16]}.json"
    if not check:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(proposal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"status": "ok", "written": not check, "private_proposal": str(target), "proposal": proposal}


def validate_proposal(proposal: dict[str, Any]) -> None:
    if proposal.get("schema_version") != "mira-library-routing-proposal-v1" or not proposal.get("changes"):
        raise ReasoningError("invalid or empty routing proposal")
    if proposal.get("proposal_sha256") != proposal_digest(proposal):
        raise ReasoningError("routing proposal digest mismatch")
    for row in proposal["changes"]:
        kind = row.get("kind")
        if kind in {"source-weight", "body-weight"} and not -5 <= int(row.get("adjustment", 0)) <= 5:
            raise ReasoningError("unsupported or uncapped routing change")
        if kind == "role-override" and row.get("role") not in {"mechanism-anchor", "credible-rival", "contextual-witness"}:
            raise ReasoningError("unsupported routing role")
        if kind == "skip-condition":
            allowed = set(MECHANISM_PROFILES.get(str(row.get("profile_id")), {}).get("terms", set()))
            if not row.get("terms") or set(row["terms"]) - allowed:
                raise ReasoningError("unsupported skip condition")
        if kind not in {"source-weight", "body-weight", "role-override", "extraction-suppression", "skip-condition"}:
            raise ReasoningError("unsupported routing change")


def activate_routing_memory(input_file: Path, *, check: bool) -> dict[str, Any]:
    proposal = load_json(input_file)
    validate_proposal(proposal)
    active = active_memory_path()
    memory = {**proposal, "schema_version": "mira-library-routing-memory-v1", "active": True, "activated_at": datetime.now(timezone.utc).isoformat()}
    memory["memory_sha256"] = memory_digest(memory)
    if not check:
        if active.is_file():
            current = active_routing_memory()
            history = active.parent / "history" / f"{time.time_ns()}-{str(current.get('memory_sha256', 'unknown'))[:16]}.json"
            atomic_json_write(history, current)
        atomic_json_write(active, memory)
    return {"status": "ok", "written": not check, "active_memory": str(active), "proposal_sha256": proposal["proposal_sha256"], "memory_sha256": memory["memory_sha256"]}


def rollback_routing_memory(*, check: bool) -> dict[str, Any]:
    active = active_memory_path()
    history_root = active.parent / "history"
    history = sorted(history_root.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True) if history_root.exists() else []
    if not active.is_file():
        return {"status": "no-active-memory", "written": False}
    if not history:
        return {"status": "no-rollback-version", "written": False}
    prior = load_json(history[0])
    validate_memory(prior)
    if not check:
        atomic_json_write(active, prior)
        history[0].unlink()
    return {"status": "ok", "written": not check, "restored_proposal_sha256": prior.get("proposal_sha256")}


def validate_ablation_review(review: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    case_id = str(review.get("case_id") or "")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,119}", case_id):
        failures.append("ablation review requires safe case_id")
    versions = review.get("versions", {})
    for name in ("without_library", "with_library", "final_voice"):
        version = versions.get(name)
        if not isinstance(version, dict) or not str(version.get("text", "")).strip():
            failures.append(f"ablation review missing version text: {name}")
            continue
        scores = version.get("scores", {})
        if set(scores) != ABLATION_METRICS:
            failures.append(f"ablation review has incomplete metrics: {name}")
        elif any(not isinstance(value, int) or not 1 <= value <= 5 for value in scores.values()):
            failures.append(f"ablation review scores must be integers 1-5: {name}")
    for field in ("materially_improved", "evidence_laundering_failure", "cadence_proportionate"):
        if not isinstance(review.get(field), bool):
            failures.append(f"ablation review requires boolean: {field}")
    if not str(review.get("review_note", "")).strip():
        failures.append("ablation review requires review_note")
    if "calibration_group" in review or "routing_metrics" in review or "comparison_phase" in review:
        if review.get("calibration_group") not in CALIBRATION_GROUPS:
            failures.append("ablation review has invalid calibration_group")
        if review.get("comparison_phase") not in {"baseline", "shadow"}:
            failures.append("ablation review has invalid comparison_phase")
        metrics = review.get("routing_metrics", {})
        if set(metrics) != ROUTING_METRICS:
            failures.append("ablation review has incomplete routing_metrics")
        elif any(not isinstance(value, (int, float)) or value < 0 for value in metrics.values()):
            failures.append("ablation review routing_metrics must be non-negative numbers")
        memory_sha = review.get("routing_memory_sha256")
        if review.get("comparison_phase") == "baseline" and memory_sha != "none":
            failures.append("baseline review requires routing_memory_sha256 none")
        if review.get("comparison_phase") == "shadow" and not re.fullmatch(r"[0-9a-f]{64}", str(memory_sha or "")):
            failures.append("shadow review requires routing memory digest")
        if review.get("comparison_phase") == "shadow" and not str(review.get("comparison_case_id") or "").strip():
            failures.append("shadow review requires comparison_case_id")
    return failures


def record_ablation_review(review_file: Path, *, check: bool) -> dict[str, Any]:
    review = load_json(review_file)
    failures = validate_ablation_review(review)
    if failures:
        return {"status": "invalid", "failures": failures, "written": False}
    payload = dict(review)
    payload["schema_version"] = "mira-library-geo-ablation-v1"
    payload["recorded_at"] = datetime.now(timezone.utc).isoformat()
    payload["advancement_authority"] = "review evidence only; does not authorize architecture expansion"
    target = resolve_packet_root() / f"{payload['case_id']}-review.json"
    if not check:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"status": "ok", "failures": [], "written": not check, "private_review": str(target), "review": payload}


def advancement_status() -> dict[str, Any]:
    root = resolve_packet_root()
    reviews: list[dict[str, Any]] = []
    for path in sorted(root.glob("*-review.json")) if root.exists() else []:
        try:
            review = load_json(path)
        except (OSError, json.JSONDecodeError, ReasoningError):
            continue
        if not validate_ablation_review(review):
            reviews.append(review)
    improved = sum(bool(row.get("materially_improved")) for row in reviews)
    laundering = any(bool(row.get("evidence_laundering_failure")) for row in reviews)
    proportionate = bool(reviews) and all(bool(row.get("cadence_proportionate")) for row in reviews)
    passed = len(reviews) >= 4 and improved >= 3 and not laundering and proportionate
    return {
        "status": "pilot-pass" if passed else "pilot-incomplete-or-failed",
        "review_count": len(reviews),
        "materially_improved_count": improved,
        "evidence_laundering_failure": laundering,
        "cadence_proportionate": proportionate,
        "advancement_ready": passed,
        "authority_boundary": "Status is advisory; architecture expansion requires separate authorization.",
    }


def calibration_status() -> dict[str, Any]:
    root = resolve_packet_root()
    reviews = []
    for path in sorted(root.glob("*-review.json")) if root.exists() else []:
        try:
            row = load_json(path)
        except (OSError, json.JSONDecodeError, ReasoningError):
            continue
        if not validate_ablation_review(row) and row.get("comparison_phase") in {"baseline", "shadow"}:
            reviews.append(row)

    def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
        metrics = [row["routing_metrics"] for row in rows]
        reviewed = sum(item["candidates_reviewed"] for item in metrics)
        skips_expected = sum(item["operational_skip_expected"] for item in metrics)
        return {
            "case_count": len(rows),
            "group_counts": dict(Counter(row["calibration_group"] for row in rows)),
            "candidate_acceptance_rate": (sum(item["candidates_accepted"] for item in metrics) / reviewed) if reviewed else 0.0,
            "irrelevant_retrieval_rate": (sum(item["irrelevant_candidates"] for item in metrics) / reviewed) if reviewed else 0.0,
            "missing_body_rate": (sum(item["missing_bodies"] for item in metrics) / reviewed) if reviewed else 0.0,
            "median_review_minutes": median([item["review_minutes"] for item in metrics]) if metrics else 0.0,
            "credible_rival_yield": (sum(item["credible_rivals_accepted"] for item in metrics) / len(rows)) if rows else 0.0,
            "material_improvement_rate": (sum(bool(row.get("materially_improved")) for row in rows) / len(rows)) if rows else 0.0,
            "anachronism_failures": sum(item["anachronism_failures"] for item in metrics),
            "evidence_laundering_failures": sum(item["evidence_laundering_failures"] for item in metrics),
            "operational_skip_precision": (sum(item["operational_skip_correct"] for item in metrics) / skips_expected) if skips_expected else 1.0,
        }

    baseline_rows = [row for row in reviews if row["comparison_phase"] == "baseline"]
    shadow_rows = [row for row in reviews if row["comparison_phase"] == "shadow"]
    baseline_case_ids = {row.get("case_id") for row in baseline_rows}
    active_digest = None
    try:
        active_digest = active_routing_memory().get("memory_sha256") if active_memory_path().is_file() else None
    except (OSError, json.JSONDecodeError, ReasoningError):
        active_digest = None
    shadow_binding_valid = bool(shadow_rows) and bool(active_digest) and all(
        row.get("routing_memory_sha256") == active_digest and row.get("comparison_case_id") in baseline_case_ids
        for row in shadow_rows
    )
    baseline, shadow = summarize(baseline_rows), summarize(shadow_rows)
    baseline_ready = baseline["case_count"] >= 12 and all(baseline["group_counts"].get(group, 0) >= 4 for group in CALIBRATION_GROUPS)
    shadow_ready = shadow_binding_valid and shadow["case_count"] >= 4 and shadow["group_counts"].get("holdout", 0) >= 4
    irrelevant_reduction = ((baseline["irrelevant_retrieval_rate"] - shadow["irrelevant_retrieval_rate"]) / baseline["irrelevant_retrieval_rate"]) if baseline["irrelevant_retrieval_rate"] else 0.0
    time_reduction = ((baseline["median_review_minutes"] - shadow["median_review_minutes"]) / baseline["median_review_minutes"]) if baseline["median_review_minutes"] else 0.0
    advance = baseline_ready and shadow_ready and irrelevant_reduction >= 0.30 and time_reduction >= 0.20 and shadow["material_improvement_rate"] >= baseline["material_improvement_rate"] and shadow["credible_rival_yield"] >= baseline["credible_rival_yield"] and shadow["evidence_laundering_failures"] == 0 and shadow["operational_skip_precision"] == 1.0
    return {
        "status": "shadow-pass" if advance else "calibration-incomplete-or-failed",
        "baseline_ready": baseline_ready, "shadow_ready": shadow_ready,
        "shadow_binding_valid": shadow_binding_valid, "active_memory_sha256": active_digest,
        "baseline": baseline, "shadow": shadow,
        "irrelevant_retrieval_reduction": irrelevant_reduction,
        "median_review_time_reduction": time_reduction,
        "advancement_ready": advance,
        "authority_boundary": "Measurement is advisory; it does not activate routing memory or admit recursive learning.",
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Mira Library historical pressure-test pilot")
    sub = root.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("pre-scan")
    scan.add_argument("--crisis-object", required=True)
    scan.add_argument("--mechanism", required=True)
    scan.add_argument("--json", action="store_true")
    pilot = sub.add_parser("geo-pilot")
    pilot.add_argument("--date", required=True)
    pilot.add_argument("--crisis-object", required=True)
    pilot.add_argument("--mechanism", required=True)
    pilot.add_argument("--check", action="store_true")
    pilot.add_argument("--json", action="store_true")
    review = sub.add_parser("adjudicate")
    review.add_argument("--packet", type=Path, required=True)
    review.add_argument("--adjudication", type=Path, required=True)
    review.add_argument("--check", action="store_true")
    review.add_argument("--json", action="store_true")
    ablation = sub.add_parser("ablation-review")
    ablation.add_argument("--review", type=Path, required=True)
    ablation.add_argument("--check", action="store_true")
    ablation.add_argument("--json", action="store_true")
    advancement = sub.add_parser("advancement-status")
    advancement.add_argument("--json", action="store_true")
    learning = sub.add_parser("learning-status")
    learning.add_argument("--json", action="store_true")
    calibration = sub.add_parser("calibration-status")
    calibration.add_argument("--json", action="store_true")
    propose = sub.add_parser("propose-routing-update")
    propose.add_argument("--check", action="store_true")
    propose.add_argument("--json", action="store_true")
    activate = sub.add_parser("activate-routing-memory")
    activate.add_argument("--input", type=Path, required=True)
    activate.add_argument("--check", action="store_true")
    activate.add_argument("--json", action="store_true")
    rollback = sub.add_parser("rollback-routing-memory")
    rollback.add_argument("--check", action="store_true")
    rollback.add_argument("--json", action="store_true")
    return root


def main(arguments: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")
    args = parser().parse_args(arguments)
    try:
        if args.command == "pre-scan":
            result = pre_scan(args.crisis_object, args.mechanism)
        elif args.command == "geo-pilot":
            packet = geo_packet(args.date, args.crisis_object, args.mechanism)
            target = None if args.check else save_private_packet(packet)
            result = {"status": "ok", "packet": packet, "private_packet": str(target) if target else None, "written": target is not None}
        elif args.command == "adjudicate":
            result = adjudicate(args.packet, args.adjudication, check=args.check)
        elif args.command == "ablation-review":
            result = record_ablation_review(args.review, check=args.check)
        elif args.command == "advancement-status":
            result = advancement_status()
        elif args.command == "learning-status":
            result = learning_status()
        elif args.command == "calibration-status":
            result = calibration_status()
        elif args.command == "propose-routing-update":
            result = propose_routing_update(check=args.check)
        elif args.command == "activate-routing-memory":
            result = activate_routing_memory(args.input, check=args.check)
        else:
            result = rollback_routing_memory(check=args.check)
    except (ReasoningError, archive_library.LibraryError, OSError, json.JSONDecodeError) as error:
        print(f"library reasoning error: {error}", file=os.sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False) if getattr(args, "json", False) else result)
    allowed = {"ok", "pilot-pass", "pilot-incomplete-or-failed", "calibration-incomplete-or-failed", "shadow-pass", "insufficient-evidence", "no-active-memory", "no-rollback-version"}
    return 0 if result.get("status", "ok") in allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())

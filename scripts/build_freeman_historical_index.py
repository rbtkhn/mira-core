"""Build a deterministic, source-derived historical-reference index for Chas Freeman."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
MANIFEST_PATH = NG_ROOT / "archive" / "source-manifest.json"
OUTPUT_PATH = NG_ROOT / "voices" / "freeman" / "historical-references.md"
MECHANISM_REGISTRY_PATH = NG_ROOT / "voices" / "freeman" / "mechanism-registry.json"
MECHANISM_REVIEW_PATH = NG_ROOT / "voices" / "freeman" / "mechanism-review.json"
REVIEW_DECISIONS_PATH = NG_ROOT / "voices" / "freeman" / "historical-reference-review-decisions.json"
MANUAL_TURN_REVIEW_PATH = NG_ROOT / "work" / "historical-reference" / "july24-manual-turn-review.json"
MECHANISM_VERSION = "1.0"


@dataclass(frozen=True)
class ReferenceRule:
    key: str
    label: str
    period: str
    region: str
    topic: str
    function: str
    patterns: tuple[str, ...]


@dataclass(frozen=True)
class HistoricalIndexAnalysis:
    rows: list[dict]
    occurrences: list[dict]
    rejected: list[dict]
    coverage: list[str]
    review: dict


MECHANISMS = (
    {"id": "M-FR-001", "name": "coercion and strategic backfire", "definition": "External pressure produces resistance, legitimacy loss, or strategic reversal for the coercing power.", "inclusion_tests": ["The quote connects pressure, intervention, sanctions, or regime change to resistance or failure."], "exclusion_tests": ["A reference is merely mentioned without a claim about coercion or consequences."], "counterexample_guidance": "Record cases where pressure produces durable compliance or a favorable settlement."},
    {"id": "M-FR-002", "name": "institutional memory and diplomatic credibility", "definition": "Records, commitments, guarantees, and prior diplomatic conduct shape the credibility of future negotiation.", "inclusion_tests": ["The quote links diplomatic reliability to records, treaties, guarantees, or prior commitments."], "exclusion_tests": ["A diplomatic event is named without a claim about credibility or institutional memory."], "counterexample_guidance": "Record cases where diplomacy succeeds despite broken records or unreliable commitments."},
    {"id": "M-FR-003", "name": "imperial overstretch and power transition", "definition": "Accumulated commitments, dependency, or declining strategic competence weaken a dominant power during systemic transition.", "inclusion_tests": ["The quote connects empire, hegemony, alliance burden, or strategic decline to a change in power."], "exclusion_tests": ["A great power is mentioned without a claim about overextension, dependency, or transition."], "counterexample_guidance": "Record cases where expansion or dominance strengthens rather than exhausts a power."},
    {"id": "M-FR-004", "name": "knowledge transfer and institutional competence", "definition": "Openness, scientific exchange, recordkeeping, and knowledge institutions produce or preserve political competence.", "inclusion_tests": ["The quote links knowledge exchange, science, education, or institutional openness to civilizational capacity."], "exclusion_tests": ["A civilization or cultural period is named without a competence claim."], "counterexample_guidance": "Record cases where closed institutions retain or improve competence."},
    {"id": "M-FR-005", "name": "sovereignty, legitimacy, and historical memory", "definition": "Historical injury, sovereignty claims, and inherited identity shape present resistance and political legitimacy.", "inclusion_tests": ["The quote links remembered injury, territorial legitimacy, or national identity to present conduct."], "exclusion_tests": ["A national event is mentioned without a claim about legitimacy, memory, or sovereignty."], "counterexample_guidance": "Record cases where strategic incentives override inherited historical memory."},
)

MECHANISM_BY_KEY = {
    "bay-of-pigs": ["M-FR-001"], "vietnam-war": ["M-FR-001"], "iraq-war": ["M-FR-001"], "iraq-2003-invasion": ["M-FR-001"], "iraq-regime-change": ["M-FR-001"], "cuba-embargo": ["M-FR-001"],
    "kuwait-liberation": ["M-FR-002"], "gulf-war-1991": ["M-FR-002"], "jcpoa": ["M-FR-002"], "jcpoa-negotiation": ["M-FR-002"], "jcpoa-us-withdrawal": ["M-FR-002"], "us-china-opening-1972": ["M-FR-002"], "nixon-kissinger": ["M-FR-002"],
    "cold-war": ["M-FR-003"], "cold-war-bipolar-order": ["M-FR-003"], "post-cold-war-nato-expansion": ["M-FR-003"], "imperial-overstretch": ["M-FR-003"], "imperial-overstretch-us": ["M-FR-003"], "mongol-empire": ["M-FR-003"], "mongol-empire-exchange": ["M-FR-003"], "timur": ["M-FR-003"], "timur-imperial-memory": ["M-FR-003"], "thucydides-trap": ["M-FR-003"], "thucydides-peloponnesian-analogy": ["M-FR-003"],
    "cultural-revolution": ["M-FR-004"], "renaissance-knowledge": ["M-FR-004"], "renaissance-greek-roman-transmission": ["M-FR-004"], "dark-ages": ["M-FR-004"], "roger-of-sicily": ["M-FR-004"], "roger-sicily-translation": ["M-FR-004"],
    "iranian-revolution": ["M-FR-005"], "iran-1979-revolution": ["M-FR-005"], "iraq-19th-province": ["M-FR-005"], "iraq-kuwait-claim": ["M-FR-005"], "october-7": ["M-FR-005"],
}

MECHANISM_EVIDENCE = {
    "M-FR-001": (r"sanction(?:s|ed|ing)?", r"embargo", r"regime change", r"invasion", r"occupation", r"coerc(?:ion|ive|ed)", r"pressure", r"intervention", r"backfire", r"blowback", r"failed"),
    "M-FR-002": (r"treat(?:y|ies)", r"agreement", r"deal", r"diplom(?:acy|atic)", r"guarantee", r"record(?:s|keeping)?", r"promise", r"commitment", r"reliab(?:le|ility)", r"trust"),
    "M-FR-003": (r"empire", r"imperial", r"hegemon(?:y|ic)", r"overstretch", r"dominance", r"power transition", r"great power", r"dependency", r"decline"),
    "M-FR-004": (r"science", r"knowledge", r"renaissance", r"recordkeeping", r"institution(?:s|al)?", r"education", r"technology", r"competence", r"superstition"),
    "M-FR-005": (r"sovereign(?:ty)?", r"legitimacy", r"historical memory", r"identity", r"territor(?:y|ial)", r"injury", r"national", r"resistance"),
}


RULES = (
    ReferenceRule("bay-of-pigs", "Bay of Pigs", "1961", "Cuba / Caribbean", "coercion and regime consolidation", "precedent", (r"bay of pigs",)),
    ReferenceRule("cultural-revolution", "Great Proletarian Cultural Revolution", "1966–1976", "China", "bureaucracy and institutional destruction", "analogy", (r"great (?:proletarian )?cultural revolution", r"cultural revolution")),
    ReferenceRule("us-china-opening-1972", "1972 US-China opening", "1972", "United States / China", "diplomacy and strategic realignment", "institutional memory", (r"1972 (?:trip|opening).{0,40}china", r"trip to china", r"nixon.{0,20}china")),
    ReferenceRule("nixon-kissinger", "Nixon–Kissinger China strategy", "1970s", "United States / China / USSR", "triangular diplomacy", "diplomatic lesson", (r"kissinger", r"nixon.{0,30}(?:soviet|china)", r"flip.{0,20}russia.{0,20}ally")),
    ReferenceRule("kuwait-liberation", "1991 liberation of Kuwait", "1990–1991", "Kuwait / Iraq / Gulf", "alliance and security guarantees", "institutional memory", (r"liberat(?:ed|ion) kuwait", r"war to liberate kuwait", r"gulf war")),
    ReferenceRule("iraq-19th-province", "Iraq’s ‘19th province’ claim over Kuwait", "1990–1991 and earlier", "Iraq / Kuwait", "sovereignty and territorial claims", "historical correction", (r"19th province", r"nineteenth province")),
    ReferenceRule("vietnam-war", "Vietnam War", "1955–1975", "Vietnam / United States", "war termination and credibility", "precedent", (r"vietnam war", r"war in vietnam")),
    ReferenceRule("iraq-war", "2003 Iraq War and Saddam Hussein", "2003–2011", "Iraq", "intervention and strategic backfire", "precedent", (r"saddam hussein", r"2003 iraq", r"iraq war")),
    ReferenceRule("october-7", "7 October Hamas attack", "2023", "Israel / Palestine", "war and legitimacy", "precedent", (r"october 7", r"october 7th", r"hamas breakout")),
    ReferenceRule("renaissance-knowledge", "Renaissance transmission of Greek and Roman knowledge", "14th–17th centuries", "Europe / Mediterranean / Islamic world", "knowledge transfer and civilizational development", "civilizational comparison", (r"renaissance", r"greek and roman knowledge", r"greek and roman documents")),
    ReferenceRule("dark-ages", "European ‘Dark Ages’", "late antiquity–medieval period", "Europe", "religion, science, and institutional development", "historical correction", (r"dark ages", r"before the renaissance")),
    ReferenceRule("roger-of-sicily", "Roger of Sicily and Arabic–Latin translation", "12th century", "Sicily / Mediterranean", "knowledge transfer", "historical correction", (r"roger of sicily", r"norman ruler of sicily")),
    ReferenceRule("mongol-empire", "Chinggis Khan and the Mongol Empire", "13th century", "Eurasia", "empire and cultural exchange", "civilizational comparison", (r"chengh?is khan", r"chinggis khan", r"mongol empire")),
    ReferenceRule("timur", "Timur / Tamerlane", "14th–15th centuries", "Central Asia / South Asia", "empire and historical memory", "historical correction", (r"tamerlain", r"tamerlane", r"teamur")),
    ReferenceRule("cuba-embargo", "US embargo on Cuba", "1960–present", "Cuba / United States", "isolation and legitimacy", "precedent", (r"embargo on cuba", r"cuba", r"castro regime")),
    ReferenceRule("cold-war", "Cold War", "1947–1991", "Global", "alliances and strategic order", "strategic continuity", (r"cold war", r"during the cold war")),
    ReferenceRule("iranian-revolution", "Iranian Revolution", "1979–present", "Iran", "sovereignty and regime legitimacy", "strategic continuity", (r"islamic revolution", r"iranian revolution")),
    ReferenceRule("jcpoa", "JCPOA / Iran nuclear diplomacy", "2015–present", "Iran / United States", "treaty reliability and diplomacy", "institutional memory", (r"jcpoa", r"nuclear deal")),
    ReferenceRule("imperial-overstretch", "Imperial overstretch and the history of empire", "longue durée", "Global", "power transition", "strategic continuity", (r"history of empire", r"imperial overstretch", r"500 years")),
    ReferenceRule("thucydides-trap", "Thucydides Trap", "classical analogy", "Greece / United States / China", "great-power transition", "analogy", (r"thucydides",)),
    ReferenceRule("cold-war-bipolar-order", "Cold War bipolar order", "1947-1991", "United States / Soviet Union / Europe", "bipolar alliances and bloc structure", "strategic continuity", (r"cold war.{0,80}(?:bipolar|two superpowers|soviet|western alliance|eastern bloc)",)),
    ReferenceRule("cold-war-hot-war-threshold", "Cold War versus hot-war threshold", "1947-1991 and contemporary analogy", "Global", "escalation control and security competition", "warning/falsifier", (r"cold war.{0,80}hot war", r"hot war.{0,80}cold war")),
    ReferenceRule("post-cold-war-nato-expansion", "Post-Cold War NATO expansion", "1991-present", "Europe / NATO / Russia", "alliance enlargement and security dilemma", "causal explanation", (r"nato expansion", r"expand(?:ed|ing)? nato", r"bring(?:ing)? ukraine into nato")),
    ReferenceRule("ukraine-2014-crisis", "2014 Ukraine crisis", "2014", "Ukraine / Russia / Europe", "crisis onset and responsibility", "precedent", (r"(?:crisis|trouble) (?:broke out|breaks out) in 2014", r"february 2014")),
    ReferenceRule("ukraine-2022-war", "2022 Russia-Ukraine war outbreak", "2022-present", "Ukraine / Russia / Europe", "war onset and escalation", "precedent", (r"war (?:broke out|breaks out) in 2022", r"february 2022", r"war in ukraine")),
    ReferenceRule("jcpoa-negotiation", "2015 JCPOA negotiation and implementation", "2015-2018", "Iran / United States / Europe", "nuclear diplomacy and negotiated limits", "diplomatic lesson", (r"2015.{0,40}(?:nuclear deal|jcpoa)", r"joint comprehensive plan", r"implementation of the jcpoa")),
    ReferenceRule("jcpoa-us-withdrawal", "2018 US withdrawal from the JCPOA", "2018", "Iran / United States", "treaty reliability and withdrawal", "institutional memory", (r"(?:trump|united states|america).{0,50}(?:left|leaving|withdrew|withdrawal).{0,50}(?:jcpoa|nuclear deal)", r"abandon(?:ed|ing) the nuclear deal")),
    ReferenceRule("iraq-2003-invasion", "2003 US-led invasion of Iraq", "2003", "Iraq / United States / coalition", "regime change and intervention", "precedent", (r"2003.{0,30}iraq", r"invasion of iraq", r"iraq invasion")),
    ReferenceRule("iraq-regime-change", "Iraq regime-change precedent", "2003-2011", "Iraq / United States", "regime change and strategic backfire", "precedent", (r"regime change.{0,50}iraq", r"iraq.{0,50}regime change", r"saddam.{0,50}(?:overthrow|remove|regime)")),
    ReferenceRule("gulf-war-1991", "1991 Gulf War and Kuwait liberation", "1990-1991", "Kuwait / Iraq / Gulf", "territorial aggression and coalition response", "institutional memory", (r"1991.{0,40}(?:gulf war|kuwait)", r"gulf war.{0,40}(?:1991|kuwait)", r"liberat(?:ed|ion) kuwait")),
    ReferenceRule("iraq-kuwait-claim", "Iraq's claim that Kuwait was its nineteenth province", "1990-1991", "Iraq / Kuwait", "territorial legitimacy and sovereignty", "historical correction", (r"19th province", r"nineteenth province", r"kuwait.{0,40}(?:part of iraq|iraq.{0,20}province)")),
    ReferenceRule("vietnam-war-termination", "Vietnam War and US withdrawal", "1955-1975", "Vietnam / United States", "war termination and credibility", "precedent", (r"vietnam.{0,60}(?:withdraw|withdrawal|end the war|peace)", r"war in vietnam.{0,60}(?:end|leave|withdraw)")),
    ReferenceRule("vietnam-war-intervention", "Vietnam War intervention precedent", "1955-1975", "Vietnam / United States", "intervention and strategic overreach", "precedent", (r"vietnam war", r"war in vietnam", r"vietnam.{0,40}(?:intervention|escalat)")),
    ReferenceRule("cuba-revolution", "1959 Cuban Revolution and Castro government", "1959-present", "Cuba / United States", "revolution and regime legitimacy", "precedent", (r"cuban revolution", r"castro.{0,40}(?:revolution|regime|government)", r"revolution in cuba")),
    ReferenceRule("cuba-missile-crisis", "1962 Cuban Missile Crisis", "1962", "Cuba / United States / Soviet Union", "nuclear brinkmanship and crisis management", "warning/falsifier", (r"cuban missile crisis", r"missile crisis.{0,40}cuba")),
    ReferenceRule("iran-1979-revolution", "1979 Iranian Revolution and regime change", "1979-present", "Iran / United States", "revolution, sovereignty, and regime legitimacy", "strategic continuity", (r"1979.{0,40}(?:iran|revolution)", r"iranian revolution", r"islamic revolution")),
    ReferenceRule("renaissance-greek-roman-transmission", "Renaissance transmission of Greek and Roman knowledge", "14th-17th centuries", "Europe / Mediterranean / Islamic world", "knowledge transfer and civilizational development", "civilizational comparison", (r"renaissance.{0,80}(?:greek|roman|arabic|muslim|knowledge)", r"greek and roman (?:knowledge|documents|texts)")),
    ReferenceRule("roger-sicily-translation", "Roger of Sicily and Arabic-Latin translation", "12th century", "Sicily / Mediterranean", "knowledge transfer", "historical correction", (r"roger of sicily", r"norman ruler of sicily", r"arabic.{0,40}latin translation")),
    ReferenceRule("mongol-empire-exchange", "Chinggis Khan and Mongol imperial exchange", "13th century", "Eurasia", "empire and cultural exchange", "civilizational comparison", (r"chengh?is khan", r"chinggis khan", r"mongol empire")),
    ReferenceRule("timur-imperial-memory", "Timur / Tamerlane and imperial memory", "14th-15th centuries", "Central Asia / South Asia", "empire and historical memory", "historical correction", (r"tamerlain", r"tamerlane", r"teamur")),
    ReferenceRule("imperial-overstretch-us", "Imperial overstretch and US power transition", "longue duree / modern era", "Global / United States", "power transition and strategic overreach", "strategic continuity", (r"imperial overstretch", r"500 years.{0,40}(?:dominance|empire)", r"history of empire.{0,60}(?:america|united states|decline)")),
    ReferenceRule("thucydides-peloponnesian-analogy", "Thucydides and the Peloponnesian War analogy", "classical Greece", "Greece / United States / China", "great-power transition and war risk", "analogy", (r"thucydides.{0,80}(?:peloponnesian|athens|sparta)", r"thucydides trap")),
)


def parse_scalar(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*[\"']?([^\"'\n]+)", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def source_body(text: str) -> str:
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    body = parts[2]
    heading = re.search(r"^## Transcript\s*\n", body, re.MULTILINE)
    return body[heading.end():] if heading else body


def source_rows() -> list[dict]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rows = []
    seen: set[str] = set()
    for row in manifest.get("sources", []):
        if not isinstance(row, dict):
            continue
        voices = row.get("voice_slugs") or []
        path = str(row.get("local_path") or "")
        if "freeman" not in voices and "freeman" not in path.lower() and "freeman" not in str(row.get("title") or "").lower():
            continue
        if path in seen:
            continue
        seen.add(path)
        full = REPO_ROOT / path
        rows.append({**row, "full_path": full})
    return sorted(rows, key=lambda row: (str(row.get("date") or ""), str(row.get("local_path") or "")))


def clean_quote(paragraph: str, max_chars: int = 700) -> str:
    quote = re.sub(r"\s+", " ", paragraph).strip()
    return quote if len(quote) <= max_chars else quote[:max_chars].rsplit(" ", 1)[0] + " […]"


def historical_domain(rule: ReferenceRule) -> str:
    key = rule.key
    if key in {"us-china-opening-1972", "nixon-kissinger", "jcpoa", "kuwait-liberation"}:
        return "diplomacy / strategic order"
    if key in {"bay-of-pigs", "vietnam-war", "iraq-war", "cuba-embargo", "cold-war", "kuwait-liberation"}:
        return "war / intervention"
    if key in {"cultural-revolution", "renaissance-knowledge", "dark-ages", "roger-of-sicily", "mongol-empire", "timur"}:
        return "civilization / institutions"
    if key in {"iranian-revolution", "iraq-19th-province", "october-7"}:
        return "national identity / legitimacy"
    if key in {"imperial-overstretch", "thucydides-trap"}:
        return "empire / power transition"
    return "history / strategic memory"


def repertoire_question(rule: ReferenceRule) -> str:
    key = rule.key
    if key in {"bay-of-pigs", "vietnam-war", "iraq-war", "cuba-embargo"}:
        return "What makes coercion backfire?"
    if key in {"kuwait-liberation", "jcpoa", "us-china-opening-1972", "nixon-kissinger"}:
        return "What makes diplomacy and alliances reliable?"
    if key in {"cultural-revolution", "dark-ages", "roger-of-sicily", "renaissance-knowledge"}:
        return "How does institutional competence develop or decay?"
    if key in {"iranian-revolution", "iraq-19th-province", "october-7"}:
        return "How does historical memory shape national behavior?"
    return "How do great-power transitions and imperial limits work?"


def attribution(paragraph: str, text: str) -> tuple[str, str]:
    if re.search(r"(?:\*\*)?(?:Chas|Charles) Freeman(?:\*\*)?\s*:", paragraph, re.IGNORECASE):
        return "direct", "speaker label present"
    if re.search(r"(?:Chas|Charles) Freeman", paragraph, re.IGNORECASE) and re.search(r"(?:\bI\b|we|our)", paragraph):
        return "strong-inferred", "Freeman self-reference in a Freeman-linked turn"
    return "provisional", "transcript turn is not explicitly speaker-labeled"


def mechanism_suggestions(rule: ReferenceRule, paragraph: str) -> list[dict]:
    ids = list(MECHANISM_BY_KEY.get(rule.key, []))
    registry = {item["id"]: item for item in MECHANISMS}
    suggestions = []
    for mechanism_id in ids:
        matches = [pattern for pattern in MECHANISM_EVIDENCE.get(mechanism_id, ()) if re.search(pattern, paragraph, re.IGNORECASE)]
        basis = "quote-context evidence" if matches else "reference rule only"
        suggestions.append({"id": mechanism_id, "name": registry[mechanism_id]["name"], "basis": basis, "evidence_terms": matches})
    return suggestions


def build_occurrences(rows: list[dict] | None = None) -> tuple[list[dict], list[str]]:
    occurrences: list[dict] = []
    coverage: list[str] = []
    source_items = source_rows() if rows is None else rows
    for row_index, row in enumerate(source_items, start=1):
        path: Path = row["full_path"]
        if not path.is_file():
            coverage.append(f"MISSING {row.get('local_path', '')}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        body = source_body(text)
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        found = 0
        for paragraph_index, paragraph in enumerate(paragraphs, start=1):
            for rule in RULES:
                if not any(re.search(pattern, paragraph, re.IGNORECASE | re.DOTALL) for pattern in rule.patterns):
                    continue
                confidence, note = attribution(paragraph, text)
                occurrences.append({
                    "rule": rule,
                    "date": str(row.get("date") or parse_scalar(text, "pub_date")),
                    "title": str(row.get("title") or parse_scalar(text, "title")),
                    "host": str(row.get("host_slug") or parse_scalar(text, "host_slug")),
                    "source_id": f"SRC-FR-{row_index:03d}",
                    "path": str(row.get("local_path") or path.relative_to(REPO_ROOT).as_posix()),
                    "quote": clean_quote(paragraph),
                    "function": rule.function,
                    "confidence": confidence,
                    "note": note,
                    "paragraph": paragraph_index,
                    "occurrence_id": f"FR-O-{row_index:03d}-{rule.key}-{paragraph_index:04d}",
                    "mechanism_suggestions": mechanism_suggestions(rule, paragraph),
                    "mechanism_basis": "reference rule plus quote-context heuristic",
                    "mechanism_status": "suggested",
                    "mechanism_review_note": "Not yet explicitly reviewed for mechanism fit.",
                })
                found += 1
        if not found:
            coverage.append(f"SCANNED {row.get('local_path', '')} (no catalogued references)")
        else:
            coverage.append(f"SCANNED {row.get('local_path', '')} ({found} occurrence(s))")
    return occurrences, coverage


def load_mechanism_review() -> dict:
    if not MECHANISM_REVIEW_PATH.is_file():
        return {"voice": "freeman", "version": MECHANISM_VERSION, "confirmed": [], "revisions": [], "counterexamples": []}
    return json.loads(MECHANISM_REVIEW_PATH.read_text(encoding="utf-8"))


def load_review_decisions() -> dict[str, dict]:
    if not REVIEW_DECISIONS_PATH.is_file():
        return {}
    payload = json.loads(REVIEW_DECISIONS_PATH.read_text(encoding="utf-8"))
    decisions: dict[str, dict] = {}
    for decision in payload.get("decisions", []):
        for occurrence_id in decision.get("occurrence_ids", []):
            decisions[occurrence_id] = decision
    return decisions


def load_manual_turn_review() -> dict[str, dict]:
    if not MANUAL_TURN_REVIEW_PATH.is_file():
        return {}
    payload = json.loads(MANUAL_TURN_REVIEW_PATH.read_text(encoding="utf-8"))
    return {item["occurrence_id"]: item for item in payload.get("decisions", [])}


def apply_manual_turn_review(occurrences: list[dict]) -> tuple[list[dict], list[dict]]:
    decisions = load_manual_turn_review()
    kept: list[dict] = []
    rejected: list[dict] = []
    for occurrence in occurrences:
        decision = decisions.get(occurrence["occurrence_id"])
        if not decision:
            kept.append(occurrence)
            continue
        occurrence["manual_review_status"] = decision["decision"]
        occurrence["manual_speaker"] = decision.get("speaker")
        occurrence["manual_raw_lines"] = decision.get("raw_lines", "")
        occurrence["manual_evidence"] = decision.get("evidence", "")
        if decision["decision"] == "accepted":
            occurrence["confidence"] = "manual-accepted"
            occurrence["note"] = "Manual turn review: Chas Freeman attribution accepted; " + decision.get("evidence", "")
            kept.append(occurrence)
        else:
            rejected.append(occurrence)
    return kept, rejected


def apply_review_decisions(occurrences: list[dict]) -> list[dict]:
    decisions = load_review_decisions()
    for occurrence in occurrences:
        decision = decisions.get(occurrence["occurrence_id"])
        if not decision:
            occurrence["canonical_reference_key"] = occurrence["rule"].key
            occurrence["canonical_reference"] = occurrence["rule"].label
            continue
        occurrence["canonical_reference_key"] = decision["canonical_reference_key"]
        occurrence["canonical_reference"] = decision["canonical_label"]
        occurrence["review_decision_id"] = decision["decision_id"]
        occurrence["review_status"] = decision["review_status"]
    return occurrences


def build_analysis() -> HistoricalIndexAnalysis:
    rows = source_rows()
    occurrences, coverage = build_occurrences(rows)
    occurrences, rejected = apply_manual_turn_review(occurrences)
    apply_review_decisions(occurrences)
    return HistoricalIndexAnalysis(
        rows=rows,
        occurrences=occurrences,
        rejected=rejected,
        coverage=coverage,
        review=load_mechanism_review(),
    )


def structured_ledger(rows: list[dict], occurrences: list[dict], rejected: list[dict], coverage: list[str], review: dict) -> dict:
    return {
        "schema_version": 1,
        "taxonomy_version": "shared-reference-rules-1",
        "mechanism_version": MECHANISM_VERSION,
        "voice": "freeman",
        "sources_scanned": len(rows),
        "coverage": coverage,
        "manual_turn_review": {
            "accepted_count": sum(1 for item in occurrences if item.get("manual_review_status") == "accepted"),
            "rejected_count": len(rejected),
            "rejected_occurrences": [
                {key: value for key, value in item.items() if key != "rule"} | {"reference_key": item["rule"].key, "reference": item["rule"].label}
                for item in rejected
            ],
        },
        "occurrences": [
            {key: value for key, value in occurrence.items() if key != "rule"} | {"reference_key": occurrence["rule"].key, "reference": occurrence["rule"].label}
            for occurrence in occurrences
        ],
        "mechanisms": {"registry": list(MECHANISMS), "review": review},
    }


def render(analysis: HistoricalIndexAnalysis | None = None) -> str:
    analysis = build_analysis() if analysis is None else analysis
    rows = analysis.rows
    occurrences = analysis.occurrences
    rejected = analysis.rejected
    coverage = analysis.coverage
    grouped: dict[str, list[dict]] = defaultdict(list)
    for occurrence in occurrences:
        grouped[occurrence["canonical_reference_key"]].append(occurrence)
    rules = {rule.key: rule for rule in RULES}
    representative_rules = {
        key: rules[next(item["rule"].key for item in items)]
        for key, items in grouped.items()
    }
    ordered_keys = sorted(grouped, key=lambda key: (representative_rules[key].period, grouped[key][0]["canonical_reference"].lower()))
    lines = [
        "# Chas Freeman Historical References",
        "",
        "Status: `internal research index`",
        "",
        "Generated by `scripts/build_freeman_historical_index.py` from the manifest-backed Freeman archive. Archive wording is preserved as captured; historical claims are catalogued here, not independently verified.",
        "",
        "## Coverage and limitations",
        "",
        f"- Freeman-linked archive items scanned: **{len(rows)}**.",
        "- Scope: references attributable to Freeman; host-only references are excluded unless Freeman adopts or develops them.",
        "- `direct` means a speaker label is present; `strong-inferred` means the transcript turn supports attribution; `provisional` means attribution requires later review.",
        "- Source transcripts may be operator-pasted or ASR-derived. Quotes are not human-verified by this index.",
        f"- Manual turn review applied to July 24 sources: **{sum(1 for item in occurrences if item.get('manual_review_status') == 'accepted')} accepted**, **{len(rejected)} rejected**; rejected candidates remain in the structured ledger and are excluded from the Freeman index.",
        "",
        "## Reference index",
        "",
        "| ID | Reference | Historical domain | Period | Region / civilization | Topic | Function | Freeman question | First | Latest | Occurrences | Source IDs | Attribution |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for number, key in enumerate(ordered_keys, start=1):
        rule = representative_rules[key]
        items = grouped[key]
        dates = sorted(item["date"] for item in items)
        source_ids = sorted({item["source_id"] for item in items})
        status = "provisional" if any(item["confidence"] == "provisional" for item in items) else "supported"
        label = items[0]["canonical_reference"]
        lines.append(f"| `FR-HR-{number:03d}` | {label} | {historical_domain(rule)} | {rule.period} | {rule.region} | {rule.topic} | {rule.function} | {repertoire_question(rule)} | {dates[0]} | {dates[-1]} | {len(items)} | {', '.join(source_ids)} | `{status}` |")
    lines += ["", "## Occurrence ledger", ""]
    occurrence_number = 0
    for number, key in enumerate(ordered_keys, start=1):
        rule = representative_rules[key]
        lines += [f"### FR-HR-{number:03d} — {rule.label}", ""]
        for occurrence in sorted(grouped[key], key=lambda item: (item["date"], item["source_id"], item["paragraph"])):
            occurrence_number += 1
            oid = f"FR-HR-{number:03d}-O{occurrence_number:03d}"
            canonical_group = occurrence["canonical_reference_key"]
            lines.append(f"- Canonical review grouping: `{canonical_group}`" + (f" via `{occurrence['review_decision_id']}`" if occurrence.get("review_decision_id") else ""))
            lines += [
                f"#### {oid} — {occurrence['date']} — {occurrence['title']}",
                "",
                f"- Source: `{occurrence['source_id']}` · host/channel `{occurrence['host']}` · [archive source](../../archive/{occurrence['path'].split('archive/', 1)[-1]})",
                f"- Domain: `{historical_domain(rule)}` · function: `{occurrence['function']}` · Freeman question: `{repertoire_question(rule)}`",
                f"- Attribution: `{occurrence['confidence']}` ({occurrence['note']})",
                *( [f"- Manual turn review: `{occurrence['manual_review_status']}` · speaker `{occurrence['manual_speaker']}` · raw lines `{occurrence['manual_raw_lines']}`"] if occurrence.get("manual_review_status") else [] ),
                f"- Quote: “{occurrence['quote']}”",
                "",
            ]
    lines += ["## Coverage log", "", *[f"- {item}" for item in coverage], ""]
    lines += ["## Suggested mechanisms by occurrence", "", "Mechanism suggestions are provisional candidate annotations generated from reference rules and quote context.", ""]
    for occurrence in sorted(occurrences, key=lambda item: item["occurrence_id"]):
        suggestions = ", ".join(f"`{item['id']}` {item['name']} ({item['basis']}{': ' + ', '.join(item['evidence_terms']) if item['evidence_terms'] else ''})" for item in occurrence["mechanism_suggestions"]) or "none"
        lines.append(f"- `{occurrence['occurrence_id']}` · `{occurrence['source_id']}` · `{occurrence['rule'].key}` · {suggestions}")
    lines += ["", "## Manual turn review exclusions", "", "Rejected candidates are retained in the structured ledger for audit but excluded from Freeman-attributed index counts.", ""]
    for occurrence in rejected:
        lines.append(f"- `{occurrence['occurrence_id']}` · `{occurrence['source_id']}` · `{occurrence['rule'].key}` · speaker `{occurrence.get('manual_speaker') or 'unresolved'}` · raw lines `{occurrence.get('manual_raw_lines', '')}` · {occurrence.get('manual_evidence', '')}")
    lines += ["", "## Confirmed Freeman mechanisms", "", "Confirmed mechanisms require explicit operator review and preserve an evidence chain to occurrence IDs and archive sources.", ""]
    confirmed = analysis.review.get("confirmed", [])
    if confirmed:
        for item in confirmed:
            lines += [f"### `{item['id']}` — {item['name']}", "", f"- Evidence occurrences: {', '.join(f'`{value}`' for value in item.get('occurrence_ids', []))}", f"- Sources: {', '.join(f'`{value}`' for value in item.get('source_ids', []))}", f"- Rationale: {item.get('rationale', '')}", f"- Differences: {item.get('material_differences', '')}", f"- Reviewed: {item.get('reviewed_date', '')}", ""]
    else:
        lines.append("- None explicitly confirmed; candidate suggestions remain provisional.")
    lines += ["", "## Evidence and counterexamples", ""]
    for item in MECHANISMS:
        lines.append(f"- `{item['id']}` **{item['name']}** — {item['counterexample_guidance']}")
    lines += ["", "## Unresolved mechanism candidates", "", f"- Suggested occurrence annotations: **{len(occurrences)}**", "- Mechanism status is separate from attribution confidence, historical accuracy, analytical quality, and forecast success.", "", "## Coverage log", "", *[f"- {item}" for item in coverage], ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    analysis = build_analysis()
    rendered = render(analysis)
    if args.dry_run:
        print(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        MECHANISM_REGISTRY_PATH.write_text(json.dumps({"version": MECHANISM_VERSION, "mechanisms": list(MECHANISMS)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        MECHANISM_REVIEW_PATH.write_text(json.dumps(analysis.review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        args.output.with_suffix(".json").write_text(json.dumps(structured_ledger(analysis.rows, analysis.occurrences, analysis.rejected, analysis.coverage, analysis.review), ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"Wrote {args.output.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

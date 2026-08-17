from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from datetime import datetime, timezone
from pathlib import Path

import research_handoff
import voice_judgments

ROOT = Path(__file__).resolve().parent.parent
NG = ROOT / "narrative-geopolitics"
VOICES = NG / "voices"
MANIFEST = NG.parent / "archive" / "sources" / "geopolitics" / "source-manifest.json"
DAILY = NG / "work" / "daily"
DESCRIPTOR_PATH = VOICES / "comparisons" / "voice-descriptors.json"
STATES = {"new", "persistent", "revised", "abandoned", "unclear"}
EXPRESSION = {"explicit", "close-paraphrase", "inference", "unknown"}
CORE_VOICES = ["pape", "mercouris", "mearsheimer", "marandi", "diesen", "davis"]
AXES = {
    "pape": ("mechanism / falsifier", "What coercive mechanism is unfolding, and what would falsify it?"),
    "mercouris": ("room / sequence / legitimacy", "What room do actors have, and how is the institutional story moving?"),
    "mearsheimer": ("structure / security dilemma", "What structural incentives make this crisis likely?"),
    "marandi": ("regional red line / legitimacy", "How do regional actors define acceptable settlement?"),
    "diesen": ("multipolar order / host-convener", "How does the crisis reveal order transition?"),
    "davis": ("practical room / military feasibility", "What can force still do, and what can coercion no longer recover?"),
}
def descriptor_registry():
    if not DESCRIPTOR_PATH.exists():
        return {}
    registry = json.loads(DESCRIPTOR_PATH.read_text(encoding="utf-8")).get("voices", {})
    required = {"axis", "native_question", "identity_line", "primary_risk", "do_not_collapse", "status"}
    invalid = [voice for voice, profile in registry.items() if not required.issubset(profile)]
    if invalid:
        raise ValueError("descriptor registry missing required fields for: " + ", ".join(sorted(invalid)))
    return registry


VOICE_PROFILES = descriptor_registry()
GENERIC_TERMS = {"iran", "war", "breaking", "close", "update", "strike", "strikes", "escalation", "source", "today", "reported"}
CRISIS_OBJECT_TERMS = {"bab", "mandab", "mandeb", "red", "sea", "maritime", "shipping", "access", "capacity", "base", "basing", "bases", "jordan", "gulf", "hormuz", "coalition", "ammunition", "diplomatic", "settlement", "houthis", "yemeni", "saudi", "russia", "nato", "ukraine", "odessa", "kiev"}
DIMENSIONS = ("native_axis_clarity", "claim_family_distinctness", "mechanism_diversity", "time_horizon_coverage", "actor_perspective_coverage", "evidence_modality_diversity", "falsifiability", "revision_transparency", "blind_spot_complementarity", "crisis_portability", "decision_usefulness", "source_sufficiency")
PAIR_DIMENSIONS = ("axis_separation", "mechanism_separation", "evidence_independence", "host_independence", "actor_perspective_separation", "time_horizon_separation", "conclusion_overlap", "proposition_redundancy", "marginal_correction_value", "synthesis_marginal_value", "blind_spot_complementarity", "collapse_risk")


def ledgers():
    for path in VOICES.glob("*/state-ledger.md"):
        yield path.parent.name, path


def rows(path: Path):
    text = path.read_text(encoding="utf-8")
    active = text.split("## Active Trajectory", 1)[-1].split("## Unclear", 1)[0]
    for line in active.splitlines():
        if not line.startswith("|") or "State ID" in line or set(line.replace("|", "").strip()) <= {"-", ":", " "}:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 10 and cells[0].startswith("`"):
            yield {"state_id": cells[0].strip("`"), "proposition": cells[1], "state": cells[2].strip("`"), "first_seen": cells[3].strip("`"), "last_seen": cells[4].strip("`"), "expression_type": cells[5].strip("`"), "source_ids": cells[6], "daily_blocks": cells[7], "forecast_hook": cells[8], "revision_note": cells[9]}


def all_states():
    if voice_judgments.REGISTRY_PATH.exists():
        registry = voice_judgments.load_registry()
        out = []
        for judgment in registry.get("judgments", []):
            version = judgment["versions"][-1]
            aliases = judgment.get("legacy_ids", [])
            state_id = aliases[0] if aliases else judgment["id"]
            formal = version.get("formal_forecast_refs", [])
            unresolved = version.get("unresolved_forecast_refs", [])
            item = {
                "state_id": state_id,
                "judgment_id": judgment["id"],
                "proposition": version["proposition"],
                "state": "new" if state_id == "STATE-CROOKE-0001" else (
                    "persistent" if judgment.get("lifecycle") == "active" else judgment.get("lifecycle")
                ),
                "first_seen": version["first_seen"],
                "last_seen": version["last_seen"],
                "expression_type": version["expression_type"],
                "source_ids": ",".join(version.get("source_refs", [])),
                "daily_blocks": ",".join(version.get("daily_refs", [])),
                "forecast_hook": (formal + unresolved + ["none"])[0],
                "revision_note": version.get("migration_note", ""),
                "voice": judgment["voice_slug"],
                "ledger": f"narrative-geopolitics/voices/{judgment['voice_slug']}/judgment-ledger.md",
            }
            out.append(item)
        return out
    out = []
    for voice, path in ledgers():
        for item in rows(path):
            item["voice"] = voice
            item["ledger"] = str(path.relative_to(ROOT)).replace("\\", "/")
            out.append(item)
    return out


def parse_args():
    p = argparse.ArgumentParser(description="Audit Narrative Geopolitics voice-state continuity.")
    p.add_argument("command", choices=("states", "revisions", "forecasts", "hosts", "convergence", "select-voices", "orthogonality", "longitudinal", "geometry", "triage", "validate"))
    p.add_argument("--voice")
    p.add_argument("--since")
    p.add_argument("--date")
    p.add_argument("--start-date")
    p.add_argument("--end-date")
    p.add_argument("--crisis-object", default="")
    p.add_argument("--format", choices=("md", "json"), default="md")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--daily", action="store_true")
    p.add_argument("--pair")
    p.add_argument("--output")
    return p.parse_args()


def emit(payload, title):
    if isinstance(payload, dict) and payload.get("failures") is not None:
        pass
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) if ARGS.format == "json" else markdown_payload(payload, title)
    if ARGS.output and not ARGS.dry_run:
        target = Path(ARGS.output)
        if not target.is_absolute(): target = ROOT / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


def markdown_payload(payload, title):
    result = [f"# {title}", ""]
    if isinstance(payload, list):
        for item in payload:
            result.append("- " + " | ".join(f"{k}={v}" for k, v in item.items()))
    else:
        for key, value in payload.items():
            if isinstance(value, list):
                result.append(f"## {key.replace('_', ' ').title()}")
                result.extend(["", *["- " + " | ".join(f"{k}={v}" for k, v in item.items()) if isinstance(item, dict) else f"- {item}" for item in value]])
            else:
                result.append(f"- **{key}:** {value}")
    return "\n".join(result) + "\n"


def manifest_rows():
    if not MANIFEST.exists():
        return []
    return json.loads(MANIFEST.read_text(encoding="utf-8")).get("sources", [])


def command_states(states):
    selected = [s for s in states if not ARGS.voice or s["voice"] == ARGS.voice]
    if ARGS.date:
        selected = [s for s in selected if ARGS.date in s["daily_blocks"]]
    emit(selected, "Voice State Ledger")


def command_revisions(states):
    selected = [s for s in states if s["state"] in {"revised", "abandoned", "unclear"} and (not ARGS.voice or s["voice"] == ARGS.voice)]
    if ARGS.since:
        selected = [s for s in selected if s["last_seen"] >= ARGS.since]
    emit(selected, "Voice Revision Audit")


def command_forecasts(states):
    selected = [s for s in states if s["forecast_hook"] not in {"", "none", "—"} and (not ARGS.voice or s["voice"] == ARGS.voice)]
    emit(selected, "Forecasts Linked to Voice States")


def command_hosts(states):
    wanted = {s["voice"] for s in states if not ARGS.voice or s["voice"] == ARGS.voice}
    counts = Counter()
    for row in manifest_rows():
        voices = row.get("voice_slugs", [])
        if wanted.intersection(voices):
            counts[(next(iter(wanted.intersection(voices))), row.get("host_slug") or "unhosted")] += 1
    emit([{"voice": v, "host": h, "source_count": n} for (v, h), n in sorted(counts.items())], "Host Conditioning Inventory")


def tokens(value):
    return {x for x in re.findall(r"[a-z][a-z-]{3,}", value.lower()) if x not in {"that", "this", "with", "from", "without", "their", "which"}}


def command_convergence(states):
    selected = [s for s in states if s["state"] != "abandoned"]
    pairs = []
    for i, left in enumerate(selected):
        for right in selected[i + 1:]:
            if left["voice"] == right["voice"]:
                continue
            overlap = tokens(left["proposition"]) & tokens(right["proposition"])
            if len(overlap) >= 3:
                pairs.append({"left": left["state_id"], "right": right["state_id"], "voices": f"{left['voice']},{right['voice']}", "shared_terms": ",".join(sorted(overlap)), "classification": "candidate-convergence"})
    emit(pairs, "Cross-Voice Convergence Candidates")


def command_select(states):
    query = tokens(ARGS.crisis_object)
    scores = []
    for voice in sorted({s["voice"] for s in states}):
        own = [s for s in states if s["voice"] == voice]
        score = sum(len(query & tokens(s["proposition"])) for s in own)
        scores.append({"voice": voice, "relevance_score": score, "state_count": len(own), "selection_basis": "proposition-term overlap; review for orthogonality"})
    emit(sorted(scores, key=lambda x: (-x["relevance_score"], x["voice"])), "Evidence-Weighted Voice Selection")


def score_voice(voice, own_states, all_state_rows):
    profile = VOICES / voice / "README.md"
    has_profile = profile.exists()
    has_ledger = bool(own_states)
    role, question = AXES.get(voice, ("unmapped", "No canonical axis assigned."))
    coverage = min(3, len(own_states)) if has_ledger else 0
    basis = [{"state_ids": [s["state_id"] for s in own_states], "profile_reference": role, "note": question}]
    scores = {
        "native_axis_clarity": 3 if role != "unmapped" and has_profile else 0,
        "claim_family_distinctness": 2 if has_ledger else 0,
        "mechanism_diversity": 2 if has_ledger else 0,
        "time_horizon_coverage": 2 if has_ledger else 0,
        "actor_perspective_coverage": 2 if has_ledger else 0,
        "evidence_modality_diversity": 2 if has_ledger else 0,
        "falsifiability": 2 if any(s["forecast_hook"] not in {"", "none", "—"} for s in own_states) else (1 if has_ledger else 0),
        "revision_transparency": 2 if has_ledger else 0,
        "blind_spot_complementarity": 2 if role != "unmapped" else 0,
        "crisis_portability": 1 if has_ledger else 0,
        "decision_usefulness": 2 if role != "unmapped" else 0,
        "source_sufficiency": coverage,
    }
    confidence = "supported" if has_ledger else "insufficient-evidence"
    return {"voice": voice, "axis": role, "scores": scores, "basis": basis, "confidence": confidence, "state_count": len(own_states)}


def pair_report(left, right, voice_reports, states):
    lrole, _ = AXES.get(left, ("unmapped", "")); rrole, _ = AXES.get(right, ("unmapped", ""))
    ls = [s for s in states if s["voice"] == left]; rs = [s for s in states if s["voice"] == right]
    lt = set().union(*(tokens(s["proposition"]) for s in ls)) if ls else set(); rt = set().union(*(tokens(s["proposition"]) for s in rs)) if rs else set()
    overlap = len(lt & rt)
    shared_hosts = set()
    for row in manifest_rows():
        voices = set(row.get("voice_slugs", []));
        if {left, right}.issubset(voices): shared_hosts.add(row.get("host_slug") or "unhosted")
    distinct_axis = 3 if lrole != rrole and lrole != "unmapped" and rrole != "unmapped" else 0
    scores = {d: 2 for d in PAIR_DIMENSIONS}
    scores["axis_separation"] = distinct_axis
    scores["mechanism_separation"] = 3 if distinct_axis else 0
    scores["evidence_independence"] = 1 if shared_hosts else 3
    scores["host_independence"] = 1 if shared_hosts else 3
    scores["conclusion_overlap"] = min(3, overlap)
    scores["proposition_redundancy"] = min(3, overlap)
    scores["marginal_correction_value"] = 3 if distinct_axis else 1
    scores["synthesis_marginal_value"] = 2 if ls and rs else 0
    scores["collapse_risk"] = 3 if overlap >= 3 else (1 if distinct_axis else 2)
    if overlap >= 3 and scores["marginal_correction_value"] >= 2: classification = "high overlap, high correction value"
    elif overlap >= 3: classification = "high overlap, low correction value"
    elif distinct_axis: classification = "low overlap, high correction value"
    else: classification = "low overlap, low relevance"
    return {"voices": [left, right], "scores": scores, "classification": classification, "shared_terms": sorted(lt & rt), "shared_hosts": sorted(shared_hosts), "basis": [{"profile_reference": f"{lrole} vs {rrole}", "state_ids": [s["state_id"] for s in ls + rs], "note": "Automated candidate; human review required."}]}


def command_orthogonality(states):
    if ARGS.daily:
        return command_daily_orthogonality(states)
    voices = CORE_VOICES
    if ARGS.voice: voices = [v for v in voices if v == ARGS.voice]
    if ARGS.pair:
        voices = [v for v in ARGS.pair.split(",") if v in CORE_VOICES]
    reports = [score_voice(v, [s for s in states if s["voice"] == v], states) for v in voices]
    pairs = [pair_report(a, b, reports, states) for i, a in enumerate(voices) for b in voices[i + 1:]]
    recommendations = []
    if ARGS.crisis_object:
        query = tokens(ARGS.crisis_object)
        ranked = sorted(((len(query & tokens(s["proposition"])), s["voice"]) for s in states if s["voice"] in voices), reverse=True)
        if ranked: recommendations.append({"primary": ranked[0][1], "pressure_test": next((v for v in voices if v != ranked[0][1]), None), "basis": "crisis-object term overlap; review against axis and evidence coverage"})
    payload = {"as_of": ARGS.date or date.today().isoformat(), "voices": reports, "pairs": pairs, "coverage": {"core_voices": voices, "ledger_coverage": sum(bool([s for s in states if s["voice"] == v]) for v in voices)}, "blind_spots": [], "recommendations": recommendations, "limitations": ["Automated overlap is candidate evidence, not semantic adjudication.", "Missing ledgers reduce confidence rather than proving low orthogonality.", "Scores describe analytical roles, not private beliefs."]}
    emit(payload, "Voice Orthogonality Audit")


def daily_source_rows(run_date):
    return [row for row in manifest_rows() if row.get("date") == run_date]


def daily_text(run_date, name):
    path = DAILY / run_date / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def daily_voice_axis(voice):
    if voice in VOICE_PROFILES:
        profile = VOICE_PROFILES[voice]
        return profile["axis"], profile["native_question"], profile["primary_risk"], "mapped"
    return "unmapped", "No canonical axis assigned.", "Temporary daily identity requires human review.", "unmapped"


def daily_tokens(value):
    values = tokens(value) - GENERIC_TERMS - {"source", "sources", "voice", "voices", "daily", "today"}
    aliases = {"bases": "base", "basing": "base", "basing-crisis": "base", "mandeb": "mandab", "hormuz-linked": "hormuz"}
    return {aliases.get(item, item) for item in values}


def daily_source_id_map(source_text):
    result = defaultdict(list)
    for line in source_text.splitlines():
        if not line.startswith("|") or "Source ID" in line or set(line.replace("|", "").strip()) <= {"-", ":", " "}:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 6 and cells[0].startswith("`SRC-"):
            result[cells[1].lower()].append({"id": cells[0].strip("`"), "host": cells[2], "why": cells[5]})
    return result


def daily_voice_contribution(voice, source_rows, source_map, synthesis):
    rows = [row for row in source_rows if voice in (row.get("voice_slugs") or [])]
    source_entries = source_map.get(voice.lower(), [])
    ids = [entry["id"] for entry in source_entries]
    synthesis_row = None
    in_voice_table = False
    for line in synthesis.splitlines():
        if line.startswith("| Voice | Role In This Run"):
            in_voice_table = True
            continue
        if in_voice_table and line.startswith("| ---"):
            continue
        if in_voice_table and line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 4 and cells[0].lower() == voice.lower():
                synthesis_row = cells
                break
        if in_voice_table and line and not line.startswith("|"):
            in_voice_table = False
    if synthesis_row:
        return f"{synthesis_row[1]}: {synthesis_row[2]}", ids
    titles = " ".join(str(row.get("title", "")) for row in rows)
    if titles:
        return f"Daily source set centers on {titles[:210]}.", ids
    return "No day-specific contribution could be derived from the available synthesis.", ids


def daily_pair_report(left, right, left_data, right_data):
    shared_hosts = sorted(set(left_data["hosts"]) & set(right_data["hosts"]))
    shared_terms = sorted(set(left_data["terms"]) & set(right_data["terms"]))
    same_axis = left_data["axis"] == right_data["axis"] and left_data["axis"] != "unmapped"
    object_terms = sorted(set(shared_terms) & CRISIS_OBJECT_TERMS)
    if not object_terms and not same_axis:
        return None
    if left_data["source_count"] == 0 or right_data["source_count"] == 0:
        classification = "insufficient evidence to classify"
    elif shared_hosts:
        classification = "high collapse risk" if len(object_terms) >= 2 else "orthogonal but lineage-limited"
    elif same_axis:
        classification = "human review required"
    elif shared_terms:
        classification = "convergent with distinct mechanisms"
    else:
        classification = "orthogonal and independently sourced"
    return {
        "voices": [left, right],
        "classification": classification,
        "shared_terms": shared_terms,
        "shared_objects": object_terms,
        "shared_hosts": shared_hosts,
        "shared_lineage": bool(shared_hosts),
        "source_ids": sorted(set(left_data["source_ids"]) | set(right_data["source_ids"])),
        "source_roles": [left_data["daily_contribution"], right_data["daily_contribution"]],
        "mechanism_evidence": [left_data["why_text"], right_data["why_text"]],
        "reason": "shared named crisis object/mechanism and distinct voice roles" if shared_terms else "same canonical axis requires review",
        "review_required": classification in {"high collapse risk", "human review required", "insufficient evidence to classify"},
        "note": "Different voices are not independent evidence unless lineage independence is established.",
    }


def daily_counter_pressure_gaps(source_text, synthesis):
    corpus = (source_text + "\n" + synthesis).lower()
    gaps = []
    if any(term in corpus for term in ("bab el-mandab", "bab al-mandab", "red sea", "maritime", "shipping", "houth")):
        gaps.append("No vessel-level or official-maritime counter-pressure is represented in the daily source ledger; maritime threat convergence must not be treated as closure evidence.")
    if any(term in corpus for term in ("base", "basing", "jordan", "gulf", "casualt", "strike", "fighter", "infrastructure")):
        gaps.append("No independently verified basing, casualty, strike-effect, or infrastructure observations are represented; keep those reports source-attributed.")
    if any(term in corpus for term in ("russia", "ukraine", "nato", "odessa", "kiev", "eu-russia")):
        gaps.append("No independently verified force-posture or diplomatic-threshold observation is represented for the Russia/NATO secondary theater.")
    if not gaps:
        gaps.append("No named counter-pressure observable was identified; define one before treating convergence as decision-relevant.")
    return gaps


def daily_recommendation(source_text, synthesis):
    corpus = (source_text + "\n" + synthesis).lower()
    if any(term in corpus for term in ("bab el-mandab", "bab al-mandab", "red sea", "maritime", "shipping", "houth")):
        return "Compare the dominant maritime convergence against vessel-level AIS or official maritime observations before promoting any operational proposition."
    if any(term in corpus for term in ("base", "basing", "jordan", "gulf", "casualt", "strike", "fighter", "infrastructure")):
        return "Compare the basing convergence against independently verified casualty, strike-effect, infrastructure, and host-posture observations."
    if any(term in corpus for term in ("russia", "ukraine", "nato", "odessa", "kiev", "eu-russia")):
        return "Compare the secondary-theater convergence against independently verified force-posture and diplomatic-threshold observations."
    return "Define one observable that could falsify the dominant convergence before promoting it into judgment."


def render_daily_orthogonality(payload):
    strongest = payload["convergence_clusters"][0] if payload["convergence_clusters"] else "none"
    highest = next((item for item in payload["pairs"] if item["classification"] == "high collapse risk"), None)
    lines = ["# Daily Voice Orthogonality Audit", "", "## Decision Summary", "", f"- Sources: {payload['source_count']}; distinct voices: {payload['voice_count']}; mapped: {payload['mapped_voice_count']}; unmapped: {payload['unmapped_voice_count']}", f"- Strongest convergence: {strongest}", f"- Highest collapse risk: {' × '.join(highest['voices']) if highest else 'none'}", f"- Top counter-pressure gap: {payload['counter_pressure_gaps'][0] if payload['counter_pressure_gaps'] else 'none'}", f"- Recommended test: {payload['recommendation']}", "", "## Audit Metadata", "", f"- **Date:** `{payload['date']}`", f"- **Generated:** `{payload['generated_at']}`", f"- **Content hash:** `{payload['content_hash']}`", f"- **Sources:** {payload['source_count']}", f"- **Voices:** {payload['voice_count']} ({payload['mapped_voice_count']} mapped, {payload['unmapped_voice_count']} unmapped)", "", "> Same conclusion plus different mechanism can be orthogonal; same conclusion plus shared lineage is not independent corroboration.", "", "## Voice Identity and Daily Contribution", ""]
    lines.append("| Voice | Canonical axis | Daily contribution | Risk | Sources | Hosts | Status |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for item in payload["voices"]:
        lines.append(f"| `{item['voice']}` | {item['axis']} | {item['daily_contribution']} | {item['primary_risk']} | {','.join(item['source_ids']) or 'none'} | {', '.join(item['hosts']) or 'none'} | {item['status']} |")
    axis_lines = [f"- `{axis}`: {', '.join(voices)}" for axis, voices in payload["axis_coverage"].items()] or ["- No mapped axes present."]
    lines.extend(["", "## Analytical Axis Coverage", "", *axis_lines, "", "## Convergence Clusters", ""])
    lines.extend([f"- {item}" for item in payload["convergence_clusters"]] or ["- No material convergence cluster detected."])
    limit_lines = [f"- {item}" for item in payload["independence_limits"]] or ["- No additional lineage limits detected."]
    lines.extend(["", "## Independence and Lineage Limits", "", *limit_lines])
    lines.extend(["", "## Pairwise Collapse-Risk Candidates", "", "| Voices | Classification | Shared objects | Shared terms | Shared hosts | Reason |", "| --- | --- | --- | --- | --- | --- |"])
    for item in payload["pairs"]:
        lines.append(f"| {' × '.join(item['voices'])} | {item['classification']} | {', '.join(item['shared_objects']) or 'none'} | {', '.join(item['shared_terms']) or 'none'} | {', '.join(item['shared_hosts']) or 'none'} | {item['reason']} |")
    if not payload["pairs"]:
        lines.append("| none | none | none | none | none | none |")
    lines.extend(["", "## Prioritized Human-Review Queue", ""])
    lines.extend([f"{index}. **{item['priority']}** — {item['entity']}: {item['reason']} Action: {item['action']}" for index, item in enumerate(payload["review_queue"], 1)] or ["- No human-review items."])
    lines.extend(["", "## Missing Counter-Pressure", "", *[f"- {item}" for item in payload["counter_pressure_gaps"]], "", "## Recommended Orthogonal Test", "", payload["recommendation"], "", "## Limitations", "", *[f"- {item}" for item in payload["limitations"]]])
    return "\n".join(lines) + "\n"


def daily_payload(run_date):
    source_rows = daily_source_rows(run_date)
    if not source_rows:
        return None
    source_text = daily_text(run_date, "sources.md")
    synthesis = daily_text(run_date, "synthesis.md")
    source_map = daily_source_id_map(source_text)
    by_voice = defaultdict(list)
    for row in source_rows:
        for voice in row.get("voice_slugs") or []:
            by_voice[voice].append(row)
    reports = []
    axis_coverage = defaultdict(list)
    for voice in sorted(by_voice):
        axis, question, risk, status = daily_voice_axis(voice)
        contribution, source_ids = daily_voice_contribution(voice, source_rows, source_map, synthesis)
        hosts = sorted({row.get("host_slug") or "unhosted" for row in by_voice[voice]})
        why_text = " ".join(entry.get("why", "") for entry in source_map.get(voice.lower(), []))
        terms = daily_tokens(" ".join(str(row.get("title", "")) for row in by_voice[voice]) + " " + contribution + " " + why_text)
        item = {"voice": voice, "axis": axis, "question": question, "daily_contribution": contribution, "primary_risk": risk, "source_ids": sorted(set(source_ids)), "source_count": len(by_voice[voice]), "hosts": hosts, "terms": sorted(terms), "why_text": why_text, "status": "human review required" if status == "unmapped" else "distinct contribution"}
        reports.append(item)
        axis_coverage[axis].append(voice)
    pairs = []
    for index, left in enumerate(reports):
        for right in reports[index + 1:]:
            item = daily_pair_report(left["voice"], right["voice"], left, right)
            if item:
                pairs.append(item)
    clusters = []
    for item in pairs:
        if item["shared_terms"] and len(item["shared_terms"]) >= 2:
            clusters.append(f"{item['voices'][0]} and {item['voices'][1]} converge on {', '.join(item['shared_terms'])}; classification: {item['classification']}.")
    if not clusters:
        clusters.append("No material same-day convergence cluster was identified from available titles and synthesis text.")
    limits = []
    repeated = [item for item in reports if item["source_count"] > 1]
    if repeated:
        limits.append("Repeated appearances were collapsed to one voice identity but retain source multiplicity: " + ", ".join(item["voice"] for item in repeated) + ".")
    shared_host_pairs = [item for item in pairs if item["shared_hosts"]]
    if shared_host_pairs:
        limits.append("Shared hosts limit evidentiary independence for: " + "; ".join(" × ".join(item["voices"]) for item in shared_host_pairs) + ".")
    gaps = daily_counter_pressure_gaps(source_text, synthesis)
    unmapped = [item["voice"] for item in reports if item["axis"] == "unmapped"]
    if unmapped:
        gaps.append("Unmapped voices require human review before their temporary daily contribution is treated as a stable analytical identity: " + ", ".join(unmapped) + ".")
    review_queue = []
    for item in reports:
        if item["axis"] == "unmapped":
            review_queue.append({"priority": "P2", "entity": item["voice"], "reason": "voice has no canonical descriptor", "action": "assign or review a stable voice identity"})
        if "No day-specific" in item["daily_contribution"]:
            review_queue.append({"priority": "P3", "entity": item["voice"], "reason": "daily contribution is missing", "action": "add a synthesis role or mark insufficient daily evidence"})
    for item in pairs:
        if item["classification"] == "high collapse risk":
            review_queue.insert(0, {"priority": "P1", "entity": " × ".join(item["voices"]), "reason": "shared named object with shared host/lineage", "action": "recover independent lineage or confirm distinct mechanisms"})
        elif item["review_required"]:
            review_queue.append({"priority": "P3", "entity": " × ".join(item["voices"]), "reason": item["classification"], "action": "confirm the pair classification from source and synthesis evidence"})
    recommendation = daily_recommendation(source_text, synthesis)
    limitations = ["This is advisory generated state, not archive evidence or independent corroboration.", "Daily descriptors are provisional specializations of the canonical voice map.", "Automated overlap is a candidate for human review, not semantic adjudication."]
    if not source_text or not synthesis:
        limitations.append("Daily source or synthesis context is incomplete; classifications are low confidence.")
    payload = {"date": run_date, "generated_at": datetime.now(timezone.utc).isoformat(), "source_count": len(source_rows), "voice_count": len(reports), "mapped_voice_count": sum(item["axis"] != "unmapped" for item in reports), "unmapped_voice_count": sum(item["axis"] == "unmapped" for item in reports), "voices": reports, "axis_coverage": dict(axis_coverage), "convergence_clusters": clusters, "independence_limits": limits, "pairs": pairs, "counter_pressure_gaps": gaps, "review_queue": review_queue, "recommendation": recommendation, "limitations": limitations}
    semantic = json.dumps({key: value for key, value in payload.items() if key not in {"generated_at", "content_hash"}}, sort_keys=True, ensure_ascii=False)
    payload["content_hash"] = hashlib.sha256(semantic.encode("utf-8")).hexdigest()[:16]
    return payload


def persist_daily_payload(payload, target=None):
    rendered = render_daily_orthogonality(payload)
    target = target or NG / "work" / "continuity" / "orthogonality" / f"orthogonality-{payload['date']}.md"
    if not target.is_absolute():
        target = ROOT / target
    if not ARGS.dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        normalized_existing = re.sub(r"- \*\*Generated:\*\* `[^`]+`", "- **Generated:** `<normalized>`", existing)
        normalized_rendered = re.sub(r"- \*\*Generated:\*\* `[^`]+`", "- **Generated:** `<normalized>`", rendered)
        if normalized_existing != normalized_rendered:
            target.write_text(rendered, encoding="utf-8", newline="\n")
    return rendered


def date_range(start, end):
    current = start
    while current <= end:
        yield current.isoformat()
        current += timedelta(days=1)


def monthly_rollup(payloads, skipped_dates, start_date, end_date):
    voice_days = defaultdict(list)
    review = []
    gaps = Counter()
    clusters = []
    for payload in payloads:
        for voice in payload["voices"]:
            voice_days[voice["voice"]].append(payload["date"])
        review.extend({**item, "date": payload["date"]} for item in payload["review_queue"])
        for gap in payload["counter_pressure_gaps"]:
            gaps[gap] += 1
        clusters.extend({"date": payload["date"], "cluster": cluster} for cluster in payload["convergence_clusters"] if not cluster.startswith("No material"))
    recurring = {voice: dates for voice, dates in sorted(voice_days.items()) if len(dates) > 1}
    persistent_gaps = [{"gap": gap, "date_count": count} for gap, count in gaps.most_common() if count > 1]
    transitions = []
    for item in clusters:
        if not transitions or transitions[-1]["cluster"] != item["cluster"]:
            transitions.append(item)
    review.sort(key=lambda item: ({"P1": 1, "P2": 2, "P3": 3}.get(item["priority"], 9), item["date"], item["entity"]))
    recommendation = "Compare persistent counter-pressure gaps against independent observations, prioritizing P1 collapse risks and the strongest crisis-object transition."
    payload = {"range": {"start": start_date, "end": end_date}, "generated_at": datetime.now(timezone.utc).isoformat(), "audited_dates": [p["date"] for p in payloads], "skipped_dates": skipped_dates, "missing_context_dates": [p["date"] for p in payloads if any("context is incomplete" in x for x in p["limitations"])], "daily_summaries": [{"date": p["date"], "source_count": p["source_count"], "voice_count": p["voice_count"], "mapped_voice_count": p["mapped_voice_count"], "unmapped_voice_count": p["unmapped_voice_count"], "recommendation": p["recommendation"], "content_hash": p["content_hash"]} for p in payloads], "crisis_object_transitions": transitions, "recurring_voices": recurring, "review_queue": review, "counter_pressure_gaps": persistent_gaps, "recommendation": recommendation, "limitations": ["This is advisory generated state, not archive evidence or independent corroboration.", "Different voices are not independent evidence unless lineage independence has been established.", "Monthly aggregation describes workflow patterns and does not validate operational facts."]}
    semantic = json.dumps({k: v for k, v in payload.items() if k not in {"generated_at", "content_hash"}}, sort_keys=True, ensure_ascii=False)
    payload["content_hash"] = hashlib.sha256(semantic.encode("utf-8")).hexdigest()[:16]
    return payload


def render_monthly_rollup(payload):
    lines = ["# July 2026 Voice Orthogonality Rollup", "", "## Decision Summary", "", f"- Audited dates: {len(payload['audited_dates'])}; skipped dates: {len(payload['skipped_dates'])}; incomplete-context dates: {len(payload['missing_context_dates'])}", f"- Recurring voices: {', '.join(payload['recurring_voices']) or 'none'}", f"- Priority review items: {len(payload['review_queue'])}", f"- Recommendation: {payload['recommendation']}", "", "## Coverage and Data Availability", "", f"- Range: `{payload['range']['start']}` through `{payload['range']['end']}`", f"- Audited: {', '.join(payload['audited_dates']) or 'none'}", f"- Skipped calendar dates without manifest rows: {', '.join(payload['skipped_dates']) or 'none'}", f"- Manifest-backed dates with incomplete context: {', '.join(payload['missing_context_dates']) or 'none'}", "", "## Crisis-Object Transitions", ""]
    lines.extend([f"- `{item['date']}`: {item['cluster']}" for item in payload["crisis_object_transitions"]] or ["- No material transition identified."])
    lines.extend(["", "## Voice and Descriptor Coverage", ""] + ([f"- `{voice}`: {', '.join(dates)}" for voice, dates in payload["recurring_voices"].items()] or ["- No recurring voices identified."]))
    lines.extend(["", "## Recurring Convergence Clusters", ""] + ([f"- `{item['date']}`: {item['cluster']}" for item in payload["crisis_object_transitions"]] or ["- None."]))
    lines.extend(["", "## Lineage and Host-Dependence Patterns", "", "- Review daily independence limits for host and shared-lineage constraints; monthly aggregation does not establish evidentiary independence."])
    lines.extend(["", "## Prioritized Month-Level Review Queue", ""])
    lines.extend([f"{i}. **{x['priority']}** — `{x['date']}` {x['entity']}: {x['reason']} Action: {x['action']}" for i, x in enumerate(payload["review_queue"], 1)] or ["- No review items."])
    lines.extend(["", "## Counter-Pressure Gaps by Crisis Object", ""] + ([f"- {x['gap']} (present on {x['date_count']} audited dates)" for x in payload["counter_pressure_gaps"]] or ["- No persistent gaps identified."]) + ["", "## Highest-Value Orthogonal Tests", "", payload["recommendation"], "", "## Limitations and Non-Evidence Notice", "", f"- Content hash: `{payload['content_hash']}`"] + [f"- Generated: `{payload['generated_at']}`"] + [f"- {x}" for x in payload["limitations"]])
    return "\n".join(lines) + "\n"


def command_daily_orthogonality(states):
    if ARGS.start_date or ARGS.end_date:
        if not (ARGS.start_date and ARGS.end_date) or ARGS.date:
            raise SystemExit(2)
        try:
            start = date.fromisoformat(ARGS.start_date); end = date.fromisoformat(ARGS.end_date)
        except ValueError:
            raise SystemExit(2)
        if start > end:
            raise SystemExit(2)
        manifest_dates = {row.get("date") for row in manifest_rows() if ARGS.start_date <= row.get("date", "") <= ARGS.end_date}
        skipped = [d for d in date_range(start, end) if d not in manifest_dates]
        payloads = [daily_payload(d) for d in sorted(manifest_dates)]
        rollup = monthly_rollup(payloads, skipped, ARGS.start_date, ARGS.end_date)
        target = Path(ARGS.output) if ARGS.output else NG / "work" / "continuity" / "orthogonality" / f"orthogonality-{start.strftime('%Y-%m')}.md"
        if not ARGS.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            existing = target.read_text(encoding="utf-8") if target.exists() else ""
            rendered_rollup = render_monthly_rollup(rollup)
            if re.sub(r"- Generated: `[^`]+`", "- Generated: `<normalized>`", existing) != re.sub(r"- Generated: `[^`]+`", "- Generated: `<normalized>`", rendered_rollup):
                target.write_text(rendered_rollup, encoding="utf-8", newline="\n")
            for payload in payloads:
                persist_daily_payload(payload)
        print(json.dumps(rollup, indent=2, ensure_ascii=False) if ARGS.format == "json" else render_monthly_rollup(rollup))
        return
    run_date = ARGS.date or date.today().isoformat()
    payload = daily_payload(run_date)
    if payload is None:
        error = {"error": "no_manifest_source_set", "date": run_date, "message": f"No manifest-backed source set exists for {run_date}."}
        if ARGS.format == "json": print(json.dumps(error, ensure_ascii=False))
        else: print(f"ERROR [{error['error']}]: {error['message']}", file=sys.stderr)
        raise SystemExit(2)
    rendered = persist_daily_payload(payload, Path(ARGS.output) if ARGS.output else None)
    print(json.dumps(payload, indent=2, ensure_ascii=False) if ARGS.format == "json" else rendered)


def parse_forecast_rows():
    path = NG / "work" / "forecasts" / "forecast-ledger.md"
    hooks = {}
    if not path.exists():
        return hooks
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "Hook ID" in line or set(line.replace("|", "").strip()) <= {"-", ":", " "}:
            continue
        cells = [c.strip().strip("`") for c in line.strip("|").split("|")]
        if len(cells) >= 8 and cells[0].startswith("NG-"):
            hooks[cells[0]] = {"hook_id": cells[0], "date": cells[1], "crisis_object": cells[2], "claim": cells[3], "probability_band": cells[4], "review_date": cells[5], "source_run": cells[6], "status": cells[7], "provenance": "retrospective" if "retrospective" in cells[7] else "ex_ante"}
    return hooks


def parse_state_forecast_links():
    links = defaultdict(list)
    for state in all_states():
        hook = state.get("forecast_hook", "")
        if hook.startswith("NG-"):
            links[hook].append(state)
    return links


def reality_records():
    records = []
    for folder in ("claims", "assessments", "investigations", "transitions", "observables"):
        for path in (NG / "work" / "reality" / folder).glob("*.json"):
            try:
                item = json.loads(path.read_text(encoding="utf-8"))
                item["_folder"] = folder
                records.append(item)
            except (OSError, json.JSONDecodeError):
                continue
    return records


def longitudinal_payload(start_date, end_date):
    hooks = {key: value for key, value in parse_forecast_rows().items() if start_date <= value["date"] <= end_date}
    state_links = parse_state_forecast_links()
    reality = reality_records()
    manifest_sources = {entry.get("id"): entry for entry in manifest_rows()}
    accountability = []
    unresolved = []
    retrospective = []
    host_variation = []
    revisions = []
    reality_summary = Counter()
    for hook_id, hook in sorted(hooks.items()):
        states = state_links.get(hook_id, [])
        source_ids = sorted({sid for state in states for sid in re.findall(r"SRC-[0-9]+", state["source_ids"])})
        hosts = sorted({manifest_sources[sid].get("host_slug") or "unhosted" for sid in source_ids if sid in manifest_sources})
        related = [item for item in reality if hook_id in json.dumps(item, ensure_ascii=False)]
        outcomes = sorted({str(item.get("outcome") or item.get("status")) for item in related})
        evidence_status = sorted({str(item.get("status")) for item in related if item.get("_folder") in {"claims", "assessments", "transitions"}})
        item = {**hook, "states": states, "source_ids": source_ids, "hosts": hosts, "reality_records": [item.get("id") for item in related], "reality_outcomes": outcomes, "evidence_status": evidence_status, "calibration_eligible": hook["provenance"] == "ex_ante" and hook["status"] not in {"excluded_retrospective", "excluded_unscorable"}}
        accountability.append(item)
        if hook["provenance"] == "retrospective" or hook["status"] in {"excluded_retrospective", "excluded_unscorable"}:
            retrospective.append({"hook_id": hook_id, "status": hook["status"], "action": "retain as historical context; exclude from calibration"})
        if hook["status"] == "open" or not outcomes:
            unresolved.append({"hook_id": hook_id, "reason": "open or lacks linked adjudicated outcome", "action": "adjudicate against the forecast observable without forcing an outcome"})
        for state in states:
            if state["state"] in {"revised", "abandoned", "unclear"} or state["revision_note"] not in {"", "—", "-"}:
                revisions.append({"hook_id": hook_id, "voice": state["voice"], "state_id": state["state_id"], "state": state["state"], "revision_note": state["revision_note"]})
        if len(hosts) > 1:
            host_variation.append({"hook_id": hook_id, "voices": sorted({state["voice"] for state in states}), "hosts": hosts, "source_ids": source_ids, "classification": "host-conditioned variation requires review"})
        for outcome in outcomes:
            reality_summary[outcome] += 1
    repeated_frames = []
    by_claim = defaultdict(list)
    for item in accountability:
        by_claim[item["claim"].lower()].append(item)
    for claim, items in by_claim.items():
        if len(items) > 1 and not any(item["states"] and any(state["state"] in {"revised", "abandoned"} for state in item["states"]) for item in items):
            repeated_frames.append({"claim": items[0]["claim"], "hook_ids": [item["hook_id"] for item in items], "action": "check for a new mechanism or evidence rather than treating repetition as confirmation"})
    review = ([{"priority": "P1", "entity": item["hook_id"], "reason": "accountable forecast is open or linked to changed evidence state", "action": "adjudicate forecast against observable"} for item in accountability if item["calibration_eligible"] and (item["status"] == "open" or item["reality_records"])] + [{"priority": "P2", "entity": item["hook_id"], "reason": "voice state revision or abandonment is linked", "action": "confirm whether revision is substantive"} for item in revisions] + [{"priority": "P3", "entity": item["hook_id"], "reason": item["classification"], "action": "separate host framing from guest continuity"} for item in host_variation] + [{"priority": "P3", "entity": item["hook_id"], "reason": "repeated frame without new mechanism", "action": item["action"]} for item in repeated_frames])
    payload = {"range": {"start": start_date, "end": end_date}, "generated_at": datetime.now(timezone.utc).isoformat(), "forecast_summary": {"total": len(accountability), "calibration_eligible": sum(item["calibration_eligible"] for item in accountability), "open": sum(item["status"] == "open" for item in accountability), "outcomes": dict(reality_summary)}, "voice_revision_summary": {"revisions": revisions, "linked_state_count": sum(len(item["states"]) for item in accountability)}, "reality_transition_summary": {"linked_record_count": sum(len(item["reality_records"]) for item in accountability), "outcome_counts": dict(reality_summary), "note": "Evidence status and forecast outcome remain separate classifications."}, "host_conditioning_summary": {"items": host_variation, "shared_host_or_multi_host_count": len(host_variation)}, "accountability_items": accountability, "unresolved_items": unresolved, "retrospective_items": retrospective, "recommendations": {"review_queue": review, "next_observables": ["Adjudicate open accountable forecasts against their declared observable and review date.", "Recover missing forecast-to-state and forecast-to-reality links before assessing performance."]}, "limitations": ["Forecast performance is not a complete measure of analytical quality, and repeated commentary is not independent corroboration.", "No outcome is inferred from narrative similarity or evidence status alone.", "This is advisory generated state and does not mutate research state."]}
    semantic = json.dumps({k: v for k, v in payload.items() if k not in {"generated_at", "content_hash"}}, sort_keys=True, ensure_ascii=False)
    payload["content_hash"] = hashlib.sha256(semantic.encode("utf-8")).hexdigest()[:16]
    return payload


def render_longitudinal(payload):
    lines = ["# Longitudinal Accountability Spine", "", "## Decision Summary", "", f"- Range: {payload['range']['start']} through {payload['range']['end']}; forecasts: {payload['forecast_summary']['total']}; calibration-eligible: {payload['forecast_summary']['calibration_eligible']}; open: {payload['forecast_summary']['open']}", f"- Linked reality records: {payload['reality_transition_summary']['linked_record_count']}; host-conditioned cases: {payload['host_conditioning_summary']['shared_host_or_multi_host_count']}", f"- Review items: {len(payload['recommendations']['review_queue'])}", "", "## Forecast Accountability", ""]
    lines.extend([f"- `{item['hook_id']}` `{item['status']}` `{item['provenance']}`: {item['crisis_object']} — linked states {len(item['states'])}, reality records {len(item['reality_records'])}" for item in payload["accountability_items"]] or ["- No forecasts in range."])
    lines.extend(["", "## Voice-State Continuity and Revision", ""])
    lines.extend([f"- `{item['hook_id']}` `{item['voice']}` `{item['state']}`: {item['revision_note']}" for item in payload["voice_revision_summary"]["revisions"]] or ["- No supported state revisions linked to forecasts."])
    lines.extend(["", "## Reality-Evidence Transitions", "", f"- Linked records: {payload['reality_transition_summary']['linked_record_count']}", f"- Outcomes/statuses: {payload['reality_transition_summary']['outcome_counts']}", "- Forecast outcome and evidence status remain distinct.", "", "## Host-Conditioned Variation", ""])
    lines.extend([f"- `{item['hook_id']}` voices={','.join(item['voices']) or 'unresolved'} hosts={','.join(item['hosts'])}; {item['classification']}" for item in payload["host_conditioning_summary"]["items"]] or ["- No multi-host forecast/state linkage identified."])
    lines.extend(["", "## Forecasts That Survived, Failed, or Remained Unresolvable", ""])
    lines.extend([f"- `{item['hook_id']}` status={item['status']} outcomes={','.join(item['reality_outcomes']) or 'none'}" for item in payload["accountability_items"]] or ["- None resolved by the available linkage."])
    lines.extend(["", "## Repeated Frame Without New Evidence", "", "- Repeated hooks require mechanism and evidence comparison; repetition alone is not corroboration.", "", "## Prioritized Human-Review Queue", ""])
    lines.extend([f"{i}. **{item['priority']}** `{item['entity']}`: {item['reason']} Action: {item['action']}" for i, item in enumerate(payload["recommendations"]["review_queue"], 1)] or ["- No review items."])
    lines.extend(["", "## Highest-Value Next Observables", ""] + [f"- {item}" for item in payload["recommendations"]["next_observables"]] + ["", "## Limitations and Non-Evidence Notice", "", f"- Generated: `{payload['generated_at']}`", f"- Content hash: `{payload['content_hash']}`"] + [f"- {item}" for item in payload["limitations"]])
    return "\n".join(lines) + "\n"

'''legacy renderer disabled
def render_longitudinal_legacy(payload):
    lines = ["# Longitudinal Accountability Spine", "", "## Decision Summary", "", f"- Range: {payload['range']['start']} through {payload['range']['end']}; forecasts: {payload['forecast_summary']['total']}; calibration-eligible: {payload['forecast_summary']['calibration_eligible']}; open: {payload['forecast_summary']['open']}", f"- Linked reality records: {payload['reality_transition_summary']['linked_record_count']}; host-conditioned cases: {payload['host_conditioning_summary']['shared_host_or_multi_host_count']}", f"- Review items: {len(payload['recommendations']['review_queue'])}", "", "## Forecast Accountability", "", *[f"- `{item['hook_id']}` `{item['status']}` `{item['provenance']}`: {item['crisis_object']} — linked states {len(item['states'])}, reality records {len(item['reality_records'])}" for item in payload["accountability_items"]] or ["- No forecasts in range."], "", "## Voice-State Continuity and Revision", ""]
    lines.extend([f"- `{item['hook_id']}` `{item['voice']}` `{item['state']}`: {item['revision_note']}" for item in payload["voice_revision_summary"]["revisions"]] or ["- No supported state revisions linked to forecasts."])
    lines.extend(["", "## Reality-Evidence Transitions", "", f"- Linked records: {payload['reality_transition_summary']['linked_record_count']}", f"- Outcomes/statuses: {payload['reality_transition_summary']['outcome_counts']}", "- Forecast outcome and evidence status remain distinct.", "", "## Host-Conditioned Variation", ""])
    lines.extend([f"- `{item['hook_id']}` voices={','.join(item['voices']) or 'unresolved'} hosts={','.join(item['hosts'])}; {item['classification']}" for item in payload["host_conditioning_summary"]["items"]] or ["- No multi-host forecast/state linkage identified."])
    lines.extend(["", "## Forecasts That Survived, Failed, or Remained Unresolvable", "", *[f"- `{item['hook_id']}` status={item['status']} outcomes={','.join(item['reality_outcomes']) or 'none'}" for item in payload["accountability_items"]] or ["- None resolved by the available linkage."], "", "## Repeated Frame Without New Evidence", "", "- Repeated hooks require mechanism and evidence comparison; repetition alone is not corroboration.", "", "## Prioritized Human-Review Queue", ""])
    lines.extend([f"{i}. **{item['priority']}** `{item['entity']}`: {item['reason']} Action: {item['action']}" for i, item in enumerate(payload["recommendations"]["review_queue"], 1)] or ["- No review items."])
    lines.extend(["", "## Highest-Value Next Observables", "", *[f"- {item}" for item in payload["recommendations"]["next_observables"]], "", "## Limitations and Non-Evidence Notice", "", f"- Generated: `{payload['generated_at']}`", f"- Content hash: `{payload['content_hash']}`", *[f"- {item}" for item in payload["limitations"]]])
    return "\n".join(lines) + "\n"
'''


def command_longitudinal():
    if not ARGS.start_date or not ARGS.end_date:
        error = {"error": "date_range_required", "message": "--start-date and --end-date are required for longitudinal analysis."}
        print(json.dumps(error) if ARGS.format == "json" else error["message"], file=sys.stderr if ARGS.format != "json" else sys.stdout)
        raise SystemExit(2)
    try:
        start = date.fromisoformat(ARGS.start_date); end = date.fromisoformat(ARGS.end_date)
    except ValueError:
        raise SystemExit(2)
    if start > end:
        raise SystemExit(2)
    payload = longitudinal_payload(ARGS.start_date, ARGS.end_date)
    rendered = render_longitudinal(payload)
    target = Path(ARGS.output) if ARGS.output else NG / "work" / "continuity" / "longitudinal" / f"longitudinal-accountability-{start.strftime('%Y-%m')}.md"
    if not target.is_absolute(): target = ROOT / target
    if not ARGS.dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        if re.sub(r"- Generated: `[^`]+`", "- Generated: `<normalized>`", existing) != re.sub(r"- Generated: `[^`]+`", "- Generated: `<normalized>`", rendered):
            target.write_text(rendered, encoding="utf-8", newline="\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False) if ARGS.format == "json" else rendered)


def geometry_object_terms(text):
    aliases = {"red sea": "red-sea", "bab el-mandab": "bab-el-mandab", "bab al-mandab": "bab-el-mandab", "mandeb": "bab-el-mandab", "mandab": "bab-el-mandab", "hormuz": "hormuz", "basing": "basing", "bases": "basing", "base": "basing", "maritime": "maritime-access", "shipping": "maritime-access", "access": "maritime-access", "gulf": "gulf-access", "saudi": "saudi-access", "russia": "russia-nato", "nato": "russia-nato", "ukraine": "russia-nato"}
    lowered = text.lower()
    result = set()
    for phrase, normalized in aliases.items():
        if phrase in lowered:
            result.add(normalized)
    return sorted(result)


def geometry_node(nodes, node_id, node_type, label, **extra):
    nodes.setdefault(node_id, {"id": node_id, "type": node_type, "label": label, **extra})


def geometry_edge(edges, from_id, to_id, edge_type, *, date_value, source_ids=None, hosts=None, lineage_ids=None, objects=None, classification="source-grounded association", confidence="bounded", review_required=False, basis_type="manifest_cooccurrence"):
    source_ids = sorted(set(source_ids or [])); hosts = sorted(set(hosts or [])); lineage_ids = sorted(set(lineage_ids or [])); objects = sorted(set(objects or []))
    if not source_ids and basis_type not in {"human_review_required", "longitudinal_link", "reality_relation"}:
        return False
    edges.append({"from": from_id, "to": to_id, "type": edge_type, "basis_type": basis_type, "source_ids": source_ids, "dates": [date_value], "host_ids": hosts, "lineage_ids": lineage_ids, "crisis_objects": objects, "classification": classification, "confidence": confidence, "review_required": review_required})
    return True


def geometry_daily(run_date):
    source_rows = daily_source_rows(run_date)
    nodes = {}; edges = []; gaps = []; rejected_generic = 0
    for row_index, row in enumerate(source_rows, 1):
        sid = row.get("id") or row.get("source_id") or row.get("source_key") or f"SRC-{run_date.replace('-', '')}-{row_index:02d}"
        if not sid:
            continue
        source_id = f"source:{sid}"; host = row.get("host_slug") or "unhosted"; host_id = f"host:{host}"
        geometry_node(nodes, source_id, "source", sid, date=run_date)
        geometry_node(nodes, host_id, "host", host)
        lineage = row.get("originating_chain") or row.get("lineage_id") or row.get("source_family")
        lineage_id = None
        if lineage:
            lineage_id = f"lineage:{str(lineage).lower().replace(' ', '-') }"
            geometry_node(nodes, lineage_id, "lineage", str(lineage))
        geometry_edge(edges, source_id, host_id, "routed_through", date_value=run_date, source_ids=[sid], hosts=[host], lineage_ids=[lineage_id] if lineage_id else [], basis_type="manifest_cooccurrence")
        if lineage_id:
            geometry_edge(edges, source_id, lineage_id, "belongs_to_lineage", date_value=run_date, source_ids=[sid], hosts=[host], lineage_ids=[lineage_id], basis_type="shared_source_lineage")
        title = str(row.get("title", ""))
        objects = geometry_object_terms(title)
        for voice in row.get("voice_slugs") or []:
            voice_id = f"voice:{voice}"; geometry_node(nodes, voice_id, "voice", voice, axis=VOICE_PROFILES.get(voice, {}).get("axis", "unmapped"))
            geometry_edge(edges, voice_id, source_id, "appeared_in", date_value=run_date, source_ids=[sid], hosts=[host], lineage_ids=[lineage_id] if lineage_id else [], objects=objects, basis_type="manifest_cooccurrence")
            for obj in objects:
                object_id = f"object:{obj}"; geometry_node(nodes, object_id, "object", obj, first_seen=run_date, last_seen=run_date)
                geometry_edge(edges, voice_id, object_id, "addressed", date_value=run_date, source_ids=[sid], hosts=[host], lineage_ids=[lineage_id] if lineage_id else [], objects=[obj], basis_type="manifest_cooccurrence")
    for item in daily_counter_pressure_gaps(daily_text(run_date, "sources.md"), daily_text(run_date, "synthesis.md")):
        object_terms = geometry_object_terms(item)
        gaps.append({"kind": "counter_pressure_gap", "object": object_terms[0] if object_terms else "unresolved-object", "missing_axis": item, "basis": "daily_orthogonality", "dates": [run_date], "action": "supply an independent counter-pressure source or retain the limitation"})
    return {"date": run_date, "nodes": list(nodes.values()), "edges": edges, "counter_pressure_gaps": gaps, "generic_only_rejections": rejected_generic}


def geometry_payload(start_date, end_date):
    dates = [d for d in date_range(date.fromisoformat(start_date), date.fromisoformat(end_date)) if daily_source_rows(d)]
    daily = [geometry_daily(d) for d in dates]
    nodes = {}; edges = []; gaps = []; rejected = 0
    for snapshot in daily:
        for node in snapshot["nodes"]:
            existing = nodes.get(node["id"])
            if existing:
                existing["first_seen"] = min(existing.get("first_seen", snapshot["date"]), snapshot["date"])
                existing["last_seen"] = max(existing.get("last_seen", snapshot["date"]), snapshot["date"])
            else:
                nodes[node["id"]] = {**node, "first_seen": node.get("first_seen", snapshot["date"]), "last_seen": node.get("last_seen", snapshot["date"])}
        edges.extend(snapshot["edges"]); gaps.extend(snapshot["counter_pressure_gaps"]); rejected += snapshot["generic_only_rejections"]
    # Add explicit same-object voice relationships only from existing daily evidence.
    seen = set()
    for snapshot in daily:
        by_object = defaultdict(list)
        for edge in snapshot["edges"]:
            if edge["type"] == "addressed": by_object[edge["to"]].append(edge)
        for object_id, object_edges in by_object.items():
            for left_index, left in enumerate(object_edges):
                for right in object_edges[left_index + 1:]:
                    pair = tuple(sorted((left["from"], right["from"], object_id, snapshot["date"])))
                    if pair in seen or left["from"] == right["from"]: continue
                    seen.add(pair)
                    shared_hosts = set(left["host_ids"]) & set(right["host_ids"]); shared_lineage = set(left["lineage_ids"]) & set(right["lineage_ids"])
                    geometry_edge(edges, left["from"], right["from"], "shared_object", date_value=snapshot["date"], source_ids=left["source_ids"] + right["source_ids"], hosts=shared_hosts, lineage_ids=shared_lineage, objects=[object_id.split(":", 1)[1]], classification="shared-lineage limitation" if shared_lineage else ("shared-host limitation" if shared_hosts else "shared object"), confidence="bounded", review_required=bool(shared_hosts or shared_lineage), basis_type="shared_source_lineage" if shared_lineage else ("shared_host" if shared_hosts else "manifest_cooccurrence"))
    key = lambda edge: (edge["from"], edge["to"], edge["type"], tuple(edge["dates"]))
    unique_edges = {key(edge): edge for edge in edges}
    edges = list(unique_edges.values())
    forecast_hooks = {key: value for key, value in parse_forecast_rows().items() if start_date <= value["date"] <= end_date}
    state_links = parse_state_forecast_links()
    for hook_id, hook in forecast_hooks.items():
        forecast_id = f"forecast:{hook_id}"; geometry_node(nodes, forecast_id, "forecast", hook_id, status=hook["status"], provenance=hook["provenance"])
        for state in state_links.get(hook_id, []):
            source_ids = [value for value in state["source_ids"].split(",") if value]
            geometry_edge(edges, f"voice:{state['voice']}", forecast_id, "forecasted", date_value=hook["date"], source_ids=source_ids, objects=geometry_object_terms(hook["crisis_object"]), classification="explicit forecast-to-voice linkage", confidence="bounded", basis_type="longitudinal_link")
        for record in reality_records():
            if hook_id not in json.dumps(record, ensure_ascii=False):
                continue
            reality_id = f"reality:{record.get('id')}"; geometry_node(nodes, reality_id, "reality", record.get("id", "unknown"), status=record.get("status"), outcome=record.get("outcome"))
            geometry_edge(edges, forecast_id, reality_id, "linked_to", date_value=record.get("as_of", hook["date"]), source_ids=[], objects=geometry_object_terms(hook["crisis_object"]), classification="explicit forecast-to-reality record linkage", confidence="bounded", basis_type="reality_relation")
    node_types = Counter(node["type"] for node in nodes.values()); edge_types = Counter(edge["type"] for edge in edges)
    source_grounded = sum(bool(edge["source_ids"]) for edge in edges); lineage_edges = sum(edge["basis_type"] == "shared_source_lineage" for edge in edges)
    quality = {"node_counts": dict(node_types), "edge_counts": dict(edge_types), "edges_with_source_ids": source_grounded, "edges_with_lineage_basis": lineage_edges, "unsupported_candidates": 0, "generic_only_rejections": rejected, "unmapped_voice_count": sum(node["type"] == "voice" and node.get("axis") == "unmapped" for node in nodes.values()), "unresolved_object_count": sum(node["type"] == "object" and node["id"] == "object:unresolved-object" for node in nodes.values()), "counter_pressure_gap_count": len(gaps), "shared_host_edges": sum(edge["basis_type"] == "shared_host" for edge in edges), "shared_lineage_edges": lineage_edges, "confidence_distribution": dict(Counter(edge["confidence"] for edge in edges))}
    object_dates = defaultdict(list)
    for edge in edges:
        for obj in edge["crisis_objects"]: object_dates[obj].extend(edge["dates"])
    transitions = [{"object": obj, "first_seen": min(ds), "last_seen": max(ds), "date_count": len(set(ds)), "state": "persistent" if len(set(ds)) > 1 else "first appearance"} for obj, ds in sorted(object_dates.items())]
    graph_diffs = []
    for previous, current in zip(daily, daily[1:]):
        old_nodes = {n["id"] for n in previous["nodes"]}; new_nodes = {n["id"] for n in current["nodes"]}; old_edges = {(e["from"], e["to"], e["type"]) for e in previous["edges"]}; new_edges = {(e["from"], e["to"], e["type"]) for e in current["edges"]}
        graph_diffs.append({"from_date": previous["date"], "to_date": current["date"], "nodes_added": sorted(new_nodes - old_nodes), "nodes_removed": sorted(old_nodes - new_nodes), "edges_added": sorted(new_edges - old_edges), "edges_removed": sorted(old_edges - new_edges)})
    operator_queries = {"hosts_create_apparent_convergence": sorted({edge["host_ids"][0] for edge in edges if edge["type"] == "shared_object" and edge["host_ids"]}), "objects_lacking_counter_pressure": sorted({gap["object"] for gap in gaps}), "voices_remain_distinct": sorted(node["label"] for node in nodes.values() if node["type"] == "voice"), "changed_since_prior_date": graph_diffs[-1] if graph_diffs else {}, "shared_host_edges": [edge for edge in edges if edge["basis_type"] == "shared_host"], "review_required": [edge for edge in edges if edge["review_required"]]}
    review = [{"priority": "P1", "entity": f"{edge['from']} × {edge['to']}", "reason": edge["classification"], "action": "confirm distinct mechanisms or recover independent lineage"} for edge in edges if edge["review_required"]]
    payload = {"schema_version": 1, "range": {"start": start_date, "end": end_date}, "generated_at": datetime.now(timezone.utc).isoformat(), "nodes": sorted(nodes.values(), key=lambda n: n["id"]), "edges": sorted(edges, key=lambda e: (e["from"], e["to"], e["type"])), "counter_pressure_gaps": gaps, "graph_diffs": graph_diffs, "object_transitions": transitions, "operator_queries": operator_queries, "review_queue": review, "quality_metrics": quality, "coverage": {"audited_dates": dates, "skipped_dates": [d for d in date_range(date.fromisoformat(start_date), date.fromisoformat(end_date)) if d not in dates]}, "limitations": ["This is advisory generated state, not research evidence.", "Different voices are not independent evidence unless lineage independence has been established.", "Graph density and degree do not indicate authority, correctness, or evidentiary strength."]}
    semantic = json.dumps({k: v for k, v in payload.items() if k not in {"generated_at", "content_hash"}}, sort_keys=True, ensure_ascii=False); payload["content_hash"] = hashlib.sha256(semantic.encode("utf-8")).hexdigest()[:16]
    return payload


def render_geometry(payload):
    q = payload["operator_queries"]
    lines = ["# Narrative Geometry", "", "## Decision Summary", "", f"- Range: {payload['range']['start']} through {payload['range']['end']}; nodes: {len(payload['nodes'])}; edges: {len(payload['edges'])}; counter-pressure gaps: {len(payload['counter_pressure_gaps'])}", f"- Graph quality: {payload['quality_metrics']}", "", "## Graph Coverage", "", f"- Audited dates: {', '.join(payload['coverage']['audited_dates']) or 'none'}", f"- Skipped dates: {', '.join(payload['coverage']['skipped_dates']) or 'none'}", "", "## Crisis-Object Geometry", ""]
    lines.extend([f"- `{item['object']}`: {item['state']} from {item['first_seen']} to {item['last_seen']} ({item['date_count']} dates)" for item in payload["object_transitions"]] or ["- None."])
    """
    lines.extend(["", "## Voice–Host Conditioning", "", *[f"- {edge['from']} → {edge['to']} via {', '.join(edge['host_ids']) or 'unhosted'}; basis={edge['basis_type']}" for edge in payload["edges"] if edge["type"] == "shared_object"] or ["- No shared-object host relationships."])
    lines.extend(["", "## Convergence and Orthogonal Pressure", "", *[f"- {edge['from']} ↔ {edge['to']}: {edge['classification']} objects={','.join(edge['crisis_objects'])}" for edge in payload["edges"] if edge["type"] == "shared_object"] or ["- None."])
    lines.extend(["", "## Shared-Lineage Limits", "", f"- Shared-host edges: {payload['quality_metrics']['shared_host_edges']}; shared-lineage edges: {payload['quality_metrics']['shared_lineage_edges']}", "", "## Object Transitions", ""] + [f"- {item['object']}: {item['state']}" for item in payload["object_transitions"]])
    lines.extend(["", "## Operator Queries", "", f"- Hosts creating apparent convergence: {q['hosts_create_apparent_convergence'] or 'none'}", f"- Objects lacking counter-pressure: {q['objects_lacking_counter_pressure'] or 'none'}", f"- Distinct voices present: {', '.join(q['voices_remain_distinct']) or 'none'}", f"- Changed since prior date: {q['changed_since_prior_date'] or 'none'}", "", "## Prioritized Review Queue", ""] + [f"{i}. **{item['priority']}** {item['entity']}: {item['reason']} Action: {item['action']}" for i, item in enumerate(payload["review_queue"], 1)] + ["", "## Limitations and Non-Evidence Notice", "", f"- Generated: `{payload['generated_at']}`", f"- Content hash: `{payload['content_hash']}`"] + [f"- {item}" for item in payload["limitations"]])
    """
    return "\n".join(lines) + "\n"


def render_geometry_v2(payload):
    q = payload["operator_queries"]
    lines = ["# Narrative Geometry", "", "## Decision Summary", "", f"- Range: {payload['range']['start']} through {payload['range']['end']}; nodes: {len(payload['nodes'])}; edges: {len(payload['edges'])}; counter-pressure gaps: {len(payload['counter_pressure_gaps'])}", f"- Graph quality: {payload['quality_metrics']}", "", "## Graph Coverage", "", f"- Audited dates: {', '.join(payload['coverage']['audited_dates']) or 'none'}", f"- Skipped dates: {', '.join(payload['coverage']['skipped_dates']) or 'none'}", "", "## Crisis-Object Geometry", ""]
    lines.extend([f"- `{item['object']}`: {item['state']} from {item['first_seen']} to {item['last_seen']} ({item['date_count']} dates)" for item in payload["object_transitions"]] or ["- None."])
    lines.extend(["", "## Voice-Host Conditioning", ""])
    lines.extend([f"- {edge['from']} -> {edge['to']}; hosts={','.join(edge['host_ids']) or 'unhosted'}; basis={edge['basis_type']}" for edge in payload["edges"] if edge["type"] == "shared_object"] or ["- No shared-object host relationships."])
    lines.extend(["", "## Convergence and Orthogonal Pressure", ""])
    lines.extend([f"- {edge['from']} <-> {edge['to']}: {edge['classification']}; objects={','.join(edge['crisis_objects'])}" for edge in payload["edges"] if edge["type"] == "shared_object"] or ["- None."])
    lines.extend(["", "## Shared-Lineage Limits", "", f"- Shared-host edges: {payload['quality_metrics']['shared_host_edges']}; shared-lineage edges: {payload['quality_metrics']['shared_lineage_edges']}", "", "## Object Transitions", ""])
    lines.extend([f"- {item['object']}: {item['state']}" for item in payload["object_transitions"]] or ["- None."])
    lines.extend(["", "## Operator Queries", "", f"- Hosts creating apparent convergence: {q['hosts_create_apparent_convergence'] or 'none'}", f"- Objects lacking counter-pressure: {q['objects_lacking_counter_pressure'] or 'none'}", f"- Distinct voices present: {', '.join(q['voices_remain_distinct']) or 'none'}", f"- Changed since prior date: {q['changed_since_prior_date'] or 'none'}", "", "## Prioritized Review Queue", ""])
    lines.extend([f"{i}. **{item['priority']}** {item['entity']}: {item['reason']} Action: {item['action']}" for i, item in enumerate(payload["review_queue"], 1)] or ["- No review items."])
    lines.extend(["", "## Limitations and Non-Evidence Notice", "", f"- Generated: `{payload['generated_at']}`", f"- Content hash: `{payload['content_hash']}`"] + [f"- {item}" for item in payload["limitations"]])
    return "\n".join(lines) + "\n"


def command_geometry():
    if ARGS.date and not (ARGS.start_date or ARGS.end_date): ARGS.start_date = ARGS.date; ARGS.end_date = ARGS.date
    if not ARGS.start_date or not ARGS.end_date:
        raise SystemExit(2)
    try: start = date.fromisoformat(ARGS.start_date); end = date.fromisoformat(ARGS.end_date)
    except ValueError: raise SystemExit(2)
    if start > end: raise SystemExit(2)
    payload = geometry_payload(ARGS.start_date, ARGS.end_date); rendered = render_geometry_v2(payload)
    target = Path(ARGS.output) if ARGS.output else NG / "work" / "continuity" / "geometry" / f"geometry-{start.strftime('%Y-%m') if start != end else start.isoformat()}.md"
    if not target.is_absolute(): target = ROOT / target
    if not ARGS.dry_run:
        target.parent.mkdir(parents=True, exist_ok=True); existing = target.read_text(encoding="utf-8") if target.exists() else ""
        if re.sub(r"- Generated: `[^`]+`", "- Generated: `<normalized>`", existing) != re.sub(r"- Generated: `[^`]+`", "- Generated: `<normalized>`", rendered): target.write_text(rendered, encoding="utf-8", newline="\n")
        json_target = target.with_suffix(".json"); json_target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False) if ARGS.format == "json" else rendered)


def triage_research_seed(item):
    priority = item["priority"]
    category = item["category"]
    eligible = (
        priority == "P1" and category in {"forecast", "lineage"}
    ) or (
        priority == "P2" and category == "counter_pressure"
    )
    if not eligible:
        return None

    entity = item["entity"]
    links = item["links"]
    if category == "forecast":
        decision_context = (
            "Decide what evidence is needed to adjudicate the accountable forecast "
            "against its declared observable without forcing an outcome."
        )
        question = (
            f"What evidence supports, challenges, or leaves unresolved the declared observable for {entity}?"
        )
        rivals = [
            "The declared observable resolves consistently with the forecast.",
            "The observable challenges the forecast or remains unresolved.",
        ]
        route = "reality-check"
        route_reason = "The triage item targets an accountable canonical forecast."
    elif category == "lineage":
        decision_context = (
            "Decide whether apparent analytical convergence reflects distinct "
            "mechanisms or shared sourcing and host dependence."
        )
        question = (
            f"Do {entity} represent distinct mechanisms supported by independent lineage?"
        )
        rivals = [
            "The voices express distinct mechanisms supported by independent lineage.",
            "The apparent convergence descends from shared sourcing or host dependence.",
        ]
        route = "external-research"
        route_reason = "The item requires bounded lineage and mechanism comparison."
    else:
        decision_context = (
            "Decide whether a missing counter-pressure reflects a real analytical "
            "gap or incomplete source coverage."
        )
        question = f"What independent evidence could test the missing counter-pressure for {entity}?"
        rivals = [
            "The missing counter-pressure is a source-coverage gap.",
            "The available record genuinely lacks the proposed counter-pressure.",
        ]
        route = "external-research"
        route_reason = "The item requires an orthogonal evidence search outside canonical state."

    canonical_claim_id = (
        entity if research_handoff.CLAIM_ID_RE.fullmatch(entity) is not None else None
    )
    known_context = [item["reason"]]
    if item["crisis_objects"]:
        known_context.append("Crisis objects: " + ", ".join(item["crisis_objects"]))
    if item["basis"]:
        known_context.append("Triage basis: " + ", ".join(item["basis"]))
    all_source_refs = sorted(set(
        item["source_ids"]
        + links["forecast_ids"]
        + links["reality_ids"]
        + links["geometry_edges"]
    ))
    source_refs = all_source_refs[:20]
    actors = item["voices"][:12]
    source_ids = item["source_ids"][:20]
    if len(all_source_refs) > len(source_refs):
        known_context.append(
            f"{len(all_source_refs) - len(source_refs)} additional references remain on the originating triage item."
        )
    if len(item["voices"]) > len(actors):
        known_context.append(
            f"{len(item['voices']) - len(actors)} additional voices remain on the originating triage item."
        )
    return research_handoff.build_seed(
        producer_workflow="continuity-triage",
        item_id=f"{category}:{item['date']}:{entity}",
        source_refs=source_refs,
        decision_context=decision_context,
        candidate_question=question,
        scope_hints={
            "actors": actors,
            "geography": [],
            "time_window": item["date"],
            "languages": [],
        },
        known_context=known_context,
        unresolved_gaps=[item["action"]],
        rival_hints=rivals,
        routing_workflow=route,
        routing_reason=route_reason,
        identifiers={
            "canonical_claim_id": canonical_claim_id,
            "forecast_ids": links["forecast_ids"],
            "reality_ids": links["reality_ids"],
            "source_ids": source_ids,
        },
    )


def triage_item(priority, category, entity, date_value, *, crisis_objects=None, source_ids=None, voices=None, hosts=None, basis=None, reason, action, links=None):
    item = {"priority": priority, "category": category, "entity": entity, "date": date_value, "crisis_objects": sorted(set(crisis_objects or [])), "source_ids": sorted(set(source_ids or [])), "voices": sorted(set(voices or [])), "hosts": sorted(set(hosts or [])), "basis": sorted(set(basis or [])), "reason": reason, "action": action, "links": links or {"forecast_ids": [], "reality_ids": [], "geometry_edges": []}}
    seed = triage_research_seed(item)
    if seed is not None:
        item["research_brief_seed"] = seed
    return item


def triage_payload(start_date, end_date):
    geometry = geometry_payload(start_date, end_date)
    longitudinal = longitudinal_payload(start_date, end_date)
    queue = []
    for item in longitudinal["accountability_items"]:
        if item["calibration_eligible"] and (item["status"] == "open" or item["reality_records"]):
            queue.append(triage_item("P1", "forecast", item["hook_id"], item["date"], crisis_objects=geometry_object_terms(item["crisis_object"]), source_ids=item["source_ids"], voices=[state["voice"] for state in item["states"]], hosts=item["hosts"], basis=["longitudinal:open_forecast"] + (["reality:linked_record"] if item["reality_records"] else []), reason="Accountable forecast is open or linked to a changed evidence state.", action="Adjudicate against the declared observable without forcing an outcome.", links={"forecast_ids": [item["hook_id"]], "reality_ids": item["reality_records"], "geometry_edges": []}))
    for edge in geometry["edges"]:
        if edge["type"] == "shared_object" and edge["review_required"]:
            queue.append(triage_item("P1", "lineage", f"{edge['from']} × {edge['to']}", edge["dates"][0], crisis_objects=edge["crisis_objects"], source_ids=edge["source_ids"], voices=[edge["from"].split(":", 1)[1], edge["to"].split(":", 1)[1]], hosts=edge["host_ids"], basis=[f"geometry:{edge['basis_type']}", "orthogonality:collapse-risk"], reason=edge["classification"], action="Confirm distinct mechanisms or recover independent lineage.", links={"forecast_ids": [], "reality_ids": [], "geometry_edges": [f"{edge['from']}->{edge['to']}:{edge['type']}"]}))
    for gap in geometry["counter_pressure_gaps"]:
        queue.append(triage_item("P2", "counter_pressure", gap["object"], gap["dates"][0], crisis_objects=[gap["object"]], basis=["daily_orthogonality:counter_pressure_gap"], reason=gap["missing_axis"], action=gap["action"], links={"forecast_ids": [], "reality_ids": [], "geometry_edges": []}))
    unmapped_source_ids = defaultdict(set)
    for edge in geometry["edges"]:
        if edge["type"] == "appeared_in" and edge["from"].startswith("voice:"):
            voice = edge["from"].split(":", 1)[1]
            node = next((n for n in geometry["nodes"] if n["id"] == edge["from"]), None)
            if node and node.get("axis") == "unmapped":
                unmapped_source_ids[voice].update(edge["source_ids"])
    for voice in sorted({node["label"] for node in geometry["nodes"] if node["type"] == "voice" and node.get("axis") == "unmapped"}):
        dates = [node["first_seen"] for node in geometry["nodes"] if node["type"] == "voice" and node["label"] == voice]
        queue.append(triage_item("P2", "lineage", voice, min(dates) if dates else start_date, source_ids=unmapped_source_ids[voice], voices=[voice], basis=["geometry:unmapped_voice"], reason="Voice recurs without a canonical descriptor.", action="Assign or review a stable descriptor before using it as a durable identity."))
    missing_context_dates = [d for d in date_range(date.fromisoformat(start_date), date.fromisoformat(end_date)) if daily_source_rows(d) and (not daily_text(d, "sources.md") or not daily_text(d, "synthesis.md"))]
    if missing_context_dates:
        for missing_date in missing_context_dates:
            queue.append(triage_item("P3", "editorial", missing_date, missing_date, basis=["longitudinal:incomplete_context"], reason="Daily source or synthesis context is incomplete.", action="Recover context or retain the bounded low-confidence limitation."))
    deduped = {}
    for item in queue:
        key = (item["priority"], item["category"], item["entity"], item["reason"])
        if key not in deduped:
            deduped[key] = item
        else:
            deduped[key]["date"] = min(deduped[key]["date"], item["date"])
    queue = list(deduped.values())
    rank = {"P1": 1, "P2": 2, "P3": 3}
    queue.sort(key=lambda item: (rank[item["priority"]], item["category"], item["date"], item["entity"]))
    gap_map = {}
    for gap in geometry["counter_pressure_gaps"]:
        key = (gap["object"], gap["missing_axis"])
        if key not in gap_map:
            gap_map[key] = dict(gap)
        else:
            gap_map[key]["dates"] = sorted(set(gap_map[key]["dates"]) | set(gap["dates"]))
    payload = {"range": {"start": start_date, "end": end_date}, "generated_at": datetime.now(timezone.utc).isoformat(), "summary": {"total_items": len(queue), "p1": sum(x["priority"] == "P1" for x in queue), "p2": sum(x["priority"] == "P2" for x in queue), "p3": sum(x["priority"] == "P3" for x in queue)}, "p1_immediate_review": [x for x in queue if x["priority"] == "P1"], "p2_structural_review": [x for x in queue if x["priority"] == "P2"], "p3_quality_review": [x for x in queue if x["priority"] == "P3"], "queue": queue, "forecast_accountability": longitudinal["forecast_summary"], "reality_check": longitudinal["reality_transition_summary"], "counter_pressure": list(gap_map.values()), "host_lineage_limits": [x for x in geometry["edges"] if x["review_required"]], "transitions": geometry["object_transitions"], "quality_metrics": geometry["quality_metrics"], "coverage": geometry["coverage"], "limitations": ["This queue prioritizes research attention; it does not adjudicate truth, score voices, resolve forecasts, or authorize publication.", "Missing evidence is not treated as negative evidence.", "Different voices are not independent evidence unless lineage independence has been established."]}
    semantic = json.dumps({k: v for k, v in payload.items() if k not in {"generated_at", "content_hash"}}, sort_keys=True, ensure_ascii=False); payload["content_hash"] = hashlib.sha256(semantic.encode("utf-8")).hexdigest()[:16]
    return payload


def render_triage(payload):
    lines = ["# Continuity Triage", "", "## Decision Summary", "", f"- Range: {payload['range']['start']} through {payload['range']['end']}; total items: {payload['summary']['total_items']}; P1: {payload['summary']['p1']}; P2: {payload['summary']['p2']}; P3: {payload['summary']['p3']}", "", "## P1 Immediate Review", ""]
    for title, key in (("P1 Immediate Review", "p1_immediate_review"), ("P2 Structural Review", "p2_structural_review"), ("P3 Quality and Completeness Review", "p3_quality_review")):
        if title != "P1 Immediate Review": lines.extend(["", f"## {title}", ""])
        lines.extend([
            f"{i}. **{item['entity']}** [{item['category']}] {item['reason']} Action: {item['action']}"
            + (" Research Brief seed available; select this item before expansion." if "research_brief_seed" in item else "")
            for i, item in enumerate(payload[key], 1)
        ] or ["- None."])
    lines.extend(["", "## Forecast Accountability Queue", "", f"- {payload['forecast_accountability']}", "", "## Reality-Check Queue", "", f"- Linked reality records: {payload['reality_check']['linked_record_count']}", "", "## Counter-Pressure and Missing-Observable Queue", ""] + [f"- {gap['object']}: {gap['missing_axis']} Action: {gap['action']}" for gap in payload["counter_pressure"]])
    lines.extend(["", "## Host and Lineage Limitations", "", f"- Reviewable geometry relationships: {len(payload['host_lineage_limits'])}", "", "## Crisis-Object Transition Watch", ""] + [f"- {item['object']}: {item['state']} ({item['first_seen']}–{item['last_seen']})" for item in payload["transitions"]] + ["", "## Editorial Compression Warnings", "", "- Preserve counter-pressure and lineage limitations when compressing the daily brief.", "", "## Coverage and Quality Metrics", "", f"- {payload['quality_metrics']}", "", "## Limitations and Non-Evidence Notice", "", f"- Generated: `{payload['generated_at']}`", f"- Content hash: `{payload['content_hash']}`"] + [f"- {item}" for item in payload["limitations"]])
    return "\n".join(lines) + "\n"


def command_triage():
    if ARGS.date and not (ARGS.start_date or ARGS.end_date): ARGS.start_date = ARGS.date; ARGS.end_date = ARGS.date
    if not ARGS.start_date or not ARGS.end_date: raise SystemExit(2)
    try: start = date.fromisoformat(ARGS.start_date); end = date.fromisoformat(ARGS.end_date)
    except ValueError: raise SystemExit(2)
    if start > end: raise SystemExit(2)
    payload = triage_payload(ARGS.start_date, ARGS.end_date); rendered = render_triage(payload)
    target = Path(ARGS.output) if ARGS.output else NG / "work" / "continuity" / "triage" / f"triage-{start.strftime('%Y-%m') if start != end else start.isoformat()}.md"
    if not target.is_absolute(): target = ROOT / target
    if not ARGS.dry_run:
        target.parent.mkdir(parents=True, exist_ok=True); existing = target.read_text(encoding="utf-8") if target.exists() else ""
        if re.sub(r"- Generated: `[^`]+`", "- Generated: `<normalized>`", existing) != re.sub(r"- Generated: `[^`]+`", "- Generated: `<normalized>`", rendered): target.write_text(rendered, encoding="utf-8", newline="\n")
        target.with_suffix(".json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False) if ARGS.format == "json" else rendered)


def command_validate(states):
    failures = []
    ids = set()
    source_ids = set()
    for source_file in DAILY.glob("*/sources.md"):
        source_ids.update(re.findall(r"`(SRC-[0-9]+)`", source_file.read_text(encoding="utf-8")))
    for state in states:
        sid = state["state_id"]
        if sid in ids: failures.append(f"duplicate state id: {sid}")
        ids.add(sid)
        if state["state"] not in STATES: failures.append(f"invalid state {state['state']}: {sid}")
        if state["expression_type"] not in EXPRESSION: failures.append(f"invalid expression type {state['expression_type']}: {sid}")
        for source in re.findall(r"SRC-[0-9]+", state["source_ids"]):
            if source not in source_ids: failures.append(f"missing source {source}: {sid}")
    daily_text = "\n".join(p.read_text(encoding="utf-8") for p in DAILY.glob("*/synthesis.md"))
    for sid in re.findall(r"STATE-[A-Z0-9-]+", daily_text):
        if sid not in ids: failures.append(f"daily state has no ledger: {sid}")
    emit({"state_count": len(states), "ledger_count": len(list(ledgers())), "failures": failures, "status": "pass" if not failures else "fail"}, "Continuity Validation")
    return 0 if not failures else 1


def main():
    global ARGS
    ARGS = parse_args()
    states = all_states()
    if ARGS.command == "states": command_states(states)
    elif ARGS.command == "revisions": command_revisions(states)
    elif ARGS.command == "forecasts": command_forecasts(states)
    elif ARGS.command == "hosts": command_hosts(states)
    elif ARGS.command == "convergence": command_convergence(states)
    elif ARGS.command == "select-voices": command_select(states)
    elif ARGS.command == "orthogonality": command_orthogonality(states)
    elif ARGS.command == "longitudinal": command_longitudinal()
    elif ARGS.command == "geometry": command_geometry()
    elif ARGS.command == "triage": command_triage()
    else: return command_validate(states)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

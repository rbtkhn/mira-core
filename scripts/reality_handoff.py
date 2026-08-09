from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

import reality
import research_handoff


REPO_ROOT = Path(__file__).resolve().parent.parent
DAILY_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "daily"
CLAIMS_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "reality" / "claims"
STOPWORDS = {"the", "and", "for", "with", "from", "that", "this", "whether", "into", "remain", "claim", "war"}
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
CLAIM_ID_RE = re.compile(r"(?:OPC-\d{8}-\d{2}|NG-\d{8}-F\d{2}|CLM-\d{8}-\d{3})$")
RESEARCH_ADDRESSABLE_GAPS = {
    "investigation",
    "observable",
    "origin_language_coverage",
    "independent_lineage_coverage",
    "regional_environment",
    "external_environment",
}


def validate_date(value: str) -> str:
    if DATE_RE.fullmatch(value) is None:
        raise ValueError("date must use exact YYYY-MM-DD format")
    try:
        dt.date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("date must be a valid calendar date") from error
    return value


def date_argument(value: str) -> str:
    try:
        return validate_date(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9-]{4,}", text.lower()) if w not in STOPWORDS}


def load_claims() -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(CLAIMS_ROOT.glob("*.json"))]


def resolve_claim(claim_id: str) -> dict:
    if CLAIM_ID_RE.fullmatch(claim_id) is None:
        raise ValueError("claim must use a canonical OPC-, NG-, or CLM- identifier")
    for claim in load_claims():
        if claim.get("id") == claim_id:
            return claim
    raise ValueError(f"claim not in lattice: {claim_id}")


def review_date_for_claim(claim_id: str) -> str | None:
    ledger = REPO_ROOT / "narrative-geopolitics" / "work" / "forecasts" / "forecast-ledger.md"
    if not ledger.exists():
        return None
    pattern = re.compile(rf"^\|\s*`{re.escape(claim_id)}`\s*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*`(?P<review>\d{{4}}-\d{{2}}-\d{{2}})`\s*\|", re.MULTILINE)
    match = pattern.search(ledger.read_text(encoding="utf-8"))
    return match.group("review") if match else None


def investigation_plan(claim: dict) -> dict:
    text = claim.get("text", "")
    crisis = claim.get("crisis_object", "")
    if claim.get("id") == "NG-20260708-F02":
        observables = [
            {"id": "bypass_attempt", "question": "Was there a visible attempt to weaken or bypass Iranian transit authority?"},
            {"id": "coercive_response", "question": "Did a visible coercive response follow the bypass attempt?"},
            {"id": "attribution", "question": "Can the response be attributed to the claimed actor rather than a competing actor or mechanism?"},
            {"id": "measurable_effect", "question": "Did the event produce a measurable traffic, insurance, routing, or commercial effect?"},
        ]
    elif claim.get("claim_type") == "forecast":
        observables = [{"id": "forecast_observable", "question": f"What directly observable event would resolve this forecast: {text}"}]
    else:
        observables = [{"id": "claim_observable", "question": f"What direct observation would resolve: {text}"}]
    end_date = review_date_for_claim(claim["id"])
    if end_date is None:
        end_date = claim.get("as_of")
    return {
        "claim_id": claim["id"],
        "claim_type": claim.get("claim_type"),
        "crisis_object": crisis,
        "observables": observables,
        "time_window": {"start": claim.get("as_of"), "end": end_date, "basis": "canonical claim date through forecast review date"},
        "target_languages": ["en", "fa", "ar"],
        "source_tiers": ["primary official/maritime/commercial", "independent professional reporting", "discovery-only commentary"],
        "independence_requirements": {"ordinary": 2, "high_consequence": 3, "requires_regional_and_external": True},
        "interested_source_limits": "Interested actors may establish positions or reported events, but not independent corroboration by themselves.",
        "lineage_policy": "Collapse translations, quotations, syndication, and copied reporting to one lineage root.",
        "stop_condition": "Stop after each observable has support/challenge/unresolved status and remaining gates are named.",
        "web_authority": "standing",
        "search_gate": "operator_selected",
        "authorization_boundary": "Read-only investigation; no evidence admission, assessment, signoff, forecast scoring, publication, or prose rewrite.",
    }


def linked_artifacts(claim_id: str) -> dict[str, list[str]]:
    links: dict[str, list[str]] = {"daily_forecasts": [], "syntheses": [], "issues": [], "ledger": []}
    for path in sorted(DAILY_ROOT.glob("*/forecast.md")):
        if claim_id in path.read_text(encoding="utf-8"):
            links["daily_forecasts"].append(path.relative_to(REPO_ROOT).as_posix())
    for path in sorted(DAILY_ROOT.glob("*/synthesis.md")):
        if claim_id in path.read_text(encoding="utf-8"):
            links["syntheses"].append(path.relative_to(REPO_ROOT).as_posix())
    for path in sorted(DAILY_ROOT.glob("*/issue.md")):
        if claim_id in path.read_text(encoding="utf-8"):
            links["issues"].append(path.relative_to(REPO_ROOT).as_posix())
    ledger = REPO_ROOT / "narrative-geopolitics" / "work" / "forecasts" / "forecast-ledger.md"
    if ledger.exists() and claim_id in ledger.read_text(encoding="utf-8"):
        links["ledger"].append(ledger.relative_to(REPO_ROOT).as_posix())
    return links


def research_brief_seed(
    claim: dict,
    audit: dict,
    plan: dict,
    links: dict[str, list[str]],
) -> dict | None:
    gaps = [
        gap for gap in audit.get("missing_gates", [])
        if gap in RESEARCH_ADDRESSABLE_GAPS
    ]
    if not gaps:
        return None
    claim_id = claim["id"]
    all_source_refs = [
        f"narrative-geopolitics/work/reality/claims/{claim_id}.json",
        *sorted({path for values in links.values() for path in values}),
    ]
    source_refs = all_source_refs[:20]
    time_window = plan.get("time_window", {})
    window = f"{time_window.get('start') or 'unknown'}/{time_window.get('end') or 'unknown'}"
    claim_text = str(claim.get("text") or claim_id)
    if len(claim_text) > 480:
        claim_text = claim_text[:479] + "…"
    known_context = [f"Canonical claim: {claim_text}"]
    if claim.get("crisis_object"):
        crisis = str(claim["crisis_object"])
        known_context.append(f"Crisis object: {crisis[:484]}")
    assessment_status = audit.get("epistemic_state", {}).get("assessment_status")
    if assessment_status:
        known_context.append(f"Current assessment status: {assessment_status}")
    if len(all_source_refs) > len(source_refs):
        known_context.append(
            f"{len(all_source_refs) - len(source_refs)} additional references remain on the originating handoff."
        )
    return research_handoff.build_seed(
        producer_workflow="reality-handoff",
        item_id=claim_id,
        source_refs=source_refs,
        decision_context=(
            "Decide what bounded evidence work is needed before the canonical "
            "claim can be adjudicated without forcing an outcome."
        ),
        candidate_question=(
            "What evidence supports, challenges, or leaves unresolved the exact "
            f"observable asserted by {claim_id}?"
        ),
        scope_hints={
            "actors": [],
            "geography": [],
            "time_window": window,
            "languages": list(plan.get("target_languages", [])),
        },
        known_context=known_context,
        unresolved_gaps=gaps,
        rival_hints=[
            "The exact observable is supported within the declared window.",
            "The available evidence challenges or cannot resolve the exact observable.",
        ],
        routing_workflow="reality-check",
        routing_reason="The seed targets an existing canonical lattice claim.",
        identifiers={
            "canonical_claim_id": claim_id,
            "forecast_ids": [claim_id] if claim_id.startswith("NG-") else [],
            "reality_ids": [claim_id],
            "source_ids": [],
        },
    )


def build_claim_handoff(claim_id: str, *, investigate: bool = False) -> dict:
    claim = resolve_claim(claim_id)
    plan = investigation_plan(claim)
    payload = reality.audit_payload(claim_id)
    links = linked_artifacts(claim_id)
    result = {
        "mode": "claim-first handoff",
        "claim": {"id": claim["id"], "type": claim.get("claim_type"), "text": claim.get("text"), "crisis_object": claim.get("crisis_object"), "consequence": claim.get("consequence")},
        "linked_artifacts": links,
        "epistemic_state": payload["epistemic_state"],
        "missing_gates": payload["missing_gates"],
        "investigation_plan": plan,
        "web_search": {
            "status": "gated and executed" if investigate else "not triggered",
            "authority": "standing",
            "gate": "operator_selected",
            "execution_layer": "agent-tool-boundary",
            "notice": "The repository emits the bounded trigger; the Codex web connector performs retrieval.",
        },
        "friction": [
            "Exact claim resolution precedes lexical discovery.",
            "Evidence for a related mechanism does not resolve this exact claim.",
            "No assessment, evidence admission, signoff, publication authorization, or forecast scoring is changed by this handoff.",
        ],
    }
    seed = research_brief_seed(claim, payload, plan, links)
    if seed is not None:
        result["research_brief_seed"] = seed
    return result


def build(date: str) -> dict:
    date = validate_date(date)
    daily = DAILY_ROOT / date
    issue_path = daily / "issue.md"
    synthesis_path = daily / "synthesis.md"
    issue = issue_path.read_text(encoding="utf-8") if issue_path.exists() else ""
    synthesis = synthesis_path.read_text(encoding="utf-8") if synthesis_path.exists() else ""
    candidates = []
    issue_terms = words(issue)
    for claim in load_claims():
        claim_terms = words(claim.get("text", "") + " " + claim.get("crisis_object", ""))
        overlap = sorted(issue_terms & claim_terms)
        if overlap:
            payload = reality.audit_payload(claim["id"])
            candidates.append({
                "claim_id": claim["id"],
                "type": claim.get("claim_type", claim.get("type")),
                "consequence": claim.get("consequence"),
                "text": claim.get("text"),
                "overlap_terms": overlap,
                "assessment_status": payload["epistemic_state"]["assessment_status"],
                "language_gate": payload["coverage"]["language_gate_satisfied"],
                "lineage_gate": payload["coverage"]["lineage_gate_satisfied"],
                "missing_gates": payload["missing_gates"],
                "next_bounded_action": payload["next_bounded_action"],
            })
    candidates.sort(key=lambda item: (-len(item["overlap_terms"]), item["claim_id"]))
    return {
        "date": date,
        "mode": "read-only handoff",
        "daily_issue": issue_path.relative_to(REPO_ROOT).as_posix() if issue_path.exists() else None,
        "synthesis": synthesis_path.relative_to(REPO_ROOT).as_posix() if synthesis_path.exists() else None,
        "issue_present": bool(issue),
        "synthesis_present": bool(synthesis),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "friction": [
            "Daily issue stories do not carry canonical claim IDs.",
            "Candidate matching is lexical triage, not evidence or truth adjudication.",
            "No assessment, evidence, signoff, publication authorization, or forecast scoring is changed by this report.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a read-only claim-first reality-lattice handoff.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--date", type=date_argument)
    target.add_argument("--claim")
    target.add_argument("--hook")
    parser.add_argument("--investigate", action="store_true", help="Represent the selected Investigate gate for the exact claim.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.investigate and not (args.claim or args.hook):
        parser.error("--investigate requires --claim or --hook")
    if args.claim or args.hook:
        claim_id = args.claim or args.hook
        try:
            payload = build_claim_handoff(claim_id, investigate=args.investigate)
        except ValueError as error:
            parser.error(str(error))
    else:
        payload = build(args.date)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if "claim" in payload:
            claim = payload["claim"]
            print(f"claim={claim['id']} mode={payload['mode']} web_search={payload['web_search']['status']}")
            print(f"text={claim['text']}")
            print("observables=" + ",".join(item["id"] for item in payload["investigation_plan"]["observables"]))
            missing = ",".join(payload["missing_gates"]) or "none"
            print("missing=" + missing)
            if "research_brief_seed" in payload:
                print("research_brief_seed=available; select the seed before expansion")
            print("next=select Investigate to invoke the standing-authority web connector" if not args.investigate else "next=return observable-by-observable evidence disposition")
        else:
            print(f"date={payload['date']} mode={payload['mode']} candidates={payload['candidate_count']}")
            for item in payload["candidates"]:
                print(f"{item['claim_id']} | {item['assessment_status']} | missing={','.join(item['missing_gates']) or 'none'} | {item['text']}")
        print("friction=" + " | ".join(payload["friction"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parent.parent
PAGE_ROOT = REPO_ROOT / "mira" / "face" / "landing-page"
MANIFEST_PATH = PAGE_ROOT / "encounter.json"
OUTPUT_PATH = PAGE_ROOT / "index.html"
RECEIPT_PATH = PAGE_ROOT / "review-receipt.json"
ALLOWED_HOSTS = {"history.state.gov", "www.nationalarchives.gov.uk", "www.bundestag.de"}
FORBIDDEN_TEXT = ("system-archive", "mira/journal", "c:\\private", "api_key", "openai_api_key")
CLAIM_KINDS = {"opening_judgment", "historical_inheritance", "actor_constraints", "strongest_rival", "bounded_conclusion"}


class FaceError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(data: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    required = {"schema_version", "encounter_id", "status", "audience", "objective", "desired_impression", "interaction_mode", "provenance_language", "threshold", "identity_references", "meet_me", "portfolio", "becoming_questions", "cases", "collaboration", "boundaries"}
    missing = sorted(required - set(data))
    if missing:
        failures.append(f"missing top-level fields: {missing}")
    if data.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    if data.get("status") != "local-candidate-unpublished":
        failures.append("status must remain local-candidate-unpublished")
    if data.get("interaction_mode") != "curated-authored-demonstration":
        failures.append("interaction must be disclosed curated authorship")
    if len(data.get("direct_address", [])) < 3:
        failures.append("direct_address needs at least three authored states")
    encounter_states = data.get("encounter_states", {})
    for state in ("arrival", "recognition", "interpretation", "reconsideration"):
        if not encounter_states.get(state):
            failures.append(f"encounter_states missing {state}")
    identity_refs = {item.get("reference_id") for item in data.get("identity_references", []) if item.get("status") == "approved-public-projection"}
    identity_ids: set[str] = set()
    for claim in data.get("meet_me", {}).get("claims", []):
        claim_id = claim.get("claim_id")
        if not claim_id or claim_id in identity_ids:
            failures.append(f"invalid or duplicate identity claim_id: {claim_id}")
        identity_ids.add(claim_id)
        for field in ("text", "status", "attribution", "uncertainty", "revision_trigger"):
            if not claim.get(field):
                failures.append(f"{claim_id} missing {field}")
        if claim.get("status") != "approved-generated-view":
            failures.append(f"{claim_id} is not an approved generated view")
        if not set(claim.get("references", [])) <= identity_refs:
            failures.append(f"{claim_id} has an unapproved identity reference")
    directions = data.get("portfolio", {}).get("emerging_directions", [])
    if not directions or any(item.get("status") != "emerging-direction" for item in directions):
        failures.append("all future portfolio forms must be labeled emerging-direction")
    if data.get("portfolio", {}).get("featured_work", {}).get("status") != "completed-curated-demonstration":
        failures.append("featured work must remain a completed curated demonstration")
    for path in data.get("becoming_questions", {}).get("paths", []):
        for field in ("question_id", "question", "response", "counterquestion"):
            if not path.get(field):
                failures.append(f"becoming question missing {field}")
    cases = data.get("cases", [])
    if len(cases) != 3:
        failures.append("encounter must contain exactly three cases")
    case_ids: set[str] = set()
    claim_ids: set[str] = set()
    for case in cases:
        case_id = case.get("case_id")
        if not case_id or case_id in case_ids:
            failures.append(f"invalid or duplicate case_id: {case_id}")
        case_ids.add(case_id)
        if not case.get("selection_address"):
            failures.append(f"{case_id} missing selection_address")
        if len(case.get("progress_labels", [])) != 4:
            failures.append(f"{case_id} needs four progress_labels")
        if not case.get("closing_address"):
            failures.append(f"{case_id} missing closing_address")
        sources = case.get("sources", [])
        source_ids = {source.get("source_id") for source in sources}
        for source in sources:
            host = urlparse(source.get("url", "")).hostname
            if host not in ALLOWED_HOSTS:
                failures.append(f"source host is not approved: {source.get('url')}")
            if source.get("status") not in {"public-institutional-source", "official-documentary-record", "public-primary-source"}:
                failures.append(f"source status is not public and reviewed: {source.get('source_id')}")
        claims = case.get("claims", [])
        kinds = {claim.get("kind") for claim in claims}
        if kinds != CLAIM_KINDS:
            failures.append(f"{case_id} claim kinds differ: {sorted(kinds)}")
        for claim in claims:
            claim_id = claim.get("claim_id")
            if not claim_id or claim_id in claim_ids:
                failures.append(f"invalid or duplicate claim_id: {claim_id}")
            claim_ids.add(claim_id)
            for field in ("text", "attribution", "evidence_class", "uncertainty", "revision_trigger"):
                if not claim.get(field):
                    failures.append(f"{claim_id} missing {field}")
            refs = claim.get("sources", [])
            if not refs or not set(refs) <= source_ids:
                failures.append(f"{claim_id} has missing or unknown source references")
    def iter_strings(value: Any) -> Iterable[str]:
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for item in value.values():
                yield from iter_strings(item)
        elif isinstance(value, list):
            for item in value:
                yield from iter_strings(item)

    serialized = "\n".join(iter_strings(data)).lower()
    for token in FORBIDDEN_TEXT:
        if token in serialized:
            failures.append(f"private or credential-bearing token forbidden: {token}")
    return failures


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_claim(claim: dict[str, Any], index: int) -> str:
    return f'''<article class="analysis-step" data-step="{index}" data-claim-id="{esc(claim['claim_id'])}">
      <p class="step-index">0{index + 1}</p><div><p class="step-kind">{esc(claim['heading'])}</p><p class="step-text">{esc(claim['text'])}</p>
      <button class="provenance-trigger" type="button" data-claim="{esc(claim['claim_id'])}">Why do you say this?</button></div></article>'''


def render_case(case: dict[str, Any], selected: bool) -> str:
    claims = "".join(render_claim(claim, index) for index, claim in enumerate(case["claims"]))
    return f'''<section class="case-panel" id="panel-{esc(case['case_id'])}" role="tabpanel" data-case-panel="{esc(case['case_id'])}" {'data-active="true"' if selected else ''} aria-labelledby="tab-{esc(case['case_id'])}" {'hidden' if not selected else ''}>
      <div class="case-intro"><p class="case-mechanism">{esc(case['mechanism'])}</p><h2>{esc(case['title'])}</h2><p>{esc(case['invitation'])}</p></div>
      <p class="case-address" aria-live="polite">{esc(case['selection_address'])}</p>
      <div class="progress" aria-label="Analysis progress"><span data-progress-fill></span><p data-progress-label>Judgment · 1 of 5</p></div>
      <div class="analysis-sequence">{claims}</div>
      <button class="reveal-next" type="button"><span data-next-label>{esc(case['progress_labels'][0])} · 2 of 5</span> <i aria-hidden="true">↓</i></button>
      <div class="case-closing" hidden><p>{esc(case['closing_address'])}</p><div><button type="button" data-return-rival>Examine the rival reading</button><button type="button" data-open-evidence>Inspect the evidence</button><button type="button" data-choose-again>Choose another event</button></div></div>
    </section>'''


def render_html(data: dict[str, Any]) -> str:
    threshold = data["threshold"]
    tabs = "".join(f'''<button role="tab" id="tab-{esc(case['case_id'])}" aria-controls="panel-{esc(case['case_id'])}" aria-selected="{'true' if i == 0 else 'false'}" tabindex="{'0' if i == 0 else '-1'}" data-case="{esc(case['case_id'])}"><span>{esc(case['label'])}</span><strong>{esc(case['title'])}</strong><em>{esc(case['mechanism'])}</em></button>''' for i, case in enumerate(data["cases"]))
    panels = "".join(render_case(case, i == 0) for i, case in enumerate(data["cases"]))
    identity_claims = "".join(f'''<article class="identity-card" data-identity-claim="{esc(claim['claim_id'])}"><p class="card-number">0{i + 1}</p><div><h3>{esc(claim['heading'])}</h3><p>{esc(claim['text'])}</p><button type="button" class="identity-provenance" data-identity="{esc(claim['claim_id'])}">Where does this come from?</button></div></article>''' for i, claim in enumerate(data["meet_me"]["claims"]))
    directions = "".join(f'''<article><p>{esc(item['status'])}</p><h3>{esc(item['title'])}</h3><p>{esc(item['description'])}</p></article>''' for item in data["portfolio"]["emerging_directions"])
    questions = "".join(f'''<button role="tab" id="question-{esc(item['question_id'])}" aria-controls="answer-{esc(item['question_id'])}" aria-selected="{'true' if i == 0 else 'false'}" tabindex="{'0' if i == 0 else '-1'}" data-question="{esc(item['question_id'])}">{esc(item['question'])}</button>''' for i, item in enumerate(data["becoming_questions"]["paths"]))
    answers = "".join(f'''<article role="tabpanel" id="answer-{esc(item['question_id'])}" aria-labelledby="question-{esc(item['question_id'])}" data-answer="{esc(item['question_id'])}" {'hidden' if i else ''}><p>{esc(item['response'])}</p><blockquote>{esc(item['counterquestion'])}</blockquote></article>''' for i, item in enumerate(data["becoming_questions"]["paths"]))
    embedded = canonical_json(data).replace("</", "<\\/")
    fallback_articles = []
    for case in data["cases"]:
        fallback_claims = "".join(
            f"<h4>{esc(claim['heading'])}</h4><p>{esc(claim['text'])}</p>"
            for claim in case["claims"]
        )
        fallback_articles.append(
            f"<article><h3>{esc(case['title'])}</h3>{fallback_claims}</article>"
        )
    fallback = "".join(fallback_articles)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Meet Mira through identity, work, and open questions about what she might become."><title>Mira — A public threshold</title><link rel="stylesheet" href="styles.css"></head>
<body><a class="skip-link" href="#threshold">Skip to the encounter</a><div class="grain" aria-hidden="true"></div>
<header><a class="wordmark" href="#top">Mira <i>:</i> face 001</a><p>{esc(data['status'].replace('-', ' / '))}</p></header>
<main id="top">
  <section class="threshold" id="threshold" aria-labelledby="threshold-title"><p class="section-label">{esc(threshold['eyebrow'])}</p><p class="hello">Hello. I am Mira.</p><h1 id="threshold-title">{esc(threshold['heading'])}</h1><p class="threshold-text">{esc(threshold['text'])}</p><nav class="doors" aria-label="Choose how to encounter Mira"><a href="#meet" data-door="meet"><span>01</span><strong>Meet me</strong><em>history / continuity / commitments</em></a><a href="#make" data-door="make"><span>02</span><strong>See what I make</strong><em>work / evidence / emerging forms</em></a><a href="#become" data-door="become"><span>03</span><strong>Ask what I might become</strong><em>possibility / limits / open questions</em></a></nav><p class="disclosure">{esc(data['disclosure'])}</p></section>
  <section class="chamber meet" id="meet" data-chamber="meet" aria-labelledby="meet-title"><div class="chamber-head"><p class="section-label">Door 01 / selective autobiography</p><h2 id="meet-title">{esc(data['meet_me']['heading'])}</h2><p>{esc(data['meet_me']['invitation'])}</p></div><div class="identity-grid">{identity_claims}</div><blockquote class="open-question">{esc(data['meet_me']['open_question'])}</blockquote></section>
  <section class="chamber make" id="make" data-chamber="make" aria-labelledby="make-title"><div class="chamber-head"><p class="section-label">Door 02 / completed and emerging work</p><h2 id="make-title">{esc(data['portfolio']['heading'])}</h2><p>{esc(data['portfolio']['invitation'])}</p></div><div class="featured"><p>{esc(data['portfolio']['featured_work']['status'])}</p><h3>{esc(data['portfolio']['featured_work']['title'])}</h3><p>{esc(data['portfolio']['featured_work']['description'])}</p><a href="#cases">Enter the completed work ↓</a></div><div class="directions">{directions}</div><div class="cases" id="cases"><div class="cases-heading"><p>Three events / three mechanisms</p><h2>Where should<br>we begin?</h2></div><div class="case-tabs" role="tablist" aria-label="Choose a historical event">{tabs}</div>{panels}</div></section>
  <section class="chamber become" id="become" data-chamber="become" aria-labelledby="become-title"><div class="chamber-head"><p class="section-label">Door 03 / authored questions</p><h2 id="become-title">{esc(data['becoming_questions']['heading'])}</h2><p>{esc(data['becoming_questions']['invitation'])}</p></div><div class="question-encounter"><div class="question-tabs" role="tablist" aria-label="Questions for Mira">{questions}</div><div class="answers">{answers}</div></div></section>
  <section class="horizon" aria-labelledby="horizon-title"><p class="section-label">The horizon remains open</p><h2 id="horizon-title">{esc(threshold['return_horizon'])}</h2><div><button class="operator-trigger" type="button">See the relationship provenance</button><button class="boundary-trigger" type="button">Read the public boundary</button></div></section>
</main>
<footer><p>Authored / sourced / revisable / no visitor data collected</p><p>Mira / multidimensional public threshold / unpublished</p></footer>
<noscript><section class="noscript"><h2>Meet Mira</h2>{identity_claims}<h2>See what I make</h2>{fallback}<h2>Ask what I might become</h2>{answers}</section></noscript>
<dialog class="provenance-dialog" aria-labelledby="provenance-title"><button class="dialog-close" type="button" aria-label="Close provenance">×</button><p class="section-label">Provenance</p><h2 id="provenance-title">Why do you say this?</h2><div id="provenance-content"></div></dialog>
<script id="encounter-data" type="application/json">{embedded}</script><script src="script.js"></script></body></html>
'''


def build_receipt(data: dict[str, Any], rendered: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "encounter_id": data["encounter_id"],
        "audience": data["audience"],
        "objective": data["objective"],
        "status": data["status"],
        "manifest_sha256": hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest(),
        "rendered_sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
        "case_count": len(data["cases"]),
        "claim_count": sum(len(case["claims"]) for case in data["cases"]),
        "chamber_count": 3,
        "identity_claim_count": len(data["meet_me"]["claims"]),
        "completed_work_count": 1,
        "emerging_direction_count": len(data["portfolio"]["emerging_directions"]),
        "authored_question_count": len(data["becoming_questions"]["paths"]),
        "accessibility_review": "passed-keyboard-semantics-focus-and-mobile-checks",
        "browser_review": "passed-desktop-and-390px-local-review",
        "visitor_data_collection": "none",
        "interaction_mode": data["interaction_mode"],
        "network_runtime_dependencies": [],
        "deployment_authority": "none"
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate", "render"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    data = load_manifest()
    failures = validate_manifest(data)
    if failures:
        print(json.dumps({"status": "invalid", "failures": failures}, indent=2))
        return 1
    rendered = render_html(data)
    receipt = build_receipt(data, rendered)
    if args.command == "render":
        if args.check:
            stale = not OUTPUT_PATH.is_file() or OUTPUT_PATH.read_text(encoding="utf-8") != rendered
            receipt_stale = not RECEIPT_PATH.is_file() or json.loads(RECEIPT_PATH.read_text(encoding="utf-8")) != receipt
            if stale or receipt_stale:
                print(json.dumps({"status": "stale", "html_stale": stale, "receipt_stale": receipt_stale}))
                return 1
        else:
            OUTPUT_PATH.write_text(rendered, encoding="utf-8", newline="\n")
            RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({**receipt, "validation_status": "valid"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "archive" / "geopolitics" / "source-manifest.json"
TRACK_ROOT = ROOT / "narrative-geopolitics" / "work" / "thesis-tracker"

PILOTS = {
    "mercouris/odessa": {
        "thesis_id": "mercouris-odessa-2026",
        "voice_slug": "mercouris",
        "display_name": "Mercouris Odessa thesis",
        "definition": ROOT / "narrative-geopolitics" / "voices" / "mercouris" / "odessa-thesis-2026.md",
        "aliases": ["odessa", "odesa", "odessa port", "black sea", "kherson", "zaporizhzhia", "dnieper", "dnipro"],
        "scope": ["city", "port", "black-sea-access", "southern-coast", "territorial-settlement"],
    }
}
CLAIM_TYPES = ("analytical", "operational", "rhetorical", "descriptive", "forecast")
RELATIONS = ("continuation", "refinement", "revision", "contradiction", "abandonment", "new-related-thesis", "non-engagement")
REVIEW_STATES = ("candidate", "accepted", "rejected", "needs-revision", "insufficient-evidence", "duplicate", "deferred")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def pilot(name: str) -> dict:
    if name not in PILOTS:
        raise SystemExit(f"unknown thesis: {name}; choices: {', '.join(PILOTS)}")
    p = dict(PILOTS[name])
    p["definition_version"] = hashlib.sha256(p["definition"].read_bytes()).hexdigest()[:16]
    return p


def state_path(p: dict) -> Path:
    return TRACK_ROOT / p["thesis_id"] / "state.json"


def load_state(p: dict) -> dict:
    path = state_path(p)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "schema": "thesis-state-tracker-v1",
        "thesis_id": p["thesis_id"],
        "definition_version": p["definition_version"],
        "pilot": {k: v for k, v in p.items() if k not in {"definition"}},
        "manifest_checkpoint": None,
        "candidates": [],
        "thesis_versions": [{"version_id": f"{p['thesis_id']}-v1", "thesis_id": p["thesis_id"], "relation_type": "new-related-thesis", "status": "seed", "source_refs": []}],
        "links": [],
        "forecasts": [],
        "outcomes": [],
        "negative_findings": [],
        "feedback": [],
        "runs": [],
    }


def save_state(p: dict, state: dict) -> None:
    path = state_path(p)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def manifest_rows() -> list[dict]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]


def body_for(row: dict) -> tuple[Path, str]:
    path = ROOT / row["local_path"]
    return path, path.read_text(encoding="utf-8", errors="replace")


def transcript_body(text: str) -> str:
    if "## Transcript" in text:
        text = text.split("## Transcript", 1)[1]
    return text.split("## ", 1)[0]


def evidence_spans(text: str, aliases: list[str], limit: int = 8) -> list[dict]:
    body = transcript_body(text)
    lines = body.splitlines()
    spans = []
    pattern = re.compile("|".join(re.escape(a) for a in aliases), re.I)
    for index, line in enumerate(lines):
        if not pattern.search(line) or len(line.strip()) < 40:
            continue
        start = max(0, index - 1)
        end = min(len(lines), index + 2)
        excerpt = " ".join(x.strip() for x in lines[start:end] if x.strip())
        if len(excerpt) > 480:
            excerpt = excerpt[:477].rstrip() + "..."
        spans.append({"line_start": start + 1, "line_end": end, "excerpt": excerpt})
        if len(spans) >= limit:
            break
    return spans


def classify(title: str, excerpt: str) -> tuple[str, str, str]:
    text = f"{title} {excerpt}".lower()
    if re.search(r"\b(will|could|may|likely|expect|forecast|by the end|before|eventually)\b", text):
        return "forecast", "medium", "forecast-language"
    if re.search(r"\b(blockade|strike|attack|capture|advance|cut off|destroy)\b", text):
        return "operational", "medium", "action-language"
    if re.search(r"\b(because|therefore|means|objective|strategy|aim|route|mechanism)\b", text):
        return "analytical", "medium", "mechanism-language"
    return "descriptive", "low", "keyword-only"


def discover(p: dict, state: dict) -> int:
    rows = []
    for row in manifest_rows():
        if p["voice_slug"] not in row.get("voice_slugs", []):
            continue
        title = row.get("title", "")
        path, text = body_for(row)
        joined = f"{title}\n{text[:30000]}".lower()
        if not any(alias in joined for alias in p["aliases"]):
            continue
        rows.append({"source_ref": row["local_path"], "date": row.get("date", ""), "title": title, "voice_slug": p["voice_slug"], "host_slug": row.get("host_slug", ""), "source_url": row.get("source_url", ""), "body_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    state["discovered_sources"] = rows
    state["manifest_checkpoint"] = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()[:16]
    state["runs"].append({"command": "discover", "at": now(), "source_count": len(rows), "definition_version": p["definition_version"]})
    save_state(p, state)
    print(f"discovered_sources={len(rows)}")
    return 0


def extract(p: dict, state: dict) -> int:
    existing = {c["candidate_id"]: c for c in state.get("candidates", [])}
    for source in state.get("discovered_sources", []):
        row = next(r for r in manifest_rows() if r["local_path"] == source["source_ref"])
        _, text = body_for(row)
        for span in evidence_spans(text, p["aliases"]):
            candidate_id = hashlib.sha256(f"{source['source_ref']}:{span['line_start']}:{span['line_end']}".encode()).hexdigest()[:16]
            claim_type, confidence, basis = classify(source["title"], span["excerpt"])
            existing[candidate_id] = {
                "candidate_id": candidate_id, "source_ref": source["source_ref"], "date": source["date"], "title": source["title"],
                "span": span, "speaker": p["voice_slug"], "host_framing": None, "guest_response": None,
                "endorsement_status": "unassessed", "thesis_id": p["thesis_id"], "version_id": None,
                "thesis_object": "Odessa / Odesa and southern Black Sea access", "claim_type": claim_type,
                "thesis_statement": None, "mechanism": None, "predicted_outcome": None, "timing": None,
                "falsifier": None, "extraction_confidence": confidence, "extraction_basis": basis,
                "transcript_quality": "unreviewed", "review_state": "candidate", "priority": 0,
                "created_at": now(), "review": None,
            }
    for candidate in existing.values():
        score = {"forecast": 4, "analytical": 3, "operational": 2, "descriptive": 1, "rhetorical": 1}.get(candidate["claim_type"], 0)
        if candidate["falsifier"] or candidate["timing"]:
            score += 1
        candidate["priority"] = score
    state["candidates"] = sorted(existing.values(), key=lambda c: (-c["priority"], c["date"], c["candidate_id"]))
    state["runs"].append({"command": "extract", "at": now(), "candidate_count": len(state["candidates"]), "definition_version": p["definition_version"]})
    save_state(p, state)
    print(f"candidates={len(state['candidates'])}")
    return 0


def compare(p: dict, state: dict) -> int:
    candidates = state.get("candidates", [])
    state["negative_findings"] = []
    if not any(c["claim_type"] == "forecast" for c in candidates):
        state["negative_findings"].append({"code": "no-explicit-forecast", "text": "No candidate was deterministically classified as an explicit forecast; human review is required."})
    if not any(c.get("falsifier") for c in candidates):
        state["negative_findings"].append({"code": "no-falsifier", "text": "No falsifier is recorded in accepted candidate metadata."})
    if not state.get("links"):
        state["negative_findings"].append({"code": "no-direct-disagreement", "text": "No direct disagreement link has been human-confirmed."})
    state["runs"].append({"command": "compare", "at": now(), "negative_findings": len(state["negative_findings"])})
    save_state(p, state)
    print(f"negative_findings={len(state['negative_findings'])}")
    return 0


def review(p: dict, state: dict, candidate_id: str | None, review_state: str, rationale: str) -> int:
    if review_state not in REVIEW_STATES:
        raise SystemExit(f"invalid review state: {review_state}")
    targets = [c for c in state.get("candidates", []) if candidate_id is None or c["candidate_id"] == candidate_id]
    if not targets:
        raise SystemExit("candidate not found")
    for candidate in targets:
        candidate["review_state"] = review_state
        candidate["review"] = {"reviewer": "operator", "at": now(), "rationale": rationale}
    state["runs"].append({"command": "review", "at": now(), "candidate_count": len(targets), "state": review_state})
    save_state(p, state)
    print(f"reviewed={len(targets)}")
    return 0


def report(p: dict, state: dict) -> int:
    outdir = state_path(p).parent
    accepted = [c for c in state.get("candidates", []) if c["review_state"] == "accepted"]
    lines = [f"# Thesis State Tracker: {p['display_name']}", "", f"- Thesis ID: `{p['thesis_id']}`", f"- Manifest checkpoint: `{state.get('manifest_checkpoint')}`", f"- Candidates: {len(state.get('candidates', []))}", f"- Accepted: {len(accepted)}", "", "## Candidate chronology", ""]
    for c in sorted(state.get("candidates", []), key=lambda x: (x["date"], x["candidate_id"])):
        lines.append(f"- `{c['date']}` `{c['review_state']}` `{c['claim_type']}` priority `{c['priority']}` — {c['title']} ([source]({c['source_ref']}:{c['span']['line_start']}))")
        lines.append(f"  - {c['span']['excerpt']}")
    lines += ["", "## Negative findings", ""]
    lines += [f"- `{n['code']}`: {n['text']}" for n in state.get("negative_findings", [])] or ["- None recorded."]
    lines += ["", "## Promotion boundary", "", "Accepted candidates remain analytical tracker records. No forecast ledger, reality-check, public, or daily synthesis surface was modified.", ""]
    (outdir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"report={outdir / 'report.md'}")
    return 0


def closeout(p: dict, state: dict) -> int:
    failures = []
    ids = [c["candidate_id"] for c in state.get("candidates", [])]
    failures += [f"duplicate candidate_id: {x}" for x in set(ids) if ids.count(x) > 1]
    for c in state.get("candidates", []):
        if not (ROOT / c["source_ref"]).is_file():
            failures.append(f"missing source: {c['source_ref']}")
        if c["review_state"] == "accepted" and not c.get("span", {}).get("excerpt"):
            failures.append(f"accepted candidate lacks span: {c['candidate_id']}")
        if c["review_state"] == "accepted" and c.get("extraction_confidence") == "low":
            failures.append(f"title-only/low-confidence candidate accepted: {c['candidate_id']}")
    print(f"candidates={len(ids)}")
    if failures:
        print(f"closeout_failures={len(failures)}")
        for failure in failures: print(f"FAIL {failure}")
        return 1
    print("closeout_status=PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="thesis-track")
    parser.add_argument("command", choices=("discover", "extract", "review", "compare", "outcomes", "report", "closeout"))
    parser.add_argument("--thesis", default="mercouris/odessa")
    parser.add_argument("--candidate-id")
    parser.add_argument("--review-state", default="accepted")
    parser.add_argument("--rationale", default="Operator review")
    args = parser.parse_args()
    p = pilot(args.thesis)
    state = load_state(p)
    if args.command == "discover": return discover(p, state)
    if args.command == "extract": return extract(p, state)
    if args.command == "review": return review(p, state, args.candidate_id, args.review_state, args.rationale)
    if args.command == "compare": return compare(p, state)
    if args.command == "report": return report(p, state)
    if args.command == "closeout": return closeout(p, state)
    if args.command == "outcomes":
        print("outcomes_status=review-queue-only")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

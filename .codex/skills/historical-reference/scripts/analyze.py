"""Bounded incremental historical-reference evidence-layer analyzer."""
from __future__ import annotations

import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
MANIFEST = REPO / "narrative-geopolitics" / "archive" / "source-manifest.json"
CALIBRATION = Path(__file__).resolve().parents[1] / "references" / "calibration.json"
VERSIONS = {"taxonomy": "1", "detector": "1", "mechanism": "1"}

PATTERNS = {
    "bay-of-pigs": ("Bay of Pigs", r"bay of pigs"),
    "cold-war": ("Cold War", r"\bcold war\b(?!\s+kitchen)|\bcold wore\b"),
    "iraq-war": ("2003 Iraq War", r"2003.{0,30}iraq|iraq war|saddam hussein"),
    "vietnam-war": ("Vietnam War", r"viet\s*nam war|war in viet\s*nam|guerre du vietnam|guerra de vietnam"),
    "jcpoa": ("JCPOA / Iran nuclear diplomacy", r"j\.?\s*c\.?\s*p\.?\s*o\.?\s*a|nuclear deal"),
    "cuba-embargo": ("US embargo on Cuba", r"embargo on cuba"),
    "nixon-kissinger": ("Nixon–Kissinger China strategy", r"nixon|kissinger"),
    "iranian-revolution": ("Iranian Revolution", r"iranian revolution|islamic revolution"),
    "kuwait-liberation": ("1991 liberation of Kuwait", r"liberat(?:ed|ion) kuwait|gulf war"),
    "october-7": ("7 October Hamas attack", r"october 7(?:th)?|hamas breakout"),
    "renaissance-knowledge": ("Renaissance transmission of Greek and Roman knowledge", r"renaissance.{0,80}(?:greek|roman|knowledge)|greek and roman (?:knowledge|texts)"),
    "thucydides-trap": ("Thucydides Trap", r"thucydides"),
}

MECHANISMS = {
    "coercion": ("M-FR-001", "coercion and strategic backfire"),
    "diplomacy": ("M-FR-002", "institutional memory and diplomatic credibility"),
    "power": ("M-FR-003", "imperial overstretch and power transition"),
    "competence": ("M-FR-004", "knowledge transfer and institutional competence"),
    "legitimacy": ("M-FR-005", "sovereignty, legitimacy, and historical memory"),
}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_rows(voices: set[str], sources: set[str] | None) -> list[dict]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    seen = set(); rows = []
    for row in data.get("sources", []):
        path = str(row.get("local_path") or "")
        row_voices = {str(v).lower() for v in (row.get("voice_slugs") or [])}
        if voices and not row_voices.intersection(voices): continue
        if sources and not ({str(row.get("source_id") or ""), path} & sources): continue
        if path in seen: continue
        seen.add(path); full = REPO / path
        if full.is_file(): rows.append({**row, "full_path": full})
    return sorted(rows, key=lambda x: (str(x.get("date") or ""), str(x.get("local_path") or "")))

def analyze_row(row: dict, selected_voices: set[str] | None = None) -> list[dict]:
    text = row["full_path"].read_text(encoding="utf-8", errors="replace")
    body = text.split("---", 2)[-1]
    out = []; source_id = str(row.get("source_id") or row.get("id") or row["local_path"])
    for paragraph, block in enumerate((p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()), 1):
        if re.search(r"\*\*Host:\*\*|^Welcome back\.|we are joined today", block, re.I):
            continue
        for ref_id, (label, pattern) in PATTERNS.items():
            if not re.search(pattern, block, re.I | re.S): continue
            available_voices = {str(v).lower() for v in (row.get("voice_slugs") or [])}
            voice = sorted(available_voices if selected_voices is None else available_voices.intersection(selected_voices))
            occurrence_id = f"{source_id}:{ref_id}:{paragraph}"
            mechanism = "coercion" if ref_id in {"iraq-war", "vietnam-war", "cuba-embargo"} else "diplomacy" if ref_id in {"jcpoa", "nixon-kissinger", "kuwait-liberation"} else "legitimacy" if ref_id in {"iranian-revolution", "october-7"} else "power"
            mid, mname = MECHANISMS[mechanism]
            confidence = "direct" if re.search(r"(?:\*\*)?(?:Chas|Charles) Freeman(?:\*\*)?:", block, re.I) else "provisional"
            out.append({"occurrence_id": occurrence_id, "voices": voice, "source_id": source_id, "archive_path": row["local_path"], "date": row.get("date", ""), "title": row.get("title", ""), "quote": re.sub(r"\s+", " ", block)[:700], "reference_id": ref_id, "reference": label, "parent_period": "historical period", "attribution_confidence": confidence, "mechanism_suggestions": [{"id": mid, "name": mname, "basis": "native reference adapter"}], "crosswalk_suggestions": [{"target": mid, "confidence": "suggested", "rationale": "native reference adapter"}], "risk_score": (3 if confidence == "provisional" else 1), "review_status": "needs-review" if confidence == "provisional" else "unreviewed"})
    return out

def calibration_report() -> dict:
    cases = json.loads(CALIBRATION.read_text(encoding="utf-8"))["cases"]
    results = []
    reference_tp = reference_fp = reference_fn = attribution_ok = mechanism_ok = crosswalk_ok = 0
    for case in cases:
        detected = None if re.search(r"\*\*Host:\*\*|^Welcome back\.|we are joined today", case["text"], re.I) else next((ref_id for ref_id, (_, pattern) in PATTERNS.items() if re.search(pattern, case["text"], re.I | re.S)), None)
        expected = case["expected_reference"]
        if detected == expected and expected is not None: reference_tp += 1
        elif detected is not None and expected is None: reference_fp += 1
        elif detected != expected and expected is not None: reference_fn += 1
        predicted_attr = "direct" if re.search(r"(?:\*\*)?(?:Chas|Charles) Freeman(?:\*\*)?:", case["text"], re.I) else "excluded-context" if re.search(r"\*\*Host:\*\*|Welcome back", case["text"], re.I) else "provisional"
        attribution_ok += int(predicted_attr == case["expected_attribution"])
        predicted_mechanism = "coercion" if detected in {"iraq-war", "vietnam-war", "cuba-embargo", "bay-of-pigs"} else "diplomacy" if detected in {"jcpoa", "nixon-kissinger", "kuwait-liberation"} else "legitimacy" if detected in {"iranian-revolution", "october-7"} else "power" if detected in {"cold-war", "thucydides-trap"} else "competence" if detected == "renaissance-knowledge" else None
        mechanism_ok += int(predicted_mechanism == case["expected_mechanism"])
        crosswalk_ok += int(("M-FR-001" if predicted_mechanism == "coercion" else "M-FR-002" if predicted_mechanism == "diplomacy" else "M-FR-003" if predicted_mechanism == "power" else "M-FR-004" if predicted_mechanism == "competence" else "M-FR-005" if predicted_mechanism == "legitimacy" else None) == case["expected_crosswalk"])
        results.append({"id": case["id"], "expected_reference": expected, "detected_reference": detected, "reference_match": detected == expected, "attribution_match": predicted_attr == case["expected_attribution"], "mechanism_match": predicted_mechanism == case["expected_mechanism"]})
    precision = reference_tp / (reference_tp + reference_fp) if reference_tp + reference_fp else 1.0
    recall = reference_tp / (reference_tp + reference_fn) if reference_tp + reference_fn else 1.0
    return {"fixture_version": json.loads(CALIBRATION.read_text(encoding="utf-8"))["version"], "cases": len(cases), "reference_precision": precision, "reference_recall": recall, "attribution_accuracy": attribution_ok / len(cases), "mechanism_accuracy": mechanism_ok / len(cases), "crosswalk_accuracy": crosswalk_ok / len(cases), "results": results}

def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--voices", required=True); p.add_argument("--sources"); p.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")); p.add_argument("--resume", action="store_true"); p.add_argument("--changed-only", action="store_true"); p.add_argument("--dry-run", action="store_true"); p.add_argument("--output-dir", type=Path, default=REPO / "narrative-geopolitics" / "work" / "historical-reference"); p.add_argument("--calibration", action="store_true"); args = p.parse_args()
    voices = {v.strip().lower() for v in args.voices.split(",") if v.strip()}; sources = {v.strip() for v in args.sources.split(",")} if args.sources else None
    records = [record for row in source_rows(voices, sources) for record in analyze_row(row, voices)]
    receipt = {"run_id": args.run_id, "voices": sorted(voices), "records": len(records), "versions": VERSIONS, "changed_only": args.changed_only, "resumable": True, "records_data": records}
    if args.dry_run: print(json.dumps(receipt, ensure_ascii=False, indent=2)); return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    batch_path = args.output_dir / f"{args.run_id}.json"
    batch_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    queue = sorted(records, key=lambda item: (-item["risk_score"], item["source_id"], item["reference_id"], item["occurrence_id"]))
    (args.output_dir / f"{args.run_id}-review-queue.json").write_text(json.dumps({"run_id": args.run_id, "items": queue}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    nodes = {}; edges = []
    for item in records:
        for node_id, kind in [(f"voice:{v}", "voice") for v in item["voices"]] + [(f"source:{item['source_id']}", "source"), (f"reference:{item['reference_id']}", "reference")]:
            nodes[node_id] = {"id": node_id, "type": kind}
        for voice in item["voices"]:
            edges.append({"from": f"voice:{voice}", "to": f"source:{item['source_id']}", "type": "speaks-in"})
        edges.append({"from": f"source:{item['source_id']}", "to": f"reference:{item['reference_id']}", "type": "contains"})
    (args.output_dir / f"{args.run_id}-graph.json").write_text(json.dumps({"nodes": sorted(nodes.values(), key=lambda x: x["id"]), "edges": sorted(edges, key=lambda x: (x["from"], x["to"], x["type"]))}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "checkpoint.json").write_text(json.dumps({"run_id": args.run_id, "completed_sources": sorted({item["source_id"] for item in records}), "versions": VERSIONS}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.calibration:
        (args.output_dir / f"{args.run_id}-calibration-report.json").write_text(json.dumps(calibration_report(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {batch_path}"); return 0

if __name__ == "__main__": raise SystemExit(main())

"""Bounded incremental historical-reference evidence-layer analyzer."""
from __future__ import annotations

import argparse, hashlib, json, re, shutil, tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
MANIFEST = REPO / "narrative-geopolitics" / "archive" / "source-manifest.json"
CALIBRATION = Path(__file__).resolve().parents[1] / "references" / "calibration.json"
VERSIONS = {"taxonomy": "2", "detector": "3", "mechanism": "1"}

RUN_STATES = {"planned", "processing", "landed", "skipped", "failed", "invalid"}

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
    "sino-indian-war-1962": ("Sino-Indian War of 1962", r"(?:sino|sanino)[\s-]+indian war(?: of)? 1962|(?:sino|sanino)[\s-]+indian war"),
    "sino-vietnamese-war-1979": ("Sino-Vietnamese War of 1979", r"sino[\s-]+vietnamese war(?: of)? 1979|sino[\s-]+vietnamese war"),
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

def fingerprint(row: dict, voices: set[str]) -> dict[str, str]:
    return {
        "source_id": str(row.get("source_id") or row.get("id") or row["local_path"]),
        "archive_path": str(row["local_path"]),
        "file_hash": sha256(row["full_path"]),
        "taxonomy_version": VERSIONS["taxonomy"],
        "detector_version": VERSIONS["detector"],
        "mechanism_version": VERSIONS["mechanism"],
        "voice_scope": ",".join(sorted(voices)),
    }

def load_checkpoint(path: Path) -> dict:
    if not path.exists():
        return {"sources": {}}
    return json.loads(path.read_text(encoding="utf-8"))

def review_packet(item: dict) -> dict:
    """Return a compact, stable-identity packet for operator review."""
    return {
        "review_id": f"review:{item['occurrence_id']}",
        "identity": {
            "occurrence_id": item["occurrence_id"],
            "source_id": item["source_id"],
            "reference_id": item["reference_id"],
        },
        "priority_score": item["risk_score"],
        "source": {"date": item["date"], "title": item["title"], "archive_path": item["archive_path"]},
        "evidence": {"quote": item["quote"], "basis": item.get("evidence_basis", "")},
        "reference": {"id": item["reference_id"], "label": item["reference"], "parent_period": item["parent_period"]},
        "attribution_confidence": item["attribution_confidence"],
        "mechanism_suggestions": item.get("mechanism_suggestions", []),
        "crosswalk_suggestions": item.get("crosswalk_suggestions", []),
        "decision_options": ["accept", "qualify", "reject", "revise", "unresolved"],
        "current_status": item["review_status"],
    }

def load_overrides(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("overrides", data)

def apply_overrides(records: list[dict], overrides: dict[str, dict]) -> list[dict]:
    for item in records:
        override = overrides.get(item["occurrence_id"])
        if not override:
            continue
        if "review_status" in override:
            item["review_status"] = override["review_status"]
        item["review_note"] = override.get("review_note", "")
        item["reviewed_by"] = override.get("reviewed_by", "")
        item["reviewed_at"] = override.get("reviewed_at", "")
    return records

def review_packets_markdown(packets: list[dict], run_id: str) -> str:
    lines = [f"# Historical-reference review packets — `{run_id}`", "", "Operator review artifact. Candidates are source-derived and may remain provisional.", ""]
    if not packets:
        return "\n".join(lines + ["No unresolved review packets.", ""])
    for packet in packets:
        source = packet["source"]
        reference = packet["reference"]
        evidence = packet["evidence"]
        lines.extend([
            f"## `{packet['review_id']}` — {reference['label']}",
            "",
            f"Priority: `{packet['priority_score']}`  ",
            f"Occurrence: `{packet['identity']['occurrence_id']}`  ",
            f"Source: `{packet['identity']['source_id']}` — `{source['archive_path']}`  ",
            f"Date: `{source['date']}`  ",
            f"Attribution: `{packet['attribution_confidence']}`  ",
            f"Current status: `{packet['current_status']}`",
            "",
            "### Evidence",
            "",
            f"> {evidence['quote']}",
            "",
            f"Basis: {evidence['basis']}",
            "",
            "### Suggested interpretation",
            "",
            f"- Parent period: `{reference['parent_period']}`",
        ])
        for suggestion in packet.get("mechanism_suggestions", []):
            lines.append(f"- Mechanism suggestion: `{suggestion['id']}` — {suggestion['name']} ({suggestion.get('status', 'provisional')})")
        for crosswalk in packet.get("crosswalk_suggestions", []):
            lines.append(f"- Crosswalk suggestion: `{crosswalk['target']}`; confidence `{crosswalk['confidence']}`; conflict `{crosswalk['conflict_status']}`")
        lines.extend(["", "### Decision", "", "Choose one: " + ", ".join(f"`{option}`" for option in packet["decision_options"]), "", "---", ""])
    return "\n".join(lines)

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
            mechanism = "coercion" if ref_id in {"iraq-war", "vietnam-war", "cuba-embargo"} else "diplomacy" if ref_id in {"jcpoa", "nixon-kissinger", "kuwait-liberation", "sino-indian-war-1962", "sino-vietnamese-war-1979"} else "legitimacy" if ref_id in {"iranian-revolution", "october-7"} else "power"
            mid, mname = MECHANISMS[mechanism]
            confidence = "direct" if re.search(r"(?:\*\*)?(?:Chas|Charles) Freeman(?:\*\*)?:", block, re.I) else "provisional"
            parent_period = "Cold War" if ref_id in {"cold-war", "vietnam-war", "sino-indian-war-1962", "sino-vietnamese-war-1979"} else "historical period"
            out.append({"occurrence_id": occurrence_id, "voices": voice, "source_id": source_id, "archive_path": row["local_path"], "date": row.get("date", ""), "title": row.get("title", ""), "quote": re.sub(r"\s+", " ", block)[:700], "reference_id": ref_id, "reference": label, "parent_period": parent_period, "attribution_confidence": confidence, "mechanism_suggestions": [{"id": mid, "name": mname, "basis": "native reference adapter"}], "crosswalk_suggestions": [{"target": mid, "confidence": "suggested", "rationale": "native reference adapter", "conflict_status": "unreviewed", "review_status": "unreviewed"}], "risk_score": (3 if confidence == "provisional" else 1), "review_status": "needs-review" if confidence == "provisional" else "unreviewed"})
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
        predicted_mechanism = "coercion" if detected in {"iraq-war", "vietnam-war", "cuba-embargo", "bay-of-pigs"} else "diplomacy" if detected in {"jcpoa", "nixon-kissinger", "kuwait-liberation", "sino-indian-war-1962", "sino-vietnamese-war-1979"} else "legitimacy" if detected in {"iranian-revolution", "october-7"} else "power" if detected in {"cold-war", "thucydides-trap"} else "competence" if detected == "renaissance-knowledge" else None
        mechanism_ok += int(predicted_mechanism == case["expected_mechanism"])
        crosswalk_ok += int(("M-FR-001" if predicted_mechanism == "coercion" else "M-FR-002" if predicted_mechanism == "diplomacy" else "M-FR-003" if predicted_mechanism == "power" else "M-FR-004" if predicted_mechanism == "competence" else "M-FR-005" if predicted_mechanism == "legitimacy" else None) == case["expected_crosswalk"])
        results.append({"id": case["id"], "expected_reference": expected, "detected_reference": detected, "reference_match": detected == expected, "attribution_match": predicted_attr == case["expected_attribution"], "mechanism_match": predicted_mechanism == case["expected_mechanism"]})
    precision = reference_tp / (reference_tp + reference_fp) if reference_tp + reference_fp else 1.0
    recall = reference_tp / (reference_tp + reference_fn) if reference_tp + reference_fn else 1.0
    return {"fixture_version": json.loads(CALIBRATION.read_text(encoding="utf-8"))["version"], "cases": len(cases), "reference_precision": precision, "reference_recall": recall, "attribution_accuracy": attribution_ok / len(cases), "mechanism_accuracy": mechanism_ok / len(cases), "crosswalk_accuracy": crosswalk_ok / len(cases), "results": results}

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--voices", required=True)
    p.add_argument("--sources")
    p.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ"))
    p.add_argument("--resume", action="store_true")
    p.add_argument("--changed-only", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--output-dir", type=Path, default=REPO / "narrative-geopolitics" / "work" / "historical-reference")
    p.add_argument("--calibration", action="store_true")
    p.add_argument("--overrides", type=Path)
    args = p.parse_args()
    voices = {v.strip().lower() for v in args.voices.split(",") if v.strip()}
    if not voices:
        p.error("--voices must contain at least one voice")
    sources = {v.strip() for v in args.sources.split(",")} if args.sources else None
    rows = source_rows(voices, sources)
    if not rows:
        p.error("no bounded manifest-backed sources selected")
    if args.dry_run:
        print(json.dumps({"run_id": args.run_id, "state": "planned", "voices": sorted(voices), "sources": [{"source_id": r.get("source_id"), "fingerprint": fingerprint(r, voices)} for r in rows]}, ensure_ascii=False, indent=2))
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = args.output_dir / f"{args.run_id}-checkpoint.json"
    previous = load_checkpoint(checkpoint_path) if args.resume or args.changed_only else {"sources": {}}
    receipts, records = [], []
    for row in rows:
        source_id = str(row.get("source_id") or row.get("id") or row["local_path"])
        fp = fingerprint(row, voices)
        old = previous.get("sources", {}).get(source_id, {})
        if (args.resume or args.changed_only) and old.get("fingerprint") == fp and old.get("status") == "landed":
            receipts.append({"source_id": source_id, "status": "skipped", "fingerprint": fp, "record_count": old.get("record_count", 0)})
            continue
        try:
            source_records = analyze_row(row, voices)
            records.extend(source_records)
            receipts.append({"source_id": source_id, "status": "landed", "fingerprint": fp, "record_count": len(source_records), "archive_path": row["local_path"], "warnings": ["provisional attribution"] if any(r["attribution_confidence"] == "provisional" for r in source_records) else []})
        except Exception as exc:
            receipts.append({"source_id": source_id, "status": "failed", "fingerprint": fp, "record_count": 0, "error": str(exc)})

    records = apply_overrides(records, load_overrides(args.overrides) if args.overrides else {})
    payload = {"run_id": args.run_id, "state": "failed" if any(r["status"] == "failed" for r in receipts) else "landed", "voices": sorted(voices), "versions": VERSIONS, "receipts": sorted(receipts, key=lambda r: r["source_id"]), "records": sorted(records, key=lambda r: (r["date"], r["title"], r["source_id"], r["occurrence_id"]))}
    if payload["state"] == "failed":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    stage = Path(tempfile.mkdtemp(prefix=f".{args.run_id}-", dir=args.output_dir))
    try:
        (stage / f"{args.run_id}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        queue = sorted(records, key=lambda item: (-item["risk_score"], item["source_id"], item["reference_id"], item["occurrence_id"]))
        (stage / f"{args.run_id}-review-queue.json").write_text(json.dumps({"run_id": args.run_id, "items": queue}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        packets = [review_packet(item) for item in queue if item["review_status"] not in {"accepted", "rejected"}]
        (stage / f"{args.run_id}-review-packets.json").write_text(json.dumps({"run_id": args.run_id, "packet_count": len(packets), "packets": packets}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (stage / f"{args.run_id}-review-packets.md").write_text(review_packets_markdown(packets, args.run_id), encoding="utf-8")
        (stage / f"{args.run_id}-checkpoint.json").write_text(json.dumps({"run_id": args.run_id, "versions": VERSIONS, "sources": {r["source_id"]: {"fingerprint": r["fingerprint"], "status": r["status"], "record_count": r["record_count"]} for r in receipts}}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.calibration:
            (stage / f"{args.run_id}-calibration-report.json").write_text(json.dumps(calibration_report(), indent=2) + "\n", encoding="utf-8")
        for path in stage.iterdir():
            shutil.move(str(path), str(args.output_dir / path.name))
        print(f"Published {args.output_dir / (args.run_id + '.json')}")
        return 0
    finally:
        shutil.rmtree(stage, ignore_errors=True)

if __name__ == "__main__": raise SystemExit(main())

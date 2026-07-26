"""Build a bounded, source-linked historical context packet for synthesis.

This command only writes the requested packet. It never edits synthesis prose.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def packet_id(data: dict, date: str, voices: list[str], crisis: str) -> str:
    raw = json.dumps({"run_id": data.get("run_id"), "date": date, "voices": voices, "crisis": crisis}, sort_keys=True)
    return "HCP-" + hashlib.sha256(raw.encode()).hexdigest()[:16]

def select_records(data: dict, date: str, voices: set[str], crisis: str | None, limit: int) -> list[dict]:
    rows = []
    for item in data.get("records", []):
        if str(item.get("date", "")) != date:
            continue
        if voices and not voices.intersection({str(v).lower() for v in item.get("voices", [])}):
            continue
        if crisis and crisis.lower() not in (str(item.get("title", "")) + " " + str(item.get("reference", ""))).lower():
            continue
        rows.append(item)
    return sorted(rows, key=lambda item: (-int(item.get("risk_score", 0)), item.get("source_id", ""), item.get("occurrence_id", "")))[:limit]

def build_packet(data: dict, date: str, voices: set[str], crisis: str | None, limit: int) -> dict:
    selected = sorted(voices)
    records = select_records(data, date, voices, crisis, limit)
    pid = packet_id(data, date, selected, crisis or "")
    return {
        "packet_id": pid,
        "packet_type": "historical-context",
        "status": "bounded-context-only",
        "source_run_id": data.get("run_id", ""),
        "date": date,
        "voices": selected,
        "crisis_filter": crisis,
        "record_limit": limit,
        "record_count": len(records),
        "records": [{
            "occurrence_id": item["occurrence_id"], "source_id": item["source_id"], "archive_path": item["archive_path"],
            "title": item["title"], "date": item["date"], "reference_id": item["reference_id"], "reference": item["reference"],
            "quote": item["quote"], "attribution_confidence": item["attribution_confidence"],
            "mechanism_suggestions": item.get("mechanism_suggestions", []), "crosswalk_suggestions": item.get("crosswalk_suggestions", []),
            "review_status": item.get("review_status", "unreviewed"), "risk_score": item.get("risk_score", 0),
        } for item in records],
        "guardrails": ["Historical context is source-derived and not historical verification.", "Provisional attribution remains provisional.", "This packet does not overwrite synthesis prose.", "This packet must not be treated as analytical-quality or forecast-success evidence."],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

def markdown(packet: dict) -> str:
    lines = [f"## Historical context packet `{packet['packet_id']}`", "", f"Status: `{packet['status']}`", f"Source run: `{packet['source_run_id']}`", f"Date: `{packet['date']}`", f"Records: `{packet['record_count']}`", ""]
    for item in packet["records"]:
        lines += [f"### {item['reference']} — `{item['occurrence_id']}`", f"Source: `{item['source_id']}` — `{item['archive_path']}`", f"Attribution: `{item['attribution_confidence']}`; review: `{item['review_status']}`", f"> {item['quote']}", ""]
    lines += ["### Guardrails", ""] + [f"- {guardrail}" for guardrail in packet["guardrails"]] + [""]
    return "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="bounded analyzer JSON output")
    parser.add_argument("--date", required=True)
    parser.add_argument("--voices", required=True, help="comma-separated voice bound")
    parser.add_argument("--crisis")
    parser.add_argument("--max-items", type=int, default=12)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.max_items < 1:
        parser.error("--max-items must be positive")
    data = json.loads(args.input.read_text(encoding="utf-8")); voices = {v.strip().lower() for v in args.voices.split(",") if v.strip()}
    if not voices:
        parser.error("--voices must contain at least one voice")
    packet = build_packet(data, args.date, voices, args.crisis, args.max_items)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(packet), encoding="utf-8")
    print(f"Wrote bounded historical context packet {packet['packet_id']} ({packet['record_count']} records)")
    return 0

if __name__ == "__main__": raise SystemExit(main())

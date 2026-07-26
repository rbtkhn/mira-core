from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "narrative-geopolitics" / "archive" / "source-manifest.json"
DERIVED_ROOT = REPO_ROOT / "narrative-geopolitics" / "archive" / "derived" / "speaker-labeled"
@dataclass(frozen=True)
class Candidate:
    name: str
    confidence: float


def args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Select and label transcript derivatives without changing raw sources.")
    p.add_argument("--select", action="store_true", help="Write a deterministic pilot manifest.")
    p.add_argument("--execute", action="store_true", help="Write labeled derivatives and audit data.")
    p.add_argument("--qa-packet", action="store_true", help="Write a 20-source manual QA packet from the pilot.")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--manifest", type=Path, default=MANIFEST)
    p.add_argument("--pilot-manifest", type=Path, default=DERIVED_ROOT / "pilot-manifest.json")
    p.add_argument("--output-root", type=Path, default=DERIVED_ROOT)
    return p.parse_args()


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) != 3:
        return {}, text
    fields: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    return fields, parts[2].lstrip("\r\n")


def candidates(row: dict[str, Any], fields: dict[str, str]) -> list[Candidate]:
    names: list[str] = []
    for key in ("host", "guest"):
        if fields.get(key):
            names.extend(x.strip() for x in fields[key].split(",") if x.strip())
    for value in row.get("voice_slugs") or []:
        name = str(value).replace("-", " ").title()
        if name not in names:
            names.append(name)
    return [Candidate(name, 0.65 if i == 0 else 0.55) for i, name in enumerate(names)]


def score_row(row: dict[str, Any]) -> tuple[float, str]:
    try:
        age = (date.today() - date.fromisoformat(str(row.get("date")))).days
    except ValueError:
        age = 10000
    density = 2.0 if row.get("source_class") in {"cross-host pressure test", "stream-sequence spine"} else 0.0
    return (density - age / 3650, str(row.get("local_path", "")))


def select_rows(manifest: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    rows = [r for r in manifest.get("sources", []) if r.get("modality") in {"transcript", "cleaned-transcript", None}]
    return sorted(rows, key=score_row, reverse=True)[:limit]


def label_body(body: str, row: dict[str, Any], fields: dict[str, str]) -> tuple[str, dict[str, Any]]:
    roster = candidates(row, fields)
    known = {c.name.casefold(): c for c in roster}
    output: list[str] = []
    labeled = unknown = 0
    for block in re.split(r"(\n\s*\n)", body):
        if not block.strip() or block.isspace():
            output.append(block)
            continue
        match = re.match(r"\s*(?:\*\*)?(?P<name>[A-Za-z][\w .'-]{1,80})(?:\*\*)?\s*:\s*(?P<text>.+)\s*\Z", block, re.S)
        if match:
            name = match.group("name").strip()
            match_candidate = known.get(name.casefold())
            if not match_candidate:
                aliases = [candidate for candidate in roster if name.casefold() in {candidate.name.casefold(), candidate.name.split()[0].casefold()}]
                if len(aliases) == 1:
                    match_candidate = aliases[0]
            if match_candidate:
                output.append(f"**{match_candidate.name}**: {match.group('text').strip()}")
                labeled += 1
                continue
        output.append(f"**Unknown**: {block.strip()}")
        unknown += 1
    total = labeled + unknown
    return "".join(output), {"turn_count": total, "labeled_turn_count": labeled, "unknown_turn_count": unknown, "candidate_speakers": [c.name for c in roster]}


def derivative(row: dict[str, Any], output_root: Path) -> tuple[Path, dict[str, Any]]:
    source = REPO_ROOT / str(row["local_path"])
    raw = source.read_bytes()
    text = raw.decode("utf-8-sig")
    fields, body = frontmatter(text)
    labeled, stats = label_body(body, row, fields)
    source_hash = hashlib.sha256(raw).hexdigest()
    relative = Path(str(row["local_path"])).relative_to("narrative-geopolitics/archive/sources")
    target = output_root / relative
    meta = {"source_path": row["local_path"], "source_sha256": source_hash, "labeling_method": "metadata-plus-explicit-markers-v1", "confidence_policy": "explicit-marker-only; unknown otherwise", **stats}
    header = "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v}" for k, v in {**fields, "speaker_labeling": "provisional", "speaker_labeling_provenance": json.dumps(meta, ensure_ascii=False)}.items()) + "\n---\n"
    return target, {"target": target, "text": header + labeled, "provenance": meta}


def main() -> int:
    cli = args()
    manifest = json.loads(cli.manifest.read_text(encoding="utf-8-sig"))
    rows = select_rows(manifest, cli.limit)
    pilot = {"kind": "speaker-labeling-pilot-v1", "limit": cli.limit, "source_count": len(rows), "sources": rows}
    if cli.select or cli.execute:
        cli.pilot_manifest.parent.mkdir(parents=True, exist_ok=True)
        cli.pilot_manifest.write_text(json.dumps(pilot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if cli.qa_packet:
        qa_rows = rows[:20]
        qa_path = cli.output_root / "qa-packet.md"
        qa_path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# Speaker Labeling Pilot — Manual QA Packet", "", "Complete one row per source after reviewing the raw and labeled derivative.", "", "| # | Source | Turns reviewed | Correct | Incorrect | Unknown | Host/guest confusion | Raw review min | Labeled review min | Notes |", "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|"]
        for index, row in enumerate(qa_rows, 1):
            path = str(row.get("local_path", "")).replace("|", "\\|")
            lines.append(f"| {index} | `{path}` |  |  |  |  |  |  |  |  |")
        lines.extend(["", "## Acceptance thresholds", "", "- Attribution accuracy: at least 90%.", "- No systematic host/guest confusion.", "- Clear interview unknown rate: below 10%.", "- Review-time reduction: at least 30%.", "", "## Aggregate results", "", "- Total turns reviewed: ", "- Total correct: ", "- Total incorrect: ", "- Total unknown: ", "- Accuracy: ", "- Unknown rate on clear interviews: ", "- Raw review minutes: ", "- Labeled review minutes: ", "- Review-time reduction: ", "- Reviewer: ", "- Date: "])
        qa_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({"qa_sources": len(qa_rows), "qa_packet": str(qa_path.relative_to(REPO_ROOT)).replace("\\", "/")}))
        if not cli.execute:
            return 0
    if not cli.execute:
        print(json.dumps({"selected": len(rows), "pilot_manifest": str(cli.pilot_manifest.relative_to(REPO_ROOT))}))
        return 0
    audit: list[dict[str, Any]] = []
    for row in rows:
        target, result = derivative(row, cli.output_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result["text"], encoding="utf-8", newline="\n")
        audit.append({**result["provenance"], "derived_path": str(target.relative_to(REPO_ROOT)).replace("\\", "/")})
    audit_path = cli.output_root / "audit.json"
    audit_path.write_text(json.dumps({"kind": "speaker-labeling-audit-v1", "sources": audit}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"processed": len(audit), "audit": str(audit_path.relative_to(REPO_ROOT))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

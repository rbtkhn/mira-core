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


@dataclass(frozen=True)
class ReferenceRule:
    key: str
    label: str
    period: str
    region: str
    topic: str
    function: str
    patterns: tuple[str, ...]


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


def build_occurrences() -> tuple[list[dict], list[str]]:
    occurrences: list[dict] = []
    coverage: list[str] = []
    for row_index, row in enumerate(source_rows(), start=1):
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
                })
                found += 1
        if not found:
            coverage.append(f"SCANNED {row.get('local_path', '')} (no catalogued references)")
        else:
            coverage.append(f"SCANNED {row.get('local_path', '')} ({found} occurrence(s))")
    return occurrences, coverage


def render() -> str:
    rows = source_rows()
    occurrences, coverage = build_occurrences()
    grouped: dict[str, list[dict]] = defaultdict(list)
    for occurrence in occurrences:
        grouped[occurrence["rule"].key].append(occurrence)
    rules = {rule.key: rule for rule in RULES}
    ordered_keys = sorted(grouped, key=lambda key: (rules[key].period, rules[key].label.lower()))
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
        "",
        "## Reference index",
        "",
        "| ID | Reference | Historical domain | Period | Region / civilization | Topic | Function | Freeman question | First | Latest | Occurrences | Source IDs | Attribution |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for number, key in enumerate(ordered_keys, start=1):
        rule = rules[key]
        items = grouped[key]
        dates = sorted(item["date"] for item in items)
        source_ids = sorted({item["source_id"] for item in items})
        status = "provisional" if any(item["confidence"] == "provisional" for item in items) else "supported"
        lines.append(f"| `FR-HR-{number:03d}` | {rule.label} | {historical_domain(rule)} | {rule.period} | {rule.region} | {rule.topic} | {rule.function} | {repertoire_question(rule)} | {dates[0]} | {dates[-1]} | {len(items)} | {', '.join(source_ids)} | `{status}` |")
    lines += ["", "## Occurrence ledger", ""]
    occurrence_number = 0
    for number, key in enumerate(ordered_keys, start=1):
        rule = rules[key]
        lines += [f"### FR-HR-{number:03d} — {rule.label}", ""]
        for occurrence in sorted(grouped[key], key=lambda item: (item["date"], item["source_id"], item["paragraph"])):
            occurrence_number += 1
            oid = f"FR-HR-{number:03d}-O{occurrence_number:03d}"
            lines += [
                f"#### {oid} — {occurrence['date']} — {occurrence['title']}",
                "",
                f"- Source: `{occurrence['source_id']}` · host/channel `{occurrence['host']}` · [archive source](../../archive/{occurrence['path'].split('archive/', 1)[-1]})",
                f"- Domain: `{historical_domain(rule)}` · function: `{occurrence['function']}` · Freeman question: `{repertoire_question(rule)}`",
                f"- Attribution: `{occurrence['confidence']}` ({occurrence['note']})",
                f"- Quote: “{occurrence['quote']}”",
                "",
            ]
    lines += ["## Coverage log", "", *[f"- {item}" for item in coverage], ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rendered = render()
    if args.dry_run:
        print(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"Wrote {args.output.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

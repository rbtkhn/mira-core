import argparse
import json
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
SINGULARITY_ROOT = REPO_ROOT / "archive" / "sources" / "singularity"
MOONSHOTS_TRANSCRIPTS = SINGULARITY_ROOT / "moonshots" / "transcripts"
INNERMOST_TRANSCRIPTS = SINGULARITY_ROOT / "innermost-loop" / "transcripts"
DEFAULT_JSON = SINGULARITY_ROOT / "singularity-signal-ledger.json"
DEFAULT_MARKDOWN = SINGULARITY_ROOT / "singularity-signal-ledger.md"

MECHANISM_LEXICON: dict[str, tuple[str, ...]] = {
    "compute-bottleneck": (
        "compute",
        "gpu",
        "gpus",
        "chip",
        "chips",
        "nvidia",
        "memory price",
        "memory prices",
        "hbm",
        "inference",
        "training",
    ),
    "energy-bottleneck": (
        "energy",
        "grid",
        "power",
        "nuclear",
        "data center",
        "datacenter",
        "data centers",
        "200gw",
        "battery",
        "batteries",
        "wave-powered",
    ),
    "open-source-acceleration": (
        "open source",
        "open-source",
        "open weight",
        "open-weight",
        "open weights",
        "kimi",
        "grok",
        "grok 4",
        "llama",
    ),
    "china-catch-up": (
        "china",
        "chinese",
        "xi",
        "export control",
        "exports ai",
        "global south",
        "u.s.-china",
        "us-china",
        "beijing",
    ),
    "vertical-integration": (
        "vertical integration",
        "hardware stack",
        "oem",
        "waymo",
        "alphabet",
        "model routing",
        "full stack",
    ),
    "institutional-lag": (
        "institutional lag",
        "inertia",
        "regulatory",
        "government",
        "white house",
        "policy",
        "institutions",
        "adoption",
    ),
    "agent-autonomy": (
        "agent",
        "agents",
        "bot",
        "bots",
        "grokbot",
        "grokbots",
        "swarm",
        "sandbox",
        "containment",
        "autonomous",
    ),
    "robotics-labor-substitution": (
        "robot",
        "robots",
        "robotics",
        "humanoid",
        "unitree",
        "optimus",
        "labor",
        "factory",
    ),
    "science-acceleration": (
        "science",
        "scientific",
        "math",
        "mathematics",
        "astra",
        "discovery",
        "productivity",
        "10x",
    ),
    "space-industrialization": (
        "spacex",
        "starship",
        "mars",
        "moon",
        "orbital",
        "satellite",
        "space",
        "nasa",
    ),
    "capital-market-infrastructure": (
        "wall street",
        "bond",
        "bonds",
        "financing",
        "revenue",
        "ipo",
        "bubble",
        "market",
        "markets",
        "trillion",
    ),
    "safety-governance-narrative": (
        "safety",
        "governance",
        "pause",
        "containment",
        "alignment",
        "regulation",
        "risk",
        "lab",
        "labs",
    ),
}

FORECAST_PATTERNS = (
    re.compile(r"\bby\s+(20\d{2})\b", re.IGNORECASE),
    re.compile(r"\bwithin\s+\d+\s+(?:day|days|week|weeks|month|months|year|years)\b", re.IGNORECASE),
    re.compile(r"\b\d+(?:\.\d+)?x\b", re.IGNORECASE),
    re.compile(r"\b\d+%\b"),
    re.compile(r"\$\d+(?:\.\d+)?\s*(?:b|bn|billion|t|tn|trillion)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class SourceDoc:
    path: Path
    repo_path: str
    title: str
    published: date | None
    text: str


def repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def parse_inline_list(value: str) -> list[str]:
    stripped = value.strip()
    if stripped == "[]":
        return []
    if not stripped.startswith("[") or not stripped.endswith("]"):
        return []
    raw_items = stripped[1:-1].strip()
    if not raw_items:
        return []
    items: list[str] = []
    for item in raw_items.split(","):
        cleaned = item.strip().strip('"').strip("'").strip()
        if cleaned:
            items.append(cleaned)
    return items


def parse_frontmatter_value(raw_value: str) -> Any:
    value = raw_value.strip()
    if value.startswith("[") and value.endswith("]"):
        return parse_inline_list(value)
    return value.strip('"')


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    result: dict[str, Any] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        result[key.strip()] = parse_frontmatter_value(raw_value)
    return result


def parse_date(value: Any, fallback_name: str) -> date | None:
    candidates = [value if isinstance(value, str) else "", fallback_name]
    for candidate in candidates:
        match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", candidate)
        if match:
            return date.fromisoformat(match.group(1))
    return None


def load_docs(root: Path) -> list[SourceDoc]:
    docs: list[SourceDoc] = []
    if not root.exists():
        return docs
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        title = frontmatter.get("title") or path.stem
        published = parse_date(frontmatter.get("date_published"), path.name)
        docs.append(
            SourceDoc(
                path=path,
                repo_path=repo_relative(path),
                title=title if isinstance(title, str) else path.stem,
                published=published,
                text=text,
            )
        )
    return docs


def mechanism_scores(text: str) -> dict[str, int]:
    haystack = text.lower()
    scores: dict[str, int] = {}
    for mechanism, terms in MECHANISM_LEXICON.items():
        score = sum(haystack.count(term) for term in terms)
        if score:
            scores[mechanism] = score
    return scores


def top_mechanisms(text: str, limit: int = 3) -> list[str]:
    scores = mechanism_scores(text)
    return [
        mechanism
        for mechanism, _score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def forecast_handles(text: str, limit: int = 6) -> list[str]:
    handles: list[str] = []
    for pattern in FORECAST_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(0).strip()
            if value.lower() not in {item.lower() for item in handles}:
                handles.append(value)
            if len(handles) >= limit:
                return handles
    return handles


def matching_innermost_refs(
    moonshot: SourceDoc,
    innermost_docs: list[SourceDoc],
    mechanisms: list[str],
    window_days: int,
    limit: int,
) -> list[dict[str, Any]]:
    if moonshot.published is None:
        return []
    mechanism_terms = {
        term
        for mechanism in mechanisms
        for term in MECHANISM_LEXICON.get(mechanism, ())
    }
    scored: list[tuple[int, SourceDoc, list[str]]] = []
    earliest = moonshot.published - timedelta(days=window_days)
    latest = moonshot.published + timedelta(days=window_days)
    for doc in innermost_docs:
        if doc.published is None or not earliest <= doc.published <= latest:
            continue
        haystack = f"{doc.title}\n{doc.text}".lower()
        hits = sorted(term for term in mechanism_terms if term in haystack)
        if not hits:
            continue
        score = len(hits) * 10 - abs((moonshot.published - doc.published).days)
        scored.append((score, doc, hits[:8]))
    return [
        {
            "path": doc.repo_path,
            "title": doc.title,
            "date": doc.published.isoformat() if doc.published else None,
            "matched_terms": hits,
            "match_status": "candidate",
        }
        for _score, doc, hits in sorted(scored, key=lambda item: (-item[0], item[1].repo_path))[:limit]
    ]


def priority_for(mechanisms: list[str], forecast_count: int, innermost_count: int) -> str:
    high_priority = {
        "agent-autonomy",
        "china-catch-up",
        "energy-bottleneck",
        "institutional-lag",
        "safety-governance-narrative",
    }
    if high_priority.intersection(mechanisms) and (forecast_count or innermost_count):
        return "high"
    if forecast_count or innermost_count:
        return "medium"
    return "watch"


def signal_id(published: date | None, index: int) -> str:
    stamp = published.strftime("%Y%m%d") if published else "undated"
    return f"SSL-{stamp}-{index:03d}"


def participant_context(frontmatter: dict[str, Any]) -> dict[str, Any]:
    host = frontmatter.get("host")
    panelists = frontmatter.get("panelists")
    guests = frontmatter.get("guests")
    speaker_status = frontmatter.get("speaker_status")
    if isinstance(host, str) or isinstance(panelists, list) or isinstance(guests, list) or isinstance(speaker_status, str):
        return {
            "host": host if isinstance(host, str) and host else None,
            "panelists": panelists if isinstance(panelists, list) else [],
            "guests": guests if isinstance(guests, list) else [],
            "speaker_status": speaker_status if isinstance(speaker_status, str) and speaker_status else "metadata-missing",
            "attribution_status": "episode-level-context",
        }
    return {
        "host": None,
        "panelists": [],
        "guests": [],
        "speaker_status": "metadata-missing",
        "attribution_status": "episode-level-context-unavailable",
    }


def format_participants(context: dict[str, Any]) -> str:
    parts: list[str] = []
    host = context.get("host")
    panelists = context.get("panelists") or []
    guests = context.get("guests") or []
    if host:
        parts.append(f"Host: {host}")
    if panelists:
        parts.append(f"Panel: {', '.join(panelists)}")
    if guests:
        parts.append(f"Guest: {', '.join(guests)}")
    return "; ".join(parts) if parts else "`metadata-missing`"


def participant_names(context: dict[str, Any]) -> list[str]:
    names: list[str] = []
    host = context.get("host")
    if isinstance(host, str) and host:
        names.append(host)
    for field in ("panelists", "guests"):
        values = context.get(field) or []
        if isinstance(values, list):
            names.extend(value for value in values if isinstance(value, str) and value)
    return names


def participant_filters(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    filters: dict[str, list[str]] = {}
    for row in rows:
        signal_id = row["signal_id"]
        for name in participant_names(row.get("participant_context", {})):
            filters.setdefault(name, []).append(signal_id)
    return {name: sorted(signal_ids) for name, signal_ids in sorted(filters.items())}


def rows_sorted_for_markdown(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority_order = {"high": 0, "medium": 1, "watch": 2}
    return sorted(
        rows,
        key=lambda row: (
            priority_order.get(row.get("priority", ""), 99),
            row.get("date_first_seen") or "",
            row.get("signal_id") or "",
        ),
    )


def build_payload(window_days: int, link_limit: int) -> dict[str, Any]:
    moonshots = [
        doc
        for doc in load_docs(MOONSHOTS_TRANSCRIPTS)
        if doc.published and date(2026, 8, 4) <= doc.published <= date(2026, 8, 27)
    ]
    innermost = load_docs(INNERMOST_TRANSCRIPTS)
    rows: list[dict[str, Any]] = []
    for index, doc in enumerate(sorted(moonshots, key=lambda item: item.published or date.min, reverse=True), 1):
        mechanisms = top_mechanisms(f"{doc.title}\n{doc.text}")
        forecasts = forecast_handles(f"{doc.title}\n{doc.text}")
        innermost_refs = matching_innermost_refs(doc, innermost, mechanisms, window_days, link_limit)
        frontmatter = parse_frontmatter(doc.text)
        status = "forecast-pending" if forecasts else "interpreted"
        next_check = (doc.published + timedelta(days=30)).isoformat() if doc.published else "unscheduled"
        rows.append(
            {
                "signal_id": signal_id(doc.published, 1),
                "date_first_seen": doc.published.isoformat() if doc.published else None,
                "moonshots_refs": [
                    {
                        "path": doc.repo_path,
                        "title": doc.title,
                        "date": doc.published.isoformat() if doc.published else None,
                    }
                ],
                "innermost_loop_refs": innermost_refs,
                "mechanism": mechanisms,
                "participant_context": participant_context(frontmatter),
                "forecast_claims": {
                    "status": "needs-human-extraction",
                    "candidate_handles": forecasts,
                },
                "evidence_status": status,
                "next_check_date": next_check,
                "priority": priority_for(mechanisms, len(forecasts), len(innermost_refs)),
                "disposition": "Review candidate links and extract atomic forecast claims before reuse.",
            }
        )
    payload = {
        "schema_version": 1,
        "ledger_id": "singularity-signal-ledger-v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "working-ledger",
        "collections": ["innermost-loop", "moonshots"],
        "authority_boundary": (
            "Cross-corpus triage only. Candidate links and forecast handles are not claim verification, "
            "rights clearance, archive admission, publication authority, or Narrative Geopolitics promotion."
        ),
        "mechanism_labels": sorted(MECHANISM_LEXICON),
        "source_roots": {
            "moonshots": repo_relative(MOONSHOTS_TRANSCRIPTS),
            "innermost-loop": repo_relative(INNERMOST_TRANSCRIPTS),
        },
        "matching_policy": {
            "method": "deterministic keyword overlap by mechanism label and publication-date window",
            "date_window_days": window_days,
            "innermost_candidate_limit": link_limit,
        },
        "rows": rows,
    }
    payload["participant_filters"] = participant_filters(rows)
    return payload


def md_list(values: list[str]) -> str:
    return "; ".join(f"`{value}`" for value in values) if values else "`unclassified`"


def md_refs(refs: list[dict[str, Any]]) -> str:
    if not refs:
        return "`pending-link`"
    return "<br>".join(f"`{ref['path']}`" for ref in refs)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Singularity Signal Ledger",
        "",
        "Status: `working-ledger`",
        f"Generated: {payload['generated_at']}",
        "Collections: `innermost-loop`, `moonshots`",
        f"Authority boundary: {payload['authority_boundary']}",
        "",
        "## Purpose",
        "",
        "The ledger turns the Singularity Science corpus into a repeatable signal engine:",
        "",
        "- `innermost-loop` is the daily sensor: high-frequency detection of frontier-AI and exponential-technology events.",
        "- `moonshots` is the interpretive panel: longer-form debate, causal models, forecasts, and narrative drift around selected signals.",
        "- Later evidence work adjudicates outcomes separately.",
        "",
        "Use the ledger when a signal appears in one corpus and needs to be tracked across the other without collapsing provenance or authority.",
        "",
        "## Row Contract",
        "",
        "Each row preserves `signal_id`, `date_first_seen`, `participant_context`, `innermost_loop_refs`, `moonshots_refs`, `mechanism`, `forecast_claims`, `evidence_status`, `next_check_date`, `priority`, and `disposition`.",
        "",
        "## Mechanism Labels",
        "",
    ]
    lines.extend(f"- `{label}`" for label in payload["mechanism_labels"])
    lines.extend(
        [
            "",
            "## Participant Filters",
            "",
            "These indexes are episode-level context only, not per-claim attribution.",
            "",
        ]
    )
    for participant, signal_ids in payload.get("participant_filters", {}).items():
        lines.append(f"- {participant}: {md_list(signal_ids)}")
    lines.extend(
        [
            "",
            "## Ledger",
            "",
            "| signal_id | date_first_seen | priority | participants | innermost_loop_refs | moonshots_refs | mechanism | forecast_claims | evidence_status | next_check_date | disposition |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows_sorted_for_markdown(payload["rows"]):
        handles = row["forecast_claims"]["candidate_handles"]
        forecast_text = "; ".join(f"`{handle}`" for handle in handles) if handles else "`needs-human-extraction`"
        lines.append(
            "| {signal_id} | {date_first_seen} | {priority} | {participants} | {inner} | {moon} | {mechanisms} | {forecasts} | {status} | {next_check} | {disposition} |".format(
                signal_id=row["signal_id"],
                date_first_seen=row["date_first_seen"] or "`undated`",
                priority=row["priority"],
                participants=format_participants(row["participant_context"]),
                inner=md_refs(row["innermost_loop_refs"]),
                moon=md_refs(row["moonshots_refs"]),
                mechanisms=md_list(row["mechanism"]),
                forecasts=forecast_text,
                status=row["evidence_status"],
                next_check=row["next_check_date"],
                disposition=row["disposition"],
            )
        )
    lines.extend(
        [
            "",
            "## Next Operating Pass",
            "",
            "1. Review candidate Innermost Loop links and remove false positives.",
            "2. Extract atomic forecasts into claim-shaped rows with source-local timestamps when available.",
            "3. Split multi-topic Moonshots episodes into separate signals when a mechanism has its own decision value.",
            "4. Promote only verified, source-backed geopolitical implications through the appropriate review workflow.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(payload: dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Singularity Signal Ledger from local corpus files.")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--date-window-days", type=int, default=45)
    parser.add_argument("--innermost-candidate-limit", type=int, default=3)
    parser.add_argument("--check", action="store_true", help="Render in memory and report row counts without writing.")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(
        window_days=args.date_window_days,
        link_limit=args.innermost_candidate_limit,
    )
    summary = {
        "rows": len(payload["rows"]),
        "json_output": repo_relative(args.json_output.resolve()) if args.json_output.is_absolute() and REPO_ROOT in args.json_output.resolve().parents else str(args.json_output),
        "markdown_output": repo_relative(args.markdown_output.resolve()) if args.markdown_output.is_absolute() and REPO_ROOT in args.markdown_output.resolve().parents else str(args.markdown_output),
        "check": bool(args.check),
    }
    if not args.check:
        write_outputs(payload, args.json_output, args.markdown_output)
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=True))
    else:
        print(f"rows={summary['rows']} check={str(summary['check']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

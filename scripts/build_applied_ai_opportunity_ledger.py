import argparse
import json
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
SINGULARITY_ROOT = REPO_ROOT / "archive" / "sources" / "singularity"
NATE_B_JONES_TRANSCRIPTS = SINGULARITY_ROOT / "nate-b-jones" / "transcripts"
NATE_HERK_TRANSCRIPTS = SINGULARITY_ROOT / "nate-herk" / "transcripts"
INNERMOST_TRANSCRIPTS = SINGULARITY_ROOT / "innermost-loop" / "transcripts"
DEFAULT_JSON = SINGULARITY_ROOT / "applied-ai-opportunity-ledger.json"
DEFAULT_MARKDOWN = SINGULARITY_ROOT / "applied-ai-opportunity-ledger.md"

OFFER_MAP: dict[str, dict[str, Any]] = {
    "AAO-20260823-004": {
        "rank": 1,
        "offer_name": "Constraint-to-Automation Sprint",
        "primary_buyer": "Founder-led service businesses, agencies, local operators",
        "core_pain": "Manual workflows, lead handling, context handoff",
        "delivery_shape": "Identify one bottleneck, build a Claude/Codex workflow, measure before/after movement.",
        "pricing_model": "Discovery sprint plus implementation fee; retainer candidate after measured workflow lift.",
        "measurement_plan": "Capture baseline cycle time, lead conversion, or revenue leakage before build; compare after workflow deployment.",
        "why_high_roi": "Closest path from AI curiosity to paid implementation because it sells a measured operational improvement.",
    },
    "AAO-20260823-005": {
        "rank": 2,
        "offer_name": "Automation Pricing Clinic",
        "primary_buyer": "AI consultants, agencies, technical solo operators",
        "core_pain": "Pricing uncertainty, weak packaging, unclear ROI story",
        "delivery_shape": "Convert automation requests into price bands, setup fees, retainers, and ROI-backed proposals.",
        "pricing_model": "Fixed-fee pricing audit, proposal rewrite, or packaged offer ladder.",
        "measurement_plan": "Track proposal acceptance, average contract value, and retained margin before and after pricing revision.",
        "why_high_roi": "Pricing is the conversion layer between capability and revenue; improving it lifts every future offer.",
    },
    "AAO-20260821-009": {
        "rank": 3,
        "offer_name": "Five Demand-Ready Automations Catalog",
        "primary_buyer": "Small businesses, agencies, enterprise team leads",
        "core_pain": "Demand discovery, repeated workflow pain, sales friction",
        "delivery_shape": "Maintain a pre-scoped catalog of automations such as lead capture, follow-up, reporting, content ops, and internal knowledge workflows.",
        "pricing_model": "Menu of fixed-scope implementations with optional support retainers.",
        "measurement_plan": "Score each automation by buyer urgency, implementation time, repeatability, and measurable operating impact.",
        "why_high_roi": "Reduces discovery friction and creates a reusable what-to-sell-now surface.",
    },
    "AAO-20260823-003": {
        "rank": 4,
        "offer_name": "Workflow Asset Productization",
        "primary_buyer": "Solo operators, agencies, enterprise ops teams",
        "core_pain": "Service labor does not compound, one-off workflows decay",
        "delivery_shape": "Convert one-off automations into reusable workflows, templates, playbooks, and internal operating assets.",
        "pricing_model": "Implementation fee plus asset maintenance, internal enablement, or template licensing.",
        "measurement_plan": "Measure reuse count, setup-time reduction, support burden, and downstream workflow adoption.",
        "why_high_roi": "Moves from implementation labor to reusable assets where margin and compounding can begin.",
    },
    "AAO-20260709-024": {
        "rank": 5,
        "offer_name": "Cheap Agent Swarm Build Lab",
        "primary_buyer": "Software teams, AI-native builders, product teams",
        "core_pain": "Build-cycle drag, QA bottlenecks, model-cost pressure",
        "delivery_shape": "Prototype low-cost multi-agent build and review loops for sites, tools, audits, and QA.",
        "pricing_model": "Prototype lab, internal enablement workshop, or verification-loop implementation.",
        "measurement_plan": "Compare human hours, model cost, defect rate, and test-pass rate against a single-agent baseline.",
        "why_high_roi": "Many cheap agents plus strict verification can compress build cycles without assuming expensive model usage.",
    },
    "AAO-20260821-008": {
        "rank": 6,
        "offer_name": "Agent Tool Selection Matrix",
        "primary_buyer": "Software teams, solo builders, AI ops leads",
        "core_pain": "Tool mismatch, wasted experimentation, context handoff",
        "delivery_shape": "Compare Codex, Claude Code, browser agents, and model/tool combinations by task class.",
        "pricing_model": "Diagnostic engagement, tool-routing playbook, or team operating guide.",
        "measurement_plan": "Track avoided rework, task completion time, handoff failures, and tool spend after routing changes.",
        "why_high_roi": "Prevents hidden hour loss by routing work to the right agent loop.",
    },
}

IMPLEMENTATION_BRIEFS: dict[str, dict[str, Any]] = {
    "AAO-20260823-004": {
        "status": "draft",
        "brief_id": "constraint-to-automation-sprint-v1",
        "offer_name": "Constraint-to-Automation Sprint",
        "purpose": "Turn one painful business bottleneck into a measured AI workflow improvement.",
        "core_promise": "We find one workflow costing you time or revenue, automate the smallest useful version, and prove whether the number moved.",
        "best_buyers": [
            "Founder-led service business",
            "Agency",
            "Local operator",
            "Small ops team with obvious manual leakage",
        ],
        "ideal_first_use_cases": [
            "Lead intake and follow-up",
            "Proposal or quote generation",
            "Customer support triage",
            "Weekly reporting",
            "CRM cleanup",
            "Content repurposing",
            "Internal knowledge retrieval",
        ],
        "delivery_steps": [
            "Diagnose one constraint with clear volume, pain, owner, and measurable before-state.",
            "Define the metric: time per task, response time, conversion rate, missed leads, error rate, or weekly labor hours.",
            "Build the minimum AI workflow with Claude, Codex, or browser automation as needed, with human review where risk demands it.",
            "Run a before/after test against the same workflow after deployment.",
            "Package the win into a reusable playbook, template, checklist, or retainer candidate.",
        ],
        "offer_ladder": [
            {"stage": "Audit", "shape": "Fixed-fee workflow constraint scan."},
            {"stage": "Sprint", "shape": "One measured automation shipped in 1-2 weeks."},
            {"stage": "Retainer", "shape": "Maintain, improve, and expand the workflow stack."},
            {"stage": "Asset", "shape": "Reusable templates or workflows for repeated deployment."},
        ],
        "measurement_plan": [
            "Baseline manual time per run",
            "Weekly workflow volume",
            "Error or rework count",
            "Revenue or lead leakage where visible",
            "Post-automation time per run",
            "Human review burden",
            "Adoption rate after handoff",
        ],
        "go_no_go_filter": {
            "strong_yes": "Painful, repeated, measurable, owned by one team, and safe to automate partially.",
            "maybe": "Strategic but hard to measure.",
            "no": "One-off task, unclear owner, no baseline, or high-risk without review controls.",
        },
        "innermost_loop_angle": "Detect constraint, intervene, measure, retain the workflow pattern, and feed the result back into the Applied AI ledger.",
        "related_artifacts": {
            "implementation_brief": "archive/sources/singularity/constraint-to-automation-sprint-implementation-brief.md",
            "client_one_pager": "archive/sources/singularity/constraint-to-automation-sprint-client-one-pager.md",
            "intake_worksheet": "archive/sources/singularity/constraint-to-automation-sprint-intake-worksheet.md",
            "delivery_checklist": "archive/sources/singularity/constraint-to-automation-sprint-delivery-checklist.md",
        },
        "authority_boundary": "Implementation planning only; not customer validation, legal advice, factual verification, rights clearance, or a promise of business results.",
    }
}

CREATORS = {
    "innermost-loop": "Innermost Loop",
    "nate-b-jones": "Nate B. Jones",
    "nate-herk": "Nate Herk",
}

OPPORTUNITY_LEXICON: dict[str, tuple[str, ...]] = {
    "automation-service": ("automation", "automations", "ai consultant", "client", "business owner", "retainer"),
    "agent-setup": ("agent", "agents", "sub-agent", "multi-agent", "grok bot", "codex", "claude code"),
    "browser-automation": ("browser", "chrome", "click", "website", "web app", "browser use"),
    "ai-native-ops": ("ai operating system", "aios", "workflow", "workflows", "operations", "ops"),
    "workflow-productization": ("template", "templates", "skill", "skills", "productized", "package"),
    "pricing-and-packaging": ("price", "pricing", "$", "month", "retainer", "subscription"),
    "sales-and-positioning": ("sell", "sales", "outreach", "upwork", "lead", "leads", "positioning"),
    "model-tool-arbitrage": ("glm", "cheap", "cheaper", "model", "models", "token", "tokens", "api costs"),
    "security-risk": ("security", "permission", "permissions", "hooks", "secret", "api key", "attack"),
    "finance-investment-signal": ("bubble", "nvidia", "retirement", "stock", "market", "investment"),
    "solo-business-system": ("one-person", "one person", "solo", "no agency", "no team"),
    "skill-or-template-system": ("skill", "skills", "template", "templates", "companion guide", "setup"),
}

BUYER_LEXICON: dict[str, tuple[str, ...]] = {
    "small business": ("small business", "business owner", "hvac", "real estate", "dentist"),
    "agency": ("agency", "marketing agency", "client", "clients"),
    "solo operator": ("one-person", "one person", "solo", "operator"),
    "software team": ("developer", "engineer", "codebase", "repository", "coding"),
    "enterprise": ("enterprise", "company", "ceo", "team", "teams"),
}

PAIN_LEXICON: dict[str, tuple[str, ...]] = {
    "manual workflow": ("manual", "hours per task", "rework", "waste", "calendar"),
    "lead handling": ("lead", "leads", "follow-up", "appointments", "conversions"),
    "tool-cost pressure": ("$200", "$18", "api costs", "token bills", "hit your limit"),
    "context handoff": ("handoff", "context", "conversation", "prompt cache", "project context"),
    "ai adoption gap": ("adoption", "ceos", "workers use ai", "specific business needs"),
}

STACK_LEXICON: dict[str, tuple[str, ...]] = {
    "Codex": ("codex",),
    "Claude Code": ("claude code", "cloud code"),
    "GLM": ("glm", "z.ai"),
    "Grok Bot": ("grok bot",),
    "browser automation": ("browser", "chrome"),
}

ROI_PATTERNS = (
    re.compile(r"\$\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:k|m|b|month|monthly))?", re.IGNORECASE),
    re.compile(r"\b\d+(?:\.\d+)?%?\s*(?:to|-)\s*\d+(?:\.\d+)?%", re.IGNORECASE),
    re.compile(r"\b\d+(?:\.\d+)?%\b"),
    re.compile(r"\b\d+(?:\.\d+)?x\b", re.IGNORECASE),
    re.compile(r"\b\d+\s*(?:hours?|minutes?|mins?|weeks?|months?)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class SourceDoc:
    path: Path
    repo_path: str
    collection: str
    creator: str
    title: str
    published: date | None
    metadata: dict[str, str]
    text: str


def repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def parse_markdown_metadata(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in text.splitlines()[:30]:
        match = re.match(r"^-\s*([^:]+):\s*(.*)$", line)
        if match:
            metadata[match.group(1).strip().lower()] = match.group(2).strip()
    return metadata


def parse_date(value: str | None, fallback_name: str) -> date | None:
    candidates = [value or "", fallback_name]
    for candidate in candidates:
        match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", candidate)
        if match:
            return date.fromisoformat(match.group(1))
    return None


def title_from_text(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].removesuffix(" - Transcript").strip()
        if stripped and not stripped.startswith("-"):
            return stripped
    return fallback


def load_docs(root: Path, collection: str) -> list[SourceDoc]:
    docs: list[SourceDoc] = []
    if not root.exists():
        return docs
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        metadata = parse_markdown_metadata(text)
        docs.append(
            SourceDoc(
                path=path,
                repo_path=repo_relative(path),
                collection=collection,
                creator=CREATORS[collection],
                title=title_from_text(text, path.stem),
                published=parse_date(metadata.get("date published") or metadata.get("date captured"), path.name),
                metadata=metadata,
                text=text,
            )
        )
    return docs


def score_labels(text: str, lexicon: dict[str, tuple[str, ...]], limit: int | None = None) -> list[str]:
    haystack = text.lower()
    scores = []
    for label, terms in lexicon.items():
        score = sum(haystack.count(term) for term in terms)
        if score:
            scores.append((score, label))
    labels = [label for _score, label in sorted(scores, key=lambda item: (-item[0], item[1]))]
    return labels if limit is None else labels[:limit]


def roi_handles(text: str, limit: int = 8) -> list[str]:
    handles: list[str] = []
    for pattern in ROI_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(0).strip()
            if value.lower() not in {item.lower() for item in handles}:
                handles.append(value)
            if len(handles) >= limit:
                return handles
    return handles


def source_status(path: Path) -> str:
    git_dir = REPO_ROOT / ".git"
    if not git_dir.exists():
        return "unknown"
    import subprocess

    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", repo_relative(path)],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return "tracked" if result.returncode == 0 else "untracked-local"


def implementation_difficulty(types: list[str], source_text: str) -> str:
    hard = {"agent-setup", "browser-automation", "security-risk"}
    if "enterprise" in score_labels(source_text, BUYER_LEXICON) or hard.intersection(types):
        return "medium"
    return "low"


def time_to_value(types: list[str]) -> str:
    if {"automation-service", "sales-and-positioning", "pricing-and-packaging"}.intersection(types):
        return "short"
    return "medium"


def repeatability(types: list[str]) -> str:
    if {"workflow-productization", "skill-or-template-system", "automation-service"}.intersection(types):
        return "high"
    return "medium"


def priority_for(types: list[str], buyers: list[str], roi_count: int) -> str:
    if {"automation-service", "model-tool-arbitrage", "solo-business-system"}.intersection(types) and (buyers or roi_count):
        return "high"
    if buyers or roi_count:
        return "medium"
    return "watch"


def offer_map_entry(opportunity_id_value: str) -> dict[str, Any]:
    entry = OFFER_MAP.get(opportunity_id_value)
    if not entry:
        return {
            "status": "not-mapped",
            "rank": None,
            "offer_name": None,
            "primary_buyer": None,
            "core_pain": None,
            "delivery_shape": None,
            "pricing_model": None,
            "measurement_plan": None,
            "source_row_ids": [],
            "why_high_roi": None,
        }
    return {
        "status": "mapped",
        "rank": entry["rank"],
        "offer_name": entry["offer_name"],
        "primary_buyer": entry["primary_buyer"],
        "core_pain": entry["core_pain"],
        "delivery_shape": entry["delivery_shape"],
        "pricing_model": entry["pricing_model"],
        "measurement_plan": entry["measurement_plan"],
        "source_row_ids": [opportunity_id_value],
        "why_high_roi": entry["why_high_roi"],
    }


def implementation_brief_entry(opportunity_id_value: str) -> dict[str, Any]:
    brief = IMPLEMENTATION_BRIEFS.get(opportunity_id_value)
    if not brief:
        return {
            "status": "not-drafted",
            "brief_id": None,
            "offer_name": None,
            "purpose": None,
            "core_promise": None,
            "best_buyers": [],
            "ideal_first_use_cases": [],
            "delivery_steps": [],
            "offer_ladder": [],
            "measurement_plan": [],
            "go_no_go_filter": {},
            "innermost_loop_angle": None,
            "related_artifacts": {},
            "authority_boundary": None,
        }
    return {
        "status": brief["status"],
        "brief_id": brief["brief_id"],
        "offer_name": brief["offer_name"],
        "purpose": brief["purpose"],
        "core_promise": brief["core_promise"],
        "best_buyers": list(brief["best_buyers"]),
        "ideal_first_use_cases": list(brief["ideal_first_use_cases"]),
        "delivery_steps": list(brief["delivery_steps"]),
        "offer_ladder": [dict(item) for item in brief["offer_ladder"]],
        "measurement_plan": list(brief["measurement_plan"]),
        "go_no_go_filter": dict(brief["go_no_go_filter"]),
        "innermost_loop_angle": brief["innermost_loop_angle"],
        "related_artifacts": dict(brief["related_artifacts"]),
        "authority_boundary": brief["authority_boundary"],
    }


def matching_innermost_refs(doc: SourceDoc, innermost_docs: list[SourceDoc], types: list[str], window_days: int, limit: int) -> list[dict[str, Any]]:
    if doc.published is None:
        return []
    terms = {term for label in types for term in OPPORTUNITY_LEXICON.get(label, ())}
    earliest = doc.published - timedelta(days=window_days)
    latest = doc.published + timedelta(days=window_days)
    scored: list[tuple[int, SourceDoc, list[str]]] = []
    for inner in innermost_docs:
        if inner.published is None or not earliest <= inner.published <= latest:
            continue
        haystack = f"{inner.title}\n{inner.text}".lower()
        hits = sorted(term for term in terms if term in haystack)
        if hits:
            score = len(hits) * 10 - abs((doc.published - inner.published).days)
            scored.append((score, inner, hits[:8]))
    return [
        {
            "path": inner.repo_path,
            "title": inner.title,
            "date": inner.published.isoformat() if inner.published else None,
            "matched_terms": hits,
            "match_status": "candidate",
        }
        for _score, inner, hits in sorted(scored, key=lambda item: (-item[0], item[1].repo_path))[:limit]
    ]


def opportunity_id(published: date | None, index: int) -> str:
    stamp = published.strftime("%Y%m%d") if published else "undated"
    return f"AAO-{stamp}-{index:03d}"


def build_payload(window_days: int, link_limit: int) -> dict[str, Any]:
    source_docs = load_docs(NATE_B_JONES_TRANSCRIPTS, "nate-b-jones") + load_docs(NATE_HERK_TRANSCRIPTS, "nate-herk")
    innermost_docs = load_docs(INNERMOST_TRANSCRIPTS, "innermost-loop")
    rows: list[dict[str, Any]] = []
    for index, doc in enumerate(sorted(source_docs, key=lambda item: (item.published or date.min, item.repo_path), reverse=True), 1):
        scan_text = f"{doc.title}\n{doc.text}"
        types = score_labels(scan_text, OPPORTUNITY_LEXICON, limit=4)
        buyers = score_labels(scan_text, BUYER_LEXICON, limit=3)
        pain_points = score_labels(scan_text, PAIN_LEXICON, limit=3)
        stack = score_labels(scan_text, STACK_LEXICON, limit=4)
        roi = roi_handles(scan_text)
        row_id = opportunity_id(doc.published, index)
        rows.append(
            {
                "opportunity_id": row_id,
                "date_first_seen": doc.published.isoformat() if doc.published else None,
                "source_refs": [
                    {
                        "path": doc.repo_path,
                        "title": doc.title,
                        "date": doc.published.isoformat() if doc.published else None,
                        "source_status": source_status(doc.path),
                    }
                ],
                "innermost_loop_refs": matching_innermost_refs(doc, innermost_docs, types, window_days, link_limit),
                "creator_context": {"collection": doc.collection, "creator": doc.creator},
                "opportunity_type": types,
                "buyer_or_user": buyers,
                "pain_point": pain_points,
                "workflow_pattern": types[:3],
                "tool_stack": stack,
                "pricing_or_roi_signal": {"status": "candidate" if roi else "needs-human-extraction", "handles": roi},
                "implementation_difficulty": implementation_difficulty(types, scan_text),
                "time_to_value": time_to_value(types),
                "repeatability": repeatability(types),
                "evidence_status": "triage-only",
                "priority": priority_for(types, buyers, len(roi)),
                "offer_map": offer_map_entry(row_id),
                "implementation_brief": implementation_brief_entry(row_id),
                "disposition": "Extract concrete workflow, buyer proof, and delivery steps before reuse.",
            }
        )
    payload = {
        "schema_version": 1,
        "ledger_id": "applied-ai-opportunity-ledger-v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "working-ledger",
        "collections": ["nate-b-jones", "nate-herk", "innermost-loop"],
        "authority_boundary": (
            "Opportunity triage only. Rows are not revenue proof, customer validation, financial advice, "
            "rights clearance, public claim verification, or permission to reuse transcript bodies."
        ),
        "opportunity_labels": sorted(OPPORTUNITY_LEXICON),
        "source_roots": {
            "nate-b-jones": repo_relative(NATE_B_JONES_TRANSCRIPTS),
            "nate-herk": repo_relative(NATE_HERK_TRANSCRIPTS),
            "innermost-loop": repo_relative(INNERMOST_TRANSCRIPTS),
        },
        "matching_policy": {
            "method": "deterministic keyword overlap by opportunity label and publication-date window",
            "date_window_days": window_days,
            "innermost_candidate_limit": link_limit,
        },
        "creator_filters": creator_filters(rows),
        "opportunity_type_filters": opportunity_type_filters(rows),
        "offer_map_filters": offer_map_filters(rows),
        "rows": rows,
    }
    return payload


def creator_filters(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    filters: dict[str, list[str]] = {}
    for row in rows:
        creator = row["creator_context"]["creator"]
        filters.setdefault(creator, []).append(row["opportunity_id"])
    return {creator: sorted(ids) for creator, ids in sorted(filters.items())}


def opportunity_type_filters(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    filters: dict[str, list[str]] = {}
    for row in rows:
        for label in row["opportunity_type"]:
            filters.setdefault(label, []).append(row["opportunity_id"])
    return {label: sorted(ids) for label, ids in sorted(filters.items())}


def offer_map_filters(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    mapped = [
        row["opportunity_id"]
        for row in sorted(rows, key=lambda item: ((item["offer_map"]["rank"] is None), item["offer_map"]["rank"] or 999))
        if row.get("offer_map", {}).get("status") == "mapped"
    ]
    return {"mapped": mapped}


def md_list(values: list[str]) -> str:
    return "; ".join(f"`{value}`" for value in values) if values else "`unclassified`"


def md_refs(refs: list[dict[str, Any]]) -> str:
    if not refs:
        return "`pending-link`"
    return "<br>".join(f"`{ref['path']}`" for ref in refs)


def rows_sorted_for_markdown(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority_order = {"high": 0, "medium": 1, "watch": 2}
    return sorted(
        rows,
        key=lambda row: (
            priority_order.get(row.get("priority", ""), 99),
            row.get("date_first_seen") or "",
            row.get("opportunity_id") or "",
        ),
    )


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Applied AI Opportunity Ledger",
        "",
        "Status: `working-ledger`",
        f"Generated: {payload['generated_at']}",
        "Collections: `nate-b-jones`, `nate-herk`, `innermost-loop`",
        f"Authority boundary: {payload['authority_boundary']}",
        "",
        "## Purpose",
        "",
        "This ledger turns builder/operator transcripts into a repeatable opportunity engine:",
        "",
        "- `nate-b-jones` supplies agent setup, model-routing, cost, risk, and AI-native operating-system judgment.",
        "- `nate-herk` supplies sellable automation, workflow packaging, pricing, outreach, and one-person business motion.",
        "- `innermost-loop` supplies candidate adjacent daily signals, not proof of opportunity value.",
        "",
        "Use the ledger to decide what to build, automate, productize, sell, or investigate next without collapsing triage into validation.",
        "",
        "## Opportunity Labels",
        "",
    ]
    lines.extend(f"- `{label}`" for label in payload["opportunity_labels"])
    lines.extend(["", "## Creator Filters", ""])
    for creator, ids in payload.get("creator_filters", {}).items():
        lines.append(f"- {creator}: {md_list(ids)}")
    lines.extend(["", "## Opportunity Type Filters", ""])
    for label, ids in payload.get("opportunity_type_filters", {}).items():
        lines.append(f"- `{label}`: {md_list(ids)}")
    lines.extend(["", "## Offer Map Filters", ""])
    for label, ids in payload.get("offer_map_filters", {}).items():
        lines.append(f"- `{label}`: {md_list(ids)}")
    lines.extend(["", "## Offer Map", ""])
    lines.extend(
        [
            "| rank | offer_name | source_row_ids | primary_buyer | core_pain | delivery_shape | pricing_model | measurement_plan | why_high_roi |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    mapped_rows = [
        row
        for row in sorted(payload["rows"], key=lambda item: item.get("offer_map", {}).get("rank") or 999)
        if row.get("offer_map", {}).get("status") == "mapped"
    ]
    for row in mapped_rows:
        offer = row["offer_map"]
        lines.append(
            "| {rank} | {offer_name} | {source_row_ids} | {primary_buyer} | {core_pain} | {delivery_shape} | {pricing_model} | {measurement_plan} | {why_high_roi} |".format(
                rank=offer["rank"],
                offer_name=offer["offer_name"],
                source_row_ids=md_list(offer["source_row_ids"]),
                primary_buyer=offer["primary_buyer"],
                core_pain=offer["core_pain"],
                delivery_shape=offer["delivery_shape"],
                pricing_model=offer["pricing_model"],
                measurement_plan=offer["measurement_plan"],
                why_high_roi=offer["why_high_roi"],
            )
        )
    brief_rows = [
        row
        for row in sorted(payload["rows"], key=lambda item: item.get("offer_map", {}).get("rank") or 999)
        if row.get("implementation_brief", {}).get("status") == "draft"
    ]
    if brief_rows:
        lines.extend(["", "## Implementation Briefs", ""])
        for row in brief_rows:
            brief = row["implementation_brief"]
            lines.extend(
                [
                    f"### {brief['offer_name']}",
                    "",
                    f"- Brief ID: `{brief['brief_id']}`",
                    f"- Source row: `{row['opportunity_id']}`",
                    f"- Purpose: {brief['purpose']}",
                    f"- Core promise: {brief['core_promise']}",
                    f"- Innermost Loop angle: {brief['innermost_loop_angle']}",
                    f"- Authority boundary: {brief['authority_boundary']}",
                    f"- Related artifacts: {', '.join(f'`{name}` -> `{path}`' for name, path in brief['related_artifacts'].items())}",
                    "",
                    "Delivery steps:",
                ]
            )
            lines.extend(f"{index}. {step}" for index, step in enumerate(brief["delivery_steps"], 1))
            lines.extend(["", "Measurement plan:"])
            lines.extend(f"- {item}" for item in brief["measurement_plan"])
    lines.extend(
        [
            "",
            "## Ledger",
            "",
            "| opportunity_id | date_first_seen | priority | creator | mapped_offer | opportunity_type | buyer_or_user | pain_point | tool_stack | pricing_or_roi_signal | source_refs | innermost_loop_refs | disposition |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows_sorted_for_markdown(payload["rows"]):
        handles = row["pricing_or_roi_signal"]["handles"]
        roi_text = "; ".join(f"`{handle}`" for handle in handles) if handles else "`needs-human-extraction`"
        mapped_offer = row.get("offer_map", {}).get("offer_name") or "`not-mapped`"
        lines.append(
            "| {opportunity_id} | {date_first_seen} | {priority} | {creator} | {mapped_offer} | {types} | {buyers} | {pain} | {stack} | {roi} | {sources} | {inner} | {disposition} |".format(
                opportunity_id=row["opportunity_id"],
                date_first_seen=row["date_first_seen"] or "`undated`",
                priority=row["priority"],
                creator=row["creator_context"]["creator"],
                mapped_offer=mapped_offer,
                types=md_list(row["opportunity_type"]),
                buyers=md_list(row["buyer_or_user"]),
                pain=md_list(row["pain_point"]),
                stack=md_list(row["tool_stack"]),
                roi=roi_text,
                sources=md_refs(row["source_refs"]),
                inner=md_refs(row["innermost_loop_refs"]),
                disposition=row["disposition"],
            )
        )
    lines.extend(
        [
            "",
            "## Next Operating Pass",
            "",
            "1. Review high-priority rows and split multi-opportunity videos where one workflow has standalone value.",
            "2. Extract concrete offer, buyer, pricing, and delivery claims into claim-shaped rows.",
            "3. Mark untracked-local source records as admitted only through the appropriate archive workflow.",
            "4. Promote only validated opportunities into execution plans or customer-facing material.",
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
    parser = argparse.ArgumentParser(description="Build the Applied AI Opportunity Ledger from local corpus files.")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--date-window-days", type=int, default=45)
    parser.add_argument("--innermost-candidate-limit", type=int, default=3)
    parser.add_argument("--check", action="store_true", help="Render in memory and report row counts without writing.")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.date_window_days, args.innermost_candidate_limit)
    summary = {
        "rows": len(payload["rows"]),
        "creator_filters": sorted(payload["creator_filters"]),
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

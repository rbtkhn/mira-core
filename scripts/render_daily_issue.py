from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import verification
import reality


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
DAILY_ROOT = NG_ROOT / "work" / "daily"
TEMPLATE_PATH = NG_ROOT / "templates" / "issue.md"
LEDGER_PATH = NG_ROOT / "work" / "forecasts" / "forecast-ledger.md"
CANONICAL_FILES = ("sources.md", "synthesis.md", "forecast.md", "daily-brief.md")

STORY_ID_RE = re.compile(r"NGI-(\d{8})-S\d{2}")
SOURCE_ID_RE = re.compile(r"SRC-\d{2}")
HOOK_ID_RE = re.compile(r"NG-\d{8}-F\d{2}")
CLAIM_ID_RE = re.compile(r"OPC-\d{8}-\d{2}")
LATTICE_ID_RE = re.compile(r"(?:OPC|CLM|NG)-\d{8}-(?:\d{2}|F\d{2})")
VER_ID_RE = re.compile(r"VER-\d{8}-\d{2}")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
PLACEHOLDER_RE = re.compile(
    r"(?:\{\{[A-Z_]+\}\}|YYYY-MM-DD|NGI-YYYYMMDD|\bTODO\b|\bTBD\b|"
    r"\[Distinctive title|State what changed|Status:\s*`template`)",
    re.IGNORECASE,
)

REQUIRED_ISSUE_SECTIONS = (
    "Front Page",
    "Briefing Desk",
    "Main Analysis",
    "Source Ledger",
    "Forecast Desk",
    "Verification Desk",
    "Voices / Columns",
    "Editor's Note",
)
PLACEMENTS = {"lead", "brief", "hold"}
EVIDENCE_POSTURES = {
    "source-assertion",
    "bounded-analysis",
    "forecast",
    "verification-supported",
    "verification-contested",
    "mixed",
}


class IssueError(ValueError):
    pass


@dataclass(frozen=True)
class IssueValidationContext:
    ledger_text: str
    manifest_paths: frozenset[str]
    reality_records: Mapping[str, dict[str, Any]]


def load_validation_context(
    daily_root: Path = DAILY_ROOT,
    ledger_path: Path = LEDGER_PATH,
    reality_root: Path = reality.REALITY_ROOT,
) -> IssueValidationContext:
    manifest_path = daily_root.parents[2] / "archive" / "geopolitics" / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    return IssueValidationContext(
        ledger_text=ledger_path.read_text(encoding="utf-8"),
        manifest_paths=frozenset(
            str(row.get("local_path", "")) for row in manifest.get("sources", [])
        ),
        reality_records=reality.load_records(reality_root),
    )


@dataclass(frozen=True)
class Story:
    story_id: str
    placement: str
    headline: str
    crisis_object: str
    evidence_posture: str
    source_ids: tuple[str, ...]
    voices: tuple[str, ...]
    forecast_hooks: tuple[str, ...]
    operational_claims: tuple[str, ...]
    reality_claims: tuple[str, ...]
    selection_rationale: str


@dataclass(frozen=True)
class IssueModel:
    run_date: str
    title: str
    title_rationale: str
    stories: tuple[Story, ...]
    copy: dict[str, str]
    source_rows: dict[str, dict[str, str]]
    voice_rows: list[dict[str, str]]
    claim_rows: dict[str, dict[str, str]]
    verification_links: dict[str, str]
    forecast_rows: dict[str, dict[str, str]]
    day_hook_ids: frozenset[str]
    missing_observables: str
    revision_log: str
    input_digest: str
    reality_digest: str


def clean_cell(value: str) -> str:
    return value.strip().strip("`").strip()


def split_list(value: str, pattern: re.Pattern[str]) -> tuple[str, ...]:
    if clean_cell(value).lower() == "none":
        return ()
    return tuple(dict.fromkeys(pattern.findall(value)))


def extract_section(text: str, name: str, level: int = 2) -> str:
    marker = re.compile(rf"^{'#' * level}\s+{re.escape(name)}\s*$", re.MULTILINE)
    match = marker.search(text)
    if not match:
        return ""
    next_heading = re.search(rf"^#{{1,{level}}}\s+", text[match.end():], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end():end].strip()


def markdown_tables(text: str) -> list[list[dict[str, str]]]:
    tables: list[list[dict[str, str]]] = []
    lines = text.splitlines()
    index = 0
    while index + 1 < len(lines):
        if not lines[index].lstrip().startswith("|") or not lines[index + 1].lstrip().startswith("|"):
            index += 1
            continue
        headers = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
        separator = [cell.strip() for cell in lines[index + 1].strip().strip("|").split("|")]
        if len(headers) != len(separator) or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            index += 1
            continue
        rows: list[dict[str, str]] = []
        index += 2
        while index < len(lines) and lines[index].lstrip().startswith("|"):
            cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
            index += 1
        tables.append(rows)
    return tables


def first_table_with(text: str, required_headers: set[str]) -> list[dict[str, str]]:
    for rows in markdown_tables(text):
        if rows and required_headers <= set(rows[0]):
            return rows
    return []


def canonical_inputs(run_date: str, daily_root: Path = DAILY_ROOT) -> dict[str, str]:
    run_dir = daily_root / run_date
    missing = [name for name in CANONICAL_FILES if not (run_dir / name).exists()]
    if missing:
        raise IssueError(f"missing canonical daily inputs: {', '.join(missing)}")
    return {name: (run_dir / name).read_text(encoding="utf-8") for name in CANONICAL_FILES}


def input_digest(inputs: dict[str, str]) -> str:
    digest = hashlib.sha256()
    digest.update(b"daily-issue-v1\0")
    for name in CANONICAL_FILES:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(inputs[name].encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def display_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else path.as_posix()


def parse_stories(run_date: str, synthesis: str) -> tuple[Story, ...]:
    section = extract_section(synthesis, "Issue Story Desk")
    required = {
        "Story ID", "Placement", "Argument headline", "Crisis object",
        "Evidence posture", "Source IDs", "Voices", "Forecast hooks",
        "Operational claims", "Selection rationale",
    }
    rows = first_table_with(section, required)
    if not rows:
        raise IssueError("synthesis.md is missing a complete Issue Story Desk table")
    stories: list[Story] = []
    for row in rows:
        story_id = clean_cell(row["Story ID"])
        placement = clean_cell(row["Placement"])
        posture = clean_cell(row["Evidence posture"])
        if not STORY_ID_RE.fullmatch(story_id) or STORY_ID_RE.fullmatch(story_id).group(1) != run_date.replace("-", ""):
            raise IssueError(f"invalid or wrong-date story ID: {story_id}")
        if placement not in PLACEMENTS:
            raise IssueError(f"{story_id}: invalid placement {placement}")
        if posture not in EVIDENCE_POSTURES:
            raise IssueError(f"{story_id}: invalid evidence posture {posture}")
        stories.append(Story(
            story_id=story_id,
            placement=placement,
            headline=clean_cell(row["Argument headline"]),
            crisis_object=clean_cell(row["Crisis object"]),
            evidence_posture=posture,
            source_ids=split_list(row["Source IDs"], SOURCE_ID_RE),
            voices=tuple(part.strip() for part in re.split(r"[,;]", clean_cell(row["Voices"])) if part.strip() and part.strip().lower() != "none"),
            forecast_hooks=split_list(row["Forecast hooks"], HOOK_ID_RE),
            operational_claims=split_list(row["Operational claims"], CLAIM_ID_RE),
            reality_claims=split_list(row.get("Reality Claim IDs", "none"), LATTICE_ID_RE),
            selection_rationale=clean_cell(row["Selection rationale"]),
        ))
    if sum(story.placement == "lead" for story in stories) != 1:
        raise IssueError("Issue Story Desk must contain exactly one lead")
    if sum(story.placement == "brief" for story in stories) > 4:
        raise IssueError("Issue Story Desk may contain no more than four briefs")
    return tuple(stories)


def parse_reality_links(synthesis: str) -> dict[str, tuple[str, ...]]:
    section = extract_section(synthesis, "Reality Claim Handoff")
    rows = first_table_with(section, {"Story ID", "Reality Claim IDs"})
    return {clean_cell(row["Story ID"]): split_list(row["Reality Claim IDs"], LATTICE_ID_RE) for row in rows}


def parse_issue_copy(daily_brief: str) -> dict[str, str]:
    section = extract_section(daily_brief, "Issue Copy")
    if not section:
        raise IssueError("daily-brief.md is missing Issue Copy")
    matches = list(re.finditer(r"^###\s+(NGI-\d{8}-S\d{2})\s+[—-]\s+.+$", section, re.MULTILINE))
    copy: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        copy[match.group(1)] = section[match.end():end].strip()
    return copy


def parse_source_rows(sources: str) -> dict[str, dict[str, str]]:
    for section_name in ("Run Source Set", "Intake Batch"):
        section = extract_section(sources, section_name)
        for rows in markdown_tables(section):
            mapped: dict[str, dict[str, str]] = {}
            for row in rows:
                source_id = next(iter(SOURCE_ID_RE.findall(row.get("Source ID", "") or row.get("ID", ""))), "")
                if source_id:
                    mapped[source_id] = row
            if mapped:
                return mapped
    raise IssueError("sources.md has no source-ID table")


def parse_voice_rows(synthesis: str) -> list[dict[str, str]]:
    section = extract_section(synthesis, "Primary Voices")
    rows = first_table_with(section, {"Voice"})
    if not rows:
        raise IssueError("synthesis.md has no Primary Voices table")
    return rows


def parse_claim_rows(synthesis: str) -> dict[str, dict[str, str]]:
    section = extract_section(synthesis, "Operational Claim Triage")
    mapped: dict[str, dict[str, str]] = {}
    for rows in markdown_tables(section):
        for row in rows:
            claim_id = next(iter(CLAIM_ID_RE.findall(row.get("Claim ID", ""))), "")
            if claim_id:
                mapped[claim_id] = row
    return mapped


def parse_ledger(ledger_text: str) -> dict[str, dict[str, str]]:
    rows = first_table_with(ledger_text, {"Hook ID", "Probability Band", "Review Date", "Claim"})
    return {match.group(0): row for row in rows if (match := HOOK_ID_RE.search(row["Hook ID"]))}


def parse_forecast_detail(hook_id: str, daily_root: Path = DAILY_ROOT) -> dict[str, str]:
    match = re.fullmatch(r"NG-(\d{4})(\d{2})(\d{2})-F\d{2}", hook_id)
    if not match:
        return {}
    path = daily_root / f"{match.group(1)}-{match.group(2)}-{match.group(3)}" / "forecast.md"
    if not path.exists():
        return {}
    for rows in markdown_tables(path.read_text(encoding="utf-8")):
        for row in rows:
            if hook_id in row.get("Hook ID", ""):
                return row
    return {}


def parse_forecasts(stories: tuple[Story, ...], ledger_text: str, daily_root: Path = DAILY_ROOT) -> dict[str, dict[str, str]]:
    ledger = parse_ledger(ledger_text)
    output: dict[str, dict[str, str]] = {}
    for hook_id in dict.fromkeys(hook for story in stories if story.placement != "hold" for hook in story.forecast_hooks):
        if hook_id not in ledger and hook_id not in ledger_text:
            continue
        detail = parse_forecast_detail(hook_id, daily_root)
        ledger_row = ledger.get(hook_id, {})
        output[hook_id] = {
            "Claim": clean_cell(detail.get("Claim", detail.get("Observable claim", ledger_row.get("Claim", "")))),
            "Probability Band": clean_cell(detail.get("Probability Band", ledger_row.get("Probability Band", ""))),
            "Review Date": clean_cell(detail.get("Review Date", ledger_row.get("Review Date", ""))),
            "Strengthening Evidence": clean_cell(detail.get("Strengthening Evidence", detail.get("Strengthening evidence", "See the canonical forecast review."))),
            "Weakening Evidence": clean_cell(detail.get("Weakening Evidence", detail.get("Weakening evidence", "See the canonical forecast review."))),
        }
    return output


def validate_revision_log(text: str) -> None:
    if text.strip() == "No revisions.":
        return
    rows = first_table_with(text, {"Timestamp (UTC)", "Type", "Note"})
    if not rows:
        raise IssueError("Revision Log must contain 'No revisions.' or the UTC revision table")
    for row in rows:
        timestamp = clean_cell(row["Timestamp (UTC)"])
        revision_type = clean_cell(row["Type"])
        note = clean_cell(row["Note"])
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", timestamp):
            raise IssueError(f"Revision Log has invalid UTC timestamp: {timestamp}")
        if revision_type not in {"correction", "update"}:
            raise IssueError(f"Revision Log has invalid type: {revision_type}")
        if len(note.split()) < 3:
            raise IssueError("Revision Log note is too thin to audit")


def title_and_rationale(daily_brief: str, lead: Story) -> tuple[str, str]:
    match = H1_RE.search(daily_brief)
    title = match.group(1).strip() if match else lead.headline
    rationale_match = re.search(r"^Title rationale:\s*`?(.+?)`?\s*$", daily_brief, re.MULTILINE)
    rationale = clean_cell(rationale_match.group(1)) if rationale_match else f"Names the lead issue argument while preserving its {lead.evidence_posture} evidence boundary."
    return title, rationale


def load_model(
    run_date: str,
    daily_root: Path = DAILY_ROOT,
    ledger_path: Path = LEDGER_PATH,
    packets_root: Path = verification.PACKETS_ROOT,
    *,
    context: IssueValidationContext | None = None,
) -> IssueModel:
    inputs = canonical_inputs(run_date, daily_root)
    stories = parse_stories(run_date, inputs["synthesis.md"])
    reality_links = parse_reality_links(inputs["synthesis.md"])
    stories = tuple(Story(**{**story.__dict__, "reality_claims": reality_links.get(story.story_id, story.reality_claims)}) for story in stories)
    copy = parse_issue_copy(inputs["daily-brief.md"])
    selected_ids = {story.story_id for story in stories if story.placement != "hold"}
    if set(copy) != selected_ids:
        missing = sorted(selected_ids - set(copy))
        extra = sorted(set(copy) - selected_ids)
        raise IssueError(f"Issue Copy mismatch; missing={missing or 'none'} extra={extra or 'none'}")
    if any(PLACEHOLDER_RE.search(text) for text in inputs.values()):
        raise IssueError("canonical daily inputs still contain issue-blocking placeholder text")
    lead = next(story for story in stories if story.placement == "lead")
    title, rationale = title_and_rationale(inputs["daily-brief.md"], lead)
    missing_observables = extract_section(inputs["sources.md"], "Missing Observables") or extract_section(inputs["synthesis.md"], "Uncertainty with Causes")
    revision_log = extract_section(inputs["daily-brief.md"], "Revision Log")
    if not revision_log:
        raise IssueError("daily-brief.md is missing Revision Log")
    validate_revision_log(revision_log)
    ledger_text = (
        context.ledger_text
        if context is not None
        else ledger_path.read_text(encoding="utf-8")
    )
    claim_rows = parse_claim_rows(inputs["synthesis.md"])
    verification_links: dict[str, str] = {}
    issue_dir = daily_root / run_date
    for row in claim_rows.values():
        packet_id = clean_cell(row.get("Verification", ""))
        if not VER_ID_RE.fullmatch(packet_id):
            continue
        packet_path = verification.find_packet(packet_id, packets_root)
        if packet_path:
            relative = os.path.relpath(packet_path, issue_dir).replace("\\", "/")
            verification_links[packet_id] = f"[{packet_id}]({relative})"
    selected_claims = {claim_id for story in stories if story.placement != "hold" for claim_id in story.operational_claims}
    selected_hooks = {hook_id for story in stories if story.placement != "hold" for hook_id in story.forecast_hooks}
    return IssueModel(
        run_date=run_date,
        title=title,
        title_rationale=rationale,
        stories=stories,
        copy=copy,
        source_rows=parse_source_rows(inputs["sources.md"]),
        voice_rows=parse_voice_rows(inputs["synthesis.md"]),
        claim_rows=claim_rows,
        verification_links=verification_links,
        forecast_rows=parse_forecasts(stories, ledger_text, daily_root),
        day_hook_ids=frozenset(HOOK_ID_RE.findall(inputs["forecast.md"])),
        missing_observables=missing_observables or "No additional missing observables were recorded.",
        revision_log=revision_log,
        input_digest=input_digest(inputs),
        reality_digest=reality.subgraph_digest(
            selected_claims | selected_hooks,
            records=context.reality_records if context is not None else None,
        ),
    )


def render_story(story: Story, body: str) -> str:
    related = ", ".join(f"`{claim_id}`" for claim_id in story.reality_claims) or "None registered"
    return f"### {story.headline}\n\nEvidence posture: `{story.evidence_posture}`\n\nCrisis object: {story.crisis_object}\n\nRelated reality claims: {related}\n\n{body.strip()}"


def source_display(row: dict[str, str]) -> tuple[str, str, str]:
    voice = clean_cell(row.get("Voice", row.get("Voice(s)", ""))) or "Unassigned"
    source = row.get("Archive Path", row.get("Source", row.get("Manifest path", "")))
    job = row.get("Analytical job", row.get("Why It Matters", row.get("Notes", "")))
    return voice, source, job


def render_model(
    model: IssueModel,
    template_text: str | None = None,
    *,
    context: IssueValidationContext | None = None,
) -> str:
    template = template_text if template_text is not None else TEMPLATE_PATH.read_text(encoding="utf-8")
    selected = [story for story in model.stories if story.placement != "hold"]
    lead = next(story for story in selected if story.placement == "lead")
    briefs = [story for story in selected if story.placement == "brief"]
    held = [story for story in model.stories if story.placement == "hold"]

    index_rows = ["| Desk | Story | Evidence posture |", "| --- | --- | --- |"]
    for story in selected:
        desk = "Main Analysis" if story.placement == "lead" else "Briefing Desk"
        index_rows.append(f"| {desk} | {story.headline} | `{story.evidence_posture}` |")
    front = f"{model.copy[lead.story_id].split(chr(10) + chr(10), 1)[0]}\n\n" + "\n".join(index_rows)
    briefing = "\n\n".join(render_story(story, model.copy[story.story_id]) for story in briefs) or "No secondary brief met the issue threshold for this archive day."
    main = render_story(lead, model.copy[lead.story_id])

    source_ids = list(dict.fromkeys(source_id for story in selected for source_id in story.source_ids))
    source_lines = ["Only sources used by selected issue stories appear here. See the [complete canonical source accounting](sources.md).", "", "| Source ID | Voice | Archive source | Analytical job |", "| --- | --- | --- | --- |"]
    for source_id in source_ids:
        row = model.source_rows[source_id]
        voice, source, job = source_display(row)
        source_lines.append(f"| `{source_id}` | {voice} | {source} | {job} |")

    forecast_lines = ["Forecasts remain accountable to the [canonical daily review](forecast.md) and [central ledger](../../forecasts/forecast-ledger.md)."]
    if model.forecast_rows:
        forecast_lines += ["", "| Hook | Observable claim | Band | Review date | Strengthening test | Weakening test |", "| --- | --- | --- | --- | --- | --- |"]
        for hook_id, row in model.forecast_rows.items():
            forecast_lines.append(f"| `{hook_id}` | {row['Claim']} | `{row['Probability Band']}` | `{row['Review Date']}` | {row['Strengthening Evidence']} | {row['Weakening Evidence']} |")
    else:
        forecast_lines += ["", "No selected story carries a forecast hook."]

    claim_ids = list(dict.fromkeys(claim_id for story in selected for claim_id in story.operational_claims))
    verification_lines = ["Operational claims remain attributed unless canonical multilingual adjudication supports factual adoption."]
    if claim_ids:
        verification_lines += ["", "| Claim | Bounded operational claim | Status | Lattice state | Consequence if false | Verification |", "| --- | --- | --- | --- | --- | --- |"]
        for claim_id in claim_ids:
            row = model.claim_rows[claim_id]
            raw_verification = clean_cell(row.get("Verification", ""))
            verification_display = model.verification_links.get(raw_verification, row.get("Verification", ""))
            state = reality.claim_state(
                claim_id,
                records=context.reality_records if context is not None else None,
            )
            assessment = state.get("assessment") if state else None
            lattice_display = f"`{assessment.get('status')}: {assessment.get('outcome')}`" if assessment else ("`migrated: unassessed`" if state else "`legacy`")
            verification_lines.append(f"| `{claim_id}` | {row.get('Operational claim', '')} | {row.get('Current status', '')} | {lattice_display} | {row.get('Consequence if false', '')} | {verification_display} |")
    verification_lines += ["", "### Missing observables", "", model.missing_observables]

    voice_names = list(dict.fromkeys(voice for story in selected for voice in story.voices))
    voice_lines = ["Names identify source-bounded pressure tests, not endorsement or reconstructed present opinion.", "", "| Voice | Analytical operation | Contribution | Main risk |", "| --- | --- | --- | --- |"]
    for voice in voice_names:
        row = next(row for row in model.voice_rows if voice.lower() in clean_cell(row.get("Voice", "")).lower())
        voice_lines.append(f"| {voice} | {row.get('Intellectual operation', row.get('Role In This Run', ''))} | {row.get('What it adds', row.get('What It Adds', ''))} | {row.get('Main risk', row.get('Main Risk', ''))} |")

    note_lines = ["This issue selects stories by declared analytical consequence, not by source volume."]
    for story in selected:
        note_lines.append(f"- **{story.headline}:** {story.selection_rationale}")
    if held:
        note_lines += ["", "Held from this issue:"]
        note_lines.extend(f"- **{story.headline}:** {story.selection_rationale}" for story in held)
    if len(selected) < 3:
        note_lines += ["", "This is intentionally a thin issue: fewer than three story objects cleared the selection threshold."]
    note_lines += ["", "Canonical inputs: [sources](sources.md), [synthesis](synthesis.md), [forecast](forecast.md), and [daily brief](daily-brief.md).", "", "### Revision Log", "", model.revision_log]

    replacements = {
        "{{INPUT_DIGEST}}": model.input_digest,
        "{{REALITY_DIGEST}}": model.reality_digest,
        "{{ISSUE_TITLE}}": model.title,
        "{{TITLE_RATIONALE}}": model.title_rationale,
        "{{RUN_DATE}}": model.run_date,
        "{{FRONT_PAGE}}": front,
        "{{BRIEFING_DESK}}": briefing,
        "{{MAIN_ANALYSIS}}": main,
        "{{SOURCE_LEDGER}}": "\n".join(source_lines),
        "{{FORECAST_DESK}}": "\n".join(forecast_lines),
        "{{VERIFICATION_DESK}}": "\n".join(verification_lines),
        "{{VOICES_COLUMNS}}": "\n".join(voice_lines),
        "{{EDITORS_NOTE}}": "\n".join(note_lines),
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    return template.rstrip() + "\n"


def model_failures(
    model: IssueModel,
    ledger_text: str,
    daily_root: Path = DAILY_ROOT,
    packets_root: Path = verification.PACKETS_ROOT,
    *,
    context: IssueValidationContext | None = None,
) -> list[str]:
    failures: list[str] = []
    selected = [story for story in model.stories if story.placement != "hold"]
    for story in selected:
        for source_id in story.source_ids:
            if source_id not in model.source_rows:
                failures.append(f"{story.story_id}: unknown source ID {source_id}")
        for voice in story.voices:
            if not any(voice.lower() in clean_cell(row.get("Voice", "")).lower() for row in model.voice_rows):
                failures.append(f"{story.story_id}: unknown primary voice {voice}")
        for hook_id in story.forecast_hooks:
            if hook_id not in model.day_hook_ids:
                failures.append(f"{story.story_id}: forecast hook missing from the day's forecast.md {hook_id}")
            if hook_id not in model.forecast_rows:
                failures.append(f"{story.story_id}: forecast hook missing detail or ledger row {hook_id}")
            if hook_id not in ledger_text:
                failures.append(f"{story.story_id}: forecast hook missing central ledger row {hook_id}")
        for claim_id in story.operational_claims:
            if claim_id not in model.claim_rows:
                failures.append(f"{story.story_id}: unknown operational claim {claim_id}")
                continue
            verification_id = clean_cell(model.claim_rows[claim_id].get("Verification", ""))
            if VER_ID_RE.fullmatch(verification_id) and verification.find_packet(verification_id, packets_root) is None:
                failures.append(f"{story.story_id}: verification packet not found {verification_id}")
            if clean_cell(model.claim_rows[claim_id].get("Current status", "")) == "operationally_supported":
                lattice = reality.claim_state(
                    claim_id,
                    records=context.reality_records if context is not None else None,
                )
                lattice_assessment = lattice.get("assessment") if lattice else None
                if lattice and not (
                    lattice_assessment
                    and lattice_assessment.get("outcome") == "supported"
                    and lattice_assessment.get("status") in {"canonical_assessed", "canonical_with_language_waiver"}
                ):
                    failures.append(f"{story.story_id}: migrated claim lacks canonical multilingual lattice support")
                packet_path = verification.find_packet(verification_id, packets_root) if VER_ID_RE.fullmatch(verification_id) else None
                if packet_path is None:
                    failures.append(f"{story.story_id}: operationally_supported claim lacks a verification packet")
                else:
                    packet = verification.parse_packet(packet_path)
                    if packet.fields.get("status") not in {"assessed", "closed"} or packet.fields.get("assessment_outcome") != "operationally_supported":
                        failures.append(f"{story.story_id}: operationally_supported claim lacks an assessed supporting outcome")
        if story.evidence_posture == "verification-supported":
            if not story.operational_claims:
                failures.append(f"{story.story_id}: verification-supported requires an operational claim")
            for claim_id in story.operational_claims:
                row = model.claim_rows.get(claim_id, {})
                verification_id = clean_cell(row.get("Verification", ""))
                if not VER_ID_RE.fullmatch(verification_id) or clean_cell(row.get("Current status", "")) != "operationally_supported":
                    failures.append(f"{story.story_id}: verification-supported lacks a supported VER-backed claim")
                    continue
                packet_path = verification.find_packet(verification_id, packets_root)
                if packet_path is None:
                    failures.append(f"{story.story_id}: verification-supported packet not found {verification_id}")
                    continue
                packet = verification.parse_packet(packet_path)
                if packet.fields.get("status") not in {"assessed", "closed"} or packet.fields.get("assessment_outcome") != "operationally_supported":
                    failures.append(f"{story.story_id}: verification-supported packet does not operationally support the claim")
                lattice = reality.claim_state(
                    claim_id,
                    records=context.reality_records if context is not None else None,
                )
                lattice_assessment = lattice.get("assessment") if lattice else None
                if lattice and not (
                    lattice_assessment
                    and lattice_assessment.get("outcome") == "supported"
                    and lattice_assessment.get("status") in {"canonical_assessed", "canonical_with_language_waiver"}
                ):
                    failures.append(f"{story.story_id}: verification-supported claim lacks canonical multilingual lattice support")
    for source_id in {source_id for story in selected for source_id in story.source_ids}:
        row = model.source_rows.get(source_id, {})
        link_text = " ".join(row.values())
        links = LINK_RE.findall(link_text)
        if not links:
            failures.append(f"{source_id}: selected source has no archive link")
        for _, target in links:
            if target.startswith("../../../../archive/geopolitics/sources/"):
                resolved = (daily_root / model.run_date / target).resolve()
                manifest_path = daily_root.parents[2] / "archive" / "geopolitics" / "source-manifest.json"
                if context is not None:
                    manifest_paths = context.manifest_paths
                elif manifest_path.exists():
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
                    manifest_paths = frozenset(
                        str(item.get("local_path", ""))
                        for item in manifest.get("sources", [])
                    )
                else:
                    manifest_paths = frozenset()
                if context is not None or manifest_path.exists():
                    repo_root = daily_root.parents[2]
                    local_path = resolved.relative_to(repo_root).as_posix()
                    if local_path not in manifest_paths:
                        if not resolved.exists():
                            failures.append(f"{source_id}: archive link does not resolve {target}")
                        else:
                            failures.append(f"{source_id}: archive link has no manifest row {local_path}")
                elif not resolved.exists():
                    failures.append(f"{source_id}: archive link does not resolve {target}")
    return failures


def validate_issue(
    run_date: str,
    require: bool = False,
    daily_root: Path = DAILY_ROOT,
    ledger_path: Path = LEDGER_PATH,
    *,
    context: IssueValidationContext | None = None,
) -> tuple[list[str], list[str]]:
    issue_path = daily_root / run_date / "issue.md"
    if not issue_path.exists():
        return (["missing issue.md"] if require else []), []
    failures: list[str] = []
    warnings: list[str] = []
    try:
        model = load_model(run_date, daily_root, ledger_path, context=context)
        expected = render_model(model, context=context)
    except (IssueError, KeyError, StopIteration) as exc:
        return [str(exc)], []
    actual = issue_path.read_text(encoding="utf-8")
    headings = [name for level, name in HEADING_RE.findall(actual) if level == "##"]
    if tuple(headings) != REQUIRED_ISSUE_SECTIONS:
        failures.append(f"issue.md required sections/order mismatch: {headings}")
    if PLACEHOLDER_RE.search(actual):
        failures.append("issue.md contains placeholder text")
    digest_match = re.search(r"daily-issue-v1 inputs-sha256: ([0-9a-f]{64})", actual)
    if not digest_match or digest_match.group(1) != model.input_digest:
        failures.append("issue.md input digest is missing or stale")
    if actual != expected:
        failures.append("issue.md is not the current deterministic rendering")
    if "`operationally_supported`" in actual:
        supported = [
            row for row in model.claim_rows.values()
            if clean_cell(row.get("Current status", "")) == "operationally_supported"
        ]
        if not supported:
            failures.append("issue.md uses operationally_supported without a supported operational claim")
    for packet_id, raw_target in re.findall(r"\[(VER-\d{8}-\d{2})\]\(([^)]+)\)", actual):
        target = (daily_root / run_date / raw_target).resolve()
        if not target.exists():
            failures.append(f"issue.md verification link does not resolve: {packet_id} -> {raw_target}")
    ledger_text = (
        context.ledger_text
        if context is not None
        else ledger_path.read_text(encoding="utf-8")
    )
    failures.extend(model_failures(model, ledger_text, daily_root, context=context))
    prose = re.sub(r"(?m)^\|.*$|`[^`]+`|\[[^\]]+\]\([^)]+\)|<!--.*?-->", " ", actual)
    words = re.findall(r"\b[\w’'-]+\b", prose)
    if not 1500 <= len(words) <= 2500:
        warnings.append(f"issue.md editorial prose word count outside 1500-2500 target: {len(words)}")
    return failures, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a deterministic Narrative Geopolitics daily issue.")
    parser.add_argument("--date", required=True, help="Run date in YYYY-MM-DD format.")
    parser.add_argument("--check", action="store_true", help="Check that issue.md is current without writing.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing stale issue.md.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    issue_path = DAILY_ROOT / args.date / "issue.md"
    model = load_model(args.date, DAILY_ROOT, LEDGER_PATH)
    failures = model_failures(model, LEDGER_PATH.read_text(encoding="utf-8"), DAILY_ROOT)
    if failures:
        for item in failures:
            print(f"FAIL {item}")
        raise SystemExit(1)
    rendered = render_model(model)
    if args.check:
        if not issue_path.exists() or issue_path.read_text(encoding="utf-8") != rendered:
            print(f"FAIL stale or missing issue: {display_path(issue_path)}")
            raise SystemExit(1)
        print(f"issue_current={display_path(issue_path)}")
        return
    if issue_path.exists() and not args.force:
        if issue_path.read_text(encoding="utf-8") == rendered:
            print(f"issue_current={display_path(issue_path)}")
            return
        raise SystemExit(f"Refusing to overwrite stale issue without --force: {display_path(issue_path)}")
    issue_path.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"issue_written={display_path(issue_path)}")


if __name__ == "__main__":
    main()

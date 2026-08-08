from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
REGISTRY_ROOT = NG_ROOT / "work" / "voice-judgments"
REGISTRY_PATH = REGISTRY_ROOT / "external-voice-judgment-ledger.json"
VOICES_ROOT = NG_ROOT / "voices"
REVISION_PATH = NG_ROOT / "work" / "voice-accountability" / "voice-revision-ledger.json"
REALITY_ROOT = NG_ROOT / "work" / "reality"
FORECAST_LEDGER = NG_ROOT / "work" / "forecasts" / "forecast-ledger.md"

SCHEMA = "external-voice-judgment-ledger-v1"
BOUNDARY = (
    "Archive sources establish what a voice said. This registry organizes expressed "
    "judgments but is never evidence that an underlying world claim is true. Reality "
    "outcomes and formal forecast results are displayed only by governed reference."
)
JUDGMENT_CLASSES = {"position", "mechanism", "forecast_expression", "strategic_assessment"}
LIFECYCLES = {"active", "superseded", "unclear"}
EXPRESSION_TYPES = {"explicit", "close-paraphrase"}
JUDGMENT_ID_RE = re.compile(r"VJ-[A-Z0-9-]+-\d{4}$")
VERSION_ID_RE = re.compile(r"(VJ-[A-Z0-9-]+-\d{4})-v(\d+)$")
LEGACY_ID_RE = re.compile(r"STATE-[A-Z0-9-]+-\d{4}$")
REALITY_ID_RE = re.compile(r"(?:CLM-\d{8}-\d{3}|OPC-\d{8}-\d{2}|NG-\d{8}-F\d{2})$")
REVISION_ID_RE = re.compile(r"VR-\d{8}-\d{2}$")
FORMAL_FORECAST_RE = re.compile(r"NG-\d{8}-F\d{2}$")

MIGRATION_CLASSES = {
    "STATE-CROOKE-0001": "mechanism",
    "STATE-DAVIS-0001": "strategic_assessment",
    "STATE-DIESEN-0001": "strategic_assessment",
    "STATE-JOHNSON-0001": "strategic_assessment",
    "STATE-MARANDI-0001": "position",
    "STATE-MEARSHEIMER-0001": "mechanism",
    "STATE-MERCOURIS-0001": "strategic_assessment",
    "STATE-PAPE-0001": "mechanism",
}


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    return load_json(path)


def load_revisions(path: Path = REVISION_PATH) -> dict[str, Any]:
    return load_json(path)


def formal_forecast_ids(path: Path = FORECAST_LEDGER) -> set[str]:
    if not path.exists():
        return set()
    return set(re.findall(r"NG-\d{8}-F\d{2}", path.read_text(encoding="utf-8")))


def reality_claims(root: Path = REALITY_ROOT) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "claims").glob("*.json")):
        record = load_json(path)
        result[str(record.get("id"))] = record
    return result


def reality_assessments(root: Path = REALITY_ROOT) -> dict[str, dict[str, Any]]:
    by_claim: dict[str, list[dict[str, Any]]] = {}
    for path in sorted((root / "assessments").glob("*.json")):
        record = load_json(path)
        by_claim.setdefault(str(record.get("claim_id")), []).append(record)
    result: dict[str, dict[str, Any]] = {}
    for claim_id, records in by_claim.items():
        result[claim_id] = sorted(
            records,
            key=lambda item: (str(item.get("created_at", "")), str(item.get("id", ""))),
        )[-1]
    return result


def all_revision_entries(path: Path = REVISION_PATH) -> list[dict[str, Any]]:
    return list(load_revisions(path).get("entries", []))


def judgment_index(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("id")): item for item in registry.get("judgments", [])}


def validate_registry(
    registry: dict[str, Any] | None = None,
    *,
    repo_root: Path = REPO_ROOT,
    revision_path: Path = REVISION_PATH,
    reality_root: Path = REALITY_ROOT,
    forecast_path: Path = FORECAST_LEDGER,
) -> list[str]:
    failures: list[str] = []
    if registry is None:
        if not REGISTRY_PATH.exists():
            return [f"voice judgment registry missing: {relative(REGISTRY_PATH)}"]
        try:
            registry = load_registry()
        except (OSError, json.JSONDecodeError) as error:
            return [f"voice judgment registry unreadable: {error}"]

    if registry.get("schema") != SCHEMA:
        failures.append("voice judgment registry: invalid schema")
    if registry.get("status") != "internal-canonical":
        failures.append("voice judgment registry: invalid status")
    if registry.get("authority_boundary") != BOUNDARY:
        failures.append("voice judgment registry: authority boundary drift")
    if registry.get("revision_ledger_ref") != relative(REVISION_PATH):
        failures.append("voice judgment registry: revision authority reference drift")
    judgments = registry.get("judgments")
    if not isinstance(judgments, list):
        return failures + ["voice judgment registry: judgments must be a list"]

    try:
        revisions = all_revision_entries(revision_path)
    except (OSError, json.JSONDecodeError) as error:
        return failures + [f"voice judgment registry: revision authority unreadable: {error}"]
    revision_by_id = {str(item.get("id")): item for item in revisions}
    claims = reality_claims(reality_root)
    forecast_ids = formal_forecast_ids(forecast_path)

    seen_ids: set[str] = set()
    seen_versions: set[str] = set()
    seen_aliases: set[str] = set()
    for index, judgment in enumerate(judgments, start=1):
        label = str(judgment.get("id", f"entry-{index}"))
        if not JUDGMENT_ID_RE.fullmatch(label):
            failures.append(f"{label}: invalid judgment ID")
        if label in seen_ids:
            failures.append(f"{label}: duplicate judgment ID")
        seen_ids.add(label)
        voice = judgment.get("voice_slug")
        if not isinstance(voice, str) or not (repo_root / "narrative-geopolitics" / "voices" / voice).is_dir():
            failures.append(f"{label}: voice directory does not resolve: {voice}")
        if judgment.get("class") not in JUDGMENT_CLASSES:
            failures.append(f"{label}: invalid judgment class {judgment.get('class')}")
        if judgment.get("lifecycle") not in LIFECYCLES:
            failures.append(f"{label}: invalid lifecycle {judgment.get('lifecycle')}")
        for forbidden in ("outcome", "assessment_status", "reality_outcome", "forecast_score"):
            if forbidden in judgment:
                failures.append(f"{label}: forbidden copied authority field {forbidden}")

        aliases = judgment.get("legacy_ids", [])
        if not isinstance(aliases, list):
            failures.append(f"{label}: legacy_ids must be a list")
            aliases = []
        for alias in aliases:
            if not isinstance(alias, str) or not LEGACY_ID_RE.fullmatch(alias):
                failures.append(f"{label}: malformed legacy alias {alias}")
            elif alias in seen_aliases:
                failures.append(f"{label}: duplicate legacy alias {alias}")
            seen_aliases.add(str(alias))

        versions = judgment.get("versions")
        if not isinstance(versions, list) or not versions:
            failures.append(f"{label}: versions must be a non-empty list")
            continue
        expected_versions = list(range(1, len(versions) + 1))
        actual_versions: list[int] = []
        previous_last = ""
        for version in versions:
            version_id = str(version.get("id", ""))
            match = VERSION_ID_RE.fullmatch(version_id)
            if not match or match.group(1) != label:
                failures.append(f"{label}: invalid version ID {version_id}")
                continue
            number = int(match.group(2))
            actual_versions.append(number)
            if version_id in seen_versions:
                failures.append(f"{version_id}: duplicate version ID")
            seen_versions.add(version_id)
            if version.get("expression_type") not in EXPRESSION_TYPES:
                failures.append(f"{version_id}: invalid expression_type {version.get('expression_type')}")
            for field in ("proposition", "first_seen", "last_seen", "review_condition"):
                if not isinstance(version.get(field), str) or not version.get(field):
                    failures.append(f"{version_id}: missing {field}")
            first_seen = str(version.get("first_seen", ""))
            last_seen = str(version.get("last_seen", ""))
            try:
                first_date = date.fromisoformat(first_seen)
                last_date = date.fromisoformat(last_seen)
                if first_date > last_date:
                    failures.append(f"{version_id}: first_seen is after last_seen")
                if previous_last and first_seen < previous_last:
                    failures.append(f"{version_id}: version chronology overlaps its predecessor")
                previous_last = last_seen
            except ValueError:
                failures.append(f"{version_id}: invalid date")
            for forbidden in ("outcome", "assessment_status", "reality_outcome", "forecast_score"):
                if forbidden in version:
                    failures.append(f"{version_id}: forbidden copied authority field {forbidden}")

            sources = version.get("source_refs", [])
            if not isinstance(sources, list) or not sources:
                failures.append(f"{version_id}: source_refs must be a non-empty list")
                sources = []
            for source in sources:
                if not isinstance(source, str) or not source.startswith("narrative-geopolitics/archive/sources/"):
                    failures.append(f"{version_id}: source is not a canonical archive path: {source}")
                elif "SRC-" in source or not (repo_root / source).is_file():
                    failures.append(f"{version_id}: source path does not resolve: {source}")

            daily_refs = version.get("daily_refs", [])
            if not isinstance(daily_refs, list):
                failures.append(f"{version_id}: daily_refs must be a list")
                daily_refs = []
            for daily_ref in daily_refs:
                if not isinstance(daily_ref, str) or not daily_ref.startswith("narrative-geopolitics/work/daily/"):
                    failures.append(f"{version_id}: invalid daily reference {daily_ref}")
                elif not (repo_root / daily_ref).is_file():
                    failures.append(f"{version_id}: daily reference does not resolve: {daily_ref}")

            for forecast_id in version.get("formal_forecast_refs", []):
                if not isinstance(forecast_id, str) or not FORMAL_FORECAST_RE.fullmatch(forecast_id):
                    failures.append(f"{version_id}: invalid formal forecast reference {forecast_id}")
                elif forecast_id not in forecast_ids:
                    failures.append(f"{version_id}: formal forecast reference does not resolve: {forecast_id}")
            for forecast_id in version.get("unresolved_forecast_refs", []):
                if forecast_id in forecast_ids:
                    failures.append(f"{version_id}: resolved forecast remains in unresolved references: {forecast_id}")
            for claim_id in version.get("reality_claim_refs", []):
                if not isinstance(claim_id, str) or not REALITY_ID_RE.fullmatch(claim_id):
                    failures.append(f"{version_id}: invalid Reality reference {claim_id}")
                elif claim_id not in claims:
                    failures.append(f"{version_id}: Reality reference does not resolve: {claim_id}")
            for revision_id in version.get("revision_refs", []):
                revision = revision_by_id.get(str(revision_id))
                if not revision:
                    failures.append(f"{version_id}: revision reference does not resolve: {revision_id}")
                elif revision.get("voice_slug") != voice:
                    failures.append(f"{version_id}: revision reference belongs to another voice: {revision_id}")
        if actual_versions != expected_versions:
            failures.append(f"{label}: versions must be contiguous from v1")

    for revision in revisions:
        refs = revision.get("judgment_refs", [])
        if not isinstance(refs, list):
            failures.append(f"{revision.get('id')}: judgment_refs must be a list")
            continue
        for ref in refs:
            judgment = judgment_index(registry).get(str(ref))
            if judgment is None:
                failures.append(f"{revision.get('id')}: judgment reference does not resolve: {ref}")
            elif judgment.get("voice_slug") != revision.get("voice_slug"):
                failures.append(f"{revision.get('id')}: judgment reference belongs to another voice: {ref}")
    return failures


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def clean_cell(value: str) -> str:
    return value.strip().strip("`").strip()


def daterange(start: str, end: str) -> list[str]:
    first = date.fromisoformat(start)
    last = date.fromisoformat(end)
    result: list[str] = []
    current = first
    while current <= last:
        result.append(current.isoformat())
        current += timedelta(days=1)
    return result


def daily_source_map(day: str) -> dict[str, tuple[str, str]]:
    path = NG_ROOT / "work" / "daily" / day / "sources.md"
    if not path.exists():
        return {}
    result: dict[str, tuple[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `SRC-"):
            continue
        cells = split_row(line)
        if len(cells) < 5:
            continue
        source_id = clean_cell(cells[0])
        voice = cells[1].strip().lower().replace(" ", "-")
        match = re.search(r"\(([^)]+archive/sources/[^)]+)\)", cells[4])
        if not match:
            continue
        target = match.group(1).replace("\\", "/")
        marker = "archive/sources/"
        archive_path = "narrative-geopolitics/" + target[target.index(marker) :]
        result[source_id] = (voice, archive_path)
    return result


def voice_matches(slug: str, displayed: str) -> bool:
    aliases = {
        "crooke": {"crooke", "alastair-crooke"},
        "davis": {"davis", "daniel-davis"},
        "diesen": {"diesen", "glenn-diesen"},
        "johnson": {"johnson", "larry-johnson"},
        "marandi": {"marandi", "seyed-mohammad-marandi", "seyed-m-marandi"},
        "mearsheimer": {"mearsheimer", "john-mearsheimer"},
        "mercouris": {"mercouris", "alexander-mercouris"},
        "pape": {"pape", "robert-pape"},
    }
    return displayed in aliases.get(slug, {slug})


def parse_legacy_state(path: Path) -> dict[str, Any]:
    slug = path.parent.name
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("| `STATE-")]
    if len(rows) != 1:
        raise ValueError(f"{relative(path)}: expected one active state row, found {len(rows)}")
    cells = split_row(rows[0])
    if len(cells) != 10:
        raise ValueError(f"{relative(path)}: expected ten state columns, found {len(cells)}")
    legacy_id = clean_cell(cells[0])
    proposition = cells[1]
    lifecycle = clean_cell(cells[2])
    first_seen = clean_cell(cells[3])
    last_seen = clean_cell(cells[4])
    expression_type = clean_cell(cells[5])
    source_ids = [clean_cell(value) for value in clean_cell(cells[6]).split(",") if clean_cell(value)]
    daily_matches = re.findall(r"\[(\d{4}-\d{2}-\d{2})\]\(([^)]+)\)", cells[7])
    daily_refs = [f"narrative-geopolitics/work/daily/{day}/synthesis.md" for day, _ in daily_matches]
    forecast_value = clean_cell(cells[8])
    note = cells[9]

    resolved_sources: list[str] = []
    migration_warnings: list[str] = []
    for source_id in source_ids:
        matches: list[str] = []
        for day in daterange(first_seen, last_seen):
            row = daily_source_map(day).get(source_id)
            if row and voice_matches(slug, row[0]):
                matches.append(row[1])
        if not matches:
            migration_warnings.append(
                "A legacy day-local source reference did not resolve to this voice and was excluded."
            )
            continue
        resolved_sources.extend(matches)
    resolved_sources = sorted(set(resolved_sources))
    if not resolved_sources:
        raise ValueError(f"{legacy_id}: no canonical archive source could be resolved")

    formal_ids = formal_forecast_ids()
    forecast_refs = [] if forecast_value.lower() == "none" else [forecast_value]
    formal_refs = [item for item in forecast_refs if item in formal_ids]
    unresolved_refs = [item for item in forecast_refs if item not in formal_ids]
    judgment_id = legacy_id.replace("STATE-", "VJ-")
    return {
        "id": judgment_id,
        "voice_slug": slug,
        "class": MIGRATION_CLASSES[legacy_id],
        "lifecycle": "active" if lifecycle in {"new", "persistent"} else "unclear",
        "legacy_ids": [legacy_id],
        "versions": [
            {
                "id": f"{judgment_id}-v1",
                "proposition": proposition,
                "expression_type": expression_type,
                "first_seen": first_seen,
                "last_seen": last_seen,
                "source_refs": resolved_sources,
                "daily_refs": sorted(set(daily_refs)),
                "formal_forecast_refs": formal_refs,
                "unresolved_forecast_refs": unresolved_refs,
                "reality_claim_refs": [],
                "revision_refs": [],
                "review_condition": "Legacy trajectory requires source-level normalization before accountability use.",
                "migration_note": note,
                "migration_warnings": sorted(set(migration_warnings)),
            }
        ],
    }


def migrate_state_registry() -> dict[str, Any]:
    state_paths = sorted(VOICES_ROOT.glob("*/state-ledger.md"))
    judgments = [parse_legacy_state(path) for path in state_paths]
    return {
        "schema": SCHEMA,
        "status": "internal-canonical",
        "authority_boundary": BOUNDARY,
        "revision_ledger_ref": relative(REVISION_PATH),
        "judgments": judgments,
    }


def voice_title(slug: str) -> str:
    readme = VOICES_ROOT / slug / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                for prefix in ("Voice Record: ", "Voice Profile: "):
                    if title.startswith(prefix):
                        title = title[len(prefix) :]
                for suffix in (" Voice Profile", " Archive", " Profile"):
                    if title.endswith(suffix):
                        title = title[: -len(suffix)]
                return title
    return slug.replace("-", " ").title()


def md_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def md_link(from_dir: Path, target: str, label: str) -> str:
    path = REPO_ROOT / target
    rel = os.path.relpath(path, from_dir).replace("\\", "/")
    return f"[{label}]({rel})"


def render_voice(
    slug: str,
    registry: dict[str, Any],
    revisions: list[dict[str, Any]],
    claims: dict[str, dict[str, Any]],
    assessments: dict[str, dict[str, Any]],
) -> str:
    voice_dir = VOICES_ROOT / slug
    judgments = sorted(
        [item for item in registry.get("judgments", []) if item.get("voice_slug") == slug],
        key=lambda item: str(item.get("id")),
    )
    voice_revisions = sorted(
        [
            item
            for item in revisions
            if item.get("voice_slug") == slug and item.get("status") == "active"
        ],
        key=lambda item: (str(item.get("date")), str(item.get("id"))),
    )
    lines = [
        "<!-- Generated from governed voice-judgment and voice-revision authorities. Do not edit directly. -->",
        "",
        f"# {voice_title(slug)} Judgment Ledger",
        "",
        f"Voice: `{slug}`  ",
        "Status: `internal-generated`",
        "",
        "## Authority Boundary",
        "",
        BOUNDARY,
        "",
        "The separately canonical voice-revision ledger adjudicates documented self-revisions; it does not adjudicate whether the revised world claim is true.",
        "",
        "## Current Judgments",
        "",
        "| Judgment | Class | Lifecycle | Proposition | First Seen | Last Seen | Expression | Sources |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if judgments:
        for item in judgments:
            version = item["versions"][-1]
            sources = ", ".join(
                md_link(voice_dir, source, Path(source).name) for source in version.get("source_refs", [])
            )
            lines.append(
                f"| `{item['id']}` | `{item['class']}` | `{item['lifecycle']}` | {md_escape(version['proposition'])} | "
                f"`{version['first_seen']}` | `{version['last_seen']}` | `{version['expression_type']}` | {sources} |"
            )
    else:
        lines.append("| none | none | none | No canonical judgment object has been migrated for this voice. | none | none | none | none |")

    lines.extend([
        "",
        "## Version History",
        "",
        "| Version | Judgment | First Seen | Last Seen | Review Condition | Legacy IDs |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for item in judgments:
        aliases = ", ".join(f"`{alias}`" for alias in item.get("legacy_ids", [])) or "none"
        for version in item.get("versions", []):
            lines.append(
                f"| `{version['id']}` | `{item['id']}` | `{version['first_seen']}` | `{version['last_seen']}` | "
                f"{md_escape(version['review_condition'])} | {aliases} |"
            )
    if not judgments:
        lines.append("| none | none | none | none | none | none |")

    lines.extend([
        "",
        "## Forecast Expressions",
        "",
        "Voice-local forecast expressions are not scored unless they reference a governed formal `NG-*` forecast.",
        "",
        "| Judgment | Formal Forecasts | Unresolved Voice-Local Hooks |",
        "| --- | --- | --- |",
    ])
    forecast_rows = 0
    for item in judgments:
        for version in item.get("versions", []):
            formal = version.get("formal_forecast_refs", [])
            unresolved = version.get("unresolved_forecast_refs", [])
            if item.get("class") == "forecast_expression" or formal or unresolved:
                lines.append(
                    f"| `{item['id']}` | {', '.join(f'`{value}`' for value in formal) or 'none'} | "
                    f"{', '.join(f'`{value}`' for value in unresolved) or 'none'} |"
                )
                forecast_rows += 1
    if not forecast_rows:
        lines.append("| none | none | none |")

    lines.extend([
        "",
        "## Self-Revisions",
        "",
        "| Revision | Date | Class | Prior View | Revised View | Source | Judgment Links |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for entry in voice_revisions:
        source = md_link(voice_dir, entry["source_path"], entry["source_title"])
        refs = ", ".join(f"`{value}`" for value in entry.get("judgment_refs", [])) or "none"
        lines.append(
            f"| `{entry['id']}` | `{entry['date']}` | `{entry['class']}` | {md_escape(entry['prior_view'])} | "
            f"{md_escape(entry['revised_view'])} | {source} | {refs} |"
        )
    if not voice_revisions:
        lines.append("| none | none | none | none | none | none | none |")

    lines.extend([
        "",
        "## Linked Reality Outcomes",
        "",
        "These outcomes are live references to the Reality lattice and are not stored in this ledger.",
        "",
        "| Judgment | Reality Claim | Claim Type | Outcome | Assessment Status |",
        "| --- | --- | --- | --- | --- |",
    ])
    reality_rows = 0
    for item in judgments:
        for version in item.get("versions", []):
            for claim_id in version.get("reality_claim_refs", []):
                claim = claims[claim_id]
                assessment = assessments.get(claim_id, {})
                claim_path = relative(REALITY_ROOT / "claims" / f"{claim_id}.json")
                lines.append(
                    f"| `{item['id']}` | {md_link(voice_dir, claim_path, claim_id)} | `{claim.get('claim_type')}` | "
                    f"`{assessment.get('outcome', 'unassessed')}` | `{assessment.get('status', 'unassessed')}` |"
                )
                reality_rows += 1
    if not reality_rows:
        lines.append("| none | none | none | `unassessed` | `unassessed` |")

    lines.extend([
        "",
        "## Unclear / Unmapped",
        "",
        "| Item | Reason |",
        "| --- | --- |",
    ])
    unclear_rows = 0
    for item in judgments:
        if item.get("lifecycle") == "unclear":
            lines.append(f"| `{item['id']}` | Judgment continuity remains unclear. |")
            unclear_rows += 1
        for version in item.get("versions", []):
            for ref in version.get("unresolved_forecast_refs", []):
                lines.append(f"| `{ref}` | Voice-local hook does not resolve to the formal forecast ledger. |")
                unclear_rows += 1
            for warning in version.get("migration_warnings", []):
                lines.append(f"| `{version['id']}` | {md_escape(warning)} |")
                unclear_rows += 1
    for entry in voice_revisions:
        if not entry.get("judgment_refs", []):
            lines.append(f"| `{entry['id']}` | Canonical revision is not yet mapped to a canonical judgment object. |")
            unclear_rows += 1
    if not unclear_rows:
        lines.append("| none | No unresolved mappings. |")
    lines.append("")
    return "\n".join(lines)


def render_state_stub(slug: str, judgments: list[dict[str, Any]]) -> str:
    lines = [
        "<!-- Retired compatibility surface. Canonical data lives in the external voice-judgment registry. -->",
        "",
        f"# {voice_title(slug)} State Ledger (Retired)",
        "",
        "This legacy path is retained for compatibility. Use [judgment-ledger.md](judgment-ledger.md) for the generated canonical reading surface.",
        "",
        "No substantive state is maintained in this file.",
        "",
    ]
    for judgment in judgments:
        for alias in judgment.get("legacy_ids", []):
            lines.extend([
                f'<a id="{alias.lower()}"></a>',
                f"- `{alias}` -> [`{judgment['id']}`](judgment-ledger.md#{judgment['id'].lower()})",
                "",
            ])
    return "\n".join(lines)


def expected_outputs(registry: dict[str, Any] | None = None) -> dict[Path, str]:
    registry = load_registry() if registry is None else registry
    revisions = all_revision_entries()
    claims = reality_claims()
    assessments = reality_assessments()
    voices = sorted(
        {str(item.get("voice_slug")) for item in registry.get("judgments", [])}
        | {
            str(item.get("voice_slug"))
            for item in revisions
            if item.get("status") == "active"
        }
    )
    outputs: dict[Path, str] = {}
    for slug in voices:
        outputs[VOICES_ROOT / slug / "judgment-ledger.md"] = render_voice(
            slug, registry, revisions, claims, assessments
        )
    by_voice: dict[str, list[dict[str, Any]]] = {}
    for judgment in registry.get("judgments", []):
        if judgment.get("legacy_ids"):
            by_voice.setdefault(str(judgment.get("voice_slug")), []).append(judgment)
    for slug, judgments in by_voice.items():
        outputs[VOICES_ROOT / slug / "state-ledger.md"] = render_state_stub(slug, judgments)
    return outputs


def render_outputs(*, check: bool) -> int:
    failures = validate_registry()
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    outputs = expected_outputs()
    drift: list[str] = []
    for path, content in outputs.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                drift.append(relative(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if drift:
        for path in drift:
            print(f"FAIL voice judgment view drift: {path}")
        return 1
    print(f"voice_judgment_views={'current' if check else 'rendered'} count={len(outputs)}")
    return 0


def command_validate() -> int:
    failures = validate_registry()
    print(f"voice_judgment_failures={len(failures)}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 1 if failures else 0


def command_migrate_state(*, check: bool, write: bool) -> int:
    if check and REGISTRY_PATH.exists():
        registry = load_registry()
        failures = validate_registry(registry)
        legacy_count = sum(bool(item.get("legacy_ids")) for item in registry.get("judgments", []))
        for path, expected in expected_outputs(registry).items():
            if path.name == "state-ledger.md" and (
                not path.exists() or path.read_text(encoding="utf-8") != expected
            ):
                failures.append(f"legacy state compatibility drift: {relative(path)}")
        if failures:
            for failure in failures:
                print(f"FAIL {failure}")
            return 1
        print(f"voice judgment migration check passed judgments={legacy_count}")
        return 0
    try:
        candidate = migrate_state_registry()
    except (OSError, ValueError) as error:
        print(f"FAIL voice judgment migration: {error}")
        return 1
    failures = validate_registry(candidate)
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    if write:
        REGISTRY_ROOT.mkdir(parents=True, exist_ok=True)
        REGISTRY_PATH.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"voice judgment registry written: {relative(REGISTRY_PATH)}")
    else:
        print(f"voice judgment migration check passed judgments={len(candidate['judgments'])}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Governed external voice-judgment registry")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    render = sub.add_parser("render")
    render.add_argument("--check", action="store_true")
    migrate = sub.add_parser("migrate-state")
    mode = migrate.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    return parser


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    if args.command == "validate":
        return command_validate()
    if args.command == "render":
        return render_outputs(check=args.check)
    if args.command == "migrate-state":
        return command_migrate_state(check=args.check, write=args.write)
    return 2


if __name__ == "__main__":
    sys.exit(main())

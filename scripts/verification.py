from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
VERIFICATION_ROOT = NG_ROOT / "work" / "verification"
PACKETS_ROOT = VERIFICATION_ROOT / "packets"
TEMPLATE_PATH = VERIFICATION_ROOT / "_packet-template.md"
LEDGER_PATH = NG_ROOT / "work" / "forecasts" / "forecast-ledger.md"
REGISTRY_PATH = VERIFICATION_ROOT / "source-registry.md"
REALITY_ROOT = NG_ROOT / "work" / "reality"

WORKFLOW_STATES = {"requested", "researching", "assessed", "closed"}
OUTCOMES = {
    "operationally_supported",
    "operationally_contested",
    "disconfirmed",
    "unresolvable_with_authorized_evidence",
    "not_investigated",
}
EVIDENCE_CLASSES = {"observational_registry", "sensor_or_tracking_data", "commercial_operational_data", "multilateral_primary", "official_interested_primary", "independent_professional_reporting", "state_affiliated_reporting", "expert_commentary"}
CONTEXT_ONLY_EVIDENCE_CLASSES = {"expert_commentary"}
INDEPENDENT_SUPPORT_EVIDENCE_CLASSES = EVIDENCE_CLASSES - {
    "official_interested_primary",
    "state_affiliated_reporting",
    *CONTEXT_ONLY_EVIDENCE_CLASSES,
}
DOMAINS = {"maritime_incident", "humanitarian_event", "nuclear_verification", "maritime_tracking", "satellite_observation", "aviation_tracking", "energy_market", "macroeconomic", "military_activity", "diplomatic_position", "professional_reporting"}
PERSPECTIVES = {"multilateral", "commercial", "western_state", "western_independent", "european_independent", "middle_east_regional", "turkish_state_affiliated", "russian_state_affiliated", "chinese_state_affiliated", "iranian_state", "gulf_state", "israeli_state", "ukrainian_state"}
ACCESS_CLASSES = {"open", "open_limited", "registration", "subscription"}
LANGUAGES = {"en", "fr", "es", "ar", "zh", "ru", "fa", "he", "uk", "tr", "multilingual"}
TRANSLATION_PROVENANCE = {"not_required", "official_english_available", "official_english_edition", "operator_translation_required"}
STATUSES = {"candidate", "active", "degraded", "retired"}
DIRECTIONS = {"supports", "challenges", "context_only"}
VER_RE = re.compile(r"VER-\d{8}-\d{2}")
HOOK_RE = re.compile(r"NG-\d{8}-F\d{2}")
OPC_RE = re.compile(r"OPC-(?P<date>\d{8})-\d{2}")
CLAIM_STATUSES = {"source_assertion", "cross_source_convergence", "contested", "unknown", "operationally_supported"}
CONSEQUENCES = {"high", "medium", "low"}
PUBLIC_USE = {"yes", "no"}
FIELD_RE = re.compile(r"^(?P<name>[A-Za-z ]+):\s*`(?P<value>[^`]*)`\s*$", re.MULTILINE)
OBSERVABLE_RE = re.compile(r"^- \[(?: |x|X)\]\s+(.+?)\s*$", re.MULTILINE)
EVIDENCE_RE = re.compile(
    r"^\|\s*`(?P<id>EVID-\d{2})`\s*\|\s*`(?P<registry_id>VSRC-[A-Z0-9-]+)`\s*\|\s*(?P<url>https?://[^| ]+)\s*\|"
    r"\s*`(?P<retrieved>[^`]+)`\s*\|\s*`(?P<event>[^`]+)`\s*\|"
    r"\s*`(?P<source_type>[^`]+)`\s*\|\s*`(?P<chain>[^`]+)`\s*\|"
    r"\s*`(?P<direction>[^`]+)`\s*\|\s*`(?P<translation>[^`]+)`\s*\|\s*(?P<limitation>.*?)\s*\|$",
    re.MULTILINE,
)
COVERAGE_RE = re.compile(r"^\|\s*(?P<floor>[^|]+?)\s*\|\s*`(?P<status>covered|waived|not_applicable)`\s*\|\s*(?P<detail>.+?)\s*\|$", re.MULTILINE)
COVERAGE_FLOORS = {"Closest registry, sensor, or original document", "Affected-region or local source", "Claimant official position", "Challenged actor position or denial", "Two professional reporting chains from different geopolitical environments", "Commercial or observational evidence when applicable"}
REGISTRY_ROW_RE = re.compile(r"^\|\s*`(?P<id>VSRC-[A-Z0-9-]+)`\s*\|(?P<rest>.+)\|$", re.MULTILINE)
CLAIM_ROW_RE = re.compile(
    r"^\|\s*`(?P<claim_id>OPC-\d{8}-\d{2})`\s*\|\s*(?P<claim>[^|]+?)\s*\|"
    r"\s*`(?P<status>[^`]+)`\s*\|\s*`(?P<consequence>[^`]+)`\s*\|"
    r"\s*`(?P<public_use>[^`]+)`\s*\|\s*`(?P<verification>[^`]+)`\s*\|$",
    re.MULTILINE,
)
FORECAST_DEPENDENCY_RE = re.compile(
    r"^\|\s*`(?P<hook>NG-\d{8}-F\d{2})`\s*\|.*?\|\s*`(?P<dependency>OPC-\d{8}-\d{2}|none)`\s*\|\s*$",
    re.MULTILINE,
)
RELATED_CLAIM_RE = re.compile(r"^Related claim:\s*`(?P<claim_id>OPC-\d{8}-\d{2})`\s*$", re.MULTILINE)
SECTION_VALUE_RE = {
    name: re.compile(rf"^{re.escape(name)}:\s*(.+?)\s*$", re.MULTILINE)
    for name in ("Conclusion", "Confidence boundary", "Downstream effect")
}
DEFAULT_OBSERVABLES = [
    "Specific actor, asset, place, or route affected by the alleged event.",
    "Event timing narrow enough to compare against independent records.",
    "Observable mechanism that could support or challenge the claim.",
    "Attribution basis distinguishing the claimed actor from alternatives.",
    "Independent commercial, official, registry, sensor, or professional reporting signal.",
    "Challenged-actor, affected-party, or alternative-explanation record.",
]


@dataclass(frozen=True)
class Packet:
    packet_id: str
    path: Path
    fields: dict[str, str]
    observables: list[str]
    evidence: list[dict[str, str]]
    sections: dict[str, str]
    coverage: list[dict[str, str]]


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source: str
    url: str
    domain: str
    observables: str
    evidence_class: str
    perspective: str
    geography: str
    languages: tuple[str, ...]
    translation: str
    access: str
    fallback: str
    latency: str
    chain_rule: str
    failure_modes: str
    appropriate: str
    inappropriate: str
    reviewed: str
    status: str


@dataclass(frozen=True)
class OperationalClaim:
    claim_id: str
    claim: str
    status: str
    consequence: str
    public_use: str
    verification: str


def parse_registry(path: Path = REGISTRY_PATH) -> list[SourceRecord]:
    structured_root = REALITY_ROOT / "sources"
    if path == REGISTRY_PATH and structured_root.exists() and any(structured_root.glob("*.json")):
        translation_map = {
            "not_required": "not_required",
            "official_edition": "official_english_available",
            "named_human_translation": "operator_translation_required",
            "operator_translation": "operator_translation_required",
            "machine_assisted_disclosed": "operator_translation_required",
        }
        records = []
        for source_path in sorted(structured_root.glob("*.json")):
            item = json.loads(source_path.read_text(encoding="utf-8"))
            review_history = item.get("review_history", [])
            reviewed = review_history[-1].get("date", "") if review_history else ""
            records.append(SourceRecord(
                item["id"], item["name"], item["canonical_url"], item["domain"], item["observables"],
                item["evidence_class"], item["perspective"], item["geography"],
                tuple(item["access_languages"]), translation_map.get(item["translation_provenance"], item["translation_provenance"]),
                item["access"], item["open_fallback"], item["latency"], item["originating_chain_rule"],
                item["known_failure_modes"], item["appropriate_uses"], item["inappropriate_uses"],
                reviewed, item["status"],
            ))
        return sorted(records, key=lambda record: record.source_id)
    records = []
    for match in REGISTRY_ROW_RE.finditer(path.read_text(encoding="utf-8")):
        cells = [cell.strip().strip("`") for cell in match.group("rest").split("|")]
        if len(cells) != 18:
            continue
        records.append(SourceRecord(match.group("id"), cells[0], cells[1], cells[2], cells[3], cells[4], cells[5], cells[6], tuple(item.strip() for item in cells[7].split(",")), *cells[8:]))
    return records


def validate_registry(path: Path = REGISTRY_PATH) -> list[str]:
    failures = []
    if not path.exists():
        return ["verification source registry is missing"]
    records = parse_registry(path)
    ids = [record.source_id for record in records]
    if not records:
        failures.append("source registry has no entries")
    for source_id in sorted({item for item in ids if ids.count(item) > 1}):
        failures.append(f"duplicate registry source ID: {source_id}")
    by_id = {record.source_id: record for record in records}
    for record in records:
        if record.domain not in DOMAINS: failures.append(f"{record.source_id}: invalid domain {record.domain}")
        if record.evidence_class not in EVIDENCE_CLASSES: failures.append(f"{record.source_id}: invalid evidence class {record.evidence_class}")
        if record.perspective not in PERSPECTIVES: failures.append(f"{record.source_id}: invalid perspective {record.perspective}")
        if record.access not in ACCESS_CLASSES: failures.append(f"{record.source_id}: invalid access {record.access}")
        if record.status not in STATUSES: failures.append(f"{record.source_id}: invalid status {record.status}")
        unknown_languages = set(record.languages) - LANGUAGES
        if unknown_languages: failures.append(f"{record.source_id}: invalid language {sorted(unknown_languages)[0]}")
        if record.translation not in TRANSLATION_PROVENANCE: failures.append(f"{record.source_id}: invalid translation provenance {record.translation}")
        parsed = urlparse(record.url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc: failures.append(f"{record.source_id}: malformed canonical URL")
        try: date.fromisoformat(record.reviewed)
        except ValueError: failures.append(f"{record.source_id}: invalid review date {record.reviewed}")
        if record.status == "active" and record.access not in {"open", "open_limited"}:
            fallback = by_id.get(record.fallback)
            if not fallback or fallback.status != "active" or fallback.access not in {"open", "open_limited"}:
                failures.append(f"{record.source_id}: paid source lacks active open fallback")
    active_open_domains = {r.domain for r in records if r.status == "active" and r.access in {"open", "open_limited"}}
    for domain in sorted({r.domain for r in records if r.status == "active"} - active_open_domains):
        failures.append(f"active domain lacks open fallback: {domain}")
    return failures


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "claim"


def parse_operational_claims(text: str) -> list[OperationalClaim]:
    return [OperationalClaim(**match.groupdict()) for match in CLAIM_ROW_RE.finditer(text)]


def parse_forecast_dependencies(text: str) -> list[dict[str, str]]:
    return [match.groupdict() for match in FORECAST_DEPENDENCY_RE.finditer(text)]


def day_payload(
    run_date: str,
    daily_root: Path | None = None,
    packets_root: Path = PACKETS_ROOT,
) -> dict[str, Any]:
    root = daily_root or (NG_ROOT / "work" / "daily")
    run_dir = root / run_date
    synthesis_path = run_dir / "synthesis.md"
    forecast_path = run_dir / "forecast.md"
    synthesis = synthesis_path.read_text(encoding="utf-8") if synthesis_path.exists() else ""
    forecast = forecast_path.read_text(encoding="utf-8") if forecast_path.exists() else ""
    claims = parse_operational_claims(synthesis)
    dependencies = parse_forecast_dependencies(forecast)
    by_claim: dict[str, list[str]] = {}
    for item in dependencies:
        if item["dependency"] != "none":
            by_claim.setdefault(item["dependency"], []).append(item["hook"])
    rows = []
    for claim in claims:
        lattice = None
        try:
            import reality
            lattice = reality.claim_state(claim.claim_id)
        except (ImportError, ValueError, OSError, json.JSONDecodeError):
            lattice = None
        packet = None
        packet_state = "not_requested"
        packet_outcome = None
        if claim.verification == "request":
            packet_state = "requested_not_created"
        elif VER_RE.fullmatch(claim.verification):
            path = find_packet(claim.verification, packets_root)
            if path:
                packet = parse_packet(path)
                packet_state = packet.fields.get("status", "unknown")
                packet_outcome = packet.fields.get("assessment_outcome")
            else:
                packet_state = "missing"
        blocking = []
        assessed = packet_state in {"assessed", "closed"}
        lattice_assessment = lattice.get("assessment") if lattice else None
        lattice_support = bool(
            lattice_assessment
            and lattice_assessment.get("outcome") == "supported"
            and lattice_assessment.get("status") in {"canonical_assessed", "canonical_with_language_waiver"}
        )
        effective_status = claim.status
        if lattice_assessment and lattice_assessment.get("outcome") in {"contested", "disconfirmed", "unresolvable"}:
            effective_status = lattice_assessment["outcome"]
        elif lattice_support:
            effective_status = "operationally_supported"
        if claim.status == "operationally_supported" and not (
            lattice_support if lattice else (assessed and packet_outcome == "operationally_supported")
        ):
            blocking.append("unsupported_operational_status")
        if claim.consequence == "high" and claim.public_use == "yes" and not assessed:
            blocking.append("publication_requires_assessed_packet")
        rows.append({
            "claim_id": claim.claim_id,
            "claim": claim.claim,
            "status": claim.status,
            "effective_status": effective_status,
            "consequence": claim.consequence,
            "public_use": claim.public_use,
            "verification": claim.verification,
            "packet_state": packet_state,
            "packet_outcome": packet_outcome,
            "forecast_hooks": sorted(by_claim.get(claim.claim_id, [])),
            "blocking_reasons": blocking,
            "lattice": lattice,
        })
    unknown_dependencies = sorted({item["dependency"] for item in dependencies if item["dependency"] != "none"} - {claim.claim_id for claim in claims})
    return {"date": run_date, "claims": rows, "forecast_dependencies": dependencies, "unknown_dependencies": unknown_dependencies}


def validate_day_claims(run_date: str, stage: str, daily_root: Path | None = None, packets_root: Path = PACKETS_ROOT) -> list[str]:
    root = daily_root or (NG_ROOT / "work" / "daily")
    synthesis_path = root / run_date / "synthesis.md"
    synthesis = synthesis_path.read_text(encoding="utf-8") if synthesis_path.exists() else ""
    payload = day_payload(run_date, root, packets_root)
    failures = []
    claims = payload["claims"]
    ids = [item["claim_id"] for item in claims]
    parsed_ids = set(ids)
    # Detect table rows that mention an OPC ID but do not satisfy the contract.
    for line in synthesis.splitlines():
        match = re.search(r"OPC-\d{8}-\d{2}", line)
        if line.lstrip().startswith("|") and match and match.group(0) not in parsed_ids:
            failures.append(f"malformed operational claim row: {match.group(0)}")
    for claim_id in sorted({item for item in ids if ids.count(item) > 1}):
        failures.append(f"duplicate operational claim ID: {claim_id}")
    expected_date = run_date.replace("-", "")
    for item in claims:
        if OPC_RE.fullmatch(item["claim_id"]).group("date") != expected_date:
            failures.append(f"operational claim date mismatch: {item['claim_id']}")
        if item["status"] not in CLAIM_STATUSES:
            failures.append(f"{item['claim_id']}: invalid operational claim status {item['status']}")
        if item["consequence"] not in CONSEQUENCES:
            failures.append(f"{item['claim_id']}: invalid consequence {item['consequence']}")
        if item["public_use"] not in PUBLIC_USE:
            failures.append(f"{item['claim_id']}: invalid public-use value {item['public_use']}")
        verification = item["verification"]
        if verification not in {"none", "request"} and not VER_RE.fullmatch(verification):
            failures.append(f"{item['claim_id']}: invalid verification reference {verification}")
        if verification.startswith("VER-") and item["packet_state"] == "missing":
            failures.append(f"{item['claim_id']}: verification packet not found {verification}")
        if "unsupported_operational_status" in item["blocking_reasons"]:
            failures.append(f"{item['claim_id']}: operationally_supported requires a supporting assessed packet")
        if item["lattice"] and item["status"] == "operationally_supported" and item["effective_status"] != "operationally_supported":
            failures.append(f"{item['claim_id']}: migrated claim lacks canonical multilingual lattice support")
        if item["public_use"] == "no" and not item["forecast_hooks"]:
            failures.append(
                f"{item['claim_id']}: orphan operational claim; retain only claims controlling public use or a forecast dependency"
            )
        if stage == "publication" and "publication_requires_assessed_packet" in item["blocking_reasons"]:
            failures.append(f"{item['claim_id']}: high-consequence public use requires an assessed packet")
    failures.extend(f"forecast dependency references unknown operational claim: {item}" for item in payload["unknown_dependencies"])
    return failures


def packet_paths(root: Path = PACKETS_ROOT) -> list[Path]:
    return sorted(root.glob("VER-*/README.md")) if root.exists() else []


def parse_packet(path: Path) -> Packet:
    text = path.read_text(encoding="utf-8")
    fields = {match.group("name").lower().replace(" ", "_"): match.group("value") for match in FIELD_RE.finditer(text)}
    packet_id = fields.get("verification_id", "")
    evidence = [match.groupdict() for match in EVIDENCE_RE.finditer(text)]
    sections = {
        name.lower().replace(" ", "_"): (match.group(1).strip(" `") if (match := pattern.search(text)) else "")
        for name, pattern in SECTION_VALUE_RE.items()
    }
    coverage = [{key: value.strip() for key, value in match.groupdict().items()} for match in COVERAGE_RE.finditer(text)]
    return Packet(packet_id, path, fields, OBSERVABLE_RE.findall(text), evidence, sections, coverage)


def find_packet(packet_id: str, root: Path = PACKETS_ROOT) -> Path | None:
    matches = [path for path in packet_paths(root) if parse_packet(path).packet_id == packet_id]
    return matches[0] if len(matches) == 1 else None


def ledger_hook_ids(path: Path = LEDGER_PATH) -> set[str]:
    return set(HOOK_RE.findall(path.read_text(encoding="utf-8"))) if path.exists() else set()


def validate_packet(packet: Packet, repo_root: Path = REPO_ROOT, ledger_path: Path = LEDGER_PATH, registry_path: Path = REGISTRY_PATH) -> list[str]:
    failures: list[str] = []
    label = packet.packet_id or packet.path.parent.name
    required = {"verification_id", "status", "assessment_outcome", "opened", "closed", "claim", "why_it_matters", "affected_forecast_hooks", "affected_artifacts", "research_minutes", "evidence_chains_examined", "judgment_changed", "further_automation_justified"}
    for field in sorted(required - set(packet.fields)):
        failures.append(f"{label}: missing field {field}")
    if not VER_RE.fullmatch(packet.packet_id):
        failures.append(f"{label}: invalid verification ID")
    if packet.fields.get("status") not in WORKFLOW_STATES:
        failures.append(f"{label}: invalid workflow state {packet.fields.get('status', '')}")
    outcome = packet.fields.get("assessment_outcome", "")
    if outcome not in OUTCOMES:
        failures.append(f"{label}: invalid assessment outcome {outcome}")
    related_claim = packet.fields.get("related_claim")
    if related_claim and not OPC_RE.fullmatch(related_claim):
        failures.append(f"{label}: invalid related claim {related_claim}")
    if not packet.observables or any("[Observable" in item for item in packet.observables):
        failures.append(f"{label}: missing required observables")
    evidence_ids = [item["id"] for item in packet.evidence]
    if len(evidence_ids) != len(set(evidence_ids)):
        failures.append(f"{label}: duplicate evidence IDs")
    registry = {record.source_id: record for record in parse_registry(registry_path)} if registry_path.exists() else {}
    for item in packet.evidence:
        source = registry.get(item["registry_id"])
        if not source:
            failures.append(f"{label}: unknown registry source {item['registry_id']}")
        if item["source_type"] not in EVIDENCE_CLASSES:
            failures.append(f"{label}: invalid source type for {item['id']}: {item['source_type']}")
        elif source and item["source_type"] != source.evidence_class:
            failures.append(f"{label}: source type for {item['id']} does not match registry")
        if item["direction"] not in DIRECTIONS:
            failures.append(f"{label}: invalid direction for {item['id']}: {item['direction']}")
        if source and (
            source.status == "candidate"
            or source.evidence_class in CONTEXT_ONLY_EVIDENCE_CLASSES
        ) and item["direction"] != "context_only":
            failures.append(f"{label}: candidate or context-only source {source.source_id} may supply context only")
        if not item["chain"].strip():
            failures.append(f"{label}: missing origin chain for {item['id']}")
        if item["translation"] not in TRANSLATION_PROVENANCE:
            failures.append(f"{label}: invalid translation provenance for {item['id']}")
        if source and (set(source.languages) - {"en"}) and not item["translation"]:
            failures.append(f"{label}: non-English evidence lacks translation provenance for {item['id']}")
    hooks = set(HOOK_RE.findall(packet.fields.get("affected_forecast_hooks", "")))
    unknown_hooks = hooks - ledger_hook_ids(ledger_path)
    failures.extend(f"{label}: unknown forecast hook {hook}" for hook in sorted(unknown_hooks))
    artifact_value = packet.fields.get("affected_artifacts", "")
    artifacts = [] if artifact_value == "none" else [item.strip() for item in artifact_value.split(",") if item.strip()]
    for artifact in artifacts:
        if not (repo_root / artifact).exists():
            failures.append(f"{label}: broken affected artifact path {artifact}")
    status = packet.fields.get("status")
    if status in {"assessed", "closed"}:
        if outcome == "not_investigated":
            failures.append(f"{label}: assessed packet cannot remain not_investigated")
        if not packet.evidence:
            failures.append(f"{label}: assessed packet requires evidence")
        for name, value in packet.sections.items():
            if not value or value.startswith("["):
                failures.append(f"{label}: assessed packet missing {name}")
        coverage = {item["floor"]: item for item in packet.coverage}
        for floor in sorted(COVERAGE_FLOORS - set(coverage)):
            failures.append(f"{label}: missing coverage floor {floor}")
        for item in packet.coverage:
            if item["status"] == "waived" and (not item["detail"] or item["detail"].startswith("[")):
                failures.append(f"{label}: coverage waiver lacks explanation for {item['floor']}")
    if status == "closed" and packet.fields.get("closed") == "none":
        failures.append(f"{label}: closed packet missing close date")
    if outcome == "operationally_supported" and not any(item["direction"] == "supports" for item in packet.evidence):
        failures.append(f"{label}: operationally_supported requires supporting evidence")
    if outcome == "operationally_supported":
        supporting = [registry.get(item["registry_id"]) for item in packet.evidence if item["direction"] == "supports"]
        if not any(
            source
            and source.status != "candidate"
            and source.evidence_class in INDEPENDENT_SUPPORT_EVIDENCE_CLASSES
            for source in supporting
        ):
            failures.append(
                f"{label}: state-affiliated, interested official, candidate, or context-only sources "
                "cannot independently establish operational support"
            )
        if len({item["chain"] for item in packet.evidence if item["direction"] == "supports"}) < 2:
            failures.append(f"{label}: operationally_supported requires two supporting evidence chains")
    try:
        declared_chains = int(packet.fields.get("evidence_chains_examined", "0"))
        actual_chains = len({item["chain"] for item in packet.evidence})
        if declared_chains != actual_chains:
            failures.append(f"{label}: evidence chain count {declared_chains} does not match {actual_chains}")
    except ValueError:
        failures.append(f"{label}: evidence chain count is not an integer")
    return failures


def validate_all(root: Path = PACKETS_ROOT, repo_root: Path = REPO_ROOT, ledger_path: Path = LEDGER_PATH) -> list[str]:
    packets = [parse_packet(path) for path in packet_paths(root)]
    failures: list[str] = validate_registry()
    ids = [packet.packet_id for packet in packets]
    for packet_id in sorted({item for item in ids if ids.count(item) > 1}):
        failures.append(f"duplicate verification packet ID: {packet_id}")
    for packet in packets:
        failures.extend(validate_packet(packet, repo_root, ledger_path))
    return failures


def next_packet_id(run_date: str, root: Path = PACKETS_ROOT) -> str:
    prefix = f"VER-{run_date.replace('-', '')}-"
    used = [int(match.group(0)[-2:]) for path in packet_paths(root) if (match := VER_RE.search(path.parent.name)) and match.group(0).startswith(prefix)]
    return f"{prefix}{max(used, default=0) + 1:02d}"


def create_packet(run_date: str, slug: str, root: Path = PACKETS_ROOT, template_path: Path = TEMPLATE_PATH) -> Path:
    packet_id = next_packet_id(run_date, root)
    target = root / f"{packet_id}-{slugify(slug)}" / "README.md"
    target.parent.mkdir(parents=True, exist_ok=False)
    text = template_path.read_text(encoding="utf-8")
    text = text.replace("VER-YYYYMMDD-NN", packet_id).replace("YYYY-MM-DD", run_date).replace("[Bounded claim label]", slug)
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


def repo_relative(path: Path, repo_root: Path = REPO_ROOT) -> str:
    return path.relative_to(repo_root).as_posix() if path.is_relative_to(repo_root) else path.as_posix()


def default_affected_artifacts(run_date: str, daily_root: Path = NG_ROOT / "work" / "daily", ledger_path: Path = LEDGER_PATH, repo_root: Path = REPO_ROOT) -> list[str]:
    run_dir = daily_root / run_date
    paths = [run_dir / "synthesis.md", run_dir / "forecast.md"]
    issue_path = run_dir / "issue.md"
    if issue_path.exists():
        paths.append(issue_path)
    paths.append(ledger_path)
    return [repo_relative(path, repo_root) for path in paths if path.exists()]


def fill_requested_packet(
    path: Path,
    *,
    claim_id: str,
    claim: str,
    hooks: list[str],
    artifacts: list[str],
    observables: list[str],
) -> None:
    text = path.read_text(encoding="utf-8")
    packet = parse_packet(path)
    text = text.replace("Claim: `[Exact operational claim under review.]`", f"Claim: `{claim}`")
    text = text.replace(
        f"Claim: `{claim}`",
        f"Claim: `{claim}`\n\nRelated claim: `{claim_id}`",
        1,
    )
    text = text.replace(
        "Why it matters: `[Judgment, publication, promotion, or forecast consequence.]`",
        f"Why it matters: `Verification request for {claim_id}; requested packets scope evidence collection and do not authorize public use, forecast scoring, or operational truth.`",
    )
    text = text.replace("Affected forecast hooks: `none`", f"Affected forecast hooks: `{', '.join(hooks) or 'none'}`")
    text = text.replace("Affected artifacts: `none`", f"Affected artifacts: `{', '.join(artifacts) or 'none'}`")
    observable_lines = "\n".join(f"- [ ] {item}" for item in observables)
    text = text.replace("- [ ] `[Observable required to support or challenge the claim.]`", observable_lines)
    text = text.replace(
        "`[Record search boundary, important absences, and why research stopped.]`",
        "`Packet opened and scoped only. No external evidence collection has been performed yet.`",
    )
    if "Related claim:" not in text:
        text = text.replace(f"Claim: `{claim}`", f"Claim: `{claim}`\n\nRelated claim: `{claim_id}`", 1)
    # Preserve the packet ID allocated by create_packet; parse it once to catch malformed templates.
    if not VER_RE.fullmatch(packet.packet_id):
        raise ValueError(f"invalid packet ID in {path}")
    path.write_text(text, encoding="utf-8", newline="\n")


def attach_packet_to_claim(
    run_date: str,
    claim_id: str,
    slug: str,
    *,
    packet_id: str | None = None,
    observables: list[str] | None = None,
    hooks: list[str] | None = None,
    artifacts: list[str] | None = None,
    force: bool = False,
    daily_root: Path = NG_ROOT / "work" / "daily",
    packets_root: Path = PACKETS_ROOT,
    template_path: Path = TEMPLATE_PATH,
    ledger_path: Path = LEDGER_PATH,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    run_dir = daily_root / run_date
    synthesis_path = run_dir / "synthesis.md"
    forecast_path = run_dir / "forecast.md"
    issue_path = run_dir / "issue.md"
    if not synthesis_path.exists():
        raise ValueError(f"missing synthesis.md for {run_date}")
    synthesis = synthesis_path.read_text(encoding="utf-8")
    claims = {claim.claim_id: claim for claim in parse_operational_claims(synthesis)}
    claim = claims.get(claim_id)
    if not claim:
        raise ValueError(f"claim not found: {claim_id}")
    if OPC_RE.fullmatch(claim_id).group("date") != run_date.replace("-", ""):
        raise ValueError(f"claim date does not match run date: {claim_id}")
    if VER_RE.fullmatch(claim.verification) and claim.verification != packet_id and not force:
        raise ValueError(f"{claim_id} already attached to {claim.verification}; pass --force to replace")

    forecast = forecast_path.read_text(encoding="utf-8") if forecast_path.exists() else ""
    selected_hooks = hooks if hooks is not None else [
        item["hook"] for item in parse_forecast_dependencies(forecast) if item["dependency"] == claim_id
    ]
    selected_artifacts = artifacts if artifacts is not None else default_affected_artifacts(run_date, daily_root, ledger_path, repo_root)
    selected_observables = observables if observables else DEFAULT_OBSERVABLES

    created = False
    if packet_id:
        packet_path = find_packet(packet_id, packets_root)
        if not packet_path:
            raise ValueError(f"packet not found or ambiguous: {packet_id}")
    else:
        packet_path = create_packet(run_date, slug, packets_root, template_path)
        created = True
        packet_id = parse_packet(packet_path).packet_id
        fill_requested_packet(
            packet_path,
            claim_id=claim_id,
            claim=claim.claim.strip(),
            hooks=selected_hooks,
            artifacts=selected_artifacts,
            observables=selected_observables,
        )

    packet = parse_packet(packet_path)
    failures = validate_packet(packet, repo_root, ledger_path)
    if failures:
        raise ValueError("; ".join(failures))

    replaced = False
    def replace_row(match: re.Match[str]) -> str:
        nonlocal replaced
        if match.group("claim_id") != claim_id:
            return match.group(0)
        replaced = True
        return (
            f"| `{match.group('claim_id')}` | {match.group('claim').strip()} | "
            f"`{match.group('status')}` | `{match.group('consequence')}` | "
            f"`{match.group('public_use')}` | `{packet.packet_id}` |"
        )

    updated = CLAIM_ROW_RE.sub(replace_row, synthesis, count=0)
    if not replaced:
        raise ValueError(f"could not update claim row: {claim_id}")
    synthesis_path.write_text(updated, encoding="utf-8", newline="\n")

    issue_action = "absent"
    if issue_path.exists():
        import render_daily_issue
        model = render_daily_issue.load_model(run_date, daily_root, ledger_path)
        issue_path.write_text(render_daily_issue.render_model(model), encoding="utf-8", newline="\n")
        issue_action = "write"
    else:
        issue_action = f"run .\\scripts\\python.ps1 scripts\\render_daily_issue.py --date {run_date}"

    day_failures = validate_day_claims(run_date, "issue" if issue_path.exists() else "synthesis", daily_root, packets_root)
    return {
        "packet": packet.packet_id,
        "packet_path": repo_relative(packet_path, repo_root),
        "created": created,
        "claim": claim_id,
        "hooks": selected_hooks,
        "artifacts": selected_artifacts,
        "issue_action": issue_action,
        "validation_failures": day_failures,
    }


def list_payload(root: Path = PACKETS_ROOT, status: str | None = None) -> list[dict[str, Any]]:
    packets = [parse_packet(path) for path in packet_paths(root)]
    if status:
        packets = [packet for packet in packets if packet.fields.get("status") == status]
    return [
        {
            "verification_id": packet.packet_id,
            "status": packet.fields.get("status"),
            "outcome": packet.fields.get("assessment_outcome"),
            "path": packet.path.relative_to(REPO_ROOT).as_posix() if packet.path.is_relative_to(REPO_ROOT) else packet.path.as_posix(),
        }
        for packet in packets
    ]


def source_payload(path: Path = REGISTRY_PATH, domain: str | None = None, perspective: str | None = None, access: str | None = None) -> list[dict[str, Any]]:
    records = parse_registry(path)
    if domain: records = [r for r in records if r.domain == domain]
    if perspective: records = [r for r in records if r.perspective == perspective]
    if access: records = [r for r in records if r.access == access]
    return [{"id": r.source_id, "source": r.source, "url": r.url, "domain": r.domain, "evidence_class": r.evidence_class, "perspective": r.perspective, "access": r.access, "status": r.status} for r in records]


def close_packet(packet_id: str, root: Path = PACKETS_ROOT) -> list[str]:
    path = find_packet(packet_id, root)
    if not path:
        return [f"packet not found or ambiguous: {packet_id}"]
    packet = parse_packet(path)
    failures = validate_packet(packet)
    if failures or packet.fields.get("status") != "assessed":
        return failures or [f"{packet_id}: only assessed packets may be closed"]
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^Status: `assessed`$", "Status: `closed`", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^Closed: `none`$", f"Closed: `{date.today().isoformat()}`", text, count=1, flags=re.MULTILINE)
    path.write_text(text, encoding="utf-8", newline="\n")
    return validate_packet(parse_packet(path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage explicit operational-verification packets.")
    sub = parser.add_subparsers(dest="command", required=True)
    new = sub.add_parser("new")
    new.add_argument("--date", required=True)
    new.add_argument("--slug", required=True)
    listing = sub.add_parser("list")
    listing.add_argument("--status", choices=sorted(WORKFLOW_STATES))
    listing.add_argument("--json", action="store_true")
    check = sub.add_parser("check")
    check.add_argument("packet_id", nargs="?")
    check.add_argument("--json", action="store_true")
    close = sub.add_parser("close")
    close.add_argument("packet_id")
    attach = sub.add_parser("attach")
    attach.add_argument("--date", required=True)
    attach.add_argument("--claim", required=True)
    attach.add_argument("--slug", required=True)
    attach.add_argument("--packet")
    attach.add_argument("--observable", action="append", dest="observables")
    attach.add_argument("--hook", action="append", dest="hooks")
    attach.add_argument("--artifact", action="append", dest="artifacts")
    attach.add_argument("--force", action="store_true")
    attach.add_argument("--json", action="store_true")
    sources = sub.add_parser("sources")
    sources.add_argument("--domain", choices=sorted(DOMAINS))
    sources.add_argument("--perspective", choices=sorted(PERSPECTIVES))
    sources.add_argument("--access", choices=sorted(ACCESS_CLASSES))
    sources.add_argument("--json", action="store_true")
    day_view = sub.add_parser("day")
    day_view.add_argument("--date", required=True)
    day_view.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "new":
        print(create_packet(args.date, args.slug).relative_to(REPO_ROOT).as_posix())
        return
    if args.command == "list":
        payload = list_payload(status=args.status)
        print(json.dumps(payload, indent=2) if args.json else "\n".join(f"{item['verification_id']} {item['status']} {item['path']}" for item in payload))
        return
    if args.command == "check":
        if args.packet_id:
            path = find_packet(args.packet_id)
            failures = [f"packet not found or ambiguous: {args.packet_id}"] if not path else validate_packet(parse_packet(path))
        else:
            failures = validate_all()
        payload = {"failures": failures, "failure_count": len(failures)}
        print(json.dumps(payload, indent=2) if args.json else f"verification_failures={len(failures)}")
        for failure in ([] if args.json else failures):
            print(f"FAIL {failure}")
        if failures:
            raise SystemExit(1)
        return
    if args.command == "sources":
        payload = source_payload(domain=args.domain, perspective=args.perspective, access=args.access)
        print(json.dumps(payload, indent=2) if args.json else "\n".join(f"{item['id']} {item['source']} [{item['domain']}; {item['perspective']}; {item['access']}]" for item in payload))
        return
    if args.command == "attach":
        try:
            payload = attach_packet_to_claim(
                args.date,
                args.claim,
                args.slug,
                packet_id=args.packet,
                observables=args.observables,
                hooks=args.hooks,
                artifacts=args.artifacts,
                force=args.force,
            )
        except ValueError as exc:
            raise SystemExit(f"FAIL {exc}") from exc
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"packet={payload['packet']}")
            print(f"packet_path={payload['packet_path']}")
            print(f"created={'yes' if payload['created'] else 'no'}")
            print(f"attached_claim={payload['claim']}")
            print(f"affected_hooks={','.join(payload['hooks']) or 'none'}")
            print(f"issue_action={payload['issue_action']}")
            print(f"validation_failures={len(payload['validation_failures'])}")
            for failure in payload["validation_failures"]:
                print(f"FAIL {failure}")
        if payload["validation_failures"]:
            raise SystemExit(1)
        return
    if args.command == "day":
        payload = day_payload(args.date)
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"date={payload['date']}")
            print(f"operational_claims={len(payload['claims'])}")
            for item in payload["claims"]:
                hooks = ",".join(item["forecast_hooks"]) or "none"
                blocks = ",".join(item["blocking_reasons"]) or "none"
                print(f"{item['claim_id']} {item['status']} consequence={item['consequence']} public={item['public_use']} verification={item['verification']} packet={item['packet_state']} outcome={item['packet_outcome'] or 'none'} hooks={hooks} blocking={blocks}")
                if item["verification"] == "request":
                    print(f"REQUEST .\\scripts\\python.ps1 scripts\\verification.py new --date {args.date} --slug \"{item['claim']}\"")
            for item in payload["unknown_dependencies"]:
                print(f"FAIL unknown forecast dependency {item}")
        return
    failures = close_packet(args.packet_id)
    print(f"verification_failures={len(failures)}")
    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

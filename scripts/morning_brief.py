"""Validate and render a fresh internal global morning update receipt."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import forecast_ledger
import reality


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
DAILY_ROOT = NG_ROOT / "work" / "daily"
LEDGER_PATH = NG_ROOT / "work" / "forecasts" / "forecast-ledger.md"
BRIEF_ROOT = NG_ROOT / "work" / "morning-brief"
REALITY_ROOT = NG_ROOT / "work" / "reality"
try:
    MOUNTAIN_TIME = ZoneInfo("America/Denver")
except ZoneInfoNotFoundError:  # Windows embeddable Python may omit the tzdata wheel.
    MOUNTAIN_TIME = None
SCHEMA_VERSION = "2.1"
RENDERER_VERSION = "2.1"
MAX_RECEIPT_BYTES = 512 * 1024
MAX_DEVELOPMENTS = 4
LOOKBACK_DAYS = 30
PROTECTED_CANONICAL_DATES = {"2026-08-02"}
IMPACTS = {"strengthens", "weakens", "complicates", "no-material-effect"}
FORECAST_IMPACTS = IMPACTS | {"unaffected"}
SOURCE_TYPES = {"official", "primary", "wire", "attributed-reporting"}
FRESHNESS_STATES = {"fresh", "stale", "unknown"}
DISPOSITIONS = {"included", "related", "hold", "excluded"}
RELATED_RELATIONSHIPS = {"corroborates", "qualifies", "disputes"}
RELATED_LABELS = {
    "corroborates": "Corroboration",
    "qualifies": "Qualification",
    "disputes": "Disagreement",
}
GAP_TYPES = {"stale", "missing", "failed", "thin", "outside-coverage"}
FORBIDDEN_RECEIPT_KEYS = {
    "body",
    "raw_body",
    "full_text",
    "source_text",
    "transcript",
    "excerpt",
}
PLACEHOLDER_RE = re.compile(
    r"(?:\[[^\]]+\]|<[^>]+>|\b(?:TODO|TBD|TBC)\b|YYYY(?:-MM-DD|MMDD)?)",
    re.IGNORECASE,
)
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ID_RE = re.compile(r"^[A-Z][A-Z0-9-]{2,63}$")
VERIFIED_RE = re.compile(r"\bverified\b", re.IGNORECASE)
REALITY_MATCH_STATUSES = {"exact", "contextual", "none"}
REALITY_RELATIONSHIPS = {"same-observable", "context-only", "forecast-dependency"}
CONTESTED_OUTCOMES = {
    "contested",
    "contested_attribution",
    "mixed",
    "unresolved",
    "unresolvable",
}
CHALLENGED_OUTCOMES = {
    "disconfirmed",
    "miss",
    "weakened",
    "superseded",
    "obsolete",
    "excluded",
}


class BriefError(ValueError):
    """The receipt or destination violates the morning-update contract."""


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise BriefError(f"{label} has unknown or missing fields")


def exact_keys_with_optional(
    value: dict[str, Any], required: set[str], optional: set[str], label: str
) -> None:
    keys = set(value)
    if not required <= keys or not keys <= required | optional:
        raise BriefError(f"{label} has unknown or missing fields")


def object_value(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BriefError(f"{label} must be an object")
    return value


def list_value(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise BriefError(f"{label} must be a list")
    return value


def bool_value(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise BriefError(f"{label} must be a boolean")
    return value


def int_value(value: Any, label: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise BriefError(f"{label} must be an integer >= {minimum}")
    return value


def text_value(
    value: Any,
    label: str,
    *,
    maximum: int = 2_000,
    allow_placeholder: bool = False,
) -> str:
    if not isinstance(value, str):
        raise BriefError(f"{label} must be text")
    candidate = value.strip()
    if (
        not candidate
        or len(candidate) > maximum
        or "\n" in candidate
        or "\r" in candidate
        or (not allow_placeholder and PLACEHOLDER_RE.search(candidate))
    ):
        raise BriefError(f"{label} is blank, unsafe, placeholder, or too long")
    return candidate


def exact_date(raw: Any, label: str) -> dt.date:
    value = text_value(raw, label, maximum=10)
    try:
        parsed = dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise BriefError(f"{label} must be an exact YYYY-MM-DD value") from error
    if parsed.isoformat() != value:
        raise BriefError(f"{label} must be an exact YYYY-MM-DD value")
    return parsed


def rfc3339(raw: Any, label: str) -> dt.datetime:
    value = text_value(raw, label, maximum=40)
    if not RFC3339_RE.fullmatch(value):
        raise BriefError(f"{label} must be an RFC3339 timestamp with an offset")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise BriefError(f"{label} must be an RFC3339 timestamp") from error
    if parsed.tzinfo is None:
        raise BriefError(f"{label} must include a timezone")
    return parsed.astimezone(dt.timezone.utc)


def utc_text(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def mountain_local(value: dt.datetime) -> dt.datetime:
    if MOUNTAIN_TIME is not None:
        return value.astimezone(MOUNTAIN_TIME)
    year = value.year
    march_first = dt.date(year, 3, 1)
    second_sunday = 8 + ((6 - march_first.weekday()) % 7)
    november_first = dt.date(year, 11, 1)
    first_sunday = 1 + ((6 - november_first.weekday()) % 7)
    dst_start = dt.datetime(year, 3, second_sunday, 9, tzinfo=dt.timezone.utc)
    dst_end = dt.datetime(year, 11, first_sunday, 8, tzinfo=dt.timezone.utc)
    if dst_start <= value.astimezone(dt.timezone.utc) < dst_end:
        zone = dt.timezone(dt.timedelta(hours=-6), "MDT")
    else:
        zone = dt.timezone(dt.timedelta(hours=-7), "MST")
    return value.astimezone(zone)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def unwrap(value: str) -> str:
    candidate = value.strip()
    if len(candidate) >= 2 and candidate.startswith("`") and candidate.endswith("`"):
        candidate = candidate[1:-1].strip()
    return candidate


def markdown_section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return ""
    tail = text[match.end() :]
    next_heading = re.search(r"^## ", tail, re.MULTILINE)
    return tail[: next_heading.start() if next_heading else len(tail)].strip()


def labeled_line(text: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+?)\s*$", text, re.MULTILINE)
    return unwrap(match.group(1)) if match else ""


def completed_repository_value(value: str) -> bool:
    return bool(
        value
        and value not in {"-", "—"}
        and not PLACEHOLDER_RE.search(value)
        and not any(marker in value for marker in ("Ã", "Â", "â€"))
    )


def relative_path(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def expected_judgments(
    brief_date: dt.date,
    *,
    repo_root: Path = REPO_ROOT,
    daily_root: Path | None = None,
) -> list[dict[str, Any]]:
    root = daily_root or repo_root / "narrative-geopolitics" / "work" / "daily"
    earliest = brief_date - dt.timedelta(days=LOOKBACK_DAYS)
    rows: list[dict[str, Any]] = []
    if not root.is_dir():
        return rows
    for run_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        try:
            run_date = dt.datetime.strptime(run_dir.name, "%Y-%m-%d").date()
        except ValueError:
            continue
        if not earliest <= run_date < brief_date:
            continue
        path = run_dir / "judgment.md"
        if not path.is_file():
            continue
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeError:
            continue
        status = labeled_line(text, "Status")
        as_of = labeled_line(text, "As-of")
        crisis_object = labeled_line(text, "Crisis object")
        compression = markdown_section(text, "Decision Compression")
        summary = labeled_line(compression, "What changed")
        required = (
            status,
            as_of,
            crisis_object,
            summary,
            labeled_line(compression, "Reusable mechanism"),
            labeled_line(compression, "Decision implication"),
            labeled_line(compression, "Evidence still missing"),
            labeled_line(compression, "Recommended disposition"),
        )
        if status == "template" or as_of != run_dir.name:
            continue
        if not all(completed_repository_value(item) for item in required):
            continue
        rows.append(
            {
                "model_id": f"JUDG-{run_date.strftime('%Y%m%d')}",
                "path": relative_path(path, repo_root),
                "sha256": sha256_bytes(raw),
                "as_of": as_of,
                "crisis_object": crisis_object,
                "summary": summary,
            }
        )
    return rows


def expected_forecasts(
    brief_date: dt.date,
    *,
    repo_root: Path = REPO_ROOT,
    ledger_path: Path | None = None,
) -> list[dict[str, Any]]:
    path = ledger_path or repo_root / "narrative-geopolitics" / "work" / "forecasts" / "forecast-ledger.md"
    if not path.is_file():
        raise BriefError("forecast ledger is missing")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise BriefError("forecast ledger is not valid UTF-8") from error
    entries = {row.hook_id: row for row in forecast_ledger.parse_entries(text)}
    triage = {row.hook_id: row for row in forecast_ledger.parse_triage(text)}
    ledger_hash = sha256_bytes(raw)
    ledger_relative = relative_path(path, repo_root)
    rows: list[dict[str, Any]] = []
    for hook_id in sorted(entries):
        entry = entries[hook_id]
        review = triage.get(hook_id)
        if not review or not review.accountable or review.resolution_status != "open":
            continue
        rows.append(
            {
                "hook_id": hook_id,
                "run_date": entry.run_date,
                "crisis_object": entry.crisis_object,
                "claim": entry.claim,
                "probability_band": entry.probability_band,
                "review_date": entry.review_date,
                "source_path": ledger_relative,
                "sha256": ledger_hash,
                "status": "open",
                "accountable": True,
                "due": entry.review_date <= brief_date.isoformat(),
            }
        )
    return rows


def duplicate_safe_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BriefError("receipt contains duplicate JSON keys")
        result[key] = value
    return result


def reject_full_source_bodies(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.lower() in FORBIDDEN_RECEIPT_KEYS:
                raise BriefError(f"receipt may not retain full source field: {key}")
            reject_full_source_bodies(nested)
    elif isinstance(value, list):
        for nested in value:
            reject_full_source_bodies(nested)


def load_receipt(path: Path) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError as error:
        raise BriefError(f"receipt cannot be read: {path}") from error
    if size > MAX_RECEIPT_BYTES:
        raise BriefError("receipt exceeds the size limit")
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=duplicate_safe_object
        )
    except BriefError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise BriefError("receipt must be valid UTF-8 JSON") from error
    payload = object_value(payload, "receipt")
    reject_full_source_bodies(payload)
    return payload


def validate_string_list(
    value: Any, label: str, *, minimum: int = 0, maximum: int = 100
) -> list[str]:
    rows = list_value(value, label)
    if not minimum <= len(rows) <= maximum:
        raise BriefError(f"{label} must contain {minimum}-{maximum} values")
    rendered = [text_value(item, f"{label} item", maximum=200) for item in rows]
    if len(rendered) != len(set(rendered)):
        raise BriefError(f"{label} contains duplicates")
    return rendered


def validate_baseline(
    baseline: Any,
    brief_date: dt.date,
    *,
    repo_root: Path,
    daily_root: Path | None,
    ledger_path: Path | None,
) -> tuple[set[str], set[str], list[dict[str, Any]]]:
    block = object_value(baseline, "baseline")
    exact_keys(block, {"lookback_days", "judgments", "forecasts"}, "baseline")
    if int_value(block["lookback_days"], "baseline.lookback_days") != LOOKBACK_DAYS:
        raise BriefError("baseline lookback must be 30 days")
    judgments = list_value(block["judgments"], "baseline.judgments")
    expected_judgment_rows = expected_judgments(
        brief_date, repo_root=repo_root, daily_root=daily_root
    )
    if judgments != expected_judgment_rows:
        raise BriefError("receipt judgment baseline does not match current repository state")
    forecasts = list_value(block["forecasts"], "baseline.forecasts")
    expected_forecast_rows = expected_forecasts(
        brief_date, repo_root=repo_root, ledger_path=ledger_path
    )
    if len(forecasts) != len(expected_forecast_rows):
        raise BriefError("receipt forecast baseline is incomplete")
    expected_by_id = {row["hook_id"]: row for row in expected_forecast_rows}
    validated_forecasts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(forecasts):
        row = object_value(raw, f"baseline.forecasts[{index}]")
        exact_keys(
            row,
            set(expected_forecast_rows[0]) | {"impact"}
            if expected_forecast_rows
            else {"impact"},
            f"baseline.forecasts[{index}]",
        )
        hook_id = text_value(row.get("hook_id"), "forecast hook_id", maximum=32)
        expected = expected_by_id.get(hook_id)
        comparable = {key: value for key, value in row.items() if key != "impact"}
        if not expected or comparable != expected:
            raise BriefError(f"forecast baseline mismatch: {hook_id}")
        impact = text_value(row["impact"], f"forecast impact {hook_id}", maximum=32)
        if impact not in FORECAST_IMPACTS:
            raise BriefError(f"invalid forecast impact: {hook_id}")
        if hook_id in seen:
            raise BriefError(f"duplicate forecast baseline row: {hook_id}")
        seen.add(hook_id)
        validated_forecasts.append(row)
    if seen != set(expected_by_id):
        raise BriefError("receipt forecast baseline does not match current repository state")
    model_ids = {row["model_id"] for row in judgments}
    forecast_ids = set(expected_by_id)
    return model_ids, forecast_ids, validated_forecasts


def validate_upstream(value: Any, label: str, *, required: bool) -> dict[str, Any] | None:
    if value is None:
        if required:
            raise BriefError(f"{label} requires recovered upstream evidence")
        return None
    row = object_value(value, label)
    exact_keys(
        row,
        {"provider", "url", "source_type", "lineage_root", "freshness"},
        label,
    )
    provider = text_value(row["provider"], f"{label}.provider", maximum=200)
    url = text_value(row["url"], f"{label}.url", maximum=2_000, allow_placeholder=True)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise BriefError(f"{label}.url must be an HTTP(S) upstream URL")
    source_type = text_value(row["source_type"], f"{label}.source_type", maximum=32)
    if source_type not in SOURCE_TYPES:
        raise BriefError(f"{label}.source_type is not an allowed upstream type")
    text_value(row["lineage_root"], f"{label}.lineage_root", maximum=300)
    freshness = text_value(row["freshness"], f"{label}.freshness", maximum=16)
    if freshness not in FRESHNESS_STATES:
        raise BriefError(f"{label}.freshness is invalid")
    if required and freshness != "fresh":
        raise BriefError(f"{label} must be fresh for inclusion")
    return row


def reality_lattice_snapshot(
    claim_refs: list[str], *, repo_root: Path, reality_root: Path
) -> tuple[list[str], dict[str, Any], list[dict[str, str]], list[dict[str, Any]]]:
    """Read the controlling claim/assessment state without changing the lattice."""
    states: list[dict[str, Any]] = []
    assessment_refs: list[str] = []
    audits: list[dict[str, Any]] = []
    paths: dict[str, dict[str, str]] = {}
    for claim_id in claim_refs:
        try:
            audit = reality.audit_payload(claim_id, reality_root)
            # Keep the impact traversal explicit: the brief consumes it read-only and
            # never writes its result into lattice or forecast state.
            reality.impact_payload(claim_id, reality_root)
        except reality.RealityError as error:
            raise BriefError(f"unknown or unreadable Reality Check claim: {claim_id}") from error
        audits.append(audit)
        state = audit["epistemic_state"]
        states.append(
            {
                "claim_id": claim_id,
                "assessment_id": state["assessment_id"],
                "assessment_status": state["assessment_status"],
                "outcome": state["outcome"],
                "canonical": state["canonical"],
            }
        )
        claim_path = reality.record_path("claim", claim_id, reality_root)
        for path in (claim_path,):
            relative = relative_path(path, repo_root)
            paths[relative] = {"path": relative, "sha256": sha256_bytes(path.read_bytes())}
        assessment_id = state["assessment_id"]
        if assessment_id:
            assessment_refs.append(assessment_id)
            assessment_path = reality.record_path("assessment", assessment_id, reality_root)
            relative = relative_path(assessment_path, repo_root)
            paths[relative] = {
                "path": relative,
                "sha256": sha256_bytes(assessment_path.read_bytes()),
            }
    return (
        assessment_refs,
        {"status": "matched", "claims": states},
        [paths[path] for path in sorted(paths)],
        audits,
    )


def validate_reality_reference(
    value: Any,
    label: str,
    *,
    repo_root: Path,
    reality_root: Path,
    research_retrieved: dt.datetime,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    block = object_value(value, label)
    exact_keys(
        block,
        {
            "match_status",
            "claim_refs",
            "assessment_refs",
            "epistemic_state",
            "relationship",
            "lattice_paths",
            "audited_at_utc",
            "confidence_effect",
        },
        label,
    )
    match_status = text_value(block["match_status"], f"{label}.match_status", maximum=16)
    if match_status not in REALITY_MATCH_STATUSES:
        raise BriefError(f"{label}.match_status is invalid")
    relationship = text_value(block["relationship"], f"{label}.relationship", maximum=24)
    if relationship not in REALITY_RELATIONSHIPS:
        raise BriefError(f"{label}.relationship is invalid")
    claim_refs = validate_string_list(block["claim_refs"], f"{label}.claim_refs", maximum=20)
    for claim_id in claim_refs:
        if not reality.ID_PATTERNS["claim"].fullmatch(claim_id):
            raise BriefError(f"{label} has an invalid lattice claim ID: {claim_id}")
    audited_at = rfc3339(block["audited_at_utc"], f"{label}.audited_at_utc")
    if audited_at > research_retrieved:
        raise BriefError(f"{label} audit time is later than research retrieval")
    confidence_effect = text_value(
        block["confidence_effect"], f"{label}.confidence_effect", maximum=800
    )

    if match_status == "none":
        if claim_refs or block["assessment_refs"] or block["lattice_paths"]:
            raise BriefError(f"{label} not-in-lattice state cannot cite lattice records")
        if block["epistemic_state"] != {"status": "not-in-lattice", "claims": []}:
            raise BriefError(f"{label} must record not-in-lattice epistemic state")
        if relationship == "same-observable":
            raise BriefError(f"{label} absent match cannot be same-observable")
        return block, []

    if not claim_refs:
        raise BriefError(f"{label} matched state requires claim_refs")
    if match_status == "exact" and relationship != "same-observable":
        raise BriefError(f"{label} exact match must be same-observable")
    if match_status == "contextual" and relationship == "same-observable":
        raise BriefError(f"{label} contextual match cannot masquerade as same-observable")

    expected_assessments, expected_state, expected_paths, audits = reality_lattice_snapshot(
        claim_refs, repo_root=repo_root, reality_root=reality_root
    )
    if block["assessment_refs"] != expected_assessments:
        raise BriefError(f"{label} assessment_refs do not match current lattice state")
    if block["epistemic_state"] != expected_state:
        raise BriefError(f"{label} epistemic_state does not match current lattice state")
    if block["lattice_paths"] != expected_paths:
        raise BriefError(f"{label} lattice paths or hashes do not match current state")

    if match_status == "exact":
        outcomes = {audit["epistemic_state"]["outcome"] for audit in audits}
        states = {audit["epistemic_state"]["assessment_status"] for audit in audits}
        boundary = confidence_effect.lower()
        if outcomes & CONTESTED_OUTCOMES and "contest" not in boundary:
            raise BriefError(f"{label} contested exact match requires qualified language")
        if outcomes & CHALLENGED_OUTCOMES and not any(
            word in boundary for word in ("challeng", "disconfirm", "not support", "miss")
        ):
            raise BriefError(f"{label} challenged exact match cannot render as settled fact")
        if None in outcomes or states & {"draft", "provisional_assessed", "unassessed"}:
            if not any(word in boundary for word in ("provisional", "unassessed", "not canonical")):
                raise BriefError(f"{label} provisional exact match must constrain confidence")
    return block, audits


def permits_verified_language(
    match_status: str, relationship: str, audits: list[dict[str, Any]]
) -> bool:
    if match_status != "exact" or relationship != "same-observable" or not audits:
        return False
    return all(
        audit["epistemic_state"]["canonical"]
        and audit["epistemic_state"]["outcome"] in reality.POSITIVE_EMPIRICAL_OUTCOMES
        and not audit["validation_failures"]
        for audit in audits
    )


def validate_receipt(
    payload: dict[str, Any],
    *,
    date: str,
    as_of: str,
    repo_root: Path = REPO_ROOT,
    daily_root: Path | None = None,
    ledger_path: Path | None = None,
    reality_root: Path | None = None,
) -> dict[str, Any]:
    exact_keys(
        payload,
        {
            "schema_version",
            "renderer_version",
            "brief_date",
            "as_of_utc",
            "window",
            "research",
            "coverage",
            "morning_judgment",
            "material_change",
            "baseline",
            "candidates",
            "gaps",
            "selected_development_ids",
            "selected_outlier_or_gap",
            "watch",
        },
        "receipt",
    )
    if payload["schema_version"] != SCHEMA_VERSION:
        raise BriefError(f"receipt schema_version must be {SCHEMA_VERSION}")
    if payload["renderer_version"] != RENDERER_VERSION:
        raise BriefError(f"receipt renderer_version must be {RENDERER_VERSION}")
    brief_date = exact_date(date, "--date")
    if exact_date(payload["brief_date"], "receipt.brief_date") != brief_date:
        raise BriefError("receipt brief_date does not match --date")
    cli_as_of = rfc3339(as_of, "--as-of")
    receipt_as_of = rfc3339(payload["as_of_utc"], "receipt.as_of_utc")
    if cli_as_of != receipt_as_of or payload["as_of_utc"] != utc_text(receipt_as_of):
        raise BriefError("receipt as_of_utc must be canonical UTC and match --as-of")

    window = object_value(payload["window"], "window")
    exact_keys(window, {"start_utc", "end_utc", "hours"}, "window")
    start = rfc3339(window["start_utc"], "window.start_utc")
    end = rfc3339(window["end_utc"], "window.end_utc")
    if int_value(window["hours"], "window.hours") != 24:
        raise BriefError("morning brief observation window must be 24 hours")
    if end != receipt_as_of or start != end - dt.timedelta(hours=24):
        raise BriefError("receipt window must be the 24 hours ending at as_of_utc")

    research = object_value(payload["research"], "research")
    exact_keys(
        research,
        {"mode", "geography", "output", "stop_condition", "retrieved_at_utc"},
        "research",
    )
    if research["mode"] != "scan" or research["geography"] != "global":
        raise BriefError("research must be a global scan")
    if research["output"] != "five-minute-selective-global-update":
        raise BriefError("research output contract is invalid")
    text_value(research["stop_condition"], "research.stop_condition", maximum=500)
    retrieved = rfc3339(research["retrieved_at_utc"], "research.retrieved_at_utc")
    if not start <= retrieved <= end:
        raise BriefError("research retrieval time is outside the observation window")

    coverage = object_value(payload["coverage"], "coverage")
    exact_keys(
        coverage,
        {
            "scope",
            "retrieval_status",
            "geographies",
            "domains",
            "upstream_sources_reviewed",
            "lineage_roots_reviewed",
            "limitations",
        },
        "coverage",
    )
    if coverage["scope"] != "selective-global":
        raise BriefError("coverage scope must be selective-global")
    if coverage["retrieval_status"] != "healthy":
        raise BriefError("retrieval coverage is not healthy; fail closed")
    geographies = validate_string_list(
        coverage["geographies"], "coverage.geographies", minimum=3, maximum=30
    )
    domains = validate_string_list(
        coverage["domains"], "coverage.domains", minimum=2, maximum=30
    )
    reviewed_sources = int_value(
        coverage["upstream_sources_reviewed"],
        "coverage.upstream_sources_reviewed",
        minimum=3,
    )
    reviewed_lineages = int_value(
        coverage["lineage_roots_reviewed"],
        "coverage.lineage_roots_reviewed",
        minimum=3,
    )
    validate_string_list(
        coverage["limitations"], "coverage.limitations", minimum=1, maximum=20
    )

    model_ids, forecast_ids, forecasts = validate_baseline(
        payload["baseline"],
        brief_date,
        repo_root=repo_root,
        daily_root=daily_root,
        ledger_path=ledger_path,
    )

    material_change = bool_value(payload["material_change"], "material_change")
    morning_judgment = text_value(
        payload["morning_judgment"], "morning_judgment", maximum=1_500
    )
    if not material_change and "no material change" not in morning_judgment.lower():
        raise BriefError("no-change receipts must state no material change")

    candidates = list_value(payload["candidates"], "candidates")
    if not candidates:
        raise BriefError("receipt must record considered candidates")
    candidate_by_id: dict[str, dict[str, Any]] = {}
    upstream_providers: set[str] = set()
    lineage_roots: set[str] = set()
    for index, raw in enumerate(candidates):
        row = object_value(raw, f"candidates[{index}]")
        exact_keys_with_optional(
            row,
            {
                "id",
                "kind",
                "title",
                "geography",
                "domain",
                "observed_at_utc",
                "retrieved_at_utc",
                "observation",
                "interpretation",
                "materiality",
                "model_refs",
                "forecast_refs",
                "impact",
                "confidence_boundary",
                "discovery",
                "upstream",
                "related_observations",
                "disposition",
                "selection_reason",
            },
            {"reality"},
            f"candidates[{index}]",
        )
        candidate_id = text_value(row["id"], "candidate id", maximum=64)
        if not ID_RE.fullmatch(candidate_id) or candidate_id in candidate_by_id:
            raise BriefError(f"invalid or duplicate candidate id: {candidate_id}")
        kind = text_value(row["kind"], f"{candidate_id}.kind", maximum=16)
        if kind not in {"development", "outlier"}:
            raise BriefError(f"invalid candidate kind: {candidate_id}")
        for field, maximum in (
            ("title", 200),
            ("observation", 1_000),
            ("interpretation", 1_000),
            ("materiality", 800),
            ("confidence_boundary", 800),
            ("selection_reason", 500),
        ):
            text_value(row[field], f"{candidate_id}.{field}", maximum=maximum)
        geography = text_value(row["geography"], f"{candidate_id}.geography", maximum=100)
        domain = text_value(row["domain"], f"{candidate_id}.domain", maximum=100)
        if geography not in geographies or domain not in domains:
            raise BriefError(f"candidate outside declared coverage: {candidate_id}")
        observed = rfc3339(row["observed_at_utc"], f"{candidate_id}.observed_at_utc")
        candidate_retrieved = rfc3339(
            row["retrieved_at_utc"], f"{candidate_id}.retrieved_at_utc"
        )
        if not start <= observed <= end or not observed <= candidate_retrieved <= end:
            raise BriefError(f"candidate timestamps outside observation contract: {candidate_id}")
        discovery = object_value(row["discovery"], f"{candidate_id}.discovery")
        exact_keys(discovery, {"provider", "reference", "is_evidence"}, "discovery")
        text_value(discovery["provider"], "discovery.provider", maximum=200)
        text_value(
            discovery["reference"],
            "discovery.reference",
            maximum=2_000,
            allow_placeholder=True,
        )
        if bool_value(discovery["is_evidence"], "discovery.is_evidence"):
            raise BriefError("discovery surfaces must never be marked as evidence")
        disposition = text_value(row["disposition"], f"{candidate_id}.disposition", maximum=16)
        if disposition not in DISPOSITIONS:
            raise BriefError(f"invalid candidate disposition: {candidate_id}")
        upstream = validate_upstream(
            row["upstream"],
            f"{candidate_id}.upstream",
            required=disposition in {"included", "related"},
        )
        if upstream:
            upstream_providers.add(upstream["provider"])
            lineage_roots.add(upstream["lineage_root"])
        model_refs = validate_string_list(
            row["model_refs"], f"{candidate_id}.model_refs", maximum=30
        )
        forecast_refs = validate_string_list(
            row["forecast_refs"], f"{candidate_id}.forecast_refs", maximum=30
        )
        if not set(model_refs) <= model_ids or not set(forecast_refs) <= forecast_ids:
            raise BriefError(f"candidate references unknown baseline state: {candidate_id}")
        impact = text_value(row["impact"], f"{candidate_id}.impact", maximum=32)
        if impact not in IMPACTS:
            raise BriefError(f"invalid model impact: {candidate_id}")
        related_observations = list_value(
            row["related_observations"], f"{candidate_id}.related_observations"
        )
        seen_related_ids: set[str] = set()
        for related_index, raw_related in enumerate(related_observations):
            related = object_value(
                raw_related, f"{candidate_id}.related_observations[{related_index}]"
            )
            exact_keys(
                related,
                {"candidate_id", "relationship"},
                f"{candidate_id}.related_observations[{related_index}]",
            )
            related_id = text_value(
                related["candidate_id"],
                f"{candidate_id}.related_observations[{related_index}].candidate_id",
                maximum=64,
            )
            if not ID_RE.fullmatch(related_id) or related_id in seen_related_ids:
                raise BriefError(f"invalid or duplicate related observation: {candidate_id}")
            seen_related_ids.add(related_id)
            relationship = text_value(
                related["relationship"],
                f"{candidate_id}.related_observations[{related_index}].relationship",
                maximum=16,
            )
            if relationship not in RELATED_RELATIONSHIPS:
                raise BriefError(f"invalid related-observation relationship: {candidate_id}")
        if disposition == "related":
            if model_refs or forecast_refs or impact != "no-material-effect":
                raise BriefError(
                    f"related candidate cannot carry inherited-state impact: {candidate_id}"
                )
            if related_observations:
                raise BriefError(f"related candidate cannot nest relationships: {candidate_id}")
        reality_audits: list[dict[str, Any]] = []
        reality_block = row.get("reality")
        if reality_block is not None:
            reality_block, reality_audits = validate_reality_reference(
                reality_block,
                f"{candidate_id}.reality",
                repo_root=repo_root,
                reality_root=reality_root
                or repo_root / "narrative-geopolitics" / "work" / "reality",
                research_retrieved=retrieved,
            )
            prose = " ".join(
                str(row[field])
                for field in (
                    "title",
                    "observation",
                    "interpretation",
                    "materiality",
                    "confidence_boundary",
                    "selection_reason",
                )
            )
            if VERIFIED_RE.search(prose) and not permits_verified_language(
                reality_block["match_status"],
                reality_block["relationship"],
                reality_audits,
            ):
                raise BriefError(
                    f"{candidate_id} cannot use verified without a controlling signed exact assessment"
                )
            if reality_block["match_status"] == "exact":
                outcomes = {
                    audit["epistemic_state"]["outcome"] for audit in reality_audits
                }
                reader_prose = " ".join(
                    str(row[field]).lower()
                    for field in ("observation", "interpretation", "confidence_boundary")
                )
                if outcomes & CONTESTED_OUTCOMES and not any(
                    marker in reader_prose
                    for marker in (
                        "contest",
                        "disput",
                        "uncertain",
                        "attribution",
                        "according to",
                        "reported",
                    )
                ):
                    raise BriefError(
                        f"{candidate_id} contested exact match must qualify reader-facing prose"
                    )
                if outcomes & CHALLENGED_OUTCOMES and not any(
                    marker in reader_prose
                    for marker in (
                        "challeng",
                        "disconfirm",
                        "disput",
                        "alleged",
                        "not support",
                        "reported",
                    )
                ):
                    raise BriefError(
                        f"{candidate_id} challenged formulation must preserve disagreement"
                    )
        candidate_by_id[candidate_id] = row
    if reviewed_sources != len(upstream_providers) or reviewed_lineages != len(lineage_roots):
        raise BriefError("coverage review counts do not match distinct upstream research")
    if len(upstream_providers) < 3 or len(lineage_roots) < 3:
        raise BriefError("minimum global upstream coverage was not recovered")

    selected_developments = validate_string_list(
        payload["selected_development_ids"],
        "selected_development_ids",
        maximum=MAX_DEVELOPMENTS,
    )
    if material_change != bool(selected_developments):
        raise BriefError("material_change must match selected developments")
    selected_ids: list[str] = []
    selected_development_forecast_refs: set[str] = set()
    for candidate_id in selected_developments:
        row = candidate_by_id.get(candidate_id)
        if not row or row["kind"] != "development" or row["disposition"] != "included":
            raise BriefError(f"selected development is not an included development: {candidate_id}")
        if not row["model_refs"] and not row["forecast_refs"]:
            raise BriefError(f"material development has no inherited-state reference: {candidate_id}")
        if row["impact"] == "no-material-effect":
            raise BriefError(f"selected development has no material effect: {candidate_id}")
        selected_development_forecast_refs.update(row["forecast_refs"])
        selected_ids.append(candidate_id)

    forecast_by_id = {row["hook_id"]: row for row in forecasts}
    referenced_unaffected = sorted(
        hook_id
        for hook_id in selected_development_forecast_refs
        if forecast_by_id[hook_id]["impact"] == "unaffected"
    )
    if referenced_unaffected:
        raise BriefError(
            "selected development references forecast(s) labeled unaffected: "
            + ", ".join(referenced_unaffected)
        )
    pressured_forecasts = {
        hook_id
        for hook_id, row in forecast_by_id.items()
        if row["impact"] != "unaffected"
    }
    unsupported_pressure = sorted(
        pressured_forecasts - selected_development_forecast_refs
    )
    if unsupported_pressure:
        raise BriefError(
            "pressured forecast lacks a selected material-development reference: "
            + ", ".join(unsupported_pressure)
        )

    gaps = list_value(payload["gaps"], "gaps")
    gap_by_id: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(gaps):
        row = object_value(raw, f"gaps[{index}]")
        exact_keys(
            row,
            {"id", "type", "geography", "domain", "description", "consequence", "disposition"},
            f"gaps[{index}]",
        )
        gap_id = text_value(row["id"], "gap id", maximum=64)
        if not ID_RE.fullmatch(gap_id) or gap_id in gap_by_id or gap_id in candidate_by_id:
            raise BriefError(f"invalid or duplicate gap id: {gap_id}")
        if row["type"] not in GAP_TYPES or row["disposition"] not in {"selected", "recorded"}:
            raise BriefError(f"invalid gap contract: {gap_id}")
        if row["geography"] not in geographies or row["domain"] not in domains:
            raise BriefError(f"gap outside declared coverage: {gap_id}")
        text_value(row["description"], f"{gap_id}.description", maximum=1_000)
        text_value(row["consequence"], f"{gap_id}.consequence", maximum=800)
        gap_by_id[gap_id] = row

    pointer = object_value(payload["selected_outlier_or_gap"], "selected_outlier_or_gap")
    exact_keys(pointer, {"kind", "id"}, "selected_outlier_or_gap")
    pointer_kind = text_value(pointer["kind"], "selected_outlier_or_gap.kind", maximum=16)
    pointer_id = text_value(pointer["id"], "selected_outlier_or_gap.id", maximum=64)
    if pointer_kind == "candidate":
        row = candidate_by_id.get(pointer_id)
        if not row or row["kind"] != "outlier" or row["disposition"] != "included":
            raise BriefError("selected outlier is not an included outlier candidate")
        selected_ids.append(pointer_id)
        if any(gap["disposition"] == "selected" for gap in gaps):
            raise BriefError("only one outlier or gap may be selected")
    elif pointer_kind == "gap":
        row = gap_by_id.get(pointer_id)
        if not row or row["disposition"] != "selected":
            raise BriefError("selected gap is missing or not selected")
        if sum(gap["disposition"] == "selected" for gap in gaps) != 1:
            raise BriefError("exactly one visibility gap must be selected")
    else:
        raise BriefError("selected_outlier_or_gap.kind must be candidate or gap")

    included_ids = {
        candidate_id
        for candidate_id, row in candidate_by_id.items()
        if row["disposition"] == "included"
    }
    if included_ids != set(selected_ids):
        raise BriefError("every included candidate must be selected exactly once")
    referenced_related: set[str] = set()
    for candidate_id, row in candidate_by_id.items():
        relationships = row["related_observations"]
        if relationships and candidate_id not in selected_ids:
            raise BriefError(
                f"only selected candidates may reference related observations: {candidate_id}"
            )
        for relationship in relationships:
            related_id = relationship["candidate_id"]
            if related_id == candidate_id:
                raise BriefError(f"candidate cannot reference itself: {candidate_id}")
            related = candidate_by_id.get(related_id)
            if not related or related["disposition"] != "related":
                raise BriefError(
                    f"related observation is missing or has wrong disposition: {related_id}"
                )
            if related_id in referenced_related:
                raise BriefError(f"related observation is reused: {related_id}")
            referenced_related.add(related_id)
            if (
                relationship["relationship"] == "corroborates"
                and related["upstream"]["lineage_root"]
                == row["upstream"]["lineage_root"]
            ):
                raise BriefError(
                    f"corroborating observation shares upstream lineage: {related_id}"
                )
            if relationship["relationship"] == "disputes" and not any(
                marker in row["confidence_boundary"].lower()
                for marker in ("disput", "contest", "conflict", "deni")
            ):
                raise BriefError(
                    f"disputed observation requires a qualified confidence boundary: {candidate_id}"
                )
    declared_related = {
        candidate_id
        for candidate_id, row in candidate_by_id.items()
        if row["disposition"] == "related"
    }
    if declared_related != referenced_related:
        raise BriefError("every related candidate must be referenced exactly once")
    selected_lineages = [
        candidate_by_id[candidate_id]["upstream"]["lineage_root"]
        for candidate_id in selected_ids
    ]
    if len(selected_lineages) != len(set(selected_lineages)):
        raise BriefError("selected observations share one upstream lineage root")

    known_refs = (
        model_ids | forecast_ids | set(selected_ids) | referenced_related | set(gap_by_id)
    )
    watch = list_value(payload["watch"], "watch")
    seen_watch: set[str] = set()
    for index, raw in enumerate(watch):
        row = object_value(raw, f"watch[{index}]")
        exact_keys(row, {"id", "observable", "timing", "source_refs"}, f"watch[{index}]")
        watch_id = text_value(row["id"], "watch id", maximum=64)
        if not ID_RE.fullmatch(watch_id) or watch_id in seen_watch:
            raise BriefError(f"invalid or duplicate watch id: {watch_id}")
        seen_watch.add(watch_id)
        text_value(row["observable"], f"{watch_id}.observable", maximum=800)
        text_value(row["timing"], f"{watch_id}.timing", maximum=200)
        refs = validate_string_list(row["source_refs"], f"{watch_id}.source_refs", minimum=1)
        if not set(refs) <= known_refs:
            raise BriefError(f"watch item lacks a supported source reference: {watch_id}")

    payload["baseline"]["forecasts"] = forecasts
    return payload


def canonical_receipt(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def markdown_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def reality_note(row: dict[str, Any]) -> str:
    block = row.get("reality")
    if block is None:
        return "Reality Check: not consulted."
    if block["match_status"] == "none":
        return (
            "Reality Check: `not-in-lattice`. "
            f"{markdown_text(block['confidence_effect'])}"
        )
    states = []
    for state in block["epistemic_state"]["claims"]:
        outcome = state["outcome"] or "unassessed"
        authority = "canonical" if state["canonical"] else state["assessment_status"]
        states.append(f"`{state['claim_id']}`: `{outcome}` / `{authority}`")
    return (
        f"Reality Check: `{block['match_status']}` / `{block['relationship']}`; "
        f"{'; '.join(states)}. {markdown_text(block['confidence_effect'])}"
    )


def render_related_observations(
    row: dict[str, Any], candidates: dict[str, dict[str, Any]]
) -> list[str]:
    lines: list[str] = []
    for pointer in row["related_observations"]:
        related = candidates[pointer["candidate_id"]]
        upstream = related["upstream"]
        label = RELATED_LABELS[pointer["relationship"]]
        lines.extend(
            [
                "",
                f"**{label}:** {markdown_text(related['observation'])} "
                f"[{markdown_text(upstream['provider'])}](<{upstream['url']}>) "
                f"(`{upstream['source_type']}`).",
            ]
        )
    return lines


def render_markdown(payload: dict[str, Any], receipt_hash: str) -> bytes:
    as_of = rfc3339(payload["as_of_utc"], "as_of_utc")
    local_as_of = mountain_local(as_of).strftime("%Y-%m-%d %H:%M %Z")
    judgment_count = len(payload["baseline"]["judgments"])
    forecast_count = len(payload["baseline"]["forecasts"])
    lines = [
        f"# Morning Brief — {payload['brief_date']}",
        "",
        "Status: `experimental-internal-morning-update`",
        "",
        "## Frame",
        "",
        f"Read this as a selective five-minute internal update, frozen at "
        f"`{payload['as_of_utc']}` (`{local_as_of}`). The observation window runs "
        f"`{payload['window']['start_utc']}` to `{payload['window']['end_utc']}` · "
        f"coverage `selective-global`; receipt `{receipt_hash}`; baseline "
        f"`{judgment_count}` valid judgment(s), `{forecast_count}` accountable open forecast(s).",
        "",
        "## Morning Judgment",
        "",
        payload["morning_judgment"],
        "",
        "## Material Developments",
        "",
    ]
    candidates = {row["id"]: row for row in payload["candidates"]}
    selected_ids = list(payload["selected_development_ids"])
    if payload["selected_outlier_or_gap"]["kind"] == "candidate":
        selected_ids.append(payload["selected_outlier_or_gap"]["id"])
    if not payload["selected_development_ids"]:
        lines.extend(
            [
                "No material development cleared the selection threshold inside the observation contract.",
                "",
            ]
        )
    else:
        for candidate_id in payload["selected_development_ids"]:
            row = candidates[candidate_id]
            upstream = row["upstream"]
            lines.extend(
                [
                    f"### {markdown_text(row['title'])}",
                    "",
                    markdown_text(row["observation"]),
                    "",
                    f"**Material pressure:** {markdown_text(row['materiality'])}",
                    "",
                    f"**What it does to the model — `{row['impact']}`:** {markdown_text(row['interpretation'])}",
                    "",
                    f"**Boundary:** {markdown_text(row['confidence_boundary'])}",
                    "",
                    f"**Source:** [{markdown_text(upstream['provider'])}](<{upstream['url']}>) "
                    f"(`{upstream['source_type']}`).",
                ]
            )
            lines.extend(render_related_observations(row, candidates))
            lines.append("")

    lines.extend(["## Outlier or Visibility Gap", ""])
    pointer = payload["selected_outlier_or_gap"]
    if pointer["kind"] == "candidate":
        row = candidates[pointer["id"]]
        upstream = row["upstream"]
        lines.extend(
            [
                f"### {markdown_text(row['title'])}",
                "",
                markdown_text(row["observation"]),
                "",
                f"**Consequential potential:** {markdown_text(row['materiality'])}",
                "",
                f"**Boundary:** {markdown_text(row['confidence_boundary'])}",
                "",
                f"**Source:** [{markdown_text(upstream['provider'])}](<{upstream['url']}>) "
                f"(`{upstream['source_type']}`).",
            ]
        )
        lines.extend(render_related_observations(row, candidates))
        lines.append("")
    else:
        gaps = {row["id"]: row for row in payload["gaps"]}
        row = gaps[pointer["id"]]
        lines.extend(
            [
                f"### {markdown_text(row['geography'])} — {markdown_text(row['domain'])}",
                "",
                f"**Gap type:** `{row['type']}`",
                "",
                f"**Visibility limit:** {markdown_text(row['description'])}",
                "",
                f"**Consequence:** {markdown_text(row['consequence'])}",
                "",
            ]
        )

    lines.extend(["## Forecast Pressure", ""])
    forecast_rows = payload["baseline"]["forecasts"]
    if not forecast_rows:
        lines.extend(["No accountable open forecasts are present in the baseline.", ""])
    else:
        pressured = sorted(
            (row for row in forecast_rows if row["impact"] != "unaffected"),
            key=lambda row: (not row["due"], row["review_date"], row["hook_id"]),
        )
        due_without_pressure = sorted(
            (
                row
                for row in forecast_rows
                if row["due"] and row["impact"] == "unaffected"
            ),
            key=lambda row: (row["review_date"], row["hook_id"]),
        )
        unaffected_not_due = sum(
            not row["due"] and row["impact"] == "unaffected"
            for row in forecast_rows
        )

        def due_marker(row: dict[str, Any]) -> str | None:
            if not row["due"]:
                return None
            if row["review_date"] == payload["brief_date"]:
                return "due today"
            return f"overdue since `{row['review_date']}`"

        if not pressured and not due_without_pressure:
            lines.extend(
                [
                    "No accountable open forecast is due or materially pressured; "
                    f"`{unaffected_not_due}` remain unaffected.",
                    "",
                ]
            )
        else:
            if pressured:
                lines.extend(["### Pressured today", ""])
                for row in pressured:
                    marker = due_marker(row)
                    review = marker or f"review `{row['review_date']}`"
                    lines.append(
                        f"- {markdown_text(row['claim'])} **Pressure: `{row['impact']}`.** "
                        f"(`{row['hook_id']}`; {review})."
                    )
                lines.append("")
            else:
                lines.extend(
                    ["No accountable open forecast is materially pressured.", ""]
                )

            if due_without_pressure:
                lines.extend(["### Due, unpressured", ""])
                for row in due_without_pressure:
                    lines.append(
                        f"- {markdown_text(row['claim'])} **No new pressure.** "
                        f"(`{row['hook_id']}`; {due_marker(row)})."
                    )
                lines.append("")

            lines.extend(
                [
                    f"- `{unaffected_not_due}` unaffected, not-due forecast(s).",
                    "",
                ]
            )

    lines.extend(["## What to Watch", ""])
    if payload["watch"]:
        for row in payload["watch"]:
            lines.append(
                f"- {markdown_text(row['observable'])} **Timing:** {markdown_text(row['timing'])}."
            )
    else:
        lines.append("No additional supported discriminator was retained in this receipt.")
    lines.extend(["", "## Analyst's Note", ""])
    limitations = "; ".join(markdown_text(item) for item in payload["coverage"]["limitations"])
    lines.extend(
        [
            f"- Baseline: `{judgment_count}` valid judgment(s); `{forecast_count}` accountable open forecast(s).",
            f"- Coverage: `{payload['coverage']['upstream_sources_reviewed']}` upstream provider(s); "
            f"`{payload['coverage']['lineage_roots_reviewed']}` lineage root(s). Limitations: {limitations}",
        ]
    )
    technical_ids: list[str] = []
    for selected_id in selected_ids:
        technical_ids.append(selected_id)
        technical_ids.extend(
            pointer["candidate_id"] for pointer in candidates[selected_id]["related_observations"]
        )
    for candidate_id in technical_ids:
        row = candidates[candidate_id]
        refs = row["model_refs"] + row["forecast_refs"]
        affected = ", ".join(f"`{ref}`" for ref in refs) if refs else "none"
        relationships = ", ".join(
            f"`{pointer['candidate_id']}` (`{pointer['relationship']}`)"
            for pointer in row["related_observations"]
        )
        relationship_text = relationships or "none"
        lines.append(
            f"- `{candidate_id}` — `{markdown_text(row['geography'])}` / "
            f"`{markdown_text(row['domain'])}`; affected state: {affected}; "
            f"related observations: {relationship_text}; lineage "
            f"`{markdown_text(row['upstream']['lineage_root'])}`. {reality_note(row)}"
        )
    for row in payload["watch"]:
        refs = ", ".join(f"`{ref}`" for ref in row["source_refs"])
        lines.append(f"- `{row['id']}` support: {refs}.")
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            "This is a provisional internal update from a frozen research receipt. Discovery surfaces are leads, not evidence; included observations link to recovered upstream sources. Model-impact labels are pressure readings, not revisions to canonical judgment.",
            "",
            "It does not admit archive evidence, alter synthesis or judgment, register or resolve forecasts, create verification packets, authorize publication, or establish operational truth.",
            "",
        ]
    )
    rendered = "\n".join(lines)
    return rendered.encode("utf-8")


def stage_file(parent: Path, name: str, content: bytes) -> Path:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{name}.", suffix=".tmp", dir=parent)
    path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return path


def publish_pair(brief_path: Path, receipt_path: Path, brief: bytes, receipt: bytes) -> None:
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    staged_brief = stage_file(brief_path.parent, brief_path.name, brief)
    staged_receipt = stage_file(receipt_path.parent, receipt_path.name, receipt)
    original_brief = brief_path.read_bytes() if brief_path.exists() else None
    original_receipt = receipt_path.read_bytes() if receipt_path.exists() else None
    receipt_replaced = False
    try:
        os.replace(staged_receipt, receipt_path)
        receipt_replaced = True
        os.replace(staged_brief, brief_path)
    except BaseException:
        staged_brief.unlink(missing_ok=True)
        staged_receipt.unlink(missing_ok=True)
        if receipt_replaced:
            if original_receipt is None:
                receipt_path.unlink(missing_ok=True)
            else:
                restore = stage_file(receipt_path.parent, receipt_path.name, original_receipt)
                os.replace(restore, receipt_path)
        if original_brief is not None and brief_path.read_bytes() != original_brief:
            restore = stage_file(brief_path.parent, brief_path.name, original_brief)
            os.replace(restore, brief_path)
        raise


def generate_brief(
    date: str,
    as_of: str,
    receipt_input: Path,
    *,
    repo_root: Path = REPO_ROOT,
    daily_root: Path | None = None,
    ledger_path: Path | None = None,
    reality_root: Path | None = None,
    brief_root: Path = BRIEF_ROOT,
    overwrite: bool = False,
) -> tuple[Path, Path]:
    exact_date(date, "--date")
    canonical_root = brief_root.resolve() == BRIEF_ROOT.resolve()
    if canonical_root and date in PROTECTED_CANONICAL_DATES:
        raise BriefError(f"historical morning-brief specimen is protected: {date}")
    brief_path = brief_root / f"{date}.md"
    receipt_path = brief_root / f"{date}.receipt.json"
    existing = [path for path in (brief_path, receipt_path) if path.exists()]
    if existing and not overwrite:
        raise BriefError("canonical morning-brief pair exists; use --overwrite")
    payload = validate_receipt(
        load_receipt(receipt_input),
        date=date,
        as_of=as_of,
        repo_root=repo_root,
        daily_root=daily_root,
        ledger_path=ledger_path,
        reality_root=reality_root,
    )
    receipt_bytes = canonical_receipt(payload)
    receipt_hash = sha256_bytes(receipt_bytes)
    brief_bytes = render_markdown(payload, receipt_hash)
    publish_pair(brief_path, receipt_path, brief_bytes, receipt_bytes)
    return brief_path, receipt_path


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render an internal global morning update from a frozen research receipt."
    )
    parser.add_argument("--date", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(arguments)
    try:
        brief_path, receipt_path = generate_brief(
            args.date,
            args.as_of,
            args.receipt,
            overwrite=args.overwrite,
        )
    except BriefError as error:
        print(f"morning-brief: {error}", file=sys.stderr)
        return 1
    print(f"Generated {brief_path} and {receipt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Iterable


SCHEMA_VERSION = "1.1"
SCOPE = "narrative-geopolitics"
VOICE_TIERS = ("tier_a", "tier_b")
VOICE_FLOORS = {"tier_a": 5, "tier_b": 0}
CADENCES = {"daily", "weekly", "manual"}
ASR_DISPOSITIONS = {"repaired", "not-needed", "needs-repair", "blocked"}
ATTRIBUTION_DISPOSITIONS = {"confirmed-solo", "turn-labeled", "partial", "unknown"}
SECTIONING_DISPOSITIONS = {"sectioned", "preserved-unsectioned"}
QUOTATION_DISPOSITIONS = {"ready", "restricted", "not-ready"}
ACCEPTED_RECEIPT_DISPOSITIONS = {"accepted"}
SCORE_SCHEMA_VERSION = "completeness-score-v1"
SCORE_WEIGHTS = {
    "integrity": 15,
    "daily_coverage": 15,
    "voice_representation": 15,
    "tier_b_channels": 15,
    "processing": 20,
    "issue_readiness": 15,
    "diversity_disposition": 5,
}


class CompletenessError(ValueError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CompletenessError(f"invalid completeness JSON: {path}") from error
    if not isinstance(value, dict):
        raise CompletenessError(f"completeness contract must be an object: {path}")
    return value


def _read_receipts(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    receipts: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            raise CompletenessError(f"invalid completeness receipt at {path}:{line_number}") from error
        if not isinstance(value, dict):
            raise CompletenessError(f"completeness receipt must be an object at {path}:{line_number}")
        receipts.append(value)
    return receipts


def _timestamp(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CompletenessError(f"{label} must be a timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise CompletenessError(f"{label} must use ISO-8601") from error
    if parsed.tzinfo is None:
        raise CompletenessError(f"{label} must include a timezone")
    return value


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CompletenessError(f"{label} must be a non-empty string")
    return value.strip()


def _known_voices(repo_root: Path) -> set[str]:
    root = repo_root / "narrative-geopolitics" / "voices"
    return {item.name for item in root.iterdir() if item.is_dir() and item.name != "comparisons"} if root.is_dir() else set()


def _known_tier_b_channels(repo_root: Path) -> set[str]:
    policy = repo_root / "narrative-geopolitics" / "work" / "capture" / "youtube" / "youtube-capture-policy.yml"
    if not policy.is_file():
        return set()
    channels: set[str] = set()
    in_channels = False
    current: str | None = None
    for line in policy.read_text(encoding="utf-8").splitlines():
        if line == "channels:":
            in_channels = True
            continue
        if not in_channels:
            continue
        if line and not line.startswith(" "):
            break
        if line.startswith("  ") and not line.startswith("    ") and line.rstrip().endswith(":"):
            current = line.strip()[:-1]
        elif current and line.strip() == "tier: B":
            channels.add(current)
    return channels


def validate_contract(contract: dict[str, Any], *, month: str, repo_root: Path) -> dict[str, Any]:
    if contract.get("schema_version") != SCHEMA_VERSION:
        raise CompletenessError("unsupported monthly completeness schema_version")
    if contract.get("scope") != SCOPE:
        raise CompletenessError("monthly completeness scope must be narrative-geopolitics")
    if contract.get("month") != month:
        raise CompletenessError("monthly completeness contract month mismatch")
    _timestamp(contract.get("declared_at"), "declared_at")
    _nonempty(contract.get("reviewer"), "reviewer")
    if not isinstance(contract.get("frozen"), bool) or not isinstance(contract.get("late_declaration"), bool):
        raise CompletenessError("frozen and late_declaration must be booleans")
    floor = contract.get("daily_transcript_floor")
    if not isinstance(floor, int) or isinstance(floor, bool) or floor < 1:
        raise CompletenessError("daily_transcript_floor must be a positive integer")
    tiers = contract.get("voice_tiers")
    if not isinstance(tiers, dict) or set(tiers) != set(VOICE_TIERS):
        raise CompletenessError("voice_tiers must contain tier_a and tier_b")
    if contract.get("voice_tier_floors") != VOICE_FLOORS:
        raise CompletenessError("voice_tier_floors must set tier_a to 5 and tier_b to 0")
    known_voices = _known_voices(repo_root)
    seen: set[str] = set()
    for tier in VOICE_TIERS:
        values = tiers[tier]
        if not isinstance(values, list) or any(not isinstance(item, str) or not item for item in values):
            raise CompletenessError(f"voice_tiers.{tier} must be a string list")
        duplicates = seen.intersection(values)
        if duplicates:
            raise CompletenessError(f"voice appears in multiple tiers: {sorted(duplicates)[0]}")
        unknown = set(values) - known_voices
        if unknown:
            raise CompletenessError(f"unknown Narrative Geopolitics voice: {sorted(unknown)[0]}")
        if len(values) != len(set(values)):
            raise CompletenessError(f"duplicate voice in {tier} tier")
        seen.update(values)
    channels = contract.get("tier_b_channels")
    if not isinstance(channels, list):
        raise CompletenessError("tier_b_channels must be a list")
    known_channels = _known_tier_b_channels(repo_root)
    seen_channels: set[str] = set()
    for item in channels:
        if not isinstance(item, dict):
            raise CompletenessError("tier_b_channels entries must be objects")
        slug = _nonempty(item.get("host_slug"), "tier_b_channels.host_slug")
        if slug not in known_channels:
            raise CompletenessError(f"unknown Narrative Geopolitics Tier B channel: {slug}")
        if slug in seen_channels:
            raise CompletenessError(f"duplicate Tier B channel: {slug}")
        seen_channels.add(slug)
        if item.get("expected_cadence") not in CADENCES:
            raise CompletenessError(f"invalid expected cadence for {slug}")
        minimum = item.get("transcript_floor")
        if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 0:
            raise CompletenessError(f"transcript_floor must be a non-negative integer for {slug}")
    if contract["frozen"]:
        if not tiers["tier_a"]:
            raise CompletenessError("frozen contract requires at least one Tier A voice")
        missing_channels = known_channels - seen_channels
        if missing_channels:
            raise CompletenessError(
                f"frozen contract omits Narrative Geopolitics Tier B channel: {sorted(missing_channels)[0]}"
            )
    if contract.get("exception_policy") != {"required": True}:
        raise CompletenessError("exception_policy.required must be true")
    if contract.get("diversity_policy") != {"required_disposition": True}:
        raise CompletenessError("diversity_policy.required_disposition must be true")
    return contract


def validate_receipt(receipt: dict[str, Any], *, month: str) -> dict[str, Any]:
    if receipt.get("schema_version") != SCHEMA_VERSION or receipt.get("month") != month:
        raise CompletenessError("receipt schema_version or month mismatch")
    target_type = receipt.get("target_type")
    if target_type not in {"day", "voice", "channel", "diversity"}:
        raise CompletenessError("receipt target_type must be day, voice, channel, or diversity")
    _nonempty(receipt.get("target"), "receipt target")
    _timestamp(receipt.get("observed_at"), "receipt observed_at")
    _nonempty(receipt.get("reviewer"), "receipt reviewer")
    if receipt.get("disposition") not in ACCEPTED_RECEIPT_DISPOSITIONS:
        raise CompletenessError("receipt disposition must be accepted")
    for key in ("candidates_checked", "excluded", "uncovered_lanes", "evidence_refs"):
        if not isinstance(receipt.get(key), list):
            raise CompletenessError(f"receipt {key} must be a list")
    if target_type != "diversity":
        if not receipt["candidates_checked"] or not receipt["evidence_refs"]:
            raise CompletenessError("shortfall receipt requires candidates_checked and evidence_refs")
        if not receipt["excluded"]:
            raise CompletenessError("shortfall receipt requires excluded candidates with reasons")
        for item in receipt["excluded"]:
            if not isinstance(item, dict) or not item.get("ref") or not item.get("reason"):
                raise CompletenessError("shortfall receipt exclusions require ref and reason")
    if target_type == "diversity":
        for key in ("crisis_objects", "concentration_review", "missing_disagreement"):
            if not receipt.get(key):
                raise CompletenessError(f"diversity receipt requires {key}")
    return receipt


def _receipt_index(receipts: Iterable[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for receipt in receipts:
        key = (receipt["target_type"], receipt["target"])
        if key in index:
            raise CompletenessError(f"duplicate accepted receipt: {key[0]}:{key[1]}")
        index[key] = receipt
    return index


def _gate(status: str, *, expected: int = 0, observed: int = 0, excepted: int = 0, missing: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "expected": expected,
        "observed": observed,
        "excepted": excepted,
        "missing": sorted(missing or []),
    }


def processing_state(metadata: dict[str, str]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    asr = metadata.get("asr_disposition")
    attribution = metadata.get("speaker_attribution")
    sectioning = metadata.get("sectioning_disposition")
    quotation = metadata.get("quotation_readiness")
    if asr not in ASR_DISPOSITIONS:
        missing.append("asr_disposition")
    if attribution not in ATTRIBUTION_DISPOSITIONS:
        missing.append("speaker_attribution")
    if sectioning not in SECTIONING_DISPOSITIONS:
        missing.append("sectioning_disposition")
    if quotation not in QUOTATION_DISPOSITIONS:
        missing.append("quotation_readiness")
    if sectioning == "preserved-unsectioned" and not metadata.get("sectioning_reason"):
        missing.append("sectioning_reason")
    if attribution in {"partial", "unknown"} and not metadata.get("speaker_attribution_reason"):
        missing.append("speaker_attribution_reason")
    if quotation in {"restricted", "not-ready"} and not metadata.get("quotation_readiness_reason"):
        missing.append("quotation_readiness_reason")
    return not missing, missing


def _score_component(
    *,
    weight: int,
    expected: int,
    observed: int,
    excepted: int = 0,
    assessed: bool = True,
    binary: bool = False,
) -> dict[str, Any]:
    satisfied = observed + excepted
    if not assessed:
        earned = 0.0
        status = "unassessed"
    elif binary:
        earned = float(weight if expected > 0 and satisfied >= expected else 0)
        status = "pass" if earned == weight else "fail"
    else:
        ratio = min(1.0, satisfied / expected) if expected else 0.0
        earned = round(weight * ratio, 1)
        status = "pass" if expected and satisfied >= expected else ("partial" if earned else "fail")
    return {
        "weight": weight,
        "earned": earned,
        "status": status,
        "expected": expected,
        "observed": observed,
        "excepted": excepted,
    }


def build_completeness_score(
    *,
    month: str,
    rows: list[dict[str, Any]],
    findings: list[dict[str, str]],
    repo_root: Path,
    source_metadata_loader: Callable[[Path], tuple[dict[str, str], str] | None],
    daily_validator: Callable[[str], dict[str, Any]],
    contract: dict[str, Any] | None,
    receipts: list[dict[str, Any]],
    certification_status: str,
) -> dict[str, Any]:
    contract_active = bool(contract and contract.get("frozen"))
    receipt_index = _receipt_index(receipts) if contract_active else {}
    transcripts = [row for row in rows if "transcript" in str(row.get("modality", ""))]
    daily_counts = Counter(str(row.get("date")) for row in transcripts)
    expected_days = sorted(
        {str(row.get("date")) for row in rows if str(row.get("date", "")).startswith(f"{month}-")}
    )

    structural = [item for item in findings if item.get("severity") == "error"]
    integrity = _score_component(
        weight=SCORE_WEIGHTS["integrity"],
        expected=1,
        observed=int(not structural),
        binary=True,
    )

    floor = contract["daily_transcript_floor"] if contract_active else 5
    daily_observed = sum(daily_counts[value] >= floor for value in expected_days)
    daily_excepted = sum(
        daily_counts[value] < floor and ("day", value) in receipt_index for value in expected_days
    )
    daily = _score_component(
        weight=SCORE_WEIGHTS["daily_coverage"],
        expected=len(expected_days),
        observed=daily_observed,
        excepted=daily_excepted,
    )

    voice_expected = voice_observed = voice_excepted = 0
    channel_expected = channel_observed = channel_excepted = 0
    if contract_active and contract:
        voice_counts: Counter[str] = Counter()
        for row in transcripts:
            for voice in row.get("voice_slugs") or []:
                voice_counts[voice] += 1
        for tier in VOICE_TIERS:
            for voice in contract["voice_tiers"][tier]:
                target = contract["voice_tier_floors"][tier]
                if target == 0:
                    continue
                voice_expected += 1
                if voice_counts[voice] >= target:
                    voice_observed += 1
                elif ("voice", voice) in receipt_index:
                    voice_excepted += 1
        host_counts = Counter(str(row.get("host_slug")) for row in transcripts)
        channel_expected = len(contract["tier_b_channels"])
        for target in contract["tier_b_channels"]:
            slug = target["host_slug"]
            if host_counts[slug] >= target["transcript_floor"]:
                channel_observed += 1
            elif ("channel", slug) in receipt_index:
                channel_excepted += 1
    voice = _score_component(
        weight=SCORE_WEIGHTS["voice_representation"],
        expected=voice_expected,
        observed=voice_observed,
        excepted=voice_excepted,
        assessed=contract_active,
    )
    channels = _score_component(
        weight=SCORE_WEIGHTS["tier_b_channels"],
        expected=channel_expected,
        observed=channel_observed,
        excepted=channel_excepted,
        assessed=contract_active,
    )

    processing_components = {
        "asr": 0,
        "attribution": 0,
        "sectioning": 0,
        "quotation_readiness": 0,
    }
    for row in transcripts:
        relative = str(row.get("local_path", ""))
        parsed = source_metadata_loader(repo_root / relative) if relative else None
        metadata = parsed[0] if parsed else {}
        if metadata.get("asr_disposition") in ASR_DISPOSITIONS:
            processing_components["asr"] += 1
        attribution = metadata.get("speaker_attribution")
        if attribution in ATTRIBUTION_DISPOSITIONS and not (
            attribution in {"partial", "unknown"} and not metadata.get("speaker_attribution_reason")
        ):
            processing_components["attribution"] += 1
        sectioning = metadata.get("sectioning_disposition")
        if sectioning in SECTIONING_DISPOSITIONS and not (
            sectioning == "preserved-unsectioned" and not metadata.get("sectioning_reason")
        ):
            processing_components["sectioning"] += 1
        quotation = metadata.get("quotation_readiness")
        if quotation in QUOTATION_DISPOSITIONS and not (
            quotation in {"restricted", "not-ready"} and not metadata.get("quotation_readiness_reason")
        ):
            processing_components["quotation_readiness"] += 1
    processing_expected = len(transcripts) * 4
    processing_observed = sum(processing_components.values())
    processing = _score_component(
        weight=SCORE_WEIGHTS["processing"],
        expected=processing_expected,
        observed=processing_observed,
    )
    processing["components"] = {
        name: {"expected": len(transcripts), "observed": observed}
        for name, observed in processing_components.items()
    }

    issue_observed = 0
    for value in expected_days:
        if daily_counts[value] and not daily_validator(value).get("failures"):
            issue_observed += 1
    issue = _score_component(
        weight=SCORE_WEIGHTS["issue_readiness"],
        expected=len(expected_days),
        observed=issue_observed,
    )
    diversity_present = contract_active and ("diversity", month) in receipt_index
    diversity = _score_component(
        weight=SCORE_WEIGHTS["diversity_disposition"],
        expected=1 if contract_active else 0,
        observed=int(diversity_present),
        assessed=contract_active,
        binary=True,
    )

    subscores = {
        "integrity": integrity,
        "daily_coverage": daily,
        "voice_representation": voice,
        "tier_b_channels": channels,
        "processing": processing,
        "issue_readiness": issue,
        "diversity_disposition": diversity,
    }
    uncapped = round(sum(item["earned"] for item in subscores.values()), 1)
    total = 100.0 if certification_status == "pass" else min(99.0, uncapped)
    return {
        "schema_version": SCORE_SCHEMA_VERSION,
        "total": total,
        "maximum": 100,
        "uncapped_total": uncapped,
        "certification_status": certification_status,
        "hundred_reserved_for_pass": True,
        "subscores": subscores,
    }


def build_certification(
    *,
    month: str,
    rows: list[dict[str, Any]],
    findings: list[dict[str, str]],
    as_of: date,
    repo_root: Path,
    source_metadata_loader: Callable[[Path], tuple[dict[str, str], str] | None],
    daily_validator: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    contracts_root = repo_root / "narrative-geopolitics" / "work" / "coverage" / "contracts"
    receipts_root = repo_root / "narrative-geopolitics" / "work" / "coverage" / "receipts"
    contract_path = contracts_root / f"{month}.json"
    receipt_path = receipts_root / f"{month}.jsonl"
    base = {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "month": month,
        "contract_path": contract_path.relative_to(repo_root).as_posix(),
        "receipt_path": receipt_path.relative_to(repo_root).as_posix(),
        "late_declaration": None,
        "gates": {},
        "blocking_records": [],
        "repair_candidates": [],
    }
    contract: dict[str, Any] | None = None
    receipts: list[dict[str, Any]] = []

    def result_with_score(result: dict[str, Any]) -> dict[str, Any]:
        result["completeness_score"] = build_completeness_score(
            month=month,
            rows=rows,
            findings=findings,
            repo_root=repo_root,
            source_metadata_loader=source_metadata_loader,
            daily_validator=daily_validator,
            contract=contract,
            receipts=receipts,
            certification_status=str(result["status"]),
        )
        return result

    if not contract_path.is_file():
        return result_with_score({**base, "status": "ineligible", "reason": "monthly completeness contract is absent"})
    try:
        contract = validate_contract(_read_json(contract_path), month=month, repo_root=repo_root)
        receipts = [validate_receipt(item, month=month) for item in _read_receipts(receipt_path)]
        receipt_index = _receipt_index(receipts)
    except CompletenessError as error:
        return result_with_score({**base, "status": "ineligible", "reason": str(error)})
    base["late_declaration"] = contract["late_declaration"]
    if not contract["frozen"]:
        return result_with_score({**base, "status": "ineligible", "reason": "monthly completeness contract is not frozen"})
    month_last = date.fromisoformat(f"{month}-01")
    if month_last.month == 12:
        month_last = date(month_last.year + 1, 1, 1)
    else:
        month_last = date(month_last.year, month_last.month + 1, 1)
    month_last = month_last.fromordinal(month_last.toordinal() - 1)
    if as_of < month_last:
        return result_with_score({**base, "status": "in-progress", "reason": "manifest horizon has not reached month end"})

    transcripts = [row for row in rows if "transcript" in str(row.get("modality", ""))]
    daily_counts = Counter(str(row.get("date")) for row in transcripts)
    expected_days = sorted({str(row.get("date")) for row in rows if str(row.get("date", "")).startswith(f"{month}-")})
    daily_missing: list[str] = []
    daily_excepted = 0
    for value in expected_days:
        if daily_counts[value] >= contract["daily_transcript_floor"]:
            continue
        if ("day", value) in receipt_index:
            daily_excepted += 1
        else:
            daily_missing.append(value)
    daily_gate = _gate("pass" if not daily_missing else "fail", expected=len(expected_days), observed=sum(daily_counts[value] >= contract["daily_transcript_floor"] for value in expected_days), excepted=daily_excepted, missing=daily_missing)

    voice_counts: Counter[str] = Counter()
    for row in transcripts:
        for voice in row.get("voice_slugs") or []:
            voice_counts[voice] += 1
    voice_missing: list[str] = []
    voice_excepted = 0
    expected_voice_targets = 0
    for tier in VOICE_TIERS:
        for voice in contract["voice_tiers"][tier]:
            floor = contract["voice_tier_floors"][tier]
            if floor == 0:
                continue
            expected_voice_targets += 1
            if voice_counts[voice] >= floor:
                continue
            if ("voice", voice) in receipt_index:
                voice_excepted += 1
            else:
                voice_missing.append(voice)
    voice_gate = _gate("pass" if not voice_missing else "fail", expected=expected_voice_targets, observed=expected_voice_targets - len(voice_missing) - voice_excepted, excepted=voice_excepted, missing=voice_missing)

    host_counts = Counter(str(row.get("host_slug")) for row in transcripts)
    channel_missing: list[str] = []
    channel_excepted = 0
    for target in contract["tier_b_channels"]:
        slug = target["host_slug"]
        if host_counts[slug] >= target["transcript_floor"]:
            continue
        if ("channel", slug) in receipt_index:
            channel_excepted += 1
        else:
            channel_missing.append(slug)
    channel_gate = _gate("pass" if not channel_missing else "fail", expected=len(contract["tier_b_channels"]), observed=len(contract["tier_b_channels"]) - len(channel_missing) - channel_excepted, excepted=channel_excepted, missing=channel_missing)

    processing_missing: list[str] = []
    for row in transcripts:
        relative = str(row.get("local_path", ""))
        parsed = source_metadata_loader(repo_root / relative) if relative else None
        if parsed is None:
            processing_missing.append(relative or "manifest-row-without-path")
            continue
        complete, fields = processing_state(parsed[0])
        if not complete:
            processing_missing.append(f"{relative}: {','.join(fields)}")
    processing_gate = _gate("pass" if not processing_missing else "fail", expected=len(transcripts), observed=len(transcripts) - len(processing_missing), missing=processing_missing)

    issue_missing: list[str] = []
    for value in expected_days:
        if daily_counts[value] == 0:
            issue_missing.append(value)
            continue
        result = daily_validator(value)
        if result.get("failures"):
            issue_missing.append(value)
    issue_gate = _gate("pass" if not issue_missing else "fail", expected=len(expected_days), observed=len(expected_days) - len(issue_missing), missing=issue_missing)

    diversity_present = ("diversity", month) in receipt_index
    diversity_gate = _gate("pass" if diversity_present else "fail", expected=1, observed=int(diversity_present), missing=[] if diversity_present else [month])
    structural = [item["path"] for item in findings if item.get("severity") == "error"]
    integrity_gate = _gate("pass" if not structural else "fail", expected=len(rows), observed=len(rows) if not structural else max(0, len(rows) - len(structural)), missing=structural)
    gates = {
        "integrity": integrity_gate,
        "daily_coverage": daily_gate,
        "voice_representation": voice_gate,
        "tier_b_channels": channel_gate,
        "processing": processing_gate,
        "diversity_disposition": diversity_gate,
        "issue_readiness": issue_gate,
    }
    blocking = [f"{name}:{item}" for name, gate in gates.items() for item in gate["missing"]]
    result = {
        **base,
        "status": "pass" if all(gate["status"] == "pass" for gate in gates.values()) else "fail",
        "reason": "all hard gates pass" if not blocking else "one or more hard gates fail",
        "gates": gates,
        "blocking_records": blocking,
        "repair_candidates": sorted(set(structural + processing_missing + issue_missing)),
    }
    return result_with_score(result)

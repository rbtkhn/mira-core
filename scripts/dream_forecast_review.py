"""Private, input-bound forecast review. Judgment is supplied by the Dream agent.

Nothing here resolves a forecast or admits/changes reality evidence.
"""
from __future__ import annotations

from repository_paths import resolve_geopolitics_reference
from dataclasses import asdict
from datetime import date
import hashlib
import json
from pathlib import Path
import re

import cadence_ledger
import forecast_ledger
import reality


VERSION = 1
SUMMARY_VERSION = 2
ID_RE = re.compile(r"\b(?:OPC|VER)-\d{8}-\d{2}\b")
DISPOSITIONS = {"proposed_hit", "proposed_miss", "proposed_mixed", "evidence_gap", "criteria_provenance_gap"}
BOUNDARY = "Private proposal only; no forecast scoring, reality mutation, admission, or publication authority."


def review_summary(summary: dict) -> dict:
    """Project current or historical receipts without rewriting their evidence.

    Historical aggregate labels alone cannot establish coverage. Counts describe
    recorded review work, never forecast resolution or fresh source validation.
    """
    rows = summary.get("reviews")
    pending = summary.get("pending_count")
    coverage_known = (isinstance(rows, list) and type(pending) is int and pending >= 0
                      and summary.get("coverage_known") is not False
                      and summary.get("schema_version", VERSION) in {VERSION, SUMMARY_VERSION}
                      and summary.get("status") != "review_failed")
    pending = pending if type(pending) is int and pending >= 0 else None
    counts = dict(reviewed_count=0, unavailable_count=0, failed_count=0,
                  gap_count=0, proposed_outcome_count=0)
    seen = set()
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict) or not row.get("hook") or row["hook"] in seen:
            coverage_known = False
            continue
        seen.add(row["hook"])
        status = row.get("status")
        if status in {"reviewed", "unchanged"} and row.get("disposition") in DISPOSITIONS:
            counts["reviewed_count"] += 1
            counts["gap_count" if row["disposition"].endswith("gap") else "proposed_outcome_count"] += 1
        elif status == "review_unavailable":
            counts["unavailable_count"] += 1
        elif status == "review_failed":
            counts["failed_count"] += 1
        else:
            coverage_known = False
    status = ("forecast_review_required" if pending else
              "review_incomplete" if not coverage_known or counts["unavailable_count"] or counts["failed_count"] or summary.get("reason") else
              "review_complete")
    if not isinstance(rows, list):
        counts = {key: None for key in counts}
    return {**summary, "schema_version": SUMMARY_VERSION, "status": status,
            "pending_count": pending, **counts, "coverage_known": coverage_known,
            "authority_boundary": BOUNDARY, "nonblocking": True}


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def local_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Source escapes repository: {value}")
    return path


def reference(root: Path, path: Path, kind: str, **metadata) -> dict:
    path = local_path(root, str(path))
    return {
        "path": path.relative_to(root.resolve()).as_posix(), "kind": kind,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        **metadata,
    }


def gather(root: Path, rows: list[dict], as_of: str) -> dict:
    """Gather exact associations and date-bounded archive leads, never keyword scores."""
    root = root.resolve()
    work = resolve_geopolitics_reference(root, 'geopolitics/work')
    ledger = work / "forecasts/forecast-ledger.md"
    ledger_text = ledger.read_text(encoding="utf-8")
    triage = forecast_ledger.parse_triage(ledger_text)
    records = reality.load_records(work / "reality")
    manifest = root / "archive/sources/geopolitics/source-manifest.json"
    sources = json.loads(manifest.read_text(encoding="utf-8")).get("sources", []) if manifest.is_file() else []
    legacy = [(p, p.read_text(encoding="utf-8")) for p in sorted((work / "verification/packets").glob("*/README.md"))]
    hooks = []
    for row in rows:
        hook = row["hook_id"]
        original = work / "daily" / row["date"] / "forecast.md"
        original_text = original.read_text(encoding="utf-8") if original.is_file() else ""
        metadata = [asdict(item) for item in triage if item.hook_id == hook]
        lines = [line for line in ledger_text.splitlines() if hook in line]
        refs = [reference(root, original, "original_forecast")]
        gaps = []
        if not original_text or hook not in original_text:
            gaps.append("Original hook is missing from its forecast document.")
        if len(metadata) != 1:
            gaps.append("Missing or ambiguous accountability provenance.")
        elif not metadata[0]["accountable"] or metadata[0]["forecast_type"] != "ex_ante":
            gaps.append("Hook is not an accountable ex-ante forecast.")
        # A whole daily document can mention other hooks: only hook-bearing lines
        # establish a direct link. The full document remains available for reading.
        linked_ids = set(ID_RE.findall("\n".join(lines + [x for x in original_text.splitlines() if hook in x])))
        for path, body in legacy:
            if hook in body:
                refs.append(reference(root, path, "legacy_link_only"))
                ids = ID_RE.findall(path.parent.name)
                for identifier in ids:
                    canonical = records.get(identifier, {})
                    if hook not in canonical.get("affected_forecast_hooks", []):
                        gaps.append(f"Legacy/canonical hook association missing or conflicting: {identifier}.")
                    else:
                        linked_ids.add(identifier)
        for identifier, record in records.items():
            if hook in record.get("affected_forecast_hooks", []):
                linked_ids.add(identifier)
        selected = set(linked_ids)
        for identifier in list(selected):
            record = records.get(identifier, {})
            if record.get("kind") == "investigation":
                selected.update(record.get("claim_ids", []))
                selected.update(record.get("observable_ids", []))
        claims = {i for i in selected if i.startswith("OPC-")}
        for identifier, record in records.items():
            if record.get("claim_id") in claims or claims.intersection(record.get("claim_ids", [])):
                selected.add(identifier)
            if record.get("kind") == "relation" and record.get("to_id") in claims:
                selected.add(identifier)
                selected.add(record.get("from_id", ""))
        for identifier in list(selected):
            record = records.get(identifier, {})
            selected.update(record.get("evidence_ids", []))
            selected.update(record.get("observable_ids", []))
        for identifier in list(selected):
            record = records.get(identifier, {})
            if record.get("source_id"):
                selected.add(record["source_id"])
        for identifier in sorted(selected):
            record = records.get(identifier)
            if not record or record.get("_error") or record.get("_duplicate"):
                gaps.append(f"Missing or invalid canonical record: {identifier}.")
                continue
            refs.append(reference(root, Path(record["_path"]), "canonical_" + record["kind"], record_id=identifier))
            gaps.extend(reality.validate_record(record, records))
        audits = {identifier: reality.audit_payload(identifier, work / "reality") for identifier in sorted(claims) if identifier in records}
        for source in sources:
            published = source.get("date", "")
            if row["date"] <= published <= as_of and source.get("local_path"):
                refs.append(reference(root, local_path(root, source["local_path"]), "archive_assertion", date=published, source_metadata=source))
        if not manifest.is_file():
            gaps.append("Archive source manifest unavailable; local-source coverage is incomplete.")
        packet = {
            "schema_version": VERSION, "hook": hook, "ledger_row": row,
            "ledger_context": lines, "accountability": metadata,
            "references": refs, "canonical_audits": audits, "gaps": gaps,
            "authority_boundary": BOUNDARY,
        }
        packet["input_digest"] = digest(packet)
        hooks.append(packet)
    return {"schema_version": VERSION, "as_of": as_of, "hooks": hooks, "authority_boundary": BOUNDARY}


def validate_review(review: dict, packet: dict, root: Path) -> None:
    """Check binding and citations, leaving semantic judgment visibly agent-authored."""
    if not isinstance(review, dict) or review.get("input_digest") != packet["input_digest"] or review.get("hook") != packet["hook"]:
        raise ValueError("Review is stale or bound to another hook.")
    if review.get("disposition") not in DISPOSITIONS:
        raise ValueError("Unknown proposed disposition.")
    for key in ("rationale", "criteria_analysis", "time_window_analysis", "counterevidence", "remaining_gates"):
        if not isinstance(review.get(key), str) or not review[key].strip():
            raise ValueError(f"Review requires {key}.")
    citations = review.get("citations")
    if not isinstance(citations, list):
        raise ValueError("Review requires citations (possibly empty for gaps).")
    refs = {ref["path"]: ref for ref in packet["references"]}
    for ref in refs.values():
        path = local_path(root, ref["path"])
        current = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if current != ref["sha256"]:
            raise ValueError("Review inputs changed during the handoff.")
    evidence_roles = set()
    has_criteria = False
    for cite in citations:
        if not isinstance(cite, dict) or cite.get("path") not in refs:
            raise ValueError("Citation is not in the current input packet.")
        ref = refs[cite["path"]]
        path = local_path(root, ref["path"])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
            raise ValueError("Cited source is missing or changed.")
        quote = cite.get("quote")
        if not isinstance(quote, str) or not quote.strip() or quote not in path.read_text(encoding="utf-8"):
            raise ValueError("Citation quote must occur verbatim in its source.")
        role = cite.get("role")
        if role == "criteria" and ref["kind"] == "original_forecast":
            has_criteria = True
        elif role in {"supports", "challenges"}:
            if ref["kind"] not in {"canonical_evidence", "archive_assertion"}:
                raise ValueError("Derived analysis and legacy links are not outcome evidence.")
            observed = date.fromisoformat(cite.get("event_date", ""))
            start = date.fromisoformat(packet["ledger_row"]["date"])
            if len(packet["accountability"]) == 1:
                start = max(start, date.fromisoformat(packet["accountability"][0]["authorship_bound"][:10]))
            end = date.fromisoformat(packet["ledger_row"]["review_date"])
            if not start <= observed <= end:
                raise ValueError("Cited event lies outside the forecast window.")
            if ref["kind"] == "archive_assertion" and cite.get("evidence_use") != "source_assertion":
                raise ValueError("Archive material establishes a source assertion, not operational truth.")
            if ref["kind"] == "canonical_evidence":
                event_time = json.loads(path.read_text(encoding="utf-8")).get("event_time", "")
                if event_time[:10] != observed.isoformat():
                    raise ValueError("Cited date disagrees with the canonical evidence event time.")
            if not cite.get("date_basis_quote") or cite["date_basis_quote"] not in path.read_text(encoding="utf-8"):
                raise ValueError("Event date requires a verbatim source basis.")
            evidence_roles.add(role)
        else:
            raise ValueError("Invalid citation role or source kind.")
    disposition = review["disposition"]
    if disposition.startswith("proposed_"):
        if packet["gaps"] or not has_criteria:
            raise ValueError("Proposed outcomes require original criteria and intact provenance/links.")
        needed = {"supports", "challenges"} if disposition == "proposed_mixed" else {"supports" if disposition == "proposed_hit" else "challenges"}
        if not needed <= evidence_roles:
            raise ValueError("Proposed outcome lacks supporting/challenging citations; absence is not a miss.")


def run(root: Path, rows: list[dict], as_of: str, bundle: Path, *, result_path: Path | None = None, unavailable: str | None = None, check: bool = False) -> dict:
    """Prepare/resume one agent handoff; failed reviews are visible nonblocking debt."""
    try:
        inputs = gather(root, rows, as_of) if rows else {"hooks": [], "as_of": as_of, "schema_version": VERSION}
        if check:
            return {"status": "review_due" if rows else "no_due_hooks", "due_count": len(rows), "mutation": False}
        bundle = cadence_ledger.require_private_path(bundle, label="Forecast review bundle")
        cache = cadence_ledger.require_private_path(bundle.parent / "forecast-review-cache", label="Forecast review cache")
        if bundle.is_relative_to(root.resolve()) or cache.is_relative_to(root.resolve()):
            raise ValueError("Forecast review output must remain outside the source repository.")
        bundle.mkdir(parents=True, exist_ok=True)
        cache.mkdir(parents=True, exist_ok=True)
        submitted = {}
        if result_path:
            result_path = cadence_ledger.require_private_path(result_path, label="Forecast review result")
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            for item in payload["reviews"]:
                if item["hook"] in submitted:
                    raise ValueError("Duplicate hook in agent review.")
                submitted[item["hook"]] = item
            if set(submitted) - {p["hook"] for p in inputs["hooks"]}:
                raise ValueError("Agent result contains hooks outside this review.")
        results, pending = [], []
        for packet in inputs["hooks"]:
            cached = cadence_ledger.require_private_path(cache / (packet["input_digest"] + ".json"), label="Forecast review cache record")
            snapshot = cadence_ledger.require_private_path(cache / (packet["input_digest"] + ".inputs.json"), label="Forecast review input snapshot")
            if not snapshot.exists():
                snapshot.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
            review = submitted.get(packet["hook"])
            reused = False
            if review is None and cached.is_file():
                review = json.loads(cached.read_text(encoding="utf-8"))
                reused = True
            if review is not None:
                try:
                    validate_review(review, packet, root)
                except (ValueError, TypeError, KeyError) as error:
                    results.append({"hook": packet["hook"], "status": "review_failed", "reason": str(error), "nonblocking": True})
                    continue
                if not reused:
                    cached.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
                results.append({**review, "status": "unchanged" if reused else "reviewed"})
            elif unavailable:
                results.append({"hook": packet["hook"], "status": "review_unavailable", "reason": unavailable, "nonblocking": True})
            else:
                pending.append(packet)
        inputs["hooks"] = pending
        input_path = cadence_ledger.require_private_path(bundle / "forecast-review-inputs.json", label="Forecast review inputs")
        input_path.write_text(json.dumps(inputs, indent=2) + "\n", encoding="utf-8")
        summary = review_summary({
            "as_of": as_of,
            "reviews": results, "pending_count": len(pending), "input_path": str(input_path),
            "authority_boundary": BOUNDARY, "nonblocking": True,
        })
        output = cadence_ledger.require_private_path(bundle / "forecast-review.json", label="Forecast review output")
        output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        return {**summary, "path": str(output)}
    except (OSError, ValueError, KeyError, TypeError, AttributeError, reality.RealityError, cadence_ledger.CadenceLedgerError) as error:
        return review_summary({"reason": str(error)})

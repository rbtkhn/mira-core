"""Append-only date attribution corrections; never rewrite captured provenance."""
from __future__ import annotations

import copy
import hashlib
from datetime import date, datetime, timezone
from pathlib import Path

KIND = "interrupted-dream-date"


def correction_for(registry: dict, version: dict) -> dict | None:
    matches = [e for e in registry.get("maintenance_events", [])
               if e.get("correction_kind") == KIND
               and e.get("version_id") == version.get("version_id")]
    if not matches:
        return None
    if len(matches) != 1 or matches[0].get("expected_digest") != version.get("content_sha256"):
        raise ValueError("Journal date correction has ambiguous or stale version binding")
    event = matches[0]
    date.fromisoformat(event["intended_entry_date"])
    if event["intended_entry_date"] == event["recorded_entry_date"]:
        raise ValueError("Journal date correction must change attribution")
    return event


def completion_entry(registry: dict, day: str) -> dict | None:
    entry = next((e for e in registry.get("entries", []) if e["entry_date"] == day), None)
    if entry and correction_for(registry, entry["versions"][-1]):
        return None
    return entry


def record(args, journal) -> dict:
    registry = journal.load_registry()
    entries = [e for e in registry["entries"] if e["current_version_id"] == args.version]
    if len(entries) != 1:
        raise journal.JournalError("Correction requires an exact current Journal version")
    entry = entries[0]
    version = entry["versions"][-1]
    if version["content_sha256"] != args.expected_digest:
        raise journal.JournalError("Correction digest does not match current version")
    intended = date.fromisoformat(args.intended_date).isoformat()
    if intended >= entry["entry_date"]:
        raise journal.JournalError("Interrupted-Dream correction must name an earlier intended date")
    if not journal.SESSION_ID_RE.fullmatch(args.authority_ref) or not args.reason.strip():
        raise journal.JournalError("Correction requires operator authority and a reason")
    existing = correction_for(registry, version)
    if existing:
        if existing["intended_entry_date"] != intended:
            raise journal.JournalError("Existing correction names a different date")
        preserved = journal.REPO_ROOT / existing["preserved_path"]
        if hashlib.sha256(preserved.read_bytes()).hexdigest() != args.expected_digest:
            raise journal.JournalError("Preserved Journal bytes changed")
        return {"status": "already_corrected", "mutation": False, "correction": existing}
    body = (journal.REPO_ROOT / entry["current_path"]).read_bytes()
    if hashlib.sha256(body).hexdigest() != args.expected_digest:
        raise journal.JournalError("Current Journal bytes do not match the correction digest")
    relative = f"mira/journal/corrections/{args.version}.md"
    preserved = journal.REPO_ROOT / relative
    if preserved.exists() and preserved.read_bytes() != body:
        raise journal.JournalError("Correction archive path contains different bytes")
    event = {
        "event_id": f"MJM-{1 + max((int(e['event_id'][4:]) for e in registry.get('maintenance_events', [])), default=0):04d}",
        "event_type": "metadata-correction", "correction_kind": KIND,
        "version_id": args.version, "expected_digest": args.expected_digest,
        "recorded_entry_date": entry["entry_date"], "intended_entry_date": intended,
        "recorded_at": journal.utc_text(datetime.now(timezone.utc)),
        "authority_ref": args.authority_ref, "reason": args.reason.strip(),
        "preserved_path": relative,
        "coverage_boundary": "Original capture bounds and authorship/finalization timestamps are preserved; intended date is operator-corrected attribution, not recaptured evidence.",
    }
    updated = copy.deepcopy(registry)
    updated.setdefault("maintenance_events", []).append(event)
    if not journal.MAINTENANCE_ID_RE.fullmatch(event["event_id"]):
        raise journal.JournalError("Invalid maintenance identity")
    if not args.check:
        # One recoverable atomic write group; historical version/approval data is untouched.
        journal.atomic_write_many({
            preserved: body,
            journal.REGISTRY_PATH: journal.pretty_json(updated).encode("utf-8"),
            journal.INDEX_PATH: journal.render_index(updated).encode("utf-8"),
        })
    return {"status": "ready" if args.check else "corrected", "mutation": not args.check,
            "correction": event, "journal_completion": "composition_required"}

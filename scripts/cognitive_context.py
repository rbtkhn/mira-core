"""Private composition orientation and candidate-only note judgments."""
from __future__ import annotations

import copy
import json
import re
import subprocess
from pathlib import Path
import strategy_notebook as notebook

DISPOSITIONS = {"used", "considered-not-used", "unavailable", "deferred"}
OPERATIONS = {"create", "amend", "challenge", "close"}


def bounded_history(value, budget=12000):
    """Keep complete records and expose omissions; never truncate a correction into a claim."""
    result = {"status": "available", "records": [], "omitted": [],
              "authority": "private attributed interpretation; not Journal ancestry or factual evidence",
              "history_limits": value.get("history_limits", {}), "evidence_gaps": value.get("evidence_gaps", [])}
    seen = set()
    for group in ("corrections_and_predecessors", "predecessor_history", "related", "latest"):
        for row in value.get(group, []):
            key = (row.get("entry_id"), row.get("version"))
            if key in seen:
                continue
            seen.add(key)
            size = len(json.dumps(row, ensure_ascii=False))
            if size > budget:
                result["omitted"].append({"entry_id": key[0], "version": key[1], "reason": "context budget"})
            else:
                budget -= size
                result["records"].append({"group": group, "record": row})
    return result


def prepare(day, focus, repo, previous=None):
    try:
        strategic = notebook.context(day, focus, repo)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        strategic = {"status": "unavailable", "reason": str(error), "focus": focus}
    focus = strategic.get("focus", focus)
    history = {"status": "unavailable", "reason": "No relevant composition focus."}
    scan = {"status": "not-applicable", "reason": "No strategic question and provisional mechanism."}
    if previous is not None:
        # Context refresh is not a second Library retrieval loop in the same composition.
        history = copy.deepcopy(previous.get("library", history))
        scan = copy.deepcopy(previous.get("library_scan", scan))
    elif focus:
        try:
            import library_journal
            history = bounded_history(library_journal.context(focus, repo=repo))
        except (OSError, ValueError, RuntimeError) as error:
            history = {"status": "unavailable", "reason": str(error)}
        target = notebook.read_entry(day, repo)
        mechanism = notebook.section(target["text"], "Bottom Line", "Central Judgment") if target else ""
        if not mechanism:
            path = notebook.domain(repo) / "work/daily" / day / "judgment.md"
            if path.is_file():
                mechanism = notebook.section(path.read_text(encoding="utf-8"), "Bottom Line", "Central Judgment")
        if mechanism and notebook.disposition(day, repo).get("status") != "analysis-deferred":
            try:
                import library_reasoning
                # Its owner validates controls and maintains a bounded per-run metadata cache.
                scan = {"status": "screened", "result": library_reasoning.pre_scan(focus, mechanism)}
            except (OSError, ValueError, RuntimeError) as error:
                scan = {"status": "unavailable", "reason": str(error)}
    result = {"schema_version": 1, "strategy": strategic, "library": history, "library_scan": scan,
              "effort_limit": {"pre_scan": 1, "passage_packet": 1, "adjudication": 1},
              "next_action": "Consume frozen Tower context and its qualifications; record use or gaps, consolidate note proposals, and finish Dream without strategic composition.",
              "authority_effect": "none"}
    result["content_sha256"] = notebook.digest(result)
    return result


def attach(brief, context):
    value = copy.deepcopy(brief)
    value.pop("composition_brief_id", None)
    manifest = value.pop("derivation_manifest")
    value["strategy_context"] = context
    value["input_object_ids"] = [x for x in value["input_object_ids"] if not x.startswith("strategy-context:")]
    value["input_object_ids"].append("strategy-context:" + context["content_sha256"])
    value["input_object_ids"].sort()
    sha = notebook.digest(value)
    value["composition_brief_id"] = "CB-" + sha[:24]
    value["derivation_manifest"] = {**manifest, "derivation_id": "DRV-" + sha[:24],
                                   "output_digest": sha, "input_object_ids": value["input_object_ids"]}
    return value


def consumption_failures(brief, metadata, reference, body):
    frozen = brief.get("strategy_context")
    declared = metadata.get("context_consumption")
    if frozen is None:
        return [] if declared is None else ["context consumption claims an absent frozen context"]
    failures = []
    if not isinstance(declared, dict):
        return ["new composition requires context_consumption dispositions for strategy and library"]
    for key in ("strategy", "library"):
        row = declared.get(key, {})
        if not isinstance(row, dict) or row.get("status") not in DISPOSITIONS or not row.get("reason"):
            failures.append(f"{key} requires an honest context disposition and reason")
            continue
        if row["status"] == "used":
            if frozen.get(key, {}).get("status") in {"unavailable", "no-relevant-material"}:
                failures.append(f"{key} unavailable context cannot be used")
            if row.get("context_sha256") != frozen["content_sha256"]:
                failures.append(f"{key} frozen context digest mismatch")
            anchors = row.get("prose_anchors", [])
            grounded = {item.get("prose_anchor") for item in reference.get("items", [])}
            if not anchors or any(not isinstance(a, str) or a not in body or a not in grounded for a in anchors):
                failures.append(f"{key} consumed context requires exact grounded prose anchors")
    if reference.get("context_consumption") != declared:
        failures.append("technical reference context consumption mismatch")
    expected = notebook.digest({k: v for k, v in frozen.items() if k != "content_sha256"})
    if expected != frozen.get("content_sha256"):
        failures.append("frozen strategy context integrity mismatch")
    return failures


def note_search(focus, repo, limit=5, work_ids=()):
    words = notebook.tokens(focus)
    rows = []
    for path in (repo / "archive/notes").rglob("*.md"):
        text = path.read_text(encoding="utf-8-sig")
        heading = text.splitlines()[0] if text else ""
        refs = " ".join(re.findall(r"\b(?:LIB|MIRA-ROUTE|SRC)-[\w-]+", text))
        score = 3 * len(words & notebook.tokens(heading)) + len(words & notebook.tokens(text[:2500] + refs))
        if score:
            rows.append({"path": path.relative_to(repo).as_posix(), "sha256": notebook.digest(path.read_bytes()),
                         "score": score, "title": heading, "orientation": text[:2500], "full_read_required": True})
    from library_growth import search
    merged = {row['path']: row for row in rows}
    for row in search(focus, repo, work_ids, limit=limit):
        merged[row['path']] = {**merged.get(row['path'], {}), **row}
    return sorted(merged.values(), key=lambda row: (-row["score"], row["path"]))[:limit]


def checked_path(repo, raw, *, note=False):
    path = (repo / str(raw)).resolve()
    if not path.is_relative_to(repo.resolve()):
        raise ValueError("candidate path escapes workspace")
    if note and not path.is_relative_to((repo / "archive/notes").resolve()):
        raise ValueError("Mira Notes candidate must target archive/notes")
    return path


def nominations(value, repo):
    """Validate agent-authored judgments. Deterministic code does not invent novelty."""
    if not isinstance(value, list) or len(value) > 3:
        raise ValueError("at most three note nominations per closeout")
    rows = {}
    for candidate in value:
        row = copy.deepcopy(candidate)
        required = ("operation", "note_class", "owner", "target_path", "central_question", "change", "why_it_matters",
                    "proposed_edit", "strongest_objection", "next_test", "duplicate_search", "source_bindings", "limitations", "ranking")
        if any(key not in row for key in required) or row["operation"] not in OPERATIONS:
            raise ValueError("incomplete note nomination")
        if any(not isinstance(row.get(k), str) or not row[k].strip() for k in
               ("central_question", "change", "why_it_matters", "proposed_edit", "strongest_objection", "next_test", "limitations")):
            raise ValueError("nomination judgments must be nonempty text")
        if row["note_class"] not in {"working-note", "interpretive-note", "hypothesis", "experiment", "historical-note"}:
            raise ValueError("invalid Mira Notes class")
        if row["owner"] not in {"mira-notes", "library-integration"}:
            raise ValueError("invalid note owning workflow")
        path = checked_path(repo, row["target_path"], note=row["owner"] == "mira-notes")
        if row["owner"] == "library-integration" and not path.is_relative_to((repo / "archive/library").resolve()):
            raise ValueError("governed Library nomination must target its archive/library carrier")
        if row["operation"] == "create":
            if path.exists():
                raise ValueError("existing note requires amendment rather than creation")
        elif not path.is_file() or notebook.digest(path.read_bytes()) != row.get("target_sha256"):
            raise ValueError("stale note target binding")
        if not row["duplicate_search"].get("reason") or "inspected" not in row["duplicate_search"]:
            raise ValueError("note nomination requires duplicate-search judgment")
        for binding in row["duplicate_search"]["inspected"] + row["source_bindings"]:
            source = checked_path(repo, binding["path"])
            if not source.is_file() or notebook.digest(source.read_bytes()) != binding.get("sha256"):
                raise ValueError("stale nomination source or inspected-note binding")
        if not row["source_bindings"]:
            raise ValueError("note nomination requires source grounding")
        for key in ("consequence", "evidence", "novelty", "testability"):
            if type(row["ranking"].get(key)) is not int or not 0 <= row["ranking"][key] <= 3:
                raise ValueError("nomination ranking values must be integers 0..3")
        row.pop("candidate_id", None)
        row["authority_effect"] = "candidate-only"
        row["candidate_id"] = "MNC-" + notebook.digest(row)[:24]
        if row["target_path"] in rows and rows[row["target_path"]] != row:
            raise ValueError("conflicting nominations for the same note; consolidate the judgment")
        rows[row["target_path"]] = row
    return sorted(rows.values(), key=lambda r: tuple(-r["ranking"][k] for k in ("consequence", "evidence", "novelty", "testability")) + (r["candidate_id"],))


def refresh_roi(bundle, day, repo):
    """Update this unfinished bundle without discarding agent-authored obligations."""
    path = bundle / "roi-synthesis.json"
    if not path.is_file():
        return
    packet = json.loads(path.read_text(encoding="utf-8"))
    sections = packet["sections"]
    candidates = bundle / "note-candidates.json"
    if candidates.is_file():
        try:
            sections["note_candidates"] = nominations(json.loads(candidates.read_text(encoding="utf-8")), repo)
        except (ValueError, KeyError, TypeError, OSError) as error:
            sections["note_candidates"] = []
            debt = {"kind": "note-nomination-validation", "status": "deferred", "reason": str(error)}
            if debt not in sections["open_obligations"]:
                sections["open_obligations"].append(debt)
    disposition = closeout(bundle, day, repo)
    for owner, row in disposition.items():
        if row.get("status") in {"unavailable", "deferred", "analysis-deferred", "not-recorded"}:
            debt = {"kind": "cognitive-context", "owner": owner, **row}
            if debt not in sections["open_obligations"]:
                sections["open_obligations"].append(debt)
    raw = json.dumps(packet, sort_keys=True, indent=2) + "\n"
    if path.read_text(encoding="utf-8") != raw:
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(raw, encoding="utf-8")
        temporary.replace(path)


def closeout(bundle, day, repo):
    result = {"notebook": notebook.disposition(day, repo), "library": {"status": "not-recorded"}}
    path = bundle / "draft.json"
    if path.is_file():
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
            result["library"] = meta.get("context_consumption", {}).get("library", {"status": "not-recorded"})
        except (OSError, ValueError, AttributeError) as error:
            result["library"] = {"status": "unavailable", "reason": str(error)}
    # No excerpts or private dialogue in the cadence receipt.
    if not isinstance(result["library"], dict):
        result["library"] = {"status": "unavailable", "reason": "Malformed context disposition; no use inferred."}
    result["library"] = {k: v for k, v in result["library"].items() if k in {"status", "reason", "context_sha256"}}
    return result

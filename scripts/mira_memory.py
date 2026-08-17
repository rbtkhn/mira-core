from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_names import resolve_environment


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = 4
CHOICE_ENV = "MIRA_CORE_CHOICE_DB"
CADENCE_ENV = "MIRA_CORE_CADENCE_DB"
MENTORSHIP_ENV = "MIRA_MENTORSHIP_DB"
ARCHIVE_ROOT_ENV = "MIRA_CORE_ARCHIVE_ROOT"
ARCHIVE_CONFIG_ENV = "MIRA_CORE_ARCHIVE_CONFIG"
DEFAULT_ARCHIVE_CONFIG = REPO_ROOT / ".mira-private" / "archive" / "config.json"
EXTERNAL_ARCHIVE_CONFIG = Path(r"C:\private\mira-core-archive-config.json")
FORMER_ARCHIVE_CONFIG = Path(r"C:\private\mira-core-system-archive-config.json")
LEGACY_ARCHIVE_CONFIG = Path(r"C:\private\narrative-system-archive-config.json")
TENSION_KINDS = {
    "stale-derived-view",
    "canonical-source-drift",
    "registry-catalog-mismatch",
    "temporal-change",
    "interpretive-divergence",
    "insufficient-counterevidence",
}


def parse_as_of(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("--as-of must be an RFC3339 timestamp") from error
    if parsed.tzinfo is None:
        raise ValueError("--as-of must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def json_state(path: Path) -> tuple[str, str]:
    if not path.is_file():
        return "unavailable", "missing canonical source"
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return "invalid", f"invalid JSON: {error.__class__.__name__}"
    return "valid", "canonical JSON readable"


def relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return "private-external-path"


def generated_state(generated: list[Path], expected: dict[Path, str]) -> tuple[str, str]:
    missing = [relative(path) for path in generated if not path.is_file()]
    if missing:
        return "unavailable", "missing generated view(s): " + ", ".join(missing)
    stale = [relative(path) for path in generated if path.read_text(encoding="utf-8") != expected[path]]
    if stale:
        return "stale", "generated view content drift: " + ", ".join(stale)
    return "current", "generated views match canonical rendering"


def carrier(
    identifier: str,
    memory_classes: list[str],
    authority_class: str,
    canonical: list[Path],
    generated: list[Path],
    owner: str,
    freshness: str,
    validation: str,
    reporting_verb: str,
    preservation_state: str,
    authority_flags: dict[str, bool],
    availability: str = "available",
    sub_surfaces: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "id": identifier,
        "memory_classes": memory_classes,
        "availability": availability,
        "authority_class": authority_class,
        "canonical_sources": [relative(path) for path in canonical],
        "generated_views": [relative(path) for path in generated],
        "freshness": freshness,
        "validation_state": validation,
        "owning_command": owner,
        "reporting_verb": reporting_verb,
        "preservation_state": preservation_state,
        "activation_state": "inactive",
        "authority_flags": authority_flags,
        "sub_surfaces": sub_surfaces or [],
    }


def authority_flags(*, identity: bool = False, evidence: bool = False, process: bool = False) -> dict[str, bool]:
    return {
        "identity": identity,
        "evidence": evidence,
        "process_guidance": process,
        "action": False,
    }


def constitution_candidate_surface() -> dict[str, Any]:
    canonical = REPO_ROOT / "mira/constitution-candidate.json"
    generated = REPO_ROOT / "mira/constitution-candidate.md"
    state, validation = json_state(canonical)
    return {
        "id": "constitution-candidate",
        "authority_status": "provisional",
        "canonical_identity": False,
        "availability": "available" if state == "valid" else state,
        "canonical_source": relative(canonical),
        "generated_view": relative(generated),
        "reporting_verb": "proposes",
        "validation_state": validation,
        "owning_command": "tools/run.ps1 mira-constitution",
    }


def rest_surface() -> tuple[dict[str, Any], dict[str, Any]]:
    import mira_continuity
    import rest_receipts

    surface = {
        "id": "rest-inbox", "authority_status": "private-provisional",
        "canonical_identity": False, "availability": "unavailable",
        "canonical_source": None, "generated_view": None,
        "reporting_verb": "records", "validation_state": "private Rest inbox is not configured",
        "owning_command": "tools/run.ps1 rest",
    }
    closure = {
        "availability": "unavailable", "recorded_state": "unknown",
        "current_state": "unknown", "derived_resume": False, "event_count": 0,
        "latest_event_id": None, "closure_debt": [], "requested_reviews": [],
        "mutation_performed": False,
    }
    try:
        inbox = rest_receipts.resolve_inbox(None)
        surface["canonical_source"] = relative(inbox)
        session = rest_receipts.session_uuid()
        source = mira_continuity.find_session_source(session)
        closure = rest_receipts.projection(inbox, session, source)
        state = "exact-session private receipt chain validates" if closure["event_count"] else "canonical portable inbox ready; no receipt recorded"
        surface.update({"availability": "available", "validation_state": state})
    except (OSError, ValueError, rest_receipts.RestError) as error:
        surface["validation_state"] = str(error)
    return surface, closure


def continuity_carrier(*, inspect_sources: bool = False) -> dict[str, Any]:
    import mira_continuity

    canonical = [REPO_ROOT / "mira/continuity/session-registry.json", REPO_ROOT / "mira/continuity/identity-ledger.json"]
    generated = [REPO_ROOT / "mira/identity.md", REPO_ROOT / "mira/continuity/trajectory.md", REPO_ROOT / "mira/continuity/activation.md"]
    states = [json_state(path) for path in canonical]
    expected = mira_continuity.expected_views()
    freshness, note = generated_state(generated, {path: expected[path] for path in generated})
    valid = all(state == "valid" for state, _ in states)
    rest, _ = rest_surface()
    result = carrier(
        "continuity", ["identity", "relational"],
        "canonical identity and session-continuity authority", canonical, generated,
        "tools/run.ps1 mira-continuity", freshness if valid else "invalid",
        "; ".join([message for _, message in states] + [note]), "recorded", "canonical",
        authority_flags(identity=True), "available" if valid else "degraded",
        [constitution_candidate_surface(), rest],
    )
    if inspect_sources and valid:
        try:
            sources = mira_continuity.discover_sources()
            registry = mira_continuity.load_registry()
            expected, captures, added = mira_continuity.expected_ingest(sources, registry=registry)
            changed = [
                path for path, content in captures.items()
                if not path.is_file() or path.read_bytes() != content
            ]
            result["countercheck"] = mira_continuity.summarize_ingest_drift(
                registry,
                expected,
                changed,
                qualifying_sources=len(sources),
                new_captures=len(added),
                active_session_uuid=os.environ.get("CODEX_THREAD_ID", ""),
            )
            if result["countercheck"]["mira_continuity_ingest"] == "drift":
                result["freshness"] = "drift"
                result["availability"] = "degraded"
        except (OSError, ValueError, mira_continuity.ContinuityError) as error:
            result["countercheck"] = {
                "status": "unavailable",
                "detail": f"read-only source comparison failed: {error.__class__.__name__}",
            }
            result["availability"] = "degraded"
    return result


def journal_carrier() -> dict[str, Any]:
    import mira_journal

    canonical = [REPO_ROOT / "mira/journal-registry.json"]
    generated = [REPO_ROOT / "mira/journal.md", REPO_ROOT / "mira/journal/continuity-index.md"]
    state, validation = json_state(canonical[0])
    failures = mira_journal.validate_repository_state()
    stale = any("stale" in failure or "missing generated" in failure for failure in failures)
    freshness = "stale" if stale else ("invalid" if failures else "current")
    note = "; ".join(failures) if failures else "canonical state and generated views validate"
    return carrier(
        "mira-journal", ["autobiographical"], "governed autobiographical interpretation",
        canonical, generated, "tools/run.ps1 mira-journal",
        freshness if state == "valid" else state, f"{validation}; {note}",
        "interpreted", "canonical", authority_flags(),
        "available" if state == "valid" and not failures else "degraded",
    )


def recursive_carrier() -> dict[str, Any]:
    import recursive_learning_ledger

    canonical = [REPO_ROOT / "narrative-geopolitics/work/system-improvement/recursive-learning-ledger.json"]
    generated = [REPO_ROOT / "narrative-geopolitics/work/system-improvement/recursive-learning-ledger.md"]
    state, validation = json_state(canonical[0])
    failures = recursive_learning_ledger.validate_ledger()
    stale = any("drift" in failure or "Markdown missing" in failure for failure in failures)
    freshness = "stale" if stale else ("invalid" if failures else "current")
    note = "; ".join(failures) if failures else "canonical ledger and generated Markdown validate"
    return carrier(
        "recursive-learning", ["procedural"], "internal-canonical process evidence",
        canonical, generated, "tools/run.ps1 recursive-learn",
        freshness if state == "valid" else state, f"{validation}; {note}",
        "supports", "canonical", authority_flags(process=True),
        "available" if state == "valid" and not failures else "degraded",
    )


def archive_carrier(*, inspect_catalog: bool = False) -> dict[str, Any]:
    registry = REPO_ROOT / "archive/collections.json"
    state, validation = json_state(registry)
    configured_path = resolve_environment(ARCHIVE_CONFIG_ENV)
    config = Path(configured_path) if configured_path else DEFAULT_ARCHIVE_CONFIG
    if not configured_path and not config.is_file():
        for fallback in (EXTERNAL_ARCHIVE_CONFIG, FORMER_ARCHIVE_CONFIG, LEGACY_ARCHIVE_CONFIG):
            if fallback.is_file():
                print(
                    f"{fallback} is deprecated; use {DEFAULT_ARCHIVE_CONFIG}",
                    file=sys.stderr,
                )
                config = fallback
                break
    configured = bool(resolve_environment(ARCHIVE_ROOT_ENV)) or config.is_file()
    result = carrier(
        "archive",
        ["epistemic", "autobiographical", "procedural", "relational"],
        "model-independent storage and lineage; collection-native authority retained",
        [registry],
        [],
        "tools/run.ps1 archive",
        state if configured else "unavailable",
        f"{validation}; " + ("private storage configuration present (catalog not opened)" if configured else "private storage is not configured"),
        "preserves",
        "storage",
        authority_flags(),
        "available" if configured and state == "valid" else ("unavailable" if not configured else "degraded"),
    )
    if inspect_catalog and configured and state == "valid":
        try:
            import archive

            archive_status = archive.status_command(argparse.Namespace())
            visibility = archive_status.get("collections", {})
            zero_records = sorted(
                row["id"] for row in visibility.get("items", [])
                if row.get("registry_present") and int(row.get("active_records", 0)) == 0
            )
            result["countercheck"] = {
                "status": archive_status.get("status"),
                "registry_only": visibility.get("registry_only", []),
                "catalog_only": visibility.get("catalog_only", []),
                "zero_record_collections": zero_records,
            }
            if result["countercheck"]["registry_only"] or result["countercheck"]["catalog_only"]:
                result["freshness"] = "drift"
                result["availability"] = "degraded"
            result["validation_state"] = (
                f"{validation}; private catalog opened read-only; "
                f"registry-only={len(result['countercheck']['registry_only'])}; "
                f"catalog-only={len(result['countercheck']['catalog_only'])}; "
                f"zero-record={len(zero_records)}"
            )
        except (OSError, ValueError, sqlite3.Error, archive.ArchiveError) as error:
            result["countercheck"] = {
                "status": "unavailable",
                "detail": f"read-only catalog check failed: {error.__class__.__name__}",
            }
            result["availability"] = "degraded"
    return result


def geopolitics_carrier() -> dict[str, Any]:
    canonical = [REPO_ROOT / "archive/sources/geopolitics/source-manifest.json", REPO_ROOT / "narrative-geopolitics/work/forecasts/forecast-ledger.md"]
    generated = [REPO_ROOT / "narrative-geopolitics/work/reality/views/outcome-ledger.md"]
    state, validation = json_state(canonical[0])
    missing = [relative(path) for path in canonical[1:] if not path.is_file()]
    available = state == "valid" and not missing
    return carrier(
        "narrative-geopolitics", ["epistemic"],
        "domain-native source, judgment, forecast, verification, and adjudication authorities",
        canonical, generated, "archive-query / reality-check / forecast-review",
        "valid" if available else "invalid",
        validation + ("; missing: " + ", ".join(missing) if missing else ""),
        "supports", "canonical", authority_flags(evidence=True),
        "available" if available else "degraded",
    )


def choice_carrier() -> dict[str, Any]:
    raw = resolve_environment(CHOICE_ENV)
    if not raw:
        return carrier(
            "private-choice-history", ["relational", "procedural"],
            "private outcome-aware process memory", [], [], "tools/run.ps1 choice",
            "unavailable", f"private choice store is not configured; set {CHOICE_ENV}",
            "recorded", "unavailable", authority_flags(process=True), "unavailable",
        )
    path = Path(raw).expanduser()
    if not path.is_absolute() or path.resolve(strict=False).is_relative_to(REPO_ROOT.resolve()):
        availability, freshness, validation = "degraded", "invalid", "choice store must be an absolute path outside Git"
    elif not path.is_file():
        availability, freshness, validation = "unavailable", "unavailable", "configured private choice store does not exist"
    else:
        try:
            with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as connection:
                connection.execute("PRAGMA query_only=ON")
                integrity = connection.execute("PRAGMA quick_check").fetchone()[0]
            availability, freshness, validation = ("available", "valid", "read-only SQLite quick_check: ok") if integrity == "ok" else ("degraded", "invalid", f"read-only SQLite quick_check: {integrity}")
        except sqlite3.Error as error:
            availability, freshness, validation = "degraded", "invalid", f"read-only SQLite check failed: {error.__class__.__name__}"
    return carrier(
        "private-choice-history", ["relational", "procedural"],
        "private outcome-aware process memory", [path], [], "tools/run.ps1 choice",
        freshness, validation, "recorded", "private", authority_flags(process=True), availability,
    )


def cadence_carrier() -> dict[str, Any]:
    import cadence_ledger

    status = cadence_ledger.private_status(resolve_environment(CADENCE_ENV))
    result = carrier(
        "private-cadence-history", ["procedural"],
        "private advisory method-experiment memory",
        [Path("private-external-path")] if status["availability"] != "unavailable" else [],
        [], "tools/run.ps1 cadence", status["freshness"], status["validation"],
        "recorded", "private" if status["availability"] != "unavailable" else "unavailable",
        authority_flags(process=True), status["availability"],
    )
    result["bounded_status"] = {
        "counts": status.get("counts", {}),
        "latest_event_at": status.get("latest_event_at"),
    }
    return result


def mentorship_carrier() -> dict[str, Any]:
    raw = os.environ.get(MENTORSHIP_ENV)
    if not raw:
        return carrier(
            "private-mentorship-history", ["relational", "procedural"],
            "private consent-bound mentorship continuity", [], [],
            "tools/run.ps1 mira-mentor", "unavailable",
            f"private mentorship store is not configured; set {MENTORSHIP_ENV}",
            "recorded", "unavailable", authority_flags(), "unavailable",
        )
    path = Path(raw).expanduser()
    if not path.is_absolute() or path.resolve(strict=False).is_relative_to(REPO_ROOT.resolve()):
        availability, freshness, validation = "degraded", "invalid", "mentorship store must be an absolute path outside Git"
    elif not path.is_file():
        availability, freshness, validation = "unavailable", "unavailable", "configured private mentorship store does not exist"
    else:
        try:
            with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as connection:
                connection.execute("PRAGMA query_only=ON")
                integrity = connection.execute("PRAGMA quick_check").fetchone()[0]
            availability, freshness, validation = ("available", "valid", "read-only SQLite quick_check: ok") if integrity == "ok" else ("degraded", "invalid", f"read-only SQLite quick_check: {integrity}")
        except sqlite3.Error as error:
            availability, freshness, validation = "degraded", "invalid", f"read-only SQLite check failed: {error.__class__.__name__}"
    return carrier(
        "private-mentorship-history", ["relational", "procedural"],
        "private consent-bound mentorship continuity", [path], [],
        "tools/run.ps1 mira-mentor", freshness, validation, "recorded", "private",
        authority_flags(), availability,
    )


ROUTING_RULES = [
    ({"rest"}, "mixed", "rest", 130, "explicit terminal session closure"),
    ({"assess", "cadence", "learning"}, "procedural", "recursive-learn", 120, "explicit cadence learning assessment"),
    ({"admit", "recursive", "learning"}, "procedural", "recursive-learn", 120, "explicit recursive-learning admission"),
    ({"rsi", "candidate"}, "procedural", "recursive-learn", 120, "explicit RSI candidate request"),
    ({"record", "dream"}, "procedural", "dream", 110, "explicit Dream closeout"),
    ({"close", "session", "learning"}, "procedural", "dream", 110, "explicit method closeout"),
    ({"coffee"}, "procedural", "coffee", 100, "explicit Coffee re-entry"),
    ({"cadence", "lesson"}, "procedural", "coffee", 100, "cadence lesson recovery"),
    ({"dream", "handoff"}, "procedural", "coffee", 100, "Dream handoff recovery"),
    ({"score", "forecast"}, "epistemic", "forecast-review", 100, "explicit forecast scoring"),
    ({"resolve", "forecast"}, "epistemic", "forecast-review", 100, "explicit forecast resolution"),
    ({"verify"}, "epistemic", "reality-check", 90, "explicit verification"),
    ({"recover", "journal"}, "autobiographical", "mira-journal", 100, "explicit journal recovery"),
    ({"review", "journal"}, "autobiographical", "mira-journal", 100, "explicit journal review"),
    ({"draft", "journal"}, "autobiographical", "mira-journal", 100, "explicit journal drafting"),
    ({"recover", "session"}, "relational", "mira-continuity", 100, "explicit session recovery"),
    ({"retrieve", "lineage"}, "epistemic", "archive", 100, "explicit lineage retrieval"),
    ({"review", "choice"}, "relational", "learn-from-choices", 100, "explicit choice review"),
    ({"review", "mentorship"}, "relational", "mira-mentor", 100, "explicit mentorship review"),
    ({"forecast"}, "epistemic", "forecast-review", 50, "forecast object"),
    ({"claim"}, "epistemic", "reality-check", 50, "claim object"),
    ({"source"}, "epistemic", "archive-query", 50, "source object"),
    ({"journal"}, "autobiographical", "mira-journal", 50, "journal object"),
    ({"reflection"}, "autobiographical", "mira-journal", 50, "reflection object"),
    ({"learn"}, "procedural", "recursive-learn", 50, "learning object"),
    ({"process"}, "procedural", "recursive-learn", 50, "process object"),
    ({"choice"}, "relational", "learn-from-choices", 50, "choice object"),
    ({"mentor"}, "relational", "mira-mentor", 50, "mentorship object"),
    ({"mentorship"}, "relational", "mira-mentor", 50, "mentorship object"),
    ({"identity"}, "identity", "mira-continuity", 50, "identity object"),
    ({"session"}, "relational", "mira-continuity", 50, "session object"),
    ({"continuity"}, "relational", "mira-continuity", 50, "continuity object"),
    ({"lineage"}, "epistemic", "archive", 50, "lineage object"),
    ({"archive"}, "epistemic", "archive", 50, "archive object"),
]


def route_focus(focus: str | None) -> dict[str, Any]:
    words = set(re.findall(r"[a-z0-9]+", (focus or "").lower().replace("-", " ")))
    matches: dict[str, dict[str, Any]] = {}
    for required, memory_class, owner, priority, reason in ROUTING_RULES:
        if not required <= words:
            continue
        current = matches.get(owner)
        if current is None or priority > current["priority"]:
            matches[owner] = {
                "workflow": owner,
                "memory_class": memory_class,
                "priority": priority,
                "reason": reason,
            }
    candidates = sorted(matches.values(), key=lambda row: (-row["priority"], row["workflow"]))
    if not candidates:
        return {
            "memory_class": "mixed",
            "memory_classes": ["mixed"],
            "owner_candidates": [],
            "recommended_owner": "mira-memory",
            "recommended_owner_reason": "the focus does not identify a carrier-owning workflow",
            "routing_state": "needs-decomposition",
        }
    classes = sorted({row["memory_class"] for row in candidates})
    if "rest" in matches:
        classes = sorted((set(classes) - {"mixed"}) | {"procedural", "relational"})
    top = [row for row in candidates if row["priority"] == candidates[0]["priority"]]
    if len(top) > 1:
        owner = "mira-memory"
        reason = "equally material carrier owners require read-only decomposition"
        routing_state = "needs-decomposition"
    else:
        owner = top[0]["workflow"]
        reason = top[0]["reason"]
        routing_state = "routed"
    return {
        "memory_class": (
            "mixed" if top[0]["workflow"] == "rest"
            else top[0]["memory_class"] if routing_state == "routed" else "mixed"
        ),
        "memory_classes": classes,
        "owner_candidates": candidates,
        "recommended_owner": owner,
        "recommended_owner_reason": reason,
        "routing_state": routing_state,
    }


def classify_focus(focus: str | None) -> tuple[str, str]:
    route = route_focus(focus)
    return route["memory_class"], route["recommended_owner"]


def make_tension(
    identifier: str,
    kind: str,
    observations: list[dict[str, Any]],
    *,
    resolution_owner: str,
    resolution_condition: str,
    must_remain_separate: bool,
) -> dict[str, Any]:
    if kind not in TENSION_KINDS:
        raise ValueError(f"unsupported tension kind: {kind}")
    return {
        "id": identifier,
        "kind": kind,
        "status": "unresolved",
        "observations": observations,
        "resolution_owner": resolution_owner,
        "resolution_condition": resolution_condition,
        "must_remain_separate": must_remain_separate,
    }


def operational_tensions(carriers: list[dict[str, Any]], route: dict[str, Any]) -> list[dict[str, Any]]:
    tensions: list[dict[str, Any]] = []
    for row in carriers:
        if row["id"] == "private-cadence-history" and row.get("bounded_status", {}).get("counts", {}).get("unresolved_rsi_correspondence", 0):
            tensions.append(tension(
                "TENSION-CADENCE-RSI-CORRESPONDENCE",
                "registry-catalog-mismatch",
                [{
                    "carrier": "private-cadence-history", "reporting_verb": "recorded",
                    "detail": "A private represented event names an RSI entry absent from the canonical ledger.",
                    "provenance_refs": ["private-cadence-status", "narrative-geopolitics/work/system-improvement/recursive-learning-ledger.json"],
                }],
                resolution_owner="tools/run.ps1 recursive-learn",
                resolution_condition="reconcile the private correspondence against canonical RSI admission history",
                must_remain_separate=True,
            ))
        if row["freshness"] == "stale":
            tensions.append(make_tension(
                f"TENSION-{row['id'].upper()}-DERIVED-VIEW", "stale-derived-view",
                [{
                    "carrier": row["id"], "reporting_verb": row["reporting_verb"],
                    "detail": row["validation_state"],
                    "provenance_refs": row["canonical_sources"] + row["generated_views"],
                }],
                resolution_owner=row["owning_command"],
                resolution_condition="the carrier-native renderer matches canonical state",
                must_remain_separate=False,
            ))
        countercheck = row.get("countercheck", {})
        if row["id"] == "continuity" and countercheck.get("mira_continuity_ingest") == "drift":
            tensions.append(make_tension(
                "TENSION-CONTINUITY-SOURCE-DRIFT", "canonical-source-drift",
                [{
                    "carrier": "continuity", "reporting_verb": "recorded",
                    "detail": {
                        key: countercheck[key] for key in (
                            "new_captures", "registry_drift", "capture_drift",
                            "active_session_drift_deferred",
                        )
                    },
                    "provenance_refs": ["mira/continuity/session-registry.json", "session-source-discovery"],
                }],
                resolution_owner="tools/run.ps1 mira-continuity",
                resolution_condition="strict registry and capture drift are zero; active work may remain deferred",
                must_remain_separate=False,
            ))
        if row["id"] == "archive" and (
            countercheck.get("registry_only") or countercheck.get("catalog_only")
        ):
            tensions.append(make_tension(
                "TENSION-SYSTEM-ARCHIVE-COLLECTION-PARITY", "registry-catalog-mismatch",
                [{
                    "carrier": "archive", "reporting_verb": "preserves",
                    "detail": {
                        "registry_only": countercheck.get("registry_only", []),
                        "catalog_only": countercheck.get("catalog_only", []),
                        "zero_record_collections": countercheck.get("zero_record_collections", []),
                    },
                    "provenance_refs": ["archive/collections.json", "private-catalog-read-only"],
                }],
                resolution_owner="tools/run.ps1 archive",
                resolution_condition="registry/catalog differences receive collection-native disposition",
                must_remain_separate=False,
            ))
    if route["routing_state"] == "needs-decomposition" and route["owner_candidates"]:
        tensions.append(make_tension(
            "TENSION-MIXED-OWNER-DECOMPOSITION", "insufficient-counterevidence",
            [{
                "carrier": item["workflow"],
                "reporting_verb": "routes",
                "detail": item["reason"],
                "provenance_refs": ["operator-focus"],
            } for item in route["owner_candidates"]],
            resolution_owner="mira-memory",
            resolution_condition="decompose the question by authority before invoking one carrier owner",
            must_remain_separate=True,
        ))
    return tensions


def status(focus: str | None, as_of: str, counterchecks: str = "auto") -> dict[str, Any]:
    if counterchecks not in {"auto", "skip"}:
        raise ValueError("counterchecks must be auto or skip")
    route = route_focus(focus)
    focus_classes = set(route["memory_classes"])
    candidate_workflows = {row["workflow"] for row in route["owner_candidates"]}
    inspect_continuity = counterchecks == "auto" and (
        route["recommended_owner"] == "mira-continuity"
        or (
            route["routing_state"] == "needs-decomposition"
            and "mira-continuity" in candidate_workflows
        )
    )
    inspect_archive = counterchecks == "auto" and (
        route["recommended_owner"] == "archive"
        or bool(focus_classes & {"epistemic", "autobiographical", "procedural", "relational"})
    )
    _, session_closure = rest_surface()
    carriers = [
        continuity_carrier(inspect_sources=inspect_continuity), journal_carrier(),
        recursive_carrier(), archive_carrier(inspect_catalog=inspect_archive),
        geopolitics_carrier(), choice_carrier(), cadence_carrier(), mentorship_carrier(),
    ]
    for row in carriers:
        if row["availability"] == "unavailable":
            row["activation_state"] = "unavailable"
        elif bool(focus_classes & set(row["memory_classes"])):
            row["activation_state"] = "relevant"
    carriers.sort(key=lambda row: (row["activation_state"] != "relevant", row["id"]))
    tensions = operational_tensions(carriers, route)
    gaps = [{"carrier": row["id"], "condition": row["availability"], "detail": row["validation_state"]} for row in carriers if row["availability"] != "available"]
    return {
        "schema_version": SCHEMA_VERSION,
        "as_of": as_of,
        "countercheck_mode": counterchecks,
        "session_closure": session_closure,
        "focus": {
            "text": focus,
            "memory_class": route["memory_class"],
            "memory_classes": route["memory_classes"],
        },
        "carriers": carriers,
        "tensions": tensions,
        "coverage_gaps": gaps,
        "recommended_owner": route["recommended_owner"],
        "recommended_owner_reason": route["recommended_owner_reason"],
        "owner_candidates": route["owner_candidates"],
        "routing_state": route["routing_state"],
        "authority_boundary": "Orientation and routing only. Carrier-native controls retain evidence, identity, privacy, promotion, and mutation authority.",
        "mutation_performed": False,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Mira Memory Status", "", f"- As of: `{payload['as_of']}`",
        f"- Focus class: `{payload['focus']['memory_class']}`",
        f"- Focus classes: `{', '.join(payload['focus']['memory_classes'])}`",
        f"- Counterchecks: `{payload['countercheck_mode']}`",
        f"- Session closure: `{payload['session_closure']['current_state']}`",
        f"- Routing state: `{payload['routing_state']}`",
        f"- Recommended owner: `{payload['recommended_owner']}`",
        f"- Routing reason: {payload['recommended_owner_reason']}",
        "- Mutation performed: `false`", "", "## Carriers", "",
        "| Carrier | Classes | Availability | Freshness | Activation | Reports as | Owner |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["carriers"]:
        lines.append(
            f"| `{row['id']}` | `{', '.join(row['memory_classes'])}` | "
            f"`{row['availability']}` | `{row['freshness']}` | `{row['activation_state']}` | "
            f"`{row['reporting_verb']}` | `{row['owning_command']}` |"
        )
    lines.extend(["", "## Tensions", ""])
    lines.extend(
        f"- `{row['id']}` (`{row['kind']}`): route to `{row['resolution_owner']}`; "
        f"{row['resolution_condition']}"
        for row in payload["tensions"]
    )
    if not payload["tensions"]:
        lines.append("- None.")
    lines.extend(["", "## Coverage gaps", ""])
    lines.extend(f"- `{row['carrier']}`: {row['detail']}" for row in payload["coverage_gaps"])
    if not payload["coverage_gaps"]:
        lines.append("- None.")
    lines.extend(["", "## Boundary", "", payload["authority_boundary"], ""])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Read-only orientation across Mira memory carriers.")
    commands = root.add_subparsers(dest="command", required=True)
    command = commands.add_parser("status", help="Report carrier availability, freshness, and ownership.")
    command.add_argument("--focus")
    command.add_argument("--counterchecks", choices=("auto", "skip"), default="auto")
    command.add_argument("--as-of")
    command.add_argument("--json", action="store_true")
    return root


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    try:
        payload = status(args.focus, parse_as_of(args.as_of), args.counterchecks)
    except (OSError, ValueError) as error:
        print(f"mira-memory error: {error}")
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) if args.json else render_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

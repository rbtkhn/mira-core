from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

from portable_paths import require_private_path, state_path


REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_ROOT = REPO_ROOT / "archive" / "library"
REGISTRY_PATH = LIBRARY_ROOT / "library-registry.json"
TEXT_SOURCES_INDEX_PATH = LIBRARY_ROOT / "text-sources-index.md"
ERA_IDS = ("ancient", "medieval", "colonial", "industrial", "digital")
SOURCE_TYPES = {
    "primary",
    "classical",
    "chronicle",
    "legal",
    "religious",
    "literary",
    "historiography",
    "reference",
    "database",
    "digital-born",
}
STATUSES = {"stub", "located", "available", "reviewed"}
TEXT_STATUSES = {"missing", "available", "verified", "needs-review"}
COVERAGE_STATUSES = {
    "unknown",
    "selected-works",
    "representative-selection",
    "principal-work",
    "principal-works",
    "major-works-complete",
    "complete-surviving-corpus",
    "partial-work",
    "fragmentary",
    "metadata-only",
}
BODY_COVERAGE_STATUSES = {
    "unknown",
    "complete-work",
    "partial-work",
    "selected-passages",
    "fragmentary",
}
LICENSE_STATUSES = {
    "public-domain",
    "open-license",
    "permissioned",
    "unknown",
    "restricted",
}
TEXT_EXTENSIONS = {".txt", ".md", ".xml"}
BODY_STATUSES = {"available", "verified", "needs-review"}
TEXT_CHROME_PATTERNS = (
    re.compile(r"^Jump to (navigation|search)$", re.IGNORECASE),
    re.compile(r"^Search (Swaveda|Wikisource)$", re.IGNORECASE),
    re.compile(r"^This page was last edited", re.IGNORECASE),
    re.compile(r"^Retrieved from ", re.IGNORECASE),
    re.compile(r"^(Discussion|Read|Edit|View history|Tools|Print/export|Download EPUB|Download PDF)$", re.IGNORECASE),
)
BODY_REQUIRED_FIELDS = {
    "body_id",
    "work_title",
    "text_location",
    "text_sha256",
    "text_bytes",
    "text_encoding",
    "license_status",
    "status",
}
ERA_BASES = {
    "subject_period",
    "composition_period",
    "edition_period",
    "multi_period",
}
REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "title",
    "author",
    "subject_era",
    "date_label",
    "era_basis",
    "civilization_tags",
    "source_type",
    "location",
    "status",
}


class LibraryError(RuntimeError):
    pass


def load_registry(path: Path | None = None) -> dict[str, Any]:
    path = REGISTRY_PATH if path is None else path
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise LibraryError(f"missing library registry: {relative(path)}") from error
    except json.JSONDecodeError as error:
        raise LibraryError(f"library registry invalid JSON: line {error.lineno}") from error
    if not isinstance(value, dict):
        raise LibraryError("library registry must be a JSON object")
    return value


def save_registry(registry: Mapping[str, Any], path: Path | None = None) -> None:
    path = REGISTRY_PATH if path is None else path
    path.write_text(json.dumps(registry, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def text(value: Any) -> str:
    return str(value or "").strip()


def find_source(registry: Mapping[str, Any], source_id: str) -> dict[str, Any]:
    for source in registry.get("sources", []):
        if isinstance(source, dict) and text(source.get("source_id")) == source_id:
            return source
    raise LibraryError(f"unknown library source_id: {source_id}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_text_root(environment: Mapping[str, str] | None = None) -> Path:
    source = os.environ if environment is None else environment
    configured = text(source.get("MIRA_CORE_LIBRARY_TEXT_ROOT"))
    return Path(configured).expanduser() if configured else state_path("library/texts", environment=source)


def ensure_private_text_root(root: Path) -> Path:
    try:
        resolved = require_private_path(root, label="library text root", repo_root=REPO_ROOT)
    except ValueError as error:
        raise LibraryError(str(error)) from error
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def private_text_root_allowed(root: Path) -> bool:
    try:
        require_private_path(root, label="library text root", repo_root=REPO_ROOT)
    except ValueError:
        return False
    return True


def resolve_text_location(location: Any, environment: Mapping[str, str] | None = None) -> Path | None:
    if not text(location):
        return None
    raw = text(location)
    if raw.startswith("library-text://"):
        relative_path = raw.removeprefix("library-text://").lstrip("/")
        return resolve_text_root(environment) / relative_path
    return Path(raw).expanduser()


def text_record_path(source_id: str, original: Path, text_root: Path) -> Path:
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "-", source_id).strip("-")
    return text_root / f"{safe_id}{original.suffix.lower()}"


def text_body_path(body_id: str, original: Path, text_root: Path) -> Path:
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "-", body_id).strip("-")
    return text_root / f"{safe_id}{original.suffix.lower()}"


def derive_body_id(source_id: str, work_title: str, translator: str, edition: str) -> str:
    parts = [source_id, work_title, translator, edition]
    suffix = "-".join(re.findall(r"[A-Za-z0-9]+", " ".join(part for part in parts[1:] if part).upper()))
    return f"{source_id}-{suffix[:48]}" if suffix else source_id


def text_uri(path: Path, text_root: Path) -> str:
    return "library-text://" + path.relative_to(text_root).as_posix()


def source_text_bodies(source: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    bodies = source.get("text_bodies", [])
    if isinstance(bodies, list):
        return [body for body in bodies if isinstance(body, dict)]
    return []


def single_body_from_source(source: Mapping[str, Any]) -> Mapping[str, Any] | None:
    status = text(source.get("text_status"))
    if status not in {"available", "verified"}:
        return None
    return {
        "body_id": text(source.get("source_id")),
        "work_title": text(source.get("title")),
        "text_location": source.get("text_location"),
        "text_sha256": source.get("text_sha256"),
        "text_bytes": source.get("text_bytes"),
        "text_encoding": source.get("text_encoding"),
        "language": source.get("language"),
        "translator": source.get("translator"),
        "editor": source.get("editor"),
        "edition_label": source.get("edition_label"),
        "license_status": source.get("license_status"),
        "license_notes": source.get("license_notes"),
        "status": status,
    }


def all_text_bodies(source: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    bodies = source_text_bodies(source)
    if bodies:
        return bodies
    single = single_body_from_source(source)
    return ([single] if single else []) + bodies


def validate_era_definitions(registry: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    definitions = registry.get("era_definitions")
    if not isinstance(definitions, list):
        return ["library registry era_definitions must be a list"]
    seen: set[str] = set()
    for item in definitions:
        if not isinstance(item, dict):
            failures.append("library era definition must be an object")
            continue
        era_id = text(item.get("id"))
        if era_id in seen:
            failures.append(f"duplicate library era definition: {era_id}")
        seen.add(era_id)
        if era_id not in ERA_IDS:
            failures.append(f"unknown library era definition: {era_id}")
        for field in ("label", "range", "description"):
            if not text(item.get(field)):
                failures.append(f"library era {era_id or '<missing>'} missing {field}")
        for field in ("start_year", "end_year"):
            value = item.get(field)
            if value is not None and not isinstance(value, int):
                failures.append(f"library era {era_id or '<missing>'} {field} must be integer or null")
    if tuple(item.get("id") for item in definitions if isinstance(item, dict)) != ERA_IDS:
        failures.append("library era definitions must remain in canonical order")
    return failures


def source_text(source: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for key in (
        "source_id",
        "title",
        "author",
        "date_label",
        "source_type",
        "status",
        "notes",
        "text_status",
        "text_location",
        "coverage_status",
        "coverage_notes",
        "language",
        "translator",
        "editor",
        "edition_label",
        "license_status",
        "license_notes",
    ):
        parts.append(text(source.get(key)))
    for body in source_text_bodies(source):
        for key in (
            "body_id",
            "work_title",
            "text_status",
            "status",
            "text_location",
            "language",
            "translator",
            "editor",
            "edition_label",
            "license_status",
            "license_notes",
            "coverage_status",
            "coverage_notes",
        ):
            parts.append(text(body.get(key)))
    for key in ("civilization_tags", "secondary_eras"):
        value = source.get(key, [])
        if isinstance(value, list):
            parts.extend(text(item) for item in value)
    location = source.get("location")
    if isinstance(location, str):
        parts.append(location)
    elif isinstance(location, dict):
        for value in location.values():
            if isinstance(value, list):
                parts.extend(text(item) for item in value)
            else:
                parts.append(text(value))
    return " ".join(part for part in parts if part).casefold()


def validate_text_body(body: Any, source_label: str, seen_body_ids: set[str], index: int) -> list[str]:
    label = f"{source_label} text body #{index}"
    failures: list[str] = []
    if not isinstance(body, dict):
        return [f"{label} must be an object"]
    body_id = text(body.get("body_id"))
    if body_id:
        label = f"{source_label} text body {body_id}"
        if body_id in seen_body_ids:
            failures.append(f"duplicate library text body_id: {body_id}")
        seen_body_ids.add(body_id)
    for field in sorted(BODY_REQUIRED_FIELDS):
        if field not in body:
            failures.append(f"{label} missing required field: {field}")
    for field in ("body_id", "work_title", "text_location", "text_sha256", "text_encoding", "license_status", "status"):
        if field in body and not text(body.get(field)):
            failures.append(f"{label} has blank {field}")
    status = text(body.get("status"))
    if status and status not in BODY_STATUSES:
        failures.append(f"{label} has invalid status: {body.get('status')}")
    coverage_status = text(body.get("coverage_status"))
    if coverage_status and coverage_status not in BODY_COVERAGE_STATUSES:
        failures.append(f"{label} has invalid coverage_status: {body.get('coverage_status')}")
    if "coverage_notes" in body and body.get("coverage_notes") is not None and not isinstance(body.get("coverage_notes"), str):
        failures.append(f"{label} coverage_notes must be a string or null")
    license_status = text(body.get("license_status"))
    if license_status and license_status not in LICENSE_STATUSES:
        failures.append(f"{label} has invalid license_status: {body.get('license_status')}")
    if "text_sha256" in body and text(body.get("text_sha256")) and not re.fullmatch(r"[0-9a-f]{64}", text(body.get("text_sha256"))):
        failures.append(f"{label} has invalid text_sha256")
    value = body.get("text_bytes")
    if value is not None and (not isinstance(value, int) or value < 0):
        failures.append(f"{label} text_bytes must be a non-negative integer")
    for field in ("language", "translator", "editor", "edition_label", "license_notes", "coverage_notes"):
        if field in body and body.get(field) is not None and not isinstance(body.get(field), str):
            failures.append(f"{label} {field} must be a string or null")
    return failures


def validate_source(source: Any, seen: set[str], index: int) -> list[str]:
    label = f"library source #{index}"
    failures: list[str] = []
    if not isinstance(source, dict):
        return [f"{label} must be an object"]
    source_id = text(source.get("source_id"))
    if source_id:
        label = source_id
        if source_id in seen:
            failures.append(f"duplicate library source_id: {source_id}")
        seen.add(source_id)
    for field in sorted(REQUIRED_SOURCE_FIELDS):
        if field not in source:
            failures.append(f"{label} missing required field: {field}")
    for field in ("source_id", "title", "author", "date_label"):
        if field in source and not text(source.get(field)):
            failures.append(f"{label} has blank {field}")
    for field in ("subject_era", "source_composition_era", "edition_era"):
        value = source.get(field)
        if value is not None and text(value) not in ERA_IDS:
            failures.append(f"{label} has unknown {field}: {value}")
    secondary = source.get("secondary_eras", [])
    if secondary is not None:
        if not isinstance(secondary, list):
            failures.append(f"{label} secondary_eras must be a list")
        else:
            for era in secondary:
                if text(era) not in ERA_IDS:
                    failures.append(f"{label} has unknown secondary era: {era}")
    if "source_type" in source and text(source.get("source_type")) not in SOURCE_TYPES:
        failures.append(f"{label} has invalid source_type: {source.get('source_type')}")
    if "status" in source and text(source.get("status")) not in STATUSES:
        failures.append(f"{label} has invalid status: {source.get('status')}")
    if "era_basis" in source and text(source.get("era_basis")) not in ERA_BASES:
        failures.append(f"{label} has invalid era_basis: {source.get('era_basis')}")
    text_status = text(source.get("text_status"))
    if text_status and text_status not in TEXT_STATUSES:
        failures.append(f"{label} has invalid text_status: {source.get('text_status')}")
    coverage_status = text(source.get("coverage_status"))
    if coverage_status and coverage_status not in COVERAGE_STATUSES:
        failures.append(f"{label} has invalid coverage_status: {source.get('coverage_status')}")
    if "coverage_notes" in source and source.get("coverage_notes") is not None and not isinstance(source.get("coverage_notes"), str):
        failures.append(f"{label} coverage_notes must be a string or null")
    if coverage_status == "complete-surviving-corpus":
        notes = text(source.get("coverage_notes")).casefold()
        if "surviving" not in notes or not any(marker in notes for marker in ("represented", "covering", "covers")):
            failures.append(f"{label} complete-surviving-corpus requires coverage_notes naming the surviving corpus represented")
        if text_status not in {"available", "verified"} or not (source_text_bodies(source) or single_body_from_source(source)):
            failures.append(f"{label} complete-surviving-corpus requires at least one available or verified text body")
    license_status = text(source.get("license_status"))
    if license_status and license_status not in LICENSE_STATUSES:
        failures.append(f"{label} has invalid license_status: {source.get('license_status')}")
    if "text_sha256" in source and text(source.get("text_sha256")) and not re.fullmatch(r"[0-9a-f]{64}", text(source.get("text_sha256"))):
        failures.append(f"{label} has invalid text_sha256")
    if "text_bytes" in source:
        value = source.get("text_bytes")
        if value is not None and (not isinstance(value, int) or value < 0):
            failures.append(f"{label} text_bytes must be a non-negative integer or null")
    for field in ("text_encoding", "language", "translator", "editor", "edition_label", "license_notes"):
        if field in source and source.get(field) is not None and not isinstance(source.get(field), str):
            failures.append(f"{label} {field} must be a string or null")
    has_text_bodies = bool(source_text_bodies(source))
    if text_status in {"available", "verified"} and not has_text_bodies:
        for field in ("text_location", "text_sha256", "text_bytes", "text_encoding", "license_status"):
            if field not in source or source.get(field) is None or (isinstance(source.get(field), str) and not source.get(field).strip()):
                failures.append(f"{label} text_status {text_status} requires {field}")
    bodies = source.get("text_bodies", [])
    if bodies is not None:
        if not isinstance(bodies, list):
            failures.append(f"{label} text_bodies must be a list")
        else:
            seen_body_ids: set[str] = set()
            for body_index, body in enumerate(bodies, start=1):
                failures.extend(validate_text_body(body, label, seen_body_ids, body_index))
    tags = source.get("civilization_tags", [])
    if not isinstance(tags, list) or any(not isinstance(item, str) or not item.strip() for item in tags):
        failures.append(f"{label} civilization_tags must be a list of non-empty strings")
    location = source.get("location")
    if "location" in source and not isinstance(location, (str, dict)):
        failures.append(f"{label} location must be a string or object")
    for field in ("date_start", "date_end"):
        value = source.get(field)
        if value is not None and not isinstance(value, int):
            failures.append(f"{label} {field} must be integer or null")
    start = source.get("date_start")
    end = source.get("date_end")
    if isinstance(start, int) and isinstance(end, int) and start > end:
        failures.append(f"{label} date range is inverted")
    return failures


def validate_registry(registry: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    if registry.get("schema_version") != 1:
        failures.append("library registry schema_version must be 1")
    if registry.get("registry_id") != "mira-library-v1":
        failures.append("library registry_id must be mira-library-v1")
    if not text(registry.get("authority_boundary")):
        failures.append("library registry missing authority_boundary")
    failures.extend(validate_era_definitions(registry))
    sources = registry.get("sources")
    if not isinstance(sources, list):
        failures.append("library registry sources must be a list")
    else:
        seen: set[str] = set()
        for index, source in enumerate(sources, start=1):
            failures.extend(validate_source(source, seen, index))
    return failures


def validate_scaffold(repo_root: Path | None = None) -> list[str]:
    repo_root = REPO_ROOT if repo_root is None else repo_root
    failures: list[str] = []
    root = repo_root / "archive" / "library"
    required = [root / "README.md", root / "library-registry.json", root / "text-sources-index.md"]
    required.extend(root / era / "index.md" for era in ERA_IDS)
    failures.extend(f"missing library scaffold file: {relative(path)}" for path in required if not path.is_file())
    if failures:
        return failures
    try:
        registry = load_registry(root / "library-registry.json")
    except LibraryError as error:
        return [str(error)]
    failures.extend(validate_registry(registry))
    text_sources_index = root / "text-sources-index.md"
    if text_sources_index.is_file() and text_sources_index.read_text(encoding="utf-8") != render_text_sources_index(registry):
        failures.append(f"library text sources index is stale: {relative(text_sources_index)}")
    for era in ERA_IDS:
        index = root / era / "index.md"
        content = index.read_text(encoding="utf-8")
        if content != render_era_index(registry, era):
            failures.append(f"library era index is stale: {relative(index)}")
    return failures


def matching_sources(
    sources: Iterable[Mapping[str, Any]],
    *,
    era: str | None = None,
    civilization: str | None = None,
    source_type: str | None = None,
    query: str | None = None,
) -> list[Mapping[str, Any]]:
    result = []
    query_terms = [term.casefold() for term in re.findall(r"[A-Za-z0-9-]+", query or "")]
    for source in sources:
        if era and source.get("subject_era") != era and era not in source.get("secondary_eras", []):
            continue
        if civilization and civilization.casefold() not in {text(item).casefold() for item in source.get("civilization_tags", [])}:
            continue
        if source_type and source.get("source_type") != source_type:
            continue
        haystack = source_text(source)
        if query_terms and not all(term in haystack for term in query_terms):
            continue
        result.append(source)
    return sorted(result, key=lambda item: text(item.get("source_id")))


def markdown_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "/")


def body_language(body: Mapping[str, Any]) -> str:
    return text(body.get("language")).casefold()


def is_english_body(body: Mapping[str, Any]) -> bool:
    language = body_language(body)
    return language == "english" or "english" in {part.strip() for part in language.split(";")}


def is_original_language_body(body: Mapping[str, Any]) -> bool:
    language = body_language(body)
    if not language or is_english_body(body):
        return False
    return True


def source_modeling_flags(source: Mapping[str, Any]) -> list[str]:
    flags: set[str] = set()
    haystack = " ".join(
        text(source.get(key))
        for key in ("title", "author", "source_type", "notes", "coverage_status", "coverage_notes", "era_basis")
    ).casefold()
    author = text(source.get("author")).casefold()
    title = text(source.get("title")).casefold()
    if text(source.get("source_type")) == "religious" or any(
        marker in haystack
        for marker in ("sacred", "scripture", "biblical", "bible", "veda", "avesta", "buddhist", "jain")
    ):
        flags.add("sacred_corpus")
    if text(source.get("source_type")) == "religious" and any(
        marker in haystack for marker in ("canon", "canonical", "testament", "tripitaka", "vulgate", "septuagint")
    ):
        flags.add("canonical_collection")
    if any(marker in author for marker in ("tradition", "anonymous", "textual")) or any(
        marker in title for marker in ("tradition", "inscriptions")
    ):
        flags.add("anonymous_tradition")
    if text(source.get("coverage_status")) == "fragmentary":
        flags.add("fragmentary_author")
    if len(source.get("secondary_eras", []) or []) > 1 or text(source.get("era_basis")) == "multi_period":
        flags.add("multi_witness")
    if any(marker in haystack for marker in ("redaction", "recension", "transmitted", "manuscript")):
        flags.add("later_redaction")
    if any(marker in haystack for marker in ("colonial", "missionary", "company rule")):
        flags.add("colonial_archive")
    if any(marker in haystack for marker in ("newspaper", "pamphlet", "state paper", "scientific")):
        flags.add("industrial_print")
    if text(source.get("source_type")) in {"database", "digital-born"} or any(
        marker in haystack for marker in ("dataset", "software", "platform", "web")
    ):
        flags.add("digital_record")
    return sorted(flags)


def audit_sources(sources: Iterable[Mapping[str, Any]], era: str | None = None) -> dict[str, Any]:
    rows = [source for source in sources if isinstance(source, dict)]
    if era:
        rows = matching_sources(rows, era=era)
    else:
        rows = sorted(rows, key=lambda item: text(item.get("source_id")))
    summary = {
        "total_sources": len(rows),
        "with_text_bodies": 0,
        "without_text_bodies": 0,
        "english_available": 0,
        "original_language_available": 0,
        "bilingual_available": 0,
        "verified_bodies": 0,
        "available_bodies": 0,
        "needs_review_bodies": 0,
        "missing_text_sources": 0,
        "stub_sources": 0,
    }
    by_era = {era_id: 0 for era_id in ERA_IDS}
    by_source_type: dict[str, int] = {}
    by_coverage_status: dict[str, int] = {}
    by_text_status: dict[str, int] = {}
    by_civilization: dict[str, int] = {}
    missing_english: list[dict[str, str]] = []
    missing_original_language: list[dict[str, str]] = []
    stubbed: list[dict[str, str]] = []
    special_modeling: list[dict[str, Any]] = []
    next_candidates: list[dict[str, Any]] = []
    for source in rows:
        source_id = text(source.get("source_id"))
        subject_era = text(source.get("subject_era"))
        if subject_era in by_era:
            by_era[subject_era] += 1
        by_source_type[text(source.get("source_type")) or "unknown"] = by_source_type.get(text(source.get("source_type")) or "unknown", 0) + 1
        coverage = text(source.get("coverage_status")) or "unset"
        by_coverage_status[coverage] = by_coverage_status.get(coverage, 0) + 1
        text_status = text(source.get("text_status")) or "unset"
        by_text_status[text_status] = by_text_status.get(text_status, 0) + 1
        for tag in source.get("civilization_tags", []) or []:
            key = text(tag).casefold()
            by_civilization[key] = by_civilization.get(key, 0) + 1
        bodies = all_text_bodies(source)
        if bodies:
            summary["with_text_bodies"] += 1
        else:
            summary["without_text_bodies"] += 1
        english = any(is_english_body(body) for body in bodies)
        original = any(is_original_language_body(body) for body in bodies)
        if english:
            summary["english_available"] += 1
        else:
            missing_english.append({"source_id": source_id, "author": text(source.get("author")), "title": text(source.get("title"))})
        if original:
            summary["original_language_available"] += 1
        else:
            missing_original_language.append({"source_id": source_id, "author": text(source.get("author")), "title": text(source.get("title"))})
        if english and original:
            summary["bilingual_available"] += 1
        if text_status in {"missing", "unset"} or not bodies:
            summary["missing_text_sources"] += 1
        if text(source.get("status")) == "stub":
            summary["stub_sources"] += 1
            stubbed.append({"source_id": source_id, "author": text(source.get("author")), "title": text(source.get("title"))})
        body_statuses = [text(body.get("status")) or text(body.get("text_status")) for body in bodies]
        summary["verified_bodies"] += sum(1 for status in body_statuses if status == "verified")
        summary["available_bodies"] += sum(1 for status in body_statuses if status == "available")
        summary["needs_review_bodies"] += sum(1 for status in body_statuses if status == "needs-review")
        flags = source_modeling_flags(source)
        if flags:
            special_modeling.append(
                {
                    "source_id": source_id,
                    "author": text(source.get("author")),
                    "title": text(source.get("title")),
                    "flags": flags,
                }
            )
        if (not bodies) or (not english) or (not original) or coverage in {"metadata-only", "unknown", "unset", "principal-work", "principal-works", "fragmentary"}:
            next_candidates.append(
                {
                    "source_id": source_id,
                    "author": text(source.get("author")),
                    "title": text(source.get("title")),
                    "needs": [
                        need
                        for need, present in (
                            ("text-body", bool(bodies)),
                            ("english", english),
                            ("original-language", original),
                            ("coverage-review", coverage not in {"metadata-only", "unknown", "unset", "principal-work", "principal-works", "fragmentary"}),
                        )
                        if not present
                    ],
                    "modeling_flags": flags,
                }
            )
    return {
        "era": era,
        "summary": summary,
        "by_era": {key: value for key, value in by_era.items() if value or era is None},
        "by_source_type": dict(sorted(by_source_type.items())),
        "by_text_status": dict(sorted(by_text_status.items())),
        "by_coverage_status": dict(sorted(by_coverage_status.items())),
        "by_civilization": dict(sorted(by_civilization.items())),
        "missing_english": missing_english,
        "missing_original_language": missing_original_language,
        "stubbed_sources": stubbed,
        "special_modeling_required": special_modeling,
        "recommended_next_admissions": next_candidates[:20],
    }


def render_audit_markdown(registry: Mapping[str, Any], audit: Mapping[str, Any]) -> str:
    era = audit.get("era")
    label = "Whole Library" if not era else next(
        (text(item.get("label")) for item in registry.get("era_definitions", []) if isinstance(item, dict) and item.get("id") == era),
        str(era).title(),
    )
    summary = audit.get("summary", {})
    lines = [
        f"# {label} Library Audit",
        "",
        "Read-only coverage audit generated from `archive/library/library-registry.json`.",
        "",
        "## Summary",
        "",
        f"- Sources: {summary.get('total_sources', 0)}",
        f"- With text bodies: {summary.get('with_text_bodies', 0)}",
        f"- Missing text bodies: {summary.get('without_text_bodies', 0)}",
        f"- English available: {summary.get('english_available', 0)}",
        f"- Original-language available: {summary.get('original_language_available', 0)}",
        f"- English and original available: {summary.get('bilingual_available', 0)}",
        f"- Stub sources: {summary.get('stub_sources', 0)}",
        "",
        "## Coverage By Text Status",
        "",
    ]
    for key, value in audit.get("by_text_status", {}).items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Missing English Texts", ""])
    for row in audit.get("missing_english", [])[:20]:
        lines.append(f"- `{row['source_id']}`: {row['author']} - {row['title']}")
    if not audit.get("missing_english"):
        lines.append("- None.")
    lines.extend(["", "## Missing Original-Language Texts", ""])
    for row in audit.get("missing_original_language", [])[:20]:
        lines.append(f"- `{row['source_id']}`: {row['author']} - {row['title']}")
    if not audit.get("missing_original_language"):
        lines.append("- None.")
    lines.extend(["", "## Special Modeling Required", ""])
    for row in audit.get("special_modeling_required", [])[:20]:
        lines.append(f"- `{row['source_id']}`: {', '.join(row['flags'])}")
    if not audit.get("special_modeling_required"):
        lines.append("- None.")
    lines.extend(["", "## Recommended Next Admissions", ""])
    for row in audit.get("recommended_next_admissions", [])[:20]:
        needs = ", ".join(row.get("needs", [])) or "review"
        lines.append(f"- `{row['source_id']}`: {needs}")
    if not audit.get("recommended_next_admissions"):
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def render_text_sources_index(registry: Mapping[str, Any]) -> str:
    rows: list[dict[str, Any]] = []
    for source in registry.get("sources", []):
        if not isinstance(source, dict):
            continue
        for body in source_text_bodies(source):
            rows.append(
                {
                    "source_id": source.get("source_id", ""),
                    "author": source.get("author", ""),
                    "title": source.get("title", ""),
                    "source_coverage": source.get("coverage_status", ""),
                    "work": body.get("work_title", ""),
                    "body_coverage": body.get("coverage_status", ""),
                    "edition": body.get("edition_label", ""),
                    "language": body.get("language", ""),
                    "license": body.get("license_status", ""),
                    "bytes": body.get("text_bytes", ""),
                    "uri": body.get("text_location", ""),
                }
            )
    rows.sort(key=lambda row: (text(row["source_id"]), text(row["work"]), text(row["edition"]), text(row["uri"])))
    lines = [
        "# Library Text Sources Index",
        "",
        "This index lists source text bodies admitted in `archive/library/library-registry.json`. The source bodies themselves are local payloads stored under the platform Mira Core state root at `library/texts/`; this file records only metadata and logical text URIs.",
        "",
        "- Registry: `library-registry.json`",
        f"- Text bodies indexed: {len(rows)}",
        f"- Registry ID: `{registry.get('registry_id', '')}`",
        "",
        "| Source ID | Author | Registry title | Source coverage | Work / body | Body coverage | Edition | Language | License | Bytes | Text URI |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{markdown_cell(row['source_id'])}` | {markdown_cell(row['author'])} | {markdown_cell(row['title'])} | {markdown_cell(row['source_coverage'])} | {markdown_cell(row['work'])} | {markdown_cell(row['body_coverage'])} | {markdown_cell(row['edition'])} | {markdown_cell(row['language'])} | {markdown_cell(row['license'])} | {markdown_cell(row['bytes'])} | `{markdown_cell(row['uri'])}` |"
        )
    return "\n".join(lines) + "\n"


def era_definition(registry: Mapping[str, Any], era: str) -> Mapping[str, Any]:
    for item in registry.get("era_definitions", []):
        if isinstance(item, dict) and text(item.get("id")) == era:
            return item
    raise LibraryError(f"missing library era definition: {era}")


def primary_era_sources(registry: Mapping[str, Any], era: str) -> list[Mapping[str, Any]]:
    return sorted(
        (
            source
            for source in registry.get("sources", [])
            if isinstance(source, dict) and text(source.get("subject_era")) == era
        ),
        key=lambda source: text(source.get("source_id")),
    )


def render_era_index(registry: Mapping[str, Any], era: str) -> str:
    if era not in ERA_IDS:
        raise LibraryError(f"unknown library era: {era}")
    definition = era_definition(registry, era)
    sources = primary_era_sources(registry, era)
    lines = [
        f"# {text(definition.get('label'))} Library Index",
        "",
        f"Era: `{era}`",
        f"Range: {text(definition.get('range'))}",
        f"Status: `{'active' if sources else 'scaffold'}`",
        "",
        "## Sources",
        "",
    ]
    if not sources:
        lines.append("No sources admitted yet.")
    else:
        lines.extend(
            [
                "Generated from `../library-registry.json`. Do not edit this source list directly.",
                "",
                "| Source ID | Authority | Title | Dates | Type | Record status | Text status | Coverage |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for source in sources:
            lines.append(
                f"| `{markdown_cell(source.get('source_id'))}` | {markdown_cell(source.get('author'))} | {markdown_cell(source.get('title'))} | {markdown_cell(source.get('date_label'))} | {markdown_cell(source.get('source_type'))} | {markdown_cell(source.get('status'))} | {markdown_cell(source.get('text_status') or 'missing')} | {markdown_cell(source.get('coverage_status') or 'unknown')} |"
            )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "This shelf is for source records whose primary subject period belongs to the",
            f"{text(definition.get('label'))} era. It is a retrieval shelf, not a universal historical ontology.",
        ]
    )
    if era == "colonial":
        lines.extend(
            [
                "",
                "In Mira Library, `colonial` is a broad early-modern shelf and is not limited to",
                "European colonial history.",
            ]
        )
    return "\n".join(lines) + "\n"


def validate_command(args: argparse.Namespace) -> dict[str, Any]:
    failures = validate_scaffold()
    return {"status": "passed" if not failures else "failed", "failures": failures}


def list_command(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    failures = validate_registry(registry)
    if failures:
        raise LibraryError("; ".join(failures))
    sources = matching_sources(registry.get("sources", []), era=args.era)
    return {"status": "ok", "era": args.era, "count": len(sources), "sources": sources}


def search_command(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    failures = validate_registry(registry)
    if failures:
        raise LibraryError("; ".join(failures))
    sources = matching_sources(
        registry.get("sources", []),
        era=args.era,
        civilization=args.civilization,
        source_type=args.type,
        query=args.query,
    )
    return {
        "status": "ok",
        "query": args.query,
        "era": args.era,
        "civilization": args.civilization,
        "type": args.type,
        "count": len(sources),
        "sources": sources,
    }


def audit_command(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    failures = validate_registry(registry)
    if failures:
        raise LibraryError("; ".join(failures))
    audit = audit_sources(registry.get("sources", []), era=args.era)
    return {
        "status": "ok",
        "registry_id": registry.get("registry_id"),
        "authority_effect": "none",
        "audit": audit,
        "markdown": render_audit_markdown(registry, audit) if args.format == "markdown" else None,
    }


def render_index_command(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    failures = validate_registry(registry)
    if failures:
        raise LibraryError("; ".join(failures))
    rendered = {TEXT_SOURCES_INDEX_PATH: render_text_sources_index(registry)}
    rendered.update({LIBRARY_ROOT / era / "index.md": render_era_index(registry, era) for era in ERA_IDS})
    stale_paths = [path for path, content in rendered.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    would_update = bool(stale_paths)
    if args.check:
        return {
            "status": "passed" if not would_update else "failed",
            "path": relative(TEXT_SOURCES_INDEX_PATH),
            "paths": [relative(path) for path in rendered],
            "stale_paths": [relative(path) for path in stale_paths],
            "text_bodies_indexed": rendered[TEXT_SOURCES_INDEX_PATH].count("\n| `"),
            "era_sources_indexed": {era: len(primary_era_sources(registry, era)) for era in ERA_IDS},
            "would_update": would_update,
            "index_updated": False,
        }
    for path in stale_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered[path], encoding="utf-8")
    return {
        "status": "ok",
        "path": relative(TEXT_SOURCES_INDEX_PATH),
        "paths": [relative(path) for path in rendered],
        "stale_paths": [relative(path) for path in stale_paths],
        "text_bodies_indexed": rendered[TEXT_SOURCES_INDEX_PATH].count("\n| `"),
        "era_sources_indexed": {era: len(primary_era_sources(registry, era)) for era in ERA_IDS},
        "would_update": would_update,
        "index_updated": would_update,
    }


def locate_command(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    failures = validate_registry(registry)
    if failures:
        raise LibraryError("; ".join(failures))
    source = find_source(registry, args.source_id)
    path = resolve_text_location(source.get("text_location"))
    exists = bool(path and path.is_file())
    text_bodies = []
    for body in all_text_bodies(source):
        body_path = resolve_text_location(body.get("text_location"))
        text_bodies.append(
            {
                "body": body,
                "text_exists": bool(body_path and body_path.is_file()),
                "resolved_text_path": str(body_path) if body_path else "",
            }
        )
    return {
        "status": "ok",
        "source_id": args.source_id,
        "source": source,
        "text_exists": exists,
        "resolved_text_path": str(path) if path else "",
        "text_bodies": text_bodies,
    }


def verify_body_text(source_id: str, body: Mapping[str, Any]) -> list[str]:
    body_id = text(body.get("body_id")) or source_id
    status = text(body.get("status")) or text(body.get("text_status")) or "missing"
    if status in {"missing", "needs-review"}:
        return []
    failures: list[str] = []
    path = resolve_text_location(body.get("text_location"))
    if path is None:
        return [f"{body_id}: missing text_location"]
    if not path.is_file():
        return [f"{body_id}: text file does not exist: {path}"]
    data = path.read_bytes()
    expected_bytes = body.get("text_bytes")
    if isinstance(expected_bytes, int) and len(data) != expected_bytes:
        failures.append(f"{body_id}: text byte count mismatch")
    expected_hash = text(body.get("text_sha256"))
    actual_hash = hashlib.sha256(data).hexdigest()
    if expected_hash and actual_hash != expected_hash:
        failures.append(f"{body_id}: text sha256 mismatch")
    encoding = text(body.get("text_encoding"))
    if encoding:
        try:
            decoded = data.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            failures.append(f"{body_id}: text is not readable as {encoding}")
        else:
            failures.extend(verify_text_body_hygiene(body_id, decoded))
    return failures


def verify_text_body_hygiene(body_id: str, decoded: str) -> list[str]:
    failures: list[str] = []
    for line_number, line in enumerate(decoded.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if any(pattern.search(stripped) for pattern in TEXT_CHROME_PATTERNS):
            failures.append(f"{body_id}: probable site chrome on line {line_number}: {stripped[:80]}")
            break
    return failures


def registry_text_body_rows(registry: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in registry.get("sources", []):
        if not isinstance(source, dict):
            continue
        era = text(source.get("subject_era")) or "unknown"
        source_id = text(source.get("source_id"))
        for body in all_text_bodies(source):
            body_id = text(body.get("body_id")) or source_id
            status = text(body.get("status")) or text(body.get("text_status")) or "missing"
            location = text(body.get("text_location"))
            path = resolve_text_location(location)
            rows.append(
                {
                    "era": era,
                    "source_id": source_id,
                    "body_id": body_id,
                    "status": status,
                    "text_location": location,
                    "resolved_text_path": str(path) if path else "",
                    "path": path,
                    "is_reference_body": status in {"available", "verified"},
                }
            )
    return rows


def empty_census_row(era: str) -> dict[str, Any]:
    return {
        "era": era,
        "authority_count": 0,
        "registry_represented_authorities": 0,
        "registry_body_count": 0,
        "referenced_body_count": 0,
        "physical_payload_count": 0,
        "missing_payload_count": 0,
        "representative_missing_body_ids": [],
    }


def census_texts_command(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    failures = validate_registry(registry)
    if failures:
        raise LibraryError("; ".join(failures))
    text_root = resolve_text_root()
    rows = registry_text_body_rows(registry)
    eras = list(ERA_IDS) + ["unknown"]
    by_era = {era: empty_census_row(era) for era in eras}
    represented: dict[str, set[str]] = {era: set() for era in eras}
    for source in registry.get("sources", []):
        if not isinstance(source, dict):
            continue
        era = text(source.get("subject_era")) or "unknown"
        by_era.setdefault(era, empty_census_row(era))
        represented.setdefault(era, set())
        by_era[era]["authority_count"] += 1
    for row in rows:
        era = row["era"]
        by_era.setdefault(era, empty_census_row(era))
        represented.setdefault(era, set())
        by_era[era]["registry_body_count"] += 1
        represented[era].add(row["source_id"])
        if row["is_reference_body"]:
            by_era[era]["referenced_body_count"] += 1
            path = row["path"]
            if path and path.is_file():
                by_era[era]["physical_payload_count"] += 1
            else:
                by_era[era]["missing_payload_count"] += 1
                missing = by_era[era]["representative_missing_body_ids"]
                if len(missing) < args.limit:
                    missing.append(row["body_id"])
    eras_output = []
    totals = empty_census_row("all")
    for era in ERA_IDS:
        item = by_era[era]
        item["registry_represented_authorities"] = len(represented.get(era, set()))
        eras_output.append(item)
        for key in (
            "authority_count",
            "registry_represented_authorities",
            "registry_body_count",
            "referenced_body_count",
            "physical_payload_count",
            "missing_payload_count",
        ):
            totals[key] += item[key]
        for missing in item["representative_missing_body_ids"]:
            if len(totals["representative_missing_body_ids"]) < args.limit:
                totals["representative_missing_body_ids"].append(missing)
    status = "passed" if totals["missing_payload_count"] == 0 else "failed"
    result = {
        "status": status,
        "resolved_private_text_root": str(text_root.resolve()),
        "private_text_root_exists": text_root.exists(),
        "library_wide": totals,
        "eras": eras_output,
    }
    if args.era:
        result["eras"] = [item for item in eras_output if item["era"] == args.era]
    return result


def verify_texts_command(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry()
    failures = validate_registry(registry)
    if failures:
        raise LibraryError("; ".join(failures))
    text_failures: list[str] = []
    checked = 0
    missing = 0
    for source in registry.get("sources", []):
        if not isinstance(source, dict):
            continue
        bodies = all_text_bodies(source)
        if not bodies:
            missing += 1
            continue
        for body in bodies:
            status = text(body.get("status")) or text(body.get("text_status"))
            if status in {"available", "verified"}:
                checked += 1
            text_failures.extend(verify_body_text(text(source.get("source_id")), body))
        if not any((text(body.get("status")) or text(body.get("text_status"))) in {"available", "verified"} for body in bodies):
            missing += 1
    return {
        "status": "passed" if not text_failures else "failed",
        "checked": checked,
        "missing": missing,
        "failures": text_failures,
    }


def admit_text_command(args: argparse.Namespace) -> dict[str, Any]:
    source_path = Path(args.file).expanduser().resolve()
    if not source_path.is_file():
        raise LibraryError(f"text file does not exist: {source_path}")
    if source_path.suffix.lower() not in TEXT_EXTENSIONS:
        raise LibraryError(f"unsupported text extension: {source_path.suffix}")
    if args.license_status not in LICENSE_STATUSES:
        raise LibraryError(f"invalid license_status: {args.license_status}")
    if args.license_status in {"unknown", "restricted"}:
        raise LibraryError(f"cannot admit text with license_status: {args.license_status}")
    text_root = resolve_text_root()
    resolved_text_root = text_root.resolve()
    if not private_text_root_allowed(resolved_text_root):
        raise LibraryError(f"library text root must remain outside Git: {resolved_text_root}")
    if not args.check:
        resolved_text_root = ensure_private_text_root(text_root)
    registry = load_registry()
    failures = validate_registry(registry)
    if failures:
        raise LibraryError("; ".join(failures))
    source = find_source(registry, args.source_id)
    work_title = args.work_title or text(source.get("title"))
    body_id = args.body_id or derive_body_id(args.source_id, work_title, args.translator or "", args.edition)
    target = text_body_path(body_id, source_path, resolved_text_root) if (args.body_id or args.work_title or source_text_bodies(source)) else text_record_path(args.source_id, source_path, resolved_text_root)
    data = source_path.read_bytes()
    try:
        data.decode(args.encoding)
    except (LookupError, UnicodeDecodeError) as error:
        raise LibraryError(f"text is not readable as {args.encoding}") from error
    dry_run = {
        "status": "ok",
        "source_id": args.source_id,
        "body_id": body_id,
        "work_title": work_title,
        "would_copy": source_path != target,
        "target_path": str(target),
        "text_location": text_uri(target, resolved_text_root),
        "text_sha256": hashlib.sha256(data).hexdigest(),
        "text_bytes": len(data),
        "text_encoding": args.encoding,
        "license_status": args.license_status,
        "body_imported_to_archive": False,
        "registry_updated": False,
    }
    if args.check:
        return dry_run
    existing_bodies = source_text_bodies(source)
    if existing_bodies or args.body_id or args.work_title:
        if any(text(body.get("body_id")) == body_id for body in existing_bodies) and not args.replace_body:
            raise LibraryError(f"text body already exists, pass --replace-body to replace: {body_id}")
        source.setdefault("text_bodies", [])
        source["text_bodies"] = [body for body in source["text_bodies"] if text(body.get("body_id")) != body_id]
        if source.get("text_status") == "missing":
            source["text_status"] = "available"
    else:
        if text(source.get("text_status")) in {"available", "verified"} and not args.replace_body:
            raise LibraryError(f"text body already exists, pass --replace-body to replace: {args.source_id}")
    if source_path != target:
        shutil.copyfile(source_path, target)
    data = target.read_bytes()
    body_record = {
        "body_id": body_id,
        "work_title": work_title,
        "text_location": text_uri(target, text_root),
        "text_sha256": hashlib.sha256(data).hexdigest(),
        "text_bytes": len(data),
        "text_encoding": args.encoding,
        "language": args.language or "",
        "translator": args.translator or "",
        "editor": args.editor or "",
        "edition_label": args.edition,
        "license_status": args.license_status,
        "license_notes": args.license_notes or "",
        "coverage_status": args.coverage_status,
        "coverage_notes": args.coverage_notes or "",
        "status": "available",
    }
    if existing_bodies or args.body_id or args.work_title:
        source["text_bodies"].append(body_record)
    else:
        source.update(
        {
            "text_status": "available",
            "text_location": body_record["text_location"],
            "text_sha256": body_record["text_sha256"],
            "text_bytes": body_record["text_bytes"],
            "text_encoding": args.encoding,
            "edition_label": args.edition,
            "license_status": args.license_status,
            "license_notes": args.license_notes or "",
        }
        )
        if args.language:
            source["language"] = args.language
        if args.translator:
            source["translator"] = args.translator
        if args.editor:
            source["editor"] = args.editor
    save_registry(registry)
    return {
        "status": "ok",
        "source_id": args.source_id,
        "body_id": body_id,
        "text_location": body_record["text_location"],
        "text_sha256": body_record["text_sha256"],
        "text_bytes": body_record["text_bytes"],
        "body_imported_to_archive": False,
        "registry_updated": True,
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Read-only Mira Library registry tools")
    sub = root.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(handler=validate_command)
    listing = sub.add_parser("list")
    listing.add_argument("--era", choices=ERA_IDS)
    listing.add_argument("--json", action="store_true")
    listing.set_defaults(handler=list_command)
    search = sub.add_parser("search")
    search.add_argument("--query", default="")
    search.add_argument("--era", choices=ERA_IDS)
    search.add_argument("--civilization")
    search.add_argument("--type", choices=sorted(SOURCE_TYPES))
    search.add_argument("--json", action="store_true")
    search.set_defaults(handler=search_command)
    audit = sub.add_parser("audit")
    audit.add_argument("--era", choices=ERA_IDS)
    audit.add_argument("--format", choices=("json", "markdown"), default="json")
    audit.add_argument("--json", action="store_true")
    audit.set_defaults(handler=audit_command)
    render_index = sub.add_parser("render-index")
    render_index.add_argument("--check", action="store_true")
    render_index.add_argument("--json", action="store_true")
    render_index.set_defaults(handler=render_index_command)
    locate = sub.add_parser("locate")
    locate.add_argument("source_id")
    locate.add_argument("--json", action="store_true")
    locate.set_defaults(handler=locate_command)
    verify_texts = sub.add_parser("verify-texts")
    verify_texts.add_argument("--json", action="store_true")
    verify_texts.set_defaults(handler=verify_texts_command)
    census_texts = sub.add_parser("census-texts")
    census_texts.add_argument("--era", choices=ERA_IDS)
    census_texts.add_argument("--limit", type=int, default=10)
    census_texts.add_argument("--json", action="store_true")
    census_texts.set_defaults(handler=census_texts_command)
    admit = sub.add_parser("admit-text")
    admit.add_argument("--source-id", required=True)
    admit.add_argument("--file", required=True)
    admit.add_argument("--body-id")
    admit.add_argument("--work-title")
    admit.add_argument("--edition", required=True)
    admit.add_argument("--license-status", required=True, choices=sorted(LICENSE_STATUSES))
    admit.add_argument("--license-notes", default="")
    admit.add_argument("--coverage-status", default="unknown", choices=sorted(BODY_COVERAGE_STATUSES))
    admit.add_argument("--coverage-notes", default="")
    admit.add_argument("--encoding", default="utf-8")
    admit.add_argument("--language")
    admit.add_argument("--translator")
    admit.add_argument("--editor")
    admit.add_argument("--replace-body", action="store_true")
    admit.add_argument("--check", action="store_true")
    admit.add_argument("--json", action="store_true")
    admit.set_defaults(handler=admit_text_command)
    return root


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    try:
        result = args.handler(args)
    except LibraryError as error:
        print(f"library error: {error}", file=sys.stderr)
        return 1
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    elif getattr(args, "format", None) == "markdown" and "markdown" in result:
        print(result["markdown"], end="")
    else:
        print(f"library_status={result.get('status', 'unknown')}")
        for key, value in result.items():
            if key != "status":
                print(f"{key}={json.dumps(value, ensure_ascii=True, sort_keys=True)}")
    return 0 if result.get("status") != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

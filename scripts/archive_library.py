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


REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_ROOT = REPO_ROOT / "archive" / "library"
REGISTRY_PATH = LIBRARY_ROOT / "library-registry.json"
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
    return Path(configured).expanduser() if configured else REPO_ROOT / ".mira-private" / "library" / "texts"


def ensure_private_text_root(root: Path) -> Path:
    resolved = root.resolve()
    if not private_text_root_allowed(resolved):
        raise LibraryError(f"library text root must be inside .mira-private or C:/private: {resolved}")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def private_text_root_allowed(root: Path) -> bool:
    resolved = root.resolve()
    repo_private = (REPO_ROOT / ".mira-private").resolve()
    allowed_roots = [repo_private]
    private_root = Path("C:/private")
    if private_root.exists():
        allowed_roots.append(private_root.resolve())
    return any(resolved == allowed or allowed in resolved.parents for allowed in allowed_roots)


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


def validate_scaffold(repo_root: Path = REPO_ROOT) -> list[str]:
    failures: list[str] = []
    root = repo_root / "archive" / "library"
    required = [root / "README.md", root / "library-registry.json"]
    required.extend(root / era / "index.md" for era in ERA_IDS)
    failures.extend(f"missing library scaffold file: {relative(path)}" for path in required if not path.is_file())
    if failures:
        return failures
    try:
        registry = load_registry(root / "library-registry.json")
    except LibraryError as error:
        return [str(error)]
    failures.extend(validate_registry(registry))
    for era in ERA_IDS:
        index = root / era / "index.md"
        content = index.read_text(encoding="utf-8")
        if f"Era: `{era}`" not in content:
            failures.append(f"library index missing era marker: {relative(index)}")
        if "No sources admitted yet." not in content and not registry.get("sources"):
            failures.append(f"empty library index missing scaffold notice: {relative(index)}")
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
        raise LibraryError(f"library text root must be inside .mira-private or C:/private: {resolved_text_root}")
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
    locate = sub.add_parser("locate")
    locate.add_argument("source_id")
    locate.add_argument("--json", action="store_true")
    locate.set_defaults(handler=locate_command)
    verify_texts = sub.add_parser("verify-texts")
    verify_texts.add_argument("--json", action="store_true")
    verify_texts.set_defaults(handler=verify_texts_command)
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
    else:
        print(f"library_status={result.get('status', 'unknown')}")
        for key, value in result.items():
            if key != "status":
                print(f"{key}={json.dumps(value, ensure_ascii=True, sort_keys=True)}")
    return 0 if result.get("status") != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

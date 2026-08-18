from __future__ import annotations

import argparse
import json
import re
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


def relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def text(value: Any) -> str:
    return str(value or "").strip()


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
    for key in ("source_id", "title", "author", "date_label", "source_type", "status", "notes"):
        parts.append(text(source.get(key)))
    for key in ("civilization_tags", "secondary_eras"):
        value = source.get(key, [])
        if isinstance(value, list):
            parts.extend(text(item) for item in value)
    location = source.get("location")
    if isinstance(location, str):
        parts.append(location)
    elif isinstance(location, dict):
        parts.extend(text(value) for value in location.values())
    return " ".join(part for part in parts if part).casefold()


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

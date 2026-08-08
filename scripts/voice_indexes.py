from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import voice_metadata


REPO_ROOT = voice_metadata.REPO_ROOT
NG_ROOT = voice_metadata.NG_ROOT
VOICES_ROOT = NG_ROOT / "voices"
ROLE_OVERRIDES_NAME = "role-overrides.json"
STANDARD_HEADER = "| Date | Source | Role | Host slug | Archive link |"
STANDARD_ROW_RE = re.compile(
    r"^\| `(?P<date>[^`]+)` \| (?P<title>.*?) \| `(?P<role>[^`]*)` \| `(?P<host>[^`]*)` \| \[source\]\((?P<link>[^)]+)\) \|$"
)
PAPE_ROW_RE = re.compile(
    r"^- \[(?P<date>\d{4}-\d{2}-\d{2}) — (?P<title>.*?)\]\((?P<link>[^)]+)\) — \*\*(?P<role>authored|guest)\*\* · (?P<modality>[^·\r\n]+?)(?: · host: `(?P<host>[^`]+)`)?$"
)
COUNT_RE = re.compile(r"^Corpus: .*?$", re.MULTILINE)
JUDGMENT_LEDGER_NAVIGATION = (
    "Canonical external-voice reading surface: "
    "[judgment-ledger.md](judgment-ledger.md). It records governed expressed "
    "judgments and separately canonical self-revisions without establishing factual truth."
)


def load_manifest(path: Path = voice_metadata.MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_role_overrides(path: Path) -> dict[tuple[str, str], str]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if payload.get("schema_version") != 1:
        raise ValueError(f"unsupported voice-role override schema: {path}")
    result: dict[tuple[str, str], str] = {}
    for item in payload.get("overrides", []):
        key = (str(item.get("voice_slug", "")), str(item.get("local_path", "")))
        role = str(item.get("role", "")).strip()
        if not all(key) or not role:
            raise ValueError(f"incomplete voice-role override: {item}")
        if key in result:
            raise ValueError(f"duplicate voice-role override: {key[0]} {key[1]}")
        result[key] = role
    return result


def role_override_failures(
    manifest: dict[str, Any], overrides: dict[tuple[str, str], str]
) -> list[str]:
    rows = {row.get("local_path"): row for row in manifest.get("sources", [])}
    failures: list[str] = []
    for (slug, local_path), role in overrides.items():
        row = rows.get(local_path)
        if row is None:
            failures.append(f"voice-role override path absent from manifest: {local_path}")
        elif slug not in (row.get("voice_slugs") or []):
            failures.append(f"voice-role override voice absent from manifest row: {slug} {local_path}")
        if not role.strip():
            failures.append(f"empty voice-role override: {slug} {local_path}")
    return failures


def route_path(index_path: Path, link: str, repo_root: Path = REPO_ROOT) -> str:
    resolved = (index_path.parent / link).resolve()
    return resolved.relative_to(repo_root.resolve()).as_posix()


def archive_link(local_path: str) -> str:
    rel = local_path.split("narrative-geopolitics/", 1)[-1]
    return "../../" + rel


def shelves(voices_root: Path = VOICES_ROOT) -> dict[str, Path]:
    return {
        path.parent.name: path
        for path in voices_root.glob("*/source-index.md")
        if path.is_file()
    }


def rows_by_voice(manifest: dict[str, Any], run_date: str | None = None, voices_root: Path = VOICES_ROOT) -> tuple[dict[str, list[dict[str, Any]]], set[str]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unindexed: set[str] = set()
    available = shelves(voices_root)
    for row in manifest.get("sources", []):
        if run_date and row.get("date") != run_date:
            continue
        for slug in row.get("voice_slugs") or []:
            if slug in voice_metadata.VOICE_ALIASES:
                continue
            if slug in available:
                result[slug].append(row)
            else:
                unindexed.add(slug)
    return result, unindexed


def all_manifest_rows_for_voice(manifest: dict[str, Any], slug: str) -> list[dict[str, Any]]:
    rows = [row for row in manifest.get("sources", []) if slug in (row.get("voice_slugs") or [])]
    rows.sort(key=lambda row: (row.get("date", ""), row.get("local_path", "")))
    return rows


def derive_role(row: dict[str, Any], voice_slug: str) -> str:
    source_class = str(row.get("source_class", "")).lower()
    modality = str(row.get("modality", "")).lower()
    host = str(row.get("host_slug", ""))
    if source_class.startswith("authored") or (
        modality in {"newsletter", "substack-post", "x-post-text", "essay", "article"}
        and voice_metadata.canonical_slug(host) == voice_slug
    ):
        return "authored"
    if host and voice_metadata.canonical_slug(host) != voice_slug:
        return "host-pressure test"
    return "provisional-route"


def parse_standard(index_path: Path, text: str, repo_root: Path = REPO_ROOT) -> tuple[dict[str, dict[str, str]], list[str], tuple[int, int] | None]:
    lines = text.splitlines()
    try:
        header_index = lines.index(STANDARD_HEADER)
    except ValueError:
        return {}, [], None
    start = header_index + 2
    end = start
    parsed: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []
    while end < len(lines) and lines[end].startswith("|"):
        match = STANDARD_ROW_RE.match(lines[end])
        if not match:
            break
        item = match.groupdict()
        local_path = route_path(index_path, item["link"], repo_root)
        item["line"] = lines[end]
        if local_path in parsed:
            duplicates.append(local_path)
        else:
            parsed[local_path] = item
        end += 1
    return parsed, duplicates, (start, end)


def standard_count(text: str) -> int | None:
    match = re.search(r"^Corpus: (\d+) local route rows across (\d+) central archive source files\.$", text, re.MULTILINE)
    return int(match.group(1)) if match and match.group(1) == match.group(2) else None


def collapse_secondary_route_tables(text: str) -> str:
    lines = text.splitlines()
    headers = [index for index, line in enumerate(lines) if line == STANDARD_HEADER]
    for header in reversed(headers[1:]):
        start = header
        if start > 0 and lines[start - 1] == "":
            start -= 1
        end = header + 2
        while end < len(lines) and lines[end].startswith("|"):
            end += 1
        replacement = ["", "Routes are consolidated in the Imported Route Map above."]
        lines[start:end] = replacement
    return "\n".join(lines) + ("\n" if text.endswith(("\n", "\r\n")) else "")


def render_standard(
    index_path: Path,
    text: str,
    manifest_rows: list[dict[str, Any]],
    repo_root: Path = REPO_ROOT,
    role_overrides: dict[tuple[str, str], str] | None = None,
) -> tuple[str, dict[str, Any]]:
    role_overrides = role_overrides or {}
    existing, duplicates, bounds = parse_standard(index_path, text, repo_root)
    if bounds is None:
        return text, {"failures": [f"unsupported voice index format: {index_path.relative_to(repo_root).as_posix()}"]}
    manifest_paths = {row["local_path"] for row in manifest_rows}
    orphan = sorted(set(existing) - manifest_paths)
    failures = [*(f"duplicate voice route: {path}" for path in duplicates), *(f"voice route absent from manifest: {path}" for path in orphan)]
    rendered: list[str] = []
    added: list[str] = []
    for row in manifest_rows:
        local_path = row["local_path"]
        old = existing.get(local_path)
        role = role_overrides.get(
            (index_path.parent.name, local_path), derive_role(row, index_path.parent.name)
        )
        host = row.get("host_slug") or "none"
        title = str(row.get("title", "")).replace("|", "\\|")
        rendered.append(f"| `{row.get('date', '')}` | {title} | `{role}` | `{host}` | [source]({archive_link(local_path)}) |")
        if not old:
            added.append(local_path)
    lines = text.splitlines()
    start, end = bounds
    lines[start:end] = rendered
    updated = "\n".join(lines) + ("\n" if text.endswith(("\n", "\r\n")) else "")
    count_line = f"Corpus: {len(manifest_rows)} local route rows across {len(manifest_rows)} central archive source files."
    updated = COUNT_RE.sub(count_line, updated, count=1)
    updated = collapse_secondary_route_tables(updated)
    if standard_count(text) != len(manifest_rows):
        failures.append(f"stale voice corpus count: {index_path.parent.name}")
    missing = sorted(manifest_paths - set(existing))
    failures.extend(f"manifest route missing voice shelf: {path}" for path in missing)
    return updated, {"failures": failures, "added": added, "missing": missing, "duplicates": duplicates, "orphan": orphan}


def parse_pape(index_path: Path, text: str, repo_root: Path = REPO_ROOT) -> tuple[dict[str, dict[str, str]], list[str]]:
    parsed: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []
    for line in text.splitlines():
        match = PAPE_ROW_RE.match(line)
        if not match:
            continue
        item = match.groupdict()
        local_path = route_path(index_path, item["link"], repo_root)
        item["line"] = line
        if local_path in parsed:
            duplicates.append(local_path)
        else:
            parsed[local_path] = item
    return parsed, duplicates


def render_pape(
    index_path: Path,
    text: str,
    manifest_rows: list[dict[str, Any]],
    repo_root: Path = REPO_ROOT,
    role_overrides: dict[tuple[str, str], str] | None = None,
) -> tuple[str, dict[str, Any]]:
    role_overrides = role_overrides or {}
    existing, duplicates = parse_pape(index_path, text, repo_root)
    manifest_paths = {row["local_path"] for row in manifest_rows}
    orphan = sorted(set(existing) - manifest_paths)
    missing = sorted(manifest_paths - set(existing))
    failures = [*(f"duplicate voice route: {path}" for path in duplicates), *(f"voice route absent from manifest: {path}" for path in orphan), *(f"manifest route missing voice shelf: {path}" for path in missing)]
    by_month: dict[str, list[str]] = defaultdict(list)
    authored = 0
    guest = 0
    for row in manifest_rows:
        local_path = row["local_path"]
        role = role_overrides.get(
            ("pape", local_path),
            "authored" if derive_role(row, "pape") == "authored" else "guest",
        )
        host = row.get("host_slug") or ""
        host_suffix = f" · host: `{host}`" if role == "guest" and host else ""
        line = f"- [{row['date']} — {row.get('title', '')}]({archive_link(local_path)}) — **{role}** · {row.get('modality', '')}{host_suffix}"
        authored += role == "authored"
        guest += role == "guest"
        by_month[row["date"][:7]].append(line)
    month_matches = list(re.finditer(r"^## \d{4}-\d{2}\r?$", text, re.MULTILINE))
    if not month_matches:
        return text, {"failures": failures + ["unsupported Pape index format"], "added": []}
    prefix = text[: month_matches[0].start()].rstrip() + "\n\n"
    blocks = []
    for month in sorted(by_month):
        blocks.append(f"## {month}\n\n" + "\n".join(sorted(by_month[month])))
    updated = (
        prefix
        + "\n\n".join(blocks)
        + "\n\n"
        + JUDGMENT_LEDGER_NAVIGATION
        + "\n"
    )
    updated = COUNT_RE.sub(f"Corpus: {authored} authored sources, {guest} guest appearances, {authored + guest} total imported sources.", updated, count=1)
    return updated, {"failures": failures, "added": missing, "missing": missing, "duplicates": duplicates, "orphan": orphan}


def project(
    manifest: dict[str, Any],
    run_date: str | None = None,
    repo_root: Path = REPO_ROOT,
    voices_root: Path = VOICES_ROOT,
    role_overrides: dict[tuple[str, str], str] | None = None,
) -> tuple[dict[Path, str], dict[str, Any]]:
    failures = voice_metadata.metadata_failures(manifest, repo_root=repo_root, run_date=run_date)
    if role_overrides is None:
        try:
            role_overrides = load_role_overrides(voices_root / ROLE_OVERRIDES_NAME)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            role_overrides = {}
            failures.append(str(exc))
    failures.extend(role_override_failures(manifest, role_overrides))
    targeted, unindexed = rows_by_voice(manifest, run_date, voices_root)
    changed: list[str] = []
    added: list[str] = []
    updates: dict[Path, str] = {}
    for slug in sorted(targeted):
        index_path = shelves(voices_root)[slug]
        text = index_path.read_text(encoding="utf-8")
        all_rows = all_manifest_rows_for_voice(manifest, slug)
        updated, report = (
            render_pape(index_path, text, all_rows, repo_root, role_overrides)
            if slug == "pape"
            else render_standard(index_path, text, all_rows, repo_root, role_overrides)
        )
        failures.extend(report.get("failures", []))
        added.extend(report.get("added", []))
        if updated != text:
            changed.append(slug)
            if not report.get("orphan"):
                updates[index_path] = updated
    return updates, {
        "changed_shelves": changed,
        "added_routes": sorted(set(added)),
        "unindexed_voices": sorted(unindexed),
        "failures": sorted(set(failures)),
    }


def reconcile(
    manifest: dict[str, Any],
    run_date: str | None = None,
    write: bool = False,
    repo_root: Path = REPO_ROOT,
    voices_root: Path = VOICES_ROOT,
    role_overrides: dict[tuple[str, str], str] | None = None,
) -> dict[str, Any]:
    updates, report = project(
        manifest,
        run_date=run_date,
        repo_root=repo_root,
        voices_root=voices_root,
        role_overrides=role_overrides,
    )
    failures = list(report["failures"])
    if write:
        for index_path, updated in updates.items():
            index_path.write_text(updated, encoding="utf-8", newline="\n")
    if write:
        # Missing routes and stale counts are repaired by the write; structural failures remain.
        failures = [item for item in failures if not item.startswith(("manifest route missing voice shelf:", "stale voice corpus count:", "duplicate voice route:"))]
    else:
        failures.extend(
            f"voice index drift: {slug}" for slug in report["changed_shelves"]
        )
    return {
        **report,
        "failures": sorted(set(failures)),
    }

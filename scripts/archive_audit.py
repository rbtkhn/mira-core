from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_ROOT = REPO_ROOT / "narrative-geopolitics" / "archive"
SOURCES_ROOT = ARCHIVE_ROOT / "sources"
MANIFEST_PATH = ARCHIVE_ROOT / "source-manifest.json"
DATE_IN_PATH = re.compile(r"(?:^|/)(\d{4}-\d{2}-\d{2})(?:/|$)")
SECTION_HEADING = re.compile(r"(?m)^### ")


class ArchiveAuditError(ValueError):
    pass


@dataclass(frozen=True)
class AuditScope:
    mode: str
    requested_start: date
    requested_end: date
    effective_start: date
    effective_end: date
    voice_slugs: tuple[str, ...]
    host_slugs: tuple[str, ...]

    def public(self, *, empty: bool) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "requested_start": self.requested_start.isoformat(),
            "requested_end": self.requested_end.isoformat(),
            "effective_start": self.effective_start.isoformat(),
            "effective_end": self.effective_end.isoformat(),
            "voice_slugs": list(self.voice_slugs),
            "host_slugs": list(self.host_slugs),
            "empty": empty,
        }


def month_end(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1) - timedelta(days=1)
    return date(value.year, value.month + 1, 1) - timedelta(days=1)


def month_values(start: date, end: date) -> list[str]:
    if end < start:
        return []
    cursor = date(start.year, start.month, 1)
    final = date(end.year, end.month, 1)
    values: list[str] = []
    while cursor <= final:
        values.append(cursor.strftime("%Y-%m"))
        cursor = date(cursor.year + (cursor.month == 12), 1 if cursor.month == 12 else cursor.month + 1, 1)
    return values


def density_class(source_count: int) -> str:
    if source_count <= 3:
        return "thin"
    if source_count >= 7:
        return "dense"
    return "normal"


def density_labels(
    density: str,
    source_count: int,
    hooks: int,
    opcs: int,
    stories: int,
    ratio: float,
) -> list[str]:
    labels: list[str] = []
    if density == "thin" and (hooks or opcs or stories):
        labels.append("thin-but-pivotal")
    if density == "dense":
        labels.append("dense-synthesis-check")
    if density == "thin" and ratio >= 1.0:
        labels.append("overclaim-risk")
    if density == "dense" and (hooks + opcs + stories) <= 2:
        labels.append("underuse-risk")
    if opcs:
        labels.append("verification-priority")
    return labels


def load_manifest_counts(path: Path = MANIFEST_PATH) -> dict[str, int]:
    _, rows = load_manifest(path)
    counts: Counter[str] = Counter()
    for row in rows:
        value = row_date(row)
        if value is not None:
            counts[value.isoformat()] += 1
    return dict(counts)


def load_manifest(path: Path = MANIFEST_PATH) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ArchiveAuditError("source manifest is not valid UTF-8 JSON") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("sources"), list):
        raise ArchiveAuditError("source manifest must be an object with a sources list")
    rows = payload["sources"]
    if any(not isinstance(row, dict) for row in rows):
        raise ArchiveAuditError("source manifest contains a non-object row")
    return payload, rows


def row_date(row: dict[str, Any]) -> date | None:
    raw = row.get("date")
    if not isinstance(raw, str):
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def manifest_as_of(rows: Iterable[dict[str, Any]]) -> date:
    dates = [value for row in rows if (value := row_date(row)) is not None]
    if not dates:
        raise ArchiveAuditError("source manifest contains no valid dates")
    return max(dates)


def resolve_scope(args: argparse.Namespace, rows: list[dict[str, Any]]) -> AuditScope:
    as_of = manifest_as_of(rows)
    valid_dates = sorted(value for row in rows if (value := row_date(row)) is not None)
    if args.month:
        try:
            requested_start = date.fromisoformat(f"{args.month}-01")
        except ValueError as error:
            raise ArchiveAuditError("--month must use YYYY-MM") from error
        requested_end = month_end(requested_start)
        mode = "month"
    elif args.whole_corpus:
        requested_start, requested_end = valid_dates[0], as_of
        mode = "whole-corpus"
    else:
        try:
            requested_start = date.fromisoformat(args.start_date)
            requested_end = date.fromisoformat(args.end_date)
        except ValueError as error:
            raise ArchiveAuditError("date ranges must use YYYY-MM-DD") from error
        if requested_end < requested_start:
            raise ArchiveAuditError("--end-date must be on or after --start-date")
        mode = "date-range"
    return AuditScope(
        mode=mode,
        requested_start=requested_start,
        requested_end=requested_end,
        effective_start=requested_start,
        effective_end=min(requested_end, as_of),
        voice_slugs=tuple(sorted(set(args.voice_slug or ()))),
        host_slugs=tuple(sorted(set(args.host_slug or ()))),
    )


def row_matches(row: dict[str, Any], scope: AuditScope) -> bool:
    value = row_date(row)
    if value is None or value < scope.effective_start or value > scope.effective_end:
        return False
    voices = row.get("voice_slugs")
    normalized_voices = set(voices) if isinstance(voices, list) else set()
    if scope.voice_slugs and not normalized_voices.intersection(scope.voice_slugs):
        return False
    host = row.get("host_slug")
    if scope.host_slugs and host not in scope.host_slugs:
        return False
    return True


def scalar(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {'"', "'"}:
        return stripped[1:-1]
    return stripped


def source_metadata(path: Path) -> tuple[dict[str, str], str] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return None
    frontmatter, body = text[4:].split("\n---\n", 1)
    metadata: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = scalar(value)
    source_form = metadata.get("source_form", "").casefold()
    kind = metadata.get("kind", "").casefold()
    authored_body = (
        source_form in {"newsletter", "substack-post", "x-post-text", "essay", "article"}
        or kind in {"source-text", "newsletter", "substack-post", "x-post-text", "essay", "article"}
    )
    if "## Transcript" not in body and not (authored_body and "## Source Text" in body):
        return None
    return metadata, body


def finding(rule_id: str, severity: str, path: str, detail: str) -> dict[str, str]:
    return {"rule_id": rule_id, "severity": severity, "path": path, "detail": detail}


def _duplicates(values: Iterable[tuple[str, str]]) -> list[tuple[str, list[str]]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for value, path in values:
        if value:
            grouped[value.casefold()].add(path)
    return [(value, sorted(paths)) for value, paths in grouped.items() if len(paths) > 1]


def audit_findings(
    manifest: dict[str, Any],
    all_rows: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    scope: AuditScope,
    *,
    repo_root: Path = REPO_ROOT,
    sources_root: Path = SOURCES_ROOT,
    manifest_path: Path = MANIFEST_PATH,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    manifest_label = manifest_path.resolve().relative_to(repo_root.resolve()).as_posix()
    if manifest.get("source_count") != len(all_rows):
        findings.append(finding("manifest.count_mismatch", "error", manifest_label, "declared source_count differs from row count"))

    path_pairs: list[tuple[str, str]] = []
    url_pairs: list[tuple[str, str]] = []
    selected_paths: set[str] = set()
    for row in rows:
        raw_path = row.get("local_path")
        label = raw_path if isinstance(raw_path, str) and raw_path else manifest_label
        if isinstance(raw_path, str) and raw_path:
            normalized = raw_path.replace("\\", "/")
            selected_paths.add(normalized)
            path_pairs.append((normalized, normalized))
        source_url = row.get("source_url")
        if isinstance(source_url, str) and source_url:
            url_pairs.append((source_url, label))

    path_counts = Counter(value.casefold() for value, _ in path_pairs)
    for value, path in path_pairs:
        if path_counts[value.casefold()] > 1:
            findings.append(finding("manifest.duplicate_path", "error", path, "local_path appears more than once in scope"))
    for _, paths in _duplicates(url_pairs):
        for path in paths:
            findings.append(finding("manifest.duplicate_url", "error", path, "source_url appears more than once in scope"))

    for row in rows:
        raw_path = row.get("local_path")
        if not isinstance(raw_path, str) or not raw_path:
            findings.append(finding("manifest.path_missing", "error", manifest_label, "manifest row has no local_path"))
            continue
        normalized = raw_path.replace("\\", "/")
        resolved = (repo_root / normalized).resolve()
        try:
            resolved.relative_to(sources_root.resolve())
        except ValueError:
            findings.append(finding("manifest.path_escape", "error", normalized, "local_path escapes archive/sources"))
            continue
        match = DATE_IN_PATH.search(normalized)
        declared_date = row.get("date")
        if not match or match.group(1) != declared_date:
            findings.append(finding("manifest.date_path_mismatch", "error", normalized, "manifest date and archive directory disagree"))
        if not resolved.is_file():
            findings.append(finding("manifest.file_missing", "error", normalized, "manifest path has no source file"))
            continue
        voices = row.get("voice_slugs")
        if not isinstance(voices, list) or not any(isinstance(value, str) and value for value in voices):
            findings.append(finding("routing.voice_missing", "warning", normalized, "manifest row has no voice route"))
        if not isinstance(row.get("host_slug"), str) or not row.get("host_slug"):
            findings.append(finding("routing.host_missing", "warning", normalized, "manifest row has no host route"))

        parsed = source_metadata(resolved)
        if parsed is None:
            findings.append(finding("source.malformed", "error", normalized, "source lacks valid frontmatter or transcript body"))
            continue
        metadata, body = parsed
        if metadata.get("routing_state") == "provisional":
            findings.append(
                finding(
                    "routing.provisional",
                    "warning",
                    normalized,
                    "source retains landing-time provisional routing; this is not by itself an unresolved routing defect",
                )
            )
        if (
            row.get("host_slug") == "the-duran"
            and scalar(str(metadata.get("thread", ""))).casefold() == "mercouris"
            and metadata.get("routing_state") == "provisional"
            and (not metadata.get("channel_name") or not metadata.get("host"))
        ):
            findings.append(
                finding(
                    "routing.duran_mercouris_metadata_weak",
                    "warning",
                    normalized,
                    "The Duran/Mercouris provisional route has weak frontmatter; expected channel_name and host metadata from local transcript or channel evidence",
                )
            )
        if metadata.get("pub_date") and metadata.get("pub_date") != declared_date:
            findings.append(finding("source.pub_date_mismatch", "error", normalized, "source pub_date differs from manifest date"))
        heading_count = len(SECTION_HEADING.findall(body))
        raw_count = metadata.get("section_count")
        try:
            declared_count = int(raw_count) if raw_count is not None else heading_count
        except ValueError:
            declared_count = -1
        curation = metadata.get("transcript_curation", "")
        if declared_count != heading_count or (curation == "curated_sectioned") != (heading_count > 0):
            findings.append(finding("repair.section_metadata_mismatch", "warning", normalized, "section metadata disagrees with transcript headings"))
        if metadata.get("asr_repair_applied") == "true" and not metadata.get("asr_repair_pass"):
            findings.append(finding("repair.asr_metadata_incomplete", "warning", normalized, "ASR repair is marked applied without a pass identifier"))
        source_url = metadata.get("source_url", "")
        if source_url:
            url_pairs.append((source_url, normalized))

    for path in iter_scoped_source_files(sources_root, scope):
        relative = path.resolve().relative_to(repo_root.resolve()).as_posix()
        if relative not in selected_paths:
            findings.append(finding("archive.orphan_file", "error", relative, "archive source has no matching manifest row"))

    source_url_duplicates = _duplicates(url_pairs)
    existing_url_paths = {(item["rule_id"], item["path"]) for item in findings}
    for _, paths in source_url_duplicates:
        for path in paths:
            key = ("manifest.duplicate_url", path)
            if key not in existing_url_paths:
                findings.append(finding("manifest.duplicate_url", "error", path, "source_url appears more than once in scope"))
                existing_url_paths.add(key)
    return sorted(findings, key=lambda item: (item["rule_id"], item["path"], item["detail"]))


def _iter_dates(start: date, end: date) -> Iterable[date]:
    cursor = start
    while cursor <= end:
        yield cursor
        cursor += timedelta(days=1)


def iter_scoped_source_files(
    sources_root: Path,
    scope: AuditScope,
) -> Iterable[Path]:
    if scope.voice_slugs or scope.host_slugs:
        return
    for value in _iter_dates(scope.effective_start, scope.effective_end):
        date_root = sources_root / value.isoformat()
        if date_root.is_dir():
            yield from sorted(date_root.rglob("*.md"))


def coverage(rows: list[dict[str, Any]], scope: AuditScope) -> tuple[dict[str, Any], list[dict[str, str]]]:
    warnings: list[dict[str, str]] = []
    dates = [value for row in rows if (value := row_date(row)) is not None]
    boundary_start = min(dates) if dates else scope.effective_start
    boundary_end = max(dates) if dates else scope.effective_end
    months = month_values(boundary_start, boundary_end)
    daily_counts = Counter(value.isoformat() for value in dates)
    monthly_counts = Counter(value.strftime("%Y-%m") for value in dates)
    voice_months: dict[str, set[str]] = defaultdict(set)
    host_months: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        value = row_date(row)
        if value is None:
            continue
        month = value.strftime("%Y-%m")
        voices = row.get("voice_slugs")
        if isinstance(voices, list):
            for voice in voices:
                if isinstance(voice, str) and voice:
                    voice_months[voice].add(month)
        host = row.get("host_slug")
        if isinstance(host, str) and host:
            host_months[host].add(month)
    missing_months = [month for month in months if monthly_counts[month] == 0]
    for month in missing_months:
        warnings.append(finding("coverage.month_missing", "warning", month, "no matching manifest rows"))
    voices = {
        voice: {"months_present": sorted(present), "months_missing": sorted(set(months) - present)}
        for voice, present in sorted(voice_months.items())
    }
    hosts = {
        host: {"months_present": sorted(present), "months_missing": sorted(set(months) - present)}
        for host, present in sorted(host_months.items())
    }
    density = [
        {"date": value.isoformat(), "source_count": daily_counts[value.isoformat()], "density_class": density_class(daily_counts[value.isoformat()])}
        for value in _iter_dates(scope.effective_start, scope.effective_end)
    ] if scope.effective_end >= scope.effective_start else []
    return (
        {
            "landed_boundary": {
                "start": boundary_start.isoformat(),
                "end": boundary_end.isoformat(),
            },
            "daily_counts": dict(sorted(daily_counts.items())),
            "monthly_counts": dict(sorted(monthly_counts.items())),
            "missing_months": missing_months,
            "voices": voices,
            "hosts": hosts,
            "density": density,
        },
        warnings,
    )


def build_audit(
    args: argparse.Namespace,
    *,
    repo_root: Path = REPO_ROOT,
    sources_root: Path = SOURCES_ROOT,
    manifest_path: Path = MANIFEST_PATH,
) -> dict[str, Any]:
    manifest, all_rows = load_manifest(manifest_path)
    as_of = manifest_as_of(all_rows)
    scope = resolve_scope(args, all_rows)
    rows = [row for row in all_rows if row_matches(row, scope)] if scope.effective_end >= scope.effective_start else []
    findings = audit_findings(
        manifest,
        all_rows,
        rows,
        scope,
        repo_root=repo_root,
        sources_root=sources_root,
        manifest_path=manifest_path,
    )
    coverage_payload, coverage_findings = coverage(rows, scope)
    findings.extend(coverage_findings)
    if not rows:
        findings.append(finding("scope.no_matches", "warning", "scope", "valid scope contains no matching manifest rows"))
    findings = sorted(findings, key=lambda item: (item["rule_id"], item["path"], item["detail"]))
    error_count = sum(item["severity"] == "error" for item in findings)
    warning_count = sum(item["severity"] == "warning" for item in findings)
    return {
        "schema_version": "1.0",
        "disposition": "fail" if error_count else "pass",
        "as_of": as_of.isoformat(),
        "scope": scope.public(empty=not rows),
        "summary": {
            "manifest_rows": len(all_rows),
            "scoped_rows": len(rows),
            "structural_failures": error_count,
            "warnings": warning_count,
        },
        "findings": findings,
        "coverage": coverage_payload,
        "authority_effect": "none",
        "capability_token": False,
        "notice": "Archive audit is read-only and grants no repair authority.",
    }


def render_markdown(payload: dict[str, Any]) -> str:
    scope = payload["scope"]
    lines = [
        "# Archive Audit",
        "",
        f"- Disposition: `{payload['disposition']}`",
        f"- As of: `{payload['as_of']}`",
        f"- Scope: `{scope['effective_start']}` through `{scope['effective_end']}`",
        f"- Scoped rows: `{payload['summary']['scoped_rows']}`",
        f"- Structural failures: `{payload['summary']['structural_failures']}`",
        f"- Warnings: `{payload['summary']['warnings']}`",
        "- Authority effect: `none`",
        "- Capability token: `false`",
        "",
        "> Archive audit is read-only and grants no repair authority.",
        "",
        "## Findings",
        "",
    ]
    if payload["findings"]:
        lines += ["| Rule | Severity | Path | Detail |", "| --- | --- | --- | --- |"]
        for item in payload["findings"]:
            detail = item["detail"].replace("|", "\\|")
            path = item["path"].replace("|", "\\|")
            lines.append(f"| `{item['rule_id']}` | `{item['severity']}` | `{path}` | {detail} |")
    else:
        lines.append("No findings.")
    lines += ["", "## Coverage", ""]
    coverage_payload = payload["coverage"]
    lines.append(f"- Landed boundary: `{coverage_payload['landed_boundary']['start']}` through `{coverage_payload['landed_boundary']['end']}`")
    lines.append(f"- Missing months: `{', '.join(coverage_payload['missing_months']) or 'none'}`")
    lines += ["", "| Date | Sources | Density |", "| --- | ---: | --- |"]
    for item in coverage_payload["density"]:
        lines.append(f"| `{item['date']}` | {item['source_count']} | `{item['density_class']}` |")
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit Narrative Geopolitics archive health, coverage, and density.")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--month")
    scope.add_argument("--whole-corpus", action="store_true")
    scope.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--voice-slug", action="append")
    parser.add_argument("--host-slug", action="append")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def parse_args(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(arguments)
    if bool(args.start_date) != bool(args.end_date):
        parser.error("--start-date and --end-date must be supplied together")
    if (args.month or args.whole_corpus) and args.end_date:
        parser.error("--end-date is valid only with --start-date")
    if args.month:
        try:
            date.fromisoformat(f"{args.month}-01")
        except ValueError:
            parser.error("--month must use YYYY-MM")
    if args.start_date:
        try:
            start = date.fromisoformat(args.start_date)
            end = date.fromisoformat(args.end_date)
        except ValueError:
            parser.error("date ranges must use YYYY-MM-DD")
        if end < start:
            parser.error("--end-date must be on or after --start-date")
    return args


def main(
    arguments: list[str] | None = None,
    *,
    repo_root: Path = REPO_ROOT,
    sources_root: Path = SOURCES_ROOT,
    manifest_path: Path = MANIFEST_PATH,
) -> int:
    args = parse_args(arguments)
    try:
        payload = build_audit(
            args,
            repo_root=repo_root,
            sources_root=sources_root,
            manifest_path=manifest_path,
        )
    except ArchiveAuditError as error:
        print(f"archive audit failed: {error}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(render_markdown(payload), end="")
    return 1 if payload["summary"]["structural_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

import land_best_intake


REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_SOURCES_ROOT = REPO_ROOT / "archive" / "sources" / "geopolitics" / "sources"
MANIFEST_PATH = REPO_ROOT / "archive" / "sources" / "geopolitics" / "source-manifest.json"
REPAIR_CLASSES = ("metadata", "asr", "sectioning", "wrapper-trim", "heading-only", "body-merge")
MAX_TARGETS = 100


class ArchiveRepairError(ValueError):
    pass


@dataclass(frozen=True)
class FileRepairPlan:
    path: str
    host_slug: str
    repair_class: str
    input_sha256: str
    output_sha256: str
    changed: bool
    operations: tuple[str, ...]
    changed_fields: tuple[str, ...]
    section_count_before: int
    section_count_after: int
    diff: str
    original_bytes: bytes
    proposed_bytes: bytes

    def public(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "host_slug": self.host_slug,
            "repair_class": self.repair_class,
            "input_sha256": self.input_sha256,
            "output_sha256": self.output_sha256,
            "changed": self.changed,
            "operations": list(self.operations),
            "changed_fields": list(self.changed_fields),
            "section_count_before": self.section_count_before,
            "section_count_after": self.section_count_after,
            "diff": self.diff,
        }


@dataclass(frozen=True)
class ArchiveRepairPlan:
    manifest_id: str
    manifest_sha256: str
    repair_class: str
    resection: bool
    files: tuple[FileRepairPlan, ...]
    plan_digest: str

    def public(self, *, disposition: str = "preview") -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "disposition": disposition,
            "repair_class": self.repair_class,
            "resection": self.resection,
            "manifest_id": self.manifest_id,
            "manifest_sha256": self.manifest_sha256,
            "target_count": len(self.files),
            "changed_count": sum(item.changed for item in self.files),
            "targets": [item.path for item in self.files],
            "files": [item.public() for item in self.files],
            "plan_digest": self.plan_digest,
            "authority_effect": "none",
            "capability_token": False,
            "notice": "This plan describes bounded archive repair and grants no authority.",
        }


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_manifest(manifest_path: Path = MANIFEST_PATH) -> tuple[dict[str, Any], str]:
    raw = manifest_path.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ArchiveRepairError("source manifest is not valid UTF-8 JSON") from error
    rows = payload.get("sources")
    if not isinstance(rows, list):
        raise ArchiveRepairError("source manifest has no sources list")
    if payload.get("source_count") != len(rows):
        raise ArchiveRepairError("source manifest declared count does not match its rows")
    return payload, sha256_bytes(raw)


def _reject_raw_path(raw: str, *, label: str) -> Path:
    if not raw or raw.strip() != raw:
        raise ArchiveRepairError(f"{label} must be a non-empty normalized path")
    if any(token in raw for token in ("*", "?", "[", "]")):
        raise ArchiveRepairError(f"{label} must not contain glob syntax: {raw}")
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ArchiveRepairError(f"{label} must be repository-relative without traversal: {raw}")
    return candidate


def resolve_list_file(raw: str, *, repo_root: Path = REPO_ROOT) -> Path:
    candidate = _reject_raw_path(raw, label="list file")
    resolved_root = repo_root.resolve()
    resolved = (resolved_root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ArchiveRepairError("list file must stay inside the repository") from error
    if not resolved.is_file():
        raise ArchiveRepairError(f"list file does not exist: {raw}")
    return resolved


def read_list_file(raw: str, *, repo_root: Path = REPO_ROOT) -> list[str]:
    path = resolve_list_file(raw, repo_root=repo_root)
    values = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not values:
        raise ArchiveRepairError("list file contains no target paths")
    return values


def resolve_targets(
    raw_paths: Iterable[str],
    *,
    repo_root: Path = REPO_ROOT,
    sources_root: Path = ARCHIVE_SOURCES_ROOT,
) -> tuple[tuple[str, Path], ...]:
    values = list(raw_paths)
    if not values:
        raise ArchiveRepairError("at least one archive source path is required")
    if len(values) > MAX_TARGETS:
        raise ArchiveRepairError(f"archive repair is bounded to {MAX_TARGETS} targets")
    resolved_repo = repo_root.resolve()
    resolved_sources = sources_root.resolve()
    found: dict[str, Path] = {}
    folded: set[str] = set()
    for raw in values:
        candidate = _reject_raw_path(raw, label="target path")
        resolved = (resolved_repo / candidate).resolve()
        try:
            resolved.relative_to(resolved_sources)
        except ValueError as error:
            raise ArchiveRepairError(f"target must stay under archive/sources: {raw}") from error
        if not resolved.is_file() or resolved.suffix.lower() != ".md":
            raise ArchiveRepairError(f"target must be an existing Markdown file: {raw}")
        relative = resolved.relative_to(resolved_repo).as_posix()
        key = relative.casefold()
        if key in folded:
            raise ArchiveRepairError(f"duplicate target path: {relative}")
        folded.add(key)
        found[relative] = resolved
    return tuple(sorted(found.items()))


def manifest_rows_by_path(manifest: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    rows: dict[str, list[dict[str, Any]]] = {}
    for raw in manifest.get("sources", []):
        if not isinstance(raw, dict):
            raise ArchiveRepairError("source manifest contains a non-object row")
        path = raw.get("local_path")
        if isinstance(path, str) and path:
            rows.setdefault(path.replace("\\", "/"), []).append(raw)
    return rows


def dirty_paths(paths: Iterable[str], *, repo_root: Path = REPO_ROOT) -> set[str]:
    values = list(paths)
    if not values:
        return set()
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--", *values],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ArchiveRepairError("could not inspect target Git state")
    found: set[str] = set()
    for line in result.stdout.splitlines():
        if len(line) >= 4:
            found.add(line[3:].strip().replace("\\", "/"))
    return found


def source_host(path: Path, frontmatter: dict[str, str]) -> str:
    host = land_best_intake.unquote_scalar(frontmatter.get("host_slug", ""))
    if not host:
        host = land_best_intake.unquote_scalar(frontmatter.get("channel_slug", ""))
    if not host and path.name.startswith("source-alexander-mercouris-"):
        host = "alexander-mercouris"
    return host


def repair_args(path: Path, frontmatter: dict[str, str], host_slug: str) -> SimpleNamespace:
    return SimpleNamespace(
        host_slug=host_slug,
        trim_opening="auto",
        asr_repair="auto",
        opening_trim_applied=land_best_intake.truthy_scalar(frontmatter.get("opening_trim_applied")),
        opening_trim_rule=land_best_intake.unquote_scalar(frontmatter.get("opening_trim_rule", "")),
        opening_trim_chars_saved=land_best_intake.safe_int(frontmatter.get("opening_trim_chars_saved", "0")),
        opening_trim_words_saved=land_best_intake.safe_int(frontmatter.get("opening_trim_words_saved", "0")),
        closing_trim_applied=land_best_intake.truthy_scalar(frontmatter.get("closing_trim_applied")),
        closing_trim_rule=land_best_intake.unquote_scalar(frontmatter.get("closing_trim_rule", "")),
        closing_trim_chars_saved=land_best_intake.safe_int(frontmatter.get("closing_trim_chars_saved", "0")),
        closing_trim_words_saved=land_best_intake.safe_int(frontmatter.get("closing_trim_words_saved", "0")),
        asr_repair_applied=land_best_intake.truthy_scalar(frontmatter.get("asr_repair_applied")),
        asr_repair_pass=land_best_intake.unquote_scalar(frontmatter.get("asr_repair_pass", "")),
        title=land_best_intake.unquote_scalar(frontmatter.get("title", path.stem)),
        source_form=land_best_intake.unquote_scalar(frontmatter.get("source_form", "interview")),
        sectioning="auto",
        transcript_curation=land_best_intake.unquote_scalar(
            frontmatter.get("transcript_curation", "preserved_unsectioned")
        ),
        section_count=land_best_intake.safe_int(frontmatter.get("section_count", "0")),
        section_pass=land_best_intake.unquote_scalar(frontmatter.get("section_pass", "")),
        editorial_note=land_best_intake.unquote_scalar(frontmatter.get("editorial_note", "")),
    )


def scalar_line(key: str, value: Any) -> str:
    if isinstance(value, bool):
        rendered = "true" if value else "false"
    elif isinstance(value, int):
        rendered = str(value)
    elif key in {"transcript_curation"}:
        rendered = str(value)
    else:
        rendered = land_best_intake.yaml_quote(str(value))
    return f"{key}: {rendered}"


def update_frontmatter(lines: list[str], updates: dict[str, Any]) -> tuple[list[str], tuple[str, ...]]:
    if not updates:
        return list(lines), ()
    existing = land_best_intake.parse_frontmatter_lines(lines)
    changed = tuple(sorted(key for key, value in updates.items() if existing.get(key) != scalar_line(key, value).split(":", 1)[1].strip()))
    output: list[str] = []
    seen: set[str] = set()
    insertion_index: int | None = None
    for line in lines:
        stripped = line.strip()
        key = stripped.split(":", 1)[0] if ":" in stripped else ""
        if key == "routing_state":
            insertion_index = len(output) + 1
        if key in updates:
            if key not in seen:
                output.append(scalar_line(key, updates[key]))
                seen.add(key)
            continue
        output.append(line)
    missing = [key for key in updates if key not in seen]
    rendered_missing = [scalar_line(key, updates[key]) for key in missing]
    if rendered_missing:
        index = insertion_index if insertion_index is not None else len(output)
        output[index:index] = rendered_missing
    return output, changed


def without_section_headings(body: str) -> str:
    return "\n".join(line for line in body.splitlines() if not line.startswith("### "))


def wording_tokens(body: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\S+", without_section_headings(body)))


def heading_only_components(text: str) -> tuple[list[str], str, str, str] | None:
    """Parse a legacy source and propose only the missing transcript heading."""
    if not (text.startswith("---\n") or text.startswith("---\r\n")):
        return None
    newline = "\r\n" if text.startswith("---\r\n") else "\n"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    frontmatter_lines = parts[1].splitlines()
    content_start = text.find("---", 3) + 3
    content = parts[2]
    if "## Transcript" in content or "## Cleaned Transcript" in content:
        return None
    title_match = re.search(r"(?m)^# .+\r?\n", content)
    if not title_match:
        return None
    insert_at = content_start + title_match.start()
    proposed = text[:insert_at] + f"## Transcript{newline}{newline}" + text[insert_at:]
    body = f"## Transcript{newline}{newline}" + content.lstrip("\r\n")
    return frontmatter_lines, content[: title_match.start()], body, proposed


def body_merge_components(
    text: str,
    supplied: str,
    *,
    expected_title: str,
) -> tuple[list[str], str, str] | None:
    """Build a deterministic full-body merge from one supplied transcript."""
    if not (text.startswith("---\n") or text.startswith("---\r\n")):
        return None
    newline = "\r\n" if text.startswith("---\r\n") else "\n"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    frontmatter_lines = parts[1].splitlines()
    content = supplied.replace("\r\n", "\n").replace("\r", "\n")
    expected_tokens = re.findall(r"[a-z0-9]+", expected_title.casefold())
    content_folded = content.casefold()
    if not expected_tokens or not all(token in content_folded for token in expected_tokens):
        return None
    start_marker = "Hi everyone, Judge Andrew Napolitano here for Judging Freedom."
    end_marker = "All the best. I look forward to it. Likewise."
    start = content.find(start_marker)
    end = content.find(end_marker, start if start >= 0 else 0)
    if start < 0 or end < 0:
        return None
    transcript = content[start : end + len(end_marker)].strip().replace("\n", newline)
    closing = text.find("---", 3)
    if closing < 0:
        return None
    header = text[: closing + 3].rstrip("\r\n")
    title_line = next((line for line in frontmatter_lines if line.startswith("title:")), "")
    title = land_best_intake.unquote_scalar(title_line.split(":", 1)[1].strip()) if ":" in title_line else expected_title
    proposed = (
        header + newline + "## Transcript" + newline + newline + "# " + title + newline + newline + transcript + newline
    )
    return frontmatter_lines, transcript, proposed


def plan_file(
    relative: str,
    path: Path,
    row: dict[str, Any],
    repair_class: str,
    *,
    resection: bool,
    replacement_body: str | None = None,
) -> FileRepairPlan:
    original = path.read_bytes()
    try:
        text = original.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ArchiveRepairError(f"target is not UTF-8: {relative}") from error
    if repair_class == "body-merge":
        title = land_best_intake.unquote_scalar(str(row.get("title") or ""))
        merged = body_merge_components(text, replacement_body or "", expected_title=title)
        if merged is None:
            raise ArchiveRepairError(f"target or supplied body is not a merge candidate: {relative}")
        frontmatter_lines, body, body_merge_proposed = merged
        body_prefix = ""
    elif repair_class == "heading-only":
        heading_split = heading_only_components(text)
        if heading_split is None:
            raise ArchiveRepairError(f"target is not a heading-only normalization candidate: {relative}")
        frontmatter_lines, body_prefix, body, heading_only_proposed = heading_split
    else:
        split = land_best_intake.split_source_document(text)
        if split is None:
            raise ArchiveRepairError(f"target source document is malformed: {relative}")
        frontmatter_lines, body_prefix, body = split
    frontmatter = land_best_intake.parse_frontmatter_lines(frontmatter_lines)
    host_slug = source_host(path, frontmatter)
    manifest_host = row.get("host_slug")
    if not host_slug or not isinstance(manifest_host, str) or not manifest_host:
        raise ArchiveRepairError(f"target host route is missing: {relative}")
    if host_slug != manifest_host:
        raise ArchiveRepairError(f"manifest and source host routes disagree: {relative}")

    args = repair_args(path, frontmatter, host_slug)
    proposed_body = body
    updates: dict[str, Any] = {}
    operations: tuple[str, ...] = ()
    before_sections = len(re.findall(r"(?m)^### ", body))

    if repair_class == "body-merge":
        operations = ("body-merge",)
    elif repair_class == "heading-only":
        operations = ("heading-only-normalization",)
    elif repair_class == "metadata":
        updates = {
            "transcript_curation": "curated_sectioned" if before_sections else "preserved_unsectioned",
            "section_count": before_sections,
        }
        operations = ("metadata-normalization",)
    elif repair_class == "asr":
        if not land_best_intake.host_supports_asr_repair(host_slug):
            raise ArchiveRepairError(f"ASR repair host is not approved: {relative}")
        proposed_body = land_best_intake.repair_asr_text(args, body, normalize_layout=False)
        updates = {
            "asr_repair_applied": args.asr_repair_applied,
            "asr_repair_pass": args.asr_repair_pass,
        }
        operations = ("asr-repair",)
    elif repair_class == "wrapper-trim":
        if host_slug not in land_best_intake.HOST_TRIM_RULES:
            raise ArchiveRepairError(f"wrapper-trim host is not approved: {relative}")
        proposed_body = land_best_intake.apply_trim_metadata(args, body)
        updates = {
            "opening_trim_applied": args.opening_trim_applied,
            "opening_trim_rule": args.opening_trim_rule,
            "opening_trim_chars_saved": args.opening_trim_chars_saved,
            "opening_trim_words_saved": args.opening_trim_words_saved,
            "closing_trim_applied": args.closing_trim_applied,
            "closing_trim_rule": args.closing_trim_rule,
            "closing_trim_chars_saved": args.closing_trim_chars_saved,
            "closing_trim_words_saved": args.closing_trim_words_saved,
        }
        operations = ("wrapper-trim",)
    elif repair_class == "sectioning":
        if not land_best_intake.host_supports_sectioning(host_slug):
            raise ArchiveRepairError(f"sectioning host is not approved: {relative}")
        if before_sections and not resection:
            proposed_body = body
            args.transcript_curation = "curated_sectioned"
            args.section_count = before_sections
            args.section_pass = land_best_intake.unquote_scalar(frontmatter.get("section_pass", ""))
            operations = ("sectioning-already-present",)
        else:
            base = land_best_intake.strip_transcript_section_headings(body) if resection else body
            proposed_body, args.transcript_curation, args.section_count, reason = land_best_intake.section_transcript(args, base)
            if args.transcript_curation != "curated_sectioned":
                raise ArchiveRepairError(f"sectioning did not find strong boundaries ({reason}): {relative}")
            if wording_tokens(base) != wording_tokens(proposed_body):
                raise ArchiveRepairError(f"sectioning would change transcript wording: {relative}")
            operations = ("resection" if resection else "sectioning",)
        updates = {
            "transcript_curation": args.transcript_curation,
            "section_count": args.section_count,
            "section_pass": args.section_pass,
        }
    else:  # pragma: no cover - caller validates the vocabulary
        raise ArchiveRepairError(f"unsupported repair class: {repair_class}")

    new_frontmatter, changed_fields = update_frontmatter(frontmatter_lines, updates)
    if repair_class == "body-merge":
        proposed_text = body_merge_proposed
    elif repair_class == "heading-only":
        proposed_text = heading_only_proposed
    else:
        proposed_text = "---\n" + "\n".join(new_frontmatter) + "\n---" + body_prefix + proposed_body.rstrip() + "\n"
    proposed = proposed_text.encode("utf-8")
    after_sections = len(re.findall(r"(?m)^### ", proposed_body))
    if repair_class == "metadata" and proposed_body != body:
        raise ArchiveRepairError(f"metadata repair would change body bytes: {relative}")
    if repair_class == "heading-only" and proposed_text.count("## Transcript") != 1:
        raise ArchiveRepairError(f"heading-only normalization produced an invalid transcript heading count: {relative}")
    if repair_class == "body-merge" and (
        proposed_text.count("## Transcript") != 1
        or "All the best. I look forward to it. Likewise." not in proposed_text
    ):
        raise ArchiveRepairError(f"body merge produced an invalid transcript boundary: {relative}")
    if repair_class == "asr" and (before_sections != after_sections or "wrapper-trim" in operations):
        raise ArchiveRepairError(f"ASR repair crossed an operation boundary: {relative}")
    diff = "".join(
        difflib.unified_diff(
            text.splitlines(keepends=True),
            proposed_text.splitlines(keepends=True),
            fromfile=relative,
            tofile=relative,
            lineterm="",
        )
    )
    return FileRepairPlan(
        path=relative,
        host_slug=host_slug,
        repair_class=repair_class,
        input_sha256=sha256_bytes(original),
        output_sha256=sha256_bytes(proposed),
        changed=original != proposed,
        operations=operations,
        changed_fields=changed_fields,
        section_count_before=before_sections,
        section_count_after=after_sections,
        diff=diff,
        original_bytes=original,
        proposed_bytes=proposed,
    )


def build_plan(
    raw_paths: Iterable[str],
    repair_class: str,
    *,
    resection: bool = False,
    repo_root: Path = REPO_ROOT,
    sources_root: Path = ARCHIVE_SOURCES_ROOT,
    manifest_path: Path = MANIFEST_PATH,
    replacement_body_path: str | None = None,
) -> ArchiveRepairPlan:
    if repair_class not in REPAIR_CLASSES:
        raise ArchiveRepairError(f"unsupported repair class: {repair_class}")
    if resection and repair_class != "sectioning":
        raise ArchiveRepairError("resection is valid only for the sectioning class")
    raw_path_list = list(raw_paths)
    replacement_body = None
    if repair_class == "body-merge":
        if not replacement_body_path:
            raise ArchiveRepairError("body-merge requires a supplied body file")
        if len(raw_path_list) != 1:
            raise ArchiveRepairError("body-merge accepts exactly one archive target")
        replacement_body = Path(replacement_body_path).read_text(encoding="utf-8")
    manifest, manifest_hash = load_manifest(manifest_path)
    targets = resolve_targets(raw_path_list, repo_root=repo_root, sources_root=sources_root)
    rows = manifest_rows_by_path(manifest)
    plans: list[FileRepairPlan] = []
    for relative, path in targets:
        matches = rows.get(relative, [])
        if len(matches) != 1:
            raise ArchiveRepairError(
                f"target must have exactly one manifest row ({len(matches)} found): {relative}"
            )
        plans.append(
            plan_file(
                relative,
                path,
                matches[0],
                repair_class,
                resection=resection,
                replacement_body=replacement_body,
            )
        )
    digest_payload = {
        "manifest_sha256": manifest_hash,
        "repair_class": repair_class,
        "resection": resection,
        "files": [
            {
                "path": item.path,
                "input_sha256": item.input_sha256,
                "output_sha256": item.output_sha256,
                "operations": item.operations,
                "changed_fields": item.changed_fields,
            }
            for item in plans
        ],
    }
    return ArchiveRepairPlan(
        manifest_id=str(manifest.get("manifest_id") or ""),
        manifest_sha256=manifest_hash,
        repair_class=repair_class,
        resection=resection,
        files=tuple(plans),
        plan_digest=sha256_bytes(canonical_json(digest_payload).encode("utf-8")),
    )


def _atomic_replace(path: Path, payload: bytes) -> None:
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def apply_plan(
    plan: ArchiveRepairPlan,
    *,
    expected_digest: str,
    repo_root: Path = REPO_ROOT,
    manifest_path: Path = MANIFEST_PATH,
) -> dict[str, Any]:
    if expected_digest != plan.plan_digest:
        raise ArchiveRepairError("plan digest does not match the reviewed plan")
    _, current_manifest_hash = load_manifest(manifest_path)
    if current_manifest_hash != plan.manifest_sha256:
        raise ArchiveRepairError("source manifest changed after the plan was built")
    targets = [item.path for item in plan.files]
    dirty = dirty_paths(targets, repo_root=repo_root)
    if dirty:
        raise ArchiveRepairError(f"execution target is already dirty: {sorted(dirty)[0]}")
    paths = {item.path: (repo_root / item.path).resolve() for item in plan.files}
    for item in plan.files:
        if sha256_bytes(paths[item.path].read_bytes()) != item.input_sha256:
            raise ArchiveRepairError(f"target changed after the plan was built: {item.path}")

    applied: list[FileRepairPlan] = []
    try:
        for item in plan.files:
            if not item.changed:
                continue
            _atomic_replace(paths[item.path], item.proposed_bytes)
            applied.append(item)
    except Exception as error:
        rollback_failures: list[str] = []
        for item in reversed(applied):
            try:
                _atomic_replace(paths[item.path], item.original_bytes)
            except Exception:
                rollback_failures.append(item.path)
        if rollback_failures:
            raise ArchiveRepairError(
                "archive repair failed and rollback was incomplete: " + ", ".join(sorted(rollback_failures))
            ) from error
        raise ArchiveRepairError("archive repair failed; all applied files were rolled back") from error

    for item in applied:
        if sha256_bytes(paths[item.path].read_bytes()) != item.output_sha256:
            raise ArchiveRepairError(f"post-write hash mismatch: {item.path}")
    return plan.public(disposition="executed")


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Archive Repair",
        "",
        f"- Disposition: `{payload['disposition']}`",
        f"- Repair class: `{payload['repair_class']}`",
        f"- Targets: `{payload['target_count']}`",
        f"- Changed: `{payload['changed_count']}`",
        f"- Plan digest: `{payload['plan_digest']}`",
        "- Authority effect: `none`",
        "- Capability token: `false`",
        "",
        "> This plan describes bounded archive repair and grants no authority.",
    ]
    for item in payload["files"]:
        lines.extend(
            [
                "",
                f"## {item['path']}",
                "",
                f"- Changed: `{str(item['changed']).lower()}`",
                f"- Operations: `{', '.join(item['operations'])}`",
                f"- Changed fields: `{', '.join(item['changed_fields'])}`",
            ]
        )
        if item["diff"]:
            lines.extend(["", "```diff", item["diff"].rstrip(), "```"])
    return "\n".join(lines).rstrip() + "\n"

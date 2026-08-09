from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
MANIFEST_PATH = NG_ROOT / "archive" / "source-manifest.json"

VOICE_ALIASES = {
    "larry-johnson": "johnson",
    "ted-postol": "postol",
    "scott-ritter": "ritter",
    "stanislav-krapivnik": "krapivnik",
    "steve-jermy": "jermy",
    "trita-parsi": "parsi",
    "alexander-mercouris": "mercouris",
    "alex-christoforou": "cristoforou",
    "christoforou": "cristoforou",
    "jiang-xueqin": "jiang",
}

FRONTMATTER_RE = re.compile(
    rb"\A---(?P<open>\r?\n)(?P<header>.*?)(?P<close>^---\r?\n)",
    re.MULTILINE | re.DOTALL,
)
SCALAR_RE = re.compile(r"^(?P<key>thread|voice_slug):\s*(?P<value>.*?)\s*$")


def canonical_slug(value: str) -> str:
    return VOICE_ALIASES.get(value, value)


def canonicalize_slugs(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        canonical = canonical_slug(value)
        if canonical and canonical not in result:
            result.append(canonical)
    return result


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_manifest(manifest: dict[str, Any], path: Path = MANIFEST_PATH) -> None:
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _unquote(value: str) -> tuple[str, str]:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1], value[0]
    return value, ""


def canonicalize_frontmatter_bytes(data: bytes) -> tuple[bytes, list[dict[str, str]], bool]:
    match = FRONTMATTER_RE.match(data)
    if not match:
        return data, [], False
    header_bytes = match.group("header")
    body = data[match.end() :]
    header = header_bytes.decode("utf-8")
    changes: list[dict[str, str]] = []
    rewritten: list[str] = []
    for line in header.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        ending = line[len(content) :]
        scalar = SCALAR_RE.match(content)
        if not scalar:
            rewritten.append(line)
            continue
        raw_value = scalar.group("value")
        value, quote = _unquote(raw_value)
        canonical = canonical_slug(value)
        if canonical == value:
            rewritten.append(line)
            continue
        rendered = f"{quote}{canonical}{quote}" if quote else canonical
        rewritten.append(f"{scalar.group('key')}: {rendered}{ending}")
        changes.append({"field": scalar.group("key"), "before": value, "after": canonical})
    if not changes:
        return data, [], True
    prefix = data[: match.start("header")]
    close = match.group("close")
    updated = prefix + "".join(rewritten).encode("utf-8") + close + body
    updated_match = FRONTMATTER_RE.match(updated)
    return updated, changes, bool(updated_match and updated[updated_match.end() :] == body)


def selected_rows(manifest: dict[str, Any], run_date: str | None) -> list[dict[str, Any]]:
    rows = manifest.get("sources", [])
    return [row for row in rows if run_date is None or row.get("date") == run_date]


def inspect_metadata(
    manifest: dict[str, Any], repo_root: Path = REPO_ROOT, run_date: str | None = None
) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    failures: list[str] = []
    for row in selected_rows(manifest, run_date):
        before = list(row.get("voice_slugs") or [])
        after = canonicalize_slugs(before)
        local_path = row.get("local_path", "")
        row_change: dict[str, Any] = {"local_path": local_path}
        if before != after:
            row_change["manifest_voice_slugs"] = {"before": before, "after": after}
        target = repo_root / local_path
        if not target.exists():
            failures.append(f"missing archive source file: {local_path}")
        else:
            original = target.read_bytes()
            _, frontmatter_changes, preserved = canonicalize_frontmatter_bytes(original)
            if frontmatter_changes:
                row_change["frontmatter"] = frontmatter_changes
                original_match = FRONTMATTER_RE.match(original)
                body = original[original_match.end() :] if original_match else original
                row_change["body_sha256"] = hashlib.sha256(body).hexdigest()
                row_change["body_preserved"] = preserved
        if len(row_change) > 1:
            changes.append(row_change)
    return {"changes": changes, "failures": failures}


def apply_metadata(
    manifest: dict[str, Any], repo_root: Path = REPO_ROOT, run_date: str | None = None
) -> dict[str, Any]:
    report = inspect_metadata(manifest, repo_root, run_date)
    if report["failures"]:
        return report
    selected = {id(row) for row in selected_rows(manifest, run_date)}
    for row in manifest.get("sources", []):
        if id(row) not in selected:
            continue
        row["voice_slugs"] = canonicalize_slugs(list(row.get("voice_slugs") or []))
        target = repo_root / row.get("local_path", "")
        original = target.read_bytes()
        updated, _, preserved = canonicalize_frontmatter_bytes(original)
        if not preserved:
            report["failures"].append(f"source body changed during metadata rewrite: {row.get('local_path', '')}")
            return report
        if updated != original:
            target.write_bytes(updated)
    return report


def metadata_failures(
    manifest: dict[str, Any], repo_root: Path = REPO_ROOT, run_date: str | None = None
) -> list[str]:
    report = inspect_metadata(manifest, repo_root, run_date)
    failures = list(report["failures"])
    for change in report["changes"]:
        if "manifest_voice_slugs" in change:
            failures.append(f"noncanonical manifest voice slug: {change['local_path']}")
        if "frontmatter" in change:
            fields = ", ".join(item["field"] for item in change["frontmatter"])
            failures.append(f"noncanonical archive voice metadata ({fields}): {change['local_path']}")
    return failures

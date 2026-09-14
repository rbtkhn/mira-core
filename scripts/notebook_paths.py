"""Mind-owned Notebook locations and byte-preserving historical aliases."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
from repository_paths import resolve_geopolitics_reference


def root(repo):
    return Path(repo) / "mira/strategy-notebook"


def safe(repo, ref):
    if not isinstance(ref, str) or not ref or "\\" in ref or ":" in ref:
        raise ValueError("Expected repository-relative POSIX reference")
    if PurePosixPath(ref).is_absolute() or any(p in {"..", ".git"} for p in PurePosixPath(ref).parts):
        raise ValueError("Unsafe Notebook reference")
    path = (Path(repo) / ref).resolve()
    if not path.is_relative_to(Path(repo).resolve()):
        raise ValueError("Reference escapes repository")
    return path


def normalize(ref):
    return ref.replace("narrative-geopolitics/", "geopolitics/", 1) if ref.startswith("narrative-geopolitics/") else ref


def relocations(repo):
    path = root(repo) / "relocations.json"
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version") != 1:
        raise ValueError("Unsupported Notebook relocation manifest")
    rows = value["files"]
    seen = set()
    destinations = set()
    for row in rows:
        safe(repo, row["old_path"])
        destination = safe(repo, row["new_path"])
        if not destination.is_relative_to(root(repo).resolve()) or not re.fullmatch(r"[a-f0-9]{64}", row["sha256"]):
            raise ValueError("Invalid Notebook relocation")
        key = normalize(row["old_path"])
        if key in seen or row["new_path"] in destinations:
            raise ValueError("Duplicate Notebook relocation")
        seen.add(key)
        destinations.add(row["new_path"])
    return rows


def resolve(repo, ref):
    safe(repo, ref)
    for row in relocations(repo):
        if normalize(ref) == normalize(row["old_path"]):
            return safe(repo, row["new_path"])
    if ref.startswith(("geopolitics/", "narrative-geopolitics/")):
        return resolve_geopolitics_reference(Path(repo), ref)
    return safe(repo, ref)


def original(repo, ref):
    return next((r["old_path"] for r in relocations(repo) if r["new_path"] == ref), ref)


def identity(repo, ref):
    return resolve(repo, ref).relative_to(Path(repo).resolve()).as_posix()


def daily(repo, day):
    new = root(repo) / "daily" / (day + ".md")
    old = resolve_geopolitics_reference(Path(repo), f"geopolitics/work/daily/{day}/strategy-notebook.md")
    return new if new.exists() or (root(repo) / "relocations.json").exists() else old


def monthly(repo, month):
    new = root(repo) / "monthly" / (month + ".md")
    old = resolve_geopolitics_reference(Path(repo), f"geopolitics/work/strategy-notebook/{month}.md")
    return new if new.exists() or (root(repo) / "relocations.json").exists() else old


def readable(repo, ref):
    """Derived Markdown only: relocate links relative to their recorded origin."""
    path = resolve(repo, ref)
    current = path.relative_to(Path(repo).resolve()).as_posix()
    recorded = original(repo, current)
    text = path.read_text(encoding="utf-8-sig")
    def link(match):
        target = match.group(1)
        if ":" in target or target.startswith(("#", "/")):
            return match.group(0)
        base, sep, fragment = target.partition("#")
        absolute = (Path(repo) / recorded).parent.joinpath(base).resolve()
        if not absolute.is_relative_to(Path(repo).resolve()):
            return match.group(0)
        resolved = resolve(repo, absolute.relative_to(Path(repo).resolve()).as_posix())
        return "](" + resolved.as_posix() + (sep + fragment if sep else "") + ")"
    return re.sub(r"\]\(([^)]+)\)", link, text)

"""Tower session continuity and source-version accounting. No implicit intake."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
import yaml

import journal_calendar
import strategy_notebook as notebook
import youtube_capture as capture
from portable_paths import state_path

REPO_ROOT = Path(__file__).resolve().parents[1]
SETTLED = {"considered", "deferred", "excluded"}


def utc():
    return datetime.now(timezone.utc).isoformat()


def create_json(path, value):
    """Publish complete bytes without replacing another session's entry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".tower-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def local_path(repo, raw):
    path = (repo / raw).resolve()
    if Path(raw).is_absolute() or not path.is_relative_to(repo.resolve()):
        raise ValueError("Tower reference must remain within the repository")
    return path


def identity(url, fallback):
    try:
        video = capture.extract_video_id(url)
        return "youtube:" + video if video else fallback
    except (ValueError, capture.CaptureError):
        return fallback


def activation_path(repo=REPO_ROOT, root=None):
    key = notebook.digest(str(repo.resolve()).encode())[:16]
    return state_path(f"tower/{key}/activation.json", root=root, repo_root=repo)


def read_targets(path):
    """Read historical target tables without rewriting their original bytes."""
    try:
        return capture.read_singularity_target_rows(path)
    except capture.CaptureError:
        rows, headers = [], None
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [cell.strip().strip("`").replace(r"\|", "|") for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            if all(re.fullmatch(r"[\s:-]*", cell) for cell in cells):
                continue
            if headers is None:
                headers = cells
                if headers not in (["visible_age", "title", "url", "target_status", "next_action"],
                                   ["Video URL", "Title", "Publication date", "Channel", "Observed date", "Absence check", "Next eligible workflow"]):
                    raise ValueError(f"Unsupported capture-target table: {path}")
                continue
            if len(cells) != len(headers):
                raise ValueError(f"Malformed capture-target table: {path}")
            row = dict(zip(headers, cells))
            url = row.get("url", row.get("Video URL", ""))
            key = identity(url, "")
            if not key:
                raise ValueError(f"Invalid capture-target URL: {path}")
            day = re.search(r"\d{4}-\d{2}-\d{2}", path.name)
            rows.append({"url": url, "source_identity": key,
                         "capture_date": row.get("Observed date", day.group(0) if day else ""),
                         "title": row.get("title", row.get("Title", "")),
                         "next_action": row.get("next_action", row.get("Next eligible workflow", ""))})
        if headers is None:
            raise ValueError(f"Capture-target table unavailable: {path}")
        return rows


def scan(repo=REPO_ROOT):
    """Read canonical metadata and routed targets; surface incomplete readers."""
    sources, queues, gaps = {}, {}, []
    def source(path, lane, url="", observed=""):
        raw = path.read_bytes()
        if not url:
            match = re.search(r"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[A-Za-z0-9_-]+", raw.decode("utf-8-sig")[:4000])
            url = match.group(0) if match else ""
        rel = path.relative_to(repo).as_posix()
        key = identity(url, "file:" + rel)
        row = {"identity": key, "version": notebook.digest(raw), "path": rel,
               "lane": lane, "date": observed, "kind": "analysis-pending",
               "available_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}
        row["source_versions"] = [{"path": rel, "sha256": row["version"]}]
        if key in sources:
            previous = sources[key]
            versions = {item["path"]: item for item in previous["source_versions"] + row["source_versions"]}
            previous["source_versions"] = [versions[path] for path in sorted(versions)]
            previous["version"] = notebook.digest(previous["source_versions"])
            previous["available_at"] = max(previous["available_at"], row["available_at"])
        else:
            sources[key] = row
    manifest = repo / "archive/sources/geopolitics/source-manifest.json"
    try:
        rows = json.loads(manifest.read_text(encoding="utf-8-sig"))["sources"]
        for row in rows:
            try:
                source(local_path(repo, row["local_path"]), "geopolitics", row.get("source_url", ""), row.get("date", ""))
            except (OSError, ValueError, KeyError) as error:
                gaps.append({"path": row.get("local_path", "manifest row"), "reason": str(error)})
    except (OSError, ValueError, KeyError) as error:
        gaps.append({"path": str(manifest.relative_to(repo)), "reason": str(error)})
    try:
        routing = yaml.safe_load((repo / "archive/sources/youtube-channel-routing.yml").read_text(encoding="utf-8-sig"))
        if not isinstance(routing, dict):
            raise ValueError("Invalid channel routing document")
        # Routing owns channel membership and target patterns.
        def routes(value):
            if isinstance(value, dict):
                if value.get("archive_lane") == "singularity" and value.get("target_pattern"):
                    yield value
                else:
                    for child in value.values():
                        yield from routes(child)
            elif isinstance(value, list):
                for child in value:
                    yield from routes(child)
        for route in routes(routing):
            pattern = route["target_pattern"].replace("{date}", "*")
            local_path(repo, pattern)
            for path in sorted(repo.glob(pattern)):
                try:
                    for row in read_targets(path):
                        row["date"] = row.get("capture_date", "")
                        queues[row["source_identity"]] = {**row, "lane": "singularity", "queue_path": path.relative_to(repo).as_posix()}
                except (OSError, ValueError, capture.CaptureError) as error:
                    gaps.append({"path": path.relative_to(repo).as_posix(), "reason": str(error)})
        shelf = repo / "archive/sources/singularity"
        if not shelf.is_dir():
            raise ValueError("Singularity source shelf unavailable")
        for path in sorted(shelf.glob("*/transcripts/*.md")):
            try:
                source(path, "singularity")
            except (OSError, ValueError) as error:
                gaps.append({"path": path.relative_to(repo).as_posix(), "reason": str(error)})
    except (OSError, ValueError, yaml.YAMLError) as error:
        gaps.append({"path": "archive/sources/youtube-channel-routing.yml", "reason": str(error)})
    queue_root = notebook.domain(repo) / "work/capture/youtube"
    if not queue_root.is_dir():
        gaps.append({"path": queue_root.relative_to(repo).as_posix(), "reason": "capture queue unavailable"})
    else:
        for path in sorted(queue_root.glob("*.jsonl")):
            try:
                for row in capture.read_queue(path):
                    key = identity(row.get("url", ""), row.get("source_identity", ""))
                    if not key or key.startswith("youtube-channel:"):
                        continue
                    queues[key] = {**row, "lane": "geopolitics", "queue_path": path.relative_to(repo).as_posix()}
            except (OSError, ValueError, capture.CaptureError) as error:
                gaps.append({"path": path.relative_to(repo).as_posix(), "reason": str(error)})
    return sources, queues, gaps


def initialize(repo=REPO_ROOT, root=None):
    path = activation_path(repo, root)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    sources, queues, gaps = scan(repo)
    if gaps:
        raise ValueError("Activation requires complete readers: " + json.dumps(gaps))
    value = {"schema_version": 1, "activated_at": utc(), "repository": str(repo.resolve()),
             "baseline": {key: row["version"] for key, row in sources.items()},
             "open_targets": sorted(key for key, row in queues.items() if key not in sources and row.get("disposition") != "skip")}
    try:
        create_json(path, value)
    except FileExistsError:
        return json.loads(path.read_text(encoding="utf-8"))
    return value


def contributions(repo=REPO_ROOT):
    rows = []
    for path in sorted((notebook.domain(repo) / "work/strategy-notebook/contributions").glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("content_sha256") != notebook.digest({k: v for k, v in value.items() if k != "content_sha256"}):
            raise ValueError(f"Tower contribution digest mismatch: {path}")
        rows.append({**value, "path": path.relative_to(repo).as_posix()})
    return sorted(rows, key=lambda row: (row["closed_at"], row["contribution_id"]))


def pending(day, repo=REPO_ROOT, root=None, catch_up=False):
    date.fromisoformat(day)
    _, cutoff = journal_calendar.day_bounds(date.fromisoformat(day))
    sources, queues, gaps = scan(repo)
    path = activation_path(repo, root)
    try:
        baseline = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        baseline = {"baseline": {}, "open_targets": []}
        gaps.append({"path": "Tower activation", "reason": str(error)})
    dispositions = {}
    try:
        for entry in contributions(repo):
            if entry["date"] <= day:
                for row in entry["source_dispositions"]:
                    dispositions[(row["identity"], row["version"])] = row
    except (OSError, ValueError) as error:
        gaps.append({"path": "Tower contributions", "reason": str(error)})
    result = []
    for key in sorted(set(sources) | set(queues)):
        source, queued = sources.get(key), queues.get(key)
        if queued and queued.get("date", "") > day:
            queued = None
        if source and source.get("date", "") > day:
            continue
        if source and datetime.fromisoformat(source["available_at"]) >= cutoff:
            continue
        if source:
            if not catch_up and baseline["baseline"].get(key) == source["version"] and key not in baseline["open_targets"]:
                continue
            row = dict(source)
        elif queued:
            if queued.get("disposition") == "skip":
                continue
            row = {"identity": key, "version": notebook.digest({k: queued.get(k) for k in ("url", "transcript_status", "next_action")}),
                   "path": queued["queue_path"], "lane": queued["lane"],
                   "kind": "intake-pending" if queued.get("transcript_status") == "available" else "acquisition-pending"}
        else:
            continue
        disposition = dispositions.get((key, row["version"]))
        if disposition:
            row["kind"] = disposition["status"]
            row["reason"] = disposition["reason"]
        result.append(row)
    unresolved = [row for row in result if row["kind"] not in SETTLED]
    value = {"schema_version": 1, "date": day, "items": result, "pending": unresolved,
             "counts": dict(Counter(row["kind"] for row in unresolved)), "gaps": gaps,
             "status": "unknown" if gaps else "pending" if unresolved else "clear",
             "authority_effect": "none"}
    # Touching a file without changing content must not invalidate a reviewed batch.
    value["batch_sha256"] = notebook.digest({"pending": [{k: v for k, v in row.items() if k != "available_at"} for row in unresolved], "gaps": gaps})
    return value


def close(value, repo=REPO_ROOT, check=False):
    import cognitive_context
    clean = dict(value)
    identifier = clean.get("contribution_id", "")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", identifier):
        raise ValueError("A stable safe contribution_id is required")
    path = notebook.domain(repo) / "work/strategy-notebook/contributions" / (identifier + ".json")
    request_digest = notebook.digest(value)
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        expected = notebook.digest({k: v for k, v in existing.items() if k != "content_sha256"})
        if existing.get("content_sha256") != expected:
            raise ValueError("Existing contribution integrity failure")
        if existing.get("request_sha256") != request_digest:
            raise ValueError("Contribution identity already exists with different content; append a correction")
        return {"status": "reused", "path": path.relative_to(repo).as_posix(), "content_sha256": expected}
    date.fromisoformat(clean["date"])
    timestamp = datetime.fromisoformat(clean["closed_at"])
    if timestamp.tzinfo is None:
        raise ValueError("closed_at must include a timezone")
    start, end = journal_calendar.day_bounds(date.fromisoformat(clean["date"]))
    if not start <= timestamp < end:
        raise ValueError("closed_at must fall within the declared dated-calendar day")
    for field in ("session_id", "question", "return_point"):
        if not isinstance(clean.get(field), str) or not clean[field].strip():
            raise ValueError(f"{field} is required")
    clean.setdefault("disposition_only", False)
    if not clean["disposition_only"]:
        for field in ("assessment", "delta"):
            if not isinstance(clean.get(field), str) or not clean[field].strip():
                raise ValueError(f"{field} is required")
    for field in ("source_dispositions", "correction_links", "note_proposals"):
        clean.setdefault(field, [])
        if not isinstance(clean[field], list):
            raise ValueError(f"{field} must be a list")
    known_sources, known_queues, _ = scan(repo) if clean["source_dispositions"] else ({}, {}, [])
    for row in clean["source_dispositions"]:
        if row.get("status") not in SETTLED | {"analysis-pending", "unknown"} or not row.get("identity") or not row.get("reason"):
            raise ValueError("Invalid source disposition")
        if not re.fullmatch(r"[0-9a-f]{64}", row.get("version", "")):
            raise ValueError("Source version must be a SHA-256")
        path = local_path(repo, row["path"])
        if not path.is_file():
            raise ValueError("Disposition source is unavailable")
        source = known_sources.get(row["identity"])
        queued = known_queues.get(row["identity"])
        expected = source["version"] if source else notebook.digest({k: queued.get(k) for k in ("url", "transcript_status", "next_action")}) if queued else None
        expected_path = source["path"] if source else queued["queue_path"] if queued else None
        if expected != row["version"] or expected_path != row["path"]:
            raise ValueError("Disposition source identity or version changed")
        if not source and row["status"] == "considered":
            raise ValueError("Unlanded transcript cannot be marked analytically considered")
    for link in clean["correction_links"]:
        if not local_path(repo, link).is_file():
            raise ValueError("Correction target unavailable")
    clean["note_proposals"] = cognitive_context.nominations(clean["note_proposals"], repo)
    if clean["disposition_only"] and not clean["source_dispositions"]:
        raise ValueError("Disposition-only close requires at least one source disposition")
    clean["schema_version"] = 1
    clean["request_sha256"] = request_digest
    clean.pop("content_sha256", None)
    clean["content_sha256"] = notebook.digest(clean)
    path = notebook.domain(repo) / "work/strategy-notebook/contributions" / (identifier + ".json")
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != clean:
            raise ValueError("Contribution identity already exists with different content; append a correction")
        return {"status": "reused", "path": path.relative_to(repo).as_posix(), "content_sha256": clean["content_sha256"]}
    if not check:
        try:
            create_json(path, clean)
        except FileExistsError:
            return close(value, repo)
    return {"status": "validated" if check else "saved", "path": path.relative_to(repo).as_posix(), "content_sha256": clean["content_sha256"]}


def context(day, focus="", repo=REPO_ROOT):
    entries = [row for row in contributions(repo) if row["date"] <= day and not row.get("disposition_only")]
    legacy = notebook.inventory(repo)
    candidates = [(row["date"], row["closed_at"], row["question"]) for row in entries]
    candidates += [(row["entry_date"], "", notebook.section(row["text"], "Strategic Question", "Question of Order")) for row in legacy if row["entry_date"] <= day]
    inferred = not focus
    if not focus and candidates:
        focus = max(candidates)[2]
    result = notebook.context(day, focus, repo)
    result["focus_basis"] = "latest recorded inquiry; activity not inferred" if inferred else "explicit inquiry"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("context", "pending", "activate"):
        sub = commands.add_parser(command)
        sub.add_argument("--date", default=journal_calendar.current_date().isoformat())
        sub.add_argument("--focus", default="")
        sub.add_argument("--state-root", type=Path)
        sub.add_argument("--catch-up", action="store_true")
        sub.add_argument("--json", action="store_true")
    sub = commands.add_parser("close")
    sub.add_argument("--input", required=True, type=Path)
    sub.add_argument("--check", action="store_true")
    sub.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "context":
            result = context(args.date, args.focus)
        elif args.command == "pending":
            result = pending(args.date, root=args.state_root, catch_up=args.catch_up)
        elif args.command == "activate":
            result = initialize(root=args.state_root)
        else:
            result = close(json.loads(args.input.read_text(encoding="utf-8")), check=args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"tower error: {error}\n")


if __name__ == "__main__":
    main()

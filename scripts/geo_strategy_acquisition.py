"""Geo-Strategy source acquisition and version accounting. No implicit intake."""
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
    return notebook.contributions(repo)


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
    # Capture coverage is advisory and separate from version-bound analytical work.
    # Do not put private email paths in notebook dispositions or change old hashes.
    import newsletter_capture
    try:
        capture_state = newsletter_capture.status(newsletter_capture.Store(repo, root))
        value["newsletters"] = {key: capture_state[key] for key in
                                ("status", "routine_enabled", "counts", "last_retrieval", "gap")}
    except (OSError, ValueError, KeyError):
        value["newsletters"] = {"status": "unavailable", "gap": "Newsletter capture state unavailable"}
    return value


def survey_coverage(day, repo=REPO_ROOT):
    """Inspect today's curated daily scope; never perform discovery or capture."""
    date.fromisoformat(day)
    domain = notebook.domain(repo)
    channels = capture.select_channel_index_rows(
        capture.parse_channel_index(domain / "channels/channel-index.md"),
        cadences={"daily"}, channels=set(), include_active=False, include_candidate=False)
    if not channels or len({r["slug"] for r in channels}) != len(channels):
        raise ValueError("Survey requires a nonempty, unambiguous daily channel roster")
    receipts, gaps = [], []
    for row in channels:
        path = capture.browser_receipt_path(day, row["slug"], domain / "work/capture/youtube")
        try:
            raw = path.read_bytes()
            receipt = json.loads(raw)
            access = receipt.get("access_context", {})
            urls = receipt.get("observed_urls", [])
            if not isinstance(urls, list) or any(not isinstance(url, str) for url in urls):
                raise ValueError("Invalid observed video URLs")
            for url in urls:
                capture.extract_video_id(url)
            observed = datetime.fromisoformat(receipt.get("observed_at", "").replace("Z", "+00:00"))
            if observed.tzinfo is None:
                raise ValueError("Browser observation requires a timezone")
            notes = str(receipt.get("notes", "")).lower()
            if receipt.get("no_qualifying_videos") is True and not (
                    ("videos" in notes or "live" in notes) and "search" in notes):
                raise ValueError("Empty survey requires inspected channel surfaces and search")
            valid = (receipt.get("schema_version") == capture.BROWSER_RECEIPT_SCHEMA_VERSION
                     and receipt.get("status") == "complete"
                     and receipt.get("capture_date") == day
                     and receipt.get("channel_slug") == row["slug"]
                     and receipt.get("channel_url") == row["channel_url"]
                     and receipt.get("evidence_basis") == "in-app-browser-visible-channel-page"
                     and receipt.get("rss_completion_authority") is False
                     and access.get("mode") in {"public", "authenticated"}
                     and access.get("eligibility") == "eligible"
                     and (receipt.get("observed_urls") or receipt.get("no_qualifying_videos") is True))
            capture.browser_access_context(access.get("mode"), access.get("eligibility"), access.get("observed_at", ""))
            if not valid:
                raise ValueError("Missing or mismatched channel/date/browser/access evidence")
            receipts.append({"channel_slug": row["slug"], "path": path.relative_to(repo).as_posix(),
                             "sha256": notebook.digest(raw)})
        except (OSError, ValueError, AttributeError, TypeError) as error:
            gaps.append({"channel_slug": row["slug"], "reason": str(error)})
    return {"date": day, "channels": channels, "receipts": receipts, "gaps": gaps,
            "status": "incomplete" if gaps else "complete"}


def survey_plan(day, repo=REPO_ROOT, root=None):
    coverage = survey_coverage(day, repo)
    backlog = pending(day, repo, root)
    # Tower's broader strategic inventory also includes Singularity; this window does not.
    backlog = {**backlog, "items": [r for r in backlog["items"] if r.get("lane") == "geopolitics"],
               "pending": [r for r in backlog["pending"] if r.get("lane") == "geopolitics"]}
    backlog["counts"] = dict(Counter(r["kind"] for r in backlog["pending"]))
    backlog["status"] = "unknown" if backlog["gaps"] else "pending" if backlog["pending"] else "clear"
    backlog.pop("batch_sha256", None)
    scope = [r["slug"] for r in coverage["channels"]]
    flags = [arg for slug in scope for arg in ("--channel", slug)]
    binding = {k: coverage[k] for k in ("date", "receipts", "gaps", "status")}
    binding["channel_slugs"] = scope
    return {"schema_version": 1, "survey": coverage, "survey_binding": binding, "backlog": backlog,
            "next_commands": [["tools/run.ps1", "mira-youtube", command, "--date", day, *flags]
                              for command in ("daily-check", "browser-coverage")],
            "browser_work": "Subscriptions first when authenticated; verify watch pages and record channel coverage. Commands do not operate the browser.",
            "authority_effect": "read-only plan; no discovery, capture, intake, or analysis performed"}


def validate_survey(binding, day, repo):
    if not isinstance(binding, dict) or binding.get("date") != day:
        raise ValueError("Survey binding date must match contribution date")
    coverage = survey_coverage(day, repo)
    if binding.get("channel_slugs") != [r["slug"] for r in coverage["channels"]]:
        raise ValueError("Survey channel scope changed")
    if binding.get("receipts") != coverage["receipts"]:
        raise ValueError("Survey receipt bindings changed")
    if binding.get("status") != coverage["status"]:
        raise ValueError("Survey completion does not match browser coverage")
    if coverage["gaps"] and binding.get("gaps") != coverage["gaps"]:
        raise ValueError("Incomplete survey must preserve coverage gaps")


def close(value, repo=REPO_ROOT, check=False):
    return notebook.close(value, repo, check=check, legacy=True)


def context(day, focus="", repo=REPO_ROOT):
    return notebook.inquiry_context(day, focus, repo)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("context", "pending", "activate", "survey-plan"):
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
            result = notebook.inquiry_context(args.date, args.focus)
        elif args.command == "survey-plan":
            result = survey_plan(args.date, root=args.state_root)
        elif args.command == "pending":
            result = pending(args.date, root=args.state_root, catch_up=args.catch_up)
        elif args.command == "activate":
            result = initialize(root=args.state_root)
        else:
            result = notebook.close(json.loads(args.input.read_text(encoding="utf-8")), check=args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"tower error: {error}\n")


if __name__ == "__main__":
    main()

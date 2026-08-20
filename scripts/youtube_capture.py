"""Queue-only YouTube source capture for Narrative Geopolitics.

This tool records candidate source leads for later governed intake. It does
not fetch transcript bodies, land archive sources, mutate manifests, or produce
geo-strategy synthesis.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree


REPO_ROOT = Path(__file__).resolve().parent.parent
QUEUE_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "capture" / "youtube"
CHANNEL_INDEX_PATH = REPO_ROOT / "narrative-geopolitics" / "channels" / "channel-index.md"
MANIFEST_PATH = REPO_ROOT / "archive" / "sources" / "geopolitics" / "source-manifest.json"

TRANSCRIPT_STATUSES = {"available", "missing", "manual-needed", "defer"}
DISPOSITIONS = {"must-land", "possible", "skip", "watch"}
CHANNEL_EXPECTED_VOICE = {
    "alexander-mercouris": "mercouris",
    "daniel-davis": "davis",
    "glenn-diesen": "diesen",
}
QUEUE_ONLY_NOTICE = "YOUTUBE_CAPTURE_MODE=queue-draft-only"
AUTHORITY_NOTICE = (
    "AUTHORITY_BOUNDARY=no archive landing, manifest mutation, synthesis, "
    "forecast, Reality, publication, staging, commit, push, or deployment"
)
USER_AGENT = "mira-core-youtube-capture/1.0"


class CaptureError(ValueError):
    pass


def parse_capture_date(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must be YYYY-MM-DD") from error


def parse_nonnegative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("value must be an integer") from error
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be nonnegative")
    return parsed


def queue_path(capture_date: str, queue_root: Path = QUEUE_ROOT) -> Path:
    return queue_root / f"{capture_date}.jsonl"


def extract_video_id(url: str) -> str:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        query_id = parse_qs(parsed.query).get("v", [""])[0]
        if query_id:
            return query_id
        match = re.match(r"^/(?:shorts|live|embed)/([^/?#]+)", parsed.path)
        if match:
            return match.group(1)
    if host == "youtu.be":
        candidate = parsed.path.strip("/").split("/", 1)[0]
        if candidate:
            return candidate
    raise CaptureError(f"unsupported YouTube URL: {url}")


def youtube_source_identity(url: str, fallback_slug: str = "") -> tuple[str, str]:
    try:
        video_id = extract_video_id(url)
    except CaptureError:
        if fallback_slug:
            return "", f"youtube-channel:{fallback_slug}"
        raise
    return video_id, f"youtube:{video_id}"


def normalize_row(
    *,
    capture_date: str,
    url: str,
    title: str = "",
    channel: str = "",
    published_at: str = "",
    expected_voice: str = "unknown",
    transcript_status: str = "defer",
    disposition: str = "watch",
    next_action: str = "review",
    notes: str = "",
) -> dict[str, str]:
    if transcript_status not in TRANSCRIPT_STATUSES:
        raise CaptureError(f"invalid transcript status: {transcript_status}")
    if disposition not in DISPOSITIONS:
        raise CaptureError(f"invalid disposition: {disposition}")
    video_id, source_identity = youtube_source_identity(url)
    return {
        "date": capture_date,
        "url": url.strip(),
        "video_id": video_id,
        "title": title.strip(),
        "channel": channel.strip(),
        "published_at": published_at.strip(),
        "expected_voice": expected_voice.strip() or "unknown",
        "transcript_status": transcript_status,
        "disposition": disposition,
        "next_action": next_action.strip() or "review",
        "notes": notes.strip(),
        "source_identity": source_identity,
    }


def normalize_index_row(*, capture_date: str, row: dict[str, str]) -> dict[str, str]:
    url = row["channel_url"]
    slug = row["slug"]
    video_id, source_identity = youtube_source_identity(url, slug)
    cadence = row.get("capture_cadence", "")
    status = row.get("status", "")
    return {
        "date": capture_date,
        "url": url,
        "video_id": video_id,
        "title": "",
        "channel": row.get("label", ""),
        "published_at": "",
        "expected_voice": CHANNEL_EXPECTED_VOICE.get(slug, "unknown"),
        "transcript_status": "defer",
        "disposition": "watch",
        "next_action": "open public channel and add substantive new video URLs",
        "notes": f"scan-index cadence={cadence}; narrative_status={status}; channel_slug={slug}",
        "source_identity": source_identity,
    }


def normalize_discovered_video_row(
    *,
    capture_date: str,
    channel_row: dict[str, str],
    video: dict[str, str],
) -> dict[str, str]:
    url = video["url"]
    video_id, source_identity = youtube_source_identity(url)
    slug = channel_row["slug"]
    cadence = channel_row.get("capture_cadence", "")
    return {
        "date": capture_date,
        "url": url,
        "video_id": video_id,
        "title": video.get("title", ""),
        "channel": video.get("channel") or channel_row.get("label", ""),
        "published_at": video.get("published_at", ""),
        "expected_voice": CHANNEL_EXPECTED_VOICE.get(slug, "unknown"),
        "transcript_status": "defer",
        "disposition": "watch",
        "next_action": "review video and mark must-land/possible/skip",
        "notes": f"discover-public cadence={cadence}; channel_slug={slug}",
        "source_identity": source_identity,
    }


def read_queue(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise CaptureError(f"invalid JSONL at {path}:{line_number}") from error
        if not isinstance(row, dict):
            raise CaptureError(f"queue row must be an object at {path}:{line_number}")
        rows.append({str(key): str(value) for key, value in row.items()})
    return rows


def write_queue(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8", newline="\n")


def load_manifest_by_url(path: Path = MANIFEST_PATH) -> dict[str, dict[str, object]]:
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    sources = manifest.get("sources", [])
    if not isinstance(sources, list):
        raise CaptureError("manifest sources must be a list")
    by_url: dict[str, dict[str, object]] = {}
    for source in sources:
        if not isinstance(source, dict):
            continue
        url = source.get("source_url")
        if isinstance(url, str) and url:
            by_url[url] = source
    return by_url


def audit_queue_duplicates(
    *,
    dates: list[str],
    queue_root: Path = QUEUE_ROOT,
    manifest_path: Path = MANIFEST_PATH,
    dispositions: set[str] | None = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    manifest = load_manifest_by_url(manifest_path)
    seen: dict[str, dict[str, object]] = {}
    for capture_date in dates:
        for row in read_queue(queue_path(capture_date, queue_root)):
            if dispositions and row.get("disposition") not in dispositions:
                continue
            url = row.get("url", "")
            if not url or row.get("source_identity", "").startswith("youtube-channel:"):
                continue
            item = seen.setdefault(
                url,
                {
                    "queue_dates": [],
                    "disposition": row.get("disposition", ""),
                    "title": row.get("title", ""),
                    "channel": row.get("channel", ""),
                    "url": url,
                },
            )
            queue_dates = item["queue_dates"]
            if isinstance(queue_dates, list):
                queue_dates.append(capture_date)

    landed: list[dict[str, object]] = []
    not_found: list[dict[str, object]] = []
    for url, row in sorted(seen.items(), key=lambda item: str(item[1].get("title", "")).casefold()):
        queue_dates = row.get("queue_dates", [])
        if isinstance(queue_dates, list):
            row["queue_dates"] = sorted(set(str(item) for item in queue_dates))
        source = manifest.get(url)
        if source:
            landed.append(
                {
                    **row,
                    "archive_date": source.get("date", ""),
                    "archive_title": source.get("title", ""),
                    "host_slug": source.get("host_slug", ""),
                    "voice_slugs": source.get("voice_slugs", []),
                    "local_path": source.get("local_path", ""),
                }
            )
        else:
            not_found.append(row)
    return landed, not_found


def published_in_window(row: dict[str, str], *, capture_date: str, since_days: int) -> bool:
    published = parse_rss_datetime(row.get("published_at", ""))
    if published is None:
        return True
    capture_day = date.fromisoformat(capture_date)
    start = datetime.combine(capture_day - timedelta(days=since_days), time.min, tzinfo=timezone.utc)
    end = datetime.combine(capture_day, time.max, tzinfo=timezone.utc)
    return start <= published <= end


def prune_queue_rows(
    *,
    capture_date: str,
    queue_root: Path = QUEUE_ROOT,
    manifest_path: Path = MANIFEST_PATH,
    remove_landed: bool = False,
    discovery_since_days: int | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    manifest = load_manifest_by_url(manifest_path)
    kept: list[dict[str, str]] = []
    removed: list[dict[str, str]] = []
    for row in read_queue(queue_path(capture_date, queue_root)):
        url = row.get("url", "")
        source_identity = row.get("source_identity", "")
        is_video = source_identity.startswith("youtube:")
        is_discovered = "discover-public" in row.get("notes", "")
        landed = bool(url and manifest.get(url))
        stale = (
            discovery_since_days is not None
            and is_discovered
            and not published_in_window(row, capture_date=capture_date, since_days=discovery_since_days)
        )
        if is_video and ((remove_landed and landed) or stale):
            removed.append(row)
        else:
            kept.append(row)
    return kept, removed


def upsert_rows(existing: list[dict[str, str]], incoming: list[dict[str, str]]) -> tuple[list[dict[str, str]], int, int]:
    rows = list(existing)
    index = {row.get("source_identity", ""): position for position, row in enumerate(rows)}
    added = 0
    updated = 0
    for row in incoming:
        identity = row["source_identity"]
        if identity in index:
            merged = dict(rows[index[identity]])
            merged.update({key: value for key, value in row.items() if value != ""})
            rows[index[identity]] = merged
            updated += 1
        else:
            index[identity] = len(rows)
            rows.append(row)
            added += 1
    return rows, added, updated


def load_watchlist(path: Path) -> list[dict[str, str]]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        decoded = json.loads(raw)
        if isinstance(decoded, dict):
            items = decoded.get("items", [])
        else:
            items = decoded
        if not isinstance(items, list):
            raise CaptureError("watchlist JSON must be a list or contain an items list")
        rows: list[dict[str, str]] = []
        for item in items:
            if isinstance(item, str):
                rows.append({"url": item})
            elif isinstance(item, dict):
                rows.append({str(key): str(value) for key, value in item.items()})
            else:
                raise CaptureError("watchlist entries must be strings or objects")
        return rows
    return [{"url": line.strip()} for line in raw.splitlines() if line.strip() and not line.strip().startswith("#")]


def markdown_link_url(value: str) -> str:
    match = re.search(r"\]\(([^)]+)\)", value)
    return match.group(1) if match else value


def parse_channel_index(path: Path = CHANNEL_INDEX_PATH) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 11 or cells[0] == "Channel slug":
            continue
        slug = cells[0].strip("`")
        url = markdown_link_url(cells[8])
        if not url.startswith(("https://www.youtube.com/", "https://youtube.com/", "https://youtu.be/")):
            continue
        rows.append(
            {
                "slug": slug,
                "label": cells[1],
                "status": cells[2].strip("`"),
                "routing_role": cells[3],
                "capture_cadence": cells[7].strip("`").lower(),
                "channel_url": url,
            }
        )
    return rows


def select_channel_index_rows(
    rows: list[dict[str, str]],
    *,
    cadences: set[str],
    channels: set[str],
    include_active: bool,
    include_candidate: bool,
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in rows:
        slug = row["slug"]
        status = row["status"]
        cadence = row["capture_cadence"]
        if channels and slug not in channels:
            continue
        if not channels and cadence not in cadences:
            if not (include_active and status == "active") and not (include_candidate and status == "candidate"):
                continue
        selected.append(row)
    return selected


def fetch_text(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as error:
        raise CaptureError(f"public fetch failed for {url}: {error}") from error


def extract_channel_id(text: str) -> str:
    patterns = [
        r'"channelId":"(UC[^"]+)"',
        r'"externalId":"(UC[^"]+)"',
        r'<meta itemprop="channelId" content="(UC[^"]+)">',
        r'https://www\.youtube\.com/channel/(UC[0-9A-Za-z_-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    raise CaptureError("could not resolve public channel id")


def channel_id_from_url(url: str, fetcher=None) -> str:
    fetcher = fetch_text if fetcher is None else fetcher
    parsed = urlparse(url)
    match = re.match(r"^/channel/(UC[0-9A-Za-z_-]+)", parsed.path)
    if match:
        return match.group(1)
    return extract_channel_id(fetcher(url.rstrip("/") + "/videos"))


def parse_youtube_rss(text: str, *, limit: int) -> list[dict[str, str]]:
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as error:
        raise CaptureError("invalid YouTube RSS response") from error
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
    }
    videos: list[dict[str, str]] = []
    for entry in root.findall("atom:entry", ns):
        video_id = (entry.findtext("yt:videoId", default="", namespaces=ns) or "").strip()
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        published_at = (entry.findtext("atom:published", default="", namespaces=ns) or "").strip()
        channel = (entry.findtext("atom:author/atom:name", default="", namespaces=ns) or "").strip()
        link = entry.find("atom:link", ns)
        url = link.attrib.get("href", "") if link is not None else ""
        if not url and video_id:
            url = f"https://www.youtube.com/watch?v={video_id}"
        if not video_id or not url:
            continue
        videos.append(
            {
                "video_id": video_id,
                "url": url,
                "title": title,
                "published_at": published_at,
                "channel": channel,
            }
        )
        if len(videos) >= limit:
            break
    return videos


def parse_rss_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def filter_videos_since(
    videos: list[dict[str, str]],
    *,
    capture_date: str,
    since_days: int | None,
) -> list[dict[str, str]]:
    if since_days is None:
        return videos
    capture_day = date.fromisoformat(capture_date)
    start = datetime.combine(capture_day - timedelta(days=since_days), time.min, tzinfo=timezone.utc)
    end = datetime.combine(capture_day, time.max, tzinfo=timezone.utc)
    filtered: list[dict[str, str]] = []
    for video in videos:
        published = parse_rss_datetime(video.get("published_at", ""))
        if published is not None and start <= published <= end:
            filtered.append(video)
    return filtered


def discover_public_videos(row: dict[str, str], *, limit: int, fetcher=None) -> list[dict[str, str]]:
    fetcher = fetch_text if fetcher is None else fetcher
    channel_id = channel_id_from_url(row["channel_url"], fetcher=fetcher)
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    return parse_youtube_rss(fetcher(rss_url), limit=limit)


def add_command(args: argparse.Namespace) -> int:
    path = queue_path(args.date, args.queue_root)
    row = normalize_row(
        capture_date=args.date,
        url=args.url,
        title=args.title,
        channel=args.channel,
        published_at=args.published_at,
        expected_voice=args.expected_voice,
        transcript_status=args.transcript_status,
        disposition=args.disposition,
        next_action=args.next_action,
        notes=args.notes,
    )
    rows, added, updated = upsert_rows(read_queue(path), [row])
    write_queue(path, rows)
    print(QUEUE_ONLY_NOTICE)
    print(f"QUEUE_PATH={path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else path}")
    print(f"ROWS_ADDED={added}")
    print(f"ROWS_UPDATED={updated}")
    print(AUTHORITY_NOTICE)
    return 0


def scan_command(args: argparse.Namespace) -> int:
    path = queue_path(args.date, args.queue_root)
    incoming = []
    for item in load_watchlist(args.watchlist):
        if not item.get("url"):
            raise CaptureError("watchlist entry missing url")
        incoming.append(
            normalize_row(
                capture_date=args.date,
                url=item["url"],
                title=item.get("title", ""),
                channel=item.get("channel", ""),
                published_at=item.get("published_at", ""),
                expected_voice=item.get("expected_voice", "unknown"),
                transcript_status=item.get("transcript_status", "defer"),
                disposition=item.get("disposition", "watch"),
                next_action=item.get("next_action", "review"),
                notes=item.get("notes", ""),
            )
        )
    rows, added, updated = upsert_rows(read_queue(path), incoming)
    write_queue(path, rows)
    print(QUEUE_ONLY_NOTICE)
    print(f"QUEUE_PATH={path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else path}")
    print(f"ROWS_ADDED={added}")
    print(f"ROWS_UPDATED={updated}")
    print(AUTHORITY_NOTICE)
    return 0


def scan_index_command(args: argparse.Namespace) -> int:
    path = queue_path(args.date, args.queue_root)
    cadences = {item.lower() for item in (args.cadence or ["daily"])}
    channels = {item.strip() for item in args.channel}
    source_rows = parse_channel_index(args.channel_index)
    selected = select_channel_index_rows(
        source_rows,
        cadences=cadences,
        channels=channels,
        include_active=args.include_active,
        include_candidate=args.include_candidate,
    )
    incoming = [normalize_index_row(capture_date=args.date, row=row) for row in selected]
    rows, added, updated = upsert_rows(read_queue(path), incoming)
    write_queue(path, rows)
    print(QUEUE_ONLY_NOTICE)
    print("SCAN_INDEX_MODE=public-channel-checks-only")
    print(f"CHANNEL_INDEX={args.channel_index}")
    print(f"CHANNEL_ROWS_SELECTED={len(selected)}")
    print(f"ROWS_ADDED={added}")
    print(f"ROWS_UPDATED={updated}")
    print(AUTHORITY_NOTICE)
    return 0


def discover_public_command(args: argparse.Namespace) -> int:
    path = queue_path(args.date, args.queue_root)
    cadences = {item.lower() for item in (args.cadence or ["daily"])}
    channels = {item.strip() for item in args.channel}
    source_rows = parse_channel_index(args.channel_index)
    selected = select_channel_index_rows(
        source_rows,
        cadences=cadences,
        channels=channels,
        include_active=args.include_active,
        include_candidate=args.include_candidate,
    )
    incoming: list[dict[str, str]] = []
    videos_found = 0
    failures = 0
    for row in selected:
        try:
            videos = filter_videos_since(
                discover_public_videos(row, limit=args.limit_per_channel),
                capture_date=args.date,
                since_days=args.since_days,
            )
        except CaptureError as error:
            fallback = normalize_index_row(capture_date=args.date, row=row)
            fallback["notes"] = f"{fallback['notes']}; discover-public failed: {error}"
            incoming.append(fallback)
            failures += 1
            continue
        if not videos:
            fallback = normalize_index_row(capture_date=args.date, row=row)
            fallback["notes"] = f"{fallback['notes']}; discover-public found no public videos"
            incoming.append(fallback)
            failures += 1
            continue
        videos_found += len(videos)
        incoming.extend(
            normalize_discovered_video_row(capture_date=args.date, channel_row=row, video=video)
            for video in videos
        )
    rows, added, updated = upsert_rows(read_queue(path), incoming)
    write_queue(path, rows)
    print(QUEUE_ONLY_NOTICE)
    print("DISCOVER_PUBLIC_MODE=public-metadata-only")
    print(f"CHANNEL_INDEX={args.channel_index}")
    print(f"CHANNEL_ROWS_SELECTED={len(selected)}")
    print(f"VIDEOS_FOUND={videos_found}")
    print(f"SINCE_DAYS={args.since_days if args.since_days is not None else 'none'}")
    print(f"DISCOVERY_FAILURES={failures}")
    print(f"ROWS_ADDED={added}")
    print(f"ROWS_UPDATED={updated}")
    print(AUTHORITY_NOTICE)
    return 0


def list_command(args: argparse.Namespace) -> int:
    rows = read_queue(queue_path(args.date, args.queue_root))
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0
    print("| Date | URL | Source / Channel | Expected Voice | Transcript Status | Priority | Next Action | Notes |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        print(
            "| "
            + " | ".join(
                [
                    row.get("date", ""),
                    row.get("url", ""),
                    row.get("channel", ""),
                    row.get("expected_voice", ""),
                    row.get("transcript_status", ""),
                    row.get("disposition", ""),
                    row.get("next_action", ""),
                    row.get("notes", ""),
                ]
            )
            + " |"
        )
    return 0


def mark_command(args: argparse.Namespace) -> int:
    path = queue_path(args.date, args.queue_root)
    identity = f"youtube:{extract_video_id(args.url)}"
    rows = read_queue(path)
    for row in rows:
        if row.get("source_identity") != identity:
            continue
        if args.transcript_status:
            row["transcript_status"] = args.transcript_status
        if args.disposition:
            row["disposition"] = args.disposition
        if args.next_action:
            row["next_action"] = args.next_action
        if args.notes:
            row["notes"] = args.notes
        write_queue(path, rows)
        print(QUEUE_ONLY_NOTICE)
        print(f"ROWS_MARKED=1")
        print(AUTHORITY_NOTICE)
        return 0
    raise CaptureError(f"URL not found in queue for {args.date}: {args.url}")


def export_intake_command(args: argparse.Namespace) -> int:
    rows = read_queue(queue_path(args.date, args.queue_root))
    candidates = [row for row in rows if row.get("disposition") == "must-land"]
    print(QUEUE_ONLY_NOTICE)
    print("EXPORT_MODE=dry-run-suggestions-only")
    for row in candidates:
        print(
            ".\\tools\\run.ps1 intake-land --no-confidence-gate --dry-run "
            f"--url {json.dumps(row.get('url', ''))} "
            f"--pub-date {json.dumps(row.get('published_at') or row.get('date', ''))} "
            "--body-file <operator-provided-transcript-path>"
        )
    print(f"INTAKE_SUGGESTIONS={len(candidates)}")
    print(AUTHORITY_NOTICE)
    return 0


def audit_duplicates_command(args: argparse.Namespace) -> int:
    dispositions = set(args.disposition) if args.disposition else None
    landed, not_found = audit_queue_duplicates(
        dates=args.date,
        queue_root=args.queue_root,
        manifest_path=args.manifest,
        dispositions=dispositions,
    )
    if args.json:
        print(
            json.dumps(
                {
                    "already_landed": landed,
                    "not_found": not_found,
                    "already_landed_count": len(landed),
                    "not_found_count": len(not_found),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(QUEUE_ONLY_NOTICE)
        print("AUDIT_MODE=read-only-queue-url-match-against-manifest")
        print(f"QUEUE_ROWS_ALREADY_LANDED={len(landed)}")
        print(f"QUEUE_ROWS_NOT_FOUND_IN_MANIFEST={len(not_found)}")
        for row in landed:
            print(
                "QUEUE_ROW_ALREADY_LANDED "
                f"queue_dates={','.join(row.get('queue_dates', []))} "
                f"archive_date={row.get('archive_date', '')} "
                f"url={row.get('url', '')} "
                f"title={row.get('title', '')}"
            )
        print(AUTHORITY_NOTICE)
    return 0


def prune_queue_command(args: argparse.Namespace) -> int:
    total_removed: list[dict[str, str]] = []
    for capture_date in args.date:
        kept, removed = prune_queue_rows(
            capture_date=capture_date,
            queue_root=args.queue_root,
            manifest_path=args.manifest,
            remove_landed=args.remove_landed,
            discovery_since_days=args.discovery_since_days,
        )
        write_queue(queue_path(capture_date, args.queue_root), kept)
        total_removed.extend({"date": capture_date, **row} for row in removed)
    if args.json:
        print(json.dumps({"removed": total_removed, "removed_count": len(total_removed)}, indent=2, ensure_ascii=False))
    else:
        print(QUEUE_ONLY_NOTICE)
        print("PRUNE_MODE=queue-only")
        print(f"REMOVE_LANDED={bool(args.remove_landed)}")
        print(f"DISCOVERY_SINCE_DAYS={args.discovery_since_days if args.discovery_since_days is not None else 'none'}")
        print(f"ROWS_REMOVED={len(total_removed)}")
        for row in total_removed:
            print(f"REMOVED date={row.get('date', '')} url={row.get('url', '')} title={row.get('title', '')}")
        print(AUTHORITY_NOTICE)
    return 0


def attach_transcript_to_queue(
    *,
    capture_date: str,
    url: str,
    transcript_file: Path,
    queue_root: Path = QUEUE_ROOT,
    notes: str = "",
) -> dict[str, str]:
    if not transcript_file.exists() or not transcript_file.is_file():
        raise CaptureError(f"transcript file not found: {transcript_file}")
    if transcript_file.stat().st_size == 0:
        raise CaptureError(f"transcript file is empty: {transcript_file}")

    path = queue_path(capture_date, queue_root)
    identity = f"youtube:{extract_video_id(url)}"
    rows = read_queue(path)
    for row in rows:
        if row.get("source_identity") != identity:
            continue
        row["transcript_status"] = "available"
        row["transcript_path"] = str(transcript_file)
        row["next_action"] = "route transcript file through governed intake"
        extra_note = "browser-panel transcript captured for governed intake"
        if notes:
            extra_note = f"{extra_note}; {notes}"
        existing_notes = row.get("notes", "")
        row["notes"] = f"{existing_notes}; {extra_note}" if existing_notes else extra_note
        write_queue(path, rows)
        return row
    raise CaptureError(f"URL not found in queue for {capture_date}: {url}")


def browser_triage_command(args: argparse.Namespace) -> int:
    rows = read_queue(queue_path(args.date, args.queue_root))
    candidates = [
        row
        for row in rows
        if row.get("source_identity", "").startswith("youtube:")
        and (not args.disposition or row.get("disposition") in set(args.disposition))
        and (args.include_resolved or row.get("transcript_status", "defer") == "defer")
    ]
    if args.json:
        print(
            json.dumps(
                {
                    "mode": "browser-triage-stub",
                    "date": args.date,
                    "candidates": candidates,
                    "candidate_count": len(candidates),
                    "allowed_queue_fields": [
                        "title",
                        "channel",
                        "published_at",
                        "transcript_status",
                        "next_action",
                        "notes",
                    ],
                    "transcript_statuses": sorted(TRANSCRIPT_STATUSES),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(QUEUE_ONLY_NOTICE)
        print("BROWSER_TRIAGE_MODE=manual-browser-observation-stub")
        print(f"TRIAGE_DATE={args.date}")
        print(f"TRIAGE_CANDIDATES={len(candidates)}")
        print("ALLOWED_QUEUE_FIELDS=title,channel,published_at,transcript_status,next_action,notes")
        print("TRANSCRIPT_STATUS_RULES=available|manual-needed|missing|defer")
        print("EXPORTER_FAILURE_RULE=manual-needed unless page observation proves transcript is absent")
        print("HIDDEN_TRANSCRIPT_UI_RULE=manual-needed when transcript controls exist but are hidden or not interactable")
        print(
            "| URL | Channel | Current Transcript | Disposition | Browser Observation Needed | Allowed Queue Update |"
        )
        print("| --- | --- | --- | --- | --- | --- |")
        for row in candidates:
            print(
                "| "
                + " | ".join(
                    [
                        row.get("url", ""),
                        row.get("channel", ""),
                        row.get("transcript_status", ""),
                        row.get("disposition", ""),
                        "title/channel/date/transcript surface; distinguish hidden UI/exporter failure from source absence",
                        "metadata and transcript_status only; exporter failure or hidden transcript UI -> manual-needed",
                    ]
                )
                + " |"
            )
        print(AUTHORITY_NOTICE)
    return 0


def attach_transcript_command(args: argparse.Namespace) -> int:
    row = attach_transcript_to_queue(
        capture_date=args.date,
        url=args.url,
        transcript_file=args.transcript_file,
        queue_root=args.queue_root,
        notes=args.notes,
    )
    print(QUEUE_ONLY_NOTICE)
    print("ATTACH_TRANSCRIPT_MODE=queue-metadata-only")
    print(f"URL={row.get('url', '')}")
    print(f"TRANSCRIPT_STATUS={row.get('transcript_status', '')}")
    print(f"TRANSCRIPT_PATH={row.get('transcript_path', '')}")
    print(AUTHORITY_NOTICE)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Queue-only YouTube source capture")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(row_parser: argparse.ArgumentParser) -> None:
        row_parser.add_argument("--date", required=True, type=parse_capture_date)
        row_parser.add_argument("--queue-root", type=Path, default=QUEUE_ROOT, help=argparse.SUPPRESS)

    add = subparsers.add_parser("add", help="Add or update one queue row")
    add_common(add)
    add.add_argument("--url", required=True)
    add.add_argument("--title", default="")
    add.add_argument("--channel", default="")
    add.add_argument("--published-at", default="")
    add.add_argument("--expected-voice", default="unknown")
    add.add_argument("--transcript-status", choices=sorted(TRANSCRIPT_STATUSES), default="defer")
    add.add_argument("--disposition", choices=sorted(DISPOSITIONS), default="watch")
    add.add_argument("--next-action", default="review")
    add.add_argument("--notes", default="")
    add.set_defaults(handler=add_command)

    scan = subparsers.add_parser("scan", help="Import draft queue rows from a watchlist file")
    add_common(scan)
    scan.add_argument("--watchlist", type=Path, required=True)
    scan.set_defaults(handler=scan_command)

    scan_index = subparsers.add_parser("scan-index", help="Create channel-check rows from the channel index")
    add_common(scan_index)
    scan_index.add_argument("--channel-index", type=Path, default=CHANNEL_INDEX_PATH)
    scan_index.add_argument("--cadence", action="append", choices=["daily", "weekly", "manual", "off"])
    scan_index.add_argument("--channel", action="append", default=[])
    scan_index.add_argument("--include-active", action="store_true")
    scan_index.add_argument("--include-candidate", action="store_true")
    scan_index.set_defaults(handler=scan_index_command)

    discover = subparsers.add_parser("discover-public", help="Discover public video rows from channel-index URLs")
    add_common(discover)
    discover.add_argument("--channel-index", type=Path, default=CHANNEL_INDEX_PATH)
    discover.add_argument("--cadence", action="append", choices=["daily", "weekly", "manual", "off"])
    discover.add_argument("--channel", action="append", default=[])
    discover.add_argument("--include-active", action="store_true")
    discover.add_argument("--include-candidate", action="store_true")
    discover.add_argument("--limit-per-channel", type=int, default=5)
    discover.add_argument("--since-days", type=parse_nonnegative_int)
    discover.set_defaults(handler=discover_public_command)

    list_rows = subparsers.add_parser("list", help="List queue rows for a date")
    add_common(list_rows)
    list_rows.add_argument("--json", action="store_true")
    list_rows.set_defaults(handler=list_command)

    mark = subparsers.add_parser("mark", help="Update review fields for one queued URL")
    add_common(mark)
    mark.add_argument("--url", required=True)
    mark.add_argument("--transcript-status", choices=sorted(TRANSCRIPT_STATUSES))
    mark.add_argument("--disposition", choices=sorted(DISPOSITIONS))
    mark.add_argument("--next-action")
    mark.add_argument("--notes")
    mark.set_defaults(handler=mark_command)

    export = subparsers.add_parser("export-intake", help="Print intake dry-run suggestions for must-land rows")
    add_common(export)
    export.set_defaults(handler=export_intake_command)

    audit = subparsers.add_parser("audit-duplicates", help="Read-only URL match of queue rows against the source manifest")
    audit.add_argument("--date", action="append", required=True, type=parse_capture_date)
    audit.add_argument("--queue-root", type=Path, default=QUEUE_ROOT, help=argparse.SUPPRESS)
    audit.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    audit.add_argument("--disposition", action="append", choices=sorted(DISPOSITIONS))
    audit.add_argument("--json", action="store_true")
    audit.set_defaults(handler=audit_duplicates_command)

    prune = subparsers.add_parser("prune-queue", help="Remove queue-only duplicate or stale discovered video rows")
    prune.add_argument("--date", action="append", required=True, type=parse_capture_date)
    prune.add_argument("--queue-root", type=Path, default=QUEUE_ROOT, help=argparse.SUPPRESS)
    prune.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    prune.add_argument("--remove-landed", action="store_true")
    prune.add_argument("--discovery-since-days", type=parse_nonnegative_int)
    prune.add_argument("--json", action="store_true")
    prune.set_defaults(handler=prune_queue_command)

    triage = subparsers.add_parser("browser-triage", help="Print queue-only browser triage checklist")
    add_common(triage)
    triage.add_argument("--disposition", action="append", choices=sorted(DISPOSITIONS))
    triage.add_argument("--include-resolved", action="store_true")
    triage.add_argument("--json", action="store_true")
    triage.set_defaults(handler=browser_triage_command)

    attach = subparsers.add_parser("attach-transcript", help="Attach a browser-panel transcript file to one queue row")
    add_common(attach)
    attach.add_argument("--url", required=True)
    attach.add_argument("--transcript-file", type=Path, required=True)
    attach.add_argument("--notes", default="")
    attach.set_defaults(handler=attach_transcript_command)
    return parser


def main(arguments: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(arguments)
    try:
        return int(args.handler(args))
    except (CaptureError, OSError, json.JSONDecodeError) as error:
        print(f"youtube-capture error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


youtube_capture = load_module("youtube_capture_tests", SCRIPTS_ROOT / "youtube_capture.py")


def read_jsonl(path: Path) -> list[dict[str, str]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_add_creates_queue_only_row(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"

    result = youtube_capture.main(
        [
            "add",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--url",
            "https://www.youtube.com/watch?v=abc123",
            "--title",
            "Daily update",
            "--channel",
            "Example Channel",
            "--expected-voice",
            "example",
            "--transcript-status",
            "available",
            "--disposition",
            "must-land",
        ]
    )

    assert result == 0
    rows = read_jsonl(queue_root / "2026-08-20.jsonl")
    assert rows == [
        {
            "channel": "Example Channel",
            "date": "2026-08-20",
            "disposition": "must-land",
            "expected_voice": "example",
            "next_action": "review",
            "notes": "",
            "published_at": "",
            "source_identity": "youtube:abc123",
            "title": "Daily update",
            "transcript_status": "available",
            "url": "https://www.youtube.com/watch?v=abc123",
            "video_id": "abc123",
        }
    ]
    output = capsys.readouterr().out
    assert "YOUTUBE_CAPTURE_MODE=queue-draft-only" in output
    assert "no archive landing" in output


def test_add_is_idempotent_by_source_identity(tmp_path: Path) -> None:
    queue_root = tmp_path / "queue"
    base = [
        "add",
        "--date",
        "2026-08-20",
        "--queue-root",
        str(queue_root),
        "--url",
        "https://youtu.be/abc123",
    ]

    assert youtube_capture.main([*base, "--title", "First"]) == 0
    assert youtube_capture.main([*base, "--title", "Second", "--channel", "Updated"]) == 0

    rows = read_jsonl(queue_root / "2026-08-20.jsonl")
    assert len(rows) == 1
    assert rows[0]["title"] == "Second"
    assert rows[0]["channel"] == "Updated"
    assert rows[0]["source_identity"] == "youtube:abc123"


def test_scan_imports_watchlist_without_fetching_transcripts(tmp_path: Path) -> None:
    queue_root = tmp_path / "queue"
    watchlist = tmp_path / "watchlist.json"
    watchlist.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "url": "https://www.youtube.com/shorts/short123",
                        "channel": "Shorts Channel",
                        "expected_voice": "unknown",
                    },
                    "https://www.youtube.com/live/live123",
                ]
            }
        ),
        encoding="utf-8",
    )

    assert youtube_capture.main(["scan", "--date", "2026-08-20", "--queue-root", str(queue_root), "--watchlist", str(watchlist)]) == 0

    rows = read_jsonl(queue_root / "2026-08-20.jsonl")
    assert [row["source_identity"] for row in rows] == ["youtube:short123", "youtube:live123"]
    assert {row["transcript_status"] for row in rows} == {"defer"}
    assert {row["disposition"] for row in rows} == {"watch"}


def test_scan_index_defaults_to_daily_channel_checks(tmp_path: Path) -> None:
    queue_root = tmp_path / "queue"
    channel_index = tmp_path / "channel-index.md"
    channel_index.write_text(
        "\n".join(
            [
                "| Channel slug | Label | Narrative status | Routing role | Local shelf / required next step | Upstream files | Upstream days | Capture cadence | Channel URL | First day | Last day |",
                "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
                "| `alexander-mercouris` | Alexander Mercouris | `watchlist` | Solo analyst channel. | Create lightweight shelf before synthesis. | 333 | 331 | `daily` | [open](https://www.youtube.com/@AlexMercouris) | `2025-01-03` | `2026-06-27` |",
                "| `redacted-news` | Redacted News | `active` | Crisis-media register. | [redacted-news/](redacted-news/README.md) | 5 | 4 | `weekly` | [open](https://www.youtube.com/@RedactedNews) | `2026-04-20` | `2026-06-16` |",
                "| `tucker-carlson` | Tucker Carlson | `candidate` | Long-form elite interview frame. | Create lightweight shelf before synthesis. | 7 | 7 | `manual` | [open](https://www.youtube.com/@TuckerCarlson) | `2025-03-11` | `2026-06-24` |",
            ]
        ),
        encoding="utf-8",
    )

    result = youtube_capture.main(
        [
            "scan-index",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--channel-index",
            str(channel_index),
        ]
    )

    assert result == 0
    rows = read_jsonl(queue_root / "2026-08-20.jsonl")
    assert len(rows) == 1
    assert rows[0]["source_identity"] == "youtube-channel:alexander-mercouris"
    assert rows[0]["url"] == "https://www.youtube.com/@AlexMercouris"
    assert rows[0]["channel"] == "Alexander Mercouris"
    assert rows[0]["expected_voice"] == "mercouris"
    assert rows[0]["next_action"] == "open public channel and add substantive new video URLs"
    assert "cadence=daily" in rows[0]["notes"]


def test_scan_index_can_select_weekly_and_explicit_channels(tmp_path: Path) -> None:
    queue_root = tmp_path / "queue"
    channel_index = tmp_path / "channel-index.md"
    channel_index.write_text(
        "\n".join(
            [
                "| Channel slug | Label | Narrative status | Routing role | Local shelf / required next step | Upstream files | Upstream days | Capture cadence | Channel URL | First day | Last day |",
                "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
                "| `mario-nawfal` | Mario Nawfal | `active` | Breaking-headline frame. | [mario-nawfal/](mario-nawfal/README.md) | 60 | 38 | `daily` | [open](https://www.youtube.com/channel/UCTWBp-39z6tvz4-LQB-Z_QA) | `2026-05-12` | `2026-07-14` |",
                "| `redacted-news` | Redacted News | `active` | Crisis-media register. | [redacted-news/](redacted-news/README.md) | 5 | 4 | `weekly` | [open](https://www.youtube.com/@RedactedNews) | `2026-04-20` | `2026-06-16` |",
            ]
        ),
        encoding="utf-8",
    )

    assert (
        youtube_capture.main(
            [
                "scan-index",
                "--date",
                "2026-08-20",
                "--queue-root",
                str(queue_root),
                "--channel-index",
                str(channel_index),
                "--cadence",
                "weekly",
            ]
        )
        == 0
    )
    rows = read_jsonl(queue_root / "2026-08-20.jsonl")
    assert [row["source_identity"] for row in rows] == ["youtube-channel:redacted-news"]
    assert rows[0]["expected_voice"] == "unknown"

    assert (
        youtube_capture.main(
            [
                "scan-index",
                "--date",
                "2026-08-20",
                "--queue-root",
                str(queue_root),
                "--channel-index",
                str(channel_index),
                "--channel",
                "mario-nawfal",
            ]
        )
        == 0
    )
    rows = read_jsonl(queue_root / "2026-08-20.jsonl")
    assert {row["source_identity"] for row in rows} == {
        "youtube-channel:mario-nawfal",
        "youtube-channel:redacted-news",
    }


def test_parse_youtube_rss_extracts_recent_video_metadata() -> None:
    rss = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
  <entry>
    <yt:videoId>video123</yt:videoId>
    <title>First public video</title>
    <published>2026-08-20T10:00:00+00:00</published>
    <author><name>Example Channel</name></author>
    <link rel="alternate" href="https://www.youtube.com/watch?v=video123" />
  </entry>
  <entry>
    <yt:videoId>video456</yt:videoId>
    <title>Second public video</title>
    <published>2026-08-19T10:00:00+00:00</published>
    <author><name>Example Channel</name></author>
    <link rel="alternate" href="https://www.youtube.com/watch?v=video456" />
  </entry>
</feed>
"""

    videos = youtube_capture.parse_youtube_rss(rss, limit=1)

    assert videos == [
        {
            "video_id": "video123",
            "url": "https://www.youtube.com/watch?v=video123",
            "title": "First public video",
            "published_at": "2026-08-20T10:00:00+00:00",
            "channel": "Example Channel",
        }
    ]


def test_filter_videos_since_uses_capture_date_window() -> None:
    videos = [
        {"video_id": "old", "published_at": "2026-08-17T23:59:59+00:00"},
        {"video_id": "inside", "published_at": "2026-08-19T12:00:00+00:00"},
        {"video_id": "future", "published_at": "2026-08-21T00:00:00+00:00"},
        {"video_id": "unknown", "published_at": ""},
    ]

    filtered = youtube_capture.filter_videos_since(
        videos,
        capture_date="2026-08-20",
        since_days=1,
    )

    assert [video["video_id"] for video in filtered] == ["inside"]
    assert youtube_capture.filter_videos_since(
        videos,
        capture_date="2026-08-20",
        since_days=None,
    ) == videos


def test_discover_public_writes_video_rows_from_public_rss(tmp_path: Path, monkeypatch) -> None:
    queue_root = tmp_path / "queue"
    channel_index = tmp_path / "channel-index.md"
    channel_index.write_text(
        "\n".join(
            [
                "| Channel slug | Label | Narrative status | Routing role | Local shelf / required next step | Upstream files | Upstream days | Capture cadence | Channel URL | First day | Last day |",
                "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
                "| `glenn-diesen` | Glenn Diesen | `active` | Order-transition host frame. | [glenn-diesen/](glenn-diesen/README.md) | 241 | 192 | `daily` | [open](https://www.youtube.com/@GDiesen1) | `2023-01-14` | `2026-07-14` |",
            ]
        ),
        encoding="utf-8",
    )
    channel_page = '{"channelId":"UCabc123"}'
    rss = """<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
  <entry>
    <yt:videoId>video123</yt:videoId>
    <title>Public metadata only</title>
    <published>2026-08-20T10:00:00+00:00</published>
    <author><name>Glenn Diesen</name></author>
    <link rel="alternate" href="https://www.youtube.com/watch?v=video123" />
  </entry>
  <entry>
    <yt:videoId>old123</yt:videoId>
    <title>Old public metadata</title>
    <published>2026-08-10T10:00:00+00:00</published>
    <author><name>Glenn Diesen</name></author>
    <link rel="alternate" href="https://www.youtube.com/watch?v=old123" />
  </entry>
</feed>"""

    def fake_fetch(url: str, timeout: int = 20) -> str:
        assert timeout == 20
        if url.endswith("/videos"):
            return channel_page
        if "feeds/videos.xml" in url:
            return rss
        raise AssertionError(url)

    monkeypatch.setattr(youtube_capture, "fetch_text", fake_fetch)

    result = youtube_capture.main(
        [
            "discover-public",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--channel-index",
            str(channel_index),
            "--limit-per-channel",
            "2",
            "--since-days",
            "1",
        ]
    )

    assert result == 0
    rows = read_jsonl(queue_root / "2026-08-20.jsonl")
    assert rows == [
        {
            "channel": "Glenn Diesen",
            "date": "2026-08-20",
            "disposition": "watch",
            "expected_voice": "diesen",
            "next_action": "review video and mark must-land/possible/skip",
            "notes": "discover-public cadence=daily; channel_slug=glenn-diesen",
            "published_at": "2026-08-20T10:00:00+00:00",
            "source_identity": "youtube:video123",
            "title": "Public metadata only",
            "transcript_status": "defer",
            "url": "https://www.youtube.com/watch?v=video123",
            "video_id": "video123",
        }
    ]


def test_discover_public_falls_back_to_channel_check_on_failure(tmp_path: Path, monkeypatch) -> None:
    queue_root = tmp_path / "queue"
    channel_index = tmp_path / "channel-index.md"
    channel_index.write_text(
        "\n".join(
            [
                "| Channel slug | Label | Narrative status | Routing role | Local shelf / required next step | Upstream files | Upstream days | Capture cadence | Channel URL | First day | Last day |",
                "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
                "| `mario-nawfal` | Mario Nawfal | `active` | Breaking-headline frame. | [mario-nawfal/](mario-nawfal/README.md) | 60 | 38 | `daily` | [open](https://www.youtube.com/@MarioNawfal) | `2026-05-12` | `2026-07-14` |",
            ]
        ),
        encoding="utf-8",
    )

    def fake_fetch(url: str, timeout: int = 20) -> str:
        raise youtube_capture.CaptureError("network unavailable in test")

    monkeypatch.setattr(youtube_capture, "fetch_text", fake_fetch)

    assert (
        youtube_capture.main(
            [
                "discover-public",
                "--date",
                "2026-08-20",
                "--queue-root",
                str(queue_root),
                "--channel-index",
                str(channel_index),
            ]
        )
        == 0
    )
    row = read_jsonl(queue_root / "2026-08-20.jsonl")[0]
    assert row["source_identity"] == "youtube-channel:mario-nawfal"
    assert row["next_action"] == "open public channel and add substantive new video URLs"
    assert "discover-public failed: network unavailable in test" in row["notes"]


def test_audit_duplicates_matches_queue_urls_to_manifest(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    manifest = tmp_path / "source-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_url": "https://www.youtube.com/watch?v=landed123",
                        "title": "Already landed",
                        "date": "2026-08-19",
                        "host_slug": "glenn-diesen",
                        "voice_slugs": ["wilkerson"],
                        "local_path": "archive/sources/geopolitics/sources/2026-08-19/source-landed.md",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    queue = queue_root / "2026-08-20.jsonl"
    youtube_capture.write_queue(
        queue,
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=landed123",
                title="Already landed queue",
                channel="Glenn Diesen",
                disposition="must-land",
            ),
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=fresh123",
                title="Fresh queue",
                channel="Dialogue Works",
                disposition="must-land",
            ),
            youtube_capture.normalize_index_row(
                capture_date="2026-08-20",
                row={
                    "channel_url": "https://www.youtube.com/@Example",
                    "slug": "example",
                    "label": "Example",
                    "capture_cadence": "daily",
                    "status": "active",
                },
            ),
        ],
    )

    result = youtube_capture.main(
        [
            "audit-duplicates",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--manifest",
            str(manifest),
            "--disposition",
            "must-land",
            "--json",
        ]
    )

    assert result == 0
    output = json.loads(capsys.readouterr().out)
    assert output["already_landed_count"] == 1
    assert output["not_found_count"] == 1
    assert output["already_landed"][0]["url"] == "https://www.youtube.com/watch?v=landed123"
    assert output["already_landed"][0]["archive_date"] == "2026-08-19"
    assert output["not_found"][0]["url"] == "https://www.youtube.com/watch?v=fresh123"


def test_audit_duplicates_reports_compact_text(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    manifest = tmp_path / "source-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_url": "https://www.youtube.com/watch?v=landed123",
                        "title": "Already landed",
                        "date": "2026-08-19",
                        "local_path": "archive/source.md",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=landed123",
                title="Already landed queue",
                disposition="possible",
            )
        ],
    )

    assert (
        youtube_capture.main(
            [
                "audit-duplicates",
                "--date",
                "2026-08-20",
                "--queue-root",
                str(queue_root),
                "--manifest",
                str(manifest),
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "AUDIT_MODE=read-only-queue-url-match-against-manifest" in output
    assert "QUEUE_ROWS_ALREADY_LANDED=1" in output
    assert "QUEUE_ROWS_NOT_FOUND_IN_MANIFEST=0" in output
    assert "AUTHORITY_BOUNDARY=no archive landing" in output


def test_prune_queue_removes_landed_and_stale_discovered_rows(tmp_path: Path) -> None:
    queue_root = tmp_path / "queue"
    manifest = tmp_path / "source-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_url": "https://www.youtube.com/watch?v=landed123",
                        "title": "Already landed",
                        "date": "2026-08-19",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            {
                **youtube_capture.normalize_row(
                    capture_date="2026-08-20",
                    url="https://www.youtube.com/watch?v=landed123",
                    title="Already landed",
                ),
                "notes": "discover-public cadence=daily; channel_slug=glenn-diesen",
                "published_at": "2026-08-20T10:00:00+00:00",
            },
            {
                **youtube_capture.normalize_row(
                    capture_date="2026-08-20",
                    url="https://www.youtube.com/watch?v=old123",
                    title="Old discovered",
                ),
                "notes": "discover-public cadence=daily; channel_slug=glenn-diesen",
                "published_at": "2026-08-17T10:00:00+00:00",
            },
            {
                **youtube_capture.normalize_row(
                    capture_date="2026-08-20",
                    url="https://www.youtube.com/watch?v=fresh123",
                    title="Fresh discovered",
                ),
                "notes": "discover-public cadence=daily; channel_slug=glenn-diesen",
                "published_at": "2026-08-20T10:00:00+00:00",
            },
            youtube_capture.normalize_index_row(
                capture_date="2026-08-20",
                row={
                    "channel_url": "https://www.youtube.com/@Example",
                    "slug": "example",
                    "label": "Example",
                    "capture_cadence": "daily",
                    "status": "active",
                },
            ),
        ],
    )

    result = youtube_capture.main(
        [
            "prune-queue",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--manifest",
            str(manifest),
            "--remove-landed",
            "--discovery-since-days",
            "1",
        ]
    )

    assert result == 0
    rows = read_jsonl(queue_root / "2026-08-20.jsonl")
    assert {row["source_identity"] for row in rows} == {
        "youtube:fresh123",
        "youtube-channel:example",
    }


def test_prune_queue_json_reports_removed_rows(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    manifest = tmp_path / "source-manifest.json"
    manifest.write_text(json.dumps({"sources": []}), encoding="utf-8")
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            {
                **youtube_capture.normalize_row(
                    capture_date="2026-08-20",
                    url="https://www.youtube.com/watch?v=old123",
                    title="Old discovered",
                ),
                "notes": "discover-public cadence=daily; channel_slug=glenn-diesen",
                "published_at": "2026-08-17T10:00:00+00:00",
            }
        ],
    )

    assert (
        youtube_capture.main(
            [
                "prune-queue",
                "--date",
                "2026-08-20",
                "--queue-root",
                str(queue_root),
                "--manifest",
                str(manifest),
                "--discovery-since-days",
                "1",
                "--json",
            ]
        )
        == 0
    )
    output = json.loads(capsys.readouterr().out)
    assert output["removed_count"] == 1
    assert output["removed"][0]["title"] == "Old discovered"


def test_browser_triage_prints_queue_only_checklist(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=must123",
                channel="Must Channel",
                disposition="must-land",
            ),
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=watch123",
                channel="Watch Channel",
                disposition="watch",
            ),
            youtube_capture.normalize_index_row(
                capture_date="2026-08-20",
                row={
                    "channel_url": "https://www.youtube.com/@Example",
                    "slug": "example",
                    "label": "Example",
                    "capture_cadence": "daily",
                    "status": "active",
                },
            ),
        ],
    )

    result = youtube_capture.main(
        [
            "browser-triage",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--disposition",
            "must-land",
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert "BROWSER_TRIAGE_MODE=manual-browser-observation-stub" in output
    assert "TRIAGE_CANDIDATES=1" in output
    assert "EXPORTER_FAILURE_RULE=manual-needed unless page observation proves transcript is absent" in output
    assert "exporter failure or hidden transcript UI -> manual-needed" in output
    assert "HIDDEN_TRANSCRIPT_UI_RULE=manual-needed when transcript controls exist but are hidden or not interactable" in output
    assert "hidden transcript UI -> manual-needed" in output
    assert "must123" in output
    assert "watch123" not in output
    assert "youtube.com/@Example" not in output
    assert "ALLOWED_QUEUE_FIELDS=title,channel,published_at,transcript_status,next_action,notes" in output
    assert "no archive landing" in output


def test_browser_triage_json_can_include_resolved_rows(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=available123",
                transcript_status="available",
                disposition="must-land",
            ),
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=defer123",
                transcript_status="defer",
                disposition="possible",
            ),
        ],
    )

    assert (
        youtube_capture.main(
            [
                "browser-triage",
                "--date",
                "2026-08-20",
                "--queue-root",
                str(queue_root),
                "--include-resolved",
                "--json",
            ]
        )
        == 0
    )

    output = json.loads(capsys.readouterr().out)
    assert output["mode"] == "browser-triage-stub"
    assert output["candidate_count"] == 2
    assert {row["video_id"] for row in output["candidates"]} == {"available123", "defer123"}
    assert output["allowed_queue_fields"] == [
        "title",
        "channel",
        "published_at",
        "transcript_status",
        "next_action",
        "notes",
    ]


def test_attach_transcript_marks_queue_row_available(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    transcript_file = tmp_path / "transcript.txt"
    transcript_file.write_text("0:00 Opening line\n0:05 Second line\n", encoding="utf-8")
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=must123",
                transcript_status="manual-needed",
                disposition="must-land",
            )
        ],
    )

    result = youtube_capture.main(
        [
            "attach-transcript",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--url",
            "https://www.youtube.com/watch?v=must123",
            "--transcript-file",
            str(transcript_file),
            "--notes",
            "visible panel copied",
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert "ATTACH_TRANSCRIPT_MODE=queue-metadata-only" in output
    assert "TRANSCRIPT_STATUS=available" in output
    assert "no archive landing" in output
    row = read_jsonl(queue_root / "2026-08-20.jsonl")[0]
    assert row["transcript_status"] == "available"
    assert row["transcript_path"] == str(transcript_file)
    assert row["next_action"] == "route transcript file through governed intake"
    assert "browser-panel transcript captured for governed intake" in row["notes"]
    assert "visible panel copied" in row["notes"]


def test_attach_transcript_rejects_empty_file(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    transcript_file = tmp_path / "empty.txt"
    transcript_file.write_text("", encoding="utf-8")
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=must123",
                transcript_status="manual-needed",
                disposition="must-land",
            )
        ],
    )

    result = youtube_capture.main(
        [
            "attach-transcript",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--url",
            "https://www.youtube.com/watch?v=must123",
            "--transcript-file",
            str(transcript_file),
        ]
    )

    assert result == 2
    assert "transcript file is empty" in capsys.readouterr().err
    row = read_jsonl(queue_root / "2026-08-20.jsonl")[0]
    assert row["transcript_status"] == "manual-needed"
    assert "transcript_path" not in row


def test_roi_receipt_measures_queue_cadence(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    youtube_capture.write_queue(
        queue_root / "2026-08-19.jsonl",
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-19",
                url="https://www.youtube.com/watch?v=must123",
                transcript_status="manual-needed",
                disposition="must-land",
            ),
            youtube_capture.normalize_row(
                capture_date="2026-08-19",
                url="https://www.youtube.com/watch?v=watch123",
                transcript_status="defer",
                disposition="watch",
            ),
        ],
    )
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            {
                **youtube_capture.normalize_row(
                    capture_date="2026-08-20",
                    url="https://www.youtube.com/watch?v=available123",
                    transcript_status="available",
                    disposition="must-land",
                ),
                "transcript_path": str(tmp_path / "available.txt"),
            }
        ],
    )

    result = youtube_capture.main(
        [
            "roi-receipt",
            "--date",
            "2026-08-19",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--baseline-minutes",
            "300",
            "--minutes-spent",
            "75",
            "--manual-transcript-minutes-avoided",
            "30",
            "--intended-capture-days",
            "5",
            "--packet-days",
            "1",
            "--json",
        ]
    )

    assert result == 0
    output = json.loads(capsys.readouterr().out)
    assert output["mode"] == "youtube-capture-roi-receipt"
    assert output["authority"] == "measurement-only"
    assert output["capture_days"] == 2
    assert output["packet_days"] == 1
    assert output["queue_rows"] == 3
    assert output["video_rows"] == 3
    assert output["must_land_rows"] == 2
    assert output["manual_needed_rows"] == 1
    assert output["available_rows"] == 1
    assert output["defer_rows"] == 1
    assert output["estimated_time_saved_minutes"] == 255.0
    assert output["estimated_time_saved_hours"] == 4.25
    assert output["reliability"] == 0.4
    assert "no archive landing" in output["boundary"]


def test_roi_receipt_can_write_optional_receipt_file(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    receipt_path = tmp_path / "receipts" / "roi.json"
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=must123",
            )
        ],
    )

    result = youtube_capture.main(
        [
            "roi-receipt",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--minutes-spent",
            "15",
            "--receipt",
            str(receipt_path),
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert "ROI_RECEIPT_MODE=measurement-only" in output
    assert f"RECEIPT_PATH={receipt_path}" in output
    written = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert written["capture_days"] == 1
    assert written["estimated_time_saved_minutes"] == 285.0
    assert written["authority"] == "measurement-only"


def test_mark_updates_review_fields_only(tmp_path: Path) -> None:
    queue_root = tmp_path / "queue"
    assert youtube_capture.main(["add", "--date", "2026-08-20", "--queue-root", str(queue_root), "--url", "https://youtube.com/watch?v=abc123"]) == 0

    result = youtube_capture.main(
        [
            "mark",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--url",
            "https://youtube.com/watch?v=abc123",
            "--transcript-status",
            "manual-needed",
            "--disposition",
            "possible",
            "--next-action",
            "try transcript later",
            "--notes",
            "candidate only",
        ]
    )

    assert result == 0
    row = read_jsonl(queue_root / "2026-08-20.jsonl")[0]
    assert row["transcript_status"] == "manual-needed"
    assert row["disposition"] == "possible"
    assert row["next_action"] == "try transcript later"
    assert row["notes"] == "candidate only"


def test_export_intake_prints_dry_run_suggestions_only(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    assert youtube_capture.main(
        [
            "add",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--url",
            "https://youtube.com/watch?v=must123",
            "--disposition",
            "must-land",
        ]
    ) == 0
    assert youtube_capture.main(
        [
            "add",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--url",
            "https://youtube.com/watch?v=watch123",
            "--disposition",
            "watch",
        ]
    ) == 0

    capsys.readouterr()
    assert youtube_capture.main(["export-intake", "--date", "2026-08-20", "--queue-root", str(queue_root)]) == 0

    output = capsys.readouterr().out
    assert "EXPORT_MODE=dry-run-suggestions-only" in output
    assert "intake-land --no-confidence-gate --dry-run" in output
    assert "must123" in output
    assert "watch123" not in output
    assert "<operator-provided-transcript-path>" in output
    assert "no archive landing" in output

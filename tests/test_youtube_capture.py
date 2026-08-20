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

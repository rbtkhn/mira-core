from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


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


def write_route_index(path: Path) -> None:
    path.write_text(
        """version: 1
routes:
  - channel_slug: nate-herk
    label: Nate Herk
    channel_handle: "@nateherk"
    canonical_url: https://www.youtube.com/@nateherk
    aliases: [Nate Herk, nateherk]
    archive_lane: singularity
    shelf: nate-herk
    output: singularity-capture-target-note
    target_pattern: archive/sources/singularity/nate-herk-capture-targets-{date}.md
  - channel_slug: nate-b-jones
    label: Nate B. Jones
    channel_handle: "@NateBJones"
    canonical_url: https://www.youtube.com/@NateBJones
    aliases: [Nate B. Jones, Nate B Jones, natebjones]
    archive_lane: singularity
    shelf: nate-b-jones
    output: singularity-capture-target-note
    target_pattern: archive/sources/singularity/nate-b-jones-capture-targets-{date}.md
""",
        encoding="utf-8",
    )


def test_add_creates_queue_only_row(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"

    result = youtube_capture.main(
        [
            "add",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--archive-lane",
            "geopolitics",
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
            "capture_date": "2026-08-20",
            "date": "2026-08-20",
            "disposition": "must-land",
            "expected_voice": "example",
            "next_action": "review",
            "notes": "",
            "published_at": "",
            "publication_date": "",
            "source_identity": "youtube:abc123",
            "title": "Daily update",
            "transcript_status": "available",
            "url": "https://www.youtube.com/watch?v=abc123",
            "video_id": "abc123",
        }
    ]
    output = capsys.readouterr().out
    assert "YOUTUBE_CAPTURE_MODE=route-aware-capture-draft-only" in output
    assert "no archive landing" in output


def test_add_is_idempotent_by_source_identity(tmp_path: Path) -> None:
    queue_root = tmp_path / "queue"
    base = [
        "add",
        "--date",
        "2026-08-20",
        "--queue-root",
        str(queue_root),
        "--archive-lane",
        "geopolitics",
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


def test_auto_add_routes_nate_herk_to_singularity_target_note(tmp_path: Path, monkeypatch, capsys) -> None:
    route_index = tmp_path / "routes.yml"
    write_route_index(route_index)
    monkeypatch.setattr(youtube_capture, "REPO_ROOT", tmp_path)
    transcript_dir = tmp_path / "archive/sources/singularity/nate-herk/transcripts"
    transcript_dir.mkdir(parents=True)

    result = youtube_capture.main(
        [
            "add",
            "--date",
            "2026-09-04",
            "--route-index",
            str(route_index),
            "--url",
            "https://www.youtube.com/watch?v=nate123",
            "--title",
            "September AI update",
            "--channel",
            "Nate Herk",
            "--published-at",
            "2026-09-04T15:00:00+00:00",
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert "ROUTE_ARCHIVE_LANE=singularity" in output
    target = tmp_path / "archive/sources/singularity/nate-herk-capture-targets-2026-09-04.md"
    text = target.read_text(encoding="utf-8")
    assert "Archive lane: singularity" in text
    assert "https://www.youtube.com/watch?v=nate123" in text
    assert "September AI update" in text
    assert "2026-09-04" in text
    assert "archive-intake" in text
    assert not (tmp_path / "narrative-geopolitics/work/capture/youtube/2026-09-04.jsonl").exists()


def test_auto_add_routes_nate_b_jones_to_singularity_target_note(tmp_path: Path, monkeypatch) -> None:
    route_index = tmp_path / "routes.yml"
    write_route_index(route_index)
    monkeypatch.setattr(youtube_capture, "REPO_ROOT", tmp_path)

    assert (
        youtube_capture.main(
            [
                "add",
                "--date",
                "2026-09-03",
                "--route-index",
                str(route_index),
                "--url",
                "https://www.youtube.com/watch?v=jones123",
                "--title",
                "Embodied AI conversation",
                "--channel",
                "Nate B. Jones",
            ]
        )
        == 0
    )

    target = tmp_path / "archive/sources/singularity/nate-b-jones-capture-targets-2026-09-03.md"
    assert "https://www.youtube.com/watch?v=jones123" in target.read_text(encoding="utf-8")


def test_auto_add_fails_closed_for_unknown_channel(tmp_path: Path, capsys) -> None:
    route_index = tmp_path / "routes.yml"
    write_route_index(route_index)

    result = youtube_capture.main(
        [
            "add",
            "--date",
            "2026-09-04",
            "--route-index",
            str(route_index),
            "--url",
            "https://www.youtube.com/watch?v=unknown123",
            "--channel",
            "Unknown Channel",
        ]
    )

    assert result == 2
    assert "no YouTube archive route" in capsys.readouterr().err


def test_route_explain_reports_index_match(tmp_path: Path, capsys) -> None:
    route_index = tmp_path / "routes.yml"
    write_route_index(route_index)

    assert (
        youtube_capture.main(
            [
                "route-explain",
                "--route-index",
                str(route_index),
                "--channel",
                "Nate B Jones",
                "--json",
            ]
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["archive_lane"] == "singularity"
    assert payload["channel_slug"] == "nate-b-jones"
    assert payload["output"] == "singularity-capture-target-note"


def write_delegated_channel_index(tmp_path: Path) -> Path:
    route_index = tmp_path / "routes.yml"
    write_route_index(route_index)
    with route_index.open("a", encoding="utf-8") as stream:
        stream.write("delegated_indexes:\n  geopolitics: channels.md\n")
    (tmp_path / "channels.md").write_text(
        "| `dialogue-works` | Dialogue Works | `active` | Interview host. | shelf | 1 | 1 | `daily` | [open](https://www.youtube.com/@dialogueworks01) | first | last |\n",
        encoding="utf-8",
    )
    return route_index


@pytest.mark.parametrize("channel", ["dialogue-works", "Dialogue Works", "@dialogueworks01", "https://www.youtube.com/@dialogueworks01"])
def test_delegated_geopolitics_route_accepts_known_channel_metadata(tmp_path: Path, monkeypatch, channel: str) -> None:
    monkeypatch.setattr(youtube_capture, "REPO_ROOT", tmp_path)
    route_index = write_delegated_channel_index(tmp_path)
    route = youtube_capture.resolve_channel_route(channel=channel, route_index_path=route_index)
    assert (route["archive_lane"], route["channel_slug"]) == ("geopolitics", "dialogue-works")


def test_delegated_add_preserves_canonical_export_routing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(youtube_capture, "REPO_ROOT", tmp_path)
    route_index = write_delegated_channel_index(tmp_path)
    queue_root = tmp_path / "queue"
    assert youtube_capture.main([
        "add", "--date", "2026-09-04", "--route-index", str(route_index),
        "--queue-root", str(queue_root), "--channel", "Dialogue Works",
        "--url", "https://youtu.be/known123", "--notes", "operator-selected",
    ]) == 0
    row = read_jsonl(queue_root / "2026-09-04.jsonl")[0]
    assert row["notes"] == "operator-selected; channel_slug=dialogue-works"
    draft = youtube_capture.build_intake_draft(row, execute_shape="preflight")
    assert draft["command_argv"][draft["command_argv"].index("--host-slug") + 1] == "dialogue-works"


def test_delegation_keeps_unknown_channels_closed_and_explicit_routes_first(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(youtube_capture, "REPO_ROOT", tmp_path)
    route_index = write_delegated_channel_index(tmp_path)
    with pytest.raises(youtube_capture.CaptureError, match="no YouTube archive route"):
        youtube_capture.resolve_channel_route(channel="Unknown Channel", route_index_path=route_index)
    assert youtube_capture.resolve_channel_route(channel="Nate Herk", route_index_path=route_index)["archive_lane"] == "singularity"
    (tmp_path / "channels.md").unlink()
    with pytest.raises(youtube_capture.CaptureError, match="delegated Geopolitics channel index not found"):
        youtube_capture.resolve_channel_route(channel="Dialogue Works", route_index_path=route_index)


def test_repeated_delegated_add_preserves_notes_unless_replaced(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(youtube_capture, "REPO_ROOT", tmp_path)
    route_index = write_delegated_channel_index(tmp_path)
    queue_root = tmp_path / "queue"
    args = [
        "add", "--date", "2026-09-04", "--route-index", str(route_index),
        "--queue-root", str(queue_root), "--channel", "Dialogue Works",
        "--url", "https://youtu.be/known123",
    ]
    assert youtube_capture.main([*args, "--notes", "operator rationale"]) == 0
    for _ in range(2):
        assert youtube_capture.main(args) == 0
        rows = read_jsonl(queue_root / "2026-09-04.jsonl")
        assert len(rows) == 1
        assert rows[0]["notes"] == "operator rationale; channel_slug=dialogue-works"
    assert youtube_capture.main([*args, "--notes", "revised rationale"]) == 0
    assert read_jsonl(queue_root / "2026-09-04.jsonl")[0]["notes"] == "revised rationale; channel_slug=dialogue-works"


def test_delegation_rejects_conflicting_channel_identifiers(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(youtube_capture, "REPO_ROOT", tmp_path)
    route_index = write_delegated_channel_index(tmp_path)
    with (tmp_path / "channels.md").open("a", encoding="utf-8") as stream:
        stream.write(
            "| `other-channel` | Other Channel | `active` | Interview host. | shelf | 1 | 1 | `daily` | [open](https://www.youtube.com/@otherchannel) | first | last |\n"
        )
    with pytest.raises(youtube_capture.CaptureError, match="ambiguous delegated"):
        youtube_capture.resolve_channel_route(
            channel="Dialogue Works", notes="channel_slug=other-channel", route_index_path=route_index,
        )


def singularity_route(tmp_path: Path, monkeypatch) -> dict[str, object]:
    monkeypatch.setattr(youtube_capture, "REPO_ROOT", tmp_path)
    route_index = tmp_path / "routes.yml"
    write_route_index(route_index)
    route = youtube_capture.resolve_channel_route(channel="Nate Herk", route_index_path=route_index)
    route["duplicate_check_scope"] = [
        "archive/sources/singularity/nate-herk/transcripts/",
        "archive/sources/singularity/nate-herk-capture-targets-*.md",
    ]
    return route


def add_singularity_target(route: dict[str, object], *, capture_date: str = "2026-09-04", video_id: str = "nate123", title: str = "AI update") -> tuple[Path, int, int]:
    return youtube_capture.upsert_singularity_target(
        route=route, capture_date=capture_date, url=f"https://youtu.be/{video_id}",
        title=title, channel="Nate Herk", published_at="2026-09-03T12:00:00Z", next_action="review",
    )


def test_singularity_duplicate_scope_finds_prior_dates_and_landed_separately(tmp_path: Path, monkeypatch) -> None:
    route = singularity_route(tmp_path, monkeypatch)
    prior, _, _ = add_singularity_target(route, capture_date="2026-09-03")
    today = youtube_capture.singularity_capture_target_path(route, "2026-09-04")
    result = youtube_capture.singularity_absence_check(route, "https://www.youtube.com/watch?v=nate123", today)
    assert "already-captured: " in result and prior.name in result
    assert "already-landed" not in result
    transcript = tmp_path / "archive/sources/singularity/nate-herk/transcripts/episode.md"
    transcript.parent.mkdir(parents=True)
    transcript.write_text("Source: https://youtu.be/nate123\n", encoding="utf-8")
    result = youtube_capture.singularity_absence_check(route, "https://youtu.be/nate123", today)
    assert "already-landed: " in result and "episode.md" in result
    assert "already-captured: " in result
    assert youtube_capture.singularity_absence_check(route, "https://youtu.be/nate12", today).startswith("not found in ")


def test_singularity_duplicate_scope_honors_configured_target_glob(tmp_path: Path, monkeypatch) -> None:
    route = singularity_route(tmp_path, monkeypatch)
    route["target_pattern"] = "custom/targets-{date}.md"
    route["duplicate_check_scope"] = ["custom/targets-*.md"]
    prior, _, _ = add_singularity_target(route, capture_date="2026-09-02")
    today, _, _ = add_singularity_target(route)
    row = youtube_capture.read_singularity_target_rows(today)[0]
    assert "already-captured: custom/" + prior.name in row["absence_check"]


def test_historical_five_column_targets_are_discovered_but_never_rewritten(tmp_path: Path, monkeypatch) -> None:
    route = singularity_route(tmp_path, monkeypatch)
    historical = youtube_capture.singularity_capture_target_path(route, "2026-09-02")
    historical.parent.mkdir(parents=True)
    historical.write_text(
        "# Nate Herk Capture Targets\n\n"
        "| visible_age | title | url | target_status | next_action |\n"
        "|---|---|---|---|---|\n"
        "| 3 weeks ago | Grok Bot is For Real. What You Need to Know. | `https://www.youtube.com/watch?v=PQBYZQqan2g` | transcript missing | Retrieve or paste transcript. |\n",
        encoding="utf-8",
    )
    before = historical.read_bytes()
    today, _, _ = add_singularity_target(route, video_id="PQBYZQqan2g")
    row = youtube_capture.read_singularity_target_rows(today)[0]
    assert "already-captured:" in row["absence_check"]
    assert historical.name in row["absence_check"]
    add_singularity_target(route, video_id="newvideo123")
    assert len(youtube_capture.read_singularity_target_rows(today)) == 2
    with pytest.raises(youtube_capture.CaptureError, match="malformed capture-target row"):
        add_singularity_target(route, capture_date="2026-09-02")
    assert historical.read_bytes() == before


def test_singularity_rows_survive_special_characters_and_subsequent_updates(tmp_path: Path, monkeypatch) -> None:
    route = singularity_route(tmp_path, monkeypatch)
    title = "AI | tools & literal &#124; <tag> \\ path\nnext line"
    path, _, _ = add_singularity_target(route, title=title)
    add_singularity_target(route, video_id="nate456", title="Second episode")
    rows = youtube_capture.read_singularity_target_rows(path)
    assert len(rows) == 2
    assert rows[0]["title"] == title
    _, added, updated = add_singularity_target(route, video_id="nate456", title="Updated | title")
    assert (added, updated) == (0, 1)
    rows = youtube_capture.read_singularity_target_rows(path)
    assert [row["title"] for row in rows] == [title, "Updated | title"]


def test_singularity_legacy_note_migrates_without_decoding_literal_entities(tmp_path: Path, monkeypatch) -> None:
    route = singularity_route(tmp_path, monkeypatch)
    path = youtube_capture.singularity_capture_target_path(route, "2026-09-04")
    path.parent.mkdir(parents=True)
    path.write_text(
        "# Legacy targets\n\n| Video URL | Title | Publication date | Channel | Observed date | Absence check | Next eligible workflow |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| https://youtu.be/legacy123 | Literal &amp; &#124; | 2026-09-03 | Nate Herk | 2026-09-04 | not found | review |\n",
        encoding="utf-8",
    )
    add_singularity_target(route)
    rows = youtube_capture.read_singularity_target_rows(path)
    assert len(rows) == 2 and rows[0]["title"] == "Literal &amp; &#124;"


@pytest.mark.parametrize("indent", ["", "  "])
def test_singularity_malformed_existing_row_blocks_rewrite_without_byte_changes(tmp_path: Path, monkeypatch, indent: str) -> None:
    route = singularity_route(tmp_path, monkeypatch)
    path, _, _ = add_singularity_target(route)
    malformed = path.read_text(encoding="utf-8").replace("AI update", "AI | update").replace("| https://", indent + "| https://")
    path.write_text(malformed, encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(youtube_capture.CaptureError, match="malformed capture-target row.*refusing rewrite"):
        add_singularity_target(route, video_id="second123")
    assert path.read_bytes() == before


def test_route_audit_fails_on_nate_contamination_in_geopolitics(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(youtube_capture, "REPO_ROOT", tmp_path)
    queue_root = tmp_path / "narrative-geopolitics/work/capture/youtube"
    queue_root.mkdir(parents=True)
    (tmp_path / "narrative-geopolitics/channels").mkdir(parents=True)
    (tmp_path / "archive/sources/geopolitics").mkdir(parents=True)
    (tmp_path / "narrative-geopolitics/channels/channel-index.md").write_text(
        "| `nate-herk` | Nate Herk |\n",
        encoding="utf-8",
    )
    (tmp_path / "archive/sources/geopolitics/source-manifest.json").write_text(
        '{"sources":[]}\n',
        encoding="utf-8",
    )
    (queue_root / "youtube-capture-policy.yml").write_text(
        "scope: geopolitics-youtube-capture-lane\n",
        encoding="utf-8",
    )

    result = youtube_capture.main(["route-audit", "--queue-root", str(queue_root), "--json"])

    assert result == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "fail"
    assert {
        (finding["path"], finding["token"]) for finding in payload["findings"]
    } == {
        ("narrative-geopolitics/channels/channel-index.md", "nate-herk"),
        ("narrative-geopolitics/channels/channel-index.md", "nate herk"),
    }


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
            "capture_date": "2026-08-20",
            "date": "2026-08-20",
            "disposition": "watch",
            "expected_voice": "diesen",
            "next_action": "review video and mark must-land/possible/skip",
            "notes": "discover-public cadence=daily; channel_slug=glenn-diesen; discovery_evidence=rss-seed-only",
            "published_at": "2026-08-20T10:00:00+00:00",
            "publication_date": "2026-08-20",
            "source_identity": "youtube:video123",
            "title": "Public metadata only",
            "transcript_status": "defer",
            "url": "https://www.youtube.com/watch?v=video123",
            "video_id": "video123",
        }
    ]


def test_discover_public_overfetches_before_date_filter_for_mcgovern_regression(
    tmp_path: Path, monkeypatch
) -> None:
    queue_root = tmp_path / "queue"
    channel_index = tmp_path / "channel-index.md"
    channel_index.write_text(
        "\n".join(
            [
                "| Channel slug | Label | Narrative status | Routing role | Local shelf / required next step | Upstream files | Upstream days | Capture cadence | Channel URL | First day | Last day |",
                "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
                "| `dialogue-works` | Dialogue Works | `active` | Interview host. | [dialogue-works/](dialogue-works/README.md) | 1 | 1 | `daily` | [open](https://www.youtube.com/@dialogueworks01) | `2026-08-01` | `2026-08-31` |",
            ]
        ),
        encoding="utf-8",
    )
    entries = []
    for index in range(3):
        entries.append(
            f"""<entry><yt:videoId>new{index}</yt:videoId><title>August 31 upload {index}</title><published>2026-08-31T1{index}:00:00+00:00</published><author><name>Dialogue Works</name></author><link rel=\"alternate\" href=\"https://www.youtube.com/watch?v=new{index}\" /></entry>"""
        )
    entries.append(
        """<entry><yt:videoId>CFzK79SVKOE</yt:videoId><title>Ray McGovern: Inside the CIA's Moscow Meeting</title><published>2026-08-30T18:04:32+00:00</published><author><name>Dialogue Works</name></author><link rel=\"alternate\" href=\"https://www.youtube.com/watch?v=CFzK79SVKOE\" /></entry>"""
    )
    rss = (
        '<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        + "".join(entries)
        + "</feed>"
    )

    def fake_fetch(url: str, timeout: int = 20) -> str:
        if url.endswith("/videos"):
            return '{"channelId":"UCdialogue"}'
        if "feeds/videos.xml" in url:
            return rss
        raise AssertionError(url)

    monkeypatch.setattr(youtube_capture, "fetch_text", fake_fetch)
    assert youtube_capture.main(
        [
            "discover-public",
            "--date",
            "2026-08-30",
            "--queue-root",
            str(queue_root),
            "--channel-index",
            str(channel_index),
            "--limit-per-channel",
            "3",
            "--since-days",
            "0",
        ]
    ) == 0

    rows = read_jsonl(queue_root / "2026-08-30.jsonl")
    assert [row["video_id"] for row in rows] == ["CFzK79SVKOE"]
    assert rows[0]["capture_date"] == "2026-08-30"
    assert rows[0]["publication_date"] == "2026-08-30"
    assert "discovery_evidence=rss-seed-only" in rows[0]["notes"]


def test_browser_receipt_is_required_for_tier_a_completion(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    channel_index = tmp_path / "channel-index.md"
    channel_index.write_text(
        "\n".join(
            [
                "| Channel slug | Label | Narrative status | Routing role | Local shelf / required next step | Upstream files | Upstream days | Capture cadence | Channel URL | First day | Last day |",
                "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
                "| `dialogue-works` | Dialogue Works | `active` | Interview host. | [dialogue-works/](dialogue-works/README.md) | 1 | 1 | `daily` | [open](https://www.youtube.com/@dialogueworks01) | `2026-08-01` | `2026-08-31` |",
            ]
        ),
        encoding="utf-8",
    )
    coverage_args = [
        "browser-coverage",
        "--date",
        "2026-08-30",
        "--queue-root",
        str(queue_root),
        "--channel-index",
        str(channel_index),
        "--channel",
        "dialogue-works",
        "--json",
    ]
    assert youtube_capture.main(coverage_args) == 1
    assert json.loads(capsys.readouterr().out)["tier_a_completion"] == "fail"

    assert youtube_capture.main(
        [
            "record-browser-receipt",
            "--date",
            "2026-08-30",
            "--queue-root",
            str(queue_root),
            "--channel-slug",
            "dialogue-works",
            "--channel-url",
            "https://www.youtube.com/@dialogueworks01/videos",
            "--observed-at",
            "2026-08-31T12:00:00-06:00",
            "--observed-url",
            "https://www.youtube.com/watch?v=CFzK79SVKOE",
        ]
    ) == 0
    capsys.readouterr()
    assert youtube_capture.main(coverage_args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["tier_a_completion"] == "pass"
    assert payload["present_receipts"] == ["dialogue-works"]


def test_daily_check_seeds_queue_and_fails_until_browser_receipts_exist(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    queue_root = tmp_path / "queue"
    channel_index = tmp_path / "channel-index.md"
    channel_index.write_text(
        "\n".join(
            [
                "| Channel slug | Label | Narrative status | Routing role | Local shelf / required next step | Upstream files | Upstream days | Capture cadence | Channel URL | First day | Last day |",
                "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
                "| `dialogue-works` | Dialogue Works | `active` | Interview host. | [dialogue-works/](dialogue-works/README.md) | 1 | 1 | `daily` | [open](https://www.youtube.com/@dialogueworks01) | `2026-08-01` | `2026-08-31` |",
                "| `redacted-news` | Redacted News | `active` | Weekly context. | [redacted-news/](redacted-news/README.md) | 1 | 1 | `weekly` | [open](https://www.youtube.com/@RedactedNews) | `2026-08-01` | `2026-08-31` |",
            ]
        ),
        encoding="utf-8",
    )
    rss = """<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
  <entry>
    <yt:videoId>sameDay</yt:videoId>
    <title>Same-day seed</title>
    <published>2026-08-30T18:04:32+00:00</published>
    <author><name>Dialogue Works</name></author>
    <link rel="alternate" href="https://www.youtube.com/watch?v=sameDay" />
  </entry>
</feed>"""

    def fake_fetch(url: str, timeout: int = 20) -> str:
        if url.endswith("/videos"):
            return '{"channelId":"UCdialogue"}'
        if "feeds/videos.xml" in url:
            return rss
        raise AssertionError(url)

    monkeypatch.setattr(youtube_capture, "fetch_text", fake_fetch)
    result = youtube_capture.main(
        [
            "daily-check",
            "--date",
            "2026-08-30",
            "--queue-root",
            str(queue_root),
            "--channel-index",
            str(channel_index),
            "--include-active",
        ]
    )

    assert result == 1
    output = capsys.readouterr().out
    assert "DAILY_CHECK_MODE=seed-plus-required-browser-check" in output
    assert "CHECK_CHANNEL=dialogue-works|https://www.youtube.com/@dialogueworks01/videos" in output
    assert "CHECK_CHANNEL=redacted-news" not in output
    assert "CHANNEL_ROWS_SELECTED=1" in output
    assert "CHANNEL_SEARCH_TERMS=2026; Aug 30 2026; August 30 2026; Iran; Hormuz; oil; Ukraine; NATO" in output
    assert "TIER_A_COMPLETION=fail" in output
    rows = read_jsonl(queue_root / "2026-08-30.jsonl")
    assert [row["source_identity"] for row in rows] == ["youtube-channel:dialogue-works", "youtube:sameDay"]


def test_no_qualifying_browser_receipt_requires_search_surface_notes(tmp_path: Path) -> None:
    assert (
        youtube_capture.main(
            [
                "record-browser-receipt",
                "--date",
                "2026-08-30",
                "--queue-root",
                str(tmp_path / "queue"),
                "--channel-slug",
                "dialogue-works",
                "--channel-url",
                "https://www.youtube.com/@dialogueworks01/videos",
                "--observed-at",
                "2026-08-31T12:00:00-06:00",
                "--no-qualifying-videos",
                "--notes",
                "Videos page checked only",
            ]
        )
        == 2
    )

    assert (
        youtube_capture.main(
            [
                "record-browser-receipt",
                "--date",
                "2026-08-30",
                "--queue-root",
                str(tmp_path / "queue"),
                "--channel-slug",
                "dialogue-works",
                "--channel-url",
                "https://www.youtube.com/@dialogueworks01/videos",
                "--observed-at",
                "2026-08-31T12:00:00-06:00",
                "--no-qualifying-videos",
                "--notes",
                "Videos and Live checked; channel search terms: 2026, Iran, Ukraine",
            ]
        )
        == 0
    )


def test_discovered_video_row_filters_shorts_to_skip() -> None:
    row = youtube_capture.normalize_discovered_video_row(
        capture_date="2026-08-20",
        channel_row={
            "slug": "judging-freedom",
            "label": "Judge Napolitano - Judging Freedom",
            "capture_cadence": "daily",
        },
        video={
            "url": "https://www.youtube.com/shorts/abc123",
            "title": "Gaza Ceasefire Lies: Israel Ignores Deal, Kills Children #shorts",
            "published_at": "2026-08-20T18:02:59+00:00",
            "channel": "Judge Napolitano - Judging Freedom",
        },
    )

    assert row["disposition"] == "skip"
    assert row["next_action"] == "short-form video; skip unless operator explicitly selects"
    assert "auto-filter=shorts" in row["notes"]


def test_discovered_video_row_demotes_segment_titles_but_preserves_named_guests() -> None:
    segment = youtube_capture.normalize_discovered_video_row(
        capture_date="2026-08-20",
        channel_row={
            "slug": "judging-freedom",
            "label": "Judge Napolitano - Judging Freedom",
            "capture_cadence": "daily",
        },
        video={
            "url": "https://www.youtube.com/watch?v=D-syqxWYPnk",
            "title": "Gaza Ceasefire Resolution Fails: Why Florida Politicians Are Fighting",
            "published_at": "2026-08-20T20:00:15+00:00",
            "channel": "Judge Napolitano - Judging Freedom",
        },
    )
    named_guest = youtube_capture.normalize_discovered_video_row(
        capture_date="2026-08-20",
        channel_row={
            "slug": "judging-freedom",
            "label": "Judge Napolitano - Judging Freedom",
            "capture_cadence": "daily",
        },
        video={
            "url": "https://www.youtube.com/watch?v=Xi9geicm3Iw",
            "title": "Prof. Jeffrey Sachs  :  Foreign Agents Fund 254 Congressional Races",
            "published_at": "2026-08-20T20:29:40+00:00",
            "channel": "Judge Napolitano - Judging Freedom",
        },
    )

    assert segment["disposition"] == "possible"
    assert segment["next_action"] == "review topical segment before transcript retrieval"
    assert "auto-filter=segment-candidate" in segment["notes"]
    assert named_guest["disposition"] == "watch"
    assert "auto-filter" not in named_guest["notes"]


def test_discover_public_preserves_existing_review_state(tmp_path: Path, monkeypatch) -> None:
    queue_root = tmp_path / "queue"
    channel_index = tmp_path / "channel-index.md"
    channel_index.write_text(
        "\n".join(
            [
                "| Channel slug | Label | Narrative status | Routing role | Local shelf / required next step | Upstream files | Upstream days | Capture cadence | Channel URL | First day | Last day |",
                "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
                "| `judging-freedom` | Judge Napolitano - Judging Freedom | `active` | Host pressure. | [judging-freedom/](judging-freedom/README.md) | 1 | 1 | `daily` | [open](https://www.youtube.com/@judgingfreedom) | `2026-08-20` | `2026-08-20` |",
            ]
        ),
        encoding="utf-8",
    )
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=Xi9geicm3Iw",
                title="Prof. Jeffrey Sachs : Foreign Agents Fund 254 Congressional Races",
                channel="Judge Napolitano - Judging Freedom",
                published_at="2026-08-20T20:29:40+00:00",
                transcript_status="available",
                disposition="must-land",
                next_action="landed in archive source",
                notes="discover-public cadence=daily; channel_slug=judging-freedom; archive_path=archive/source.md",
            )
        ],
    )
    channel_page = '{"channelId":"UCjudging"}'
    rss = """<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
  <entry>
    <yt:videoId>Xi9geicm3Iw</yt:videoId>
    <title>Prof. Jeffrey Sachs  :  The political collapse of AIPAC - American Voters Reject Israel Lobby</title>
    <published>2026-08-20T20:29:40+00:00</published>
    <author><name>Judge Napolitano - Judging Freedom</name></author>
    <link rel="alternate" href="https://www.youtube.com/watch?v=Xi9geicm3Iw" />
  </entry>
</feed>"""

    def fake_fetch(url: str, timeout: int = 20) -> str:
        if url.endswith("/videos"):
            return channel_page
        if "feeds/videos.xml" in url:
            return rss
        raise AssertionError(url)

    monkeypatch.setattr(youtube_capture, "fetch_text", fake_fetch)

    assert youtube_capture.main(
        [
            "discover-public",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--channel-index",
            str(channel_index),
            "--channel",
            "judging-freedom",
        ]
    ) == 0

    row = read_jsonl(queue_root / "2026-08-20.jsonl")[0]
    assert row["title"] == "Prof. Jeffrey Sachs  :  The political collapse of AIPAC - American Voters Reject Israel Lobby"
    assert row["transcript_status"] == "available"
    assert row["disposition"] == "must-land"
    assert row["next_action"] == "landed in archive source"


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
    assert youtube_capture.main(
        [
            "add",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--archive-lane",
            "geopolitics",
            "--url",
            "https://youtube.com/watch?v=abc123",
        ]
    ) == 0

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
    transcript_file = tmp_path / "must.txt"
    transcript_file.write_text("Transcript body", encoding="utf-8")
    assert youtube_capture.main(
        [
            "add",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--archive-lane",
            "geopolitics",
            "--url",
            "https://youtube.com/watch?v=must123",
            "--title",
            "Must Land Source",
            "--channel",
            "Dialogue Works",
            "--expected-voice",
            "johnson",
            "--transcript-status",
            "available",
            "--disposition",
            "must-land",
            "--notes",
            "discover-public cadence=daily; channel_slug=dialogue-works",
        ]
    ) == 0
    assert youtube_capture.main(
        [
            "attach-transcript",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--url",
            "https://youtube.com/watch?v=must123",
            "--transcript-file",
            str(transcript_file),
        ]
    ) == 0
    assert youtube_capture.main(
        [
            "add",
            "--date",
            "2026-08-20",
            "--queue-root",
            str(queue_root),
            "--archive-lane",
            "geopolitics",
            "--url",
            "https://youtube.com/watch?v=watch123",
            "--transcript-status",
            "available",
            "--disposition",
            "watch",
        ]
    ) == 0

    capsys.readouterr()
    assert youtube_capture.main(["export-intake", "--date", "2026-08-20", "--queue-root", str(queue_root)]) == 0

    output = capsys.readouterr().out
    assert "EXPORT_MODE=command-draft-only" in output
    assert "python\" \"scripts\\\\land_best_intake.py" in output
    assert "--preflight" in output
    assert "--host-slug\" \"dialogue-works" in output
    assert "--voice-slug\" \"johnson" in output
    assert "must123" in output
    assert "watch123" not in output
    assert json.dumps(str(transcript_file)) in output
    assert "no archive landing" in output


def test_export_intake_json_preserves_uncertainty_and_placeholder(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://youtube.com/watch?v=unknown123",
                title="Unknown voice source",
                channel="Unknown Channel",
                transcript_status="available",
                disposition="must-land",
                expected_voice="unknown",
                notes="discover-public cadence=weekly; channel_slug=unknown-channel",
            )
        ],
    )

    assert (
        youtube_capture.main(
            [
                "export-intake",
                "--date",
                "2026-08-20",
                "--queue-root",
                str(queue_root),
                "--execute-shape",
                "landing",
                "--json",
            ]
        )
        == 0
    )

    output = json.loads(capsys.readouterr().out)
    draft = output["drafts"][0]
    argv = draft["command_argv"]
    assert output["mode"] == "youtube-capture-intake-draft"
    assert output["execute_shape"] == "landing"
    assert "--preflight" not in argv
    assert "--host-slug" in argv
    assert "unknown-channel" in argv
    assert "--voice-slug" not in argv
    assert "<operator-provided-transcript-path>" in argv
    assert "expected_voice unknown" in " ".join(draft["warnings"])
    assert "missing transcript_path" in " ".join(draft["warnings"])
    assert "no archive landing" in output["authority"]


def test_status_json_reports_landed_rows_by_manifest_url(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    manifest = tmp_path / "source-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_url": "https://www.youtube.com/watch?v=landed123",
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
            {
                **youtube_capture.normalize_row(
                    capture_date="2026-08-20",
                    url="https://www.youtube.com/watch?v=landed123",
                    title="Already landed",
                    transcript_status="available",
                    disposition="must-land",
                    notes="discover-public cadence=daily; channel_slug=dialogue-works",
                ),
                "transcript_path": str(tmp_path / "landed.txt"),
            },
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=fresh123",
                title="Fresh",
                transcript_status="manual-needed",
                disposition="possible",
                notes="discover-public cadence=weekly; channel_slug=redacted-news",
            ),
        ],
    )

    assert (
        youtube_capture.main(
            [
                "status",
                "--date",
                "2026-08-20",
                "--queue-root",
                str(queue_root),
                "--manifest",
                str(manifest),
                "--json",
            ]
        )
        == 0
    )

    output = json.loads(capsys.readouterr().out)
    assert output["counts"]["queue_rows"] == 2
    assert output["counts"]["landed_rows"] == 1
    assert output["counts"]["available_rows"] == 1
    assert output["counts"]["manual_needed_rows"] == 1
    landed = [row for row in output["rows"] if row["landed"]]
    assert landed[0]["archive_path"] == "archive/source.md"
    assert landed[0]["has_transcript_path"] is True


def test_status_text_can_filter_by_cadence_channel_and_disposition(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    manifest = tmp_path / "source-manifest.json"
    manifest.write_text(json.dumps({"sources": []}), encoding="utf-8")
    youtube_capture.write_queue(
        queue_root / "2026-08-20.jsonl",
        [
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=dialogue123",
                title="Dialogue ready",
                channel="Dialogue Works",
                transcript_status="available",
                disposition="must-land",
                notes="discover-public cadence=daily; channel_slug=dialogue-works",
            ),
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=redacted123",
                title="Redacted watch",
                channel="Redacted",
                transcript_status="defer",
                disposition="watch",
                notes="discover-public cadence=weekly; channel_slug=redacted-news",
            ),
        ],
    )

    assert (
        youtube_capture.main(
            [
                "status",
                "--date",
                "2026-08-20",
                "--queue-root",
                str(queue_root),
                "--manifest",
                str(manifest),
                "--cadence",
                "daily",
                "--channel",
                "dialogue-works",
                "--disposition",
                "must-land",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "STATUS_MODE=queue-and-manifest-only" in output
    assert "QUEUE_ROWS=1" in output
    assert "Dialogue Works" in output
    assert "Dialogue ready" in output
    assert "https://www.youtube.com/watch?v=dialogue123" in output
    assert "available" in output
    assert "must-land" in output
    assert "review" in output
    assert "redacted123" not in output
    assert "no archive landing" in output


def test_catch_up_groups_ready_needs_transcript_and_landed(tmp_path: Path, capsys) -> None:
    queue_root = tmp_path / "queue"
    manifest = tmp_path / "source-manifest.json"
    transcript_file = tmp_path / "ready.txt"
    transcript_file.write_text("ready", encoding="utf-8")
    manifest.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_url": "https://www.youtube.com/watch?v=landed123",
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
                    url="https://www.youtube.com/watch?v=ready123",
                    title="Ready",
                    transcript_status="available",
                    disposition="must-land",
                ),
                "transcript_path": str(transcript_file),
            },
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=needed123",
                title="Needs transcript",
                transcript_status="manual-needed",
                disposition="possible",
            ),
            youtube_capture.normalize_row(
                capture_date="2026-08-20",
                url="https://www.youtube.com/watch?v=landed123",
                title="Already landed",
                transcript_status="available",
                disposition="must-land",
            ),
        ],
    )

    assert (
        youtube_capture.main(
            [
                "catch-up",
                "--date",
                "2026-08-20",
                "--queue-root",
                str(queue_root),
                "--manifest",
                str(manifest),
                "--json",
            ]
        )
        == 0
    )

    output = json.loads(capsys.readouterr().out)
    assert output["mode"] == "youtube-capture-catch-up"
    assert [row["video_id"] for row in output["ready_for_intake"]] == ["ready123"]
    assert [row["video_id"] for row in output["needs_transcript"]] == ["needed123"]
    assert [row["video_id"] for row in output["already_landed_or_stale"]] == ["landed123"]
    assert "no archive landing" in output["authority"]

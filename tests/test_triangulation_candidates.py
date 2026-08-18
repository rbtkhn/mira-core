from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import triangulation_candidates
from tools import run_repo


def row(
    run_date: str,
    stem: str,
    voices: list[str],
    host: str,
    *,
    source_form: str = "youtube-transcript",
    manifest_date: str | None = None,
    source_url: str | None = None,
) -> dict:
    return {
        "date": run_date if manifest_date is None else manifest_date,
        "title": f"Title {stem}",
        "local_path": f"archive/sources/geopolitics/sources/{run_date}/source-{stem}.md",
        "source_identity": f"youtube:{stem}",
        "source_url": source_url or f"https://example.test/{stem}",
        "voice_slugs": voices,
        "host_slug": host,
        "source_form": source_form,
    }


def build(rows: list[dict], args: list[str]) -> dict:
    scope = triangulation_candidates.resolve_scope(
        triangulation_candidates.parse_args(args)
    )
    return triangulation_candidates.build_report(rows, scope)


def test_same_host_is_excluded_and_two_hosts_are_included() -> None:
    report = build(
        [
            row("2026-08-01", "same-a", ["voice-a"], "host-a"),
            row("2026-08-01", "same-b", ["voice-a"], "host-a"),
            row("2026-08-02", "multi-a", ["voice-a"], "host-a"),
            row("2026-08-02", "multi-b", ["voice-a"], "host-b"),
        ],
        ["--month", "2026-08"],
    )
    assert report["summary"]["candidate_count"] == 1
    assert report["candidates"][0]["date"] == "2026-08-02"
    assert report["candidates"][0]["hosts"] == ["host-a", "host-b"]


def test_multi_voice_source_associates_with_each_voice_once() -> None:
    report = build(
        [
            row("2026-08-03", "panel", ["voice-a", "voice-b"], "host-a"),
            row("2026-08-03", "solo-a", ["voice-a"], "host-b"),
            row("2026-08-03", "solo-b", ["voice-b"], "host-c"),
        ],
        ["--month", "2026-08"],
    )
    assert [candidate["voice"] for candidate in report["candidates"]] == [
        "voice-a",
        "voice-b",
    ]
    assert all(candidate["source_count"] == 2 for candidate in report["candidates"])


def test_path_date_fallback_for_missing_or_invalid_manifest_dates() -> None:
    report = build(
        [
            row("2026-08-04", "a", ["voice-a"], "host-a", manifest_date="not-a-date"),
            row("2026-08-04", "b", ["voice-a"], "host-b", manifest_date=""),
        ],
        ["--month", "2026-08"],
    )
    candidate = report["candidates"][0]
    assert candidate["date_fallback_used"] is True
    assert report["summary"]["date_fallback_candidates"] == 1
    assert {source["date_source"] for source in candidate["sources"]} == {
        "path-fallback"
    }


def test_voice_filter_and_date_scope() -> None:
    report = build(
        [
            row("2026-08-05", "a", ["voice-a"], "host-a"),
            row("2026-08-05", "b", ["voice-a"], "host-b"),
            row("2026-08-05", "c", ["voice-b"], "host-a"),
            row("2026-08-05", "d", ["voice-b"], "host-b"),
            row("2026-08-06", "e", ["voice-a"], "host-a"),
            row("2026-08-06", "f", ["voice-a"], "host-b"),
        ],
        [
            "--start-date",
            "2026-08-05",
            "--end-date",
            "2026-08-05",
            "--voice-slug",
            "voice-b",
        ],
    )
    assert report["summary"]["candidate_count"] == 1
    assert report["candidates"][0]["voice"] == "voice-b"
    assert report["candidates"][0]["date"] == "2026-08-05"


def test_markdown_and_json_contract() -> None:
    report = build(
        [
            row("2026-08-07", "substack", ["pape"], "escalation-trap", source_form="newsletter"),
            row("2026-08-07", "live", ["pape"], "mario-nawfal"),
        ],
        ["--month", "2026-08"],
    )
    markdown = triangulation_candidates.render_markdown(report)
    assert "2026-08-07 `pape`" in markdown
    assert "ROI tier: `high`" in markdown
    assert "archive/sources/geopolitics/sources/2026-08-07/source-live.md" in markdown
    payload = json.loads(json.dumps(report))
    assert set(payload) == {"scope", "summary", "candidates", "authority_boundary"}


def test_routine_tier_for_mercouris_duran_pair() -> None:
    report = build(
        [
            row("2026-08-08", "solo", ["mercouris"], "alexander-mercouris"),
            row("2026-08-08", "duran", ["mercouris"], "the-duran"),
        ],
        ["--month", "2026-08"],
    )
    assert report["candidates"][0]["roi_tier"] == "routine"


def test_substack_url_infers_author_controlled_tier() -> None:
    report = build(
        [
            row(
                "2026-08-09",
                "essay",
                ["crooke"],
                "crooke",
                source_url="https://conflictsforum.substack.com/p/example",
            ),
            row("2026-08-09", "interview", ["crooke"], "glenn-diesen"),
        ],
        ["--month", "2026-08"],
    )
    assert report["candidates"][0]["roi_tier"] == "high"
    assert report["candidates"][0]["sources"][0]["host_type"] == "author-controlled"


def test_runner_exposes_triangulation_candidates() -> None:
    assert run_repo.SURFACES["triangulation-candidates"].name == "triangulation_candidates.py"

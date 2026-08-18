from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import source_topic_scan


def write_source(root: Path, run_date: str, stem: str, text: str) -> str:
    relative = f"archive/sources/geopolitics/sources/{run_date}/source-{stem}.md"
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return relative


def row(
    root: Path,
    run_date: str,
    stem: str,
    text: str,
    voices: list[str],
    host: str,
) -> dict:
    return {
        "date": run_date,
        "title": f"Title {stem}",
        "voice_slugs": voices,
        "host_slug": host,
        "source_identity": f"youtube:{stem}",
        "source_url": f"https://example.test/{stem}",
        "local_path": write_source(root, run_date, stem, text),
    }


def build(tmp_path: Path, rows: list[dict], args: list[str]) -> dict:
    source_topic_scan.REPO_ROOT = tmp_path
    scope = source_topic_scan.resolve_scope(source_topic_scan.parse_args(args))
    return source_topic_scan.build_report(rows, scope)


def test_date_scoped_scan_finds_terms_across_all_manifest_rows(tmp_path: Path) -> None:
    report = build(
        tmp_path,
        [
            row(tmp_path, "2026-08-17", "a", "nuclear weapons and blockade", ["aguilar"], "mario-nawfal"),
            row(tmp_path, "2026-08-17", "b", "tactical nuclear escalation", ["ritter"], "dialogue-works"),
            row(tmp_path, "2026-08-18", "c", "nuclear but wrong date", ["aguilar"], "mario-nawfal"),
        ],
        ["--date", "2026-08-17", "--query", "nuclear weapons"],
    )

    assert report["summary"]["manifest_rows"] == 2
    assert report["summary"]["scanned_sources"] == 2
    assert report["summary"]["matching_sources"] == 2
    assert report["summary"]["missing_sources"] == 0
    assert [result["title"] for result in report["results"]] == ["Title a", "Title b"]


def test_voice_and_host_filters_narrow_results(tmp_path: Path) -> None:
    rows = [
        row(tmp_path, "2026-08-17", "a", "nuclear topic", ["aguilar"], "mario-nawfal"),
        row(tmp_path, "2026-08-17", "b", "nuclear topic", ["aguilar"], "dialogue-works"),
        row(tmp_path, "2026-08-17", "c", "nuclear topic", ["ritter"], "mario-nawfal"),
    ]

    report = build(
        tmp_path,
        rows,
        [
            "--date",
            "2026-08-17",
            "--term",
            "nuclear",
            "--voice-slug",
            "aguilar",
            "--host-slug",
            "mario-nawfal",
        ],
    )

    assert report["summary"]["manifest_rows"] == 1
    assert report["results"][0]["voice_slugs"] == ["aguilar"]
    assert report["results"][0]["host_slug"] == "mario-nawfal"


def test_missing_source_bodies_are_reported_without_crashing(tmp_path: Path) -> None:
    report = build(
        tmp_path,
        [
            {
                "date": "2026-08-17",
                "title": "Missing",
                "voice_slugs": ["aguilar"],
                "host_slug": "mario-nawfal",
                "local_path": "archive/sources/geopolitics/sources/2026-08-17/missing.md",
            }
        ],
        ["--date", "2026-08-17", "--term", "nuclear"],
    )

    assert report["summary"]["missing_sources"] == 1
    assert report["summary"]["missing_source_paths"] == [
        "archive/sources/geopolitics/sources/2026-08-17/missing.md"
    ]
    assert report["results"] == []


def test_json_contract_and_markdown_fields_are_stable(tmp_path: Path) -> None:
    report = build(
        tmp_path,
        [
            row(
                tmp_path,
                "2026-08-17",
                "a",
                "The sentence before. Nuclear weapons are discussed here. The sentence after.",
                ["aguilar"],
                "mario-nawfal",
            )
        ],
        ["--date", "2026-08-17", "--query", "nuclear weapons"],
    )

    payload = json.loads(json.dumps(report))
    assert set(payload) == {
        "scope",
        "summary",
        "results",
        "authority_boundary",
    }
    markdown = source_topic_scan.render_markdown(report)
    for expected in (
        "Title a",
        "aguilar",
        "mario-nawfal",
        "source-a.md",
        "Match count",
        "Nuclear weapons are discussed here",
    ):
        assert expected in markdown

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reporter = load_module(
    "intake_observability_report_tests", REPO_ROOT / "scripts" / "report_trim_stats.py"
)


def source_text(
    *, ingest_date: str, host_slug: str = "", curation: str = "", headings: int = 0
) -> str:
    heading_text = "\n".join(f"### Segment {index}\nBody" for index in range(headings))
    return (
        "---\n"
        f"ingest_date: {ingest_date}\n"
        "pub_date: 2026-07-07\n"
        f"host_slug: {host_slug}\n"
        "opening_trim_applied: false\n"
        "closing_trim_applied: false\n"
        f"transcript_curation: {curation}\n"
        "asr_repair_applied: false\n"
        "---\n# Source\n\n## Transcript\n\n"
        f"Title - YouTube\n\nTranscripts:\n{heading_text}\n"
    )


def configure(monkeypatch, tmp_path: Path) -> Path:
    archive = tmp_path / "archive" / "sources" / "geopolitics"
    sources = archive / "sources" / "2026-07-07"
    sources.mkdir(parents=True)
    first = sources / "source-a.md"
    second = sources / "source-b.md"
    first.write_text(
        source_text(ingest_date="2026-07-08", curation="curated_sectioned", headings=1),
        encoding="utf-8",
    )
    second.write_text(
        source_text(
            ingest_date="2026-07-09",
            host_slug="daniel-davis",
            curation="curated_sectioned",
            headings=2,
        ),
        encoding="utf-8",
    )
    manifest = {
        "sources": [
            {
                "local_path": "archive/sources/geopolitics/sources/2026-07-07/source-a.md",
                "host_slug": "dialogue-works",
                "voice_slugs": ["barnes"],
            },
            {
                "local_path": "archive/sources/geopolitics/sources/2026-07-07/source-b.md",
                "host_slug": "daniel-davis",
                "voice_slugs": ["davis"],
            },
        ]
    }
    manifest_path = archive / "source-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(reporter, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(reporter, "ARCHIVE_SOURCES_ROOT", archive / "sources")
    monkeypatch.setattr(reporter, "MANIFEST_PATH", manifest_path)
    return sources


def test_ingestion_cohort_and_manifest_host_fallback(monkeypatch, tmp_path: Path) -> None:
    configure(monkeypatch, tmp_path)
    report = reporter.collect_report(ingested_since="2026-07-08")
    assert report["summary"]["sources"] == 2
    assert report["summary"]["unknown_hosts"] == 0
    assert report["hosts"]["dialogue-works"]["sources"] == 1


def test_frontmatter_can_be_read_without_loading_source_body(
    monkeypatch, tmp_path: Path
) -> None:
    sources = configure(monkeypatch, tmp_path)
    frontmatter = reporter.read_frontmatter(sources / "source-a.md")
    assert frontmatter["ingest_date"] == "2026-07-08"


def test_ingestion_date_filter_excludes_older_landings(monkeypatch, tmp_path: Path) -> None:
    configure(monkeypatch, tmp_path)
    report = reporter.collect_report(ingested_since="2026-07-09")
    assert report["summary"]["sources"] == 1
    assert set(report["hosts"]) == {"daniel-davis"}


def test_curation_and_wrapper_states_are_honest(monkeypatch, tmp_path: Path) -> None:
    configure(monkeypatch, tmp_path)
    report = reporter.collect_report(ingested_since="2026-07-08")
    summary = report["summary"]
    assert summary["weak_sectioning"] == 1
    assert summary["useful_sectioning"] == 1
    assert summary["transcript_wrapper_remnants"] == 2
    assert summary["youtube_title_wrapper_remnants"] == 2
    assert summary["asr_checked_no_change"] == 2

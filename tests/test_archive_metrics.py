from __future__ import annotations

from scripts.archive_metrics import is_transcript_modality, load_metrics
from scripts.archive_query import load_curated_channels, query_snapshot


def test_transcript_predicate_includes_cleaned_transcripts() -> None:
    assert is_transcript_modality("transcript")
    assert is_transcript_modality("cleaned-transcript")
    assert not is_transcript_modality("article")


def test_august_metrics_reconcile_manifest_and_files() -> None:
    result = load_metrics("2026-08")
    assert result["manifest_rows"] == 301
    assert result["transcript_like_rows"] == 296
    assert result["daily_statistics"]["median"] == 9
    assert result["parity"]["manifest_paths"] == result["parity"]["source_files"] == 301
    assert result["parity"]["missing_files"] == []
    assert result["parity"]["unlisted_files"] == []

def test_curated_roster_deduplicates_operational_channels() -> None:
    roster = load_curated_channels()
    slugs = [row["slug"] for row in roster]
    assert len(slugs) == len(set(slugs))
    assert "dialogue-works" in slugs

def test_explicit_singularity_collection_is_separate() -> None:
    result = query_snapshot(("moonshots",))
    assert result["collections"][0]["retrieval_policy"] == "explicit-only"
    assert all(row["_collection"] == "moonshots" for row in result["records"])

def test_default_query_does_not_include_singularity() -> None:
    result = query_snapshot()
    assert {row["_collection"] for row in result["records"]} == {"geopolitics"}

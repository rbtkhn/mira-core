from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "docs" / "skill-drafts"


def text(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


def test_archive_family_has_four_canonical_names() -> None:
    assert "name: archive-intake" in text("archive-intake")
    assert "name: archive-query" in text("archive-query")
    assert "name: archive-repair" in text("archive-repair")
    assert "name: archive-audit" in text("archive-audit")


def test_intake_redirects_are_permanent_and_canonical() -> None:
    for name in ("smart-intake", "best-intake"):
        value = text(name)
        assert "../archive-intake/SKILL.md" in value
        assert "compatibility" in value.lower()


def test_archive_intake_has_deployable_ui_metadata() -> None:
    metadata = (SKILLS / "archive-intake" / "agents" / "openai.yaml").read_text(
        encoding="utf-8"
    )
    assert 'display_name: "Archive Intake"' in metadata
    assert "$archive-intake" in metadata


def test_local_family_routes_are_explicit() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for name in ("archive-query", "archive-repair", "archive-audit"):
        assert f"docs/skill-drafts/{name}/SKILL.md" in agents
    assert "docs/skill-drafts/archive-intake/SKILL.md" in agents


def test_library_import_route_is_explicit_and_bounded() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    normalized_agents = " ".join(agents.split())
    skill = text("library-import")

    assert "docs/skill-drafts/library-import/SKILL.md" in agents
    assert "source-body admission into Git" in normalized_agents
    assert "name: library-import" in skill
    assert "Treat every external file, URL, edition number, and filename as a candidate" in skill
    assert "never claim `complete-surviving-corpus`" in skill
    assert "platform state root at `library/texts/`" in skill


def test_library_import_separates_readiness_and_authority_gates() -> None:
    skill = text("library-import")
    normalized = " ".join(skill.split())

    for gate in (
        "`roster-ready`",
        "`metadata-ready`",
        "`body-research-ready`",
        "`admission-ready`",
    ):
        assert gate in skill

    assert "Roster acceptance does not authorize metadata mutation" in normalized
    assert "Metadata admission does not authorize downloading or admitting a" in normalized
    assert "Body admission does not authorize staging, commit, push" in normalized


def test_library_import_large_batches_are_resumable_and_auditable() -> None:
    skill = text("library-import")
    normalized = " ".join(skill.split())

    assert "A normal large-shelf batch contains 8-12 authorities" in skill
    assert "For more than five authorities or ten candidate bodies" in skill
    assert "Do not split an already authorized inspection batch into per-authority approval prompts" in normalized
    assert "stable `candidate_id`" in skill
    for state in (
        "`proposed`",
        "`metadata-ready`",
        "`body-research-incomplete`",
        "`downloaded`",
        "`inspected`",
        "`admission-ready`",
        "`reconciled`",
        "`review-pending`",
        "`admitted`",
        "`rejected`",
        "`paused`",
    ):
        assert state in skill

    assert "Do not redownload, renormalize, or re-admit an unchanged verified body" in skill
    assert "last verified batch step and exact re-entry point" in skill
    assert "it does not stop independent rows" in skill


def test_library_import_batches_use_one_review_boundary_and_two_receipts() -> None:
    skill = text("library-import")
    normalized = " ".join(skill.split())

    assert "one reconciled Markdown receipt and one JSON receipt" in normalized
    assert "stop before registry mutation or body admission" in normalized
    assert "Default to exactly two inspection-batch artifacts" in normalized
    assert "per-authority supplement only when" in normalized
    assert "run the full suite once after all independent authorized mutations" in normalized


def test_library_import_requires_maturity_and_navigation_integrity() -> None:
    skill = text("library-import")
    normalized = " ".join(skill.split())

    assert "Level 6 requires an explicit authority review" in skill
    assert "No availability check, bilingual pair, or `complete-work` body automatically" in normalized
    assert "text-source index and era index must both agree with the registry" in normalized
    assert "If no deterministic era-index renderer and drift check exist" in normalized


def test_library_import_benchmarks_fail_closed_on_rights_and_provenance() -> None:
    skill = text("library-import")
    normalized = " ".join(skill.split())

    assert "Do not convert online-available personal-reading texts into rights blockers" in normalized
    assert "a modern online text has no stable file route or cannot be inspected" in normalized
    assert "no file is admitted" in normalized
    assert "catalogue, aggregator, or OCR transcription" in normalized
    assert "routes further research rather than guessing" in normalized


def test_query_duplicate_source_is_retired() -> None:
    assert not (ROOT / ".codex" / "skills" / "archive-query" / "SKILL.md").exists()


def test_archive_repair_routes_inspection_to_audit() -> None:
    value = text("archive-repair")
    assert "archive-audit" in value
    assert "- `inspect`:" not in value


def test_archive_readme_keeps_manifest_as_the_only_index_authority() -> None:
    value = (
        ROOT / "archive" / "sources" / "geopolitics" / "README.md"
    ).read_text(encoding="utf-8")

    assert "source-manifest.json" in value
    assert "sole authoritative index" in value
    assert "Authority effect: `none`." in value

    for workflow in (
        "archive-intake",
        "archive-query",
        "archive-audit",
        "archive-repair",
    ):
        assert workflow in value

    assert "archive-index.md" not in value
    assert not re.search(
        r"\b\d[\d,]*\s+(?:imported\s+)?sources?\b",
        value,
        re.IGNORECASE,
    )


def test_archive_intake_hands_same_day_analysis_to_scan_or_geo_strategy() -> None:
    value = text("archive-intake")
    normalized = " ".join(value.split())
    assert "same date" in normalized
    assert "geo-strategy" in value
    assert "source-topic-scan" in value
    assert "remembered partial corpus" in normalized

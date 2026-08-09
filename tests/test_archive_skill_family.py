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


def test_query_duplicate_source_is_retired() -> None:
    assert not (ROOT / ".codex" / "skills" / "archive-query" / "SKILL.md").exists()


def test_archive_repair_routes_inspection_to_audit() -> None:
    value = text("archive-repair")
    assert "archive-audit" in value
    assert "- `inspect`:" not in value


def test_archive_readme_keeps_manifest_as_the_only_index_authority() -> None:
    value = (
        ROOT / "narrative-geopolitics" / "archive" / "README.md"
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

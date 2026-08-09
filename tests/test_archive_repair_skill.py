from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "docs" / "skill-drafts" / "archive-repair" / "SKILL.md"


def skill_text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_skill_names_canonical_command_and_four_classes() -> None:
    text = skill_text()
    assert "tools\\run.ps1 archive-repair" in text
    for repair_class in ("metadata", "asr", "sectioning", "wrapper-trim"):
        assert f"`{repair_class}`" in text


def test_skill_requires_direct_digest_bound_execution() -> None:
    text = skill_text()
    assert "--execute" in text
    assert "--plan-digest" in text
    assert "direct explicit" in text


def test_skill_keeps_query_scope_non_authorizing() -> None:
    text = " ".join(skill_text().split())
    assert "archive-query" in text
    assert "grants no authority" in text
    assert "re-read the source manifest" in text


def test_skill_marks_legacy_helpers_as_compatibility_only() -> None:
    text = skill_text()
    assert "compatibility adapters" in text
    assert "run_asr_repair_pilot.py" in text
    assert "backfill_section_list.py" in text

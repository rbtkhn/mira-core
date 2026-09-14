"""Structural integration checks; real behavior is evaluated separately."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "docs/skill-drafts"
REFERENCE = SKILLS / "mira-mind/references/development-practice.md"


def test_all_named_owners_link_one_existing_development_reference():
    controls = [SKILLS / name / "SKILL.md" for name in (
        "mira-mind", "mira-memory", "mira-work", "mira-read",
        "library-reasoning", "mira-journal", "mira-notes", "mira-essays",
        "mira-letters", "coffee", "dream",
    )] + [SKILLS / "mira-work/references/inquiry-practices.md"]
    for control in controls:
        targets = re.findall(r"\]\(([^)]+development-practice\.md)\)",
                             control.read_text(encoding="utf-8"))
        assert len(targets) == 1, control
        assert (control.parent / targets[0]).resolve() == REFERENCE.resolve()
    assert REFERENCE.is_file()


def test_shared_practice_reuses_the_existing_memory_reference():
    text = REFERENCE.read_text(encoding="utf-8")
    target = re.search(r"\]\((memory-use\.md)\)", text)
    assert target and (REFERENCE.parent / target[1]).is_file()
    assert not (SKILLS / "mira-mind/scripts").exists()
    assert "tools/run.ps1 mira-memory status" not in text


def test_no_private_evaluation_body_is_embedded_in_shared_reference():
    text = REFERENCE.read_text(encoding="utf-8")
    # A documented optional root is discoverable; actual private source handles
    # and old conversation bodies must stay in the private baseline.
    assert "mira-mind-evolution/window.md" in text
    assert "rollout-2026" not in text
    assert "01a0889c" not in text
    assert "01a096b1" not in text

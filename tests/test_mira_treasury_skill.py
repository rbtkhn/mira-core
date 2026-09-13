"""Structural contract checks; behavioral scenarios require review, not string scoring."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "docs/skill-drafts/mira-treasury"


def test_local_skill_links_resolve():
    for path in SKILL.rglob("*.md"):
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if target.startswith("#"):
                continue
            assert (path.parent / target.split("#")[0]).resolve().exists(), (path, target)


def test_behavioral_cases_are_distinct_and_reviewable():
    cases = json.loads((SKILL / "references/validation-fixtures.json").read_text(encoding="utf-8"))
    assert len({case["id"] for case in cases}) == len(cases)
    assert {case["expected_activation"] for case in cases} == {True, False}
    for case in cases:
        assert case["prompt"].strip()
        assert case["required_behaviors"] and case["forbidden_behaviors"]
        assert not set(case["required_behaviors"]) & set(case["forbidden_behaviors"])


def test_worked_handoff_fragment_links_resolve():
    text = (SKILL / "references/worked-handoff.md").read_text(encoding="utf-8")
    headings = {re.sub(r"[^a-z0-9 -]", "", h.lower()).replace(" ", "-")
                for h in re.findall(r"^#+ (.+)$", text, re.M)}
    for fragment in re.findall(r"\]\(#([^)]*)\)", text):
        assert fragment in headings

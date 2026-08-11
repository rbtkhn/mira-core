from __future__ import annotations

import re
from pathlib import Path

from scripts import codex_skill_registry


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "docs" / "skill-drafts" / "repo-audit" / "SKILL.md"


def test_agents_routes_narrative_repo_audit_through_canonical_contract() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "When `repo-audit` targets Narrative Systems" in agents
    assert "docs/skill-drafts/repo-audit/SKILL.md" in agents
    assert "deployable mirror, not a second authority" in agents
    assert "archive-audit" in agents
    assert "do not" in agents.lower()
    assert "repair authority" in agents


def test_repo_audit_is_registered_as_portable() -> None:
    entry = codex_skill_registry.build_registry()["repo-audit"]

    assert entry.source == CANONICAL
    assert entry.dest.name == "SKILL.md"


def test_only_canonical_source_claims_repo_audit_name() -> None:
    skill_roots = (ROOT / "docs" / "skill-drafts", ROOT / ".codex" / "skills")
    canonical_claims: list[str] = []

    for skill_root in skill_roots:
        for path in skill_root.glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            match = re.search(r"(?m)^name:\s*[\"']?([^\"'\r\n]+)", text)
            if match and match.group(1).strip() == "repo-audit":
                canonical_claims.append(path.relative_to(ROOT).as_posix())

    assert canonical_claims == ["docs/skill-drafts/repo-audit/SKILL.md"]


def test_repo_audit_bounds_authorship_lineage_and_truncated_diagnostics() -> None:
    skill = CANONICAL.read_text(encoding="utf-8")
    assert "## Bound authorship and lineage inference" in skill
    assert "outside the formal repository finding set" in skill
    assert "private psychology, demographics, motives" in skill
    assert "Treat repository genealogy as branching" in skill
    assert "when history is shallow, rewritten, imported, mirrored" in skill
    assert "If command output truncates" in skill
    assert "rerun against the smallest named surfaces" in skill

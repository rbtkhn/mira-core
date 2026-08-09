from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import check_codex_skills_sync
import codex_skill_registry
import sync_codex_skills


def test_reality_check_skill_metadata_and_authority_contract() -> None:
    skill_root = REPO_ROOT / "docs" / "skill-drafts" / "reality-check"
    text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    keys = {
        line.split(":", 1)[0]
        for line in frontmatter.splitlines()
        if line.strip() and ":" in line
    }
    assert keys == {"name", "description"}
    assert "`OPC-*`, `CLM-*`, or `NG-*`" in frontmatter
    assert "unrelated general-purpose fact checking" in frontmatter
    assert "Keep a plain reality check read-only" in text
    assert "ask whether the operator wants to sign" in text
    assert "Never infer a reviewer" in text
    assert "references/kremlin-sourcing.md" in text
    assert "two-human requirements pass" in text
    assert "research-brief-seed-v1" in text
    assert "Do not emit seeds for" in text
    assert "does not\ntrigger browsing" in text

    metadata = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert 'display_name: "Reality Check"' in metadata
    assert "$reality-check" in metadata

    kremlin = (skill_root / "references" / "kremlin-sourcing.md").read_text(
        encoding="utf-8"
    )
    assert "VSRC-OFF-KREMLIN" in kremlin
    assert "One event, one lineage" in kremlin
    assert "Omission is not renunciation" in kremlin
    assert "identity rhetoric into a territorial requirement" in kremlin


def test_skill_sync_mirrors_complete_directory_and_detects_drift(
    tmp_path: Path, monkeypatch
) -> None:
    source_root = tmp_path / "repo" / "reality-check"
    dest_root = tmp_path / "installed" / "reality-check"
    (source_root / "agents").mkdir(parents=True)
    (dest_root / "obsolete").mkdir(parents=True)
    (source_root / "SKILL.md").write_text("skill\n", encoding="utf-8")
    (source_root / "agents" / "openai.yaml").write_text("interface: {}\n", encoding="utf-8")
    (dest_root / "SKILL.md").write_text("old\n", encoding="utf-8")
    (dest_root / "obsolete" / "stale.txt").write_text("stale\n", encoding="utf-8")
    entry = codex_skill_registry.SkillEntry(
        name="reality-check",
        source=source_root / "SKILL.md",
        dest=dest_root / "SKILL.md",
    )
    registry = {"reality-check": entry}
    monkeypatch.setattr(sync_codex_skills, "build_registry", lambda: registry)
    monkeypatch.setattr(check_codex_skills_sync, "build_registry", lambda: registry)

    assert sync_codex_skills.sync_skill("reality-check", dry_run=True).startswith("WOULD-SYNC")
    assert (dest_root / "SKILL.md").read_text(encoding="utf-8") == "old\n"
    assert sync_codex_skills.sync_skill("reality-check", dry_run=False).startswith("SYNCED")
    assert (dest_root / "SKILL.md").read_text(encoding="utf-8") == "skill\n"
    assert (dest_root / "agents" / "openai.yaml").exists()
    assert not (dest_root / "obsolete" / "stale.txt").exists()
    assert check_codex_skills_sync.check_skill("reality-check")[1] is True

    (dest_root / "agents" / "openai.yaml").write_text("drift\n", encoding="utf-8")
    message, current = check_codex_skills_sync.check_skill("reality-check")
    assert current is False
    assert message.startswith("DRIFT")

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_mira_writing_skills_have_minimal_metadata_and_ui_prompts() -> None:
    for name in ("mira-notes", "mira-essays"):
        skill_root = ROOT / "docs" / "skill-drafts" / name
        text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = [
            line.split(":", 1)[0]
            for line in text.split("---", 2)[1].splitlines()
            if ":" in line
        ]
        metadata = (skill_root / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )

        assert frontmatter == ["name", "description"]
        assert f"name: {name}" in text
        assert f"${name}" in metadata
        assert "TODO" not in text


def test_agents_routes_all_three_mira_writing_forms() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for name in ("mira-journal", "mira-notes", "mira-essays"):
        assert f"docs/skill-drafts/{name}/SKILL.md" in agents


def test_note_and_essay_imperatives_carry_bounded_github_lifecycle_authority() -> None:
    notes = (ROOT / "docs" / "skill-drafts" / "mira-notes" / "SKILL.md").read_text(encoding="utf-8")
    essays = (ROOT / "docs" / "skill-drafts" / "mira-essays" / "SKILL.md").read_text(encoding="utf-8")
    for text, phrase in ((notes, "note this"), (essays, "essay this")):
        normalized = " ".join(text.split())
        assert phrase in text
        assert "stage only" in text
        assert "commit it, and push that exact" in normalized
        assert "descriptive or interrogative" in text
        assert "unrelated dirty paths" in text


def test_mira_writing_storage_is_separated() -> None:
    assert (ROOT / "mira" / "journal").is_dir()
    assert (ROOT / "archive" / "notes").is_dir()
    assert (ROOT / "archive" / "essays").is_dir()
    assert not (ROOT / "mira" / "notes").exists()
    assert not (ROOT / "mira" / "essays").exists()
    assert not (ROOT / "mira" / "reflections").exists()

    history = ROOT / "archive" / "notes" / "2026-08-15-from-civilization-memory-to-mira-core.md"
    essay = ROOT / "archive" / "essays" / "2026-08-15-the-responsible-custody-of-inheritance.md"
    assert history.is_file()
    assert essay.is_file()
    assert "../notes/2026-08-15-from-civilization-memory-to-mira-core.md" in essay.read_text(
        encoding="utf-8"
    )


def test_innermost_loop_paths_follow_notes_migration() -> None:
    governed = (
        ROOT / "archive" / "notes" / "innermost-loop-simulation" / "protocol.json"
    ).read_text(encoding="utf-8")
    implementation = (ROOT / "scripts" / "innermost_loop_simulation.py").read_text(
        encoding="utf-8"
    )

    assert "archive/notes/innermost-loop-simulation" in governed
    assert "mira/reflections" not in governed
    assert "archive/notes/innermost-loop-simulation" in implementation
    assert "mira/reflections" not in implementation

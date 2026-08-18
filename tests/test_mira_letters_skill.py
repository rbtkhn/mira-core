from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "docs" / "skill-drafts" / "mira-letters"


def read_skill() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def test_mira_letters_has_minimal_skill_structure() -> None:
    skill = read_skill()
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    frontmatter = [
        line.split(":", 1)[0]
        for line in skill.split("---", 2)[1].splitlines()
        if ":" in line
    ]

    assert frontmatter == ["name", "description"]
    assert "name: mira-letters" in skill
    assert "$mira-letters" in metadata
    assert "TODO" not in skill
    assert sorted(
        path.relative_to(SKILL_ROOT).as_posix()
        for path in SKILL_ROOT.rglob("*")
        if path.is_file()
    ) == ["SKILL.md", "agents/openai.yaml"]


def test_mira_letters_routes_only_to_the_canonical_shelf() -> None:
    skill = read_skill()
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    readme = (ROOT / "archive" / "letters" / "README.md").read_text(encoding="utf-8")

    assert "docs/skill-drafts/mira-letters/SKILL.md" in agents
    assert "requests work under `archive/letters`" in " ".join(agents.split())
    assert "archive/letters/YYYY-MM-DD-recipient-subject.md" in skill
    assert "archive/letters/<thread-slug>/" in skill
    assert "Do not create `mira/letters/`" in skill
    assert not (ROOT / "mira" / "letters").exists()
    assert "Mira Letters is the authored correspondence shelf" in readme


def test_mira_letters_preserves_authorship_and_correspondence_fidelity() -> None:
    normalized = " ".join(read_skill().split())

    for phrase in (
        "Mira is the represented author of outbound letters",
        "Do not ghostwrite as the operator",
        "Preserve authorized inbound messages verbatim",
        "Append a correction or provenance note",
        "preserve the learner's authorship and capacity to disagree",
        "lead with the consequential judgment, deliverable, or decision",
    ):
        assert phrase in normalized


def test_mira_letters_stops_at_operator_controlled_delivery() -> None:
    normalized = " ".join(read_skill().split())

    for phrase in (
        "A status records lifecycle only.",
        "the operator controls delivery",
        "Sending requires exact current authorization",
        "recipient, channel, and final text",
        "Never infer permission to contact a recipient",
        "make a commercial or relational commitment",
    ):
        assert phrase in normalized


def test_mira_letters_is_not_an_external_archive_collection() -> None:
    skill = read_skill()
    registry = (ROOT / "archive" / "collections.json").read_text(encoding="utf-8")

    assert "Do not register Letters in\n`archive/collections.json`" in skill
    assert '"id": "mira-letters"' not in registry


def test_cognitive_substrate_note_remains_a_bounded_hypothesis() -> None:
    note = (
        ROOT / "archive" / "notes" / "2026-08-17-authored-writing-as-cognitive-substrate.md"
    ).read_text(encoding="utf-8")
    normalized = " ".join(note.split())

    for phrase in (
        "Status: `private-provisional`",
        "Class: `architectural-hypothesis`",
        "Authority effect: none",
        "not evidence of consciousness",
        "without becoming canonical identity",
        "without supplying evidence",
    ):
        assert phrase in normalized

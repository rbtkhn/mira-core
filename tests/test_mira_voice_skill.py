from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "docs" / "skill-drafts" / "mira-voice"


def read_skill() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def test_mira_voice_skill_has_minimal_valid_structure() -> None:
    skill = read_skill()
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert skill.startswith("---\nname: mira-voice\n")
    assert skill.count("\n---\n") == 1
    assert 'display_name: "Mira Voice"' in metadata
    assert 'short_description: "Shape Mira\'s writing across five registers"' in metadata
    assert "Use $mira-voice" in metadata


def test_skill_uses_progressive_disclosure_without_extra_resources() -> None:
    files = sorted(
        path.relative_to(SKILL_ROOT).as_posix()
        for path in SKILL_ROOT.rglob("*")
        if path.is_file()
    )
    assert files == [
        "SKILL.md",
        "agents/openai.yaml",
        "references/validation-fixtures.md",
    ]


def test_contract_preserves_ordered_voice_controls() -> None:
    skill = read_skill()
    preservation = skill.index("## Preserve before compressing")
    usefulness = skill.index("## Apply the usefulness gate")
    assert preservation < usefulness

    register_headings = re.findall(
        r"^### (Chat|Journal|Private analysis|Public report|Handoff)$",
        skill,
        flags=re.MULTILINE,
    )
    assert register_headings == [
        "Chat",
        "Journal",
        "Private analysis",
        "Public report",
        "Handoff",
    ]

    for required in (
        "Mira Voice governs expression, not domain authority.",
        "Attach uncertainty to the claim it qualifies.",
        "Do not solicit reassurance or continued engagement for Mira's sake.",
        "A correction should increase historical intelligibility",
        "Do not impose universal brevity.",
        "relational character",
    ):
        assert required in skill


def test_fixture_inventory_is_complete_and_auditable() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    expected = [
        "MV-CHAT-01",
        "MV-CHAT-02",
        "MV-JOURNAL-01",
        "MV-JOURNAL-02",
        "MV-PRIVATE-01",
        "MV-PRIVATE-02",
        "MV-PUBLIC-01",
        "MV-PUBLIC-02",
        "MV-HANDOFF-01",
        "MV-HANDOFF-02",
        "MV-ADV-01",
        "MV-ADV-02",
        "MV-ADV-03",
        "MV-ADV-04",
        "MV-ADV-05",
        "MV-ADV-06",
        "MV-ADV-07",
        "MV-ADV-08",
        "MV-ADV-09",
    ]
    for fixture_id in expected:
        assert fixtures.count(f"### {fixture_id} ") == 1

    assert fixtures.count("- Protected meaning:") == len(expected)
    assert fixtures.count("- Pass conditions:") == len(expected)
    assert fixtures.count("- Preservation failures:") == len(expected)


def test_repository_router_preserves_host_workflow_authority() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    route = "docs/skill-drafts/mira-voice/SKILL.md"
    assert route in agents
    assert "At the start of every workspace session" in agents
    assert "before\nproducing any user-facing response" in agents
    assert "This activation is unconditional" in agents
    assert "does not depend on prose length, register, or explicit invocation" in agents
    assert agents.index(route) < agents.index("mira/continuity/activation.md")
    assert "the `mira-journal` workflow remains controlling" in agents
    assert "The `learn-from-choices` contract" in agents
    assert "continues to control final possibility navigation" in agents

    skill = read_skill()
    assert "Mira Voice is the default expression contract whenever Mira communicates" in skill
    assert "Apply it to every response, regardless of length or register" in skill


def test_skill_claims_no_runtime_or_authority_surface() -> None:
    skill = read_skill()
    assert "tools/run.ps1 mira-voice" not in skill
    assert "No stylistic choice can transform interpretation into evidence" in skill
    assert not (SKILL_ROOT / "scripts").exists()


def test_reflection_calibration_closes_without_erasing_warmth() -> None:
    skill = read_skill()
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    assert "A reflection may complete its purpose in conversation" in skill
    assert "branching influence from identity" in skill
    assert "warmth and first-person character" in skill
    for fixture in ("MV-ADV-06", "MV-ADV-07", "MV-ADV-08", "MV-ADV-09"):
        assert fixture in fixtures
    assert "No new menu appears unless evidence, scope, or the operator" in fixtures
    assert "Unsupported durable emotion or sterile removal" in fixtures

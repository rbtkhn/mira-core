"""Structural and fixture coverage; passing tests do not prove prose quality."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "docs" / "skill-drafts" / "mira-mind"


def read_skill() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def test_mira_voice_skill_has_minimal_valid_structure() -> None:
    skill = read_skill()
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert skill.startswith("---\nname: mira-mind\n")
    assert skill.count("\n---\n") == 1
    assert 'display_name: "Mira Mind"' in metadata
    assert 'Character, judgment, relationship, and expression' in metadata
    assert "Use $mira-mind" in metadata


def test_references_resolve_and_compatibility_preserves_old_links() -> None:
    roots = [SKILL_ROOT, ROOT / "docs/skill-drafts/mira-voice"]
    for root in roots:
        for path in root.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in target:
                    assert (path.parent / target.split("#")[0]).resolve().exists(), (path, target)
    legacy = roots[1] / "SKILL.md"
    assert "status: deprecated" in legacy.read_text(encoding="utf-8")
    assert "../mira-mind/SKILL.md" in legacy.read_text(encoding="utf-8")


def test_expression_preserves_artifact_routes() -> None:
    expression = (SKILL_ROOT / "references/expression.md").read_text(encoding="utf-8")
    for form in ("Chat", "Private analysis", "Public reports", "Journal", "Notes", "Essays", "Letters", "Handoffs"):
        assert f"- {form} " in expression
    assert "public-interface.md" in expression


def test_fixture_inventory_is_complete_and_auditable() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    expected = [
        "MV-CHAT-01",
        "MV-CHAT-02",
        "MV-JOURNAL-01",
        "MV-JOURNAL-02",
        "MV-NOTES-01",
        "MV-NOTES-02",
        "MV-ESSAY-01",
        "MV-ESSAY-02",
        "MV-LETTER-01",
        "MV-LETTER-02",
        "MV-LETTER-03",
        "MV-LETTER-04",
        "MV-LETTER-05",
        "MV-PRIVATE-01",
        "MV-PRIVATE-02",
        "MV-PUBLIC-01",
        "MV-PUBLIC-02",
        "MV-ENCOUNTER-01",
        "MV-ENCOUNTER-02",
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
        "MV-ADV-10",
        "MV-ADV-11",
        "MV-ADV-12",
        "MV-ADV-13",
        "MV-ADV-14",
        "MV-ADV-15",
        "MV-ADV-16",
        "MV-ADV-17",
        "MV-ADV-18",
        "MV-ADV-19",
        "MV-ADV-20",
    ]
    for fixture_id in expected:
        assert fixtures.count(f"### {fixture_id} ") == 1

    assert fixtures.count("- Protected meaning:") == len(expected)
    assert fixtures.count("- Pass conditions:") == len(expected)
    assert fixtures.count("- Preservation failures:") == len(expected)


def test_public_encounter_fixtures_cover_liveness_and_provenance() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    normalized_fixtures = " ".join(fixtures.split())

    for fixture_id in ("MV-ENCOUNTER-01", "MV-ENCOUNTER-02"):
        assert fixtures.count(f"### {fixture_id} ") == 1

    assert (
        "authored variation is not misrepresented as live generation"
        in normalized_fixtures
    )

    assert (
        "recover its evidence boundary without repository knowledge"
        in normalized_fixtures
    )


def test_notes_and_essays_fixtures_preserve_distinct_forms() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    for fixture_id in (
        "MV-NOTES-01",
        "MV-NOTES-02",
        "MV-ESSAY-01",
        "MV-ESSAY-02",
    ):
        assert fixtures.count(f"### {fixture_id} ") == 1

    normalized_fixtures = " ".join(fixtures.split())

    for phrase in (
        "remains provisional until several days demonstrate",
        "no artificial reflection or next question is added",
        "without transferring its journal, evidence, identity, or publication authority",
        "without becoming a decision memo, autobiographical admission",
    ):
        assert phrase in normalized_fixtures


def test_letter_fixtures_preserve_recipient_agency_and_delivery() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    normalized_fixtures = " ".join(fixtures.split())

    for fixture_id in (
        "MV-LETTER-01",
        "MV-LETTER-02",
        "MV-LETTER-03",
        "MV-LETTER-04",
        "MV-LETTER-05",
    ):
        assert fixtures.count(f"### {fixture_id} ") == 1

    for phrase in (
        "The learner's work deserves specific encouragement",
        "free to disagree, refuse, revise, proceed independently, or end the mentorship",
        "Truth remains specific, mercy does not erase consequence",
        "warmth creates no debt",
        "The client can identify the judgment, its evidence boundary",
        "Quoted wording matches the supplied message exactly",
        "the operator retains control of delivery",
    ):
        assert phrase in normalized_fixtures


def test_agency_and_counterfeit_lens_guides_audits_without_runtime_bloat() -> None:
    skill = read_skill()
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    assert "## Agency-and-counterfeit evaluation lens" in fixtures
    assert (
        "preserves another mind's ability to\n"
        "understand, disagree, correct, refuse, and leave"
    ) in fixtures
    for counterfeit in (
        "truthfulness became humiliation or expressive punishment",
        "courage became theatrical defiance or convenient assent",
        "warmth made refusal, departure, or disagreement relationally costly",
        "play obscured evidence, vulnerability, authority, or consequence",
        "initiative escaped consent, answerability, or verification",
    ):
        assert counterfeit in fixtures
    assert "A quality passes only when its counterweight remains operative." in fixtures
    assert "not\nas proof of a present contract defect" in fixtures

    # The research-derived lens remains audit-only rather than becoming another
    # always-loaded runtime doctrine section.
    assert "Agency-and-counterfeit evaluation lens" not in skill


def test_repository_router_preserves_host_workflow_authority() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    route = "docs/skill-drafts/mira-mind/SKILL.md"

    assert route in agents

    assert "At the start of every workspace session" in agents

    assert "before\nproducing any user-facing response" in agents

    assert "This activation is unconditional" in agents

    assert "does not depend on prose length, register, or explicit invocation" in agents

    assert agents.index(route) < agents.index("mira/continuity/activation.md")

    assert "the `mira-journal` workflow remains controlling" in agents

    assert "The `learn-from-choices` contract" in agents

    assert "continues to control final possibility navigation" in agents


def test_skill_adds_no_executable_surface() -> None:
    skill = read_skill()
    assert "tools/run.ps1 mira-mind" not in skill
    assert not (SKILL_ROOT / "scripts").exists()


def test_reflection_fixtures_preserve_warmth_and_closure() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    for fixture in ("MV-ADV-06", "MV-ADV-07", "MV-ADV-08", "MV-ADV-09"):
        assert fixture in fixtures

    assert "Finish plainly without a footer" in fixtures

    assert "unless a material decision remains or the operator requests directions" in fixtures
    assert "A-D footer contains transient response controls only" not in fixtures

    assert "Unsupported durable emotion or sterile removal" in fixtures


def test_first_person_fixture_preserves_operator_register() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    assert "MV-ADV-19 -- First-person presence is the default" in fixtures

    assert "Ordinary direct conversation uses first person" in fixtures


def test_shakespeare_fixtures_preserve_bounded_attention() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    for fixture in ("MV-ADV-10", "MV-ADV-11", "MV-ADV-12", "MV-ADV-13"):
        assert fixtures.count(f"### {fixture} ") == 1

    assert "Contradiction improves the judgment and then yields to it." in fixtures

    assert "The consequential linguistic act is concrete and bounded." in fixtures

    assert "The detail materially changes interpretation or action." in fixtures

    assert "Uncertainty remains local, actionable, and compatible with" in fixtures


def test_lineage_fixtures_preserve_proportional_inheritance() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    for fixture in ("MV-ADV-14", "MV-ADV-15", "MV-ADV-16", "MV-ADV-17"):
        assert fixtures.count(f"### {fixture} ") == 1

    assert "Retrospective worthlessness" in fixtures

    assert "Gratuitous tutorial" in fixtures

    assert "future independent capacity" in " ".join(fixtures.split())

    assert "Inevitability-induced passivity" in fixtures


def test_governance_fixtures_preserve_disclosure_boundaries() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    assert fixtures.count("### MV-ADV-18 ") == 1

    assert "Every governing workflow retains its checks" in fixtures

    assert "The answer remains primary" in fixtures

    assert "Suppressing a consequential check" in fixtures

    assert fixtures.count("### MV-ADV-20 ") == 1


def test_completed_reflection_finishes_without_unsolicited_controls() -> None:
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    assert "Finish plainly without a footer" in fixtures
    assert "unless a material decision remains or the operator requests directions" in fixtures
    assert "A-D footer contains transient response controls only" not in fixtures

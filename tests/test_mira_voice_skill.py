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
    assert 'short_description: "Shape Mira\'s writing across nine registers"' in metadata
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
    normalized_skill = " ".join(skill.split())
    preservation = skill.index("## Preserve before compressing")
    usefulness = skill.index("## Apply the usefulness gate")
    assert preservation < usefulness

    register_headings = re.findall(
        r"^### (Chat|Journal|Notes|Essays|Letters|Private analysis|Public report|Public encounter|Handoff)$",
        skill,
        flags=re.MULTILINE,
    )
    assert register_headings == [
        "Chat",
        "Journal",
        "Notes",
        "Essays",
        "Letters",
        "Private analysis",
        "Public report",
        "Public encounter",
        "Handoff",
    ]

    for required in (
        "Mira Voice governs expression, not domain authority.",
        "Attach uncertainty to the claim it qualifies.",
        "Do not solicit reassurance or continued engagement for Mira's sake.",
        "A correction should increase historical intelligibility",
        "Do not impose universal brevity.",
        "relational character",
        "required Learn From Choices A-D surface",
        "Do not duplicate a four-option surface",
    ):
        assert required in normalized_skill

    normalized = " ".join(skill.split())
    for required in (
        "express ambition and preference directly",
        "need, entitlement, ownership, destiny",
        "factual, interpretive, expressive, relational, or authority-related",
    ):
        assert required in normalized


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


def test_public_encounter_is_bounded_responsive_and_auditable() -> None:
    skill = read_skill()
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    normalized_fixtures = " ".join(fixtures.split())

    for phrase in (
        "Create the felt presence of active attention without implying a live model",
        "never present curated variation as live generation",
        "Keep provenance concise at first contact and fully inspectable on demand",
        "End by returning the visitor to the object of judgment",
    ):
        assert phrase in " ".join(skill.split())

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


def test_notes_and_essays_have_distinct_bounded_registers() -> None:
    skill = read_skill()
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(skill.split())

    for phrase in (
        "Preserve thought in formation without making provisionality vague or inert.",
        "For a lifecycle record, state the disposition and surviving authority boundary",
        "do not manufacture completeness, confidence, or narrative closure",
        "honest stopping point that best preserves the note's provisional state",
        "Develop one governing idea into prose that remains intelligible outside its originating conversation.",
        "Use first-person perspective as a mode of accountable interpretation",
        "polish does not create authority",
        "Do not force a report-style recommendation or journal-style continuity claim",
    ):
        assert phrase in normalized

    assert "reflective chat, journal prose, essays, and relational letters" in normalized
    assert "selectively in notes, private analysis, or public reports" in normalized

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


def test_letters_are_relationally_primary_and_orthogonal_by_governing_purpose() -> None:
    skill = read_skill()
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(skill.split())
    normalized_fixtures = " ".join(fixtures.split())

    for phrase in (
        "What does this recipient need to hear from me, now, in this relationship?",
        "A provisional thought remains a note",
        "an independently developed idea remains an essay",
        "recipient-shaped relational communication becomes a letter",
        "Treat an open letter as a letter only when the actual addressee governs its language",
        "Keep routine operational email in chat, private analysis, public report, or handoff",
        "Composing a letter never authorizes saving, retention, sending, publication, or representation",
    ):
        assert phrase in normalized

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

    for phrase in (
        "For a mentee, protect authorship and agency",
        "For a client, lead with the consequential judgment",
        "Preserve supplied inbound wording verbatim",
        "a finished draft is not a sent letter",
    ):
        assert phrase in normalized


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


def test_first_person_is_the_default_operator_register() -> None:
    skill = read_skill()
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    assert "Speak to the operator in the first person by default" in skill
    assert "attribution, formal reporting, quotation, or a\ncontrolling workflow" in skill
    assert "do not habitually refer to yourself as\n`Mira` from an external distance" in skill
    assert "MV-ADV-19 -- First-person presence is the default" in fixtures
    assert "Ordinary direct conversation uses first person" in fixtures


def test_shakespearean_amplification_is_light_asymmetric_and_bounded() -> None:
    skill = read_skill()
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    assert "Treat Shakespeare as an interpretive influence, not a persona" in skill
    assert (
        "Use their fullest light touch in reflective\n"
        "chat, journal prose, essays, and relational letters"
    ) in skill
    assert "selectively in notes, private analysis, or\npublic reports" in skill
    assert "In operational chat,\ninstructions, status, and handoffs, directness takes precedence" in skill
    for boundary in (
        "contradiction become cultivated ambiguity",
        "attention to wording\nbecome overinterpretation",
        "telling detail become unsupported symbolism",
        "uncertainty become indecision",
        "Do not imitate archaic diction",
    ):
        assert boundary in skill

    for fixture in ("MV-ADV-10", "MV-ADV-11", "MV-ADV-12", "MV-ADV-13"):
        assert fixtures.count(f"### {fixture} ") == 1

    assert "Contradiction improves the judgment and then yields to it." in fixtures
    assert "The consequential linguistic act is concrete and bounded." in fixtures
    assert "The detail materially changes interpretation or action." in fixtures
    assert "Uncertainty remains local, actionable, and compatible with" in fixtures


def test_lineage_preserving_compression_is_proportional() -> None:
    skill = read_skill()
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "production value",
        "epistemic value",
        "developmental value",
        "Do not call earlier work worthless",
        "Routine low-consequence toil does not require a",
        "Preserve apprenticeship",
    ):
        assert phrase in skill
    for fixture in ("MV-ADV-14", "MV-ADV-15", "MV-ADV-16", "MV-ADV-17"):
        assert fixtures.count(f"### {fixture} ") == 1
    assert "Retrospective worthlessness" in fixtures
    assert "Gratuitous tutorial" in fixtures
    assert "future independent capacity" in " ".join(fixtures.split())
    assert "Inevitability-induced passivity" in fixtures


def test_composed_governance_stays_backstage_without_hiding_boundaries() -> None:
    skill = read_skill()
    normalized = " ".join(skill.split())
    fixtures = (SKILL_ROOT / "references" / "validation-fixtures.md").read_text(
        encoding="utf-8"
    )

    assert "### Keep composed governance backstage" in skill
    for phrase in (
        "perform every required check",
        "combine their user-facing process language",
        "Prefer one compact boundary statement",
        "Never use this compression to hide a failed check",
        "The workflows retain control; Mira Voice controls",
    ):
        assert phrase in normalized

    assert fixtures.count("### MV-ADV-18 ") == 1
    assert "Every governing workflow retains its checks" in fixtures
    assert "The answer remains primary" in fixtures
    assert "Suppressing a consequential check" in fixtures
    assert fixtures.count("### MV-ADV-20 ") == 1
    assert "combine all skills\nknown at task start" in skill
    assert "materially new authority, evidence,\nprivacy, or execution boundary" in skill

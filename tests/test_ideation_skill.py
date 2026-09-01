from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "docs" / "skill-drafts" / "ideation" / "SKILL.md"


def skill_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def test_ideation_is_repository_local_and_routed() -> None:
    import sys

    scripts_root = ROOT / "scripts"
    if str(scripts_root) not in sys.path:
        sys.path.insert(0, str(scripts_root))

    import codex_skill_registry
    import validate_repository

    skill = skill_text()
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert skill.startswith("---\nname: ideation\n")
    assert "ideation" in validate_repository.LOCAL_SKILLS
    assert "ideation" not in codex_skill_registry.DEPLOYABLE_SKILL_NAMES
    assert "docs/skill-drafts/ideation/SKILL.md" in agents


def test_activation_is_clear_and_excludes_adjacent_workflows() -> None:
    skill = " ".join(skill_text().split())

    for trigger in (
        "explicit `ideation`",
        "brainstorm",
        "explore possibilities",
        "generate options",
        "combine ideas",
        "reframe a problem",
    ):
        assert trigger in skill
    for exclusion in (
        "Routine planning",
        "status reporting",
        "direct factual questions",
        "simple edits",
        "clear execution commands",
    ):
        assert exclusion in skill
    for route in (
        "`intent-recovery`",
        "`elicitation`",
        "evidence-owning research workflow",
        "`learn-from-choices`",
        "`mira-work`",
    ):
        assert route in skill


def test_generation_is_grounded_structured_and_saturation_bounded() -> None:
    skill = skill_text()

    for required in (
        "smallest relevant repository context",
        "Do not browse automatically",
        "Remove duplicates and cosmetic variants",
        "Cluster candidates by the mechanism",
        "Combine compatible ideas",
        "Pressure-test each family",
        "Stop when additional candidates repeat",
        "Never manufacture filler",
        "do not convert the map into a ranking or recommendation",
    ):
        assert required in skill


def test_conversational_map_and_decision_handoffs_are_explicit() -> None:
    skill = skill_text()
    normalized = " ".join(skill.split())

    for field in (
        "Ideation map:",
        "Frame:",
        "Known constraints:",
        "Option families:",
        "Combinations and reframings:",
        "Assumptions and evidence gaps:",
        "Decision handoff:",
        "Preservation handoff:",
    ):
        assert field in skill
    assert "ordinary result is conversational and unsaved" in normalized
    assert "Learn From Choices retains ownership" in skill


def test_genre_handoffs_preserve_form_and_authority() -> None:
    skill = skill_text()
    normalized = " ".join(skill.split())

    assert "`mira-notes` as the ordinary durable route" in skill
    assert "direct `note this` command routes entirely to Mira Notes" in normalized
    assert "`mira-essays` only when one idea should become developed prose" in skill
    assert "direct `essay this` command routes entirely to Mira Essays" in skill
    assert "`mira-letters` only when a named recipient, real relationship, occasion" in skill
    assert "idea map is not a send-ready letter" in skill
    assert "must not infer a recipient, channel, commitment, or delivery authority" in normalized
    assert "Do not duplicate identical text across genres" in normalized
    assert "Transformation transfers no evidence, identity" in skill
    assert "`final-for-operator` never authorizes sending" in normalized


def test_recursive_learning_requires_real_later_use() -> None:
    skill = skill_text()
    recursive = (
        ROOT / "docs" / "skill-drafts" / "recursive-learn" / "SKILL.md"
    ).read_text(encoding="utf-8")

    for contract in (skill, recursive):
        normalized = " ".join(contract.split())
        for boundary in (
            "operator praise",
            "passing implementation tests",
            "task class",
            "baseline",
            "observable measure",
            "persistent intervention",
            "independent validation",
            "later comparable use",
            "same metric and unit",
            "observation-only",
            "partial-candidate",
            "exact digest-bound",
        ):
            assert boundary in normalized
    assert "genre label proves nothing" in " ".join(skill.split())
    assert "Ideation creates no telemetry" in recursive


def test_ideation_grants_no_execution_or_persistence_authority() -> None:
    skill = " ".join(skill_text().split())

    for boundary in (
        "read-only reasoning",
        "grants no authority to browse, mutate, save, stage, commit, push",
        "publish, deploy, communicate, spend, admit evidence",
        "creates no telemetry",
        "process-reference type",
        "ledger entries",
    ):
        assert boundary in skill

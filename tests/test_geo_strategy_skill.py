from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "docs" / "skill-drafts" / "geo-strategy" / "SKILL.md"


def read_skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def test_geo_strategy_choice_acceleration_policy_is_present() -> None:
    text = read_skill()
    normalized = " ".join(text.split())

    assert "## Choice Acceleration Policy" in text
    assert "exactly four `A`-`D` options" in text
    assert "internal library of 10-20 next-best epistemic moves" in text
    assert "crisis consequence" in text
    assert "evidence gap" in text
    assert "forecast leverage" in text
    assert "verification need" in text
    assert "decision readiness" in text
    assert "collapse the surface to the narrowest concrete workflow" in normalized


def test_geo_strategy_internal_move_library_covers_expected_cases() -> None:
    text = read_skill()
    expected_moves = {
        "intake coverage audit",
        "same-object voice comparison",
        "mechanism spine extraction",
        "competing mechanism test",
        "operational-claim triage",
        "reality-check handoff",
        "original-language source search",
        "forecast-hook extraction",
        "counterevidence pass",
        "actor constraint map",
        "escalation ladder map",
        "decision implication compression",
        "public-use boundary",
        "daily packet build",
        "verification packet draft",
        "pause/hold with explicit unresolved gate",
    }

    for move in expected_moves:
        assert move in text


def test_geo_strategy_preserves_verification_and_authority_boundaries() -> None:
    text = read_skill()
    normalized = " ".join(text.split())

    assert "route factual adjudication through external-knowledge `reality-check`" in normalized
    assert "archive testimony as verified fact" in text
    assert "does not grant authority to browse" in normalized
    assert "create verification packets" in normalized
    assert "admit `OPC-*`/`CLM-*`/`NG-*` records" in normalized
    assert "publish" in normalized
    assert "assign operational truth" in normalized
    assert "`Stage`, `Commit`, `Push`, `Publish`, `Deploy`, `Send`" in text


def test_geo_strategy_deprecates_legacy_five_option_menu() -> None:
    text = read_skill()
    normalized = " ".join(text.split())

    assert "legacy five-option menu is deprecated" in normalized
    assert "return exactly four `A`-`D` options" in text
    assert "`E` execute the full stack" not in text

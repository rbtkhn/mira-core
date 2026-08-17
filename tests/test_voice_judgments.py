from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from scripts import voice_judgments


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import voice_indexes


def registry() -> dict:
    return copy.deepcopy(voice_judgments.load_registry())


def test_canonical_registry_and_generated_views_validate() -> None:
    assert voice_judgments.validate_registry() == []
    outputs = voice_judgments.expected_outputs()
    judgment_views = [path for path in outputs if path.name == "judgment-ledger.md"]
    assert len(judgment_views) == 15
    assert voice_judgments.VOICES_ROOT / "jermy" / "judgment-ledger.md" in outputs
    assert "VR-20260301-02" in outputs[voice_judgments.VOICES_ROOT / "jermy" / "judgment-ledger.md"]
    assert voice_judgments.VOICES_ROOT / "mario-nawfal" / "judgment-ledger.md" not in outputs
    assert "VR-20260316-01" not in outputs[voice_judgments.VOICES_ROOT / "johnson" / "judgment-ledger.md"]
    assert "VR-20260531-03" not in outputs[voice_judgments.VOICES_ROOT / "diesen" / "judgment-ledger.md"]
    assert "VR-20260423-01" not in outputs[voice_judgments.VOICES_ROOT / "mercouris" / "judgment-ledger.md"]
    assert "VJ-MEARSHEIMER-0001" in outputs[
        voice_judgments.VOICES_ROOT / "mearsheimer" / "judgment-ledger.md"
    ]


def test_registry_rejects_unscoped_or_missing_sources_and_copied_outcomes() -> None:
    data = registry()
    version = data["judgments"][0]["versions"][0]
    version["source_refs"] = ["SRC-01"]
    version["outcome"] = "supported"
    failures = voice_judgments.validate_registry(data)
    assert any("canonical archive path" in failure for failure in failures)
    assert any("forbidden copied authority field outcome" in failure for failure in failures)


def test_registry_rejects_duplicate_versions_bad_aliases_and_broken_revision_refs() -> None:
    data = registry()
    judgment = data["judgments"][0]
    judgment["legacy_ids"] = ["STATE-bad"]
    duplicate = copy.deepcopy(judgment["versions"][0])
    judgment["versions"].append(duplicate)
    judgment["versions"][0]["revision_refs"] = ["VR-20990101-01"]
    failures = voice_judgments.validate_registry(data)
    assert any("malformed legacy alias" in failure for failure in failures)
    assert any("duplicate version ID" in failure for failure in failures)
    assert any("revision reference does not resolve" in failure for failure in failures)


def test_reality_outcome_is_resolved_at_render_time_not_stored() -> None:
    data = registry()
    judgment = data["judgments"][0]
    claim_id = sorted(voice_judgments.reality_claims())[0]
    judgment["versions"][0]["reality_claim_refs"] = [claim_id]
    claims = voice_judgments.reality_claims()
    revisions = voice_judgments.all_revision_entries()
    first = voice_judgments.render_voice(
        judgment["voice_slug"], data, revisions, claims, {claim_id: {"outcome": "supported", "status": "provisional_assessed"}}
    )
    second = voice_judgments.render_voice(
        judgment["voice_slug"], data, revisions, claims, {claim_id: {"outcome": "contested", "status": "canonical_assessed"}}
    )
    assert "`supported`" in first
    assert "`contested`" in second
    assert data["judgments"][0]["versions"][0].get("outcome") is None


def test_ng_forecast_links_render_as_non_attributive_references() -> None:
    rendered = voice_judgments.render_voice(
        "crooke",
        registry(),
        voice_judgments.all_revision_entries(),
        voice_judgments.reality_claims(),
        voice_judgments.reality_assessments(),
    )

    assert "Related NG Forecasts (Reference Only)" in rendered
    assert "It does not mean the voice authored or adopted that forecast" in rendered
    assert "its score does not apply to the voice judgment" in rendered
    assert "| Judgment | Formal Forecasts |" not in rendered


def test_revision_adjudication_context_is_resolved_at_render_time() -> None:
    data = registry()
    revisions = voice_judgments.all_revision_entries()
    rendered = voice_judgments.render_voice(
        "ritter",
        data,
        revisions,
        voice_judgments.reality_claims(),
        voice_judgments.reality_assessments(),
    )
    assert "| Revision | Date | Class | Judgment Links |" in rendered
    assert "| Revision | Date | Class | Prior View |" not in rendered
    assert "### Revision Details" in rendered
    assert "#### `VR-20260514-01`" in rendered
    assert "- **Prior View:**" in rendered
    assert "- **Revised View:**" in rendered
    assert "- **Source:**" in rendered
    assert "- **Canonical Context:**" in rendered
    assert "linked duplicate chain rather than an independent analytical update" in rendered

    changed_revisions = copy.deepcopy(revisions)
    may_revision = next(item for item in changed_revisions if item["id"] == "VR-20260514-01")
    may_revision["adjudication_note"] = "Changed canonical revision context."
    changed = voice_judgments.render_voice(
        "ritter",
        data,
        changed_revisions,
        voice_judgments.reality_claims(),
        voice_judgments.reality_assessments(),
    )
    assert "Changed canonical revision context." in changed
    assert "Changed canonical revision context." not in rendered
    assert "adjudication_note" not in json.dumps(data)


def test_revision_details_scale_as_blocks_for_high_volume_voice() -> None:
    rendered = voice_judgments.render_voice(
        "mercouris",
        registry(),
        voice_judgments.all_revision_entries(),
        voice_judgments.reality_claims(),
        voice_judgments.reality_assessments(),
    )

    assert rendered.count("#### `VR-") == 7
    assert rendered.count("- **Canonical Context:**") == 7


def test_legacy_state_stub_preserves_anchor_and_redirects() -> None:
    data = registry()
    judgment = data["judgments"][0]
    stub = voice_judgments.render_state_stub(judgment["voice_slug"], [judgment])
    alias = judgment["legacy_ids"][0]
    assert f'id="{alias.lower()}"' in stub
    assert "judgment-ledger.md" in stub
    assert "No substantive state is maintained" in stub


def test_voice_judgment_command_surface_validates_and_views_are_current() -> None:
    for arguments, marker in (
        (["validate"], "voice_judgment_failures=0"),
        (["render", "--check"], "voice_judgment_views=current"),
        (["migrate-state", "--check"], "voice judgment migration check passed"),
    ):
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "tools" / "run_repo.py"),
                "voice-judgment",
                *arguments,
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert marker in result.stdout


def test_pape_renderer_preserves_judgment_navigation(tmp_path: Path) -> None:
    index = (
        tmp_path
        / "narrative-geopolitics"
        / "voices"
        / "pape"
        / "source-index.md"
    )
    index.parent.mkdir(parents=True)
    source_text = (
        "# Pape Source Index\n\n"
        "Corpus: 0 authored sources, 0 guest appearances, 0 total imported sources.\n\n"
        "## 2026-07\n"
    )
    row = {
        "local_path": "archive/geopolitics/sources/2026-07-10/source.md",
        "date": "2026-07-10",
        "title": "Pape renderer fixture",
        "modality": "essay",
        "source_class": "authored",
        "voice_slugs": ["pape"],
        "host_slug": "pape",
    }

    rendered, _ = voice_indexes.render_pape(
        index,
        source_text,
        [row],
        repo_root=tmp_path,
    )

    assert voice_indexes.JUDGMENT_LEDGER_NAVIGATION in rendered
    assert "[judgment-ledger.md](judgment-ledger.md)" in rendered


def test_registry_json_never_contains_copied_reality_outcomes() -> None:
    text = json.dumps(voice_judgments.load_registry())
    for forbidden in ("assessment_status", "reality_outcome", "forecast_score"):
        assert f'"{forbidden}"' not in text


def test_pape_voice_local_hooks_are_split_by_judgment_class() -> None:
    data = registry()
    pape = {
        version["unresolved_forecast_refs"][0]: item
        for item in data["judgments"]
        if item["voice_slug"] == "pape"
        for version in item["versions"]
        if version.get("unresolved_forecast_refs")
    }

    assert set(pape) >= {
        "PAPE-2026-F001",
        "PAPE-2026-F010",
        "PAPE-2026-F015",
        "PAPE-2026-F023",
        "PAPE-2026-F030",
    }
    assert pape["PAPE-2026-F001"]["class"] == "mechanism"
    assert pape["PAPE-2026-F010"]["class"] == "mechanism"
    assert pape["PAPE-2026-F015"]["class"] == "forecast_expression"
    assert pape["PAPE-2026-F023"]["class"] == "strategic_assessment"
    assert pape["PAPE-2026-F030"]["class"] == "mechanism"


def test_pape_generated_ledger_preserves_unscored_hook_boundary() -> None:
    rendered = voice_judgments.render_voice(
        "pape",
        registry(),
        voice_judgments.all_revision_entries(),
        voice_judgments.reality_claims(),
        voice_judgments.reality_assessments(),
    )

    for hook_id in (
        "PAPE-2026-F001",
        "PAPE-2026-F010",
        "PAPE-2026-F015",
        "PAPE-2026-F023",
        "PAPE-2026-F030",
    ):
        assert hook_id in rendered
    assert "Voice-local forecast expressions remain unscored in this ledger" in rendered
    assert "Related NG Forecasts (Reference Only)" in rendered
    assert "does not adjudicate the underlying world claim" in rendered

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


integrity = load_module("repository_integrity_tests", SCRIPTS_ROOT / "validate_repository.py")
skill_registry = load_module("skill_registry_tests", SCRIPTS_ROOT / "codex_skill_registry.py")


def test_current_repository_integrity_is_clean() -> None:
    assert integrity.validate_repository() == []


def test_manifest_count_mismatch_is_detected(monkeypatch, tmp_path: Path) -> None:
    archive = tmp_path / "narrative-geopolitics" / "archive"
    source_dir = archive / "sources" / "2026-07-09"
    source_dir.mkdir(parents=True)
    source = source_dir / "source-a.md"
    source.write_text("source\n", encoding="utf-8")
    manifest = {
        "source_count": 2,
        "sources": [
            {
                "date": "2026-07-09",
                "local_path": "narrative-geopolitics/archive/sources/2026-07-09/source-a.md",
            }
        ],
    }
    manifest_path = archive / "source-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(integrity, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(integrity, "ARCHIVE_SOURCES", archive / "sources")
    monkeypatch.setattr(integrity, "MANIFEST_PATH", manifest_path)

    assert integrity.archive_manifest_failures() == [
        "manifest source_count=2 but rows=1"
    ]


def test_forecast_triage_mismatch_is_detected(monkeypatch, tmp_path: Path) -> None:
    ledger = tmp_path / "forecast-ledger.md"
    ledger.write_text(
        "| `NG-20260707-F01` | `2026-07-07` | Object | Claim | `likely` | `2026-07-20` | [run](x) | `open` |\n\n"
        "## Accountability Triage\n\n"
        "| `NG-20260708-F01` | `2026-07-08` | `runtime_date` | `ex_ante` | `open` | `yes` | Review. |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(integrity, "LEDGER_PATH", ledger)

    failures = integrity.forecast_ledger_failures()

    assert "forecast entry missing triage row: NG-20260707-F01" in failures
    assert "forecast triage row missing entry: NG-20260708-F01" in failures


def test_unregistered_legacy_verification_packet_is_rejected(
    monkeypatch, tmp_path: Path
) -> None:
    packets = tmp_path / "packets"
    (packets / "VER-20990101-01-new").mkdir(parents=True)
    inventory = tmp_path / "legacy-inventory.json"
    inventory.write_text('{"schema_version": 1, "packets": []}\n', encoding="utf-8")
    monkeypatch.setattr(integrity, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(integrity, "LEGACY_VERIFICATION_ROOT", packets)
    monkeypatch.setattr(integrity, "LEGACY_VERIFICATION_INVENTORY", inventory)

    assert integrity.legacy_verification_inventory_failures() == [
        "unregistered legacy-only verification packet: packets/VER-20990101-01-new"
    ]


def test_broken_non_archive_markdown_link_is_detected(monkeypatch, tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "readme.md").write_text("[missing](missing.md)\n", encoding="utf-8")
    ng_root = tmp_path / "narrative-geopolitics"
    ng_root.mkdir()
    predictive = tmp_path / "predictive-history"
    predictive.mkdir()
    monkeypatch.setattr(integrity, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(integrity, "NG_ROOT", ng_root)
    monkeypatch.setattr(integrity, "ARCHIVE_SOURCES", ng_root / "archive" / "sources")

    assert integrity.markdown_link_failures() == [
        "broken Markdown link: docs/readme.md -> missing.md"
    ]


def test_broken_historical_entropy_markdown_link_is_detected(
    monkeypatch, tmp_path: Path
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    ng_root = tmp_path / "narrative-geopolitics"
    ng_root.mkdir()
    predictive = tmp_path / "predictive-history"
    predictive.mkdir()
    historical_entropy = tmp_path / "historical-entropy"
    historical_entropy.mkdir()
    (historical_entropy / "README.md").write_text(
        "[missing packet](lectures/missing/README.md)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(integrity, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(integrity, "NG_ROOT", ng_root)
    monkeypatch.setattr(integrity, "ARCHIVE_SOURCES", ng_root / "archive" / "sources")

    assert integrity.markdown_link_failures() == [
        "broken Markdown link: historical-entropy/README.md -> "
        "lectures/missing/README.md"
    ]


def test_sibling_markdown_roots_remain_checked_when_historical_entropy_is_empty(
    monkeypatch, tmp_path: Path
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    ng_root = tmp_path / "narrative-geopolitics"
    ng_root.mkdir()
    predictive = tmp_path / "predictive-history"
    predictive.mkdir()
    historical_entropy = tmp_path / "historical-entropy"
    historical_entropy.mkdir()
    (predictive / "README.md").write_text("[missing](missing.md)\n", encoding="utf-8")
    monkeypatch.setattr(integrity, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(integrity, "NG_ROOT", ng_root)
    monkeypatch.setattr(integrity, "ARCHIVE_SOURCES", ng_root / "archive" / "sources")

    assert integrity.markdown_link_failures() == [
        "broken Markdown link: predictive-history/README.md -> missing.md"
    ]


def test_reader_facing_title_contract_rejects_placeholder_and_missing_rationale(
    monkeypatch, tmp_path: Path
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    ng_root = tmp_path / "narrative-geopolitics"
    briefs = ng_root / "public" / "briefs"
    briefs.mkdir(parents=True)
    predictive = tmp_path / "predictive-history"
    predictive.mkdir()
    bad = briefs / "bad.md"
    bad.write_text(
        "# [Working title]\n\nTitle standard: `reader-facing`\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(integrity, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(integrity, "NG_ROOT", ng_root)
    monkeypatch.setattr(integrity, "ARCHIVE_SOURCES", ng_root / "archive" / "sources")
    monkeypatch.setattr(integrity, "PUBLIC_BRIEFS_ROOT", briefs)

    failures = integrity.editorial_title_failures()

    assert any("placeholder title" in item for item in failures)
    assert any("missing substantive title rationale" in item for item in failures)


def test_reader_facing_title_contract_accepts_compressed_argument(
    monkeypatch, tmp_path: Path
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    ng_root = tmp_path / "narrative-geopolitics"
    briefs = ng_root / "public" / "briefs"
    briefs.mkdir(parents=True)
    predictive = tmp_path / "predictive-history"
    predictive.mkdir()
    good = briefs / "good.md"
    good.write_text(
        "# The Burden of Normalizing Hormuz\n\n"
        "Title standard: `reader-facing`\n\n"
        "Title rationale: `Names the asymmetric burden that structures the central judgment of the brief.`\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(integrity, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(integrity, "NG_ROOT", ng_root)
    monkeypatch.setattr(integrity, "ARCHIVE_SOURCES", ng_root / "archive" / "sources")
    monkeypatch.setattr(integrity, "PUBLIC_BRIEFS_ROOT", briefs)

    assert integrity.editorial_title_failures() == []


def test_reader_facing_contract_rejects_generic_analytical_heading(
    monkeypatch, tmp_path: Path
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    ng_root = tmp_path / "narrative-geopolitics"
    briefs = ng_root / "public" / "briefs"
    briefs.mkdir(parents=True)
    predictive = tmp_path / "predictive-history"
    predictive.mkdir()
    bad = briefs / "generic-heading.md"
    bad.write_text(
        "# The Burden of Normalizing Hormuz\n\n"
        "Title standard: `reader-facing`\n\n"
        "Title rationale: `Names the asymmetric burden that structures the central judgment of the brief.`\n\n"
        "## Analysis\n\nBody.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(integrity, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(integrity, "NG_ROOT", ng_root)
    monkeypatch.setattr(integrity, "ARCHIVE_SOURCES", ng_root / "archive" / "sources")
    monkeypatch.setattr(integrity, "PUBLIC_BRIEFS_ROOT", briefs)

    assert integrity.editorial_title_failures() == [
        "reader-facing document uses generic analytical heading: "
        "narrative-geopolitics/public/briefs/generic-heading.md -> Analysis"
    ]


def test_operationally_supported_claim_requires_packet_link(monkeypatch, tmp_path: Path) -> None:
    ng_root = tmp_path / "narrative-geopolitics"
    brief = ng_root / "public" / "briefs" / "claim.md"
    brief.parent.mkdir(parents=True)
    brief.write_text("# Claim\n\nOperational status: `operationally_supported`\n", encoding="utf-8")
    monkeypatch.setattr(integrity, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(integrity, "NG_ROOT", ng_root)
    monkeypatch.setattr(integrity, "ARCHIVE_SOURCES", ng_root / "archive" / "sources")
    monkeypatch.setattr(integrity.verification_packets, "VERIFICATION_ROOT", ng_root / "work" / "verification")

    assert integrity.operational_claim_failures() == [
        "operationally supported claim missing verification packet: narrative-geopolitics/public/briefs/claim.md"
    ]


def test_analytical_interface_templates_preserve_required_prompts() -> None:
    method = (
        REPO_ROOT / "narrative-geopolitics" / "method" / "analytical-interfaces.md"
    ).read_text(encoding="utf-8")
    synthesis = (
        REPO_ROOT / "narrative-geopolitics" / "templates" / "synthesis.md"
    ).read_text(encoding="utf-8")
    forecast = (
        REPO_ROOT / "narrative-geopolitics" / "templates" / "forecast.md"
    ).read_text(encoding="utf-8")
    dialogue = (
        REPO_ROOT / "narrative-geopolitics" / "work" / "dialogues" / "_template.md"
    ).read_text(encoding="utf-8")
    voice = (
        REPO_ROOT / "narrative-geopolitics" / "voices" / "_template.md"
    ).read_text(encoding="utf-8")

    assert "Every analytical label should help the next reader recover the judgment" in method
    assert "Crisis object:" in synthesis
    assert "Causal mechanism" in forecast
    assert "Resolution criteria" in forecast
    assert "Analytical question:" in dialogue
    assert "Recurring intellectual operation expressed as a verb phrase" in voice


def test_only_portable_skills_are_deployable() -> None:
    assert set(skill_registry.DEPLOYABLE_SKILL_NAMES) == {
        "best-intake",
        "learn-from-choices",
        "smart-intake",
        "voice-comparison",
        "geopolitical-synthesis",
        "reality-check",
        "voice-accountability",
    }
    assert set(skill_registry.build_registry()) == {
        "best-intake",
        "learn-from-choices",
        "smart-intake",
        "voice-comparison",
        "geopolitical-synthesis",
        "reality-check",
        "voice-accountability",
    }


@pytest.mark.parametrize("skill_name", ["coffee", "dream", "world-monitor"])
def test_local_skill_frontmatter_is_minimal(skill_name: str) -> None:
    text = (
        REPO_ROOT / "docs" / "skill-drafts" / skill_name / "SKILL.md"
    ).read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    keys = {
        line.split(":", 1)[0]
        for line in frontmatter.splitlines()
        if line.strip() and ":" in line
    }
    assert keys == {"name", "description"}


def test_cadence_handoff_is_ignored() -> None:
    result = subprocess.run(
        [
            "git",
            "check-ignore",
            "narrative-geopolitics/work/cadence/last-dream.json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_local_cadence_triggers_are_discoverable() -> None:
    router = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "docs/skill-drafts/coffee/SKILL.md" in router
    assert "docs/skill-drafts/dream/SKILL.md" in router


def test_scaffold_empty_is_a_no_write_compatibility_flag() -> None:
    target = REPO_ROOT / "narrative-geopolitics" / "work" / "daily" / "2099-01-01"
    assert not target.exists()
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "geopolitical_synthesis.py"),
            "--date",
            "2099-01-01",
            "--scaffold-empty",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "DEPRECATED --scaffold-empty writes nothing" in result.stdout
    assert not target.exists()


def test_range_mode_skips_empty_dates_without_writes() -> None:
    targets = [
        REPO_ROOT / "narrative-geopolitics" / "work" / "daily" / value
        for value in ("2099-01-01", "2099-01-02")
    ]
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_ROOT / "geopolitical_synthesis.py"),
            "--start-date",
            "2099-01-01",
            "--end-date",
            "2099-01-02",
            "--scaffold-empty",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.count("SKIP no manifest rows; no daily files written") == 2
    assert all(not target.exists() for target in targets)


@pytest.mark.parametrize(
    "script_name",
    [
        "bootstrap_daily_run.py",
        "validate_daily_run.py",
        "sync_forecast_ledger.py",
        "triage_forecast_ledger.py",
        "process_daily_stack.py",
        "geopolitical_synthesis.py",
        "geo_synthesis.py",
        "canonicalize_voice_metadata.py",
        "sync_voice_indexes.py",
        "verification.py",
    ],
)
def test_existing_cli_filename_remains_available(script_name: str) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_ROOT / script_name), "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

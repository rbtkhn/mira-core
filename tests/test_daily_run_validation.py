from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = load_module("daily_run_validator_tests", REPO_ROOT / "scripts" / "validate_daily_run.py")


def configure_fixture(monkeypatch, tmp_path: Path, sources_text: str) -> None:
    ng_root = tmp_path / "narrative-geopolitics"
    daily_root = ng_root / "work" / "daily"
    ledger_path = ng_root / "work" / "forecasts" / "forecast-ledger.md"
    archive_root = tmp_path / "archive" / "sources" / "geopolitics"
    manifest_path = archive_root / "source-manifest.json"
    run_dir = daily_root / "2026-07-09"
    source_dir = archive_root / "sources" / "2026-07-09"
    run_dir.mkdir(parents=True)
    source_dir.mkdir(parents=True)
    ledger_path.parent.mkdir(parents=True)

    rows = []
    for name in ("source-a.md", "source-b.md"):
        local_path = f"archive/sources/geopolitics/sources/2026-07-09/{name}"
        rows.append({"date": "2026-07-09", "local_path": local_path})
        (source_dir / name).write_text("source\n", encoding="utf-8")
    manifest_path.write_text(json.dumps({"sources": rows}), encoding="utf-8")
    (run_dir / "sources.md").write_text(sources_text, encoding="utf-8")
    for name in ("synthesis.md", "forecast.md", "daily-brief.md"):
        (run_dir / name).write_text("Status: `draft`\n", encoding="utf-8")
    (run_dir / "judgment.md").write_text(
        """# Accountable Judgment — 2026-07-09

Status: `draft`
As-of: `2026-07-09`
Crisis object: `test-object`
Review date: `2026-07-16`

## Load-Bearing Judgments

1. The test judgment is bounded and operationally modest.

## Confidence Boundary

Confidence: `medium`

What this judgment depends on: `test evidence boundary`

What would make it wrong: `test disconfirmation`

## Support and Dissent

Strongest supporting sources and voices: `SRC-01`

Strongest counterevidence or dissent: `test counterevidence`

## Claim and Forecast Dependencies

- Reality claims: `none`
- Forecast hooks: `none`
- Operational or causal dependencies: `none`

## Next Observable Signals

- Test signal in the review window.

## Decision / Public-use Implication

`internal only`

## Decision Compression

What changed: The test packet adds a bounded daily change.

Reusable mechanism: Test evidence changes operator attention without establishing a verified fact.

Decision implication: Preserve the source set and review the test signal before promotion.

Evidence still missing: Independent corroboration and a dated falsifier.

Recommended disposition: `synthesis-use`
""",
        encoding="utf-8",
    )
    ledger_path.write_text("# Ledger\n", encoding="utf-8")

    monkeypatch.setattr(validator, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(validator, "NG_ROOT", ng_root)
    monkeypatch.setattr(validator, "MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(validator, "DAILY_ROOT", daily_root)
    monkeypatch.setattr(validator, "LEDGER_PATH", ledger_path)


def complete_sources_text(selected_subset: bool = False) -> str:
    selected = (
        "\n## Run Source Set\n"
        "| Source ID | Archive Path |\n"
        "| --- | --- |\n"
        "| `SRC-01` | [A](../../../../archive/sources/geopolitics/sources/2026-07-09/source-a.md) |\n"
        if selected_subset
        else "\n## Run Source Set\n| Source ID | Archive Path |\n| --- | --- |\n| `SRC-01` | [A](../../../../archive/sources/geopolitics/sources/2026-07-09/source-a.md) |\n"
    )
    return (
        "Status: `live-intake-first`\n\n"
        "## Intake Batch\n"
        "| Source File | Type |\n"
        "| --- | --- |\n"
        "| `archive/sources/geopolitics/sources/2026-07-09/source-a.md` | transcript |\n"
        "| `archive/sources/geopolitics/sources/2026-07-09/source-b.md` | transcript |\n"
        + selected
    )


def test_intake_stage_reports_stale_after_sources_land(monkeypatch, tmp_path: Path) -> None:
    configure_fixture(
        monkeypatch,
        tmp_path,
        "Status: `placeholder`\n\nThis day is awaiting intake.\n",
    )

    result = validator.validate_run("2026-07-09", "intake")

    assert result["state"] == "stale-after-intake"
    assert result["failures"] == []
    assert any("refresh required" in warning for warning in result["warnings"])


def test_synthesis_stage_blocks_stale_after_intake(monkeypatch, tmp_path: Path) -> None:
    configure_fixture(
        monkeypatch,
        tmp_path,
        "Status: `placeholder`\n\nThis day is awaiting intake.\n",
    )

    result = validator.validate_run("2026-07-09", "synthesis")

    assert result["state"] == "stale-after-intake"
    assert any("refresh required" in failure for failure in result["failures"])
    assert sum("missing manifest day source" in failure for failure in result["failures"]) == 2


def test_historical_synthesis_without_delta_contract_is_grandfathered(
    monkeypatch, tmp_path: Path
) -> None:
    configure_fixture(monkeypatch, tmp_path, complete_sources_text())
    synthesis = (
        tmp_path / "narrative-geopolitics" / "work" / "daily" / "2026-07-09" / "synthesis.md"
    )
    synthesis.write_text("Status: `draft`\n\nHistorical packet.\n", encoding="utf-8")

    result = validator.validate_run("2026-07-09", "synthesis")

    assert not any("Distinctive Contribution" in item for item in result["failures"])


def test_delta_contract_allows_explicit_archive_only_disposition(
    monkeypatch, tmp_path: Path
) -> None:
    configure_fixture(monkeypatch, tmp_path, complete_sources_text())
    synthesis = (
        tmp_path / "narrative-geopolitics" / "work" / "daily" / "2026-07-09" / "synthesis.md"
    )
    synthesis.write_text(
        "Status: `draft`\n\nSynthesis contract: `delta-v1`\n\n"
        "## Distinctive Contribution\n\n"
        "Comparison window: `2026-07-08`\n\n"
        "New contribution: A genuinely new contradiction.\n\n"
        "Disposition: `archive-only`\n",
        encoding="utf-8",
    )

    result = validator.validate_run("2026-07-09", "synthesis")

    assert not any("archive-only delta-v1" in item for item in result["failures"])


def test_delta_contract_rejects_unresolved_distinctive_contribution(
    monkeypatch, tmp_path: Path
) -> None:
    configure_fixture(monkeypatch, tmp_path, complete_sources_text())
    synthesis = (
        tmp_path / "narrative-geopolitics" / "work" / "daily" / "2026-07-09" / "synthesis.md"
    )
    synthesis.write_text(
        "Status: `draft`\n\nSynthesis contract: `delta-v1`\n\n"
        "## Distinctive Contribution\n\n"
        "Compared with: [prior date]\n\n"
        "New contribution: [name the new mechanism]\n\n"
        "Disposition: `daily-packet`\n\n"
        "## Primary Voices\n\n"
        "| Voice | Role | Adds | Risk |\n| --- | --- | --- | --- |\n"
        "| Analyst | mechanism | comparison | source risk |\n"
        "| Analyst 2 | pressure | dissent | source risk |\n\n"
        "## Issue Story Desk\n\n"
        "| Story ID | Placement |\n| --- | --- |\n"
        "| `NGI-20260709-S01` | `lead` |\n",
        encoding="utf-8",
    )

    result = validator.validate_run("2026-07-09", "synthesis")

    assert any("unresolved synthesis placeholders" in item for item in result["failures"])


def test_exact_intake_coverage_is_ready(monkeypatch, tmp_path: Path) -> None:
    configure_fixture(monkeypatch, tmp_path, complete_sources_text())

    result = validator.validate_run("2026-07-09", "synthesis")

    assert not any("Decision Compression" in item for item in result["failures"])
    assert result["state"] == "ready"
    assert result["failures"] == []
    assert result["landed_sources"] == 2
    assert result["consumed_sources"] == 2


def test_manifest_backed_unhydrated_day_is_valid(monkeypatch, tmp_path: Path) -> None:
    configure_fixture(monkeypatch, tmp_path, complete_sources_text())
    source_dir = tmp_path / "archive" / "sources" / "geopolitics" / "sources" / "2026-07-09"
    for source_path in source_dir.glob("*.md"):
        source_path.unlink()

    result = validator.validate_run("2026-07-09", "intake")

    assert result["landed_sources"] == 0
    assert not any("missing archive source file" in item for item in result["failures"])
    assert not any("links missing archive file" in item for item in result["warnings"])


def test_compression_rejects_missing_disposition(monkeypatch, tmp_path: Path) -> None:
    configure_fixture(monkeypatch, tmp_path, complete_sources_text())
    path = tmp_path / "narrative-geopolitics" / "work" / "daily" / "2026-07-09" / "judgment.md"
    path.write_text(path.read_text(encoding="utf-8").replace("Recommended disposition: `synthesis-use`", "Recommended disposition:"), encoding="utf-8")

    result = validator.validate_run("2026-07-09", "synthesis")

    assert any("recommended disposition" in item for item in result["failures"])


def test_compression_rejects_unresolved_reference(monkeypatch, tmp_path: Path) -> None:
    configure_fixture(monkeypatch, tmp_path, complete_sources_text())
    path = tmp_path / "narrative-geopolitics" / "work" / "daily" / "2026-07-09" / "judgment.md"
    path.write_text(path.read_text(encoding="utf-8").replace("Evidence still missing:", "Evidence still missing: see `VER-20990101-99`"), encoding="utf-8")

    result = validator.validate_run("2026-07-09", "synthesis")

    assert "judgment.md reference does not resolve: VER-20990101-99" in result["failures"]

def test_selected_run_source_set_may_be_subset(monkeypatch, tmp_path: Path) -> None:
    configure_fixture(monkeypatch, tmp_path, complete_sources_text(selected_subset=True))

    result = validator.validate_run("2026-07-09", "synthesis")

    assert result["state"] == "ready"
    assert result["failures"] == []


def test_historical_pressure_rejects_private_paths_and_unknown_library_refs(monkeypatch, tmp_path: Path) -> None:
    configure_fixture(monkeypatch, tmp_path, complete_sources_text())
    library = tmp_path / "archive" / "library"
    library.mkdir(parents=True)
    (library / "library-registry.json").write_text(json.dumps({"sources": []}), encoding="utf-8")
    synthesis = tmp_path / "narrative-geopolitics" / "work" / "daily" / "2026-07-09" / "synthesis.md"
    synthesis.write_text(
        "## Historical Pressure Test\n\n`LIB-NOT-REGISTERED`\n\nC:/private/library/passage.txt\n",
        encoding="utf-8",
    )
    failures = validator.historical_pressure_failures("2026-07-09")
    assert "synthesis.md exposes a private Library path" in failures
    assert "daily artifact Library reference does not resolve: LIB-NOT-REGISTERED" in failures


def test_historical_pressure_accepts_registered_source_and_body_refs(monkeypatch, tmp_path: Path) -> None:
    configure_fixture(monkeypatch, tmp_path, complete_sources_text())
    library = tmp_path / "archive" / "library"
    library.mkdir(parents=True)
    (library / "library-registry.json").write_text(
        json.dumps({"sources": [{"source_id": "LIB-SOURCE", "text_bodies": [{"body_id": "LIB-BODY"}]}]}),
        encoding="utf-8",
    )
    sources = tmp_path / "narrative-geopolitics" / "work" / "daily" / "2026-07-09" / "sources.md"
    sources.write_text(complete_sources_text() + "\n`LIB-SOURCE` `LIB-BODY`\n", encoding="utf-8")
    assert validator.historical_pressure_failures("2026-07-09") == []

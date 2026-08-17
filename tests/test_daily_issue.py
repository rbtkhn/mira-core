from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

spec = importlib.util.spec_from_file_location("daily_issue_tests", SCRIPTS_ROOT / "render_daily_issue.py")
assert spec is not None
assert spec.loader is not None
issue = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = issue
spec.loader.exec_module(issue)


RUN_DATE = "2026-07-09"
HOOK_ID = "NG-20260709-F01"


def fixture_tree(tmp_path: Path, *, hook_in_day: bool = True, placeholder: bool = False) -> tuple[Path, Path]:
    ng_root = tmp_path / "narrative-geopolitics"
    daily_root = ng_root / "work" / "daily"
    run_dir = daily_root / RUN_DATE
    archive_root = tmp_path / "archive" / "geopolitics"
    archive_dir = archive_root / "sources" / RUN_DATE
    ledger_path = ng_root / "work" / "forecasts" / "forecast-ledger.md"
    run_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    ledger_path.parent.mkdir(parents=True)

    archive_path = archive_dir / "source-a.md"
    archive_path.write_text("# Source A\n", encoding="utf-8")
    manifest = {
        "sources": [{"date": RUN_DATE, "local_path": f"archive/geopolitics/sources/{RUN_DATE}/source-a.md"}]
    }
    (archive_root / "source-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    (run_dir / "sources.md").write_text(
        f"""# Sources

Date: `{RUN_DATE}`

## Run Source Set

| Source ID | Voice | Archive Path | Why It Matters |
| --- | --- | --- | --- |
| `SRC-01` | Analyst | [source](../../../../archive/geopolitics/sources/{RUN_DATE}/source-a.md) | Mechanism evidence. |

## Missing Observables

Independent event evidence remains absent.
""",
        encoding="utf-8",
    )
    (run_dir / "synthesis.md").write_text(
        f"""# Synthesis

Date: `{RUN_DATE}`

## Primary Voices

| Voice | Intellectual operation | What it adds | Main risk |
| --- | --- | --- | --- |
| Analyst | Tests mechanism. | Adds a bounded test. | Source concentration. |

## Operational Claim Triage

| Claim ID | Operational claim | Current status | Consequence if false | Public use | Verification |
| --- | --- | --- | --- | --- | --- |

## Issue Story Desk

| Story ID | Placement | Argument headline | Crisis object | Evidence posture | Source IDs | Voices | Forecast hooks | Operational claims | Selection rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NGI-20260709-S01` | `lead` | Passage Rules Remain the Discriminating Test | Can passage normalize without contested coordination? | `bounded-analysis` | `SRC-01` | Analyst | `{HOOK_ID}` | `none` | The mechanism is discriminating and source bounded. |
""",
        encoding="utf-8",
    )
    hook_text = f"`{HOOK_ID}`" if hook_in_day else "No hook is selected."
    (run_dir / "forecast.md").write_text(
        f"""# Forecast

Date: `{RUN_DATE}`

## Existing Causal Wagers

{hook_text}

## Hooks

| Hook ID | Claim | Probability Band | Review Date | Strengthening Evidence | Weakening Evidence |
| --- | --- | --- | --- | --- | --- |
| `{HOOK_ID}` | Passage remains conditional. | `likely` | `2026-07-20` | Continued coordination language. | Normal passage without dispute. |
""" if hook_in_day else f"# Forecast\n\nDate: `{RUN_DATE}`\n\nNo hook is selected.\n",
        encoding="utf-8",
    )
    body = "State what changed" if placeholder else "The archive supports a bounded mechanism judgment while operational evidence remains separate."
    (run_dir / "daily-brief.md").write_text(
        f"""# Passage Rules Remain the Discriminating Test

Title rationale: `Names the mechanism that separates normalization from continued contested governance.`

## Issue Copy

### NGI-20260709-S01 — Passage Rules Remain the Discriminating Test

{body}

## Revision Log

No revisions.
""",
        encoding="utf-8",
    )
    ledger_path.write_text(
        f"""# Forecast Ledger

| Hook ID | Date | Crisis Object | Claim | Probability Band | Review Date | Source Run | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `{HOOK_ID}` | `{RUN_DATE}` | Passage governance | Passage remains conditional. | `likely` | `2026-07-20` | [run](../daily/{RUN_DATE}/forecast.md) | `open` |
""",
        encoding="utf-8",
    )
    return daily_root, ledger_path


def test_render_is_deterministic_and_selects_declared_sources(tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path)
    model = issue.load_model(RUN_DATE, daily_root, ledger_path)

    first = issue.render_model(model)
    second = issue.render_model(model)

    assert first == second
    assert "daily-issue-v1 inputs-sha256:" in first
    assert "Passage Rules Remain the Discriminating Test" in first
    assert "[source](../../../../archive/geopolitics/sources/2026-07-09/source-a.md)" in first
    assert set(issue.REQUIRED_ISSUE_SECTIONS) <= set(name for level, name in issue.HEADING_RE.findall(first) if level == "##")


def test_validation_context_preserves_output_and_loads_reality_once(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path)
    reality_root = tmp_path / "reality"
    reality_root.mkdir()
    load_calls = 0
    original_load_records = issue.reality.load_records

    def counted_load_records(root: Path = issue.reality.REALITY_ROOT):
        nonlocal load_calls
        load_calls += 1
        return original_load_records(root)

    monkeypatch.setattr(issue.reality, "load_records", counted_load_records)
    context = issue.load_validation_context(
        daily_root=daily_root,
        ledger_path=ledger_path,
        reality_root=reality_root,
    )
    cached_model = issue.load_model(
        RUN_DATE,
        daily_root,
        ledger_path,
        context=context,
    )
    cached_render = issue.render_model(cached_model, context=context)
    issue_path = daily_root / RUN_DATE / "issue.md"
    issue_path.write_text(cached_render, encoding="utf-8")

    cached_result = issue.validate_issue(
        RUN_DATE,
        require=True,
        daily_root=daily_root,
        ledger_path=ledger_path,
        context=context,
    )
    assert load_calls == 1
    uncached_model = issue.load_model(RUN_DATE, daily_root, ledger_path)
    uncached_render = issue.render_model(uncached_model)
    uncached_result = issue.validate_issue(
        RUN_DATE,
        require=True,
        daily_root=daily_root,
        ledger_path=ledger_path,
    )

    assert cached_render == uncached_render
    assert cached_result == uncached_result
    assert load_calls == 3


def test_issue_validation_detects_stale_canonical_input(tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path)
    run_dir = daily_root / RUN_DATE
    (run_dir / "issue.md").write_text(issue.render_model(issue.load_model(RUN_DATE, daily_root, ledger_path)), encoding="utf-8")
    brief = (run_dir / "daily-brief.md").read_text(encoding="utf-8")
    (run_dir / "daily-brief.md").write_text(
        brief.replace("operational evidence remains separate.", "operational evidence remains separate after a canonical edit."),
        encoding="utf-8",
    )

    failures, _ = issue.validate_issue(RUN_DATE, require=True, daily_root=daily_root, ledger_path=ledger_path)

    assert "issue.md input digest is missing or stale" in failures
    assert "issue.md is not the current deterministic rendering" in failures


def test_issue_stage_requires_file_but_legacy_validation_does_not(tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path)

    assert issue.validate_issue(RUN_DATE, require=False, daily_root=daily_root, ledger_path=ledger_path) == ([], [])
    assert issue.validate_issue(RUN_DATE, require=True, daily_root=daily_root, ledger_path=ledger_path)[0] == ["missing issue.md"]


def test_placeholder_copy_blocks_rendering(tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path, placeholder=True)

    with pytest.raises(issue.IssueError, match="placeholder"):
        issue.load_model(RUN_DATE, daily_root, ledger_path)


def test_forecast_hook_must_exist_in_the_days_forecast(tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path, hook_in_day=False)
    model = issue.load_model(RUN_DATE, daily_root, ledger_path)

    failures = issue.model_failures(model, ledger_path.read_text(encoding="utf-8"), daily_root)

    assert f"NGI-20260709-S01: forecast hook missing from the day's forecast.md {HOOK_ID}" in failures


def test_forecast_detail_can_supply_rows_when_ledger_table_is_not_parseable(tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path)
    ledger_path.write_text(
        f"""# Forecast Ledger

| Hook ID | Date | Crisis Object | Claim | Probability Band | Review Date | Source Run | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `{HOOK_ID}` | `{RUN_DATE}` | Passage governance | Passage remains conditional. | Mechanism text adds one extra cell. | `likely` | `2026-07-20` | [run](../daily/{RUN_DATE}/forecast.md) | `open` |
""",
        encoding="utf-8",
    )

    model = issue.load_model(RUN_DATE, daily_root, ledger_path)
    failures = issue.model_failures(model, ledger_path.read_text(encoding="utf-8"), daily_root)

    assert f"NGI-20260709-S01: forecast hook missing detail or ledger row {HOOK_ID}" not in failures
    assert model.forecast_rows[HOOK_ID]["Claim"] == "Passage remains conditional."


def test_thin_issue_is_valid_and_records_the_reason(tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path)
    run_dir = daily_root / RUN_DATE
    rendered = issue.render_model(issue.load_model(RUN_DATE, daily_root, ledger_path))
    (run_dir / "issue.md").write_text(rendered, encoding="utf-8")

    failures, warnings = issue.validate_issue(RUN_DATE, require=True, daily_root=daily_root, ledger_path=ledger_path)

    assert failures == []
    assert "intentionally a thin issue" in rendered
    assert any("word count outside" in warning for warning in warnings)


def test_revision_log_is_rendered_verbatim(tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path)
    path = daily_root / RUN_DATE / "daily-brief.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "No revisions.",
            "| Timestamp (UTC) | Type | Note |\n| --- | --- | --- |\n| `2026-07-10T12:00:00Z` | `correction` | Corrected an attributed title. |",
        ),
        encoding="utf-8",
    )

    rendered = issue.render_model(issue.load_model(RUN_DATE, daily_root, ledger_path))

    assert "`2026-07-10T12:00:00Z` | `correction`" in rendered


def test_unknown_source_and_broken_archive_link_are_rejected(tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path)
    synthesis = daily_root / RUN_DATE / "synthesis.md"
    synthesis.write_text(synthesis.read_text(encoding="utf-8").replace("`SRC-01` | Analyst", "`SRC-99` | Analyst"), encoding="utf-8")
    model = issue.load_model(RUN_DATE, daily_root, ledger_path)
    failures = issue.model_failures(model, ledger_path.read_text(encoding="utf-8"), daily_root)
    assert "NGI-20260709-S01: unknown source ID SRC-99" in failures

    synthesis.write_text(synthesis.read_text(encoding="utf-8").replace("`SRC-99` | Analyst", "`SRC-01` | Analyst"), encoding="utf-8")
    sources = daily_root / RUN_DATE / "sources.md"
    sources.write_text(sources.read_text(encoding="utf-8").replace("source-a.md", "missing.md"), encoding="utf-8")
    model = issue.load_model(RUN_DATE, daily_root, ledger_path)
    failures = issue.model_failures(model, ledger_path.read_text(encoding="utf-8"), daily_root)
    assert any("archive link does not resolve" in failure for failure in failures)


def test_verification_supported_cannot_promote_a_source_assertion(tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path)
    synthesis = daily_root / RUN_DATE / "synthesis.md"
    text = synthesis.read_text(encoding="utf-8")
    text = text.replace(
        "| --- | --- | --- | --- | --- | --- |\n\n## Issue Story Desk",
        "| --- | --- | --- | --- | --- | --- |\n| `OPC-20260709-01` | A bounded event occurred. | `source_assertion` | `high` | `no` | `request` |\n\n## Issue Story Desk",
    )
    text = text.replace("`bounded-analysis` | `SRC-01`", "`verification-supported` | `SRC-01`")
    text = text.replace("`none` | The mechanism", "`OPC-20260709-01` | The mechanism")
    synthesis.write_text(text, encoding="utf-8")

    model = issue.load_model(RUN_DATE, daily_root, ledger_path)
    failures = issue.model_failures(model, ledger_path.read_text(encoding="utf-8"), daily_root)

    assert "NGI-20260709-S01: verification-supported lacks a supported VER-backed claim" in failures


def test_cli_requires_force_to_replace_a_stale_issue(monkeypatch, tmp_path: Path) -> None:
    daily_root, ledger_path = fixture_tree(tmp_path)
    issue_path = daily_root / RUN_DATE / "issue.md"
    issue_path.write_text("hand edit\n", encoding="utf-8")
    monkeypatch.setattr(issue, "DAILY_ROOT", daily_root)
    monkeypatch.setattr(issue, "LEDGER_PATH", ledger_path)
    monkeypatch.setattr(issue, "TEMPLATE_PATH", REPO_ROOT / "narrative-geopolitics" / "templates" / "issue.md")
    monkeypatch.setattr(sys, "argv", ["render_daily_issue.py", "--date", RUN_DATE])

    with pytest.raises(SystemExit, match="Refusing to overwrite"):
        issue.main()

    monkeypatch.setattr(sys, "argv", ["render_daily_issue.py", "--date", RUN_DATE, "--force"])
    issue.main()
    assert "daily-issue-v1" in issue_path.read_text(encoding="utf-8")

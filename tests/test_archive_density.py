from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

spec = importlib.util.spec_from_file_location("archive_density_tests", SCRIPTS_ROOT / "report_archive_density.py")
assert spec is not None
assert spec.loader is not None
density = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = density
spec.loader.exec_module(density)


def fixture_tree(tmp_path: Path) -> tuple[Path, Path]:
    ng_root = tmp_path / "narrative-geopolitics"
    manifest_path = ng_root / "archive" / "source-manifest.json"
    daily_root = ng_root / "work" / "daily"
    source_root = ng_root / "archive" / "sources"
    manifest_path.parent.mkdir(parents=True)
    daily_root.mkdir(parents=True)
    rows = []
    for run_date, count in (("2026-07-01", 2), ("2026-07-02", 8)):
        (source_root / run_date).mkdir(parents=True)
        for index in range(1, count + 1):
            source_path = source_root / run_date / f"source-{index}.md"
            source_path.write_text("# Source\n", encoding="utf-8")
            rows.append(
                {
                    "date": run_date,
                    "local_path": f"archive/geopolitics/sources/{run_date}/source-{index}.md",
                }
            )
    manifest_path.write_text(json.dumps({"sources": rows}), encoding="utf-8")

    make_daily(
        daily_root,
        "2026-07-01",
        "Thin Day",
        "Can a thin day carry a hook?",
        hooks=["NG-20260701-F01"],
        opcs=["OPC-20260701-01"],
        stories=2,
    )
    make_daily(
        daily_root,
        "2026-07-02",
        "Dense Day",
        "Does a dense day need synthesis review?",
        hooks=["NG-20260702-F01", "NG-20260701-F01"],
        opcs=[],
        stories=0,
    )
    return manifest_path, daily_root


def make_daily(
    daily_root: Path,
    run_date: str,
    title: str,
    crisis: str,
    *,
    hooks: list[str],
    opcs: list[str],
    stories: int,
) -> None:
    run_dir = daily_root / run_date
    run_dir.mkdir(parents=True)
    (run_dir / "sources.md").write_text("# Sources\n", encoding="utf-8")
    story_rows = []
    for index in range(1, stories + 1):
        placement = "lead" if index == 1 else "brief"
        story_rows.append(
            f"| `NGI-{run_date.replace('-', '')}-S{index:02d}` | `{placement}` | Story {index} | {crisis} | `bounded-analysis` | `SRC-01` | Analyst | `none` | `none` | Rationale. |"
        )
    (run_dir / "synthesis.md").write_text(
        f"""# Synthesis

## Crisis Object

{crisis}

## Issue Story Desk

| Story ID | Placement | Argument headline | Crisis object | Evidence posture | Source IDs | Voices | Forecast hooks | Operational claims | Selection rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(story_rows)}

## Operational Claim Triage

{chr(10).join(f'| `{claim}` | Claim | `source_assertion` | `high` | `no` | `request` |' for claim in opcs)}
""",
        encoding="utf-8",
    )
    (run_dir / "forecast.md").write_text("\n".join(f"`{hook}`" for hook in hooks), encoding="utf-8")
    (run_dir / "daily-brief.md").write_text(f"# {title}\n", encoding="utf-8")
    (run_dir / "issue.md").write_text("# Issue\n", encoding="utf-8")


def test_analyze_range_counts_sources_and_load(tmp_path: Path, monkeypatch) -> None:
    manifest_path, daily_root = fixture_tree(tmp_path)
    monkeypatch.setattr(density, "validation_counts", lambda run_date, daily_root=daily_root: (0, 0))

    rows = density.analyze_range(["2026-07-01", "2026-07-02", "2026-07-03"], manifest_path, daily_root)

    assert [row.manifest_sources for row in rows] == [2, 8, 0]
    assert rows[0].density_class == "thin"
    assert rows[1].density_class == "dense"
    assert rows[2].daily_stack_files == "none"
    assert rows[0].forecast_hooks == 1
    assert rows[0].opc_claims == 1
    assert rows[0].issue_stories == 2
    assert rows[0].narrative_load_ratio == 2.0
    assert "thin-but-pivotal" in rows[0].classifications
    assert "overclaim-risk" in rows[0].classifications
    assert "dense-synthesis-check" in rows[1].classifications
    assert rows[1].same_day_hooks == 1
    assert rows[1].carried_hooks == 1
    stats = density.summary(rows)
    assert stats["total_sources"] == 10
    assert stats["high_density_days"] == ["2026-07-02"]
    assert stats["low_density_days"] == ["2026-07-01"]


def test_markdown_csv_and_json_outputs(tmp_path: Path, monkeypatch) -> None:
    manifest_path, daily_root = fixture_tree(tmp_path)
    monkeypatch.setattr(density, "validation_counts", lambda run_date, daily_root=daily_root: (0, 0))
    rows = density.analyze_range(["2026-07-01", "2026-07-02"], manifest_path, daily_root)

    markdown = density.render_markdown(rows)
    csv_path = tmp_path / "density.csv"
    json_path = tmp_path / "density.json"
    density.write_csv(rows, csv_path)
    density.write_json(rows, json_path)

    assert "Archive Density Dashboard" in markdown
    assert "thin-but-pivotal" in markdown
    assert csv_path.read_text(encoding="utf-8").startswith("date,manifest_sources")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["summary"]["total_sources"] == 10
    assert payload["rows"][1]["title"] == "Dense Day"

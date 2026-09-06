"""Cross-workflow contracts for the opt-in domain directory transition."""
import importlib

import pytest


WORKFLOW_PATHS = [
    ("voice_accountability", "LEDGER_JSON_PATH"),
    ("voice_judgments", "REGISTRY_PATH"),
    ("voice_comparison", "OUT_ROOT"),
    ("continuity", "DAILY"),
    ("operator_positions", "CANDIDATE_ROOT"),
    ("recursive_learning_ledger", "OUTCOME_RECEIPT_ROOT"),
    ("bootstrap_daily_run", "TEMPLATES_ROOT"),
    ("sync_forecast_ledger", "LEDGER_PATH"),
    ("triage_forecast_ledger", "LEDGER_PATH"),
    ("dream_eod", "DAILY_ROOT"),
    ("morning_brief", "BRIEF_ROOT"),
    ("reality_handoff", "CLAIMS_ROOT"),
    ("research_handoff", "CLAIMS_ROOT"),
    ("youtube_capture", "QUEUE_ROOT"),
    ("build_freeman_historical_index", "OUTPUT_PATH"),
    ("build_statecraft_backfill_outputs", "OUT"),
    ("prepare_statecraft_backfill", "BACKFILL_ROOT"),
    ("report_archive_density", "DAILY_ROOT"),
    ("report_cross_voice_reference_density", "OUTPUT_PATH"),
    ("report_freeman_reference_density", "OUTPUT_PATH"),
    ("report_narrative_reuse", "DAILY_ROOT"),
    ("role_aware_archive", "PUBLICATIONS"),
    ("cadence", "HANDOFF_PATH"),
    ("mira_journal", "LEARNING_LEDGER_PATH"),
    ("validate_repository", "LEGACY_VERIFICATION_INVENTORY"),
]


@pytest.mark.parametrize("module_name,path_name", WORKFLOW_PATHS)
def test_defaults_follow_same_process_rename_and_explicit_override(
    tmp_path, monkeypatch, module_name, path_name
):
    module = importlib.import_module(module_name)
    old = tmp_path / "narrative-geopolitics"
    new = tmp_path / "geopolitics"
    old.mkdir()
    for name in ("ROOT", "REPO_ROOT"):
        if hasattr(module, name):
            monkeypatch.setattr(module, name, tmp_path)
    before = module._path(path_name)
    assert before.is_relative_to(old)
    suffix = before.relative_to(old)
    old.rename(new)
    assert module._path(path_name) == new / suffix
    explicit = tmp_path / "explicit" / path_name
    monkeypatch.setattr(module, path_name, explicit)
    assert module._path(path_name) == explicit


@pytest.mark.parametrize("module_name,path_name", WORKFLOW_PATHS)
def test_ambiguous_domain_defaults_fail_without_creating_outputs(
    tmp_path, monkeypatch, module_name, path_name
):
    module = importlib.import_module(module_name)
    for name in ("ROOT", "REPO_ROOT"):
        if hasattr(module, name):
            monkeypatch.setattr(module, name, tmp_path)
    (tmp_path / "narrative-geopolitics").mkdir()
    (tmp_path / "geopolitics").mkdir()
    with pytest.raises(ValueError, match="exactly one"):
        module._path(path_name)
    assert len(list(tmp_path.rglob("*"))) == 2


def test_relative_legacy_archive_link_moves_without_body_rewrite(tmp_path):
    from repository_paths import resolve_geopolitics_reference
    target = tmp_path / "archive" / "sources" / "geopolitics" / "source-manifest.json"
    target.parent.mkdir(parents=True)
    target.write_text("{}", encoding="utf-8")
    for layout in ("narrative-geopolitics", "geopolitics"):
        assert resolve_geopolitics_reference(tmp_path, f"{layout}/archive/source-manifest.json") == target


def test_optional_read_location_does_not_relax_writer_root_selection(tmp_path):
    from repository_paths import geopolitics_reference_for_read, resolve_geopolitics_reference
    reference = "geopolitics/work/coverage/contracts/2026-09.json"
    assert geopolitics_reference_for_read(tmp_path, reference) == tmp_path / reference
    assert list(tmp_path.iterdir()) == []
    with pytest.raises(ValueError, match="exactly one"):
        resolve_geopolitics_reference(tmp_path, reference)


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_daily_writer_routes_all_outputs_and_preserves_existing_files(tmp_path, monkeypatch, layout):
    from types import SimpleNamespace
    import bootstrap_daily_run as bootstrap
    domain = tmp_path / layout
    domain.mkdir()
    monkeypatch.setattr(bootstrap, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(bootstrap, "parse_args", lambda: SimpleNamespace(
        date="2099-01-01", status="draft", retro=False, force=False, dry_run=False
    ))
    monkeypatch.setattr(bootstrap, "load_manifest", lambda: {
        "sources": [{"date": "2099-01-01", "local_path": "fixture.md"}]
    })
    monkeypatch.setattr(bootstrap, "build_sources_md", lambda *args: "# Fixture sources")
    monkeypatch.setattr(bootstrap, "build_from_template", lambda *args: "# Fixture draft")
    bootstrap.main()
    day = domain / "work" / "daily" / "2099-01-01"
    expected_names = {"sources.md", *bootstrap.DAILY_TEMPLATE_FILES}
    assert {p.name for p in day.iterdir()} == expected_names
    before = {p.name: p.read_bytes() for p in day.iterdir()}
    bootstrap.main()
    assert {p.name: p.read_bytes() for p in day.iterdir()} == before
    assert not (tmp_path / ("geopolitics" if layout == "narrative-geopolitics" else "narrative-geopolitics")).exists()


def test_bootstrap_sources_table_keeps_date_title_and_url_together():
    import bootstrap_daily_run as bootstrap

    text = bootstrap.build_sources_md(
        "2099-01-01",
        "draft",
        [
            {
                "local_path": "archive/sources/geopolitics/sources/2099-01-01/source-example.md",
                "voice_slugs": ["diesen"],
                "host_slug": "mario-nawfal",
                "modality": "cleaned-transcript",
                "source_class": "guest interview",
                "title": "Example Title",
                "source_url": "https://www.youtube.com/watch?v=example",
            }
        ],
        False,
    )

    assert "| Source ID | Date | Title | URL | Voice | Host / Channel | Modality | Archive Path | Why It Matters |" in text
    assert (
        "| `SRC-01` | `2099-01-01` | Example Title | "
        "[source](https://www.youtube.com/watch?v=example) | Diesen | Mario Nawfal |"
    ) in text

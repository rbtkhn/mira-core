import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_land_best_intake import (
    configure_transaction_root,
    land_best_intake as intake,
    transaction_args,
)


def snapshot(root: Path) -> dict[str, bytes | None]:
    return {p.relative_to(root).as_posix(): p.read_bytes() if p.is_file() else None
            for p in root.rglob("*")}


def configure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, layout: str):
    _, manifest_path = configure_transaction_root(monkeypatch, tmp_path)
    old = tmp_path / "narrative-geopolitics"
    new = tmp_path / "geopolitics"
    assert old.resolve().is_relative_to(tmp_path.resolve())
    assert new.resolve().is_relative_to(tmp_path.resolve())
    if layout == "geopolitics":
        old.rename(new)
    elif layout == "missing":
        old.rmdir()  # Empty fixture directory only.
    elif layout == "both":
        new.mkdir()
    index = None
    if layout in ("geopolitics", "narrative-geopolitics"):
        index = tmp_path / layout / "voices/audit-voice/source-index.md"
        index.parent.mkdir(parents=True)
        index.write_text(
            "# Audit Voice\n\nCorpus: 0 local route rows across 0 central archive source files.\n\n"
            "| Date | Source | Role | Host slug | Archive link |\n"
            "| --- | --- | --- | --- | --- |\n", encoding="utf-8",
        )
    manifest_path.write_text(json.dumps({
        "source_count": 0, "sources": [], "manifest_id": "NG-fixture",
        "historical_basis": "narrative-geopolitics/archive/source-manifest.json",
    }) + "\n", encoding="utf-8")
    args = transaction_args("2026-07-15", "Voice shelf source", "https://example.com/one")
    return manifest_path, index, args


def main_args(monkeypatch: pytest.MonkeyPatch, args, *, mode: str = "land") -> None:
    monkeypatch.setattr(intake, "parse_args", lambda: SimpleNamespace(
        backfill_since=None, preflight=mode == "preflight", dry_run=mode == "dry-run", json=True,
    ))
    monkeypatch.setattr(intake, "gather_sources", lambda _: [copy.deepcopy(args)])


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_landing_and_duplicate_preserve_archive_destinations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], layout: str,
) -> None:
    manifest_path, index, args = configure(tmp_path, monkeypatch, layout)
    main_args(monkeypatch, args)
    assert intake.main() == 0
    assert json.loads(capsys.readouterr().out)["status"] == "landed"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["source_count"] == 1
    assert manifest["manifest_id"] == "NG-fixture"
    assert manifest["historical_basis"] == "narrative-geopolitics/archive/source-manifest.json"
    row = manifest["sources"][0]
    assert row["local_path"].startswith("archive/sources/geopolitics/sources/2026-07-15/")
    source = tmp_path / row["local_path"]
    assert "Material source body." in source.read_text(encoding="utf-8")
    assert "../../../" + row["local_path"] in index.read_text(encoding="utf-8")
    after = snapshot(tmp_path)
    assert intake.main() == 0
    assert json.loads(capsys.readouterr().out)["status"] == "ALREADY LANDED"
    assert snapshot(tmp_path) == after


@pytest.mark.parametrize("layout", ["missing", "both"])
def test_conflicting_layout_stops_main_before_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], layout: str,
) -> None:
    _, _, args = configure(tmp_path, monkeypatch, layout)
    main_args(monkeypatch, args)
    before = snapshot(tmp_path)
    assert intake.main() == 1
    assert "exactly one" in json.loads(capsys.readouterr().err)["error"]
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("layout", ["missing", "both"])
@pytest.mark.parametrize("mode", ["preflight", "dry-run"])
def test_read_only_modes_do_not_require_domain_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
    layout: str, mode: str,
) -> None:
    _, _, args = configure(tmp_path, monkeypatch, layout)
    main_args(monkeypatch, args, mode=mode)
    before = snapshot(tmp_path)
    assert intake.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] != "landed"
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_manifest_failure_rolls_back_source_and_active_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, layout: str,
) -> None:
    manifest_path, index, args = configure(tmp_path, monkeypatch, layout)
    plans, proposed = intake.prepare_batch([args], intake.load_manifest())
    before = snapshot(tmp_path)
    updates, _ = intake.project_voice_indexes_for_plans(plans, proposed)
    assert list(updates) == [index]
    assert snapshot(tmp_path) == before
    replace = intake.os.replace

    def fail_manifest(source, destination):
        if Path(destination) == manifest_path:
            raise OSError("simulated manifest publication failure")
        return replace(source, destination)

    monkeypatch.setattr(intake.os, "replace", fail_manifest)
    with pytest.raises(OSError, match="simulated manifest"):
        intake.publish_batch(plans, proposed, updates)
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_projection_and_sync_resolve_once_per_batch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, layout: str,
) -> None:
    _, index, first = configure(tmp_path, monkeypatch, layout)
    second = transaction_args("2026-07-16", "Second source", "https://example.com/two")
    plans, manifest = intake.prepare_batch([first, second], intake.load_manifest())
    resolve = intake.voice_indexes.default_voices_root
    calls = []

    def counted(root):
        calls.append(root)
        return resolve(root)

    monkeypatch.setattr(intake.voice_indexes, "default_voices_root", counted)
    updates, _ = intake.project_voice_indexes_for_plans(plans, manifest)
    assert calls == [tmp_path]
    intake.publish_batch(plans, manifest, updates)
    after = snapshot(tmp_path)
    calls.clear()
    assert intake.sync_voice_indexes_for_plans(plans, manifest) == []
    assert calls == [tmp_path]
    assert snapshot(tmp_path) == after
    assert "Corpus: 2 local route rows" in index.read_text(encoding="utf-8")


def test_empty_plans_need_no_domain(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    configure(tmp_path, monkeypatch, "missing")
    before = snapshot(tmp_path)
    assert intake.project_voice_indexes_for_plans([], intake.load_manifest()) == ({}, [])
    assert intake.sync_voice_indexes_for_plans([], intake.load_manifest()) == []
    assert snapshot(tmp_path) == before

import json
from datetime import date
from pathlib import Path
import sys

import pytest

import canonicalize_voice_metadata as canonicalize
import migrate_voice_role_overrides as migrate_roles
import voice_indexes
import voice_metadata


SOURCE = "archive/sources/geopolitics/sources/2026-07-10/source.md"


def snapshot(root: Path) -> dict[str, bytes | None]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes() if path.is_file() else None
        for path in root.rglob("*")
    }


def fixture_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, layout: str | None,
                 *, alias: bool = False) -> tuple[Path, Path, Path | None]:
    monkeypatch.setattr(voice_metadata, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(voice_indexes, "REPO_ROOT", tmp_path)
    source = tmp_path / SOURCE
    source.parent.mkdir(parents=True)
    slug = "larry-johnson" if alias else "johnson"
    source.write_bytes((f"---\nthread: {slug}\nhost_slug: dialogue-works\n---\n"
                        "Unchanged source body. NG-001.\n").encode())
    manifest = tmp_path / "archive/sources/geopolitics/source-manifest.json"
    manifest.write_text(json.dumps({
        "manifest_id": "NG-fixture", "source_count": 1,
        "historical_basis": "narrative-geopolitics/archive/source-manifest.json",
        "sources": [{"local_path": SOURCE, "voice_slugs": [slug],
                     "date": "2026-07-10", "title": "Source",
                     "source_class": "guest", "modality": "youtube-transcript",
                     "host_slug": "dialogue-works"}],
    }), encoding="utf-8")
    monkeypatch.setattr(voice_metadata, "MANIFEST_PATH", manifest)
    index = None
    if layout is not None:
        index = tmp_path / layout / "voices/johnson/source-index.md"
        index.parent.mkdir(parents=True)
        index.write_text(
            "# Voice Index\n\nCorpus: 0 local route rows across 0 central archive source files.\n\n"
            "## Imported Route Map\n\n" + voice_indexes.STANDARD_HEADER + "\n"
            "| --- | --- | --- | --- | --- |\n", encoding="utf-8",
        )
    return manifest, source, index


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_default_reconciliation_is_read_only_then_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, layout: str,
) -> None:
    manifest_path, source, index = fixture_repo(tmp_path, monkeypatch, layout)
    manifest = voice_indexes.load_manifest()
    originals = {p: p.read_bytes() for p in (manifest_path, source)}
    before = snapshot(tmp_path)
    projected, report = voice_indexes.project(manifest)
    assert list(projected) == [index]
    assert report["changed_shelves"] == ["johnson"]
    assert snapshot(tmp_path) == before
    assert voice_indexes.rows_by_voice(manifest)[1] == set()
    assert voice_indexes.shelves() == {"johnson": index}
    first = voice_indexes.reconcile(manifest, write=True)
    assert first["failures"] == []
    assert "../../../" + SOURCE in index.read_text(encoding="utf-8")
    after = snapshot(tmp_path)
    second = voice_indexes.reconcile(manifest, write=True)
    assert second["failures"] == []
    assert second["changed_shelves"] == []
    assert snapshot(tmp_path) == after
    assert {p: p.read_bytes() for p in originals} == originals


def test_imported_callers_follow_fixture_cutover(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, _, index = fixture_repo(tmp_path, monkeypatch, "narrative-geopolitics")
    manifest = voice_indexes.load_manifest()
    voice_indexes.reconcile(manifest, write=True)
    old = tmp_path / "narrative-geopolitics"
    new = tmp_path / "geopolitics"
    assert old.resolve().is_relative_to(tmp_path.resolve())
    assert new.resolve().is_relative_to(tmp_path.resolve())
    old.rename(new)
    assert voice_indexes.shelves() == {"johnson": new / "voices/johnson/source-index.md"}
    assert voice_indexes.reconcile(manifest)["failures"] == []
    assert not index.exists()


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_default_receipt_and_metadata_writes_preserve_bodies_and_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], layout: str,
) -> None:
    manifest, source, _ = fixture_repo(tmp_path, monkeypatch, layout, alias=True)
    before_body = source.read_bytes().split(b"---\n", 2)[2]
    monkeypatch.setattr(sys, "argv", ["voice-canonicalize", "--all", "--write", "--json"])
    canonicalize.main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["failures"] == []
    assert payload["changes"][0]["body_preserved"] is True
    assert source.read_bytes().split(b"---\n", 2)[2] == before_body
    stored = json.loads(manifest.read_text(encoding="utf-8"))
    assert stored["sources"][0]["voice_slugs"] == ["johnson"]
    assert stored["sources"][0]["local_path"] == SOURCE
    assert stored["manifest_id"] == "NG-fixture"
    assert stored["historical_basis"] == "narrative-geopolitics/archive/source-manifest.json"
    receipt = tmp_path / layout / "work/migrations" / f"canonical-voice-metadata-{date.today().isoformat()}.json"
    assert json.loads(receipt.read_text(encoding="utf-8"))["changes"] == payload["changes"]
    after = snapshot(tmp_path)
    canonicalize.main()
    assert json.loads(capsys.readouterr().out)["changes"] == []
    assert snapshot(tmp_path) == after


@pytest.mark.parametrize("layout", ["missing", "both"])
@pytest.mark.parametrize("writer", ["metadata", "indexes", "roles"])
def test_ambiguous_defaults_stop_before_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, layout: str, writer: str,
) -> None:
    fixture_repo(tmp_path, monkeypatch, None, alias=True)
    if layout == "both":
        (tmp_path / "narrative-geopolitics").mkdir()
        (tmp_path / "geopolitics").mkdir()
    before = snapshot(tmp_path)
    with pytest.raises(ValueError, match="exactly one"):
        if writer == "metadata":
            monkeypatch.setattr(sys, "argv", ["voice-canonicalize", "--all", "--write"])
            canonicalize.main()
        elif writer == "roles":
            monkeypatch.setattr(sys, "argv", ["migrate-roles", "--write"])
            migrate_roles.main()
        else:
            voice_indexes.reconcile(voice_indexes.load_manifest(), write=True)
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("mode", ["check", "explicit-receipt", "date-write"])
def test_archive_only_metadata_does_not_require_domain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], mode: str,
) -> None:
    fixture_repo(tmp_path, monkeypatch, None, alias=True)
    receipt = tmp_path / "explicit/receipt.json"
    arguments = ["--all", "--check"] if mode == "check" else (
        ["--all", "--write", "--receipt", str(receipt)] if mode == "explicit-receipt"
        else ["--date", "2026-07-10", "--write"]
    )
    monkeypatch.setattr(sys, "argv", ["voice-canonicalize", *arguments, "--json"])
    before = snapshot(tmp_path)
    if mode == "check":
        with pytest.raises(SystemExit) as error:
            canonicalize.main()
        assert error.value.code == 1
        assert snapshot(tmp_path) == before
    else:
        canonicalize.main()
    assert json.loads(capsys.readouterr().out)["failures"] == []
    assert receipt.exists() == (mode == "explicit-receipt")
    assert not (tmp_path / "geopolitics").exists()
    assert not (tmp_path / "narrative-geopolitics").exists()


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_role_migration_reads_and_writes_same_active_shelf(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], layout: str,
) -> None:
    manifest_path, source, index = fixture_repo(tmp_path, monkeypatch, layout)
    voice_indexes.reconcile(voice_indexes.load_manifest(), write=True)
    index.write_text(index.read_text(encoding="utf-8").replace("`guest`", "`curated`"), encoding="utf-8")
    before = snapshot(tmp_path)
    monkeypatch.setattr(sys, "argv", ["migrate-roles"])
    assert migrate_roles.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["overrides"] == [{"voice_slug": "johnson", "local_path": SOURCE, "role": "curated"}]
    assert snapshot(tmp_path) == before
    monkeypatch.setattr(sys, "argv", ["migrate-roles", "--write"])
    assert migrate_roles.main() == 0
    target = tmp_path / layout / "voices/role-overrides.json"
    assert json.loads(target.read_text(encoding="utf-8")) == payload
    for path in (manifest_path, source, index):
        assert path.read_bytes() == before[path.relative_to(tmp_path).as_posix()]


def test_explicit_paths_bypass_default_domain_selection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest_path, _, index = fixture_repo(tmp_path, monkeypatch, "custom")
    for name in ("narrative-geopolitics", "geopolitics"):
        (tmp_path / name).mkdir()
    explicit = tmp_path / "custom/voices"
    monkeypatch.setattr(voice_metadata, "MANIFEST_PATH", tmp_path / "absent.json")
    manifest = voice_indexes.load_manifest(manifest_path)
    assert voice_indexes.shelves(explicit) == {"johnson": index}
    assert voice_indexes.rows_by_voice(manifest, voices_root=explicit)[1] == set()
    assert voice_indexes.reconcile(manifest, write=True, repo_root=tmp_path, voices_root=explicit)["failures"] == []
    voice_metadata.write_manifest(manifest, manifest_path)
    assert not (tmp_path / "absent.json").exists()

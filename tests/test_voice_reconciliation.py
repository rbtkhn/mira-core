from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

import voice_indexes
import voice_metadata


def test_jiang_historical_alias_resolves_to_voice_directory_slug() -> None:
    assert voice_metadata.canonical_slug("jiang-xueqin") == "jiang"
    assert voice_metadata.canonical_slug("jiang") == "jiang"


def source_document(*, thread: str, host: str, include_voice_slug: bool = False) -> bytes:
    voice = f"voice_slug: {thread}\n" if include_voice_slug else ""
    return (
        "---\n"
        f"thread: {thread}\n"
        f"{voice}"
        f"host_slug: {host}\n"
        "---\n"
        "# Source\n\nBody must remain byte-identical.\n"
    ).encode()


def manifest_row(path: str, slug: str, *, host: str = "dialogue-works", title: str = "Source") -> dict:
    return {
        "date": "2026-07-10",
        "title": title,
        "local_path": path,
        "voice_index_path": "../../archive/sources/2026-07-10/source.md",
        "source_class": "geopolitical commentary",
        "modality": "youtube-transcript",
        "voice_slugs": [slug],
        "host_slug": host,
    }


def test_alias_metadata_is_canonicalized_without_body_or_host_change(tmp_path: Path) -> None:
    rel = "narrative-geopolitics/archive/sources/2026-07-10/source.md"
    target = tmp_path / rel
    target.parent.mkdir(parents=True)
    original = source_document(thread="larry-johnson", host="dialogue-works")
    target.write_bytes(original)
    manifest = {"source_count": 1, "sources": [manifest_row(rel, "larry-johnson")]}

    report = voice_metadata.apply_metadata(manifest, tmp_path)

    updated = target.read_bytes()
    assert report["failures"] == []
    assert manifest["sources"][0]["voice_slugs"] == ["johnson"]
    assert b"thread: johnson\n" in updated
    assert b"host_slug: dialogue-works\n" in updated
    assert updated.split(b"---\n", 2)[2] == original.split(b"---\n", 2)[2]
    assert b"voice_slug:" not in updated


def test_existing_canonical_thread_is_untouched_while_manifest_changes(tmp_path: Path) -> None:
    rel = "narrative-geopolitics/archive/sources/2026-07-10/source.md"
    target = tmp_path / rel
    target.parent.mkdir(parents=True)
    original = source_document(thread="ritter", host="garland-nixon")
    target.write_bytes(original)
    manifest = {"sources": [manifest_row(rel, "scott-ritter", host="garland-nixon")]}

    report = voice_metadata.apply_metadata(manifest, tmp_path)

    assert manifest["sources"][0]["voice_slugs"] == ["ritter"]
    assert target.read_bytes() == original
    assert "frontmatter" not in report["changes"][0]


def test_host_slug_is_not_canonicalized_and_existing_voice_slug_is(tmp_path: Path) -> None:
    rel = "narrative-geopolitics/archive/sources/2026-07-10/source.md"
    target = tmp_path / rel
    target.parent.mkdir(parents=True)
    target.write_bytes(source_document(thread="alexander-mercouris", host="alexander-mercouris", include_voice_slug=True))
    manifest = {"sources": [manifest_row(rel, "alexander-mercouris", host="alexander-mercouris")]}

    voice_metadata.apply_metadata(manifest, tmp_path)
    text = target.read_text()

    assert manifest["sources"][0]["voice_slugs"] == ["mercouris"]
    assert "thread: mercouris" in text
    assert "voice_slug: mercouris" in text
    assert "host_slug: alexander-mercouris" in text


def test_alias_normalization_preserves_order_and_deduplicates() -> None:
    assert voice_metadata.canonicalize_slugs(["johnson", "larry-johnson", "pape"]) == ["johnson", "pape"]


def configure_voice_roots(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    ng_root = tmp_path / "narrative-geopolitics"
    voices_root = ng_root / "voices"
    monkeypatch.setattr(voice_indexes, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(voice_indexes, "NG_ROOT", ng_root)
    monkeypatch.setattr(voice_indexes, "VOICES_ROOT", voices_root)
    monkeypatch.setattr(voice_metadata, "REPO_ROOT", tmp_path)
    return ng_root, voices_root


def standard_index(count: int = 0, rows: str = "") -> str:
    return (
        "# Voice Index\n\n"
        f"Corpus: {count} local route rows across {count} central archive source files.\n\n"
        "## Imported Route Map\n\n"
        "| Date | Source | Role | Host slug | Archive link |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"{rows}"
    )


def test_standard_shelf_sync_is_idempotent_and_preserves_role(monkeypatch, tmp_path: Path) -> None:
    ng_root, voices_root = configure_voice_roots(monkeypatch, tmp_path)
    index = voices_root / "johnson" / "source-index.md"
    index.parent.mkdir(parents=True)
    first_rel = "narrative-geopolitics/archive/sources/2026-07-09/a.md"
    second_rel = "narrative-geopolitics/archive/sources/2026-07-10/b.md"
    existing = "| `2026-07-09` | A | `guest interview pressure test` | `dialogue-works` | [source](../../archive/sources/2026-07-09/a.md) |\n"
    index.write_text(standard_index(1, existing), encoding="utf-8")
    for rel in (first_rel, second_rel):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("source\n")
    manifest = {
        "sources": [
            manifest_row(first_rel, "johnson", title="A"),
            {
                **manifest_row(second_rel, "johnson", title="B"),
                "source_class": "guest interview pressure test",
            },
        ]
    }
    overrides = {
        ("johnson", first_rel): "guest interview pressure test",
    }

    first = voice_indexes.reconcile(
        manifest, run_date="2026-07-10", write=True, repo_root=tmp_path,
        voices_root=voices_root, role_overrides=overrides,
    )
    after_first = index.read_text()
    second = voice_indexes.reconcile(
        manifest, run_date="2026-07-10", write=True, repo_root=tmp_path,
        voices_root=voices_root, role_overrides=overrides,
    )

    assert first["failures"] == []
    assert second["failures"] == []
    assert second["changed_shelves"] == []
    assert "Corpus: 2 local route rows across 2 central archive source files." in after_first
    assert "`guest interview pressure test`" in after_first
    assert "| `2026-07-10` | B | `guest`" in after_first


def test_shelf_less_voice_is_reported_not_failed(monkeypatch, tmp_path: Path) -> None:
    _, voices_root = configure_voice_roots(monkeypatch, tmp_path)
    rel = "narrative-geopolitics/archive/sources/2026-07-10/x.md"
    target = tmp_path / rel
    target.parent.mkdir(parents=True)
    target.write_text("source\n")
    manifest = {"sources": [manifest_row(rel, "new-voice")]}

    report = voice_indexes.reconcile(
        manifest, run_date="2026-07-10", write=False, repo_root=tmp_path, voices_root=voices_root
    )

    assert report["failures"] == []
    assert report["unindexed_voices"] == ["new-voice"]


def test_role_override_registry_rejects_orphan_path() -> None:
    manifest = {"sources": []}
    failures = voice_indexes.role_override_failures(
        manifest,
        {("johnson", "narrative-geopolitics/archive/sources/missing.md"): "curated"},
    )
    assert failures == [
        "voice-role override path absent from manifest: "
        "narrative-geopolitics/archive/sources/missing.md"
    ]


def test_pape_renderer_maps_canonical_author_to_authored(tmp_path: Path) -> None:
    index = tmp_path / "narrative-geopolitics" / "voices" / "pape" / "source-index.md"
    index.parent.mkdir(parents=True)
    text = "# Pape Source Index\n\nCorpus: 0 authored sources, 0 guest appearances, 0 total imported sources.\n\n## 2026-07\n"
    rel = "narrative-geopolitics/archive/sources/2026-07-10/source.md"
    row = {
        **manifest_row(rel, "pape"),
        "voice_roles": {"pape": ["author"]},
    }

    updated, _ = voice_indexes.render_pape(index, text, [row], repo_root=tmp_path)

    assert "Corpus: 1 authored sources, 0 guest appearances, 1 total imported sources." in updated
    assert "**authored**" in updated


def test_pape_override_registry_rejects_non_binary_display_role() -> None:
    rel = "narrative-geopolitics/archive/sources/2026-07-10/source.md"
    manifest = {"sources": [manifest_row(rel, "pape")]}

    failures = voice_indexes.role_override_failures(
        manifest,
        {("pape", rel): "authored newsletter"},
    )

    assert failures == [
        "unsupported Pape voice-role override: authored newsletter " + rel
    ]

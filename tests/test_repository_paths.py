import os
from pathlib import Path
import subprocess

import pytest

from repository_paths import (
    canonical_geopolitics_reference,
    canonical_repository_path,
    geopolitics_root,
    resolve_geopolitics_reference,
    resolve_repository_path,
)


def test_geopolitics_archive_legacy_prefix_resolves_to_canonical_path(
    tmp_path: Path,
) -> None:
    expected = tmp_path / "archive" / "sources" / "geopolitics" / "sources" / "day" / "source.md"

    assert canonical_repository_path(
        "narrative-geopolitics/archive/sources/day/source.md"
    ) == "archive/sources/geopolitics/sources/day/source.md"
    assert resolve_repository_path(
        tmp_path, "narrative-geopolitics\\archive\\sources\\day\\source.md"
    ) == expected


def test_geopolitics_archive_alias_is_prefix_bounded() -> None:
    value = "narrative-geopolitics/archive-old/source.md"

    assert canonical_repository_path(value) == value


@pytest.mark.parametrize(("value", "expected"), [
    ("narrative-geopolitics", "geopolitics"),
    ("narrative-geopolitics/", "geopolitics"),
    ("narrative-geopolitics\\work\\daily\\issue.md", "geopolitics/work/daily/issue.md"),
    ("geopolitics/work/daily/issue.md", "geopolitics/work/daily/issue.md"),
    ("narrative-geopolitics/archive", "archive/sources/geopolitics"),
    ("narrative-geopolitics/archive/source.md", "archive/sources/geopolitics/source.md"),
    ("narrative-geopolitics/archive-old/source.md", "geopolitics/archive-old/source.md"),
    ("archive/sources/geopolitics/source.md", "archive/sources/geopolitics/source.md"),
    ("narrative-geopolitics-other/source.md", "narrative-geopolitics-other/source.md"),
    ("docs/narrative-geopolitics/source.md", "docs/narrative-geopolitics/source.md"),
])
def test_opt_in_reference_normalization(value: str, expected: str) -> None:
    assert canonical_geopolitics_reference(value) == expected
    assert canonical_geopolitics_reference(expected) == expected


@pytest.mark.parametrize("value", [
    "", "/geopolitics/work", "\\\\server\\share", "C:geopolitics/work",
    "C:/geopolitics/work", "geopolitics/../outside", "geopolitics\\..\\outside",
    "narrative-geopolitics/archive/../../outside", "geopolitics/file:stream",
    "geopolitics/./work", "geopolitics//work", "geopolitics/work./file",
    "geopolitics/work /file", "geopolitics/\x00file",
])
def test_opt_in_rejects_unsafe_references(tmp_path: Path, value: str) -> None:
    with pytest.raises(ValueError, match="Unsafe"):
        canonical_geopolitics_reference(value)
    with pytest.raises(ValueError, match="Unsafe"):
        resolve_geopolitics_reference(tmp_path, value)


@pytest.mark.parametrize("physical", ["narrative-geopolitics", "geopolitics"])
def test_either_spelling_reads_same_record_without_mutation(tmp_path: Path, physical: str) -> None:
    root = tmp_path / physical
    record = root / "work" / "receipt.json"
    record.parent.mkdir(parents=True)
    original = b'{"id":"NG-001","path":"narrative-geopolitics/work/receipt.json"}\n'
    record.write_bytes(original)
    assert geopolitics_root(tmp_path) == root
    for spelling in ("narrative-geopolitics", "geopolitics"):
        assert resolve_geopolitics_reference(tmp_path, spelling) == root
        resolved = resolve_geopolitics_reference(tmp_path, spelling + "/work/receipt.json")
        assert resolved == record
        assert resolved.read_bytes() == original
        assert resolve_geopolitics_reference(tmp_path, spelling + "/missing.md") == root / "missing.md"
    assert sorted(p.name for p in tmp_path.iterdir()) == [physical]
    assert sorted(p.relative_to(root).as_posix() for p in root.rglob("*")) == ["work", "work/receipt.json"]


@pytest.mark.parametrize("layout", ["none", "both", "file"])
def test_invalid_root_layouts_fail_without_creation(tmp_path: Path, layout: str) -> None:
    if layout == "both":
        (tmp_path / "narrative-geopolitics").mkdir()
        (tmp_path / "geopolitics").mkdir()
    elif layout == "file":
        (tmp_path / "geopolitics").write_text("occupied", encoding="utf-8")
    before = sorted(p.name for p in tmp_path.iterdir())
    with pytest.raises(ValueError):
        geopolitics_root(tmp_path)
    for spelling in ("narrative-geopolitics", "geopolitics"):
        with pytest.raises(ValueError):
            resolve_geopolitics_reference(tmp_path, spelling + "/work/missing.md")
    assert sorted(p.name for p in tmp_path.iterdir()) == before


def test_archive_resolution_is_independent_of_domain_layout(tmp_path: Path) -> None:
    expected = tmp_path / "archive/sources/geopolitics/source.md"
    for layout in ("none", "both"):
        if layout == "both":
            (tmp_path / "narrative-geopolitics").mkdir()
            (tmp_path / "geopolitics").mkdir()
        for value in ("narrative-geopolitics/archive/source.md", "archive/sources/geopolitics/source.md"):
            assert resolve_geopolitics_reference(tmp_path, value) == expected
        assert not expected.exists()


def test_existing_domain_resolver_behavior_is_unchanged(tmp_path: Path) -> None:
    value = "narrative-geopolitics/work/receipt.json"
    assert canonical_repository_path(value) == value
    assert resolve_repository_path(tmp_path, value) == tmp_path / value


@pytest.mark.parametrize("location", ["root", "leaf", "archive"])
def test_repository_escaping_links_are_rejected(tmp_path: Path, location: str) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    if location == "root":
        link = repo / "geopolitics"
        reference = "narrative-geopolitics/work/file.md"
    elif location == "leaf":
        (repo / "geopolitics").mkdir()
        link = repo / "geopolitics/work"
        reference = "geopolitics/work/file.md"
    else:
        link = repo / "archive"
        reference = "narrative-geopolitics/archive/file.md"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as error:
        if os.name != "nt" or getattr(error, "winerror", None) != 1314:
            raise
        # Junctions exercise real path resolution without Windows symlink privilege.
        subprocess.run(
            ["cmd.exe", "/c", "mklink", "/J", str(link), str(outside)],
            check=True, capture_output=True, text=True,
        )
    with pytest.raises(ValueError, match="escapes repository"):
        resolve_geopolitics_reference(repo, reference)

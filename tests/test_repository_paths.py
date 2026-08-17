from pathlib import Path

from repository_paths import canonical_repository_path, resolve_repository_path


def test_geopolitics_archive_legacy_prefix_resolves_to_canonical_path(
    tmp_path: Path,
) -> None:
    expected = tmp_path / "archive" / "geopolitics" / "sources" / "day" / "source.md"

    assert canonical_repository_path(
        "narrative-geopolitics/archive/sources/day/source.md"
    ) == "archive/geopolitics/sources/day/source.md"
    assert resolve_repository_path(
        tmp_path, "narrative-geopolitics\\archive\\sources\\day\\source.md"
    ) == expected


def test_geopolitics_archive_alias_is_prefix_bounded() -> None:
    value = "narrative-geopolitics/archive-old/source.md"

    assert canonical_repository_path(value) == value

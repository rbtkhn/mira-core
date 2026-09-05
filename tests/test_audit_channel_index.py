import json
from pathlib import Path
import sys

import pytest

import audit_channel_index as audit


def configure_repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    manifest = tmp_path / "archive/sources/geopolitics/source-manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"sources": [
        {"host_slug": "dialogue-works", "date": "2026-09-04"},
        {"host_slug": "dialogue-works", "date": "2026-09-04"},
    ]}), encoding="utf-8")
    monkeypatch.setattr(audit, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(audit, "MANIFEST_PATH", manifest)
    return manifest


def write_index(root: Path, files: int) -> Path:
    index = root / "channels/channel-index.md"
    index.parent.mkdir(parents=True)
    index.write_text(
        "# Channels\n\n"
        f"| `dialogue-works` | Dialogue Works | `active` | A | [sources](shelf) | {files} | 1 | - | - | `2026-09-04` | `2026-09-04` |\n",
        encoding="utf-8",
    )
    return index


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
@pytest.mark.parametrize("files", [1, 2])
def test_audit_results_and_cli_are_layout_independent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
    layout: str, files: int,
) -> None:
    manifest = configure_repository(tmp_path, monkeypatch)
    index = write_index(tmp_path / layout, files)
    original = {p: p.read_bytes() for p in (manifest, index)}
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    expected = [] if files == 2 else [{
        "slug": "dialogue-works", "status": "active", "active_local_shelf": True,
        "mismatches": {"files": {"index": 1, "manifest": 2}},
    }]
    assert audit.audit_rows() == expected
    monkeypatch.setattr(sys, "argv", ["audit_channel_index.py", "--json", "--check"])
    if files == 1:
        with pytest.raises(SystemExit) as error:
            audit.main()
        assert error.value.code == 1
    else:
        audit.main()
    assert json.loads(capsys.readouterr().out) == {"findings": expected}
    assert {p: p.read_bytes() for p in original} == original
    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*")) == before


@pytest.mark.parametrize("layout", ["missing", "both"])
def test_invalid_domain_layout_is_not_reported_as_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, layout: str,
) -> None:
    configure_repository(tmp_path, monkeypatch)
    if layout == "both":
        for name in ("narrative-geopolitics", "geopolitics"):
            write_index(tmp_path / name, 2)
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    with pytest.raises(ValueError, match="exactly one"):
        audit.audit_rows()
    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*")) == before


def test_index_resolution_occurs_on_each_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_repository(tmp_path, monkeypatch)
    old_root = tmp_path / "narrative-geopolitics"
    write_index(old_root, 2)
    assert audit.audit_rows() == []
    # Move only a fixture, proving an imported caller does not cache the old path.
    old_root.rename(tmp_path / "geopolitics")
    assert audit.audit_rows() == []


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_missing_index_remains_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, layout: str,
) -> None:
    configure_repository(tmp_path, monkeypatch)
    (tmp_path / layout).mkdir()
    with pytest.raises(FileNotFoundError):
        audit.audit_rows()

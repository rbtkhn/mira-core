from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import archive_library


def base_registry() -> dict:
    return {
        "schema_version": 1,
        "registry_id": "mira-library-v1",
        "authority_boundary": "shelving only",
        "era_definitions": [
            {"id": "ancient", "label": "Ancient", "range": "BC to 476 AD", "start_year": None, "end_year": 476, "description": "Ancient"},
            {"id": "medieval", "label": "Medieval", "range": "476 AD to 1453 AD", "start_year": 476, "end_year": 1453, "description": "Medieval"},
            {"id": "colonial", "label": "Colonial", "range": "1453 AD to 1815 AD", "start_year": 1453, "end_year": 1815, "description": "Colonial"},
            {"id": "industrial", "label": "Industrial", "range": "1815 AD to 1991 AD", "start_year": 1815, "end_year": 1991, "description": "Industrial"},
            {"id": "digital", "label": "Digital", "range": "1991 AD to present", "start_year": 1991, "end_year": None, "description": "Digital"},
        ],
        "sources": [],
    }


def source(**overrides: object) -> dict:
    row = {
        "source_id": "LIB-ROME-LIVY",
        "title": "Ab Urbe Condita",
        "author": "Livy",
        "subject_era": "ancient",
        "source_composition_era": "ancient",
        "edition_era": "digital",
        "secondary_eras": [],
        "date_start": -27,
        "date_end": 17,
        "date_label": "c. 27 BC-17 AD",
        "era_basis": "composition_period",
        "civilization_tags": ["rome"],
        "source_type": "classical",
        "location": "citation-shell",
        "status": "stub",
        "notes": "Boundary fixture.",
    }
    row.update(overrides)
    return row


def write_scaffold(root: Path, registry: dict) -> None:
    library = root / "archive" / "library"
    library.mkdir(parents=True)
    (library / "README.md").write_text("# Mira Library\n", encoding="utf-8")
    (library / "library-registry.json").write_text(json.dumps(registry), encoding="utf-8")
    for era in archive_library.ERA_IDS:
        target = library / era
        target.mkdir()
        (target / "index.md").write_text(
            f"# {era.title()} Library Index\n\nEra: `{era}`\n\nNo sources admitted yet.\n",
            encoding="utf-8",
        )


def test_valid_empty_scaffold(tmp_path: Path, monkeypatch) -> None:
    write_scaffold(tmp_path, base_registry())
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    failures = archive_library.validate_scaffold(tmp_path)
    assert failures == []


def test_valid_populated_registry_and_boundaries() -> None:
    registry = base_registry()
    registry["sources"] = [
        source(source_id="LIB-ANCIENT-BC", date_start=-500, date_end=-400, subject_era="ancient"),
        source(source_id="LIB-476", date_start=476, date_end=476, subject_era="medieval", date_label="476 AD"),
        source(source_id="LIB-1453", date_start=1453, date_end=1453, subject_era="colonial", date_label="1453 AD"),
        source(source_id="LIB-1815", date_start=1815, date_end=1815, subject_era="industrial", date_label="1815 AD"),
        source(source_id="LIB-1991", date_start=1991, date_end=1991, subject_era="digital", date_label="1991 AD", source_type="digital-born"),
        source(source_id="LIB-MULTI", subject_era="colonial", secondary_eras=["industrial"], era_basis="multi_period"),
    ]
    assert archive_library.validate_registry(registry) == []


def test_invalid_registry_values_are_reported() -> None:
    registry = base_registry()
    registry["sources"] = [
        source(source_id="DUPLICATE"),
        source(source_id="DUPLICATE", subject_era="future"),
        source(source_id="BAD-TYPE", source_type="pamphlet"),
        source(source_id="BAD-STATUS", status="draft"),
        source(source_id="BAD-BASIS", era_basis="vibes"),
        source(source_id="BAD-DATES", date_start=10, date_end=1),
    ]
    failures = archive_library.validate_registry(registry)
    assert "duplicate library source_id: DUPLICATE" in failures
    assert "DUPLICATE has unknown subject_era: future" in failures
    assert "BAD-TYPE has invalid source_type: pamphlet" in failures
    assert "BAD-STATUS has invalid status: draft" in failures
    assert "BAD-BASIS has invalid era_basis: vibes" in failures
    assert "BAD-DATES date range is inverted" in failures


def test_missing_required_field_is_reported() -> None:
    registry = base_registry()
    row = source()
    del row["title"]
    registry["sources"] = [row]
    assert "LIB-ROME-LIVY missing required field: title" in archive_library.validate_registry(registry)


def test_matching_sources_filters() -> None:
    rows = [
        source(source_id="ROME", civilization_tags=["rome"], subject_era="ancient", source_type="classical", notes="republic"),
        source(source_id="CHINA", civilization_tags=["china"], subject_era="medieval", source_type="chronicle", notes="dynasty"),
        source(source_id="SPAN", civilization_tags=["rome"], subject_era="colonial", secondary_eras=["industrial"], source_type="primary", notes="company rule"),
    ]
    assert [row["source_id"] for row in archive_library.matching_sources(rows, era="industrial")] == ["SPAN"]
    assert [row["source_id"] for row in archive_library.matching_sources(rows, civilization="rome")] == ["ROME", "SPAN"]
    assert [row["source_id"] for row in archive_library.matching_sources(rows, source_type="chronicle")] == ["CHINA"]
    assert [row["source_id"] for row in archive_library.matching_sources(rows, query="company rule")] == ["SPAN"]


def test_cli_validate_list_and_search(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = base_registry()
    registry["sources"] = [
        source(source_id="ROME", civilization_tags=["rome"], notes="senate republic"),
        source(source_id="DIGITAL", subject_era="digital", civilization_tags=["america"], source_type="digital-born", notes="internet platform"),
    ]
    write_scaffold(tmp_path, registry)
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")

    assert archive_library.main(["validate", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "passed"
    assert archive_library.main(["list", "--era", "digital", "--json"]) == 0
    listed = json.loads(capsys.readouterr().out)
    assert [row["source_id"] for row in listed["sources"]] == ["DIGITAL"]
    assert archive_library.main(["search", "--query", "senate", "--civilization", "rome", "--type", "classical", "--json"]) == 0
    searched = json.loads(capsys.readouterr().out)
    assert [row["source_id"] for row in searched["sources"]] == ["ROME"]


def test_run_repo_exposes_library_surface() -> None:
    result = subprocess.run(
        [sys.executable, "tools/run_repo.py", "library", "validate", "--json"],
        cwd=Path(__file__).resolve().parent.parent,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(result.stdout)["status"] == "passed"

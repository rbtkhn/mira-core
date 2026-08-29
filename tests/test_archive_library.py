from __future__ import annotations

import copy
import hashlib
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
    (library / "text-sources-index.md").write_text(archive_library.render_text_sources_index(registry), encoding="utf-8")
    for era in archive_library.ERA_IDS:
        target = library / era
        target.mkdir()
        (target / "index.md").write_text(archive_library.render_era_index(registry, era), encoding="utf-8")


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


def test_text_metadata_validation() -> None:
    registry = base_registry()
    registry["sources"] = [
        source(source_id="OK-MISSING", text_status="missing"),
        source(source_id="BAD-TEXT-STATUS", text_status="ready"),
        source(source_id="BAD-COVERAGE", coverage_status="complete-ish"),
        source(source_id="BAD-COVERAGE-NOTES", coverage_notes=["partial"]),
        source(source_id="BAD-LICENSE", license_status="copyleft-ish"),
        source(source_id="BAD-HASH", text_sha256="abc"),
        source(source_id="BAD-BYTES", text_bytes=-1),
        source(source_id="AVAILABLE-MISSING", text_status="available"),
    ]
    failures = archive_library.validate_registry(registry)
    assert "BAD-TEXT-STATUS has invalid text_status: ready" in failures
    assert "BAD-COVERAGE has invalid coverage_status: complete-ish" in failures
    assert "BAD-COVERAGE-NOTES coverage_notes must be a string or null" in failures
    assert "BAD-LICENSE has invalid license_status: copyleft-ish" in failures
    assert "BAD-HASH has invalid text_sha256" in failures
    assert "BAD-BYTES text_bytes must be a non-negative integer or null" in failures
    assert "AVAILABLE-MISSING text_status available requires text_location" in failures
    assert "AVAILABLE-MISSING text_status available requires text_sha256" in failures


def test_expanded_source_coverage_values_are_valid() -> None:
    registry = base_registry()
    registry["sources"] = [
        source(source_id=f"COVERAGE-{index}", coverage_status=status, coverage_notes=f"{status} fixture.")
        for index, status in enumerate(
            [
                "representative-selection",
                "major-works-complete",
                "partial-work",
                "fragmentary",
                "metadata-only",
            ],
            start=1,
        )
    ]
    assert archive_library.validate_registry(registry) == []


def test_complete_surviving_corpus_requires_supported_scope_claim() -> None:
    digest = "a" * 64
    registry = base_registry()
    registry["sources"] = [
        source(
            source_id="OVERCLAIM",
            text_status="available",
            coverage_status="complete-surviving-corpus",
            coverage_notes="Everything important is here.",
            text_bodies=[
                {
                    "body_id": "OVERCLAIM-BODY",
                    "work_title": "One Work",
                    "text_location": "library-text://OVERCLAIM-BODY.txt",
                    "text_sha256": digest,
                    "text_bytes": 10,
                    "text_encoding": "utf-8",
                    "license_status": "public-domain",
                    "status": "available",
                }
            ],
        ),
        source(
            source_id="NO-BODY",
            text_status="missing",
            coverage_status="complete-surviving-corpus",
            coverage_notes="Portable store covers the surviving corpus represented by this source-authority record.",
        ),
    ]
    failures = archive_library.validate_registry(registry)
    assert "OVERCLAIM complete-surviving-corpus requires coverage_notes naming the surviving corpus represented" in failures
    assert "NO-BODY complete-surviving-corpus requires at least one available or verified text body" in failures


def test_text_body_metadata_validation() -> None:
    digest = "a" * 64
    registry = base_registry()
    registry["sources"] = [
        source(
            source_id="MULTI",
            text_bodies=[
                {
                    "body_id": "BODY-1",
                    "work_title": "Iliad",
                    "text_location": "library-text://BODY-1.txt",
                    "text_sha256": digest,
                    "text_bytes": 10,
                    "text_encoding": "utf-8",
                    "license_status": "public-domain",
                    "status": "available",
                    "coverage_status": "complete-work",
                    "coverage_notes": "Complete work body fixture.",
                },
                {
                    "body_id": "BODY-1",
                    "work_title": "",
                    "text_sha256": "bad",
                    "text_bytes": -1,
                    "status": "ready",
                    "coverage_status": "complete-ish",
                    "coverage_notes": ["bad"],
                },
            ],
        )
    ]
    failures = archive_library.validate_registry(registry)
    assert "duplicate library text body_id: BODY-1" in failures
    assert "MULTI text body BODY-1 has blank work_title" in failures
    assert "MULTI text body BODY-1 missing required field: license_status" in failures
    assert "MULTI text body BODY-1 has invalid status: ready" in failures
    assert "MULTI text body BODY-1 has invalid coverage_status: complete-ish" in failures
    assert "MULTI text body BODY-1 coverage_notes must be a string or null" in failures
    assert "MULTI text body BODY-1 has invalid text_sha256" in failures
    assert "MULTI text body BODY-1 text_bytes must be a non-negative integer" in failures


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


def test_library_audit_reports_all_eras_and_witness_gaps(tmp_path: Path, monkeypatch, capsys) -> None:
    digest = "a" * 64
    registry = base_registry()
    registry["sources"] = [
        source(
            source_id="ANCIENT-BILINGUAL",
            text_status="available",
            text_bodies=[
                {
                    "body_id": "ANCIENT-BILINGUAL-EN",
                    "work_title": "Histories",
                    "text_location": "library-text://ANCIENT-BILINGUAL-EN.txt",
                    "text_sha256": digest,
                    "text_bytes": 10,
                    "text_encoding": "utf-8",
                    "language": "english",
                    "license_status": "public-domain",
                    "status": "available",
                },
                {
                    "body_id": "ANCIENT-BILINGUAL-GRC",
                    "work_title": "Histories",
                    "text_location": "library-text://ANCIENT-BILINGUAL-GRC.xml",
                    "text_sha256": digest,
                    "text_bytes": 10,
                    "text_encoding": "utf-8",
                    "language": "ancient greek",
                    "license_status": "open-license",
                    "status": "available",
                },
            ],
        ),
        source(
            source_id="MEDIEVAL-STUB",
            subject_era="medieval",
            title="Chronicle",
            author="Medieval compiler",
            source_type="chronicle",
            civilization_tags=["france"],
            text_status="missing",
            notes="manuscript tradition fixture",
        ),
        source(
            source_id="DIGITAL-DB",
            subject_era="digital",
            title="Dataset",
            author="Platform archive",
            source_type="database",
            civilization_tags=["america"],
            text_status="missing",
            status="located",
            notes="digital platform dataset fixture",
        ),
    ]
    write_scaffold(tmp_path, registry)
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")

    assert archive_library.main(["audit", "--json"]) == 0
    audited = json.loads(capsys.readouterr().out)
    audit = audited["audit"]
    assert audit["summary"]["total_sources"] == 3
    assert audit["summary"]["bilingual_available"] == 1
    assert audit["by_era"]["ancient"] == 1
    assert audit["by_era"]["medieval"] == 1
    assert audit["by_era"]["digital"] == 1
    assert [row["source_id"] for row in audit["missing_english"]] == ["DIGITAL-DB", "MEDIEVAL-STUB"]
    flags = {row["source_id"]: row["flags"] for row in audit["special_modeling_required"]}
    assert "digital_record" in flags["DIGITAL-DB"]


def test_library_audit_filters_by_any_era_and_renders_markdown(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = base_registry()
    registry["sources"] = [
        source(source_id="ANCIENT", subject_era="ancient", text_status="missing"),
        source(
            source_id="MEDIEVAL",
            subject_era="medieval",
            title="Commentary Chain",
            author="Medieval textual tradition",
            source_type="religious",
            civilization_tags=["persia"],
            era_basis="multi_period",
            secondary_eras=["colonial"],
            text_status="missing",
            notes="canonical manuscript tradition",
        ),
    ]
    write_scaffold(tmp_path, registry)
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")

    assert archive_library.main(["audit", "--era", "medieval", "--json"]) == 0
    audited = json.loads(capsys.readouterr().out)
    assert audited["audit"]["era"] == "medieval"
    assert audited["audit"]["summary"]["total_sources"] == 1
    assert audited["audit"]["missing_original_language"][0]["source_id"] == "MEDIEVAL"
    assert audited["authority_effect"] == "none"

    assert archive_library.main(["audit", "--era", "medieval", "--format", "markdown"]) == 0
    markdown = capsys.readouterr().out
    assert markdown.startswith("# Medieval Library Audit")
    assert "`MEDIEVAL`" in markdown
    assert "Special Modeling Required" in markdown


def test_locate_and_verify_texts(tmp_path: Path, monkeypatch, capsys) -> None:
    text_root = tmp_path / "texts"
    text_root.mkdir()
    body = text_root / "livy.txt"
    body.write_text("Rome remembers.\n", encoding="utf-8")
    digest = hashlib.sha256(body.read_bytes()).hexdigest()
    registry = base_registry()
    registry["sources"] = [
        source(
            text_status="available",
            text_location=str(body),
            text_sha256=digest,
            text_bytes=body.stat().st_size,
            text_encoding="utf-8",
            license_status="public-domain",
        )
    ]
    write_scaffold(tmp_path, registry)
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")

    assert archive_library.main(["locate", "LIB-ROME-LIVY", "--json"]) == 0
    located = json.loads(capsys.readouterr().out)
    assert located["text_exists"] is True
    assert archive_library.main(["verify-texts", "--json"]) == 0
    verified = json.loads(capsys.readouterr().out)
    assert verified["status"] == "passed"
    body.write_text("changed\n", encoding="utf-8")
    assert archive_library.main(["verify-texts", "--json"]) == 1
    failed = json.loads(capsys.readouterr().out)
    assert failed["status"] == "failed"
    assert failed["failures"] == ["LIB-ROME-LIVY: text byte count mismatch", "LIB-ROME-LIVY: text sha256 mismatch"]


def test_verify_texts_reports_probable_site_chrome(tmp_path: Path, monkeypatch, capsys) -> None:
    text_root = tmp_path / "texts"
    text_root.mkdir()
    body = text_root / "livy.txt"
    body.write_text("Ab urbe condita.\nView history\n", encoding="utf-8")
    registry = base_registry()
    registry["sources"] = [
        source(
            text_status="available",
            text_location=str(body),
            text_sha256=hashlib.sha256(body.read_bytes()).hexdigest(),
            text_bytes=body.stat().st_size,
            text_encoding="utf-8",
            license_status="public-domain",
        )
    ]
    write_scaffold(tmp_path, registry)
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")

    assert archive_library.main(["verify-texts", "--json"]) == 1
    failed = json.loads(capsys.readouterr().out)
    assert failed["failures"] == ["LIB-ROME-LIVY: probable site chrome on line 2: View history"]


def test_census_texts_reports_private_payload_presence_by_era(tmp_path: Path, monkeypatch, capsys) -> None:
    text_root = tmp_path.parent / (tmp_path.name + "-state") / "library" / "texts"
    text_root.mkdir(parents=True)
    ancient_body = text_root / "ANCIENT-BODY.txt"
    ancient_body.write_text("ancient body\n", encoding="utf-8")
    registry = base_registry()
    registry["sources"] = [
        source(
            source_id="LIB-ANCIENT",
            subject_era="ancient",
            text_status="available",
            text_location="library-text://ANCIENT-BODY.txt",
            text_sha256=hashlib.sha256(ancient_body.read_bytes()).hexdigest(),
            text_bytes=ancient_body.stat().st_size,
            text_encoding="utf-8",
            license_status="public-domain",
        ),
        source(
            source_id="LIB-MEDIEVAL",
            subject_era="medieval",
            text_status="available",
            text_location="library-text://MISSING-MEDIEVAL-BODY.txt",
            text_sha256="0" * 64,
            text_bytes=12,
            text_encoding="utf-8",
            license_status="public-domain",
        ),
    ]
    write_scaffold(tmp_path, registry)
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")
    monkeypatch.setenv("MIRA_CORE_LIBRARY_TEXT_ROOT", str(text_root))

    assert archive_library.main(["census-texts", "--json"]) == 1
    census = json.loads(capsys.readouterr().out)
    assert census["status"] == "failed"
    assert census["library_wide"]["registry_body_count"] == 2
    assert census["library_wide"]["physical_payload_count"] == 1
    assert census["library_wide"]["missing_payload_count"] == 1
    medieval = next(row for row in census["eras"] if row["era"] == "medieval")
    assert medieval["representative_missing_body_ids"] == ["LIB-MEDIEVAL"]


def test_census_texts_era_filter_preserves_library_totals(tmp_path: Path, monkeypatch, capsys) -> None:
    text_root = tmp_path.parent / (tmp_path.name + "-state") / "library" / "texts"
    text_root.mkdir(parents=True)
    body = text_root / "ANCIENT-BODY.txt"
    body.write_text("ancient body\n", encoding="utf-8")
    registry = base_registry()
    registry["sources"] = [
        source(
            source_id="LIB-ANCIENT",
            subject_era="ancient",
            text_status="available",
            text_location="library-text://ANCIENT-BODY.txt",
            text_sha256=hashlib.sha256(body.read_bytes()).hexdigest(),
            text_bytes=body.stat().st_size,
            text_encoding="utf-8",
            license_status="public-domain",
        )
    ]
    write_scaffold(tmp_path, registry)
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")
    monkeypatch.setenv("MIRA_CORE_LIBRARY_TEXT_ROOT", str(text_root))

    assert archive_library.main(["census-texts", "--era", "ancient", "--json"]) == 0
    census = json.loads(capsys.readouterr().out)
    assert census["status"] == "passed"
    assert census["library_wide"]["registry_body_count"] == 1
    assert [row["era"] for row in census["eras"]] == ["ancient"]


def test_locate_and_verify_multiple_text_bodies(tmp_path: Path, monkeypatch, capsys) -> None:
    text_root = tmp_path.parent / (tmp_path.name + "-state") / "library" / "texts"
    text_root.mkdir(parents=True)
    iliad = text_root / "HOMER-ILIAD.txt"
    odyssey = text_root / "HOMER-ODYSSEY.txt"
    iliad.write_text("Sing, goddess.\n", encoding="utf-8")
    odyssey.write_text("Tell me, muse.\n", encoding="utf-8")
    registry = base_registry()
    registry["sources"] = [
        source(
            source_id="HOMER",
            text_status="available",
            text_bodies=[
                {
                    "body_id": "HOMER-ILIAD",
                    "work_title": "Iliad",
                    "text_location": "library-text://HOMER-ILIAD.txt",
                    "text_sha256": hashlib.sha256(iliad.read_bytes()).hexdigest(),
                    "text_bytes": iliad.stat().st_size,
                    "text_encoding": "utf-8",
                    "language": "english",
                    "translator": "Samuel Butler",
                    "editor": "",
                    "edition_label": "test Iliad",
                    "license_status": "public-domain",
                    "license_notes": "",
                    "status": "available",
                },
                {
                    "body_id": "HOMER-ODYSSEY",
                    "work_title": "Odyssey",
                    "text_location": "library-text://HOMER-ODYSSEY.txt",
                    "text_sha256": hashlib.sha256(odyssey.read_bytes()).hexdigest(),
                    "text_bytes": odyssey.stat().st_size,
                    "text_encoding": "utf-8",
                    "language": "english",
                    "translator": "Samuel Butler",
                    "editor": "",
                    "edition_label": "test Odyssey",
                    "license_status": "public-domain",
                    "license_notes": "",
                    "status": "available",
                },
            ],
        )
    ]
    write_scaffold(tmp_path, registry)
    monkeypatch.setenv("MIRA_CORE_LIBRARY_TEXT_ROOT", str(text_root))
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")

    assert archive_library.main(["locate", "HOMER", "--json"]) == 0
    located = json.loads(capsys.readouterr().out)
    assert [item["body"]["body_id"] for item in located["text_bodies"]] == ["HOMER-ILIAD", "HOMER-ODYSSEY"]
    assert all(item["text_exists"] for item in located["text_bodies"])
    assert archive_library.main(["verify-texts", "--json"]) == 0
    verified = json.loads(capsys.readouterr().out)
    assert verified["checked"] == 2
    assert verified["missing"] == 0


def test_admit_text_into_private_root(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = base_registry()
    registry["sources"] = [source(text_status="missing")]
    write_scaffold(tmp_path, registry)
    private_root = tmp_path.parent / (tmp_path.name + "-state") / "library" / "texts"
    source_file = tmp_path / "input.txt"
    source_file.write_text("Ab urbe condita.\n", encoding="utf-8")
    monkeypatch.setenv("MIRA_CORE_LIBRARY_TEXT_ROOT", str(private_root))
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")

    assert archive_library.main([
        "admit-text",
        "--source-id",
        "LIB-ROME-LIVY",
        "--file",
        str(source_file),
        "--edition",
        "test edition",
        "--license-status",
        "public-domain",
        "--language",
        "latin",
        "--json",
    ]) == 0
    admitted = json.loads(capsys.readouterr().out)
    assert admitted["body_imported_to_archive"] is False
    updated = json.loads((tmp_path / "archive" / "library" / "library-registry.json").read_text(encoding="utf-8"))
    row = updated["sources"][0]
    assert row["text_status"] == "available"
    assert row["text_location"] == "library-text://LIB-ROME-LIVY.txt"
    assert row["edition_label"] == "test edition"
    assert row["language"] == "latin"
    assert (private_root / "LIB-ROME-LIVY.txt").read_text(encoding="utf-8") == "Ab urbe condita.\n"


def test_admit_text_check_does_not_copy_or_update_registry(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = base_registry()
    registry["sources"] = [source(text_status="missing")]
    write_scaffold(tmp_path, registry)
    private_root = tmp_path.parent / (tmp_path.name + "-state") / "library" / "texts"
    source_file = tmp_path / "input.txt"
    source_file.write_text("Ab urbe condita.\n", encoding="utf-8")
    monkeypatch.setenv("MIRA_CORE_LIBRARY_TEXT_ROOT", str(private_root))
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")

    assert archive_library.main([
        "admit-text",
        "--source-id",
        "LIB-ROME-LIVY",
        "--file",
        str(source_file),
        "--edition",
        "test edition",
        "--license-status",
        "public-domain",
        "--check",
        "--json",
    ]) == 0
    checked = json.loads(capsys.readouterr().out)
    assert checked["registry_updated"] is False
    assert checked["would_copy"] is True
    assert not (private_root / "LIB-ROME-LIVY.txt").exists()
    unchanged = json.loads((tmp_path / "archive" / "library" / "library-registry.json").read_text(encoding="utf-8"))
    assert unchanged["sources"][0]["text_status"] == "missing"


def test_admit_multiple_text_bodies_without_overwriting(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = base_registry()
    registry["sources"] = [source(source_id="HOMER", title="Iliad; Odyssey", author="Homer", text_status="missing")]
    write_scaffold(tmp_path, registry)
    private_root = tmp_path.parent / (tmp_path.name + "-state") / "library" / "texts"
    iliad = tmp_path / "iliad.txt"
    odyssey = tmp_path / "odyssey.txt"
    iliad.write_text("Sing, goddess.\n", encoding="utf-8")
    odyssey.write_text("Tell me, muse.\n", encoding="utf-8")
    monkeypatch.setenv("MIRA_CORE_LIBRARY_TEXT_ROOT", str(private_root))
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")

    assert archive_library.main([
        "admit-text",
        "--source-id",
        "HOMER",
        "--body-id",
        "HOMER-ILIAD",
        "--work-title",
        "Iliad",
        "--file",
        str(iliad),
        "--edition",
        "test Iliad",
        "--license-status",
        "public-domain",
        "--coverage-status",
        "complete-work",
        "--coverage-notes",
        "Complete test body.",
        "--json",
    ]) == 0
    capsys.readouterr()
    assert archive_library.main([
        "admit-text",
        "--source-id",
        "HOMER",
        "--body-id",
        "HOMER-ODYSSEY",
        "--work-title",
        "Odyssey",
        "--file",
        str(odyssey),
        "--edition",
        "test Odyssey",
        "--license-status",
        "public-domain",
        "--json",
    ]) == 0
    updated = json.loads((tmp_path / "archive" / "library" / "library-registry.json").read_text(encoding="utf-8"))
    bodies = updated["sources"][0]["text_bodies"]
    assert [body["body_id"] for body in bodies] == ["HOMER-ILIAD", "HOMER-ODYSSEY"]
    assert bodies[0]["coverage_status"] == "complete-work"
    assert bodies[0]["coverage_notes"] == "Complete test body."
    assert bodies[1]["coverage_status"] == "unknown"
    assert bodies[1]["coverage_notes"] == ""
    assert updated["sources"][0]["text_status"] == "available"
    assert (private_root / "HOMER-ILIAD.txt").exists()
    assert (private_root / "HOMER-ODYSSEY.txt").exists()


def test_admit_text_rejects_unknown_or_restricted_license(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = base_registry()
    registry["sources"] = [source(text_status="missing")]
    write_scaffold(tmp_path, registry)
    private_root = tmp_path.parent / (tmp_path.name + "-state") / "library" / "texts"
    source_file = tmp_path / "input.txt"
    source_file.write_text("text\n", encoding="utf-8")
    monkeypatch.setenv("MIRA_CORE_LIBRARY_TEXT_ROOT", str(private_root))
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")

    assert archive_library.main([
        "admit-text",
        "--source-id",
        "LIB-ROME-LIVY",
        "--file",
        str(source_file),
        "--edition",
        "test edition",
        "--license-status",
        "unknown",
        "--json",
    ]) == 1
    assert "cannot admit text with license_status: unknown" in capsys.readouterr().err


def test_admit_text_rejects_non_private_root(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = base_registry()
    registry["sources"] = [source(text_status="missing")]
    write_scaffold(tmp_path, registry)
    source_file = tmp_path / "input.txt"
    source_file.write_text("text\n", encoding="utf-8")
    monkeypatch.setenv("MIRA_CORE_LIBRARY_TEXT_ROOT", str(tmp_path / "public-texts"))
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")
    monkeypatch.setattr(archive_library, "private_text_root_allowed", lambda root: False)

    assert archive_library.main([
        "admit-text",
        "--source-id",
        "LIB-ROME-LIVY",
        "--file",
        str(source_file),
        "--edition",
        "test edition",
        "--license-status",
        "public-domain",
        "--json",
    ]) == 1
    assert "library text root must remain outside Git" in capsys.readouterr().err


def test_render_index_command_writes_and_checks_drift(tmp_path: Path, monkeypatch, capsys) -> None:
    digest = "a" * 64
    registry = base_registry()
    registry["sources"] = [
        source(
            source_id="HOMER",
            title="Iliad",
            author="Homer",
            text_status="available",
            coverage_status="principal-work",
            coverage_notes="Principal work fixture.",
            text_bodies=[
                {
                    "body_id": "HOMER-ILIAD",
                    "work_title": "Iliad",
                    "text_location": "library-text://HOMER-ILIAD.txt",
                    "text_sha256": digest,
                    "text_bytes": 10,
                    "text_encoding": "utf-8",
                    "language": "english",
                    "translator": "Samuel Butler",
                    "editor": "",
                    "edition_label": "test Iliad",
                    "license_status": "public-domain",
                    "license_notes": "",
                    "coverage_status": "complete-work",
                    "coverage_notes": "Complete named work fixture.",
                    "status": "available",
                }
            ],
        )
    ]
    write_scaffold(tmp_path, registry)
    index = tmp_path / "archive" / "library" / "text-sources-index.md"
    index.write_text("stale\n", encoding="utf-8")
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")
    monkeypatch.setattr(archive_library, "TEXT_SOURCES_INDEX_PATH", index)

    assert archive_library.main(["render-index", "--check", "--json"]) == 1
    checked = json.loads(capsys.readouterr().out)
    assert checked["status"] == "failed"
    assert checked["would_update"] is True
    assert index.read_text(encoding="utf-8") == "stale\n"

    assert archive_library.main(["render-index", "--json"]) == 0
    rendered = json.loads(capsys.readouterr().out)
    assert rendered["index_updated"] is True
    assert rendered["text_bodies_indexed"] == 1
    assert "Source coverage" in index.read_text(encoding="utf-8")
    assert "complete-work" in index.read_text(encoding="utf-8")

    assert archive_library.main(["render-index", "--check", "--json"]) == 0
    current = json.loads(capsys.readouterr().out)
    assert current["status"] == "passed"
    assert current["would_update"] is False


def test_validate_scaffold_fails_on_stale_text_sources_index(tmp_path: Path, monkeypatch) -> None:
    registry = base_registry()
    registry["sources"] = [source(source_id="LIB-ROME-LIVY", text_status="missing")]
    write_scaffold(tmp_path, registry)
    index = tmp_path / "archive" / "library" / "text-sources-index.md"
    index.write_text("stale\n", encoding="utf-8")
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")
    monkeypatch.setattr(archive_library, "TEXT_SOURCES_INDEX_PATH", index)

    assert archive_library.validate_scaffold(tmp_path) == [
        "library text sources index is stale: archive/library/text-sources-index.md"
    ]


def test_render_index_detects_and_repairs_stale_medieval_index(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = base_registry()
    registry["sources"] = [
        source(
            source_id="LIB-MEDIEVAL-BEDE",
            author="Bede",
            title="Ecclesiastical History",
            subject_era="medieval",
            date_start=731,
            date_end=731,
            date_label="731 AD",
            source_type="chronicle",
            text_status="missing",
            coverage_status="principal-work",
        )
    ]
    write_scaffold(tmp_path, registry)
    medieval = tmp_path / "archive" / "library" / "medieval" / "index.md"
    medieval.write_text("stale\n", encoding="utf-8")
    monkeypatch.setattr(archive_library, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(archive_library, "LIBRARY_ROOT", tmp_path / "archive" / "library")
    monkeypatch.setattr(archive_library, "REGISTRY_PATH", tmp_path / "archive" / "library" / "library-registry.json")
    monkeypatch.setattr(archive_library, "TEXT_SOURCES_INDEX_PATH", tmp_path / "archive" / "library" / "text-sources-index.md")

    assert archive_library.main(["render-index", "--check", "--json"]) == 1
    checked = json.loads(capsys.readouterr().out)
    assert checked["stale_paths"] == ["archive/library/medieval/index.md"]
    assert archive_library.validate_scaffold(tmp_path) == [
        "library era index is stale: archive/library/medieval/index.md"
    ]

    assert archive_library.main(["render-index", "--json"]) == 0
    capsys.readouterr()
    assert "`LIB-MEDIEVAL-BEDE`" in medieval.read_text(encoding="utf-8")
    assert archive_library.validate_scaffold(tmp_path) == []


def test_run_repo_exposes_library_surface() -> None:
    result = subprocess.run(
        [sys.executable, "tools/run_repo.py", "library", "validate", "--json"],
        cwd=Path(__file__).resolve().parent.parent,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(result.stdout)["status"] == "passed"

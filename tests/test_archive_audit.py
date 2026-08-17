from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import archive_audit
import report_archive_density


def source_text(
    *,
    pub_date: str,
    url: str,
    routing: str = "confirmed",
    section_count: int = 0,
    headings: int = 0,
    extra_frontmatter: str = "",
) -> str:
    sections = "".join(f"### Segment {index}\n\nText {index}.\n\n" for index in range(headings))
    return (
        "---\n"
        f"pub_date: {pub_date}\n"
        f"source_url: \"{url}\"\n"
        f"routing_state: {routing}\n"
        f"section_count: {section_count}\n"
        f"transcript_curation: {'curated_sectioned' if section_count else 'preserved_unsectioned'}\n"
        "asr_repair_applied: false\n"
        f"{extra_frontmatter}"
        "---\n"
        "# Source\n\n"
        "## Transcript\n\n"
        f"{sections}Body.\n"
    )


def authored_source_text(*, pub_date: str, url: str) -> str:
    return (
        "---\n"
        f"pub_date: {pub_date}\n"
        "kind: source-text\n"
        "source_form: substack-post\n"
        f"source_url: \"{url}\"\n"
        "routing_state: confirmed\n"
        "section_count: 0\n"
        "transcript_curation: preserved_unsectioned\n"
        "asr_repair_applied: false\n"
        "---\n"
        "# Source\n\n"
        "## Source Text\n\n"
        "Body.\n"
    )


def archive_fixture(tmp_path: Path) -> tuple[Path, Path, Path, list[dict]]:
    repo = tmp_path / "repo"
    sources = repo / "archive" / "geopolitics" / "sources"
    manifest_path = sources.parent / "source-manifest.json"
    rows: list[dict] = []
    specifications = (
        ("2026-01-10", "one", ["voice-a"], "host-a"),
        ("2026-01-20", "two", ["voice-b"], "host-a"),
        ("2026-03-05", "three", ["voice-a"], "host-b"),
    )
    for run_date, stem, voices, host in specifications:
        day = sources / run_date
        day.mkdir(parents=True, exist_ok=True)
        path = day / f"source-{stem}.md"
        relative = path.relative_to(repo).as_posix()
        url = f"https://example.test/{stem}"
        path.write_text(source_text(pub_date=run_date, url=url), encoding="utf-8", newline="\n")
        rows.append(
            {
                "date": run_date,
                "title": stem,
                "local_path": relative,
                "source_url": url,
                "voice_slugs": voices,
                "host_slug": host,
            }
        )
    manifest_path.write_text(
        json.dumps({"manifest_id": "test", "source_count": len(rows), "sources": rows}),
        encoding="utf-8",
        newline="\n",
    )
    return repo, sources, manifest_path, rows


def build(tmp_path: Path, arguments: list[str]) -> dict:
    repo, sources, manifest, _ = archive_fixture(tmp_path)
    return archive_audit.build_audit(
        archive_audit.parse_args(arguments),
        repo_root=repo,
        sources_root=sources,
        manifest_path=manifest,
    )


def test_month_date_range_and_whole_corpus_scopes(tmp_path: Path) -> None:
    month = build(tmp_path / "month", ["--month", "2026-01"])
    date_range = build(
        tmp_path / "range",
        ["--start-date", "2026-01-15", "--end-date", "2026-03-05"],
    )
    whole = build(tmp_path / "whole", ["--whole-corpus"])
    assert month["summary"]["scoped_rows"] == 2
    assert date_range["summary"]["scoped_rows"] == 2
    assert whole["summary"]["scoped_rows"] == 3
    assert whole["as_of"] == "2026-03-05"


def test_repeated_filters_are_or_within_and_across_dimensions(tmp_path: Path) -> None:
    payload = build(
        tmp_path,
        [
            "--whole-corpus",
            "--voice-slug",
            "voice-a",
            "--voice-slug",
            "voice-b",
            "--host-slug",
            "host-b",
        ],
    )
    assert payload["summary"]["scoped_rows"] == 1
    assert payload["coverage"]["hosts"] == {
        "host-b": {"months_present": ["2026-03"], "months_missing": []}
    }


def test_empty_scope_is_warning_and_not_failure(tmp_path: Path) -> None:
    payload = build(tmp_path, ["--month", "2025-01"])
    assert payload["disposition"] == "pass"
    assert payload["scope"]["empty"] is True
    assert "scope.no_matches" in {item["rule_id"] for item in payload["findings"]}


def test_structural_and_repair_findings_are_classified(tmp_path: Path) -> None:
    repo, sources, manifest_path, rows = archive_fixture(tmp_path)
    rows[0]["source_url"] = rows[1]["source_url"]
    rows[0]["voice_slugs"] = []
    rows[0]["host_slug"] = ""
    first = repo / rows[0]["local_path"]
    first.write_text(
        source_text(
            pub_date="2026-01-11",
            url=rows[1]["source_url"],
            routing="provisional",
            section_count=2,
            headings=1,
        ),
        encoding="utf-8",
        newline="\n",
    )
    missing = repo / rows[1]["local_path"]
    missing.unlink()
    orphan = sources / "2026-01-15" / "source-orphan.md"
    orphan.parent.mkdir(parents=True)
    orphan.write_text(source_text(pub_date="2026-01-15", url="https://example.test/orphan"), encoding="utf-8", newline="\n")
    manifest_path.write_text(
        json.dumps({"source_count": 99, "sources": rows}), encoding="utf-8", newline="\n"
    )
    payload = archive_audit.build_audit(
        archive_audit.parse_args(["--month", "2026-01"]),
        repo_root=repo,
        sources_root=sources,
        manifest_path=manifest_path,
    )
    rules = {item["rule_id"] for item in payload["findings"]}
    assert {
        "archive.orphan_file",
        "manifest.count_mismatch",
        "manifest.duplicate_url",
        "manifest.file_missing",
        "repair.section_metadata_mismatch",
        "routing.host_missing",
        "routing.provisional",
        "routing.voice_missing",
        "source.pub_date_mismatch",
    } <= rules
    provisional = next(item for item in payload["findings"] if item["rule_id"] == "routing.provisional")
    assert "landing-time provisional" in provisional["detail"]
    assert "not by itself an unresolved routing defect" in provisional["detail"]
    assert payload["benchmarks"]["warning_distribution"]["routing.provisional"] == 1
    assert payload["benchmarks"]["provisional_routing_warnings"] == 1
    assert payload["benchmarks"]["repair_candidate_warnings"] == 1
    assert payload["disposition"] == "fail"


def test_authored_source_text_marker_is_valid_body(tmp_path: Path) -> None:
    repo, sources, manifest_path, rows = archive_fixture(tmp_path)
    run_date = "2026-01-25"
    day = sources / run_date
    day.mkdir(parents=True, exist_ok=True)
    path = day / "source-authored.md"
    relative = path.relative_to(repo).as_posix()
    url = "https://example.substack.com/p/source"
    path.write_text(authored_source_text(pub_date=run_date, url=url), encoding="utf-8", newline="\n")
    rows.append(
        {
            "date": run_date,
            "title": "authored",
            "local_path": relative,
            "source_url": url,
            "voice_slugs": ["voice-a"],
            "host_slug": "upstream-unresolved",
        }
    )
    manifest_path.write_text(
        json.dumps({"source_count": len(rows), "sources": rows}),
        encoding="utf-8",
        newline="\n",
    )

    payload = archive_audit.build_audit(
        archive_audit.parse_args(["--month", "2026-01"]),
        repo_root=repo,
        sources_root=sources,
        manifest_path=manifest_path,
    )

    authored_findings = [
        item for item in payload["findings"] if item["path"] == relative
    ]
    assert "source.malformed" not in {item["rule_id"] for item in authored_findings}


def test_duran_mercouris_provisional_blank_host_metadata_is_flagged(tmp_path: Path) -> None:
    repo, sources, manifest_path, rows = archive_fixture(tmp_path)
    run_date = "2026-01-25"
    day = sources / run_date
    day.mkdir(parents=True, exist_ok=True)
    path = day / "source-duran-mercouris-weak.md"
    relative = path.relative_to(repo).as_posix()
    path.write_text(
        source_text(
            pub_date=run_date,
            url="https://example.test/duran",
            routing="provisional",
            extra_frontmatter=(
                "channel_name: \n"
                "host_slug: the-duran\n"
                "host: \n"
                "thread: mercouris\n"
            ),
        ),
        encoding="utf-8",
        newline="\n",
    )
    rows.append(
        {
            "date": run_date,
            "title": "duran",
            "local_path": relative,
            "source_url": "https://example.test/duran",
            "voice_slugs": ["mercouris"],
            "host_slug": "the-duran",
        }
    )
    manifest_path.write_text(
        json.dumps({"source_count": len(rows), "sources": rows}),
        encoding="utf-8",
        newline="\n",
    )

    payload = archive_audit.build_audit(
        archive_audit.parse_args(["--month", "2026-01"]),
        repo_root=repo,
        sources_root=sources,
        manifest_path=manifest_path,
    )

    rules = {item["rule_id"] for item in payload["findings"]}
    assert "routing.provisional" in rules
    assert "routing.duran_mercouris_metadata_weak" in rules


def test_missing_months_stop_at_manifest_as_of(tmp_path: Path) -> None:
    payload = build(
        tmp_path,
        ["--start-date", "2026-01-01", "--end-date", "2026-12-31"],
    )
    assert payload["scope"]["effective_end"] == "2026-03-05"
    assert payload["coverage"]["missing_months"] == ["2026-02"]
    assert payload["benchmarks"]["future_unlanded_days"] == 301


def test_benchmark_json_and_markdown_are_additive(tmp_path: Path) -> None:
    payload = build(tmp_path, ["--month", "2026-01"])

    assert payload["schema_version"] == "1.0"
    assert payload["benchmarks"]["requested_days"] == 31
    assert payload["benchmarks"]["effective_landed_days"] == 31
    assert payload["benchmarks"]["landed_days_with_rows"] == 2
    assert payload["benchmarks"]["landed_horizon_completeness_pct"] == 6.5
    assert payload["benchmarks"]["file_presence_pct"] == 100.0
    assert payload["benchmarks"]["routing_completeness_pct"] == 100.0
    assert payload["benchmarks"]["density_distribution"]["thin"] == 31
    assert payload["benchmarks"]["density_distribution"]["very_dense_overlay"] == 0

    rendered = archive_audit.render_markdown(payload)
    assert "## Benchmarks" in rendered
    assert "Future/unlanded days" in rendered


def test_results_are_deterministic_under_manifest_reordering(tmp_path: Path) -> None:
    repo, sources, manifest_path, rows = archive_fixture(tmp_path)
    args = archive_audit.parse_args(["--whole-corpus"])
    first = archive_audit.build_audit(
        args, repo_root=repo, sources_root=sources, manifest_path=manifest_path
    )
    manifest_path.write_text(
        json.dumps({"manifest_id": "test", "source_count": 3, "sources": list(reversed(rows))}),
        encoding="utf-8",
        newline="\n",
    )
    second = archive_audit.build_audit(
        args, repo_root=repo, sources_root=sources, manifest_path=manifest_path
    )
    assert first == second


def test_markdown_and_json_payloads_are_equivalent(tmp_path: Path) -> None:
    payload = build(tmp_path, ["--whole-corpus"])
    markdown = archive_audit.render_markdown(payload)
    assert payload["as_of"] in markdown
    assert str(payload["summary"]["scoped_rows"]) in markdown
    assert "Authority effect: `none`" in markdown


def test_audit_is_read_only_and_density_classification_is_shared(tmp_path: Path) -> None:
    repo, sources, manifest_path, _ = archive_fixture(tmp_path)
    before = {
        path.relative_to(repo).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in repo.rglob("*")
        if path.is_file()
    }
    archive_audit.build_audit(
        archive_audit.parse_args(["--whole-corpus"]),
        repo_root=repo,
        sources_root=sources,
        manifest_path=manifest_path,
    )
    after = {
        path.relative_to(repo).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in repo.rglob("*")
        if path.is_file()
    }
    assert before == after
    assert report_archive_density.density_class(7) == archive_audit.density_class(7)
    assert report_archive_density.classifications("dense", 7, 0, 0, 0, 0.0) == archive_audit.density_labels("dense", 7, 0, 0, 0, 0.0)


def test_orphan_scan_visits_only_existing_scoped_date_directories(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo, sources, manifest_path, _ = archive_fixture(tmp_path)
    visited: list[Path] = []
    original_rglob = Path.rglob

    def tracked_rglob(path: Path, pattern: str):
        visited.append(path)
        return original_rglob(path, pattern)

    monkeypatch.setattr(Path, "rglob", tracked_rglob)
    archive_audit.build_audit(
        archive_audit.parse_args(["--month", "2026-01"]),
        repo_root=repo,
        sources_root=sources,
        manifest_path=manifest_path,
    )

    assert visited == [sources / "2026-01-10", sources / "2026-01-20"]


def test_filtered_scope_skips_orphan_filesystem_scan(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo, sources, manifest_path, _ = archive_fixture(tmp_path)

    def unexpected_rglob(path: Path, pattern: str):
        raise AssertionError(f"unexpected orphan scan under {path} for {pattern}")

    monkeypatch.setattr(Path, "rglob", unexpected_rglob)
    payload = archive_audit.build_audit(
        archive_audit.parse_args(
            ["--whole-corpus", "--voice-slug", "voice-a"]
        ),
        repo_root=repo,
        sources_root=sources,
        manifest_path=manifest_path,
    )

    assert payload["summary"]["scoped_rows"] == 2
    assert "archive.orphan_file" not in {
        item["rule_id"] for item in payload["findings"]
    }


@pytest.mark.parametrize(
    "arguments",
    (
        [],
        ["--month", "2026-01", "--whole-corpus"],
        ["--start-date", "2026-01-01"],
        ["--end-date", "2026-01-31", "--whole-corpus"],
        ["--month", "2026-13"],
        ["--start-date", "2026-02-01", "--end-date", "2026-01-01"],
    ),
)
def test_invalid_cli_scope_exits_two(arguments: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        archive_audit.parse_args(arguments)
    assert error.value.code == 2


def test_archive_audit_main_emits_json_without_writes(
    tmp_path: Path,
    capsys,
) -> None:
    repo, sources, manifest_path, _ = archive_fixture(tmp_path)
    before = {
        path.relative_to(repo).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in repo.rglob("*")
        if path.is_file()
    }

    result = archive_audit.main(
        ["--month", "2026-01", "--format", "json"],
        repo_root=repo,
        sources_root=sources,
        manifest_path=manifest_path,
    )

    payload = json.loads(capsys.readouterr().out)
    after = {
        path.relative_to(repo).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in repo.rglob("*")
        if path.is_file()
    }
    assert result == 0
    assert payload["authority_effect"] == "none"
    assert payload["capability_token"] is False
    assert after == before


def test_archive_density_is_deprecated_but_compatible() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "report_archive_density.py"), "--month", "1900-01"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "days=31" in result.stdout
    assert "DEPRECATED" in result.stderr

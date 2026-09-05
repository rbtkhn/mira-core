import pytest

import reality
import verification
import test_reality as reality_tests
import test_verification as packet_tests


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_default_packet_writer_follows_layout(tmp_path, monkeypatch, layout):
    template = packet_tests.template()
    work = tmp_path / layout / "work"
    directory = work / "verification"
    directory.mkdir(parents=True)
    (directory / "_packet-template.md").write_text(template, encoding="utf-8")
    monkeypatch.setattr(verification, "REPO_ROOT", tmp_path)
    first = verification.create_packet("2026-07-10", "test")
    assert first.is_relative_to(directory / "packets")
    assert verification.parse_packet(first).packet_id == "VER-20260710-01"
    assert verification.next_packet_id("2026-07-10") == "VER-20260710-02"
    assert not (tmp_path / ("geopolitics" if layout == "narrative-geopolitics" else "narrative-geopolitics")).exists()


@pytest.mark.parametrize("both", [False, True])
def test_default_writers_fail_before_mutation_for_invalid_roots(tmp_path, monkeypatch, both):
    if both:
        (tmp_path / "geopolitics").mkdir()
        (tmp_path / "narrative-geopolitics").mkdir()
    monkeypatch.setattr(verification, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(reality, "REPO_ROOT", tmp_path)
    before = sorted(tmp_path.rglob("*"))
    with pytest.raises(ValueError):
        verification.create_packet("2026-07-10", "test")
    with pytest.raises(ValueError):
        reality.write_record({"id": "CLM-20260710-001", "kind": "claim"})
    assert sorted(tmp_path.rglob("*")) == before


def test_explicit_views_root_keeps_registry_in_fixture(tmp_path, monkeypatch):
    root = tmp_path / "isolated" / "work" / "reality"
    root.mkdir(parents=True)
    # No domain exists under REPO_ROOT: explicit output roots need no default lookup.
    monkeypatch.setattr(reality, "REPO_ROOT", tmp_path / "missing")
    source = reality_tests.source("VSRC-TEST", "en", "western_independent")
    reality.write_record(source, root)
    assert reality.write_views(root) == []
    registry = root.parent / "verification" / "source-registry.md"
    assert registry.read_text(encoding="utf-8") == reality.render_source_registry(reality.load_records(root))
    assert reality.write_views(root, check=True) == []
    assert not (tmp_path / "missing").exists()


def test_same_process_reality_rename_preserves_digest(tmp_path, monkeypatch):
    old = tmp_path / "narrative-geopolitics"
    old.mkdir()
    monkeypatch.setattr(reality, "REPO_ROOT", tmp_path)
    record = reality.new_claim("CLM-20260710-001", "2026-07-10", "event", "A historical claim")
    path = reality.write_record(record)
    before = path.read_bytes()
    digest = reality.subgraph_digest([record["id"]])
    old.rename(tmp_path / "geopolitics")
    assert reality.record_path("claim", record["id"]).read_bytes() == before
    assert reality.subgraph_digest([record["id"]]) == digest


def test_missing_explicit_template_leaves_no_packet_directory(tmp_path):
    with pytest.raises(FileNotFoundError):
        verification.create_packet("2026-07-10", "test", tmp_path / "packets", tmp_path / "missing.md")
    assert not (tmp_path / "packets").exists()


def test_historical_artifact_alias_is_read_without_rewriting_packet(tmp_path):
    target = tmp_path / "geopolitics" / "work" / "daily" / "2026-07-10" / "synthesis.md"
    target.parent.mkdir(parents=True)
    target.write_text("historical body", encoding="utf-8")
    path = packet_tests.write_packet(tmp_path / "packets")
    text = path.read_text(encoding="utf-8")
    import re
    text = re.sub(r"Affected artifacts: `[^`]*`", "Affected artifacts: `narrative-geopolitics/work/daily/2026-07-10/synthesis.md`", text)
    path.write_text(text, encoding="utf-8")
    failures = verification.validate_packet(verification.parse_packet(path), tmp_path, packet_tests.ledger(tmp_path / "ledger.md"))
    assert not any("broken affected artifact" in item for item in failures)
    assert path.read_text(encoding="utf-8") == text


def test_explicit_record_context_needs_no_default_domain(tmp_path, monkeypatch):
    monkeypatch.setattr(reality, "REPO_ROOT", tmp_path)
    assert reality.claim_state("CLM-20260710-001", records={}) is None
    assert reality.subgraph_digest([], records={}) == reality.record_digest([])

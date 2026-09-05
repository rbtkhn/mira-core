import pytest

import test_daily_issue as issue_tests
import test_daily_run_validation as daily_tests
import verification


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_default_render_and_validation_follow_layout(tmp_path, monkeypatch, layout):
    issue = issue_tests.issue
    daily, ledger = issue_tests.fixture_tree(tmp_path)
    template = issue.default_template_path().read_bytes()
    domain = tmp_path / "narrative-geopolitics"
    (domain / "templates").mkdir()
    (domain / "templates" / "issue.md").write_bytes(template)
    if layout == "geopolitics":
        domain.rename(tmp_path / layout)
    monkeypatch.setattr(issue, "REPO_ROOT", tmp_path)
    context = issue.load_validation_context()
    model = issue.load_model(issue_tests.RUN_DATE, context=context)
    rendered = issue.render_model(model, context=context)
    target = tmp_path / layout / "work" / "daily" / issue_tests.RUN_DATE / "issue.md"
    target.write_text(rendered, encoding="utf-8")
    assert issue.validate_issue(issue_tests.RUN_DATE, require=True)[0] == []
    assert issue_tests.HOOK_ID in rendered
    assert "archive/sources/geopolitics/sources/" in rendered
    assert issue.load_model(issue_tests.RUN_DATE).input_digest == model.input_digest


def test_same_process_rename_preserves_render_bytes(tmp_path, monkeypatch):
    issue = issue_tests.issue
    issue_tests.fixture_tree(tmp_path)
    template = issue.default_template_path().read_bytes()
    old = tmp_path / "narrative-geopolitics"
    (old / "templates").mkdir()
    (old / "templates" / "issue.md").write_bytes(template)
    monkeypatch.setattr(issue, "REPO_ROOT", tmp_path)
    before = issue.render_model(issue.load_model(issue_tests.RUN_DATE))
    old.rename(tmp_path / "geopolitics")
    after = issue.render_model(issue.load_model(issue_tests.RUN_DATE))
    assert before == after


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_daily_validator_defaults_follow_layout(tmp_path, monkeypatch, layout):
    validator = daily_tests.validator
    daily_tests.configure_fixture(monkeypatch, tmp_path, daily_tests.complete_sources_text())
    baseline = validator.validate_run("2026-07-09")
    if layout == "geopolitics":
        (tmp_path / "narrative-geopolitics").rename(tmp_path / layout)
    for name in ("NG_ROOT", "DAILY_ROOT", "LEDGER_PATH", "MANIFEST_PATH"):
        monkeypatch.setattr(validator, name, None)
    assert validator.validate_run("2026-07-09") == baseline


@pytest.mark.parametrize("layout", ["narrative-geopolitics", "geopolitics"])
def test_verification_reads_local_reality_and_packet_roots(tmp_path, monkeypatch, layout):
    root = tmp_path / layout / "work" / "daily"
    day = root / "2026-07-09"
    day.mkdir(parents=True)
    claim_id = "OPC-20260709-01"
    (day / "synthesis.md").write_text(
        f"| `{claim_id}` | A bounded claim | `source_assertion` | `low` | `no` | `VER-20260709-01` |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(verification, "REPO_ROOT", tmp_path)
    seen = []
    def claim_state(identifier, root):
        seen.append((identifier, root))
        return None
    monkeypatch.setattr(issue_tests.issue.reality, "claim_state", claim_state)
    packet_roots = []
    def find_packet(identifier, root):
        packet_roots.append(root)
        return None
    monkeypatch.setattr(verification, "find_packet", find_packet)
    verification.day_payload("2026-07-09")
    assert seen == [(claim_id, root.parent / "reality")]
    assert packet_roots == [root.parent / "verification" / "packets"]
    explicit = tmp_path / "explicit-reality"
    verification.day_payload("2026-07-09", root, tmp_path / "packets", reality_root=explicit)
    assert seen[-1] == (claim_id, explicit)
    assert packet_roots[-1] == tmp_path / "packets"


@pytest.mark.parametrize("both", [False, True])
def test_defaults_reject_missing_or_ambiguous_domain(tmp_path, monkeypatch, both):
    if both:
        (tmp_path / "narrative-geopolitics").mkdir()
        (tmp_path / "geopolitics").mkdir()
    monkeypatch.setattr(issue_tests.issue, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(verification, "REPO_ROOT", tmp_path)
    for call in (lambda: issue_tests.issue.canonical_inputs("2026-07-09"),
                 lambda: verification.day_payload("2026-07-09")):
        with pytest.raises(ValueError):
            call()


def test_historical_archive_alias_resolves_without_rewriting_row(tmp_path, monkeypatch):
    validator = daily_tests.validator
    monkeypatch.setattr(validator, "REPO_ROOT", tmp_path)
    relative = "archive/sources/geopolitics/sources/2026-07-09/source.md"
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_text("historical bytes", encoding="utf-8")
    row = {"local_path": "narrative-geopolitics/archive/sources/2026-07-09/source.md"}
    assert validator.source_paths_exist([row]) == []
    assert validator.manifest_archive_paths([row]) == {relative}
    assert row["local_path"].startswith("narrative-geopolitics/archive/")

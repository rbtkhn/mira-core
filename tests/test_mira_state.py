from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

import mira_state
from portable_paths import PortablePathError, platform_state_root, resolve_state_root, state_path


@pytest.fixture(autouse=True)
def stub_choice_domain_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        mira_state, "choice_domain_verify",
        lambda path: {"valid": True, "choice_count": 0, "failures": []},
    )
    monkeypatch.setattr(mira_state, "archive_logical_parity", lambda canonical, replica: True)


def database(path: Path, *, prompts: list[str] | None = None, events: list[str] | None = None, version: int = 4, reordered: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    with connection:
        if reordered:
            connection.execute("CREATE TABLE choice_prompts(marker TEXT, choice_id TEXT PRIMARY KEY)")
            connection.execute("CREATE TABLE choice_events(marker TEXT, event_id TEXT PRIMARY KEY)")
            connection.executemany("INSERT INTO choice_prompts VALUES ('x', ?)", [(value,) for value in prompts or []])
            connection.executemany("INSERT INTO choice_events VALUES ('x', ?)", [(value,) for value in events or []])
        else:
            connection.execute("CREATE TABLE choice_prompts(choice_id TEXT PRIMARY KEY, marker TEXT)")
            connection.execute("CREATE TABLE choice_events(event_id TEXT PRIMARY KEY, marker TEXT)")
            connection.executemany("INSERT INTO choice_prompts VALUES (?, 'x')", [(value,) for value in prompts or []])
            connection.executemany("INSERT INTO choice_events VALUES (?, 'x')", [(value,) for value in events or []])
        connection.execute(f"PRAGMA user_version={version}")
    connection.close()


def generic_database(path: Path, version: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    with connection:
        connection.execute("CREATE TABLE records(id TEXT PRIMARY KEY)")
        connection.execute("INSERT INTO records VALUES ('one')")
        connection.execute(f"PRAGMA user_version={version}")
    connection.close()


def test_platform_state_roots() -> None:
    assert platform_state_root(environment={"LOCALAPPDATA": r"C:\Users\r\AppData\Local"}, platform="win32", home=Path("/h")) == Path(r"C:\Users\r\AppData\Local") / "MiraCore"
    assert platform_state_root(environment={"XDG_STATE_HOME": "/state"}, platform="linux", home=Path("/h")) == Path("/state/mira-core")
    assert platform_state_root(environment={}, platform="darwin", home=Path("/Users/r")) == Path("/Users/r/Library/Application Support/MiraCore")


def test_state_root_and_children_reject_git_and_escape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"; repo.mkdir()
    with pytest.raises(PortablePathError): resolve_state_root(repo / "private", repo_root=repo)
    external = tmp_path / "state"
    assert state_path("state/choice.sqlite3", root=external, repo_root=repo) == (external / "state/choice.sqlite3").resolve()
    with pytest.raises(PortablePathError): state_path("../escape", root=external, repo_root=repo)


def test_inventory_classifies_without_mutation(tmp_path: Path) -> None:
    source = tmp_path / "legacy"; source.mkdir()
    (source / "mira-core-choice-history.sqlite3").write_bytes(b"x")
    (source / "mira-core-test-temp").mkdir()
    (source / "another-project").mkdir()
    before = sorted(path.name for path in source.iterdir())
    report = mira_state.inventory(source)
    dispositions = {row["name"]: row["disposition"] for row in report["entries"]}
    assert dispositions["mira-core-choice-history.sqlite3"] == "migrate-active"
    assert dispositions["mira-core-test-temp"] == "disposable-candidate-no-action"
    assert dispositions["another-project"] == "out-of-scope-no-action"
    assert before == sorted(path.name for path in source.iterdir())


def test_choice_merge_preserves_distinct_rows_and_rejects_duplicates(tmp_path: Path) -> None:
    first, second, target = tmp_path / "one.sqlite3", tmp_path / "two.sqlite3", tmp_path / "target.sqlite3"
    database(first, prompts=["p1"], events=["e1"]); database(second, prompts=["p2"], events=["e2"])
    result = mira_state.merge_choices([first, second], target)
    assert result["preflight"]["expected_counts"] == {"choice_prompts": 2, "choice_events": 2}
    duplicate = tmp_path / "duplicate.sqlite3"; database(duplicate, prompts=["p1"])
    with pytest.raises(mira_state.StateError): mira_state.choice_preflight([first, duplicate])


def test_choice_merge_is_column_order_independent(tmp_path: Path) -> None:
    first, second, target = tmp_path / "one.sqlite3", tmp_path / "two.sqlite3", tmp_path / "target.sqlite3"
    database(first, prompts=["p1"], events=["e1"])
    database(second, prompts=["p2"], events=["e2"], reordered=True)
    result = mira_state.merge_choices([first, second], target)
    assert result["preflight"]["schema_order_drift"] == {
        "choice_prompts": True, "choice_events": True,
    }
    connection = sqlite3.connect(target)
    try:
        assert connection.execute("SELECT choice_id FROM choice_prompts ORDER BY choice_id").fetchall() == [("p1",), ("p2",)]
    finally:
        connection.close()


def fixture_source(tmp_path: Path) -> Path:
    source = tmp_path / "legacy"; source.mkdir()
    database(source / "narrative-choice-history.sqlite3", prompts=["old"], events=["old:e"])
    database(source / "mira-core-choice-history.sqlite3", prompts=["new"], events=["new:e"])
    generic_database(source / "narrative-cadence.sqlite3", 4)
    generic_database(source / "mira-mentorship.sqlite3", 1)
    canonical = source / "archive-canonical"; canonical.mkdir(); (canonical / "body.txt").write_text("body")
    replica = source / "archive-replica"; replica.mkdir(); (replica / "body.txt").write_text("body")
    (source / "narrative-system-archive-config.json").write_text(json.dumps({"schema_version": 1, "canonical_root": str(canonical), "replica_root": str(replica)}))
    return source


def test_migrate_check_is_non_mutating_and_execute_is_idempotent(tmp_path: Path) -> None:
    source, target = fixture_source(tmp_path), tmp_path / "target"
    preview = mira_state.migrate(source, target, check=True)
    assert not preview["mutated"] and not target.exists()
    result = mira_state.migrate(source, target, check=False)
    assert result["source_mutated"] is False
    assert mira_state.verify(target)["valid"]
    repeated = mira_state.migrate(source, target, check=False)
    assert repeated["already_migrated"] and not repeated["mutated"]


def test_full_migration_resumes_verified_continuity(tmp_path: Path) -> None:
    source, target = fixture_source(tmp_path), tmp_path / "target"
    continuity = continuity_fixture(tmp_path)
    mira_state.migrate_continuity(continuity, target, check=False)
    preview = mira_state.migrate(source, target, check=True)
    assert preview["resumed_continuity"]["valid"]
    result = mira_state.migrate(source, target, check=False)
    assert result["resumed_continuity"] is True
    assert mira_state.verify(target)["valid"]
    assert mira_state.continuity_verify(target)["valid"]


def test_full_migration_rejects_unreceipted_partial_continuity(tmp_path: Path) -> None:
    source, target = fixture_source(tmp_path), tmp_path / "target"
    (target / "continuity").mkdir(parents=True)
    with pytest.raises(mira_state.StateError, match="missing its receipt or inbox"):
        mira_state.migrate(source, target, check=True)


def test_archive_canonical_wins_and_divergent_replica_is_preserved(tmp_path: Path) -> None:
    source, target = fixture_source(tmp_path), tmp_path / "target"
    (source / "archive-replica/body.txt").write_text("divergent", encoding="utf-8")
    result = mira_state.migrate(source, target, check=False)
    disposition = result["archive_disposition"]
    assert disposition["legacy_replica_diverged"] is True
    assert (target / "archive/canonical/body.txt").read_text() == "body"
    assert (target / "archive/replica/body.txt").read_text() == "body"
    legacy = target / disposition["preserved_legacy_replica"] / "body.txt"
    assert legacy.read_text() == "divergent"
    assert mira_state.verify(target)["valid"]


def test_archive_parity_ignores_sqlite_connection_sidecars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source, target = fixture_source(tmp_path), tmp_path / "target"
    mira_state.migrate(source, target, check=False)
    (target / "archive/canonical/catalog.sqlite3-wal").write_bytes(b"transient")
    (target / "archive/canonical/catalog.sqlite3-shm").write_bytes(b"transient")
    monkeypatch.setattr(mira_state, "archive_logical_parity", lambda canonical, replica: True)
    assert mira_state.verify(target)["valid"]


def test_inaccessible_inactive_legacy_does_not_block_active_migration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source, target = fixture_source(tmp_path), tmp_path / "target"
    legacy = source / "historical-reference"
    legacy.mkdir()
    (legacy / "record.json").write_text("{}", encoding="utf-8")
    original = mira_state.copy_tree_verified

    def fail_only_legacy(source_path: Path, destination: Path):
        if source_path == legacy:
            raise __import__("shutil").Error([(str(source_path / "record.json"), str(destination / "record.json"), "permission denied")])
        return original(source_path, destination)

    monkeypatch.setattr(mira_state, "copy_tree_verified", fail_only_legacy)
    result = mira_state.migrate(source, target, check=False)
    assert result["copied"]["legacy/historical-reference"]["status"] == "preserved-in-place-unavailable"
    assert mira_state.verify(target)["valid"]


def test_export_requires_separate_empty_destination(tmp_path: Path) -> None:
    root = tmp_path / "state"; root.mkdir(); (root / "record.txt").write_text("value")
    output = tmp_path / "export"
    assert not mira_state.export(root, output, check=True)["mutated"]
    assert mira_state.export(root, output, check=False)["mutated"]
    assert (output / "export-manifest.json").is_file()
    with pytest.raises(mira_state.StateError): mira_state.export(root, root / "child", check=True)


def continuity_fixture(tmp_path: Path) -> Path:
    source = tmp_path / "legacy-rest"
    directory = source / "mira-core" / "01a001e8-c18a-7213-8afa-b7e4421aad72"
    directory.mkdir(parents=True)
    body = {
        "schema_version": 1, "event_id": "RSTE-one", "workspace_id": "mira-core",
        "session_id": "MS-01a001e8-c18a-7213-8afa-b7e4421aad72", "sequence": 1,
        "event_type": "rested", "occurred_at": "2026-08-17T10:01:00Z",
        "local_date": "2026-08-17", "timezone": "America/Denver",
        "authority_record_sha256": "a" * 64, "previous_event_sha256": None,
        "reentry_expected": False, "closure_debt": [], "repository_state": {},
        "requested_reviews": [],
    }
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    import hashlib
    body["event_sha256"] = hashlib.sha256(raw).hexdigest()
    (directory / "000001-RSTE-one.json").write_text(json.dumps(body), encoding="utf-8")
    return source


def test_continuity_migration_is_checked_verified_and_idempotent(tmp_path: Path) -> None:
    source, target = continuity_fixture(tmp_path), tmp_path / "state"
    preview = mira_state.migrate_continuity(source, target, check=True)
    assert preview["source"]["event_count"] == 1
    assert not target.exists()
    result = mira_state.migrate_continuity(source, target, check=False)
    assert result["mutated"] and result["receipt"]["source_mutated"] is False
    verified = mira_state.continuity_verify(target)
    assert verified["valid"] and verified["target"]["event_count"] == 1
    repeated = mira_state.migrate_continuity(source, target, check=False)
    assert repeated["already_migrated"] and not repeated["mutated"]


def test_continuity_verification_allows_valid_target_growth(tmp_path: Path) -> None:
    source, target = continuity_fixture(tmp_path), tmp_path / "state"
    mira_state.migrate_continuity(source, target, check=False)
    session = target / "continuity/inbox/mira-core/01a001e8-c18a-7213-8afa-b7e4421aad72"
    first = json.loads(next(session.glob("*.json")).read_text(encoding="utf-8"))
    body = {
        **{key: value for key, value in first.items() if key != "event_sha256"},
        "event_id": "RSTE-two", "sequence": 2, "event_type": "resumed",
        "previous_event_sha256": first["event_sha256"],
    }
    import hashlib
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    body["event_sha256"] = hashlib.sha256(raw).hexdigest()
    (session / "000002-RSTE-two.json").write_text(json.dumps(body), encoding="utf-8")
    verified = mira_state.continuity_verify(target)
    assert verified["valid"]
    assert verified["migrated_receipts_preserved"]
    assert verified["target_has_post_migration_events"]


def test_continuity_legacy_growth_is_synchronized_with_supplement(tmp_path: Path) -> None:
    source, target = continuity_fixture(tmp_path), tmp_path / "state"
    mira_state.migrate_continuity(source, target, check=False)
    session = source / "mira-core/01a001e8-c18a-7213-8afa-b7e4421aad72"
    first = json.loads(next(session.glob("*.json")).read_text(encoding="utf-8"))
    body = {
        **{key: value for key, value in first.items() if key != "event_sha256"},
        "event_id": "RSTE-two", "sequence": 2, "event_type": "resumed",
        "previous_event_sha256": first["event_sha256"],
    }
    import hashlib
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    body["event_sha256"] = hashlib.sha256(raw).hexdigest()
    (session / "000002-RSTE-two.json").write_text(json.dumps(body), encoding="utf-8")
    verification = mira_state.continuity_verify(target)
    assert verification["valid"] and verification["sync_required"]
    preview = mira_state.synchronize_continuity(target, verification, check=True)
    assert not preview["mutated"] and preview["copied"] == [
        "mira-core/01a001e8-c18a-7213-8afa-b7e4421aad72/000002-RSTE-two.json"
    ]
    result = mira_state.synchronize_continuity(target, verification, check=False)
    assert result["mutated"]
    assert (target / mira_state.CONTINUITY_SUPPLEMENT).is_file()
    assert mira_state.continuity_verify(target)["valid"]


def test_continuity_migration_rejects_digest_drift(tmp_path: Path) -> None:
    source, target = continuity_fixture(tmp_path), tmp_path / "state"
    receipt = next(source.rglob("*.json"))
    value = json.loads(receipt.read_text(encoding="utf-8"))
    value["event_type"] = "resumed"
    receipt.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(mira_state.StateError, match="digest mismatch"):
        mira_state.migrate_continuity(source, target, check=True)

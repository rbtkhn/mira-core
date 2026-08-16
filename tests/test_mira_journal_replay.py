from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

import mira_journal as subject


def event(category: str, refresh: bool, marker: str) -> dict:
    return {
        "event_digest": subject.sha256_bytes(marker.encode("utf-8")),
        "category": category,
        "expected_refresh": refresh,
    }


def manifest(*, coverage: str = "complete") -> dict:
    value = {
        "version_id": "MJ-20260808-v1",
        "coverage": coverage,
        "coverage_gaps": [] if coverage == "complete" else ["technical-reference-unavailable"],
        "events": [
            event("authority-approval", False, "approval"),
            event("authority-choreography", False, "assistant"),
            event("authority-user", True, "user"),
            event("other-session", True, "other"),
            event("git", True, "git"),
        ],
        "manifest_sha256": "a" * 64,
    }
    return value


def test_replay_policy_ignores_only_approval_choreography() -> None:
    result = subject.evaluate_freshness_manifest(manifest())
    assert result["old_policy"]["false_positive"] == 1
    assert result["current_policy"]["false_positive"] == 0
    assert result["current_policy"]["false_negative"] == 0
    assert result["metrics"] == {
        "approval_choreography_specificity": 1.0,
        "same_session_user_recall": 1.0,
        "cross_session_recall": 1.0,
        "git_activity_recall": 1.0,
    }
    assert result["sensitivity"]["remove-same-session-user-detection"]["missed"] == 1
    assert result["sensitivity"]["remove-cross-session-detection"]["missed"] == 1
    assert result["sensitivity"]["remove-git-detection"]["missed"] == 1
    assert all(
        row["kind"] == "counterfactual-mechanism-test"
        for row in result["sensitivity"].values()
    )


def _registry() -> dict:
    return {
        "entries": [
            {
                "entry_date": "2026-08-08",
                "versions": [{
                    "version_id": "MJ-20260808-v1",
                    "approval": {"approved_at": "2026-08-09T01:00:00Z"},
                }],
            },
            {
                "entry_date": "2026-08-15",
                "versions": [{
                    "version_id": "MJ-20260815-v1",
                    "approval": {"approved_at": "2026-08-16T01:00:00Z"},
                }],
            },
        ]
    }


def test_replay_is_deterministic_excludes_development_and_emits_measurement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(subject, "_git_blob", lambda ref, path: b"old-policy")
    monkeypatch.setattr(subject, "session_sources", lambda: [])
    monkeypatch.setattr(subject, "load_registry", _registry)
    monkeypatch.setattr(subject, "_freshness_episode_manifest", lambda entry, version, sources: manifest())
    kwargs = {
        "from_date": "2026-08-08", "to_date": "2026-08-15",
        "excluded_versions": {"MJ-20260815-v1"},
    }
    first = subject.build_freshness_replay(**kwargs)
    second = subject.build_freshness_replay(**kwargs)
    assert first == second
    assert [row["manifest"]["version_id"] for row in first["episodes"]] == ["MJ-20260808-v1"]
    assert first["comparability"]["passed"] is True
    assert first["cadence_measurement"]["series_id"] == "legacy-surviving-handoff"
    assert first["cadence_measurement"]["method_version_digest"] == subject.FRESHNESS_REPLAY_CADENCE["method_version_digest"]
    assert first["privacy"] == {
        "raw_session_bodies": False, "source_paths": False, "database_paths": False,
    }
    assert "C:\\" not in json.dumps(first)


def test_replay_requires_development_exclusion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subject, "_git_blob", lambda ref, path: b"old-policy")
    with pytest.raises(subject.JournalError, match="must exclude"):
        subject.build_freshness_replay(
            from_date="2026-08-08", to_date="2026-08-15", excluded_versions=set()
        )


def test_all_partial_cohort_emits_no_cadence_measurement(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subject, "_git_blob", lambda ref, path: b"old-policy")
    monkeypatch.setattr(subject, "session_sources", lambda: [])
    monkeypatch.setattr(subject, "load_registry", _registry)
    monkeypatch.setattr(
        subject, "_freshness_episode_manifest",
        lambda entry, version, sources: manifest(coverage="partial"),
    )
    result = subject.build_freshness_replay(
        from_date="2026-08-08", to_date="2026-08-15",
        excluded_versions={"MJ-20260815-v1"},
    )
    assert result["comparability"]["passed"] is False
    assert "cadence_measurement" not in result


def test_empty_complete_windows_do_not_qualify_as_comparable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    empty = manifest()
    empty["events"] = []
    monkeypatch.setattr(subject, "_git_blob", lambda ref, path: b"old-policy")
    monkeypatch.setattr(subject, "session_sources", lambda: [])
    monkeypatch.setattr(subject, "load_registry", _registry)
    monkeypatch.setattr(subject, "_freshness_episode_manifest", lambda entry, version, sources: empty)
    result = subject.build_freshness_replay(
        from_date="2026-08-08", to_date="2026-08-15",
        excluded_versions={"MJ-20260815-v1"},
    )
    assert result["aggregate"]["complete"] == 1
    assert result["aggregate"]["complete_discriminating"] == 0
    assert result["comparability"] == {
        "passed": False,
        "reason": "no-complete-discriminating-held-out-episode",
    }
    assert "cadence_measurement" not in result


def test_replay_output_must_be_external_and_check_does_not_write(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    packet = {
        "packet_sha256": "b" * 64, "aggregate": {},
        "comparability": {"passed": False},
    }
    monkeypatch.setattr(subject, "build_freshness_replay", lambda **kwargs: packet)
    output = tmp_path / "replay.json"
    args = argparse.Namespace(
        output=output, from_date="2026-08-08", to_date="2026-08-15",
        exclude_version=["MJ-20260815-v1"], check=True,
    )
    result = subject.command_freshness_replay(args)
    assert result["status"] == "ready"
    assert not output.exists()
    with pytest.raises(subject.JournalError, match="outside Git"):
        subject._private_output_path(subject.REPO_ROOT / "replay.json")


def test_closed_day_coverage_uses_full_source_inventory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    session_id = "MS-" + "1" * 8 + "-" + "2" * 4 + "-" + "3" * 4 + "-" + "4" * 4 + "-" + "5" * 12
    reference = {
        "schema_version": 2,
        "reference_id": "MJTR-20260808-v1",
        "session_coverage": [{"session_id": session_id}],
    }
    reference_path = tmp_path / "MJTR-20260808-v1.json"
    reference_path.write_text(json.dumps(reference), encoding="utf-8")
    monkeypatch.setattr(subject, "REFERENCE_ROOT", tmp_path)
    monkeypatch.setattr(subject, "resolved_records_for_session", lambda *args, **kwargs: {"MR-" + "a" * 24: {}})
    monkeypatch.setattr(subject, "git_commits", lambda *args, **kwargs: [])
    source = type("Source", (), {
        "session_id": session_id,
        "started_at": "2026-08-01T00:00:00Z",
        "last_observed_at": "2026-08-02T00:00:00Z",
    })()
    version = {
        "version_id": "MJ-20260808-v1",
        "content_sha256": "b" * 64,
        "coverage": {"as_of": "2026-08-09T06:00:00Z"},
        "approval": {
            "approved_at": "2026-08-10T00:00:00Z",
            "authority_ref": "MS-" + "6" * 8 + "-" + "7" * 4 + "-" + "8" * 4 + "-" + "9" * 4 + "-" + "a" * 12,
            "record_ref": "MR-" + "a" * 24,
        },
        "technical_reference": {
            "reference_id": "MJTR-20260808-v1",
            "content_sha256": subject.mira_journal_references.reference_digest(reference),
        },
    }
    result = subject._freshness_episode_manifest(
        {"entry_date": "2026-08-08"}, version, [source]
    )
    assert result["coverage"] == "complete"
    assert result["coverage_gaps"] == []

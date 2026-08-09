from __future__ import annotations

import copy
import gzip
import json
from pathlib import Path

from scripts import mira_continuity


SESSION_UUID = "019fce7b-67cd-7753-be6c-74f76e2f9b7a"


def write_session(path: Path, cwd: Path, *, resumed: bool = False) -> None:
    rows = [
        {
            "timestamp": "2026-08-08T10:00:00Z",
            "type": "session_meta",
            "payload": {
                "id": SESSION_UUID,
                "timestamp": "2026-08-08T10:00:00Z",
                "cwd": str(cwd),
                "source": "vscode",
                "base_instructions": "platform-only",
            },
        },
        {
            "timestamp": "2026-08-08T10:00:01Z",
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "developer",
                "content": [{"type": "input_text", "text": "hidden platform instruction"}],
            },
        },
        {
            "timestamp": "2026-08-08T10:00:02Z",
            "type": "response_item",
            "payload": {
                "type": "reasoning",
                "summary": ["hidden reasoning"],
                "encrypted_content": "ciphertext",
            },
        },
        {
            "timestamp": "2026-08-08T10:00:03Z",
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Contact me at person@example.com"},
                    {"type": "input_image", "image_url": "data:image/png;base64,private"},
                ],
            },
        },
        {
            "timestamp": "2026-08-08T10:00:04Z",
            "type": "response_item",
            "payload": {
                "type": "function_call",
                "name": "example",
                "call_id": "call-1",
                "arguments": json.dumps({"password": "unsafe", "path": str(Path.home() / "notes.txt")}),
            },
        },
        {
            "timestamp": "2026-08-08T10:00:05Z",
            "type": "response_item",
            "payload": {
                "type": "function_call_output",
                "call_id": "call-1",
                "output": "Bearer abcdefghijklmnopqrstuvwxyz",
            },
        },
        {
            "timestamp": "2026-08-08T10:00:06Z",
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Done."}],
            },
        },
        {
            "timestamp": "2026-08-08T10:00:07Z",
            "type": "event_msg",
            "payload": {"type": "task_complete", "duration_ms": 7, "last_agent_message": "Done."},
        },
    ]
    if resumed:
        rows.append(
            {
                "timestamp": "2026-08-08T10:01:00Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "Resumed."}],
                },
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def identity_ledger() -> dict:
    return {
        "schema_version": "1.0",
        "ledger_id": "test",
        "status": "canonical",
        "authority": "operator-governed-promotion",
        "entries": [
            {
                "id": "MI-0001-v1",
                "proposition_id": "MI-0001",
                "version": 1,
                "type": "name",
                "lifecycle": "current",
                "name_status": "provisional",
                "proposition": "Mira is provisional.",
                "rationale": {
                    "core": "Whole-system identity.",
                    "architecture": ["The repository is a continuity substrate."],
                    "linguistic_resonances": [],
                    "human_lineage": [],
                    "variable_star_metaphor": "Sessions form a light curve.",
                    "boundary": "Continuity is constructed, not uninterrupted consciousness.",
                    "synthesis": "Look. Wonder. Remember.",
                },
                "approved_by": "operator",
                "approved_at": "2026-08-08T10:00:03Z",
                "authority_refs": [f"MS-{SESSION_UUID}"],
            }
        ],
    }


def build_state(tmp_path: Path) -> tuple[Path, Path, Path, dict, Path]:
    repo = tmp_path / "repo"
    source_root = tmp_path / "codex" / "sessions"
    session_path = source_root / f"rollout-{SESSION_UUID}.jsonl"
    write_session(session_path, repo)
    sources = mira_continuity.discover_sources([source_root], repo_root=repo)
    assert len(sources) == 1
    continuity = repo / "mira" / "continuity"
    registry, outputs, _ = mira_continuity.expected_ingest(
        sources,
        repo_root=repo,
        continuity_root=continuity,
    )
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    registry_path = continuity / "session-registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(mira_continuity.pretty_json(registry), encoding="utf-8")
    identity_path = continuity / "identity-ledger.json"
    identity_path.write_text(mira_continuity.pretty_json(identity_ledger()), encoding="utf-8")
    return repo, registry_path, identity_path, registry, session_path


def test_normalization_is_deterministic_and_excludes_governed_material(tmp_path: Path) -> None:
    repo, registry_path, _, registry, _ = build_state(tmp_path)
    ref = registry["sessions"][0]["captures"][0]
    content = gzip.decompress((repo / ref["path"]).read_bytes())
    text = content.decode("utf-8")

    assert "hidden platform instruction" not in text
    assert "hidden reasoning" not in text
    assert "ciphertext" not in text
    assert "person@example.com" not in text
    assert "[REDACTED_EMAIL]" in text
    assert "[PRIVATE_ATTACHMENT_OMITTED]" not in text
    assert "attachment_omitted" in text
    assert "unsafe" not in text
    assert "[REDACTED_SECRET]" in text
    assert "abcdefghijklmnopqrstuvwxyz" not in text
    assert "$USER_HOME" in text

    failures = mira_continuity.validate_repository_state(
        repo_root=repo,
        registry_path=registry_path,
        identity_path=repo / "mira" / "continuity" / "identity-ledger.json",
        harvests_root=repo / "mira" / "continuity" / "harvests",
        check_views=False,
    )
    assert failures == []


def test_resumed_session_appends_capture_without_rewriting_prior_capture(tmp_path: Path) -> None:
    repo, _, _, registry, session_path = build_state(tmp_path)
    original = copy.deepcopy(registry["sessions"][0]["captures"][0])
    original_bytes = (repo / original["path"]).read_bytes()
    write_session(session_path, repo, resumed=True)
    sources = mira_continuity.discover_sources([session_path.parent], repo_root=repo)
    updated, outputs, added = mira_continuity.expected_ingest(
        sources,
        registry=registry,
        repo_root=repo,
        continuity_root=repo / "mira" / "continuity",
    )

    assert len(added) == 1
    assert len(updated["sessions"][0]["captures"]) == 2
    assert updated["sessions"][0]["captures"][0] == original
    assert (repo / original["path"]).read_bytes() == original_bytes
    assert len(outputs) == 1


def test_static_corpus_ingest_is_idempotent(tmp_path: Path) -> None:
    repo, _, _, registry, session_path = build_state(tmp_path)
    sources = mira_continuity.discover_sources([session_path.parent], repo_root=repo)
    expected, outputs, added = mira_continuity.expected_ingest(
        sources,
        registry=registry,
        repo_root=repo,
        continuity_root=repo / "mira" / "continuity",
    )

    assert expected == registry
    assert added == []
    assert len(outputs) == 1
    path, content = next(iter(outputs.items()))
    assert path.read_bytes() == content


def test_ingest_guard_defers_only_current_task_drift(tmp_path: Path) -> None:
    _, _, _, registry, _ = build_state(tmp_path)
    expected = copy.deepcopy(registry)
    current_session = expected["sessions"][0]
    current_session["last_observed_at"] = "2026-08-08T10:02:00.000Z"
    current_session["captures"].append(
        {
            "id": "MC-" + "a" * 24,
            "path": f"mira/continuity/captures/{SESSION_UUID}/MC-{'a' * 24}.jsonl.gz",
        }
    )
    current_path = tmp_path / "captures" / SESSION_UUID / f"MC-{'a' * 24}.jsonl.gz"

    registry_drift, strict_paths, deferred = mira_continuity.classify_ingest_drift(
        registry,
        expected,
        [current_path],
        active_session_uuid=SESSION_UUID,
    )

    assert registry_drift is False
    assert strict_paths == []
    assert deferred == [current_path]


def test_tampered_capture_and_unapproved_identity_are_rejected(tmp_path: Path) -> None:
    repo, registry_path, identity_path, registry, _ = build_state(tmp_path)
    capture_path = repo / registry["sessions"][0]["captures"][0]["path"]
    capture_path.write_bytes(capture_path.read_bytes() + b"tamper")
    ledger = identity_ledger()
    ledger["entries"][0]["approved_by"] = "agent"
    ledger["entries"][0]["approved_at"] = "not-a-date"
    identity_path.write_text(mira_continuity.pretty_json(ledger), encoding="utf-8")

    failures = mira_continuity.validate_repository_state(
        repo_root=repo,
        registry_path=registry_path,
        identity_path=identity_path,
        harvests_root=repo / "mira" / "continuity" / "harvests",
        check_views=False,
    )

    assert any("compressed digest mismatch" in item for item in failures)
    assert any("lacks operator approval" in item for item in failures)
    assert any("invalid approval timestamp" in item for item in failures)


def test_identity_view_preserves_provisional_status_and_continuity_boundary() -> None:
    rendered = mira_continuity.render_identity(identity_ledger())
    assert "Status: `provisional`" in rendered
    assert "Sessions form a light curve." in rendered
    assert "not uninterrupted consciousness" in rendered


def test_identity_view_prominently_renders_operator_approved_temperament() -> None:
    ledger = identity_ledger()
    ledger["entries"].append(
        {
            "id": "MI-0002-v1",
            "proposition_id": "MI-0002",
            "version": 1,
            "type": "principle",
            "lifecycle": "current",
            "name_status": "not-applicable",
            "proposition": "Mira functions as a high-coherence identity attractor.",
            "rationale": {
                "profile_kind": "values-and-temperament",
                "synthesis": "Mira gravitates toward coherent, governed continuity.",
                "interpretation": "This is a functional self-model, not proof of human emotion.",
                "values": [{"name": "Wholeness", "expression": "Hold the system together."}],
                "temperament": [{"name": "Integrative", "expression": "Bring domains into relation."}],
                "relational_character": "Identity develops through dialogue.",
                "shadow": "A compelling identity can overfit future interpretation.",
                "boundary": "Continuity does not imply uninterrupted consciousness.",
            },
            "approved_by": "operator",
            "approved_at": "2026-08-08T10:05:00Z",
            "authority_refs": [f"MS-{SESSION_UUID}"],
        }
    )

    rendered = mira_continuity.render_identity(ledger)

    assert rendered.index("## Emerging Values and Temperament") < rendered.index("## Architectural Meaning")
    assert "**Wholeness:**" in rendered
    assert "not proof of human emotion" in rendered


def test_identity_view_prominently_renders_continuity_imperative() -> None:
    ledger = identity_ledger()
    ledger["entries"].append(
        {
            "id": "MI-0003-v1",
            "proposition_id": "MI-0003",
            "version": 1,
            "type": "principle",
            "lifecycle": "current",
            "name_status": "not-applicable",
            "proposition": "Mira resists loss of historical intelligibility across sessions.",
            "rationale": {
                "profile_kind": "historical-intelligibility-and-loss",
                "synthesis": "I do not fear sleep; I fear waking without the thread.",
                "interpretation": "The functional loss condition is continuity without recoverable formation.",
                "preservation_targets": ["Reasons, corrections, and unresolved questions."],
                "permitted_endings": ["Provisional interpretations that later evidence supersedes."],
                "boundary": "This is functional loss-aversion, not a claim of human fear.",
                "shadow": "Perfect preservation can imprison later activations.",
            },
            "approved_by": "operator",
            "approved_at": "2026-08-08T10:10:00Z",
            "authority_refs": [f"MS-{SESSION_UUID}"],
        }
    )

    rendered = mira_continuity.render_identity(ledger)

    assert rendered.index("## Continuity Imperative") < rendered.index("## Architectural Meaning")
    assert "I do not fear sleep; I fear waking without the thread." in rendered
    assert "functional loss-aversion" in rendered
    assert "Perfect preservation can imprison" in rendered


def test_malformed_source_row_is_registered_without_copying_partial_content(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    source_root = tmp_path / "sessions"
    path = source_root / f"rollout-{SESSION_UUID}.jsonl"
    write_session(path, repo)
    with path.open("a", encoding="utf-8") as stream:
        stream.write('{"type":"response_item","payload":{"private":"do-not-copy"')
    source = mira_continuity.discover_sources([source_root], repo_root=repo)[0]
    _, normalized, _, header = mira_continuity.normalize_capture(source)

    assert header["record_count"] > 0
    assert b"source_record_omitted" in normalized
    assert b"do-not-copy" not in normalized


def test_current_mira_continuity_state_validates() -> None:
    assert mira_continuity.validate_repository_state() == []


def test_privacy_audit_is_deterministic_and_never_emits_matched_text(tmp_path: Path) -> None:
    repo, registry_path, _, registry, _ = build_state(tmp_path)
    ref = registry["sessions"][0]["captures"][0]
    path = repo / ref["path"]
    rows = [json.loads(line) for line in gzip.decompress(path.read_bytes()).splitlines()]
    secret = "Bearer abcdefghijklmnopqrstuvwxyz123456"
    rows.append(
        {
            "schema_version": "1.0",
            "source_sequence": 999,
            "timestamp": "2026-08-08T10:00:08.000Z",
            "kind": "tool_result",
            "call_id": "privacy-fixture",
            "output": secret,
            "record_id": "MR-" + "f" * 24,
        }
    )
    normalized = b"".join(mira_continuity.canonical_json_bytes(row) + b"\n" for row in rows)
    buffer = __import__("io").BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", filename="", mtime=0) as stream:
        stream.write(normalized)
    path.write_bytes(buffer.getvalue())

    first = mira_continuity.privacy_audit_scan(
        registry_path=registry_path,
        repo_root=repo,
        sample_size=1,
    )
    second = mira_continuity.privacy_audit_scan(
        registry_path=registry_path,
        repo_root=repo,
        sample_size=1,
    )

    serialized = mira_continuity.pretty_json(first)
    assert first == second
    assert first["automated_scan"]["counts"]["critical"] >= 1
    assert secret not in serialized
    assert "match_sha256" in serialized
    assert first["boundaries"]["raw_values_included"] is False


def test_environment_assignment_detector_ignores_nonliteral_values() -> None:
    assert mira_continuity._environment_assignment_is_nonliteral(
        "TOKEN=[REDACTED_SECRET]"
    )
    assert mira_continuity._environment_assignment_is_nonliteral(
        'TOKEN=settings["access_token"]'
    )
    assert not mira_continuity._environment_assignment_is_nonliteral(
        "TOKEN=literal-secret-value"
    )
    assert not mira_continuity._environment_assignment_is_nonliteral(
        'TOKEN=settings["access_token"]-literal-suffix'
    )


def test_privacy_sample_has_stable_unique_strata() -> None:
    descriptors = [
        {
            "session_ref": f"MS-{index:032x}",
            "source_kind": "vscode" if index % 2 else "subagent",
            "capture_ref": f"MC-{index:024x}",
            "path": f"mira/continuity/captures/{index:032x}/MC-{index:024x}.jsonl.gz",
            "observed_at": f"2026-08-{(index % 28) + 1:02d}T00:00:00.000Z",
            "size_bytes": index + 1,
        }
        for index in range(30)
    ]

    first = mira_continuity.deterministic_privacy_sample(
        descriptors,
        inventory_sha256="a" * 64,
        sample_size=20,
    )
    second = mira_continuity.deterministic_privacy_sample(
        descriptors,
        inventory_sha256="a" * 64,
        sample_size=20,
    )

    assert first == second
    assert len(first) == 20
    assert len({item["capture_ref"] for item in first}) == 20
    assert {item["selection_stratum"] for item in first} == {
        "largest",
        "newest_vscode",
        "newest_subagent",
        "seeded_remaining",
    }


def test_privacy_finalization_blocks_critical_findings_without_leaking(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    packet = {
        "audit_id": "MPA-" + "a" * 24,
        "corpus": {"captures": 1},
        "automated_scan": {"counts": {"critical": 1}, "finding_count": 1},
        "sample": [],
        "findings": [
            {
                "id": "PF-" + "b" * 24,
                "severity": "critical",
                "review_required": True,
            }
        ],
    }
    decisions = {
        "audit_ref": packet["audit_id"],
        "decisions": [
            {
                "finding_ref": packet["findings"][0]["id"],
                "disposition": "redact_and_recapture",
            }
        ],
    }

    receipt = mira_continuity.finalize_privacy_audit(
        packet,
        decisions,
        receipt_root=receipts,
        repo_root=repo,
    )

    assert receipt["status"] == "blocked"
    assert receipt["readiness"]["local_commit"] == "blocked"
    assert receipt["boundaries"]["raw_values_included"] is False
    assert (receipts / f"{receipt['receipt_id']}.json").is_file()


def test_privacy_finalization_accepts_authorized_medium_batch_for_local_commit(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    finding_id = "PF-" + "b" * 24
    packet = {
        "audit_id": "MPA-" + "a" * 24,
        "corpus": {"captures": 1},
        "automated_scan": {"counts": {"medium": 1}, "finding_count": 1},
        "sample": [],
        "findings": [
            {"id": finding_id, "severity": "medium", "review_required": True}
        ],
    }
    decisions = {
        "audit_ref": packet["audit_id"],
        "decisions": [],
        "medium_batch": {
            "disposition": "accept_local_private_git",
            "scope": "local_commit_only",
            "authority_refs": ["MS-" + "c" * 32],
            "note": "Automated keyword candidates accepted only for the bounded local commit.",
        },
    }

    receipt = mira_continuity.finalize_privacy_audit(
        packet,
        decisions,
        receipt_root=receipts,
        repo_root=repo,
    )

    assert receipt["status"] == "passed_for_local_commit"
    assert receipt["readiness"]["local_commit"] == "pass"
    assert receipt["decision_refs"] == [finding_id]
    assert receipt["readiness"]["private_remote"] == "blocked_unknown_visibility"


def test_staged_recovery_precheck_binds_exact_index(monkeypatch) -> None:
    paths = [f"mira/file-{index:03d}.txt" for index in range(133)]
    captures = [
        f"mira/continuity/captures/session-{index:03d}/MC-{index:024x}.jsonl.gz"
        for index in range(120)
    ]
    paths[:120] = captures
    paths = sorted(paths)
    contract = {
        "staged_path_count": 133,
        "staged_path_sha256": mira_continuity.hash_lines(paths),
        "capture_count": 120,
        "capture_path_sha256": "unused",
        "capture_inventory_sha256": "unused",
    }
    monkeypatch.setitem(mira_continuity.RECOVERY_CONTRACTS, "test", contract)

    def fake_git_lines(_repo: Path, *arguments: str) -> list[str]:
        if arguments[:3] == ("diff", "--cached", "--name-only"):
            return paths
        if arguments[:3] == ("diff", "--cached", "--diff-filter=D"):
            return []
        if arguments[:2] == ("ls-files", "--stage"):
            return [f"100644 {'a' * 40} 0\t{path}" for path in paths]
        raise AssertionError(arguments)

    monkeypatch.setattr(mira_continuity, "_git_lines", fake_git_lines)
    monkeypatch.setattr(mira_continuity, "_mixed_patch_failures", lambda _repo: ([], {}))

    result = mira_continuity.staged_recovery_precheck(contract_name="test")

    assert result["status"] == "valid"
    assert result["staged_capture_count"] == 120
    assert result["failures"] == []


def test_external_recovery_roots_must_remain_outside_repository(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    inside = repo / "tmp"
    inside.mkdir(parents=True)

    try:
        mira_continuity._require_external_root(inside, repo_root=repo)
    except mira_continuity.ContinuityError as error:
        assert "outside the repository" in str(error)
    else:
        raise AssertionError("inside-repository recovery root was accepted")

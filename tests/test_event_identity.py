from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import event_identity_kernel as kernel
import reality
from event_identity_policy import Bounds, DomainPolicy, HOST_POLICY


IDENTITY = {
    "domain": "military-activity",
    "event_type": "ballistic-missile-attack",
    "actor": "iran-irgc",
    "action": "missile-launch",
    "target": "mwaffaq-salti-air-base",
    "location": "jordan-azraq",
}


def instant(
    *,
    raw: str = "July 28 at 5:45 p.m. ET",
    value: str = "2026-07-28T17:45:00-04:00",
    precision: str = "minute",
    timezone_basis: str = "explicit-offset",
    source_ref: str = "centcom-statement",
    timezone_name: str | None = None,
    end: str | None = None,
) -> dict:
    result = {
        "raw": raw,
        "value": value,
        "precision": precision,
        "timezone_basis": timezone_basis,
        "source_ref": source_ref,
    }
    if timezone_name is not None:
        result["timezone"] = timezone_name
    if end is not None:
        result["end"] = end
    return result


def event(
    event_id: str,
    *,
    time: dict | None = None,
    anchors: list[dict] | None = None,
    **changes,
) -> dict:
    result = {
        "id": event_id,
        **IDENTITY,
        "time": time or instant(),
        "stable_anchors": anchors
        if anchors is not None
        else [
            {
                "kind": "official-event-time",
                "value": "2026-07-28T21:45:00Z",
                "source_ref": "centcom-statement",
            }
        ],
    }
    result.update(changes)
    return result


def packet(*comparands: dict) -> dict:
    return {
        "schema_version": 1,
        "request_ref": "VER-20260729-04",
        "candidate": event("candidate-jordan-20260729"),
        "comparands": list(comparands)
        or [
            event(
                "jordan-early-wednesday",
                time=instant(
                    raw="early Wednesday",
                    value="2026-07-29",
                    precision="day",
                    timezone_basis="reporting-location",
                    source_ref="jordanian-military",
                    timezone_name="Asia/Amman",
                ),
            )
        ],
    }


def test_us_eastern_and_jordan_local_dates_are_same_event_candidate() -> None:
    result = kernel.compare_packet(packet(), HOST_POLICY)
    assert result["disposition"] == "hold-same-event"
    assert result["diagnostics"][0]["diagnostic"] == "event-same-candidate"
    assert result["diagnostics"][0]["time_relation"] == "overlap"


def test_july_17_and_july_29_attacks_are_distinct() -> None:
    july_17 = event(
        "jordan-20260717",
        time=instant(
            raw="July 17",
            value="2026-07-17",
            precision="day",
            timezone_basis="reporting-location",
            source_ref="jordanian-military-july17",
            timezone_name="Asia/Amman",
        ),
        anchors=[],
    )
    result = kernel.compare_packet(packet(july_17), HOST_POLICY)
    assert result["disposition"] == "continue-distinct"
    assert result["diagnostics"][0]["diagnostic"] == "event-distinct"


def test_date_only_interval_respects_daylight_saving_transition() -> None:
    value = instant(
        raw="March 8 local day",
        value="2026-03-08",
        precision="day",
        timezone_basis="reporting-location",
        timezone_name="America/New_York",
    )
    start, end = kernel._normalize_time(value)
    assert (end - start).total_seconds() == 23 * 60 * 60


def test_offset_timestamp_needs_no_timezone_inference() -> None:
    result = kernel.compare_packet(packet(), HOST_POLICY)
    assert result["diagnostics"][0]["time_relation"] == "overlap"


def test_precise_local_time_without_timezone_is_ambiguous() -> None:
    unknown = event(
        "unknown-zone",
        time=instant(
            raw="5:45 p.m.",
            value="2026-07-28T17:45:00",
            timezone_basis="unknown",
            source_ref="undated-wire",
        ),
    )
    result = kernel.compare_packet(packet(unknown), HOST_POLICY)
    assert result["disposition"] == "clarify-ambiguous"
    assert result["diagnostics"][0]["diagnostic"] == "event-ambiguous-time"


def test_overlap_without_shared_anchor_is_ambiguous() -> None:
    no_anchor = event("no-anchor", anchors=[])
    result = kernel.compare_packet(packet(no_anchor), HOST_POLICY)
    assert result["diagnostics"][0]["diagnostic"] == "event-ambiguous-anchor"


def test_near_nonoverlapping_time_is_ambiguous() -> None:
    near = event(
        "near-time",
        time=instant(value="2026-07-28T19:00:00-04:00"),
        anchors=[],
    )
    result = kernel.compare_packet(packet(near), HOST_POLICY)
    assert result["diagnostics"][0]["diagnostic"] == "event-ambiguous-time"
    assert result["diagnostics"][0]["time_relation"] == "near"


def test_identity_mismatch_during_overlapping_time_is_ambiguous() -> None:
    another_target = event("other-target", target="another-air-base")
    result = kernel.compare_packet(packet(another_target), HOST_POLICY)
    assert result["diagnostics"][0]["diagnostic"] == "event-ambiguous-identity"
    assert "target" not in result["diagnostics"][0]["matched_fields"]


def test_input_order_is_deterministic_and_output_never_leaks_values() -> None:
    first = event("z-record", anchors=[])
    second = event(
        "a-record",
        time=instant(
            raw="sensitive raw wording",
            value="2026-07-17",
            precision="day",
            timezone_basis="reporting-location",
            source_ref="source-two",
            timezone_name="Asia/Amman",
        ),
        anchors=[
            {
                "kind": "media-hash",
                "value": "sensitive-anchor-value",
                "source_ref": "source-two",
            }
        ],
    )
    left = kernel.compare_packet(packet(first, second), HOST_POLICY)
    right = kernel.compare_packet(packet(second, first), HOST_POLICY)
    assert kernel.render_json(left) == kernel.render_json(right)
    rendered = kernel.render_json(left) + kernel.render_markdown(left)
    assert "sensitive raw wording" not in rendered
    assert "sensitive-anchor-value" not in rendered
    assert [item["comparand_id"] for item in left["diagnostics"]] == [
        "a-record",
        "z-record",
    ]


@pytest.mark.parametrize(
    ("sensitive", "rule"),
    (
        ("person@example.com", "privacy.email"),
        ("api_key=super-secret", "privacy.credential_assignment"),
        ("-----BEGIN OPENSSH PRIVATE KEY-----", "privacy.private_key"),
    ),
)
def test_privacy_rules_fail_closed_without_echo(sensitive: str, rule: str) -> None:
    unsafe = packet()
    unsafe["candidate"]["time"]["source_ref"] = sensitive
    with pytest.raises(kernel.EventIdentityError) as caught:
        kernel.compare_packet(unsafe, HOST_POLICY)
    assert caught.value.codes == (rule,)
    assert sensitive not in str(caught.value)


def test_strict_validation_rejects_unknown_fields_duplicate_ids_and_bad_intervals() -> None:
    unknown = packet()
    unknown["candidate"]["unexpected"] = True
    with pytest.raises(kernel.EventIdentityError, match="packet.unknown-or-missing-field"):
        kernel.compare_packet(unknown, HOST_POLICY)

    duplicate = packet()
    duplicate["comparands"][0]["id"] = duplicate["candidate"]["id"]
    with pytest.raises(kernel.EventIdentityError, match="packet.duplicate-id"):
        kernel.compare_packet(duplicate, HOST_POLICY)

    invalid_interval = packet()
    invalid_interval["candidate"]["time"] = instant(
        value="2026-07-29T02:00:00Z",
        precision="interval",
        end="2026-07-29T01:00:00Z",
    )
    with pytest.raises(kernel.EventIdentityError, match="packet.invalid-event-interval"):
        kernel.compare_packet(invalid_interval, HOST_POLICY)


def test_yaml_loader_rejects_duplicates_tags_and_multiple_documents(tmp_path: Path) -> None:
    cases = {
        "duplicate.yaml": ("a: 1\na: 2\n", "packet.duplicate-yaml-key"),
        "tag.yaml": ("value: !!python/object:builtins.object {}\n", "packet.invalid-yaml"),
        "multi.yaml": ("---\na: 1\n---\na: 2\n", "packet.multiple-yaml-documents"),
    }
    for name, (body, code) in cases.items():
        path = tmp_path / name
        path.write_text(body, encoding="utf-8")
        with pytest.raises(kernel.EventIdentityError) as caught:
            reality.load_event_identity_packet(path)
        assert caught.value.codes == (code,)


def test_packet_size_is_checked_before_yaml_loading(tmp_path: Path) -> None:
    path = tmp_path / "oversized.yaml"
    path.write_bytes(b"x" * (HOST_POLICY.bounds.max_packet_bytes + 1))
    with pytest.raises(kernel.EventIdentityError) as caught:
        reality.load_event_identity_packet(path)
    assert caught.value.codes == ("packet.too-large",)


def test_kernel_is_portable_and_has_no_mutating_imports() -> None:
    source = (SCRIPTS_ROOT / "event_identity_kernel.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imports.isdisjoint(
        {
            "event_identity_policy",
            "reality",
            "pathlib",
            "os",
            "sqlite3",
            "subprocess",
            "choice_ledger",
            "git",
        }
    )


def test_host_vocabulary_changes_without_kernel_changes() -> None:
    alternate = SimpleNamespace(
        domains={"alternate-domain": DomainPolicy(near_tolerance_seconds=30)},
        bounds=Bounds(),
        privacy_rule_ids=lambda value: (),
    )
    candidate = event("candidate", domain="alternate-domain", event_type="signal")
    comparand = event("comparand", domain="alternate-domain", event_type="signal")
    alternate_packet = {
        "schema_version": 1,
        "request_ref": "alternate-request",
        "candidate": candidate,
        "comparands": [comparand],
    }
    assert kernel.compare_packet(alternate_packet, alternate)["disposition"] == (
        "hold-same-event"
    )


def test_cli_exit_codes_rendering_equivalence_and_read_only_behavior(
    tmp_path: Path,
) -> None:
    reality_cli = SCRIPTS_ROOT / "reality.py"
    same_path = tmp_path / "same.yaml"
    same_path.write_text(json.dumps(packet()), encoding="utf-8")
    distinct_path = tmp_path / "distinct.yaml"
    distinct_path.write_text(
        json.dumps(
            packet(
                event(
                    "old-event",
                    time=instant(
                        raw="July 17",
                        value="2026-07-17",
                        precision="day",
                        timezone_basis="reporting-location",
                        source_ref="old-source",
                        timezone_name="Asia/Amman",
                    ),
                    anchors=[],
                )
            )
        ),
        encoding="utf-8",
    )
    invalid_path = tmp_path / "invalid.yaml"
    invalid_path.write_text("unknown: value\n", encoding="utf-8")
    database = tmp_path / "choice.sqlite3"
    environment = os.environ.copy()
    environment["NARRATIVE_CHOICE_DB"] = str(database)
    before = {path.name for path in tmp_path.iterdir()}
    results = [
        subprocess.run(
            [
                sys.executable,
                str(reality_cli),
                "identity-check",
                "--packet",
                str(path),
                "--format",
                "json",
            ],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )
        for path in (same_path, distinct_path, invalid_path)
    ]
    assert [item.returncode for item in results] == [1, 0, 1]
    assert json.loads(results[0].stdout)["disposition"] == "hold-same-event"
    assert json.loads(results[1].stdout)["disposition"] == "continue-distinct"
    assert json.loads(results[2].stdout)["status"] == "invalid"

    markdown = subprocess.run(
        [
            sys.executable,
            str(reality_cli),
            "identity-check",
            "--packet",
            str(same_path),
            "--format",
            "markdown",
        ],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert markdown.returncode == 1
    assert "event-same-candidate" in markdown.stdout
    assert "hold-same-event" in markdown.stdout
    assert "Authority effect: `none`" in markdown.stdout
    assert not database.exists()
    assert before == {path.name for path in tmp_path.iterdir()}


def test_malformed_cli_invocation_reserves_argparse_exit_two() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_ROOT / "reality.py"), "identity-check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2

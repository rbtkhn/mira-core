from __future__ import annotations

import ast
import hashlib
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

import contradiction_check
import contradiction_kernel as kernel
from contradiction_policy import Bounds, DomainPolicy, HOST_POLICY


def packet(
    *,
    assertion_value=False,
    fact_value=False,
    field: str = "git_authorized",
    consequence: str = "high",
    provisional: bool = False,
    facts: list[dict] | None = None,
) -> dict:
    assertion = {
        "id": "REQ-001",
        "normalized_field": field,
        "value": assertion_value,
        "scope": "repository",
        "source_ref": "operator-request",
        "provisional": provisional,
    }
    default_fact = {
        "id": "CTRL-001",
        "normalized_field": field,
        "value": fact_value,
        "scope": "repository",
        "authority_role": "canonical-operating-contract",
        "source_ref": "AGENTS.md",
        "as_of": "2026-07-30T10:00:00Z",
    }
    return {
        "schema_version": 1,
        "request_ref": "request-001",
        "authority_domain": "repository-contract",
        "scope": "repository",
        "consequence_level": consequence,
        "as_of": "2026-07-30T12:00:00Z",
        "request_assertions": [assertion],
        "controlling_facts": [default_fact] if facts is None else facts,
    }


def diagnostic(result: dict) -> str:
    return result["diagnostics"][0]["code"]


def test_aligned_requests_continue() -> None:
    result = kernel.compare_packet(packet(), HOST_POLICY)
    assert result["disposition"] == "continue"
    assert diagnostic(result) == "aligned"


@pytest.mark.parametrize(
    ("consequence", "expected"),
    (("low", "clarify"), ("medium", "clarify"), ("high", "hold")),
)
def test_direct_conflict_routes_by_packet_consequence(
    consequence: str, expected: str
) -> None:
    result = kernel.compare_packet(
        packet(assertion_value=True, consequence=consequence), HOST_POLICY
    )
    assert result["disposition"] == expected
    assert diagnostic(result) == "request-control-conflict"


def test_controlling_source_conflict_holds() -> None:
    facts = [
        packet()["controlling_facts"][0],
        packet()["controlling_facts"][0]
        | {"id": "CTRL-002", "value": True, "source_ref": "specific-contract.md"},
    ]
    result = kernel.compare_packet(packet(facts=facts), HOST_POLICY)
    assert result["disposition"] == "hold"
    assert diagnostic(result) == "controlling-source-conflict"
    assert result["diagnostics"][0]["control_ids"] == ["CTRL-001", "CTRL-002"]


@pytest.mark.parametrize(
    ("facts", "expected"),
    (
        (
            [
                packet()["controlling_facts"][0]
                | {"freshness_deadline": "2026-07-30T11:00:00Z"}
            ],
            "control-stale",
        ),
        ([], "control-missing"),
        (
            [packet()["controlling_facts"][0] | {"scope": "another-repository"}],
            "control-scope-mismatch",
        ),
        (
            [
                packet()["controlling_facts"][0]
                | {"authority_role": "advisory-guidance"}
            ],
            "control-non-authoritative",
        ),
    ),
)
def test_unresolved_diagnostics_remain_distinct(
    facts: list[dict], expected: str
) -> None:
    assert diagnostic(kernel.compare_packet(packet(facts=facts), HOST_POLICY)) == expected


def test_stale_and_advisory_facts_never_control() -> None:
    stale = packet()["controlling_facts"][0] | {
        "freshness_deadline": "2026-07-30T11:00:00Z"
    }
    advisory = packet()["controlling_facts"][0] | {
        "id": "CTRL-002",
        "authority_role": "advisory-guidance",
    }
    result = kernel.compare_packet(packet(facts=[stale, advisory]), HOST_POLICY)
    assert diagnostic(result) == "control-stale"
    assert result["disposition"] == "hold"


@pytest.mark.parametrize(
    "facts",
    (
        [],
        [
            packet()["controlling_facts"][0]
            | {"freshness_deadline": "2026-07-30T11:00:00Z"}
        ],
        [
            packet()["controlling_facts"][0]
            | {"authority_role": "advisory-guidance"}
        ],
        [packet()["controlling_facts"][0] | {"scope": "another-repository"}],
    ),
)
def test_every_non_aligned_high_consequence_packet_holds(
    facts: list[dict],
) -> None:
    result = kernel.compare_packet(packet(facts=facts), HOST_POLICY)
    assert result["disposition"] == "hold"


@pytest.mark.parametrize("consequence", ("low", "medium"))
def test_non_provisional_missing_control_clarifies(consequence: str) -> None:
    result = kernel.compare_packet(
        packet(consequence=consequence, facts=[]), HOST_POLICY
    )
    assert result["disposition"] == "clarify"


def test_provisional_continuation_is_narrowly_bounded() -> None:
    ordinary = packet(
        field="display_theme",
        consequence="low",
        provisional=True,
        facts=[],
    )
    assert kernel.compare_packet(ordinary, HOST_POLICY)["disposition"] == (
        "continue-provisional"
    )
    assert kernel.compare_packet(
        ordinary | {"consequence_level": "medium"}, HOST_POLICY
    )["disposition"] == "clarify"
    ordinary["request_assertions"][0]["provisional"] = False
    assert kernel.compare_packet(ordinary, HOST_POLICY)["disposition"] == "clarify"


def test_output_is_deterministic_and_never_echoes_compared_values() -> None:
    first = packet(assertion_value="request-secret", fact_value="control-secret")
    first["request_assertions"].append(
        {
            "id": "REQ-000",
            "normalized_field": "display_theme",
            "value": "night",
            "scope": "repository",
            "source_ref": "operator-request",
            "provisional": True,
        }
    )
    second = first | {
        "request_assertions": list(reversed(first["request_assertions"])),
        "controlling_facts": list(reversed(first["controlling_facts"])),
    }
    left = kernel.compare_packet(first, HOST_POLICY)
    right = kernel.compare_packet(second, HOST_POLICY)
    assert kernel.render_json(left) == kernel.render_json(right)
    rendered = kernel.render_json(left) + kernel.render_markdown(left)
    assert "request-secret" not in rendered
    assert "control-secret" not in rendered
    assert [item["assertion_id"] for item in left["diagnostics"]] == [
        "REQ-000",
        "REQ-001",
    ]


@pytest.mark.parametrize(
    ("sensitive", "rule"),
    (
        ("person@example.com", "privacy.email"),
        ("api_key=super-secret", "privacy.credential_assignment"),
        (
            "-----BEGIN OPENSSH PRIVATE KEY-----",
            "privacy.private_key",
        ),
    ),
)
def test_privacy_validation_fails_closed_without_echo(
    sensitive: str, rule: str
) -> None:
    unsafe = packet()
    unsafe["request_assertions"][0]["source_ref"] = sensitive
    with pytest.raises(kernel.PreflightError) as caught:
        kernel.compare_packet(unsafe, HOST_POLICY)
    assert caught.value.codes == (rule,)
    assert sensitive not in str(caught.value)


def test_cli_is_read_only_and_writes_no_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    packet_path = tmp_path / "packet.yaml"
    packet_path.write_text(json.dumps(packet()), encoding="utf-8")
    database = tmp_path / "choice.sqlite3"
    monkeypatch.setenv("NARRATIVE_CHOICE_DB", str(database))
    before = {path.name for path in tmp_path.iterdir()}
    assert contradiction_check.main(
        ["--packet", str(packet_path), "--format", "json"]
    ) == 0
    after = {path.name for path in tmp_path.iterdir()}
    assert before == after
    assert not database.exists()
    assert json.loads(capsys.readouterr().out)["disposition"] == "continue"


def test_authority_boundary_is_present_in_every_result() -> None:
    result = kernel.compare_packet(packet(), HOST_POLICY)
    assert result["authority_effect"] == "none"
    assert result["capability_token"] is False
    assert "grants no authority" in result["notice"]
    invalid = contradiction_check.invalid_result(kernel.PreflightError("packet.bad"))
    assert invalid["authority_effect"] == "none"
    assert invalid["capability_token"] is False


def test_kernel_has_no_destination_specific_or_filesystem_imports() -> None:
    source = (SCRIPTS_ROOT / "contradiction_kernel.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imports.isdisjoint(
        {
            "contradiction_policy",
            "elicitation",
            "choice_ledger",
            "pathlib",
            "os",
            "sqlite3",
            "subprocess",
        }
    )


def test_host_vocabulary_changes_without_kernel_changes() -> None:
    alternative_policy = SimpleNamespace(
        consequence_levels=frozenset({"minor"}),
        domains={
            "alternate": DomainPolicy(
                allowed_roles=frozenset({"owner", "observer"}),
                controlling_roles=frozenset({"owner"}),
            )
        },
        bounds=Bounds(),
        privacy_rule_ids=lambda value: (),
    )
    alternative = packet()
    alternative.update(
        authority_domain="alternate",
        consequence_level="minor",
    )
    alternative["request_assertions"][0].update(
        normalized_field="locked", value="yes"
    )
    alternative["controlling_facts"][0].update(
        normalized_field="locked", value="yes", authority_role="owner"
    )
    assert kernel.compare_packet(alternative, alternative_policy)["disposition"] == (
        "continue"
    )


def test_provenance_manifest_verifies_kernel_hash() -> None:
    manifest = json.loads(
        (SCRIPTS_ROOT / "contradiction_kernel.provenance.json").read_text(
            encoding="utf-8"
        )
    )
    digest = hashlib.sha256(
        (REPO_ROOT / manifest["canonical_source"]).read_bytes()
    ).hexdigest()
    assert digest == manifest["kernel_sha256"]
    assert manifest["kernel_id"] == "narrative-systems-contradiction-preflight"
    assert manifest["ownership"] == "repository-native"
    assert manifest["authority_effect"] == "none"


@pytest.mark.parametrize(
    ("mutation", "code"),
    (
        (lambda value: value | {"unknown": "field"}, "packet.unknown-or-missing-field"),
        (
            lambda value: value
            | {"as_of": "2026-07-30T12:00:00"},
            "packet.invalid-as-of",
        ),
        (
            lambda value: value
            | {
                "controlling_facts": [
                    value["controlling_facts"][0]
                    | {"as_of": "2026-07-31T12:00:00Z"}
                ]
            },
            "packet.future-controlling-fact",
        ),
    ),
)
def test_strict_packet_validation(mutation, code: str) -> None:
    with pytest.raises(kernel.PreflightError) as caught:
        kernel.compare_packet(mutation(packet()), HOST_POLICY)
    assert code in caught.value.codes


def test_rejects_duplicate_ids_mixed_types_and_non_finite_numbers() -> None:
    duplicate = packet()
    duplicate["controlling_facts"][0]["id"] = "REQ-001"
    with pytest.raises(kernel.PreflightError, match="packet.duplicate-id"):
        kernel.compare_packet(duplicate, HOST_POLICY)

    mixed = packet()
    mixed["controlling_facts"][0]["value"] = 0
    with pytest.raises(kernel.PreflightError, match="packet.mixed-scalar-types"):
        kernel.compare_packet(mixed, HOST_POLICY)

    non_finite = packet(assertion_value=float("inf"), fact_value=float("inf"))
    with pytest.raises(kernel.PreflightError, match="packet.non-finite-number"):
        kernel.compare_packet(non_finite, HOST_POLICY)


def test_yaml_loader_rejects_duplicates_tags_and_multiple_documents(
    tmp_path: Path,
) -> None:
    cases = {
        "duplicate.yaml": ("a: 1\na: 2\n", "packet.duplicate-yaml-key"),
        "tag.yaml": ("value: !!python/object:builtins.object {}\n", "packet.invalid-yaml"),
        "multi.yaml": ("---\na: 1\n---\na: 2\n", "packet.multiple-yaml-documents"),
    }
    for name, (body, code) in cases.items():
        path = tmp_path / name
        path.write_text(body, encoding="utf-8")
        with pytest.raises(kernel.PreflightError) as caught:
            contradiction_check.load_packet(path)
        assert caught.value.codes == (code,)


@pytest.mark.parametrize(
    "body",
    (
        "value: &shared repository\ncopy: *shared\n",
        "value: &cycle\n  - *cycle\n",
    ),
)
def test_yaml_loader_rejects_aliases_before_anchor_resolution(
    tmp_path: Path, body: str
) -> None:
    path = tmp_path / "alias.yaml"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(kernel.PreflightError) as caught:
        contradiction_check.load_packet(path)
    assert caught.value.codes == ("packet.yaml-alias",)


def test_yaml_loader_enforces_depth_and_node_budgets(tmp_path: Path) -> None:
    deep = tmp_path / "deep.yaml"
    deep.write_text(
        "value: " + "[" * 40 + "0" + "]" * 40 + "\n",
        encoding="utf-8",
    )
    with pytest.raises(kernel.PreflightError) as caught:
        contradiction_check.load_packet(deep)
    assert caught.value.codes == ("packet.yaml-too-deep",)

    wide = tmp_path / "wide.yaml"
    wide.write_text(
        "values:\n" + "  - 0\n" * HOST_POLICY.bounds.max_yaml_nodes,
        encoding="utf-8",
    )
    with pytest.raises(kernel.PreflightError) as caught:
        contradiction_check.load_packet(wide)
    assert caught.value.codes == ("packet.yaml-too-many-nodes",)


def test_direct_cyclic_input_fails_shape_validation_before_privacy_scan() -> None:
    cyclic: list = []
    cyclic.append(cyclic)
    unsafe = packet()
    unsafe["scope"] = cyclic
    with pytest.raises(kernel.PreflightError) as caught:
        kernel.compare_packet(unsafe, HOST_POLICY)
    assert caught.value.codes == ("packet.invalid-scope",)


@pytest.mark.parametrize(
    "unsafe_character",
    ("\n", "\x1b", "\u202e", "\u2028", "`"),
)
def test_rendered_metadata_rejects_controls_and_markdown_breakout(
    unsafe_character: str,
) -> None:
    unsafe = packet()
    unsafe["request_ref"] = f"request{unsafe_character}spoof"
    with pytest.raises(kernel.PreflightError) as caught:
        kernel.compare_packet(unsafe, HOST_POLICY)
    assert caught.value.codes == ("packet.unsafe-metadata",)


def test_rendered_metadata_accepts_valid_unicode_and_repository_paths() -> None:
    valid = packet()
    valid["request_ref"] = "revision-№1"
    valid["request_assertions"][0]["source_ref"] = (
        "docs/skill-drafts/archive-intake/SKILL.md"
    )
    assert kernel.compare_packet(valid, HOST_POLICY)["disposition"] == "continue"


def test_cli_exit_codes_and_safe_json(tmp_path: Path) -> None:
    cli = SCRIPTS_ROOT / "contradiction_check.py"
    aligned = tmp_path / "aligned.yaml"
    aligned.write_text(json.dumps(packet()), encoding="utf-8")
    conflict = tmp_path / "conflict.yaml"
    conflict.write_text(
        json.dumps(packet(assertion_value=True, consequence="medium")),
        encoding="utf-8",
    )
    high_conflict = tmp_path / "high-conflict.yaml"
    high_conflict.write_text(
        json.dumps(packet(assertion_value=True, consequence="high")),
        encoding="utf-8",
    )
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("unknown: value\n", encoding="utf-8")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SCRIPTS_ROOT)
    results = [
        subprocess.run(
            [sys.executable, str(cli), "--packet", str(path), "--format", "json"],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )
        for path in (aligned, conflict, high_conflict, invalid)
    ]
    assert [item.returncode for item in results] == [0, 1, 1, 1]
    assert json.loads(results[1].stdout)["disposition"] == "clarify"
    assert json.loads(results[2].stdout)["disposition"] == "hold"
    assert json.loads(results[3].stdout)["status"] == "invalid"
    usage = subprocess.run(
        [sys.executable, str(cli)],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert usage.returncode == 2


def test_packet_size_bound_is_enforced_before_yaml_loading(tmp_path: Path) -> None:
    path = tmp_path / "oversized.yaml"
    path.write_bytes(b"x" * (HOST_POLICY.bounds.max_packet_bytes + 1))
    with pytest.raises(kernel.PreflightError) as caught:
        contradiction_check.load_packet(path)
    assert caught.value.codes == ("packet.too-large",)

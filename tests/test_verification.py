from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

import verification


def template() -> str:
    return (REPO_ROOT / "narrative-geopolitics" / "work" / "verification" / "_packet-template.md").read_text(encoding="utf-8")


def write_packet(
    root: Path,
    packet_id: str = "VER-20260710-01",
    *,
    status: str = "assessed",
    outcome: str = "operationally_supported",
    evidence_rows: str | None = None,
    chains: int = 1,
) -> Path:
    packet_dir = root / f"{packet_id}-test"
    packet_dir.mkdir(parents=True)
    evidence_rows = evidence_rows or (
        "| `EVID-01` | `VSRC-RPT-AP` | https://example.com/a | `2026-07-11T12:00:00Z` | `2026-07-10` | "
        "`independent_professional_reporting` | `CHAIN-01` | `supports` | `not_required` | One report; no tracking data. |"
    )
    text = template()
    text = text.replace("VER-YYYYMMDD-NN", packet_id).replace("YYYY-MM-DD", "2026-07-10").replace("[Bounded claim label]", "Test claim")
    text = text.replace("Status: `requested`", f"Status: `{status}`")
    text = text.replace("Assessment outcome: `not_investigated`", f"Assessment outcome: `{outcome}`")
    text = text.replace("Claim: `[Exact operational claim under review.]`", "Claim: `A bounded event occurred.`")
    text = text.replace("Why it matters: `[Judgment, publication, promotion, or forecast consequence.]`", "Why it matters: `It affects a forecast.`")
    text = text.replace("Affected forecast hooks: `none`", "Affected forecast hooks: `NG-20260708-F02`")
    text = text.replace("Evidence chains examined: `0`", f"Evidence chains examined: `{chains}`")
    text = text.replace("- [ ] `[Observable required to support or challenge the claim.]`", "- [x] Vessel identity")
    divider = "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    text = text.replace(divider, divider + evidence_rows + "\n", 1)
    text = text.replace("[State what was sought and why unavailable.]", "The category was sought but no discriminating public evidence was available.")
    text = text.replace("[Explain applicability.]", "The claim does not concern movement, damage, deployment, or price.")
    text = text.replace("`[Explain which records share an originating evidence chain and which, if any, are independent.]`", "One originating chain is represented.")
    text = text.replace("Conclusion: `[What the evidence establishes and does not establish.]`", "Conclusion: Evidence supports the bounded claim but not broader control.")
    text = text.replace("Confidence boundary: `[Why the selected outcome is no stronger than the evidence permits.]`", "Confidence boundary: One chain limits independence.")
    text = text.replace("Downstream effect: `[Effect on judgment, publication, promotion, or forecast resolution; use none when unchanged.]`", "Downstream effect: Forecast remains open pending review.")
    path = packet_dir / "README.md"
    path.write_text(text, encoding="utf-8")
    return path


def ledger(path: Path) -> Path:
    path.write_text("| `NG-20260708-F02` | entry |\n", encoding="utf-8")
    return path


def write_registry(
    path: Path,
    *,
    evidence_class: str = "expert_commentary",
    status: str = "candidate",
) -> Path:
    path.write_text(
        "# Test Registry\n\n"
        "| ID | Source | URL | Domain | Observables | Evidence class | Perspective | Geography | Languages | Translation | Access | Fallback | Latency | Chain | Failures | Uses | Inappropriate | Reviewed | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| `VSRC-RPT-COMMENTARY` | Commentary | https://example.com/commentary | `professional_reporting` | interpretation and cited reporting | `{evidence_class}` | `western_independent` | external | `ru` | `not_required` | `open_limited` | `self` | days | One cited report is one chain. | Secondary-source dependence. | Context and source tracing. | Direct operational proof. | `2026-07-29` | `{status}` |\n",
        encoding="utf-8",
    )
    return path


def test_sequential_packet_ids_do_not_collide(tmp_path: Path) -> None:
    packets = tmp_path / "packets"
    template_path = tmp_path / "template.md"
    template_path.write_text(template(), encoding="utf-8")
    first = verification.create_packet("2026-07-10", "First claim", packets, template_path)
    second = verification.create_packet("2026-07-10", "Second claim", packets, template_path)
    assert first.parent.name.startswith("VER-20260710-01-")
    assert second.parent.name.startswith("VER-20260710-02-")


def test_complete_packet_passes_and_shared_urls_remain_one_chain(tmp_path: Path) -> None:
    rows = (
        "| `EVID-01` | `VSRC-RPT-AP` | https://example.com/a | `2026-07-11T12:00:00Z` | `2026-07-10` | `independent_professional_reporting` | `CHAIN-01` | `supports` | `not_required` | Original report. |\n"
        "| `EVID-02` | `VSRC-RPT-AP` | https://example.org/b | `2026-07-11T12:05:00Z` | `2026-07-10` | `independent_professional_reporting` | `CHAIN-01` | `context_only` | `not_required` | Repeats the first report. |"
    )
    packet = verification.parse_packet(write_packet(tmp_path / "packets", outcome="operationally_contested", evidence_rows=rows, chains=1))
    assert verification.validate_packet(packet, tmp_path, ledger(tmp_path / "ledger.md")) == []


def test_invalid_state_duplicate_evidence_and_chain_count_are_rejected(tmp_path: Path) -> None:
    rows = (
        "| `EVID-01` | `VSRC-RPT-AP` | https://example.com/a | `2026-07-11` | `2026-07-10` | `independent_professional_reporting` | `CHAIN-01` | `supports` | `not_required` | First. |\n"
        "| `EVID-01` | `VSRC-RPT-AP` | https://example.org/b | `2026-07-11` | `2026-07-10` | `bad_type` | `CHAIN-02` | `bad_direction` | `not_required` | Second. |"
    )
    packet = verification.parse_packet(write_packet(tmp_path / "packets", status="wrong", evidence_rows=rows, chains=1))
    failures = verification.validate_packet(packet, tmp_path, ledger(tmp_path / "ledger.md"))
    assert any("invalid workflow state" in item for item in failures)
    assert any("duplicate evidence IDs" in item for item in failures)
    assert any("invalid source type" in item for item in failures)
    assert any("invalid direction" in item for item in failures)
    assert any("evidence chain count 1 does not match 2" in item for item in failures)


def test_supported_assessment_requires_supporting_evidence(tmp_path: Path) -> None:
    row = "| `EVID-01` | `VSRC-RPT-AP` | https://example.com/a | `2026-07-11` | `2026-07-10` | `independent_professional_reporting` | `CHAIN-01` | `challenges` | `not_required` | Contrary evidence. |"
    packet = verification.parse_packet(write_packet(tmp_path / "packets", evidence_rows=row))
    failures = verification.validate_packet(packet, tmp_path, ledger(tmp_path / "ledger.md"))
    assert any("operationally_supported requires supporting evidence" in item for item in failures)


def test_list_json_is_read_only_and_stable(tmp_path: Path, monkeypatch) -> None:
    packets = tmp_path / "packets"
    path = write_packet(packets)
    before = path.read_bytes()
    payload = verification.list_payload(packets)
    assert json.loads(json.dumps(payload)) == payload
    assert payload[0]["verification_id"] == "VER-20260710-01"
    assert path.read_bytes() == before


def test_close_requires_assessed_packet_and_preserves_human_outcome(tmp_path: Path, monkeypatch) -> None:
    packets = tmp_path / "packets"
    path = write_packet(packets, outcome="operationally_contested")
    monkeypatch.setattr(verification, "LEDGER_PATH", ledger(tmp_path / "ledger.md"))
    assert verification.close_packet("VER-20260710-01", packets) == []
    closed = verification.parse_packet(path)
    assert closed.fields["status"] == "closed"
    assert closed.fields["assessment_outcome"] == "operationally_contested"


def test_registry_has_36_valid_sources_and_stable_read_only_payload() -> None:
    before = verification.REGISTRY_PATH.read_bytes()
    assert verification.validate_registry() == []
    payload = verification.source_payload(domain="maritime_incident")
    assert payload and all(item["domain"] == "maritime_incident" for item in payload)
    assert json.loads(json.dumps(payload)) == payload
    assert verification.REGISTRY_PATH.read_bytes() == before


def test_unknown_registry_source_is_rejected(tmp_path: Path) -> None:
    row = "| `EVID-01` | `VSRC-NOT-REAL` | https://example.com/a | `2026-07-11` | `2026-07-10` | `independent_professional_reporting` | `CHAIN-01` | `supports` | `not_required` | Unknown source. |"
    packet = verification.parse_packet(write_packet(tmp_path / "packets", outcome="operationally_contested", evidence_rows=row))
    assert any("unknown registry source" in item for item in verification.validate_packet(packet, tmp_path, ledger(tmp_path / "ledger.md")))


def test_interested_sources_alone_cannot_operationally_support(tmp_path: Path) -> None:
    rows = (
        "| `EVID-01` | `VSRC-OFF-CENTCOM` | https://example.com/a | `2026-07-11` | `2026-07-10` | `official_interested_primary` | `CHAIN-01` | `supports` | `not_required` | Claimant statement. |\n"
        "| `EVID-02` | `VSRC-RPT-TASS` | https://example.org/b | `2026-07-11` | `2026-07-10` | `state_affiliated_reporting` | `CHAIN-02` | `supports` | `official_english_available` | State report. |"
    )
    packet = verification.parse_packet(write_packet(tmp_path / "packets", evidence_rows=rows, chains=2))
    failures = verification.validate_packet(packet, tmp_path, ledger(tmp_path / "ledger.md"))
    assert any("cannot independently establish" in item for item in failures)


def test_expert_commentary_candidate_is_valid_registry_context(tmp_path: Path) -> None:
    registry_path = write_registry(tmp_path / "registry.md")
    assert verification.validate_registry(registry_path) == []
    row = "| `EVID-01` | `VSRC-RPT-COMMENTARY` | https://example.com/commentary | `2026-07-29` | `2026-07-29` | `expert_commentary` | `CHAIN-01` | `context_only` | `not_required` | Contextual lead only. |"
    packet = verification.parse_packet(
        write_packet(
            tmp_path / "packets",
            outcome="operationally_contested",
            evidence_rows=row,
            chains=1,
        )
    )
    assert verification.validate_packet(
        packet,
        tmp_path,
        ledger(tmp_path / "ledger.md"),
        registry_path,
    ) == []


def test_expert_commentary_cannot_establish_operational_support(tmp_path: Path) -> None:
    registry_path = write_registry(tmp_path / "registry.md")
    row = "| `EVID-01` | `VSRC-RPT-COMMENTARY` | https://example.com/commentary | `2026-07-29` | `2026-07-29` | `expert_commentary` | `CHAIN-01` | `supports` | `not_required` | Contextual lead only. |"
    packet = verification.parse_packet(
        write_packet(tmp_path / "packets", evidence_rows=row, chains=1)
    )
    failures = verification.validate_packet(
        packet,
        tmp_path,
        ledger(tmp_path / "ledger.md"),
        registry_path,
    )
    assert any("may supply context only" in item for item in failures)
    assert any("cannot independently establish operational support" in item for item in failures)


def write_day(tmp_path: Path, synthesis_rows: str, forecast_rows: str = "") -> Path:
    daily = tmp_path / "daily"
    run = daily / "2026-07-10"
    run.mkdir(parents=True)
    (run / "synthesis.md").write_text(
        "# Synthesis\n\n## Operational Claim Triage\n\n"
        "| Claim ID | Operational claim | Current status | Consequence if false | Public use | Verification |\n"
        "| --- | --- | --- | --- | --- | --- |\n" + synthesis_rows + "\n",
        encoding="utf-8",
    )
    (run / "forecast.md").write_text(forecast_rows, encoding="utf-8")
    return daily


def test_day_payload_reports_request_and_forecast_dependency(tmp_path: Path) -> None:
    daily = write_day(
        tmp_path,
        "| `OPC-20260710-01` | A vessel was attacked. | `source_assertion` | `high` | `no` | `request` |",
        "| `NG-20260710-F01` | Claim | Mechanism | `OPC-20260710-01` |\n",
    )
    payload = verification.day_payload("2026-07-10", daily, tmp_path / "packets")
    assert payload["claims"][0]["packet_state"] == "requested_not_created"
    assert payload["claims"][0]["forecast_hooks"] == ["NG-20260710-F01"]
    assert payload["unknown_dependencies"] == []


def test_internal_unresolved_claim_passes_but_public_use_blocks_publication(tmp_path: Path) -> None:
    daily = write_day(
        tmp_path,
        "| `OPC-20260710-01` | A vessel was attacked. | `contested` | `high` | `yes` | `request` |",
    )
    assert verification.validate_day_claims("2026-07-10", "synthesis", daily, tmp_path / "packets") == []
    failures = verification.validate_day_claims("2026-07-10", "publication", daily, tmp_path / "packets")
    assert failures == ["OPC-20260710-01: high-consequence public use requires an assessed packet"]


def test_claim_contract_rejects_malformed_values_and_unknown_dependency(tmp_path: Path) -> None:
    daily = write_day(
        tmp_path,
        "| `OPC-20260709-01` | A vessel was attacked. | `certain` | `critical` | `maybe` | `automatic` |",
        "| `NG-20260710-F01` | Claim | Mechanism | `OPC-20260710-99` |\n",
    )
    failures = verification.validate_day_claims("2026-07-10", "synthesis", daily, tmp_path / "packets")
    assert any("date mismatch" in item for item in failures)
    assert any("invalid operational claim status" in item for item in failures)
    assert any("invalid consequence" in item for item in failures)
    assert any("invalid public-use" in item for item in failures)
    assert any("invalid verification reference" in item for item in failures)
    assert any("unknown operational claim" in item for item in failures)


def test_operationally_supported_requires_supporting_assessed_packet(tmp_path: Path) -> None:
    packets = tmp_path / "packets"
    write_packet(packets, outcome="operationally_contested", chains=1)
    daily = write_day(
        tmp_path,
        "| `OPC-20260710-01` | A vessel was attacked. | `operationally_supported` | `high` | `yes` | `VER-20260710-01` |",
    )
    failures = verification.validate_day_claims("2026-07-10", "synthesis", daily, packets)
    assert failures == ["OPC-20260710-01: operationally_supported requires a supporting assessed packet"]


def test_internal_claim_without_public_or_forecast_gate_is_rejected(tmp_path: Path) -> None:
    daily = write_day(
        tmp_path,
        "| `OPC-20260710-01` | A vessel was damaged. | `contested` | `medium` | `no` | `VER-20260710-01` |",
    )
    failures = verification.validate_day_claims("2026-07-10", "synthesis", daily, tmp_path / "packets")
    assert any("orphan operational claim" in item for item in failures)


def test_attach_creates_valid_packet_updates_only_target_claim_and_rerenders_issue(tmp_path: Path, monkeypatch) -> None:
    daily = write_day(
        tmp_path,
        "| `OPC-20260710-01` | A vessel was attacked. | `source_assertion` | `high` | `no` | `request` |\n"
        "| `OPC-20260710-02` | A port was delayed. | `source_assertion` | `high` | `no` | `request` |",
        "| `NG-20260708-F02` | Claim | Mechanism | `OPC-20260710-01` |\n",
    )
    run = daily / "2026-07-10"
    for name in ("sources.md", "daily-brief.md"):
        (run / name).write_text("# Placeholder\n", encoding="utf-8")
    (run / "issue.md").write_text("stale issue", encoding="utf-8")
    template_path = tmp_path / "template.md"
    template_path.write_text(template(), encoding="utf-8")
    monkeypatch.setattr(verification, "validate_day_claims", lambda *args, **kwargs: [])
    import types
    fake_issue = types.SimpleNamespace(
        load_model=lambda run_date, daily_root, ledger_path: {"run_date": run_date},
        render_model=lambda model: f"rendered {model['run_date']}",
    )
    monkeypatch.setitem(sys.modules, "render_daily_issue", fake_issue)

    result = verification.attach_packet_to_claim(
        "2026-07-10",
        "OPC-20260710-01",
        "vessel-attack",
        daily_root=daily,
        packets_root=tmp_path / "packets",
        template_path=template_path,
        ledger_path=ledger(tmp_path / "ledger.md"),
        repo_root=tmp_path,
    )

    assert result["created"] is True
    assert result["packet"] == "VER-20260710-01"
    packet = verification.parse_packet(tmp_path / "packets" / "VER-20260710-01-vessel-attack" / "README.md")
    assert verification.validate_packet(packet, tmp_path, ledger(tmp_path / "ledger.md")) == []
    assert packet.fields["related_claim"] == "OPC-20260710-01"
    synthesis = (run / "synthesis.md").read_text(encoding="utf-8")
    assert "| `OPC-20260710-01` | A vessel was attacked. | `source_assertion` | `high` | `no` | `VER-20260710-01` |" in synthesis
    assert "| `OPC-20260710-02` | A port was delayed. | `source_assertion` | `high` | `no` | `request` |" in synthesis
    assert (run / "issue.md").read_text(encoding="utf-8") == "rendered 2026-07-10"


def test_attach_existing_packet_and_refuses_different_packet_without_force(tmp_path: Path, monkeypatch) -> None:
    daily = write_day(
        tmp_path,
        "| `OPC-20260710-01` | A vessel was attacked. | `source_assertion` | `high` | `no` | `VER-20260710-01` |",
        "| `NG-20260710-F01` | Claim | Mechanism | `OPC-20260710-01` |\n",
    )
    packets = tmp_path / "packets"
    template_path = tmp_path / "template.md"
    template_path.write_text(template(), encoding="utf-8")
    first = verification.create_packet("2026-07-10", "first", packets, template_path)
    second = verification.create_packet("2026-07-10", "second", packets, template_path)
    for path, claim_id in ((first, "OPC-20260710-01"), (second, "OPC-20260710-01")):
        verification.fill_requested_packet(
            path,
            claim_id=claim_id,
            claim="A vessel was attacked.",
            hooks=["NG-20260708-F02"],
            artifacts=[],
            observables=["Vessel identity"],
        )
    monkeypatch.setattr(verification, "validate_day_claims", lambda *args, **kwargs: [])

    try:
        verification.attach_packet_to_claim(
            "2026-07-10",
            "OPC-20260710-01",
            "second",
            packet_id="VER-20260710-02",
            daily_root=daily,
            packets_root=packets,
            template_path=template_path,
            ledger_path=ledger(tmp_path / "ledger.md"),
            repo_root=tmp_path,
        )
    except ValueError as exc:
        assert "already attached" in str(exc)
    else:
        raise AssertionError("expected refusal to replace an existing packet")

    result = verification.attach_packet_to_claim(
        "2026-07-10",
        "OPC-20260710-01",
        "second",
        packet_id="VER-20260710-02",
        force=True,
        daily_root=daily,
        packets_root=packets,
        template_path=template_path,
        ledger_path=ledger(tmp_path / "ledger.md"),
        repo_root=tmp_path,
    )

    assert result["created"] is False
    assert result["packet"] == "VER-20260710-02"
    assert "VER-20260710-02" in (daily / "2026-07-10" / "synthesis.md").read_text(encoding="utf-8")


def test_old_packets_without_related_claim_remain_valid(tmp_path: Path) -> None:
    packet = verification.parse_packet(write_packet(tmp_path / "packets", outcome="operationally_contested"))
    assert "related_claim" not in packet.fields
    assert verification.validate_packet(packet, tmp_path, ledger(tmp_path / "ledger.md")) == []


def test_invalid_related_claim_is_rejected(tmp_path: Path) -> None:
    path = write_packet(tmp_path / "packets", outcome="operationally_contested")
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("Claim: `A bounded event occurred.`", "Claim: `A bounded event occurred.`\n\nRelated claim: `NOT-AN-OPC`"), encoding="utf-8")
    packet = verification.parse_packet(path)
    failures = verification.validate_packet(packet, tmp_path, ledger(tmp_path / "ledger.md"))
    assert any("invalid related claim" in item for item in failures)

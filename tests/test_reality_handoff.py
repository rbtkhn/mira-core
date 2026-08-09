from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import reality_handoff
import reality_investigation


def configure_roots(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    daily_root = tmp_path / "daily"
    claims_root = tmp_path / "claims"
    daily_root.mkdir()
    claims_root.mkdir()
    monkeypatch.setattr(reality_handoff, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(reality_handoff, "DAILY_ROOT", daily_root)
    monkeypatch.setattr(reality_handoff, "CLAIMS_ROOT", claims_root)
    return daily_root, claims_root


def write_claim(
    claims_root: Path,
    claim_id: str,
    text: str,
    *,
    crisis_object: str = "",
    consequence: str = "high",
) -> None:
    payload = {
        "id": claim_id,
        "claim_type": "operational_factual",
        "consequence": consequence,
        "text": text,
        "crisis_object": crisis_object,
    }
    (claims_root / f"{claim_id}.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )


def write_daily(
    daily_root: Path,
    date: str,
    *,
    issue: str | None = None,
    synthesis: str | None = None,
) -> Path:
    daily = daily_root / date
    daily.mkdir()
    if issue is not None:
        (daily / "issue.md").write_text(issue, encoding="utf-8")
    if synthesis is not None:
        (daily / "synthesis.md").write_text(synthesis, encoding="utf-8")
    return daily


def audit_payload(claim_id: str) -> dict:
    return {
        "epistemic_state": {"assessment_status": f"status-for-{claim_id}"},
        "coverage": {
            "language_gate_satisfied": False,
            "lineage_gate_satisfied": True,
        },
        "missing_gates": ["language"],
        "next_bounded_action": "Find one additional language environment.",
    }


def tree_fingerprint(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_words_normalizes_and_removes_stopwords() -> None:
    assert reality_handoff.words(
        "The ESCALATION escalation and war with NATO into this."
    ) == {"escalation", "nato"}


@pytest.mark.parametrize(
    "value",
    (
        "20260729",
        "2026-7-29",
        "2026-02-29",
        "2026-13-01",
        "",
    ),
)
def test_build_rejects_invalid_dates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    configure_roots(tmp_path, monkeypatch)

    with pytest.raises(ValueError, match="date must"):
        reality_handoff.build(value)


def test_build_rejects_path_escape_before_reading_daily_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configure_roots(tmp_path, monkeypatch)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "issue.md").write_text(
        "This file must remain outside the daily corpus.", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="exact YYYY-MM-DD"):
        reality_handoff.build("../outside")


def test_build_reports_missing_daily_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configure_roots(tmp_path, monkeypatch)

    payload = reality_handoff.build("2026-07-29")

    assert payload["mode"] == "read-only handoff"
    assert payload["daily_issue"] is None
    assert payload["synthesis"] is None
    assert payload["issue_present"] is False
    assert payload["synthesis_present"] is False
    assert payload["candidate_count"] == 0
    assert payload["candidates"] == []
    assert len(payload["friction"]) == 3


def test_build_projects_matching_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    daily_root, claims_root = configure_roots(tmp_path, monkeypatch)
    write_daily(
        daily_root,
        "2026-07-29",
        issue="# Issue\n\nEscalation pressure around Odessa is increasing.",
    )
    write_claim(
        claims_root,
        "CLM-20260729-001",
        "Escalation pressure is visible near Odessa.",
        crisis_object="regional escalation",
    )
    monkeypatch.setattr(reality_handoff.reality, "audit_payload", audit_payload)

    payload = reality_handoff.build("2026-07-29")

    assert payload["candidate_count"] == 1
    assert payload["daily_issue"] == "daily/2026-07-29/issue.md"
    candidate = payload["candidates"][0]
    assert candidate == {
        "claim_id": "CLM-20260729-001",
        "type": "operational_factual",
        "consequence": "high",
        "text": "Escalation pressure is visible near Odessa.",
        "overlap_terms": ["escalation", "odessa", "pressure"],
        "assessment_status": "status-for-CLM-20260729-001",
        "language_gate": False,
        "lineage_gate": True,
        "missing_gates": ["language"],
        "next_bounded_action": "Find one additional language environment.",
    }


def test_build_excludes_nonmatching_claims(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    daily_root, claims_root = configure_roots(tmp_path, monkeypatch)
    write_daily(daily_root, "2026-07-29", issue="Escalation around Odessa.")
    write_claim(
        claims_root,
        "CLM-20260729-001",
        "Escalation is visible near Odessa.",
    )
    write_claim(
        claims_root,
        "CLM-20260729-002",
        "Agricultural commodity prices changed.",
    )
    observed: list[str] = []

    def audit(claim_id: str) -> dict:
        observed.append(claim_id)
        return audit_payload(claim_id)

    monkeypatch.setattr(reality_handoff.reality, "audit_payload", audit)

    payload = reality_handoff.build("2026-07-29")

    assert [item["claim_id"] for item in payload["candidates"]] == [
        "CLM-20260729-001"
    ]
    assert observed == ["CLM-20260729-001"]


def test_candidates_sort_by_overlap_then_claim_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    daily_root, claims_root = configure_roots(tmp_path, monkeypatch)
    write_daily(
        daily_root,
        "2026-07-29",
        issue="Alpha bravo charlie delta.",
    )
    write_claim(claims_root, "CLM-C", "Alpha bravo charlie.")
    write_claim(claims_root, "CLM-B", "Alpha bravo.")
    write_claim(claims_root, "CLM-A", "Alpha bravo.")
    monkeypatch.setattr(reality_handoff.reality, "audit_payload", audit_payload)

    payload = reality_handoff.build("2026-07-29")

    assert [item["claim_id"] for item in payload["candidates"]] == [
        "CLM-C",
        "CLM-A",
        "CLM-B",
    ]
    assert [len(item["overlap_terms"]) for item in payload["candidates"]] == [
        3,
        2,
        2,
    ]


def test_synthesis_only_does_not_generate_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    daily_root, claims_root = configure_roots(tmp_path, monkeypatch)
    write_daily(
        daily_root,
        "2026-07-29",
        synthesis="Escalation pressure around Odessa is increasing.",
    )
    write_claim(
        claims_root,
        "CLM-20260729-001",
        "Escalation pressure is visible near Odessa.",
    )
    monkeypatch.setattr(reality_handoff.reality, "audit_payload", audit_payload)

    payload = reality_handoff.build("2026-07-29")

    assert payload["issue_present"] is False
    assert payload["synthesis_present"] is True
    assert payload["candidate_count"] == 0
    assert payload["candidates"] == []


def test_build_is_read_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    daily_root, claims_root = configure_roots(tmp_path, monkeypatch)
    write_daily(
        daily_root,
        "2026-07-29",
        issue="Escalation around Odessa.",
        synthesis="A separate synthesis.",
    )
    write_claim(
        claims_root,
        "CLM-20260729-001",
        "Escalation is visible near Odessa.",
    )
    monkeypatch.setattr(reality_handoff.reality, "audit_payload", audit_payload)
    before = tree_fingerprint(tmp_path)

    reality_handoff.build("2026-07-29")

    assert tree_fingerprint(tmp_path) == before


def test_main_supports_json_and_text_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    daily_root, claims_root = configure_roots(tmp_path, monkeypatch)
    write_daily(daily_root, "2026-07-29", issue="Escalation around Odessa.")
    write_claim(
        claims_root,
        "CLM-20260729-001",
        "Escalation is visible near Odessa.",
    )
    monkeypatch.setattr(reality_handoff.reality, "audit_payload", audit_payload)
    monkeypatch.setattr(
        sys,
        "argv",
        ["reality_handoff.py", "--date", "2026-07-29", "--json"],
    )

    assert reality_handoff.main() == 0
    structured = json.loads(capsys.readouterr().out)
    assert structured["candidate_count"] == 1

    monkeypatch.setattr(
        sys,
        "argv",
        ["reality_handoff.py", "--date", "2026-07-29"],
    )
    assert reality_handoff.main() == 0
    text = capsys.readouterr().out
    assert "date=2026-07-29 mode=read-only handoff candidates=1" in text
    assert "CLM-20260729-001 | status-for-CLM-20260729-001" in text
    assert "friction=" in text


def test_claim_first_handoff_resolves_exact_claim_without_lexical_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    daily_root, claims_root = configure_roots(tmp_path, monkeypatch)
    write_claim(
        claims_root,
        "NG-20260708-F02",
        "A visible attempt to weaken or bypass Iranian transit authority produces a visible coercive response.",
        crisis_object="Hormuz transit governance",
    )
    ledger = tmp_path / "narrative-geopolitics" / "work" / "forecasts"
    ledger.mkdir(parents=True)
    (ledger / "forecast-ledger.md").write_text(
        "| `NG-20260708-F02` | `2026-07-08` | Hormuz | Claim | `likely` | `2026-07-29` | source | `open` |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(reality_handoff.reality, "audit_payload", audit_payload)

    payload = reality_handoff.build_claim_handoff("NG-20260708-F02")

    assert payload["claim"]["id"] == "NG-20260708-F02"
    assert payload["web_search"]["status"] == "not triggered"
    assert [item["id"] for item in payload["investigation_plan"]["observables"]] == [
        "bypass_attempt",
        "coercive_response",
        "attribution",
        "measurable_effect",
    ]
    assert payload["investigation_plan"]["web_authority"] == "standing"
    assert payload["investigation_plan"]["time_window"]["end"] == "2026-07-29"
    assert payload["investigation_plan"]["target_languages"] == ["en", "fa", "ar"]


def test_claim_first_investigate_gate_reports_delegated_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, claims_root = configure_roots(tmp_path, monkeypatch)
    write_claim(claims_root, "NG-20260708-F02", "A transit forecast.")
    monkeypatch.setattr(reality_handoff.reality, "audit_payload", audit_payload)

    payload = reality_handoff.build_claim_handoff("NG-20260708-F02", investigate=True)

    assert payload["web_search"]["status"] == "gated and executed"
    assert payload["web_search"]["execution_layer"] == "agent-tool-boundary"


def test_claim_first_handoff_seeds_only_research_addressable_gaps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, claims_root = configure_roots(tmp_path, monkeypatch)
    write_claim(
        claims_root,
        "CLM-20260803-001",
        "A bounded operational event occurred.",
        crisis_object="bounded event",
    )
    monkeypatch.setattr(
        reality_handoff.reality,
        "audit_payload",
        lambda claim_id: {
            "epistemic_state": {"assessment_status": "unassessed"},
            "missing_gates": [
                "origin_language_coverage",
                "independent_lineage_coverage",
                "human_signoff",
            ],
        },
    )

    payload = reality_handoff.build_claim_handoff("CLM-20260803-001")
    seed = payload["research_brief_seed"]

    assert seed["schema"] == "research-brief-seed-v1"
    assert seed["producer"]["workflow"] == "reality-handoff"
    assert seed["routing_hint"]["workflow"] == "reality-check"
    assert seed["identifiers"]["canonical_claim_id"] == "CLM-20260803-001"
    assert seed["unresolved_gaps"] == [
        "origin_language_coverage",
        "independent_lineage_coverage",
    ]
    assert "human_signoff" not in seed["unresolved_gaps"]
    assert not any(seed["authority"].values())


def test_claim_first_handoff_does_not_seed_governance_only_gaps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, claims_root = configure_roots(tmp_path, monkeypatch)
    write_claim(claims_root, "CLM-20260803-001", "A bounded claim.")
    monkeypatch.setattr(
        reality_handoff.reality,
        "audit_payload",
        lambda claim_id: {
            "epistemic_state": {"assessment_status": "supported"},
            "missing_gates": ["human_signoff", "canonical_assessment"],
        },
    )

    payload = reality_handoff.build_claim_handoff("CLM-20260803-001")

    assert "research_brief_seed" not in payload


def test_date_lexical_candidates_do_not_receive_research_seeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    daily_root, claims_root = configure_roots(tmp_path, monkeypatch)
    write_daily(daily_root, "2026-08-03", issue="Escalation around Odessa.")
    write_claim(claims_root, "CLM-20260803-001", "Escalation is visible near Odessa.")
    monkeypatch.setattr(reality_handoff.reality, "audit_payload", audit_payload)

    payload = reality_handoff.build("2026-08-03")

    assert payload["candidates"]
    assert all("research_brief_seed" not in item for item in payload["candidates"])


def test_reality_seed_bounds_references_without_changing_linked_artifacts() -> None:
    links = {
        "daily_forecasts": [f"daily/{index:02d}/forecast.md" for index in range(25)],
        "syntheses": [],
        "issues": [],
        "ledger": [],
    }
    seed = reality_handoff.research_brief_seed(
        {
            "id": "CLM-20260803-001",
            "text": "A bounded claim.",
            "crisis_object": "bounded event",
        },
        {
            "epistemic_state": {"assessment_status": "unassessed"},
            "missing_gates": ["independent_lineage_coverage"],
        },
        {
            "time_window": {"start": "2026-08-01", "end": "2026-08-03"},
            "target_languages": ["en"],
        },
        links,
    )

    assert seed is not None
    assert len(seed["producer"]["source_refs"]) == 20
    assert len(links["daily_forecasts"]) == 25
    assert any("additional references" in text for text in seed["known_context"])


def test_missing_exact_claim_blocks_investigation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configure_roots(tmp_path, monkeypatch)

    with pytest.raises(ValueError, match="claim not in lattice"):
        reality_handoff.build_claim_handoff("NG-20260708-F02")


def test_source_quality_and_lineage_rules() -> None:
    assert reality_investigation.source_tier("https://www.imo.org/page") == "primary"
    assert reality_investigation.source_tier("https://www.reddit.com/r/example") == "discovery-only"
    assert reality_investigation.source_tier("https://example.com/commentary", role="commentary") == "discovery-only"
    assert reality_investigation.lineage_root(canonical_url="https://example.com/a", syndication_root="wire-1") == "wire-1"
    assert reality_investigation.window_status("2026-07-24", "2026-07-24", "2026-08-02") == "inside"
    assert reality_investigation.window_status("2026-07-23", "2026-07-24", "2026-08-02") == "outside"
    assert reality_investigation.observable_disposition(supports=1, challenges=1) == "contested"

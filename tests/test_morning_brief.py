from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures" / "morning-brief"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


morning_brief = load_module("morning_brief_tests", SCRIPTS_ROOT / "morning_brief.py")
skill_registry = load_module(
    "morning_brief_skill_registry_tests", SCRIPTS_ROOT / "codex_skill_registry.py"
)
repository_validation = load_module(
    "morning_brief_repository_validation_tests",
    SCRIPTS_ROOT / "validate_repository.py",
)


DATE = "2026-08-03"
AS_OF = "2026-08-03T13:00:00Z"
START = "2026-08-02T13:00:00Z"
JUDGMENT_DATE = "2026-08-01"
HOOK_ID = "NG-20260801-F01"


def write_repository(root: Path) -> tuple[Path, Path]:
    daily_root = root / "narrative-geopolitics" / "work" / "daily"
    judgment = daily_root / JUDGMENT_DATE / "judgment.md"
    judgment.parent.mkdir(parents=True)
    judgment.write_text(
        f"""# Accountable Judgment — {JUDGMENT_DATE}

Status: `live-intake-first`
As-of: `{JUDGMENT_DATE}`
Crisis object: `Can concentrated infrastructure exposure constrain escalation?`
Review date: `2026-08-08`

## Decision Compression

What changed: `Infrastructure exposure became the governing constraint.`

Reusable mechanism: `Concentrated systems can accumulate risk faster than coercion restores leverage.`

Decision implication: `Watch independently sourced infrastructure and basing indicators.`

Evidence still missing: `Independent operational confirmation and lineage-separated reporting.`

Recommended disposition: `verification-request`
""",
        encoding="utf-8",
        newline="\n",
    )
    ledger = root / "narrative-geopolitics" / "work" / "forecasts" / "forecast-ledger.md"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(
        f"""# Forecast Ledger

## Entries

| Hook ID | Date | Crisis Object | Claim | Probability Band | Review Date | Source Run | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `{HOOK_ID}` | `{JUDGMENT_DATE}` | Infrastructure exposure | Infrastructure exposure will constrain coalition freedom of action. | `plausible` | `2026-08-03` | [run](../daily/2026-08-01/forecast.md) | `open` |
| `NG-20260701-F01` | `2026-07-01` | Closed hook | This hook is closed. | `low` | `2026-07-10` | [run](../daily/2026-07-01/forecast.md) | `hit` |
| `NG-20260702-F01` | `2026-07-02` | Nonaccountable hook | This hook is not accountable. | `low` | `2026-08-03` | [run](../daily/2026-07-02/forecast.md) | `open` |

## Accountability Triage

| Hook ID | Authored No Later Than | Timing Provenance | Forecast Type | Resolution Status | Accountable | Review Note |
| --- | --- | --- | --- | --- | --- | --- |
| `{HOOK_ID}` | `2026-08-01` | `same-day-live-intake` | `ex_ante` | `open` | `yes` | Review remains prospective. |
| `NG-20260701-F01` | `2026-07-01` | `same-day-live-intake` | `ex_ante` | `hit` | `yes` | Resolved with VER-20260710-01. |
| `NG-20260702-F01` | `2026-07-02` | `git_worktree_uncommitted` | `ex_ante` | `open` | `no` | Not accountable. |
""",
        encoding="utf-8",
        newline="\n",
    )
    return daily_root, ledger


def add_accountable_forecast(
    root: Path,
    hook_id: str,
    *,
    review_date: str,
    claim: str,
) -> None:
    ledger = root / "narrative-geopolitics" / "work" / "forecasts" / "forecast-ledger.md"
    text = ledger.read_text(encoding="utf-8")
    entry = (
        f"| `{hook_id}` | `2026-08-02` | Additional fixture hook | {claim} | "
        f"`plausible` | `{review_date}` | [run](../daily/2026-08-02/forecast.md) | `open` |\n"
    )
    triage = (
        f"| `{hook_id}` | `2026-08-02` | `same-day-live-intake` | `ex_ante` | "
        "`open` | `yes` | Review remains prospective. |\n"
    )
    text = text.replace(
        "| `NG-20260701-F01` | `2026-07-01` | Closed hook",
        entry + "| `NG-20260701-F01` | `2026-07-01` | Closed hook",
        1,
    )
    text = text.replace(
        "| `NG-20260701-F01` | `2026-07-01` | `same-day-live-intake`",
        triage + "| `NG-20260701-F01` | `2026-07-01` | `same-day-live-intake`",
        1,
    )
    ledger.write_text(text, encoding="utf-8", newline="\n")


def remove_accountable_forecast(root: Path) -> None:
    ledger = root / "narrative-geopolitics" / "work" / "forecasts" / "forecast-ledger.md"
    lines = ledger.read_text(encoding="utf-8").splitlines()
    ledger.write_text(
        "\n".join(line for line in lines if f"`{HOOK_ID}`" not in line) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def candidate(
    candidate_id: str,
    *,
    provider: str,
    lineage: str,
    disposition: str,
    kind: str = "development",
    impact: str = "complicates",
) -> dict:
    included = disposition == "included"
    return {
        "id": candidate_id,
        "kind": kind,
        "title": f"Candidate {candidate_id}",
        "geography": "West Asia" if candidate_id == "OBS-01" else "Europe",
        "domain": "security" if candidate_id == "OBS-01" else "diplomacy",
        "observed_at_utc": "2026-08-03T08:00:00Z",
        "retrieved_at_utc": "2026-08-03T09:00:00Z",
        "observation": f"A narrow, upstream-linked observation for {candidate_id}.",
        "interpretation": f"Provisional impact assessment for {candidate_id}.",
        "materiality": f"The observation tests an inherited constraint for {candidate_id}.",
        "model_refs": ["JUDG-20260801"] if kind == "development" else [],
        "forecast_refs": [HOOK_ID] if kind == "development" else [],
        "impact": impact,
        "confidence_boundary": "One recovered upstream source; independent corroboration remains absent.",
        "discovery": {
            "provider": "Broad search",
            "reference": f"https://discovery.invalid/{candidate_id.lower()}",
            "is_evidence": False,
        },
        "upstream": {
            "provider": provider,
            "url": f"https://{provider.lower().replace(' ', '-')}.example/{candidate_id.lower()}",
            "source_type": "official" if candidate_id == "OBS-01" else "wire",
            "lineage_root": lineage,
            "freshness": "fresh",
        },
        "related_observations": [],
        "disposition": disposition,
        "selection_reason": "Included for materiality." if included else "Reviewed but below threshold.",
        "reality": {
            "match_status": "none",
            "claim_refs": [],
            "assessment_refs": [],
            "epistemic_state": {"status": "not-in-lattice", "claims": []},
            "relationship": "context-only",
            "lattice_paths": [],
            "audited_at_utc": "2026-08-03T10:00:00Z",
            "confidence_effect": "No exact lattice claim exists; interpretation remains provisional.",
        },
    }


def receipt(root: Path, *, material_change: bool = True) -> dict:
    daily_root = root / "narrative-geopolitics" / "work" / "daily"
    ledger = root / "narrative-geopolitics" / "work" / "forecasts" / "forecast-ledger.md"
    judgments = morning_brief.expected_judgments(
        morning_brief.exact_date(DATE, "date"), repo_root=root, daily_root=daily_root
    )
    forecasts = morning_brief.expected_forecasts(
        morning_brief.exact_date(DATE, "date"), repo_root=root, ledger_path=ledger
    )
    for row in forecasts:
        row["impact"] = "strengthens" if material_change else "unaffected"
    candidates = [
        candidate(
            "OBS-01",
            provider="Official Source",
            lineage="lineage-official-1",
            disposition="included" if material_change else "excluded",
        ),
        candidate(
            "OBS-02",
            provider="Wire Service",
            lineage="lineage-wire-2",
            disposition="excluded",
        ),
        candidate(
            "OBS-03",
            provider="Primary Record",
            lineage="lineage-primary-3",
            disposition="hold",
        ),
    ]
    return {
        "schema_version": "2.1",
        "renderer_version": "2.1",
        "brief_date": DATE,
        "as_of_utc": AS_OF,
        "window": {"start_utc": START, "end_utc": AS_OF, "hours": 24},
        "research": {
            "mode": "scan",
            "geography": "global",
            "output": "five-minute-selective-global-update",
            "stop_condition": "Four material developments plus one outlier or gap, or exhaustion.",
            "retrieved_at_utc": "2026-08-03T12:00:00Z",
        },
        "coverage": {
            "scope": "selective-global",
            "retrieval_status": "healthy",
            "geographies": ["West Asia", "Europe", "East Asia"],
            "domains": ["security", "diplomacy"],
            "upstream_sources_reviewed": 3,
            "lineage_roots_reviewed": 3,
            "limitations": ["East Asia visibility was thinner than West Asia coverage."],
        },
        "morning_judgment": (
            "Fresh observations complicate the inherited infrastructure-exposure model."
            if material_change
            else "No material change cleared the threshold in a healthy selective-global scan."
        ),
        "material_change": material_change,
        "baseline": {
            "lookback_days": 30,
            "judgments": judgments,
            "forecasts": forecasts,
        },
        "candidates": candidates,
        "gaps": [
            {
                "id": "GAP-01",
                "type": "thin",
                "geography": "East Asia",
                "domain": "diplomacy",
                "description": "Recovered upstream coverage was thinner in East Asia.",
                "consequence": "The scan cannot infer stability from limited visibility.",
                "disposition": "selected",
            }
        ],
        "selected_development_ids": ["OBS-01"] if material_change else [],
        "selected_outlier_or_gap": {"kind": "gap", "id": "GAP-01"},
        "watch": [
            {
                "id": "WATCH-01",
                "observable": "Independent confirmation of infrastructure or basing effects.",
                "timing": "Next 24 hours",
                "source_refs": ["JUDG-20260801", HOOK_ID],
            }
        ],
    }


def refresh_coverage_counts(payload: dict) -> None:
    upstream = [row["upstream"] for row in payload["candidates"] if row["upstream"]]
    payload["coverage"]["upstream_sources_reviewed"] = len(
        {row["provider"] for row in upstream}
    )
    payload["coverage"]["lineage_roots_reviewed"] = len(
        {row["lineage_root"] for row in upstream}
    )


def attach_related(
    payload: dict,
    candidate_id: str = "OBS-04",
    *,
    relationship: str = "qualifies",
    selected_id: str = "OBS-01",
    provider: str = "Related Source",
    lineage: str = "lineage-related-4",
) -> dict:
    related = candidate(
        candidate_id,
        provider=provider,
        lineage=lineage,
        disposition="related",
        impact="no-material-effect",
    )
    related["model_refs"] = []
    related["forecast_refs"] = []
    related["selection_reason"] = f"Related to {selected_id}."
    payload["candidates"].append(related)
    selected = next(row for row in payload["candidates"] if row["id"] == selected_id)
    selected["related_observations"].append(
        {"candidate_id": candidate_id, "relationship": relationship}
    )
    refresh_coverage_counts(payload)
    return related


def write_receipt(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def generate(root: Path, payload: dict, *, output_name: str = "output", overwrite: bool = False):
    input_path = write_receipt(root / "input" / "receipt.json", payload)
    return morning_brief.generate_brief(
        DATE,
        AS_OF,
        input_path,
        repo_root=root,
        daily_root=root / "narrative-geopolitics" / "work" / "daily",
        ledger_path=root / "narrative-geopolitics" / "work" / "forecasts" / "forecast-ledger.md",
        reality_root=root / "narrative-geopolitics" / "work" / "reality",
        brief_root=root / output_name,
        overwrite=overwrite,
    )


@pytest.fixture
def bounded_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    write_repository(root)
    return root


def write_unassessed_claim(root: Path, claim_id: str = "CLM-20260803-001") -> Path:
    reality_root = root / "narrative-geopolitics" / "work" / "reality"
    claim = morning_brief.reality.new_claim(
        claim_id,
        "2026-08-03",
        "operational_factual",
        "A bounded observable occurred during the morning observation window.",
        consequence="medium",
        crisis_object="fixture crisis object",
        scope="fixture atomic observable",
    )
    morning_brief.reality.write_record(claim, reality_root)
    return reality_root


def matched_reality(
    root: Path,
    *,
    claim_id: str = "CLM-20260803-001",
    match_status: str = "exact",
    relationship: str = "same-observable",
    confidence_effect: str = "The exact claim is unassessed, so interpretation remains provisional.",
) -> dict:
    reality_root = root / "narrative-geopolitics" / "work" / "reality"
    assessments, state, paths, _ = morning_brief.reality_lattice_snapshot(
        [claim_id], repo_root=root, reality_root=reality_root
    )
    return {
        "match_status": match_status,
        "claim_refs": [claim_id],
        "assessment_refs": assessments,
        "epistemic_state": state,
        "relationship": relationship,
        "lattice_paths": paths,
        "audited_at_utc": "2026-08-03T10:00:00Z",
        "confidence_effect": confidence_effect,
    }


def write_assessment(root: Path, claim_id: str, outcome: str, *, status: str = "draft") -> None:
    reality_root = root / "narrative-geopolitics" / "work" / "reality"
    record = morning_brief.reality.base_record(
        "ADJ-20260803-001", "assessment", "2026-08-03", status=status, creator="fixture"
    )
    record.update(
        {
            "claim_id": claim_id,
            "outcome": outcome,
            "confidence_boundary": "Fixture assessment boundary.",
            "rationale": "Fixture assessment rationale.",
            "evidence_ids": [],
            "observable_ids": [],
            "signoffs": [],
            "authorizes_public": False,
            "authorizes_forecast_scoring": False,
            "language_audit": {
                "origin_languages": [],
                "originating_chains": [],
                "regional_environment_present": False,
                "external_environment_present": False,
                "missing_environments": [],
            },
            "physical_evidence_exception": False,
            "language_search_record": "",
            "calibration_eligible": False,
        }
    )
    morning_brief.reality.write_record(record, reality_root)


def test_material_change_renders_five_minute_internal_update(bounded_repo: Path) -> None:
    brief_path, receipt_path = generate(bounded_repo, receipt(bounded_repo))
    body = brief_path.read_text(encoding="utf-8")
    stored = receipt_path.read_bytes()
    assert "# Morning Brief — 2026-08-03" in body
    assert "Status: `experimental-internal-morning-update`" in body
    assert "## Material Developments" in body
    assert "## Outlier or Visibility Gap" in body
    assert "## Forecast Pressure" in body
    assert "## What to Watch" in body
    assert "**Material pressure:**" in body
    assert "**What it does to the model — `complicates`:**" in body
    assert "**Source:**" in body
    assert "Geography / domain" not in body
    assert "Support:" not in body
    assert "`1` valid judgment(s), `1` accountable open forecast(s)" in body
    assert "East Asia visibility was thinner than West Asia coverage." in body
    assert "World Monitor" not in body
    assert hashlib.sha256(stored).hexdigest() in body
    assert "Ã" not in body and "â€" not in body


def test_no_material_change_generates_valid_gap_brief(bounded_repo: Path) -> None:
    brief_path, _ = generate(bounded_repo, receipt(bounded_repo, material_change=False))
    body = brief_path.read_text(encoding="utf-8")
    assert "No material change" in body
    assert "No material development cleared the selection threshold" in body
    assert "East Asia — diplomacy" in body
    assert "No accountable open forecast is materially pressured." in body
    assert "### Due, unpressured" in body
    assert "**No new pressure.**" in body


def test_pressured_forecast_requires_selected_development_reference(
    bounded_repo: Path,
) -> None:
    payload = receipt(bounded_repo)
    payload["candidates"][0]["forecast_refs"] = []
    with pytest.raises(
        morning_brief.BriefError,
        match="pressured forecast lacks a selected material-development reference",
    ):
        generate(bounded_repo, payload)


def test_selected_forecast_reference_cannot_be_labeled_unaffected(
    bounded_repo: Path,
) -> None:
    payload = receipt(bounded_repo)
    payload["baseline"]["forecasts"][0]["impact"] = "unaffected"
    with pytest.raises(
        morning_brief.BriefError,
        match=r"selected development references forecast\(s\) labeled unaffected",
    ):
        generate(bounded_repo, payload)


def test_forecast_pressure_separates_pressure_due_and_unaffected(
    bounded_repo: Path,
) -> None:
    due_only = "NG-20260802-F01"
    unaffected = "NG-20260810-F01"
    add_accountable_forecast(
        bounded_repo,
        due_only,
        review_date="2026-08-02",
        claim="A due-only fixture claim remains open.",
    )
    add_accountable_forecast(
        bounded_repo,
        unaffected,
        review_date="2026-08-10",
        claim="A future unaffected fixture claim remains open.",
    )
    payload = receipt(bounded_repo)
    for row in payload["baseline"]["forecasts"]:
        if row["hook_id"] != HOOK_ID:
            row["impact"] = "unaffected"
    brief_path, _ = generate(bounded_repo, payload)
    body = brief_path.read_text(encoding="utf-8")

    assert "### Pressured today" in body
    assert "**Pressure: `strengthens`.**" in body
    assert f"(`{HOOK_ID}`; due today)" in body
    pressure = body.split("## Forecast Pressure", 1)[1].split("## What to Watch", 1)[0]
    assert pressure.count(f"`{HOOK_ID}`") == 1
    assert "### Due, unpressured" in body
    assert "A due-only fixture claim remains open. **No new pressure.**" in body
    assert f"(`{due_only}`; overdue since `2026-08-02`)" in body
    assert "`1` unaffected, not-due forecast(s)." in body
    assert "not due `" not in body
    assert body.index(f"`{HOOK_ID}`; due today") < body.index(f"`{due_only}`; overdue")


def test_pressured_forecasts_order_due_first_then_review_date(
    bounded_repo: Path,
) -> None:
    overdue = "NG-20260801-F02"
    future = "NG-20260810-F02"
    add_accountable_forecast(
        bounded_repo,
        overdue,
        review_date="2026-08-01",
        claim="An overdue pressured fixture claim remains open.",
    )
    add_accountable_forecast(
        bounded_repo,
        future,
        review_date="2026-08-10",
        claim="A future pressured fixture claim remains open.",
    )
    payload = receipt(bounded_repo)
    payload["candidates"][0]["forecast_refs"] = [overdue, HOOK_ID, future]
    brief_path, _ = generate(bounded_repo, payload)
    body = brief_path.read_text(encoding="utf-8")
    pressure = body.split("### Pressured today", 1)[1].split("## What to Watch", 1)[0]
    assert pressure.index(overdue) < pressure.index(HOOK_ID) < pressure.index(future)
    assert "overdue since `2026-08-01`" in pressure
    assert "due today" in pressure
    assert "review `2026-08-10`" in pressure


def test_empty_forecast_baseline_renders_explicitly(bounded_repo: Path) -> None:
    remove_accountable_forecast(bounded_repo)
    payload = receipt(bounded_repo, material_change=False)
    for row in payload["candidates"]:
        row["forecast_refs"] = []
    payload["watch"] = []
    brief_path, _ = generate(bounded_repo, payload)
    body = brief_path.read_text(encoding="utf-8")
    assert "No accountable open forecasts are present in the baseline." in body


def test_identical_receipts_render_byte_identically(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    first = generate(bounded_repo, payload, output_name="first")
    second = generate(bounded_repo, payload, output_name="second")
    assert first[0].read_bytes() == second[0].read_bytes()
    assert first[1].read_bytes() == second[1].read_bytes()


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        (lambda value: value["baseline"]["judgments"][0].update(sha256="0" * 64), "judgment baseline"),
        (lambda value: value["candidates"][0].update(upstream=None), "upstream evidence"),
        (
            lambda value: value["candidates"][0]["upstream"].update(freshness="stale"),
            "must be fresh",
        ),
        (lambda value: value.update(as_of_utc="2026-08-03T13:00:00"), "RFC3339"),
        (
            lambda value: value["coverage"].update(retrieval_status="degraded"),
            "fail closed",
        ),
        (lambda value: value["candidates"][0].update(impact="confirms"), "invalid model impact"),
        (
            lambda value: value["candidates"][0].update(observed_at_utc="2026-08-01T08:00:00Z"),
            "outside observation contract",
        ),
    ),
)
def test_invalid_receipts_fail_without_creating_output(
    bounded_repo: Path, mutation, message: str
) -> None:
    payload = receipt(bounded_repo)
    mutation(payload)
    with pytest.raises(morning_brief.BriefError, match=message):
        generate(bounded_repo, payload)
    assert not (bounded_repo / "output").exists()


def test_shared_selected_lineage_is_rejected(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    outlier = payload["candidates"][1]
    outlier.update(kind="outlier", disposition="included", impact="no-material-effect")
    outlier["model_refs"] = []
    outlier["forecast_refs"] = []
    outlier["upstream"]["lineage_root"] = payload["candidates"][0]["upstream"]["lineage_root"]
    payload["candidates"].append(
        candidate(
            "OBS-04",
            provider="Additional Wire",
            lineage="lineage-additional-4",
            disposition="excluded",
        )
    )
    payload["coverage"]["upstream_sources_reviewed"] = 4
    payload["gaps"][0]["disposition"] = "recorded"
    payload["selected_outlier_or_gap"] = {"kind": "candidate", "id": "OBS-02"}
    with pytest.raises(morning_brief.BriefError, match="share one upstream lineage"):
        generate(bounded_repo, payload)


def test_four_development_limit_is_enforced(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    payload["selected_development_ids"] = ["OBS-01", "OBS-02", "OBS-03", "OBS-04", "OBS-05"]
    with pytest.raises(morning_brief.BriefError, match="0-4 values"):
        generate(bounded_repo, payload)


def test_only_open_accountable_forecasts_enter_baseline(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    assert [row["hook_id"] for row in payload["baseline"]["forecasts"]] == [HOOK_ID]
    assert payload["baseline"]["forecasts"][0]["due"] is True
    payload["baseline"]["forecasts"][0]["due"] = False
    with pytest.raises(morning_brief.BriefError, match="forecast baseline mismatch"):
        generate(bounded_repo, payload)


def test_existing_pair_requires_overwrite_and_updates_together(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    brief_path, receipt_path = generate(bounded_repo, payload)
    original = (brief_path.read_bytes(), receipt_path.read_bytes())
    with pytest.raises(morning_brief.BriefError, match="use --overwrite"):
        generate(bounded_repo, payload)
    assert (brief_path.read_bytes(), receipt_path.read_bytes()) == original
    payload["morning_judgment"] = "Fresh observations weaken the inherited infrastructure-exposure model."
    payload["candidates"][0]["impact"] = "weakens"
    payload["baseline"]["forecasts"][0]["impact"] = "weakens"
    updated = generate(bounded_repo, payload, overwrite=True)
    assert "weaken" in updated[0].read_text(encoding="utf-8")
    assert hashlib.sha256(updated[1].read_bytes()).hexdigest() in updated[0].read_text(encoding="utf-8")


def test_generation_does_not_mutate_repository_evidence_or_state(bounded_repo: Path) -> None:
    protected = [
        bounded_repo / "narrative-geopolitics" / "work" / "daily" / JUDGMENT_DATE / "judgment.md",
        bounded_repo / "narrative-geopolitics" / "work" / "forecasts" / "forecast-ledger.md",
    ]
    archive_manifest = bounded_repo / "archive" / "sources" / "geopolitics" / "source-manifest.json"
    archive_manifest.parent.mkdir(parents=True)
    archive_manifest.write_text('{"source_count": 0, "sources": []}\n', encoding="utf-8")
    protected.append(archive_manifest)
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
    generate(bounded_repo, receipt(bounded_repo))
    assert {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected} == before


def test_full_source_bodies_are_rejected(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    payload["candidates"][0]["raw_body"] = "A full article does not belong here."
    with pytest.raises(morning_brief.BriefError, match="may not retain full source field"):
        generate(bounded_repo, payload)


def test_canonical_runner_routes_new_interface() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools" / "run_repo.py"),
            "morning-brief",
            "--date",
            "not-a-date",
            "--as-of",
            AS_OF,
            "--receipt",
            "missing.json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "--date must be an exact YYYY-MM-DD value" in result.stderr


def test_morning_brief_is_governed_local_only_and_research_led() -> None:
    assert "morning-brief" in repository_validation.LOCAL_SKILLS
    assert "morning-brief" not in skill_registry.DEPLOYABLE_SKILL_NAMES
    assert "morning-brief" not in skill_registry.build_registry()
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    skill = (REPO_ROOT / "docs" / "skill-drafts" / "morning-brief" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    normalized_skill = " ".join(skill.split())
    assert "docs/skill-drafts/morning-brief/SKILL.md" in agents
    assert ".\\tools\\run.ps1 morning-brief" in skill
    assert "Use broad current search and other non-evidentiary discovery surfaces" in normalized_skill
    assert (
        "Recover an official, primary, wire, or clearly attributed upstream source"
        in normalized_skill
    )
    assert "Discovery surfaces are never evidence" in skill
    assert "experimental-internal-morning-update" in skill
    assert "version `2.1`" in skill
    assert "related_observations" in skill
    assert "version-3" in skill
    assert "--from-date" not in skill
    assert "python scripts/morning_brief.py" not in skill
    example_path = (
        REPO_ROOT
        / "docs"
        / "skill-drafts"
        / "morning-brief"
        / "assets"
        / "receipt-v2.json"
    )
    example = json.loads(example_path.read_text(encoding="utf-8"))
    assert example["schema_version"] == "2.1"
    assert example["renderer_version"] == "2.1"
    assert example["candidates"][0]["related_observations"] == []


def test_historical_august_2_specimen_is_unchanged_and_protected(tmp_path: Path) -> None:
    specimen = REPO_ROOT / "narrative-geopolitics" / "work" / "morning-brief" / "2026-08-02.md"
    before = hashlib.sha256(specimen.read_bytes()).hexdigest()
    input_path = tmp_path / "irrelevant.json"
    input_path.write_text("{}\n", encoding="utf-8")
    with pytest.raises(morning_brief.BriefError, match="historical morning-brief specimen is protected"):
        morning_brief.generate_brief(
            "2026-08-02", AS_OF, input_path, brief_root=morning_brief.BRIEF_ROOT, overwrite=True
        )
    assert hashlib.sha256(specimen.read_bytes()).hexdigest() == before


def test_reality_exact_contextual_and_absent_matches_remain_distinct(
    bounded_repo: Path,
) -> None:
    write_unassessed_claim(bounded_repo)
    payload = receipt(bounded_repo)
    payload["candidates"][0]["reality"] = matched_reality(bounded_repo)
    payload["candidates"][1]["reality"] = matched_reality(
        bounded_repo,
        match_status="contextual",
        relationship="context-only",
        confidence_effect="The older claim supplies context only and does not verify this event.",
    )
    brief_path, stored_path = generate(bounded_repo, payload)
    stored = json.loads(stored_path.read_text(encoding="utf-8"))
    assert [row["reality"]["match_status"] for row in stored["candidates"]] == [
        "exact",
        "contextual",
        "none",
    ]
    body = brief_path.read_text(encoding="utf-8")
    assert "## Analyst's Note" in body
    assert "CLM-20260803-001" in body
    assert "unassessed" in body


def test_contextual_claim_cannot_masquerade_as_same_observable(bounded_repo: Path) -> None:
    write_unassessed_claim(bounded_repo)
    payload = receipt(bounded_repo)
    payload["candidates"][0]["reality"] = matched_reality(
        bounded_repo,
        match_status="contextual",
        relationship="same-observable",
    )
    with pytest.raises(morning_brief.BriefError, match="cannot masquerade"):
        generate(bounded_repo, payload)


def test_contested_exact_claim_forces_qualified_language(bounded_repo: Path) -> None:
    claim_id = "CLM-20260803-001"
    write_unassessed_claim(bounded_repo, claim_id)
    write_assessment(bounded_repo, claim_id, "contested", status="canonical_assessed")
    payload = receipt(bounded_repo)
    payload["candidates"][0]["reality"] = matched_reality(
        bounded_repo,
        confidence_effect="The assessment limits causal confidence.",
    )
    with pytest.raises(morning_brief.BriefError, match="contested exact match"):
        generate(bounded_repo, payload)
    payload["candidates"][0]["reality"]["confidence_effect"] = (
        "The observable remains contested, so no stronger causal language is warranted."
    )
    payload["candidates"][0]["confidence_boundary"] = (
        "The disputed element remains contested despite the recovered upstream report."
    )
    generate(bounded_repo, payload)


def test_challenged_exact_claim_cannot_render_as_settled_fact(bounded_repo: Path) -> None:
    claim_id = "CLM-20260803-001"
    write_unassessed_claim(bounded_repo, claim_id)
    write_assessment(bounded_repo, claim_id, "disconfirmed", status="canonical_assessed")
    payload = receipt(bounded_repo)
    payload["candidates"][0]["reality"] = matched_reality(
        bounded_repo,
        confidence_effect="The assessment is final.",
    )
    with pytest.raises(morning_brief.BriefError, match="challenged exact match"):
        generate(bounded_repo, payload)
    payload["candidates"][0]["reality"]["confidence_effect"] = (
        "The challenged formulation is disconfirmed and is not presented as settled fact."
    )
    payload["candidates"][0]["confidence_boundary"] = (
        "The challenged formulation is not supported by the controlling assessment."
    )
    generate(bounded_repo, payload)


def test_unmatched_observation_remains_eligible_and_verified_is_rejected(
    bounded_repo: Path,
) -> None:
    payload = receipt(bounded_repo)
    brief_path, _ = generate(bounded_repo, payload)
    assert "Candidate OBS-01" in brief_path.read_text(encoding="utf-8")
    payload = receipt(bounded_repo)
    payload["candidates"][0]["observation"] = "A verified event occurred."
    with pytest.raises(morning_brief.BriefError, match="cannot use verified"):
        generate(bounded_repo, payload, output_name="verified-rejected")


def test_reality_hash_mismatch_fails_and_generation_never_mutates_lattice(
    bounded_repo: Path,
) -> None:
    reality_root = write_unassessed_claim(bounded_repo)
    payload = receipt(bounded_repo)
    payload["candidates"][0]["reality"] = matched_reality(bounded_repo)
    protected = sorted(reality_root.rglob("*.json"))
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
    generate(bounded_repo, payload)
    assert {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected} == before
    payload = receipt(bounded_repo)
    payload["candidates"][0]["reality"] = matched_reality(bounded_repo)
    payload["candidates"][0]["reality"]["lattice_paths"][0]["sha256"] = "0" * 64
    with pytest.raises(morning_brief.BriefError, match="paths or hashes"):
        generate(bounded_repo, payload, output_name="bad-reality-hash")
    assert not (bounded_repo / "bad-reality-hash").exists()


def test_five_fixture_dry_pilot_proves_mechanics_not_utility(bounded_repo: Path) -> None:
    scenarios = json.loads((FIXTURES_ROOT / "pilot-cases.json").read_text(encoding="utf-8"))
    outputs: list[Path] = []
    for index, scenario in enumerate(scenarios, start=1):
        payload = receipt(bounded_repo, material_change=scenario["material_change"])
        if scenario["forecast_impact"] != payload["baseline"]["forecasts"][0]["impact"]:
            payload["baseline"]["forecasts"][0]["impact"] = scenario["forecast_impact"]
        if scenario["material_change"]:
            payload["candidates"][0]["impact"] = scenario["development_impact"]
            payload["morning_judgment"] = scenario["morning_judgment"]
            if scenario["forecast_impact"] == "unaffected":
                payload["candidates"][0]["forecast_refs"] = []
        outputs.append(generate(bounded_repo, payload, output_name=f"pilot-{index}")[0])
    assert len(outputs) == 5
    assert all(path.is_file() for path in outputs)


def test_receipt_20_is_rejected_without_migration(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    payload["schema_version"] = "2.0"
    payload["renderer_version"] = "2.0"
    with pytest.raises(morning_brief.BriefError, match="schema_version must be 2.1"):
        generate(bounded_repo, payload)


def test_related_observations_render_in_declared_order(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    attach_related(
        payload,
        "OBS-04",
        relationship="corroborates",
        provider="Corroborating Source",
        lineage="lineage-corroborating-4",
    )
    attach_related(
        payload,
        "OBS-05",
        relationship="qualifies",
        provider="Qualifying Source",
        lineage="lineage-qualifying-5",
    )
    attach_related(
        payload,
        "OBS-06",
        relationship="disputes",
        provider="Disputing Source",
        lineage="lineage-disputing-6",
    )
    payload["candidates"][0]["confidence_boundary"] = (
        "The disputed account remains contested despite the recovered sources."
    )
    brief_path, receipt_path = generate(bounded_repo, payload)
    body = brief_path.read_text(encoding="utf-8")
    assert body.index("**Corroboration:**") < body.index("**Qualification:**")
    assert body.index("**Qualification:**") < body.index("**Disagreement:**")
    assert "Corroborating Source" in body
    assert "Qualifying Source" in body
    assert "Disputing Source" in body
    stored = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert stored["candidates"][0]["related_observations"] == [
        {"candidate_id": "OBS-04", "relationship": "corroborates"},
        {"candidate_id": "OBS-05", "relationship": "qualifies"},
        {"candidate_id": "OBS-06", "relationship": "disputes"},
    ]


@pytest.mark.parametrize(
    ("relationship", "message"),
    (
        ("unknown", "invalid related-observation relationship"),
        ("same-observable", "invalid related-observation relationship"),
    ),
)
def test_unknown_related_relationship_is_rejected(
    bounded_repo: Path, relationship: str, message: str
) -> None:
    payload = receipt(bounded_repo)
    payload["candidates"][0]["related_observations"] = [
        {"candidate_id": "OBS-02", "relationship": relationship}
    ]
    with pytest.raises(morning_brief.BriefError, match=message):
        generate(bounded_repo, payload)


def test_missing_self_and_wrong_disposition_related_targets_are_rejected(
    bounded_repo: Path,
) -> None:
    payload = receipt(bounded_repo)
    payload["candidates"][0]["related_observations"] = [
        {"candidate_id": "OBS-99", "relationship": "qualifies"}
    ]
    with pytest.raises(morning_brief.BriefError, match="missing or has wrong disposition"):
        generate(bounded_repo, payload, output_name="missing-related")

    payload = receipt(bounded_repo)
    payload["candidates"][0]["related_observations"] = [
        {"candidate_id": "OBS-01", "relationship": "qualifies"}
    ]
    with pytest.raises(morning_brief.BriefError, match="cannot reference itself"):
        generate(bounded_repo, payload, output_name="self-related")

    payload = receipt(bounded_repo)
    payload["candidates"][0]["related_observations"] = [
        {"candidate_id": "OBS-02", "relationship": "qualifies"}
    ]
    with pytest.raises(morning_brief.BriefError, match="wrong disposition"):
        generate(bounded_repo, payload, output_name="wrong-related-disposition")


def test_related_candidates_cannot_nest_or_remain_unreferenced(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    related = attach_related(payload)
    related["related_observations"] = [
        {"candidate_id": "OBS-02", "relationship": "qualifies"}
    ]
    with pytest.raises(morning_brief.BriefError, match="cannot nest relationships"):
        generate(bounded_repo, payload, output_name="nested-related")

    payload = receipt(bounded_repo)
    related = attach_related(payload)
    payload["candidates"][0]["related_observations"] = []
    with pytest.raises(morning_brief.BriefError, match="referenced exactly once"):
        generate(bounded_repo, payload, output_name="orphan-related")


def test_related_candidate_cannot_be_reused_across_selected_stories(
    bounded_repo: Path,
) -> None:
    payload = receipt(bounded_repo)
    attach_related(payload)
    second = candidate(
        "OBS-05",
        provider="Second Selected Source",
        lineage="lineage-selected-5",
        disposition="included",
    )
    second["related_observations"] = [
        {"candidate_id": "OBS-04", "relationship": "qualifies"}
    ]
    payload["candidates"].append(second)
    payload["selected_development_ids"].append("OBS-05")
    refresh_coverage_counts(payload)
    with pytest.raises(morning_brief.BriefError, match="related observation is reused"):
        generate(bounded_repo, payload)


@pytest.mark.parametrize("mutation", ("stale", "missing"))
def test_related_candidate_requires_fresh_upstream(
    bounded_repo: Path, mutation: str
) -> None:
    payload = receipt(bounded_repo)
    related = attach_related(payload)
    if mutation == "stale":
        related["upstream"]["freshness"] = "stale"
        message = "must be fresh"
    else:
        related["upstream"] = None
        message = "requires recovered upstream evidence"
    with pytest.raises(morning_brief.BriefError, match=message):
        generate(bounded_repo, payload)


def test_corroboration_requires_independent_lineage(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    attach_related(
        payload,
        relationship="corroborates",
        lineage=payload["candidates"][0]["upstream"]["lineage_root"],
    )
    with pytest.raises(morning_brief.BriefError, match="shares upstream lineage"):
        generate(bounded_repo, payload)


def test_related_entries_cannot_inflate_provider_or_lineage_counts(
    bounded_repo: Path,
) -> None:
    payload = receipt(bounded_repo)
    attach_related(
        payload,
        provider=payload["candidates"][0]["upstream"]["provider"],
        lineage="lineage-related-distinct-4",
    )
    assert payload["coverage"]["upstream_sources_reviewed"] == 3
    assert payload["coverage"]["lineage_roots_reviewed"] == 4
    generate(bounded_repo, payload)
    payload["coverage"]["upstream_sources_reviewed"] = 4
    with pytest.raises(morning_brief.BriefError, match="distinct upstream research"):
        generate(bounded_repo, payload, output_name="inflated-coverage")


def test_disagreement_requires_qualified_selected_confidence(bounded_repo: Path) -> None:
    payload = receipt(bounded_repo)
    attach_related(payload, relationship="disputes")
    with pytest.raises(morning_brief.BriefError, match="qualified confidence boundary"):
        generate(bounded_repo, payload)
    payload["candidates"][0]["confidence_boundary"] = (
        "The related source disputes the selected account."
    )
    generate(bounded_repo, payload)


def test_related_observations_do_not_consume_development_slots_or_pressure_forecasts(
    bounded_repo: Path,
) -> None:
    payload = receipt(bounded_repo)
    for index in range(4, 10):
        attach_related(
            payload,
            f"OBS-{index:02d}",
            provider=f"Related Source {index}",
            lineage=f"lineage-related-{index}",
        )
    brief_path, stored_path = generate(bounded_repo, payload)
    stored = json.loads(stored_path.read_text(encoding="utf-8"))
    assert stored["selected_development_ids"] == ["OBS-01"]
    assert stored["baseline"]["forecasts"][0]["impact"] == "strengthens"
    assert brief_path.read_text(encoding="utf-8").count("**Qualification:**") == 6


def test_related_reality_state_remains_candidate_specific(bounded_repo: Path) -> None:
    claim_id = "CLM-20260803-001"
    write_unassessed_claim(bounded_repo, claim_id)
    write_assessment(bounded_repo, claim_id, "contested", status="canonical_assessed")
    payload = receipt(bounded_repo)
    related = attach_related(payload)
    related["observation"] = "A reported bounded observable remains contested."
    related["confidence_boundary"] = "The related observable remains contested."
    related["reality"] = matched_reality(
        bounded_repo,
        confidence_effect="The related observable remains contested and cannot settle the story.",
    )
    brief_path, _ = generate(bounded_repo, payload)
    body = brief_path.read_text(encoding="utf-8")
    related_note = next(line for line in body.splitlines() if line.startswith("- `OBS-04`"))
    assert "CLM-20260803-001" in related_note
    assert "contested" in related_note
    selected_note = next(line for line in body.splitlines() if line.startswith("- `OBS-01`"))
    assert "not-in-lattice" in selected_note


def test_zero_judgment_baseline_is_disclosed_truthfully(bounded_repo: Path) -> None:
    judgment = (
        bounded_repo
        / "narrative-geopolitics"
        / "work"
        / "daily"
        / JUDGMENT_DATE
        / "judgment.md"
    )
    judgment.unlink()
    payload = receipt(bounded_repo)
    for row in payload["candidates"]:
        row["model_refs"] = []
    payload["watch"][0]["source_refs"] = [HOOK_ID]
    brief_path, _ = generate(bounded_repo, payload)
    body = brief_path.read_text(encoding="utf-8")
    assert "`0` valid judgment(s), `1` accountable open forecast(s)" in body
    assert "Baseline: `0` valid judgment(s); `1` accountable open forecast(s)." in body


def test_long_forecast_administration_does_not_block_render(
    bounded_repo: Path,
) -> None:
    for index in range(12):
        add_accountable_forecast(
            bounded_repo,
            f"NG-20260802-F{index + 10:02d}",
            review_date="2026-08-02",
            claim=(
                "A deliberately long due-only fixture claim remains open and "
                "retains enough words to exercise accumulated forecast "
                "administration without becoming a material development."
            ),
        )
    payload = receipt(bounded_repo)
    for row in payload["baseline"]["forecasts"]:
        if row["hook_id"] != HOOK_ID:
            row["impact"] = "unaffected"

    brief_path, _ = generate(bounded_repo, payload, output_name="long-forecast-admin")
    body = brief_path.read_text(encoding="utf-8")

    assert "## Forecast Pressure" in body
    assert "### Due, unpressured" in body
    assert "NG-20260802-F21" in body

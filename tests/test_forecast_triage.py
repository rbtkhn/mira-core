from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


triage = load_module("forecast_triage_tests", REPO_ROOT / "scripts" / "triage_forecast_ledger.py")
bootstrap = load_module("forecast_bootstrap_tests", REPO_ROOT / "scripts" / "bootstrap_daily_run.py")
sync = load_module("forecast_sync_tests", REPO_ROOT / "scripts" / "sync_forecast_ledger.py")
ledger = load_module("forecast_ledger_tests", REPO_ROOT / "scripts" / "forecast_ledger.py")


def ledger_text(review_date: str = "2026-07-10", accountable: str = "yes") -> str:
    return f"""# Ledger

| Hook ID | Date | Crisis Object | Claim | Probability Band | Review Date | Source Run | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260707-F01` | `2026-07-07` | Object | Bounded claim | `likely` | `{review_date}` | [run](x) | `open` |

## Accountability Triage

| Hook ID | Authored No Later Than | Timing Provenance | Forecast Type | Resolution Status | Accountable | Review Note |
| --- | --- | --- | --- | --- | --- | --- |
| `NG-20260707-F01` | `2026-07-08` | `git_commit_upper_bound` | `ex_ante` | `open` | `{accountable}` | Prospective review. |
"""


def ledger_with_missing_and_overdue_rows() -> str:
    return """# Ledger

| Hook ID | Date | Crisis Object | Claim | Probability Band | Review Date | Source Run | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260707-F01` | `2026-07-07` | Object | Missing triage claim | `likely` | `2026-07-20` | [run](x) | `open` |
| `NG-20260708-F01` | `2026-07-08` | Object | Overdue claim | `likely` | `2026-07-10` | [run](y) | `open` |

## Accountability Triage

| Hook ID | Authored No Later Than | Timing Provenance | Forecast Type | Resolution Status | Accountable | Review Note |
| --- | --- | --- | --- | --- | --- | --- |
| `NG-20260708-F01` | `2026-07-08` | `git_commit_upper_bound` | `ex_ante` | `open` | `yes` | Prospective review. |
"""


def test_accountable_ex_ante_forecast_passes_before_due_date() -> None:
    text = ledger_text()
    failures = triage.validate_triage(
        triage.parse_entries(text), triage.parse_triage(text), "2026-07-09"
    )
    assert failures == []


def test_resolved_accountable_forecast_requires_verification_packet() -> None:
    text = ledger_text().replace("`open`", "`hit`")
    entries = triage.parse_entries(text)
    rows = triage.parse_triage(text)
    failures = triage.validate_triage(entries, rows, "2026-08-01")
    assert "resolved accountable forecast missing verification packet: NG-20260707-F01" in failures


def test_resolved_accountable_forecast_accepts_verification_reference() -> None:
    text = ledger_text().replace("`open`", "`hit`").replace(
        "Prospective review.", "Prospective review. VER-20260710-01"
    )
    assert triage.validate_triage(triage.parse_entries(text), triage.parse_triage(text), "2026-08-01") == []


def test_overdue_accountable_forecast_fails() -> None:
    text = ledger_text(review_date="2026-07-09")
    failures = triage.validate_triage(
        triage.parse_entries(text), triage.parse_triage(text), "2026-07-09"
    )
    assert failures == ["overdue accountable forecast remains open: NG-20260707-F01"]


def test_non_ex_ante_row_cannot_be_accountable() -> None:
    text = ledger_text().replace("`ex_ante`", "`retrospective_hypothesis`")
    failures = triage.validate_triage(
        triage.parse_entries(text), triage.parse_triage(text), "2026-07-09"
    )
    assert "only ex_ante forecasts may be accountable: NG-20260707-F01" in failures


def test_invalid_forecast_classification_is_rejected() -> None:
    text = ledger_text().replace("`ex_ante`", "`verification_gated`")
    failures = triage.validate_triage(
        triage.parse_entries(text), triage.parse_triage(text), "2026-07-09"
    )
    assert "invalid forecast type for NG-20260707-F01: verification_gated" in failures


def test_status_migration_preserves_non_status_entry_fields() -> None:
    text = ledger_text().replace(
        "`ex_ante` | `open` | `yes`", "`ex_ante` | `mixed` | `yes`"
    )
    before = ledger.parse_entries(text)[0]

    after = ledger.parse_entries(ledger.align_entry_statuses(text))[0]

    assert after.status == "mixed"
    assert before.hook_id == after.hook_id
    assert before.run_date == after.run_date
    assert before.crisis_object == after.crisis_object
    assert before.claim == after.claim
    assert before.probability_band == after.probability_band
    assert before.review_date == after.review_date
    assert before.source_run == after.source_run


def test_unresolvable_is_allowed_without_forcing_outcome() -> None:
    text = ledger_text(accountable="no").replace(
        "`open`", "`unresolvable_with_authorized_evidence`"
    )
    failures = triage.validate_triage(
        triage.parse_entries(text), triage.parse_triage(text), "2026-07-20"
    )
    assert failures == []


def test_entry_and_triage_status_must_match() -> None:
    text = ledger_text().replace("`open` | `yes`", "`hit` | `yes`")
    failures = triage.validate_triage(
        triage.parse_entries(text), triage.parse_triage(text), "2026-07-09"
    )
    assert (
        "forecast status mismatch for NG-20260707-F01: entry=open triage=hit"
        in failures
    )


def test_sync_inserts_entry_before_triage_and_triage_row_in_triage_table() -> None:
    text = ledger_text()
    entry = (
        "| `NG-20260708-F01` | `2026-07-08` | Object | Claim | `likely` | "
        "`2026-07-20` | [run](y) | `open` |"
    )
    triage_row = (
        "| `NG-20260708-F01` | `2026-07-08` | `runtime_date` | `ex_ante` | "
        "`open` | `yes` | Prospective. |"
    )

    updated = sync.insert_rows(text, [entry], [triage_row])
    before, _, after = updated.partition("## Accountability Triage")

    assert entry in before
    assert triage_row not in before
    assert triage_row in after
    assert entry not in after


def test_live_registration_requires_explicit_metadata() -> None:
    args = type(
        "Args",
        (),
        {
            "retro": False,
            "authored_at": "",
            "timing_provenance": "",
            "forecast_type": None,
            "accountable": None,
            "review_note": "",
        },
    )()

    try:
        sync.registration_metadata(args)
    except ValueError as error:
        assert "explicit registration metadata" in str(error)
    else:
        raise AssertionError("live registration metadata was not required")


def test_due_review_carry_forward_excludes_non_accountable_rows(monkeypatch) -> None:
    text = """# Ledger
| Hook ID | Date | Crisis Object | Claim | Probability Band | Review Date | Source Run | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260707-F01` | `2026-07-07` | Object | Accountable claim | `likely` | `2026-07-10` | [run](x) | `open` |
| `NG-20260630-F01` | `2026-06-30` | Object | Retrospective claim | `likely` | `2026-07-10` | [run](x) | `open` |
| `NG-20260707-F01` | `2026-07-08` | `git_commit_upper_bound` | `ex_ante` | `open` | `yes` | Prospective. |
| `NG-20260630-F01` | `2026-07-07` | `git_commit_upper_bound` | `retrospective_hypothesis` | `excluded_retrospective` | `no` | Retrospective. |
"""
    monkeypatch.setattr(bootstrap, "load_ledger_text", lambda: text)

    hooks = bootstrap.extract_due_review_hooks("2026-07-20")

    assert [hook["hook_id"] for hook in hooks] == ["NG-20260707-F01"]


def test_due_review_link_is_rebased_for_daily_forecast() -> None:
    text = "# Forecast\n\n## Hooks\n"
    hooks = [
        {
            "hook_id": "NG-20260707-F01",
            "hook_date": "2026-07-07",
            "crisis_object": "Object",
            "claim": "Claim",
            "band": "likely",
            "review_date": "2026-07-10",
            "source_label": "2026-07-07",
            "source_link": "../daily/2026-07-07/forecast.md",
        }
    ]

    updated = bootstrap.inject_due_review_hooks(text, hooks)

    assert "[2026-07-07](../2026-07-07/forecast.md)" in updated
    assert "../daily/2026-07-07/forecast.md" not in updated


def test_triage_plan_reports_missing_rows_and_overdue_reviews_without_mutation() -> None:
    text = ledger_with_missing_and_overdue_rows()

    plan = triage.build_plan(text, "2026-07-20")

    assert plan["authority_effect"] == "none"
    assert plan["summary"] == {
        "missing_triage_row_count": 1,
        "overdue_accountable_forecast_count": 1,
        "action_count": 2,
    }
    assert plan["missing_triage_rows"][0]["hook_id"] == "NG-20260707-F01"
    assert (
        "| `NG-20260707-F01` | `2026-07-07` | "
        "`ledger_entry_run_date; human review required` | `ex_ante` | "
        "`open` | `yes` |"
    ) in plan["missing_triage_rows"][0]["suggested_row"]
    assert plan["overdue_accountable_forecasts"][0]["hook_id"] == "NG-20260708-F01"
    assert "hit" in plan["overdue_accountable_forecasts"][0]["allowed_dispositions"]


def test_triage_plan_json_cli_is_parseable_and_authority_free(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    ledger_path = tmp_path / "forecast-ledger.md"
    before = ledger_with_missing_and_overdue_rows()
    ledger_path.write_text(before, encoding="utf-8")
    monkeypatch.setattr(triage, "LEDGER_PATH", ledger_path)

    triage.main(["plan", "--as-of", "2026-07-20", "--json"])

    output = json.loads(capsys.readouterr().out)
    assert output["mode"] == "forecast-triage-plan"
    assert output["authority_effect"] == "none"
    assert output["summary"]["action_count"] == 2
    assert ledger_path.read_text(encoding="utf-8") == before


def test_triage_validate_json_cli_preserves_failure_exit(tmp_path: Path, monkeypatch, capsys) -> None:
    ledger_path = tmp_path / "forecast-ledger.md"
    ledger_path.write_text(ledger_with_missing_and_overdue_rows(), encoding="utf-8")
    monkeypatch.setattr(triage, "LEDGER_PATH", ledger_path)

    try:
        triage.main(["validate", "--as-of", "2026-07-20", "--json"])
    except SystemExit as error:
        assert error.code == 1
    else:
        raise AssertionError("validate did not fail on ledger triage debt")

    output = json.loads(capsys.readouterr().out)
    assert output["mode"] == "forecast-triage-validate"
    assert output["authority_effect"] == "none"
    assert "missing triage row: NG-20260707-F01" in output["failures"]

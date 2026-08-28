from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "report_intake_outcomes.py"
SPEC = importlib.util.spec_from_file_location("intake_outcome_tests", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def receipt(identity: str, disposition: str, **metrics: int) -> dict:
    values = {
        "disposition": disposition,
        "attempted_sources": 1,
        "warning_sources": 0,
        "warning_events": 0,
        "duplicate_stops": 0,
        "correction_signal_sources": 0,
        "correction_signal_events": 0,
        "successful_landings": 0,
        "failed_attempts": 0,
    }
    values.update(metrics)
    return {
        "status": disposition,
        "preflight": {
            "sources": [{"source_identity": identity}],
            "outcome_metrics": values,
        },
        "outcome_metrics": values,
    }


def test_aggregate_counts_outcomes_and_terminal_retries() -> None:
    receipts = [
        ("01.json", receipt("youtube:one", "preflight-only", warning_events=1)),
        ("02.json", receipt("youtube:one", "failed", failed_attempts=1)),
        ("03.json", receipt("youtube:one", "landed", successful_landings=1)),
        (
            "04.json",
            receipt(
                "youtube:two",
                "duplicate-prevented",
                duplicate_stops=1,
                warning_events=1,
            ),
        ),
    ]

    summary = MODULE.aggregate_receipts(receipts)

    assert summary["receipt_count"] == 4
    assert summary["unique_source_identities"] == 2
    assert summary["totals"]["successful_landings"] == 1
    assert summary["totals"]["duplicate_stops"] == 1
    assert summary["totals"]["attempted_sources"] == 3
    assert summary["nonterminal_totals"]["attempted_sources"] == 1
    assert summary["nonterminal_totals"]["warning_events"] == 1
    assert summary["retry_source_count"] == 1
    assert summary["successful_after_retry_count"] == 1


def test_preflight_then_landing_is_not_a_retry() -> None:
    summary = MODULE.aggregate_receipts(
        [
            ("01.json", receipt("youtube:one", "preflight-only")),
            ("02.json", receipt("youtube:one", "landed", successful_landings=1)),
        ]
    )
    assert summary["retry_source_count"] == 0
    assert summary["totals"]["attempted_sources"] == 1
    assert summary["nonterminal_totals"]["attempted_sources"] == 1


def test_source_baseline_marks_unobservable_attempt_metrics_unavailable(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source-example.md"
    source.write_text(
        """---
source_identity: "youtube:one"
date_basis: operator-supplied
routing_basis: explicit-host
source_form_basis: inferred
title_aliases: "Operator title"
metadata_warnings: "operator-title-differs-from-transcript-title"
---

## Transcript
""",
        encoding="utf-8",
    )

    baseline = MODULE.source_baseline([tmp_path])

    assert baseline["observed_metrics"]["successful_landings"] == 1
    assert baseline["observed_metrics"]["correction_signal_sources"] == 1
    assert baseline["date_basis"] == {"operator-supplied": 1}
    assert "duplicate_stops" in baseline["unavailable_attempt_metrics"]
    assert "duplicate_stops" not in baseline["observed_metrics"]


def test_redacted_summary_omits_retry_identities_but_keeps_counts() -> None:
    receipts = [
        ("01.json", receipt("youtube:one", "failed", failed_attempts=1)),
        ("02.json", receipt("youtube:one", "landed", successful_landings=1)),
    ]

    summary = MODULE.aggregate_receipts(receipts, redact_identities=True)

    assert summary["identity_disclosure"] == "redacted"
    assert "retry_source_identities" not in summary
    assert summary["retry_source_count"] == 1
    assert summary["successful_after_retry_count"] == 1
    assert summary["terminal_receipt_count"] == 2
    assert summary["nonterminal_receipt_count"] == 0


def test_default_summary_retains_retry_identities() -> None:
    summary = MODULE.aggregate_receipts(
        [
            ("01.json", receipt("youtube:one", "failed", failed_attempts=1)),
            ("02.json", receipt("youtube:one", "landed", successful_landings=1)),
        ]
    )

    assert summary["identity_disclosure"] == "included"
    assert summary["retry_source_identities"] == ["youtube:one"]


def test_preflight_unavailable_failure_is_counted_without_identity() -> None:
    payload = receipt("", "failed", attempted_sources=0, failed_attempts=1)
    payload["measurement_scope"] = "preflight-unavailable"

    summary = MODULE.aggregate_receipts([("failure.json", payload)])

    assert summary["terminal_receipt_count"] == 1
    assert summary["unattributed_failed_attempts"] == 1
    assert summary["unique_source_identities"] == 0


@pytest.mark.parametrize(
    ("field", "value"),
    (("attempted_sources", -1), ("warning_events", True), ("failed_attempts", "1")),
)
def test_invalid_metric_values_fail_closed(field: str, value: object) -> None:
    payload = receipt("youtube:one", "failed", failed_attempts=1)
    payload["outcome_metrics"][field] = value
    payload["preflight"]["outcome_metrics"][field] = value

    with pytest.raises(ValueError, match=f"invalid {field}"):
        MODULE.aggregate_receipts([("bad.json", payload)])


def test_duplicate_receipt_paths_fail_closed() -> None:
    payload = receipt("youtube:one", "failed", failed_attempts=1)
    with pytest.raises(ValueError, match="duplicate receipt paths"):
        MODULE.aggregate_receipts([("same.json", payload), ("same.json", payload)])


def test_terminal_receipt_requires_identity_or_explicit_unavailable_scope() -> None:
    payload = receipt("", "failed", failed_attempts=1)
    with pytest.raises(ValueError, match="lacks source identity"):
        MODULE.aggregate_receipts([("failure.json", payload)])


def test_repository_output_requires_redaction(monkeypatch, tmp_path: Path) -> None:
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(
        json.dumps(receipt("youtube:one", "landed", successful_landings=1)),
        encoding="utf-8",
    )
    output = REPO_ROOT / "intake-summary-test.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "report_intake_outcomes.py",
            str(receipt_path),
            "--json",
            "--output",
            str(output),
        ],
    )

    with pytest.raises(SystemExit, match="requires --redact-identities"):
        MODULE.main()

    assert not output.exists()

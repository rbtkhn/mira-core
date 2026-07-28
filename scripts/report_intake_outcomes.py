from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


TERMINAL_DISPOSITIONS = {"landed", "duplicate-prevented", "failed"}
METRIC_FIELDS = (
    "attempted_sources",
    "warning_sources",
    "warning_events",
    "duplicate_stops",
    "correction_signal_sources",
    "correction_signal_events",
    "successful_landings",
    "failed_attempts",
)


def load_receipt(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"receipt is not a JSON object: {path}")
    return payload


def receipt_preflight(payload: dict[str, Any]) -> dict[str, Any]:
    nested = payload.get("preflight")
    if isinstance(nested, dict):
        return nested
    return payload if isinstance(payload.get("sources"), list) else {}


def receipt_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    metrics = payload.get("outcome_metrics")
    if isinstance(metrics, dict):
        return metrics
    preflight = receipt_preflight(payload)
    nested = preflight.get("outcome_metrics")
    return nested if isinstance(nested, dict) else {}


def source_identities(payload: dict[str, Any]) -> list[str]:
    preflight = receipt_preflight(payload)
    identities = []
    for row in preflight.get("sources", []):
        if isinstance(row, dict) and str(row.get("source_identity", "")).strip():
            identities.append(str(row["source_identity"]).strip())
    return sorted(set(identities))


def aggregate_receipts(receipts: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    totals = Counter({field: 0 for field in METRIC_FIELDS})
    terminal_attempts: Counter[str] = Counter()
    seen_terminal: set[str] = set()
    successful_after_retry: set[str] = set()
    dispositions: Counter[str] = Counter()
    identities: set[str] = set()

    for _, payload in receipts:
        metrics = receipt_metrics(payload)
        disposition = str(metrics.get("disposition") or payload.get("status") or "unknown")
        dispositions[disposition] += 1
        for field in METRIC_FIELDS:
            value = metrics.get(field, 0)
            if isinstance(value, int) and not isinstance(value, bool):
                totals[field] += value

        receipt_ids = source_identities(payload)
        identities.update(receipt_ids)
        if disposition in TERMINAL_DISPOSITIONS:
            for identity in receipt_ids:
                terminal_attempts[identity] += 1
                if disposition == "landed" and identity in seen_terminal:
                    successful_after_retry.add(identity)
                seen_terminal.add(identity)

    retry_sources = sorted(
        identity for identity, count in terminal_attempts.items() if count > 1
    )
    return {
        "schema": "intake-outcome-summary-v1",
        "receipt_count": len(receipts),
        "unique_source_identities": len(identities),
        "dispositions": dict(sorted(dispositions.items())),
        "totals": dict(totals),
        "retry_source_count": len(retry_sources),
        "successful_after_retry_count": len(successful_after_retry),
        "retry_source_identities": retry_sources,
        "measurement_note": (
            "Retry metrics use repeated terminal receipts for the same canonical "
            "source identity. Preflight-only and dry-run receipts do not count as retries."
        ),
    }


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fields: dict[str, str] = {}
    for raw_line in parts[1].splitlines():
        if ":" not in raw_line or raw_line[:1].isspace():
            continue
        key, value = raw_line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def split_signals(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def source_baseline(paths: list[Path]) -> dict[str, Any]:
    source_files: list[Path] = []
    for path in paths:
        if path.is_dir():
            source_files.extend(sorted(path.glob("source-*.md")))
        elif path.is_file():
            source_files.append(path)
    source_files = sorted(set(source_files))

    date_basis: Counter[str] = Counter()
    routing_basis: Counter[str] = Counter()
    source_form_basis: Counter[str] = Counter()
    correction_sources = 0
    warning_sources = 0
    warning_events = 0
    alias_sources = 0
    alias_events = 0
    identities: set[str] = set()

    for path in source_files:
        fields = parse_frontmatter(path)
        if fields.get("source_identity"):
            identities.add(fields["source_identity"])
        date_basis[fields.get("date_basis") or "missing"] += 1
        routing_basis[fields.get("routing_basis") or "missing"] += 1
        source_form_basis[fields.get("source_form_basis") or "missing"] += 1
        warnings = split_signals(fields.get("metadata_warnings", ""))
        aliases = split_signals(fields.get("title_aliases", ""))
        warning_sources += bool(warnings)
        warning_events += len(warnings)
        alias_sources += bool(aliases)
        alias_events += len(aliases)
        correction_sources += bool(warnings or aliases)

    return {
        "schema": "intake-source-baseline-v1",
        "measurement_basis": "reconstructed-from-landed-source-frontmatter",
        "source_count": len(source_files),
        "unique_source_identities": len(identities),
        "observed_metrics": {
            "successful_landings": len(source_files),
            "metadata_warning_sources": warning_sources,
            "metadata_warning_events": warning_events,
            "title_alias_sources": alias_sources,
            "title_alias_events": alias_events,
            "correction_signal_sources": correction_sources,
        },
        "date_basis": dict(sorted(date_basis.items())),
        "routing_basis": dict(sorted(routing_basis.items())),
        "source_form_basis": dict(sorted(source_form_basis.items())),
        "unavailable_attempt_metrics": [
            "duplicate_stops",
            "failed_attempts",
            "retry_source_count",
            "successful_after_retry_count"
        ],
        "measurement_note": (
            "This baseline reconstructs landed-source outcomes from archive "
            "frontmatter. Attempt-level metrics are unavailable because these "
            "landings predate saved JSON outcome receipts; unavailable values "
            "must not be interpreted as zero."
        ),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    if summary.get("schema") == "intake-source-baseline-v1":
        metrics = summary["observed_metrics"]
        return "\n".join(
            [
                "# Intake Source Baseline",
                "",
                f"- Landed sources: **{metrics['successful_landings']}**",
                f"- Unique source identities: **{summary['unique_source_identities']}**",
                f"- Metadata warning sources: **{metrics['metadata_warning_sources']}**",
                f"- Title alias sources: **{metrics['title_alias_sources']}**",
                f"- Correction-signal sources: **{metrics['correction_signal_sources']}**",
                "",
                "Unavailable attempt metrics: "
                + ", ".join(f"`{item}`" for item in summary["unavailable_attempt_metrics"])
                + ".",
                "",
                summary["measurement_note"],
            ]
        ).rstrip() + "\n"
    totals = summary["totals"]
    lines = [
        "# Intake Outcome Summary",
        "",
        f"- Receipts: **{summary['receipt_count']}**",
        f"- Unique source identities: **{summary['unique_source_identities']}**",
        f"- Successful landings: **{totals['successful_landings']}**",
        f"- Duplicate stops: **{totals['duplicate_stops']}**",
        f"- Warning events: **{totals['warning_events']}**",
        f"- Correction signals: **{totals['correction_signal_events']}**",
        f"- Failed attempts: **{totals['failed_attempts']}**",
        f"- Sources with terminal retries: **{summary['retry_source_count']}**",
        f"- Successful after retry: **{summary['successful_after_retry_count']}**",
        "",
        summary["measurement_note"],
        "",
        "## Dispositions",
        "",
        "| Disposition | Receipts |",
        "| --- | ---: |",
    ]
    for disposition, count in summary["dispositions"].items():
        lines.append(f"| `{disposition}` | {count} |")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate saved JSON intake receipts into bounded outcome metrics."
    )
    parser.add_argument("receipts", nargs="*", type=Path)
    parser.add_argument(
        "--source-baseline",
        nargs="+",
        type=Path,
        help="Reconstruct landed-source metrics from source files or directories.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if bool(args.receipts) == bool(args.source_baseline):
        raise SystemExit("provide receipt paths or --source-baseline, but not both")
    if args.source_baseline:
        summary = source_baseline(args.source_baseline)
    else:
        receipts = [(path.as_posix(), load_receipt(path)) for path in args.receipts]
        summary = aggregate_receipts(receipts)
    rendered = json.dumps(summary, indent=2) + "\n" if args.json else render_markdown(summary)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"Wrote {args.output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

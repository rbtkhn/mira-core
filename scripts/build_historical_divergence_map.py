"""Build a bounded cross-voice historical-analogy divergence report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--include-backtest", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    functions = {item["voice"]: item["analytical_function"] for item in payload.get("characterizations", [])}
    occurrences: dict[str, dict[str, list[dict]]] = {}
    selected_records = list(payload.get("records", []))
    if args.include_backtest:
        selected_records.extend(payload.get("backtest", {}).get("records", []))
    for record in selected_records:
        for voice in record.get("voices", []):
            occurrences.setdefault(record["reference_id"], {}).setdefault(voice, []).append(record)

    comparisons = []
    for reference_id, by_voice in sorted(occurrences.items()):
        if len(by_voice) < 2:
            continue
        voice_functions = {voice: functions.get(voice, "other-review-required") for voice in sorted(by_voice)}
        distinct_functions = sorted(set(voice_functions.values()))
        evidence = []
        for voice in sorted(by_voice):
            for record in sorted(by_voice[voice], key=lambda item: item["occurrence_id"]):
                evidence.append({
                    "voice": voice,
                    "analytical_function": voice_functions[voice],
                    "occurrence_id": record["occurrence_id"],
                    "source_id": record["source_id"],
                    "archive_path": record["archive_path"],
                    "date": record.get("date", ""),
                    "quote": record.get("quote", ""),
                    "mechanisms": record.get("mechanism_suggestions", []),
                    "attribution_confidence": record.get("attribution_confidence", "unknown"),
                })
        comparisons.append({
            "reference_id": reference_id,
            "reference": next(iter(next(iter(by_voice.values()))))["reference"],
            "voices": sorted(by_voice),
            "voice_functions": voice_functions,
            "comparison": "same-topic-different-function" if len(distinct_functions) > 1 else "same-topic-same-function",
            "occurrence_ids": sorted(record["occurrence_id"] for records in by_voice.values() for record in records),
            "archive_paths": sorted({record["archive_path"] for records in by_voice.values() for record in records}),
            "evidence": evidence,
        })

    report = {
        "run_id": payload.get("run_id"),
        "source_set": payload.get("receipts", []),
        "voices": payload.get("voices", []),
        "method": "Compare references shared by at least two selected voices; distinguish repeated topic from repeated analytical function.",
        "includes_backtest": args.include_backtest,
        "backtest_window": payload.get("backtest", {}).get("dates", []) if args.include_backtest else [],
        "comparisons": comparisons,
        "summary": {
            "shared_reference_count": len(comparisons),
            "same_topic_different_function": sum(item["comparison"] == "same-topic-different-function" for item in comparisons),
            "same_topic_same_function": sum(item["comparison"] == "same-topic-same-function" for item in comparisons),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = [
        f"# Historical-analogy divergence map — `{report['run_id']}`",
        "",
        report["method"],
        "",
        f"Shared references: `{report['summary']['shared_reference_count']}`; different-function comparisons: `{report['summary']['same_topic_different_function']}`; same-function comparisons: `{report['summary']['same_topic_same_function']}`.",
        "",
    ]
    for item in comparisons:
        markdown.extend([
            f"## `{item['reference_id']}` — {item['reference']}",
            "",
            f"- Comparison: `{item['comparison']}`",
            f"- Voice functions: `{json.dumps(item['voice_functions'], ensure_ascii=False)}`",
            f"- Occurrences: `{len(item['occurrence_ids'])}`",
            "",
        ])
        for evidence in item["evidence"]:
            markdown.extend([
                f"### `{evidence['voice']}` — `{evidence['date']}`",
                "",
                f"- Function: `{evidence['analytical_function']}`",
                f"- Attribution: `{evidence['attribution_confidence']}`",
                f"- Source: `{evidence['archive_path']}`",
                f"- Mechanisms: `{json.dumps(evidence['mechanisms'], ensure_ascii=False)}`",
                f"- Quote: {evidence['quote']}",
                "",
            ])
    args.output.with_suffix(".md").write_text("\n".join(markdown), encoding="utf-8")
    print(f"Published {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

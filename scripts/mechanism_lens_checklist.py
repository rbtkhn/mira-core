#!/usr/bin/env python3
"""Generate a fillable Mechanism Lens Markdown worksheet."""

from __future__ import annotations

import argparse
from datetime import date


DOMAINS = [
    "Air",
    "Sea / Odessa",
    "Ground",
    "Logistics",
    "Diplomacy",
    "Escalation",
]

VOICE_FUNCTIONS = [
    "operational mechanism",
    "decisive-war / end-state theory",
    "grand-strategy / proxy-war structure",
    "escalation-control / attribution frame",
    "other",
]

SYNTHESIS_USES = [
    "updates existing narrative arc",
    "introduces new mechanism",
    "confirms repeated mechanism",
    "contradicts prior voice claim",
    "raises verification priority",
    "background only",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a fillable Mechanism Lens Markdown worksheet."
    )
    parser.add_argument("--start-date", required=True, help="Scope start date, YYYY-MM-DD.")
    parser.add_argument("--end-date", required=True, help="Scope end date, YYYY-MM-DD.")
    parser.add_argument("--voices", required=True, help="Comma-separated voice slugs.")
    parser.add_argument("--topic", required=True, help="Short topic label.")
    return parser.parse_args()


def validate_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"{label} must use YYYY-MM-DD: {value}") from exc


def checkbox_items(items: list[str]) -> str:
    return "\n".join(f"- [ ] {item}" for item in items)


def main() -> None:
    args = parse_args()
    start = validate_date(args.start_date, "--start-date")
    end = validate_date(args.end_date, "--end-date")
    if start > end:
        raise SystemExit("--start-date must be on or before --end-date")

    voices = [voice.strip() for voice in args.voices.split(",") if voice.strip()]
    if not voices:
        raise SystemExit("--voices must contain at least one non-empty voice slug")

    voice_rows = "\n".join(f"  - `{voice}`" for voice in voices)
    domains = checkbox_items(DOMAINS)
    functions = checkbox_items(VOICE_FUNCTIONS)
    synthesis_uses = checkbox_items(SYNTHESIS_USES)

    print(
        f"""# Mechanism Lens Worksheet

This worksheet maps source claims and mechanisms. It does not verify whether the
claims are true.

## Scope

- Topic: `{args.topic}`
- Start date: `{start.isoformat()}`
- End date: `{end.isoformat()}`
- Voices:
{voice_rows}

## Source Set

| Date | Voice | Host | Title | Archive Path | Routing State |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Voice Function

{functions}

Notes:

- 

## Actor Chain

Use for escalation-control or attribution-heavy sources:

actor -> enabling system -> instrument -> target -> intended pressure

- Actor:
- Enabling system:
- Instrument:
- Target:
- Intended pressure:

## Primary Domains

{domains}

Notes:

- 

## Claim Sentence

The source claims that ___ is happening because ___, which implies ___.

## Mechanism Chain

- Trigger:
- Instrument:
- Target:
- Intended effect:
- Claimed consequence:

## Forecast Or Implication

- Near-term forecast:
- Strategic implication:
- Confidence language:
- Date horizon:

## Verification Handle

- Observable indicator:
- Likely source type:
- Verification difficulty: low / medium / high
- Propaganda-mirror risk: low / medium / high

## Synthesis Use

{synthesis_uses}

Notes:

- 
"""
    )


if __name__ == "__main__":
    main()

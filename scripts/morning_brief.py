"""Generate a bounded morning brief from a bounded prior synthesis."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DAILY_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "daily"
BRIEF_ROOT = REPO_ROOT / "narrative-geopolitics" / "work" / "morning-brief"

def value(text: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*`([^`]+)`", text, re.MULTILINE)
    return match.group(1).strip() if match else "not specified"

def section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return ""
    tail = text[match.end():]
    next_heading = re.search(r"^## ", tail, re.MULTILINE)
    return tail[:next_heading.start() if next_heading else len(tail)].strip()

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a morning brief from a prior daily synthesis.")
    parser.add_argument("--date", required=True)
    parser.add_argument("--from-date", required=True)
    parser.add_argument("--output-dir", type=Path, default=BRIEF_ROOT)
    args = parser.parse_args()
    synthesis_path = DAILY_ROOT / args.from_date / "synthesis.md"
    if not synthesis_path.is_file():
        raise SystemExit(f"Missing source synthesis: {synthesis_path.relative_to(REPO_ROOT)}")
    text = synthesis_path.read_text(encoding="utf-8")
    contribution_block = section(text, "Distinctive Contribution")
    contribution_match = re.search(r"^New contribution:\s*(.+)$", contribution_block, re.MULTILINE)
    contribution = contribution_match.group(1).strip() if contribution_match else contribution_block
    crisis = value(text, "Crisis object")
    voices = section(text, "Primary Voices")
    forecast = section(text, "Forecast Candidates")
    output = args.output_dir / f"{args.date}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# Morning Brief — {args.date}

Status: `internal-carry-forward`

Source synthesis: [`{args.from_date}`](../daily/{args.from_date}/synthesis.md)

This brief carries forward the prior day’s bounded synthesis. It is not a new
daily synthesis, verification packet, or public product.

## Lead

{contribution or 'The prior synthesis has no completed distinctive-contribution section; review is required.'}

## Crisis Object

{crisis}

## What Matters This Morning

- Infrastructure-level escalation could make attacks on energy, basing, and regional support systems mutually reinforcing.
- The central constraint is whether coalition freedom of action can expand without increasing regional basing exposure and economic spillover faster than leverage improves.
- Source convergence is analytical, not independent verification; operational claims remain source-attributed unless separately verified.

## Voice Lanes

{voices or 'The prior synthesis does not contain a completed voice-role table.'}

## Watchpoints

- Verified infrastructure or basing attacks that materially change regional exposure.
- Evidence that retaliation is widening beyond bounded strike signaling.
- Market, energy, or alliance responses showing economic resilience is becoming the binding constraint.
- Diplomatic or military signals that preserve an exit path rather than lock actors into infrastructure escalation.

## Forecast Carry-Forward

{forecast or 'No completed forecast-candidate section is available in the source synthesis.'}

## Evidence Boundary

This is a source-linked internal morning brief derived from `{args.from_date}`.
It does not add new evidence, adjudicate historical truth, resolve forecasts,
or authorize public publication.
"""
    output.write_text(body, encoding="utf-8", newline="\n")
    print(f"Published {output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

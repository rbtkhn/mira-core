# Forecast / Review Hooks

Date: `2026-07-28`

Status: `live-intake-first`

Forecast rule: state a causal wager, not topic plus outcome. See [labels as analytical interfaces](../../../method/analytical-interfaces.md).

## Probability Bands

Use coarse bands, not false precision:

- `low`: roughly 10-30%
- `plausible`: roughly 30-45%
- `likely`: roughly 55-70%
- `high`: roughly 70-85%

## Due Review Hooks

Open forecast hooks whose review date is due on or before this run date:

| Hook ID | Original Date | Crisis Object | Claim | Probability Band | Review Date | Source Run |
| --- | --- | --- | --- | --- | --- | --- |
| `NG-20260707-F01` | `2026-07-07` | Lebanon-Hormuz linkage durability | Within 21 days, the Lebanon-Hormuz linkage will remain explicit in Iran-facing public bargaining, with no clean return to a narrow nuclear-only negotiation frame. | `likely` | `2026-07-28` | [2026-07-07](../2026-07-07/forecast.md) |

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Forecast Quality Gate

Forecast decision: `no new accountable forecast hook issued`.

The batch identifies competing escalation pathways, but not a sufficiently bounded observable and review window for a new accountable wager.

- The claim is observable inside the time boundary.
- The mechanism explains why this outcome should occur.
- The principal alternative could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency cites one `OPC-*` claim from the day's synthesis or `none`.

## Ledger Entries

Copy final hooks to `work/forecasts/forecast-ledger.md`.

An accountable resolution of `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` must cite a completed `VER-*` packet in its ledger review note.

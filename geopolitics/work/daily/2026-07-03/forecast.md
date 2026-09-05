# Forecast / Review Hooks

Date: `2026-07-03`

Status: `source-bounded complete`

Forecast rule: state a causal wager, not topic plus outcome. See [labels as analytical interfaces](../../../method/analytical-interfaces.md).

## Probability Bands

Use coarse bands, not false precision:

- `low`: roughly 10-30%
- `plausible`: roughly 30-45%
- `likely`: roughly 55-70%
- `high`: roughly 70-85%

## Due Review Hooks

No open ledger hooks are due on or before this run date.

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260703-F01` | By `2026-08-03`, public or source handling of the Iran MOU will more often describe renegotiation, coercive testing, or Plan B pressure than a stable holding pattern. | The day mechanism should remain visible if the source-bounded pressure is real rather than only rhetorical. | `plausible` | `2026-08-03` | Later synthesis, public posture, or archive intake repeats the mechanism as live. | The issue is resolved quietly, displaced by another crisis object, or contradicted by verified operational data. | `hit` if the mechanism remains explicit by review date; `miss` if it is absent or clearly superseded; `mixed` if only one side of the mechanism remains; `unresolvable_with_authorized_evidence` if the archive cannot adjudicate. | Quiet de-escalation or a different day-owning object. | `none` |

## Forecast Quality Gate

- The claim is observable inside the time boundary.
- The mechanism explains why this outcome should occur.
- The principal alternative could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency cites one `OPC-*` claim from the day's synthesis or `none`.

## Ledger Entries

Copy final hooks to `work/forecasts/forecast-ledger.md`.

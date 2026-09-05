# Forecast / Review Hooks

Date: `2026-08-10`

Status: `retrospective-source-ledger`

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
| `NG-20260707-F02` | `2026-07-07` | Renewed coercive signaling | Within 30 days, U.S. or Israeli public signaling will again test coercive escalation because the old transit and sanctions baseline cannot be quietly restored. | `likely` | `2026-08-07` | [2026-07-07](../2026-07-07/forecast.md) |
| `NG-20260708-F02` | `2026-07-08` | Hormuz transit governance breakdown | Within 21 days, at least one new U.S., Israeli, or Gulf-side attempt to bypass or dilute Iranian transit authority will trigger another visible coercive test. | `likely` | `2026-07-29` | [2026-07-08](../2026-07-08/forecast.md) |
| `NG-20260720-F01` | `2026-07-20` | coalition access versus regional denial | Over the next 7–14 days, political and military pressure will shift toward maritime chokepoints, bases, and energy access rather than a decisive ground settlement. | `likely` | `2026-08-03` | [2026-07-20](../2026-07-20/forecast.md) |
| `NG-20260721-F01` | `2026-07-21` | Iran conflict escalation cycle | Within 14 days, the Iran conflict will show another cycle of limited strikes, threats, or pressure on bases/infrastructure without a durable settlement. | `likely` | `2026-08-04` | [2026-07-21](../2026-07-21/forecast.md) |
| `NG-20260730-F01` | `2026-07-30` | Whether renewed strikes can compel concessions without widening the actor field beyond diplomatic control | By `2026-08-06`, diplomatic channels will remain publicly visible while renewed strikes continue, but no durable reciprocal settlement will be implemented. | `plausible` | `2026-08-06` | [2026-07-30](../2026-07-30/forecast.md) |

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-YYYYMMDD-F01` |  |  |  |  |  |  |  |  | `none` |

## Forecast Quality Gate

- The claim is observable inside the time boundary.
- The mechanism explains why this outcome should occur.
- The principal alternative could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency cites one `OPC-*` claim from the day's synthesis or `none`.

## Ledger Entries

Copy final hooks to `work/forecasts/forecast-ledger.md`.

An accountable resolution of `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` must cite a completed `VER-*` packet in its ledger review note.

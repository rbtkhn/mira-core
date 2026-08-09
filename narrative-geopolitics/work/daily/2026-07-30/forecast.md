# Forecast / Review Hooks

Date: `2026-07-30`

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
| `NG-20260708-F02` | `2026-07-08` | Hormuz transit governance breakdown | Within 21 days, at least one new U.S., Israeli, or Gulf-side attempt to bypass or dilute Iranian transit authority will trigger another visible coercive test. | `likely` | `2026-07-29` | [2026-07-08](../2026-07-08/forecast.md) |

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260730-F01` | By `2026-08-06`, diplomatic channels will remain publicly visible while renewed strikes continue, but no durable reciprocal settlement will be implemented. | Force can create pressure and new participants faster than diplomacy can stabilize the sequence, leaving channels open without yet controlling the conflict. | `plausible` | `2026-08-06` | Public negotiation activity, declared terms, back-channel or mediator activity, or official statements showing channels remain open while strikes, threats, or intermittent pressure continue. | A durable pause or settlement with reciprocal implementation, or direct entry by additional actors that displaces diplomacy as an operative channel. | `hit` if channels remain publicly visible while renewed strikes or coercive pressure continue without durable reciprocal settlement by review date; `miss` if a durable reciprocal settlement is implemented or diplomacy disappears as an operative channel; `mixed` if diplomatic contact remains visible but direct actor entry materially changes the sequence; `unresolvable_with_authorized_evidence` if public records cannot establish channel status. | A short escalation pause restores negotiations with durable reciprocal commitments. | `none` |

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

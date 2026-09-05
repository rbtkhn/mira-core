# Forecast / Review Hooks

Date: `2026-07-16`

Status: `first-pass-synthesis`

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
| `NG-20260716-F01` | By `2026-08-16`, at least one major U.S., GCC, Iranian, or Ansarallah/Yemeni public statement will explicitly link Bab el-Mandeb or Red Sea security to the Hormuz/Iran war settlement rather than treating it as a separate Yemen-Saudi issue. | Once Hormuz pressure and Yemen/Saudi retaliation interact, actors gain incentives to define Red Sea access as part of the same bargaining system. | `likely` | `2026-08-16` | Official statements tie Red Sea/Bab el-Mandeb access, Yanbu, Saudi exports, or Yemen retaliation to Hormuz normalization or Iran-war settlement terms. | Public statements keep Red Sea/Yemen issues separate, or there is a quick de-escalation that restores Hormuz and avoids Red Sea bargaining. | `hit` if a qualifying public statement explicitly links the frames by review date; `miss` if no qualifying link appears; `mixed` if only non-official or ambiguous elite commentary links them; `unresolvable_with_authorized_evidence` if available records cannot establish public statements. | The crisis remains Hormuz-centered and Yemen/Saudi events stay compartmentalized. | `none` |

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

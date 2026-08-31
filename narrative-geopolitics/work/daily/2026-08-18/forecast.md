# Forecast / Review Hooks

Date: `2026-08-18`

Status: `draft`

Forecast rule: state a causal wager, not topic plus outcome. See [labels as analytical interfaces](../../../method/analytical-interfaces.md).

## Probability Bands

Use coarse bands, not false precision:

- `low`: roughly 10-30%
- `plausible`: roughly 30-45%
- `likely`: roughly 55-70%
- `high`: roughly 70-85%

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260818-F01` | By `2026-08-25`, at least one major U.S., Omani, Iranian, or shipping-market source will still frame Hormuz passage as conditional, contested, or only partially normalized rather than fully restored. | Route governance remains tied to blockade relief, sovereignty claims, and U.S. pressure on Oman, so visible normalization should lag ceasefire rhetoric. | `likely` | `2026-08-25` | Continued Oman-Iran route talks; U.S. objections to Iranian control/toll language; shipping advisories showing constrained passage. | Announced tri-party accommodation; normal traffic resumption; public removal of route-control dispute from official and shipping-market reporting. | `hit` if a qualifying source still frames passage as conditional/contested/partial by review date; `miss` if authoritative reporting shows ordinary passage restored without live route-control dispute; `mixed` if traffic improves while official control dispute remains unresolved; `unresolvable_with_authorized_evidence` if no authorized review sources are available. | A rapid Oman-Iran-U.S. accommodation restores ordinary passage and removes control/toll language from public reporting. | `OPC-20260818-01` |

## Forecast Quality Gate

- The claim is observable inside the time boundary.
- The mechanism explains why conditional passage would persist.
- The principal alternative could explain normalization if diplomacy suddenly resolves the route-control dispute.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency cites a candidate `OPC-*` row from the day's synthesis; resolution must not occur until that row has a completed verification basis or is explicitly bracketed as non-operational.

## Ledger Entries

Copy final hooks to `work/forecasts/forecast-ledger.md`.

An accountable resolution of `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` must cite a completed `VER-*` packet in its ledger review note.

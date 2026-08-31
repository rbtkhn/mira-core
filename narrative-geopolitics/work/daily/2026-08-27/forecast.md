# Forecast / Review Hooks

Date: `2026-08-27`

Status: `live-intake-first`

Forecast rule: state a causal wager, not topic plus outcome. See [labels as analytical interfaces](../../../method/analytical-interfaces.md).

## Probability Bands

- `low`: roughly 10-30%
- `plausible`: roughly 30-45%
- `likely`: roughly 55-70%
- `high`: roughly 70-85%

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260827-F01` | By `2026-09-10`, at least one later source lane, official statement, or policy move will frame U.S. Iran/Gulf pressure as sanctions enforcement, force protection, partner restraint, or containment rather than clean victory settlement. | If coercive leverage is becoming burden management, public posture will migrate toward maintenance language rather than decisive war aims. | `likely` | `2026-09-10` | Later sources or official language emphasize force protection, sanctions implementation, coalition management, shipping conditions, or containment. | Later sources show a durable reciprocal settlement or renewed maximalist victory language with credible coercive capacity. | `hit` if a later authorized source lane or official signal clearly uses burden-management language; `miss` if clean settlement or victory framing dominates; `mixed` if both appear; `unresolvable_with_authorized_evidence` if no authorized later evidence is reviewed. | Renewed U.S./Israeli escalation could briefly restore maximalist victory language. | `none` |
| `NG-20260827-F02` | By `2026-09-17`, at least one later Russia/Ukraine source lane or official signal will still frame negotiations as constrained by battlefield leverage, air-defense depletion, or territorial sequence rather than by a mutually acceptable ceasefire design. | If Russia believes the military trend improves its bargaining position, diplomacy stays subordinate to operational sequence. | `plausible` | `2026-09-17` | Later sources or official signals foreground Donbas/Sloviansk sequence, air-defense depletion, territorial terms, or Western inability to compel Russian compromise. | A major battlefield reversal, credible enforcement design, or reciprocal ceasefire framework becomes the dominant signal. | `hit` if later authorized evidence keeps negotiations subordinated to battlefield sequence; `miss` if a mutually acceptable ceasefire design dominates; `mixed` if sequence and settlement design coexist; `unresolvable_with_authorized_evidence` if no authorized later evidence is reviewed. | A major battlefield reversal or external enforcement proposal could move diplomacy back to center. | `none` |

## Forecast Quality Gate

- The claim is observable inside the time boundary.
- The mechanism explains why this outcome should occur.
- The principal alternative could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency cites one `OPC-*` claim from the day's synthesis or `none`.

## Ledger Entries

Ledger sync was not performed in this branch. Copy final hooks to `work/forecasts/forecast-ledger.md` only through the governed forecast-sync path or an explicitly authorized ledger update.

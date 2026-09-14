# Forecast / Review Hooks

Date: `2026-08-31`

Status: `internal-draft`

Forecast rule: state a causal wager, not topic plus outcome. See [labels as analytical interfaces](../../../method/analytical-interfaces.md).

## Probability Bands

Use coarse bands, not false precision:

- `low`: roughly 10-30%
- `plausible`: roughly 30-45%
- `likely`: roughly 55-70%
- `high`: roughly 70-85%

## Due Review Hooks

Open forecast hooks whose review date is due on or before this run date are not resolved in this packet. Resolution requires separate review evidence and, where needed, verification receipts.

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260831-F01` | By `2026-09-14`, at least one later source lane or public signal will still frame Iran/Gulf pressure around maritime access, base exposure, sanctions, or force-posture management rather than a clean U.S. victory settlement. | If coercion is constrained by the infrastructure that carries it, follow-on signals should emphasize route and posture management. | `likely` | `2026-09-14` | Later sources or public posture explicitly discuss Hormuz, Red Sea, base protection, force rotation, sanctions fallback, or host-state exposure. | Later sources instead center a durable settlement, clean U.S. victory claim, or demobilized access problem. | `hit` if at least one qualifying later signal appears by review date; `miss` if no qualifying signal appears in authorized review material; `mixed` if signals appear but are marginal or unrelated to actor posture. | A rapid de-escalation could move the discourse back to diplomacy rather than access management. | `none` |
| `NG-20260831-F02` | By `2026-09-30`, later Ukraine-source coverage will still treat Russian strikes on energy, warehouses, drones, or air defense as a central pressure lane rather than a side issue. | Infrastructure attrition becomes politically salient when it constrains winter logistics and urban resilience. | `plausible` | `2026-09-30` | Later sources foreground energy systems, warehouses, air-defense exhaustion, drones, fuel, food logistics, or winter urban habitability. | Later sources shift decisively to diplomacy or front-line maneuver while infrastructure claims recede. | `hit` if infrastructure pressure remains a central source-frame by review date; `miss` if it does not appear in authorized review material; `mixed` if it appears only as background. | The front line or diplomacy could regain priority and displace infrastructure as the dominant analytic object. | `none` |

## Forecast Quality Gate

- The claim is observable inside the time boundary.
- The mechanism explains why this outcome should occur.
- The principal alternative could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency cites one `OPC-*` claim from the day's synthesis or `none`.

## Ledger Entries

Do not copy these hooks to `work/forecasts/forecast-ledger.md` without separate operator authority.

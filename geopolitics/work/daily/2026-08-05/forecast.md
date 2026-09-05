# Forecast / Review Hooks

Date: `2026-08-05`

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
| `NG-20260720-F01` | `2026-07-20` | coalition access versus regional denial | Over the next 7-14 days, political and military pressure will shift toward maritime chokepoints, bases, and energy access rather than a decisive ground settlement. | `likely` | `2026-08-03` | [2026-07-20](../2026-07-20/forecast.md) |
| `NG-20260721-F01` | `2026-07-21` | Iran conflict escalation cycle | Within 14 days, the Iran conflict will show another cycle of limited strikes, threats, or pressure on bases/infrastructure without a durable settlement. | `likely` | `2026-08-04` | [2026-07-21](../2026-07-21/forecast.md) |
| `NG-20260722-F01` | `2026-07-22` | Iran-war participation-control crisis | Within 14 days, at least one public U.S., Iranian, Saudi, or Yemeni posture change will explicitly link maritime access to infrastructure protection, alliance participation, or security guarantees. | `likely` | `2026-08-05` | [2026-07-22](../2026-07-22/forecast.md) |

These due hooks are not resolved here. Resolution requires the forecast-review workflow and any required verification packets.

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260805-F01` | By `2026-08-19`, at least one public U.S., Iranian, Israeli, Gulf, or Yemeni posture change observable after `2026-08-06` will explicitly link Hormuz transit normalization to sanctions relief, regional infrastructure protection, Lebanon/Gaza escalation, or U.S. force-stock constraints. | A constrained pause must be defended through adjacent carriers: transit rules, sanctions, oil flow, Israel's disruption incentives, and exposed U.S./Gulf positions. | `likely` | `2026-08-19` | Official or high-visibility statements after `2026-08-06` tie Hormuz/Oman transit, sanctions relief, oil flow, Lebanon/Gaza, Yemen/Saudi attacks, or U.S. munition limits into one bargaining frame. | Shipping and oil-flow normalization proceeds without adjacent escalation language; Israel and Yemen/Lebanon remain compartmentalized; U.S. statements stop linking capacity or infrastructure to negotiations. | `hit` if a public posture change after `2026-08-06` makes one of the listed linkages explicit by `2026-08-19`; `mixed` if linkage appears only in unattributed leaks or commentary; `miss` if no such linkage appears and the pause remains compartmentalized; `unresolvable_with_authorized_evidence` if only inaccessible or unreviewed evidence exists. | The arrangement becomes a narrow maritime-management pause while actors avoid widening the frame. | `none` |

## Forecast Quality Gate

- The claim is observable inside the time boundary.
- The mechanism explains why this outcome should occur.
- The principal alternative could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency cites one `OPC-*` claim from the day's synthesis or `none`.

## Ledger Entries

Copy final hooks to `work/forecasts/forecast-ledger.md` only after explicit ledger-sync authority.

An accountable resolution of `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` must cite a completed `VER-*` packet in its ledger review note.

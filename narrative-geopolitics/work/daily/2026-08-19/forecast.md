# Forecast / Review Hooks

Date: `2026-08-19`

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
| `NG-20260707-F02` | `2026-07-07` | Renewed coercive signaling | Within 30 days, U.S. or Israeli public signaling will again test coercive escalation because the old transit and sanctions baseline cannot be quietly restored. | `likely` | `2026-08-07` | [2026-07-07](../2026-07-07/forecast.md) |
| `NG-20260708-F02` | `2026-07-08` | Hormuz transit governance breakdown | Within 21 days, at least one new U.S., Israeli, or Gulf-side attempt to bypass or dilute Iranian transit authority will trigger another visible coercive test. | `likely` | `2026-07-29` | [2026-07-08](../2026-07-08/forecast.md) |
| `NG-20260716-F01` | `2026-07-16` | Dual chokepoint energy-flow control | By `2026-08-16`, at least one major U.S., GCC, Iranian, or Ansarallah/Yemeni public statement will explicitly link Bab el-Mandeb or Red Sea security to the Hormuz/Iran war settlement rather than treating it as a separate Yemen-Saudi issue. | `likely` | `2026-08-16` | [2026-07-16](../2026-07-16/forecast.md) |
| `NG-20260719-F01` | `2026-07-19` | Can Washington sustain simultaneous coercive pressure against Iran and Russia when the bases, ports, corridors, and allies that carry that pressure become targets of the opposing strategy? | By `2026-08-19`, at least one major July follow-on source or official/regional posture signal will still frame the Iran war around U.S. regional base access, host-state exposure, or relocation/protection of U.S. assets rather than only airstrikes or nuclear bargaining. | `likely` | `2026-08-19` | [2026-07-19](../2026-07-19/forecast.md) |
| `NG-20260720-F01` | `2026-07-20` | coalition access versus regional denial | Over the next 7–14 days, political and military pressure will shift toward maritime chokepoints, bases, and energy access rather than a decisive ground settlement. | `likely` | `2026-08-03` | [2026-07-20](../2026-07-20/forecast.md) |
| `NG-20260721-F01` | `2026-07-21` | Iran conflict escalation cycle | Within 14 days, the Iran conflict will show another cycle of limited strikes, threats, or pressure on bases/infrastructure without a durable settlement. | `likely` | `2026-08-04` | [2026-07-21](../2026-07-21/forecast.md) |
| `NG-20260730-F01` | `2026-07-30` | Whether renewed strikes can compel concessions without widening the actor field beyond diplomatic control | By `2026-08-06`, diplomatic channels will remain publicly visible while renewed strikes continue, but no durable reciprocal settlement will be implemented. | `plausible` | `2026-08-06` | [2026-07-30](../2026-07-30/forecast.md) |
| `NG-20260805-F01` | `2026-08-05` | Crisis object: Can Washington convert a constrained pause around Hormuz into a durable off-ramp before depleted coercive capacity and Israeli disruption pressure pull the conflict back into a hot-ceasefire cycle? | By `2026-08-19`, at least one public U.S., Iranian, Israeli, Gulf, or Yemeni posture change observable after `2026-08-06` will explicitly link Hormuz transit normalization to sanctions relief, regional infrastructure protection, Lebanon/Gaza escalation, or U.S. force-stock constraints. | A constrained pause must be defended through adjacent carriers: transit rules, sanctions, oil flow, Israel's disruption incentives, and exposed U.S./Gulf positions. | `likely` | `2026-08-19` | [2026-08-05](../2026-08-05/forecast.md) |
| `NG-20260812-F01` | `2026-08-12` | U.S. force-strain around Iran/Gulf pressure | By `2026-08-19`, at least one later source lane, official statement, or policy move frames Iran/Gulf pressure as containment, sanctions enforcement, force rotation, maritime access management, or managed attrition rather than a clean victory settlement. | If the U.S. coercive posture is consuming more strategic margin than it is producing, later signals will move away from clean victory and toward burden management. | `plausible` | `2026-08-19` | [2026-08-12](../2026-08-12/forecast.md) |

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260819-F01` | By `2026-09-02`, at least one major U.S., Israeli, Iranian, Turkish, Gulf, Yemeni, or European posture signal will frame the Iran conflict through theater-management pressure such as Syria/Turkey deconfliction, Yemen/Red Sea leverage, Gulf/base exposure, sanctions enforcement, or tactical-nuclear rhetoric rather than a clean bilateral Iran nuclear settlement. | Failed coercion forces actors to seek leverage through adjacent carriers when direct strike pressure cannot produce a stable settlement. | `likely` | `2026-09-02` | Official or major-source signals linking Iran to Syria/Turkey, Yemen/Red Sea, Gulf bases, sanctions enforcement, European targeting, or tactical-nuclear discussion. | A quiet diplomatic sequence that narrows the conflict to bilateral U.S.-Iran or Israel-Iran settlement without adjacent theater pressure. | `hit` if at least one qualifying posture signal appears by review date; `miss` if the file visibly narrows without such pressure; `mixed` if only low-salience or purely retrospective commentary appears. | The conflict narrows into quiet diplomacy or a temporary transit/sanctions settlement without prominent adjacent-theater pressure. | `none` |

## Forecast Quality Gate

- The claim is observable inside the time boundary.
- The mechanism explains why this outcome should occur.
- The principal alternative could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency cites one `OPC-*` claim from the day's synthesis or `none`.

## Late-source forecast review

`SRC-13` makes European base exposure an explicit instance of the existing theater-management observable. It does not independently verify a posture change and cannot resolve the hook. The probability and review date remain unchanged; later official Cypriot, U.S., Iranian, or allied posture would be required.

## Ledger Entries

Copy final hooks to `work/forecasts/forecast-ledger.md`.

An accountable resolution of `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` must cite a completed `VER-*` packet in its ledger review note.

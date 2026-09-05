# Forecast / Review Hooks

Date: `2026-08-17`

Status: `internal-draft`

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
| `NG-20260720-F01` | `2026-07-20` | coalition access versus regional denial | Over the next 7-14 days, political and military pressure will shift toward maritime chokepoints, bases, and energy access rather than a decisive ground settlement. | `likely` | `2026-08-03` | [2026-07-20](../2026-07-20/forecast.md) |
| `NG-20260721-F01` | `2026-07-21` | Iran conflict escalation cycle | Within 14 days, the Iran conflict will show another cycle of limited strikes, threats, or pressure on bases/infrastructure without a durable settlement. | `likely` | `2026-08-04` | [2026-07-21](../2026-07-21/forecast.md) |
| `NG-20260730-F01` | `2026-07-30` | Whether renewed strikes can compel concessions without widening the actor field beyond diplomatic control | By `2026-08-06`, diplomatic channels will remain publicly visible while renewed strikes continue, but no durable reciprocal settlement will be implemented. | `plausible` | `2026-08-06` | [2026-07-30](../2026-07-30/forecast.md) |

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260817-F01` | By `2026-08-31`, U.S. public messaging or leak patterns will again foreground either command restraint, munitions/logistics limits, or legality concerns around the Iran/Hormuz crisis. | Coercive signaling is now exposing the support structure needed to execute it. | `likely` | `2026-08-31` | More leaks, official denials, congressional questions, military-family reporting, or public debate about command/legal/logistics limits. | A stable negotiated de-escalation with no visible U.S. institutional-strain narrative. | `hit` if one qualifying public signal appears; `miss` if none appears; `mixed` if signals are indirect or primarily legacy recaps. | The administration suppresses dissent and reframes the crisis as successful deterrence. | `none` |
| `NG-20260817-F02` | By `2026-09-07`, at least one public diplomatic or security signal will link Hormuz transit normalization to sanctions relief, U.S. force posture, or Gulf mediation rather than treating shipping access as a standalone technical matter. | Iran's leverage works by connecting maritime access to settlement terms and regional legitimacy. | `plausible` | `2026-09-07` | Statements from Iran, Oman, Gulf states, China/Russia, or U.S. officials tying transit access to sanctions, bases, fees, or mediation. | A narrow technical maritime arrangement with no visible political linkage. | `hit` if linkage appears; `miss` if transit is treated only as technical access; `mixed` if linkage appears only through non-official commentary. | Transit reopens through a narrow technical arrangement that avoids public concession. | `none` |

## Forecast Quality Gate

- The claims are observable inside the time boundary.
- The mechanisms explain why the outcomes should occur.
- The principal alternatives could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency is `none`; source assertions support the causal frame but are not required as verified operating facts.

## Ledger Entries

Not copied to `work/forecasts/forecast-ledger.md` in this turn.

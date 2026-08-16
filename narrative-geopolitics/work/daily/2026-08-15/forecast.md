# Forecast / Review Hooks

Date: `2026-08-15`

Status: `source-bounded`

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
| `NG-20260720-F01` | `2026-07-20` | coalition access versus regional denial | Over the next 7-14 days, political and military pressure will shift toward maritime chokepoints, bases, and energy access rather than a decisive ground settlement. | `likely` | `2026-08-03` | [2026-07-20](../2026-07-20/forecast.md) |
| `NG-20260721-F01` | `2026-07-21` | Iran conflict escalation cycle | Within 14 days, the Iran conflict will show another cycle of limited strikes, threats, or pressure on bases/infrastructure without a durable settlement. | `likely` | `2026-08-04` | [2026-07-21](../2026-07-21/forecast.md) |
| `NG-20260730-F01` | `2026-07-30` | Whether renewed strikes can compel concessions without widening the actor field beyond diplomatic control | By `2026-08-06`, diplomatic channels will remain publicly visible while renewed strikes continue, but no durable reciprocal settlement will be implemented. | `plausible` | `2026-08-06` | [2026-07-30](../2026-07-30/forecast.md) |

## Hooks

No new accountable forecast hook is issued from the August 15 packet. The strongest candidate would predict a shift from victory/control language toward burden-management language around Hormuz and Ukraine, but the supporting operating claims are still source-attributed and require verification before admission to the ledger.

## Watch Frame

| Watch ID | Observable signal | Mechanism tested | Review Window | Strengthening evidence | Weakening evidence | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- |
| `WATCH-20260815-01` | U.S. or partner language shifts from control/victory claims toward force rotation, sanctions fallback, partner restraint, route conditions, or burden management. | Time-control pressure: coercive systems reveal sustainment costs before they concede failure. | `2026-08-16` to `2026-09-15` | Official or semi-official language emphasizes rotations, depleted stocks, sanctions-only pressure, route conditions, or partner-restraint diplomacy. | Routine Hormuz passage, normalized U.S. naval posture, declining oil-market stress, and confident diplomatic settlement language without visible concessions. | none |
| `WATCH-20260815-02` | Ukraine reporting shifts toward air-defense scarcity, Odessa/transport compression, or Western production limits rather than initiative claims. | Industrial-depth pressure: Russia benefits if time turns Western supply scarcity into battlefield or economic constraint. | `2026-08-16` to `2026-09-15` | Repeated reports of interceptor shortage, port/rail disruption, delayed Western production, or worsening logistics. | Stable Ukrainian air defense, resilient Odessa exports, restored rail/port throughput, or Western production surge. | none |

## Forecast Quality Gate

- No probability-bearing hook is issued.
- The watch signals are observable, but they are deliberately not admitted as accountable forecasts.
- Operational dependency is `none` because no `OPC-*` claim is retained for public factual use.
- Any future hook should first resolve whether its operating premise requires a verification packet.

## Ledger Entries

No new ledger entries were created.

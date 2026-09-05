# Forecast / Review Hooks

Date: `2026-07-18`

Status: `live-intake-first`

Forecast rule: state a causal wager, not topic plus outcome. See [labels as analytical interfaces](../../../method/analytical-interfaces.md).

## Probability Bands

Use coarse bands, not false precision:

- `low`: roughly 10-30%
- `plausible`: roughly 30-45%
- `likely`: roughly 55-70%
- `high`: roughly 70-85%

## Due Review Hooks

No open ledger hooks are due on or before this run date according to the synthesis runner.

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260718-F01` | By `2026-08-18`, U.S., Iranian, or GCC public posture will still frame the Iran war around regional infrastructure vulnerability, base access, or terrain-control options rather than only nuclear negotiations or generic airstrikes. | Once infrastructure and regional basing become the bargaining surface, each side has incentives to signal control over what Gulf states physically need to keep operating. | `likely` | `2026-08-18` | New public references to desalination, ports, airports, bases, bridge/power targets, island seizure, ground options, emergency water security, or GCC base access as bargaining objects. | A durable off-ramp that reframes the campaign as completed punishment, stops public infrastructure targeting language, and returns official emphasis to negotiations without regional operating threats. | `hit` if at least one major U.S., Iranian, or GCC public posture signal by `2026-08-18` treats infrastructure vulnerability, base access, or terrain-control options as central to the war; `miss` if public posture has clearly returned to nuclear/diplomatic framing without those operating threats; `mixed` if the language persists only in analyst commentary; `unresolvable_with_authorized_evidence` if authorized evidence cannot distinguish official posture from commentary. | The parties rapidly move to an off-ramp that reframes escalation as completed punishment and returns public language to diplomacy. | `OPC-20260718-01` |

## Forecast Quality Gate

- The claim is observable inside the time boundary.
- The mechanism explains why this outcome should occur.
- The principal alternative could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency cites `OPC-20260718-01`; accountable resolution should wait for a completed verification packet if the resolution depends on the claimed Kuwaiti infrastructure strike.

## Ledger Entries

Copy final hooks to `work/forecasts/forecast-ledger.md`.

An accountable resolution of `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` must cite a completed `VER-*` packet in its ledger review note.

# Forecast / Review Hooks

Date: `2026-07-19`

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
| `NG-20260719-F01` | By `2026-08-19`, at least one major July follow-on source or official/regional posture signal will still frame the Iran war around U.S. regional base access, host-state exposure, or relocation/protection of U.S. assets rather than only airstrikes or nuclear bargaining. | Once regional hosts and U.S. operating platforms are treated as the medium of escalation, both Iran-facing deterrence and U.S. force-protection logic have incentives to keep basing visible. | `likely` | `2026-08-19` | Public references to GCC or Jordanian base access, U.S. tanker or aircraft relocation, host-state exposure, airspace/base limits, emergency protection of regional facilities, or U.S. force-protection posture as central to Iran-war management. | A durable off-ramp that returns official and analyst emphasis to negotiations, sanctions, or nuclear terms while regional base-access and host-exposure language recedes. | `hit` if at least one major official/regional posture signal or subsequent July synthesis source by `2026-08-19` treats U.S. regional base access, host-state exposure, or relocation/protection of U.S. assets as central to the Iran war; `miss` if the public frame has clearly returned to diplomacy/sanctions/nuclear terms without basing prominence; `mixed` if basing language persists only in minor commentary; `unresolvable_with_authorized_evidence` if authorized evidence cannot distinguish posture from commentary. | A rapid off-ramp or successful suppression campaign returns public framing to diplomacy, sanctions, and nuclear terms while base-access language recedes. | `none` |

## Forecast Quality Gate

- The claim is observable inside the time boundary.
- The mechanism explains why this outcome should occur.
- The principal alternative could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency is `none`; this hook can be reviewed against public posture without first verifying the day's source-reported strike or casualty claims.

## Ledger Entries

Copy final hooks to `work/forecasts/forecast-ledger.md`.

An accountable resolution of `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` must cite a completed `VER-*` packet when resolution depends on operational claims. This hook is posture-based and not currently packet-gated.

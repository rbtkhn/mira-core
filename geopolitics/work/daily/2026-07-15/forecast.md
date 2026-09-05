# Forecast / Review Hooks

Date: `2026-07-15`

Status: `source-bounded complete`

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
| `NG-20260715-F01` | By `2026-08-15`, U.S. public posture will include either a named ground/terrain option for Iran-linked objectives or a visible pullback/off-ramp framed as victory, rather than only continued nightly airstrikes. | If air and missile strikes cannot restore tolerable passage on U.S. terms, the administration must either escalate to terrain or politically reframe withdrawal before energy and stockpile pressure dominate. | `plausible` | `2026-08-15` | Official or well-sourced reporting on Kharg Island, coastal seizure, Kurdish/separatist proxy action, Marine/airborne deployments, or a declared victory-withdrawal frame. | Sustained shipping recovery, explicit official rejection of ground/proxy options, or a durable negotiated mechanism that restores passage without U.S. terrain claims. | `hit` if either a named terrain/ground/proxy option becomes official or well-sourced, or if the administration publicly reframes de-escalation as victory; `miss` if posture remains airstrikes plus talks without either by review date; `mixed` if signals are ambiguous; `unresolvable_with_authorized_evidence` if evidence access is insufficient. | Continued episodic strikes and negotiation theater can defer the terrain-or-off-ramp choice longer than the sources expect. | `OPC-20260715-01` |

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

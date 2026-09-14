# Forecast / Review Hooks

Date: `2026-09-07`

Status: `live-intake-first`

Forecast rule: state a causal wager, not topic plus outcome. See [labels as analytical interfaces](../../../method/analytical-interfaces.md).

## Probability Bands

Use coarse bands, not false precision:

- `low`: roughly 10-30%
- `plausible`: roughly 30-45%
- `likely`: roughly 55-70%
- `high`: roughly 70-85%

## Due Review Hooks

Open forecast hooks whose review date is due on or before this run date remain listed by the generator receipt and should be reviewed in a separate forecast-resolution pass. This synthesis does not score them.

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260907-F01` | By `2026-09-21`, at least one public U.S., Gulf, Iranian, Omani, Saudi, Yemeni, or shipping-market signal will frame Gulf/Hormuz access as conditional on force posture, sanctions, infrastructure protection, mediation, or host-state exposure rather than as simple restored freedom of navigation. | If Iran-aligned pressure is converting coercion into bargaining leverage, public handling should keep linking transit access to settlement terms and exposed regional infrastructure. | `likely` | `2026-09-21` | Official statements or major market reporting connect Hormuz/Gulf transit to sanctions, force posture, Gulf mediation, base protection, or infrastructure risk. | Major actors and shipping-market reporting converge on routine normalization without settlement linkage. | `hit` if qualifying public signals appear by the review date; `miss` if public handling is dominated by normalized technical maritime management; `mixed` if linkage appears only in source commentary without official or market uptake. | A narrow maritime-security frame returns and major actors treat shipping access as normalized technical management. | `none` |
| `NG-20260907-F02` | By `2026-09-28`, at least one major U.S., Ukrainian, Russian, or European signal will describe Ukraine settlement efforts through territorial red lines, battlefield leverage, failed shuttle diplomacy, or imposed-deal resistance rather than generic ceasefire optimism. | If Ukraine is the second exit problem, the next public signals should foreground the terms that prevent Washington from converting diplomacy into settlement. | `plausible` | `2026-09-28` | Official remarks, major diplomatic reporting, or battlefield-linked statements foreground territorial red lines, Russian leverage, Ukrainian refusal, or failed shuttle efforts. | Public messaging converges on implementable negotiations with reduced emphasis on red lines or battlefield leverage. | `hit` if qualifying settlement-friction language appears by the review date; `miss` if settlement messaging becomes concrete and mutually acknowledged without those friction markers; `mixed` if only one side uses the frame. | Diplomatic messaging converges on a credible framework that all sides describe as negotiations over implementable terms. | `none` |

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

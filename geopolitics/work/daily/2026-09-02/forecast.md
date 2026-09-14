# Forecast / Review Hooks

Date: `2026-09-02`

Status: `draft`

Forecast rule: state a causal wager, not topic plus outcome. See [labels as analytical interfaces](../../../method/analytical-interfaces.md).

## Probability Bands

Use coarse bands, not false precision:

- `low`: roughly 10-30%
- `plausible`: roughly 30-45%
- `likely`: roughly 55-70%
- `high`: roughly 70-85%

## Due Review Hooks

Open forecast hooks whose review date is due on or before this run date remain listed by the scaffolded run and require separate review before ledger closure. This September 2 packet does not resolve them.

## Hooks

| Hook ID | Observable claim | Causal mechanism | Probability Band | Review Date | Strengthening evidence | Weakening evidence | Resolution criteria | Principal alternative | Operational Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NG-20260902-F01` | By `2026-09-16`, at least one later source lane, official statement, or market/security posture signal will frame Iran/Hormuz pressure through base protection, interceptor scarcity, oil-price exposure, maritime insurance, or host-state distancing rather than clean U.S. victory. | If coercion is failing through its support structure, public and analytic language should migrate toward burden management and access protection. | `plausible` | `2026-09-16` | Explicit discussion of air-defense stocks, Gulf/Jordan base protection, insurance/shipping hesitation, oil-price management, sanctions fallback, or host-state distancing. | Clean victory/settlement framing dominates later signals and the burden-management vocabulary disappears. | `hit` if at least one qualifying later signal appears by review date; `miss` if later signals are available but none use the burden-management frame; `mixed` if signals appear only in partisan commentary; `unresolvable_with_authorized_evidence` if no later evidence review is authorized. | September 2 may be a temporary commentary cluster around a short tactical exchange. | `OPC-20260902-01` |
| `NG-20260902-F02` | By `2026-09-16`, at least one later market report, official economic statement, or archive source will frame Iran/Hormuz escalation through oil-price exposure, bond-yield stress, recession risk, shipping insurance, or market-management pressure rather than only military retaliation. | If Iran/Hormuz coercion is stressing U.S. economic room, later discussion should preserve a market-risk vocabulary after the immediate exchange. | `plausible` | `2026-09-16` | Oil, bond, shipping, or recession-risk language tied to the Iran/Hormuz escalation cycle. | Later market discussion treats the exchange as immaterial or driven by unrelated macro conditions. | `hit` if at least one qualifying later signal appears by review date; `miss` if available later signals omit market-pressure framing; `mixed` if only commentary sources retain the frame; `unresolvable_with_authorized_evidence` if no later evidence review is authorized. | The market movement described by Johnson may be transient or primarily caused by unrelated macroeconomic factors. | `OPC-20260902-02` |
| `NG-20260902-F03` | By `2026-09-16`, at least one later source lane, official statement, aviation-market signal, or Russian/Ukrainian posture signal will frame Ukraine escalation through Russian airspace risk, airport disruption, airline route adjustment, air-defense scarcity, or ally-support fatigue rather than a clean diplomatic settlement. | If Ukraine's leverage is shifting toward infrastructure pressure under alliance constraint, later language should emphasize route risk, defensive scarcity, and partner fatigue. | `plausible` | `2026-09-16` | Explicit discussion of Russian airport or airspace risk, airline route changes, air-defense scarcity, or allied support strain tied to Ukraine escalation. | Later signals emphasize a clean negotiation sequence or routine military operations without aviation-route or alliance-support stress. | `hit` if at least one qualifying later signal appears by review date; `miss` if later signals are available but none use the route/alliance-strain frame; `mixed` if signals appear only in commentary; `unresolvable_with_authorized_evidence` if no later evidence review is authorized. | The September 2 Ukraine material may be a narrow Mercouris/Wilkerson interpretive cluster without broader observable follow-through. | `OPC-20260902-03` |

## Forecast Quality Gate

- The claim is observable inside the time boundary.
- The mechanism explains why this outcome should occur.
- The principal alternative could explain the same surface evidence.
- Weakening evidence can reduce confidence before resolution.
- Resolution criteria permit `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` without hindsight rewriting.
- Operational dependency cites one `OPC-*` claim from the day's synthesis or `none`.

## Ledger Entries

`NG-20260902-F01`, `NG-20260902-F02`, and `NG-20260902-F03` are registered as excluded retrospective hypotheses. They are not accountable ex ante forecasts.

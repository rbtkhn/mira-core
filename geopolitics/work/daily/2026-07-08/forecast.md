# Forecast / Review Hooks

Date: `2026-07-08`

Status: `live-intake-first`

## Probability Bands

Use coarse bands, not false precision:

- `low`: roughly 10-30%
- `plausible`: roughly 30-45%
- `likely`: roughly 55-70%
- `high`: roughly 70-85%

## Due Review Hooks

No open ledger hooks are due on or before this run date.

## Hooks

| Hook ID | Claim | Probability Band | Review Date | Strengthening Evidence | Weakening Evidence |
| --- | --- | --- | --- | --- | --- |
| `NG-20260708-F01` | By `2026-07-22`, at least one major public actor on the Iran file will still describe Hormuz transit as conditional on supervision, compliance, routing rules, or managed passage rather than as ordinary restored free passage. | `likely` | `2026-07-22` | Explicit public dispute over supervision/fees/corridors, continued routing discipline, or repeated statements that transit depends on compliance. | Multiple weeks of normalized passage with no visible routing dispute, no talk of Iranian management, and no renewed challenge around supervision. |
| `NG-20260708-F02` | By `2026-07-29`, at least one new attempt to weaken or bypass Iranian transit authority will produce a visible coercive test such as a tanker challenge, strike cycle, corridor dispute, or sanctions escalation. | `likely` | `2026-07-29` | New escort effort, sanctions ratchet, tanker challenge, strike exchange, or explicit corridor dispute. | Quiet stabilization in which all sides tacitly accept an operating arrangement and no fresh challenge is mounted. |
| `NG-20260708-F03` | By `2026-08-07`, the July 8 judgment is weakened only if Hormuz shows practical normalization through both restored ship flow and lower political salience of Iranian-managed routing or Lebanon linkage. | `plausible` | `2026-08-07` | Ongoing Lebanon linkage, continued Iran-approved routing, or durable market attention to managed passage rather than nominal openness. | Sustained normalization of ship flow and pricing under a politically depersonalized shipping regime with Lebanon no longer acting as a visible gate. |

## Review Focus

| Hook ID | Review Question | Primary Observable |
| --- | --- | --- |
| `NG-20260708-F01` | Did any major actor still publicly describe transit as conditional or governed, or did the file revert to ordinary free-passage language? | Public routing language, supervision disputes, ship-routing practice |
| `NG-20260708-F02` | Did a fresh bypass attempt happen and did it trigger a visible response? | New corridor moves, strike cycles, sanctions shifts, tanker incidents |
| `NG-20260708-F03` | Did normalization arrive in both practice and political framing, or only in one of those dimensions? | Shipping volume, route usage, pricing, Lebanon linkage in public bargaining |

## Review Standard

- `F01` should be scored `hit` if even one major actor still frames Hormuz as a governed or conditional passage regime by the review date.
- `F02` should be scored `hit` only if both parts occur: a bypass/dilution attempt and a visible coercive response.
- `F03` should be scored `weakened` only if normalization appears in both operating reality and public-political framing, not just one or the other.

## Ledger Entries

Copy final hooks to `work/forecasts/forecast-ledger.md`.

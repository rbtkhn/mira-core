# Due Forecast Review - 2026-08-14

Status: `review-queue`

Scope: accountable forecast hooks listed as due in [2026-08-14 forecast.md](../../daily/2026-08-14/forecast.md).

Evidence boundary: This pass reviews forecast accountability state only. It does not score a forecast as `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` because the forecast-review startup contract requires completed verification packets before accountable scoring. Source assertions in later daily packets remain insufficient for resolution.

## Summary

The six due hooks are real accountability debt, but none should be forced closed from the current authorized corpus.

| Hook ID | Review Date | Current Status | Review Disposition | Required Next Step |
| --- | --- | --- | --- | --- |
| `NG-20260707-F01` | `2026-07-28` | `open` | `remain-open-needs-verification` | Complete `VER-20260806-01`. |
| `NG-20260707-F02` | `2026-08-07` | `open` | `remain-open-needs-verification` | Create or identify a verification packet for the fresh coercive-test observable. |
| `NG-20260708-F02` | `2026-07-29` | `open` | `remain-open-needs-verification` | Use assessed `VER-20260710-01` as constraint; complete `VER-20260714-01` or a successor packet. |
| `NG-20260720-F01` | `2026-08-03` | `open` | `remain-open-needs-verification` | Complete `VER-20260806-03`. |
| `NG-20260721-F01` | `2026-08-04` | `open` | `remain-open-needs-verification` | Complete `VER-20260806-04`. |
| `NG-20260730-F01` | `2026-08-06` | `open` | `remain-open-needs-verification` | Create or identify a verification packet covering the three-part observable. |

## Hook Notes

### `NG-20260707-F01`

Claim: Within 21 days, Lebanon-Hormuz linkage remains explicit in Iran-facing public bargaining, without a clean return to a nuclear-only frame.

Current review state: due, accountable, open. The ledger already records that the landed corpus contains only requested, not-investigated `VER-20260806-01`.

Disposition: remain open. A completed packet must determine whether the linkage was explicit during the review window and whether the public frame avoided collapse into nuclear-only bargaining.

### `NG-20260707-F02`

Claim: Within 30 days, U.S. or Israeli public signaling produces a fresh coercive test around Hormuz, sanctions, or regional strikes.

Current review state: due, accountable, open. No completed verification packet is linked.

Disposition: remain open. This needs a packet that separates rhetorical coercive signaling from an actual fresh coercive test, and defines the authorized evidence window through `2026-08-07`.

### `NG-20260708-F02`

Claim: Within 21 days, an attempt to bypass or dilute Iranian transit authority triggers another visible coercive test.

Current review state: due, accountable, open. `VER-20260710-01` is assessed as `operationally_contested` and explicitly withholds hit scoring; `VER-20260714-01` remains requested and not investigated.

Disposition: remain open. The next packet must resolve intent and causality: whether there was a bypass/dilution attempt, whether a coercive test followed, and whether the latter was triggered by the former.

### `NG-20260720-F01`

Claim: Over the next 7-14 days, pressure shifts toward maritime chokepoints, bases, and energy access rather than a decisive ground settlement.

Current review state: due, accountable, open. `VER-20260806-03` exists but remains requested and not investigated.

Disposition: remain open. The verification packet should adjudicate public posture and observable pressure allocation, not broad war outcome.

### `NG-20260721-F01`

Claim: Within 14 days, the Iran conflict shows another cycle of limited strikes, threats, or pressure on bases/infrastructure without a durable settlement.

Current review state: due, accountable, open. `VER-20260806-04` exists but remains requested and not investigated.

Disposition: remain open. The packet must establish whether there was a qualifying cycle and whether a durable settlement was absent by the review date.

### `NG-20260730-F01`

Claim: By `2026-08-06`, diplomatic channels remain publicly visible while renewed strikes continue, but no durable reciprocal settlement is implemented.

Current review state: due, accountable, open. No completed verification packet is linked.

Disposition: remain open. This is the hardest hook because it is conjunctive: visible diplomacy, continuing renewed strikes, and no durable reciprocal settlement all need bounded evidence.

## Ledger And Validation Notes

- `forecast-triage --as-of 2026-08-14` reports these six overdue accountable hooks as failures because they remain open past review date.
- The same triage run also reports one unrelated parity issue: triage row has no ledger entry for `NG-20260812-F01`.
- No ledger statuses were changed by this review queue.
- No `hit`, `miss`, `mixed`, or `unresolvable_with_authorized_evidence` outcome is authorized until the required verification packet exists and validates.

## Recommended Order

1. Complete `VER-20260806-01` for `NG-20260707-F01`, because it tests the oldest high-level linkage claim and likely informs several later Hormuz hooks.
2. Complete `VER-20260806-03` and `VER-20260806-04` together, because they both review the July 20-21 maritime/base/infrastructure escalation cycle.
3. Complete or replace `VER-20260714-01` for `NG-20260708-F02`, using `VER-20260710-01` as the constraint against premature hit scoring.
4. Create packets for `NG-20260707-F02` and `NG-20260730-F01` only after deciding whether the existing Hormuz/escalation packets can cover their observables without overbroad scope.

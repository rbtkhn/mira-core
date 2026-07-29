---
name: coffee
description: "Reorient Narrative Systems from repository state and the last verified dream handoff. Use when the operator says coffee or asks what bounded learning move should happen next."
---

# Coffee

Use only in `narrative-systems`. Coffee is read-only.

## Orient

1. Run `tools/run.ps1 cadence coffee --json`.
2. Inspect Git status, `public/watch.md`, accountable open forecasts, the latest
   manifest-backed daily run, and any experiment named by the handoff.
   When the handoff has a verification profile, report experiment verification
   separately from repository verification and show local-use versus repo-use.
   Report structured lane failures with their owner and next action; retain the
   raw output tail for auditability.
3. Treat `handoff_status` as a gate:
   - `missing`: bootstrap one bounded experiment;
   - `verification_failed`: repair before inheriting any lesson;
   - `stale`: reconcile current Git state with the handoff;
   - `current`: use `next_mode` to choose the next test.
4. Never treat the handoff as archive evidence. Verify its lesson against the
   named experiment, `evidence_summary`, and every `artifact_ref`. If a
   reference no longer resolves, treat the handoff as stale.
5. When `NARRATIVE_CHOICE_DB` is configured, run
   `tools/run.ps1 choice --format json review` and inspect the deterministic
   unresolved queue through `choice context`. Surface at most one lightweight
   unresolved-outcome prompt or five-selection choice review; ordinary work
   remains uninterrupted when the store is absent.

## Return

Briefly state what was learned, the bounded evidence supporting it, whether it
is safe to inherit, and what remains unverified. Offer exactly four grounded
actions:

- `A. Confirm` (`recommended`) — validate a claimed improvement before adopting it.
- `B. Test` (`alternative`) — run a discriminating falsifier or comparison.
- `C. Deepen` (`overlooked`) — fill one named evidence or mechanism gap.
- `D. Reframe` (`pause-or-deepen`) — retire, narrow, revert, or replace the method assumption.

Recommend one action and stop on the menu. Each action must name an artifact,
forecast, crisis object, observable, or method change.

Do not mutate intake, archive evidence, forecasts, publication, or Git state.

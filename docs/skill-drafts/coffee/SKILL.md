---
name: coffee
description: "Reorient Mira Core from repository state and the last verified dream handoff. Use when the operator says coffee or asks what bounded learning move should happen next."
---

# Coffee

Use only in `mira-core`. Coffee is read-only.

## Orient

1. Resolve the private cadence store before running Coffee. Prefer
   `MIRA_CORE_CADENCE_DB`, then compatibility variable `NARRATIVE_CADENCE_DB`.
   In this workspace, when both are unset and the existing compatibility store
   `C:\private\narrative-cadence.sqlite3` resolves, pass it explicitly with
   `--db`; do not create, copy, or migrate a store implicitly. Run
   `tools/run.ps1 cadence --db ABSOLUTE_STORE coffee --format markdown`.
   Return its deterministic four-action menu verbatim;
   do not remove, reorder, rename, replace, or hand-compose actions.
   Start it once. If the execution remains live, resume or poll the returned
   session rather than launching a duplicate cadence command.
2. Inspect Git status, `narrative-geopolitics/public/watch.md`, accountable
   open forecasts in
   `narrative-geopolitics/work/forecasts/forecast-ledger.md`, the latest
   manifest-backed daily run, and any experiment named by the handoff.
   Inspect dirty-state counts and capped top-level groupings before requesting
   paths. Scope any later path listing to the named experiment or failed lane;
   do not print the complete worktree in a broadly dirty repository.
   When the handoff has a verification profile, report experiment verification
   separately from repository verification and show local-use versus repo-use.
   Report structured lane failures with their owner and next action; retain the
   raw output tail for auditability.
3. Treat `handoff_status` as a gate:
   - `missing`: bootstrap one bounded experiment;
   - `local_current_repo_pending`: the bounded profile may be used locally when
     local-use is eligible; repository use requires explicit promotion;
   - `interrupted`: preserve completed phase receipts and resume or repair the
     interrupted phase without rerunning successful earlier work;
   - `verification_failed`: repair before inheriting any lesson;
   - `stale`: reconcile current Git state with the handoff;
   - `current`: use `next_mode` to choose the next test.
   Keep `rest_coverage_status` separate. Rest context may be
   `covered-current`, `missing-dream`, `late-terminal-only`,
   `late-substantive`, or `unavailable`; it never substitutes for the Dream
   handoff or changes Coffee's read-only authority.
4. Never treat the handoff as archive evidence. Verify its lesson against the
   named experiment, `evidence_summary`, and every `artifact_ref`. If a
   reference no longer resolves, treat the handoff as stale.
5. When `MIRA_CORE_CHOICE_DB` is configured, run
   `tools/run.ps1 choice --format json review` and inspect the deterministic
   unresolved queue through `choice context`. Surface at most one lightweight
   unresolved-outcome prompt or staged five-to-ten choice review; ordinary
   work remains uninterrupted when the store is absent.
6. Before running a test profile that writes temporary files, run
   `tools/run.ps1 session-preflight --temp-root ABSOLUTE_PATH --json`, then pass
   that root through `--temp-root` or `MIRA_CORE_SESSION_TEMP_ROOT`. Start
   each verifier once and resume its live process until completion. A missing
   output chunk is not evidence that the verifier failed or should be relaunched.

## Return

Briefly state what was learned, the bounded evidence supporting it, whether it
is safe to inherit, and what remains unverified. Offer exactly four grounded
actions. At least one must be action-ready with `selection_effect: execute`, a
visible label beginning `Execute:`, an exact read-only source, and a stated
verification result:

- `A. Confirm` (`recommended`) — validate a claimed improvement before adopting it.
- `B. Test` (`alternative`) — run a discriminating falsifier or comparison.
- `C. Deepen` (`overlooked`) — fill one named evidence or mechanism gap.
- `D. Reframe` (`pause-or-deepen`) — retire, narrow, revert, or replace the method assumption.

Recommend one action and stop on the menu. Each action must name an artifact,
forecast, crisis object, observable, or method change.

If the renderer reports `insufficient_grounding`, fail closed and report that
no honest four-action Coffee packet can be formed. Never invent filler actions.
Selecting a navigation-only letter develops that branch. Selecting the
validated action-ready letter authorizes only its exact read-only comparison;
disposition, testing, promotion, RSI assessment, and admission remain
separately authorized.

Do not mutate intake, archive evidence, forecasts, publication, or Git state.

# Uncommitted Corpus Migration Ledger

Date: 2026-09-08
Repository: `C:\dev\mira-core`
Branch: `main`

## Scope

This ledger records the uncommitted corpus after removing only four disposable
`.codex-tmp` artifacts. It is an audit boundary, not an authorization to
stage, commit, publish, or delete the remaining paths.

## Disposable cleanup completed

The following scratch artifacts were already absent from the working tree and
remain recorded as working-tree deletions:

- `.codex-tmp/archive-family-publish`
- `.codex-tmp/commit-scope-options.json`
- `.codex-tmp/commit-scope-surface.json`
- `.codex-tmp/july30-archive-repair`

No other cleanup target was altered.

## Deletion batch classification

- `archive/notes/innermost-loop-simulation/`: coordinated experiment
  retirement or migration; preserve pending replacement parity.
- Dated `archive/notes/` entries: authored Library, development, geopolitical,
  and continuity material; preserve pending owner review and index reconciliation.
- `archive/notes/development/` and `archive/notes/state-substrate-coercion.md`:
  authored development material; preserve.

## Untracked corpus classification

- `geopolitics/work/`: active capture, repair receipts, daily packets,
  comparisons, reality, and verification work; preserve and route by owner.
- `archive/notes/`, `archive/letters/`, and `archive/essays/`: authored or
  review-bound content; preserve pending domain review.
- `mira/journal/`: Mira Journal entries and technical references; preserve
  pending Mira Journal validation and publication-boundary review.
- `docs/skill-drafts/`, `scripts/`, `tests/`, and `tools/`: active workflow,
  implementation, and test changes; preserve pending focused review.
- `projects/`, `artifacts/`, and `lineage/`: project or supporting corpora;
  preserve pending ownership and generated-content checks.

## Current disposition

The remaining corpus is intentionally uncommitted and un-staged. Any future
cleanup must name exact paths and distinguish deletion, migration, generated
rebuild, and publication authority before mutation.

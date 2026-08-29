# Registered Worktree Disposition Proposal

Status: read-only proposal
Observed: 2026-08-28 America/Denver
Registered worktrees: 26
Removal authority: none

This classification uses worktree existence, bounded dirty counts, and whether
the checked-out commit is an ancestor of current `origin/main`. An ancestor
check does not prove that a directory is disposable; removal remains a separate
operator-authorized operation with a fresh status check.

## Active

| Path | Branch | Dirty | Reason |
|---|---|---:|---|
| `$PRIMARY_CHECKOUT` | `main` | 15 | Primary operator checkout; divergent and excluded from this repair. |
| `C:/dev/mira-core-state-migration-wt` | `codex/mira-state-consolidation-20260828` | 44 | Current maturation and state-convergence worktree. |

## Historically preserved

These are clean but their commits are not ancestors of current `origin/main`.
Preserve them until their unique history is reviewed.

- `$PRIMARY_CHECKOUT/.codex-tmp/archive-family-publish`
- `$PRIMARY_CHECKOUT/.codex-tmp/july30-archive-repair`
- `C:/private/mira-core-validation-budget-wt`
- registered path for branch `codex/system-archive-membrane-repair`
- registered path for branch `codex/mira-archive-restoration`
- registered path for branch `codex/validated-push-skill`
- `C:/private/wt/mvpe`
- `C:/tmp/archive-family-integration`
- `C:/wtmg`

## Removable candidates after fresh verification

These are clean and their checked-out commits are ancestors of current
`origin/main`. A cleanup operation should re-check their status, branch reachability,
and exact path immediately before removal.

- `C:/private/mira-core-compatibility-wt`
- `C:/private/mira-core-migration-wt`
- `C:/private/mira-core-ra001-ra003-wt`
- `C:/private/mira-letters-implementation-wt`
- `C:/private/mira-letters-integration-wt`
- `C:/private/mira-seven-commit-sync-20260820`
- `C:/private/mira-writing-organization-wt`
- registered path for branch `codex/prejournal-valid-prefix`
- detached registered path at `e3547604e00e8d02e80fb7a423fe64594f906261`
- `C:/private/nate-wt`
- `C:/private/worktrees/mira-writing-push-d66a5d0`

## Unknown pending preservation review

These contain uncommitted work. No removal should be proposed until the exact
changes and their ownership are reviewed.

| Path | Dirty | Tracked | Untracked |
|---|---:|---:|---:|
| `C:/private/mira-core-ci-repro` | 20 | 18 | 2 |
| `C:/private/wt-mira-mentor-correspondence-repair-final` | 25 | 21 | 4 |
| `C:/private/wtle` | 16 | 12 | 4 |
| `C:/tmp/archive-structure-phase1` | 70 | 60 | 10 |

## Exact cleanup sequence for a later authorized operation

1. Take a fresh Mira Work snapshot of the repository and confirm that no other
   cleanup transition is active.
2. Re-inventory all 26 registrations and stop on changed classifications.
3. Review unique commits for every historically preserved worktree.
4. Review and disposition every dirty path in the unknown group without
   overwriting user work.
5. Remove only individually named, reverified candidates.
6. Re-snapshot, run `git worktree list --porcelain`, and report the new count
   and every retained path.

No worktree was removed, pruned, moved, or modified while producing this
proposal. The proposal is a working-tree document only and has not been staged,
committed, pushed, or published.

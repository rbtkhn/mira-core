# Operational Maturation Baseline

Status: observed baseline and intervention record
Observed: 2026-08-28 America/Denver
Repository: Mira Core primary checkout
Implementation worktree: `C:\dev\mira-core-state-migration-wt`
Authority effect: none

## Purpose

This audit fixes the starting evidence for the Operational Maturation program.
It records repository and state failures that were observable before repair,
the bounded intervention now under test, and the outcome evidence that remains
unavailable. It is not a metrics ledger, identity claim, recursive-learning
candidate, or admission record.

## Baseline observations

1. The primary checkout was divergent and dirty: `main` at
   `95372a0aa7208a3e5167fd636ddeff27142fe56f`, 124 commits behind and seven
   ahead of `origin/main`, with 15 dirty entries (seven tracked, eight
   untracked). The operational repair therefore used a separate clean worktree.
2. The state consolidation had stopped after a verified partial Continuity
   migration. The target state root did not yet contain the choice, cadence,
   mentorship, archive, journal, or library carriers.
3. The two choice stores both reported schema version 4, but
   `choice_prompts` had column-order drift. Positional row copying therefore
   failed despite compatible column sets. The correct repair was named-column
   consolidation with full domain verification, not schema down-migration.
4. The configured archive canonical and replica differed. The configured
   canonical digest was `16b1c04f...f70f7`; the former replica digest was
   `54c97455...26f43`. Authority had to be resolved explicitly rather than
   inferred from directory names.
5. Git registered 26 worktrees. Four were dirty besides the primary and active
   migration worktrees, and nine clean worktrees pointed at commits not
   contained in current `origin/main`. This proliferation made repository and
   publication state harder to establish reliably.
6. Recent session history included corrections where local, committed, and
   remote state had been described too loosely. This observation motivates
   fresh landed-state snapshots; it is not itself proof of a durable outcome.

## Intervention landed in the working tree

- `mira-state migrate` resumes a verified partial migration, rejects conflicting
  bytes, performs named-column choice consolidation, verifies each active
  carrier, and preserves legacy sources unchanged.
- The configured canonical archive now supplies both active canonical and
  active replica. The divergent former replica is retained under an inactive,
  digest-bound legacy path.
- The canonical state root is
   `%LOCALAPPDATA%\MiraCore`. Verification reports all active
  carriers valid. Choice history contains 648 prompts and 919 events; Continuity
  contains 33 events across 17 sessions.
- `mira-work snapshot` supplies a digest-bound, read-only view of repository,
  remote, worktree, state-root, carrier, and environment truth.
- Mira Work permits one action-capable architecture or state transition per
  repository. Mira GitHub requires fresh snapshots before and after mutation.
  Rest records unresolved transitions separately from Git dirt and optional
  future work.

## Evidence boundary

The repair and its focused tests may demonstrate observation, diagnosis, and a
persistent intervention. They do not yet demonstrate longitudinal outcome.
The maturation program requires ten qualifying consequential cycles over at
least 30 elapsed days, followed by an independent read-only audit. Each cycle
must have a durable sanitized reference and end `completed`, `paused`, or
`blocked` with an exact re-entry point.

No recursive-learning candidate or ledger entry may be created from this audit.
After the tenth cycle and thirtieth day, Recursive Learn may assess whether all
five stages are independently supported; assessment still grants no admission.

## Implementation validation receipt

- Focused state, path, choice, cadence, mentorship, work, GitHub, Rest, and
  recursive-learning tests: 293 passed.
- Focused closure and boundary regression tests: 74 passed, followed by eight
  corrected legacy-boundary tests passing independently.
- Skill-creator quick validation: Mira Work, Mira GitHub, and Rest valid.
- Canonical state verification: valid with no failures; legacy sources unchanged.
- State discovery without legacy environment variables succeeded from both the
  active migration worktree and the divergent primary checkout. Both resolved
  `%LOCALAPPDATA%\MiraCore` and found choice, cadence, mentorship, archive, and
  Continuity available. Snapshot digests were `ad9a0253...3808f` and
  `3280cefa...e6728`, respectively.
- Full repository validation reached 1,592 passing tests, five skips, one
  deselection, and four failures. The remaining failures are outside this
  transition: a Moonshots manifest count expectation (29 versus 37), a stale
  library text-sources index, five stale Reality generated views, and a missing
  Learn From Choices wording assertion. Structural validation also reports the
  existing August 17–18 daily-source/link corpus failures. State, operational
  claims, skill contracts, recursive learning, Continuity, Journal, Archive,
  repository identity, obsolete-guidance, and voice-routing checks passed.

These remaining failures are recorded as the exact landed baseline, not silently
described as green. This operation did not repair the unrelated archive corpus,
generated views, or choice-language contract.

## Baseline acceptance measures

- zero wrong-repository or cross-scope mutations;
- zero unsupported equivalence claims among working-tree, committed, remote,
  and hosted state;
- a fresh snapshot before every consequential mutation;
- one action-capable transition per repository;
- exact closure or resumption for every qualifying cycle;
- canonical state discovery after restart from two clean checkouts;
- no state loss and no dependency on legacy environment variables;
- fewer unresolved registered worktrees after separately authorized cleanup.

Repository mutation status: working-tree document only. It has not been staged,
committed, pushed, published, or admitted to recursive learning.

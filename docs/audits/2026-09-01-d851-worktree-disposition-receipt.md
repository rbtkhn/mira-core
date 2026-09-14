# d851 Worktree Disposition Receipt

Date: 2026-09-01

Status: `cleanup-disposition`

Repository: `C:/dev/mira-core`

Worktree under review: Codex worktree `d851/mira-core`.

Worktree HEAD: `634b18216657eb5455f3720c96d850a6b45f783a`

Worktree state: detached HEAD, dirty.

Authority boundary: This receipt records the cleanup basis for a later
worktree deletion decision. It does not stage, commit, push, publish, ingest
Archive material, admit library metadata, assess reality claims, or authorize
future deletion by itself.

## Cleanup Actions Already Completed

- Removed clean registered worktrees:
  - `C:/dev/mira-core-sync-nate-20260829`
  - `C:/private/mira-core-temp/push-validate-7f611b14`
  - `C:/private/mira-core-temp/push-validate-d4d16d44`
- Removed the registered singularity worktree:
  - Codex worktree `mira-core-singularity-cadence-publication-20260828`
- Preserved the singularity branch ref:
  - `codex/singularity-cadence-publication-20260828`
- Recovered the salvageable `VER-20260818-01` requested/uninvestigated
  reality-check files into the current worktree.
- Copied private library text payloads from `d851` into the configured AppData
  text store:
  - 132 registered Colonial payloads
  - 302 verifier-reported Ancient/Medieval payloads

## Verification Evidence

After private payload repair:

```json
{"checked":550,"failures":[],"missing":23,"status":"passed"}
```

The `missing: 23` field was retained verbatim from the tool output. Because
`failures` is empty and `status` is `passed`, it appears stale or semantically
different from current missing-file count.

Focused Colonial check after copy:

```text
COLONIAL_ITEMS=132
COLONIAL_MISSING_AFTER_COPY=0
```

## Remaining d851 Dirty State

At the final safety check, `d851` still had 246 dirty Git entries:

```text
?? 226
M   17
 M   3
```

Top-level grouping:

```text
archive                 207
narrative-geopolitics    23
scripts                   7
tests                     5
docs                      4
```

The staged control-plane changes were inspected and classified as mostly
already landed or superseded on current `main`. The untracked library artifacts
were classified as older proposals, receipts, metadata packets, inspection
records, and planning controls whose admitted body IDs are already represented
in current `archive/library/library-registry.json`.

## Disposition

`d851` is no longer preservation-critical for private library payloads. It can
be removed only if the operator explicitly chooses to abandon its remaining
dirty Git state, including staged changes and untracked receipt/proposal
history.

Recommended deletion boundary: remove the registered worktree only, leaving
remote/local branch refs untouched unless a separate branch-ref cleanup is
authorized.

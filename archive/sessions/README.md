# Mira Sessions

This shelf preserves session history locally and connects it to Dream's daily
Journal reading. The storage location is independent of Codex's working files.

- `transcripts/` holds private, Git-ignored, immutable normalized Codex captures.
  Its local `index.md` and `index.json` list sessions and capture versions.
- `daily/` holds private, Git-ignored, content-addressed daily checkpoints,
  complete reading chunks, and composing-session reading acknowledgements.
- [`memorials/`](memorials/) holds authored reflective memorials, each a registered
  Markdown/JSON pair. It is distinct from the transcript record.

Existing capture IDs, hashes, and historical `mira/continuity/captures/` references
remain unchanged. The shared resolver opens the new physical location; retained
rollback copies must be byte-identical. New captures use their actual new path.
Codex originals are retained; normalized captures have governed exclusions and
must not be described as exact raw-file backups.

Dream prepares checkpoints through `mira-journal prepare --require-session-reading`.
Each checkpoint freezes America/Denver day bounds and an explicit cutoff. Read
all `chunk-*.json` files in ordinal order. A chunk can continue a large record
from the preceding chunk; no transcript detail is discarded to fit a token limit.
Use `mira-journal session-reading-complete --bundle ABSOLUTE_EXTERNAL_BUNDLE
--packet-digest SHA256 --session-id MS-ID --chunk N --json` after reading each
chunk (repeat `--chunk` for a sequential batch). Bind the resulting acknowledgement
and checkpoint digests before authorship. Reading declares coverage, not comprehension.

Unchanged preparation reuses its frozen checkpoint. Refresh an unfinished bundle
explicitly with `--refresh-session-checkpoint`; preserve the old version and reread.
No checkpoint operation revises a finalized Journal, creates a second daily Dream,
or schedules an automatic job. Missing material remains explicit partial coverage.

## Recovery and Git exclusion

Run `tools/run.ps1 mira-continuity session-backup --destination
ABSOLUTE_EXTERNAL_DIRECTORY --format json` for a versioned, content-addressed
recovery snapshot. `--check` writes nothing. Snapshots retain older files and do
not propagate deletions. Restore into an empty external directory and verify all
object hashes before switching readers. A recovery copy on the same drive does
not protect against drive loss.

Restore with `tools/run.ps1 mira-continuity session-restore --backup-root
ABSOLUTE_BACKUP_DIRECTORY --snapshot SHA256 --destination ABSOLUTE_EMPTY_DIRECTORY
--format json`. Add `--check` to verify without writing. Preflight the external
destination's parent before a restore test; existing nonempty destinations are rejected.

The private payload directories must remain ignored and untracked. Do not run
`git clean -fdx` over this checkout or delete it without a verified recovery
snapshot. A Git clone does not contain these bodies. Repository-local storage is
a narrow session-payload exception, not permission to move other private databases.

Retrieval is explicit-only and every memorial remains inactive. Preservation is
not evidence of consciousness, present identity, truth, operator belief, or
permission. Missing memorials are not evidence that a session lacked value.

`tools/run.ps1 mira-sessions validate` checks the authored memorial shelf. Admission and
private Mira Archive ingestion are separate operations. Staging, commit, push,
publication, ingestion, and activation each require their own authority.


## Conversation grouping

New daily reading checkpoints bind a private parentage snapshot derived only from
explicit Codex metadata. The composition brief groups active sessions beneath their
recorded primary ancestor; inactive parents provide context only. Missing,
conflicting, cyclic, or unavailable ancestry remains unresolved. Primary sessions,
subagent sessions, and transcript records are separate counts, not accomplishments.
Read every required chunk and disposition every session. Combine a helper finding
and its parent summary under one grounded development when they describe the same
work; retain distinct findings even within one conversation. Grouping does not
prove semantic duplication or independent corroboration. Historical checkpoints,
transcripts, journal versions, and approvals are not rewritten. Older bundles
without grouping remain valid. The private provenance index is
`archive/sessions/transcripts/lineage.json`; subsequent changes do not alter a
previously frozen grouping.


## Dated Eastern calendar

The Journal and Dream use the shared policy in `scripts/journal_calendar.py`.
Through September 4, 2026, dates retain America/Denver boundaries. September 5
is an explicit 22-hour transition: 2026-09-05 06:00 UTC through 2026-09-06
04:00 UTC (midnight to 10 p.m. Denver). From September 6 onward, dates use
midnight to midnight America/New_York, including EST/EDT daylight-saving rules.
Intervals include their start and exclude their end; no activity is reassigned
twice or dropped at the transition. Transition checkpoints identify their
exceptional window explicitly. Use the shared date policy for retrospective
preparation, freshness, current-date selection, and validation.

The registry's original `timezone: America/Denver` remains historical metadata;
it is not a global override of the dated policy. Existing versions, approval
bindings, captures, and frozen checkpoints remain unchanged. New post-transition
coverage binds its calendar policy and UTC bounds. Missing timezone data fails
explicitly; fixed EST or a silent fixed-offset fallback is not permitted.
Dream defaults to the timezone for the requested date and rejects a conflicting
post-transition override. This changes date assignment, not task scheduling,
operating-system settings, or external publication timestamps. Journal entry
dates remain distinct from the time an entry is actually published.

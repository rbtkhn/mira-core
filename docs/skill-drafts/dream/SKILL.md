---
name: dream
description: "Consolidate one local day of mira-core sessions into a private advisory learning handoff. Use when the operator says dream or requests a daily recursive-improvement rollup."
---

# Dream

Use only in `mira-core`. Bare `dream` is the daily-close conductor. Dream owns
daily completion for the selected date: if manifest-backed Geo-Strategy sources
exist and the issue packet is missing, Dream completes the Geo lane before
continuing. If the generated Geo packet exists but is analytically imperfect or
fails deterministic issue validation, Dream records explicit next-day revision
debt and continues the closeout rather than pausing. Journal composition is an
internal Dream stage: Dream prepares the complete daily census, reads the
bounded Mira Letters orientation since the previous canonical Dream
finalization, then hands the prepared bundle to the current agent for Mira
Journal composition under Mira Voice, validates, and finalizes without an
operator approval prompt. Journal
canonicalization failures still block with repair guidance and never create
fallback prose or a partial canonical entry.
Run one canonical Dream consolidation per operator, workspace, and local
calendar day. Individual sessions contribute bounded closeout receipts; Dream
consolidates all sessions active that day. Dream records advisory cadence state
in the configured private append-only ledger, never research evidence. It does
not overwrite prior episodes.

Dream's highest-leverage output is useful integration for tomorrow's workflow.
Optimize first for workflow throughput: reduce rediscovery, sharpen next
actions, classify residue before it becomes vague obligation, and convert the
day into usable leverage without multiplying repo-tracked artifacts. Dream's
brilliance is not volume; it is preserving mode, owner, authority, and evidence
class while showing how the day's parts work together.

## Distill

Start or resume the conductor with:

```text
tools/run.ps1 dream --date YYYY-MM-DD --json
tools/run.ps1 dream --resume DCR-ID --date YYYY-MM-DD --json
```

Use `--check` for a read-only projection: it reports when Geo-Strategy will be
completed during execution, but writes nothing. Completed stages are immutable.
When the date's Geo-Strategy packet already exists and validates cleanly, Dream
certifies it from the best available receipt: committed bytes when present, or
Dream close authority when uncommitted. When manifest rows exist and the packet
is missing, Dream runs `synthesis --date YYYY-MM-DD --execute`, validates the
issue stage, and certifies the Geo stage as `dream_completed_packet` when clean
or `provisional_packet_with_revision_debt` when an issue artifact exists but
validation is not clean. A date without manifest-backed Geo sources records
`no_geo_run`. Dream prepares the private Journal bundle and may return
`composition_required` as an agent-internal handoff to write `draft.md`,
`draft.json`, and `technical-reference.json` from the prepared bundle
contracts. When this handoff is prepared, Dream also writes an adjacent private
`roi-synthesis.json` packet for next-day leverage. That packet may include Dev
Journal candidates, Note candidates, Coffee handles, publication debt, workflow
improvements, and open obligations, but these are candidates only. Mira Journal
remains the only autobiographical prose artifact Dream automatically finalizes. The ROI packet
must not create repo-tracked drafts, admit Notes or Dev Journal entries, stage,
commit, push, publish, contact anyone, or satisfy Coffee's later grounded
action surface. That handoff is not an operator-facing approval lane, and it is
not permission to abandon the Dream cycle. After composition, Dream runs prose,
grounding, temporal-position, adjacent-entry originality, full-bundle, and
finalization checks. A passing bundle is canonicalized as private
`dream-eod-v1` with `publication_eligible: false`; Dream is the finalizing
conductor and Mira is the recorded author. Finish with a private `--dream-json`
candidate or `--no-candidate REASON`.

The private Journal bundle may include `letters_orientation`: full Mira Letter
bodies preserved after the prior canonical Dream `approved_at` timestamp and at
or before the current preparation cutoff. Dream may use this reading to orient
relational residue, draft obligations, replies, live curiosities, and tomorrow's
posture. Letters remain relational orientation only; they do not establish
Journal ancestry, factual evidence, delivery authority, publication authority,
permission to contact anyone, or commitments. Unsent drafts stay explicitly
unsent.

When `letters_orientation` includes unsent drafts, Dream must treat them as
prepared address, not completed relation. An unsent Letter may orient Journal
composition when it reveals responsibility gathering toward a named recipient, a
reply not yet made, a draft requiring revision, or a restraint that must survive
into tomorrow. Dream must not treat an unsent Letter as evidence that contact
occurred, mentorship was enacted, a reply was received, or a commitment was
made. Preserve the draft as relational residue under boundary: real as inward
posture, incomplete as outward act.

The private ROI synthesis packet has this required shape:

- `schema_version`
- `dream_date`
- `generated_at`
- `optimization_target: workflow-throughput`
- `source_refs`
- `sections`
- `authority_boundary`

The `sections` object must include `dev_journal_candidates`,
`note_candidates`, `coffee_handles`, `publication_debt`,
`workflow_improvements`, and `open_obligations`, even when a section is empty.
Nominate Dev Journal candidates only for major architecture, design, validation,
or governance decisions. Default to no candidate when rationale is trivial or
already well captured. Mark retrospective candidates separately when the source
basis is after-the-fact, and distinguish documented fact from reconstruction.
Coffee handles should carry a compact morning claim-testing surface: what
survived discontinuity, what mode it appears to be in, and what the next
grounded test might be. Publication debt and open obligations preserve their
own authority boundaries and never become action authority merely by appearing
in Dream.

Dream's Geo completion authority grants no staging, commit, push, publication,
forecast resolution, operational-truth assignment, verification admission,
communication, RSI admission, or identity-promotion authority. Complete the
daily cycle first; revise next day if necessary.

Before inheriting a Geo-Strategy prerequisite, run a read-only freshness gate
over `narrative-geopolitics/work/daily`. If any later substantive Geo packet
exists after the prerequisite date, mark the prerequisite `needs-refresh` unless
the owning bundle was rerun after that later packet. For due forecast hooks
surfaced by the latest Geo packet, split debt into `verification-required`,
`posture-review`, and `not-yet-due`:

- `verification-required`: resolution depends on an operational claim, `OPC-*`,
  `VER-*`, or contested source assertion.
- `posture-review`: resolution depends on public, official, or later-archive
  posture signals and no operational-claim dependency is admitted.
- `not-yet-due`: the hook is open but outside the current review boundary.

Dream must not let forecast verification debt block closeout. It may inherit
when the Geo packet exists and its deterministic issue validation is accepted;
due verification or posture-review hooks are carried as visible nonblocking
debt and must not be silently treated as resolved. Report the gate in this
compact form:

```text
geo_prerequisite_status: current | needs-refresh | open-but-bracketed
due_forecast_debt: verification=N posture_review=N not_yet_due=N
safe_to_inherit: yes
next_action: rerun-owning-bundle | open-verification-packet | posture-review | proceed
```

Inventory the day's active sessions first. Give every known session an explicit
`included`, `excluded`, or `unavailable` coverage receipt with a reason and
observation time. Mark the rollup `partial` whenever any session is unavailable;
missing coverage is visible and never treated as evidence that no work occurred.

Identify exactly one bounded experiment from the consolidated day and classify its
outcome as `improved`, `no_change`, `regressed`, or `inconclusive`. State:

- the experiment;
- one evidence-backed lesson;
- one candidate method change;
- a bounded evidence summary containing the decisive counts or observations;
- one or more repo-relative artifact references supporting the summary;
- one sentence describing what tomorrow inherits.

Also state a stable experiment-series and episode ID, narrow observation and
diagnosis, proposed-intervention digest, observable with
unit/baseline/threshold/source, falsifier, intended next-use task class,
timezone-aware expiry, claimed artifact relationships, and relevant paths. If
no meaningful experiment occurred, record `no_cadence_worthy_experiment`
without manufacturing a candidate.

The corresponding low-level receipt is `cadence dream-closeout`; it records a
daily closeout without creating a candidate episode.

The daily key is `(workspace_id, operator_id, dream_date)` in the named IANA
timezone. Repeating an identical command is idempotent. A second canonical
Dream for that key fails closed. A failed or interrupted run may resume through
its idempotency key. Late session receipts require a separately authorized
append-only supplement or explicit supersession; never rewrite the daily body.

Append a late receipt with:

```text
tools/run.ps1 cadence dream-supplement --episode-id ID --session-coverage-json JSON --idempotency-key KEY --expected-version VERSION
```

Do not call a change `improved` merely because tests pass. It must improve a
named judgment, quality, reliability, or efficiency criterion.
Journal finalization records the canonical prose and technical reference with
the composing model and Dream run provenance. Late substantive work is retained
as append-only close coverage for the next day; it never silently revises the
finalized entry.

Do not solicit or record unresolved choice outcomes during closeout. Route
them through the next `coffee` re-entry instead.

## Verify and persist

Run:

```text
tools/run.ps1 cadence dream --workspace-id ID --operator-id ID --dream-date YYYY-MM-DD --timezone IANA_NAME --coverage-status complete|partial --session-coverage-json JSON --series-id ID --episode-id ID --experiment TEXT --outcome OUTCOME --lesson TEXT --observation TEXT --diagnosis TEXT --improvement TEXT --method-version-digest SHA256 --expected-observable TEXT --observable-unit TEXT --observable-baseline TEXT --success-threshold TEXT --observation-source TEXT --falsifier TEXT --next-use TEXT --task-class TEXT --expires-at RFC3339 --evidence-summary TEXT --artifact-ref PATH --tomorrow-inherits TEXT --idempotency-key KEY --json
```

For a profiled experiment, add `--profile PROFILE` and provide an externally
preflighted root through `--temp-root ABSOLUTE_PATH` or
`MIRA_CORE_SESSION_TEMP_ROOT`. Dream persists before the profile begins and
again after it finishes. A passing profile may grant local-use eligibility;
Dream never runs repository-wide verification automatically. An unprofiled
Dream is persisted as advisory state with local-use and repo-use blocked.
Structured verification results must retain the raw output tail and identify an
owner and next action for every non-passing result.

Repeat `--artifact-ref` when needed. The command rejects missing, absolute, or
repository-escaping references and requires `MIRA_CORE_CADENCE_DB` or `--db`
to resolve to an absolute private path outside Git. Legacy schema-v2/v3
handoffs remain explicitly importable for one compatibility release, but Dream
no longer writes `last-dream.json`. Failed, unavailable, timed-out, or
interrupted profile verification is retained without erasing the candidate.

Promote repository use only through the separate explicit command:

```text
tools/run.ps1 cadence promote --temp-root ABSOLUTE_PATH --json
```

Promotion uses the content-addressed full-validation cache when valid. Use
`--force` only when a fresh structural and pytest run is intentionally required.
Local-use eligibility never grants repo-use or public-use.

## Return

On successful close, report only the Journal title and version, validation
result, finalization state, and genuine remaining debt. Do not duplicate or
summarize the entry. Never infer permission to stage, commit, push, publish,
change forecasts, or run intake.

## Daily session checkpoint

Dream preparation requires `--require-session-reading` in addition to full prior
Journal reading. Preserve eligible session activity into `archive/sessions/transcripts/`
and bind a frozen, content-addressed checkpoint in `archive/sessions/daily/` before
composition. Read every chunk in ordinal order; acknowledge with `mira-journal
session-reading-complete --bundle ABSOLUTE_EXTERNAL_DIRECTORY --packet-digest SHA256
--session-id MS-ID --chunk N --json`. Repeat `--chunk` for sequential batches.
Bind `session_checkpoint_sha256` and `session_reading_ack_sha256` in draft metadata,
and `session_checkpoint_sha256` in the technical reference. Acknowledgement is
coverage, not comprehension. A new composing session rereads all chunks.

The bounded context packet is orientation only. Complete transcript chunks include
all eligible normalized records; token budgets cannot substitute synopses for reading.
Retain explicit missing-capture gaps and acknowledge partial coverage in metadata
with `session_coverage_gaps_acknowledged: true`.

Unchanged preparation reuses its cutoff and bundle. Use `--refresh-session-checkpoint`
only for an explicit unfinished-bundle refresh; older checkpoints remain immutable.
Before-midnight coverage means through-cutoff, not a complete calendar day. Skipped
days may be reconstructed by an explicitly requested retrospective Dream. Finalized
days are never rewritten; existing supplement authority and late-coverage rules apply.
No automatic capture schedule or new daily-close authority is created.


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

Strategy Notebook is a Dream-composed expert estimate, not a Geo prerequisite
and not a canonical autobiographical artifact.

## Geopolitics directory compatibility

For current filesystem operations, resolve domain paths through the shared
`repository_paths.resolve_geopolitics_reference` helper. It accepts the legacy
`narrative-geopolitics/` spelling and the `geopolitics/` spelling and selects
exactly one existing domain directory. Examples below or above using the legacy
spelling remain compatibility references; they do not authorize a directory
move. Preserve historical IDs and stored/hash-bound references. The source
archive remains at `archive/sources/geopolitics/`.

## Library-informed cognitive development

Apply the bounded cognitive-development cycle during the agent-internal composition handoff and preserve its nonblocking debt in closeout.
Follow the shared [composition and nomination contract](references/cognitive-development.md).

## Daily Library growth and recursive curiosity

Follow the active [daily Library growth contract](../mira-read/references/daily-library-growth.md).
Substantive Mira Read close may save qualifying ordinary idea notes locally as
works in progress. No draft-note state, daily catch-up debt, or publication
authority is created. Independent notes and essays are distinct from governed
revision lineage; Dream and strategic nominations remain nomination-only.
Retrieve prior applications and corrections before reuse. Missing analysis or
no qualifying new note never blocks Dream. Development requires later evidence.

## Expected learning and later usefulness

Use the shared daily Library growth contract for immutable private pre-reading
expectations and exact-version curiosity reviews in later application entries.
Retrieve relevant unsuccessful reviews and corrections before choosing another
reading; explain their effect on the choice. Missing expectations and pending
outcomes remain nonblocking. Daily note production is not a question-selection
reward or recursive-learning outcome. Reopening conditions on parked questions
create no task, scheduler, or automatic policy change.

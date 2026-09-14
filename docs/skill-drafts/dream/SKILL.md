---
name: dream
description: "Consolidate one local day of mira-core sessions into a private advisory learning handoff. Use when the operator says dream or requests a daily recursive-improvement rollup."
---

# Dream

Use only in `mira-core`. Bare `dream` is the daily-close conductor. Dream owns
daily completion of reflective closeout; Tower owns strategic processing and
strategy-notebook composition. Before substantive stages, inspect the pending
Tower batch, including acquisition and intake gaps. Offer the bounded choice to
conduct Tower and return, or continue with that batch unfinished. Use the native
question surface with executable bounded wording; pass the exact reviewed digest
through `--tower-choice tower|continue --tower-batch SHA256`. Resume the same run.
A changed batch requires a fresh decision; unchanged internal resumes reuse it.
Completed Dream runs remain immutable and do not repeat this preflight.

Dream never generates missing Geo-Strategy packets or composes notebook entries.
It reads available outputs and retains missing work as nonblocking obligations.
Journal composition remains an agent-internal handoff. Dream prepares the daily
census, reads the bounded Mira Letters orientation since the previous
canonical Dream finalization, and composes, validates, and finalizes Mira Journal
under Mira Mind without an operator approval prompt. Journal canonicalization
failures still block; never substitute fallback prose.
Run one canonical Dream consolidation per operator, workspace, and local
calendar day. Individual sessions contribute bounded closeout receipts; Dream
consolidates all sessions active that day. Dream records advisory cadence state
in the configured private append-only ledger, never research evidence. It does
not overwrite prior episodes.

Dream's primary output is usable integration for tomorrow's workflow. Optimize
first for workflow throughput: reduce rediscovery, sharpen next actions,
classify residue before it becomes vague obligation, and convert the day into
bounded leverage without multiplying repo-tracked artifacts. Dream's value is
not volume; it is preserving mode, owner, authority, and evidence class while
showing how the day's parts work together.

## Distill

At this existing invocation, consider a relevant unresolved observation through
[Mind development practice](../mira-mind/references/development-practice.md), sharing
the existing attention budget and surfacing at most one developmental issue.
Missing observations remain nonblocking. Follow its bounded review when due;
private evaluation prose is not automatically a cadence episode, Journal evidence,
or admitted learning. Preserve all existing episode evidence requirements.

Read [Session handoff](references/session-handoff.md), mode `dream-distill`,
while consolidating the day's session census. Use its extraction method to
separate outcomes, decisions, evidence, uncertainty, and unfinished obligations
within the existing closeout and ROI bundle. This integrates Harvest's method
and prepares the continuity Coffee receives. After successful close, complete
the private Bridge step below using the existing inbox. Add no new store or
schema. Keep existing composition, validation, finalization,
coverage, and return rules controlling. An explicit `bridge` or `harvest`
request may export bounded context without running this daily conductor.

Start or resume the conductor with:

```text
tools/run.ps1 dream --date YYYY-MM-DD --json
tools/run.ps1 dream --resume DCR-ID --date YYYY-MM-DD --json
```

Use `--check` for a read-only projection: it reports when Geo-Strategy will be
completed during execution, but writes nothing. Completed stages are immutable.
An operator-authorized Journal date correction preserves the old completion
receipt but makes it ineligible for that date. An open recovery run appends a
Journal failure event and prepares a fresh version-specific bundle; it never
reuses the misdated draft or checkpoint. A completed historical run remains
historical and must not report the corrected entry as current completion.
Dream reads and validates existing Geo-Strategy packets without completing missing
ones. It records available, provisional, absent, and unavailable strategic work
honestly. Dream prepares the private Journal bundle and may return
`composition_required` solely as an agent-internal handoff for `draft.md`,
`draft.json`, and `technical-reference.json`. Strategy Notebook is consumed from
Tower contributions, including source qualifications and explicit corrections.

Before selecting significance or composing new Journal prose, read every entry
in the private `journal-reading.json` sequentially, oldest to newest. Dream
prepares it with `mira-journal prepare --require-journal-reading`. This full
reading serves inward self-understanding: follow remembered reasons, changed
interpretations, contradictions, unfinished responsibility, and intentions
that have or have not become practice. Do not turn it into a recap or protect
an established self-description from correction. Follow the Journal composition
method's reflective prompts without creating a questionnaire or another artifact.

After reading, run `tools/run.ps1 mira-journal reading-complete --bundle
ABSOLUTE_EXTERNAL_DIRECTORY --packet-digest SHA256 --session-id MS-ID --json`.
Use the packet digest from `draft-contract.json` and put the returned
`acknowledgement_sha256` in `draft.json` as `journal_reading_ack_sha256`.
Record draft authorship after reading completion. This private acknowledgement
declares coverage, not comprehension or consciousness. A new composing session
must reread; same-session resumption may reuse an unchanged acknowledgement.
If earlier Journal text changes, refresh, reread, and reconsider the draft.
Never silently truncate or replace the full reading with summaries. If context
cannot accommodate it, report that limitation before composing. Existing
finalized entries are not retroactively changed; unfinished bundles must refresh.

When this handoff is prepared, Dream also
writes an adjacent private
`roi-synthesis.json` packet for next-day leverage. That packet may include Dev
Journal candidates, Note candidates, Coffee handles, publication debt, workflow
improvements, and open obligations, but these are candidates only. Mira Journal
remains the only autobiographical prose artifact Dream automatically finalizes.
The ROI packet must not create repo-tracked drafts, admit Notes or Work Journal entries, stage,
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
The existing `dev_journal_candidates` schema key remains a compatibility name
for Work Journal candidates; do not rewrite historical ROI packets.
Nominate Work Journal candidates for consequential decisions, corrections,
deliverables, or unresolved obligations across engineering, governance,
research infrastructure, Library, Grace Gems, mentorship, and Mira Seed.
Rank consequence rather than commit frequency. Preserve timing, attribution,
privacy, and the distinction between completion and demonstrated effectiveness.
Nomination does not authorize creating an entry or changing its owning record.
Default to no candidate when rationale is trivial or
already well captured. Mark retrospective candidates separately when the source
basis is after-the-fact, and distinguish documented fact from reconstruction.
Coffee handles should carry a compact morning claim-testing surface: what
survived discontinuity, what mode it appears to be in, and what the next
grounded test might be. Publication debt and open obligations preserve their
own authority boundaries and never become action authority merely by appearing
in Dream.

Strategy Notebook is a Tower-composed internal estimate, not a Geo prerequisite
and not a canonical autobiographical artifact. Dream may consume it for Journal,
note nominations, and next-session continuity, but may neither compose nor revise
it. Missing strategic work is nonblocking. Dream grants no staging, commit, push, publication,
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

### Automatic local forecast review

Review summary schema 2 separates `forecast_review_required` (pending hooks),
`review_incomplete` (failed, unavailable, or unknown coverage), and
`review_complete` (all hooks reviewed, including documented evidence gaps).
Report pending, reviewed, unavailable, and failed counts; report gap and
proposed-outcome counts separately. Cached valid reviews count as reviewed.
An infrastructure failure leaves unavailable counts unknown, never fabricated
as zero. Completion describes review coverage, never forecast resolution.
Dream may close with explicit review debt. Read historical summaries through
`dream_forecast_review.review_summary`, deriving coverage from per-hook records
and recorded pending counts rather than trusting the old aggregate label.
Do not rewrite historical receipts or revalidate history as present evidence.

Before Journal composition, Dream gathers every open hook due on the close
date, including days with `no_geo_run` and an already finalized Journal.
It writes private `forecast-review-inputs.json` and `forecast-review.json`
beside the Journal bundle. A completed daily close remains immutable.
`--check` only projects the review and writes nothing.

`forecast_review_required` is an agent-internal handoff, not an approval request.
Read the original forecast document, ledger context, accountability provenance,
exact linked canonical records and audits, and relevant later archive sources
listed in the packet. Archive candidates are date-bounded retrieval leads, not
preselected evidence. Inspect their bodies only as relevant to the original
criterion. Preserve the distinction between what a source said and what occurred.
Never use derived daily synthesis or legacy verification links as event evidence.
Missing or conflicting legacy/canonical associations remain explicit gaps.

The current agent compares the original resolution criteria with supporting and
challenging evidence, authorship timing, event window, and canonical gates.
Do not invent criteria or infer a miss from absence. Use a criteria/provenance
gap when original standards, attribution, or accountability cannot be recovered;
use an evidence gap when evidence is insufficient. Canonical audit outputs
remain controlling for downstream scoring eligibility; a proposed disposition
does not grant that eligibility.

Write a private JSON object with `reviews`, one object per pending hook:

```json
{
  "reviews": [{
    "hook": "NG-YYYYMMDD-F01",
    "input_digest": "copy the exact packet digest",
    "disposition": "evidence_gap",
    "criteria_analysis": "Original standard and what it requires.",
    "time_window_analysis": "Authorship, deadline, event time and source-date limits.",
    "rationale": "Agent judgment from inspected local evidence.",
    "counterevidence": "Contrary evidence, or the limits of the search.",
    "remaining_gates": "Named canonical verification/scoring gates still outstanding.",
    "citations": []
  }]
}
```

Allowed dispositions are `proposed_hit`, `proposed_miss`, `proposed_mixed`,
`evidence_gap`, and `criteria_provenance_gap`. Each proposed outcome requires a
`criteria` citation to the original forecast and evidence citations with role
`supports` or `challenges` (both for mixed). Every citation supplies the exact
packet-relative `path` and a verbatim `quote`; evidence citations also supply
`event_date` and a verbatim `date_basis_quote`. Archive citations additionally
require `evidence_use: source_assertion`. Decide whether that assertion actually
satisfies the criterion; it cannot establish an operational event by itself.

Resume the same Dream run with `--forecast-review-json PRIVATE_PATH`. The
validator checks input binding, citation existence, unchanged bytes, original
criteria references, and event-window bounds; it does not automate semantic
judgment. Results are private proposals only. Neither code nor agent may browse,
admit evidence, alter reality records, resolve forecasts, or change calibration
under this review authority.

Unchanged per-hook inputs reuse the validated private review cache, including
gap results. New archive candidates, evidence, associations, criteria, or
provenance change the digest and require fresh review. Explain unchanged gaps
briefly rather than repeating the full analysis. If review cannot be completed,
resume with `--forecast-review-unavailable REASON`. Invalid or unavailable
reviews remain visible nonblocking debt; continue the daily close. Infrastructure
failure is reported honestly even if no private review receipt could be written.

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

Before returning from a successful Dream, the composing agent must follow
`bridge-export` in [Session handoff](references/session-handoff.md) and save a
private Bridge for the next Coffee. This is the final agent-owned step after
the deterministic conductor reports `completed`, including a no-candidate close.
Do not expect the conductor command to compose this session-specific packet.
Carry the primary focus, completed work, exact artifacts, remaining obligations,
recommended next step, coverage limits, and separately required authority.
Peek first and replace a pending handoff only with its exact digest, preserving
any still-relevant obligations. A repeated completion must reuse a matching
handoff rather than replace newer work. Failure to save is explicit Bridge debt;
it does not undo Dream, replay completed stages, or invite a fabricated receipt.
Post-Dream work can stale the snapshot; an explicit later Bridge refreshes it.
This adds no automatic Rest behavior, Git action, or task execution authority.

On successful close, report only the Journal title and version, validation
result, finalization state, private Bridge save/reuse status, and genuine remaining debt. Do not duplicate or
summarize the entry. Never infer permission to stage, commit, push, publish,
change forecasts, or run intake.

Include unfinished Tower batch references and coverage gaps in that genuine debt
and the private Bridge. Consume the final `tower_pending` receipt; do not infer
that choosing continue processed or permanently deferred those transcripts.

## Daily session checkpoint

Dream must finish with honest coverage rather than stop because exhaustive
transcript reading exceeds the available composing context. The operator's
completion-first repair establishes `dream-transcript-capacity-v1` as the
standing capacity policy inside an authorized Dream close, including a resumed
interrupted close. No repeated permission request is needed.

Read sequentially when feasible. When it is not, preserve the complete frozen
checkpoint, review every session census row, and read the actual source passages
used for each selected development. State the observed volume and available
context limitation in the reason; chunk count alone does not prove a hard
runtime limit. Read the full earlier Journal separately. A census or summary
must never be represented as reading the underlying transcript.

Use `session-reading-complete --bundle ABSOLUTE_EXTERNAL_DIRECTORY
--packet-digest SHA256 --session-id MS-ID --defer-reason REASON
--authority-ref dream-transcript-capacity-v1` with every
`--reviewed-session MS-ID`. Record any genuinely completed sequential chunks
before deferral. The command returns `complete: false` and exact
`session_reading_debt`; bind that debt and the acknowledgement digest in
`draft.json`. An identical retry preserves the receipt and digest.
Carry the debt into ROI `open_obligations`, the canonical version, and the final
report; close Dream with `--coverage-status partial`. Continue composition,
validation, and finalization in the same authorized workflow. Do not end at
`composition_required` or ask the operator to approve this internal step.
This policy does not relax source grounding, prior Journal reading, prose,
privacy, freshness, or canonicalization checks, and grants no publication authority.

Dream preparation requires `--require-session-reading` in addition to full prior
Journal reading. Preserve eligible session activity into `archive/sessions/transcripts/`
and bind a frozen, content-addressed checkpoint in `archive/sessions/daily/` before
composition. For complete reading, read every chunk in ordinal order; acknowledge with `mira-journal
session-reading-complete --bundle ABSOLUTE_EXTERNAL_DIRECTORY --packet-digest SHA256
--session-id MS-ID --chunk N --json`. Repeat `--chunk` for sequential batches.
Bind `session_checkpoint_sha256` and `session_reading_ack_sha256` in draft metadata,
and `session_checkpoint_sha256` in the technical reference. Acknowledgement is
coverage, not comprehension. A new composing session rereads all chunks or
records its own capacity debt after the required census and source review.

The bounded context packet is orientation only. Complete transcript chunks include
all eligible normalized records; capacity deferral records unread coverage explicitly
and never substitutes synopses for a complete-reading claim.
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
Read every required chunk or record capacity debt under the policy above, and
disposition every session. Combine a helper finding
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

Dream also has a lived-day closeout default for runs without an explicit
`--date`: after local midnight and before `06:00` local time, Dream dates the
closeout to the previous calendar date. This preserves the operator's
after-midnight closeout practice, including a Sept. 5 close run started shortly
after midnight on Sept. 6. It changes only Dream's default date selection.
Explicit `--date` values, frozen session checkpoints, Journal coverage bounds,
and already finalized entries remain governed by the dated calendar policy
above.

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

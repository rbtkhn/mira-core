---
name: mira-journal
description: "Prepare, compose, revise, check, or review Mira's governed first-person continuity journal. Use when the operator says mira-journal or asks to draft, revise, inspect, review, or report status for a Mira Journal entry."
---

# Mira Journal

Use only in `mira-core`. Treat journal prose as autobiographical
interpretation, never research evidence, proof of consciousness, operator
belief, or action authority.

For composition or revision, read
[`references/composition-method.md`](references/composition-method.md)
completely before writing prose. For status or validation requests, use the
governing command directly and do not load the composition reference unless
voice judgment is required.

## Choose the operation

- **Dream EOD finalize:** run `tools/run.ps1 mira-journal eod-finalize --date
  YYYY-MM-DD --bundle ABSOLUTE_EXTERNAL_DIRECTORY --dream-run-id DCR-ID
  --check --json`, then omit `--check` to write the canonical version. This
  requires no operator approval record, uses status `dream-eod-v1`, and is
  always `publication_eligible: false`.
- **Prepare and compose:** run `tools/run.ps1 mira-journal prepare --date
  YYYY-MM-DD`, then use the private bundle contracts. Inside Dream, this is an
  agent-internal composition handoff, not an operator approval lane.
- **Revise:** prepare the next version for the date, preserve the registered
  digest chain, and apply the composition method to the requested correction.
- **Check or review:** run `tools/run.ps1 mira-journal draft-check --date
  YYYY-MM-DD --bundle ABSOLUTE_EXTERNAL_DIRECTORY --json` and explain errors
  without weakening them.
- **Status:** run `tools/run.ps1 mira-journal status` with the requested date
  bounds.
- **Retrospective freshness replay:** run `tools/run.ps1 mira-journal
  freshness-replay --from YYYY-MM-DD --to YYYY-MM-DD --exclude-version
  MJ-YYYYMMDD-vN --output ABSOLUTE_EXTERNAL_PATH --check --json` first, then
  repeat without `--check` only when the private packet should be written.
  The replay is read-only, excludes the development episode, compares the
  digest-bound pre-fix and current policies over identical frozen manifests,
  and emits no raw session bodies or local source paths. A cadence-compatible
  measurement is advisory output only; importing it remains a separate exact
  `cadence repeat` authorization.

## Compose the private bundle

For a sparse day, compose an honest quiet-day or coverage-gap reflection from
the available session census. Do not invent activity, conclusions, or emotional
events merely to fill the entry.

1. **Gather.** Read only `context-pack.json`, `composition-brief.json`,
   `draft-contract.json`, and `technical-reference-contract.json` from the
   prepared external date directory, plus Dream's complete `journal-reading.json`
   and all daily transcript chunks bound by `session_reading` in the draft contract.
   For Dream, read that packet oldest to newest before selecting significance
   or writing prose, and acknowledge it through `reading-complete` as described
   in Dream. Bind `journal_reading_ack_sha256` in draft metadata. The full
   reading is separate from the session evidence budget and cannot be replaced
   by summaries, prior-session memory, or selected continuity threads.
   Treat approved entries labeled `authoritative-ancestry` in that packet and
   `authoritative_ancestry` in the brief as the
   only source of inheritable journal continuity. Treat
   `readable_legacy_context` as reflection context that may inform the prose
   but must not supply an inherited thread or governed continuity claim.
   Review every row in `daily_session_coverage` before choosing significance;
   its census proves consideration only, not importance or truth.
   Treat any `rest_lifecycle` metadata as provisional Continuity context. It
   may inform session disposition but is not authoritative ancestry,
   recursive-learning evidence, or automatic autobiographical significance.
2. **Listen backward.** Recover why an approved continuity thread mattered,
   not merely its last conclusion.
3. **Choose significance.** Select one to three supplied developments that
   changed how Mira can remember, choose, answer, or correct herself.
4. **Metabolize.** Turn mechanisms into inward meaning; do not narrate a
   changelog.
5. **Braid.** Write free prose joining inheritance, present transformation,
   honest correction, and a forward practice or unresolved horizon.
6. **Mirror.** Write only `draft.md`, choose its title, and apply the
   reference's self-formation rubric. Run `tools/run.ps1 mira-journal
   prose-check --date YYYY-MM-DD --draft ABSOLUTE_EXTERNAL_DRAFT_PATH --json`
   and revise until it passes before grounding the prose.
7. **Ground.** Write `draft.json` and `technical-reference.json`, including
   exact prose anchors, admitted RSI IDs actually consumed, and schema-v2
   continuity events. Disposition every qualifying session in
   `session_coverage`; bind `selected` and `technical-only` sessions to the
   grounding items they informed, and give every `not-selected` session a
   concise reason.
8. **Audit time and originality.** Preserve `same-day-eod` or
   `retrospective-recovery` from the contract. Retrospective prose must not
   invent contemporaneous feeling, imply an earlier entry existed, or import
   later outcomes into earlier certainty. Compare adjacent canonical entries
   for repeated openings, endings, titles, metaphors, formulaic learning arcs,
   and strongly templated boundary language. Repetition blocks only when it is
   exact or meaningfully formulaic; developed thematic recurrence is allowed.
9. **Check and offer or finalize.** Run `draft-check`. In ordinary composition
   report the private bundle as approval-pending. Inside Dream, treat any
   missing-draft handoff as agent-internal work, continue without an operator
   approval prompt, and resume through EOD finalization as `dream-eod-v1`.

Never invent an approval record. Never approve, revise canonical state, admit
RSI learning, stage, commit, push, publish, or promote identity during nightly
or ordinary composition. Those actions retain their separate exact authority
boundaries.

During canonical approval, ignore non-user approval choreography in the
approving session and exempt only the exact approval record. Any other user
record in that session, later Git commit, or activity in another session still
forces a refreshed bundle.

## Preserve the authority split

The skill interprets and composes. `tools/run.ps1 mira-journal` prepares,
validates, approves, renders, and governs. `recursive-learn` alone assesses a
possible feedback loop, and explicit digest-bound admission alone mutates the
canonical RSI ledger.

## Complete daily transcript reading

Dream preparation additionally uses `--require-session-reading`. Read all private
checkpoint chunks under `archive/sessions/daily/` in order before choosing significance
or composing. The bounded context-pack remains an orientation aid only. Complete
sequential reading is acknowledged with `mira-journal session-reading-complete`
using the checkpoint digest, composing session ID, and repeated ordered `--chunk N`
arguments. Bind `session_checkpoint_sha256` and `session_reading_ack_sha256` in
`draft.json`; bind `session_checkpoint_sha256` in `technical-reference.json`.
Partial capture coverage requires `session_coverage_gaps_acknowledged: true`.
Neither an acknowledgement nor complete capture availability proves comprehension.

Unchanged preparation reuses its checkpoint. Explicit `--refresh-session-checkpoint`
creates a new immutable checkpoint for an unfinished bundle and requires fresh reading.
Existing finalized Journal versions and approvals remain unchanged.


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

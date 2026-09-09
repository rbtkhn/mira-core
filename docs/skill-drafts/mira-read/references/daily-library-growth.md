# Daily Library growth: active local contract

Effective prospectively from 2026-09-09. The operator's recursive curiosity
means improving question selection through remembered results of earlier inquiry.
Aim for at least one new substantive Library note per calendar day. Notes are
always works in progress: there is no draft-note state or analytical finish gate.
One work can support many independent notes and essays; one artifact can explicitly
relate to several works. A new file is not necessarily a new idea.

## Reading and question selection

Before suggesting a reading, run Library Journal context and
`tools/run.ps1 strategy-notebook note-search --focus "QUESTION" --work-id WORK_ID --json`.
Inspect the strongest matches in full, including their limitations and prior
failed applications. Recommend one question by consequence, unresolved tension,
passage availability, and discriminating potential. No numerical optimality score.
Use approximately one in four completed encounters for unfamiliar promising
questions; the latest curiosity history informs this rolling preference. Operator
direction controls, and missed exploration creates no debt.

At substantive close, retain at most three consequential follow-up questions
inside the existing Library Journal thread, with one recommended. A question may
be open, answered, reframed, or parked. Parking is not unfinished work. Preserve
the selection reason and expected resolution; later results can change both.

## Bounded local save authority

A substantive Mira Read close authorizes a private Journal entry and direct local
creation or amendment of qualifying ordinary Library idea notes through the
closeout command. The operator's no-save instruction overrides both. Menus,
interruptions, incomplete readings, and mere retrieval create neither artifact.
This permission never invokes the `note this` Git shorthand. Essays require their
own explicit composition instruction. Governed cognitive notes still route through
Library Integration; strategic and Dream nominations remain nomination-only.

Search before authoring; amend for the same central question, create for a distinct
durable question. Explain the judgment; lexical matching is only a duplicate aid.
Preserve earlier reasons and objections in dated amendments. New prose must state
question, source passages, interpretation, strongest limitation, and next test.
Review quotation/privacy before saving: preserve source handles and attributed
context, never restricted source bodies or private conversation in tracked prose.
One encounter can save up to three substantive notes. No-note and amendment-only
closeouts are valid; give the reason. Daily shortfalls do not block Dream or create
catch-up obligations. Additional work requires a distinct substantive encounter.

## Runtime interfaces

Use the existing private Journal store and approved external temporary root. Run
session preflight before writing input. Prepare an agent-authored JSON object:

```json
{
  "entry": {
    "...": "all fields required by library-journal prepare",
    "curiosity": {
      "question": "The selected question",
      "why_selected": "Consequence or unresolved tension",
      "expected_resolution": "What the passage might distinguish",
      "thread_id": "LJT-existing-thread",
      "selection": "need",
      "followups": [
        {"question": "Next question", "status": "open", "thread_id": "LJT-existing-thread"}
      ],
      "recommended_followup": 0
    }
  },
  "mode": "normal",
  "note_disposition": "Why these ideas merit saving, or why no note is warranted",
  "notes": [{
    "operation": "create",
    "path": "archive/notes/library/topic-first-slug.md",
    "title": "A distinct idea",
    "question": "Its central question",
    "work_ids": ["CANONICAL_WORK_ID"],
    "source_ids": ["ENCOUNTER_PASSAGE_SOURCE_ID"],
    "interpretation": "Source-grounded authored reasoning",
    "limitation": "Strongest objection or uncertainty",
    "next_test": "Discriminating later test",
    "novelty_reason": "Why this is distinct from inspected notes",
    "inspected": [{"path": "MATCH_PATH", "sha256": "CURRENT_MATCH_DIGEST"}]
  }]
}
```

This is a shape example, not executable placeholder content. `selection` is need,
exploration, or operator. Empty followups omit `recommended_followup`. Every thread
must appear in the encounter's thread list. Resolve canonical works and admitted
source bodies through Library before composition. `notes: []` is valid.
For amendment set `operation: amend`, the exact `expected_digest`, and a
`change_reason`; keep the central question and target identity. Inspect all returned
top matches using current digests. Complete unchanged check then execution:

```text
tools/run.ps1 library-journal closeout --input ABSOLUTE_PRIVATE_JSON --check --json
tools/run.ps1 library-journal closeout --input ABSOLUTE_PRIVATE_JSON --json
```

The command validates sources, duplicates, paths, and stale targets, then saves
each note atomically and records one Journal entry. An identical retry reuses
embedded save identities and timestamps. If Journal recording fails after a save,
preserve the note and retry identical input; report the exact partial result.
Completed encounters replay recorded receipts without consulting current sources.
Changed inputs cannot silently revise a completed receipt.

## Artifact view, ownership, and density

The `library-artifact-v1` JSON envelope in a Markdown comment supplies explicit
`kind` (note or essay), `title`, `question`, `work_ids`, and `sources`. Notes created
by closeout also retain stable idea identity, save events, and body digest.
Separately authored essays may use the same envelope without note save events.
References in prose do not create bindings. Where a relationship matters, explain
how one idea supports, challenges, qualifies, or supplies a mechanism to another.

```text
tools/run.ps1 library-journal artifact-search --work-id WORK_ID --focus "QUESTION" --json
```

This rebuildable view reads notes and essays; it is not a registry, graph edge, or
operational eligibility decision. The governed work registry's `note_refs` remains
revision lineage, not an all-writing catalog. Do not migrate historical artifacts.
Legacy unbound notes remain discoverable through ordinary note-search, with work
association unrecorded. Keep each kind of content in its owner: ideas in notes,
encounters/applications in Library Journal, standalone arguments in essays,
strategic estimates in Notebook, and remembered practice in Mira Journal.

## Later application and evaluation

Review on relevant retrieval, counterevidence, or dependency change, not by daily
whole-collection ritual. Record substantive subsequent use as an existing Library
Journal application with predecessor thread, rejection condition, and separate
artifact. Optional `note_applications` rows contain `idea_id`, `note_ref`,
`application_ref`, `effect` (used, no-change, qualified, rejected, changed,
failed-transfer), and `reason`. Bind both refs in artifacts; the application ref
must be in `later_use_refs`. Mere retrieval cannot populate this field.
Optional `friction` prose records actual duplicated effort or unproductive review;
absence means not-recorded, not zero effort.

```text
tools/run.ps1 library-journal daily-growth --from YYYY-MM-DD --through YYYY-MM-DD --json
```

Report daily target/attainment, period monthly totals, distinct notes applied,
corrections with linked applications, and reported friction separately. First
successful local save earns credit on the shared Journal calendar; amendments,
essays, renames, retries, and rehearsals do not. A saved note awaiting Journal
recording is disclosed separately and counts only with intact embedded save data.
Old records lack retrospective save evidence: report not-recorded. Period monthly
totals cover only the requested dates; they are not necessarily whole months.
Do not calculate a reuse rate without an explicit observation window and eligible
cohort; this report deliberately supplies counts and examples, not a blended score.

After 30 days, `review_due` prompts assessment at an existing review occasion;
there is no scheduler. Examine fragmentation, reuse, question selection, and effort.
Propose adjustments without automatically changing policy. Invoke Recursive Learn
only for a concrete method improvement supported separately across all five stages.
Reading, note production, tests, and rehearsals do not demonstrate later outcomes.

## Compare expected learning with later usefulness

Before interpreting the selected passage, preserve one private expectation:

```text
tools/run.ps1 library-journal expect --input PRIVATE_JSON --check --json
tools/run.ps1 library-journal expect --input PRIVATE_JSON --json
```

Input contains `encounter_id`, `thread_id`, `question`, `why_selected`, `selection`
(need/exploration/operator), `expected_resolution`, `challenge` (an observation
that would challenge usefulness), nonempty `work_ids` and `source_ids`, and
`prior_exposure`. Use the same existing question-thread identity through reading
and application. For a new question, a new encounter may bind
`predecessor_checkpoint: {encounter_id, digest}`. `save_requested: false` prevents
saving. Runtime supplies recording time and digest; no supplied time establishes
prospectivity. The timestamp proves recording time, not unfamiliarity with a work.

The checkpoint lives at `expectations/<encounter-digest>.json` within the existing
workspace-bound private Journal store. It is immutable preparation, not a note,
completed encounter, or growth credit. Identical retries reuse it; changed content
requires a new encounter. Interrupted reading resumes the same checkpoint. No
checkpoint is retroactively attached to an already completed encounter.

Closeout accepts `entry.expectation_ref: {encounter_id, digest}`. Curiosity's
question, why_selected, selection, expected_resolution, and thread_id are populated
from the checkpoint; optional followups remain authored at closeout. Conflicting
copies are rejected. Missing checkpoints permit honest `expectation_status` of
unrecorded or retrospective. Do not silently downgrade an invalid claimed binding.
No expectation or unproductive inquiry blocks ordinary completion or Dream.

For later application, add optional `curiosity_review` to the existing application
entry. It contains `baseline: {entry_id, version, digest}`, the original
`expectation_ref` when present, and these prose fields: `expected` (exact original
expected_resolution, or not-recorded), `observed`, `next_choice`, `explanation`,
and `boundary_test`. Add `application_ref` from later_use_refs and `disposition`:
supported, partly-supported, not-supported, or not-yet-assessable. The baseline is
an explicit predecessor and need not have produced a note. Bind a separately
authored application artifact. Describe why its case tests a relevant boundary;
a new filename does not establish independence. Retain earlier versions and use
ordinary Journal correction rather than rewriting the expectation.

Context and prepare return at most three relevant comparisons with evidence
handles, gaps, and omitted version handles. Read corrections before reuse. Explain
briefly how the comparisons changed the next question or why they did not apply.
Do not mechanically select topics by note yield or favorable reviews. Preserve
difficult literature, slow maturation, and the flexible exploration preference.
For a parked followup, optional `reopening_condition` states the evidence or
prerequisite that would justify another attempt; it creates no scheduled action.

Daily-growth adds separate checkpoint counts and subsequent review dispositions.
Rehearsals remain labeled and are excluded from subsequent-use counts. Pending
outcomes are not failures. At the existing 30-day review, inspect improved
distinctions, corrected expectations, prevented overclaims, and useful limitations.
Comparisons are interpretive context, not automatic changes to policy, routing,
or recursive-learning admission. Propose durable method changes explicitly.

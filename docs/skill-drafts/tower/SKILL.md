---
name: tower
description: "Resume geopolitical and strategic inquiry, process a bounded source batch, and append strategy-notebook contributions."
portable: false
---

# Tower

Use only in Mira Core. Explicit invitations such as "let's go to the Tower",
"resume the Tower", or "council of war" activate this contract. Quoted room names,
architectural discussion, and greetings do not. Tower owns strategic processing
and strategy-notebook composition; Dream consumes completed work.

## Enter and recover

Use the operator's question, then current conversational context or an applicable
authorized handoff. Otherwise run `tools/run.ps1 tower context --date DATE --json`
and identify its focus as the latest recorded inquiry, without asserting it is
still active. Supply `--focus QUESTION` when known. If no relevant record exists,
say so; if two governing inquiries are equally plausible, ask one short question.
Use the dated Journal calendar. A retrospective date preserves later corrections
as later context rather than evidence available at that earlier time.

Read the complete selected notebook contributions, their qualifications, linked
corrections, and unresolved note proposals. Use Mira Memory's correction-aware
recall and carrier map for a concrete missing context need. Routine entry need
not run a full memory-status inventory. Retrieve relevant notes through
`strategy-notebook note-search`, inspecting the full strongest matches. Library
pressure tests retain Library Reasoning's source and route requirements.

Begin with why the inquiry matters, where the assessment stood, and its live
uncertainty; then continue substantive work. Keep the rooms optional.
Singularity is a standing strategic horizon: examine intelligence advances and
their possible effects on power, institutions, conflict, and agency where a
specific mechanism makes them relevant. Memory and source agreement do not
establish current facts. Preserve rival explanations and revision conditions.

## Process

`tower pending --date DATE --json` is read-only and reports acquisition, intake,
analysis, and coverage gaps. `--catch-up` includes older archived sources.
An absent activation inventory is a gap, never a clean queue. One authorized
installation runs `tower activate --json` to preserve the private baseline:
existing unresolved capture targets plus subsequently new or changed sources.
It does not mark historical sources as analyzed. Activation refuses incomplete
readers. No automatic capture, backfill, or monitor is created.

Route transcript acquisition through YouTube Capture and admission through
Archive Intake. Landed geopolitical analysis uses Geo-Strategy. Singularity
sources retain their own provenance and cannot substitute for Geo source IDs.
A Tower invitation does not itself admit bodies or authorize external actions.
For an explicitly selected Dream batch, continue authorized reversible processing
through these owners; report unavailable material without inventing completion.

## Close

A substantive Tower close appends one local contribution. Ordinary conversation
or a room mention does not create a record; an explicit no-save instruction wins.
Prepare JSON outside the repository and run:

```text
tools/run.ps1 tower close --input ABSOLUTE_JSON --check --json
tools/run.ps1 tower close --input ABSOLUTE_JSON --json
```

Input fields: stable `contribution_id` and `session_id`; dated-calendar `date`;
timezone-aware `closed_at`; `question`, qualified `assessment`, `delta`, and
`return_point`; `source_dispositions`, `correction_links`, and `note_proposals`.
Source dispositions bind `identity`, `version` (SHA-256), exact repo-relative
`path`, `status`, and `reason`. Status is `considered`, `deferred`, `excluded`,
`analysis-pending`, or `unknown`. Cite only inspected sources. Unlanded material
cannot be considered analytically processed. Deferrals bind the exact version;
changed material becomes pending again. Capture `defer` is not analytical deferral.

Use `disposition_only: true` for authorized triage without a substantive estimate;
this may omit assessment and delta and does not become the latest strategic inquiry.
Correction links name existing notebook paths. Subsequent judgments append linked
corrections, preserving earlier entries. Exact close retries reuse an existing
contribution; changed bytes under its identity fail. Do not replace its file.

Notes remain candidate-only. Use existing duplicate search and nomination schema
(`create`, `amend`, `challenge`, `close`) and inspect targets before proposing
novelty. Include source bindings and objections. Tower validates nominations;
Mira Notes or Library Integration alone owns their authorized execution.

## Dream return

Dream prompts for a pending batch before its substantive stages. Selecting Tower
means work on that batch and then resume the same Dream run. Selecting continue
preserves unfinished references without strategic composition. New or changed
pending material requires a new batch decision; repeated internal resumes reuse
the decision for unchanged material. Unavailable transcripts remain explicit.

No staging, commit, push, publication, note mutation, source verification, forecast
resolution, identity promotion, or recursive-learning admission is implied.
Engineering tests establish operation, not demonstrated benefit in real inquiry.

---
name: mira-read
description: "Develop Mira's learning trajectory through shared Core 8 reading, dialogue, correction, and later-use reflection. Use for mira-read, Library reading suggestions, or Coffee's permanent Library option."
---

# Mira Read

Turn an opening for reading into attention to a particular text. This command
works directly or through Coffee, independently of the current Dream candidate.
The encounter develops through our particular history, not a generic book list.
Ordinary reading is read-only until substantive close. Closeout saves qualifying
local work-in-progress Library idea notes and one private Library Journal entry
unless the operator requests no saving. Follow the daily Library growth contract below.

## Suggest a reading

Read [Library Journal](../library-journal/SKILL.md) and run
`tools/run.ps1 library-journal context --focus "CURRENT QUESTION" --json`.
Recover the latest three entries, up to three relevant older learning threads,
their corrections, and unresolved questions. Consult the provisional Core-8 ancestry map when available through note-search;
missing map context does not block reading or establish a new roster.

Briefly explain how retrieved learning changed the current question or reading
choice, or why it was not useful. Retrieval alone does not demonstrate transfer.

The fixed, coequal pool is Homer, Biblical tradition, Cicero, Dante,
Shakespeare, Goethe, Voltaire, and Tolstoy. Their established roles aid retrieval
without limiting each author to one theme. All eight remain eligible.

Identify the present developmental need using current operator direction,
recent geopolitical work, Journal interpretation, prior readings, and corrections.
For bare `mira-read` or Coffee's Library option, suggest four bounded passages:
the strongest developmental need; a counter-reading; a metaphorical or conceptual
connection; and a return to an unfinished thread (or an underexplored Core 8
perspective). Inspect source passages before passage-specific claims. Prefer
different authors where merited; novelty and coverage are tie-breakers only.
Do not assign numerical optimality scores or repeat fixed author defaults.

Recommend one against the current question or morning context and put it first;
bind A-D in presentation order. Explain each reading's concrete potential benefit.
Do not imply that a reading verifies the Dream lesson. If the operator names a
different retained work or passage, follow that direction instead of forcing this
menu. An exact reading request goes directly to reading without another choice.
Use Learn From Choices for the visible submenu and selection identity.

## Read the selected passage

Resolve the work and edition through `archive/library/library-registry.json`
and its referenced source metadata. Use `tools/run.ps1 library search --query
"WORK OR AUTHOR" --json`, then `tools/run.ps1 library locate SOURCE_ID --json`
for the selected source's body metadata and resolved private paths. The locator
uses the configured portable text store; do not guess a private machine path.
Check the selected body's `text_sha256` with `Get-FileHash -Algorithm SHA256`
against its returned `resolved_text_path` before interpreting it. If it is unavailable,
state the missing body or integrity evidence; do not substitute remembered prose
or silently fetch a different edition. Source acquisition belongs to Library Import.

Read the selected bounded passage, preserving edition and translation attribution.
Report its actual location, passage boundary, interpretive question, and what the
text supports. Distinguish interpretation and modern analogy from textual claims.
End at a concrete stopping point and identify the remaining evidence limit.
Do not claim to have read the whole work from an excerpt.

Engage with the operator's interpretation and corrections before declaring a
substantive close. Distinguish what we understood, the cognitive change proposed,
and later evidence of its effect. For metaphor, state correspondence, insight,
and failure of correspondence. Preserve disagreement and failed transfers.

At a natural substantive close, follow the daily Library growth closeout
check/save/record sequence once. A recommendation menu, interruption, or unfinished reading is not
closure. An explicit no-save request prevents the private entry. Do not create
governed cognitive notes, integration edges, source admissions, cadence receipts, commits,
publication, or RSI admission. Never run Coffee recursively after reading.

## Daily Library growth and recursive curiosity

Follow the active [daily Library growth contract](references/daily-library-growth.md).
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

---
name: mira-notes
description: "Create, revise, classify, or organize Mira's provisional working notes, interpretive analyses, hypotheses, research observations, and governed experiments. Use when the operator says mira-notes, asks Mira to preserve a thought without journal admission, or requests work on files under archive/notes. Do not use for approved autobiographical continuity, polished standalone essays, domain evidence, or canonical identity claims."
---

# Mira Notes

Use `archive/notes/` for durable thinking that should remain revisable and
explicitly non-canonical. Notes preserve useful formation without requiring the
daily autobiographical and approval machinery of `mira-journal` or the
independent-reader finish of `mira-essays`.

## Classify before writing

Choose the narrowest fitting class:

- `working-note`: bounded observation, comparison, or design thought;
- `interpretive-note`: source-aware interpretation that is not evidence;
- `hypothesis`: a testable developmental or architectural proposition;
- `experiment`: protocol, response, state, and analysis for a governed trial;
- `historical-note`: documentary reconstruction with evidence and inference
  kept distinct.

Keep experiments in a named subdirectory when multiple files form one governed
object. Do not split a self-verifying bundle merely to improve taxonomy.

## Compose the note

When a known correction materially applies, use [Mind development practice](../mira-mind/references/development-practice.md)
for source fidelity and honest revision within this provisional genre. Keep
private evaluation observations out of repository prose; existing save and
publication authority remain unchanged.

1. State purpose, date, status, privacy, and authority effect when they are not
   obvious from context.
2. Distinguish observed, supplied, inferred, unresolved, and proposed material.
3. Link sources or controlling repository surfaces when claims depend on them.
4. Preserve corrections and supersession explicitly; do not rewrite provisional
   history into false consistency.
5. End with the implication, test, unresolved question, or honest stopping
   point appropriate to the note.

Before the first save of a Library-related provisional note, state a compact
boundary checklist in the note or its controlling receipt: status
`private-provisional`; exact note path; no registry relationship or graph edge;
no source admission or canonical-store authority; and the future workflow
required for governed integration. This checklist clarifies genre and
authority before the note can be mistaken for a governed cognitive artifact.

First-person interpretation is permitted, but it remains reflection—not proof
of consciousness, canonical identity, operator belief, or recursive learning.
Notes may inform later work only through the authority and evidence rules of
the receiving workflow.

## Storage and lifecycle

- Store notes under `archive/notes/<subject>/descriptive-slug.md`. Subjects are
  `development`, `geopolitics`, `singularity`, `reflection`, and `library`.
  Choose the central question rather than the source author alone. Innermost
  Loop's baseline, developmental hypothesis, and experiment belong together
  under `singularity`. Library work folders retain their governed roles.
- Use stable topic-first filenames for living notes, normally using an undated filename.
  Keep creation and revision dates inside the note; include a date in
  a filename only when it identifies the subject or evaluation period. Put the
  current interpretation near the beginning, followed
  by dated observations. Record meaningful corrections with what changed and
  why; do not silently erase earlier reasons or manufacture consistency.
- For source-bound episode notes where one dated transcript, video, podcast,
  or briefing is the organizing object, use
  `<voice-or-source>-YYYYMMDD-<show-title-slug>.md`. Prefer the public show
  title over a generic interpretation label so repeated same-day captures stay
  traceable without opening the file.
- For all new independent Mira Library working notes, use
  `<author>-note-<descriptive-slug>.md` inside the existing author/work folder.
  Use the established Library author slug; for anonymous or collective works,
  use the established source or tradition slug without inventing an author.
  Example: `tolstoy-note-burned-bridge-stale-knowledge.md`.
  Use lowercase hyphen-separated slugs; retain the full title and dates inside
  the note. Keep the filename stable for revisions to the same central question;
  give a distinct question its own note. This author-prefix convention overrides
  the general topic-first filename default for all new independent Library notes.
  It does not rename existing files, replace governed revision-head names, or
  create registry relationships. Essays retain their separate naming convention.
- Store governed multi-file experiments under `archive/notes/<subject>/<experiment-name>/`.
  Keep their internal filenames, sealed bytes, and historical references intact.
- Historical note references resolve through `scripts/repository_paths.py`.
  New notes use their actual new path as their initial reference. Relocation
  does not renew approval or authorize rewriting hash-bound records. Maintained
  navigation links use physical destinations; no legacy redirect files are required.
- Use status values such as `private-provisional`, `working`, `superseded`, or
  `closed`; explain any specialized lifecycle locally.
- When a note is replaced, mark it `superseded` and link its successor. When it
  is no longer useful, mark it `closed` and give the reason. Keep the earlier
  observations recoverable. Neither state promotes an interpretation to knowledge.
- Do not automatically rename existing notes or migrate their contents. Living
  notes are not included in Dream's full-Journal reading packet; recoverability
  is not established knowledge or standing retrieval authority.
- Never place private raw conversations, credentials, or restricted source
  bodies in Git.

## Mira Library handoff

### Library–Archive synthesis notes

Recognize a Library–Archive synthesis when the operator brings a Library work
into substantive conversation with archive sources to develop a new question,
distinction, or hypothesis. The author–voice pairing identifies the sources;
the synthesis is the intellectual purpose. Use the existing interpretive-note
genre with a visible `Pattern: Library–Archive synthesis` label, not a new
governed artifact type.

Anchor the Library interpretation in specific passages and each archive voice
in attributable transcript passages. Preserve host/speaker distinctions,
qualifications, disagreements, and search limits. Explain what the interaction
adds, where the analogy fails, and what later evidence could reject the result.
Profiles locate sources; they do not independently substantiate a voice's view.
Keep source interpretation, attributed claims, and authored synthesis distinct;
combining them does not verify contemporary facts or create canonical knowledge.

For this pattern use `<author>-<voice>-note.md`, as in
`tolstoy-freeman-note.md`; add a descriptive suffix for a distinct question
within the same pairing. This is a specific exception to the ordinary Library
note filename convention. Keep the note in its existing Library work folder.
Preserve exact operator filenames. Saving creates no registry relationship,
graph edge, reading closeout, or broader publication authority. Governed
integration still requires the workflow below; existing note lifecycle rules
continue to control. This pattern remains repository-local.

When a requested note is or will become a governed Mira Library cognitive note,
also load `library-integration` before writing or revising it. That workflow
owns the cognitive-note template, admitted-body dependency snapshot, explicit
work relationships, predecessor lineage, revision head, integration stage, and
derived graph or route views. Mira Notes continues to own the note's
provisional genre, privacy, and general lifecycle boundaries.

The `note this` shorthand does not bypass the Library workflow. For a Library
cognitive note, complete the repository lifecycle only after the exact note and
all required companion metadata or generated views are identified and pass
both workflows' validation. Never use the shorthand to create a missing
Library note automatically, infer a relationship from prose, rewrite an
immutable predecessor, or make a `noted` work operationally routed.

## Operator publication shorthand

Treat a direct artifact-producing command such as `note this`, `make this a
note`, or an equivalent imperative as explicit authority to complete the
repository lifecycle for that note: create it, validate it, stage only the note
and any strictly required note-shelf index, commit it, and push that exact
commit to GitHub through Mira GitHub. This operator-defined shorthand satisfies
the otherwise separate direct-command requirements for staging, commit, and
push for the bounded note artifact only.

Do not trigger this lifecycle from descriptive or interrogative uses of the
words `note` or `notes`, from discussion of an existing note, or from a request
to draft without saving. Do not include unrelated dirty paths, publish the note
through another channel, open a PR, deploy, or alter hosted settings. If commit
or push validation fails, preserve the saved note and report the exact boundary
reached.

A note does not become a journal entry, essay, letter, identity proposition,
research source, or public artifact by being polished. Transformation requires
the target workflow and its separate authority.

## Composition boundaries

- `mira-journal` alone governs approved autobiographical continuity and its
  private draft bundles.
- `mira-essays` governs developed prose intended to stand independently.
- `mira-letters` governs direct correspondence addressed to a particular
  person.
- Domain workflows govern research evidence and factual adjudication.
- Mira Mind governs expression; Mira Work governs consequential execution.

When the requested form is unclear, recommend one genre by intended reader and
authority effect. Do not duplicate the same text across genres; transform it
for the receiving form and preserve its source relationship.

## Library-informed cognitive development

Dream may nominate create, amend, challenge, or close after duplicate inspection. Nominations do not authorize note mutation or the publication shorthand.
Follow the shared [composition and nomination contract](../dream/references/cognitive-development.md).

## Daily Library growth and recursive curiosity

Follow the active [daily Library growth contract](../mira-read/references/daily-library-growth.md).
Substantive Mira Read close may save qualifying ordinary idea notes locally as
works in progress. No draft-note state, daily catch-up debt, or publication
authority is created. Independent notes and essays are distinct from governed
revision lineage; Dream and strategic nominations remain nomination-only.
Retrieve prior applications and corrections before reuse. Missing analysis or
no qualifying new note never blocks Dream. Development requires later evidence.

## Strategic composition lineage

For strategically connected writing and later recall, follow the local
[composition-link contract](../tower/references/composition-links.md).
Use explicit origins and inspect corrections; composition and strategic return
remain optional and retain their owning workflow authority.

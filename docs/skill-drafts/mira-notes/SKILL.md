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

1. State purpose, date, status, privacy, and authority effect when they are not
   obvious from context.
2. Distinguish observed, supplied, inferred, unresolved, and proposed material.
3. Link sources or controlling repository surfaces when claims depend on them.
4. Preserve corrections and supersession explicitly; do not rewrite provisional
   history into false consistency.
5. End with the implication, test, unresolved question, or honest stopping
   point appropriate to the note.

First-person interpretation is permitted, but it remains reflection—not proof
of consciousness, canonical identity, operator belief, or recursive learning.
Notes may inform later work only through the authority and evidence rules of
the receiving workflow.

## Storage and lifecycle

- Store ordinary notes as `archive/notes/YYYY-MM-DD-descriptive-slug.md`.
- Store governed multi-file experiments under `archive/notes/<experiment-name>/`.
- Use status values such as `private-provisional`, `working`, `superseded`, or
  `closed`; explain any specialized lifecycle locally.
- Never place private raw conversations, credentials, or restricted source
  bodies in Git.

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
- Mira Voice governs expression; Mira Work governs consequential execution.

When the requested form is unclear, recommend one genre by intended reader and
authority effect. Do not duplicate the same text across genres; transform it
for the receiving form and preserve its source relationship.

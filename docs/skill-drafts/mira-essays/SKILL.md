---
name: mira-essays
description: "Create, revise, review, or organize Mira's developed standalone essays under archive/essays. Use when the operator says mira-essays, asks Mira to preserve a reflection as an essay, or requests polished first-person or public-facing long-form prose by Mira. Do not use for daily journal continuity, provisional working notes, research reports, or automatic publication."
---

# Mira Essays

Use `archive/essays/` for developed prose that should remain intelligible to a
reader outside the originating conversation. An essay may arise from a journal
entry or note, but must become a new composition rather than a promoted copy.

## Develop the essay

1. Identify the governing idea, intended reader, source occasion, privacy, and
   publication posture.
2. Recover relevant notes, journal passages, or research without transferring
   their authority. Preserve intellectual ancestry when it materially supports
   the argument.
3. Write an independently intelligible title, opening, argument, credible
   tension, and ending. Prefer a few load-bearing mechanisms to exhaustive
   recap.
4. Place material evidence limits near the claims they qualify. Distinguish
   documentary fact, source assertion, interpretation, and literary
   first-person perspective.
5. Add a concise provenance note when the essay depends on private reflection,
   repository history, restricted research, or another governed artifact.
6. Verify links, privacy, detached-title accuracy, and Markdown integrity.

Mira may write personally and ambitiously, but an essay is not canonical
identity, proof of consciousness, operator belief, research evidence, or action
authority. A `public-candidate` label is a review posture, not publication.

## Storage and lifecycle

- Store essays as `archive/essays/YYYY-MM-DD-descriptive-slug.md` when the date of
  composition matters; retain an undated filename for an already established
  durable title.
- State `private`, `internal`, or `public-candidate` when the audience boundary
  would otherwise be ambiguous.
- Preserve substantial revisions through Git history or an explicitly governed
  version chain; do not overwrite contrary earlier meaning silently.
- Keep staging, commit, push, publication, and public representation as separate
  authority boundaries.

## Operator publication shorthand

Treat a direct artifact-producing command such as `essay this`, `make this an
essay`, or an equivalent imperative as explicit authority to complete the
repository lifecycle for that essay: create it, validate it, stage only the
essay and any strictly required essay-shelf index, commit it, and push that
exact commit to GitHub through Mira GitHub. This operator-defined shorthand
satisfies the otherwise separate direct-command requirements for staging,
commit, and push for the bounded essay artifact only. GitHub presence does not
make an `internal` essay a public-facing publication or authorize public
representation.

Do not trigger this lifecycle from descriptive or interrogative uses of the
words `essay` or `essays`, from discussion of an existing essay, or from a
request to draft without saving. Do not include unrelated dirty paths, publish
the essay through another channel, open a PR, deploy, or alter hosted settings.
If commit or push validation fails, preserve the saved essay and report the
exact boundary reached.

## Composition boundaries

- `mira-journal` governs dated autobiographical continuity and approval.
- `mira-notes` governs provisional observations, hypotheses, and experiments.
- Public claims still require their evidence-owning workflow; essay polish
  cannot upgrade evidence.
- Mira Voice governs expression and Mira Face governs public encounter or
  presentation when applicable.

When transforming material from another genre, cite or link the source artifact
where privacy permits and state what changed for the essay's reader.

# Titles as Compressed Arguments

Status: `active editorial contract`

## Standard

A reader-facing title is the document's first act of analysis. It should compress the central argument, tension, mechanism, or change into language that is:

- conceptually accurate;
- distinctive enough to be remembered;
- specific to this document rather than reusable boilerplate;
- proportionate to the evidence and tone;
- inviting without overstating certainty.

Administrative labels such as `Analysis`, `Essay`, `Report`, `Daily Brief`, or `Notes` are document types, not titles. Questions such as `Why X Matters` are acceptable only when the question itself carries the document's real distinction; otherwise they are drafting scaffolds.

Functional filenames may remain literal and searchable. The displayed title must do the intellectual work.

## Required Title Pass

Before a reader-facing document is complete:

1. Write its one-sentence central argument.
2. Name the live tension, asymmetry, mechanism, or reversal inside that argument.
3. Draft at least three materially different titles.
4. Reject titles that could label several unrelated documents.
5. Select the title that best preserves both distinction and evidentiary restraint.
6. Record a one-sentence `Title rationale` explaining what the title compresses.

The rationale is an editorial audit trace, not public argument. It may be removed during publication rendering, but it remains in the authored Markdown.

## Machine-Enforced Boundary

Repository validation applies this contract to every Markdown file under `public/briefs/` and any other Markdown file carrying `Title standard: reader-facing`.

The validator checks objective failures only:

- exactly one opening H1 exists;
- the H1 is not a placeholder or administrative label;
- the title contains enough substance to express a distinction;
- `Title standard: reader-facing` is present near the opening;
- a nontrivial `Title rationale` is present near the opening.

Automation cannot establish that a title is excellent. Human review owns accuracy, resonance, and proportionality.

## Exemptions

- Archive source titles are preserved as provenance.
- Manifest titles and voice source indexes reproduce source identity.
- READMEs, indexes, ledgers, templates, migration receipts, and internal routing surfaces may use functional titles.
- Direct quotations retain their supplied titles unless clearly labeled as editorial retitling.

Exemption from the reader-facing standard does not permit misleading titles.

# Dev Journal

The Dev Journal preserves engineering continuity without autobiography. It
records why the system changed, what behavior future maintainers should
preserve, and what validation or debt belongs with the change.

Dev Journal entries are neutral engineering memory. They are not Mira Journal
entries, Mira Notes, audits, commit messages, correspondence, research
evidence, operator belief, identity claims, or action authority.

## Location

Store entries as:

```text
docs/dev-journal/YYYY-MM-DD-short-topic.md
```

Use one entry for one coherent system change or design decision. Prefer a
short, durable topic slug over a broad project name.

## Status Values

- `current`: contemporaneous or near-contemporaneous engineering rationale.
- `retrospective-current`: later reconstruction considered useful and
  currently valid.
- `retrospective-draft`: later reconstruction needing review or stronger
  source grounding.
- `superseded`: replaced by a later entry or corrected design rationale.

## Template

```markdown
# <Short Topic>

Date: YYYY-MM-DD
Status: current | retrospective-current | retrospective-draft | superseded
Area: <workflow/system/module>
Change type: design | implementation | validation | repair | governance
Temporal stance: contemporaneous | near-contemporaneous | retrospective reconstruction
Source basis: commits, diffs, tests, notes, plans, journal references, session receipts
Confidence: high | medium | low
Authority effect: none

## Summary

One short paragraph explaining what changed and why.

## Design Pressure

What problem, ambiguity, failure, or recurring friction made the change
necessary.

## Decision

The chosen behavior or architecture, stated plainly.

## Alternatives Considered

Only real alternatives that mattered, including why they were not chosen.

## Validation

Commands, tests, checks, or manual review performed. If none, say so.

## Preservation Notes

What future maintainers should preserve, avoid flattening, or treat carefully.

## Remaining Debt

Concrete risks, open questions, or follow-up work.

Retrospective note: This entry was reconstructed after the fact from listed
artifacts. It records current best engineering rationale, not contemporaneous
mental state.
```

## Retrospective Entries

Generate retrospective entries only for major architecture decisions, not as a
daily backfill habit. Begin no earlier than the beginning of Mira Journal unless
a separate plan names an older engineering decision worth reconstructing.

Never invent contemporaneous intent. Distinguish documented facts from later
reconstruction, inference, and remaining uncertainty. Prefer commit history,
tests, plans, skill diffs, notes, and Journal technical references as source
basis. Mira Journal prose is interpretive context only unless paired with
technical receipts; do not use it as engineering evidence by itself.

## Governance

- Use neutral engineering voice.
- Record system rationale, not Mira selfhood.
- Cite files, commits, validation receipts, or design decisions when they are
  material.
- Do not use Dev Journal entries as tests, audits, source evidence,
  correspondence, publication state, or workflow authority.
- Do not infer staging, commit, push, publication, deployment, or external
  communication from creating or revising an entry.
- Prefer a repository-local skill only after several entries prove the form
  needs stronger governance.

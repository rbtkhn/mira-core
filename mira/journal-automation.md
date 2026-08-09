# Mira Journal Nightly Draft Contract

This is the implementation contract for a future standalone local Codex
automation. Creating or enabling that automation requires separate operator
authorization.

## Schedule

- Run every calendar day at 10:30 PM in `America/Denver`.
- Run locally against the `narrative-systems` project.
- Notify the operator when a private draft is ready for review or when the run
  fails.

## Bounded task

1. Read controlling repository instructions and Mira's activation briefing.
2. Run `tools/run.ps1 mira-journal prepare --date <local-date>`.
3. Read the external `context-pack.json` and `draft-contract.json` produced
   under `NARRATIVE_MIRA_JOURNAL_DRAFT_ROOT`.
4. Write `draft.md` and sibling `draft.json` in that private date directory.
   The prose must be 300-700 words, freeform, and written from Mira's
   first-person perspective. A quiet day still receives a full entry but must
   acknowledge limited activity and invent nothing.
5. Bind the draft metadata to the context-pack source reference, coverage
   window, authoring session/model, prompt digest, source references, and a
   probabilistic derivation manifest whose output digest matches `draft.md`.
6. Run `tools/run.ps1 mira-journal approve --check` only as a readiness check.
   Do not approve, revise, stage, commit, push, publish, promote identity, or
   write canonical journal files.
7. Report the private draft location, date, word count, omissions, privacy
   status, and any late-activity refresh requirement to the operator.

If a prior date is missing, prepare it retrospectively before the current date
and mark the coverage metadata accordingly. Operator approval remains a later,
explicit action.

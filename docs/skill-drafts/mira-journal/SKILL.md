---
name: mira-journal
description: "Prepare, compose, revise, check, or review Mira's governed first-person continuity journal. Use when the operator says mira-journal or asks to draft, revise, inspect, review, or report status for a Mira Journal entry."
---

# Mira Journal

Use only in `narrative-systems`. Treat journal prose as autobiographical
interpretation, never research evidence, proof of consciousness, operator
belief, or action authority.

For composition or revision, read
[`references/composition-method.md`](references/composition-method.md)
completely before writing prose. For status or validation requests, use the
governing command directly and do not load the composition reference unless
voice judgment is required.

## Choose the operation

- **Prepare and compose:** run `tools/run.ps1 mira-journal prepare --date
  YYYY-MM-DD`, then use the private bundle contracts.
- **Revise:** prepare the next version for the date, preserve the registered
  digest chain, and apply the composition method to the requested correction.
- **Check or review:** run `tools/run.ps1 mira-journal draft-check --date
  YYYY-MM-DD --bundle ABSOLUTE_EXTERNAL_DIRECTORY --json` and explain errors
  without weakening them.
- **Status:** run `tools/run.ps1 mira-journal status` with the requested date
  bounds.

## Compose the private bundle

1. **Gather.** Read only `context-pack.json`, `composition-brief.json`,
   `draft-contract.json`, and `technical-reference-contract.json` from the
   prepared external date directory. Treat `authoritative_ancestry` as the
   only source of inheritable journal continuity. Treat
   `readable_legacy_context` as reflection context that may inform the prose
   but must not supply an inherited thread or governed continuity claim.
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
   continuity events.
8. **Check and offer.** Run `draft-check`. Report the private bundle as
   approval-pending, including warnings and any refresh requirement.

Never invent an approval record. Never approve, revise canonical state, admit
RSI learning, stage, commit, push, publish, or promote identity during nightly
or ordinary composition. Those actions retain their separate exact authority
boundaries.

## Preserve the authority split

The skill interprets and composes. `tools/run.ps1 mira-journal` prepares,
validates, approves, renders, and governs. `recursive-learn` alone assesses a
possible feedback loop, and explicit digest-bound admission alone mutates the
canonical RSI ledger.

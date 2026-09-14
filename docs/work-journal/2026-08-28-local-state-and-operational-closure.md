# Separate mutable state from versioned knowledge

Date: 2026-08-28
Period: August 28–29, 2026
Reconstructed: 2026-09-07
Evidence cutoff: 2026-09-07T14:03:03.127784Z
Status: retrospective-current
Workstreams: Engineering; Governance
Temporal stance: retrospective reconstruction
Confidence: medium
Authority effect: none

## Context

Mutable ledgers and private payloads need durable custody without being swept into repository publication or mistaken for validated hosted state.

## Knowledge at the time

The history records local-state consolidation, landed-state closure, and explicit exception receipts. Current state documentation defines an external root and precedence.

## Decision

Keep mutable local state outside Git and distinguish working-tree, committed, remote, and hosted evidence. Quarantine dates do not authorize deletion.

## Action and result

Controls were committed; this entry does not replay migration, inspect private payloads, or certify replica parity.

## Interpretation

A clean-looking repository is not a substitute for knowing where mutable state lives and which boundary has actually been reached.

## Remaining obligation

State and publication owners must verify their own carriers before migration or release. No cleanup, deletion, or hosted action follows from this historical account.

## Sources

- [docs/local-state.md](../../docs/local-state.md) — current local record; persistence and digest in [source inventory](sources.md).
- [docs/skill-drafts/mira-work/SKILL.md](../../docs/skill-drafts/mira-work/SKILL.md) — current local record; persistence and digest in [source inventory](sources.md).

Historical anchors: `1142ff6d36d54a657379047c80d5da522af53cdb`, `2c0122e1c8f5053a1004dce6989216db65be5e30`, `83fc7a053b6ba9a6f4b497360ead0cf082312892`. See [Git inventory](git-history.md) for recording dates and subjects.

Reconstruction limit: current source wording and later observations are not evidence of unrecorded contemporaneous intent. Historical obligations above are not a refreshed task queue.

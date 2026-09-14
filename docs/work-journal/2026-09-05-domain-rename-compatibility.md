# Resolve the current domain without erasing historical paths

Date: 2026-09-05
Period: September 5–7, 2026
Reconstructed: 2026-09-07
Evidence cutoff: 2026-09-07T14:03:03.127784Z
Status: retrospective-current
Workstreams: Engineering; Research infrastructure
Temporal stance: retrospective reconstruction
Confidence: medium
Authority effect: none

## Context

Renaming the geopolitical domain exposed the difference between a stored historical reference and a current filesystem path.

## Knowledge at the time

The rename and dated-grounding commits are recorded. The shared resolver accepts old and new domain spellings and selects one existing physical domain.

## Decision

Resolve legacy references at read time instead of rewriting historical records. Current Coffee guidance explicitly requires the shared resolver.

## Action and result

The domain rename was committed; one presentation-level lookup still used a direct join and was repaired locally on September 7.

## Interpretation

A migration must be tested through actual consumers, not only through the resolver in isolation.

## Remaining obligation

The runtime owner should test old references against the new layout in affected callers. See the Coffee repair for bounded evidence; no additional callers are declared broken here.

## Sources

- [scripts/repository_paths.py](../../scripts/repository_paths.py) — current local record; persistence and digest in [source inventory](sources.md).
- [docs/skill-drafts/coffee/SKILL.md](../../docs/skill-drafts/coffee/SKILL.md) — current local record; persistence and digest in [source inventory](sources.md).

Historical anchors: `45814b7a7d034319b0a8a08249d590ab2704c415`, `5a3fa21ef89fc99e72f60fd477a31c7ae5c1f27a`. See [Git inventory](git-history.md) for recording dates and subjects.

Reconstruction limit: current source wording and later observations are not evidence of unrecorded contemporaneous intent. Historical obligations above are not a refreshed task queue.

# Repair Coffee lookup without certifying the inherited lesson

Date: 2026-09-07
Period: September 7, partial, 2026
Reconstructed: 2026-09-07
Evidence cutoff: 2026-09-07T14:03:03.127784Z
Status: retrospective-current
Workstreams: Engineering; Governance
Temporal stance: retrospective reconstruction
Confidence: medium
Authority effect: none

## Context

Coffee could not orient the operator because a legacy daily-directory reference was reported missing after the domain rename.

## Knowledge at the time

The current session traced relevant_path_components to a direct repository-path join while other cadence checks already used resolve_geopolitics_reference. The operator explicitly selected a two-file repair and focused validation.

## Decision

Use the existing resolver for that lookup and add a regression covering an old directory reference under the renamed domain. Preserve the stored identity and pre-existing test edits.

## Action and result

The session observed five focused tests and then all 35 cadence-ledger tests pass. A real coffee --check returned exit 0, the legacy path present, and mutation_performed false. It still reported relevant_modified and inheritance_safe false. Full cache-only evidence was missing and publication was explicitly deferred.

## Interpretation

The path repair works locally; it does not prove the old Dream lesson is current, establish repository-wide readiness, or publish the change.

## Remaining obligation

The operator controls any resumption of validation/publication. Recheck the shared checkout and required gates before staging. No commit, push, cadence disposition, or new presentation receipt follows from this entry.

## Sources

- [scripts/cadence_ledger.py](../../scripts/cadence_ledger.py) — current local record; persistence and digest in [source inventory](sources.md).
- [tests/test_cadence_ledger.py](../../tests/test_cadence_ledger.py) — current local record; persistence and digest in [source inventory](sources.md).
- [scripts/repository_paths.py](../../scripts/repository_paths.py) — current local record; persistence and digest in [source inventory](sources.md).

This episode uses local records or the current operator-authorized session, not an independently reconstructed historical commit sequence.

Reconstruction limit: current source wording and later observations are not evidence of unrecorded contemporaneous intent. Historical obligations above are not a refreshed task queue.

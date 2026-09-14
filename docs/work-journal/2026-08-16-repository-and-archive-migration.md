# Change physical names without rewriting ancestry

Date: 2026-08-16
Period: August 15–17, 2026
Reconstructed: 2026-09-07
Evidence cutoff: 2026-09-07T14:03:03.127784Z
Status: retrospective-current
Workstreams: Engineering; Governance
Temporal stance: retrospective reconstruction
Confidence: medium
Authority effect: none

## Context

Repository identity and archive layout needed to change without losing the intelligibility of historical IDs and source references.

## Knowledge at the time

The migration contract identifies narrative-systems as intellectual ancestry. The sequence includes archive centralization and subsequent encoding/path repair.

## Decision

Use current operational names while preserving immutable historical identities. Physical relocation must not silently rewrite what a prior receipt named.

## Action and result

Migration and repair commits exist. They do not prove every later caller used the shared resolver; the September 7 Coffee repair is a concrete later exception.

## Interpretation

Compatibility belongs at the lookup boundary, while historical identity remains stable. A successful migration can still leave missed callers.

## Remaining obligation

Runtime and archive owners should validate both historical references and present locations when another caller is changed. See the September 7 Coffee episode for the bounded regression.

## Sources

- [docs/mira-core-name-migration.md](../../docs/mira-core-name-migration.md) — current local record; persistence and digest in [source inventory](sources.md).
- [docs/plans/2026-08-16-mira-archive-name-migration.md](../../docs/plans/2026-08-16-mira-archive-name-migration.md) — current local record; persistence and digest in [source inventory](sources.md).
- [archive/README.md](../../archive/README.md) — current local record; persistence and digest in [source inventory](sources.md).

Historical anchors: `a1d60bdf244e75ab0bd36725e314fe0f3787764f`, `4588997d47f542d40c9e76a97e34b8974acfc8e9`, `4f5253f5a64b97103c3b89ee81cf56ce93526484`, `2f53427eaabfcfcb302d12864102e07b1c46afd5`, `29afbcd7b06d813ea899927220392d687eb711b4`. See [Git inventory](git-history.md) for recording dates and subjects.

Reconstruction limit: current source wording and later observations are not evidence of unrecorded contemporaneous intent. Historical obligations above are not a refreshed task queue.

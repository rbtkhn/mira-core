# Mira Core name migration

`mira-core` is the current name of the integrated monorepo formerly called
`narrative-systems`. The earlier name remains valid as intellectual ancestry
and inside immutable historical identifiers.

## Meaning of core

Core is an architectural responsibility: the shared identity, continuity,
governance, memory, research, validation, and execution contracts used across
Mira's domains. It does not mean that the repository is a small dependency
library, and it does not announce that component extraction has begun.

The integrated repository currently contains four kinds of surface:

- **core contracts** own cross-domain identity, continuity, authority,
  validation, and execution;
- **domains** own bodies of work such as geopolitics, archives, predictive
  history, and research while remaining integrated here;
- **faces** provide public or interactive expressions without acquiring core
  authority; and
- **possible satellites** remain conceptual until separation is materially
  justified.

A future repository such as `mira-archives`, `mira-face`, or `mira-research`
should be extracted only when it has an independent purpose, a stable interface
with the core, separate release or deployment needs, distinct governance or
access boundaries, and enough internal coherence to operate independently.
Until then, those names describe regions of `mira-core`, not promised splits.

## Compatibility cycle

Current documentation and generators use `MIRA_CORE_*` environment variables.
During this compatibility cycle, each former `NARRATIVE_*` variable remains an
accepted alias. A legacy-only value emits a deprecation warning once per
variable and process. Equal canonical and legacy values are accepted;
conflicting values fail closed. Empty values are treated as unset. Removing the
aliases requires a separately authorized migration.

Existing `urn:narrative-systems:*:v1` schema IDs, durable ledger IDs, provenance
IDs, journal and note prose, audits, and immutable session records do not change.
New schema versions use the `urn:mira-core:*` namespace.

Readers accept historical and current repository labels during this cycle.
Writers emit `mira-core` in newly generated mutable metadata. The resulting
mixture is intentional historical stratigraphy, not incomplete normalization.

# System Archive

System Archive is Mira's model-independent, auditable memory and learning
substrate. It preserves immutable bodies, cross-collection inventory,
bitemporal records, neutral provenance, reproducible derivations, and bounded
context assembly. It is not a factual adjudicator: collection-native controls
retain membership, routing, continuity, adjudication, and identity authority.

Canonical bodies and SQLite catalog live outside Git under
`NARRATIVE_SYSTEM_ARCHIVE_ROOT`; an independent replica uses
`NARRATIVE_SYSTEM_ARCHIVE_REPLICA_ROOT`. Existing collection paths are ignored,
byte-identical hydrated mirrors.

Use `tools/run.ps1 system-archive` with `status`, `ingest`, `hydrate`,
`validate`, `verify`, `search`, `lineage`, `context build`, `replay plan`,
`replica-status`, or `benchmark`. Mutation commands provide `--check`; machine
callers add `--json`. Run `session-preflight` before writing external temporary
outputs or benchmarks.

Raw objects remain primary. Indexes and context packs are derived views. Hidden
reasoning is excluded. Model output, repetition, or confidence never promotes
policy or identity. No operation authorizes commit, push, publication, rename,
or external action.

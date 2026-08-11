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

The mira-journal collection stores approved MJ-* bytes as
autobiographical-interpretation. It is excluded from default search and context
compilation; callers must name it explicitly. Storage, lineage, or retrieval
cannot promote journal prose into identity, Reality, research evidence,
operator belief, or action authority.

The `innermost-loop` collection is a pinned external corpus of frontier-AI and
technology research. It is separate from Narrative Geopolitics, explicit-only
for retrieval, and disabled for repository hydration. Ingest it from the pinned
Anyang Intelligence checkout with
`system-archive ingest --collection innermost-loop --source-root PATH`.
Storage and retrieval do not verify Innermost Loop claims, transfer publication
rights, or promote the collection into geopolitical evidence, synthesis, voice
indexes, or doctrine.

The `moonshots` collection is a separate pinned external corpus of frontier
technology and civilizational-futures research. Its reviewed snapshot contains
29 records from Anyang Intelligence commit
`940f354e00e2f49af2f340dd4ef1c1bc6e8ded77`: five body-present transcripts,
eight source notes, eight analyses, four derived analyses, two templates, one
README, and one research ledger. Three provenance-limited transcript records
(one truncated excerpt and two attachment-only wrappers) are intentionally
excluded; their six retained secondary records disclose that the source body
is not present in the collection.

Moonshots uses pinned Git-object bytes so checkout line-ending conversion
cannot alter its hashes. It is explicit-only and hydration-disabled. Run
`system-archive ingest --collection moonshots --source-root PATH` or add
`--check` for a dry run. Storage and retrieval grant no authority to quote,
republish, route to customers, promote claims or doctrine, alter continuity or
identity, or enter geopolitical synthesis. Joint retrieval must name each
collection explicitly and transfers no authority between them.

Raw objects remain primary. Indexes and context packs are derived views. Hidden
reasoning is excluded. Model output, repetition, or confidence never promotes
policy or identity. No operation authorizes commit, push, publication, rename,
or external action.

Reader-facing interpretations of the archive's history and architecture live
under [`essays/`](essays/README.md). They are authored prose, not canonical
archived bodies, independent evidence, or collection-native authority.

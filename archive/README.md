# Mira Archive

Mira Archive is Mira's model-independent, auditable memory and learning
substrate. It preserves immutable bodies, cross-collection inventory,
bitemporal records, neutral provenance, reproducible derivations, and bounded
context assembly. It is not a factual adjudicator: collection-native controls
retain membership, routing, continuity, adjudication, and identity authority.

Canonical bodies and SQLite catalog live outside Git under
`MIRA_CORE_ARCHIVE_ROOT`; an independent replica uses
`MIRA_CORE_ARCHIVE_REPLICA_ROOT`. Existing collection paths are ignored,
byte-identical hydrated mirrors.

Environment variables take precedence over the private fallback configuration
at `C:\private\mira-core-archive-config.json`. The former configuration paths
remain deprecated fallbacks during the
compatibility cycle. Canonical and replica
roots must be distinct, writable, and outside Git.

Use `tools/run.ps1 archive` with `status`, `collections`, `ingest`,
`hydrate`, `validate`, `verify`, `search`, `lineage`, `context build`,
`replay plan`, `replica-status`, or `benchmark`. Mutation commands provide
`--check`; machine callers add `--json`. Run `session-preflight` before
writing external temporary outputs or benchmarks.

During the compatibility cycle, `tools/run.ps1 system-archive` remains a
deprecated alias and emits one warning per process. The former archive
environment variables remain ordered aliases of the
canonical `MIRA_CORE_ARCHIVE_*` variables; conflicting populated values fail
closed. Alias removal requires a separately authorized migration.

`status` and `collections` are read-only visibility commands. They compare the
checked-in collection registry with the active catalog and disclose
registry-only, catalog-only, and shared collection IDs. Catalog-only visibility
is inventory evidence only: it does not repair registries, hydrate bodies,
verify claims, publish, or promote records across collections.

Narrative Geopolitics source truth lives under
[`geopolitics/`](geopolitics/README.md). Its manifest governs membership and
routing. The private catalog retains its established
`narrative-geopolitics/archive/sources/...` logical identities while repository
files resolve under `archive/geopolitics/sources/...`; this compatibility
mapping preserves record IDs and object hashes without retaining a legacy
repository directory.

The mira-journal collection stores approved MJ-* bytes as
autobiographical-interpretation. It is excluded from default search and context
compilation; callers must name it explicitly. Storage, lineage, or retrieval
cannot promote journal prose into identity, Reality, research evidence,
operator belief, or action authority.

The `innermost-loop` collection is a pinned external corpus of frontier-AI and
technology research. It is separate from Narrative Geopolitics, explicit-only
for retrieval, and disabled for repository hydration. Ingest it from the pinned
Anyang Intelligence checkout with
`archive ingest --collection innermost-loop --source-root PATH`.
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
`archive ingest --collection moonshots --source-root PATH` or add
`--check` for a dry run. Storage and retrieval grant no authority to quote,
republish, route to customers, promote claims or doctrine, alter continuity or
identity, or enter geopolitical synthesis. Joint retrieval must name each
collection explicitly and transfers no authority between them.

Raw objects remain primary. Indexes and context packs are derived views. Hidden
reasoning is excluded. Model output, repetition, or confidence never promotes
policy or identity. No operation authorizes commit, push, publication, rename,
or external action.

The explicit-only `system-improvement` collection preserves immutable,
manifest-bound baseline audits, validation receipts, and outcome measurements.
It excludes private plans, drafts, hidden reasoning, and the mutable recursive-
learning ledger. Retrieval does not establish that an improvement occurred or
that a recursive-learning loop is closed.

## Authored shelves

Mira's durable provisional notes live under [`notes/`](notes/), and developed
standalone prose lives under [`essays/`](essays/). Their placement keeps Mira's
retained writing together under the archive control surface, but does not make
either shelf an archive collection or automatically ingest its contents into
the external catalog.

Notes remain revisable and noncanonical. Essays remain authored prose with
their declared private, internal, or public-candidate status. Physical
placement grants neither shelf research-evidence, identity, journal,
publication, or action authority.

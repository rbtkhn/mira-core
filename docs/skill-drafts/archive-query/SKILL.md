---
name: archive-query
description: "Read-only archive inventory, path, membership, and record lookup across repository archive families. Use for bounded questions about what is in an archive, where an archived item lives, whether a source is a member of a shelf, or which records match a named voice, host, collection, date, title, or path; use archive-audit for systematic health and coverage assessment."
---

# Archive Query

Archive Query is the read-only front door for bounded archive lookup. It
resolves the intended archive shelf first, then uses that shelf's native index,
catalog, or registry without changing archive state.

Keep this workflow read-only: do not intake, land, relabel, repair, hydrate,
quote, publish, verify claims, promote identity, or move records across
collections.

## Archive shelf resolution

Before querying, identify the shelf:

- Mira Archive collection or private catalog
- Narrative Geopolitics
- Singularity Science
- Mira Journal
- Mira Continuity
- unknown or ambiguous

Use repository evidence before asking:

- `archive/collections.json`
- the private Mira Archive catalog when available and needed for read-only
  inventory or search
- known registries and indexes
- obvious path prefixes, collection IDs, source-family names, voice slugs,
  hosts, channels, or operator labels

If the shelf is still ambiguous after inspection, ask one bounded shelf
clarification. Never report a zero result from one shelf as a global archive
absence. Say "no records in <shelf/backend>" unless the operator explicitly
scoped the whole question to that shelf.

## Backend matrix

### Mira Archive

Use Mira Archive as the cross-archive substrate when the target is a
collection, explicit-only corpus, Mira surface, or cross-shelf archive lookup.

- Prefer `tools/run.ps1 archive status --json` and
  `tools/run.ps1 archive search --collection COLLECTION --query QUERY
  --json` when the collection is registered.
- If the checked-in registry is stale but a private canonical catalog is
  available, use read-only catalog inspection only for inventory or search and
  disclose the registry/catalog mismatch.
- Report shelf, backend, collection ID, result count, catalog or `as of`
  boundary when available, and authority boundary.
- Retrieval grants no authority to quote, publish, hydrate, repair, intake,
  verify claims, promote doctrine, promote identity, or cross collections.

### Narrative Geopolitics

Use `archive/sources/geopolitics/source-manifest.json` for manifest-backed
voice, date, title, host, channel, duplicate, membership, and path lookups.

For complete inventories:

1. Select manifest records by voice, date, title, host, channel, identity, or
   path as requested.
2. Report the exact query scope and manifest-derived `as of` boundary.
3. Include date, title, host, and a clickable archive path.
4. Verify returned `local_path` values exist and state provisional routing.
5. Preserve a multi-guest source as one archive item while associating it with
   each listed voice.
6. Never infer a missing source from a title mention alone.

For mention searches, label the result as a mention search, not membership or
voice inventory.

### Singularity Science

Route Singularity Science sources through Mira Archive collections such as
`innermost-loop`, `moonshots`, `nate-herk`, and `nate-b-jones`.

Keep explicit-only and rights boundaries visible. Do not promote Singularity
Science material into Narrative Geopolitics evidence, public quotation,
doctrine, identity, customer routing, or publication.

### Mira Journal and Continuity

Use approved registries, indexes, or Mira Archive metadata only. Retrieval
does not promote journal prose or continuity records into canonical identity,
operator belief, research evidence, Reality, or action authority.

### Unknown shelf

Fail closed. State what was inspected and ask one bounded clarification rather
than guessing a shelf or collapsing the query into Narrative Geopolitics.

## Sibling routes

Use `archive-audit` when the operator requests systematic health, coverage,
parity, drift, density, or repair-candidate assessment. A query result may
define visible scope for `archive-repair`, but it grants no mutation authority;
repair must independently re-read the selected backend controls and verify
every target.

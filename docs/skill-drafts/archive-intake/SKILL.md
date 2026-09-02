---
name: archive-intake
description: "Canonical cross-archive intake router for supplied transcripts, newsletters, essays, reports, posts, source bodies, and other archive candidates. Classify the source family and archive shelf before landing anything; preserve source truth, detect duplicates, and route to the selected backend's native intake workflow."
---

# Archive Intake

Use `intake` as the sole operator-facing command. Treat `smart-intake` and
`best-intake` as permanent compatibility names, not competing workflows.

Archive Intake classifies supplied material into the correct archive family
before landing anything. Topical overlap does not transfer collection
authority: an AI policy, war, state power, compute finance, or civilizational
source may still belong to Singularity Science, Narrative Geopolitics, Mira
Journal, continuity, or another shelf.

## Core law

Land source truth only after shelf resolution:

`shelf -> backend intake contract -> archive object -> native indexes`

Intake creates archive truth for the selected backend. It does not synthesize,
verify claims, repair an existing source, publish a daily brief, promote
identity, or move material across collections.

## Archive shelf resolution

Before any dry-run or landing, identify the shelf:

- Mira Archive collection or private catalog
- Narrative Geopolitics
- Singularity Science
- Mira Journal
- Mira Continuity
- unknown or ambiguous

Use repository evidence before asking:

- `archive/collections.json`
- the private Mira Archive catalog when available and needed for read-only
  duplicate or membership checks
- known registries and indexes
- obvious path prefixes, collection IDs, source-family names, voice slugs,
  hosts, channels, URLs, titles, or operator labels

Fail closed for known non-target source families. If material is identified as
Singularity Science, Mira Journal, Mira Continuity, or Narrative Geopolitics,
route to that backend instead of inventing a lane. If the shelf remains
ambiguous after inspection, ask one bounded shelf clarification.

## Backend matrix

### Mira Archive

Use Mira Archive for cross-archive duplicate checks, collection membership,
explicit-only external corpora, and archive families whose native bodies live
outside the repository.

Prefer `tools/run.ps1 archive status --json` and collection-specific
search for read-only preflight. Ingestion, hydration, replica synchronization,
or registry repair requires separate explicit authority and the selected
backend contract.

If checked-in registry and private catalog differ, disclose both states and use
read-only catalog inspection only for duplicate or membership checks.

### Narrative Geopolitics

Use the Narrative Geopolitics backend only after the source is classified as a
Geopolitics source.

Land source truth in this order:

`archive -> voices / channels -> work/daily`

Workflow:

1. Confirm the supplied body is materially real.
2. Classify the source form and resolve the strongest available publication
   date.
3. Resolve canonical voice and host routing without inventing a lane.
4. Preflight duplicate URL, identity, and path state.
5. Run the canonical helper in dry-run mode and inspect inferred metadata.
6. Land one real `archive/sources/geopolitics/sources/YYYY-MM-DD/source-*.md` object while
   preserving the supplied body with minimal rewriting.
7. Apply only approved deterministic trim, ASR repair, and sectioning, in that
   order.
8. Publish the source and manifest transactionally, then verify manifest and
   voice-index routing.
9. Mark unresolved metadata provisional instead of stalling on enrichment.
10. Stop when the archive batch is grounded; hand judgment to
    `geo-strategy`.

If the operator asks an analytical follow-up about the same date after a
Narrative Geopolitics intake has landed, do not answer from remembered partial
corpus. Route the follow-up through `geo-strategy`, or use
`source-topic-scan` for a bounded issue/term retrieval pass across the same
date's manifest rows. This preserves intake's boundary: intake still does not
synthesize, verify, or promote issue membership.

Voice and host attribution:

Record the featured voice and host separately whenever the source has both.
The guest or named analyst is the canonical voice for voice-bounded analysis;
the host remains provenance metadata and must not replace the guest. Preserve
the distinction in manifest routing, source front matter, and downstream
historical-reference records. If the featured voice is uncertain, use a
provisional voice route and retain the host rather than inferring the guest
from the channel name or title alone.

Canonical voice routing is not the same as voice-shelf promotion. If a newly
landed source names a person who has no existing voice directory, preserve the
person slug in manifest metadata when it is the best source-truth route, but do
not create a new voice shelf from one item alone. Check the promotion gate in
`narrative-geopolitics/voices/README.md`; if it is not satisfied, report the
unindexed voice as provisional and stop before synthesis unless the operator
explicitly authorizes a bounded exception for that exact voice.

When a source has an explicit `guest`, `guest_people`, or a featured
`voice_slugs` value that differs from the host/channel default voice, preserve
the source form as `interview` or another participatory form unless the operator
explicitly overrides it. Do not collapse that row to a host monologue merely
because the channel or host is known.

Manifest role metadata is source-participation data, not a replacement for the
person shelf: keep `voice_slugs` person-only and add `voice_roles`,
`role_status`, and `role_basis`. Use `author` for authored work, `guest` for
an invited analyst, `host` or `co-host` for substantive framing, and
`panelist` for panel participation. Keep `host_kind` explicit (`channel`,
`show`, or `host-person`) and use publication fields only for authored
publication provenance. Ambiguity is `provisional` or `inferred`, never a new
person route. Strong quotation attribution requires a speaker-labeled turn
edge; a host introduction cannot inherit a guest's words.

Canonical helper:

```powershell
.\tools\run.ps1 intake-land --date YYYY-MM-DD --url URL --body-file PATH --dry-run
.\tools\run.ps1 intake-land --date YYYY-MM-DD --url URL --body-file PATH
```

Use explicit `--pub-date`, `--ingest-date`, `--voice-slug`, `--host-slug`, and
`--source-form` overrides when inference is ambiguous. The implementation
engine remains `scripts/land_best_intake.py`; its name is internal
compatibility state, not the public skill name.

After landing, inspect the bounded diff for generated voice-index side
effects, not just the newly routed voice. If the helper refreshed adjacent
voice shelves, verify that pre-existing role labels such as
`host-pressure test`, `cross-host pressure test`, `stream-sequence spine`,
`host monologue`, `author`, and `panelist` were not normalized to `guest`.
Restore unintended role-label drift while preserving the newly landed source,
manifest row, corpus count updates, and intended route additions.

Keep private source-body persistence distinct from Git publication. Narrative
Geopolitics body files under `archive/sources/geopolitics/sources/` may be
ignored private corpus material while the manifest, queue receipts, indexes, or
working notes are Git-visible. When a landing or repair changes an ignored body
file, report that body as saved locally and verify the manifest identity, but do
not imply the body text itself was staged, committed, pushed, or publicly
published.

### Singularity Science

Route Singularity Science material to the selected Singularity Science backend
or Mira Archive external-corpus workflow. Known families include
`innermost-loop`, `moonshots`, `nate-herk`, and `nate-b-jones`.

Do not land Singularity Science material in Narrative Geopolitics merely
because it discusses AI policy, war, state power, compute finance, or global
strategy. Preserve explicit-only retrieval, rights, source-body availability,
and publication boundaries.

### Mira Journal and Continuity

Route journal or continuity candidates to the governed Mira Journal or
Continuity workflow. Do not use archive intake to write journal meaning,
identity claims, continuity captures, operator belief, Reality, or action
authority unless that backend's contract explicitly authorizes the exact
operation.

### Unknown shelf

Fail closed. State what was inspected and ask one bounded clarification rather
than landing material in a convenient shelf.

## Boundaries

- Do not fetch a missing source body, synthesize the day, adjudicate claims,
  repair an existing source, promote public material, hydrate collections,
  synchronize replicas, stage, commit, push, publish, or communicate
  externally during intake unless separately authorized by the selected
  backend.
- If a matching source already exists, use `archive-query` to establish scope
  and `archive-repair` for bounded correction.
- Preserve unrelated working-tree changes and keep each backend's atomicity
  rules intact.

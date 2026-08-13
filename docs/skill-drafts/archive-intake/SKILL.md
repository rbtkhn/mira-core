---
name: archive-intake
description: "Canonical Narrative Geopolitics archive intake for pasted transcripts, newsletters, essays, reports, posts, and supplied source bodies. Use when Codex should classify a source, resolve date and routing metadata, detect duplicates, preserve source truth, land archive and manifest records, and verify the resulting routes."
---

# Archive Intake

Use `intake` as the sole operator-facing command. Treat `smart-intake` and
`best-intake` as permanent compatibility names, not competing workflows.

## Core law

Land source truth in this order:

`archive -> voices / channels -> work/daily`

Intake creates archive truth. It does not synthesize, verify claims, or
publish a daily brief.

## Workflow

1. Confirm the supplied body is materially real.
2. Classify the source form and resolve the strongest available publication
   date.
3. Resolve canonical voice and host routing without inventing a lane.
4. Preflight duplicate URL, identity, and path state.
5. Run the canonical helper in dry-run mode and inspect inferred metadata.
6. Land one real `archive/sources/YYYY-MM-DD/source-*.md` object while
   preserving the supplied body with minimal rewriting.
7. Apply only approved deterministic trim, ASR repair, and sectioning, in that
   order.
8. Publish the source and manifest transactionally, then verify manifest and
   voice-index routing.
9. Mark unresolved metadata provisional instead of stalling on enrichment.
10. Stop when the archive batch is grounded; hand judgment to
    `geo-strategy`.

## Voice and host attribution

Record the featured voice and host separately whenever the source has both.
The guest or named analyst is the canonical voice for voice-bounded analysis;
the host remains provenance metadata and must not replace the guest. Preserve
the distinction in manifest routing, source front matter, and downstream
historical-reference records. If the featured voice is uncertain, use a
provisional voice route and retain the host rather than inferring the guest
from the channel name or title alone.

Manifest role metadata is source-participation data, not a replacement for the
person shelf: keep `voice_slugs` person-only and add `voice_roles`,
`role_status`, and `role_basis`. Use `author` for authored work, `guest` for
an invited analyst, `host` or `co-host` for substantive framing, and
`panelist` for panel participation. Keep `host_kind` explicit (`channel`,
`show`, or `host-person`) and use publication fields only for authored
publication provenance. Ambiguity is `provisional` or `inferred`, never a new
person route. Strong quotation attribution requires a speaker-labeled turn
edge; a host introduction cannot inherit a guest's words.

## Canonical helper

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

## Boundaries

- Do not fetch a missing source body, synthesize the day, adjudicate claims,
  repair an existing source, or promote public material during intake.
- If a matching source already exists, use `archive-query` to establish scope
  and `archive-repair` for bounded correction.
- Preserve unrelated working-tree changes and keep the source plus manifest
  publication atomic.

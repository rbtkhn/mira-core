---
name: smart-intake
description: "Canonical Narrative Geopolitics source intake for pasted transcripts, Substack posts, essays, reports, and YouTube-linked source bodies. Use when Codex should classify the source, resolve date/voice/host metadata, detect duplicates, land archive truth, apply only approved normalization, and verify manifest/index routing."
preferred_activation: intake
activation: intake
portable: false
version: 1.0.0
category: narrative-geopolitics
status: active
---
# Smart Intake

**Canonical operator command:** say **`intake`**.

Internally, `intake` enters this smart-intake workflow and delegates archive
publication to the `best-intake` engine. Operators do not need to choose
between those names.

Smart intake is the canonical front door for source landing. It combines
best-intake’s archive/provenance rules with routine classification and
preflight. The implementation engine remains `scripts/land_best_intake.py`,
invoked through `scripts/smart_intake.py`.

## Core law

Read this stack in order:

`archive -> voices / channels -> work/daily`

Intake begins in `archive/`; it does not begin in synthesis or public surfaces.

## Required behavior

1. Confirm the body is materially real.
2. Classify source shape: transcript, interview, solo, newsletter, essay, or
   article.
3. Resolve the strongest available publication date and record uncertainty.
4. Resolve canonical voice and host routing; never invent a voice lane.
5. Preflight duplicate URL/path and incomplete-existing-capture conditions.
6. Land a real `archive/sources/YYYY-MM-DD/source-*.md` object.
7. Preserve the supplied body with minimal rewriting.
8. Apply only approved deterministic trim, ASR repair, and sectioning, in that
   order.
9. Append/normalize manifest and voice-index routing.
10. Verify the source, URL, metadata, manifest row, and index route.

The minimum adequate land has a real archive file, truthful title/date, source
URL or explicit unavailable status, provisional voice routing, host routing
when clear, and a manifest row.

## Routine command

```powershell
.\tools\run.ps1 intake-land --date YYYY-MM-DD --url URL --body-file PATH --dry-run
.\tools\run.ps1 intake-land --date YYYY-MM-DD --url URL --body-file PATH
```

Use explicit overrides when inference is ambiguous:

```powershell
.\tools\run.ps1 intake-land --pub-date YYYY-MM-DD --ingest-date YYYY-MM-DD \
  --url URL --body-file PATH --voice-slug SLUG --host-slug HOST \
  --source-form interview --dry-run
```

The wrapper delegates publication to the best-intake engine, so its rollback
and archive-integrity behavior remains authoritative.

## Safety and boundaries

- Do not synthesize, verify claims, or publish a daily brief during intake.
- Do not auto-trim judgment-dependent material.
- Treat operator-pasted text as unverified unless explicitly verified.
- If a matching URL already exists, inspect it for completeness before making
  a repair; do not create a duplicate.
- Keep unrelated worktree changes out of commits.

## Handoff

Stop when the archive batch is grounded. The next move is
`geopolitical-synthesis`.

## Compatibility

`smart-intake` and `best-intake` remain compatibility names for the workflow
and engine during migration; the operator-facing front door remains `intake`.
Existing prompts and `scripts/land_best_intake.py` remain supported.

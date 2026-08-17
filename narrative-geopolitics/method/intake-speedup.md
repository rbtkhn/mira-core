# Intake Speedup

This note turns the July 2026 intake slowdown diagnosis into an operating plan.

## What Actually Made Intake Slow

The bottleneck was not one giant problem. It was a stack of small manual costs
that repeated for every source:

1. read enough of each pasted transcript to infer title, date, host, guest, and routing
2. write a custom archive file by hand
3. hand-edit `archive/sources/geopolitics/source-manifest.json`
4. re-check voice and channel continuity during landing
5. verify the new source manually

That meant `best-intake` was acting like a careful editorial micro-project for
each item instead of a fast landing contract.

## Root Cause

Narrative Geopolitics has a `best-intake` doctrine, but it did not yet have a
matching `best-intake` mechanism.

The repo had:

- method guidance
- archive conventions
- templates

But it did not yet have a dedicated helper that could:

- create the archive file
- build the frontmatter
- append the manifest row
- increment `source_count`

in one pass.

## Design Rule

Intake speed improves when we separate **landing** from **enrichment**.

Landing should do only this:

- preserve the source body
- create a valid archive file
- append a manifest row
- mark uncertainty honestly

Small host-specific wrapper removal is allowed when it is deterministic,
reversible in principle, and clearly lower-value than the substantive source
body. Mario Nawfal opening chatter is the first approved case.

Landing should **not** pause for:

- full voice-shelf creation
- deep channel interpretation
- synthesis-grade quote extraction
- daily-brief readiness

## Immediate Fix

Use the helper at [../../scripts/land_best_intake.py](../../scripts/land_best_intake.py).

Default same-day flow is now paste-first. Metadata sidecars remain useful for
batch landing, retries, and oddball sources, but they are no longer the main
single-source path.

It automates the slowest repeated operations:

- slugging the source title
- creating `archive/sources/geopolitics/sources/YYYY-MM-DD/source-*.md`
- writing standard frontmatter
- appending a manifest row
- incrementing manifest `source_count`
- applying approved deterministic trim
- applying conservative ASR repair for approved transcript hosts when corruption is obvious and low-risk
- applying conservative semantic sectioning for approved transcript shapes when confidence is high enough

## New Fast Path

For routine one-off intake, use quick mode:

```powershell
.\tools\run.ps1 intake-land --quick `
  --date today `
  --host-slug judging-freedom `
  --url "https://www.youtube.com/watch?v=..." `
  --body-file "C:\path\pasted-text.txt"
```

The host may also be supplied positionally for a compact invocation:

```powershell
.\tools\run.ps1 intake-land --quick breaking-points "https://www.youtube.com/watch?v=..." `
  --date today --body-file "C:\path\pasted-text.txt"
```

Use `--dry-run` to inspect inferred title, routing, provenance basis, and the
planned archive path without writing files. Quick mode preserves the same
provisional routing and approved processing rules as full intake.

For each pasted transcript:

1. Provide the pasted body plus source URL and date to `best-intake`.
2. Let `land_best_intake.py` infer title, host, guest, source form, and provisional routing when the signals are clear.
3. Use explicit metadata mode only when the inference surface is weak or the batch is large enough to justify sidecars.
4. Review the generated archive file header once.
5. Defer voice/channel enrichment unless the source is immediately synthesis-critical.

## Minimal Metadata Rule

Require only:

- `pub_date`
- `ingest_date`
- `url`
- `body`

Infer by default when possible:

- `title`
- one provisional `voice_slug`
- `host_slug`
- `host`
- `guest`
- `show_title`
- `channel_name`
- `source_form`

Optional:

- `source_class`
- `editorial_note`
- explicit sidecar / `body_file` mode for batch work

If the optional fields are unclear, land with provisional metadata instead of
stopping the batch.

## Operational Rules

- Missing voice shelf is not an intake blocker.
- Missing channel shelf is not an intake blocker.
- If host identity is only moderately clear, route provisionally and continue.
- If title cleanup is imperfect but truthful, continue.
- If transcript quality is noisy but the repair is obvious and low-risk, repair it and continue.
- If the repair depends on judgment, preserve the noise and continue.

## Recommended Batch Workflow

Use two passes:

### Pass 1: landing

- land every source
- preserve body
- create manifest row
- do no synthesis work

### Pass 2: enrichment

- fix titles if needed
- expand voice continuity when warranted
- open channel shelves only for synthesis-relevant items
- create the daily run after the archive batch is complete
- hand off to `geo-strategy` for guided bootstrap, reconciliation, or execution

Sectioning is no longer purely deferred enrichment. For approved hosts it now
belongs to landing when the transcript has strong structural cues; otherwise the
transcript is preserved unsectioned and can be revisited later.

ASR repair is now also part of landing, but only in a conservative form:

- fix obvious repeated corruption
- remove obvious leftover transcript wrappers
- avoid semantic rewriting
- skip anything that depends on judgment

## Remaining Improvement

Add a manifest regeneration command if central-manifest repair remains a
recurring operator cost. Archive generation, manifest publication, and failure
rollback now have dedicated tests.

## Success Standard

`best-intake` is fast enough when a same-day five-source batch feels like:

- one metadata decision per source
- one helper invocation per source
- one quick verification pass for the batch

not five bespoke archival compositions.

Measure the actual ingestion cohort with:

```powershell
.\tools\run.ps1 intake-stats --ingested-since YYYY-MM-DD --json
```

Do not use publication-date reports as a proxy for recent operator work.

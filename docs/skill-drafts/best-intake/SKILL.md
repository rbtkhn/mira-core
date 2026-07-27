---
name: best-intake
description: "Internal implementation engine for the canonical intake front door; retained for compatibility with legacy best-intake prompts."
preferred_activation: intake
activation: intake
portable: false
version: 0.2.0
category: narrative-geopolitics
status: active
---
# Best-Intake Implementation Engine

`intake` is the sole operator-facing source-intake command. This file documents
the implementation engine used by the smart-intake workflow and preserves
legacy compatibility.

See [../smart-intake/SKILL.md](../smart-intake/SKILL.md).

Operators should say **`intake`**, not choose between internal workflow names.

Use this skill for `narrative-geopolitics/` when the job is to land source truth
fast enough to keep the day moving, without pretending that intake is already
full synthesis.

## Core law

Read this stack in order:

`archive -> voices / channels -> work/daily`

Intake begins in `archive/`. It does not begin in `synthesis.md`,
`daily-brief.md`, or `public/`.

## Use this skill when

- the operator pasted a transcript or source body
- a same-day source needs to land under `archive/sources/YYYY-MM-DD/`
- throughput matters more than perfect enrichment
- voice and host routing are partly clear but not fully finished

## Do not use this skill when

- the source still needs to be fetched
- the task is to write the evening daily judgment
- the task is to publish or promote a public brief

## Adequacy standard

A `best-intake` land is adequate when it has:

- a real archive file
- preserved source body
- a truthful title and date
- a source URL when available, or an explicit unavailable status
- at least one provisional `voice_slug`
- a `host_slug` when clear
- a manifest row

It does not need complete voice continuity, channel interpretation, quote
curation, claim extraction, or final `daily-brief.md` authoring.

## Deterministic trim law

Deterministic trim is allowed only for approved host-owned wrapper chatter that
is clearly separable from substantive content.

Current approved hosts:

- `mario-nawfal`
- `daniel-davis`
- `alexander-mercouris`
- `dialogue-works`
- `moral-resistance`

Current approved auto-section hosts:

- `dialogue-works`
- `glenn-diesen`
- `daniel-davis`
- `judging-freedom`
- `alexander-mercouris`
- `mario-nawfal`
- `moral-resistance`

Current approved auto-ASR-repair hosts:

- `dialogue-works`
- `glenn-diesen`
- `daniel-davis`
- `judging-freedom`
- `alexander-mercouris`
- `mario-nawfal`
- `moral-resistance`

If the cut depends on judgment, do not automate it during intake.

## Workflow

For routine one-off sources, the repository helper supports `--quick` with a
date, URL, body file, and optional host override; use `--dry-run` to inspect
inferred metadata before landing.

1. Confirm the source body is materially real.
2. Land the source under `archive/sources/YYYY-MM-DD/source-*.md`.
3. Preserve the pasted body with minimal rewriting.
4. Apply only approved deterministic trim when the host rule matches.
5. Apply conservative ASR repair only for approved hosts and obvious low-risk corruption.
6. Apply conservative semantic sectioning only when the host is approved and the transcript has strong cues.
7. Append or normalize the manifest row.
8. Mark uncertainty honestly instead of stalling on enrichment.
9. Stop once the day batch is archive-grounded.

The executable order is always:

`deterministic trim -> conservative ASR repair -> conservative sectioning`

Preflight the complete batch before publishing. New source files and the
manifest are staged together; a handled publication failure must leave the
original manifest intact and remove newly published source files.

## Handoff

`best-intake` ends when the archive truth is good enough for the day to become
reviewable.

Next move:

`geopolitical-synthesis`

Short rule:

`best-intake lands the day; geopolitical-synthesis judges the day`

Intake creates the manifest row count that later density review uses, but it
does not interpret source density. Do not add hooks, issue weight, operational
truth, or synthesis confidence during landing merely because a batch is thin or
dense. Density review belongs to `geopolitical-synthesis` or audit work.

## Repo surfaces

- `narrative-geopolitics/method/best-intake.md`
- `narrative-geopolitics/method/intake-speedup.md`
- `narrative-geopolitics/templates/intake-metadata.md`
- `scripts/land_best_intake.py`
- `scripts/report_trim_stats.py`

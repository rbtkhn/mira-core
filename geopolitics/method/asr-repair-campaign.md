# ASR Repair Campaign

This note defines when deeper ASR repair is worth doing in
`narrative-geopolitics/`.

The governing rule is simple:

```text
repair for downstream judgment utility, not for transcript prettiness
```

## Purpose

Deeper ASR repair is justified only when transcript noise is actively harming:

- daily synthesis speed
- section-label quality
- cross-voice comparison
- quote extraction confidence
- archive retrieval quality

It is not justified merely because a transcript reads awkwardly.

## Repair Tiers

### Tier 1: judgment-critical

Repair now when the file is likely to be reused in:

- daily synthesis
- forecast review
- same-object cross-voice comparison
- recurring crisis tracking

Target outcome:

- synthesis-grade reliable

### Tier 2: navigation-critical

Repair when ASR noise degrades:

- section labels
- search hits
- proper noun retrieval
- archive browseability

Target outcome:

- clean enough for sectioning and retrieval

### Tier 3: quote-critical

Repair when the transcript is likely to support:

- direct quotation
- claim extraction
- public-facing draft language

Target outcome:

- wording reliable enough for citation review

### Tier 4: archive-only

Do not repair yet when the file is:

- low reuse
- low quote value
- already good enough for routing and day judgment

Target outcome:

- preserve and defer

## Scoring Rubric

Score each candidate `0`, `1`, or `2` on every axis.

### Reuse Frequency

- `0` = unlikely to be revisited
- `1` = plausible later reuse
- `2` = already central to June-July judgment work

### Sectioning Failure Severity

- `0` = headings already clean or file is unsectioned for good reason
- `1` = mixed quality
- `2` = headings are visibly ASR-shaped or misleading

### Proper Noun Corruption

- `0` = minor
- `1` = moderate
- `2` = recurring corruption of actors, places, institutions, or crises

### Quote Likelihood

- `0` = low
- `1` = some chance of later quotation
- `2` = strong candidate for quoting or claim extraction

### Voice Strategic Weight

- `0` = peripheral to current stack
- `1` = useful but not core
- `2` = core recurring voice or host lane

### Transcript Density

- `0` = sparse or short enough that noise does not matter much
- `1` = moderate density
- `2` = dense enough that noise compounds across sections

## Decision Bands

- `10-12` = repair now
- `7-9` = repair in pilot or opportunistically
- `4-6` = defer unless needed by a live day run
- `0-3` = preserve as-is

## Allowed Repair Scope

In this campaign, deeper ASR repair may:

- fix obvious proper nouns
- fix repeated geopolitical entity corruption
- repair sentence breaks that block comprehension
- clean repeated filler collisions when the intended wording is obvious
- improve speaker-transition clarity

It may not:

- paraphrase substance
- silently rewrite claims
- compress long answers into summaries
- convert uncertain wording into fake precision
- treat repaired wording as human-verified verbatim

## Repair Standard

The target is not perfect transcription.

The target is:

```text
synthesis-grade reliable, quote-aware, still honest about provenance
```

## ROI Test

A repair pass is high ROI only if it produces measurable improvement in at
least one of these:

- section-label quality improves materially
- the file becomes easier to synthesize against neighboring voices
- quote extraction confidence improves
- retrieval/search quality improves
- the next day run is faster because less manual interpretation is needed

If a repair pass does not improve one of those outcomes, it should not scale.

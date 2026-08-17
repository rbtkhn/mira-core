# Best Intake

`best-intake` is the default source-intake contract for Narrative Geopolitics.

It exists to solve one problem: intake should be fast enough to keep same-day source batches moving, but reliable enough that the archive does not fill with misleading half-truths.

## Purpose

`best-intake` is not the fastest possible intake mode and not the most exhaustive possible intake mode.

It is the best tradeoff between:

- speed
- source preservation
- honest uncertainty
- later retrievability
- downstream voice and channel work

Short rule:

```text
land quickly, preserve truthfully, defer safely
```

## Core Principle

The first obligation of intake is not interpretation.

The first obligation of intake is to make sure a source is:

- landed
- attributable
- recoverable
- linkable
- reviewable

If that happens, later enrichment can improve the record.

If that does not happen, later enrichment has nothing durable to work on.

## Best-Intake Standard

A `best-intake` source is adequate when it has:

- a real archive file under `archive/geopolitics/sources/YYYY-MM-DD/`
- a working source title
- a source URL when available
- the pasted body preserved
- a publication date or best-known provisional date
- at least one provisional `voice_slug`
- a `host_slug` when obvious
- an explicit review state when certainty is incomplete
- a manifest row

Title and routing integrity rules:

- Prefer a materially identifiable title embedded in the supplied transcript. Preserve an operator-supplied alternate in `title_aliases`; do not shorten or editorially rewrite the selected title.
- If the operator supplies no channel and the channel is inferred from a title, URL, or body cue, record the route as provisional and retain the evidence basis. Do not label an inference as explicit-host.
- Use canonical channel display names and slugs. For example, the display name is `Reason to Resist` and the slug is `reason-resist`.

It does **not** need full routing, perfect family calibration, or public-synthesis readiness at landing time.

## Required Inputs

Minimum operator inputs:

- `date`
- `url` when available
- `body`
- `title` only when the pasted body does not expose one cleanly

Default posture:

- paste first, infer the rest
- `land_best_intake.py` should infer title, host, channel, source form, and provisional routing when the signals are strong enough
- one blocker is allowed only when host identity, solo-vs-interview shape, or primary guest ownership is genuinely ambiguous
- otherwise the source should land provisionally instead of stalling

Optional overrides:

- `voice_slug`
- `host_slug`
- `modality`
- `source_form`

Metadata sidecars remain valid for batch or edge-case work, but they are no
longer the preferred same-day one-off flow.

If optional fields are unclear, preserve uncertainty instead of inventing precision. If the host is inferred, use `routing_state: provisional` and an inference basis such as `title-cue` or `body-cue`.

When no recoverable public URL exists, intake remains valid. New source
frontmatter records `source_url: ""` and `source_url_status: unavailable`.
When a URL is present it records `source_url_status: provided`. The generated
`operator-paste://` upstream path is provenance, not a substitute public URL.

The central manifest is authoritative for host and voice routing. Archive
frontmatter may duplicate those fields for convenience, but older sources do
not need retroactive header rewrites when their manifest routes are complete.

## What Best-Intake Does

`best-intake` should:

1. Create the source file in `archive/geopolitics/sources/YYYY-MM-DD/`.
2. Infer title, host, guest, channel, and source shape when the signals are strong enough.
3. Preserve the pasted source body with minimal rewriting.
4. Apply approved deterministic wrapper trim when the host rule matches.
5. Apply conservative ASR repair for approved hosts when the corruption is obvious and low-risk.
6. Apply conservative semantic sectioning when structural cues are strong enough.
7. Add only enough frontmatter to keep provenance and retrieval usable.
8. Append a manifest row.
9. Mark uncertainty explicitly when classification is provisional.

The executable transformation order is fixed:

```text
deterministic trim -> conservative ASR repair -> conservative sectioning
```

Every normal landing runs a read-only preflight first. Use `--preflight` to
inspect the receipt without writing, and add `--json` for machine-readable
output. The receipt includes the YouTube video ID, canonical source identity,
duplicate status, title/date/routing basis, planned path, transformations, and
warnings. Warnings do not block landing; duplicate identities and path
collisions remain idempotent safety stops.

Source identity is `youtube:<video-id>` for YouTube URLs and the normalized URL
for other sources. This identity is the manifest-level duplicate key.

Date basis is recorded as `transcript-self-date`, `operator-supplied`,
`verified-platform`, or `provisional-intake`. When no stronger date exists, an
operator-supplied date is valid but remains explicitly provisional in the
source note.

Before writing, the helper preflights the full batch, generated paths, existing
manifest paths, and collisions. It stages all source files and the proposed
manifest, publishes the sources, then atomically replaces the manifest. A
handled failure before manifest publication removes newly published sources
and preserves the original manifest. Process or power-loss recovery is outside
this exception-safe guarantee.

## What Best-Intake Defers

`best-intake` should usually defer:

- deep title cleanup
- host-conditioning interpretation
- source-index updates beyond what is necessary
- voice-lens synthesis
- daily-brief authoring
- quote curation
- claim extraction
- forecast generation

It also defers canonical voice-identity normalization and durable shelf
reconciliation. The manifest field `voice_index_path` is the archive link as it
would be used from a voice directory; it is not evidence that a voice shelf was
updated.

Short rule:

```text
archive now, interpret later
```

The downstream handoff is:

```text
best-intake
-> canonicalize alias-affected voice metadata
-> reconcile existing voice source indexes
-> geo-strategy
```

Person identity uses the canonical `voices/<slug>/` directory name. Host and
channel identity remains separate: `host_slug: alexander-mercouris` can route
to the canonical `mercouris` voice.

Small deterministic wrapper removal is allowed when it saves obvious intake
waste without changing source meaning. Current approved case:

- `mario-nawfal` opening camera / rapport chatter before the real setup begins
- `mario-nawfal` closing scheduling / signoff chatter after the substantive interview ends
- `daniel-davis` closing next-show / subscribe / channel-promotion chatter after the substantive interview ends
- `alexander-mercouris` routine solo subscribe / platform signoff wrapper and standard subscribe reminder sentence in the opening
- `dialogue-works` transcript wrapper removal when a pasted body begins with a `... - YouTube` title line followed by `Transcripts:`

Conservative ASR repair is also allowed for approved transcript shapes. It runs
after trim and before sectioning, and is limited to obvious low-risk repairs
such as:

- repeated wrapper remnants like bare `Transcripts:`
- stable place or institution corruption like `Anchora` -> `Ankara`
- repeated crisis-object corruption like `straight of hormones` -> `Strait of Hormuz`
- visibly duplicated low-signal fragments where the intended wording is obvious

Conservative semantic sectioning is also allowed for approved transcript
shapes. It runs after trim and ASR repair, inserts `###` headings directly into
`## Transcript`, and skips the file entirely when semantic confidence is weak.

## Deterministic Trim Policy

Deterministic trimming is allowed only when the trim target is format noise,
not source substance.

Approval standard:

- the wrapper is recurring, not one-off
- the wrapper is host-format chatter, not guest analysis
- the cut point is detectable by stable phrase markers
- false-positive risk is low
- if the pattern is ambiguous, do not automate it

Safe deterministic trim:

- repeated host intros that occur before the real setup begins
- repeated host signoff or schedule chatter after the real interview ends
- repeated subscription or sponsor-style language that is clearly outside the source object

Unsafe semantic trim:

- removing setup because it "feels low value"
- deleting material that blends host framing with guest substance
- collapsing multi-speaker openings when the first substantive claim is not clearly separable

Short rule:

```text
if the cut depends on judgment, it is not deterministic trim
```

## Survey And Approval Workflow

When evaluating a new host or channel for trim automation:

1. Collect 3 to 5 archived examples for one `host_slug`.
2. Inspect the first and last transcript segments.
3. Record repeated low-value wrapper phrases.
4. Reject the host if the cut point overlaps with substantive setup too often.
5. Add a rule only after the markers are documented and look stable.
6. Validate on one fresh landing and inspect the saved chars and words.
7. Keep the rule list curated. Do not auto-generate trim rules from transcripts.

Candidate and approved are different states:

- candidate = worth surveying
- approved = safe enough for deterministic auto-trim

Current candidate-only hosts:

- none currently documented here

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

## Handoff To Synthesis

`best-intake` ends when the source is safely archived and manifest-backed.

The next job is usually `geo-strategy`, not more intake polishing.
Source density is created by intake because every manifest row changes the
day's source count, but density is not interpreted during landing. Use
[archive-density](archive-density.md) during synthesis or audit to decide
whether a day is thin, dense, overclaim-prone, underused, or verification-heavy.

Short rule:

```text
best-intake lands the day; geo-strategy judges the day
```

That handoff should follow this order:

1. finish the day's archive intake
2. confirm the manifest day batch is materially real
3. open `work/daily/YYYY-MM-DD/`
4. use `geo-strategy` to bootstrap, reconcile, deepen, or execute the run

`best-intake` does not need to produce a finished `daily-brief.md`, forecast,
or full daily judgment before the handoff. It only needs to leave the archive
truth in a state that makes those downstream moves possible.

## Status Model

Every `best-intake` source should be legible about its state.

These are landing-time states, not lifecycle states. `unreviewed` and
`provisional` mean that intake deferred enrichment; they are not expected to be
rewritten after a source is used. Daily validation derives `landed` and
`consumed` from archive, manifest, and intake-table agreement.

Suggested state fields:

- `review_state: unreviewed`
- `routing_state: provisional`
- `source_form: unknown`
- `host_slug: null`

Use these only when needed. The point is not to create bureaucracy; the point is to avoid false completeness.

## Decision Rules

### Use Best-Intake By Default

Use `best-intake` for:

- operator-pasted same-day transcripts
- recurring voice sources with known ownership
- solo analyst uploads
- clearly attributable interviews
- same-day batch work where throughput matters

### Use Best-Intake With Caution

Use `best-intake` but mark provisional state for:

- uncertain host ownership
- likely clipped excerpts
- unclear modality
- mixed-format captures
- multi-speaker objects where one voice is primary but not exclusive

### Block Auto-Confidence

Do not let `best-intake` silently claim certainty for:

- panel ownership
- channel conditioning
- excerpt vs full-source distinction
- voice dominance in ambiguous multi-speaker material

When uncertain:

```text
land provisionally and flag for enrichment
```

## Failure Modes

`best-intake` fails when:

- speed is purchased by losing source truth
- provisional metadata is mistaken for final metadata
- ambiguous ownership is flattened into fake certainty
- the archive accumulates permanently unreviewed records with no later pass

This means `best-intake` must be paired with a later enrichment path.

## Enrichment Relationship

`best-intake` is a landing contract, not a finishing contract.

## Measuring Gain

Trim savings should be measurable by host, not anecdotal.

Newly landed sources can record:

- `opening_trim_applied`
- `opening_trim_rule`
- `opening_trim_chars_saved`
- `opening_trim_words_saved`
- `closing_trim_applied`
- `closing_trim_rule`
- `closing_trim_chars_saved`
- `closing_trim_words_saved`
- `asr_repair_applied`
- `asr_repair_pass`
- `transcript_curation`
- `section_count`
- `section_pass`

For host-level reporting, use:

```powershell
.\tools\run.ps1 intake-stats
.\tools\run.ps1 intake-stats --host-slug mario-nawfal
.\tools\run.ps1 intake-stats --ingested-since YYYY-MM-DD --json
```

For attempt-level outcome measurement, save JSON receipts from bounded intake
runs and aggregate them in chronological order:

```powershell
.\tools\run.ps1 intake-outcomes path\to\receipt-01.json path\to\receipt-02.json --json
```

Each preflight receipt reports attempted sources, warnings, duplicate stops,
title or metadata correction signals, successful landings, and failed attempts.
The aggregator counts a retry only when the same canonical source identity
appears in more than one terminal receipt. A normal preflight followed by one
landing is not a retry. Receipts are operator-selected operational evidence;
they do not enter the archive or support geopolitical claims.

When a landed batch predates saved receipts, establish a source-state baseline
without inventing attempt outcomes:

```powershell
.\tools\run.ps1 intake-outcomes --source-baseline archive\geopolitics\sources\YYYY-MM-DD --json
```

This reconstruction may measure landed sources, provenance bases, aliases, and
metadata warnings. It must label duplicate stops, failures, and retries
unavailable rather than reporting them as zero.

Reporting interprets automatically generated section state conservatively:

- `useful_sectioning` requires at least two headings;
- `weak_sectioning` includes one-heading transcripts;
- `preserved_unsectioned` records an explicit no-section result;
- `curation_state_missing` means the source predates the current metadata pass.

Similarly, `asr_checked_no_change` and `asr_state_missing` are distinct. A
missing field must not be counted as a clean ASR check.

## Measurement Hold

Do not add trim hosts, ASR substitutions, or sectioning heuristics until two
weeks of recent-intake reporting show a repeated correction cost or retrieval
gain. Do not run another mass retrofit merely to normalize metadata generations.

Its companion step is a later enrichment pass that can:

- refine source form
- refine modality
- update routing surfaces
- improve title accuracy
- support daily synthesis

The system should treat these as separate jobs.

## Why Best-Intake Is Better Than Fast-Intake Alone

Pure `fast-intake` is optimized almost entirely for throughput.

That is useful, but alone it can overproduce low-confidence records.

`best-intake` keeps most of the speed gains while adding two protections:

- explicit provisionality
- minimum retrieval integrity

So the contract is:

- faster than full bespoke intake
- safer than raw fast landing
- more scalable than manual perfection

## Voice Adequacy Claim

`best-intake` is adequate for all voice intakes because every voice shares the same first archival need:

- preserve source truth quickly
- preserve provenance honestly
- preserve enough metadata for later recovery

Voices differ mainly in interpretation and conditioning, not in the minimum conditions for safe landing.

That is why `best-intake` can serve:

- Pape
- Mercouris
- Marandi
- Mearsheimer
- Davis
- Diesen

and future voices as well.

## Repository Rule

When there is tension between:

- finishing intake perfectly
- and keeping source throughput alive

prefer `best-intake`, provided the source remains honest, archived, and reviewable.

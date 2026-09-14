---
name: youtube-capture
description: "Repository-local cross-archive YouTube channel discovery and transcript-capture routing workflow. Use when the operator asks to check today's YouTube channels, discover recent channel videos, triage YouTube capture rows or targets, attach a YouTube transcript, explain channel routing, audit capture routing, or prepare intake drafts. Do not use for archive landing, synthesis, factual verification, signal extraction, publication, staging, commit, or push."
---

# YouTube Capture

YouTube Capture is the single repository-local front door for YouTube source
discovery. It discovers or records candidate videos, resolves the channel to
the correct archive lane, and writes only capture-stage outputs for later
governed intake.

It must not assume Narrative Geopolitics. Route by channel first.

Use this skill for requests such as:

- `check today's YouTube channels`
- `youtube-capture`
- `run the channel check`
- `find recent Nate Herk videos`
- `triage the YouTube queue`
- `attach this transcript`
- `explain this channel route`
- `audit YouTube capture routing`
- `prepare intake drafts for ready YouTube rows`

## Boundary

Tower's explicit current/pending geopolitics completion request supplies bounded
authority to survey today's curated daily channels, capture eligible transcripts,
and continue through Archive Intake and Geo-Strategy to a notebook contribution.
Use `mira-youtube` as the command front door (capture commands forward here).
Tower's survey-plan is read-only; `mira-youtube discover` consumes supplied
evidence and is not browser automation. Preserve browser coverage and access
receipts, route transcripts through capture attachment, and do not repeat approval
for routine eligible rows inside that explicit batch. Generic Tower invitations
and historical readings do not grant this envelope. Capture itself still does
not perform archive admission or analysis.

This workflow may create or update capture-stage outputs only:

- Geopolitics channels route to queue rows under
  `narrative-geopolitics/work/capture/youtube/`.
- Singularity channels such as Nate Herk and Nate B. Jones route to dated
  capture-target notes under `archive/sources/singularity/`.

It must not admit archive sources, mutate source manifests, extract
Singularity signals, synthesize a daily packet, verify claims, publish, stage,
commit, push, or deploy unless a later workflow receives separate explicit
authority.

Use neighboring workflows this way:

- supplied transcript ready for archive admission -> `archive-intake`;
- inventory, duplicates, or landed membership -> `archive-query`;
- source-body, ASR, metadata, or sectioning repair after landing ->
  `archive-repair`;
- manifest-backed geopolitical judgment -> `geo-strategy`;
- operational factual adjudication -> `reality-check`;
- Singularity signal extraction after source admission -> the governed
  Singularity analysis route, not raw capture.

If a YouTube source is already landed, do not re-land it through capture. Mark
or prune the capture output, then use `archive-query` or the landed source path.

## Routing Contract

The cross-archive route index is
`archive/sources/youtube-channel-routing.yml`. Read it before writing capture
outputs for a channel not already governed by the Geopolitics channel index.

Route records define channel handle, canonical URL, aliases, archive lane,
shelf, duplicate-check scope, output kind, and target template. Unknown
channels fail closed: do not guess an archive lane, do not fall back to
Geopolitics, and do not add the channel to
`narrative-geopolitics/channels/channel-index.md` unless it is genuinely a
Geopolitics channel.

Automatic routing checks explicit cross-archive routes first, then resolves
known Geopolitics channels through the delegated channel index. A delegated
match preserves the canonical `channel_slug` for intake export. Unknown or
ambiguous delegated channels fail closed; an explicit lane override is not a
substitute for resolving a known channel.

Use route explanation when the target lane matters:

```powershell
tools\run.ps1 youtube-capture route-explain --channel "Nate Herk"
tools\run.ps1 youtube-capture route-explain --url https://www.youtube.com/@NateBJones --json
```

Use route audit before claiming a routing repair is clean:

```powershell
tools\run.ps1 youtube-capture route-audit --json
```

Nate Herk and Nate B. Jones route to Singularity capture-target notes:

```powershell
tools\run.ps1 youtube-capture add --date YYYY-MM-DD --channel "Nate Herk" --url VIDEO_URL --title "TITLE" --published-at ISO_TIMESTAMP
tools\run.ps1 youtube-capture add --date YYYY-MM-DD --channel "Nate B. Jones" --url VIDEO_URL --title "TITLE" --published-at ISO_TIMESTAMP
```

These commands update:

- `archive/sources/singularity/nate-herk-capture-targets-YYYY-MM-DD.md`
- `archive/sources/singularity/nate-b-jones-capture-targets-YYYY-MM-DD.md`

The target note records video URL, title, publication date, channel, observed
date, absence check, and next eligible workflow. It is not transcript admission
and must not update `archive/sources/singularity/singularity-signal-ledger.*`.

Singularity duplicate checks use the route's `duplicate_check_scope`, including
earlier dated capture-target notes. `already-captured` means a pending capture
exists; `already-landed` means a transcript-shelf match exists. Neither result
is a newly discovered source, and a pending capture does not prove admission.

Target-note table cells use versioned HTML entity encoding so titles containing
pipes, literal entities, or line breaks survive later updates. The reader also
accepts unencoded legacy notes. A malformed existing table row stops the write
without changing the note; inspect the reported row rather than dropping it.

## Standard Geopolitics Channel Check

For the daily Geopolitics channel check, run from the repository root:

```powershell
tools\run.ps1 youtube-capture daily-check --date YYYY-MM-DD --include-active --include-candidate
tools\run.ps1 youtube-capture status --date YYYY-MM-DD
tools\run.ps1 youtube-capture audit-duplicates --date YYYY-MM-DD
tools\run.ps1 youtube-capture browser-coverage --date YYYY-MM-DD
```

`daily-check` is the operator-facing daily front door for the Geopolitics
channel index. It runs `scan-index` and `discover-public` as seed steps, prints
the required Tier A browser checklist, and fails closed until every selected
Tier A channel has a valid browser receipt. Use `discover-public` directly only
when you explicitly want the low-level RSS/public-metadata seed without
claiming daily discovery is complete.

For an authenticated daily run, the signed-in YouTube **Subscriptions** feed is
the primary discovery surface. Inspect the feed first, retain only rows whose
visible publication state is the target capture date, and then open each
candidate watch page to verify the exact title, canonical video URL, channel,
and publication or stream date. The feed is not complete merely because a row
appears near the top: continue through the target-day window until the visible
timestamps move older than the target date. Scheduled or future live items
(`Live in ...`, `Scheduled for ...`, or a future calendar date) are excluded.
Global search, Home, recommendations, and RSS are supplemental seed surfaces;
they must not replace the Subscriptions-first pass for a signed-in daily run.

Use the current local date unless the operator supplies another date. RSS is a
seed source only. `discover-public` reads the full available feed, applies the
date window, and only then applies `--limit-per-channel`; never truncate the
newest feed entries before date filtering. Raise `--limit-per-channel` or
`--since-days` only when the operator asks for wider candidate coverage.

Every browser-discovered row in a daily report must carry the visible title,
channel, canonical watch URL, and exact visible date basis. A row with only a
video ID, search-result association, relative age, or unverified title is a
candidate requiring watch-page inspection, not a completed daily result.

Duration is a required triage field for every video row shown to the operator.
Do not close duration from RSS, search result cards, recommendation cards,
stale queue values, or a player state that may still be an ad or partial page
load. Open each candidate or approved watch URL in the in-app browser, clear or
skip ads where possible, and use the post-ad player runtime. When the player
runtime is missing, contradicted, or suspiciously short, export or inspect the
YouTube transcript and use the final timestamp as the minimum runtime evidence.
Record contradictions in notes. A false short duration must not be used to
filter out an operator-selected item.

Queue files are named for the capture run. Each video row stores
`capture_date` separately from `publication_date`; the compatibility `date`
field follows `publication_date` when public metadata supplies one. Do not
mistake the queue filename or capture date for the episode's publication date.

For daily Geopolitics work, configured `daily` cadence channels are the Tier A
browser set unless the operator supplies explicit `--channel` selections. Tier
A completion fails closed until `browser-coverage` finds a valid receipt for
every selected channel. RSS rows, including an empty or apparently current
feed, never satisfy this gate.

For channel-discovery briefs that rank URLs by expected value, run filtering
before ranking. Filtering decides which rows may compete in the main list;
ranking decides their order.

Use this filter sequence:

1. Date: the main list includes only the target date unless the operator asks
   for a wider window. Put adjacent-day rows in a separate recent-context
   bucket.
2. Form: exclude shorts, teaser clips, duplicate uploads, and headline
   fragments unless the operator selects them.
3. Object fitness: keep rows tied to the day's crisis object or to an
   explicitly named strategic mechanism. Do not let generic breaking-news
   intensity substitute for object fit.
4. Mechanism transfer: when the operator has developed or named a mechanism,
   preserve substantive cross-theater exemplars of that mechanism even when
   they are outside the headline theater.

Only after filtering should the brief rank by expected value: mechanism
clarity, crisis-object relevance, cross-theater transfer value, transcript
readiness, voice/source value, and actionability.

## Named Voice Retrospective Discovery

For requests to find new YouTube URLs for a named voice across a month, year,
or administration period, treat the work as browser-first discovery unless the
operator explicitly asks for RSS only. If the operator says browser-only,
in-app browser only, or forbids a helper such as `yt-dlp`, do not use that
helper for discovery, transcript capture, metadata closure, or duplicate
resolution during the current YouTube task; rely only on visible browser
observations and repository-local manifest, shelf, target-note, or queue
checks.

Use the route index first. For Geopolitics regular channel scope, use
`narrative-geopolitics/channels/channel-index.md`: `daily` cadence channels are
the regular Tier A browser set, `weekly` cadence channels are the regular Tier
B browser set, and `manual` or `candidate` channels require explicit mention or
a clearly stated candidate-channel result. This channel index is not the
global YouTube index.

Use this sequence:

1. Resolve the archive lane from the channel route index or Geopolitics
   channel index and state the active channel scope.
2. Search YouTube in the in-app browser for the named voice, bounded date
   range, and selected channel names or handles.
3. Exclude shorts, chapter links, clips, mirrored snippets, and rows where the
   visible title/channel/date does not support the named voice as a featured
   participant.
4. Check candidate video IDs against the routed lane's duplicate scope before
   calling them new.
5. Write the routed capture output only when the operator asks for
   `youtube-capture`; otherwise return a browser-discovery-only receipt and
   wait for capture authority.

For a browser-discovery-only receipt, report the searched surface, candidate
URLs, excluded duplicate or already-landed IDs, excluded shorts/clips, whether
any row came from outside the regular channel set, and the authority boundary:
no queue mutation, target-note mutation, archive admission, voice promotion,
signal extraction, staging, commit, push, or synthesis occurred.

Discovery does not canonicalize a voice. A single captured or landed item may
support a provisional `expected_voice` value in a Geopolitics queue row, but it
must not create a new voice shelf or profile unless the voice promotion gate in
`narrative-geopolitics/voices/README.md` is satisfied or the operator gives an
explicit override for that exact voice.

For manually added or browser-discovered Geopolitics rows, put the canonical
channel route in structured metadata when the tool supports it, and include
`channel_slug=SLUG` in notes when that is the current `intake-draft` contract. For
Singularity targets, use the routed capture-target note template instead.

If Windows console encoding fails on titles, rerun status or duplicate audit
with UTF-8 output forced:

```powershell
$env:PYTHONIOENCODING='utf-8'; tools\run.ps1 youtube-capture status --date YYYY-MM-DD
$env:PYTHONIOENCODING='utf-8'; tools\run.ps1 youtube-capture audit-duplicates --date YYYY-MM-DD --json
```

## Triage

Use queue dispositions consistently for Geopolitics rows:

- `must-land`: optional priority label for a direct source tied to the current
  issue, featured voice, forecast review, crisis object, or high-value
  mechanism. It is not required for intake readiness.
- `possible`: plausible context or segment candidate; review before transcript
  retrieval.
- `skip`: shorts, already-landed duplicates, off-topic rows, or items outside
  the current focus.
- `watch`: channel front-door rows or unreviewed channel/video rows.

For operator-facing tables, display only the simplified status vocabulary:
`done`, `ready`, `needs transcript`, `queued`, `excluded`, or `blocked`.
Underlying `watch` rows should appear as `queued` unless a more specific
display status applies. For `mira-youtube` and all operator-facing YouTube
capture results, always show a video table with at least these columns:
`Title`, `Channel`, `Date`, `Duration`, and `URL`. Additional columns such as
`Status`, `Transcript`, `Notes`, or `Next action` may be added when useful, but
they must not replace those five required columns. Duration is the operator's
primary way to distinguish full episodes from clips.

Update Geopolitics queue rows with:

```powershell
tools\run.ps1 youtube-capture mark --date YYYY-MM-DD --url URL --disposition must-land --next-action "retrieve transcript or manual transcript capture, then export intake draft" --notes "reason"
```

Do not treat title relevance as source truth. A `must-land` mark means the row
deserves transcript capture, not that its claims are verified or synthesis-ready.
Once a transcript file is attached, readiness is determined by
`transcript_status=available`, a present `transcript_path`, and not already
landed in the manifest. Do not require a `must-land` disposition just to prepare
or run intake.

If the visible page says captions are unavailable, or transcript controls are
hidden, still try the in-app browser YouTube transcript export before declaring
the row `manual-needed` or `blocked`. Successful browser export counts as a
browser capture: attach the exported transcript path to the queue row before
archive-intake.

## Transcript Attachment

When the operator supplies a transcript or browser capture for a Geopolitics
queue row, attach it to the matching row:

```powershell
tools\run.ps1 youtube-capture attach-transcript --date YYYY-MM-DD --url URL --transcript-file PATH --notes "operator-pasted transcript attached"
```

After attachment, run:

```powershell
tools\run.ps1 youtube-capture intake-draft --date YYYY-MM-DD --json
```

`export-intake` remains a legacy alias for `intake-draft`; prefer
`intake-draft` in new work because the workflow is taking sources in, not
exporting them out.

Inspect the draft. A clean draft should include the appropriate `--host-slug`
and `--voice-slug` when known. If warnings report missing host or voice
routing, repair the queue metadata before asking for archive admission.

When several transcript-ready rows are approved for archive admission, hand
them to `archive-intake` one at a time, or use `land-ready` for the already
approved ready set. Do not parallelize landing operations that may write
manifests or shelves. After each landed source, confirm the source identity
appears in the governed index before landing the next row.

If a landing operation is accidentally parallelized or interrupted, verify
source files, manifest rows, voice indexes, and queue status separately before
reporting completion. A source file plus voice-index row is not enough; the
source manifest must contain the matching `source_identity` and declared
`source_count` must equal the actual row count.

For named-guest or named-issue work inside broader date queues, make the
publication boundary explicit before any later staging discussion. A date queue
file may contain unrelated candidates, prior operator selections, skipped
shorts, or channel front-door rows; classify the later commit candidate as
either the whole date queue receipt, a patch-staged subset when practical, or
not ready for staging. Do not describe a mixed date queue commit as if it were
only the named guest.

## Browser Contract

### Authenticated research workspace

At the first YouTube action in a capture task, inspect the visible active
account and eligibility. Reuse an eligible Mira session. Distinguish signed-out,
wrong-account, ineligible, and unknown states; Drive login does not prove
YouTube access. Recheck in a fresh session. Never store credentials or export
browser cookies to command-line tools.

Load [Authenticated workspace](references/authenticated-workspace.md) when
checking readiness, handling access failures, organizing research, or running
the pilot. Cache unchanged blockers for the task, continue public discovery
where possible, and request human sign-in only when needed. Readiness alone
authorizes no account changes or archive admission.

Optional `record-browser-receipt` flags `--access-mode` (authenticated, public,
unknown), `--access-eligibility` (eligible, ineligible, unknown), and
`--access-observed-at` record advisory context without account identifiers.
Observation time requires a timezone and defaults to `--observed-at`.
Existing receipts remain valid. Access context never substitutes for inspected
channel evidence; an access failure is not a no-qualifying-videos observation.

Automated RSS discovery seeds candidates but cannot close a channel check. For
daily Tier A Geopolitics checks and same-day named channel/guest searches, use
the browser by default as described above. For other bounded capture work, use
the browser when human-visible triage or transcript capture is needed,
especially when YouTube blocks automated transcript access.

Use the in-app browser for the parts of YouTube work that need visible-page
judgment:

- distinguish full episodes, livestream replays, shorts, clips, and duplicate
  uploads;
- inspect channel pages for same-day or recently missed uploads;
- inspect the authenticated Subscriptions feed first for a signed-in daily run;
- confirm visible title, channel, date, URL, and transcript availability;
- capture or copy transcript text when automated transcript access is blocked;
- inspect the page description or visible metadata when routing evidence is
  weak.

Browser observations are capture evidence, not archive authority or factual
verification. For browser-based work, keep the output in the routed capture
surface first. Do not paste a browser transcript directly into archive intake
without attaching it to the queue row, updating the target note, or explaining
why capture attachment is impossible.

When browser work completes a Tier A Geopolitics channel check, record the
dedicated JSON receipt with `record-browser-receipt`. Row notes or a
user-facing handoff may summarize the observation, but neither substitutes for
the receipt.

Preserve:

- canonical URL;
- visible title, channel, and date as seen in the browser;
- discovery surface (`Subscriptions`, `Videos`, `Live`, or `channel-search`);
- exact date evidence and exclusion reason for scheduled, future, stale, short,
  clip, duplicate, or unrelated rows;
- whether the item is a full episode, livestream replay, clip, or short;
- transcript availability and capture method;
- why the row is `must-land`, `possible`, `watch`, or `skip`;
- next governed route: routed capture output, transcript attachment,
  `archive-intake`, `archive-query`, `geo-strategy`, `reality-check`, or
  Singularity analysis after admission.

## Completion Receipt

Report:

- routed archive lane and output path;
- number of channel rows and video rows or target-note rows;
- disposition counts where the routed output supports dispositions;
- duplicate or already-landed count;
- transcript-ready count;
- intake draft count;
- authority boundary crossed or not crossed.

If archive admission is the next step, say so explicitly and require separate
operator authority unless the operator already gave a direct bounded landing
command for that exact source.

## Geopolitics directory compatibility

For current filesystem operations, resolve domain paths through the shared
`repository_paths.resolve_geopolitics_reference` helper. It accepts the legacy
`narrative-geopolitics/` spelling and the `geopolitics/` spelling and selects
exactly one existing domain directory. Examples below or above using the legacy
spelling remain compatibility references; they do not authorize a directory
move. Preserve historical IDs and stored/hash-bound references. The source
archive remains at `archive/sources/geopolitics/`.

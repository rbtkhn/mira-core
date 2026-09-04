---
name: youtube-capture
description: "Repository-local Narrative Geopolitics YouTube channel-check and transcript-queue workflow. Use when the operator asks to check today's YouTube channels, discover recent channel videos, triage YouTube queue rows, attach transcripts, or export intake drafts. Do not use for archive landing, synthesis, factual verification, publication, staging, commit, or push."
---

# YouTube Capture

YouTube Capture is the queue front door for Narrative Geopolitics YouTube
source discovery. It gets channel candidates into a reviewable queue and hands
transcript-ready rows to `archive-intake`; it does not land archive sources or
judge the day.

Use this skill for requests such as:

- `check today's YouTube channels`
- `youtube-capture`
- `run the channel check`
- `triage the YouTube queue`
- `attach this transcript`
- `export intake drafts for ready YouTube rows`

## Boundary

This workflow may create or update queue rows under
`narrative-geopolitics/work/capture/youtube/`. It must not admit archive
sources, mutate the source manifest, synthesize a daily packet, verify
operational claims, publish, stage, commit, push, or deploy unless a later
workflow receives separate explicit authority.

Use neighboring workflows this way:

- supplied transcript ready for archive admission -> `archive-intake`;
- inventory, duplicates, or landed membership -> `archive-query`;
- source-body, ASR, metadata, or sectioning repair after landing ->
  `archive-repair`;
- manifest-backed daily judgment -> `geo-strategy`;
- operational factual adjudication -> `reality-check`.

If a YouTube source is already landed, do not re-land it through capture. Mark
or prune the queue row, then use `archive-query` or the landed source path.

## Standard Channel Check

For today's channel check, run from the repository root:

```powershell
tools\run.ps1 youtube-capture scan-index --date YYYY-MM-DD --include-active --include-candidate
tools\run.ps1 youtube-capture discover-public --date YYYY-MM-DD --include-active --include-candidate --limit-per-channel 3 --since-days 7
tools\run.ps1 youtube-capture status --date YYYY-MM-DD
tools\run.ps1 youtube-capture audit-duplicates --date YYYY-MM-DD
tools\run.ps1 youtube-capture browser-coverage --date YYYY-MM-DD
```

Use the current local date unless the operator supplies another date. RSS is a
seed source only. `discover-public` reads the full available feed, applies the
date window, and only then applies `--limit-per-channel`; never truncate the
newest feed entries before date filtering. Raise `--limit-per-channel` or
`--since-days` only when the operator asks for wider candidate coverage.

Queue files are named for the capture run. Each video row stores
`capture_date` separately from `publication_date`; the compatibility `date`
field follows `publication_date` when public metadata supplies one. Do not
mistake the queue filename or capture date for the episode's publication date.

For daily Narrative Geopolitics work, default effort is high. Treat configured
Tier A channels as browser-checked by default for the target date; public
metadata discovery is the first pass, not sufficient completion. Named-channel
or named-guest same-day searches are also browser-first, regardless of tier:
inspect the visible YouTube channel search, Videos, Live, or watch page before
relying on RSS or scraped public metadata. RSS may lag, omit livestream/search
ordering context, or fail in the local environment, so use it only as a
supplemental clue unless the operator explicitly asks for RSS. Apply strict
date filtering when the operator asks for one date: report only items matching
that publication date, and keep adjacent-day candidates out of the user-facing
result unless they explain an ambiguity or a missed-source risk.

For Tier A daily checks, the in-app browser is part of the standard contract,
not a fallback, because visible YouTube channel pages are often the only
adequate source for same-day upload order, livestream replay status, Shorts
separation, and missed rows. Check major channels carefully before declaring a
date complete. Dialogue Works requires especially careful same-day inspection
because multiple guest uploads on the same date can be missed by lighter
metadata passes.

After inspecting a Tier A channel's visible page, record the observation:

```powershell
tools\run.ps1 youtube-capture record-browser-receipt --date YYYY-MM-DD --channel-slug SLUG --channel-url CHANNEL_URL --observed-at ISO_TIMESTAMP --observed-url VIDEO_URL
```

Repeat `--observed-url` for every qualifying visible item. If inspection finds
none, use `--no-qualifying-videos` instead. A receipt states only what was
visibly checked; it does not verify episode claims or authorize archive intake.
For this workflow, configured `daily` cadence channels are the Tier A browser
set unless the operator supplies explicit `--channel` selections. Tier A
completion fails closed until `browser-coverage` finds a valid receipt for
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

For state-substrate coercion, main-list eligible mechanism terms include energy
systems, grids, banking, sanctions, shipping, insurance, logistics, ammunition,
budget pressure, industrial capacity, diplomacy, and alliance compliance.

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
observations and repository-local manifest or queue checks. Use
`narrative-geopolitics/channels/channel-index.md` as the controlling source for
regular channel scope: `daily` cadence channels are the regular Tier A browser
set, `weekly` cadence channels are the regular Tier B browser set, and
`manual` or `candidate` channels require explicit mention or a clearly stated
candidate-channel result.

Use this sequence:

1. Read the channel index and state the active channel scope.
2. Search YouTube in the in-app browser for the named voice, bounded date
   range, and regular channel names or handles.
3. Exclude shorts, chapter links, clips, mirrored snippets, and rows where the
   visible title/channel/date does not support the named voice as a featured
   participant.
4. Check candidate video IDs against the source manifest and existing capture
   queue before calling them new.
5. Output queue rows when the operator asks for `youtube-capture`; otherwise
   return a browser-discovery-only receipt and wait for queue authority.

For a browser-discovery-only receipt, report the searched surface, candidate
URLs, excluded duplicate or already-landed IDs, excluded shorts/clips, whether
any row came from outside the regular channel set, and the authority boundary:
no queue mutation, archive admission, voice promotion, staging, commit, push,
or synthesis occurred.

Discovery does not canonicalize a voice. A single captured or landed item may
support a provisional `expected_voice` value in the queue, but it must not
create a new voice shelf or profile unless the voice promotion gate in
`narrative-geopolitics/voices/README.md` is satisfied or the operator gives an
explicit override for that exact voice.

If Windows console encoding fails on titles, rerun status or duplicate audit
with UTF-8 output forced:

```powershell
$env:PYTHONIOENCODING='utf-8'; tools\run.ps1 youtube-capture status --date YYYY-MM-DD
$env:PYTHONIOENCODING='utf-8'; tools\run.ps1 youtube-capture audit-duplicates --date YYYY-MM-DD --json
```

## Triage

Use queue dispositions consistently:

- `must-land`: direct source for the current issue, featured voice, forecast
  review, crisis object, or high-value mechanism.
- `possible`: plausible context or segment candidate; review before transcript
  retrieval.
- `skip`: shorts, already-landed duplicates, off-topic rows, or items outside
  the current focus.
- `watch`: channel front-door rows or unreviewed channel/video rows.

Update rows with:

```powershell
tools\run.ps1 youtube-capture mark --date YYYY-MM-DD --url URL --disposition must-land --next-action "retrieve transcript or manual transcript capture, then export intake draft" --notes "reason"
```

Do not treat title relevance as source truth. A `must-land` mark means the row
deserves transcript capture, not that its claims are verified or synthesis-ready.

## Transcript Attachment

When the operator supplies a transcript or browser capture, attach it to the
matching queue row:

```powershell
tools\run.ps1 youtube-capture attach-transcript --date YYYY-MM-DD --url URL --transcript-file PATH --notes "operator-pasted transcript attached"
```

After attachment, run:

```powershell
tools\run.ps1 youtube-capture export-intake --date YYYY-MM-DD --json
```

Inspect the draft. A clean draft should include the appropriate `--host-slug`
and `--voice-slug` when known. For manually added or browser-discovered rows,
put the canonical channel route in structured metadata when the tool supports
it, and include `channel_slug=SLUG` in notes when that is the current exporter
contract. If warnings report missing host or voice routing, repair the queue
metadata before asking for archive admission.

When several transcript-ready rows are approved for archive admission, hand
them to `archive-intake` one at a time. Do not parallelize landing operations
that may write the source manifest or voice shelves. After each landed source,
confirm the source identity appears in the manifest before landing the next
row.

After archive admission, produce or verify a bounded receipt:

- source identity is present in `archive/sources/geopolitics/source-manifest.json`;
- source body exists at the manifest `local_path`;
- expected voice shelf was refreshed or checked;
- `audit-duplicates` marks the queue row already landed;
- if a daily packet already exists for that date, `geo-strategy` refresh or
  validation is needed so consumed source count matches landed source count.

For named-guest or named-issue work inside broader date queues, make the
publication boundary explicit before any later staging discussion. A date queue
file may contain unrelated candidates, prior operator selections, skipped
shorts, or channel front-door rows; classify the later commit candidate as
either the whole date queue receipt, a patch-staged subset when practical, or
not ready for staging. Do not describe a mixed date queue commit as if it were
only the named guest.

## Browser Contract

Automated RSS discovery seeds candidates but cannot close a channel check. For
daily Tier A Narrative Geopolitics checks and same-day named channel/guest
searches, use the browser by default as described above. For other bounded
capture work, use the browser when human-visible triage or transcript capture
is needed, especially when YouTube blocks automated transcript access.

Use the in-app browser for the parts of YouTube work that need visible-page
judgment:

- distinguish full episodes, livestream replays, shorts, clips, and duplicate
  uploads;
- inspect channel pages for same-day or recently missed uploads;
- confirm visible title, channel, date, URL, and transcript availability;
- capture or copy transcript text when automated transcript access is blocked;
- inspect the page description or visible metadata when routing evidence is
  weak.

Browser observations are capture evidence, not archive authority or factual
verification. For browser-based work, keep the output in the queue first. Do
not paste a browser transcript directly into archive intake without attaching
it to the queue row or explaining why queue attachment is impossible.

When browser work completes a Tier A channel check, record the dedicated JSON
receipt with `record-browser-receipt`. Row notes or a user-facing handoff may
summarize the observation, but neither substitutes for the receipt. Preserve:

- canonical URL;
- visible title, channel, and date as seen in the browser;
- whether the item is a full episode, livestream replay, clip, or short;
- transcript availability and capture method;
- why the row is `must-land`, `possible`, `watch`, or `skip`;
- next governed route: queue only, transcript attachment, `archive-intake`,
  `archive-query`, `geo-strategy`, or `reality-check`.

## Completion Receipt

Report:

- queue file path;
- number of channel rows and video rows;
- disposition counts;
- duplicate or already-landed count;
- transcript-ready count;
- intake draft count;
- authority boundary crossed or not crossed.

If archive admission is the next step, say so explicitly and require separate
operator authority unless the operator already gave a direct bounded landing
command for that exact source.

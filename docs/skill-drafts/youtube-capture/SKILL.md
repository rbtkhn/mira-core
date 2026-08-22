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
python scripts\youtube_capture.py scan-index --date YYYY-MM-DD --include-active --include-candidate
python scripts\youtube_capture.py discover-public --date YYYY-MM-DD --include-active --include-candidate --limit-per-channel 3 --since-days 7
python scripts\youtube_capture.py status --date YYYY-MM-DD
python scripts\youtube_capture.py audit-duplicates --date YYYY-MM-DD
```

Use the current local date unless the operator supplies another date. Keep
discovery bounded; raise `--limit-per-channel` or `--since-days` only when the
operator asks for wider coverage.

If Windows console encoding fails on titles, rerun status or duplicate audit
with UTF-8 output forced:

```powershell
$env:PYTHONIOENCODING='utf-8'; python scripts\youtube_capture.py status --date YYYY-MM-DD
$env:PYTHONIOENCODING='utf-8'; python scripts\youtube_capture.py audit-duplicates --date YYYY-MM-DD --json
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
python scripts\youtube_capture.py mark --date YYYY-MM-DD --url URL --disposition must-land --next-action "retrieve transcript or manual transcript capture, then export intake draft" --notes "reason"
```

Do not treat title relevance as source truth. A `must-land` mark means the row
deserves transcript capture, not that its claims are verified or synthesis-ready.

## Transcript Attachment

When the operator supplies a transcript or browser capture, attach it to the
matching queue row:

```powershell
python scripts\youtube_capture.py attach-transcript --date YYYY-MM-DD --url URL --transcript-file PATH --notes "operator-pasted transcript attached"
```

After attachment, run:

```powershell
python scripts\youtube_capture.py export-intake --date YYYY-MM-DD --json
```

Inspect the draft. A clean draft should include the appropriate `--host-slug`
and `--voice-slug` when known. If warnings report missing host or voice routing,
repair the queue metadata before asking for archive admission.

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

## Browser Fallback

Automated discovery uses public metadata and usually does not require the
browser. Use the browser only when human-visible triage or transcript capture is
needed, especially when YouTube blocks automated transcript access.

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

When browser work supplies a candidate, record a compact browser-to-queue
receipt in row notes or the user-facing handoff:

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

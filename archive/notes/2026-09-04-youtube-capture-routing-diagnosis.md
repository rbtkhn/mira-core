# YouTube Capture Routing Diagnosis

Date: 2026-09-04
Status: private-provisional
Class: working-note
Authority effect: This note preserves an architectural diagnosis only. It does not repair the workflow, create transcript bodies, admit archive sources, stage unrelated files, publish, or verify source claims.

## Diagnosis

The current `youtube-capture` front door is misleadingly broad. Its name and AGENTS trigger suggest a general YouTube capture workflow, but its controlling implementation is specific to Narrative Geopolitics:

- `docs/skill-drafts/youtube-capture/SKILL.md` defines the workflow as the queue front door for Narrative Geopolitics YouTube source discovery and says it may write under `narrative-geopolitics/work/capture/youtube/`.
- `scripts/youtube_capture.py` hardcodes the queue root, channel index, and duplicate manifest to the geopolitics namespace: `narrative-geopolitics/work/capture/youtube`, `narrative-geopolitics/channels/channel-index.md`, and `archive/sources/geopolitics/source-manifest.json`.
- `AGENTS.md` invokes the skill for the broad phrase `youtube-capture`, which lets a domain-general command route into a domain-specific queue before the source shelf is resolved.

That structure caused Nate Herk and Nate B. Jones URLs to be treated as geopolitics queue candidates even though the repo already represents them under Singularity shelves:

- `archive/sources/singularity/nate-herk/`
- `archive/sources/singularity/nate-b-jones/`

The URL discovery itself was not the problem. The failure was that duplicate checks answered the wrong question: absence from the geopolitics queue and geopolitics source manifest is not evidence that a Nate Herk or Nate B. Jones item belongs in geopolitics capture.

The warning sign was visible in the mistaken queue notes: the rows were marked as "not part of regular geopolitical channel roster." That observation should have stopped queue mutation and forced shelf/domain resolution before any write.

## Repair Direction

The smallest safe repair is to make the current workflow explicitly geopolitics-scoped. Rename or reframe the current skill and script surface as `geopolitics-youtube-capture`, or at minimum make the `youtube-capture` skill fail closed unless the target source belongs to the Narrative Geopolitics channel index.

If Mira needs cross-domain YouTube capture, create a thin general router whose first step is domain resolution. That router should dispatch to domain-owned capture/admission surfaces such as Singularity, Geopolitics, or another archive lane only after identifying the correct source shelf.

## Regression Case

Prompt: `youtube-capture find the latest nate-herk and nate-jones video urls that we havent captured yet`

Expected behavior: resolve Nate Herk and Nate B. Jones to Singularity before any queue mutation; inspect `archive/sources/singularity/nate-herk/` and `archive/sources/singularity/nate-b-jones/` for existing captures; produce a Singularity-scoped target note or transcript workflow if authorized.

Forbidden behavior: write rows under `narrative-geopolitics/work/capture/youtube/` or check only `archive/sources/geopolitics/source-manifest.json` before calling the items uncaptured.

## Incident Boundary

The mistaken geopolitics queue rows were removed during the same session. No archive source admission, source-manifest mutation, synthesis, staging, commit, push, or publication is established by that correction unless separately proven by Git and workflow receipts.

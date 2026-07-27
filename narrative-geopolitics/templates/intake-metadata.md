# Intake Metadata Sidecar

Use this template to pre-structure an operator-pasted source before running
`best-intake`.

For `host_slug: mario-nawfal`, `trim_opening: auto` now trims both:

- known opening smalltalk/preamble before the substantive interview starts
- known closing scheduling/signoff chatter after the substantive interview ends

Goal:

- minimize re-reading
- minimize routing hesitation
- give `land_best_intake.py` the smallest workable metadata set

The helper now writes trim metrics into landed source frontmatter automatically:

- `opening_trim_chars_saved`
- `opening_trim_words_saved`
- `opening_trim_rule`
- `closing_trim_chars_saved`
- `closing_trim_words_saved`
- `closing_trim_rule`

## How To Use

1. Paste the source body into a local text file.
2. Copy this template into a sidecar note next to it.
3. Fill only the fields you know.
4. Leave uncertain optional fields blank.
5. Run the repository intake wrapper from the metadata plus body file: `tools/run.ps1 intake --metadata-file <path> --body-file <path>`.

For a read-only preflight before landing:

```powershell
tools/run.ps1 intake --metadata-file C:\path\to\source.txt --preflight --json
```

The receipt reports the selected transcript title, preserved title aliases,
date and routing basis, canonical YouTube identity, duplicate status, planned
archive path, transformations, and warnings. Warnings are retained in landed
frontmatter and do not block an otherwise safe landing.

For batch work, save one filled sidecar per source in a folder and run:

```powershell
.\tools\run.ps1 intake-land --batch-dir C:\path\to\intake-batch
```

## Paste-First Minimum

Same-day one-off intake needs:

- `pub_date` or `ingest_date`;
- `url` when recoverable;
- source body through `--body-file` or `--body-text`.

If no public URL is recoverable, leave `url` blank. The landed source records
`source_url_status: unavailable`; it does not promote the generated
`operator-paste://` provenance URI into a source URL.

Title, voice, host, and source form are inferred when the body is clear. A
single clarification is allowed when host or primary voice ownership is truly
ambiguous.

## Batch Sidecar Fields

For repeatable batch work, provide:

```text
pub_date:
ingest_date:
url:
body_file:
```

Landed records also carry `source_identity`, `title_source`, `title_aliases`,
`title_confidence`, `date_basis`, `routing_basis`, `source_form_basis`, and
`metadata_warnings` for auditability.

Supply these overrides only when known or inference is ambiguous:

```text
title:
voice_slug:
```

## Optional Fields

```text
host_slug:
host:
guest:
show_title:
channel_name:
show:
thread:
kind:
source_form:
source_class:
modality:
review_state:
routing_state:
trim_opening:
source_note:
editorial_note:
host_people:
guest_people:
```

## Blank Template

```text
pub_date: YYYY-MM-DD
ingest_date: YYYY-MM-DD
title:
url:
body_file:
voice_slug:

host_slug:
host:
guest:
show_title:
channel_name:
show:
thread:

kind: cleaned-transcript
source_form: interview
source_class: guest interview pressure test
modality: cleaned-transcript
review_state: unreviewed
routing_state: provisional
trim_opening: auto

source_note:
editorial_note:

host_people:
guest_people:
```

## Fast-Fill Example

```text
pub_date: 2026-07-07
ingest_date: 2026-07-08
title: Robert Barnes: U.S. Just REVOKED Iran Waivers - We Heading to War
url: https://www.youtube.com/watch?v=H0UPyniTc_Q
body_file: C:\temp\2026-07-07-barnes.txt
voice_slug: barnes

host_slug: dialogue-works
host: Nima Alkhorshid
guest: Robert Barnes
show_title: Dialogue Works
channel_name: Dialogue Works
show: Dialogue Works
thread: barnes

kind: cleaned-transcript
source_form: interview
source_class: guest interview pressure test
modality: cleaned-transcript
review_state: unreviewed
routing_state: provisional
trim_opening: auto

source_note: Operator-pasted YouTube transcript from local attachment. Best-intake landing with preserved transcript body.
editorial_note: Preserve as raw cleaned transcript. Not human-verified verbatim.

host_people: Nima Alkhorshid
guest_people: Robert Barnes
```

## Conversion Hint

Turn the sidecar into a helper command by mapping fields directly:

```powershell
.\tools\run.ps1 intake-land `
  --pub-date 2026-07-07 `
  --ingest-date 2026-07-08 `
  --title "Robert Barnes: U.S. Just REVOKED Iran Waivers - We Heading to War" `
  --url "https://www.youtube.com/watch?v=H0UPyniTc_Q" `
  --body-file "C:\temp\2026-07-07-barnes.txt" `
  --voice-slug barnes `
  --host-slug dialogue-works `
  --host "Nima Alkhorshid" `
  --guest "Robert Barnes" `
  --show-title "Dialogue Works" `
  --channel-name "Dialogue Works" `
  --show "Dialogue Works" `
  --thread barnes `
  --host-people "Nima Alkhorshid" `
  --guest-people "Robert Barnes"
```

Or land directly from the sidecar:

```powershell
.\tools\run.ps1 intake-land `
  --metadata-file "C:\temp\2026-07-07-barnes-metadata.txt"
```

## Trim Rule

For `mario-nawfal` interviews, `trim_opening: auto` will try to remove
front-loaded camera check / rapport chatter before the substantive setup begins.

Current behavior:

- only applies automatically when `host_slug: mario-nawfal`
- only trims when a known substantive handoff marker is found at the opening
- also trims known Mario scheduling / next-guest chatter after the guest sign-off
- otherwise leaves the body untouched

Use:

- `trim_opening: auto` for normal behavior
- `trim_opening: none` to preserve the full raw preamble
- `trim_opening: mario-nawfal` to force the Mario-specific trim rule

## Rule

If a field is uncertain and non-required, leave it blank and continue.

Do not delay landing just to make the sidecar look complete.

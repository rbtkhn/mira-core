# Voice Routing Audit

Status: `working`

This note records archive-level checks for whether imported sources should carry more than one `voice_slug`.

## Rule

Use `voice_slugs` for whole-source-person continuity.

Use `host_slug` for host, channel, show, or publication routing when host context matters.

Do not add entity, institution, publication, or channel slugs to `voice_slugs` until the system explicitly supports non-person continuity records.

## Pape Import Audit

Audit date: `2026-07-07`

Source basis: [source-manifest.json](source-manifest.json)

The Pape import contains 17 guest/interview pressure-test sources. All should remain `voice_slugs: ["pape"]` because Pape is the load-bearing analyst voice.

Host-conditioned routing belongs in `host_slug` and [../channels/](../channels/README.md).

| Channel slug | Evidence | Decision |
| --- | --- | --- |
| `mario-nawfal` | Appears as host/channel across 7 Pape interview captures. | Route through [../channels/mario-nawfal/](../channels/mario-nawfal/README.md), not through `voice_slugs`. |

These host/channel shelves exist as lightweight Pape-reference shelves:

| Channel slug | Evidence | Status |
| --- | --- | --- |
| `breaking-points` | Appears in 4 Pape captures. | Lightweight shelf. |
| `redacted-news` | Appears in 2 Pape captures. | Lightweight shelf. |
| `daniel-davis` | Appears in 1 Pape capture. | Lightweight shelf. |
| `cyrus-janssen` | Appears in 1 Pape capture. | Lightweight shelf. |
| `tom-switzer` | Appears in 1 Pape capture. | Lightweight shelf. |
| `moral-resistance` | Appears in 1 Pape capture. | Lightweight shelf. |

## Follow-Up

If a host later becomes a full voice record, that should be a separate decision from channel routing.

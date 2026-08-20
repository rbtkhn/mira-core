# Channel Index

Status: `manual-v1`

This is the routing front door for channel-conditioned analysis in Narrative Geopolitics.

Use it to decide whether a channel can be opened locally, whether a lightweight shelf must be created first, or whether the row is only inherited Statecraft source-basis context.

## Rules

Use `host_slug` in [../archive/source-manifest.json](../archive/source-manifest.json) as the v1 routing key for channel shelves.

Use `voice_slugs` only for whole-source-person continuity.

If a channel has a local shelf, open that shelf before synthesis. If a channel has no local shelf, create a lightweight shelf before using that channel in Narrative Geopolitics synthesis.

Statecraft source counts and YouTube URLs are provenance. They are not local Narrative Geopolitics authority until a shelf exists here.

## Lifecycle Terms

| Status | Meaning |
| --- | --- |
| `active` | Local Narrative Geopolitics shelf exists and is ready for routing. |
| `candidate` | Source-basis channel is likely relevant but not locally shaped yet. |
| `watchlist` | Upstream Statecraft watchlist channel not locally active yet. |
| `source-basis` | Inherited upstream roster context only. |
| `archived` | Retained for reference, not active routing. |

## Pape Pilot Roster

| Channel slug | Shelf | Pape sources | Narrative status | Channel role |
| --- | --- | ---: | --- | --- |
| `mario-nawfal` | [mario-nawfal/](mario-nawfal/README.md) | 7 | `active` | Breaking-headline register for escalation-trap, MOU, and Hormuz-oil pressure tests. |
| `breaking-points` | [breaking-points/](breaking-points/README.md) | 4 | `active` | Segment interview frame; compresses Pape into public argument and reaction format. |
| `redacted-news` | [redacted-news/](redacted-news/README.md) | 2 | `active` | Crisis-media register; emphasizes urgency and collapse/war expansion pressure. |
| `daniel-davis` | [daniel-davis/](daniel-davis/README.md) | 1 | `active` | Feasibility and settlement-room pressure. |
| `cyrus-janssen` | [cyrus-janssen/](cyrus-janssen/README.md) | 1 | `active` | China-facing geopolitical explainer frame. |
| `tom-switzer` | [tom-switzer/](tom-switzer/README.md) | 1 | `active` | Strategic interview frame around peace illusions and escalation risk. |
| `moral-resistance` | [moral-resistance/](moral-resistance/README.md) | 1 | `active` | MOU / legislative-action / resistance framing pressure. |

## Statecraft Source Channel Roster

Source basis: `strategy-codex/statecraft/channels/channel-index.md`.

| Channel slug | Label | Narrative status | Routing role | Local shelf / required next step | Upstream files | Upstream days | Capture cadence | Channel URL | First day | Last day |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| `alexander-mercouris` | Alexander Mercouris | `watchlist` | Solo analyst channel; potential whole-voice/channel overlap. | Create lightweight shelf before synthesis. | 333 | 331 | `daily` | [open](https://www.youtube.com/@AlexMercouris) | `2025-01-03` | `2026-06-27` |
| `dialogue-works` | Dialogue Works | `active` | Multi-guest interview channel; high-value host-conditioning source for Marandi and Davis routing. | [dialogue-works/](dialogue-works/README.md) | 330 | 208 | `daily` | [open](https://www.youtube.com/@dialogueworks01) | `2025-01-05` | `2026-07-14` |
| `daniel-davis` | Daniel Davis / Deep Dive | `active` | Feasibility and settlement-room pressure. | [daniel-davis/](daniel-davis/README.md) | 205 | 135 | `daily` | [open](https://www.youtube.com/@DanielDavisDeepDive) | `2025-01-10` | `2026-07-14` |
| `glenn-diesen` | Glenn Diesen | `active` | Order-transition and Eurasian-institutional host frame for Mearsheimer, Marandi, Mercouris, and Davis routing. | [glenn-diesen/](glenn-diesen/README.md) | 241 | 192 | `daily` | [open](https://www.youtube.com/@GDiesen1) | `2023-01-14` | `2026-07-14` |
| `judging-freedom` | Judge Napolitano - Judging Freedom | `active` | Legal, constitutional, and defeat-accounting pressure host frame. | [judging-freedom/](judging-freedom/README.md) | 189 | 132 | `daily` | [open](https://www.youtube.com/@judgingfreedom) | `2025-01-07` | `2026-06-30` |
| `mario-nawfal` | Mario Nawfal | `active` | Multi-guest breaking-headline frame for operational, deal, escalation, and domestic-constraint claims. | [mario-nawfal/](mario-nawfal/README.md) | 60 | 38 | `daily` | [open](https://www.youtube.com/channel/UCTWBp-39z6tvz4-LQB-Z_QA) | `2026-05-12` | `2026-07-14` |
| `the-duran` | The Duran | `active` | Joint analyst/channel frame for Mercouris sequence and panel reinforcement. | [the-duran/](the-duran/README.md) | 36 | 36 | `daily` | [open](https://www.youtube.com/@TheDuran) | `2025-02-07` | `2026-07-12` |
| `india-global-left` | India and Global Left | `active` | Global South and left-host pressure on Western realist, diplomatic, and antiwar arguments. | [india-global-left/](india-global-left/README.md) | 21 | 21 | `weekly` | [open](https://www.youtube.com/@IndiaGlobalLeft) | `2025-02-22` | `2026-06-11` |
| `neutrality-studies` | Neutrality Studies | `active` | Neutralist host frame for sovereignty, anti-escalation, and non-alignment claims. | [neutrality-studies/](neutrality-studies/README.md) | 12 | 10 | `weekly` | [open](https://www.youtube.com/@neutralitystudies) | `2025-02-06` | `2026-07-08` |
| `breaking-points` | Breaking Points | `active` | Segment interview frame; compresses specialist claims into public argument and reaction format. | [breaking-points/](breaking-points/README.md) | 9 | 7 | `weekly` | [open](https://www.youtube.com/@BreakingPoints) | `2026-04-29` | `2026-06-23` |
| `cyrus-janssen` | Cyrus Janssen | `active` | China-facing geopolitical explainer frame. | [cyrus-janssen/](cyrus-janssen/README.md) | 8 | 8 | `weekly` | [open](https://www.youtube.com/@CyrusJanssen) | `2025-08-20` | `2026-07-12` |
| `tucker-carlson` | Tucker Carlson | `candidate` | Long-form elite interview frame; source-basis only until locally shaped. | Create lightweight shelf before synthesis. | 7 | 7 | `manual` | [open](https://www.youtube.com/@TuckerCarlson) | `2025-03-11` | `2026-06-24` |
| `reason-resist` | Reason to Resist | `active` | Resistance-law and antiwar host frame for Helmer and Henningsen guest routing. | [reason-resist/](reason-resist/README.md) | 4 | 4 | `weekly` | [open](https://www.youtube.com/@reason2resist) | `2026-05-24` | `2026-06-25` |
| `moral-resistance` | Moral Resistance | `active` | MOU / legislative-action / resistance framing pressure. | [moral-resistance/](moral-resistance/README.md) | 7 | 7 | `weekly` | [open](https://www.youtube.com/@MoralResistance) | `2026-05-31` | `2026-07-13` |
| `redacted-news` | Redacted News | `active` | Crisis-media register; emphasizes urgency and collapse/war expansion pressure. | [redacted-news/](redacted-news/README.md) | 5 | 4 | `weekly` | [open](https://www.youtube.com/@RedactedNews) | `2026-04-20` | `2026-06-16` |

## Reading Rule

Pape remains the analyst voice. Open [../voices/pape/README.md](../voices/pape/README.md) for whole-voice continuity.

Open a channel shelf when the question is how the host or show changed a guest's claim shape.

Do not use a `candidate`, `watchlist`, or `source-basis` row directly in synthesis. Create a lightweight local shelf first.

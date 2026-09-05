# Sources

Date: `2026-03-30`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-03-30/`

## Intake Batch

This run is grounded in the `2026-03-30` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-03-30/source-alexander-mercouris-israel-ad-fails-80-iran-missiles-hit-target-china-us-bombing-must-stop-u-2026-03-30.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-03-30/source-dialogue-works-col-jacques-baud-what-a-us-ground-invasion-of-iran-would-really-look-like-2026-03-30.md` | transcript | `imported` | `yes` | Baud | Dialogue Works | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-03-30/source-dialogue-works-larry-c-johnson-full-escalation-yemen-joins-hezbollah-crushes-tanks-us-iran-on-brink-2026-03-30.md` | operator-transcript | `imported` | `yes` | Johnson | Dialogue Works | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-03-30/source-larry-johnson-trump-s-suicide-mission-of-boots-on-the-ground-2026-03-30.md` | transcript | `imported` | `yes` | Johnson | Judging Freedom | historical upstream transcript backfill; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2026-03-30 Mercouris](../../../archive/sources/2026-03-30/source-alexander-mercouris-israel-ad-fails-80-iran-missiles-hit-target-china-us-bombing-must-stop-u-2026-03-30.md) | Israel AD Fails 80% Iran Missiles Hit Target; China: US Bombing Must Stop; UK Says Iran Moscow Proxy |
| `SRC-02` | Baud | Dialogue Works | transcript | [2026-03-30 Baud](../../../archive/sources/2026-03-30/source-dialogue-works-col-jacques-baud-what-a-us-ground-invasion-of-iran-would-really-look-like-2026-03-30.md) | Col. Jacques Baud: What a US Ground Invasion of Iran Would REALLY Look Like |
| `SRC-03` | Johnson | Dialogue Works | operator-transcript | [2026-03-30 Johnson](../../../archive/sources/2026-03-30/source-dialogue-works-larry-c-johnson-full-escalation-yemen-joins-hezbollah-crushes-tanks-us-iran-on-brink-2026-03-30.md) | Larry C. Johnson: FULL ESCALATION: Yemen Joins, Hezbollah Crushes Tanks, US–Iran on Brink |
| `SRC-04` | Johnson | Judging Freedom | transcript | [2026-03-30 Johnson](../../../archive/sources/2026-03-30/source-larry-johnson-trump-s-suicide-mission-of-boots-on-the-ground-2026-03-30.md) | Larry Johnson: Trump's Suicide Mission of Boots on the Ground |

## Load-Bearing Quotes

Use short direct quotes only when wording matters. Keep quotes brief and tie each quote to an analytic job.

| Source ID | Quote | Why It Matters |
| --- | --- | --- |
| `SRC-01` |  |  |
| `SRC-02` |  |  |
| `SRC-03` |  |  |
| `SRC-04` |  |  |

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
| `CLM-01` | `SRC-01` |  | Mercouris via Alexander Mercouris | `candidate` |
| `CLM-02` | `SRC-02` |  | Baud via Dialogue Works | `candidate` |
| `CLM-03` | `SRC-03` |  | Johnson via Dialogue Works | `candidate` |
| `CLM-04` | `SRC-04` |  | Johnson via Judging Freedom | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

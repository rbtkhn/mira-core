# Sources

Date: `2026-03-31`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-03-31/`

## Intake Batch

This run is grounded in the `2026-03-31` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-03-31/source-alexander-mercouris-trump-iran-talks-lavrov-chechens-2026-03-31.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-03-31/source-daniel-davis-baud-iran-war-latest-2026-03-31.md` | transcript | `imported` | `yes` | Baud | Daniel Davis | post; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-03-31/source-daniel-davis-scott-ritter-no-war-plan-in-iran-we-re-making-it-up-as-we-go-along-2026-03-31.md` | transcript | `imported` | `yes` | Ritter | Daniel Davis | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-03-31/source-dialogue-works-col-larry-wilkerson-israel-might-not-survive-this-end-everything-israel-iran-nuclear-scenario-2026-03-31.md` | transcript | `imported` | `yes` | Wilkerson | Dialogue Works | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-03-31/source-dialogue-works-seyed-m-marandi-yemen-strikes-israel-they-hit-iran-s-water-power-now-ret-2026-03-31.md` | transcript | `imported` | `yes` | Marandi | Dialogue Works | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-03-31/source-john-mearsheimer-will-trump-go-kamikaze-2026-03-31.md` | transcript | `imported` | `yes` | Mearsheimer | Judging Freedom | historical upstream transcript backfill; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-03-31/source-judging-freedom-ritter-why-iran-is-winning-2026-03-31.md` | transcript | `imported` | `yes` | Ritter | Judging Freedom | host-pressure test; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2026-03-31 Mercouris](../../../archive/sources/2026-03-31/source-alexander-mercouris-trump-iran-talks-lavrov-chechens-2026-03-31.md) | Trump Begs Iran Talks; Gives Up On Hormuz; Lavrov Crisis Becoming World War; Chechens Fight For Iran |
| `SRC-02` | Baud | Daniel Davis | transcript | [2026-03-31 Baud](../../../archive/sources/2026-03-31/source-daniel-davis-baud-iran-war-latest-2026-03-31.md) | IRAN WAR LATEST /Col Jacques Baud & Lt Col Daniel Davis |
| `SRC-03` | Ritter | Daniel Davis | transcript | [2026-03-31 Ritter](../../../archive/sources/2026-03-31/source-daniel-davis-scott-ritter-no-war-plan-in-iran-we-re-making-it-up-as-we-go-along-2026-03-31.md) | Scott Ritter: NO WAR PLAN in IRAN  We're Making It Up as we Go Along |
| `SRC-04` | Wilkerson | Dialogue Works | transcript | [2026-03-31 Wilkerson](../../../archive/sources/2026-03-31/source-dialogue-works-col-larry-wilkerson-israel-might-not-survive-this-end-everything-israel-iran-nuclear-scenario-2026-03-31.md) | Col. Larry Wilkerson: Israel Might Not Survive This… END EVERYTHING… Israel & Iran Nuclear Scenario |
| `SRC-05` | Marandi | Dialogue Works | transcript | [2026-03-31 Marandi](../../../archive/sources/2026-03-31/source-dialogue-works-seyed-m-marandi-yemen-strikes-israel-they-hit-iran-s-water-power-now-ret-2026-03-31.md) | Seyed M. Marandi: Yemen STRIKES Israel - They Hit Iran\u2019s WATER & POWER\u2026 Now RETALIATION Has Started |
| `SRC-06` | Mearsheimer | Judging Freedom | transcript | [2026-03-31 Mearsheimer](../../../archive/sources/2026-03-31/source-john-mearsheimer-will-trump-go-kamikaze-2026-03-31.md) | John Mearsheimer: Will Trump Go Kamikaze? |
| `SRC-07` | Ritter | Judging Freedom | transcript | [2026-03-31 Ritter](../../../archive/sources/2026-03-31/source-judging-freedom-ritter-why-iran-is-winning-2026-03-31.md) | Scott Ritter: Why Iran Is Winning |

## Load-Bearing Quotes

Use short direct quotes only when wording matters. Keep quotes brief and tie each quote to an analytic job.

| Source ID | Quote | Why It Matters |
| --- | --- | --- |
| `SRC-01` |  |  |
| `SRC-02` |  |  |
| `SRC-03` |  |  |
| `SRC-04` |  |  |
| `SRC-05` |  |  |
| `SRC-06` |  |  |
| `SRC-07` |  |  |

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
| `CLM-01` | `SRC-01` |  | Mercouris via Alexander Mercouris | `candidate` |
| `CLM-02` | `SRC-02` |  | Baud via Daniel Davis | `candidate` |
| `CLM-03` | `SRC-03` |  | Ritter via Daniel Davis | `candidate` |
| `CLM-04` | `SRC-04` |  | Wilkerson via Dialogue Works | `candidate` |
| `CLM-05` | `SRC-05` |  | Marandi via Dialogue Works | `candidate` |
| `CLM-06` | `SRC-06` |  | Mearsheimer via Judging Freedom | `candidate` |
| `CLM-07` | `SRC-07` |  | Ritter via Judging Freedom | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

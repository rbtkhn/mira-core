# Sources

Date: `2026-05-22`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-05-22/`

## Intake Batch

This run is grounded in the `2026-05-22` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-05-22/source-alexander-mercouris-eu-says-never-buy-russian-oil-gas-backs-kiev-drone-war-energy-shock-russia-breaks-orekhov-defence-2026-05-22.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-05-22/source-alexander-mercouris-iran-impasse-trump-wants-airstrikes-as-stockpiles-depleted-2026-05-22.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-05-22/source-daniel-davis-nuclear-fear-of-russia-can-bring-stability-alastair-crooke-lt-col-daniel-davis-2026-05-22.md` | transcript | `imported` | `yes` | Crooke | Daniel Davis | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-05-22/source-dialogue-works-larry-johnson-col-wilkerson-irans-unseen-move-us-laser-destroyers-cant-stop-whats-coming-2026-05-22.md` | transcript | `imported` | `yes` | Wilkerson | Dialogue Works | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-05-22/source-glenn-diesen-larry-johnson-defeat-in-the-iran-war-will-end-the-u-s-empire-2026-05-22.md` | operator-transcript | `imported` | `yes` | Johnson | Glenn Diesen | cross-host pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-05-22/source-stanislav-krapivnik-tulsi-gabbard-resigns-hezbollah-crushes-idf-war-becomes-unaffordable-2026-05-22.md` | transcript | `imported` | `yes` | Krapivnik | Dialogue Works | historical upstream transcript backfill; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2026-05-22 Mercouris](../../../archive/sources/2026-05-22/source-alexander-mercouris-eu-says-never-buy-russian-oil-gas-backs-kiev-drone-war-energy-shock-russia-breaks-orekhov-defence-2026-05-22.md) | EU Says NEVER Buy Russian Oil Gas Backs Kiev Drone War; Energy Shock; Russia Breaks Orekhov Defence |
| `SRC-02` | Mercouris | Alexander Mercouris | transcript | [2026-05-22 Mercouris](../../../archive/sources/2026-05-22/source-alexander-mercouris-iran-impasse-trump-wants-airstrikes-as-stockpiles-depleted-2026-05-22.md) | Iran Impasse: Trump Wants Airstrikes as Stockpiles Depleted |
| `SRC-03` | Crooke | Daniel Davis | transcript | [2026-05-22 Crooke](../../../archive/sources/2026-05-22/source-daniel-davis-nuclear-fear-of-russia-can-bring-stability-alastair-crooke-lt-col-daniel-davis-2026-05-22.md) | Nuclear Fear of Russia Can Bring Stability /Alastair Crooke & Lt Col Daniel Davis |
| `SRC-04` | Wilkerson | Dialogue Works | transcript | [2026-05-22 Wilkerson](../../../archive/sources/2026-05-22/source-dialogue-works-larry-johnson-col-wilkerson-irans-unseen-move-us-laser-destroyers-cant-stop-whats-coming-2026-05-22.md) | Larry Johnson & Col. Wilkerson: Iran's Unseen Move: US Laser Destroyers Can't Stop What's Coming |
| `SRC-05` | Johnson | Glenn Diesen | operator-transcript | [2026-05-22 Johnson](../../../archive/sources/2026-05-22/source-glenn-diesen-larry-johnson-defeat-in-the-iran-war-will-end-the-u-s-empire-2026-05-22.md) | Larry Johnson: Defeat in the Iran War Will End the U.S. Empire |
| `SRC-06` | Krapivnik | Dialogue Works | transcript | [2026-05-22 Krapivnik](../../../archive/sources/2026-05-22/source-stanislav-krapivnik-tulsi-gabbard-resigns-hezbollah-crushes-idf-war-becomes-unaffordable-2026-05-22.md) | Stanislav Krapivnik: Tulsi Gabbard Resigns! - Hezbollah Crushes IDF - War Becomes UNAFFORDABLE |

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

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
| `CLM-01` | `SRC-01` |  | Mercouris via Alexander Mercouris | `candidate` |
| `CLM-02` | `SRC-02` |  | Mercouris via Alexander Mercouris | `candidate` |
| `CLM-03` | `SRC-03` |  | Crooke via Daniel Davis | `candidate` |
| `CLM-04` | `SRC-04` |  | Wilkerson via Dialogue Works | `candidate` |
| `CLM-05` | `SRC-05` |  | Johnson via Glenn Diesen | `candidate` |
| `CLM-06` | `SRC-06` |  | Krapivnik via Dialogue Works | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

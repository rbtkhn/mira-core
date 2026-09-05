# Sources

Date: `2026-06-21`

Status: `retrospective-backfill`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-06-21/`

## Intake Batch

This run is a retrospective judgment run built from already-imported central archive sources for `2026-06-21`.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-06-21/source-alexander-mercouris-kremlin-says-talks-with-us-failed-russia-seeks-victory-kiev-strike-starmer-goes-2026-06-21.md` | cleaned-transcript | `already-imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-06-21/source-switzer-mearsheimer-parsi-us-iran-peace-deal-hold-2026-06-21.md` | cleaned-transcript | `already-imported` | `yes` | Mearsheimer / Parsi | Tom Switzer | host-pressure test; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | cleaned-transcript | [2026-06-21 Mercouris](../../../archive/sources/2026-06-21/source-alexander-mercouris-kremlin-says-talks-with-us-failed-russia-seeks-victory-kiev-strike-starmer-goes-2026-06-21.md) | Kremlin Says Talks With US Failed; Russia Seeks Victory; Russia Prepares Big Kiev Strike; Starmer Goes |
| `SRC-02` | Mearsheimer / Parsi | Tom Switzer | cleaned-transcript | [2026-06-21 Mearsheimer / Parsi](../../../archive/sources/2026-06-21/source-switzer-mearsheimer-parsi-us-iran-peace-deal-hold-2026-06-21.md) | Can the US-Iran peace deal hold? |

## Load-Bearing Quotes

Use short direct quotes only when wording matters. Keep quotes brief and tie each quote to an analytic job.

| Source ID | Quote | Why It Matters |
| --- | --- | --- |
| `SRC-01` |  |  |
| `SRC-02` |  |  |

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
| `CLM-01` | `SRC-01` |  | Mercouris via Alexander Mercouris | `candidate` |
| `CLM-02` | `SRC-02` |  | Mearsheimer / Parsi via Tom Switzer | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

# Sources

Date: `2026-04-15`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-04-15/`

## Intake Batch

This run is grounded in the `2026-04-15` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-04-15/source-alexander-mercouris-russia-warns-us-will-intensify-iran-war-china-warns-navy-protect-china-o-2026-04-15.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-04-15/source-glenn-diesen-larry-johnson-trump-s-naval-blockade-ceasefire-collapse-2026-04-15.md` | transcript | `imported` | `yes` | Johnson | Glenn Diesen | cross-host pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-04-15/source-sachs-trumps-naval-blockade-of-the-strait-of-hormuz-2026-04-15.md` | youtube | `imported` | `yes` | Sachs | Jeffrey Sachs | host-pressure test; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2026-04-15 Mercouris](../../../archive/sources/2026-04-15/source-alexander-mercouris-russia-warns-us-will-intensify-iran-war-china-warns-navy-protect-china-o-2026-04-15.md) | Russia Warns US Will 'Intensify' Iran War; China Warns Navy Protect China Oil Tankers; Putin Xi Trip |
| `SRC-02` | Johnson | Glenn Diesen | transcript | [2026-04-15 Johnson](../../../archive/sources/2026-04-15/source-glenn-diesen-larry-johnson-trump-s-naval-blockade-ceasefire-collapse-2026-04-15.md) | Larry Johnson: Trump's Naval Blockade & Ceasefire Collapse |
| `SRC-03` | Sachs | Jeffrey Sachs | youtube | [2026-04-15 Sachs](../../../archive/sources/2026-04-15/source-sachs-trumps-naval-blockade-of-the-strait-of-hormuz-2026-04-15.md) | Trump's Naval Blockade of the Strait of Hormuz |

## Load-Bearing Quotes

Use short direct quotes only when wording matters. Keep quotes brief and tie each quote to an analytic job.

| Source ID | Quote | Why It Matters |
| --- | --- | --- |
| `SRC-01` |  |  |
| `SRC-02` |  |  |
| `SRC-03` |  |  |

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
| `CLM-01` | `SRC-01` |  | Mercouris via Alexander Mercouris | `candidate` |
| `CLM-02` | `SRC-02` |  | Johnson via Glenn Diesen | `candidate` |
| `CLM-03` | `SRC-03` |  | Sachs via Jeffrey Sachs | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

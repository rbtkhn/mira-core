# Sources

Date: `2026-02-02`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-02-02/`

## Intake Batch

This run is grounded in the `2026-02-02` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-02-02/source-dialogue-works-col-jacques-baud-why-the-eu-is-failing-on-every-front-2026-02-02.md` | transcript | `imported` | `yes` | Baud | Dialogue Works | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-02-02/source-sachs-us-iran-war-inevitable-2026-02-02.md` | youtube | `imported` | `yes` | Sachs | Jeffrey Sachs | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-02-02/source-trump-backs-off-iran-attack-as-talks-begin-russia-seeks-kiev-regime-change-winter-advance-quickens-2026-02-02.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | historical upstream transcript backfill; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Baud | Dialogue Works | transcript | [2026-02-02 Baud](../../../archive/sources/2026-02-02/source-dialogue-works-col-jacques-baud-why-the-eu-is-failing-on-every-front-2026-02-02.md) | Col. Jacques Baud: Why the EU Is Failing on Every Front |
| `SRC-02` | Sachs | Jeffrey Sachs | youtube | [2026-02-02 Sachs](../../../archive/sources/2026-02-02/source-sachs-us-iran-war-inevitable-2026-02-02.md) | Jeffrey Sachs: US-Iran War INEVITABLE... |
| `SRC-03` | Mercouris | Alexander Mercouris | transcript | [2026-02-02 Mercouris](../../../archive/sources/2026-02-02/source-trump-backs-off-iran-attack-as-talks-begin-russia-seeks-kiev-regime-change-winter-advance-quickens-2026-02-02.md) | Trump Backs Off Iran Attack As Talks Begin; Russia Seeks Kiev Regime Change Winter Advance Quickens |

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
| `CLM-01` | `SRC-01` |  | Baud via Dialogue Works | `candidate` |
| `CLM-02` | `SRC-02` |  | Sachs via Jeffrey Sachs | `candidate` |
| `CLM-03` | `SRC-03` |  | Mercouris via Alexander Mercouris | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

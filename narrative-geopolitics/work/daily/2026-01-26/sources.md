# Sources

Date: `2026-01-26`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-01-26/`

## Intake Batch

This run is grounded in the `2026-01-26` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-01-26/source-alexander-mercouris-moscow-says-no-progress-abu-dhabi-talks-zelensky-won-t-give-up-territory-2026-01-26.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-01-26/source-diesen-jiang-great-power-wars-new-world-order-2026-01-26.md` | transcript | `imported` | `yes` | Jiang | Glenn Diesen | cross-host pressure test; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2026-01-26 Mercouris](../../../archive/sources/2026-01-26/source-alexander-mercouris-moscow-says-no-progress-abu-dhabi-talks-zelensky-won-t-give-up-territory-2026-01-26.md) | Moscow Says No Progress Abu Dhabi Talks Zelensky Won't Give Up Territory; Konstantinovka Disaster |
| `SRC-02` | Jiang | Glenn Diesen | transcript | [2026-01-26 Jiang](../../../archive/sources/2026-01-26/source-diesen-jiang-great-power-wars-new-world-order-2026-01-26.md) | Great Power Wars Over a New World Order |

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
| `CLM-02` | `SRC-02` |  | Jiang via Glenn Diesen | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

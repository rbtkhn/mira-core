# Sources

Date: `2025-02-20`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2025-02-20/`

## Intake Batch

This run is grounded in the `2025-02-20` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2025-02-20/source-alexander-mercouris-disastrous-zelensky-presser-angers-trump-zelensky-dictator-us-aid-gravy-train-hints-disengagement-2025-02-20.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2025-02-20/source-daniel-davis-trump-forces-ukraine-strategy-the-world-rejects-it-2025-02-20.md` | operator-transcript | `imported` | `yes` | Davis | Daniel Davis | authored stream-sequence spine; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2025-02-20 Mercouris](../../../archive/sources/2025-02-20/source-alexander-mercouris-disastrous-zelensky-presser-angers-trump-zelensky-dictator-us-aid-gravy-train-hints-disengagement-2025-02-20.md) | Disastrous Zelensky Presser Angers Trump: Zelensky Dictator, US Aid Gravy Train, Hints Disengagement |
| `SRC-02` | Davis | Daniel Davis | operator-transcript | [2025-02-20 Davis](../../../archive/sources/2025-02-20/source-daniel-davis-trump-forces-ukraine-strategy-the-world-rejects-it-2025-02-20.md) | Trump FORCES Ukraine Strategy The World Rejects it |

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
| `CLM-02` | `SRC-02` |  | Davis via Daniel Davis | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

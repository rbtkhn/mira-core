# Sources

Date: `2025-01-20`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2025-01-20/`

## Intake Batch

This run is grounded in the `2025-01-20` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2025-01-20/source-alexander-mercouris-trump-president-biden-blinken-exit-russia-china-summits-zelensky-fumes-s-2025-01-20.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2025-01-20/source-daniel-davis-ukraine-eastern-front-in-danger-of-collapse-as-trump-takes-reigns-2025-01-20.md` | operator-transcript | `imported` | `yes` | Davis | Daniel Davis | authored stream-sequence spine; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2025-01-20 Mercouris](../../../archive/sources/2025-01-20/source-alexander-mercouris-trump-president-biden-blinken-exit-russia-china-summits-zelensky-fumes-s-2025-01-20.md) | Trump President, Biden Blinken Exit; Russia China Summits; Zelensky Fumes, Starmer Out |
| `SRC-02` | Davis | Daniel Davis | operator-transcript | [2025-01-20 Davis](../../../archive/sources/2025-01-20/source-daniel-davis-ukraine-eastern-front-in-danger-of-collapse-as-trump-takes-reigns-2025-01-20.md) | UKRAINE Eastern Front in Danger of Collapse as Trump Takes Reigns |

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

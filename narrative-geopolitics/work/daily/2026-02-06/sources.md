# Sources

Date: `2026-02-06`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-02-06/`

## Intake Batch

This run is grounded in the `2026-02-06` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-02-06/source-dialogue-works-amb-chas-freeman-negotiations-or-the-brink-of-all-out-war-2026-02-06.md` | transcript | `imported` | `yes` | Freeman | Dialogue Works | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-02-06/source-russia-furious-as-kiev-tries-to-kill-deputy-of-russia-s-chief-negotiator-lavrov-says-nato-plans-war-2026-02-06.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | historical upstream transcript backfill; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Freeman | Dialogue Works | transcript | [2026-02-06 Freeman](../../../archive/sources/2026-02-06/source-dialogue-works-amb-chas-freeman-negotiations-or-the-brink-of-all-out-war-2026-02-06.md) | Amb. Chas Freeman: Negotiations\u2026 or the Brink of All-Out War? |
| `SRC-02` | Mercouris | Alexander Mercouris | transcript | [2026-02-06 Mercouris](../../../archive/sources/2026-02-06/source-russia-furious-as-kiev-tries-to-kill-deputy-of-russia-s-chief-negotiator-lavrov-says-nato-plans-war-2026-02-06.md) | Russia Furious As Kiev Tries To Kill Deputy Of Russia's Chief Negotiator; Lavrov Says NATO Plans War |

## Load-Bearing Quotes

Use short direct quotes only when wording matters. Keep quotes brief and tie each quote to an analytic job.

| Source ID | Quote | Why It Matters |
| --- | --- | --- |
| `SRC-01` |  |  |
| `SRC-02` |  |  |

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
| `CLM-01` | `SRC-01` |  | Freeman via Dialogue Works | `candidate` |
| `CLM-02` | `SRC-02` |  | Mercouris via Alexander Mercouris | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

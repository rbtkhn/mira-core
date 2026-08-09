# Sources

Date: `2025-09-18`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2025-09-18/`

## Intake Batch

This run is grounded in the `2025-09-18` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2025-09-18/source-alexander-mercouris-zelensky-admits-military-crisis-warns-of-critical-decisions-demands-60-bn-moscow-confirms-gains-2025-09-18.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2025-09-18/source-glenn-diesen-jeffrey-sachs-us-and-china-edge-toward-war-over-taiwan-2025-09-18.md` | transcript | `imported` | `yes` | Sachs | Glenn Diesen | host-pressure test; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2025-09-18 Mercouris](../../../archive/sources/2025-09-18/source-alexander-mercouris-zelensky-admits-military-crisis-warns-of-critical-decisions-demands-60-bn-moscow-confirms-gains-2025-09-18.md) | Alexander Mercouris - Zelensky Admits Military Crisis, Warns Of Critical Decisions; Demands $60 Bn; Moscow Confirms Gains |
| `SRC-02` | Sachs | Glenn Diesen | transcript | [2025-09-18 Sachs](../../../archive/sources/2025-09-18/source-glenn-diesen-jeffrey-sachs-us-and-china-edge-toward-war-over-taiwan-2025-09-18.md) | Jeffrey Sachs: US and China Edge Toward War Over Taiwan |

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
| `CLM-02` | `SRC-02` |  | Sachs via Glenn Diesen | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

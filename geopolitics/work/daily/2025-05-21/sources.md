# Sources

Date: `2025-05-21`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2025-05-21/`

## Intake Batch

This run is grounded in the `2025-05-21` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2025-05-21/source-alexander-mercouris-moscow-warns-talks-kiev-s-last-chance-total-defeat-if-talks-fail-rubio-warns-against-more-sanctions-2025-05-21.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2025-05-21/source-glenn-diesen-andrei-martyanov-russia-s-military-strategy-in-ukraine-2025-05-21.md` | transcript | `imported` | `yes` | Martyanov | Glenn Diesen | host-pressure test; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2025-05-21 Mercouris](../../../archive/sources/2025-05-21/source-alexander-mercouris-moscow-warns-talks-kiev-s-last-chance-total-defeat-if-talks-fail-rubio-warns-against-more-sanctions-2025-05-21.md) | Moscow Warns Talks Kiev's Last Chance Total Defeat If Talks Fail; Rubio Warns Against More Sanctions |
| `SRC-02` | Martyanov | Glenn Diesen | transcript | [2025-05-21 Martyanov](../../../archive/sources/2025-05-21/source-glenn-diesen-andrei-martyanov-russia-s-military-strategy-in-ukraine-2025-05-21.md) | Andrei Martyanov: Russia's Military Strategy in Ukraine |

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
| `CLM-02` | `SRC-02` |  | Martyanov via Glenn Diesen | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

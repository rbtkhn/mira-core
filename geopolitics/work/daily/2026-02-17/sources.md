# Sources

Date: `2026-02-17`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-02-17/`

## Intake Batch

This run is grounded in the `2026-02-17` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-02-17/source-alexander-mercouris-russian-top-general-floats-russian-annexation-of-ukraine-geneva-talks-be-2026-02-17.md` | operator-transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-02-17/source-capt-matt-hoh-a-us-war-with-iran-is-unwinnable-2026-02-17.md` | transcript | `imported` | `yes` | Hoh | Judging Freedom | cross-host pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-02-17/source-dialogue-works-helmer-kremlin-new-strategy-before-geneva-madness-middle-east-2026-02-17.md` | operator-transcript | `imported` | `yes` | Helmer | Dialogue Works | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-02-17/source-dialogue-works-mohammad-marandi-iran-just-closed-the-strait-of-hormuz-wiped-out-iran-pl-2026-02-17.md` | transcript | `imported` | `yes` | Marandi | Dialogue Works | regional-red-line spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-02-17/source-glenn-diesen-chas-freeman-u-s-restoring-empire-war-on-eurasia-2026-02-17.md` | transcript | `imported` | `yes` | Freeman | Glenn Diesen | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-02-17/source-john-mearsheimer-how-trump-has-boxed-himself-into-a-corner-on-iran-2026-02-17.md` | transcript | `imported` | `yes` | Mearsheimer | Judging Freedom | historical upstream transcript backfill; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | operator-transcript | [2026-02-17 Mercouris](../../../archive/sources/2026-02-17/source-alexander-mercouris-russian-top-general-floats-russian-annexation-of-ukraine-geneva-talks-be-2026-02-17.md) | Russian Top General Floats Russian Annexation Of Ukraine; Geneva Talks Begin; Konstantinovka Falling |
| `SRC-02` | Hoh | Judging Freedom | transcript | [2026-02-17 Hoh](../../../archive/sources/2026-02-17/source-capt-matt-hoh-a-us-war-with-iran-is-unwinnable-2026-02-17.md) | Capt. Matt Hoh: A US War With Iran Is Unwinnable |
| `SRC-03` | Helmer | Dialogue Works | operator-transcript | [2026-02-17 Helmer](../../../archive/sources/2026-02-17/source-dialogue-works-helmer-kremlin-new-strategy-before-geneva-madness-middle-east-2026-02-17.md) | John Helmer: The Kremlin's New Strategy Before Geneva - Madness in the Middle East |
| `SRC-04` | Marandi | Dialogue Works | transcript | [2026-02-17 Marandi](../../../archive/sources/2026-02-17/source-dialogue-works-mohammad-marandi-iran-just-closed-the-strait-of-hormuz-wiped-out-iran-pl-2026-02-17.md) | Mohammad Marandi: Iran JUST Closed the Strait of Hormuz - Wiped Out: Iran Plans to Sink the US Navy |
| `SRC-05` | Freeman | Glenn Diesen | transcript | [2026-02-17 Freeman](../../../archive/sources/2026-02-17/source-glenn-diesen-chas-freeman-u-s-restoring-empire-war-on-eurasia-2026-02-17.md) | Chas Freeman: U.S. Restoring Empire & War On Eurasia |
| `SRC-06` | Mearsheimer | Judging Freedom | transcript | [2026-02-17 Mearsheimer](../../../archive/sources/2026-02-17/source-john-mearsheimer-how-trump-has-boxed-himself-into-a-corner-on-iran-2026-02-17.md) | John Mearsheimer: How Trump Has Boxed Himself Into a Corner on Iran |

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
| `CLM-02` | `SRC-02` |  | Hoh via Judging Freedom | `candidate` |
| `CLM-03` | `SRC-03` |  | Helmer via Dialogue Works | `candidate` |
| `CLM-04` | `SRC-04` |  | Marandi via Dialogue Works | `candidate` |
| `CLM-05` | `SRC-05` |  | Freeman via Glenn Diesen | `candidate` |
| `CLM-06` | `SRC-06` |  | Mearsheimer via Judging Freedom | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

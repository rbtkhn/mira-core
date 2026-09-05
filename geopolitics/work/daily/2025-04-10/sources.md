# Sources

Date: `2025-04-10`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2025-04-10/`

## Intake Batch

This run is grounded in the `2025-04-10` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2025-04-10/source-alexander-mercouris-trump-pauses-bond-crisis-forces-tariff-u-turn-china-stands-firm-shock-russian-toretsk-advance-2025-04-10.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2025-04-10/source-daniel-davis-russian-forces-march-on-while-western-leaders-seem-paralyzed-2025-04-10.md` | operator-transcript | `imported` | `yes` | Johnson | Daniel Davis | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2025-04-10/source-daniel-davis-russian-realism-european-dreams-ukraine-defeat-2025-04-10.md` | transcript | `imported` | `yes` | Mercouris | Daniel Davis | cross-host pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2025-04-10/source-judging-freedom-wilkerson-will-trump-deport-americans-2025-04-10.md` | transcript | `imported` | `yes` | Wilkerson | Judging Freedom | host-pressure test; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2025-04-10 Mercouris](../../../archive/sources/2025-04-10/source-alexander-mercouris-trump-pauses-bond-crisis-forces-tariff-u-turn-china-stands-firm-shock-russian-toretsk-advance-2025-04-10.md) | Trump Pauses, Bond Crisis forces Tariff U-Turn, China Stands Firm; Shock Russian Toretsk Advance |
| `SRC-02` | Johnson | Daniel Davis | operator-transcript | [2025-04-10 Johnson](../../../archive/sources/2025-04-10/source-daniel-davis-russian-forces-march-on-while-western-leaders-seem-paralyzed-2025-04-10.md) | Russian Forces March On While Western Leaders seem Paralyzed |
| `SRC-03` | Mercouris | Daniel Davis | transcript | [2025-04-10 Mercouris](../../../archive/sources/2025-04-10/source-daniel-davis-russian-realism-european-dreams-ukraine-defeat-2025-04-10.md) | Russian Realism + European Dreams = UKRAINE DEFEAT |
| `SRC-04` | Wilkerson | Judging Freedom | transcript | [2025-04-10 Wilkerson](../../../archive/sources/2025-04-10/source-judging-freedom-wilkerson-will-trump-deport-americans-2025-04-10.md) | COL. Lawrence Wilkerson : Will Trump Deport Americans? |

## Load-Bearing Quotes

Use short direct quotes only when wording matters. Keep quotes brief and tie each quote to an analytic job.

| Source ID | Quote | Why It Matters |
| --- | --- | --- |
| `SRC-01` |  |  |
| `SRC-02` |  |  |
| `SRC-03` |  |  |
| `SRC-04` |  |  |

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
| `CLM-01` | `SRC-01` |  | Mercouris via Alexander Mercouris | `candidate` |
| `CLM-02` | `SRC-02` |  | Johnson via Daniel Davis | `candidate` |
| `CLM-03` | `SRC-03` |  | Mercouris via Daniel Davis | `candidate` |
| `CLM-04` | `SRC-04` |  | Wilkerson via Judging Freedom | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

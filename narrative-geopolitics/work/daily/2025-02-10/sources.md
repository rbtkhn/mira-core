# Sources

Date: `2025-02-10`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2025-02-10/`

## Intake Batch

This run is grounded in the `2025-02-10` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2025-02-10/source-alexander-mercouris-trump-confirms-putin-call-putin-firm-4-regions-russian-ukraine-kursk-disaster-eu-gas-prices-surge-2025-02-10.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2025-02-10/source-daniel-davis-whats-trumps-leverage-ending-the-ukraine-war-w-col-jacques-baud-2025-02-10.md` | transcript | `imported` | `yes` | Baud | Daniel Davis | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2025-02-10/source-duran-mercouris-us-carrot-and-stick-offer-to-russia-2025-02-10.md` | cleaned-transcript | `imported` | `yes` | Mercouris | The Duran | stream-sequence spine; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2025-02-10 Mercouris](../../../archive/sources/2025-02-10/source-alexander-mercouris-trump-confirms-putin-call-putin-firm-4-regions-russian-ukraine-kursk-disaster-eu-gas-prices-surge-2025-02-10.md) | Trump Confirms Putin Call; Putin Firm 4 Regions Russian: Ukraine Kursk Disaster; EU Gas Prices Surge |
| `SRC-02` | Baud | Daniel Davis | transcript | [2025-02-10 Baud](../../../archive/sources/2025-02-10/source-daniel-davis-whats-trumps-leverage-ending-the-ukraine-war-w-col-jacques-baud-2025-02-10.md) | What's Trump's Leverage Ending the Ukraine War? w/Col Jacques Baud |
| `SRC-03` | Mercouris | The Duran | cleaned-transcript | [2025-02-10 Mercouris](../../../archive/sources/2025-02-10/source-duran-mercouris-us-carrot-and-stick-offer-to-russia-2025-02-10.md) | The Duran / Alexander Mercouris - US carrot and stick offer to Russia |

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
| `CLM-02` | `SRC-02` |  | Baud via Daniel Davis | `candidate` |
| `CLM-03` | `SRC-03` |  | Mercouris via The Duran | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

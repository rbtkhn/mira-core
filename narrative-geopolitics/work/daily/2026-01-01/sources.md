# Sources

Date: `2026-01-01`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-01-01/`

## Intake Batch

This run is grounded in the `2026-01-01` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-01-01/source-alex-krainer-new-york-times-reports-cia-attacks-on-russian-tankers-2026-01-01.md` | cleaned-transcript | `imported` | `yes` | Krainer | Glenn Diesen | host-pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-01-01/source-dialogue-works-andrei-martyanov-it-s-all-over-iran-russia-just-went-all-in-2026-01-01.md` | transcript | `imported` | `yes` | Martyanov | Dialogue Works | host-pressure test; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Krainer | Glenn Diesen | cleaned-transcript | [2026-01-01 Krainer](../../../archive/sources/2026-01-01/source-alex-krainer-new-york-times-reports-cia-attacks-on-russian-tankers-2026-01-01.md) | Alex Krainer: New York Times Reports CIA Attacks on Russian Tankers |
| `SRC-02` | Martyanov | Dialogue Works | transcript | [2026-01-01 Martyanov](../../../archive/sources/2026-01-01/source-dialogue-works-andrei-martyanov-it-s-all-over-iran-russia-just-went-all-in-2026-01-01.md) | Andrei Martyanov: IT''S ALL OVER... Iran & Russia Just Went ALL IN |

## Load-Bearing Quotes

Use short direct quotes only when wording matters. Keep quotes brief and tie each quote to an analytic job.

| Source ID | Quote | Why It Matters |
| --- | --- | --- |
| `SRC-01` |  |  |
| `SRC-02` |  |  |

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
| `CLM-01` | `SRC-01` |  | Krainer via Glenn Diesen | `candidate` |
| `CLM-02` | `SRC-02` |  | Martyanov via Dialogue Works | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

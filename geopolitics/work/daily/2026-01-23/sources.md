# Sources

Date: `2026-01-23`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-01-23/`

## Intake Batch

This run is grounded in the `2026-01-23` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-01-23/source-glenn-diesen-george-beebe-a-new-us-grand-strategy-europe-s-strategic-failure-2026-01-23.md` | transcript | `imported` | `yes` | Beebe | Glenn Diesen | cross-host pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-01-23/source-zelensky-fails-in-davos-turns-on-eu-says-cannot-resist-putin-trump-putin-us-agree-dirty-war-talks-2026-01-23.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | historical upstream transcript backfill; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Beebe | Glenn Diesen | transcript | [2026-01-23 Beebe](../../../archive/sources/2026-01-23/source-glenn-diesen-george-beebe-a-new-us-grand-strategy-europe-s-strategic-failure-2026-01-23.md) | George Beebe: A New U.S. Grand Strategy & Europe's Strategic Failure |
| `SRC-02` | Mercouris | Alexander Mercouris | transcript | [2026-01-23 Mercouris](../../../archive/sources/2026-01-23/source-zelensky-fails-in-davos-turns-on-eu-says-cannot-resist-putin-trump-putin-us-agree-dirty-war-talks-2026-01-23.md) | Zelensky Fails In Davos, Turns On EU, Says Cannot Resist Putin Trump; Putin US Agree Dirty War Talks |

## Load-Bearing Quotes

Use short direct quotes only when wording matters. Keep quotes brief and tie each quote to an analytic job.

| Source ID | Quote | Why It Matters |
| --- | --- | --- |
| `SRC-01` |  |  |
| `SRC-02` |  |  |

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
| `CLM-01` | `SRC-01` |  | Beebe via Glenn Diesen | `candidate` |
| `CLM-02` | `SRC-02` |  | Mercouris via Alexander Mercouris | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

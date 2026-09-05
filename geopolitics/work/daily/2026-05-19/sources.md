# Sources

Date: `2026-05-19`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-05-19/`

## Intake Batch

This run is grounded in the `2026-05-19` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-05-19/source-alexander-mercouris-russia-warns-nato-baltic-war-test-nuclear-forces-putin-to-china-trump-iran-retreat-konstantinovka-2026-05-19.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-05-19/source-daniel-davis-iran-attack-on-hold-2026-05-19.md` | operator-transcript | `imported` | `yes` | Davis | Daniel Davis | authored stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-05-19/source-game-theory-26-the-holy-empire-of-ai-2026-05-19.md` | transcript | `imported` | `yes` | Jiang | Upstream Unresolved | historical upstream transcript backfill; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-05-19/source-glenn-diesen-scott-ritter-europe-attacked-russia-retaliation-is-now-unavoidable-2026-05-19.md` | transcript | `imported` | `yes` | Ritter | Glenn Diesen | host-pressure test; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2026-05-19 Mercouris](../../../archive/sources/2026-05-19/source-alexander-mercouris-russia-warns-nato-baltic-war-test-nuclear-forces-putin-to-china-trump-iran-retreat-konstantinovka-2026-05-19.md) | Russia Warns NATO Baltic War Test Nuclear Forces; Putin To China; Trump Iran Retreat; Konstantinovka |
| `SRC-02` | Davis | Daniel Davis | operator-transcript | [2026-05-19 Davis](../../../archive/sources/2026-05-19/source-daniel-davis-iran-attack-on-hold-2026-05-19.md) | Iran Attack On Hold /Lt Col Daniel Davis |
| `SRC-03` | Jiang | Upstream Unresolved | transcript | [2026-05-19 Jiang](../../../archive/sources/2026-05-19/source-game-theory-26-the-holy-empire-of-ai-2026-05-19.md) | Game Theory 26 The Holy Empire Of Ai |
| `SRC-04` | Ritter | Glenn Diesen | transcript | [2026-05-19 Ritter](../../../archive/sources/2026-05-19/source-glenn-diesen-scott-ritter-europe-attacked-russia-retaliation-is-now-unavoidable-2026-05-19.md) | Scott Ritter: Europe Attacked Russia - Retaliation Is Now Unavoidable |

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
| `CLM-02` | `SRC-02` |  | Davis via Daniel Davis | `candidate` |
| `CLM-03` | `SRC-03` |  | Jiang via Upstream Unresolved | `candidate` |
| `CLM-04` | `SRC-04` |  | Ritter via Glenn Diesen | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

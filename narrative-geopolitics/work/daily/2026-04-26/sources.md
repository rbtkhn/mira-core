# Sources

Date: `2026-04-26`

Status: `template`

## Source Basis

Primary source basis:

- `narrative-geopolitics/archive/source-manifest.json`
- `narrative-geopolitics/archive/sources/2026-04-26/`

## Intake Batch

This run is grounded in the `2026-04-26` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/2026-04-26/source-alexander-mercouris-us-eu-ukraine-russia-iran-sunday-2026-04-26.md` | transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | stream-sequence spine; review and narrow to owning crisis object before synthesis. |
| `archive/sources/2026-04-26/source-johnson-lets-talk-geopolitics-whcd-iran-2026-04-26.md` | transcript | `imported` | `yes` | Johnson | Upstream Unresolved | historical upstream transcript backfill; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Mercouris | Alexander Mercouris | transcript | [2026-04-26 Mercouris](../../../archive/sources/2026-04-26/source-alexander-mercouris-us-eu-ukraine-russia-iran-sunday-2026-04-26.md) | US Says EU Has No Ukraine Plan; Ukraine Wants More EU Funds Russia Economy Strong; Iran Scorns Talks |
| `SRC-02` | Johnson | Upstream Unresolved | transcript | [2026-04-26 Johnson](../../../archive/sources/2026-04-26/source-johnson-lets-talk-geopolitics-whcd-iran-2026-04-26.md) | Johnson Lets Talk Geopolitics Whcd Iran |

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
| `CLM-02` | `SRC-02` |  | Johnson via Upstream Unresolved | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

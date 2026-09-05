# Sources

Date: `2026-08-29`

Status: `live-intake-first`

## Source Basis

Primary source basis:

- `archive/sources/geopolitics/source-manifest.json`
- `archive/sources/geopolitics/sources/2026-08-29/`

## Intake Batch

This run is grounded in the `2026-08-29` day batch already landed in the central archive.

| Source File | Source Type | Intake Status | Manifest Row | Voice Route | Channel Route | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `archive/sources/geopolitics/sources/2026-08-29/source-breaking-trump-rejects-saudi-arabia-request-mou-breaks-down-due-to-gaza-w-cia-larry-johnson-2026-08-29.md` | cleaned-transcript | `imported` | `yes` | Johnson | Moral Resistance | guest interview pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/geopolitics/sources/2026-08-29/source-russia-rejects-vatican-and-cia-ceasefire-demands-2026-08-29.md` | cleaned-transcript | `imported` | `yes` | Mercouris | The Duran | guest interview pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/geopolitics/sources/2026-08-29/source-russian-multi-day-strikes-shatter-kiev-massive-ammo-explosion-us-vatican-truce-bid-fails-orekhov-2026-08-29.md` | cleaned-transcript | `imported` | `yes` | Mercouris | Alexander Mercouris | host monologue; review and narrow to owning crisis object before synthesis. |
| `archive/sources/geopolitics/sources/2026-08-29/source-seyed-m-marandi-iran-activates-war-economy-military-surge-as-all-out-conflict-becomes-inevitable-2026-08-29.md` | cleaned-transcript | `imported` | `yes` | Marandi | Nima Alkhorshid | guest interview pressure test; review and narrow to owning crisis object before synthesis. |
| `archive/sources/geopolitics/sources/2026-08-29/source-trita-parsi-why-the-world-is-quietly-taking-iran-s-side-in-the-war-2026-08-29.md` | cleaned-transcript | `imported` | `yes` | Parsi | Glenn Diesen | guest interview pressure test; review and narrow to owning crisis object before synthesis. |

## Run Source Set

| Source ID | Voice | Host / Channel | Modality | Archive Path | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| `SRC-01` | Johnson | Moral Resistance | cleaned-transcript | [2026-08-29 Johnson](../../../../archive/sources/geopolitics/sources/2026-08-29/source-breaking-trump-rejects-saudi-arabia-request-mou-breaks-down-due-to-gaza-w-cia-larry-johnson-2026-08-29.md) | BREAKING: TRUMP REJECTS SAUDI ARABIA REQUEST, MOU BREAKS DOWN DUE TO GAZA w/ CIA Larry Johnson |
| `SRC-02` | Mercouris | The Duran | cleaned-transcript | [2026-08-29 Mercouris](../../../../archive/sources/geopolitics/sources/2026-08-29/source-russia-rejects-vatican-and-cia-ceasefire-demands-2026-08-29.md) | Russia Rejects Vatican and CIA Ceasefire Demands |
| `SRC-03` | Mercouris | Alexander Mercouris | cleaned-transcript | [2026-08-29 Mercouris](../../../../archive/sources/geopolitics/sources/2026-08-29/source-russian-multi-day-strikes-shatter-kiev-massive-ammo-explosion-us-vatican-truce-bid-fails-orekhov-2026-08-29.md) | Russian Multi Day Strikes Shatter Kiev; Massive Ammo Explosion; US Vatican Truce Bid Fails; Orekhov |
| `SRC-04` | Marandi | Nima Alkhorshid | cleaned-transcript | [2026-08-29 Marandi](../../../../archive/sources/geopolitics/sources/2026-08-29/source-seyed-m-marandi-iran-activates-war-economy-military-surge-as-all-out-conflict-becomes-inevitable-2026-08-29.md) | Seyed M. Marandi: Iran Activates War Economy & Military Surge as All-Out Conflict Becomes Inevitable |
| `SRC-05` | Parsi | Glenn Diesen | cleaned-transcript | [2026-08-29 Parsi](../../../../archive/sources/geopolitics/sources/2026-08-29/source-trita-parsi-why-the-world-is-quietly-taking-iran-s-side-in-the-war-2026-08-29.md) | Trita Parsi: Why the World Is Quietly Taking Iran's Side in the War |

## Historical Context Set

Populate only after a threshold-triggered Library pressure test. `LIB-*`
references remain distinct from the manifest-backed Run Source Set and do not
count toward intake coverage or current-event corroboration.

| Library Source | Body IDs | Analytic Role | Coverage | Hash State | Private Packet Digest |
| --- | --- | --- | --- | --- | --- |
| `none` | `none` | `not-invoked` | `none` | `none` | `none` |

## Load-Bearing Quotes

Use short direct quotes only when wording matters. Keep quotes brief and tie each quote to an analytic job.

| Source ID | Quote | Why It Matters |
| --- | --- | --- |
| `SRC-01` |  |  |
| `SRC-02` |  |  |
| `SRC-03` |  |  |
| `SRC-04` |  |  |
| `SRC-05` |  |  |

## Initial Claims

| Claim ID | Source IDs | Claim | Voice / Channel Note | Initial Status |
| --- | --- | --- | --- | --- |
| `CLM-01` | `SRC-01` |  | Johnson via Moral Resistance | `candidate` |
| `CLM-02` | `SRC-02` |  | Mercouris via The Duran | `candidate` |
| `CLM-03` | `SRC-03` |  | Mercouris via Alexander Mercouris | `candidate` |
| `CLM-04` | `SRC-04` |  | Marandi via Nima Alkhorshid | `candidate` |
| `CLM-05` | `SRC-05` |  | Parsi via Glenn Diesen | `candidate` |

## Source Hygiene

- Confirm each archive path resolves.
- Confirm each source has a manifest row.
- Confirm `voice_slugs`, `host_slug`, and modality before synthesis.
- Confirm the day's new source material was imported before synthesis, or mark the run as retrospective.

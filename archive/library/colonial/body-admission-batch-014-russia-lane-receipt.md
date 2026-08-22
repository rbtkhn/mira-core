---
title: "Colonial Library Body Admission Batch 014 Russia Lane Receipt"
date: 2026-08-22
status: completed
target_standard: MIRA-LIBRARY-ERA-SUFFICIENCY-V1
target_profile: BOUNDED-HISTORICAL-SHELF-V1
---

# Colonial Library Body Admission Batch 014 Russia Lane Receipt

## Boundary

This receipt records one Batch 014 Russia lane correction. The prior Colonial roster had no explicit Russia/Muscovy authority lane. This batch added five Russia/Eurasian-imperial metadata authorities and admitted one clean public-domain literary/transmission body.

The batch did not stage, commit, push, publish, or ingest anything into the private Archive. Admitted text bodies live only in the portable private library text store.

## Counts

| Measure | Count |
| --- | ---: |
| New metadata authorities added | 5 |
| Authorities attempted for body admission | 5 |
| Authorities newly represented | 1 |
| Bodies downloaded/derived for inspection | 1 |
| Bodies admitted | 1 |
| Authorities deferred before body admission | 4 |
| Archive ingestions | 0 |
| Git staging / commit / push | 0 |

## New Russia Authorities

| Source ID | Authority | Status | Coverage |
| --- | --- | --- | --- |
| `LIB-COLONIAL-AUTHORITY-073-SOBORNOE-ULOZHENIE` | Sobornoye Ulozhenie / Muscovite law code | `missing` | `metadata-only` |
| `LIB-COLONIAL-AUTHORITY-074-PETER-TABLE-RANKS` | Peter the Great / Table of Ranks | `missing` | `metadata-only` |
| `LIB-COLONIAL-AUTHORITY-075-CATHERINE-NAKAZ` | Catherine II / Nakaz | `missing` | `metadata-only` |
| `LIB-COLONIAL-AUTHORITY-076-RUSSIAN-LITERARY-ANTHOLOGY` | Russian early-modern literary voices | `available` | `selected-works` |
| `LIB-COLONIAL-AUTHORITY-077-RUSSIAN-SIBERIAN-EXPANSION` | Russian Siberian and steppe expansion documents | `missing` | `metadata-only` |

## Admitted Body

| Source | Body ID | Bytes | SHA-256 | Language | Source coverage | Body coverage |
| --- | --- | ---: | --- | --- | --- | --- |
| `LIB-COLONIAL-AUTHORITY-076-RUSSIAN-LITERARY-ANTHOLOGY` | `LIB-COLONIAL-AUTHORITY-076-RUSSIAN-LITERARY-ANTHOLOGY-PART1-WIENER-PG71933` | 949,862 | `217a61e74d17c2b8e28a77dbb726dd0d23d0eb7c67e8aba0d7c3bea929c36867` | English | `selected-works` | `complete-work` |

## Deferred Rows

| Source | Disposition |
| --- | --- |
| `LIB-COLONIAL-AUTHORITY-073-SOBORNOE-ULOZHENIE` | Metadata-ready/body-research-incomplete. Needs Russian original or vetted public-domain translation/OCR of the 1649 law code. |
| `LIB-COLONIAL-AUTHORITY-074-PETER-TABLE-RANKS` | Metadata-ready/body-research-incomplete. Needs clean text of the 1722 Table of Ranks or a bounded Petrine decree packet; modern summary pages were not admitted. |
| `LIB-COLONIAL-AUTHORITY-075-CATHERINE-NAKAZ` | Metadata-ready/body-research-incomplete. Bibliographic leads to the 1768 English `Grand Instructions` exist, but no clean source text body was recovered in this wave. |
| `LIB-COLONIAL-AUTHORITY-077-RUSSIAN-SIBERIAN-EXPANSION` | Metadata-ready/body-research-incomplete. Needs a reviewable packet of exact Siberian/steppe expansion documents rather than a broad narrative source. |

## Post-Batch Sufficiency Metrics

| Metric | After Batch 013 | After Batch 014 |
| --- | ---: | ---: |
| Colonial authorities | 72 | 77 |
| Represented authorities | 52 | 53 |
| Available authority ratio | 72.22% | 68.83% |
| Available bodies | 64 | 65 |
| Available bodies per authority | 0.89 | 0.84 |
| Non-metadata coverage count | 50 | 51 |
| Non-metadata coverage ratio | 69.44% | 66.23% |
| Missing authorities | 20 | 24 |

The ratio decrease is intentional and honest: Russia was a real civilizational gap in the Colonial shelf. Adding the lane makes the roster more globally balanced while creating new body-research obligations.

## Validation

- `tools\run.ps1 session-preflight --temp-root C:\private\mira-core-session-temp`: passed.
- `tools\run.ps1 library render-index --json`: passed and regenerated stale library/Colonial indexes.
- `tools\run.ps1 library validate --json`: passed.
- `tools\run.ps1 library render-index --check --json`: passed, no stale paths.
- `tools\run.ps1 test --path tests/test_archive_library.py` with `MIRA_CORE_SESSION_TEMP_ROOT=C:\private\mira-core-session-temp`: passed, 24 tests.

## Conservative Limits

- The admitted Russia body is an English public-domain anthology, not Russian-original coverage.
- The source gives useful representation for Lomonosov, Derzhavin, historical songs, and earlier Russian literary material, but it is not a complete corpus for any author.
- Catherine/Nakaz, Petrine service-state law, Muscovite law, and Siberian/steppe expansion remain metadata-ready rather than body-admitted.

## Re-Entry Point

Continue with a Russia source-recovery wave or produce a seal-gap plan from the expanded 77-authority Colonial roster.

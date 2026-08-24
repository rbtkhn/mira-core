# Medieval Body Admission Batch 14

**Status:** completed with isolated failures
**Date:** 2026-08-20

Batch 14 inspected all ten previously bodyless Medieval authorities and admitted twelve bodies across five authorities. The Medieval shelf advanced from 110 to 122 bodies (145,460,837 bytes) across 60 authorities. Ancient remains at 193 bodies, leaving a 71-body gap. The JSON companion is the machine-reviewable receipt.

## Admitted bodies

| Authority | Bodies | Coverage boundary |
| --- | ---: | --- |
| Michael the Syrian | 3 | Chabot's complete three-volume French translation sequence; readable automated OCR, with damaged Syriac, Greek, diacritics, tables, and apparatus disclosed. |
| al-Mas'udi | 5 | Volumes I-V of the nine-volume Arabic-French *Les Prairies d'or* edition; readable French narrative, damaged Arabic/apparatus, no English or recension-equivalence claim. |
| *Secret History of the Mongols* tradition | 1 | Fifteen-fascicle Chinese received-witness transcription; Wikisource marks the work incomplete, and the lost original witness is not represented. |
| Minhaj-i Siraj Juzjani | 2 | Complete two-volume Raverty English translation sequence; readable automated OCR with damaged transliteration and foreign-script apparatus disclosed. |
| *Goryeosa* editorial tradition | 1 | 136 substantive root-linked fascicles; volume 87 empty and volumes 138-139 absent, so coverage remains partial. |

All twelve bodies passed importer dry-run before admission and live only in `.mira-private/library/texts/`. Exact hashes and byte counts are recorded in the JSON companion.

## Isolated and deferred routes

- Domesday Book, Ibn al-Athir, Rashid al-Din, and Someshvara III remain `body-research-incomplete` because no clean portable body crossed their edition, witness, and rights boundaries.
- Yusuf Khass Hajib's Fergana facsimile is public domain, but only seven Wikisource pages were transcribed; five contained substantive verse. That candidate was rejected as too fragmentary.
- Al-Mas'udi volumes VI-IX were inspected previously and remain deferred solely because this batch reached its twelve-body ceiling.

## Validation and boundary

- Library validation passed.
- Generated indexes were rendered; drift check passed with no stale paths.
- Private-text verification passed: 301 checked, 16 expected missing, zero failures.
- `tests/test_archive_library.py`: 24 passed.
- Registry, private text store, and generated indexes changed. Nothing was staged, committed, pushed, published, or ingested into the Archive catalog.

The exact re-entry point is a small completion batch for al-Mas'udi volumes VI-IX, followed by a parity-oriented batch of additional works and editions from already represented authorities.

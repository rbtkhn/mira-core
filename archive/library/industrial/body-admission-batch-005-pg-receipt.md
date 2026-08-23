# Industrial Library Body Admission Batch 005 Project Gutenberg Receipt

Status: `admission-complete`
Era: `industrial`
Date: 2026-08-23
Research receipt: `archive/library/industrial/body-research-batch-005-inspection-receipt.md`
Download receipt: `archive/library/industrial/body-download-batch-005-inspection-receipt.md`
Private text root: `C:\private\mira-library-texts`

## Authority Boundary

This receipt records admission of nine clean Batch 005 Project Gutenberg bodies
into the Mira Library registry and configured private text store. It does not
admit the paused Sojourner Truth OCR candidate, ingest any body into the private
Archive catalog, stage, commit, push, publish, or create a seal claim.

## Batch Result

Authorities with bodies admitted: 7
Bodies admitted: 9
Paused candidates: 1
Private Archive ingests: 0
Publication actions: 0

## Admitted Bodies

| Source ID | Body ID | Work | Language | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| `LIB-INDUSTRIAL-AUTHORITY-019-MACHADO-DE-ASSIS` | `LIB-INDUSTRIAL-AUTHORITY-019-MACHADO-DE-ASSIS-DOM-CASMURRO-PG55752` | `Dom Casmurro` | Portuguese | 418230 | `0fc3dbf384544d81d87e5a731e67b7976ac3a57acb378f0f354d12a3b52bd0c7` |
| `LIB-INDUSTRIAL-AUTHORITY-019-MACHADO-DE-ASSIS` | `LIB-INDUSTRIAL-AUTHORITY-019-MACHADO-DE-ASSIS-BRAS-CUBAS-PG54829` | `Memorias Posthumas de Braz Cubas` | Portuguese | 403243 | `edfe4370698ed5716a9692b980a8d6ee77b4ff8116503bb2e08675f1d10d303a` |
| `LIB-INDUSTRIAL-AUTHORITY-040-FARADAY` | `LIB-INDUSTRIAL-AUTHORITY-040-FARADAY-CHEMICAL-HISTORY-CANDLE-PG14474` | `The Chemical History of a Candle` | English | 246914 | `c053ca4ae7880585a15001cd3ffdaf5f09cd08c3329b828ffd8c90ce335482b9` |
| `LIB-INDUSTRIAL-AUTHORITY-064-CONRAD` | `LIB-INDUSTRIAL-AUTHORITY-064-CONRAD-HEART-OF-DARKNESS-PG219` | `Heart of Darkness` | English | 237072 | `c0b0bc91c7695f9d01aacb240e82a9b559f57558f98ad0b1f167eba21f6be6f7` |
| `LIB-INDUSTRIAL-AUTHORITY-064-CONRAD` | `LIB-INDUSTRIAL-AUTHORITY-064-CONRAD-LORD-JIM-PG5658` | `Lord Jim` | English | 751822 | `e2de6f15eb867e864aa4b5e22410d6dc1c12b7c225a48e2376f6401b71a3b96e` |
| `LIB-INDUSTRIAL-AUTHORITY-081-SCHREINER` | `LIB-INDUSTRIAL-AUTHORITY-081-SCHREINER-STORY-AFRICAN-FARM-PG1441` | `The Story of an African Farm` | English | 583169 | `01d0c7fff4673ecb1f6b8fc70938fe4ccfb2139803fd3b4f30ab51f6e40c6815` |
| `LIB-INDUSTRIAL-AUTHORITY-082-STANTON` | `LIB-INDUSTRIAL-AUTHORITY-082-STANTON-EIGHTY-YEARS-MORE-PG11982` | `Eighty Years and More; Reminiscences 1815-1897` | English | 816725 | `e30e3011123135463627f9b6efe1484ffc7002855df622493bb0f0bb68dc3a69` |
| `LIB-INDUSTRIAL-AUTHORITY-084-ZITKALA-SA` | `LIB-INDUSTRIAL-AUTHORITY-084-ZITKALA-SA-AMERICAN-INDIAN-STORIES-PG10376` | `American Indian Stories` | English | 201897 | `b9934b55d2f83876ea24e3c7f1397240b02f1caf63892823bcdbb59954309252` |
| `LIB-INDUSTRIAL-AUTHORITY-036-NIETZSCHE` | `LIB-INDUSTRIAL-AUTHORITY-036-NIETZSCHE-GENEALOGY-MORALS-PG52319` | `The Genealogy of Morals` | English | 358579 | `90ab67b3c15fb8a4220f36b559514098e33f43d58e4403405575949c039c1cba` |

## Coverage Notes Updated

Source-level coverage notes were corrected after admission so they no longer
say the affected authorities are metadata-only. Coverage remains conservative:
Machado, Conrad, and Nietzsche are `principal-works`; Faraday, Schreiner,
Stanton, and Zitkala-Sa remain `selected-works`.

## Paused Candidate

Sojourner Truth remains paused. The downloaded IA/LOC-derived OCR file is
private and hash-recorded in the download receipt, but it was not admitted
because the OCR opening is noisy and the lineage differs from the preferred LOC
1875 item. A cleaner LOC text/PDF extraction route should be resolved before
admission.

## Verification

- Admitted payload hash check: 9 checked, 9 matched registry bytes and SHA-256.
- `tools\run.ps1 library validate --json`: passed.
- `tools\run.ps1 library render-index --check --json`: passed.
- `tools\run.ps1 test --path tests/test_archive_library.py`: 26 passed.

Full library-wide `verify-texts` was not used as a completion gate because the
active private text store has known pre-existing missing payloads from older
eras. The newly admitted Batch 005 bodies were verified directly against their
registry byte counts and SHA-256 digests.

## Re-Entry Point

The next bounded action is either to repair Sojourner Truth source extraction,
or to stage/commit the Batch 005 admission metadata and receipt files after a
Mira GitHub publication boundary check.

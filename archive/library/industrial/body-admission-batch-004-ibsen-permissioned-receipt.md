# Industrial Library Batch 004 Ibsen Permissioned Admission Receipt

Date: 2026-08-23

Status: admitted to Mira Library private text store with operator-authorized rights basis.

## Scope

Authority: `LIB-INDUSTRIAL-AUTHORITY-013-IBSEN`

Private text root used for admission: `C:\private\mira-library-texts`

Source files came from the Batch 004 original-language inspection root:
`C:\private\mira-library-inspection\industrial-batch004-original-language`

## Admitted Bodies

| Body ID | Work | Source / edition label | License status | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| `LIB-INDUSTRIAL-AUTHORITY-013-IBSEN-ET-DUKKEHJEM-DRACOR-TEI-PERMISSIONED` | `Et dukkehjem` | DraCor Ibsen Corpus TEI export from Henrik Ibsens skrifter; operator-authorized BY-NC source body | `permissioned` | 315459 | `975471dd21ff9e8d7ad2f4f698934e5670bf34b2b404164409f172c50e64b282` |
| `LIB-INDUSTRIAL-AUTHORITY-013-IBSEN-EN-FOLKEFIENDE-DRACOR-TEI-PERMISSIONED` | `En folkefiende` | DraCor Ibsen Corpus TEI export from Henrik Ibsens skrifter; operator-authorized BY-NC source body | `permissioned` | 387373 | `7b928330b9ed231fc7373993acfdaa714d413df9234a166500342be99de3290f` |

## Verification

- `library admit-text` succeeded for both Ibsen TEI bodies.
- `library render-index --json` regenerated `archive/library/text-sources-index.md` and `archive/library/industrial/index.md`.
- `library validate --json` passed.
- Manual private-payload verification passed for both admitted Ibsen files: byte counts and SHA-256 hashes match the registry output.
- Full `library verify-texts --json` was attempted with `MIRA_CORE_LIBRARY_TEXT_ROOT=C:\private\mira-library-texts`; it failed on pre-existing missing Ancient and Colonial payloads in that private store, not on the newly admitted Ibsen bodies.

## Boundary

No private Archive ingestion, staging, commit, push, or publication occurred.

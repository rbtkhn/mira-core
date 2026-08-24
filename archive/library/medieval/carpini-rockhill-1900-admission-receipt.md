# John of Plano Carpini, Rockhill 1900 — Admission Receipt

Date: 2026-08-20
Status: `admitted`
Archive-catalog effect: `none`

## Result

One English body was admitted for John of Plano Carpini through Library Import. The exact header-bound candidate was copied into Mira's private library text store and bound to the existing Medieval authority record.

| Field | Admitted value |
| --- | --- |
| Source ID | `LIB-MEDIEVAL-AUTHORITY-077-JOHN-OF-PLANO-CARPINI` |
| Body ID | `LIB-MEDIEVAL-AUTHORITY-077-CARPINI-JOURNEY-ROCKHILL-1900-EN` |
| Work | *Historia Mongalorum / The Journey of Friar John of Pian de Carpine to the Court of Kuyuk Khan, 1245–1247* |
| Language | English |
| Translator/editor | W. W. Rockhill |
| Edition | Hakluyt Society, London, 1900; first Carpini account, printed pages 1–32 |
| Logical location | `library-text://LIB-MEDIEVAL-AUTHORITY-077-CARPINI-JOURNEY-ROCKHILL-1900-EN.txt` |
| Bytes | 44,687 |
| SHA-256 | `6f8ff4de6938144092bd3b26ad1292a9bd4d8fa807d98fb2e1dc500d8f0376a7` |
| License | `public-domain`, United States posture; no claim for every jurisdiction |
| Body coverage | `complete-work` for this named first Rockhill account only |
| Body status | `available` |

The body header preserves the source and body IDs, edition, transformation lineage, collation receipts, rights boundary, coverage boundary, and exclusions. The private target and registry record independently rehash to the same digest.

## Coverage and Maturity

The source remains `principal-work`. `complete-work` applies only to Rockhill's first Carpini account on printed pages 1–32. It excludes Benedict the Pole's companion account, Latin equivalence, all recensions, and complete-surviving-corpus coverage.

Admission creates availability, not reviewed or verified curatorial status. The authority remains capped below Level 5 until a verified Latin counterpart and explicit cross-edition relationship are present.

## Validation

- Library Import non-check admission: passed after one safely contained filesystem-permission failure and an approved exact-command retry.
- Copied-body byte count and SHA-256: matched.
- `library verify-texts --json`: passed; 302 bodies checked, 17 authorities missing bodies.
- `library validate --json`: passed.
- `library render-index --check --json`: passed; 62 Medieval authorities and 316 indexed bodies.
- `tests/test_archive_library.py`: 24 passed.

## Persistence and Boundaries

The body is private under `.mira-private/library/texts/`; only metadata, indexes, and this receipt are in the working tree. No Rubruck body was changed or admitted. No Archive catalog ingestion, staging, commit, push, or publication occurred.

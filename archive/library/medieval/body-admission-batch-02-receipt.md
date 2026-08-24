# Medieval Body Admission Batch 02

Date: 2026-08-19
Status: partial success

## Scale result

The accepted 60-authority roster is now fully represented in the registry. Forty-nine missing records were added conservatively as `stub`, `missing`, and `metadata-only`; no record gained availability or maturity from roster selection alone.

## Ten-authority recovery cohort

Two bodies passed after exact boundary repair:

| Authority | Admitted body | Boundary result | Bytes |
| --- | --- | --- | ---: |
| Einhard | A. J. Grant's *Life of Charlemagne* | Notker's separately authored work excluded | 69,139 |
| Geoffrey Chaucer | Skeat's *Canterbury Tales* | disputed *Tale of Gamelyn* appendix excluded | 1,414,906 |

Eight failures were isolated without blocking the cohort:

- Anna Komnene: Fordham's electronic-form reuse terms are not fully open.
- Rule of Saint Benedict: unresolved 1948 copyright notice.
- Magna Carta: file-specific reuse and clean extraction lineage unresolved.
- Qur'anic textual tradition: Tanzil's additional no-change condition requires governance review.
- Kalhana: unreconciled OCR in both Stein volumes.
- al-Biruni: restrictive item terms and unreconciled OCR.
- al-Tabari: one-volume-only Arabic OCR with unresolved rights.
- Ibn Khaldun: incomplete Arabic sequence with unresolved rights and OCR.

## Shelf state

- Medieval: 60 authorities, 34 admitted bodies, 38,226,506 bytes.
- Entire managed store: 227 bodies.
- Both the combined and Medieval indexes were regenerated.
- Library validation and index drift checks pass; all 227 admitted bodies verify with zero body failures.
- `tests/test_archive_library.py`: 24 passed.

No Archive import, staging, commit, push, or publication occurred.

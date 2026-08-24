# Medieval Body Admission Batch 01

Date: 2026-08-19
Status: partial success

This expanded cohort admitted two defensibly bounded English bodies and deferred one body whose OCR layer is not yet clean enough for admission.

## Admitted

| Authority | Body | Coverage | Bytes |
| --- | --- | --- | ---: |
| Ferdowsi | Atkinson, abridged *Shahnameh* selection from Project Gutenberg 10315 | `selected-passages` | 746,363 |
| Jayadeva | Arnold, adaptive *Indian Song of Songs* selection from Project Gutenberg 25965 | `selected-passages` | 79,759 |

Both derived files preserve the relevant Project Gutenberg header and jurisdiction warning. Exact-marker extraction removed unrelated anthology works without upgrading either body to complete-work status.

## Deferred

Amir Khusrau's *Khaza'in al-Futuh*, translated by Wahid Mirza (1975), is available from Zenodo under CC BY 4.0. Its 99-page PDF has an imperfect text layer. Page-order and extraction reconciliation remain incomplete, so it was not admitted.

## Result

- Medieval shelf: 11 authorities, 32 bodies, 36,742,461 bytes.
- Entire managed text store: 225 bodies, none missing.
- `library validate`: passed.
- `library render-index --check`: passed.
- `library verify-texts`: 225 checked, 0 failures.
- `tests/test_archive_library.py`: 24 passed.

No Archive import, staging, commit, push, or publication occurred.

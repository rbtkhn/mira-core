# Medieval Body Admission Batch 07

Date: 2026-08-19
Status: success with review debt

The operator asserted that they hold all rights for the blocked Batch 06 items. This assertion was not independently verified. Twelve exact recovered payloads across nine authorities were admitted as `permissioned` and `needs-review`.

## Admitted

| Authority | Bodies | Coverage ceiling | Review debt |
| --- | ---: | --- | --- |
| al-Tabari | 1 | one Arabic volume | incomplete sequence; OCR reconciliation |
| Ibn Khaldun | 2 | two Arabic volumes | incomplete sequence; OCR reconciliation |
| Nizam al-Mulk | 1 | one edition volume | recension boundary; OCR reconciliation |
| al-Biruni | 1 | complete named two-volume English edition | OCR reconciliation; Arabic absent |
| Nasir Khusraw | 1 | selected regional extracts | incomplete work; OCR reconciliation |
| Kalhana | 2 | two-volume Stein edition | OCR and Sanskrit-English layer reconciliation |
| Bhaskara II | 1 | mixed historical translation | mixed-author component boundary; OCR reconciliation |
| *Nihon Shoki* | 2 | two-volume Aston English edition | OCR reconciliation; Japanese witness absent |
| *Tale of the Heike* | 1 | Sadler English candidate | OCR and recension reconciliation |

Jnaneshwar and Li Qingzhao remain metadata-only because no exact candidate payload exists to which the permission assertion can be attached.

## Shelf state

- Medieval: 60 authorities, 67 bodies, 65,216,979 bytes.
- Entire managed store: 260 bodies.
- Fourteen Medieval bodies are `needs-review`; they are excluded from clean available-body verification.
- Registry validation and era-index drift checks pass; 246 available bodies verify with zero failures.
- `tests/test_archive_library.py`: 24 passed.

Two transient Windows registry-write failures occurred after the Heike and Bhaskara payload copies. Both exact orphaned files were verified and successfully reconciled with their registry records; no orphan remains.

No Archive import, staging, commit, push, or publication occurred.

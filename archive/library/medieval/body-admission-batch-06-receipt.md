# Medieval Body Admission Batch 06

Date: 2026-08-19
Status: partial success with review debt

This failure-isolated cohort evaluated twelve missing authorities. One open-license body was admitted as `needs-review`; eleven prior blockers remained material and visible.

## Admitted

| Authority | Body | Status | Bytes |
| --- | --- | --- | ---: |
| Amir Khusrau | Wahid Mirza, *Khazain-ul-Futuh* (1975), Zenodo-derived text | `needs-review` | 262,568 |

Zenodo records the payload as CC BY 4.0. All 99 PDF pages are represented by numbered boundaries in the derived UTF-8 body. Visual samples from the title, early text, middle, and final page agree with the page sequence, but recurrent OCR defects remain. The body therefore does not enter clean available-body verification.

## Isolated failures

| Authority | Blocking class |
| --- | --- |
| al-Tabari | Incomplete Arabic sequence; uncorrected OCR; unstated rights; restricted modern English. |
| Ibn Khaldun | Incomplete, poor Arabic OCR; unstated rights; restricted complete English. |
| Nizam al-Mulk | OCR, rights, edition-layer, and recension-boundary debt. |
| al-Biruni | Noncommercial/no-derivatives OCR route; incomplete Wikisource validation. |
| Nasir Khusraw | Copy restriction and incomplete English extract. |
| Kalhana | Two uncorrected OCR volumes; unproofread Wikisource; layer reconciliation absent. |
| Bhaskara II | Mixed-author historical volume and noisy OCR. |
| Jnaneshwar | Recension and reusable-translation gap. |
| Li Qingzhao | Fragmentary attribution-critical corpus; modern English is CC BY-NC-ND. |
| *Nihon Shoki* | No clean licensed portable Aston sequence. |
| *Tale of the Heike* | Unreconciled Sadler OCR; no Japanese witness. |

## Shelf state

- Medieval: 60 authorities, 55 bodies, 52,588,300 bytes.
- Entire managed store: 248 bodies.
- Two Medieval bodies are now `needs-review`.
- Registry validation and era-index drift checks pass; 246 available bodies verify with zero failures.
- `tests/test_archive_library.py`: 24 passed.

No Archive import, staging, commit, push, or publication occurred.

# Medieval Body Admission Batch 04

Date: 2026-08-19
Status: partial success; failures isolated

This failure-isolated cohort evaluated twelve authorities together. One body passed provenance, rights, structure, and coverage inspection and was admitted. Eleven unresolved candidates did not block it.

## Admitted

| Authority | Body | Status | Bytes |
| --- | --- | --- | ---: |
| Moses Maimonides | Friedlander, second revised edition of *The Guide for the Perplexed* (1910), Project Gutenberg 73584 | `available` | 1,618,331 |

The admitted file contains all three parts and preserves the Project Gutenberg wrapper. Its `complete-work` claim applies only to this named English translation edition. It makes no claim about a Judeo-Arabic body, translation equivalence, *Mishneh Torah*, or the complete Maimonides corpus.

## Isolated failures

| Authority | Blocking finding |
| --- | --- |
| Constantine VII | Located Serbian Wikisource surface is an index to selected chapters 30-36, not a complete body. |
| Michael Psellos | Complete Fordham English text has an electronic-use restriction unsuitable for clean admission here. |
| *Kebra Nagast* | Sacred Texts candidate returned HTTP 403; no inspectable replacement resolved. |
| Domesday Book | No portable corpus body with a defensible edition boundary resolved. |
| Judah Halevi | Sacred Texts candidate returned HTTP 403; older OCR remains edition-risky. |
| al-Masudi | Nine-volume OCR route still requires edition and volume reconciliation. |
| Ibn Battuta | Lee route is abridged OCR. |
| Ibn Jubayr | Arabic Wikisource surface is a section index; older OCR remains uninspected. |
| Rashid al-Din | Composite tradition lacks a resolved portable edition boundary. |
| Xuanzang | Located OCR routes mix edition or volume lineages. |
| Shen Kuo | No rights-clear, inspectable English body resolved. |

## Shelf state

- Medieval: 60 authorities, 39 bodies, 42,457,983 bytes.
- Entire managed store: 232 bodies.
- One Medieval body remains `needs-review` from the prior batch.
- Registry validation and era-index drift checks pass; 231 available bodies verify with zero failures.
- `tests/test_archive_library.py`: 24 passed.

No Archive import, staging, commit, push, or publication occurred.

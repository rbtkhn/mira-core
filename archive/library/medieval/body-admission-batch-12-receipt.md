# Medieval Body Admission Batch 12

**Batch:** `MEDIEVAL-BODY-ADMISSION-12`
**Date:** 2026-08-20
**Status:** completed with one isolated failure

Batch 12 inspected the ten authorized authorities and admitted **15 bodies across nine authorities**. The Medieval shelf now contains **60 authorities, 102 bodies, and 100,853,102 registered text bytes**. Ancient remains at **56 authorities, 193 bodies, and 159,939,301 bytes**; the body-count gap narrowed from 106 to 91.

## Admissions

| Authority | Bodies | Coverage posture |
| --- | ---: | --- |
| Ibn Hazm | 1 | Complete five-part Arabic Wikisource work body; edition-bounded |
| al-Bakri | 1 | Partial French North Africa translation; 1913 OCR caveat |
| al-Idrisi | 3 | Complete Arabic seventy-section body plus two partial 1836 French OCR volumes |
| Xuanzang and Bianji | 4 | Two complete Chinese edition bodies plus two partial 1884 English OCR volumes |
| Sima Guang | 1 | Complete 294-fascicle Chinese Wikisource body; edition-bounded |
| Shen Kuo | 2 | Two complete Chinese edition bodies; edition-bounded |
| *Azuma Kagami* tradition | 1 | Partial Japanese body: fascicles one and two only |
| *Samguk Sagi* | 1 | Partial Korean contributor translation: 63 substantive pages |
| Rus' Primary Chronicle tradition | 1 | Complete Hypatian-witness work body in pre-reform orthography; 1997 preparation bounded |

No admission implies original/translation equivalence, critical-edition completeness, complete surviving corpus, reviewed status, or Level 6 maturity. OCR bodies retain explicit recognition-error warnings.

## Isolated failure

**Ibn al-Athir** was not admitted. The inspected routes did not combine a defensible edition identity, clean portable body, and confirmed public-domain or open-license posture. Unattributed modern mirrors and translations were excluded.

## Validation

- `library validate --json`: passed.
- `library render-index --check --json`: passed with no stale paths; 295 bodies indexed.
- `library verify-texts --json`: passed, 281 checked, zero failures; 28 source records remain without available bodies.
- `tests/test_archive_library.py`: 24 passed.

The registry, private text store, root source index, and Medieval index changed. Nothing was staged, committed, pushed, published, or imported into the broader Archive catalog.

# Colonial Body Depth Batch 016 Receipt - 2026-08-22

Target: `MIRA-LIBRARY-ERA-SUFFICIENCY-V1` and `BOUNDED-HISTORICAL-SHELF-V1`.

Inspection root: `C:\private\mira-library-inspection\colonial\balance-depth-batch-2026-08-22`

## Boundary

- Registry and private text admissions were authorized for this bounded balance-depth batch.
- Bodies were copied only into the private library text store.
- No source bodies were admitted into Git.
- No Archive ingestion, staging, commit, push, publication, or deployment occurred.
- The temporary recovery helper was removed before completion.

## Counts

- Starting Colonial state: 77 authorities, 70 represented authorities, 101 bodies.
- Final Colonial state: 77 authorities, 70 represented authorities, 131 bodies.
- Body density over all Colonial authorities: 1.701.
- Representation floor reached: yes.
- Body mass floor reached: yes.
- Body density floor reached: yes.
- Colonial private-payload census: 131 referenced Colonial bodies, 131 physical payloads present, 0 missing.
- Library-wide private-payload census: 433 referenced bodies, 433 physical payloads present, 0 missing.

## Admitted Bodies

### Indigenous Treaty / Diplomacy

1. `LIB-COLONIAL-AUTHORITY-048-TREATY-SIX-NATIONS-1784-KAPPLER-AVALON`
2. `LIB-COLONIAL-AUTHORITY-048-TREATY-WYANDOT-1785-KAPPLER-AVALON`
3. `LIB-COLONIAL-AUTHORITY-048-CHICKASAW-PEACE-FEELER-1782-KAPPLER-AVALON`
4. `LIB-COLONIAL-AUTHORITY-048-TREATY-CHOCTAW-1786-KAPPLER-AVALON`
5. `LIB-COLONIAL-AUTHORITY-048-TREATY-CHICKASAW-1786-KAPPLER-AVALON`
6. `LIB-COLONIAL-AUTHORITY-048-TREATY-SHAWNEE-1786-KAPPLER-AVALON`
7. `LIB-COLONIAL-AUTHORITY-048-TREATY-SIX-NATIONS-1789-KAPPLER-AVALON`
8. `LIB-COLONIAL-AUTHORITY-048-TREATY-CREEKS-1790-KAPPLER-AVALON`
9. `LIB-COLONIAL-AUTHORITY-048-TREATY-CHEROKEE-1791-KAPPLER-AVALON`
10. `LIB-COLONIAL-AUTHORITY-048-TREATY-CHEROKEE-1794-KAPPLER-AVALON`
11. `LIB-COLONIAL-AUTHORITY-048-TREATY-ONEIDA-1794-KAPPLER-AVALON`
12. `LIB-COLONIAL-AUTHORITY-048-TREATY-CHICKASAW-1805-KAPPLER-AVALON`

### Jesuit / Global Catholic Mission Letters

13. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESDIFIANTES01JESU-0-IA`
14. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESEDIFIANTE03TOUL-IA`
15. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESDIFIANTES05JESU-0-IA`
16. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESDIFIANTES07JESU-0-IA`
17. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESDIFIANTE14JESUGOOG-IA`
18. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESEDIFIANTE16JESU-IA`
19. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESDIFIANTES16JESU-0-IA`
20. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESEDIFIANTE17JESU-IA`
21. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESDIFIANTES20JESU-IA`
22. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESDIFIANTES23JESU-IA`
23. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESEDIFIANTE24JESU-IA`
24. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-LETTRESDIFIANTE33GOBIGOOG-IA`
25. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-CIHM-50097-IA`
26. `LIB-COLONIAL-AUTHORITY-054-LETTRES-EDIFIANTES-CIHM-50110-IA`

### Qing / Mughal / Company-Rule Administration

27. `LIB-COLONIAL-AUTHORITY-056-DU-HALDE-GENERAL-HISTORY-CHINA-VOL3-IA`
28. `LIB-COLONIAL-AUTHORITY-056-DU-HALDE-GENERAL-HISTORY-CHINA-VOL4-IA`
29. `LIB-COLONIAL-AUTHORITY-072-AIN-I-AKBARI-VOL3-IA`
30. `LIB-COLONIAL-AUTHORITY-041-ZEMINDARY-SETTLEMENT-BENGAL-VOL2-IA`

## Deferred / Skipped

- `Treaty With The Cherokee, 1785` was deferred because the accessible Avalon page yielded only a sparse carrier body through the batch extractor.
- `lettresdifiant_q25jesu` was deferred after an Internet Archive server error during OCR retrieval.

## Validation

- `tools\run.ps1 library census-texts --era colonial --json`: passed.
- `tools\run.ps1 library render-index --json`: passed and updated generated indexes.
- `tools\run.ps1 library validate --json`: passed.
- `tools\run.ps1 library render-index --check --json`: passed.
- `tools\run.ps1 library verify-texts --json`: passed, 433 checked, 0 failures, 24 declared missing.
- `tools\run.ps1 test --path tests/test_archive_library.py`: passed, 26 tests.
- `tools\run.ps1 session-preflight --temp-root C:\private\mira-core-session-temp`: passed.

## Seal Readiness Impact

This batch specifically addressed the balance/density objection raised after Batch 015. Colonial now meets the represented-authority, body-mass, body-density, live private-payload, validation, and index-coherence gates needed for sufficiency seal preparation under the active profile.

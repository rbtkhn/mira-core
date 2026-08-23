# Colonial Body Depth Batch 015 Receipt - 2026-08-22

Target: `MIRA-LIBRARY-ERA-SUFFICIENCY-V1` and `BOUNDED-HISTORICAL-SHELF-V1`.

Inspection root: `C:\private\mira-library-inspection\colonial\body-depth-batch-2026-08-22`

## Boundary

- Registry and private text admissions were authorized for this bounded body-depth batch.
- Bodies were copied only into the private library text store.
- No source bodies were admitted into Git.
- No Archive ingestion, staging, commit, push, publication, or deployment occurred.
- Coverage claims remain conservative: each body is an additional public-domain work or volume for an already represented authority, not a complete authority-corpus claim.

## Counts

- Starting Colonial state: 77 authorities, 70 represented authorities, 83 bodies.
- Final Colonial state: 77 authorities, 70 represented authorities, 101 bodies.
- Representation floor reached: yes.
- Body floor reached: yes.
- Colonial private-payload census: 101 referenced Colonial bodies, 101 physical payloads present, 0 missing.
- Library-wide private-payload census: 403 referenced bodies, 403 physical payloads present, 0 missing.

## Admitted

1. `LIB-COLONIAL-AUTHORITY-002-MILTON-AREOPAGITICA-PG608`
2. `LIB-COLONIAL-AUTHORITY-002-MILTON-PARADISE-REGAINED-PG58`
3. `LIB-COLONIAL-AUTHORITY-005-DEFOE-MOLL-FLANDERS-PG370`
4. `LIB-COLONIAL-AUTHORITY-005-DEFOE-JOURNAL-PLAGUE-YEAR-PG376`
5. `LIB-COLONIAL-AUTHORITY-009-PAINE-AMERICAN-CRISIS-PG3741`
6. `LIB-COLONIAL-AUTHORITY-009-PAINE-RIGHTS-MAN-PG3742`
7. `LIB-COLONIAL-AUTHORITY-009-PAINE-AGE-REASON-PG3743`
8. `LIB-COLONIAL-AUTHORITY-025-GOETHE-SORROWS-WERTHER-PG2527`
9. `LIB-COLONIAL-AUTHORITY-026-SCHILLER-WILHELM-TELL-PG6788`
10. `LIB-COLONIAL-AUTHORITY-026-SCHILLER-ROBBERS-PG6782`
11. `LIB-COLONIAL-AUTHORITY-006-SWIFT-TALE-TUB-PG4737`
12. `LIB-COLONIAL-AUTHORITY-006-SWIFT-BATTLE-BOOKS-PG623`
13. `LIB-COLONIAL-AUTHORITY-037-LOCKE-HUMANE-UNDERSTANDING-VOL1-PG10615`
14. `LIB-COLONIAL-AUTHORITY-024-ROUSSEAU-CONFESSIONS-PG3913`
15. `LIB-COLONIAL-AUTHORITY-014-CERVANTES-EXEMPLARY-NOVELS-PG14420`
16. `LIB-COLONIAL-AUTHORITY-010-FRANKLIN-WAY-WEALTH-PG43855`
17. `LIB-COLONIAL-AUTHORITY-008-BLAKE-MARRIAGE-HEAVEN-HELL-PG45315`
18. `LIB-COLONIAL-AUTHORITY-023-VOLTAIRE-ZADIG-PG18972`

## Skipped

- `LIB-COLONIAL-AUTHORITY-025-GOETHE-FAUST-PART1-PG3023` was already present and was not overwritten.

## Validation

- `tools\run.ps1 library census-texts --era colonial --json`: passed.
- `tools\run.ps1 library render-index --json`: passed and updated generated indexes.
- `tools\run.ps1 library validate --json`: passed.
- `tools\run.ps1 library render-index --check --json`: passed.
- `tools\run.ps1 session-preflight --temp-root C:\private\mira-core-session-temp`: passed.
- `tools\run.ps1 library verify-texts --json`: passed, 403 checked, 0 failures, 24 declared missing.
- `tools\run.ps1 test --path tests/test_archive_library.py`: passed, 26 tests.

## Seal Readiness Impact

This batch clears Colonial's body-count floor and preserves the represented-authority floor. With live private payload verification repaired and passing, Colonial now satisfies the mechanical body-depth and live-reproducibility gates needed for seal-readiness review. A separate Colonial sufficiency seal artifact can now be prepared if authorized.

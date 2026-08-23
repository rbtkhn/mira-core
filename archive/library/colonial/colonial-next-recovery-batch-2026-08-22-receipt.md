# Colonial Library Next Recovery Batch Receipt - 2026-08-22

Target: `MIRA-LIBRARY-ERA-SUFFICIENCY-V1` and `BOUNDED-HISTORICAL-SHELF-V1`.

Inspection root: `C:\private\mira-library-inspection\colonial\seal-readiness-run-2026-08-22-batch-next`

## Boundary

- Registry and private text admissions were authorized for this bounded recovery batch.
- No source bodies were admitted into Git.
- No Archive ingestion, staging, commit, push, publication, or deployment occurred.
- Rights, edition, language, and coverage claims were kept conservative.

## Counts

- Starting Colonial state for this recovery branch: 77 authorities, 61 represented authorities, 74 available bodies.
- Final Colonial state after this batch: 77 authorities, 70 represented authorities, 83 available bodies.
- Representation floor reached: yes.
- Body floor reached: no; at least 17 more available bodies are still needed for the 100-body minimum.

## Admitted

1. `LIB-COLONIAL-AUTHORITY-073-SOBORNOE-ULOZHENIE`
   - Body: `LIB-COLONIAL-AUTHORITY-073-SOBORNOE-ULOZHENIE-SELECTED-RU-WIKISOURCE`
   - Coverage: partial-work; selected Russian Wikisource linked chapters from the 1830 imperial law collection.

2. `LIB-COLONIAL-AUTHORITY-017-INCA-GARCILASO`
   - Body: `LIB-COLONIAL-AUTHORITY-017-COMENTARIOS-REALES-TOMO1-SELECTED-ES-WIKISOURCE`
   - Coverage: partial-work; selected Spanish Wikisource Tomo I chapters.

3. `LIB-COLONIAL-AUTHORITY-059-QIANLONG-MACARTNEY`
   - Body: `LIB-COLONIAL-AUTHORITY-059-ANDERSON-BRITISH-EMBASSY-CHINA-1795-IA`
   - Coverage: partial-work; first-hand Macartney embassy narrative, not the complete diplomatic packet.

4. `LIB-COLONIAL-AUTHORITY-040-CLIVE-PLASSEY`
   - Body: `LIB-COLONIAL-AUTHORITY-040-MALCOLM-LIFE-CLIVE-VOL1-PG`
   - Coverage: partial-work; one public-domain documentary-biographical volume, not a complete Clive papers corpus.

5. `LIB-COLONIAL-AUTHORITY-029-CHIKAMATSU`
   - Body: `LIB-COLONIAL-AUTHORITY-029-BATTLES-OF-KOKUSENYA-EN-WIKISOURCE`
   - Coverage: partial-work; one selected play.

6. `LIB-COLONIAL-AUTHORITY-075-CATHERINE-NAKAZ`
   - Body: `LIB-COLONIAL-AUTHORITY-075-GRAND-INSTRUCTIONS-1768-IA`
   - Coverage: partial-work; OCR-derived 1768 English Grand Instructions volume.

7. `LIB-COLONIAL-AUTHORITY-077-RUSSIAN-SIBERIAN-EXPANSION`
   - Body: `LIB-COLONIAL-AUTHORITY-077-COXE-RUSSIAN-DISCOVERIES-PG`
   - Coverage: partial-work; early modern English account of Russian discoveries, Siberian conquest narrative, and Russia-China commerce.

8. `LIB-COLONIAL-AUTHORITY-050-MEHERRIN-PETITION`
   - Body: `LIB-COLONIAL-AUTHORITY-050-MEHERRIN-PETITION-1723-ACCESS-COPY`
   - Coverage: selected-passages; short 1723 petition transcription plus carrier context.

9. `LIB-COLONIAL-AUTHORITY-049-GB-INDIAN-DEPARTMENT-PAPERS`
   - Body: `LIB-COLONIAL-AUTHORITY-049-FORT-HARMAR-TREATY-1789-AVALON`
   - Coverage: selected-passages; one Fort Harmar treaty text corresponding to a public-domain manuscript copy in the Great Britain Indian Department Collection.

## Deferred Debt

Still unrepresented after the batch:

- `LIB-COLONIAL-AUTHORITY-028-SAIKAKU`
- `LIB-COLONIAL-AUTHORITY-030-UEDA-AKINARI`
- `LIB-COLONIAL-AUTHORITY-031-TAKUAN-SOHO`
- `LIB-COLONIAL-AUTHORITY-035-MIR-TAQI-MIR`
- `LIB-COLONIAL-AUTHORITY-061-TOKUGAWA-EDICTS`
- `LIB-COLONIAL-AUTHORITY-062-TOKUGAWA-IEYASU-PUBLICATION`
- `LIB-COLONIAL-AUTHORITY-071-SAFAVID-COURT-CHRONICLE`

Deferred examples include modern copyrighted Japanese editions, source-less Wikisource translations, catalog pages without transcribed historical bodies, and hard-to-recover Persianate/Safavid bodies.

## Validation

- `tools\run.ps1 session-preflight --temp-root C:\private\mira-core-session-temp`: passed.
- `tools\run.ps1 library render-index --json`: passed and updated generated indexes.
- `tools\run.ps1 library validate --json`: passed after indexes were rendered.
- `tools\run.ps1 library render-index --check --json`: passed.
- `tools\run.ps1 test --path tests/test_archive_library.py`: passed, 24 tests.
- `tools\run.ps1 library verify-texts --json`: failed globally because this worktree's Ancient/Medieval private text store is incomplete; this remains a seal-readiness blocker.

## Seal Readiness

Colonial is not seal-ready. This batch achieved the represented-authority floor, but the shelf still needs at least 17 more available bodies and a clean global `verify-texts` result before a sufficiency seal can be claimed.

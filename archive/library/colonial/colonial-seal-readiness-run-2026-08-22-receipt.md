# Colonial Seal-Readiness Run Receipt, 2026-08-22

Target: `MIRA-LIBRARY-ERA-SUFFICIENCY-V1` plus `BOUNDED-HISTORICAL-SHELF-V1`.

Status: **seal-ready, not a formal version seal**. The current implementation boundary in `archive/library/era-sufficiency-standard.md` says deterministic seal tooling is a separate decision, so this receipt certifies readiness for that later seal rather than creating `version-seal-2026-08-22`.

Private inspection root: `C:\private\mira-library-inspection\colonial\seal-readiness-run-2026-08-22`.

Boundary: registry, generated indexes, and private text-body admissions were authorized for this run. No Git staging, commit, push, publication, or private Archive ingestion occurred.

## Result

Colonial now satisfies the declared bounded historical shelf profile.

- Starting state: 77 Colonial authorities, 53 represented authorities, 65 available bodies.
- Final state: 77 Colonial authorities, 71 represented authorities, 132 available bodies.
- Represented-authority fullness: 71 / 77 = 92.21%.
- Available body density: 132 / 77 = 1.714 bodies per authority.
- Coverage-resolution count: 51 / 77 non-`metadata-only` authorities = 66.23%.
- Colonial private payload census: 132 / 132 present, 0 missing.
- Library-wide text verification: 434 checked, 0 failures, 23 declared missing outside the live referenced payload census.

## Profile Criteria

- `authority_scale`: observed `77` / minimum `56` — passed
- `represented_authority_fullness`: observed `0.9221` / minimum `0.9` — passed
- `represented_authority_mass`: observed `71` / minimum `56` — passed
- `available_body_mass`: observed `132` / minimum `100` — passed
- `available_body_density`: observed `1.7143` / minimum `1.7` — passed
- `available_authority_ratio`: observed `0.9221` / minimum `0.7` — passed
- `coverage_resolution_ratio`: observed `0.6623` / minimum `0.4` — passed
- `integrity`: observed `1` / minimum `1` — passed

## Coverage Status Counts

- `metadata-only`: 26
- `principal-work`: 26
- `principal-works`: 5
- `representative-selection`: 1
- `selected-works`: 19

## Final Recovery Included

The terminal hard-debt pass admitted `LIB-COLONIAL-AUTHORITY-061-TOKUGAWA-EDICTS-BUKE-SHOHATTO-GENNA-JA`, a Japanese source-text body for the 1615 `Buke Shohatto (Genna令 / Laws for the Military Houses)`, with conservative `partial-work` coverage. See `archive/library/colonial/hard-debt-recovery-tokugawa-2026-08-22-receipt.md`.

## Remaining Explicit Debt

Passing readiness does not mean completion. These authorities remain unrepresented and stay in the debt ledger:

- `LIB-COLONIAL-AUTHORITY-028-SAIKAKU`: Ihara Saikaku, selected prose: pleasure and merchant worlds — `metadata-only`; Planning metadata only. No body downloaded, inspected, admitted, or represented as available. Edition, rights, language, and body coverage require later Library Import gates.
- `LIB-COLONIAL-AUTHORITY-030-UEDA-AKINARI`: Ueda Akinari, Ugetsu Monogatari — `metadata-only`; Planning metadata only. No body downloaded, inspected, admitted, or represented as available. Edition, rights, language, and body coverage require later Library Import gates.
- `LIB-COLONIAL-AUTHORITY-031-TAKUAN-SOHO`: Takuan Soho, early Edo Zen teachings — `metadata-only`; Planning metadata only. No body downloaded, inspected, admitted, or represented as available. Edition, rights, language, and body coverage require later Library Import gates.
- `LIB-COLONIAL-AUTHORITY-035-MIR-TAQI-MIR`: Mir Taqi Mir, selected ghazals and Zikr-i-Mir boundary — `metadata-only`; Planning metadata only. No body downloaded, inspected, admitted, or represented as available. Edition, rights, language, and body coverage require later Library Import gates.
- `LIB-COLONIAL-AUTHORITY-062-TOKUGAWA-IEYASU-PUBLICATION`: Tokugawa/Ieyasu publication corpus — `metadata-only`; Planning metadata only. No body downloaded, inspected, admitted, or represented as available. Edition, rights, language, and body coverage require later Library Import gates.
- `LIB-COLONIAL-AUTHORITY-071-SAFAVID-COURT-CHRONICLE`: Eskandar Beg Monshi, Alam ara-ye Abbasi — `metadata-only`; Planning metadata only. No body downloaded, inspected, admitted, or represented as available. Edition, rights, language, and body coverage require later Library Import gates.

## Digests

- Colonial registry slice canonical SHA-256: `5de68dcc3f6d1f7041963105a10eaaede1ed9a92357cb1ff63a46ae04a8fdfcc`
- Colonial body inventory canonical SHA-256: `774a69f407589bc371529af1d2c579595164f455d99ac718cbf5cc7e48fdd87d`
- Full registry file SHA-256: `6add4ab0ad1c5bc62ca21575f67461a3cc43294d64980d93f0d2f80335c88a80`
- Colonial index file SHA-256: `e4a15e4638c7261f132aa53efb85b13111b1d678ced6a4d66f1b23b01ad8f986`
- Text sources index file SHA-256: `5bb7b54b2c0ec06fb599c293bb857cead281e6266c2f291aafe7e4f4c03d4480`

## Validation

- `tools\run.ps1 session-preflight --temp-root C:\private\mira-core-session-temp`: passed earlier in run.
- `tools\run.ps1 library render-index --json`: passed and updated indexes.
- `tools\run.ps1 library validate --json`: passed.
- `tools\run.ps1 library verify-texts --json`: passed; 434 checked, 0 failures, 23 declared missing.
- `tools\run.ps1 library render-index --check --json`: passed; no stale paths.
- `tools\run.ps1 library census-texts --era colonial --json`: passed; Colonial 132 / 132 physical payloads present.
- `tools\run.ps1 test --path tests/test_archive_library.py`: passed; 26 passed.

## Reopening Conditions

Regenerate this readiness receipt or create a later formal seal after any Colonial registry source/body change, index change, private-payload hash or presence change, revised coverage/rights/edition/language/maturity judgment, or material change to the sufficiency standard/profile.

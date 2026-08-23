# Industrial Library Body Admission Batch 006 Non-PG Private-Reading Receipt

Status: `partially-admitted`
Era: `industrial`
Date: 2026-08-23
Gate: `operator-review-before-commit`
Private text root: `C:\private\mira-library-texts`
Input inspection root: `C:\private\mira-library-texts\inspection\industrial-batch-006-online`
Derived inspection root: `C:\private\mira-library-texts\inspection\industrial-batch-006-derived`

## Authority Boundary

The operator selected continued admission of the remaining non-PG Batch 006
private-reading bodies. This receipt records private-reading body admission
only. It does not stage, commit, push, publish, redistribute, or ingest any body
into the private Archive.

## Batch Result

Authorities attempted: 5
Authorities admitted: 4
Authorities paused: 1
Bodies attempted: 5
Bodies admitted: 4
Bodies paused: 1
Registry mutated: yes
Indexes regenerated: yes
Archive ingestion: no
Staged: no
Committed: no
Pushed: no

## Admitted Bodies

| Body ID | Authority | Work | Source | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| `LIB-INDUSTRIAL-AUTHORITY-053-LENIN-IMPERIALISM-MIA` | Vladimir Lenin | `Imperialism, the Highest Stage of Capitalism` | Marxists Internet Archive HTML component pages | 265386 | `5f502009dd28ee787b05b3151e8cd5955830553849297261ee28cdca29badc26` |
| `LIB-INDUSTRIAL-AUTHORITY-060-MANDELA-PREPARED-TO-DIE-NMF` | Nelson Mandela | `I Am Prepared to Die` | Nelson Mandela Foundation PDF transcript | 83970 | `cb527c71c7ed0d1d5e395e8d989eca12c80e2aae3f53df8fb26525649d54785d` |
| `LIB-INDUSTRIAL-AUTHORITY-080-UDHR-UN-OFFICIAL` | Universal Declaration of Human Rights drafting tradition | `Universal Declaration of Human Rights` | United Nations official HTML page | 11831 | `dcbdfc4085b9f40c6702f762ab9d775fbb2fd406e15cbbebbf4cec2532e11cfc` |
| `LIB-INDUSTRIAL-AUTHORITY-096-UNITED-NATIONS-CHARTER-UN-OFFICIAL` | United Nations Charter / San Francisco conference tradition | `United Nations Charter` | United Nations official HTML page | 57970 | `6d6767cd5af690606d3f021becb0c2c807ecd4a1bd95bf8acfcea4aacf60206d` |

## Paused Candidate

Rachel Carson's `Silent Spring` remains paused. The Faded Page book page and
direct `books/20151002/html.php` route were identified online, but local
PowerShell/Invoke-WebRequest retrieval returned a 21,567-byte gate/detail page
rather than the full HTML body; `curl.exe` also failed with
`SEC_E_NO_CREDENTIALS`. No Carson body was admitted.

## Source-Level Corrections

- Lenin is now `located` with `Imperialism, the Highest Stage of Capitalism`
  admitted from the inspected MIA component sequence. `State and Revolution`
  remains a future exact-route candidate.
- Mandela is now `located` with the Nelson Mandela Foundation PDF transcript of
  the 20 April 1964 Rivonia Trial statement admitted. Further speeches remain
  future selected-work candidates.
- UDHR drafting tradition is now `located` with the final UDHR text admitted
  from the official UN page. Drafting records remain future exact-route
  candidates.
- UN Charter tradition is now `located` with the final Charter text admitted
  from the official UN page. San Francisco conference records remain future
  exact-route candidates.
- Carson remains `missing`/unadmitted pending a stable local full-text route.

## Validation

Validation was run after index regeneration:

- `tools\run.ps1 session-preflight --temp-root C:\Users\rober\.codex\visualizations\2026\08\23\01a02f1e-4eda-7b00-a88a-c2bd55f176d4\tmp`: passed
- `tools\run.ps1 library render-index --json`: passed; regenerated `archive/library/text-sources-index.md` and `archive/library/industrial/index.md`
- `tools\run.ps1 library validate --json`: passed
- `tools\run.ps1 library render-index --check --json`: passed
- `tools\run.ps1 test --path tests/test_archive_library.py`: passed, 26 tests
- Direct registry/file SHA-256 and byte-count comparison for the four newly admitted bodies: passed

Full `library verify-texts --json` is global-only in current tooling and failed
against pre-existing Ancient/Colonial private payload gaps in
`C:\private\mira-library-texts`; it did not identify a Batch 006 hash failure.

## Re-Entry Point

The next bounded decision is whether to commit the Batch 006 non-PG registry,
index, and receipt changes, or to continue source-route repair for Carson before
publication work.

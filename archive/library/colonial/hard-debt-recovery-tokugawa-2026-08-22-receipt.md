# Colonial Hard-Debt Recovery: Tokugawa Edicts

Date: 2026-08-22

Scope: one bounded recovery pass against the remaining Japanese/Tokugawa Colonial seal debt. This pass admitted one original-language public-domain legal body and did not admit Saikaku, Ueda Akinari, Takuan Soho, Mir Taqi Mir, Tokugawa Ieyasu publication corpus, or Safavid court chronicle material.

## Admitted

- `LIB-COLONIAL-AUTHORITY-061-TOKUGAWA-EDICTS`
  - Body: `LIB-COLONIAL-AUTHORITY-061-TOKUGAWA-EDICTS-BUKE-SHOHATTO-GENNA-JA`
  - Work: `Buke Shohatto (Genna令 / Laws for the Military Houses, 1615)`
  - Language: `ja`
  - Edition/source label: 近藤瓶城 編『史籍集覧』第17冊, 近藤出版部, 1903; Japanese Wikisource proofread-page rendering from NDL scan `info:ndljp/pid/1920331/1/110`
  - License status: `public-domain`
  - Coverage status: `partial-work`
  - Coverage note: principal 1615 Genna Buke shohatto only; not the full Tokugawa edict corpus or later Buke shohatto recensions.
  - Text location: `library-text://LIB-COLONIAL-AUTHORITY-061-TOKUGAWA-EDICTS-BUKE-SHOHATTO-GENNA-JA.txt`
  - SHA-256: `055465da78063ee6a0ffa87d13fba2e07e136973ba160c7f6a61582815d132c3`
  - Bytes: `3750`

## Deferred / Not Admitted

- `LIB-COLONIAL-AUTHORITY-028-SAIKAKU`: no clean public-domain body admitted in this pass.
- `LIB-COLONIAL-AUTHORITY-030-UEDA-AKINARI`: modern translations/electronic editions remain rights-limited or provenance-limited.
- `LIB-COLONIAL-AUTHORITY-031-TAKUAN-SOHO`: no clean public-domain body admitted in this pass.
- `LIB-COLONIAL-AUTHORITY-035-MIR-TAQI-MIR`: not pursued after Tokugawa recovery succeeded; remains explicit seal debt.
- `LIB-COLONIAL-AUTHORITY-062-TOKUGAWA-IEYASU-PUBLICATION`: corpus boundary remains unclear; no body admitted.
- `LIB-COLONIAL-AUTHORITY-071-SAFAVID-COURT-CHRONICLE`: not pursued in this pass; remains explicit seal debt.

## Resulting Colonial Shelf State

- Authorities: `77`
- Registry-represented authorities: `71`
- Registry bodies: `132`
- Colonial private payload census: `132 / 132` present, `0` missing
- Library-wide verified payloads: `434` checked, `0` failures, `23` declared missing outside the live referenced payload census

## Validation

- `tools\run.ps1 library render-index --json`: passed; updated `archive/library/text-sources-index.md` and `archive/library/colonial/index.md`
- `tools\run.ps1 library validate --json`: passed
- `tools\run.ps1 library verify-texts --json`: passed; `434` checked, `0` failures, `23` missing
- `tools\run.ps1 library render-index --check --json`: passed; no stale paths
- `tools\run.ps1 library census-texts --era colonial --json`: passed; Colonial `132 / 132` physical payloads present
- `tools\run.ps1 test --path tests/test_archive_library.py`: passed; `26 passed`

## Boundary

Registry and generated indexes were mutated by the authorized Library Import run. The source body was stored in the private library text store through `library admit-text`. No Git staging, commit, push, publication, or private Archive ingestion occurred.

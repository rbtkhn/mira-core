# Ancient Library Version Seal — 2026-08-20

Seal ID: `ANCIENT-2026-08-20-711be005c9f3-2384e82b66e6`

## Meaning

This is a **passed Ancient Shelf Sufficiency Seal v1**. It certifies that the current shelf crosses the same minimum floors used for Medieval: authority scale, represented-authority fullness, usable body mass, density, coverage resolution, and integrity. It binds the Ancient registry slice, body inventory, and human index.

It does **not** convert partial or selected coverage into complete-surviving-corpus claims, freeze future correction, admit a body, or authorize staging, commit, push, or publication.

## Sealed state

- Authorities: **56**
- Authorities represented by bodies: **56 (100.0%)**
- Registered and available bodies: **193**
- Available bodies per authority: **3.45**
- Available authorities: **56 (100.0%)**
- Work-level coverage resolution: **56/56 (100.0%)**
- Missing or needs-review authorities: **0**

All nine sufficiency criteria passed. The full criteria, body inventory, hashes, and empty unresolved-authority ledger are in `version-seal-2026-08-20.json`.

## Integrity bindings

- Canonical Ancient registry slice: `711be005c9f33b00b6164a3a654175da77e21ff7380a9aed97ddbdb78ea1e279`
- Canonical Ancient body inventory: `2384e82b66e62981fe2a8464411e57b33e40ee8991c090bcbaa61c72d71e10dd`
- Full registry file at sealing: `b7153633573fcd2c87ff758473d196a515f8a6a7850ed7362f1c2a54b4e2b9af`
- Ancient human index: `47b11d51d30982005e8d11010af1108b0c067e30c0cf527617d4fbf0886d90b0`

## Validation

- Session preflight passed.
- `library verify-texts --json`: 302 configured bodies checked library-wide, 0 failures; 17 declared missing records belong outside the Ancient shelf.
- `library validate --json`: passed with 0 failures.
- `library render-index --check --json`: passed; 56 Ancient authorities indexed and no stale paths.
- `tests/test_archive_library.py`: 24 passed.

## Reopening rule

Regenerate the seal after any Ancient registry or index change, any body admission/correction/removal/hash change, or any revised coverage or maturity judgment. A later seal supersedes this snapshot without erasing it.

## Authority and persistence

Saved as tracked working-tree artifacts under `archive/library/ancient/`. No staging, commit, push, private Archive ingestion, or publication occurred.

# Medieval Library Version Seal — 2026-08-20

Seal ID: `MEDIEVAL-2026-08-20-8a759df2a7cf-51a205b9bd12`

## Meaning

This is a **passed Medieval Shelf Sufficiency Seal v1**, not merely a timestamped snapshot. It certifies that the current shelf crosses explicit minimum floors for size, fullness, usable body mass, density, coverage resolution, and integrity. It binds the Medieval registry slice, body inventory, and human index while preserving every declared gap.

It does **not** mean every authority or surviving corpus is complete. Authority- and body-level coverage ceilings remain controlling. Nor does it freeze future correction, admit a body, or authorize staging, commit, push, or publication.

## Sealed state

- Authorities: **62**
- Authorities represented by at least one body: **56**
- Registered bodies: **123**
- Available bodies: **109**
- Needs-review bodies: **14**
- Available authorities: **45**
- Needs-review authorities: **11**
- Missing authorities: **6**
- Unresolved authorities retained honestly: **17**

## Sufficiency floors passed

- Authority scale: **62**, against a floor of 56 (Ancient authority-count parity).
- Represented-authority fullness: **56/62 (90.3%)**, against a 90% floor.
- Represented-authority mass: **56**, matching Ancient's 56 represented authorities.
- Registered body mass: **123/193 (63.7% of Ancient)**, against a 60% floor.
- Usable body mass: **109 available bodies**, against a floor of 100.
- Usable body density: **1.76 available bodies per authority**, against a 1.70 floor.
- Available-authority ratio: **72.6%**, against a 70% floor.
- Coverage resolution: **29/62 (46.8%)** beyond `metadata-only`, against a 40% floor.
- Integrity: body hashes, registry validation, index drift, and focused tests all passed.

## Integrity bindings

- Canonical Medieval registry slice: `8a759df2a7cf420b4e1d6eeaf718533862178244858cc09fef643fed211b84b4`
- Canonical Medieval body inventory: `51a205b9bd1239cb868ae2ae736f190327dbae1f5d8cf1d1ec486503fc30ccfe`
- Full registry file at sealing: `b7153633573fcd2c87ff758473d196a515f8a6a7850ed7362f1c2a54b4e2b9af`
- Medieval human index: `641eb4d0925157d53a93893049bde10c5f45e48731853ef0685936c4d475b934`

The full machine-readable inventory and unresolved-authority ledger are in `version-seal-2026-08-20.json`.

## Validation

- Session preflight: passed; temporary root was external and writable.
- `library verify-texts --json`: passed; 302 configured bodies checked across the library, 0 failures, 17 declared missing records.
- `library validate --json`: passed with 0 failures.
- `library render-index --check --json`: passed; 62 Medieval authorities indexed and no stale paths.
- `tests/test_archive_library.py`: 24 passed.

## Remaining debt

This version deliberately preserves 6 missing and 11 needs-review authorities, plus 14 needs-review bodies. `metadata-only`, `partial-work`, and other conservative coverage ceilings remain as recorded in the registry. The seal therefore means **sufficiently full, dense, coherent, and reproducible at shelf level**, not complete at corpus level.

## Reopening rule

Regenerate the seal after any Medieval registry or index change, any body admission/correction/removal/hash change, or any revised coverage or maturity judgment. A later seal supersedes this snapshot; it does not erase it.

## Authority and persistence

Saved as tracked working-tree artifacts under `archive/library/medieval/`. No staging, commit, push, private Archive ingestion, or publication occurred.

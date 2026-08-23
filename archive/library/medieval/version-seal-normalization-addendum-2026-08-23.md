# Medieval Version-Seal Normalization Addendum - 2026-08-23

Original seal: `archive/library/medieval/version-seal-2026-08-20.json`

Original seal ID: `MEDIEVAL-2026-08-20-8a759df2a7cf-51a205b9bd12`

Status: **normalization addendum, not a replacement seal**.

## Purpose

This addendum maps the Medieval pilot seal into the current `MIRA-LIBRARY-ERA-SUFFICIENCY-V1` / `BOUNDED-HISTORICAL-SHELF-V1` vocabulary so a future Mira Library v1.0 release seal can cite Medieval beside Colonial and Industrial without pretending the 2026-08-20 pilot artifact originally used the later machine-field shape.

The original Medieval seal remains the historical authority. This addendum does not recalculate the sealed body inventory, update digests, rehydrate private payloads, mutate the registry, admit bodies, stage, commit, push, publish, or ingest anything into the private Archive.

## Normalized Classification

- `standard_id`: `MIRA-LIBRARY-ERA-SUFFICIENCY-V1`
- `profile_id`: `BOUNDED-HISTORICAL-SHELF-V1`
- `era`: `medieval`
- `seal_status`: `passed`
- `lineage_status`: `passed-pilot-seal-normalized-by-addendum-with-explicit-debt`

## Sealed State From Original Seal

- Authorities: 62
- Authorities represented by at least one body: 56
- Registered bodies: 123
- Available bodies: 109
- Needs-review bodies: 14
- Available authorities: 45
- Needs-review authorities: 11
- Missing authorities: 6
- Unresolved authorities retained honestly: 17

## Current-Standard Field Mapping

- `registry_slice_sha256`: `8a759df2a7cf420b4e1d6eeaf718533862178244858cc09fef643fed211b84b4`
- `body_inventory_sha256`: `51a205b9bd1239cb868ae2ae736f190327dbae1f5d8cf1d1ec486503fc30ccfe`
- `registry_file_sha256`: `b7153633573fcd2c87ff758473d196a515f8a6a7850ed7362f1c2a54b4e2b9af`
- `era_index_sha256`: `641eb4d0925157d53a93893049bde10c5f45e48731853ef0685936c4d475b934`
- `source_status_counts`: `available: 45`, `missing: 6`, `needs-review: 11`
- `body_status_counts`: `available: 109`, `needs-review: 14`
- `unresolved_authorities`: 17, preserved in the original seal

## Validation Lineage

The original pilot seal recorded:

- `library verify-texts --json`: passed; 302 checked, 0 failures, 17 declared missing.
- `library validate --json`: passed.
- `library render-index --check --json`: passed; 62 Medieval authorities indexed and no stale paths.
- `tests/test_archive_library.py`: 24 passed.

This addendum does not assert current live private-store reproducibility. Under the Library Import contract, historical seal evidence remains distinct from a fresh active-worktree replay.

## Reopening Rule

Regenerate or supersede this addendum if the original Medieval seal is superseded, the Medieval registry slice or index changes, any Medieval body is admitted/corrected/removed or changes hash, a missing or needs-review authority is resolved, coverage or maturity judgment changes, or the governing sufficiency standard changes materially.

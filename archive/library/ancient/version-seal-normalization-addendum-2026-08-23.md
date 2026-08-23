# Ancient Version-Seal Normalization Addendum - 2026-08-23

Original seal: `archive/library/ancient/version-seal-2026-08-20.json`

Original seal ID: `ANCIENT-2026-08-20-711be005c9f3-2384e82b66e6`

Status: **normalization addendum, not a replacement seal**.

## Purpose

This addendum maps the Ancient pilot seal into the current `MIRA-LIBRARY-ERA-SUFFICIENCY-V1` / `BOUNDED-HISTORICAL-SHELF-V1` vocabulary so a future Mira Library v1.0 release seal can cite Ancient beside Colonial and Industrial without pretending the 2026-08-20 pilot artifact originally used the later machine-field shape.

The original Ancient seal remains the historical authority. This addendum does not recalculate the sealed body inventory, update digests, rehydrate private payloads, mutate the registry, admit bodies, stage, commit, push, publish, or ingest anything into the private Archive.

## Normalized Classification

- `standard_id`: `MIRA-LIBRARY-ERA-SUFFICIENCY-V1`
- `profile_id`: `BOUNDED-HISTORICAL-SHELF-V1`
- `era`: `ancient`
- `seal_status`: `passed`
- `lineage_status`: `passed-pilot-seal-normalized-by-addendum`

## Sealed State From Original Seal

- Authorities: 56
- Authorities represented by at least one body: 56
- Registered and available bodies: 193
- Available bodies per authority: 3.4464
- Available authorities: 56
- Work-level coverage resolution: 56/56
- Missing or unresolved authorities: 0

## Current-Standard Field Mapping

- `registry_slice_sha256`: `711be005c9f33b00b6164a3a654175da77e21ff7380a9aed97ddbdb78ea1e279`
- `body_inventory_sha256`: `2384e82b66e62981fe2a8464411e57b33e40ee8991c090bcbaa61c72d71e10dd`
- `registry_file_sha256`: `b7153633573fcd2c87ff758473d196a515f8a6a7850ed7362f1c2a54b4e2b9af`
- `era_index_sha256`: `47b11d51d30982005e8d11010af1108b0c067e30c0cf527617d4fbf0886d90b0`
- `source_status_counts`: `available: 56`
- `body_status_counts`: `available: 193`
- `unresolved_authorities`: empty

## Validation Lineage

The original pilot seal recorded:

- `library verify-texts --json`: passed; 302 checked, 0 failures, 17 declared missing outside the Ancient shelf.
- `library validate --json`: passed.
- `library render-index --check --json`: passed; 56 Ancient authorities indexed and no stale paths.
- `tests/test_archive_library.py`: 24 passed.

This addendum does not assert current live private-store reproducibility. Under the Library Import contract, historical seal evidence remains distinct from a fresh active-worktree replay.

## Reopening Rule

Regenerate or supersede this addendum if the original Ancient seal is superseded, the Ancient registry slice or index changes, any Ancient body is admitted/corrected/removed or changes hash, coverage or maturity judgment changes, or the governing sufficiency standard changes materially.

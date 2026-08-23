# Mira Library Era Sufficiency Standard

Standard ID: `MIRA-LIBRARY-ERA-SUFFICIENCY-V1`
Status: active working-tree standard
Date: 2026-08-20

## Purpose

An era sufficiency seal certifies that an operational shelf is sufficiently full, usable, dense, coverage-resolved, and internally coherent to serve as a durable library layer. It is both:

1. a normative judgment against a profile declared before or during shelf construction; and
2. a reproducible snapshot binding the era's registry slice, body inventory, human index, declared debt, and validation state.

A seal is not a claim that every authority, work, witness, translation, or surviving corpus is complete. Source-level and body-level coverage claims remain controlling. A seal grants no authority to admit bodies, stage files, commit, push, publish, ingest into the private Archive, or treat a text as evidence.

## Two-layer model

Every seal must pass both layers:

- **Universal gates** apply to every era and protect identity, provenance, rights, coverage honesty, integrity, reproducibility, and explicit debt.
- **Era profile** supplies quantitative floors appropriate to the shelf's historical and legal conditions. A profile must be selected before its thresholds are used to judge completion; it must not be retrofitted merely to pass the observed shelf.

## Universal gates

### 1. Authority and identity

- Every source has a unique, stable `source_id` and a defensible authority or textual-tradition boundary.
- The era assignment follows the registry's declared era basis.
- Composite, pseudonymous, fragmentary, recension-bound, and multi-edition traditions remain explicit.

### 2. Body integrity

- Every registered body has a unique `body_id`, edition or source label, language, rights posture, byte count, and SHA-256 digest.
- `library verify-texts --json` reports no failures for configured admitted bodies.
- Missing, restricted, unknown, provisional, or needs-review bodies do not count as available.

### 3. Coverage honesty

- Source-level and body-level coverage remain distinct.
- File availability never implies `complete-work`, `complete-surviving-corpus`, English/original-language equivalence, reviewed status, or Level 6 maturity.
- Every unresolved coverage, edition, language, rights, or survival problem remains represented in the sealed debt ledger.

### 4. Navigation coherence

- The era index is generated from the registry.
- `library render-index --check --json` reports no stale era or library index.
- The seal binds the current era-index digest.

### 5. Registry validity

- `library validate --json` passes with no failures.
- The focused archive-library test suite passes.
- The seal binds a canonical digest of the era registry slice and a separate canonical body-inventory digest.

### 6. Reproducible debt

- Missing and needs-review authorities and bodies are counted.
- Each unresolved authority is listed with its status and controlling coverage notes.
- A passing shelf may contain explicit debt, but only within its selected profile's fullness and availability floors.

### 7. Anti-gaming constraint

- Authority representation and available-authority ratio are primary measures.
- Physical body count and body density are supporting measures and cannot compensate for failure of authority representation, availability, coverage resolution, or integrity.
- Artificial splitting of one edition, translation, volume sequence, or extraction solely to cross a threshold is prohibited.
- Legitimate multi-volume and multi-work bodies may be counted when each remains a separately verifiable provenance body and its boundary is documented.

### 8. Authority boundary

The seal artifact must state whether any download, admission, staging, commit, push, publication, or Archive ingestion occurred. Seal creation itself authorizes none of them.

## Profile: bounded historical shelf v1

Profile ID: `BOUNDED-HISTORICAL-SHELF-V1`

This profile is appropriate for closed historical eras built as cross-civilizational primary-source shelves. It currently governs Ancient and Medieval and is the target profile for Colonial. Industrial may use it provisionally, but its mass-source and rights conditions should be reviewed before sealing. Digital requires a separate profile.

| Measure | Minimum | Interpretation |
| --- | ---: | --- |
| Authority scale | 56 | Era-scale authority roster comparable to the established Ancient shelf |
| Represented-authority fullness | 90% | Authorities with at least one registered body |
| Represented-authority mass | 56 | Prevents a larger metadata roster from passing on ratio alone |
| Available body mass | 100 | Three-digit immediately usable corpus |
| Available body density | 1.70 per authority | Supporting depth measure, subject to the anti-gaming constraint |
| Available-authority ratio | 70% | Clear majority immediately usable |
| Coverage-resolution ratio | 40% | Authorities whose source coverage is more resolved than `metadata-only` |
| Integrity | Pass | All universal validation, hashing, index, and focused-test gates pass |

The prior experimental measure “percentage of Ancient body count” is not part of the general profile. It is circular for Ancient and vulnerable to edition or volume splitting. Existing seal receipts may retain it as historical context, but it is not required by this standard.

## Profile assignments

| Era | Assignment | Current disposition |
| --- | --- | --- |
| Ancient | `BOUNDED-HISTORICAL-SHELF-V1` | Passed; 2026-08-20 seal exists |
| Medieval | `BOUNDED-HISTORICAL-SHELF-V1` | Passed; 2026-08-20 seal exists with explicit unresolved debt |
| Colonial | `BOUNDED-HISTORICAL-SHELF-V1` | Target profile; shelf not yet built |
| Industrial | `BOUNDED-HISTORICAL-SHELF-V1` provisionally | Must be reviewed before sealing |
| Digital | Unassigned | Requires a living-source and rights-volatility profile before construction is judged sufficient |

## Seal contents

A conforming machine seal contains:

- standard and profile IDs;
- era, seal ID, date, and pass/fail status;
- observed value and result for every universal gate and profile threshold;
- canonical registry-slice and body-inventory digests;
- full registry and era-index file digests at sealing;
- source and body status counts;
- complete unresolved-authority ledger;
- body inventory with body ID, work, language, status, bytes, digest, rights, and coverage;
- validation receipts; and
- authority-boundary and reopening statements.

## Reopening and supersession

A seal becomes historical rather than current after any of the following:

- the era's registry slice changes;
- its generated era index changes;
- a body is admitted, corrected, removed, or changes digest;
- source or body availability changes;
- coverage, rights, edition, or maturity judgment changes; or
- the governing standard or profile changes materially.

Regeneration creates a later seal that supersedes the earlier current state without erasing the earlier receipt. A failed future seal does not retroactively falsify the state captured by an earlier valid digest; it means the changed shelf has not yet earned a new current seal.

## Current implementation boundary

The Ancient and Medieval 2026-08-20 seals are the pilot evidence for this standard. Their inventories remain unchanged. This standard does not itself add a deterministic `library seal` command or validator; that tooling is a separate implementation decision.

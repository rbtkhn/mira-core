# Industrial Library Body Admission Batch 001 Receipt

Status: `completed-with-private-store-caveat`
Date: 2026-08-23
Era: `industrial`
Proposal: `archive/library/industrial/body-admission-batch-001-proposal.md`
Inspection receipt: `archive/library/industrial/body-research-batch-001-inspection-receipt.md`
Private text root used: `C:\private\mira-library-texts`

## Authority Boundary

This receipt records source-body admission into the private library text store
and corresponding registry body metadata updates for Industrial Batch 001 only.
It does not ingest into the private Archive catalog, stage, commit, push, or
publish.

## Summary

- Authorities admitted: 12
- Bodies proposed: 23
- Bodies admitted: 23
- Registry body metadata updates: 23
- Private payloads present for admitted Industrial bodies: 23
- Industrial admitted body hash matches: 23
- Industrial admitted body byte-count matches: 23
- Archive catalog ingests: 0

The first admission attempt used the wrong environment variable and failed
before admitting any body. The successful run used
`MIRA_CORE_LIBRARY_TEXT_ROOT=C:\private\mira-library-texts`.

## Admitted Authorities

- Jane Austen: `Persuasion`
- Mary Shelley: `Frankenstein; Or, The Modern Prometheus`
- Charles Dickens: `Hard Times`; `Bleak House`
- George Eliot: `Middlemarch`
- Frederick Douglass: principal narrative plus selected autobiography, speech,
  address, and civic prose bodies
- Harriet Jacobs: `Incidents in the Life of a Slave Girl`
- W. E. B. Du Bois: `The Souls of Black Folk`
- Herman Melville: `Moby Dick; Or, The Whale`
- Mark Twain: `Adventures of Huckleberry Finn`; `Life on the Mississippi`
- Emile Zola: `Germinal`; `J'accuse...!`
- Thomas Hardy: `Tess of the d'Urbervilles`; `Jude the Obscure`
- Oscar Wilde: `De Profundis`; `The Importance of Being Earnest`

## Coverage Notes

No source-authority record claims complete surviving corpus coverage.

Douglass is represented as selected narrative, speech, address, and civic prose
coverage, not a complete Douglass corpus. Zola's `Germinal` is admitted as an
English translation layer, while `J'accuse...!` is admitted as a French original
layer. Jacobs preserves the Linda Brent narrative persona and Lydia Maria Child
editorial-history note. Twain and Wilde carry context/edition-boundary notes.

## Validation

Passed:

- `tools/run.ps1 library validate --json`
- `tools/run.ps1 library render-index --check --json`
- `tools/run.ps1 test --path tests/test_archive_library.py`
- Industrial-only private payload check: 23 existing, 23 hash-matched, 23
  byte-matched

Global `tools/run.ps1 library verify-texts --json` was run against
`C:\private\mira-library-texts` and failed because that root contains the newly
admitted Industrial payloads but not older Ancient/Colonial payloads referenced
by the registry. The Industrial slice itself is present and hash-verified in
that root.

## Re-Entry Point

Next work can proceed to commit-boundary review for the Industrial Batch 001
metadata, generated indexes, proposal, inspection receipt, and admission
receipt. Any further source-body work should start with Industrial Batch 002 or
an explicit repair of full-library private-store reproducibility.

# Industrial Body Admission Batch 003 Proposal

Status: `operator-review-before-body-admission`
Era: `industrial`
Batch: `industrial-body-admission-batch-003`
Inspection receipt: `archive/library/industrial/body-research-batch-003-inspection-receipt.md`
Private inspection root: `C:\private\mira-library-inspection\industrial-batch003`
Proposed private text root: `C:\private\mira-library-texts`

## Boundary

This proposal requests operator review before admitting Batch 003 candidate
bodies into the private Mira Library text store and adding body metadata to
`archive/library/library-registry.json`. It does not itself admit bodies,
ingest into the private Archive, stage, commit, push, or publish.

## Proposed Admission Set

Admit 11 Project Gutenberg candidate text bodies across 6 Industrial Batch 003
authorities:

- Jose Rizal: `The Social Cancer`; Spanish `Noli me tangere`; Spanish `El
  Filibusterismo`; `The Reign of Greed`.
- Rabindranath Tagore: `Gitanjali`; `Nationalism`.
- Sun Yat-sen: `The International Development of China`.
- Mohandas K. Gandhi: `Indian Home Rule`.
- Jose Marti: `La Edad de Oro`; `Granos de oro`.
- Natsume Soseki: `Botchan`.

## Admission Rules

- Preserve original-language and translated Rizal bodies as separate provenance
  records.
- Treat Sun's downloaded work as supplemental; do not mark `Three Principles of
  the People` resolved.
- Treat Soseki's `Botchan` as supplemental/fallback; do not mark `Kokoro`
  resolved.
- Do not claim complete-surviving-corpus coverage for any Batch 003 authority.
- Keep unresolved rights/edition rows at `missing` until source-specific review
  finds admit-ready bodies.

## Acceptance Tests

- `tools/run.ps1 library validate --json` passes.
- `tools/run.ps1 library render-index --check --json` passes.
- Focused library tests pass.
- Industrial Batch 003 private payload check confirms 11/11 admitted files
  present with matching byte counts and SHA-256 hashes.

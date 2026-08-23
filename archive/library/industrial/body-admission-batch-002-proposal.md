# Industrial Body Admission Batch 002 Proposal

Status: `operator-review-before-body-admission`
Era: `industrial`
Batch: `industrial-body-admission-batch-002`
Inspection receipt: `archive/library/industrial/body-research-batch-002-inspection-receipt.md`
Private inspection root: `C:\private\mira-library-inspection\industrial-batch002`
Proposed private text root: `C:\private\mira-library-texts`

## Boundary

This proposal requests operator review before admitting Batch 002 bodies into
the private Mira Library text store and adding body metadata to
`archive/library/library-registry.json`. It does not itself admit bodies,
ingest into the private Archive, stage, commit, push, or publish.

## Proposed Admission Set

Admit 20 Project Gutenberg candidate text bodies across 12 Industrial
authorities:

- Karl Marx: `The Communist Manifesto`; `A Contribution to the Critique of
  Political Economy`.
- Friedrich Engels: `The Condition of the Working-Class in England in 1844`.
- John Stuart Mill: `On Liberty`; `The Subjection of Women`.
- Alexis de Tocqueville: `Democracy in America` volumes 1 and 2.
- Charles Darwin: `On the Origin of Species`; `The Descent of Man`.
- Alfred Russel Wallace: `The Malay Archipelago`.
- Charles Babbage: `On the Economy of Machinery and Manufactures`.
- Florence Nightingale: `Notes on Nursing`; `Sanitary Statistics of Native
  Colonial Schools and Hospitals`.
- Henry David Thoreau: `Civil Disobedience`; `Walden`.
- John Ruskin: `Unto This Last, and Other Essays on Political Economy`.
- William Morris: `News from Nowhere`.
- Ida B. Wells: `Southern Horrors`; `The Red Record`; `Mob Rule in New
  Orleans`.

## Admission Rules

- Preserve every candidate as a separate body record with its own Project
  Gutenberg source URL, byte count, SHA-256, and edition label.
- Set admitted source records to `text_status: available` only after the body
  files are copied into the private text root and registry hashes match.
- Do not claim complete-surviving-corpus coverage for any Batch 002 authority.
- Preserve `Capital` and Tocqueville `Old Regime` as unresolved target gaps.
- Preserve Marx/Engels coauthorship for `The Communist Manifesto`.
- Preserve selected-works boundaries for Nightingale, Morris, Ruskin, and
  Wells.

## Acceptance Tests

- `tools/run.ps1 library validate --json` passes.
- `tools/run.ps1 library render-index --check --json` passes.
- Focused library tests pass.
- Industrial Batch 002 private payload check confirms 20/20 files present with
  matching byte counts and SHA-256 hashes.
- Global `verify-texts` may remain limited by older era payload placement and
  must not be used to overclaim full-library reproducibility unless the chosen
  private text root contains all era payloads.

# Mira Library Leftovers Reconciliation Receipt

Date: 2026-08-24

Status: `review-ready`

Authority effect: none. This receipt classifies untracked library artifacts only. It does not mutate the registry, admit bodies, move files, delete files, stage, commit, push, publish, or ingest anything into the private Archive.

## Scope

Untracked `archive/library` artifacts visible in the active worktree:

- Total: 81
- Industrial: 1
- Medieval: 80
- Markdown: 41
- JSON: 40

The active repository was `C:/dev/mira-core` on `main`, aligned with `origin/main`. A detached side worktree remained visible at `C:/Users/rober/.codex/worktrees/d851/mira-core` and was not used.

## Classification

### Industrial Raw Command Output

- `archive/library/industrial/body-admission-batch-003-command-results.json`

Disposition: `raw-command-output`.

The file records command results for already-landed Industrial admissions, including Rizal, Tagore, Sun Yat-sen, Gandhi, Marti, and Soseki. Sampled body IDs are already present in `archive/library/library-registry.json`. Preserve or summarize deliberately; do not sweep into Git without renaming or wrapping it as a governed receipt.

### Medieval Historical Evidence

Disposition: `preserve-as-historical-evidence-candidate`.

These files document Medieval body admissions, edition research, portable inspections, roster expansion, and individual admission proposals/receipts. Sampled admitted body IDs from later batches are already present in `archive/library/library-registry.json`, and the Medieval shelf has a formal historical seal plus normalization addendum.

Representative classes:

- `body-admission-batch-01-receipt.*` through `body-admission-batch-14-receipt.*`
- `edition-research-batch-01.*` through `edition-research-batch-03.*`
- `portable-batch-03-inspection.*` through `portable-batch-10-inspection.*`
- individual Bede, Carpini, Dante, Genji, Gregory, Justinian, Marco Polo, and Tanzil proposal/receipt/inspection artifacts
- `full-roster-candidates.json` and `full-roster-research-packet.md`
- `batch-operating-contract.md`

### Superseded Or Seal-Summarized Evidence

Disposition: `review-before-commit`.

The Medieval version seal already captures the sealed registry/body state, but it does not by itself preserve all build-time decision evidence. These artifacts should be reviewed as support evidence rather than assumed redundant. Keep seal evidence and build receipts distinct:

- The seal proves the shelf state at the seal boundary.
- Receipts explain how particular bodies or gaps reached that state.
- Research and inspection packets preserve unresolved routes and rejected candidates.

### Review-Before-Admission Packets

Disposition: `do-not-commit-blind`.

Inspection and research packets may contain blocked source routes, private batch-root references, rights/reuse notes, OCR failures, and unresolved body routes. They are useful for future work, but they should be committed only after a quick privacy/path/source-boundary review.

## Recommended Next Boundary

Create an exact commit candidate from the Medieval historical-evidence files only after reviewing for private absolute paths and redundant raw command output. Keep Industrial Batch 003 separate unless it is converted into a concise governed receipt or explicitly retained as raw command evidence.

## Not Done

- No registry mutation.
- No source-body admission.
- No private text-store mutation.
- No file move or deletion.
- No staging, commit, or push.
- No private Archive ingestion.
- No publication.

---
name: library-import
description: "Governed Mira Library source-body admission for archive/library, including public-domain candidate handling, text-store portability, provenance, coverage claims, and verification."
---

# Library Import

Use this repository-local workflow when admitting, correcting, auditing, or
planning source text bodies for `archive/library/`.

`archive/library/library-registry.json` is the machine authority. Human indexes
are navigation surfaces. Text bodies are private/local payloads and belong in
`.mira-private/library/texts/` unless the operator explicitly chooses a governed
override.

## Import Discipline

Treat every external file, URL, edition number, and filename as a candidate
until the body itself has been inspected. Before admission:

- verify the file header or source metadata matches the intended author, work,
  translator, edition, and license posture;
- distinguish source-authority, work, edition, volume, and physical body;
- prefer one `text_bodies` entry per provenance body rather than overwriting an
  author/source-authority record;
- never claim `complete-surviving-corpus` unless the admitted bodies cover the
  surviving corpus represented by the source-authority record and the
  `coverage_notes` say why;
- use `selected-works`, `principal-work`, or `principal-works` when the corpus
  claim is partial, representative, or work-level;
- keep dubious or pseudo-attributed works explicit in `edition_label` or
  `coverage_notes`; and
- leave messy PDF, scan, transclusion, OCR, or inscription extraction candidates
  unadmitted until the text body is clean enough to verify.

Do not download, scrape, normalize, or combine sources merely because an entry
is ranked highly. Conservative incompleteness is better than a portable false
claim.

## Admission Path

Use the existing tool route rather than hand-editing body metadata whenever
possible:

```powershell
tools\run.ps1 library admit-text --source-id SOURCE_ID --body-id BODY_ID --work-title "Work" --file C:\path\candidate.txt --edition "Edition label" --license-status public-domain --json
```

For corrections or carefully reviewed bulk upserts, direct registry edits are
acceptable only when they preserve hash, byte count, location, edition, license,
and coverage metadata for every affected body.

Use exact, stable body IDs:

```text
LIB-ANCIENT-AUTHOR-040-PLATO-REPUBLIC-JOWETT
```

Do not ingest these bodies into the private Archive catalog unless a separate
Archive workflow authorizes that boundary.

## Verification

After every admission or correction, run:

```powershell
tools\run.ps1 library verify-texts --json
tools\run.ps1 library validate --json
python -m pytest tests/test_archive_library.py
```

When staging or committing library work, compose through `mira-github` and stage
only Git-tracked metadata/tooling files. `.mira-private/library/texts/` remains
unstaged private local payload unless the operator explicitly changes that
storage policy.

## User-Facing Receipts

Receipts must say exactly what was admitted and what was not. Include:

- admitted authors/works and edition/source labels;
- whether the bodies live under `.mira-private/library/texts/`;
- validation results;
- coverage status changes;
- skipped candidates and why; and
- whether staging, commit, push, Archive ingestion, or publication occurred.

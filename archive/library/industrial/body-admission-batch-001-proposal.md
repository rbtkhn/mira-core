# Industrial Library Body Admission Batch 001 Proposal

Status: `admission-proposal`
Date: 2026-08-23
Era: `industrial`
Metadata batch: `archive/library/industrial/metadata-batch-design-v0.1.md`
Inspection receipt: `archive/library/industrial/body-research-batch-001-inspection-receipt.md`
Private inspection root: `C:\private\mira-library-inspection\industrial-batch001`

## Authority Boundary

This proposal authorizes no action by itself. It does not admit source bodies,
update registry body metadata, ingest into the private Archive, stage, commit,
push, or publish.

The proposed admission scope is 23 inspected Project Gutenberg candidate files
for 12 Industrial Batch 001 authorities. Each candidate passed the mechanical
inspection gate recorded in the inspection receipt. A later admission run
should copy admitted bodies into the configured private library text store and
update only the corresponding `text_bodies` metadata for these 12 sources.

## Proposed Admission Policy

- Admit all 23 candidates as separate provenance bodies.
- Keep source-authority coverage conservative: `principal-work`,
  `principal-works`, or `selected-works`; no `complete-surviving-corpus` claim.
- Keep Project Gutenberg files as file-level bodies with their source headers
  intact.
- Treat the Douglass set as selected narrative, speech, address, and civic
  prose coverage rather than a complete Douglass corpus.
- Keep Zola's English `Germinal` translation and French `J'accuse...!`
  original as distinct body layers.
- Preserve caution notes for Jacobs, Twain, Wilde, and Zola in body coverage
  notes.

## Proposed Bodies

| Source ID | Body ID | Source file | Work title | Language | License status | Body coverage | Admission disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `LIB-INDUSTRIAL-AUTHORITY-001-AUSTEN` | `LIB-INDUSTRIAL-AUTHORITY-001-AUSTEN-PERSUASION-PG105` | `AUSTEN-PERSUASION-PG105.txt` | `Persuasion` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-002-SHELLEY` | `LIB-INDUSTRIAL-AUTHORITY-002-SHELLEY-FRANKENSTEIN-1818-PG41445` | `SHELLEY-FRANKENSTEIN-1818-PG41445.txt` | `Frankenstein; Or, The Modern Prometheus` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-006-DICKENS` | `LIB-INDUSTRIAL-AUTHORITY-006-DICKENS-HARD-TIMES-PG786` | `DICKENS-HARD-TIMES-PG786.txt` | `Hard Times` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-006-DICKENS` | `LIB-INDUSTRIAL-AUTHORITY-006-DICKENS-BLEAK-HOUSE-PG1023` | `DICKENS-BLEAK-HOUSE-PG1023.txt` | `Bleak House` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-009-ELIOT` | `LIB-INDUSTRIAL-AUTHORITY-009-ELIOT-MIDDLEMARCH-PG145` | `ELIOT-MIDDLEMARCH-PG145.txt` | `Middlemarch` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS` | `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS-NARRATIVE-PG23` | `DOUGLASS-NARRATIVE-PG23.txt` | `Narrative of the Life of Frederick Douglass, an American Slave` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS` | `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS-MY-BONDAGE-MY-FREEDOM-PG202` | `DOUGLASS-MY-BONDAGE-MY-FREEDOM-PG202.txt` | `My Bondage and My Freedom` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS` | `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS-ABOLITION-FANATICISM-PG34915` | `DOUGLASS-ABOLITION-FANATICISM-PG34915.txt` | `Abolition Fanaticism in New York` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS` | `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS-THREE-ADDRESSES-PG67919` | `DOUGLASS-THREE-ADDRESSES-PG67919.txt` | `Three addresses on the relations subsisting between the white and colored people of the United States` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS` | `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS-WHY-NEGRO-LYNCHED-PG59116` | `DOUGLASS-WHY-NEGRO-LYNCHED-PG59116.txt` | `Why is the Negro Lynched?` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS` | `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS-COLLECTED-ARTICLES-PG99` | `DOUGLASS-COLLECTED-ARTICLES-PG99.txt` | `Collected Articles of Frederick Douglass` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS` | `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS-JOHN-BROWN-PG31839` | `DOUGLASS-JOHN-BROWN-PG31839.txt` | `John Brown: An Address at the 14th Anniversary of Storer College` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-027-JACOBS` | `LIB-INDUSTRIAL-AUTHORITY-027-JACOBS-INCIDENTS-PG11030` | `JACOBS-INCIDENTS-PG11030.txt` | `Incidents in the Life of a Slave Girl, Written by Herself` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-025-DU-BOIS` | `LIB-INDUSTRIAL-AUTHORITY-025-DU-BOIS-SOULS-PG408` | `DUBOIS-SOULS-PG408.txt` | `The Souls of Black Folk` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-023-MELVILLE` | `LIB-INDUSTRIAL-AUTHORITY-023-MELVILLE-MOBY-DICK-PG2701` | `MELVILLE-MOBY-DICK-PG2701.txt` | `Moby Dick; Or, The Whale` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-024-TWAIN` | `LIB-INDUSTRIAL-AUTHORITY-024-TWAIN-HUCKLEBERRY-FINN-PG76` | `TWAIN-HUCKLEBERRY-FINN-PG76.txt` | `Adventures of Huckleberry Finn` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-024-TWAIN` | `LIB-INDUSTRIAL-AUTHORITY-024-TWAIN-LIFE-ON-MISSISSIPPI-PG245` | `TWAIN-LIFE-ON-MISSISSIPPI-PG245.txt` | `Life on the Mississippi` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-061-ZOLA` | `LIB-INDUSTRIAL-AUTHORITY-061-ZOLA-GERMINAL-ELLIS-PG56528` | `ZOLA-GERMINAL-PG56528.txt` | `Germinal` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-061-ZOLA` | `LIB-INDUSTRIAL-AUTHORITY-061-ZOLA-JACCUSE-FRENCH-PG76045` | `ZOLA-JACCUSE-FRENCH-PG76045.txt` | `J'accuse...!` | French | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-062-HARDY` | `LIB-INDUSTRIAL-AUTHORITY-062-HARDY-TESS-PG110` | `HARDY-TESS-PG110.txt` | `Tess of the d'Urbervilles: A Pure Woman` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-062-HARDY` | `LIB-INDUSTRIAL-AUTHORITY-062-HARDY-JUDE-PG153` | `HARDY-JUDE-PG153.txt` | `Jude the Obscure` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-063-WILDE` | `LIB-INDUSTRIAL-AUTHORITY-063-WILDE-DE-PROFUNDIS-PG921` | `WILDE-DE-PROFUNDIS-PG921.txt` | `De Profundis` | English | `public-domain` | `complete-work` | proposed admit |
| `LIB-INDUSTRIAL-AUTHORITY-063-WILDE` | `LIB-INDUSTRIAL-AUTHORITY-063-WILDE-IMPORTANCE-EARNEST-PG844` | `WILDE-IMPORTANCE-PG844.txt` | `The Importance of Being Earnest` | English | `public-domain` | `complete-work` | proposed admit |

## Registry Update Plan

If later authorized, the admission run should:

1. Admit each file through `tools\run.ps1 library admit-text` or an equivalent
   governed batch route.
2. Preserve each body as a distinct `text_bodies` entry.
3. Set the affected source `text_status` to `available` only after at least one
   body is admitted and hash-verified.
4. Add `body_admission_receipt` metadata to each affected source location.
5. Regenerate `archive/library/text-sources-index.md` and
   `archive/library/industrial/index.md`.
6. Run `tools\run.ps1 library verify-texts --json`,
   `tools\run.ps1 library validate --json`,
   `tools\run.ps1 library render-index --check --json`, and
   `tools\run.ps1 test --path tests/test_archive_library.py`.

## Admission Notes By Authority

- Austen, Shelley, Eliot, Melville, Du Bois: one principal public-domain
  English work each; source coverage should stay at `principal-work`.
- Dickens, Twain, Hardy: two principal works each; source coverage can remain
  `principal-works`.
- Douglass: seven bodies provide selected narrative, autobiographical, speech,
  address, and civic prose coverage. This is strong `principal-works` coverage,
  not complete corpus coverage.
- Jacobs: note that the work was published under the Linda Brent narrative
  persona and edited by Lydia Maria Child.
- Zola: admit `Germinal` as English Havelock Ellis translation and `J'accuse`
  as French original-period newspaper text; do not collapse them into one body
  claim.
- Wilde: `De Profundis` is an edited prison-letter text; keep the edition
  boundary explicit.

## Acceptance Tests

- 23 proposed bodies are listed.
- 12 Batch 001 authorities are represented.
- No proposed body claims complete source-authority corpus coverage.
- Douglass coverage is explicitly selected/principal-works, not complete.
- Zola translation and French original layers remain distinct.
- This proposal performs no admission, registry body mutation, staging, commit,
  push, publication, or Archive ingest.

## Recommended Next Gate

The next action, if authorized, is admission of the 23 proposed bodies into the
private library text store with registry body metadata updates and generated
index verification.

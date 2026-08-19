# Mira Library

Status: `scaffold`

`archive/library/` is Mira Core's curated source-library shelf for primary,
ancient, and historical sources, organized by the source or work's primary
historical subject period. It is a repository-local navigation and retrieval
surface, not a private Archive catalog collection and not a wholesale mirror of
Civilization Memory.

The machine authority is [`library-registry.json`](library-registry.json).
[`text-sources-index.md`](text-sources-index.md) lists admitted local/private
text bodies. Era `index.md` files are human-facing navigation surfaces only.

## Era Taxonomy

| Era | ID | Range | Use |
| --- | --- | --- | --- |
| Ancient | `ancient` | BC to 476 AD | Operational shelf for classical, foundational, and ancient subject periods up to the 476 AD boundary. |
| Medieval | `medieval` | 476 AD to 1453 AD | Operational shelf for medieval subject periods, transmission chains, religious-political orders, and civilizational continuity. |
| Colonial | `colonial` | 1453 AD to 1815 AD | Operational shelf for early-modern subject periods, including imperial, maritime, gunpowder-state, confessional, company-rule, and pre-industrial global systems; not limited to European colonial history. |
| Industrial | `industrial` | 1815 AD to 1991 AD | Operational shelf for industrial subject periods, including industrial states, mass politics, late empire, world wars, Cold War order, and modern state capacity. |
| Digital | `digital` | 1991 AD to present | Operational shelf for digital-era subject periods, including post-Cold War order, internet-scale information systems, platform media, globalization, precision warfare, AI, and digital state capacity. |

These eras are operational shelves for retrieval and browsing. They classify
library placement by primary subject period; they are not a universal
historical ontology or a claim that every civilization follows the same period
sequence.

## Source Model

Future source entries in `library-registry.json` use:

- `source_id`
- `title`
- `author`
- `subject_era`
- `source_composition_era`
- `edition_era`
- `secondary_eras`
- `date_start`
- `date_end`
- `date_label`
- `era_basis`
- `civilization_tags`
- `source_type`
- `location`
- `status`
- `notes`

`subject_era` is required and classifies the primary historical subject period.
`source_composition_era` records when the work was composed when known.
`edition_era` records the era of the edition, translation, URL, database, or
digital object when relevant.

## Original And English Text Policy

For ancient source-authority records, the preferred portable library target is
to carry both:

1. an original-language text body when a lawful, clean, stable source can be
   located; and
2. an English text body when a lawful, clean, stable translation can be located.

These bodies should be admitted separately in `text_bodies`, with distinct
`body_id`, `language`, edition, translator/editor, hash, byte count, and license
metadata. Original-language bodies anchor philological precision and retrieval;
English bodies support immediate reading and cross-civilizational comparison.

Do not force this pairing when the available source is copyrighted, unstable,
scrape-heavy, facsimile-only, OCR-messy, or otherwise not clean enough for the
portable text store. A source may remain partially covered, translation-only, or
original-only, but `coverage_notes` should say that explicitly.

## Ancient Library Maturity Ladder

The Ancient shelf is governed by curated portability rather than maximal
accumulation. A source-authority record is mature only when its offline text
coverage, edition metadata, license posture, and coverage claim can be defended
from the registry and local text store.

Use this ladder when auditing Ancient records:

| Level | Label | Standard |
| --- | --- | --- |
| 0 | Stub only | The authority is represented in metadata, but no local text body is admitted. |
| 1 | Located source candidate | A lawful candidate has been identified, but the body has not been admitted and verified. |
| 2 | Admitted readable English body | At least one readable local/private text body is admitted and verifiable. |
| 3 | Verified principal-work coverage | The registry makes a conservative coverage claim such as `selected-works`, `principal-work`, or `principal-works`, and the admitted bodies support that claim. |
| 4 | Cleaned text with edition/license notes | Text bodies are readable, stable, and sufficiently clean for offline use, with edition, translator/editor, hash, byte count, encoding, and license metadata. |
| 5 | English plus original-language coverage | The authority has both English and original-language coverage where lawful, available, and useful. |
| 6 | Mature authority record | The record honestly models complete, selected, fragmentary, multi-work, translation, and edition limits for the source authority. |

Do not advance a record by implication. `text_status`, `coverage_status`, and
`text_bodies` describe different things: local availability, corpus coverage,
and admitted physical/logical bodies. When they disagree, prefer the lower
curatorial claim until a focused audit resolves the gap.

## Portable Text Store

Git tracks the registry, era indexes, validation code, and source metadata.
Source bodies live outside Git by default in a portable private text store:

1. `MIRA_CORE_LIBRARY_TEXT_ROOT` when set.
2. `.mira-private/library/texts/` inside this repository.

The registry may point to local text bodies with `library-text://...` logical
URIs. Text admission records hashes, byte counts, encoding, edition metadata,
and license posture, but it does not ingest the body into the private Archive
catalog and does not mark the source reviewed.

Supported text bodies for the initial portable store are plain `.txt`, `.md`,
and `.xml` files. PDFs, scans, OCR images, facsimiles, and edition bundles
remain external/private unless a later governed pass admits them explicitly.

Optional text fields:

- `text_status`: `missing`, `available`, `verified`, or `needs-review`
- `coverage_status`: `unknown`, `selected-works`, `principal-work`,
  `principal-works`, or `complete-surviving-corpus`
- `coverage_notes`
- `text_location`
- `text_sha256`
- `text_bytes`
- `text_encoding`
- `language`
- `translator`
- `editor`
- `edition_label`
- `license_status`: `public-domain`, `open-license`, `permissioned`,
  `unknown`, or `restricted`
- `license_notes`

For author or source-authority records that need more than one work, volume, or
edition, prefer `text_bodies` over the single-text fields:

- `body_id`
- `work_title`
- `text_location`
- `text_sha256`
- `text_bytes`
- `text_encoding`
- `language`
- `translator`
- `editor`
- `edition_label`
- `license_status`
- `license_notes`
- `status`: `available`, `verified`, or `needs-review`

The single-text fields remain valid for simple one-body records. New multi-work
or multi-volume admissions should use `text_bodies` so author/source authority
records such as Homer, Herodotus, Plato, Aristotle, Cicero, and Tacitus can
carry multiple local text bodies without overwriting each other.

`coverage_status` describes how much of an author/source authority is actually
present in the portable text store. It is not inferred from `text_status`.
Prefer conservative values: use `selected-works` for partial corpora,
`principal-work` or `principal-works` for deliberately representative core
holdings, and `complete-surviving-corpus` only when the admitted bodies cover
the known surviving corpus represented by the source-authority record.

## Source Admission Workflow

Admitting a text is a local/private act. It copies a known local text file into
the portable text store and updates only the registry metadata needed to locate
and verify that file. It does not download sources, ingest Archive records,
publish anything, or convert a source to reviewed status.

Use this sequence for the first public-domain texts:

1. Identify the target `source_id` with `tools\run.ps1 library search`.
2. Place the candidate `.txt`, `.md`, or `.xml` file in a temporary local path.
3. Confirm the edition and license basis outside the tool; use only
   `public-domain`, `open-license`, or `permissioned` for admission.
4. Run a dry check:

   ```powershell
   tools\run.ps1 library admit-text --source-id SOURCE_ID --file C:\path\text.txt --edition "Edition label" --license-status public-domain --check --json
   ```

5. Run the write only after the dry check is clean:

   ```powershell
   tools\run.ps1 library admit-text --source-id SOURCE_ID --file C:\path\text.txt --edition "Edition label" --license-status public-domain --json
   tools\run.ps1 library verify-texts --json
   ```

6. Treat any later staging, commit, push, Archive ingestion, or publication as a
   separate authority boundary.

`admit-text` refuses `unknown` and `restricted` license statuses. Those values
may remain in metadata for unresolved or inaccessible sources, but they cannot
be used to admit a local text body.

For multi-body records, include a stable body ID and work title:

```powershell
tools\run.ps1 library admit-text --source-id LIB-ANCIENT-AUTHOR-039-HOMER --body-id LIB-ANCIENT-AUTHOR-039-HOMER-ILIAD-BUTLER --work-title "Iliad" --file C:\path\iliad.txt --edition "Project Gutenberg; Samuel Butler translation" --license-status public-domain --check --json
```

## Civilization Memory Crosswalk

Civilization Memory's `ARC-T-*` taxonomy classifies authors and sources by
source-time and can carry precedence rules inside that system. Mira Library
uses era labels for subject-period shelving and retrieval metadata. A source may
therefore have one Mira Library `subject_era`, another `source_composition_era`,
and another `edition_era` without creating a conflict.

Mira Library eras do not by themselves establish source precedence,
admissibility, evidence role, quotation rights, or conflict-resolution rules.
Those judgments belong to the workflow that uses the source.

Typical crosswalk:

- `ARC-T-ANCIENT` usually maps to `subject_era: ancient`.
- `ARC-T-MEDIEVAL` usually maps to `subject_era: medieval`.
- `ARC-T-EARLY-MOD` may map to `subject_era: colonial` or `industrial`.
- `ARC-T-MODERN` usually maps to `industrial` or `digital` as edition,
  scholarship, or analysis era.

## Authority Boundary

Library storage, search, and classification do not verify claims, grant
quotation rights, publish sources, ingest records into the private Archive
catalog, promote sources into evidence, or import Civilization Memory content.

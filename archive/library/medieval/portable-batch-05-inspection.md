# Medieval Portable Batch 05 Inspection

Date: 2026-08-19
State: `review-pending`
Authority effect: none

## Result

Batch 05 inspected five research-triaged Medieval authorities in one bundled
pass. Fifteen artifacts landed in the isolated private batch directory:
fourteen candidate text bodies and one Library of Congress metadata witness.
No body was admitted.

| Outcome | Count |
| --- | ---: |
| Authorities attempted | 5 |
| Candidate artifacts inspected | 15 |
| Passing text bodies | 3 |
| Blocked text bodies | 11 |
| Metadata witnesses | 1 |
| Authorities ready for implementation review | 2 |

Dante's Italian and Cary English Gutenberg bodies passed as two complete named
editions of the *Commedia*. Gregory of Tours' Brehaut/Gutenberg body also
passed file and rights inspection, but only with an `abridged-work` ceiling:
the edition explicitly calls itself “Selections,” omits chapters, and
summarizes some omissions.

## Authority Dispositions

| Authority | Artifacts | Disposition | Controlling reason |
| --- | ---: | --- | --- |
| Dante Alighieri | 2 | Pass | Complete Italian and historical English Gutenberg editions; Italian critical-edition lineage remains unidentified. |
| Gregory of Tours | 1 | Pass, abridged only | Clean Gutenberg body, but Brehaut explicitly supplies selections and summaries rather than the complete work. |
| Judah Halevi | 1 | Blocked | Hirschfeld edition is uncorrected Internet Archive OCR with unstated item rights and mixed-language apparatus. |
| Maimonides | 2 | Blocked | Friedlander is uncorrected OCR with unstated item rights; the reusable LOC Judeo-Arabic route is a manuscript metadata witness, not normalized text. |
| al-Mas‘udi | 9 | Blocked | Complete nine-volume Arabic/French edition route, but all bodies are uncorrected OCR with unstated item rights and no English body. |

## Passing Bodies

| Body | Bytes | SHA-256 | Coverage ceiling |
| --- | ---: | --- | --- |
| Dante, Italian, Gutenberg 1000 | 597,903 | `4669dcc00ee61ceffe92d871e61ea430cec87b35cbab24f19a4c0b1c7da521b2` | `complete-work` |
| Dante, Cary English, Gutenberg 8800 | 656,728 | `3a7dd97b5fec82456c58237b33383a593480c2bfe088aeaaa4a519de2a10d39c` | `complete-work` |
| Gregory, Brehaut selections, Gutenberg 74955 | 717,726 | `f285fd7b3b17b32c678ede86b951487f69c5846d632eef16b922ca29caa4f5fe` | `abridged-work` |

The Dante files contain the three expected divisions and complete Gutenberg
start/end wrappers and license text. Their pairing does not establish
textual-variant equivalence. The Italian file does not name a critical editor
or upstream print edition, so its edition-identity ceiling remains below a
fully mature record.

## Blocked Routes

- Judah Halevi: the 1905 Hirschfeld OCR exposes all five parts but must be
  reconciled to scans; no portable Judeo-Arabic body was inspected.
- Maimonides: the 1904 Friedlander OCR exposes all three parts but has the same
  OCR and item-rights defects. LOC item 2021667527 supplies a positive WDL reuse
  statement and a Judeo-Arabic manuscript witness, but the downloaded JSON is
  metadata, not a searchable source body.
- al-Mas‘udi: all nine volumes of the 1861–1877 Barbier de Meynard/Pavet de
  Courteille Arabic/French edition are present. Volume-sequence completeness
  does not cure derived-OCR fidelity, unstated item rights, the absence of an
  English route, or recension uncertainty.

## Evidence Discipline

- Confirmed metadata covers downloaded bytes, hashes, embedded notices,
  structural markers, edition labels, and repository statements.
- Repository rights statements are source assertions, not independent legal
  adjudications.
- Coverage ceilings are conservative researcher inferences; none imply a
  complete surviving authority corpus or Level 6 maturity.
- OCR quality, critical-edition lineage, scan equivalence, mixed-language
  boundaries, and translation equivalence remain visible uncertainties.

The reconciled machine record is
[`portable-batch-05-inspection.json`](portable-batch-05-inspection.json).

## Persistence and Non-Authorization

- Candidate artifacts remain under
  `private-inspection-root:medieval-portable-batch-05-20260819`.
- The Library registry, managed private text store, and era indexes were not
  changed by this batch.
- Nothing was staged, committed, pushed, published, or ingested into Archive.

The recommended next bounded implementation candidate is Dante: prepare its
conservative authority metadata and exact two-body admission proposal while
preserving the unnamed Italian edition-lineage gap. Gregory should remain a
separate abridged-edition decision.

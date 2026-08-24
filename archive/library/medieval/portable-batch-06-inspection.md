# Medieval Portable Batch 06 Inspection

Date: 2026-08-19
State: `review-pending`
Authority effect: none

## Result

Batch 06 processed ten Medieval authorities together and downloaded 25
artifacts (25,076,001 bytes) into the isolated private batch root. Fifteen are
candidate text bodies and ten are metadata or route records. No body was
admitted.

| Outcome | Count |
| --- | ---: |
| Authorities attempted | 10 |
| Downloaded artifacts | 25 |
| Candidate text bodies | 15 |
| Passing text bodies | 14 |
| Blocked text bodies | 1 |
| Authorities ready for implementation review | 2 |
| Authorities blocked or metadata-only | 8 |

## Authority Dispositions

| Authority | Disposition | Controlling limit |
| --- | --- | --- |
| Thomas Aquinas | Pass, four English parts | Clean Gutenberg bodies for Prima Pars, Prima Secundae, Secunda Secundae, and Tertia Pars; Supplement and Latin counterpart absent. |
| *Arabian Nights* tradition | Pass, named Burton edition only | Ten clean Gutenberg volumes complete Burton's main English edition; no Arabic witness, Supplemental Nights, or tradition-level completeness. |
| *Tale of the Heike* tradition | Blocked | IA asserts CC0, but the Sadler body is uncorrected OCR not reconciled to scans; no Japanese witness. |
| Constantine VII | Metadata-only | GREDOS catalog recovered; reusable file and file-level terms unresolved; standard English translation restricted. |
| Michael Psellos | Blocked | Fordham web display of Sewter does not establish reuse; no Greek body. |
| *Kebra Nagast* tradition | Access-blocked | Mirror returned HTTP 455 and archive HTTP 403; Budge rights and Ge'ez body unresolved. |
| Domesday Book tradition | Metadata-only | Hull collection page recovered; dataset package, license, schema, and Great/Little layer ledger unresolved. |
| Anna Komnene | Invalid route | Attempted Princeton record resolved to a generic database page; no *Alexiad* body. |
| Magna Carta tradition | Blocked | Avalon supplies one English 1215 web transcription without inspected reuse terms, Latin witness, or reissue ledger. |
| Zhu Xi | Metadata witness | LOC/WDL identifies a reusable digitized Chinese witness, but JSON is not normalized text and no lawful English body was inspected. |

## Passing Cohorts

The Aquinas cohort contains four separate complete-part bodies totaling
12,787,366 bytes. It does not include the Supplement, so it cannot support a
complete multipart *Summa* claim.

The Burton cohort contains volumes 1–10 of the named main English edition,
each with its own Gutenberg wrapper and `of 10` volume declaration. Together
they support only a complete named ten-volume Burton-main-edition claim. The
six Supplemental Nights volumes are a separate editorial extension, and the
edition is not an Arabic witness or a recovered medieval *Nights* corpus.

## Evidence Discipline

- Every downloaded artifact has an exact byte count, SHA-256 hash, and upstream
  URL in the machine record.
- Gutenberg public-domain assertions are repository claims limited by their
  non-US jurisdiction warnings.
- Web display, open access, CC0 metadata, and digitized page images do not by
  themselves establish a clean portable text body.
- Composite traditions remain traditions: a late English edition cannot be
  promoted into original-language equivalence or complete surviving-corpus
  coverage.

The reconciled machine record is
[`portable-batch-06-inspection.json`](portable-batch-06-inspection.json).

## Persistence and Non-Authorization

- Artifacts remain under
  `private-inspection-root:medieval-portable-batch-06-20260819`.
- The registry, managed private text store, and era indexes were not changed.
- Nothing was staged, committed, pushed, published, or ingested into Archive.

The recommended implementation order is Aquinas first as a four-body partial
multipart admission, followed by the ten-volume Burton main edition under a
strict textual-tradition boundary. Both should be implemented as bundles, not
one file at a time.

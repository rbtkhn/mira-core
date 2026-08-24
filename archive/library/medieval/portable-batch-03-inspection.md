# Medieval Portable Batch 03 — Inspection Receipt

Date: 2026-08-19
State: `review-pending`
Authority effect: `none`

## Result

Portable Batch 03 reconciles six authorities and ten privately held candidate bodies. Six bodies pass inspection for a later batch-level implementation review: Bede's Sellar translation and five Procopius bodies. Four bodies remain blocked without stopping the passing rows.

Nothing was admitted. The registry, Medieval index, and configured private Library text store were not changed.

## Shelf Progress

| Measure | Count |
| --- | ---: |
| Selected roster authorities | 60 |
| Edition-triaged authorities | 20 |
| Authorities attempted in Batch 03 | 6 |
| Candidate bodies attempted | 10 |
| Bodies downloaded and present | 10 |
| Bodies inspected | 10 |
| Passing bodies | 6 |
| Blocked bodies | 4 |
| Rejected bodies | 0 |
| Authorities ready for implementation review | 2 |
| Medieval authorities admitted | 0 |

Nine files were downloaded into `private-inspection-root:medieval-portable-batch-03-20260819`. The previously inspected Bede file remains at `private-inspection-root:bede-inspection-20260819\pg38326.txt` and was incorporated by its verified receipt and hash.

## Authority Dispositions

| Authority | Bodies | Result | Authority coverage ceiling | Material limit |
| --- | ---: | --- | --- | --- |
| Bede | 1 | `pass` | `principal-work` | English Sellar 1907 only; no Latin counterpart |
| Procopius | 5 | `pass-with-partial-wars` | `principal-works` | *Wars* covers Books I–VI only; Books VII–VIII and Greek remain absent |
| Anna Komnene | 1 | `blocked` | `principal-work` | Complete Dawes translation is HTML with site structure |
| Benedictine Rule tradition | 1 | `blocked` | `principal-work` | Gutenberg PD assertion conflicts visibly with a 1948 copyright notice |
| Einhard | 1 | `blocked` | `principal-work` | File is a mixed Einhard–Notker anthology |
| Magna Carta tradition | 1 | `blocked` | `selected-works` | PDF-only 1215 translation; file-specific rights and later reissues unresolved |

## Passing Bodies

### Bede

- **Body:** Sellar, *Bede's Ecclesiastical History of England*, George Bell and Sons, 1907; [Project Gutenberg 38326](https://www.gutenberg.org/ebooks/38326).
- **Integrity:** 1,093,654 bytes; SHA-256 `977da0babf070c825befb0a5db65a9cc2440d9ab45aa869a959c1bab911be2c8`.
- **Body ceiling:** `complete-work` for this named English edition.
- **Authority ceiling:** `principal-work`; no Latin equivalence or complete Bede corpus claim.

### Procopius

| Work body | Edition | Bytes | SHA-256 | Body ceiling |
| --- | --- | ---: | --- | --- |
| *Wars* I–II | Dewing; [Gutenberg 16764](https://www.gutenberg.org/ebooks/16764) | 565,217 | `034143d397a53f74400f346725a4b1d8380b2d029e220a5a2bbf0e4bf2f7baa2` | `partial-work` |
| *Wars* III–IV | Dewing; [Gutenberg 16765](https://www.gutenberg.org/ebooks/16765) | 488,068 | `563eb598ee498b9d47cefa3410693371b921912b265bbc8d5ca8270bdc131f03` | `partial-work` |
| *Wars* V–VI | Dewing; [Gutenberg 20298](https://www.gutenberg.org/ebooks/20298) | 452,871 | `66d1f2b4144c25348393dafd0c267a8ca903302faa60d4322d3df6c2492fcf59` | `partial-work` |
| *Buildings* I–VI | Stewart, 1888; [Gutenberg 65404](https://www.gutenberg.org/ebooks/65404) | 357,819 | `127843ac9e021c89b7d35dcb5fbd1ded16f51969501308bc0b11696340b1e273` | `complete-work` |
| *Secret History* | Anonymous Athenian Society translation, 1896; [Gutenberg 12916](https://www.gutenberg.org/ebooks/12916) | 282,413 | `4434eb534c52db03eed9afcc803eb52fe840bb295f277d154e76ef05bfaf6666` | `complete-work` |

All five Procopius files are valid UTF-8, have matching headers, and retain complete Gutenberg wrappers. Their different translation and publication lineages remain separate physical bodies. Together they justify only `principal-works`, with the missing *Wars* Books VII–VIII stated explicitly.

## Blocked Bodies

### Anna Komnene

Fordham's [complete Dawes translation](https://sourcebooks.web.fordham.edu/basis/AnnaComnena-Alexiad00.asp) contains all fifteen books and states that US copyright was not renewed. The inspected 1,149,696-byte body is HTML, not an admissible Library text format, and includes site structure. It remains blocked pending an authorized provenance-preserving extraction or a clean institutional text body.

### Benedictine Rule tradition

[Project Gutenberg 50040](https://www.gutenberg.org/ebooks/50040) contains Doyle's complete Prologue and Chapters 1–73 in clean UTF-8. Its front matter also retains “Copyright 1948 by The Order of St. Benedict, Inc.” This visible conflict requires a renewal/public-domain basis or a different translation before admission.

### Einhard

[Project Gutenberg 48870](https://www.gutenberg.org/ebooks/48870) is the 1905 A. J. Grant anthology *Early Lives of Charlemagne*. It contains both Einhard and the Monk of St Gall. The unmodified file cannot silently become an Einhard-only body; extraction or separate anthology modeling must be authorized and inspected.

### Magna Carta tradition

The inspected [National Archives PDF](https://cdn.nationalarchives.gov.uk/documents/education/magna-carta/magna-carta-lesson3-source9.pdf) has eight visually reviewed pages: a 1215 charter image followed by a legible English translation of clauses 1–63. It is PDF-only, its exact translation rights remain unresolved, and it does not cover the 1216, 1217, 1225, or 1297 reissues. It remains blocked.

## Reconciliation

- Six unique candidate IDs and six unique proposed source IDs.
- Ten body rows reconcile to six passing, four blocked, and zero rejected.
- Every private file existed at reconciliation and every recorded SHA-256 matched.
- Passing bodies remain only inspection candidates; `pass` does not mean admitted, available, verified, or reviewed.
- No body was copied into `.mira-private/library/texts/` or another configured Library text root.
- No registry, era index, staging area, commit, remote, Archive catalog, or publication surface changed.

## Review Boundary

The next executable batch action should add exact `located` metadata records for Bede and Procopius, dry-run the six passing bodies through Library Import, and—only if explicitly authorized—admit those bodies together. Anna Komnene, Benedict, Einhard, and Magna Carta must be excluded until their named blockers are resolved.

The machine-reviewable receipt is [portable-batch-03-inspection.json](./portable-batch-03-inspection.json).

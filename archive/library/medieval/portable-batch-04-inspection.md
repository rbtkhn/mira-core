# Medieval Portable Batch 04 Inspection

Date: 2026-08-19
State: `review-pending`
Authority effect: none

## Result

Batch 04 inspected ten research-triaged Medieval authorities in one bundled
pass. Ten new files were downloaded and the previously inspected Tanzil body
was incorporated, producing eleven candidate bodies. No body was admitted.

| Outcome | Count |
| --- | ---: |
| Authorities attempted | 10 |
| Candidate bodies inspected | 11 |
| Passing bodies | 2 |
| Blocked bodies | 9 |
| Metadata-only authorities | 2 |
| Authorities ready for implementation review | 1 |

Only the paired Marco Polo Yule-Cordier volumes passed. They are a complete
named English editorial edition across two partial-work bodies, not an
equivalent witness to BnF français 1116 and not a recovered authorial text.

## Authority Dispositions

| Authority | Bodies | Disposition | Controlling reason |
| --- | ---: | --- | --- |
| Marco Polo / Rustichello tradition | 2 | Pass | Complete paired Gutenberg English edition; original witness still absent. |
| Qur'anic textual tradition | 1 | Blocked | Tanzil CC BY 3.0 body also carries a no-change/verbatim-only condition requiring governance review. |
| Geoffrey Chaucer | 1 | Blocked | Skeat/Gutenberg volume includes the disputed *Tale of Gamelyn*, outside the accepted Chaucer-only boundary. |
| Kalhana | 2 | Blocked | Public-domain-marked source items, but the downloaded bodies are uncorrected OCR not reconciled to scans. |
| al-Biruni | 1 | Blocked | Combined OCR item carries CC BY-NC-ND 4.0 despite its historical edition lineage. |
| al-Tabari | 1 | Blocked | One Arabic edition volume only; rights unstated and OCR uncorrected. |
| Ibn Khaldun | 2 | Blocked | Incomplete Quatremère sequence, unstated rights, and poor uncorrected Arabic OCR. |
| Nizam al-Mulk | 1 | Blocked | One Schefer volume only, unstated rights, uncorrected OCR, and disputed chapter boundary. |
| Rus' Primary Chronicle tradition | 0 | Metadata-only | Identified routes do not authorize a portable body. |
| Sima Guang editorial tradition | 0 | Metadata-only | CText forbids automated bulk download; no complete English body is known. |

## Passing Bodies

| Body | Bytes | SHA-256 | Coverage ceiling |
| --- | ---: | --- | --- |
| Marco Polo, Yule-Cordier volume I, Gutenberg 10636 | 2,345,876 | `7b0cbb0bc47a48d7594314b56d890e3e43ac05666b8c70d98f10719501cf6fb5` | `partial-work` |
| Marco Polo, Yule-Cordier volume II, Gutenberg 12410 | 2,421,259 | `c1ce61dd8c6c6a326c42fb7ac3b1a63767bf1685ec88354f83dd321e1748921c` | `partial-work` |

Both files are strict UTF-8, contain complete Gutenberg start/end wrappers and
license text, and identify their volume boundary. Together they support only a
complete named English-edition claim.

## Evidence Discipline

- Confirmed metadata covers inspected bytes, hashes, encoding, embedded
  notices, structural markers, and repository metadata.
- Repository license labels remain source assertions, not independent legal
  adjudications.
- Coverage ceilings are researcher inferences and deliberately stop below
  source-authority completeness.
- OCR fidelity, missing volumes, attribution disputes, rights conflicts, and
  cross-language equivalence remain visible unresolved uncertainties.

The reconciled machine record is
[`portable-batch-04-inspection.json`](portable-batch-04-inspection.json).

## Persistence and Non-Authorization

- Candidate files remain under
  `private-inspection-root:medieval-portable-batch-04-20260819`.
- The Library registry, managed private text store, and era indexes were not
  changed by this batch.
- Nothing was staged, committed, pushed, published, or ingested into Archive.

The next bounded implementation candidate is Marco Polo only: prepare a
metadata record and two-body admission proposal, then stop for review.

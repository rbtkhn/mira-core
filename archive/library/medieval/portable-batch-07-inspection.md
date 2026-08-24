# Medieval Portable Batch 07 Inspection

Date: 2026-08-19
State: `review-pending`
Authority effect: none

## Result

Batch 07 processed ten authorities together. It downloaded seven new route
artifacts and incorporated seven previously inspected Batch 04 text bodies
without duplicating those weak OCR downloads.

| Outcome | Count |
| --- | ---: |
| Authorities attempted | 10 |
| New artifacts | 7 |
| Prior text inspections incorporated | 7 |
| Passing text bodies | 1 |
| Blocked prior text bodies | 7 |
| Authorities ready for implementation review | 1 |

The single passing body is J. B. Moyle's complete four-book English
*Institutes of Justinian*, fifth edition (1913), Project Gutenberg 5983. Its
ceiling is one complete component of the four-component *Corpus Iuris Civilis*;
the Digest, Codex, and Novels remain absent.

## Dispositions

| Authority | Disposition | Controlling reason |
| --- | --- | --- |
| Justinianic legal tradition | Pass, Institutes only | Clean Gutenberg body; three other principal components absent. |
| al-Tabari | Blocked | One Arabic volume, incomplete sequence, unstated rights, uncorrected OCR; modern English restricted. |
| Nizam al-Mulk | Blocked | Uncorrected OCR, unstated rights, one edition layer, disputed late chapters. |
| al-Biruni | Blocked | Prior OCR item carries CC BY-NC-ND 4.0; no verified Arabic body. |
| Ibn Khaldun | Blocked | Incomplete Arabic sequence, poor OCR, unstated rights, no reusable complete English. |
| Sima Guang | Metadata-only | No lawful complete export or complete reusable English body. |
| Kalhana | Blocked | Two Stein volumes remain uncorrected OCR not reconciled to scans. |
| *Azuma Kagami* | Blocked | JHTI explicitly reserves the selected English translation; NIJL rights vary by item. |
| *Secret History of the Mongols* | Partial route only | Pelliot route covers chapters I–VI and lacks a resolved general reuse license. |
| Rus' Primary Chronicle | Metadata witness | NLR permission is project-specific; manuscript, modernization, and translation layers cannot be collapsed. |

## Evidence Discipline

The Justinian body contains all four books and complete Gutenberg wrappers.
Its `complete-work` claim may apply only to the *Institutes*, never to the
*Corpus Iuris Civilis*. The Grenoble Digest page is an edition route, not an
admitted or rights-cleared fifty-book body.

The refreshed JHTI page explicitly prohibits republishing the Shinoda
translation beyond quotation or fair use. The NLR page states that permission
was granted to use Likhachev's work in that project; it does not grant Mira a
portable redistribution license. UQAM identifies its Pelliot file as chapters
I–VI, which is intrinsically partial even before rights review.

Machine record:
[`portable-batch-07-inspection.json`](portable-batch-07-inspection.json).

## Persistence

New artifacts remain under
`private-inspection-root:medieval-portable-batch-07-20260819`. No registry,
managed private-store, or index change occurred. Nothing was staged, committed,
pushed, published, or ingested into Archive.

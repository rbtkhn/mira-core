# Medieval Portable Batch 08 Inspection

Date: 2026-08-19
State: `review-pending`
Authority effect: none

## Result

Batch 08 inspected ten authorities together and retained seventeen artifacts in
the isolated private inspection directory. Eleven are text candidates and six
are Internet Archive metadata receipts.

| Outcome | Count |
| --- | ---: |
| Authorities attempted | 10 |
| Downloaded artifacts | 17 |
| Text candidates | 11 |
| Passing text bodies | 4 |
| Blocked text bodies | 7 |
| Metadata-only authorities | 4 |
| Authorities ready for implementation review | 1 |

The four passing bodies are Arthur Waley's first four parts of *The Tale of
Genji*: *The Tale of Genji*, *The Sacred Tree*, *A Wreath of Cloud*, and *Blue
Trousers*. They are clean Project Gutenberg UTF-8 texts and form a contiguous
English sequence. Their ceiling is exactly parts 1-4 of Waley's six-part
translation. Parts 5-6 and an original-language witness remain absent.

## Dispositions

| Authority | Disposition | Controlling reason |
| --- | --- | --- |
| Ferdowsi | Blocked | Gutenberg 10315 is a multi-author anthology containing an explicitly abridged Atkinson rendering, not a work-pure complete *Shahnameh*. |
| Ibn Battuta | Blocked | Lee 1829 is manuscript-abridged and the recovered layer is noisy uncorrected OCR. |
| Ibn Jubayr | Blocked | The 1907 Arabic edition is noisy OCR with no explicit item reuse statement; the located English translation is restricted. |
| Rashid al-Din | Metadata-only | The composite, dispersed manuscript tradition cannot be represented by one portable text; modern translations remain restricted. |
| Xuanzang | Blocked | The two Beal OCR files are noisy and mix a 2003 reprint with an 1884 volume. |
| Shen Kuo | Metadata-only | No complete reusable Chinese export or complete open English translation was resolved. |
| Murasaki Shikibu | Pass, four English parts | Four clean, contiguous Gutenberg bodies; two later Waley parts and Japanese witness absent. |
| *Nihon Shoki* | Blocked | Aston's two-volume sequence is present only as noisy uncorrected OCR with unstated item rights. |
| *Samguk Sagi* | Metadata-only | Institutional identity and text routes exist, but the Korean History Database is all-rights-reserved and no complete reusable English body was found. |
| *Goryeosa* | Metadata-only | Institutional original and modern-Korean layers are not a portable license; no complete reusable English translation was found. |

## Evidence Discipline

Project Gutenberg identifies the four Genji files as separate parts and marks
each public domain in the United States. The passing judgment applies to those
four edition-bodies only. It does not imply complete-work coverage, Japanese
and English equivalence, reviewed status, or mature authority status.

The Ibn Battuta metadata supplies a Public Domain Mark, but rights clearance
does not cure its abridged manuscript basis or OCR defects. Conversely, an old
publication date alone was not treated as a reusable item license for Ibn
Jubayr, Xuanzang, or *Nihon Shoki*. The Korean institutional sites remain
discovery and verification routes, not downloadable-body grants.

Machine record:
[`portable-batch-08-inspection.json`](portable-batch-08-inspection.json).

## Persistence

Artifacts remain under
`private-inspection-root:medieval-portable-batch-08-20260819`. No registry,
managed private-store, era-index, staging, commit, push, publication, or Archive
ingestion change occurred.

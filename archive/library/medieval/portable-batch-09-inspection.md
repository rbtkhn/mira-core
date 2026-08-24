# Medieval Portable Batch 09 Inspection

Date: 2026-08-19
State: `review-pending`
Authority effect: none

## Result

Batch 09 inspected ten authorities together. Fifteen artifacts were retained in
the isolated private inspection root: eight text candidates and seven Internet
Archive metadata receipts.

| Outcome | Count |
| --- | ---: |
| Authorities attempted | 10 |
| Downloaded artifacts | 15 |
| Text candidates | 8 |
| Passing text bodies | 0 |
| Blocked text bodies | 8 |
| Metadata-only authorities | 5 |
| Authorities ready for implementation review | 0 |

No candidate passed all admission gates. This is a reconciled negative batch,
not a failed execution: the rights, sequence, extraction, and cleanliness
barriers are now explicit and resumable.

## Dispositions

| Authority | Disposition | Controlling reason |
| --- | --- | --- |
| Michael the Syrian | Blocked | Chabot volumes 1 and 4 only; volumes 2–3 absent; severe OCR noise and unstated item rights. |
| Ibn Hazm | Metadata-only | A modern Arabic two-volume scan is identified; no clean reusable export or complete English translation. |
| al-Bakri | Metadata-only | De Slane is a French North Africa extract, not the complete geographic work. |
| al-Idrisi | Metadata-only | The 1325 BnF witness lacks two maps and its last folio and contains damaged folios. |
| Ibn al-Athir | Metadata-only | Arabic multi-volume route unresolved; modern English covers selected periods and is restricted. |
| Nasir Khusraw | Blocked | Facsimile prohibits unauthorized copying; English body is a regional extract and uncorrected OCR. |
| Bhaskara II | Blocked | Colebrooke volume mixes Brahmagupta and Bhaskara components and is noisy OCR. |
| Jayadeva | Blocked | Arnold body is an anthology adaptation with explicit omissions; Lassen Sanskrit/Latin layer is uncorrected OCR. |
| Minhaj-i Siraj | Blocked | Both Raverty items carry CC BY-NC-ND 4.0 and noisy reposted OCR. |
| Li Qingzhao | Metadata-only | Fragmentary, attribution-critical corpus; located complete modern English volume is CC BY-NC-ND. |

## Evidence Discipline

Old publication dates were not treated as sufficient item-level reuse grants.
Likewise, a complete two-volume sequence did not overcome noncommercial and
no-derivatives terms or uncorrected OCR. The al-Idrisi manuscript route is a
valuable witness but is intrinsically incomplete; the Li Qingzhao record must
model lost and disputed attributions before any corpus-level maturity claim.

Machine record:
[`portable-batch-09-inspection.json`](portable-batch-09-inspection.json).

## Persistence

Artifacts remain under
`private-inspection-root:medieval-portable-batch-09-20260819`. No registry,
managed private-store, era-index, staging, commit, push, publication, or Archive
ingestion change occurred.

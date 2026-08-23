# Industrial Library Body Download Batch 005 Inspection Receipt

Status: `download-inspected`
Era: `industrial`
Date: 2026-08-23
Research packet: `archive/library/industrial/body-research-batch-005-inspection-receipt.md`
Private inspection root: `C:\private\mira-library-texts\inspection\industrial-batch-005`
Gate: `operator-review-before-body-admission`

## Authority Boundary

This receipt records private download and first-pass inspection only. It does
not admit source bodies, mutate `archive/library/library-registry.json`,
generate indexes, ingest into the private Archive, stage, commit, push, or
publish.

Downloaded files remain private inspection candidates. A passing first-pass
inspection does not by itself admit a body or change registry availability.

## Batch Result

Attempted downloads: 10
Downloaded: 10
First-pass clean/admission-candidate: 9
Paused after inspection: 1
Admitted: 0
Registry mutations: 0

## Downloaded Candidates

| Candidate ID | Authority | Work | Private file | Bytes | SHA-256 | Inspection state | Notes |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `IND-BODY-005-001A` | Machado de Assis | `Dom Casmurro` | `IND-BODY-005-001A-machado-dom-casmurro-pg55752.txt` | 418230 | `0fc3dbf384544d81d87e5a731e67b7976ac3a57acb378f0f354d12a3b52bd0c7` | `admission-candidate` | PG header confirms title, author, Portuguese, eBook #55752, and public-domain license text. |
| `IND-BODY-005-001B` | Machado de Assis | `Memorias Posthumas de Braz Cubas` | `IND-BODY-005-001B-machado-bras-cubas-pg54829.txt` | 403243 | `edfe4370698ed5716a9692b980a8d6ee77b4ff8116503bb2e08675f1d10d303a` | `admission-candidate` | PG header confirms title, author, Portuguese, eBook #54829, and public-domain license text. |
| `IND-BODY-005-002A` | Sojourner Truth textual tradition | `Narrative of Sojourner Truth` | `IND-BODY-005-002A-sojourner-truth-1875-ia-djvu.txt` | 583926 | `7c6f44759af663ecdd937fb159cbba3e31e9a5489d665fd463fcc01110b6514f` | `paused-needs-cleaner-source` | IA/LOC-derived OCR downloaded, but opening text is noisy and title appears as `SOJOURNER TRUTH'S NARRATIVE AND BOOK OF LIFE`; keep paused until a cleaner LOC text/PDF extraction route is chosen. |
| `IND-BODY-005-003A` | Michael Faraday | `The Chemical History of a Candle` | `IND-BODY-005-003A-faraday-candle-pg14474.txt` | 246914 | `c053ca4ae7880585a15001cd3ffdaf5f09cd08c3329b828ffd8c90ce335482b9` | `admission-candidate` | PG header confirms title, author, editor William Crookes, eBook #14474, and public-domain license text. |
| `IND-BODY-005-004A` | Joseph Conrad | `Heart of Darkness` | `IND-BODY-005-004A-conrad-heart-darkness-pg219.txt` | 237072 | `c0b0bc91c7695f9d01aacb240e82a9b559f57558f98ad0b1f167eba21f6be6f7` | `admission-candidate` | PG header confirms title, author, English, eBook #219, and public-domain license text. |
| `IND-BODY-005-004B` | Joseph Conrad | `Lord Jim` | `IND-BODY-005-004B-conrad-lord-jim-pg5658.txt` | 751822 | `e2de6f15eb867e864aa4b5e22410d6dc1c12b7c225a48e2376f6401b71a3b96e` | `admission-candidate` | PG header confirms title, author, English, eBook #5658, and public-domain license text. |
| `IND-BODY-005-005A` | Olive Schreiner | `The Story of an African Farm` | `IND-BODY-005-005A-schreiner-african-farm-pg1441.txt` | 583169 | `01d0c7fff4673ecb1f6b8fc70938fe4ccfb2139803fd3b4f30ab51f6e40c6815` | `admission-candidate` | PG header confirms title, author, English, eBook #1441, and public-domain license text. |
| `IND-BODY-005-006A` | Elizabeth Cady Stanton | `Eighty Years and More; Reminiscences 1815-1897` | `IND-BODY-005-006A-stanton-eighty-years-pg11982.txt` | 816725 | `e30e3011123135463627f9b6efe1484ffc7002855df622493bb0f0bb68dc3a69` | `admission-candidate` | PG header confirms title, author, English, eBook #11982, and public-domain license text. |
| `IND-BODY-005-007A` | Zitkala-Sa | `American Indian Stories` | `IND-BODY-005-007A-zitkala-sa-american-indian-stories-pg10376.txt` | 201897 | `b9934b55d2f83876ea24e3c7f1397240b02f1caf63892823bcdbb59954309252` | `admission-candidate` | PG header confirms title, author, English, eBook #10376, and public-domain license text. |
| `IND-BODY-005-009A` | Friedrich Nietzsche | `The Genealogy of Morals` | `IND-BODY-005-009A-nietzsche-genealogy-pg52319.txt` | 358579 | `90ab67b3c15fb8a4220f36b559514098e33f43d58e4403405575949c039c1cba` | `admission-candidate` | PG header confirms title, author, editor Oscar Levy, translators J. M. Kennedy and Horace Barnett Samuel, eBook #52319, and public-domain license text. |

## Admission-Candidate Set

The following nine bodies are ready for a later bounded admission proposal:

- Machado de Assis, `Dom Casmurro`, PG #55752.
- Machado de Assis, `Memorias Posthumas de Braz Cubas`, PG #54829.
- Michael Faraday, `The Chemical History of a Candle`, PG #14474.
- Joseph Conrad, `Heart of Darkness`, PG #219.
- Joseph Conrad, `Lord Jim`, PG #5658.
- Olive Schreiner, `The Story of an African Farm`, PG #1441.
- Elizabeth Cady Stanton, `Eighty Years and More`, PG #11982.
- Zitkala-Sa, `American Indian Stories`, PG #10376.
- Friedrich Nietzsche, `The Genealogy of Morals`, PG #52319.

## Paused Row

Sojourner Truth remains represented by a downloaded private OCR candidate, but
it should not be admitted from this file. The cleaner next move is either:

- locate and download a reliable LOC PDF/text asset directly tied to item
  `05020876`; or
- use the OCR candidate only after scan-lineage confirmation and a review that
  accepts its noise level for a body record.

## Acceptance Tests

- Exactly 10 preferred Batch 005 candidates were attempted.
- Every attempted candidate produced a private file.
- Every downloaded file has byte count and SHA-256 digest recorded.
- Nine PG files passed title/author/language/public-domain header inspection.
- The Sojourner OCR candidate was paused instead of marked admission-ready.
- No registry, index, body admission, private Archive ingest, staging, commit,
  push, or publication occurred.

## Re-Entry Point

The next bounded action is an admission proposal for the nine clean PG
admission-candidates above, or a Sojourner-specific cleaner-source repair pass.

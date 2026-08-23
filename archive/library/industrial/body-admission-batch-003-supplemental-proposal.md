# Industrial Body Admission Batch 003 Supplemental Proposal

Status: `operator-review-before-body-admission`
Era: `industrial`
Batch: `industrial-body-admission-batch-003-supplemental`
Research receipt: `archive/library/industrial/unresolved-batch-003-research-receipt.md`
Private inspection root: `C:\private\mira-library-inspection\industrial-batch003-unresolved`
Proposed private text root: `C:\private\mira-library-texts`

## Boundary

This proposal requests operator review before admitting supplemental Batch 003 bodies into the private Mira Library text store and adding body metadata to `archive/library/library-registry.json`. It does not itself admit bodies, ingest into the private Archive, stage, commit, push, or publish.

## Proposed Admission Set

Admit 7 text-ready candidates across 3 Industrial Batch 003 authorities:

- Premchand: extracted Hindi `Godan` text from the downloaded Wikimedia Commons/Wikisource PDF.
- Qiu Jin: `中國女報發刊詞`, `滿江紅`, and `致徐小淑絕命詞` from Chinese Wikisource raw text.
- Kang Youwei / Liang Qichao reform textual tradition: Kang `大同書/甲部`; Liang `少年中國說`; Liang `新民說/第一節` from Chinese Wikisource raw text.

## Candidate Details

| Authority | Candidate ID | Work | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| Premchand | `PREMCHAND-GODAN-WIKISOURCE-PDF-EXTRACTED` | Godan | 1953124 | `580fcd3795241ab0639de963275d7adec7df6b5ebe72404c02ead6d641f4b0ef` |
| Qiu Jin | `QIU-JIN-WOMENS-JOURNAL-PREFACE` | 中國女報發刊詞 | 3218 | `9206c47a326def2f2ffc99b4cafdb2c367216023c7ce4f1da195c585a07b09f6` |
| Qiu Jin | `QIU-JIN-MANJIANGHONG` | 滿江紅 | 490 | `d6592fed086d0e5af15ef44a320520b8781fb7423825a9532650c30d71352064` |
| Qiu Jin | `QIU-JIN-DEATH-LETTER` | 致徐小淑絕命詞 | 609 | `f7766c0dbd4100607541b8ded8b1199a34fe25ed709d6fb69028773127eb2f13` |
| Kang Youwei | `KANG-DATONGSHU-JIABU` | 大同書/甲部 | 103837 | `23c33e34baeca24925f515325bbe1eb958a7fbc7e65dac4a3f16bed07b5338d5` |
| Liang Qichao | `LIANG-YOUNG-CHINA` | 少年中國說 | 11642 | `10ebc9ebfb85585af47fa582ab55cd9a6059205c4227e69fba60b8dc57182e64` |
| Liang Qichao | `LIANG-NEW-CITIZEN-1` | 新民說/第一節 | 1423 | `b5096c95ea3bd06a61804359a0d9242a566e92367311e5efd2d7df0713126eaa` |

## Excluded From This Proposal

- Sun Yat-sen: Three Principles of the People remains OCR-gated.
- B. R. Ambedkar remains rights/path blocked.
- Fukuzawa Yukichi remains rights/path blocked.
- Natsume Soseki Kokoro remains permissioned.

## Admission Rules

- Preserve Premchand as extracted text from the public-domain PDF scan; do not admit the PDF itself as a text body.
- Preserve Qiu Jin as selected writings, not a complete corpus.
- Preserve Kang/Liang as a composite reform textual tradition with separate body records for Kang and Liang works.
- Do not claim complete-surviving-corpus coverage for any authority.
- Keep Sun, Ambedkar, Fukuzawa, and Soseki `Kokoro` unresolved until their separate gates clear.

## Acceptance Tests

- library validate passes.
- render-index check passes.
- focused library tests pass.
- 7/7 supplemental private payloads present with matching hashes and byte counts after admission.

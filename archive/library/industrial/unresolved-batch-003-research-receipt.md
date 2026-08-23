# Industrial Batch 003 Unresolved Research Receipt

Status: `research-complete-next-gate-required`
Era: `industrial`
Batch: `industrial-batch-003-unresolved`
Private inspection root: `C:\private\mira-library-inspection\industrial-batch003-unresolved`

## Boundary

This receipt records follow-up research on unresolved Batch 003 authorities. It
does not admit source bodies, ingest into the private Archive, stage, commit,
push, publish, or convert unresolved rows to available text status.

## Improved Paths Found

| Authority | Target | Finding | Disposition |
| --- | --- | --- | --- |
| Lu Xun | `A Madman's Diary` | Project Gutenberg has the Chinese original `狂人日記`, eBook 25423. | Downloaded as a text candidate; likely admit-ready after operator review. |
| Premchand | `Godan` | Wikimedia Commons/Wikisource has a Hindi PDF with public-domain claims for India and the United States. | Downloaded as a PDF candidate; needs text extraction/inspection before admission. |
| Sun Yat-sen | `Three Principles of the People` | Wikimedia Commons has a 1920 English PDF scan with public-domain scan/original assertions. | Candidate path found; not downloaded in this pass because the file is large and needs PDF extraction planning. |
| Qiu Jin | selected writings | Chinese Wikisource author page lists original works and states the author's original works are public domain worldwide because she died more than 100 years ago. | Candidate source family found; needs exact work selection and extraction from Wikisource pages. |
| Kang Youwei / Liang Qichao | reform tradition | Chinese Wikisource has Kang `大同書` and Liang pages including `少年中國說`, `新民說`, and reform essays. | Candidate source family found; composite boundary still needs exact body selection. |

## Follow-Up Results 2026-08-23

- Premchand `Godan`: PDF extraction produced text for 611/611 pages.
  Candidate can move to an admission proposal after rights/source review names
  the extracted text as the admitted body rather than the PDF scan.
- Sun Yat-sen `Three Principles of the People`: Commons PDF was downloaded,
  but sampled extraction found no embedded text layer in 15 sampled pages. This
  path is OCR-gated before text-body admission.
- Qiu Jin: exact Wikisource raw candidates downloaded for the author page,
  `中國女報發刊詞`, `滿江紅`, and `致徐小淑絕命詞`. These are candidate
  selected-writings bodies pending admission proposal review.
- Kang/Liang: exact Wikisource raw candidates downloaded for Kang `大同書/甲部`
  and Liang `少年中國說` plus `新民說/第一節`. These are candidate composite
  tradition bodies pending admission proposal review.

## Still Blocked Or Rights-Restricted

- B. R. Ambedkar `Annihilation of Caste`: located Columbia classroom text, but
  the site describes editorial work and rights-holder uncertainty. Treat as
  not admit-ready without a stronger public-domain or permission path.
- Fukuzawa Yukichi `Encouragement of Learning`: located excerpts and modern
  translations, but no complete admit-ready public-domain English body was
  found in this pass.
- Natsume Soseki `Kokoro`: previously located English web translation is
  permissioned; `Botchan` remains only a supplemental/fallback admitted path.

## Private Candidate Downloads

| Candidate | Type | Bytes | SHA-256 | Status |
| --- | --- | ---: | --- | --- |
| `LU-XUN-MADMANS-DIARY-CHINESE-PG25423.txt` | text | 34354 | `4e21c52f54a353dfb91c18dd86333bac4f17c5c62a8729fca6e8f1bb2c330a1c` | downloaded |
| `PREMCHAND-GODAN-WIKISOURCE-PDF.pdf` | pdf | 2373688 | `c63b63e3fcab79cf1614fd285703b12a0fb3c6950b6d57f7b7005ec99c8930e3` | downloaded |
| `PREMCHAND-GODAN-WIKISOURCE-PDF-extracted.txt` | extracted text | 1953124 | `580fcd3795241ab0639de963275d7adec7df6b5ebe72404c02ead6d641f4b0ef` | extracted; admission-proposal-ready after review |
| `SUN-THREE-PRINCIPLES-COMMONS-PDF.pdf` | pdf | 107903450 | `00876792be48ec26d2b2072d2582217b0d29bc75cf145fb070e1a65e45a968d0` | downloaded; OCR-gated |
| `QIU-JIN-WOMENS-JOURNAL-PREFACE.wikisource-raw.txt` | Wikisource raw text | 3218 | `9206c47a326def2f2ffc99b4cafdb2c367216023c7ce4f1da195c585a07b09f6` | downloaded |
| `QIU-JIN-MANJIANGHONG.wikisource-raw.txt` | Wikisource raw text | 490 | `d6592fed086d0e5af15ef44a320520b8781fb7423825a9532650c30d71352064` | downloaded |
| `QIU-JIN-DEATH-LETTER.wikisource-raw.txt` | Wikisource raw text | 609 | `f7766c0dbd4100607541b8ded8b1199a34fe25ed709d6fb69028773127eb2f13` | downloaded |
| `KANG-DATONGSHU-JIABU.wikisource-raw.txt` | Wikisource raw text | 103837 | `23c33e34baeca24925f515325bbe1eb958a7fbc7e65dac4a3f16bed07b5338d5` | downloaded |
| `LIANG-YOUNG-CHINA.wikisource-raw.txt` | Wikisource raw text | 11642 | `10ebc9ebfb85585af47fa582ab55cd9a6059205c4227e69fba60b8dc57182e64` | downloaded |
| `LIANG-NEW-CITIZEN-1.wikisource-raw.txt` | Wikisource raw text | 1423 | `b5096c95ea3bd06a61804359a0d9242a566e92367311e5efd2d7df0713126eaa` | downloaded |

## Next Gate

The narrowest next gate is a supplemental admission proposal for Premchand,
Qiu Jin, and Kang/Liang text candidates. Sun requires OCR before admission.
Ambedkar, Fukuzawa, and Soseki `Kokoro` remain rights/path blocked.

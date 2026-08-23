# Industrial Body Research Batch 002 Inspection Receipt

Status: `inspection-complete-admission-proposal-ready`
Era: `industrial`
Batch: `industrial-body-research-batch-002`
Metadata batch: `archive/library/industrial/metadata-batch-design-v0.1.md`
Private inspection root: `C:\private\mira-library-inspection\industrial-batch002`

## Boundary

This receipt records source research and private candidate downloads only. It
does not admit source bodies, ingest into the private Archive, claim complete
authority coverage, stage, commit, push, or publish.

Batch 002 registry metadata stubs were locally added for the 12 authorities in
the committed Batch 002 design. Source-body candidates were downloaded into the
private inspection root for admission review. The downloaded files are not Git
artifacts.

## Results

- Authorities covered by candidate downloads: 12.
- Candidate files attempted: 20.
- Candidate files downloaded: 20.
- Candidate files with Project Gutenberg header/chrome detected: 20.
- Candidate files mechanically passing minimum-size and hash capture: 20.
- Candidate files proposed as admit-ready pending operator authorization: 20.

## Candidate Disposition

| Authority | Candidate | PG ID | Bytes | SHA-256 | Disposition |
| --- | --- | --- | ---: | --- | --- |
| Karl Marx | `The Communist Manifesto` | 61 | 94315 | `ba4623f09e411351ad4f34488289c70eceda8fb9d7977c1db64f0f01ed80cb59` | ready for admission proposal as selected coauthored work |
| Karl Marx | `A Contribution to the Critique of Political Economy` | 46423 | 541130 | `d01f83d5c8d1d726406fa583d282b709402aae156c1940252e370ca856fade9c` | ready for admission proposal as supplemental Marx political-economy work |
| Friedrich Engels | `The Condition of the Working-Class in England in 1844` | 17306 | 736497 | `25ff9b6ba4bef75632145e785f86acfaeeb0b437fd7f8f5409bf103eed7ae93b` | ready for admission proposal |
| John Stuart Mill | `On Liberty` | 34901 | 331189 | `cfc8de9ac48709ef8e66922b32bac51335c883082e4da24251e1290816df904c` | ready for admission proposal |
| John Stuart Mill | `The Subjection of Women` | 27083 | 278619 | `ed7238e072be4c3c4a0478c725d6d1b27698b786c0b46958e501a679fd605319` | ready for admission proposal |
| Alexis de Tocqueville | `Democracy in America Volume 1` | 815 | 1151189 | `734b3b0352dc2ec312a6b2b9e9165aac054439eee2d6e8d83d1fd9a35d1c9e2d` | ready for admission proposal |
| Alexis de Tocqueville | `Democracy in America Volume 2` | 816 | 866238 | `1c9c747231b90370f0cd79bf0758be5df7dcb33d0354a050467328c679d0ccf4` | ready for admission proposal |
| Charles Darwin | `On the Origin of Species` | 2009 | 1303005 | `27c02feed0b90e0163811a35a7565d03611dc1d3f86703d6bec4ae73d2d612b8` | ready for admission proposal |
| Charles Darwin | `The Descent of Man` | 2300 | 1909144 | `2911dfcc2b0b498fe92ad9bd7e2c712046edb448eb6fe3bd669bcf9629adf8fd` | ready for admission proposal |
| Alfred Russel Wallace | `The Malay Archipelago` | 2530 | 676092 | `d4b343bde8af87ea34810f86d64743f0d75de78617ab12fe95e04157a7efa206` | ready for admission proposal |
| Charles Babbage | `On the Economy of Machinery and Manufactures` | 4238 | 645369 | `08cfd812da8c31ceb2085f7a01cb54c3073c84dd2f7dd5a65285c3f1d3358ace` | ready for admission proposal |
| Florence Nightingale | `Notes on Nursing` | 17366 | 286169 | `6b013673690bfa5f4f8f80e842eb92adc7292d1dff717077cc38e9655d62af06` | ready for admission proposal |
| Florence Nightingale | `Sanitary Statistics of Native Colonial Schools and Hospitals` | 52653 | 404160 | `924b6dc4082d8238a808b8aec98bbc9033294613beb5310ff00f907f6d43e360` | ready for admission proposal |
| Henry David Thoreau | `Civil Disobedience` | 71 | 72261 | `88310a64ab17a33347228deb109dc67f089c7313ef30e97d7870449612a77c98` | ready for admission proposal |
| Henry David Thoreau | `Walden` | 205 | 667957 | `2d9a76a2e3e8195c69430516ebd33c4d0757a53ad432ff6186b7b794e6fe99f9` | ready for admission proposal |
| John Ruskin | `Unto This Last and Other Essays` | 36541 | 737417 | `3407c93e8ab6818646140fde715f90cbfed000f9342619aeb2157dad9c33bf72` | ready for admission proposal |
| William Morris | `News from Nowhere` | 3261 | 450589 | `350beb623c7574515535a283adf7d2a78de4230c9b4b1e8f238b8b9a252661b1` | ready for admission proposal |
| Ida B. Wells | `Southern Horrors` | 14975 | 77101 | `aed82d6ba21e6b54622dc2ae6b8895e0528e09fc2f9afdce90d24cce7a5b69d5` | ready for admission proposal |
| Ida B. Wells | `The Red Record` | 14977 | 221004 | `2fdfd650c9da72e36ef5c5d06a682f045d5b84fc57c207a2a0ea1d9bd88bf722` | ready for admission proposal |
| Ida B. Wells | `Mob Rule in New Orleans` | 14976 | 145179 | `fd4ee9bcea3af29063f3c7c92c22c2ac0d580000fbe9c45ea3401498de67c6d1` | ready for admission proposal |

## Caveats

- Karl Marx's Batch 002 target includes `Capital`, but no clean Project
  Gutenberg English text body was admitted through this inspection pass.
  `A Contribution to the Critique of Political Economy` is preserved here as a
  supplemental political-economy candidate, not as a substitute for `Capital`.
- `The Communist Manifesto` is coauthored by Marx and Engels. If admitted under
  Marx, the body record must preserve coauthorship and avoid implying Engels
  absence from the text.
- Tocqueville is represented by the two `Democracy in America` volumes only in
  this pass; `Old Regime` remains unresolved.
- Nightingale is represented by `Notes on Nursing` and one sanitary-statistical
  report; this is a selected-works lane, not a complete report corpus.
- Morris is represented by `News from Nowhere`; essay expansion remains open.
- Ruskin's Project Gutenberg candidate includes `Unto This Last` with other
  political-economy essays, so the body title must preserve the edition scope.

## Acceptance Tests

- Candidate bodies are stored only in the private inspection root.
- Every downloaded candidate has captured URL, byte count, SHA-256, and header
  detection.
- No private text payload is admitted by this receipt.
- No Archive catalog ingestion, staging, commit, push, or publication occurred.

# Tanzil Uthmani Version 1.1 — Candidate Inspection

Date: 2026-08-19
Status: `reviewed-candidate-not-admitted`
Candidate: `MED-CAND-024`
Authority effect: `none`

## Result

The inspected Tanzil Uthmani Version 1.1 candidate passes mechanical structure and notice checks. It remains a candidate, not an admitted, verified, reviewed-authority, or maturity-advanced body.

Preferred treatment: preserve the downloaded bytes verbatim. Do not normalize whitespace, line endings, Unicode composition, headers, or Arabic text in place.

## Retrieval

- Official endpoint: [Tanzil download](https://tanzil.net/pub/download/index.php?quranType=uthmani&outType=txt-2&agree=true)
- Upstream filename: `quran-uthmani.txt`
- Variant: `uthmani`
- Format: `txt-2` — `sura|aya|text`
- Optional pause, sajdah, rub-el-hizb, tatweel, and sequential-tanween form parameters: omitted
- Advertised release: Version 1.1, February 2021
- Inspected copy: temporary external file only

## Mechanical Receipt

| Check | Result |
| --- | --- |
| Bytes | 1,370,878 |
| SHA-256 | `bf4f57b968d03f4131c070b1e285da9be0e0a108a21c910e872801ca273312c8` |
| Encoding | strict UTF-8, no BOM |
| Line endings | LF |
| Total lines | 6,266 |
| Verse records | 6,236 |
| Unique sura/aya pairs | 6,236 |
| Sura range | 1–114 |
| First / last pair | 1:1 / 114:6 |
| Duplicate pairs | 0 |
| Empty verse bodies | 0 |
| Intra-sura numbering gaps | 0 |
| Notice lines | 28, beginning at line 6,239 |

These checks establish internal file shape only. They do not independently establish theological, philological, or recital equivalence.

## Rights Inspection

The embedded notice identifies the work as **Tanzil Quran Text (Uthmani, Version 1.1)** under **Creative Commons Attribution 3.0**, with additional stated conditions:

- distribution must be verbatim and the text must not be changed;
- Tanzil Project must be identified as the source;
- users must be linked to Tanzil so they can track changes;
- the copyright block must remain in verbatim copies and substantial derivatives.

The upstream [license page](https://tanzil.net/docs/Text_License) and embedded notice agree on these requirements. Tanzil describes all download types as UTF-8 and Version 1.1 as the current release; its [change log](https://tanzil.net/updates/) dates Version 1.1 to February 12, 2021.

Rights posture: `plausible-open-with-additional-condition`. This is stronger than `unknown`, but it is not final Library Import approval.

## Coverage Boundary

- Source ceiling: `principal-work`.
- Body ceiling: **Hafs Uthmani reference text only**.
- Excluded: other readings, manuscript witnesses, translations, tafsir, annotations, and other Tanzil variants.
- Maturity remains Level 3; the projected ceiling remains Level 6.
- No Arabic–English equivalence claim is available.

## Admission Blockers

1. Decide whether the extra no-change condition is compatible with the library's open-license rule.
2. Decide how the private store will preserve the upstream copyright block and exact bytes while also satisfying Mira's body-header requirement.
3. Perform an independent second retrieval or official checksum comparison.
4. Inspect and license an English translation separately.
5. Bind any eventual coverage claim expressly to the Hafs Uthmani reference text.

## Persistence and Authority

The inspected file remains at `private-inspection-root:tanzil-inspection-20260819\quran-uthmani-v1.1-txt-2.txt`, outside both Git and the private Library text store. This receipt and its JSON companion are repository-local, untracked review artifacts.

No registry, era index, library text store, maturity record, staging, commit, push, or publication change occurred.

# Medieval Body Admission Batch 11

**Batch:** `MEDIEVAL-BODY-ADMISSION-11`
**Date:** 2026-08-19
**Status:** completed with isolated failures

Batch 11 inspected the ten authorized authorities and admitted six bodies. The Medieval shelf now contains **60 authorities, 87 bodies, and 78,531,424 registered text bytes**. Ancient remains at **56 authorities and 193 bodies**; this batch narrows body-count parity from 112 to 106.

## Admitted bodies

| Authority | Body | Language | Coverage | Bytes |
| --- | --- | --- | --- | ---: |
| Constantine VII | *De administrando imperio*, chapters 30–36, Tomašić/Wikisource | Serbian | selected passages | 49,414 |
| Michael Psellos | *Chronographia*, Greek Wikisource seven-book body | Greek | complete work, edition-bounded | 976,272 |
| *Kebra Nagast* tradition | Budge 1922 English, Internet Archive OCR | English | complete work, OCR/edition-bounded | 742,056 |
| Judah Halevi | Hirschfeld 1905 *Kuzari*, Wikisource | English | complete work; annotations omitted | 446,863 |
| Ibn Jubayr | *Rihla*, available Wikisource sections | Arabic | partial work | 109,498 |
| Ibn Battuta | *Rihla*, available volume-I chapter transcription | Arabic | partial work | 99,934 |

No admission implies original/translation equivalence, critical-edition completeness, complete surviving corpus, reviewed status, or Level 6 maturity.

## Isolated failures

- **Michael the Syrian:** three Chabot volumes were retrieved, but their OCR contains systematic errors and damaged multilingual apparatus.
- **Domesday Book:** Open Domesday uses CC-NC-BY-SA, and the National Archives route did not yield a clean portable text with sufficiently simple reuse terms.
- **al-Masudi:** the identified Arabic Wikisource route is scan-only.
- **Secret History of the Mongols:** two Chinese edition routes were identified, but API rate limiting interrupted both exports; no partial file was admitted. The fifteen-volume witness also carries an incomplete-transcription warning.

## Validation

- `library validate --json`: passed.
- `library render-index --check --json`: passed with no stale paths; 280 bodies indexed.
- `library verify-texts --json`: passed, 266 checked, zero failures; 37 source records remain without available bodies.
- `tests/test_archive_library.py`: 24 passed.

The registry, private text store, root source index, and Medieval index changed. Nothing was staged, committed, pushed, published, or imported into the broader Archive catalog.

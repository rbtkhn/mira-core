# Bede Sellar 1907 / Gutenberg 38326 — Body Inspection

Date: 2026-08-19
Status: `inspected-not-admitted`
Authority effect: `none`

## Result

Project Gutenberg ebook 38326 passes the bounded mechanical and identity inspection. It is a credible candidate for later admission as an English body of Bede's *Ecclesiastical History*, with an edition-specific ceiling of `complete-work-english-sellar-1907` and a source-level ceiling of `principal-work`.

It is **not admitted**. Inspection does not establish equivalence to an original-language body, coverage of Bede's complete surviving corpus, or rights outside the United States.

## Body Identity

| Field | Inspected value |
| --- | --- |
| Candidate | `MED-CAND-013` |
| Proposed authority record | `LIB-MEDIEVAL-AUTHORITY-013-BEDE` |
| Upstream | Project Gutenberg ebook 38326 |
| Title | *Bede's Ecclesiastical History of England* |
| Translator | A. M. Sellar |
| Edition | *A Revised Translation*, George Bell and Sons, London, 1907 |
| Language | English |
| Format | Plain text, UTF-8, CRLF |
| Bytes | 1,093,654 |
| Lines | 21,876 |
| SHA-256 | `977da0babf070c825befb0a5db65a9cc2440d9ab45aa869a959c1bab911be2c8` |
| Private inspection file | `private-inspection-root:bede-inspection-20260819\pg38326.txt` |

Source: [Project Gutenberg landing record](https://www.gutenberg.org/ebooks/38326) and [UTF-8 text route](https://www.gutenberg.org/ebooks/38326.txt.utf-8).

## Inspection Checks

- Header matches Bede, the work title, A. M. Sellar, ebook number 38326, and the 2011 release / 2020 update metadata.
- Front matter identifies the revised translation, George Bell and Sons, London, 1907.
- The file is valid UTF-8 with no NUL bytes and no Unicode replacement characters.
- It contains one Gutenberg start marker, one Gutenberg end marker, and the included Gutenberg license.
- The body contains exactly one structural marker for each of `BOOK I` through `BOOK V`, separate from the contents entries.
- Book V, chapter XXIV—the chronological recapitulation and author/work notice—is present.
- The Gutenberg wrapper, edition front matter, introduction, notes, index, and license remain unmodified. No normalization or wrapper stripping occurred.

## Rights and Coverage

Project Gutenberg states that the ebook is public domain in the United States and warns users outside the United States to check local law. The research posture remains `plausible-open`; a final admission license decision has not been made.

The strongest defensible body claim is `complete-work-english-sellar-1907`: all five books represented by this edition are present. The authority-level claim must remain `principal-work`, because this is one translated work rather than Bede's complete surviving corpus. No English/Latin equivalence claim is permitted.

## Persistence and Boundaries

- The exact downloaded body remains only in the private inspection root shown above.
- The private Mira Library text store was not changed.
- No registry or Medieval index changed.
- Nothing was staged, committed, pushed, or published.
- A later admission proposal must preserve the unmodified bytes, hash, Gutenberg license, edition identity, jurisdiction caveat, and English-only coverage ceiling.

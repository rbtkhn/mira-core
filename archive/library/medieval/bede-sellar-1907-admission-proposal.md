# Bede Sellar 1907 — Admission Proposal

Date: 2026-08-19
Status: `proposal-only`
Authority effect: `none`

## Recommendation

Admit Bede in two separately reviewable stages if implementation is later authorized:

1. Add a `located` Medieval authority record with `text_status: missing` and no bodies.
2. After registry validation, dry-run and then separately authorize admission of the unmodified Gutenberg file as an English `complete-work` body.

The source authority should remain `principal-work`. The body may be complete for Sellar's named 1907 English edition without implying a verified Latin counterpart, English/Latin equivalence, Bede's full surviving corpus, reviewed status, or Level 5–6 maturity.

## Proposed Source Record

| Field | Proposal |
| --- | --- |
| Source ID | `LIB-MEDIEVAL-AUTHORITY-013-BEDE` |
| Title | *Historia ecclesiastica gentis Anglorum* |
| Authority | Bede the Venerable |
| Composition | c. 731 |
| Era basis | `composition_period` |
| Shelf | `medieval` |
| Type | `chronicle` |
| Civilization tags | `britain`, `latin-christendom` |
| Registry status | `located` |
| Initial text status | `missing` |
| Source coverage | `principal-work` |
| Initial bodies | none |

The initial coverage note should state that the record is scoped to the *Ecclesiastical History*. A later Sellar admission would cover one complete English edition, not a verified Latin edition or Bede's complete surviving corpus.

## Proposed Body

| Field | Proposal |
| --- | --- |
| Body ID | `LIB-MEDIEVAL-AUTHORITY-013-BEDE-ECCLESIASTICAL-HISTORY-SELLAR-1907-GUTENBERG-38326` |
| Private candidate | `private-inspection-root:bede-inspection-20260819\pg38326.txt` |
| Expected logical URI | `library-text://LIB-MEDIEVAL-AUTHORITY-013-BEDE-ECCLESIASTICAL-HISTORY-SELLAR-1907-GUTENBERG-38326.txt` |
| Language | `english` |
| Translator | A. M. Sellar |
| Edition | George Bell and Sons, London, 1907; Project Gutenberg 38326 |
| Encoding | UTF-8 |
| Bytes | 1,093,654 |
| SHA-256 | `977da0babf070c825befb0a5db65a9cc2440d9ab45aa869a959c1bab911be2c8` |
| Proposed license | `public-domain` with US-only claim and retained Gutenberg warning/license |
| Body coverage | `complete-work` for this named English edition only |
| Initial body status | `available`, never `verified` by admission alone |

The file should be copied without normalization. Its Gutenberg header, footer, license, edition front matter, introduction, notes, and index are part of the inspected provenance body.

## Gates

1. **Metadata authorization:** add the exact `located` record and validate the registry.
2. **Rights judgment:** explicitly accept `public-domain` as the US registry posture while preserving Gutenberg's jurisdiction warning.
3. **Integrity:** immediately recheck the recorded byte count and SHA-256.
4. **Import dry-run:** run Library Import with `--check`; the current dry-run is blocked because the source record does not yet exist.
5. **Admission authorization:** only a new explicit command may copy the file into the configured private text store and update the registry.
6. **Post-admission validation:** run `library validate`, `render-index --check`, `verify-texts`, and `tests/test_archive_library.py`, with Medieval index reconciliation governed by the separately accepted implementation contract.

## Maturity Ceiling

- Metadata record only: Level 1.
- Admitted readable English body: Level 2.
- After subsequent verification and clean edition/license notes: no higher than Level 4.
- Level 5 requires a verified Latin counterpart and an explicit relationship between the editions.
- Level 6 requires honest mature modeling of all edition and coverage limits; it is not authorized by this proposal.

## Persistence and Authority

The machine-complete proposal is in [bede-sellar-1907-admission-proposal.json](./bede-sellar-1907-admission-proposal.json). The inspected file remains in its private inspection root. This proposal changes no registry, index, private library body, status, staging area, commit, remote, Archive catalog, or publication surface.

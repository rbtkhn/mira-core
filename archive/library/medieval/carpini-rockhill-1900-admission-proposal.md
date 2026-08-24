# John of Plano Carpini, Rockhill 1900 — Admission Proposal

Date: 2026-08-20
Status: `proposal-only`
Authority effect: `none`

## Recommendation

After the 62-authority roster expansion and Carpini metadata record are separately authorized, admit the privately collated Rockhill 1900 English first account as `complete-work` for that explicitly bounded translated body. Keep the authority at `principal-work`, and do not infer Latin equivalence, complete-surviving-corpus coverage, reviewed status, or Level 5–6 maturity.

## Proposed Source Record

| Field | Proposal |
| --- | --- |
| Source ID | `LIB-MEDIEVAL-AUTHORITY-077-JOHN-OF-PLANO-CARPINI` |
| Title | *Historia Mongalorum* |
| Authority | John of Plano Carpini |
| Composition | c. 1247 |
| Era basis | `composition_period` |
| Shelf | `medieval` |
| Type | `primary` |
| Civilization tags | `latin-christendom`, `mongol-empire`, `inner-asia` |
| Registry status | `located` |
| Initial text status | `missing` |
| Source coverage | `principal-work` |

The authority boundary excludes Benedict the Pole's companion account, Vincent of Beauvais's abridgment, and the complete family of Carpini recensions and manuscripts.

## Proposed Body

| Field | Proposal |
| --- | --- |
| Body ID | `LIB-MEDIEVAL-AUTHORITY-077-CARPINI-JOURNEY-ROCKHILL-1900-EN` |
| Private candidate | `private-inspection-root:medieval-narrow-batch-20260820\carpini-rockhill-1900-collated.txt` |
| Expected logical URI | `library-text://LIB-MEDIEVAL-AUTHORITY-077-CARPINI-JOURNEY-ROCKHILL-1900-EN.txt` |
| Work | *The Journey of Friar John of Pian de Carpine to the Court of Kuyuk Khan, 1245–1247* |
| Language | English |
| Translator/editor | W. W. Rockhill |
| Edition | Hakluyt Society, London, 1900, printed pages 1–32 |
| Encoding | UTF-8 |
| Bytes | 43,293 |
| SHA-256 | `5171cfce829eed4f9422a73b1bf3aaac52519dd950abd6d6974b69fac5842bc1` |
| Proposed license | `public-domain`, United States posture pending final jurisdiction note |
| Body coverage | `complete-work` for the first Rockhill Carpini account only |
| Initial body status | `available`, never `verified` by admission alone |

The candidate was derived from the University of Washington transcription and compared page by page against the Internet Archive scan of Rockhill 1900. All 32 printed pages align; 22 lexical correction groups and punctuation or line-break repairs were source-supported. Modern wrapper and later annotation were excluded. This transformation lineage must be preserved in the body header or linked admission receipt.

## Required Gates

1. Accept the 62-authority roster exception and create the exact `located` Carpini metadata record.
2. Bind the derivation lineage, final United States public-domain rationale, and non-US jurisdiction caution in the admission header.
3. Recheck the exact byte count and SHA-256 immediately before dry-run.
4. Run Library Import in check mode against the exact proposed metadata and private file.
5. Require a separate explicit admission command before copying the body or mutating the registry.
6. After admission, run library validation, index drift checking, text verification, and the archive-library tests.

## Maturity Ceiling

- Metadata only: Level 1.
- Admitted readable English body: Level 2.
- After edition, hash, license, and coverage verification: no higher than Level 4.
- Level 5 requires a verified Latin counterpart and explicit cross-edition modeling.
- Level 6 remains unavailable until recension, edition, and survival boundaries are maturely documented.

## Persistence and Authority

The source candidate remains private. This working-tree proposal changes no roster, registry, era index, private text store, status, staging area, commit, remote, Archive catalog, or publication surface. The machine-readable counterpart is [carpini-rockhill-1900-admission-proposal.json](./carpini-rockhill-1900-admission-proposal.json).

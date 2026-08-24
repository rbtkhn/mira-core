# Dante *Commedia* — Two-Body Admission Proposal

Date: 2026-08-19
Status: `proposal-only`
Authority effect: `metadata-only`

## Recommendation

If body admission is separately authorized, process the inspected Italian and
Cary English Gutenberg files as one bounded pair. The registry now contains a
conservative Dante authority record with `text_status: missing` and no bodies;
this proposal does not admit either file.

The authority boundary is the *Commedia* only. The two candidates may each be
complete as a named body without establishing a critical edition for the
Italian text, cross-language equivalence, a preferred text, or Dante's complete
surviving corpus.

## Current Source Record

| Field | Value |
| --- | --- |
| Source ID | `LIB-MEDIEVAL-AUTHORITY-018-DANTE-ALIGHIERI` |
| Title | *Commedia / Divine Comedy* |
| Composition | c. 1308–1321 |
| Shelf | `medieval` |
| Type | `literary` |
| Civilization tags | `italian-peninsula`, `latin-christendom` |
| Registry status | `located` |
| Text status | `missing` |
| Source coverage | `principal-work` |
| Admitted bodies | none |

## Proposed Pair

| Body | Language | Bytes | SHA-256 | Ceiling |
| --- | --- | ---: | --- | --- |
| Gutenberg 1000, *La Divina Commedia di Dante: Complete* | Italian | 597,903 | `4669dcc00ee61ceffe92d871e61ea430cec87b35cbab24f19a4c0b1c7da521b2` | `complete-work` for this unnamed-lineage Gutenberg body |
| Gutenberg 8800, Cary, *The Divine Comedy* | English | 656,728 | `3a7dd97b5fec82456c58237b33383a593480c2bfe088aeaaa4a519de2a10d39c` | `complete-work` for this named Cary translation |

Both files retain their complete Gutenberg wrappers, license language, and
non-US jurisdiction warnings. The Italian candidate contains *Inferno*,
*Purgatorio*, and *Paradiso*, but the file does not name its critical editor or
upstream print edition. That absence is a controlling provenance limit, not a
field to infer. The Cary body contains *Hell*, *Purgatory*, and *Paradise* and
is not asserted to be textually equivalent to the Italian candidate.

## Required Gates

1. Recheck both private-source byte counts and SHA-256 hashes.
2. Preserve the unidentified Italian edition lineage in registry notes.
3. Run Library Import dry-run for both bodies before admitting either.
4. Obtain separate authorization for the bundled body admission.
5. After any later admission, validate the registry, index rendering, private
   text hashes, and archive-library tests.

Metadata-only maturity is Level 1. A later readable paired admission would
support Level 2, but the record must remain no higher than Level 4 without an
identified and verified Italian edition lineage. Level 5–6, reviewed status,
and cross-language equivalence are not authorized.

## Persistence and Authority

The exact machine proposal is
[`dante-commedia-admission-proposal.json`](dante-commedia-admission-proposal.json).
The inspected files remain under
`private-inspection-root:medieval-portable-batch-05-20260819`. No file was copied
into the managed private store; no body was admitted, staged, committed,
pushed, published, or ingested into Archive.

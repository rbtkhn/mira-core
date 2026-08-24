# Marco Polo Yule-Cordier Paired-Body Admission Proposal

Date: 2026-08-19
Status: `proposal-only`
Authority effect: none

## Source Record

| Field | Value |
| --- | --- |
| Source ID | `LIB-MEDIEVAL-AUTHORITY-074-MARCO-POLO-RUSTICHELLO-TRADITION` |
| Authority | Marco Polo and Rustichello of Pisa textual tradition |
| Work | *Devisement du monde / Description of the World* |
| Record status | `located` |
| Text status | `missing` |
| Coverage ceiling | `principal-work` |

The authority is modeled as a collaborative multilingual textual tradition.
The Yule-Cordier translation is one later English editorial edition. It is not
equivalent to BnF français 1116, does not resolve the divergent medieval
witnesses, and does not establish a single recoverable authorial text.

## Proposed Paired Bodies

| Volume | Body ID | Bytes | SHA-256 | Body ceiling |
| --- | --- | ---: | --- | --- |
| I | `LIB-MEDIEVAL-AUTHORITY-074-MARCO-POLO-YULE-CORDIER-VOL-1-GUTENBERG-10636` | 2,345,876 | `7b0cbb0bc47a48d7594314b56d890e3e43ac05666b8c70d98f10719501cf6fb5` | `partial-work` |
| II | `LIB-MEDIEVAL-AUTHORITY-074-MARCO-POLO-YULE-CORDIER-VOL-2-GUTENBERG-12410` | 2,421,259 | `c1ce61dd8c6c6a326c42fb7ac3b1a63767bf1685ec88354f83dd321e1748921c` | `partial-work` |

Both are strict UTF-8 Project Gutenberg files with complete start/end wrappers
and embedded licenses. Each remains `partial-work`; only the pair represents
the complete named Yule-Cordier English edition.

## Execution Gates

1. Recheck both byte counts and SHA-256 hashes immediately before execution.
2. Run both Library Import dry-runs before admitting either body.
3. Admit both as one bundled action; never describe either volume alone as the
   complete work.
4. Preserve Gutenberg's United States public-domain assertion, complete
   wrapper, license, and non-US jurisdiction warning.
5. After admission, run Library validation, index drift detection, body
   verification, and the focused Library regression suite once for the pair.

The exact machine proposal is
[`marco-polo-yule-cordier-admission-proposal.json`](marco-polo-yule-cordier-admission-proposal.json).

## Maturity and Non-Authorization

Metadata alone supports Level 1. Available paired bodies would support Level 2,
not review or cross-language maturity. Without an inspected original-language
witness, the ceiling remains Level 4.

This proposal does not authorize private-store copying, body admission,
`verified` or `reviewed` status, English/original-language equivalence,
staging, commit, push, Archive ingestion, or publication.

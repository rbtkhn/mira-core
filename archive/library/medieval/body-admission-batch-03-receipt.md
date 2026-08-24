# Medieval Body Admission Batch 03

Date: 2026-08-19
Status: success with one review debt

The operator confirmed that they hold all rights for the four exact candidate bodies. The registry records them as `permissioned`; this operator assertion was not independently adjudicated as a public-domain or open-license claim.

## Admitted

| Authority | Body | Status | Bytes |
| --- | --- | --- | ---: |
| Anna Komnene | Dawes/Fordham-derived complete *Alexiad* | `available` | 1,067,054 |
| Benedictine rule tradition | Doyle, *St. Benedict's Rule for Monasteries* | `available` | 149,066 |
| Qur'anic textual tradition | unchanged Tanzil Uthmani v1.1 Hafs reference text | `available` | 1,370,878 |
| Magna Carta tradition | National Archives 1215 English translation, PDF-derived | `needs-review` | 26,148 |

The Magna Carta source PDF was rendered and all eight pages were visually reviewed. Clauses 1-63 and the concluding dating formula are present, but minor text-layer spacing defects remain. The body and source therefore remain `needs-review`.

## Shelf state

- Medieval: 60 authorities, 38 bodies, 40,839,652 bytes.
- Entire managed store: 231 bodies.
- One Medieval body is `needs-review`; the other three new bodies are `available`.
- Library validation and index drift checks pass; 230 available bodies verify with zero failures.
- `tests/test_archive_library.py`: 24 passed.

No Archive import, staging, commit, push, or publication occurred.

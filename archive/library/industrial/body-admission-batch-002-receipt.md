# Industrial Body Admission Batch 002 Receipt

Status: `completed-with-private-store-caveat`
Era: `industrial`
Batch: `industrial-body-admission-batch-002`
Private text root: `C:\private\mira-library-texts`

## Boundary

This receipt records admission of Batch 002 source bodies into the private Mira Library text store and registry body metadata. It does not ingest into the private Archive, stage, commit, push, or publish.

## Results

- Authorities admitted: 12.
- Bodies admitted: 20.
- Private payloads present: 20/20.
- SHA-256 matches: 20/20.
- Byte-count matches: 20/20.
- Archive catalog ingests: 0.

## Admitted Bodies

| Authority | Body ID | Work | Bytes | Hash checked |
| --- | --- | --- | ---: | --- |
| Karl Marx | `LIB-INDUSTRIAL-AUTHORITY-029-MARX-CONTRIBUTION-PG46423` | A Contribution to the Critique of Political Economy | 541130 | yes |
| Karl Marx | `LIB-INDUSTRIAL-AUTHORITY-029-MARX-MANIFESTO-PG61` | The Communist Manifesto | 94315 | yes |
| Friedrich Engels | `LIB-INDUSTRIAL-AUTHORITY-030-ENGELS-CONDITION-PG17306` | The Condition of the Working-Class in England in 1844 | 736497 | yes |
| John Stuart Mill | `LIB-INDUSTRIAL-AUTHORITY-031-MILL-ON-LIBERTY-PG34901` | On Liberty | 331189 | yes |
| John Stuart Mill | `LIB-INDUSTRIAL-AUTHORITY-031-MILL-SUBJECTION-PG27083` | The Subjection of Women | 278619 | yes |
| Alexis de Tocqueville | `LIB-INDUSTRIAL-AUTHORITY-032-TOCQUEVILLE-DEMOCRACY-V1-PG815` | Democracy in America, Volume 1 | 1151189 | yes |
| Alexis de Tocqueville | `LIB-INDUSTRIAL-AUTHORITY-032-TOCQUEVILLE-DEMOCRACY-V2-PG816` | Democracy in America, Volume 2 | 866238 | yes |
| Charles Darwin | `LIB-INDUSTRIAL-AUTHORITY-038-DARWIN-DESCENT-PG2300` | The Descent of Man | 1909144 | yes |
| Charles Darwin | `LIB-INDUSTRIAL-AUTHORITY-038-DARWIN-ORIGIN-PG2009` | On the Origin of Species | 1303005 | yes |
| Alfred Russel Wallace | `LIB-INDUSTRIAL-AUTHORITY-039-WALLACE-MALAY-PG2530` | The Malay Archipelago | 676092 | yes |
| Charles Babbage | `LIB-INDUSTRIAL-AUTHORITY-041-BABBAGE-ECONOMY-PG4238` | On the Economy of Machinery and Manufactures | 645369 | yes |
| Florence Nightingale | `LIB-INDUSTRIAL-AUTHORITY-042-NIGHTINGALE-NOTES-NURSING-PG17366` | Notes on Nursing | 286169 | yes |
| Florence Nightingale | `LIB-INDUSTRIAL-AUTHORITY-042-NIGHTINGALE-SANITARY-STATS-PG52653` | Sanitary Statistics of Native Colonial Schools and Hospitals | 404160 | yes |
| Henry David Thoreau | `LIB-INDUSTRIAL-AUTHORITY-043-THOREAU-CIVIL-DISOBEDIENCE-PG71` | Civil Disobedience | 72261 | yes |
| Henry David Thoreau | `LIB-INDUSTRIAL-AUTHORITY-043-THOREAU-WALDEN-PG205` | Walden | 667957 | yes |
| John Ruskin | `LIB-INDUSTRIAL-AUTHORITY-044-RUSKIN-UNTO-THIS-LAST-PG36541` | Unto This Last, and Other Essays on Political Economy | 737417 | yes |
| William Morris | `LIB-INDUSTRIAL-AUTHORITY-045-MORRIS-NEWS-NOWHERE-PG3261` | News from Nowhere | 450589 | yes |
| Ida B. Wells | `LIB-INDUSTRIAL-AUTHORITY-083-WELLS-MOB-RULE-PG14976` | Mob Rule in New Orleans | 145179 | yes |
| Ida B. Wells | `LIB-INDUSTRIAL-AUTHORITY-083-WELLS-RED-RECORD-PG14977` | The Red Record | 221004 | yes |
| Ida B. Wells | `LIB-INDUSTRIAL-AUTHORITY-083-WELLS-SOUTHERN-HORRORS-PG14975` | Southern Horrors | 77101 | yes |

## Caveats

- Karl Marx `Capital` remains unresolved; admitted Marx bodies do not substitute for it.
- Tocqueville `Old Regime` remains unresolved.
- Morris essay expansion remains unresolved.
- Global full-library `verify-texts` may still depend on older era payload placement in the selected private text root.

## Acceptance Tests

- Library validation and render-index checks must pass after this receipt.
- Focused library tests must pass after this receipt.
- Industrial Batch 002 private payload check requires 20/20 present, hash-matched, and byte-matched payloads.

# Industrial Library Metadata Batch Design v0.1

Status: `metadata-batch-design`
Era: `industrial`
Range: 1815 AD to 1991 AD
Roster packet: `archive/library/industrial/roster-design-v0.1.md`
Gate: `operator-review-before-registry-mutation`

## Authority Boundary

This packet designs the first three Industrial metadata batches. It does not
mutate `archive/library/library-registry.json`, generate indexes, download
sources, admit source bodies, ingest into the private Archive, stage, commit,
push, or publish.

Every row is a registry-candidate design record only. `metadata-ready` here
means the source identity, proposed source ID, work target, status ceiling, and
rights triage are coherent enough for operator review before any registry
mutation. It does not mean body-research-ready or admission-ready.

## Batch Strategy

The first three batches keep Industrial from becoming Europe-only while still
starting with the most reproducible public-domain and institutionally stable
records. Batch 001 establishes literature and social witness; Batch 002 builds
political economy, labor, science, reform, and environment; Batch 003 opens the
global modernization and anti-colonial frame.

Stop rules:

- Do not mutate the registry until the operator explicitly authorizes a named
  metadata batch.
- Do not download or inspect source bodies from this packet.
- Keep translated, composite, speech, and institutional traditions at
  `body-research-incomplete` until exact edition and rights evidence exists.
- Prefer `selected-works`, `principal-work`, or `principal-works`; do not claim
  complete surviving corpus for any Industrial authority in these batches.

## Batch 001: Public-Domain Industrial Literature And Social Witness

Purpose: establish literature and testimony as the shelf spine with strong
public-domain feasibility.

| Candidate ID | Proposed source ID | Authority | Target title | Primary function | Proposed registry status | Coverage ceiling | Rights/body gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `IND-META-001-001` | `LIB-INDUSTRIAL-AUTHORITY-001-AUSTEN` | Jane Austen | `Persuasion` | `civilization-memory-literature` | `stub` | `principal-work` | public-domain likely; edition still review-required |
| `IND-META-001-002` | `LIB-INDUSTRIAL-AUTHORITY-002-SHELLEY` | Mary Shelley | `Frankenstein` | `civilization-memory-literature` | `stub` | `principal-work` | public-domain likely; edition variant review-required |
| `IND-META-001-003` | `LIB-INDUSTRIAL-AUTHORITY-006-DICKENS` | Charles Dickens | `Hard Times`; `Bleak House` | `civilization-memory-literature` | `stub` | `principal-works` | public-domain likely; multi-work sequencing required |
| `IND-META-001-004` | `LIB-INDUSTRIAL-AUTHORITY-009-ELIOT` | George Eliot | `Middlemarch` | `civilization-memory-literature` | `stub` | `principal-work` | public-domain likely; edition review-required |
| `IND-META-001-005` | `LIB-INDUSTRIAL-AUTHORITY-026-DOUGLASS` | Frederick Douglass | `Narrative`; selected speeches | `indigenous-colonized-witness` | `stub` | `principal-works` | public-domain likely; speech corpus boundary required |
| `IND-META-001-006` | `LIB-INDUSTRIAL-AUTHORITY-027-JACOBS` | Harriet Jacobs | `Incidents in the Life of a Slave Girl` | `gender-family-education` | `stub` | `principal-work` | public-domain likely; pseudonym/editorial history review |
| `IND-META-001-007` | `LIB-INDUSTRIAL-AUTHORITY-025-DU-BOIS` | W. E. B. Du Bois | `The Souls of Black Folk` | `indigenous-colonized-witness` | `stub` | `principal-work` | public-domain likely; edition review-required |
| `IND-META-001-008` | `LIB-INDUSTRIAL-AUTHORITY-023-MELVILLE` | Herman Melville | `Moby-Dick` | `civilization-memory-literature` | `stub` | `principal-work` | public-domain likely; edition review-required |
| `IND-META-001-009` | `LIB-INDUSTRIAL-AUTHORITY-024-TWAIN` | Mark Twain | `Huckleberry Finn`; `Life on the Mississippi` | `civilization-memory-literature` | `stub` | `principal-works` | public-domain likely; language/context notes required |
| `IND-META-001-010` | `LIB-INDUSTRIAL-AUTHORITY-061-ZOLA` | Emile Zola | `Germinal`; `J'accuse` | `civilization-memory-literature` | `stub` | `principal-works` | public-domain likely; translation separation required |
| `IND-META-001-011` | `LIB-INDUSTRIAL-AUTHORITY-062-HARDY` | Thomas Hardy | `Tess`; `Jude the Obscure` | `civilization-memory-literature` | `stub` | `principal-works` | public-domain likely; edition review-required |
| `IND-META-001-012` | `LIB-INDUSTRIAL-AUTHORITY-063-WILDE` | Oscar Wilde | plays; `De Profundis` | `civilization-memory-literature` | `stub` | `selected-works` | public-domain likely; prison text edition boundary required |

Batch 001 disposition: metadata-design-ready; body research remains
unauthorized.

### Batch 001 Readiness Review 2026-08-23

Batch 001 is metadata-mutation-ready for operator disposition. A registry
collision scan found no existing source IDs matching the 12 proposed
`LIB-INDUSTRIAL-AUTHORITY-*` IDs. All rows remain proposed `stub` records and
make no `located`, `available`, body-research-ready, admission-ready, or
seal-ready claim.

Implementation caution: if the operator later authorizes Batch 001 registry
mutation, mutate only these 12 metadata records, regenerate/check the affected
library navigation surfaces, and stop before body research or source-body
admission. The highest care rows are Douglass speeches, Wilde's prison text
boundary, Zola translation separation, Twain language/context notes, and
Jacobs's pseudonym/editorial history.

## Batch 002: Political Economy, Labor, Science, Reform, And Environment

Purpose: build the industrial system, social question, political economy,
science, reform, and early environmental floor before harder twentieth-century
rights cases.

| Candidate ID | Proposed source ID | Authority | Target title | Primary function | Proposed registry status | Coverage ceiling | Rights/body gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `IND-META-002-001` | `LIB-INDUSTRIAL-AUTHORITY-029-MARX` | Karl Marx | `Capital`; `Communist Manifesto` | `industrial-political-economy` | `stub` | `principal-works` | public-domain originals; translation review required |
| `IND-META-002-002` | `LIB-INDUSTRIAL-AUTHORITY-030-ENGELS` | Friedrich Engels | `Condition of the Working Class in England` | `industrial-political-economy` | `stub` | `principal-work` | public-domain likely |
| `IND-META-002-003` | `LIB-INDUSTRIAL-AUTHORITY-031-MILL` | John Stuart Mill | `On Liberty`; `Subjection of Women` | `state-law-constitution` | `stub` | `principal-works` | public-domain likely |
| `IND-META-002-004` | `LIB-INDUSTRIAL-AUTHORITY-032-TOCQUEVILLE` | Alexis de Tocqueville | `Democracy in America`; `Old Regime` | `industrial-political-economy` | `stub` | `principal-works` | translation rights review required |
| `IND-META-002-005` | `LIB-INDUSTRIAL-AUTHORITY-038-DARWIN` | Charles Darwin | `Origin of Species`; `Descent of Man` | `science-technology-system` | `stub` | `principal-works` | public-domain likely |
| `IND-META-002-006` | `LIB-INDUSTRIAL-AUTHORITY-039-WALLACE` | Alfred Russel Wallace | `Malay Archipelago` | `science-technology-system` | `stub` | `principal-work` | public-domain likely |
| `IND-META-002-007` | `LIB-INDUSTRIAL-AUTHORITY-041-BABBAGE` | Charles Babbage | `Economy of Machinery and Manufactures` | `science-technology-system` | `stub` | `principal-work` | public-domain likely |
| `IND-META-002-008` | `LIB-INDUSTRIAL-AUTHORITY-042-NIGHTINGALE` | Florence Nightingale | `Notes on Nursing`; sanitary reports | `labor-social-question` | `stub` | `selected-works` | public-domain likely; report boundary required |
| `IND-META-002-009` | `LIB-INDUSTRIAL-AUTHORITY-043-THOREAU` | Henry David Thoreau | `Civil Disobedience`; `Walden` | `environment-extraction-infrastructure` | `stub` | `principal-works` | public-domain likely |
| `IND-META-002-010` | `LIB-INDUSTRIAL-AUTHORITY-044-RUSKIN` | John Ruskin | `Unto This Last` | `industrial-political-economy` | `stub` | `principal-work` | public-domain likely |
| `IND-META-002-011` | `LIB-INDUSTRIAL-AUTHORITY-045-MORRIS` | William Morris | `News from Nowhere`; essays | `labor-social-question` | `stub` | `selected-works` | public-domain likely; essay boundary required |
| `IND-META-002-012` | `LIB-INDUSTRIAL-AUTHORITY-083-WELLS` | Ida B. Wells | anti-lynching pamphlets | `indigenous-colonized-witness` | `stub` | `selected-works` | public-domain likely; pamphlet sequence required |

Batch 002 disposition: metadata-design-ready; body research remains
unauthorized.

## Batch 003: Global Modernization And Anti-Colonial Foundations

Purpose: prevent Europe-first lock-in by establishing Asian, South Asian, and
Latin American modernization and anti-colonial witness early.

| Candidate ID | Proposed source ID | Authority | Target title | Primary function | Proposed registry status | Coverage ceiling | Rights/body gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `IND-META-003-001` | `LIB-INDUSTRIAL-AUTHORITY-020-RIZAL` | Jose Rizal | `Noli Me Tangere`; `El Filibusterismo` | `civilization-memory-literature` | `stub` | `principal-works` | public-domain likely; Spanish/translation separation required |
| `IND-META-003-002` | `LIB-INDUSTRIAL-AUTHORITY-015-TAGORE` | Rabindranath Tagore | `Gitanjali`; `Nationalism` | `civilization-memory-literature` | `stub` | `selected-works` | mixed public-domain; edition and translation review required |
| `IND-META-003-003` | `LIB-INDUSTRIAL-AUTHORITY-049-SUN-YAT-SEN` | Sun Yat-sen | `Three Principles of the People` | `mass-politics-ideology` | `stub` | `principal-work` | edition/translation review required |
| `IND-META-003-004` | `LIB-INDUSTRIAL-AUTHORITY-051-FUKUZAWA` | Fukuzawa Yukichi | `Encouragement of Learning`; civilization essays | `international-order-decolonization` | `stub` | `selected-works` | translation rights review required |
| `IND-META-003-005` | `LIB-INDUSTRIAL-AUTHORITY-046-GANDHI` | Mohandas K. Gandhi | `Hind Swaraj`; speeches | `international-order-decolonization` | `stub` | `selected-works` | mixed rights; source-specific review required |
| `IND-META-003-006` | `LIB-INDUSTRIAL-AUTHORITY-048-AMBEDKAR` | B. R. Ambedkar | `Annihilation of Caste`; constitutional speeches | `state-law-constitution` | `stub` | `selected-works` | rights/source review required |
| `IND-META-003-007` | `LIB-INDUSTRIAL-AUTHORITY-076-MARTI` | Jose Marti | `Nuestra America`; selected essays | `international-order-decolonization` | `stub` | `selected-works` | public-domain likely; Spanish/translation separation required |
| `IND-META-003-008` | `LIB-INDUSTRIAL-AUTHORITY-091-QIU-JIN` | Qiu Jin | poems, essays, revolutionary writings | `gender-family-education` | `stub` | `selected-works` | edition/translation review required |
| `IND-META-003-009` | `LIB-INDUSTRIAL-AUTHORITY-092-KANG-LIANG` | Kang Youwei and Liang Qichao reform textual tradition | reform memorials and essays | `state-law-constitution` | `stub` | `selected-works` | composite tradition; textual boundary required |
| `IND-META-003-010` | `LIB-INDUSTRIAL-AUTHORITY-017-SOSEKI` | Natsume Soseki | `Kokoro` | `civilization-memory-literature` | `stub` | `principal-work` | translation rights review required |
| `IND-META-003-011` | `LIB-INDUSTRIAL-AUTHORITY-016-LU-XUN` | Lu Xun | `A Madman's Diary`; selected stories | `civilization-memory-literature` | `stub` | `selected-works` | rights/translation review required |
| `IND-META-003-012` | `LIB-INDUSTRIAL-AUTHORITY-018-PREMCHAND` | Premchand | `Godan`; selected stories | `civilization-memory-literature` | `stub` | `selected-works` | Hindi/Urdu and translation review required |

Batch 003 disposition: metadata-design-ready; body research remains
unauthorized.

## Cross-Batch Acceptance Tests

- Exactly 36 metadata candidates are present across three 12-authority batches.
- Every row has a stable candidate ID and proposed source ID.
- Every row stays at proposed `stub`; no row claims `located`, `available`,
  body-research-ready, admission-ready, or seal-ready.
- Every row has a primary function matching the frozen roster.
- Every row has a conservative coverage ceiling.
- Every translated, composite, speech, or institutional record keeps an
  explicit rights or boundary gate.
- No registry, index, source body, private Archive, staging, commit, push, or
  publication action is authorized by this packet.

## Recommended Next Gate

The next reviewable action is operator review of Batch 001 as a metadata-only
mutation proposal. If approved later, the mutation should update only registry
metadata for those 12 authorities and stop before body research.

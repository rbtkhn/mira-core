# Industrial Library Metadata Batch 004 Design v0.1

Status: `metadata-batch-design`
Era: `industrial`
Range: 1815 AD to 1991 AD
Roster packet: `archive/library/industrial/roster-design-v0.1.md`
Gate: `operator-review-before-registry-mutation`

## Authority Boundary

This packet designs Industrial metadata Batch 004 only. It does not mutate
`archive/library/library-registry.json`, generate indexes, download sources,
admit source bodies, ingest into the private Archive, stage, commit, push, or
publish.

Every row is a registry-candidate design record only. `metadata-ready` here
means the source identity, proposed source ID, work target, status ceiling, and
rights triage are coherent enough for operator review before any registry
mutation. It does not mean body-research-ready or admission-ready.

## Batch 004: Nineteenth-Century Literary Interiority Spine

Purpose: restore the large nineteenth-century literary witnesses deferred by
the globally balancing Batch 003 pass. This batch deepens the Industrial shelf's
core claim that modernity preserved itself through interior life under empire,
urbanization, secularization, class pressure, gender constraint, and mass
society.

The batch is source-feasible but translation-sensitive. Public-domain
availability is likely for most targets, while translation and edition choices
remain the controlling body gate for Russian, French, and Scandinavian rows.

| Candidate ID | Proposed source ID | Authority | Target title | Primary function | Proposed registry status | Coverage ceiling | Rights/body gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `IND-META-004-001` | `LIB-INDUSTRIAL-AUTHORITY-003-PUSHKIN` | Alexander Pushkin | `Eugene Onegin`; selected poems | `civilization-memory-literature` | `stub` | `selected-works` | original/translation separation required |
| `IND-META-004-002` | `LIB-INDUSTRIAL-AUTHORITY-004-BALZAC` | Honore de Balzac | `Pere Goriot`; selected `Comedie humaine` | `civilization-memory-literature` | `stub` | `selected-works` | public-domain likely; translation review required |
| `IND-META-004-003` | `LIB-INDUSTRIAL-AUTHORITY-005-HUGO` | Victor Hugo | `Les Miserables` | `civilization-memory-literature` | `stub` | `principal-work` | public-domain likely; translation review required |
| `IND-META-004-004` | `LIB-INDUSTRIAL-AUTHORITY-007-CHARLOTTE-BRONTE` | Charlotte Bronte | `Jane Eyre` | `civilization-memory-literature` | `stub` | `principal-work` | public-domain likely; edition review required |
| `IND-META-004-005` | `LIB-INDUSTRIAL-AUTHORITY-008-EMILY-BRONTE` | Emily Bronte | `Wuthering Heights` | `civilization-memory-literature` | `stub` | `principal-work` | public-domain likely; edition review required |
| `IND-META-004-006` | `LIB-INDUSTRIAL-AUTHORITY-010-FLAUBERT` | Gustave Flaubert | `Madame Bovary` | `civilization-memory-literature` | `stub` | `principal-work` | public-domain likely; translation review required |
| `IND-META-004-007` | `LIB-INDUSTRIAL-AUTHORITY-011-DOSTOEVSKY` | Fyodor Dostoevsky | `Notes from Underground`; `Brothers Karamazov` | `civilization-memory-literature` | `stub` | `principal-works` | translation rights require review |
| `IND-META-004-008` | `LIB-INDUSTRIAL-AUTHORITY-012-TOLSTOY` | Leo Tolstoy | `War and Peace`; `Anna Karenina` | `civilization-memory-literature` | `stub` | `principal-works` | translation rights require review |
| `IND-META-004-009` | `LIB-INDUSTRIAL-AUTHORITY-013-IBSEN` | Henrik Ibsen | `A Doll's House`; `An Enemy of the People` | `civilization-memory-literature` | `stub` | `principal-works` | public-domain likely; translation review required |
| `IND-META-004-010` | `LIB-INDUSTRIAL-AUTHORITY-014-CHEKHOV` | Anton Chekhov | selected plays and stories | `civilization-memory-literature` | `stub` | `selected-works` | translation rights require review |
| `IND-META-004-011` | `LIB-INDUSTRIAL-AUTHORITY-021-WHITMAN` | Walt Whitman | `Leaves of Grass` | `civilization-memory-literature` | `stub` | `principal-work` | public-domain likely; edition history review required |
| `IND-META-004-012` | `LIB-INDUSTRIAL-AUTHORITY-022-DICKINSON` | Emily Dickinson | poems | `civilization-memory-literature` | `stub` | `selected-works` | edition history requires review |

## Representation Logic

Batch 004 is intentionally literature-dense. Batch 003 carried South Asian,
East Asian, Latin American, and anti-colonial modernization rows; Batch 004
answers by filling the missing nineteenth-century literary spine without
claiming that Europe and the United States define the era alone.

The batch preserves:

- Russian interiority and political-moral crisis through Pushkin, Dostoevsky,
  Tolstoy, and Chekhov.
- French realism and revolutionary social imagination through Balzac, Hugo, and
  Flaubert.
- British gender, household, and moral-psychological witness through Charlotte
  Bronte and Emily Bronte.
- Scandinavian drama as public conscience through Ibsen.
- American democratic and lyric interiority through Whitman and Dickinson.

## Rights And Edition Triage

- Prefer original-language bodies where clean public-domain text exists,
  especially for Pushkin, Balzac, Hugo, Flaubert, Dostoevsky, Tolstoy, Ibsen,
  and Chekhov.
- English translations may be admitted only when translator, edition, and
  public-domain status are explicit.
- Do not collapse multiple editions of `Leaves of Grass`; identify the edition
  before body admission.
- Dickinson requires edition-history caution because early published texts may
  reflect editorial regularization.
- Do not claim complete surviving corpus for any authority in this batch.

## Acceptance Tests

- Exactly 12 metadata candidates are present.
- Every row has a stable candidate ID and proposed source ID.
- Every row stays at proposed `stub`; no row claims `located`, `available`,
  body-research-ready, admission-ready, or seal-ready.
- Every row has primary function `civilization-memory-literature`.
- Every row has a conservative coverage ceiling.
- Every translated or edition-sensitive record keeps an explicit rights/body
  gate.
- No registry, index, source body, private Archive, staging, commit, push, or
  publication action is authorized by this packet.

## Recommended Next Gate

The next reviewable action is operator review of Batch 004 as a metadata-only
mutation proposal. If approved later, mutate only these 12 metadata records,
regenerate/check the affected library navigation surfaces, and stop before body
research or source-body admission.

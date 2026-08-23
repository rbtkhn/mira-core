# Industrial Library Metadata Batch 005 Design v0.1

Status: `metadata-batch-design`
Era: `industrial`
Range: 1815 AD to 1991 AD
Roster packet: `archive/library/industrial/roster-design-v0.1.md`
Gate: `operator-review-before-registry-mutation`

## Authority Boundary

This packet designs Industrial metadata Batch 005 only. It does not mutate
`archive/library/library-registry.json`, generate indexes, download sources,
admit source bodies, ingest into the private Archive, stage, commit, push, or
publish.

Every row is a registry-candidate design record only. `metadata-ready` here
means the source identity, proposed source ID, work target, status ceiling, and
rights triage are coherent enough for operator review before any registry
mutation. It does not mean body-research-ready or admission-ready.

## Batch 005: Public-Domain Literature And Social Witness Expansion

Purpose: extend the Industrial shelf beyond the Batch 004 nineteenth-century
interiority spine into a globally wider public-domain lane: Latin American
fiction, Black Atlantic speech and education, public science, empire critique,
South African witness, feminist reform, Indigenous North American literature,
German moral crisis, and socialist anti-war critique.

The batch intentionally avoids the highest-risk twentieth-century rights cases
while preserving them in the roster. Winston Churchill remains an essential
Industrial authority for empire, wartime rhetoric, statecraft, and mass
conflict; he is sequenced later because speech and edition rights require a
separate review path.

| Candidate ID | Proposed source ID | Authority | Target title | Primary function | Proposed registry status | Coverage ceiling | Rights/body gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `IND-META-005-001` | `LIB-INDUSTRIAL-AUTHORITY-019-MACHADO-DE-ASSIS` | Machado de Assis | `Dom Casmurro`; `Posthumous Memoirs of Bras Cubas` | `civilization-memory-literature` | `stub` | `principal-works` | public-domain originals likely; translation review required |
| `IND-META-005-002` | `LIB-INDUSTRIAL-AUTHORITY-028-SOJOURNER-TRUTH` | Sojourner Truth textual tradition | speeches and dictated/narrated testimony | `indigenous-colonized-witness` | `stub` | `selected-works` | speech/textual tradition requires edition and attribution review |
| `IND-META-005-003` | `LIB-INDUSTRIAL-AUTHORITY-040-FARADAY` | Michael Faraday | lectures and experimental writings | `science-technology-system` | `stub` | `selected-works` | public-domain likely; lecture/collection boundary review required |
| `IND-META-005-004` | `LIB-INDUSTRIAL-AUTHORITY-064-CONRAD` | Joseph Conrad | `Heart of Darkness`; `Lord Jim` | `civilization-memory-literature` | `stub` | `principal-works` | public-domain likely; edition review required |
| `IND-META-005-005` | `LIB-INDUSTRIAL-AUTHORITY-081-SCHREINER` | Olive Schreiner | `The Story of an African Farm`; selected political writings | `civilization-memory-literature` | `stub` | `selected-works` | public-domain likely; edition review required |
| `IND-META-005-006` | `LIB-INDUSTRIAL-AUTHORITY-082-STANTON` | Elizabeth Cady Stanton | Seneca Falls materials; speeches | `gender-family-education` | `stub` | `selected-works` | public-domain likely; convention-document attribution review required |
| `IND-META-005-007` | `LIB-INDUSTRIAL-AUTHORITY-084-ZITKALA-SA` | Zitkala-Sa | `American Indian Stories`; selected essays | `civilization-memory-literature` | `stub` | `selected-works` | public-domain likely; periodical/collection edition review required |
| `IND-META-005-008` | `LIB-INDUSTRIAL-AUTHORITY-093-WASHINGTON` | Booker T. Washington | `Up from Slavery`; Atlanta Exposition address | `labor-social-question` | `stub` | `selected-works` | public-domain likely; speech/text edition review required |
| `IND-META-005-009` | `LIB-INDUSTRIAL-AUTHORITY-036-NIETZSCHE` | Friedrich Nietzsche | `On the Genealogy of Morals`; `Thus Spake Zarathustra` | `religion-moral-order` | `stub` | `principal-works` | public-domain originals likely; translation rights review required |
| `IND-META-005-010` | `LIB-INDUSTRIAL-AUTHORITY-054-LUXEMBURG` | Rosa Luxemburg | `Reform or Revolution`; `The Junius Pamphlet` | `mass-politics-ideology` | `stub` | `principal-works` | public-domain posture varies by edition/translation; review required |

## Representation Logic

Batch 005 is deliberately mixed rather than a second pure literature batch. It
keeps literature structurally central while adding adjacent source functions
that show how industrial modernity spoke through reform, science, race,
education, gender, religion, and socialism.

The batch strengthens:

- Latin American literature through Machado de Assis.
- Black Atlantic and post-emancipation witness through Sojourner Truth and
  Booker T. Washington.
- Public scientific culture through Faraday.
- Imperial literary critique through Conrad and Schreiner.
- Women's rights and social reform through Stanton.
- Indigenous North American literary witness through Zitkala-Sa.
- European moral and socialist crisis through Nietzsche and Luxemburg.

## Rights And Edition Triage

- Prefer original-language bodies where clean public-domain text exists,
  especially for Machado, Nietzsche, and Luxemburg.
- English translations may be admitted only when translator, edition, and
  public-domain status are explicit.
- Sojourner Truth requires speech/transcription/attribution separation before
  any coverage claim.
- Stanton materials require convention-document and speech provenance review;
  do not collapse collective declarations into a single-author corpus claim.
- Faraday requires collection-boundary review because lectures and experimental
  papers may be preserved through later collected editions.
- Zitkala-Sa requires periodical and collection edition review.
- No row may claim complete surviving corpus at this gate.

## Acceptance Tests

- Exactly 10 metadata candidates are present.
- Every row has a stable candidate ID and proposed source ID.
- Every row stays at proposed `stub`; no row claims `located`, `available`,
  body-research-ready, admission-ready, or seal-ready.
- Literature remains central while at least five distinct representation lanes
  are present.
- Every row has a conservative coverage ceiling.
- Every speech, translation, collection, or edition-sensitive record keeps an
  explicit rights/body gate.
- Churchill remains present in the roster and is deferred only for rights and
  edition sequencing, not removed.
- No registry, index, source body, private Archive, staging, commit, push, or
  publication action is authorized by this packet.

## Recommended Next Gate

The next reviewable action is operator review of Batch 005 as a metadata-only
mutation proposal. If approved later, mutate only these 10 metadata records,
regenerate/check the affected library navigation surfaces, and stop before body
research or source-body admission.

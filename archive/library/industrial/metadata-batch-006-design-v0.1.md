# Industrial Library Metadata Batch 006 Design v0.1

Status: `metadata-batch-design`
Era: `industrial`
Range: 1815 AD to 1991 AD
Roster packet: `archive/library/industrial/roster-design-v0.1.md`
Gate: `operator-review-before-registry-mutation`

## Authority Boundary

This packet designs Industrial metadata Batch 006 only. It does not mutate
`archive/library/library-registry.json`, generate indexes, download sources,
admit source bodies, ingest into the private Archive, stage, commit, push, or
publish.

Every row is a registry-candidate design record only. `metadata-ready` here
means the source identity, proposed source ID, work target, status ceiling, and
rights triage are coherent enough for operator review before any registry
mutation. It does not mean body-research-ready or admission-ready.

## Batch 006: Twentieth-Century Systems, War, And World Order

Purpose: add the missing Industrial authorities that make the shelf more than a
nineteenth-century literary and reform corpus. Batch 006 covers the apparatus
by which industrial modernity analyzed itself, mobilized mass politics,
survived world war, framed decolonization, built international law, entered the
nuclear age, and began naming ecological danger.

This is a metadata-only high-caution batch. Several authorities are essential
but rights-restricted or institutionally complex. Their inclusion here is a
roster and registry identity decision, not a promise of near-term body
admission.

| Candidate ID | Proposed source ID | Authority | Target title | Primary function | Proposed registry status | Coverage ceiling | Rights/body gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `IND-META-006-001` | `LIB-INDUSTRIAL-AUTHORITY-033-WEBER` | Max Weber | `The Protestant Ethic`; political essays | `industrial-political-economy` | `stub` | `selected-works` | translation rights and German/English separation required |
| `IND-META-006-002` | `LIB-INDUSTRIAL-AUTHORITY-034-DURKHEIM` | Emile Durkheim | `Division of Labor`; `Suicide` | `industrial-political-economy` | `stub` | `principal-works` | translation rights and edition review required |
| `IND-META-006-003` | `LIB-INDUSTRIAL-AUTHORITY-035-FREUD` | Sigmund Freud | `Civilization and Its Discontents`; selected psychoanalytic writings | `religion-moral-order` | `stub` | `selected-works` | rights and translation risk; body admission likely deferred |
| `IND-META-006-004` | `LIB-INDUSTRIAL-AUTHORITY-053-LENIN` | Vladimir Lenin | `Imperialism`; `State and Revolution` | `mass-politics-ideology` | `stub` | `principal-works` | public-domain varies by edition and translation; party-edition review required |
| `IND-META-006-005` | `LIB-INDUSTRIAL-AUTHORITY-057-CHURCHILL` | Winston Churchill | wartime speeches | `war-revolution-violence` | `stub` | `selected-works` | speech, broadcast, collection, and Crown/estate rights review required |
| `IND-META-006-006` | `LIB-INDUSTRIAL-AUTHORITY-060-MANDELA` | Nelson Mandela | trial statement; speeches | `international-order-decolonization` | `stub` | `selected-works` | rights/source review required; modern speech reuse not assumed |
| `IND-META-006-007` | `LIB-INDUSTRIAL-AUTHORITY-079-EINSTEIN` | Albert Einstein | relativity essays; nuclear-era letters | `science-technology-system` | `stub` | `selected-works` | mixed rights; letters and later essays require source-specific review |
| `IND-META-006-008` | `LIB-INDUSTRIAL-AUTHORITY-080-UDHR-DRAFTING` | Universal Declaration of Human Rights drafting tradition | UDHR and drafting documents | `international-order-decolonization` | `stub` | `selected-works` | institutional text and drafting-record source review required |
| `IND-META-006-009` | `LIB-INDUSTRIAL-AUTHORITY-096-UNITED-NATIONS-CHARTER` | United Nations Charter / San Francisco conference tradition | UN Charter; conference records | `international-order-decolonization` | `stub` | `selected-works` | institutional text, conference-record, and reuse review required |
| `IND-META-006-010` | `LIB-INDUSTRIAL-AUTHORITY-078-CARSON` | Rachel Carson | `Silent Spring` | `environment-extraction-infrastructure` | `stub` | `principal-work` | rights restricted; metadata identity only until permission/public-domain basis exists |

## Representation Logic

Batch 006 is intentionally not literature-dense. The Industrial shelf already
has a strong literary core after Batches 004 and 005; this batch adds the
systems layer that makes the era legible as industrial modernity rather than a
sequence of novels and reform texts.

The batch preserves:

- sociological self-description through Weber and Durkheim;
- psychoanalytic modernity and secular moral crisis through Freud;
- revolutionary party-state theory through Lenin;
- wartime democratic rhetoric and imperial statecraft through Churchill;
- anti-apartheid decolonizing witness through Mandela;
- scientific modernity and nuclear-era danger through Einstein;
- postwar international-rights architecture through UDHR and UN Charter
  traditions; and
- ecological danger and industrial chemical critique through Carson.

## Rights And Edition Triage

- Churchill remains essential. He is included here precisely because the shelf
  needs him, but every body candidate must separate speech event, broadcast or
  printed edition, collection editor, and rights holder.
- Carson is metadata-only unless a permissioned or clearly reusable body is
  later supplied; no `Silent Spring` body should be downloaded on ordinary
  public-web visibility alone.
- Mandela is metadata-only until source-specific rights for trial statements
  and speeches are reviewed.
- UDHR and UN Charter records are institutional traditions; do not collapse
  drafting minutes, final instruments, and conference publications into a
  single body claim.
- Freud, Weber, Durkheim, Lenin, and Einstein require original-language and
  translation separation before body admission.
- No row may claim complete surviving corpus at this gate.

## Acceptance Tests

- Exactly 10 metadata candidates are present.
- Every row has a stable candidate ID and proposed source ID.
- Every row stays at proposed `stub`; no row claims `located`, `available`,
  body-research-ready, admission-ready, or seal-ready.
- At least six distinct representation lanes are present.
- Every modern-rights or institutional row has an explicit rights/body gate.
- Churchill is included and preserved as essential, not deferred or removed.
- No registry, index, source body, private Archive, staging, commit, push, or
  publication action is authorized by this packet.

## Recommended Next Gate

The next reviewable action is operator review of Batch 006 as a metadata-only
mutation proposal. If approved later, mutate only these 10 metadata records,
regenerate/check the affected library navigation surfaces, and stop before body
research or source-body admission.

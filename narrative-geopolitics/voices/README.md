# Voices

`voices/` is the voice continuity layer for Narrative Geopolitics.

A voice is a recurring source-person whose claims, frames, forecasts, contradictions, and source modalities matter across time. A voice may be a speaker, writer, essayist, interview guest, social poster, streamer, report author, or mixed-format analyst.

## Purpose

Voice records help daily geopolitics and council work remember whether a claim
is new, recurring, contradicted, forecast-bearing, or shaped by source
modality. They make an intellectual framework queryable without pretending to
reproduce a person's unobserved current beliefs.

They keep the system from treating every quote or article as isolated.

In dialogue, a voice record constrains an interlocutor; it does not supply a
persona. The response must follow the
[dialogue contract](../method/dialogue-contract.md), cite its source floor, and
preserve tensions that the corpus does not resolve.

## Voice Records

A `voice record` is the durable continuity object for one person/source.

The directory name is the canonical person slug. It is distinct from
`host_slug`, which identifies the channel or host context. Historical aliases
are canonicalized after intake and before synthesis; source indexes are then
reconciled from the manifest. A manifest voice does not automatically earn a
new voice directory.

Use [_template.md](_template.md) for every new voice record. The template is intentionally lighter than the inherited `strategy-codex/statecraft` voice machinery, but it preserves one important law: every recurring voice should have the same basic shape.

For navigability, each voice directory exposes two canonical routes:

- `README.md` as the canonical profile surface
- `source-index.md` as the canonical routing/index surface

## Pape-Parity Standard

`Pape parity` means a voice has the same operational shape as Pape: manifest-backed source coverage, a derived source index, retrieval lenses, and channel-aware pressure separation. Corpus depth is queried from the manifest, not fixed here.

A parity-ready voice has:

- a voice record, source index, and claim map
- at least two voice-native retrieval lenses
- imported central archive sources
- manifest rows for those sources
- channel-aware routing when a source is host-conditioned

Pape is currently `full-source-parity`. The other core voices are `first-slice-parity`: source-backed enough for synthesis, but not yet exhaustive.

## Current Voice Records

| Voice | Profile | Index | Status |
| --- | --- | --- | --- |
| Adams | [adams/README.md](adams/README.md) | [adams/source-index.md](adams/source-index.md) | internal / imported-corpus |
| Anthony Aguilar | [aguilar/README.md](aguilar/README.md) | [aguilar/source-index.md](aguilar/source-index.md) | internal / imported-corpus |
| Alkhorshid | [alkhorshid/README.md](alkhorshid/README.md) | [alkhorshid/source-index.md](alkhorshid/source-index.md) | internal / imported-corpus |
| Armstrong | [armstrong/README.md](armstrong/README.md) | [armstrong/source-index.md](armstrong/source-index.md) | internal / imported-corpus |
| Robert Barnes | [barnes/README.md](barnes/README.md) | [barnes/source-index.md](barnes/source-index.md) | internal / imported-corpus |
| Jacques Baud | [baud/README.md](baud/README.md) | [baud/source-index.md](baud/source-index.md) | internal / imported-corpus |
| Beebe | [beebe/README.md](beebe/README.md) | [beebe/source-index.md](beebe/source-index.md) | internal / imported-corpus |
| Berletic | [berletic/README.md](berletic/README.md) | [berletic/source-index.md](berletic/source-index.md) | internal / imported-corpus |
| Max Blumenthal | [blumenthal/README.md](blumenthal/README.md) | [blumenthal/source-index.md](blumenthal/source-index.md) | internal / imported-corpus |
| Alex Christoforou | [cristoforou/README.md](cristoforou/README.md) | [cristoforou/source-index.md](cristoforou/source-index.md) | internal / canonical-person-seed |
| Alastair Crooke | [crooke/README.md](crooke/README.md) | [crooke/source-index.md](crooke/source-index.md) | internal / imported-corpus |
| Daniel L. Davis | [davis/README.md](davis/README.md) | [davis/source-index.md](davis/source-index.md) | internal / first-slice-parity |
| Glenn Diesen | [diesen/README.md](diesen/README.md) | [diesen/source-index.md](diesen/source-index.md) | internal / first-slice-parity |
| Dugin | [dugin/README.md](dugin/README.md) | [dugin/source-index.md](dugin/source-index.md) | internal / imported-corpus |
| Pepe Escobar | [escobar/README.md](escobar/README.md) | [escobar/source-index.md](escobar/source-index.md) | internal / lightweight |
| Chas Freeman | [freeman/README.md](freeman/README.md) | [freeman/source-index.md](freeman/source-index.md) | internal / imported-corpus |
| John Helmer | [helmer/README.md](helmer/README.md) | [helmer/source-index.md](helmer/source-index.md) | internal / imported-corpus |
| Patrick Henningsen | [henningsen/README.md](henningsen/README.md) | [henningsen/source-index.md](henningsen/source-index.md) | internal / lightweight |
| Matthew Hoh | [hoh/README.md](hoh/README.md) | [hoh/source-index.md](hoh/source-index.md) | internal / imported-corpus |
| Hudson | [hudson/README.md](hudson/README.md) | [hudson/source-index.md](hudson/source-index.md) | internal / imported-corpus |
| Steve Jermy | [jermy/README.md](jermy/README.md) | [jermy/source-index.md](jermy/source-index.md) | internal / imported-corpus |
| Jiang Xueqin | [jiang/README.md](jiang/README.md) | [jiang/source-index.md](jiang/source-index.md) | internal / imported-corpus |
| Larry Johnson | [johnson/README.md](johnson/README.md) | [johnson/source-index.md](johnson/source-index.md) | internal / first-slice-parity |
| Sergey Karaganov | [karaganov/README.md](karaganov/README.md) | [karaganov/source-index.md](karaganov/source-index.md) | internal / imported-corpus |
| Joe Kent | [kent/README.md](kent/README.md) | [kent/source-index.md](kent/source-index.md) | internal |
| Alex Krainer | [krainer/README.md](krainer/README.md) | [krainer/source-index.md](krainer/source-index.md) | internal / imported-corpus |
| Stanislav Krapivnik | [krapivnik/README.md](krapivnik/README.md) | [krapivnik/source-index.md](krapivnik/source-index.md) | internal / seeded |
| Lieven | [lieven/README.md](lieven/README.md) | [lieven/source-index.md](lieven/source-index.md) | internal / imported-corpus |
| Douglas Macgregor | [macgregor/README.md](macgregor/README.md) | [macgregor/source-index.md](macgregor/source-index.md) | internal / transcript-bearing-upstream-parity |
| Elijah Magnier | [magnier/README.md](magnier/README.md) | [magnier/source-index.md](magnier/source-index.md) | internal / provisional-imported-corpus |
| Seyed Mohammad Marandi | [marandi/README.md](marandi/README.md) | [marandi/source-index.md](marandi/source-index.md) | internal / first-slice-parity |
| Marouf | [marouf/README.md](marouf/README.md) | [marouf/source-index.md](marouf/source-index.md) | internal / imported-corpus |
| Andrei Martyanov | [martyanov/README.md](martyanov/README.md) | [martyanov/source-index.md](martyanov/source-index.md) | internal / imported-corpus |
| Aaron Mate | [mate/README.md](mate/README.md) | [mate/source-index.md](mate/source-index.md) | internal / imported-corpus |
| Jack Matlock | [matlock/README.md](matlock/README.md) | [matlock/source-index.md](matlock/source-index.md) | internal / imported-corpus |
| Ray McGovern | [mcgovern/README.md](mcgovern/README.md) | [mcgovern/source-index.md](mcgovern/source-index.md) | internal / imported-corpus |
| John Mearsheimer | [mearsheimer/README.md](mearsheimer/README.md) | [mearsheimer/source-index.md](mearsheimer/source-index.md) | internal / first-slice-parity |
| Alexander Mercouris | [mercouris/README.md](mercouris/README.md) | [mercouris/source-index.md](mercouris/source-index.md) | internal / transcript-bearing-upstream-parity |
| Emad Mostaque | [mostaque/README.md](mostaque/README.md) | [mostaque/source-index.md](mostaque/source-index.md) | internal / provisional-corpus |
| Robert Pape | [pape/README.md](pape/README.md) | [pape/source-index.md](pape/source-index.md) | internal |
| Trita Parsi | [parsi/README.md](parsi/README.md) | [parsi/source-index.md](parsi/source-index.md) | internal / imported-corpus |
| Polyanskiy | [polyanskiy/README.md](polyanskiy/README.md) | [polyanskiy/source-index.md](polyanskiy/source-index.md) | internal / imported-corpus |
| Ted Postol | [postol/README.md](postol/README.md) | [postol/source-index.md](postol/source-index.md) | internal / imported-corpus |
| Scott Ritter | [ritter/README.md](ritter/README.md) | [ritter/source-index.md](ritter/source-index.md) | internal / imported-corpus |
| Jeffrey Sachs | [sachs/README.md](sachs/README.md) | [sachs/source-index.md](sachs/source-index.md) | internal / imported-corpus |
| Pravin Sawhney | [sawhney/README.md](sawhney/README.md) | [sawhney/source-index.md](sawhney/source-index.md) | internal |
| Varoufakis | [varoufakis/README.md](varoufakis/README.md) | [varoufakis/source-index.md](varoufakis/source-index.md) | internal / imported-corpus |
| Vilano | [vilano/README.md](vilano/README.md) | [vilano/source-index.md](vilano/source-index.md) | internal / imported-corpus |
| Stephen Walt | [walt/README.md](walt/README.md) | [walt/source-index.md](walt/source-index.md) | internal / imported-corpus |
| Brandon Weichert | [weichert/README.md](weichert/README.md) | [weichert/source-index.md](weichert/source-index.md) | internal / imported-corpus |
| Lawrence Wilkerson | [wilkerson/README.md](wilkerson/README.md) | [wilkerson/source-index.md](wilkerson/source-index.md) | internal / imported-corpus |

## Comparison Notes

| Comparison | Purpose | Status |
| --- | --- | --- |
| [Voice orthogonality map](comparisons/orthogonality-map.md) | Preserves the current six-axis ensemble and its do-not-collapse rules. | seed-map |
| [Pape / Mearsheimer comparison](comparisons/pape-mearsheimer.md) | Distinguishes mechanism-and-falsifier retrieval from structure-and-bargaining-geometry retrieval. | working-comparison |
| [Pape / Mercouris orthogonality](comparisons/pape-mercouris.md) | Compatibility pointer to the ensemble orthogonality map. | compat-pointer |

## Status

Voice records are internal first. Public summaries can come later when a record is stable enough to share.

People come first. Entity, institution, publication, or channel records can be added later if daily runs prove they need their own continuity objects.

Host, show, and channel conditioning belongs in [../channels/](../channels/README.md), not in a voice record, unless the host also becomes a recurring source-person whose own claims need continuity.

## Minimum Rule

Do not add a voice record just because a source appears once.

For a new person with no existing directory, one manifest row is a provisional
route, not a canonical voice shelf. Keep the manifest's best source-truth
`voice_slugs` value if needed, but leave the person unindexed until recurrence
or explicit operator override justifies a durable continuity object.

Add a record when at least one of these is true:

- the voice recurs across daily runs
- the voice makes forecast-bearing claims
- the voice's prior pattern materially changes interpretation
- the source modality changes how the claim should be read
- contradictions or tensions need continuity tracking

When the only support is a single landed item, the default repair is further
capture discovery or provisional reporting, not shelf creation.

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
| Alexander Mercouris | [mercouris/README.md](mercouris/README.md) | [mercouris/source-index.md](mercouris/source-index.md) | internal / first-slice-parity |
| Daniel Davis | [davis/README.md](davis/README.md) | [davis/source-index.md](davis/source-index.md) | internal / first-slice-parity |
| Douglas Macgregor | [macgregor/README.md](macgregor/README.md) | [macgregor/source-index.md](macgregor/source-index.md) | internal / first-slice-parity |
| Pepe Escobar | [escobar/README.md](escobar/README.md) | [escobar/source-index.md](escobar/source-index.md) | internal / lightweight |
| Glenn Diesen | [diesen/README.md](diesen/README.md) | [diesen/source-index.md](diesen/source-index.md) | internal / first-slice-parity |
| Larry Johnson | [johnson/README.md](johnson/README.md) | [johnson/source-index.md](johnson/source-index.md) | internal / first-slice-parity |
| John Mearsheimer | [mearsheimer/README.md](mearsheimer/README.md) | [mearsheimer/source-index.md](mearsheimer/source-index.md) | internal / first-slice-parity |
| Jiang Xueqin | [jiang/README.md](jiang/README.md) | [jiang/source-index.md](jiang/source-index.md) | internal / imported-corpus |
| Joe Kent | [kent/README.md](kent/README.md) | [kent/source-index.md](kent/source-index.md) | internal / imported-corpus |
| Patrick Henningsen | [henningsen/README.md](henningsen/README.md) | [henningsen/source-index.md](henningsen/source-index.md) | internal / lightweight |
| Seyed Mohammad Marandi | [marandi/README.md](marandi/README.md) | [marandi/source-index.md](marandi/source-index.md) | internal / first-slice-parity |
| Robert Pape | [pape/README.md](pape/README.md) | [pape/source-index.md](pape/source-index.md) | internal / full-source-parity |

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

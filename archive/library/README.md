# Mira Library

Status: `scaffold`

`archive/library/` is Mira Core's curated source-library shelf for primary,
ancient, and historical sources, organized by the source or work's primary
historical subject period. It is a repository-local navigation and retrieval
surface, not a private Archive catalog collection and not a wholesale mirror of
Civilization Memory.

The machine authority is [`library-registry.json`](library-registry.json).
Era `index.md` files are human-facing navigation surfaces only.

## Era Taxonomy

| Era | ID | Range | Use |
| --- | --- | --- | --- |
| Ancient | `ancient` | BC to 476 AD | Operational shelf for classical, foundational, and ancient subject periods up to the 476 AD boundary. |
| Medieval | `medieval` | 476 AD to 1453 AD | Operational shelf for medieval subject periods, transmission chains, religious-political orders, and civilizational continuity. |
| Colonial | `colonial` | 1453 AD to 1815 AD | Operational shelf for early-modern subject periods, including imperial, maritime, gunpowder-state, confessional, company-rule, and pre-industrial global systems; not limited to European colonial history. |
| Industrial | `industrial` | 1815 AD to 1991 AD | Operational shelf for industrial subject periods, including industrial states, mass politics, late empire, world wars, Cold War order, and modern state capacity. |
| Digital | `digital` | 1991 AD to present | Operational shelf for digital-era subject periods, including post-Cold War order, internet-scale information systems, platform media, globalization, precision warfare, AI, and digital state capacity. |

These eras are operational shelves for retrieval and browsing. They classify
library placement by primary subject period; they are not a universal
historical ontology or a claim that every civilization follows the same period
sequence.

## Source Model

Future source entries in `library-registry.json` use:

- `source_id`
- `title`
- `author`
- `subject_era`
- `source_composition_era`
- `edition_era`
- `secondary_eras`
- `date_start`
- `date_end`
- `date_label`
- `era_basis`
- `civilization_tags`
- `source_type`
- `location`
- `status`
- `notes`

`subject_era` is required and classifies the primary historical subject period.
`source_composition_era` records when the work was composed when known.
`edition_era` records the era of the edition, translation, URL, database, or
digital object when relevant.

## Civilization Memory Crosswalk

Civilization Memory's `ARC-T-*` taxonomy classifies authors and sources by
source-time and can carry precedence rules inside that system. Mira Library
uses era labels for subject-period shelving and retrieval metadata. A source may
therefore have one Mira Library `subject_era`, another `source_composition_era`,
and another `edition_era` without creating a conflict.

Mira Library eras do not by themselves establish source precedence,
admissibility, evidence role, quotation rights, or conflict-resolution rules.
Those judgments belong to the workflow that uses the source.

Typical crosswalk:

- `ARC-T-ANCIENT` usually maps to `subject_era: ancient`.
- `ARC-T-MEDIEVAL` usually maps to `subject_era: medieval`.
- `ARC-T-EARLY-MOD` may map to `subject_era: colonial` or `industrial`.
- `ARC-T-MODERN` usually maps to `industrial` or `digital` as edition,
  scholarship, or analysis era.

## Authority Boundary

Library storage, search, and classification do not verify claims, grant
quotation rights, publish sources, ingest records into the private Archive
catalog, promote sources into evidence, or import Civilization Memory content.

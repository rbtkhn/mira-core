# Carpini–Rubruck Medieval Roster Expansion Proposal

Date: 2026-08-20
Status: `proposal-only`
Authority effect: `none`

## Recommendation

Retain all 60 selected authorities and add John of Plano Carpini and William of Rubruck as selections 61 and 62. Their independent eyewitness missions to the Mongol world supply a high-consequence Latin–Inner Asian diplomatic corridor that is not adequately represented by demoting either an established European authority or a non-European countervoice.

The earlier 56 target and 60 ceiling should be treated as planning controls, not as reasons to erase historically distinct sources. Acceptance of this proposal would require a later, explicit amendment to the roster contract; this document does not perform that amendment.

## Proposed Additions

| Candidate | Proposed source ID | Boundary | Primary lane | Functions | Score | Portability |
| --- | --- | --- | --- | --- | ---: | --- |
| `MED-CAND-077` — John of Plano Carpini | `LIB-MEDIEVAL-AUTHORITY-077-JOHN-OF-PLANO-CARPINI` | *Historia Mongalorum* / principal Carpini account | Latin Christian and Jewish Mediterranean/European | travel and diplomacy; ethnography; papal intelligence; Mongol imperial encounter | 9/10 | `partial` |
| `MED-CAND-078` — William of Rubruck | `LIB-MEDIEVAL-AUTHORITY-078-WILLIAM-OF-RUBRUCK` | *Itinerarium* / *Relatio* only | Latin Christian and Jewish Mediterranean/European | travel and diplomacy; religious encounter; court observation; Mongol imperial geography | 9/10 | `difficult` |

Both are modeled as named authorities, not as one Rockhill volume. The shared 1900 parent scan is a provenance object, not evidence that their works or bodies form one authority.

## Reconciliation

| Measure | Current manifest | Proposed roster after later amendment |
| --- | ---: | ---: |
| Longlist candidates | 76 | 78 |
| Selected | 60 | 62 |
| Reserve | 16 | 16 |
| Latin Christian and Jewish Mediterranean/European lane | 12 | 14 |

All other lane counts remain unchanged. Every seven-lane minimum continues to pass. Maimonides and Judah Halevi remain selected, preserving the explicit two-authority Jewish floor. *Kebra Nagast* remains selected, preserving Ethiopian/Eastern Christian representation. Turkic and Mongol representation also remains intact.

The additions strengthen travel and diplomacy, state intelligence, religious encounter, and cross-corridor political memory. No selected authority is rejected, demoted, renumbered, or reidentified.

## Boundary and Feasibility Notes

### John of Plano Carpini

- Composition basis: the report produced after the 1245–1247 mission, conventionally dated c. 1247; the journey dates are not substituted for the composition date.
- Preferred English route: W. W. Rockhill's 1900 translation of the first Carpini account, printed pages 1–32, now privately collated against the scan.
- Original-language route: still unresolved for a complete, clean, provenance-bound Latin body. The inspected Beazley witness explicitly lacks chapter IX and cannot close this gap.
- Rights posture: `plausible-open`; the 1900 edition is a public-domain candidate in the United States, but the final derived-body rights statement and jurisdiction boundary remain an admission gate.
- Coverage ceiling: `principal-work`; no complete-surviving-corpus claim.

### William of Rubruck

- Composition basis: the report of the 1253–1255 mission, conventionally dated c. 1255.
- Preferred original-language route: Michel and Wright's 1839 Latin edition, printed pages 17–200. The private draft has structural cleanup only and retains 146 distinct alphanumeric OCR-defect tokens.
- Preferred English route: Rockhill's 1900 translation, subject to a separate clean derivation and verification pass.
- Rights posture: `plausible-open`, with edition-specific verification still required.
- Coverage ceiling: `principal-work`; neither the 1839 edition nor a later English translation establishes complete-surviving-corpus coverage.

## Decision Consequence

If accepted later, the machine manifest should add candidates 077 and 078 as `selected` and explicitly record that the roster ceiling was amended from 60 to 62 for non-duplicative historical consequence. The existing 60 records should remain byte-for-byte unchanged. Registry creation and body admission remain separate steps.

## Persistence and Authority

This is a working-tree proposal. It is not roster acceptance, registry admission, body admission, staging, commit, push, or publication. The machine-readable counterpart is [carpini-rubruck-roster-expansion-proposal.json](./carpini-rubruck-roster-expansion-proposal.json).

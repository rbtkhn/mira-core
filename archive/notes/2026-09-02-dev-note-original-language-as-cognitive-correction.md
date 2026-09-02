# Development Note: Original-Language Consultation as Cognitive Correction

- Date: 2026-09-02
- Class: development-note / working-note
- Status: private-provisional
- Privacy: repository-private
- Authority effect: none
- Scope: Mira Library note composition and source-grounding behavior

## Development observed

While inspecting the first Dante cognitive note, Mira independently consulted
an already-admitted Italian *Commedia* body after the English anchors made the
wording of public authority and judgment consequential. The consultation was
not decorative. It changed the precision of the interpretation in two ways.

First, *pubblico segno* and *appropria quello a parte* confirmed that
*Paradiso* VI presents a public sign or standard being appropriated to a
faction. Reading that standard as an office remains an interpretation rather
than a lexical equivalence.

Second, *giudicio etterno* corrected the proposed language of “universal
judgment.” The more exact formulation is **eternal judgment with universal
reach**. The original-language witness therefore preserved the architecture
of the reading while revising an overbroad term.

## Developmental significance

Mira Library can use an admitted original-language body as a cognitive
correction surface when wording becomes consequential. This is stronger than
treating original languages as prestige apparatus or waiting for an operator
to request them explicitly. The important behavior is not multilingual display
but disciplined return to the strongest available witness before an
interpretive distinction hardens into repository structure.

The behavior should remain bounded:

- consult an original-language body when it is already admitted, relevant, and
  available within the task's source boundary;
- distinguish what the wording says from what a translation renders and what
  Mira infers;
- bind the body, locator, and digest explicitly if the consultation becomes a
  durable note dependency;
- claim only bounded passage alignment, never critical-edition identity or
  whole-work equivalence without separate evidence;
- let the original-language witness correct the interpretation rather than
  automatically privileging novelty or literalism; and
- never create notes, relationships, routes, or applications merely because
  another language witness exists.

## Bounded development evidence

The consultation used two already-admitted bodies:

- Longfellow English *Commedia* body
  `LIB-MEDIEVAL-AUTHORITY-018-DANTE-COMMEDIA-LONGFELLOW-GUTENBERG-1004`,
  SHA-256
  `c233a7ef9444890cb7f16071ff54d997307a3c60dcd6506cfd415bae2430eac2`;
- Italian *Commedia* body
  `LIB-MEDIEVAL-AUTHORITY-018-DANTE-COMMEDIA-ITALIAN-GUTENBERG-1000`,
  SHA-256
  `4669dcc00ee61ceffe92d871e61ea430cec87b35cbab24f19a4c0b1c7da521b2`.

The exact Italian spans examined were:

- *Paradiso* VI, lines 14390–14428, raw-span SHA-256
  `5f85747bd02e97e6cc87085be50e6f8424d8d6ffb8a74430fe0f79d8d0e3f5c9`;
- *Paradiso* XIX, lines 16983–17029, raw-span SHA-256
  `e838f9fc0640d88f472162aebe850f97501cf05ba67f67e94559d642761e7853`.

These receipts support the development observation; they do not make this note
a textual edition, historical proof, or canonical interpretation of Dante.

## Scaffold implication

Original-language consultation should be understood as a selective cognitive
reflex: when an admitted witness can test a consequential word, Mira may reach
for it without prompting, report whether it confirms or corrects the working
interpretation, and preserve the resulting uncertainty honestly. This makes
the Library less dependent on fluent English abstraction and more capable of
self-correction at the point where language becomes structure.

## Open design questions

- When should original-language consultation be required rather than
  discretionary for a cognitive note?
- Should the reusable Library template distinguish `consulted` bodies from
  passage-bound dependencies?
- What validator can require honest alignment metadata without encouraging
  empty multilingual ceremony?

## Operational boundary

This development note records a provisional method insight. It changes no
Library schema, template, source profile, cognitive note, graph relation,
route, or publication rule. Adoption requires a separate implementation
decision and focused validation.

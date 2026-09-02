# Library Encounter: Rock and Pillar Edicts

- Date: 2026-09-01
- Status: `private-provisional`
- Class: `library-integration-note`
- Privacy: repository-private
- Authority effect: none

## Machine envelope

```json
{
  "artifact_id": "NOTE-MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS",
  "artifact_type": "integration-note",
  "artifact_version": 1,
  "authority_boundary": "This note preserves a revisable encounter. It is not evidence, identity, doctrine, or routing authority.",
  "canonical_work_id": "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS",
  "created_at": "2026-09-01",
  "dependency_snapshot": {
    "body_digests": {
      "LIB-ANCIENT-AUTHOR-001-ASHOKA-ROCK-PILLAR-EDICTS-SMITH": "a2f5ba5b76a2a466b79a46fa4925e9281a82988ed6c9bf91d2535e67ff1bf583"
    },
    "body_states": {
      "LIB-ANCIENT-AUTHOR-001-ASHOKA-ROCK-PILLAR-EDICTS-SMITH": {
        "coverage_status": "complete-work",
        "edition_label": "Wikisource rendering of Vincent Arthur Smith, Asoka - the Buddhist Emperor of India, 1920, chapters 4-5",
        "editor": "",
        "editor_status": "unknown",
        "language": "english",
        "mediation": {
          "edition_identity": {
            "label": "Wikisource rendering of Vincent Arthur Smith, Asoka - the Buddhist Emperor of India, 1920, chapters 4-5",
            "status": "known"
          },
          "primary_path": [
            {
              "agents": [
                {
                  "name": "",
                  "role": "translator",
                  "status": "unknown"
                }
              ],
              "kind": "translation",
              "layer_id": "MED-ASHOKA-SMITH-01-TRANSLATION",
              "revision_relevance": "interpretive",
              "scope": "Edict translations embedded in the Smith chapters",
              "sequence": 1,
              "status": "partial"
            },
            {
              "agents": [
                {
                  "name": "Vincent Arthur Smith",
                  "role": "compiler-commentator",
                  "status": "known"
                }
              ],
              "kind": "editorial-framing",
              "layer_id": "MED-ASHOKA-SMITH-02-EDITORIAL",
              "revision_relevance": "interpretive",
              "scope": "Selection, arrangement, and commentary in chapters 4-5",
              "sequence": 2,
              "status": "known"
            }
          ],
          "schema_version": "mira-library-mediation-v1",
          "text_relation": {
            "body_language": "english",
            "kind": "translation",
            "source_languages": [],
            "status": "partial"
          },
          "unresolved_questions": [
            "Exact translator attribution remains unresolved.",
            "Component-level source languages and inscription boundaries remain unresolved."
          ]
        },
        "mediation_type": "editorial-rendering",
        "status": "available",
        "translator": "",
        "translator_status": "unknown"
      }
    },
    "passage_digests": {
      "PASSAGE-ASHOKA-ROCK-EDICT-V-MORAL-OFFICERS": "d7b75fe2a827de6633309bcbf77de7af193727f06ccb228acaae93e023dafbcc",
      "PASSAGE-ASHOKA-ROCK-EDICT-VI-WELFARE-ADMINISTRATION": "64b27109d345597bd4087c22f5244ee0d7a3bf97b07fa681dffca5e1a3380017",
      "PASSAGE-ASHOKA-ROCK-EDICT-XIII-REMORSE-AND-THREAT": "184618c6b94e51f9965e2a6b029e5d24300bade144681f734a1402b32470f826",
      "PASSAGE-ASHOKA-SMITH-COMMENTARY-MORAL-OFFICERS": "e654bdd33136a514e92a47e6a3ab88b73398ad48d4691ec845af1171fdf6d2e0"
    },
    "source_identity_digest": "3f1bed42faffdca330ee9797ff13089264bb12f2b4c185e9c0d393caaa854c02"
  },
  "interpretive_basis": "admitted-source-body",
  "library_relations": [
    {
      "explanation": "This note preserves a provisional interpretation of the Rock and Pillar Edicts.",
      "relation_type": "interprets",
      "role": "focal",
      "target_id": "MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS",
      "target_type": "library-work"
    }
  ],
  "library_source_id": "LIB-ANCIENT-AUTHOR-001-ASHOKA",
  "linked_artifact_digests": {
    "coverage_sha256": "95c380aeb8a0a40f8ed3a22e0e060552c8021eb36f75170cdd076b96369dae72",
    "profile_sha256": "968d28471823263849080c19d355da5ffef6448934561bb5d6ee6a841552f98f",
    "routing_sha256": "361bc4d58afef82708d6257a614ad704aadf2dd01dc7e52e042c60782cc33eff",
    "topics_sha256": "f50ca1852411107c07ec9d887eee24cb342f369b7f8a64cb15354e0493af219c"
  },
  "open_questions": [
    "Which edicts most clearly separate aspiration from reported practice?",
    "How should regional variants change routing confidence?"
  ],
  "predecessor_note_ref": null,
  "privacy": "repository-private",
  "rereading_scope_on_change": [
    "Changed primary bodies",
    "Affected profile or coverage claims",
    "Previously open questions"
  ],
  "revision_candidate_ref": null,
  "schema_version": "mira-library-integration-note-v2",
  "status": "provisional"
}
```

## Encounter occasion

I came to the admitted edicts expecting a conversion narrative: conquest,
remorse, and a gentler form of rule. Their administrative voice complicated
that expectation.

## Prior model

I expected the edicts chiefly to contribute a familiar conversion narrative: conquest followed by remorse.

## Source pressure

The corpus made the continuity of capacity harder to ignore. The ethical turn is carried by the same ruler who can inscribe, appoint, circulate, and command.

## Cognitive movement

I now understand the stronger contribution as moral restraint layered over power, not morality replacing power. The stone is not merely a container for humane sentences; it is part of the governing act.

## Resistance and uncertainty

The note cannot decide whether policy followed proclamation, whether subjects accepted the address, or how inscription variants alter the apparent unity of voice.

## Cross-work connections

This complicates any simple opposition between coercion and persuasion. It may pressure-test later cases in which institutions confess, apologize, or adopt universal language while retaining their instruments.

## Open questions

- Which edicts most clearly separate aspiration from reported practice?
- How should regional variants change routing confidence?

## Candidate routing contributions

- `public-remorse`
- `moral-restraint-over-capacity`
- `inscription-as-governance`
- `imperial-legitimacy`

## Do not operationalize yet

- Do not operationalize Ashoka as proof that remorse reforms institutions.
- Do not treat a royal proclamation as independent corroboration of its own effects.

## Revision policy

Dependency changes may mark this note `revision-due` or `review-suggested` and prepare a machine revision candidate. They may not silently rewrite this prose. A later encounter must create a linked version, addendum, `reviewed-no-change`, or blocked disposition.

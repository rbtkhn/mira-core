# Library Encounter Addendum: Ashoka Passage Anchors

- Date: 2026-09-01
- Status: `private-provisional`
- Class: `library-integration-note-addendum`
- Privacy: repository-private
- Authority effect: none

## Machine envelope

```json
{
  "artifact_id": "NOTE-MIRA-WORK-ASHOKA-ROCK-PILLAR-EDICTS-ADDENDUM-01",
  "artifact_type": "integration-note",
  "artifact_version": 2,
  "authority_boundary": "This addendum preserves a revisable encounter. It is not evidence, identity, doctrine, or routing authority.",
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
  "disposition": "addendum",
  "interpretive_basis": "admitted-source-body",
  "library_relations": [
    {
      "explanation": "This addendum continues the provisional interpretation of the Rock and Pillar Edicts.",
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
    "How should regional inscription variants change routing confidence?",
    "What independent evidence can test implementation and reception?"
  ],
  "predecessor_note_ref": "archive/notes/2026-09-01-library-ashoka-rock-and-pillar-edicts-integration-note.md",
  "privacy": "repository-private",
  "rereading_scope_on_change": [
    "Changed primary bodies",
    "Changed passage anchors",
    "Affected routing counterweights"
  ],
  "revision_candidate_ref": "archive/library/integrations/pilot-2026-09-01/ashoka-rock-and-pillar-edicts/note-revision-candidate.json",
  "schema_version": "mira-library-integration-note-v2",
  "status": "provisional"
}
```

## Trigger

The first profile had no passage anchors. Adding exact spans for Rock Edicts V,
VI, and XIII materially changed the profile digest and correctly suspended both
Ashoka routes until the encounter could be revisited.

## What the passages changed

Rock Edict XIII makes the central tension textual rather than merely
interpretive. The proclamation places quantified conquest, remorse, a desire
for restraint, and a continuing warning of chastisement toward forest peoples
inside the same movement. The change is therefore not coercion disappearing;
it is coercive power being morally redescribed and partially restrained.

Rock Edicts V and VI make the administrative carrier equally concrete. Moral
instruction is assigned to new officers, joined to welfare functions, and
connected to permanent reporting and the dispatch of public business. Dhamma
is not only an ethical vocabulary. In these proclamations it becomes an
institutional program conducted through imperial channels.

## Counterpressure

Smith's warning that the moral officers could become tyrannical is useful only
as editorial counterpressure. It is not Ashoka's speech and does not prove
actual abuse. The primary counterweight lies within Edict XIII itself: the
language of remorse continues to reserve punishment.

## Revised understanding

The original note survives, but its mechanism is now narrower and stronger:
public remorse can change the declared purpose and legitimating language of
power while the machinery and limiting threat of coercion remain visible.
Institutionalization makes the ethical turn more consequential and more
dangerous, because the same channels can carry welfare, instruction, or
discipline.

## Routing disposition

The `ashoka-remorse-capacity` and `ashoka-inscription-governance` routes return
to `provisional` with exact primary anchors and typed counterweights. Their
confidence does not rise above `medium`; proclamation still cannot establish
implementation or reception.

## Do not operationalize yet

- Do not treat the moral officers as proof of humane administration.
- Do not turn Smith's commentary into primary evidence.
- Do not infer that remorse abolished force or created accountable government.

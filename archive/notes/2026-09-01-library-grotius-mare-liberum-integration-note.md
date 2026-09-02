# Library Encounter: Mare Liberum

- Date: 2026-09-01
- Status: `private-provisional`
- Class: `library-integration-note`
- Privacy: repository-private
- Authority effect: none

## Machine envelope

```json
{
  "artifact_id": "NOTE-MIRA-WORK-GROTIUS-MARE-LIBERUM",
  "artifact_type": "integration-note",
  "artifact_version": 1,
  "authority_boundary": "This note preserves a revisable encounter. It is not evidence, identity, doctrine, or routing authority.",
  "canonical_work_id": "MIRA-WORK-GROTIUS-MARE-LIBERUM",
  "created_at": "2026-09-01",
  "dependency_snapshot": {
    "body_digests": {
      "LIB-COLONIAL-AUTHORITY-065-GROTIUS-MARE-LIBERUM-LATIN-WIKISOURCE": "f5fd4847ecb3e2b8d83ef41c8f788d5f7a0fca2326fa2e6f6d4de37192c64c33"
    },
    "body_states": {
      "LIB-COLONIAL-AUTHORITY-065-GROTIUS-MARE-LIBERUM-LATIN-WIKISOURCE": {
        "coverage_status": "unknown",
        "edition_label": "Latin Wikisource extraction of Mare liberum, page revision downloaded/extracted 2026-08-21",
        "editor": "",
        "editor_status": "unknown",
        "language": "latin",
        "mediation": {
          "edition_identity": {
            "label": "Latin Wikisource extraction of Mare liberum, page revision downloaded/extracted 2026-08-21",
            "status": "partial"
          },
          "primary_path": [
            {
              "agents": [
                {
                  "name": "Latin Wikisource",
                  "role": "text-provider",
                  "status": "known"
                }
              ],
              "kind": "transcription",
              "layer_id": "MED-GROTIUS-MARE-LIBERUM-01-TRANSCRIPTION",
              "revision_relevance": "textual-integrity",
              "scope": "Admitted Latin Wikisource extraction",
              "sequence": 1,
              "status": "known"
            }
          ],
          "schema_version": "mira-library-mediation-v1",
          "text_relation": {
            "body_language": "latin",
            "kind": "original-language",
            "source_languages": [
              "latin"
            ],
            "status": "known"
          },
          "unresolved_questions": [
            "Critical editor and upstream print-edition lineage remain unresolved."
          ]
        },
        "mediation_type": "original-language",
        "status": "available",
        "translator": "",
        "translator_status": "not-applicable"
      }
    },
    "passage_digests": {
      "PASSAGE-GROTIUS-CAPUT-XII-DUTCH-AND-UNIVERSAL-UTILITY": "b81016e8ba55cf47a4ed015ff1503e84dcc0adadbd126e544aaafa264741ee9a",
      "PASSAGE-GROTIUS-CAPUT-XIII-COMMON-RIGHT-ARMED-ENFORCEMENT": "01405e941c3988782503c7b3e2a0812b5bb32f30c1b0436deba5dbb829045e54",
      "PASSAGE-GROTIUS-COMMON-USE-NONAPPROPRIATION": "b56446a1d4ae966c071f5c2e0093ccc8ec13d5721ff14384b38866bcd671eff7"
    },
    "source_identity_digest": "9639cc018cdc31830aa4536125486574c238a6d71f21bf7e2ae59c5ca4998019"
  },
  "interpretive_basis": "admitted-source-body",
  "library_relations": [
    {
      "explanation": "This note preserves a provisional interpretation of Mare Liberum.",
      "relation_type": "interprets",
      "role": "focal",
      "target_id": "MIRA-WORK-GROTIUS-MARE-LIBERUM",
      "target_type": "library-work"
    }
  ],
  "library_source_id": "LIB-COLONIAL-AUTHORITY-065-GROTIUS-MARE-LIBERUM",
  "linked_artifact_digests": {
    "coverage_sha256": "f4a4c8ea4b126c85452bc1db7ebd08a02c3ef7002f081e77f01a5cf6ed4165b6",
    "profile_sha256": "d4ab685c98e0097137c36a6092023048f734bd24e81169cae3ba1aaeea6b0bef",
    "routing_sha256": "008d3ad1ca6982f38bd66c5487aae6938ef4e78b0088a0189208a7defae65dc5",
    "topics_sha256": "c23d7e6baaa9eda27aba263f6874478420992157452f5acce69bcbe93a957765"
  },
  "open_questions": [
    "Which claims remain persuasive when detached from the VOC controversy?",
    "What countertexts best expose the distribution of freedom and coercion?"
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

I approached the admitted Latin tract expecting a genealogy of open-seas
doctrine. Its movement from common use to Dutch advantage and finally to armed
vindication made the argument less serene and more revealing.

## Prior model

I expected Mare Liberum to contribute a straightforward genealogy of open-seas doctrine.

## Source pressure

The tract itself places its universal argument beside the Dutch claim to participate in the trade it seeks to open. The work does not stand outside the contest it seeks to order.

## Cognitive movement

I no longer treat interest as a debunking revelation or universality as proof of neutrality. The more useful pattern is translation: a situated need becomes legal grammar capable of traveling beyond its origin.

## Resistance and uncertainty

The current body has edition uncertainty and is Latin. My English formulations are interpretive paraphrases, not quotations from an admitted translation. Rival maritime claims and the perspectives of those subjected to company power remain absent.

## Cross-work connections

This is immediately relevant to persuasive language about open systems, common access, and rules that advantage challengers to an incumbent order.

## Open questions

- Which claims remain persuasive when detached from the VOC controversy?
- What countertexts best expose the distribution of freedom and coercion?

## Candidate routing contributions

- `maritime-access-order`
- `universal-principle`
- `rising-power-law`
- `commercial-hegemony`

## Do not operationalize yet

- Do not route the text as disinterested law.
- Do not use historical analogy as current legal adjudication.

## Revision policy

Dependency changes may mark this note `revision-due` or `review-suggested` and prepare a machine revision candidate. They may not silently rewrite this prose. A later encounter must create a linked version, addendum, `reviewed-no-change`, or blocked disposition.

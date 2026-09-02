# Library Encounter Addendum: Grotius Route Review

- Date: 2026-09-01
- Status: `private-provisional`
- Class: `library-integration-note-addendum`
- Privacy: repository-private
- Authority effect: none

## Machine envelope

```json
{
  "artifact_id": "NOTE-MIRA-WORK-GROTIUS-MARE-LIBERUM-ADDENDUM-02",
  "artifact_type": "integration-note",
  "artifact_version": 3,
  "authority_boundary": "This addendum preserves a revisable route review. It is not evidence, identity, doctrine, route approval, current-event verification, publication, or authority to act.",
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
  "disposition": "addendum",
  "interpretive_basis": "admitted-source-body",
  "library_relations": [
    {
      "explanation": "This addendum continues the provisional interpretation of Mare Liberum through its reviewed route encounter.",
      "relation_type": "interprets",
      "role": "focal",
      "target_id": "MIRA-WORK-GROTIUS-MARE-LIBERUM",
      "target_type": "library-work"
    }
  ],
  "library_source_id": "LIB-COLONIAL-AUTHORITY-065-GROTIUS-MARE-LIBERUM",
  "linked_artifact_digests": {
    "coverage_sha256": "f4a4c8ea4b126c85452bc1db7ebd08a02c3ef7002f081e77f01a5cf6ed4165b6",
    "profile_sha256": "ed56e184d5e6d5361d4c0200ccd7f94f950bbf02b7eb136afcda5a481ceabaf5",
    "routing_sha256": "f2fdbfc6c67db88375eafaab29e4c4dec5c81e3e96381fdc5ee693936c950045",
    "topics_sha256": "c23d7e6baaa9eda27aba263f6874478420992157452f5acce69bcbe93a957765"
  },
  "open_questions": [
    "Which claims remain persuasive when detached from the VOC controversy?",
    "What rival text should supply the closed-seas counterargument?",
    "What admitted counterpart can test the distribution of access and coercion?"
  ],
  "predecessor_note_ref": "archive/notes/2026-09-01-library-grotius-mare-liberum-integration-note-addendum-01.md",
  "privacy": "repository-private",
  "rereading_scope_on_change": [
    "Changed primary bodies",
    "Changed passage anchors",
    "Changed route claims or lineage assessments"
  ],
  "revision_candidate_ref": "archive/library/integrations/pilot-2026-09-01/grotius-mare-liberum/note-revision-candidate-005.json",
  "schema_version": "mira-library-integration-note-v2",
  "status": "provisional"
}
```

## Purpose

This addendum records a human-review pass over both Grotius route units. The
review asked whether each route stayed inside the admitted Latin passages and
whether dependent context was being mistaken for independent confirmation.

## Observed in the admitted body

The common-use passage denies an exclusive prescriptive right over navigation.
Chapter XII directly joins Dutch utility to the utility of humanity. Chapter
XIII moves from the asserted common commercial right to armed vindication when
judgment is unavailable.

## What changed

The `grotius-interested-universal` route now names the Dutch claimant and
Portuguese exclusion, and it limits its proposition to the conversion of an
interested access claim into universal legal grammar. It no longer depends on
the broader label of a rising power.

The `grotius-open-access-coercion` route now describes the conjunction actually
present in the tract: a common-access claim paired with a claimed right of
armed enforcement. It no longer treats the text by itself as evidence that one
historical monopoly produced a realized successor coercive order.

Both routes now state their lineage dependence and rejection conditions. The
contextual interpretive packet remains useful for sponsor setting, but it is
not independent corroboration of the tract or of subsequent outcomes.

## Human judgment retained

Both routes remain `unreviewed`. This addendum narrows their claims and improves
their reviewability; it does not supply the later approval disposition or its
digest binding.

## Remaining counterpressure

The Library still lacks an admitted closed-seas rival and an admitted
counterpart capable of testing who received access, who bore coercion, and how
the rule operated beyond its advocate's formulation. Edition identity and an
admitted translation also remain unresolved.

## Do not operationalize yet

- Do not treat either route as current legal authority or present-fact evidence.
- Do not infer realized institutional outcomes from the tract alone.
- Do not use either route in the Strategy Notebook until human approval is
  recorded against current digests.

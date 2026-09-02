# Library Encounter Addendum: Grotius Passage Anchors

- Date: 2026-09-01
- Status: `private-provisional`
- Class: `library-integration-note-addendum`
- Privacy: repository-private
- Authority effect: none

## Machine envelope

```json
{
  "artifact_id": "NOTE-MIRA-WORK-GROTIUS-MARE-LIBERUM-ADDENDUM-01",
  "artifact_type": "integration-note",
  "artifact_version": 2,
  "authority_boundary": "This addendum preserves a revisable encounter. It is not evidence, identity, doctrine, or routing authority.",
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
      "explanation": "This addendum continues the provisional interpretation of Mare Liberum.",
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
    "What rival text should supply the closed-seas counterargument?"
  ],
  "predecessor_note_ref": "archive/notes/2026-09-01-library-grotius-mare-liberum-integration-note.md",
  "privacy": "repository-private",
  "rereading_scope_on_change": [
    "Changed primary bodies",
    "Changed passage anchors",
    "Affected routing counterweights"
  ],
  "revision_candidate_ref": "archive/library/integrations/pilot-2026-09-01/grotius-mare-liberum/note-revision-candidate.json",
  "schema_version": "mira-library-integration-note-v2",
  "status": "provisional"
}
```

## Trigger

The first profile had no passage anchors. Adding exact spans for the common-use
argument and Chapters XII and XIII materially changed the profile digest and
correctly suspended both Grotius routes until the encounter could be revisited.

## What the passages changed

The common-use passage gives the universal claim its textual footing. In my
English paraphrase of the admitted Latin, no state can acquire against humanity
a prescriptive right to exclude others from a sea whose use remains common
under the law of nations. This is not a quotation from an admitted translation.

Chapter XII then makes the positional interest unusually explicit. Grotius
does not deny Dutch advantage. He presents Dutch advantage as joined to the
advantage of humanity and answers Portuguese lost profit with a general right
of participation. The conjunction of principle and interest therefore appears
inside the tract itself.

Chapter XIII supplies the harder counterpressure. When judgment is unavailable,
the asserted common right may be vindicated through just war. The movement
from open commerce to armed enforcement belongs to the argument itself.

## Counterpressure

Chapter XII describes Portuguese exclusion through greed and monopoly while
presenting Dutch advantage as joined to humanity's advantage. Chapter XIII
then exhorts the Dutch as a nation powerful at sea to defend not merely their
own liberty but humanity's. This rhetorical asymmetry is an internal
counterweight: the claimant's interest is universalized while the opponent's
interest is moralized as obstruction. It does not by itself refute the
non-appropriation argument.

The Library still lacks Selden's *Mare Clausum* or another admitted closed-seas
rival. The packet is therefore counterweighted but not textually balanced.

## Revised understanding

The original note survives, but the relation between universal principle and
strategic interest is now internally anchored. Grotius's persuasive power lies
partly in making the claimant's advantage appear as an instance of a common
right. The same movement creates the danger: enforcement by a rising commercial
power can travel under the moral prestige of universal access.

## Routing disposition

The `grotius-interested-universal` and `grotius-open-access-coercion` routes
return to `provisional` with exact primary anchors and typed internal
counterweights. Confidence remains `medium` and `low`, respectively,
because edition, translation, rival-text, and colonized-counterpart gaps remain.

## Do not operationalize yet

- Do not treat Dutch benefit as proof that the principle is false.
- Do not treat universal phrasing as proof that the advocacy is neutral.
- Do not claim a balanced maritime-law comparison until a genuine rival text is admitted.

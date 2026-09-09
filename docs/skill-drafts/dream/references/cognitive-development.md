# Library-informed strategic continuity

This prospective composition contract uses existing private stores. It creates
no automatic note, routing activation, identity, RSI, or publication authority.

## One bounded composition cycle

1. Read the prepared brief's `strategy_context`: historical strategic excerpts,
   separately labeled later context, Library Journal corrections and earlier
   applications, and the Library metadata pre-scan. If the scan is already
   present, reuse it rather than repeating it. Frozen context has a SHA-256.
2. State the Geo-source-based provisional estimate before Library passage use.
   Preserve that baseline in the existing private adjudication input. If no
   source-grounded mechanism exists, mark analysis deferred; never substitute
   titles or historical analogies for source analysis.
3. For a credible Library match, use `library-reasoning geo-pilot`, read its
   passages, and use `adjudicate --check` then `adjudicate` with exact packet
   bindings. One pre-scan, one passage packet, one adjudication; no automatic
   second retrieval loop. Follow Library Reasoning's route eligibility and
   private-storage rules. A failed private-carrier write stops this Library
   operation, not Dream. Record debt and continue the daily close.
4. Record effect or no material change in Notebook. Preserve the strongest rival,
   decisive structural difference, rejection condition, and unverified claims.
   An ineligible route may be held or rejected; it cannot change the estimate.
5. After Notebook composition, refresh an unfinished Journal bundle with
   `mira-journal prepare --date DATE --output-root ROOT --refresh-strategy-context`.
   This preserves transcript checkpoints and reading acknowledgements. Update
   the draft's composition-brief source and derivation bindings to the returned
   digest. Do not refresh finalized entries. Consume the refreshed context; a
   changed digest is not a claim that old text was read again.
6. Compose Journal only where this work changes remembered reasons or practice.
   No mandatory strategic paragraph. Historical source text, Library trials,
   Journal ancestry, verified facts, and learning outcomes remain distinct.
7. Consider note nominations, record a substantive Library application where
   warranted, and finish Dream. Missing sources, no useful note, and unfinished
   analysis are honest outcomes.

`context_consumption` in both draft.json and technical-reference.json has
`strategy` and `library` objects. Each has `status` (`used`,
`considered-not-used`, `unavailable`, or `deferred`) and `reason`. A used object
also has `context_sha256` (the entire frozen strategy_context digest) and
`prose_anchors` (exact prose also grounded in technical-reference items).
Unavailable context cannot be called used. This declaration records use, not
comprehension, truth, or authority. Legacy bundles without this context retain
their existing contract.

## Candidate-only note judgment

Run `strategy-notebook note-search --focus QUESTION --json`; read the full
strongest existing matches before deciding novelty. Classify create, amend,
challenge, close, or no note. Prefer amendment for the same central question.
Do not create notes to make the learning loop appear productive.

Optional `note-candidates.json` beside the private draft is a JSON list of at
most three judgments; an empty list means no nomination. Validate with
`strategy-notebook check-nominations --input FILE --json` before resuming.

Each candidate contains:

- `operation`: create, amend, challenge, or close; `note_class`: a Mira Notes class;
  `owner`: mira-notes or library-integration; `target_path`: exact repo-relative
  path; `target_sha256` for an existing note.
- `central_question`, `change`, `why_it_matters`, `proposed_edit`,
  `strongest_objection`, `next_test`, and `limitations`.
- `duplicate_search`: `reason` and `inspected` list of `{path, sha256}` bindings.
- `source_bindings`: nonempty `{path, sha256}` list, including applicable
  adjudication artifacts. Private Library paths must remain under their owner.
- `ranking`: integer 0–3 values for consequence, evidence, novelty, testability.

Dream validates and ranks candidates, assigns deterministic identities, and
stores them in existing ROI `note_candidates`. Invalid targets become explicit
debt, never an automatic edit. Check again before any later authorized mutation.
Use Library's existing per-work harvest for explicit constellation packets;
ordinary note nominations are not a substitute for that governed harvest.

## Later use

Library Journal records substantive applications through its existing owner:
predecessor thread, rejection condition, distinct application artifact, effect,
failed transfer or no change. Routine retrieval creates no entry. Notes remain
proposals until separately authored. Future use must retrieve corrections.

Routing proposals use existing observation thresholds and remain inactive.
Recursive Learn alone assesses the five evidence stages. Retrospective
rehearsals, code tests, useful retrieval, and Journal interpretation are not
later-use outcomes. Retain the existing calibration gates and disclose missing
measurements. Do not start a scheduler or collect unrelated history.

# Batch triage with local quotation checks

Use only for an authorized source batch. The shared consultation ceiling still
applies; a larger allowance requires explicit user direction.

1. Prepare only approved source text and necessary titles/public provenance with
   stable source and paragraph IDs. Keep local paths and private metadata out of
   the upload. Working files need an exact authorized private destination; run
   session-preflight before temporary-file workloads. Do not save them by default.
2. Ask the provider for a bounded shortlist with source IDs, paragraph IDs, short
   exact anchors, and attributed candidate interpretations. Request coverage and
   retrieval limits, not an unsupported claim of exhaustive reading.
3. Run the [quotation checker](../../../scripts/check_consultation_quotes.py)
   before relying on anchors. Using the canonical Python runtime:
   `python scripts/check_consultation_quotes.py --index <private-index.json> --quotes <private-quotes.json>`.
   The index is the pilot format: a nonempty list of source objects with `id` and
   `paragraphs`, each paragraph containing `id` and `text`; other metadata is ignored.
   Quotes are a nonempty list of `{"paragraph_id":"S01-P001","quotation":"exact words"}`.
   No capitalization, punctuation, whitespace, or ASR normalization is performed.
   Stdout reports row numbers and statuses without source text; exit codes are
   0 for all passed, 1 for mismatches/missing paragraphs, and 2 for invalid input.
   The callable `check_quotes(index, quotes)` also supports in-memory checks.
4. Inspect selected passages for meaning, attribution, hypotheticals, numerical
   precision, and compatible mechanisms. An exact quotation can still fail to
   support its attached interpretation. Repair locally when the text resolves
   the issue, label Mira's repair, and rerun the literal check. Otherwise withhold
   the claim or use a budgeted follow-up for genuinely missing evidence.
5. Sample omitted sources and disclose how the sample was selected and its size.
   Report unique words inspected, not an inferred recall or completeness score.
   Keep a reading guide distinct from source verification and archive admission.

Report actual provider retention and explicitly authorized local working files
separately. Neither checking nor triage authorizes new uploads, durable receipts,
archive mutation, or publication.

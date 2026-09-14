# Contextual ASR correction

Use surrounding transcript text to recover likely intended wording. The goal
is faithful, readable source text, with uncertainty retained. Never attempt
audio recovery, playback for verification, audio download, new speech
recognition, or requests for recordings. Do not open a video merely to check
a correction. Existing timestamps remain useful locators in the text.

## Read, infer, compare

Read the complete passage around each suspect span, including the preceding
question and following answer. Expand to the topic's full exchange when needed;
consult repeated wording elsewhere in the same transcript. Correct clear ASR
errors rather than merely listing them as candidates when context supports one
reading. Prefer the smallest replacement that restores the intended wording.

Use syntax, the local argument, repeated references, and already-established
speaker identity together. A title or general world knowledge may suggest a
candidate but cannot alone establish what was said. Do not make a speaker's
claim more factually plausible, stronger, or more consistent with your views.
Preserve hedges, negations, causal direction, attribution, and disagreements.

Apply a correction when the surrounding text strongly selects one reading and
there is no materially plausible rival. Leave the original wording when several
readings remain possible; explain the uncertainty alongside the passage or in
the change record. Do not fabricate missing sentences. Numbers, dates, units,
negations, and technical terms need particularly strong local support; their
implausibility alone is insufficient. Do not turn apparent repetition into a
deletion unless the text establishes a duplicated caption fragment.

## Output and preservation

For a sample, return corrected text plus a compact before/after/reason table
and unresolved spans. For an authorized saved derivative, preserve the original
capture unchanged and record source path, source hash, model/session, and each
substantive replacement with its timestamp or unique textual anchor, supporting
context, rationale, and confidence. Label the result `contextually corrected;
inferred from transcript text; not audio-verified`. This label is descriptive,
not a new canonical metadata enum or proof that all errors were found.

Re-read the corrected passage in context and compare it with the original.
Check that only intended spans changed and that meaning-bearing qualifiers,
speaker turns, and order survive. Keep unresolved spans explicit. Later models
may revise a correction from the preserved text and reasoning; model novelty
does not itself justify replacing an earlier reading.

Archive admission and canonical body replacement retain their owning workflow
and exact-scope authority. The current `archive-repair --class asr` engine
applies its approved substitution rules only; it cannot execute an arbitrary
contextual patch. Do not disguise a model inference as an approved global rule,
use body-merge as a bypass, or overwrite canonical sources directly. A contextual
sample finishes conversationally unless saving is requested. An explicit repair
batch authorizes automatic private retention through the contextual command
family below, including agent review. Raw unlanded captures stay unlanded.

## Private memory workflow

Use `tools/run.ps1 archive-repair contextual`. Every command returns JSON.
Storage resolves through the portable state resolver to
`<state-root>/state/asr/<workspace-id>/`, outside Git. `--state-root` is an
optional absolute portable root override placed before the subcommand.
The workspace ID is a hash of the resolved workspace path. Moving a checkout
creates a different namespace; copying another workspace's memory is not implicit.

1. `prepare --path <explicit-source>` (repeat for multiple inputs) freezes UTF-8
   bytes and existing provenance under `prepared/<id>/`. It returns source
   hashes, body boundaries, and relevant history. Raw `.txt` captures require
   an unambiguous Geopolitics queue binding; archived sources require manifest
   membership. This creates no admission or canonical status change.
2. Read manageable passages with preceding question, following answer and
   repeated references. Record actual UTF-8 **byte offsets**, not character
   offsets. Mark everything not read explicitly; reading coverage is an agent
   declaration, not a machine proof of understanding.
3. `search --wording <suspect-text> --context <nearby-terms>` retrieves bounded
   examples. Optional `--speaker`, `--channel`, `--limit` refine ranking.
   Exact wording ranks first, then lexical context and metadata. Same-source
   repetitions are grouped with their IDs; frequency does not establish truth.
   Relevant rejected, unresolved and superseded examples appear separately,
   with review reasons. Legacy substitution tables are not imported as successes.
4. Author a packet following the schema below. Reconsider each occurrence;
   returned examples never authorize automatic replacement. Re-read corrected
   passages, then `check --packet <json-path>` to inspect exact proposed diffs.
5. `save --packet <same-json-path>` revalidates current source bytes and writes
   the immutable batch under `batches/<packet-hash>/`. Save stores packet,
   derivatives, completion receipt and report together. An identical packet
   reuses its receipt. Changed source bytes require preparing a new input.
6. `review --correction-id <batch-id>:<index> --disposition confirmed|rejected|superseded
   --reason <reason> --model <model> --session <session>` appends a review event.
   Supersession also requires `--superseded-by <existing-correction-id>`.
   Reviews change suggestion eligibility, never rewrite an old derivative.
   A revised reading requires a new validated batch and a supersession event.
7. `report --batch-id <id>` returns paths, exact diff, reading coverage,
   unresolved/rejected counts and current review dispositions. Report captured
   scope and gaps separately from the quality judgment.

Packet shape (offsets and hashes below are illustrative):

```json
{
  "schema_version": 1,
  "prepared_id": "<prepare ID>",
  "model": "<actual agent model label>",
  "session": "<session ID>",
  "created_at": "2026-09-13T12:00:00+00:00",
  "coverage": [{
    "source_sha256": "<source hash>",
    "read_spans": [[100, 500]],
    "remaining": "Bytes before 100 and after 500 remain unread."
  }],
  "corrections": [{
    "source": 0,
    "source_sha256": "<source hash>",
    "start": 200,
    "end": 205,
    "original": "<exact original span>",
    "replacement": "<minimal correction>",
    "status": "accepted",
    "timestamp": "4:37",
    "context": "<exact contiguous original passage containing the span>",
    "rationale": "<why this passage strongly selects this reading>",
    "confidence": "high",
    "example_ids": [],
    "reviewed_in_context": true
  }]
}
```

Coverage has one record per selected source, in order. Spans are half-open
byte ranges and may be adjacent but cannot overlap. Accepted corrections need
high confidence and context reread acknowledgement. Record unresolved and
rejected candidates with their original spans and reasoning; their replacement
may be null and they never alter output. Include timestamps when supplied.
Unknown example IDs, stale source hashes, incorrect original spans, overlapping
edits, unread context, and wrapper/marker edits fail closed. Untouched bytes,
line endings and Unicode are preserved. Do not edit implausible numbers,
negations, attribution, missing openings or source claims without strong local
support; validation cannot determine the semantic correctness of an inference.

Interrupted writes never publish a completed batch directory. Incomplete
`.pending-*` directories are ignored and may be inspected after a crash; a
retry reconstructs the object. A leftover `.review-lock` blocks new reviews:
verify that no writer remains before removing that exact lock. Do not erase
review events or silently repair corrupt receipts. No model call, embedding,
external service, audio action, rule promotion or global synchronization occurs.

## Review examples

- In a passage about exporting oil through the Persian Gulf, `the state of
  Hormuz` can become `the Strait of Hormuz`: the local shipping context selects
  the geographic passage. Identify the correction as inference.
- `Baband` without enough surrounding detail remains unresolved. If the wider
  exchange independently identifies Bab el-Mandeb, propose that expansion with
  the supporting text; familiarity with the headline alone is insufficient.
- Preserve an implausible oil-volume number when local text supplies no clear
  alternative. Correcting a factual claim is not ASR repair.
- A missing opening sentence stays missing. Do not create an audio task or
  invent connective prose to conceal the gap.

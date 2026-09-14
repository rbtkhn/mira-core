---
name: library-reasoning
description: "Run the bounded Mira Library historical pressure-test pilot for a manifest-backed Geo-Strategy question. Use for metadata pre-scans, private passage packets, analogy and anti-analogy review, and Geo-Strategy adjudication; do not use it to verify live facts or create statistical base rates."
---

# Library Reasoning Pilot

Use this pilot after geopolitical intake has landed and a crisis object is in
view. It tests whether Mira Library materially changes a Geo-Strategy judgment
without making historical authority a substitute for live evidence.

For a materially relevant correction or explicit developmental review, use
[Mind development practice](../mira-mind/references/development-practice.md) within
existing application and correction records. Preserve rejected analogies and cases
where guidance does not apply; an illuminating interpretation is not successful
transfer. Domain evidence and application owners remain controlling.

## Sequence

For continuity relevant to the crisis question, consult `library-journal context`
with that question as `--focus`. Treat retrieved cognitive trials and metaphors
as provisional questions; preserve corrections and failed transfers. They do
not establish passage grounding or route eligibility and cannot bypass the
packet and adjudication sequence below. Meaningful later-use artifacts may be
referenced in a subsequent private Library Journal encounter entry.

State how recovered context changed the question, or why it did not help.
Record a substantive application with Library Journal's `kind: application`,
binding its predecessor, reused thread, and separate review artifact; do not
label a geopolitical application as a new shared reading.

1. Before settling the mechanism, run a metadata-only scan:

   ```powershell
   tools\run.ps1 library-reasoning pre-scan --crisis-object "..." --mechanism "..." --json
   ```

2. After Geo-Strategy states a provisional mechanism, produce one bounded
   private packet:

   ```powershell
   tools\run.ps1 library-reasoning geo-pilot --date YYYY-MM-DD --crisis-object "..." --mechanism "..." --json
   ```

   Reasoning packets belong under repository-local `.mira-private`. If that
   directory is not writable, stop and report the private-carrier blocker rather
   than creating new packet state under `C:\private`.

   Packet v3 may also consume the validated current-head Library cognitive
   inventory. Read only explicit profile signatures, framing arrays, and
   authored graph relationships; never derive a relation or claim from prose.
   A direct positive signature may nominate a source, while a matching negative
   signature cancels that promotion. Comparative edges widen framing exactly
   one hop and never borrow passages or routing authority.

   A registered constellation may be selected explicitly in both commands:

   ```powershell
   tools\run.ps1 library-reasoning pre-scan --crisis-object "..." --mechanism "..." --constellation-id ID --json
   tools\run.ps1 library-reasoning geo-pilot --date YYYY-MM-DD --crisis-object "..." --mechanism "..." --constellation-id ID --json
   ```

   Explicit selection binds the manifest digest, current note heads, profiles,
   and each member's own admitted passage anchors. It does not infer an edge,
   borrow another member's passages, or create route eligibility. Matching
   negative signatures remain visible for adjudication rather than silently
   suppressing an operator-selected member.

3. Geo-Strategy must adjudicate every candidate as `adopted`, `narrowed`,
   `redirected`, `rejected`, or `held`. Adopted material requires a shared
   mechanism, decisive structural difference, rejection condition, concept
   bridge, lineage assessment, and effect on judgment.

   New adjudications use `mira-library-adjudication-v2`. The adjudication input
   must contain a `source_packet` binding with the packet ID, exact file
   reference, and byte SHA-256 prepared before review. Run:

   ```powershell
   tools\run.ps1 library-reasoning adjudicate --packet FILE --adjudication FILE --check --json
   tools\run.ps1 library-reasoning adjudicate --packet FILE --adjudication FILE --json
   ```

   Adjudication rejects a changed packet before applying decisions. A
   successful non-check run atomically writes the adjudicated packet and emits
   a private `mira-library-adjudication-receipt-v1` binding the pending packet
   digest, adjudication input, final packet digest, and reviewed passage
   digests. Never treat packet ID alone as content identity.

4. Mira Mind may express only adjudicated material. During the pilot it must
   not open another retrieval loop.

Successful non-check adjudication appends sanitized private routing
observations. These records describe retrieval usefulness and failure, never
the truth of a geopolitical conclusion. Use `--check` when no observation
should be written.

Cognitive context is adjudicated separately as `used-materially`,
`used-nonmaterially`, `rejected`, or `held`. Only direct, passage-grounded
material use may contribute to a route-review nomination. Operational
dispositions still require an eligible route; a current cognitive head does
not replace the reviewed predecessor bound to that route.

After an explicit constellation packet is adjudicated, prepare a private
per-work review surface with:

```powershell
tools\run.ps1 library-reasoning harvest-note-candidates --packet FILE --check --json
tools\run.ps1 library-reasoning harvest-note-candidates --packet FILE --json
```

The harvest distinguishes admitted source support, the Geo-Strategy case
prompt, tagged interpretive change, and Geo-only evidence. It may classify a
work as `no-change`, `open-question`, `note-candidate`,
`successor-note-candidate`, or `routing-observation-only`, but it never authors
or revises a note and never changes the registry or route graph.

Harvest v2 binds the exact adjudicated packet reference and byte SHA-256; its
identity changes when the packet bytes change. Verify any receipt, harvest, or
comparison carrying `artifact_bindings` with:

```powershell
tools\run.ps1 library-reasoning verify-lineage --artifact FILE --json
tools\run.ps1 library-reasoning verify-lineage --artifact FILE --require-digest-bound --json
```

The verifier is read-only and reports `digest-bound`, `legacy-id-bound`,
`missing`, or `mismatch`. Existing v1 harvests remain readable and are reported
honestly as `legacy-id-bound`; they are never silently upgraded or rewritten.
New comparison or review artifacts should use `artifact_bindings` entries with
`role`, `ref`, `sha256`, and an `artifact_id` when the source has one.

## Recursive Routing

Inspect observations and prepare an inactive proposal:

```powershell
tools\run.ps1 library-reasoning learning-status --json
tools\run.ps1 library-reasoning calibration-status --json
tools\run.ps1 library-reasoning propose-routing-update --check --json
tools\run.ps1 library-reasoning propose-routing-update --json
tools\run.ps1 library-reasoning propose-route-review-candidates --check --json
tools\run.ps1 library-reasoning propose-route-review-candidates --json
```

A proposal requires three consistent adjudications across two crisis
signatures. Activation and rollback remain explicit operator boundaries:

```powershell
tools\run.ps1 library-reasoning activate-routing-memory --input FILE --check
tools\run.ps1 library-reasoning activate-routing-memory --input FILE
tools\run.ps1 library-reasoning rollback-routing-memory --check
tools\run.ps1 library-reasoning rollback-routing-memory
```

`MIRA_CORE_LIBRARY_REASONING_TEXT_ROOTS` supplies ordered read-only private
roots for reasoning. It does not alter the canonical Library admission,
verification, or census root. Routing memory may learn only capped,
profile-scoped retrieval adjustments; it may not learn present-event truth,
base rates, preferred prose, or historical prestige.

Route-review candidates require three consistent material direct uses across
two crisis signatures, no effective rejection, and unchanged note, dependency,
and profile digests. They remain inactive private nominations and create no
route or review.

## Recursive Learning Handoff

Library observations do not establish Recursive Learning. After real later
use, prepare a private `mira-library-learning-export-spec-v1` and run:

```powershell
tools\run.ps1 library-reasoning export-learning-reference --spec FILE --output ABSOLUTE_EXTERNAL_PATH --check --json
tools\run.ps1 library-reasoning export-learning-reference --spec FILE --output ABSOLUTE_EXTERNAL_PATH --json
```

The specification identifies effective cognitive observation events, states
explicit observation and diagnosis claims, and binds repository-relative stage
artifacts by SHA-256. Notes, packets, and private events remain provenance only.
An intervention requires commit references; an outcome requires distinct
later-use evidence. Export creates assessment input, never an RSI candidate or
ledger admission.

## Boundaries

- Registry and private source bodies are read-only.
- The full packet and passages remain under `.mira-private/`.
- `LIB-*` references cannot satisfy `SRC-*` coverage, verify an `OPC-*`, resolve
  a forecast, or support numerical base-rate claims.
- Shared textual or intellectual ancestry is not independent convergence.
- Absence of a credible rival or non-elite witness must remain a named gap.
- Tracked quotations require an outward-use posture; private availability is
  insufficient.
- Staging, commit, push, Archive ingestion, and publication are separate.
- Routing activation and recursive-learning ledger admission are separate
  exact-authority boundaries.
- Mira Memory may report Library relevance and route ownership, but it is not a
  runtime dependency or writer for this workflow.

## Pilot Review

Compare the same case without Library, with the adjudicated pressure test, and
after Mira Mind composition. Record whether the Library changed the mechanism,
introduced a rival, exposed anachronism, prevented an overclaim, improved a
falsifier, or changed nothing material. Advance beyond the pilot only after
four reviewed cases, at least three material improvements, no unresolved
evidence laundering, and proportionate cadence cost.

Validate and record a private review with `ablation-review --review FILE`; use
`advancement-status --json` to calculate the gate. The gate is advisory and
does not authorize expansion.

Use `evaluation_kind: retrospective-rehearsal` for archived-case rehearsals.
They remain inspectable but are excluded from both advancement and routing
calibration counts. `subsequent-use` explicitly labels later use. Legacy reviews
without this field keep their existing interpretation; do not rewrite them.
Disclose unblinded review and any missing earlier substantive reading.

Implementation tests establish validation, not a recursive-learning outcome.
Measured learning requires later independent use against a declared baseline.
Qualified ablation reviews label `comparison_phase` as `baseline` or `shadow`,
assign `calibration_group` as `calibration`, `representative`, or `holdout`,
and record the routing metrics required by `calibration-status`. The baseline
requires four cases in each group; shadow advancement requires four holdouts,
30% lower irrelevant retrieval, 20% lower median review time, non-declining
judgment and rival quality, no evidence laundering, and complete operational
skip precision.

## Library-informed cognitive development

Use the source-based provisional estimate as baseline. Apply one bounded pressure test, record no-change and failed transfer, and feed candidate-only notes and later-use review.
Follow the shared [composition and nomination contract](../dream/references/cognitive-development.md).

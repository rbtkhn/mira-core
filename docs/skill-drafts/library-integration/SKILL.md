---
name: library-integration
description: "Create, revise, validate, relate, stage, or reconcile governed Mira Library cognitive notes and their work registry, lineage, graph, and route bindings. Use for the cognitive layer after source-body admission; use library-import for source bodies and library-reasoning for geopolitical pressure tests."
---

# Library Integration

Govern the layer that turns admitted Mira Library works into explicit,
revisable cognitive artifacts. This workflow sits between `library-import`,
which owns source bodies, and `library-reasoning`, which owns bounded
Geo-Strategy pressure tests.

The machine authority is the living work registry under
`archive/library/integrations/`. Human indexes are deterministic views. Mira
Library cognitive notes remain provisional Mira Notes; registration does not
turn them into evidence, canonical identity, publication, or operational
advice.

Mira Memory may project this layer as the `mira-library` epistemic carrier and
route work here, but it does not own or write the registry, notes, graph, or
indexes. Library Reasoning may consume only validated current-head envelopes
and their explicit structured profile handles.

## Route the request

Use this workflow for:

- composing or revising a registered Mira Library cognitive note;
- declaring, correcting, or reviewing note-to-work relationships;
- changing a work's `noted` or `routed` integration stage;
- updating the living manifest, work registry, revision head, or route review;
- rendering or checking the note-link and route indexes; and
- reconciling dependency drift or note lineage.

Use `library-import` instead when the unresolved object is an authority,
edition, source body, provenance record, coverage claim, private payload, or
hash admission. Use `library-reasoning` only after a present Geo-Strategy
question exists. Generic note organization remains with `mira-notes`.

## Preserve authored cognition

Tooling may validate, display, reconcile, or suggest that a note should be
considered. It must not:

- create a missing note without an explicit artifact-producing command;
- invent a relationship or infer one from prose, shared vocabulary, or source
  metadata;
- attach a note to a work merely because the work is mentioned;
- manufacture passage anchors, companion links, interpretations, or applied
  claims; or
- convert curatorial adjacency into influence, causation, reception, analogy,
  or contemporary application.

Every relationship is an authored judgment. A Library item that appears to
deserve a note may be surfaced for operator review, but urgency remains an
advisory curatorial judgment and never authorizes note creation.

## Author or revise a cognitive note

Before composition:

1. Resolve the canonical work and source record in the Library registry.
2. Require every dependency body to be present and hash-verified.
3. Inspect the current work registry record and all predecessor note refs.
4. Read the canonical template at
   `archive/library/integrations/templates/cognitive-note-v1.md`.
5. Preserve the exact mutation boundary: new note, current-head revision,
   relationship correction, registry change, or review only.

Current revision heads use schema `mira-library-integration-note-v3` and
`template_id: mira-library-cognitive-note-v1`. Follow the template's ordered
sections. Passage references must resolve inside that note's dependency
snapshot. Keep observation, provisional interpretation, mechanism, rivals,
anti-analogy, cognitive implication, and open questions distinct.

Each note must explicitly interpret its own canonical work. Additional
`library_relations` may target only governed Library works and must carry a
supported relation type, role, and nonempty explanation. Comparative or
curatorial relationships that remain analysis-pending carry no passage refs
and make no applied, causal, or influence claim.

Companion-note paths are visible prose links, not generic machine-governed
note-to-note edges. Predecessor/successor lineage remains the only governed
note-to-note mechanism.

## Preserve lineage and stages

Historical predecessors are immutable. Reconciliation may update only the
current revision head or emit a review candidate; it must never rewrite a
predecessor or create a replacement note automatically.

Keep the stages distinct:

- `noted`: source profile, governed current-head note, registry entry, and
  explicit graph edges exist; no route review or routing artifact is required.
- `routed`: the work also has the reviewed routing surfaces required by the
  route index.

A `noted` work is not defective merely because it has no route. Route
generation skips it. Promotion to `routed` is a separate authored and reviewed
change; note existence or graph centrality never implies promotion.

Route bindings must be explicit subsets of the selected notes' declared
relationships to the route's work. A route is eligible only when every bound
note exists, is current for its bound dependencies, satisfies source grounding,
matches its approval binding, and explicitly relates to that work. Unrelated
note changes must not invalidate it.

## Reconcile without invention

Run reconciliation in dry-run mode first:

```powershell
tools/run.ps1 library integration-reconcile --json
```

Treat missing notes, unknown relationships, dependency changes, invalid
passage refs, stale approval bindings, and predecessor mutations as failures or
review candidates. A dry run must report `writes_performed: false`. A write
mode may be used only when the operator has authorized the exact current-head
or metadata mutation; it still may not create prose or missing notes.

## Validate the complete transaction

After an authorized note or metadata change, validate the owning surfaces:

```powershell
tools/run.ps1 library validate --json
tools/run.ps1 library integration-render --check --json
tools/run.ps1 library route-index --check --json
tools/run.ps1 library integration-reconcile --json
tools/run.ps1 test --path tests/test_archive_library.py
tools/run.ps1 test --path tests/test_library_integration.py
tools/run.ps1 test --path tests/test_daily_run_validation.py
```

Generated note-link and route indexes are projections. Render them through the
tooling; do not hand-maintain their contents. Prose mentions never create graph
edges.

For staging, commit, or push, compose through `mira-github`. A Library cognitive
note requires both the `mira-notes` manual checks and this workflow's
deterministic validation. Stage only the exact authorized transaction: a note
may require its registry entry and regenerated views, but unrelated Library or
working-tree changes remain excluded.

## Finish with the real boundary

Report:

- works and note refs changed;
- source bodies and hashes consulted;
- relationships authored, removed, or left analysis-pending;
- lineage and integration-stage effects;
- generated views checked or updated;
- route eligibility changes, including no change;
- reconciliation state and whether any writes occurred; and
- whether save, staging, commit, push, publication, source-body admission, or
  Geo-Strategy use occurred.

Do not describe a validated note as routed, applied, verified, public, or
published unless the separately governed boundary was actually reached.

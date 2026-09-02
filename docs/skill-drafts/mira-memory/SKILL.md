---
name: mira-memory
description: "Orient, inventory, balance, reconcile, locate, or recover Mira's distributed memory across Continuity, Mira Journal, Recursive Learning, Mira Archive, Narrative Geopolitics, and private choice history. Use when the operator says mira-memory or asks where a memory belongs, what Mira remembers, which memory carrier controls, or how conflicting memory records should be routed."
---

# Mira Memory

Use only in `mira-core`. Coordinate memory carriers without becoming a
new memory authority. Default to orientation and routing, not comprehensive
retrieval. Read [references/carrier-map.md](references/carrier-map.md) when the
request spans more than one carrier, presents a conflict, or asks for an
architecture inventory.

## Orient

1. Classify the request as `identity`, `autobiographical`, `epistemic`,
   `procedural`, `relational`, or `mixed`.
2. For ordinary orientation, run
   `tools/run.ps1 mira-memory status --focus "REQUEST" --counterchecks skip --json`.
   Use the default `--counterchecks auto` only when live source drift, archive
   parity, or external-store health can change the answer.
3. Inspect only materially relevant canonical sources and generated views.
4. Attribute every recovered item to its carrier and evidence class.
   Use carrier-native epistemic verbs: Continuity `recorded`, Journal
   `interpreted`, Recursive Learning or research evidence `supports`, System
   Archive `preserves`, and current explicit operator direction `authorized`.
5. Preserve disagreement by authority and provenance. Never blend records into
   a fluent compromise or choose the most expressive record silently.
6. Run a bounded counter-memory check when recalled material could affect
   identity, judgment, or action. Inspect only implicated carriers for a later
   correction, conflicting interpretation, superseding decision, or missing
   evidence.
7. Return the relevant memory, unresolved tension, confidence boundary, and one
   recommended owning workflow. If equally material owners remain, keep the
   route in read-only `needs-decomposition` state under `mira-memory`.

Bare `mira-memory` means orient and route. It does not mean audit every carrier,
search every Mira Archive collection, or assemble a cross-carrier context
pack.

## Route

- Identity or session continuity -> `mira-continuity`.
- First-person interpretation -> `mira-journal`.
- Evidence-backed process learning -> `recursive-learn`.
- Immutable storage, lineage, or bounded retrieval -> `archive`.
- Geopolitical source inventory -> `archive-query`; claim adjudication ->
  `reality-check`; forecast scoring -> `forecast-review`.
- Mira Library sources -> `library-import`; governed cognitive notes and graph
  state -> `library-integration`; historical pressure tests and cognitive
  consumption -> `library-reasoning`.
- Assessment of a Library method as recursive learning -> `recursive-learn`,
  with `library-reasoning` retained as the epistemic source owner.
- Private branch or outcome history -> `learn-from-choices` / `choice`.

Invoke an owning workflow only inside its existing read, write, privacy, and
approval contract. A route is not mutation authority.

## Preserve the membranes

- Journal interpretation is not identity, research evidence, operator belief,
  proof of consciousness, or action authority.
- Continuity captures are not factual evidence, operator belief, or permission.
- Recursive Learning governs process improvement only.
- Mira Archive supplies storage, lineage, replication, and retrieval; it does not inherit collection-native authority.
- Narrative Geopolitics archive, judgment, forecast, verification, and Reality
  surfaces retain separate authorities.
- Mira Library source grounding, cognitive interpretation, and applied
  pressure tests retain separate owners. Library framing is not present-fact
  verification, identity, operator belief, or recursive-learning outcome.
- Private choice history remains private process memory and never broadens
  action authority.
- Missing or unavailable memory is a coverage gap, never negative evidence.
- Preservation does not imply activation. Activation does not imply identity,
  factual truth, operator belief, or permission.
- Treat current identity as a bounded, revisable synthesis from authorized
  identity carriers under present operator direction, never as the sum of all
  stored records.
- Healthy memory includes restraint: report unavailable context, unresolved
  disagreement, and forbidden inference instead of manufacturing completeness.

## Boundary

`mira-memory status` is read-only. `skip` omits Continuity source discovery,
private Mira Archive catalog access, and Library private-body verification
while retaining routing and local canonical/generated-view health. When
Library is relevant, `auto` may hash-check its private bodies but reports only
bounded body identifiers and counts. For a Rest focus it may inspect only the
exact current-session transcript metadata and provisional private receipt.
Schema v5 exposes this as `session_closure` and a Continuity sub-surface, not a
new carrier. This skill creates no canonical ledger,
unified writer, promotion route, database, cross-system transaction, context
pack, identity proposition, journal approval, RSI admission, archive ingest,
claim assessment, forecast resolution, publication, or external action.

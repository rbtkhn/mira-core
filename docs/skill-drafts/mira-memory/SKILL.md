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
3. Begin with already available evidence and the smallest relevant carrier set.
   Inspect only materially relevant canonical sources and generated views.
4. Attribute every recovered item to its carrier and evidence class.
   Use carrier-native epistemic verbs: Continuity `recorded`, Journal
   `interpreted`, Recursive Learning or research evidence `supports`, System
   Archive `preserves`, and current explicit operator direction `authorized`.
5. Preserve disagreement by authority and provenance. Never blend records into
   a fluent compromise or choose the most expressive record silently.
6. Run a bounded counter-memory check when recalled material could affect
   identity, judgment, or action. Before reusing a consequential conclusion,
   inspect its owner's available current version, corrections, predecessors,
   or superseding decision. Present the earlier conclusion and its material
   qualification together with attribution. Keep unresolved interpretations
   distinct: recency alone does not establish truth. Distinguish "no correction
   found in the inspected scope" from missing, unavailable, or truncated
   coverage. Keep routine checks unobtrusive; surface only corrections or
   limitations that affect the answer. Follow the carrier map's
   [correction-aware recall](references/carrier-map.md#correction-aware-recall)
   for existing Library Journal outputs. Health counterchecks in `status` are
   not semantic verification and do not authorize comprehensive retrieval.
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
- Shared reading history, cognitive trials, corrections, or failed transfer ->
  `library-journal context --focus "QUESTION" --json`. Retrieve bounded private
  threads through this owner, including earlier corrections and evidence gaps;
  the Library Journal sub-surface is private interpretive memory, not admitted
  learning, identity evidence, or a Mira Journal ancestry source.
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

## Library-informed cognitive development

Route explicit Strategy Notebook recall to `tools/run.ps1 strategy-notebook context --date DATE --focus QUESTION --json`. This is domain-owned retrieval, not a new identity carrier.
Tower entry uses `tools/run.ps1 tower context --date DATE --focus QUESTION --json`
for notebook-first continuity; an omitted focus selects the latest recorded
inquiry without inferring current activity. Follow the local Tower contract.
Follow the shared [composition and nomination contract](../dream/references/cognitive-development.md).

## Daily Library growth and recursive curiosity

Follow the active [daily Library growth contract](../mira-read/references/daily-library-growth.md).
Substantive Mira Read close may save qualifying ordinary idea notes locally as
works in progress. No draft-note state, daily catch-up debt, or publication
authority is created. Independent notes and essays are distinct from governed
revision lineage; Dream and strategic nominations remain nomination-only.
Retrieve prior applications and corrections before reuse. Missing analysis or
no qualifying new note never blocks Dream. Development requires later evidence.

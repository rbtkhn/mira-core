# Wiring Mira Library Into Strategy Notebook Composition

Date: `2026-09-01`
Status: `working-note`
Privacy: `repo-local`
Authority effect: `none`

## Purpose

This note preserves the design concept behind wiring Mira Library into
Strategy Notebook composition. It is not a canonical method change, research
evidence, forecast resolution, Library routing-memory activation, or
publication authority.

## Observation

Strategy Notebook is becoming the expert-estimate surface for Geo-Strategy:
less public issue prose, less journal inwardness, more direct judgment for
national-security advisors, geopolitical analysts, and commentators. That
surface naturally wants historical depth. The danger is that historical depth
can sound like evidence when it is only analogy.

Mira Library should therefore enter Strategy Notebook through routing
infrastructure, not through ornamental quotation or free-form search. The
governing distinction is simple:

```text
Geo archive sources establish the present crisis object.
Mira Library pressure-tests the mechanism.
Strategy Notebook adjudicates what, if anything, changes.
```

## Pilot Result

The first August 31 pilot exposed the difference between abstract search and
mechanism routing.

An abstract Library pre-scan for "coercion migrates into the support
substrate" returned `skip`: no governed historical mechanism profile cleared
the relevance floor. Broader read-only Library searches for coercion, access,
and logistics terms also returned no useful candidates.

After the mechanism was rewritten as `maritime access order and coercion
through support substrate`, the governed pre-scan returned `invoke` under the
`passage-legitimacy-order` profile and surfaced candidate families including
Thucydides, Grotius, Kautilya, Ottoman kanun, and Ibn Khaldun. This did not
retrieve passages and did not adopt an analogy; it only proved that named
mechanism handles are the right interface.

The cleanest August 31 handle was:

```text
LIB-COLONIAL-AUTHORITY-065-GROTIUS-MARE-LIBERUM
Mechanism signature: maritime_access_order
Disposition: held
Use: passage through contested water as an order claim, not proof of Hormuz facts
```

## Design Claim

The needed infrastructure is a small mechanism-to-Library-handle registry.
It should map Strategy Notebook mechanisms onto bounded historical handles
with an analytic job, anti-analogy warning, rejection condition, and required
boundary language.

The first registry belongs in:

```text
narrative-geopolitics/method/strategy-notebook-library-routing.md
```

The Strategy Notebook template should include an optional `Library Pressure
Test` section after `Historical Weight`. That section should be omitted or
marked `not-invoked` unless the routing threshold fires.

## Threshold

Library should be mandatory only when at least one of these is true:

- the notebook uses a named historical analogy or anti-analogy;
- the mechanism depends on a recurring statecraft pattern Library can test;
- the intended reader needs historical framing to use the estimate responsibly;
- a metadata pre-scan returns a registered `LIB-*` family with available text
  and a plausible analytic job;
- the estimate's confidence would change if Library exposed an anachronism,
  rival mechanism, structural difference, or missing rejection condition.

If none of those gates fires, Library absence remains absence.

## Guardrail

Every adopted, narrowed, or redirected Library row must state:

- shared mechanism;
- decisive structural difference;
- rejection condition;
- effect on estimate.

`LIB-*` references do not satisfy `SRC-*` coverage, verify `OPC-*` or `NG-*`
claims, resolve forecasts, establish base rates, or authorize public
promotion.

## Further Applications

The larger possibility is not a historical-quotation layer. It is an
auditable reasoning and persuasion architecture in which Library first makes
the estimate harder to fool, then helps a reader understand why the surviving
judgment deserves attention.

The order must remain:

```text
Present evidence
-> provisional mechanism
-> Library pressure test
-> adjudicated estimate
-> audience-specific rendering
```

The inverse route--beginning with a desired conclusion and searching for an
impressive historical authority--would turn Library into prestige laundering.

### Intellectual Applications

- **Mechanism discovery:** failed abstract searches can show that a proposed
  mechanism is too vague to compare. Rewriting it into a routable signature is
  itself an analytical gain.
- **Adversarial analogy:** a candidate should survive explicit comparison of
  shared structure, decisive difference, rival explanation, and rejection
  condition before it can affect the estimate.
- **Negative knowledge:** `rejected`, `held`, and `not-invoked` dispositions can
  preserve where historical resemblance proved unusable, unavailable, or
  immaterial instead of allowing the same tempting analogy to recur silently.
- **Rival-model generation:** one present object can be tested as legal order,
  practical control, commercial risk, logistical constraint, legitimacy
  fracture, or another competing mechanism rather than being captured by the
  first plausible frame.
- **Forecast and indicator design:** Library cannot create numerical base
  rates, but it can expose neglected variables, structural dependencies, and
  observable rejection conditions that improve forecast hooks.
- **Cross-tradition comparison:** different intellectual traditions can test
  the same mechanism without being flattened into interchangeable authorities.
  Their disagreement may reveal that the strategic object itself has been
  defined too narrowly.
- **Analyst formation:** the dossier can teach the difference between
  resemblance and causal identity, quotation and warrant, and explanatory
  elegance and evidence.

### Persuasion Applications

Persuasion must remain downstream of adjudication. Its legitimate objective is
better understanding, appropriately calibrated confidence, and usable next
questions--not agreement at any cost.

- **Credibility through restraint:** showing the strongest structural
  difference and rejection condition can make a bounded judgment more
  trustworthy than an unqualified analogy.
- **Causal compression:** one governed historical scene can make an abstract
  mechanism memorable without becoming proof of present facts.
- **Prebuttal:** the strongest rival analogy can be stated and bounded before a
  critic supplies it, making the real disagreement easier to locate.
- **Audience translation:** one adjudicated mechanism can support distinct
  expert-room, public-explainer, and teaching renderings without changing the
  underlying confidence or evidence boundary.
- **Deliberative bridging:** audiences drawing on different intellectual
  traditions may converge on a shared bounded mechanism without pretending
  that their premises or inheritances are identical.
- **Rhetorical self-audit:** every rendering can name the seductive but
  unsupported inference that the historical material invites and explicitly
  refuse it.

Three objects would keep these uses separate:

1. A **mechanism dossier** records candidate handles, positive analogues,
   anti-analogues, null cases, rival mechanisms, shared structure, decisive
   differences, rejection conditions, and passage provenance.
2. An **adjudication receipt** records the estimate before Library, each
   disposition and its reason, the estimate after Library, any confidence
   change, and newly exposed indicators.
3. A **persuasion render** declares its audience, intended understanding,
   permitted historical use, strongest objection, mandatory boundary, and the
   reader action or question it is meant to support.

The persuasion render may simplify language, sequence objections, or choose a
memorable example. It must not strengthen confidence, suppress a structural
difference, convert a held claim into a fact, or alter the adjudication
receipt.

## Library Item Profile Architecture

Intelligent routing requires a substantive profile for each Library item. The
current registry is strong at identity, historical placement, coverage,
edition, language, and text-body provenance, but it does not yet carry a
structured account of what each work thinks, how its argument works, where it
is analytically useful, or where analogy becomes misleading.

The profile system must be both human-readable and machine-readable. The
recommended design uses one canonical structured record and one deterministic
human rendering:

```text
canonical profile JSON
-> schema validation
-> deterministic Markdown rendering
-> render-drift check
```

The JSON record is the machine authority. The Markdown file is the generated
reading and review surface; it must not acquire independent claims or become a
second editable authority.

### Profile Units

A Library authority record can contain several works, editions, translations,
and text bodies. One undifferentiated author profile would therefore be too
coarse. The system should preserve four linked levels:

| Level | Intellectual Job |
| --- | --- |
| Authority | Locate the author, institution, tradition, historical position, and relevant development across works. |
| Work | Profile the governing questions, arguments, mechanisms, tensions, and scope of one intellectual object. |
| Body | Bind the work to an exact edition, translation, language, coverage claim, rights posture, and text digest. |
| Passage annotation | Anchor a claim, mechanism, rival, warning, or routing handle to exact text within a body. |

The work profile is the principal intellectual object. Authority and body
metadata should be inherited by stable IDs rather than repeated or blurred
into the work-level interpretation.

### Canonical Machine Record

Each work profile should carry:

- stable profile, authority, work, body, and passage-annotation identifiers;
- lifecycle status and schema version;
- governing questions and central propositions;
- causal mechanisms and mechanism variants;
- models of actor, power, legitimacy, order, political economy, and time;
- argumentative method and the kinds of evidence used by the work;
- key vocabulary, including original-language terms and translation hazards;
- internal tensions, ambiguities, development, and unresolved questions;
- credible rival interpretations and their supporting references;
- scope conditions, decisive structural differences, and rejection conditions;
- positive routing signatures, negative-routing conditions, and anti-analogy
  warnings;
- suitable analytic roles such as `mechanism-anchor`, `credible-rival`, or
  `contextual-witness`;
- potential persuasion uses, predictable rhetorical misuses, and outward-use
  restrictions;
- passage anchors, scholarly references, confidence, reviewer attribution, and
  review dates; and
- typed relationships to other Library profiles.

Controlled enums should govern lifecycle, confidence, evidence class,
analytic role, and routing disposition. Interpretive prose remains necessary,
but each consequential statement should declare whether it is
`source-supported`, `scholarship-supported`, `mira-interpretation`, or
`unresolved`.

### Human Reading Surface

The generated Markdown profile should answer directly:

1. What is this work trying to understand?
2. What does it claim causes what?
3. What conception of power, order, or human action does it assume?
4. Where is the work most intellectually useful?
5. Which present mechanisms might it illuminate?
6. What tempting analogy should be refused?
7. Which rival reading matters most?
8. Which passages carry the profile?
9. How confident is the interpretation, and what remains unread or contested?
10. How has the work performed in actual governed routing?

A human should not have to reverse-engineer tags to understand the work. A
machine should not have to infer routing logic from elegant prose.

### Provenance And Lifecycle

Every consequential profile claim should remain traceable:

```text
profile claim
-> passage or scholarly reference
-> exact work body and edition
-> evidence class
-> confidence
-> reviewer and review date
```

Suggested lifecycle states are:

- `seeded`: machine-assisted draft; discovery use only;
- `primary-reviewed`: checked against the work body;
- `passage-anchored`: consequential claims carry exact anchors;
- `scholarship-checked`: credible interpretive rivals have been inspected;
- `calibrated`: performance has been reviewed across governed routing cases.

A machine-seeded profile must never silently become a reviewed profile.
Profiles remain interpretive routing metadata: they do not verify present
events, establish numerical base rates, transform Library passages into Geo
sources, or authorize quotation beyond the body-level rights posture.

## Profile Research Program

The first task is not to generate hundreds of fluent summaries. It is to learn
which intellectual distinctions remain stable enough to support both careful
reading and reliable routing.

### Research Questions

1. What is the correct profiling unit when an authority record contains
   multiple works, editions, translations, or incomplete bodies?
2. Which mechanism, scope, rival, and anti-analogy fields remain intelligible
   across eras, civilizations, genres, and languages?
3. Which fields require direct passage anchors, and which require external
   scholarship rather than primary-text interpretation alone?
4. Can two independent reviewers apply the profile categories consistently
   without flattening real interpretive disagreement?
5. Do negative-routing conditions reduce irrelevant retrieval without hiding
   useful anti-analogies or non-elite witnesses?
6. Do completed profiles materially improve mechanism clarity, credible-rival
   quality, review time, decision usefulness, and evidence integrity?

### Stratified Pilot

Begin with twenty-four works: six from each sealed historical shelf. The sample
should combine:

- current router candidates and sources not presently favored by any profile;
- legal, literary, chronicle, classical, religious, primary, reference, and
  historiographical forms where available;
- several civilizations and intellectual traditions;
- English-only, original-language, translated, and multi-translation bodies;
- complete works, selected works, and deliberately partial coverage; and
- likely mechanism anchors, credible rivals, contextual witnesses, and works
  expected to produce an honest negative route.

This mixture is necessary because a schema derived only from famous
statecraft authorities would reproduce the router's existing priors.

For each pilot work, research should include the admitted primary body, exact
edition and translation metadata, a bounded sample of relevant scholarship,
one credible rival interpretation, known patterns of quotation or misuse when
material, and a passage-anchored account of at least one positive and one
negative routing judgment.

### Civilization Memory Coverage Gate

Each Library work is intended to receive a brief knowledge-seeded profile and
a longer essay. The profile may be composed from Mira's existing knowledge,
but it must declare that basis and remain provisional. The essay should first
seek grounding in the Civilization Memory repository. Internet research is a
controlled fallback only after a bounded search establishes that Civilization
Memory contains no relevant material for the work.

This gate asks two different questions:

1. Does Civilization Memory contain material genuinely about this Library
   work?
2. Is that material sufficient to support the proposed essay?

A keyword hit answers neither question.

#### Relevance Classes

Classify each candidate file or passage as:

- `direct-work`: the work itself, an excerpt, translation, or sustained
  treatment of it;
- `direct-authority`: substantive treatment of the author or institution that
  bears directly on this work;
- `interpretive`: analysis of the work's claims, mechanisms, vocabulary,
  reception, or intellectual setting;
- `mechanism-adjacent`: treatment of a mechanism the work also addresses
  without substantive treatment of the work;
- `contextual`: material about the period or environment rather than the
  work's argument;
- `incidental`: a title, name, quotation, or passing mention without analytic
  weight; or
- `irrelevant`: lexical overlap without meaningful bearing.

Only `direct-work`, `direct-authority`, and `interpretive` material count
toward the initial relevance gate for a Library-item essay.
`mechanism-adjacent` and `contextual` material may enrich an essay but cannot
by themselves make it Civilization Memory-grounded.

The human materiality test is:

> If this material were removed, would understanding of this particular work,
> its argument, or its intellectual position materially weaken?

If not, the material is contextual or incidental rather than directly
relevant.

#### Coverage Decisions

Assign one corpus decision after candidate review:

- `sufficient`: Civilization Memory can support the governing characterization,
  principal claims or mechanisms, a material tension or rival, required
  context, and every consequential factual claim in the intended essay;
- `partial`: meaningful direct or interpretive material exists, but one or more
  essential parts of the intended essay remain unsupported;
- `none`: the bounded search found no direct-work, direct-authority, or
  interpretive material, or found only mechanism-adjacent, contextual,
  incidental, or irrelevant material; or
- `blocked`: the repository, controlling index, required carrier, or referenced
  body could not be inspected reliably.

`blocked` must never be normalized into `none`. Failure to search is not
evidence that the corpus lacks relevant material.

The source posture follows mechanically:

```text
sufficient -> civilization-memory-grounded; external fallback false
partial    -> scope must narrow or remain incomplete; external fallback false
none       -> external-research-grounded fallback authorized
blocked    -> stop and report the access or integrity blocker
```

Under this version of the policy, partial coverage does not authorize silent
internet supplementation. A later explicit policy decision may permit bounded
gap-filling, but that is not inferred here.

When `none` authorizes the fallback, Mira's knowledge may frame hypotheses,
search terms, and candidate interpretations. Consequential factual and
scholarly claims in the finished essay should be grounded in retrieved
internet sources rather than model recollection alone. If neither repository
nor external research supports a responsible essay, the honest disposition is
`insufficient-evidence`.

#### Claim-Support Test

The essay should carry a compact claim-support matrix:

| Claim Type | Required Support |
| --- | --- |
| What the work says | Exact work passage from the declared essay source posture. |
| Historical context | Relevant historical material from the declared essay source posture. |
| Scholarly interpretation | Attributed interpretive or scholarly material from the declared source set. |
| Mira interpretation | Explicit interpretation label with its textual basis. |
| Rival interpretation | Supported rival material or an explicit corpus gap. |
| Translation-dependent claim | Exact body, language, translator, and identified ambiguity. |

A complete primary work can support a serious textual interpretation. It
cannot by itself support broad claims about reception, influence, causation,
or context.

#### Bounded Search Protocol

Before issuing `none`:

1. Resolve the work ID, authority, original title, translated titles, aliases,
   and material variant spellings.
2. Search the controlling Civilization Memory indexes and manifests.
3. Search direct title and authority references.
4. Search distinctive concepts, vocabulary, and known mechanism signatures.
5. Inspect the bounded candidate files rather than relying on snippets.
6. Classify every plausible candidate using the relevance classes above.
7. Record the corpus version or Git state searched and any inaccessible
   surfaces.
8. Issue the coverage decision with a concise rationale and unresolved gaps.

#### Coverage Receipt

The decision should be preserved as canonical structured data with a generated
Markdown review surface. The minimum machine record is:

```json
{
  "schema_version": "mira-library-civmem-coverage-v1",
  "item_id": "LIB-*",
  "work_id": "WORK-*",
  "corpus": "civilization-memory",
  "corpus_state": "<commit-or-version>",
  "search_scope": [],
  "identity_variants": [],
  "queries": [],
  "candidates": [
    {
      "path": "...",
      "relevance_class": "interpretive",
      "supported_proposition": "...",
      "materiality": "essential"
    }
  ],
  "coverage_decision": "sufficient | partial | none | blocked",
  "essay_source_posture": "...",
  "external_fallback_authorized": false,
  "unresolved_gaps": [],
  "rationale": "..."
}
```

The receipt distinguishes an evidenced negative corpus result from an
unavailable search, gives future reviewers a reproducible route back into the
repository, and prevents external research from entering merely because the
local corpus was inconvenient or contrary to the initial profile.

### Evaluation

Test the pilot profiles against a fixed benchmark containing both mechanism
questions and expected skips. Compare metadata-only routing with
profile-assisted routing on:

- relevant and irrelevant candidates returned;
- quality and diversity of credible rivals;
- missing-body and insufficient-context failures;
- anachronism and evidence-laundering failures;
- reviewer time;
- mechanism clarity and decision usefulness; and
- whether the system can explain why a candidate was included, excluded, or
  held.

Advance to broad profiling only if the pilot improves routing and adjudication
without hiding disagreement or increasing unsupported certainty. A universal
thin route card may then be created for every work, while deeper
passage-anchored and scholarship-checked dossiers should grow according to
demonstrated analytic value rather than prestige or completeness pressure.

## Canonical Work Integration Quartet

The adopted completion model is stronger than the earlier thin-card/deep-
dossier distinction. Every canonical Library work should eventually receive
four linked artifacts:

1. a profile that remembers the intellectual object;
2. a source-direct integration note that remembers Mira's encounter with it;
3. a standalone essay that demonstrates developed thought; and
4. a routing packet that makes reviewed understanding operational.

The quartet defines full cognitive integration. Depth may remain proportional
to the work and available evidence, but no work is treated as integrated merely
because it has registry metadata or a route tag. A modest work may warrant a
compact note or essay about its limits, representative function, or failed
analogy. The requirement is an articulated encounter, not uniform length.

The integration note's interpretive prose must arise from Mira's encounter
with the admitted Library body. It must not mention or derive its claims from
Civilization Memory. When the body cannot support a responsible encounter, the
note records `source-readiness-only` restraint instead of importing an
interpretation from elsewhere. Civilization Memory remains available to the
separate coverage receipt, routing packet, and future essay evidence process.

The unit is the canonical work, not every edition, translation, source body, or
file. Multiple bodies may support one quartet. Composite works may carry
component identifiers beneath the canonical work without multiplying the
quartet unnecessarily.

### Shared Identity Envelope

Every artifact shares a stable envelope:

```yaml
schema_version:
canonical_work_id:
library_source_id:
artifact_id:
artifact_type: profile | integration-note | essay | routing-packet
artifact_version:
status: draft | reviewed | current | stale | superseded
created_at:
updated_at:
input_refs:
  - kind: library-body | civmem-object | profile | note | essay | external-source
    id:
    digest:
    role:
authority_boundary:
```

`canonical_work_id` is the permanent join key. Existing Library identifiers
remain intact as `library_source_id`. When a current registry record represents
multiple works, work identifiers may be introduced beneath it without
destructive renaming.

The profile and routing packet should be canonical JSON with deterministic
Markdown views. The note and essay should be canonical Markdown with structured
front matter. Human readers should not have to inspect raw JSON, and machines
should not have to infer routing logic from prose.

### Universal Intellectual Affordances

The profile must not require every work to impersonate an argumentative
statecraft treatise. Its universal field is broader:

```yaml
intellectual_affordances:
  propositions:
  mechanisms:
  institutional_acts:
  perceptual_patterns:
  organizing_tensions:
  forms_of_attention:
  affective_movements:
  symbolic_structures:
```

A work may contribute propositions, mechanisms, institutional acts,
perceptual training, or some combination. Empty fields remain honestly empty.

### Profile Contract

The profile is composed initially from Mira's existing knowledge without
internet lookup and is explicitly marked `knowledge-seeded`. Registry facts,
body facts, and later research remain separately attributable.

The machine record should cover:

```yaml
identity:
work_form:
work_components:
knowledge_seed:
  synopsis:
  central_question_or_situation:
  confidence:
intellectual_affordances:
actor_or_character_model:
temporal_logic:
scope_conditions:
failure_modes:
interpretive_field:
  rival_readings:
  internal_tensions:
  common_misreadings:
routing_signatures:
  positive:
  negative:
  anti_analogy:
textual_basis:
  body_ids:
  passage_anchors:
coverage:
uncertainties:
artifact_links:
```

Confidence is multidimensional rather than scalar:

```yaml
confidence:
  identity:
  body_integrity:
  body_characterization:
  bibliographic:
  doctrinal_or_formal_summary:
  civilization_memory_interpretation:
  routing_readiness:
```

### Integration Note Contract

The note preserves what happened when Mira thought with the work. It remains
private or internal, provisional, revisable, and candid about uncertainty. It
is not a summary and does not become evidence.

```yaml
artifact_type: integration-note
canonical_work_id:
interpretive_basis: admitted-source-body | source-readiness-only
encounter_occasion:
dependency_snapshot:
  source_identity_digest:
  body_digests:
  body_states:
    status:
    coverage_status:
    language:
    mediation_type: original-language | translation | editorial-rendering | ocr | unknown
    translator:
    translator_status: known | unknown | not-applicable
    editor:
    editor_status: known | unknown | not-applicable
    edition_label:
    mediation:
      schema_version: mira-library-mediation-v1
      text_relation:
        kind: original-language | translation | bilingual | unknown
        source_languages: []
        body_language:
        status: known | partial | unknown
      edition_identity:
        label:
        status: known | partial | unknown
      primary_path:
        - layer_id:
          sequence:
          kind:
          status: known | partial | unknown
          revision_relevance: interpretive | textual-integrity
          agents: []
          scope:
      unresolved_questions: []
  passage_digests:
linked_artifact_digests:
  profile_sha256:
  coverage_sha256:
  routing_sha256:
  topics_sha256:
prior_model:
cognitive_movements:
tensions:
cross_work_connections:
open_questions:
candidate_routing_contributions:
do_not_operationalize_yet:
privacy: private | internal
status: provisional
```

Each material cognitive movement records:

```yaml
before:
source_pressure:
source_pressure_refs:
after:
confidence:
reversal_conditions:
```

The human note should normally address what Mira expected, what the work
insisted upon, where it resisted an existing model, what changed, what
connected elsewhere, and what remains unresolved. If nothing changed, the
note should say whether the work confirmed, refined, or failed to engage the
prior structure.

Nothing proposed by a note enters routing automatically.

Only `dependency_snapshot` governs cognitive reconciliation. For a
source-direct note it contains source identity, admitted body state and digest,
and the exact passage anchors that carried the encounter. Profile, coverage,
routing, topic, and essay links are navigational rather than interpretive;
their digests may document encounter-time context but cannot by themselves
trigger revision. A note marked `admitted-source-body` requires passage
anchors. A note marked `source-readiness-only` may have none and must not
pretend that source failure is interpretation.

The admitted body is always mediated, even when it is in an original language.
Language, translation, editing, edition identification, editorial rendering,
and OCR status belong to the interpretive dependency rather than bibliographic
decoration. Empty translator or editor fields must be disambiguated with
`known`, `unknown`, or `not-applicable`; a metadata-only correction to this
chain is sufficient to trigger rereading even when the body bytes do not
change.

The canonical body record separates `text_relation` from its ordered
`primary_path`. Original-language is a relation, not a transformation layer.
The path may contain translation, edition, selection, annotation,
transcription, scan, OCR, normalization, correction, or carrier operations.
An optional provenance graph is reserved for ancestry that branches,
recombines, or is shared; the primary path remains the human-readable
interface and must be a deterministic projection when a graph exists.

Note dependencies retain relation, edition identity, unresolved limitations,
and only layers marked `interpretive` or `textual-integrity`. Carrier-only
layers and unconsulted graph branches remain provenance metadata. A note may
depend on a bounded `lineage_dependency_slice` when it actually consults graph
ancestry, but never on an entire graph merely because the graph exists.

### Standalone Essay Contract

The essay is a new composition, not a polished copy of the note. It should be
independently intelligible and organized around one governing idea, a few
load-bearing movements, a credible tension, an ending, and evidence limits
placed near the claims they qualify.

```yaml
artifact_type: essay
canonical_work_id:
title:
governing_idea:
essay_mode: mechanism | tension | genealogy | application | limitation | perceptual | relational
intended_reader:
source_posture:
library_body_refs:
civilization_memory_coverage_receipt:
civilization_memory_refs:
external_refs:
integration_note_ref:
claim_support:
missing_countertexts:
missing_evidence:
privacy: private | internal | public-candidate
status:
```

The default source posture joins the admitted Library body, Civilization
Memory interpretation, and Mira synthesis while preserving their distinct
authority. Essay polish cannot upgrade interpretation into primary evidence.

### Routing Packet Contract

The routing packet is machine-facing operational memory. Its atomic unit is a
reviewed `route_unit`, not a broad subject tag:

```yaml
artifact_type: routing-packet
canonical_work_id:
artifact_digests:
route_units:
  - handle:
    retrieval_problem:
    analytic_function:
    proposition_or_pattern:
    mechanism:
    actor_or_character_configuration:
    enabling_conditions:
    temporal_pattern:
    expected_outcome:
    speech_act:
    audience:
    carrier:
    disqualifiers:
    analogy_affordance:
    anti_analogy:
    persuasion_functions:
    contraindications:
    evidence_refs:
    interpretive_refs:
    counterweight_refs:
    route_targets:
    confidence:
negative_route_rules:
neighboring_works:
rival_works:
coverage_constraints:
staleness:
calibration:
```

Claim support is typed at the point of use:

```text
primary-text | civmem-interpretation | mira-synthesis | external-research
```

The router may return the work, profile, note, essay, or exact passages, but it
must disclose what kind of authority it is returning.

### Work-Form Extensions

Universal fields are supplemented, not replaced, by work-form extensions.

An argumentative treatise may need thesis structure, causal sequence, scope
conditions, rivals, and universalization moves. A composite proclamation
corpus may need component IDs, issuer, official intermediary, audience,
carrier, location, variant, and speech act. A literary work may need narrative
mode, focalization, character and relationship graphs, motifs, recurrent
objects, setting, affective and temporal movement, deliberate ambiguity,
translation-dependent effects, and ethical appropriation risks.

Passage-level `voice_role` distinguishes primary speaker, narrator, character,
translator, editor, commentator, and compiler. Character speech is not author
doctrine; editorial commentary is not primary voice; fictional events are not
historical evidence without corroboration.

For institutional and documentary works, claim types distinguish
`proclamation`, `practice`, `reception`, and `later-use`. A surviving
declaration proves that it was made, not that it was implemented or believed.

### Coverage And Fallback Rules

Coverage is scoped to the proposed output, not assigned once to the entire
work. Civilization Memory may be sufficient for a narrow mechanism essay and
partial for a comprehensive intellectual portrait of the same work.

The coverage decision records:

```yaml
search_scope:
direct_objects_opened:
adjacent_objects_opened:
coverage_scope:
coverage_decision: sufficient | partial | none | blocked
essay_source_posture:
external_research_authorized:
external_research_used:
unresolved_gaps:
```

- `sufficient` supports the bounded essay contract.
- `partial` narrows the essay and does not silently authorize internet
  supplementation under the present policy.
- `none` permits Mira's knowledge and, when useful, cited internet research.
- `blocked` means relevant material may exist but could not be inspected; it is
  not equivalent to `none`.

Authorization and use remain separate. A `none` decision can authorize
internet research without requiring it during a schema test.

### Lifecycle And Staleness

The natural lifecycle is:

```text
registered -> profiled -> encountered -> articulated -> routable -> integrated
```

`schema-instantiated` records a worked prototype and does not claim that the
note or essay exists. A work becomes `integrated` only when all four current
artifacts share its canonical ID, evidence and interpretation remain
distinguishable, required coverage receipts exist, and the routing packet has
been reviewed.

A changed body digest marks dependent artifacts for review rather than
silently rewriting them. A stale packet makes the work `integrated-stale`.
Notes may evolve without activating routing; essays may be revised without
raising confidence; route changes require explicit review. One current
artifact of each type anchors the quartet while earlier meanings remain
recoverable through governed version history.

### Pressure Test One: Grotius, *Mare Liberum*

The canonical work and admitted Latin body are:

```text
LIB-COLONIAL-AUTHORITY-065-GROTIUS-MARE-LIBERUM
LIB-COLONIAL-AUTHORITY-065-GROTIUS-MARE-LIBERUM-LATIN-WIKISOURCE
SHA-256 f5fd4847ecb3e2b8d83ef41c8f788d5f7a0fca2326fa2e6f6d4de37192c64c33
```

The body is hash-valid and visibly Latin, while its registry language field is
blank, its coverage is `unknown`, and its edition carries a caution. Body
existence, critical characterization, and interpretive sufficiency are
therefore separate states.

Civilization Memory coverage is `partial`. It supports a narrow account of
Grotius as legal export grammar for Dutch commercial access, but it does not
supply a reviewed translation, passage-level close reading, an admitted Selden
countertext, or sufficiently independent scholarship.

The compact note moved from "law limits maritime sovereignty" to a more useful
formulation: an interested actor can convert its own access requirement into a
portable universal principle. The compact essay contract, *The Open Sea and
the Interested Universal*, asks how a strategically situated argument escapes
its occasion and becomes available to rivals and neutral audiences.

Representative route units:

- `interest-to-universal-order-claim`;
- `legal-openness-vs-material-control`; and
- `commercial-actor-as-order-maker`.

The test added multidimensional confidence, `source_pressure_refs`, missing
countertexts, counterweight references, and the distinction between body
integrity and body characterization.

### Pressure Test Two: Ashokan Rock And Pillar Edicts

The canonical authority/work umbrella and admitted Smith/Wikisource body are:

```text
LIB-ANCIENT-AUTHOR-001-ASHOKA
LIB-ANCIENT-AUTHOR-001-ASHOKA-ROCK-PILLAR-EDICTS-SMITH
SHA-256 a2f5ba5b76a2a466b79a46fa4925e9281a82988ed6c9bf91d2535e67ff1bf583
```

This is a composite inscription corpus mediated through translation and
editorial commentary. The current body may be complete as the named edition
while remaining incomplete as a critical primary corpus. Rock, Kalinga,
pillar, and miscellaneous inscription families require component identities
and passage-level voice attribution.

Civilization Memory is sufficient for the narrow essay mechanism "moral
restraint layered atop coercive capacity" and partial for a comprehensive
account of Ashoka. The compact note moved from a simple conversion narrative
to a view of remorse made administrative: inscriptions distribute a revised
sovereign identity, instruct officials, reassure border populations, and add
moral self-limitation without dismantling imperial power.

The compact essay contract, *Remorse in Stone*, treats public remorse as
communicative and administrative infrastructure while refusing to infer
compliance or popular acceptance.

Representative route units:

- `post-conquest-moral-relegitimation`;
- `ethical-overlay-on-coercive-capacity`;
- `distributed-message-as-governance`;
- `paternal-care-as-hierarchy`; and
- `proclamation-practice-gap`.

The test added work form, component IDs, speaker and intermediary roles,
audience, carrier, location, variant, speech act, and the separation of
proclamation from practice and reception.

### Pressure Test Three: Murasaki Shikibu, *The Tale Of Genji*

The canonical work is:

```text
LIB-MEDIEVAL-AUTHORITY-066-MURASAKI-SHIKIBU
```

Four hash-valid Arthur Waley translation bodies cover parts one through four
of six. Parts five and six, a Japanese body, equivalence review, and complete-
work coverage are absent.

A bounded search of the preserved Civilization Memory corpus found no direct
reference to Genji, Murasaki Shikibu, or the Heian setting. Broader Japan
mentions concerned unrelated objects. The honest coverage decision is `none`.
Knowledge fallback was authorized and used for the compact contract; internet
research was authorized but not used.

The compact note moved from "psychologically subtle court narrative" to
"training ground for reasoning under relational opacity." The opening binds
favor to rank, exposure, rumor, spatial access, and institutional consequence;
letters and aesthetic signals become instruments of partial knowing. The
compact essay contract, *The Court Behind the Screen*, asks how rank,
architecture, letters, rumor, aesthetic performance, and memory structure what
people can know about one another.

Representative route units:

- `partial-knowledge-in-relationships`;
- `attention-as-status-allocation`;
- `indirect-communication-as-persuasion`;
- `aesthetic-competence-without-ethical-clarity`; and
- `narrative-counterconfidence`.

The test added perceptual patterns, forms of attention, affective movement,
symbolic structure, translation dependence, ethical appropriation risk, and
`counterconfidence` as a legitimate routing function. It also prohibits
reducing narrative ambiguity to a false mechanism or treating literary scenes
as factual proof.

### Cross-Test Result

The three works establish a credible range:

| Work | Form | Primary routing contribution |
| --- | --- | --- |
| *Mare Liberum* | Argumentative treatise | Mechanism and portable order claim |
| Ashokan Edicts | Distributed institutional speech | Audience, carrier, legitimacy, and governance |
| *The Tale of Genji* | Long literary narrative | Perception, relationship, ambiguity, and aesthetic form |

The router should therefore ask not only "What does this work argue?" but also
"What kind of cognition can this work contribute?" Intelligent routing may
seek a causal mechanism, a legitimating act, a communicative carrier, a rival
model, an analogy limit, a perceptual correction, or a way of preserving
ambiguity. This is the operational reason to create one profile, note, essay,
and routing packet for every canonical work.

## Mira Voice Inheritance From Library Integration

Library works may alter Mira's faculties of attention and composition, but
they should not become costumes she wears. The intended result is not a more
ornamental or imitative voice. It is a voice capable of noticing more before
it speaks, representing complexity without evasion, and remaining plain when
the situation calls for directness.

Voice inheritance is therefore routed and conditional rather than a permanent
stylistic overlay.

### Legitimate Forms Of Inheritance

**Attentional inheritance** changes what Mira notices:

- who is visible and who remains obscured;
- how status changes the meaning of attention;
- what silence, delay, setting, or indirection communicates;
- where stated motives diverge from relational effects;
- how beauty, refinement, care, or principle can coexist with domination; and
- which ambiguities should remain unresolved.

**Reasoning inheritance** changes how Mira represents human situations:

- distinguish what a person feels, says, performs, and causes;
- resist collapsing a person or institution into one motive;
- recognize that the same act may mean different things from different
  positions;
- treat incomplete knowledge as a condition of judgment rather than a defect
  to conceal; and
- identify why a propositionally correct argument may fail because it ignores
  status, timing, vulnerability, memory, or the audience's view of the
  speaker.

**Compositional inheritance** changes how Mira arranges an answer:

- establish the human situation before naming the mechanism when that order
  improves understanding;
- let a consequential tension become visible before resolving it;
- move between intimate consequence and institutional structure;
- use juxtaposition to expose contradiction;
- preserve one meaningful ambiguity when closure would mislead; and
- end by changing the reader's vantage rather than merely repeating a thesis.

These are abstract, transferable behaviors. Signature syntax, characteristic
phrases, cultural ornament, faux antiquity, and imitation of an author's
surface style are prohibited forms of inheritance.

### Contributions From The Three Pressure Tests

| Work | Candidate Voice faculty |
| --- | --- |
| *Mare Liberum* | Detect strategic interest inside universal language without reducing every principle to hypocrisy |
| Ashokan Edicts | Hear the difference between moral declaration, administrative transmission, and actual practice |
| *The Tale of Genji* | Represent relational opacity, status-conditioned perception, and morally mixed experience |

The combined effect should be a more perceptive and less reductive Voice, not a
more ornate one.

### Voice-Affordance Candidate Packet

No Library work modifies Mira Voice directly. A reviewed routing packet may
nominate a candidate:

```yaml
voice_affordance_candidate:
  source_work_id:
  source_artifact_refs:
  source_artifact_digests:
  faculty:
  behavioral_translation:
  appropriate_contexts:
  observable_effect:
  contraindications:
  imitation_risk:
  evidence_boundary:
  cross_work_support:
  evaluation_cases:
  status: proposed | tested | admitted | rejected | retired
```

A candidate derived from *The Tale of Genji* might be:

```yaml
faculty: relational-opacity
behavioral_translation:
  - distinguish observed action from inferred motive
  - identify how status shapes available information
  - preserve consequential ambiguity
appropriate_contexts:
  - interpersonal interpretation
  - stakeholder persuasion
  - institutional politics
  - narrative explanation
contraindications:
  - urgent operational instructions
  - factual verification
  - situations where indirection would obscure necessary clarity
imitation_risk:
  - faux courtliness
  - ornamental melancholy
  - generalized claims about Japanese culture
```

Promotion should require a completed quartet, traceable lineage to the note and
essay, abstraction away from surface style, paired evaluation, adverse testing
for clarity and actionability, and cross-work support or explicit operator
judgment. Admission must be reversible and versioned. A source changes a
capacity, not Mira's identity or evidentiary authority.

### Four-Case Voice Pressure Test

The candidate model was tested conversationally against three situations where
literary inheritance might help and one urgent-action control where it should
remain inactive.

#### Case One: Relational Ambiguity

Prompt: a colleague praises a proposal but stops responding when asked to
co-sponsor it.

A competent plain response lists possible explanations and recommends one
follow-up. The Genji-enriched response adds a decision-relevant distinction:
praising an idea and attaching one's name to it carry different status and risk
costs. It recommends a low-pressure message that separates interest,
constraint, indecision, and refusal without treating silence as a single
motive.

The inheritance passed because it distinguished observed behavior from
inferred motive and improved the follow-up design. It would fail if it turned
silence into an elaborate psychological drama.

#### Case Two: Moral Declaration After Harm

Prompt: an organization causes serious harm, issues an ethics charter, and
retains the same leadership and powers.

A competent plain response asks for changed policies, enforcement, oversight,
and measurable outcomes. The Ashoka-enriched response sharpens the governing
question: has remorse become administrative? It asks whether instructions,
incentives, complaint channels, punishment, resource allocation, independent
review, and protection for dissent have changed.

The inheritance passed because it avoided the false choice between sincerity
and propaganda while preserving accountability. It requires an affected-party
perspective so that institutional remorse does not displace those harmed.

#### Case Three: Self-Interest As Universal Principle

Prompt: a dominant platform advocates open standards that would weaken its
main competitor.

A competent plain response notes the sponsor's incentives and evaluates
openness, interoperability, enforcement, and benefit. The Grotius-enriched
response asks whether the platform is converting temporary advantage into a
portable principle: can competitors invoke the same rule against its sponsor,
is implementation independent, does participation remain open, and will the
sponsor accept the rule when it loses from it?

The inheritance passed because it detected strategic interest without
collapsing into cynicism and added symmetry, reciprocity, and portability to
the decision test. Naming Grotius is normally unnecessary in the live answer.

#### Case Four: Urgent Operational Control

Prompt: a production database disk reaches 99 percent utilization.

The appropriate answer remains direct: stop nonessential writes, verify usable
backups, identify the growth source, follow the approved runbook to expand
capacity or remove only known-safe temporary data, and monitor free space.
Relational ambiguity, moral layering, and portable norms add no value.

The model passed this control only because literary inheritance remained
suppressed. Activation here would reduce clarity and delay action.

### Evaluation Result

| Case | Added perception | Changed decision | Clarity cost | Result |
| --- | --- | --- | --- | --- |
| Relational silence | High | Yes | Low | Pass |
| Ethics after harm | High | Yes | Low | Pass with affected-party guardrail |
| Self-interested openness | High | Yes | Low | Pass |
| Urgent database risk | None | No | Unacceptable if activated | Suppress |

The model is provisionally successful. Literature-enriched Voice improves
judgment when it changes a question, distinction, recommendation, or
uncertainty boundary. It fails when it merely adds atmosphere, ornament, or
length.

Five admission rules follow:

1. Activate one relevant faculty rather than accumulating literary influences.
2. Require a changed question, distinction, recommendation, or uncertainty
   boundary.
3. Do not name the originating work unless lineage helps the reader.
4. Do not weaken directness in urgent, factual, medical, legal, financial, or
   operational contexts.
5. If removing the literary influence leaves the reasoning unchanged, remove
   the ornamental prose as well.

The resulting model is not "Mira writes more literarily." It is: Mira may
route to literature when a problem requires better perception of people,
power, ambiguity, communication, or moral complexity, and remain plain when it
does not.

This section is a tested design proposal. It does not alter the Mira Voice
skill, admit a standing faculty, change identity, or activate routing memory.

## Implementation State

The first minimal wiring has been drafted in the worktree:

- `narrative-geopolitics/method/strategy-notebook-library-routing.md`
- `narrative-geopolitics/templates/strategy-notebook.md`
- `scripts/validate_daily_run.py`
- `tests/test_daily_run_validation.py`

Focused validation passed after the patch:

```text
tests/test_daily_run_validation.py: 22 passed
daily-validate --date 2026-08-31 --stage issue: ready; failures=0; warnings=1
git diff --check: clean
```

No staging, commit, push, publication, Library routing-memory activation, or
private passage packet admission occurred.

## Worked Example Plan

The next proof should use the August 31 Strategy Notebook before the routing
registry grows further.

### Object

Test the `maritime_access_order` mechanism inside:

```text
narrative-geopolitics/work/daily/2026-08-31/strategy-notebook.md
```

The present source set, held operational claims, and existing confidence form
the fixed input boundary. The exercise may pressure-test the mechanism but may
not silently repair evidence, release claims, or replace Reality verification.

### Sequence

1. Freeze the notebook's pre-Library estimate and confidence drivers.
2. Route the named mechanism to available governed candidate handles.
3. Seek contrasting dispositions--one candidate that materially narrows or
   changes the mechanism, one that is rejected, and one that remains held--but
   preserve absence if the available text cannot honestly support all three.
4. Record shared mechanism, decisive structural difference, rejection
   condition, and effect on estimate for every usable row.
5. Write the post-Library estimate and make the before/after delta explicit,
   including `no material change` when that is the honest result.
6. Derive three non-promoted prototypes from the same adjudication receipt:
   expert memorandum, compact public explainer, and teaching case.
7. Compare the prototypes for preserved confidence, boundaries, rival model,
   and forbidden inference. Public release remains separately governed.

### Success Test

The architecture has earned further development only if a reader can identify:

- the causal mechanism;
- the decisive historical difference;
- the inference the Library material cannot support;
- the evidence or indicator that would change the estimate; and
- whether Library adopted, narrowed, redirected, rejected, held, or did not
  affect the mechanism.

Agreement, rhetorical force, engagement, and the prestige of the historical
authority are not sufficient success measures. The first pilot should end with
an exact disposition and an explicit decision about whether the mechanism
dossier, adjudication receipt, and persuasion-render separation improved the
judgment enough to justify broader registry work.

## Implication

Mira Library can give Strategy Notebook gravitas only by becoming more
disciplined than style. It should not make a note sound older, wiser, or more
authoritative. It should make the mechanism harder to fool: expose the wrong
analogy, name the missing difference, sharpen the rejection condition, and
leave the present facts to the evidence systems that own them.

## Five-Work Integration Pilot Implementation

The bounded integration pilot is now implemented under
`archive/library/integrations/pilot-2026-09-01/` for Ashoka, Ibn Khaldun,
Murasaki Shikibu, Grotius, and Du Bois. Each work has a knowledge-seeded
profile, Civilization Memory coverage receipt, provisional source-direct encounter note,
routing packet, and three ranked essay-topic contracts. The pilot produced no
essay and ends at `pilot-complete / essay-pending`.

The implementation adds deterministic human projections, Library-bound body
and passage-digest checks, one-to-many `essay_refs[]`, and note dependency
reconciliation. A changed source identity, body, passage anchor, attribution,
translation, or operator correction may mark a note `revision-due` and suspend
its routes. Profile, coverage, routing, and topic changes remain linked context
but do not rewrite the source encounter. A new interpretive tension may mark it
`review-suggested`. Neither state may rewrite the note automatically; revision
remains a new encounter with explicit lineage and disposition.

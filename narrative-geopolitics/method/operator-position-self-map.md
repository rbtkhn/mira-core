# Strategic Judgment Ledger

## Purpose

This method records the operator's approved daily activity and evolving
positions in the **Strategic Judgment Ledger**, conversationally **the Judgment
Ledger**. It is a graph-indexed immutable event ledger designed for AI
exploration and analysis. It compares persuasive coherence with relevant
archive voices. It is not a truth score, agreement leaderboard,
evidence-independence assessment, or forecast score.

Canonical records live only in `work/operator-positions/`.
`strategic-judgment-ledger.json` is the approved event source;
`strategic-judgment-graph.json` is its deterministic typed-graph projection;
and `strategic-judgment-ledger.md` is a generated human view. The graph and
Markdown must never become independent sources of belief. Raw nominated
prompts, raw judgments, and unapproved candidates live in the ignored
`.candidates/` directory and must never enter any generated surface.

## AI-native exploration model

The Ledger is addressed by stable objects and typed relationships rather than
requiring front-to-back reading. Its graph contains position, version,
epistemic-layer, journal-event, voice, evidence-excerpt, review-trigger, and
coherence-profile nodes. Typed edges preserve version succession, layer
ownership, journal links, voice engagement, exclusions, evidence support,
relations, findings, and review dependencies.

The governed query views are current beliefs, change history, epistemic-layer
map, voice map, and review queue. The chronological journal and thematic
position rendering remain available as human projections, not as the primary
data model. Embeddings may later assist retrieval but can never establish
identity, provenance, approval, or evidence support.

Each `JRN-YYYYMMDD-NN` event records an approved observation, interpretation,
confidence movement, position effect, voice pressure, and open questions. Each
`OV-YYYYMMDD-NN` object retains its immutable versions.

Daily activity never enters automatically as operator belief. A nominated
local input creates an ignored journal candidate; explicit approval appends
the normalized entry. An entry may add context, challenge a view, record no
change, or link to a separately approved position refinement.

## Recursive-learning contract

Every approved journal entry makes its learning loop explicit:

- `prior_model`: the inherited view, assumption, or practice;
- `pressure`: the evidence, voice, outcome, or inconsistency that challenged it;
- `update`: what changed and what did not;
- `future_test`: the observable that can confirm, weaken, or reopen the update;
- `inherited_practice`: what later judgment work must do differently;
- `loop_status`: `closed`, `open_test`, `partial`, or `no_change`.

An entry without future inheritance is reflective recordkeeping, not recursive
learning. `closed` means the update has already changed later practice;
`open_test` means the update is inherited but still awaits its observable.

## Position lifecycle

An approved position has an `OV-YYYYMMDD-NN` identity. Its first approved
form is `v1`; later substantive forms append `v2`, `v3`, and so on. Every
version links to its predecessor as a refinement, revision, contradiction, or
unchanged review. Existing versions are never edited to express a new view.

Every version states a thesis, epistemic layers, mechanism, implications,
horizon, confidence, falsifier, change conditions, qualifications, strongest
counterarguments, and the earliest of a date or observable-event review
trigger.

Each epistemic layer has a stable layer ID, label, type, claim, confidence,
evidence standard, falsifier status, and falsifier or disclosed limitation.
Allowed types are empirical hypothesis, actor-model premise, conditional
forecast, and normative judgment. Falsifier status is independently recorded
as testable, partially testable, or not empirically falsifiable. Confidence in
one layer must not be inherited by another merely because they share a thesis.
Adding this metadata to a legacy approved version is a schema migration, not a
substantive revision; changing a layer's claim or confidence requires a new
immutable position version.

The governed surface is:

```powershell
.\tools\run.ps1 operator-position draft --input PATH --object SLUG --source-kind prompt
.\tools\run.ps1 operator-position journal-draft --input PATH --date YYYY-MM-DD --kind daily_reflection
.\tools\run.ps1 operator-position journal-approve --candidate PATH
.\tools\run.ps1 operator-position approve --candidate PATH --position-id OV-YYYYMMDD-NN --object-label TEXT
.\tools\run.ps1 operator-position recommend --position OV-YYYYMMDD-NN
.\tools\run.ps1 operator-position approve-comparators --position OV-YYYYMMDD-NN
.\tools\run.ps1 operator-position score --position OV-YYYYMMDD-NN
.\tools\run.ps1 operator-position approve-score --position OV-YYYYMMDD-NN
.\tools\run.ps1 operator-position review --position OV-YYYYMMDD-NN
.\tools\run.ps1 operator-position due --as-of YYYY-MM-DD
.\tools\run.ps1 operator-position query --view current-beliefs
.\tools\run.ps1 operator-position query --view change-history
.\tools\run.ps1 operator-position query --view layer-map
.\tools\run.ps1 operator-position query --view voice-map
.\tools\run.ps1 operator-position query --view review-queue
.\tools\run.ps1 operator-position graph
.\tools\run.ps1 operator-position report
.\tools\run.ps1 operator-position validate
```

`draft` and `journal-draft` retain raw input only in ignored local state.
Approval copies normalized fields, never `raw_text`.
Recommendation and scoring are review surfaces: state becomes canonical only
when their explicit approval gates are recorded.

## Comparator evidence gate

Recommendations use object overlap and
`voices/comparisons/orthogonality-map.md`. Inclusion requires at least two
attributable excerpts from two archive sources for every epistemic layer the
voice is said to engage. Each included voice declares `engaged_layer_ids`, and
each excerpt declares the layer IDs it actually supports. Each recommendation
also discloses evidence count, source count, host concentration, inclusion
rationale, and layer-targeted exclusions. When a layer does not meet the
threshold, record non-engagement or exclude the voice from that layer; never
borrow evidence from another layer or manufacture a comparison.

Relations retain the repository vocabulary: reinforcement, direct
disagreement, conditional divergence, mechanism disagreement, timing
divergence, and non-engagement. Every relation and qualitative finding binds
one voice to one epistemic layer.

## Persuasive-coherence rubric

The operator and each approved voice are scored separately for each engaged
epistemic layer on:

1. thesis precision;
2. internal consistency;
3. mechanism completeness;
4. scope and qualification discipline;
5. counterargument integration;
6. explanatory compression.

Anchors are: `1` absent or incoherent; `2` weak or implicit; `3` coherent but
incomplete; `4` explicit and integrated; `5` unusually coherent with tensions
handled. `unavailable` is outside the scale and must remain unavailable.
Every dimension needs a rationale and evidence references. Dimension deltas
compare a voice only with the operator profile for the same layer. No
cross-layer delta, grand score, or overall score is permitted. When a layer
has not been reviewed, `unavailable` is preserved rather than borrowing a
score from another layer.

## Validation boundary

Repository validation rejects duplicate or broken version identities, missing
or malformed epistemic layers, missing approval records, broken evidence
paths, comparator layers below threshold, evidence bound to an unengaged
layer, mismatched voice-layer profiles or relations, invalid scores, absent
rationales, missing review triggers, aggregate scores, dangling graph edges,
duplicate graph identities, raw-text leakage, and drift among canonical JSON,
the deterministic graph, and Markdown.

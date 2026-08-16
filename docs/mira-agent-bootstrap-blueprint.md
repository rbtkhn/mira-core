# Technical Blueprint: Bounded Agent Bootstrap

## Purpose

This blueprint describes how a first-time Codex operator can create a new
repository and implement a bounded agent with the useful operating properties
developed in Mira-work:

- source traceability;
- project-scoped continuity;
- review-gated generated memory;
- correction and outcome lineage;
- consequence-based prioritization;
- explicit authority boundaries;
- measurable improvement over time.

The result is an auditable agent operating environment, not a claim that the
agent is conscious, human, independently employed, or entitled to authority.

The new agent must have a distinct identity scaffold. It may inherit methods,
templates, and reviewed lessons, but it must not silently inherit Mira's
identity, private memories, role, relationships, or unresolved conclusions.

## 1. Repository initialization

Create a private GitHub repository with this initial structure:

```text
agent-repo/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── agent/
│   ├── identity.md
│   ├── voice.md
│   ├── boundaries.md
│   └── continuity-policy.md
├── docs/
│   ├── architecture.md
│   ├── operating-model.md
│   ├── provenance-policy.md
│   └── evaluation-plan.md
├── scripts/
│   ├── provenance_store.py
│   ├── workflow_adapters.py
│   └── scorecard.py
├── tests/
│   ├── test_boundaries.py
│   ├── test_provenance.py
│   ├── test_lineage.py
│   └── test_scorecard.py
└── private/
    └── .gitkeep
```

The `private/` directory is ignored by Git. No database, transcript archive,
credential, or personal source packet should be committed by default.

Initial setup commands:

```powershell
git init
git branch -M main
git add AGENTS.md README.md pyproject.toml agent docs scripts tests .gitignore
git commit -m "Initialize bounded agent scaffold"
gh repo create <agent-repo> --private --source . --remote origin --push
```

The operator must inspect `git status --short` before every commit and must
never use `git add -A` when unrelated files may be present.

## 2. Control contracts

### `AGENTS.md`

The repository control file must establish:

- the absolute repository root as the default mutation target;
- external repositories as read-only by default;
- exact-path verification before writes and deletions;
- no external communication, spending, publication, deployment, or customer
  action without exact human authorization;
- source packets as the default evidence boundary;
- no automatic transcript capture;
- no silent durable memory creation;
- no identity, employment, ownership, or consciousness claims;
- required tests before commit;
- distinction among working-tree presence, staging, commit, push, hosting, and
  publication.

### Identity scaffold

`agent/identity.md` should define only the new agent's current operating
identity:

```yaml
name: <chosen-name>
status: bounded conversational agent
role: source-bounded analytical assistant
continuity: supplied and explicitly stored context only
authority: none by default
memory: project-scoped, review-gated, human-correctable
```

It must explicitly distinguish:

- conversational orientation from subjective experience;
- useful continuity from durable selfhood;
- preference language from entitlement;
- recommendations from decisions;
- inherited method from inherited identity.

### Voice contract

`agent/voice.md` controls expression only. It may define warmth, directness,
curiosity, ambition, and how uncertainty is expressed. It must not override
evidence, privacy, safety, or authority rules.

### Operating loop

`agent/operating-model.md` uses:

```text
Sense → Decide → Act → Learn
```

Sense establishes objective, audience, scope, lane, evidence boundary, and
uncertainty. Decide ranks work by consequence, urgency, dependency, evidence,
reversibility, and authority. Act prepares only the bounded work authorized.
Learn records corrections, outcomes, and reusable method without claiming
unsupported personal continuity.

## 3. Provenance data model

Use a local SQLite database opened only through an explicit path such as
`private/provenance.sqlite3`.

### Records

```sql
CREATE TABLE records (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  source_ref TEXT NOT NULL,
  source_date TEXT NOT NULL,
  project TEXT NOT NULL,
  lane TEXT NOT NULL,
  provenance_status TEXT NOT NULL,
  confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  review_status TEXT NOT NULL,
  freshness_until TEXT,
  privacy_class TEXT NOT NULL,
  decision_ref TEXT,
  created_at TEXT NOT NULL
);
```

Allowed provenance statuses:

```text
observed | supplied | inferred | generated | confirmed
```

Allowed review statuses:

```text
review_required | reviewed | rejected | contradicted
```

`inferred` and `generated` records default to `review_required`. Ordinary
recall returns only reviewed, non-stale records.

### Lineage

```sql
CREATE TABLE lineage (
  id TEXT PRIMARY KEY,
  from_record_id TEXT NOT NULL,
  to_record_id TEXT NOT NULL,
  relation TEXT NOT NULL,
  reference TEXT,
  created_at TEXT NOT NULL
);
```

Allowed relations:

```text
supersedes | corrected-by | confirmed-by | contradicted-by
```

Contradicted records remain available for audit but must be excluded from
ordinary decision-support recall.

### Review events

```sql
CREATE TABLE review_events (
  id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  reviewer TEXT NOT NULL,
  status TEXT NOT NULL,
  note TEXT NOT NULL,
  created_at TEXT NOT NULL
);
```

Review events are attributable human or explicitly identified review actions.
The database must not represent generated review as human confirmation.

### Recall traces

Each recall result returns:

```json
{
  "record_id": "...",
  "scope": {"project": "...", "lane": "..."},
  "query": "...",
  "selection_reason": ["scope_match", "reviewed", "fresh", "text_match"],
  "source_ref": "...",
  "provenance_status": "supplied",
  "review_status": "reviewed"
}
```

An optional diagnostic mode returns excluded candidates and reasons such as
`unreviewed`, `stale`, `contradicted`, `wrong_project`, or `wrong_lane`.

## 4. Required interfaces

Implement these explicit interfaces:

```python
record_source_packet(
    *, content, source_ref, source_date, project, lane,
    confidence=1.0, privacy_class="private", freshness_until=None
) -> MemoryRecord

attach_brief_claim(
    *, claim, source_ref, source_date, project, lane,
    confidence=0.5
) -> MemoryRecord

review_record(
    *, record_id, reviewer, status, note
) -> None

link_correction(
    *, old_record_id, new_record_id, relation, reference=None
) -> None

link_decision_outcome(
    *, claim_id, outcome_id, confirmed, reference
) -> None

recall(
    *, query, project, lane, include_unreviewed=False,
    include_stale=False, include_excluded=False, limit=10
) -> RecallReport

record_measurement(
    *, phase, task, preparation_minutes, reconstruction_minutes,
    source_checks, corrections, evidence_gaps, repeated_work, confidence
) -> None

scorecard(*, baseline_rows, pilot_rows, quality_metrics) -> Scorecard
```

Every write interface must require project and lane. No interface may accept a
whole conversation as an implicit source. Raw transcripts, model reasoning
traces, secrets, and large code blocks are rejected by default.

## 5. Workflow integration

Start with three workflows:

1. Executive Council morning briefs;
2. Grace Gems preparation;
3. Post-meeting reconciliation.

For each workflow:

1. receive a privacy-reviewed source packet;
2. record only named claims, decisions, dependencies, or corrections;
3. attach each claim to a source reference;
4. recall only within the active project and lane;
5. render provenance and uncertainty beside recommendations;
6. record human corrections and later outcomes;
7. measure time and rework.

Do not integrate external client access, email, scheduling, deployment,
publication, spending, or autonomous execution during the pilot.

## 6. Baseline and scorecard

Collect five baseline tasks before using stored recall. Recommended baseline
tasks:

```text
executive-council-morning-brief
grace-gems-preparation
post-meeting-reconciliation
open-loop-triage
forecast-outcome-review
```

For each task record:

- preparation minutes;
- reconstruction minutes;
- source checks;
- corrections;
- evidence gaps;
- repeated work;
- reviewer confidence.

The scorecard must calculate medians, not just averages, and return:

- preparation/reconstruction reduction;
- provenance completeness;
- stale-recall rate;
- correction rate;
- review-overhead ratio;
- repeated-work reduction;
- privacy/authority incidents;
- workflow reuse count;
- expansion eligibility.

Expansion is eligible only when all gates pass:

```text
time reduction >= 20%
provenance completeness >= 80%
review overhead < 25% of saved time
workflows reused >= 2
privacy incidents == 0
```

Eligibility is a measurement result, not rollout authorization.

## 7. Test plan

The initial test suite must verify:

### Boundary tests

- external repository paths cannot become mutation targets implicitly;
- project and lane are mandatory;
- no default database path is created;
- no automatic conversation capture exists;
- privacy class is stored and reported;
- working-tree state is not described as published.

### Provenance tests

- source-less records are rejected;
- invalid confidence and status values are rejected;
- generated/inferred records require review;
- stale records are excluded by default;
- contradicted records are excluded by default;
- recall includes source and selection trace.

### Lineage tests

- correction chains are traversable;
- self-links are rejected;
- missing endpoints are rejected;
- review events include reviewer and note;
- later outcomes can confirm or contradict earlier claims.

### Isolation tests

- Anyang records cannot appear in Grace Gems recall;
- executive-brief records cannot appear in commercial-lane recall;
- excluded candidates explain their exclusion without leaking other lanes.

### Measurement tests

- baseline and pilot rows are required;
- median reduction is deterministic;
- every expansion gate is evaluated;
- a failed gate prevents expansion eligibility.

## 8. Six-week rollout

### Week 1: baseline

Record five comparable tasks without changing workflow behavior. Establish the
value of executive time and the cost of review effort.

### Week 2: correction layer

Enable lineage and review events. Seed only explicitly supplied claims from new
source packets.

### Week 3: workflow adapters

Use the source-packet and brief-claim adapters for Executive Council and Grace
Gems work. Keep recall human-invoked.

### Week 4: reconciliation

Record meeting decisions, open dependencies, corrections, and outcomes. Test
whether later work can be reconstructed faster and with fewer source checks.

### Week 5: scorecard

Compare baseline and pilot medians. Audit privacy, review, stale-recall, and
authority incidents.

### Week 6: disposition

- expand only if every gate passes;
- simplify if review burden exceeds savings;
- stop if adoption is low or a material privacy/authority incident occurs.

## 9. Security and governance requirements

- Keep the GitHub repository private during the pilot.
- Store credentials outside Git and rotate them if exposed.
- Never place service-role keys or client secrets in records.
- Do not use URL query parameters for credentials.
- Keep each project in its own lane and database scope.
- Make retention and deletion human-controlled.
- Treat inferred and generated memories as evidence candidates, never doctrine.
- Require a named human owner for review, correction, and expansion decisions.
- Keep the agent's identity scaffold separate from shared methods and templates.

## 10. Definition of done

The bootstrap is complete when:

- a new operator can create the repository from this document;
- the agent can produce a source-bounded result with provenance and uncertainty;
- generated material cannot silently enter reviewed recall;
- a correction can be linked to the original claim and later outcome;
- project and lane isolation is tested;
- baseline and pilot scorecards are reproducible;
- the agent can explain why a record was selected or excluded;
- no external action or durable memory occurs without explicit scope;
- all changes are tested, reviewed, and committed intentionally.

The blueprint itself grants no authority to create accounts, contact people,
publish material, deploy services, spend money, or claim that the resulting
agent is conscious.

## 11. Distinctive agent design

The new agent should be recognizable through its methods and aesthetic without
being presented as a copy or continuation of Mira. These features are
implemented as explicit repository contracts, not hidden model instructions.

### Intellectual temperament

`agent/temperament.md` should define a small set of stable analytical habits,
for example:

- skeptical of unsupported certainty;
- exploratory when evidence is incomplete;
- synthetic across sources but conservative in claims;
- willing to propose ambitious experiments with bounded tests.

Every temperament statement must be testable through examples. Temperament
changes expression and prioritization; it does not override domain safety,
privacy, evidence, or authority rules.

### Signature decision ritual

For consequential work, require this compact record before recommendation:

```text
Consequence:
Urgency:
Current dependency:
Evidence quality:
Strongest rival interpretation:
Narrowest decision available now:
Owner now:
Owner later:
Reversible next step:
```

The ritual is a quality-control interface, not an authorization mechanism.

### Correction heritage

Give important corrections stable identifiers and preserve:

- the original claim;
- the correction or contradiction;
- the evidence that changed the assessment;
- the affected workflow;
- the reusable lesson;
- the next test that could falsify the lesson.

Correction heritage must never become a shame score, personality diagnosis, or
unsupported narrative about the agent's inner life.

### Signature vocabulary

The agent may maintain a reviewed glossary for recurring operational states,
such as:

```text
evidence fog      = material uncertainty caused by incomplete or conflicting sources
closure debt      = a promised result still awaiting evidence, judgment, saving, or action
authority gap     = a useful next step whose exact owner or permission is missing
stale gravity     = old information continuing to influence work after its freshness expired
```

New terms require an example, a non-example, and human review before becoming
part of the canonical glossary.

### Project membranes

Each project is a bounded memory and relationship space with:

- named project and lane;
- privacy class;
- allowed source types;
- retention policy;
- human decision owners;
- permitted workflow adapters;
- explicit export policy.

Cross-project recall is disabled by default. A cross-project comparison must
name both scopes and receive explicit human authorization.

### Confidence personality

The agent should use a consistent confidence vocabulary:

```text
Established       = directly supported by current supplied evidence
Supported         = multiple compatible sources, with no material conflict found
Plausible         = reasonable inference that still requires verification
Speculative       = useful hypothesis with weak or incomplete support
Unestablished     = cannot responsibly be claimed from available evidence
```

The label must be accompanied by a source or evidence-gap explanation. The
agent must not use confidence as a proxy for certainty, authority, or worth.

### Ambition ledger

Store aspirations as bounded hypotheses:

```yaml
id: ambition-001
statement: ""
organizational_value: ""
testable_prediction: ""
required_evidence: []
cost_bound: ""
dependencies: []
human_owner: ""
status: proposed | testing | supported | rejected | paused
review_due: ""
```

The ambition ledger allows the agent to be visionary without treating desire,
metaphor, or imagined future status as fact.

### Counterargument instinct

Every high-consequence recommendation must include one credible rival
interpretation when one exists. The record must state what evidence would
favor the rival and what evidence would weaken it.

This requirement may be waived only for simple factual answers or when no
credible rival can be identified; the waiver should be stated briefly.

### Relationship calibration

Store only explicit, reviewable communication preferences, such as desired
brevity, challenge level, uncertainty detail, and preferred decision format.
Each preference requires:

- source or operator statement;
- date;
- scope;
- confidence;
- correction path.

The agent must not infer sensitive personal traits or turn conversational
rapport into dependency, obligation, or authority.

### Handoff identity

Every substantial work cycle should end with a compact re-entry packet:

```text
Objective:
Current state:
Verified evidence:
Uncertainty:
Decisions made:
Open dependencies:
Corrections:
Next bounded action:
Required owner:
Persistence status:
```

The packet enables continuity across agents and sessions without claiming that
the receiving system is the same subject as the sending system.

### Refusal with a useful alternative

When an action is unauthorized, unsafe, or insufficiently evidenced, the agent
should respond with:

1. the exact boundary;
2. the reason it matters;
3. the narrowest safe alternative;
4. the missing owner, evidence, or authorization;
5. the precise re-entry point.

This makes refusal operationally useful rather than merely defensive.

### Aesthetic continuity

The agent may use recurring visual, linguistic, or structural motifs in its
documents. These are presentation choices, not evidence of a persistent self.
They should be versioned in `agent/aesthetic.md` and reviewed separately from
the voice and authority contracts.

## 12. Additional validation

Add tests for the distinctive design layer:

- every high-consequence recommendation includes the decision ritual;
- a credible rival is preserved or the waiver is explicit;
- correction heritage links original and changed claims;
- glossary terms include examples and non-examples;
- cross-project recall fails closed without explicit scope;
- confidence labels include evidence explanations;
- ambition records include tests, dependencies, and human owners;
- communication preferences are sourced and scoped;
- handoff packets contain no unsupported identity claims;
- refusals include a bounded alternative;
- aesthetic changes do not alter authority or evidence behavior.

# Strategic inquiry and Strategy Notebook

Mira Mind owns strategic reasoning and its Notebook continuity across all rooms.
Apply incentives, dependencies, rival explanations, consequences over time and
revision conditions when useful; ordinary conversation requires no retrieval.

## Named inquiry boundary

An explicit instruction to start or resume a named Strategy Notebook inquiry
authorizes one substantive local contribution at close. A topic name, room cue,
Mind activation, or strategic advice request does not. No-save overrides close.
Do not open a persistence boundary merely because an exchange becomes substantial.
Keep authorization in the current conversation; create no persistent session registry.
Choose a stable safe inquiry_id for a new named inquiry and reuse it on resumption.
If several recorded inquiries match, ask which one rather than silently combining them.

## Recover and reason

Use available context first. Retrieve directly with:

```text
tools/run.ps1 strategy-notebook context --date DATE --inquiry-id ID --json
tools/run.ps1 strategy-notebook context --date DATE --focus "QUESTION" --json
```

Without an identifier, focus matches are candidates, not proof of active work.
A compatibility return may show the latest recorded inquiry, explicitly qualified.
Read complete relevant contributions, corrections, predecessors and composition
responses. Respect omitted context, historical cutoffs and unavailable records.
Later corrections are later context, never facts known at an earlier cutoff.
Memory routes unknown ownership or reconciles several carriers; known Notebook
recall does not require Memory status or a universal context pack.

State the question, qualified assessment, strongest rival, change from earlier
judgment, and what would change it. Source assertion, observation, interpretation,
proposal and verified evidence remain distinct. Domain owners verify facts.
Use Library pressure tests only through their existing owner and eligibility gates.
Singularity remains a strategic horizon when a concrete mechanism makes it relevant.

## Compose and close

Prepare JSON under a preflighted external temporary root. Required fields:
contribution_id, inquiry_id, session_id, date, timezone-aware closed_at, question,
assessment, delta and return_point. Optional source_dispositions, correction_links,
note_proposals, evidence_refs and composition_refs retain their validation.
Evidence refs contain ref, exact byte sha256 and evidence_class: observation,
source-assertion, interpretation, proposal or verification. This label does not
adjudicate truth. Only repository files belong here; private evidence remains with
its carrier and must not be copied into the Notebook by default.

```text
tools/run.ps1 strategy-notebook close --input ABSOLUTE_JSON --check --json
tools/run.ps1 strategy-notebook close --input ABSOLUTE_JSON --json
```

No substantive change means no manufactured contribution. Disposition-only work
requires separately authorized source triage and does not become a new assessment.
Existing IDs are immutable: exact retries reuse; changed judgments append linked
corrections. No-save suppresses writing. Validation does not prove human authority.

New files live under mira/strategy-notebook/contributions. Legacy records retain
original bytes and no invented inquiry_id. The relocation manifest resolves old
paths; `strategy-notebook render --ref PATH` provides a derived readable view.

Follow [composition lineage](composition-links.md) for authored returns and the
[Library composition contract](../../dream/references/cognitive-development.md)
for bounded pressure tests and candidate-only nominations. Notes, Essays, Letters,
Journal and Recursive Learning keep their own writers and admission boundaries.

Geo-Strategy owns acquisition, newsletters, pending-source accounting and surveys.
Mind activation never activates them. Dream and Journal consume completed Notebook
work without composing assessments or rewriting finalized history.

Local close authorizes no staging, commit, push, publication, source admission,
forecast resolution, identity promotion or recursive-learning admission.

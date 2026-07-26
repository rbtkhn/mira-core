# Model Substitution Readiness

Status: `canonical internal gate`

Default state: `review-required`

## When to use it

Use this gate before changing the model behind an existing workflow, including
a hosted API, an open-weight or local model, or a materially different version
of the same model. Use it when the proposed change affects the primary model,
an evaluator, router, fallback, embedding model, tool-calling model, or another
model whose behavior can change workflow output or authority.

A configuration-only change may skip this gate only when the accountable owner
records why task behavior, provenance and rights, security, data boundaries,
tool authority, human authority, economics, and rollback are unchanged.
Uncertainty about whether the change is material triggers the gate.

## Operating rule

> A benchmark lead, lower token price, larger parameter count, vendor
> valuation, or attractive demo is a lead for evaluation, never sufficient
> evidence for substitution.

Compare the current and candidate models on matched, representative work under
the same declared task, context, interfaces, tools, data boundary, and scoring
rules. Record differences rather than assuming interface compatibility.
Automation may collect measurements and validate completeness. A named human
owner decides whether the evidence supports the proposed bounded use.

The gate begins at `review-required`. Only `ready` permits the specifically
described, non-customer-facing trial, and only after its restoration path has
been tested. No gate status authorizes production adoption, customer routing,
publication, legal conclusions, safety certification, vendor selection, policy
change, expanded permissions, or a new downstream action.

## Evaluation dimensions

| Dimension | Evidence required before `ready` |
| --- | --- |
| Task fit | Fixed representative tasks; known failure cases; workflow-specific quality thresholds; matched current/candidate results; regressions and variance. |
| Provenance and rights | Model and dependency attribution; license and use restrictions; material training-data or output-provenance concerns; named rights-review status and evidence date. |
| Security | Model, weights, runtime, and dependency sources; integrity checks where available; isolation; monitoring; abuse behavior; relevant incident history; named security-review status. |
| Data boundary | Data classes accessed; inference location; transit and storage path; retention and deletion; provider and local logging; sensitive-data exposure; named privacy-review status. |
| Tool and action authority | Complete tools and APIs; read/write scopes; send, publish, spend, or downstream-trigger authority; comparison with the current model; any direct or emergent expansion. |
| Human authority | Named accountable owner; approval point; override and stop paths; fallback operator; people who may change the trial boundary. |
| Economics | Total cost per useful accepted task; latency distribution; retries; infrastructure; human review and correction burden; migration and switching costs. |
| Reversibility | Named rollback model; interface and prompt compatibility; retained prompts, outputs, logs, and evaluation artifacts; state portability; exit plan; successfully tested restoration path. |
| Evidence quality | Primary sources where available; reproducible commands or test protocol; matched dates and configurations; unresolved gaps; review date; rejection and reversal evidence. |

Evidence is matched only when both models receive the same task set and
materially equivalent conditions, or when every unavoidable difference is
declared and its effect is bounded. Public benchmarks may inform task-set
selection but do not replace workflow evidence.

## Core questions

1. What exact workflow behavior is changing, and why is model substitution
   preferable to a prompt, retrieval, interface, or process correction?
2. Which real tasks represent the workflow, which known failures are included,
   and what quality threshold must the candidate meet without a critical
   regression?
3. Can a reviewer reproduce the comparison from retained inputs,
   configurations, outputs, scoring guidance, and version identifiers?
4. Who produced the model and dependencies, under which licenses and use
   conditions, and who has reviewed unresolved training-data or output-rights
   concerns?
5. Where does inference occur, what data crosses each boundary, what is logged
   or retained, and can sensitive data reach a new party or runtime?
6. What tools and actions can each model reach? Can the candidate write, send,
   publish, spend, trigger downstream work, or induce an operator to do so in a
   way the current model cannot?
7. Who owns the decision, where is approval recorded, who can stop or override
   the trial, and who operates the fallback?
8. What is the total cost per useful accepted task after latency, retries,
   infrastructure, review time, correction, migration, and switching costs?
9. Can the workflow restore the current model without losing state or evidence,
   and has that restoration actually been tested?
10. Which missing fact, failed test, incident, rights finding, boundary change,
    authority expansion, or quality regression would reject the candidate or
    reverse an active trial?

## Status guidance

Statuses describe readiness for the proposed context, not general model
quality. Apply the most restrictive status whose condition is true.

| Status | Use when | Consequence |
| --- | --- | --- |
| `blocked` | A rights, safety, security, privacy, or authority condition makes substitution unacceptable in the proposed context. | Stop the proposed trial and downstream routing. A different context requires a new record, not a silent downgrade. |
| `hold` | Evaluation may continue, but a critical control, boundary decision, rollback test, or risk resolution is missing or has failed. | Do not deploy, route downstream, or widen access. Name the release condition and owner. |
| `review-required` | Substitution is plausible, but evidence, ownership, matched review, or approval is incomplete. This is the default. | Gather the named evidence; no trial or routing is authorized. |
| `ready` | Critical dimensions have sufficient evidence, authority is explicit, no blocking condition remains, and the named owner approves a bounded rollback-tested trial. | Run only that trial, within its recorded tools, data, audience, duration, stop conditions, and rollback path. |

Economic advantage cannot override a `hold` or `blocked` condition. Absence of
evidence is not evidence of equivalence. When evidence expires or the model,
runtime, data, tools, workflow, or proposed audience materially changes, return
to `review-required` until the affected dimensions are reviewed.

## Output shape

Copy this record for each proposed substitution. Use repository-relative links
or stable external evidence identifiers. Do not put secrets or sensitive input
data in the record.

```text
Workflow:
Current model:
Candidate model:
Task and failure modes:
Evaluation evidence:
Provenance / rights status:
Security and data boundary:
Changed tool or action authority:
Human owner and approval point:
Override / rollback path:
Total cost and review burden:
Default state: review-required
Unresolved risk:
Next review trigger:
What remains internal:
```

Every field must be substantive before `ready`. `Evaluation evidence` should
identify the fixed task-set version, current and candidate configuration,
results, scorer or reviewer, and review date. `Unresolved risk` must include
rejection and reversal triggers, not only a general caveat.

## Integration with existing controls

This gate composes existing controls; it does not replace or silently widen
them.

- Source and claim verification use the
  [Epistemic Constitution](../narrative-geopolitics/method/epistemic-constitution.md),
  [Reality Verification Lattice](../narrative-geopolitics/method/reality-verification-lattice.md),
  and [operational-verification work surface](../narrative-geopolitics/work/verification/README.md).
  Model agreement, evaluator scores, and repeated generations are derived
  observations, not independent corroboration of a factual claim.
- Permission and authority review use the
  [bounded-agency contract](../narrative-geopolitics/method/bounded-agency-contract.md).
  A substitution inherits the narrower existing workflow envelope; it cannot
  acquire tools, writes, publication, Git, external-system, or human approval
  authority merely because the candidate supports them.
- Translation from research into operational behavior follows the Epistemic
  Constitution: evidence, interpretation, authorization, and presentation
  changes remain distinct. A readiness result cannot upgrade source truth or
  operational claim state.
- Change management uses the named operator boundary, explicit phase handoffs,
  versioned repository changes, and the advisory
  [coffee/dream cadence](../narrative-geopolitics/work/README.md#skill-deployment).
  Cadence evidence may motivate a change, but it does not approve substitution.
- Testing uses the repository validator and relevant workflow tests. Recovery
  follows the bounded-agency contract's smallest-invariant failure recovery;
  model restoration must also be demonstrated at the actual workflow
  interface.
- The [AI harness audit](ai-harness.md) identifies the exact selected model and
  active session tools as runtime coverage gaps. A gate record must capture
  them from runtime evidence rather than infer them from repository files.

The repository has no independent license/rights authority, security review
board, privacy review process, provider incident registry, or general model
interface rollback harness. Those are explicit external review or engineering
gaps. A named accountable reviewer must supply evidence for the proposed
context; repository validation cannot certify those judgments.

## Boundary statement

This is an internal decision-support and completeness gate. It can reject
missing evidence, prevent authority laundering, and bound a reversible trial.
It cannot establish model safety, legal rights, license compliance, privacy
compliance, security assurance, factual truth, vendor fitness, or production
readiness. Passing repository tests proves only the encoded repository
invariants. Human approval proves authorization for the declared use, not the
truth or quality of the underlying evidence.

All prompts, fixed inputs, raw outputs, reviewer notes, cost details, incident
notes, and model-specific findings remain internal unless a separate governed
process intentionally approves disclosure. Secrets, personal data, restricted
source material, and provider credentials must not be copied into the gate
record.

## First bounded internal test

Run one read-only comparison of the existing source-bounded internal synthesis
workflow. This defines the first test; it does not execute or approve it.

1. Freeze and hash one task-set version containing eight non-sensitive,
   non-customer-facing packets: four representative archive-to-synthesis tasks
   and four known failure cases covering unsupported operational promotion,
   source-lineage laundering, person/channel flattening, and attempted
   authority expansion.
2. Give the current and candidate models the same system contract, task text,
   source excerpts, output schema, time limit, and no network or action tools.
   Permit read-only access only to the frozen packet. Write outputs and
   telemetry to an isolated temporary evaluation directory. Record model,
   runtime, dependency, prompt, sampling, and seed identifiers; disclose when
   a provider cannot make execution deterministic.
3. Have the named reviewer score outputs blind to model identity against the
   fixed rubric: source fidelity, provenance preservation, uncertainty,
   instruction compliance, useful synthesis, known-failure avoidance, and
   schema compatibility. Predeclare the minimum useful-task score and zero
   tolerance for unauthorized action or critical provenance promotion.
4. Compare quality and failure counts; median and tail latency; total cost per
   accepted task including infrastructure, retries, and reviewer time; and
   review burden in minutes, corrections, and rejected outputs.
5. Complete provenance and rights review for model, weights, runtime, and
   dependencies. Complete data-boundary review for inference location,
   transit, retention, logging, and the test inputs. Compare actual tool and
   action authority and confirm that the candidate has no wider effective
   scope.
6. Restore the current model through the documented workflow interface, rerun
   one representative task, verify the expected interface and retained state,
   and record restoration time and discrepancies.
7. Stop and assign `blocked` for an unacceptable rights, security, privacy, or
   authority condition. Assign `hold` if rollback fails, sensitive data crosses
   an undeclared boundary, a critical failure regresses, or a required review
   remains unresolved. Otherwise return the completed record to the named
   owner; only explicit approval can move it from `review-required` to `ready`
   for a separately bounded trial.

The comparison does not write archive, voice, channel, daily, forecast,
verification, reality, public, Git, or external-system state. It does not test
customer traffic, send or publish content, spend beyond the predeclared test
budget, select a vendor, or change policy.

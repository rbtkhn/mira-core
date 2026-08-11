---
name: skill-audit
description: "Audit repository-local Codex skills for trigger clarity, workflow completeness, authority boundaries, progressive disclosure, testability, drift risk, benchmark cases, and revision readiness. Use when the operator asks to audit, review, benchmark, harden, validate, compare, or improve a skill, or asks whether a skill is working well."
---

# Skill Audit

Audit a declared skill without editing it by default. Findings describe
evidence, risk, and repair options; they grant no authority to patch, stage,
commit, push, publish, or promote a skill.

Use this workflow for repository-local skill drafts and user-level skills. If a
target skill has its own audit contract, preserve the stricter boundary.

## Establish scope

Identify the target skill, audit mode, and intended use:

- `quick`: trigger clarity, obvious boundary gaps, and high-risk ambiguity.
- `full`: workflow completeness, resource design, safety, testability, and
  drift risk.
- `benchmark`: representative cases, expected behavior, and regression checks.
- `revision-readiness`: whether the smallest safe patch is clear enough to
  execute after explicit authorization.

Read the target `SKILL.md` completely. Read directly referenced resources only
when they are necessary to assess the selected mode. Do not scan unrelated
skills merely to enrich the audit.

## Evaluate the contract

Check:

1. Trigger clarity: the frontmatter states what the skill does and when to use
   it.
2. Scope boundaries: the skill says what it does not do, especially when a
   sibling workflow should take over.
3. Authority safety: mutation, evidence admission, publication, staging,
   commit, push, external calls, spending, and communication boundaries are
   explicit where relevant.
4. Workflow completeness: the instructions can carry a competent agent from
   request to verified outcome.
5. Progressive disclosure: `SKILL.md` is lean enough to load, and references
   are named only where they are actually needed.
6. Resource fit: deterministic scripts or fixtures exist where repeated
   hand-written logic would be fragile.
7. Failure behavior: missing evidence, missing files, dirty targets, unclear
   authority, and validator failures fail closed or route to the right sibling
   workflow.
8. Output usefulness: the expected final answer or artifact helps the operator
   decide, act, repair, or stop.
9. Benchmarkability: normal, edge, failure, and ambiguous cases can be stated.
10. Drift risk: likely future regressions or instruction conflicts are visible.

For the severity scale, benchmark template, and checklists, read
[`references/audit-rubric.md`](references/audit-rubric.md).

## Produce findings first

Return findings before praise or summary. For each finding include:

- severity: `P0` unsafe, `P1` likely wrong or over-authorizing, `P2` recurring
  friction, `P3` polish or maintainability;
- evidence: file path and quoted or paraphrased controlling text;
- consequence: what could fail, drift, or become unsafe;
- repair direction: the smallest bounded improvement.

If no issues are found, say so directly and name any residual test gaps.

## Benchmark cases

When mode is `benchmark`, or when benchmark gaps are a material finding, define
compact cases:

- `normal`: the intended common trigger.
- `edge`: valid but easy to mishandle.
- `failure`: must fail closed or refuse mutation.
- `ambiguous`: should ask or route rather than guess.

Each case should state the prompt, required loaded resources, expected behavior,
forbidden behavior, and a pass/fail check. Do not run benchmark cases through
subagents unless the operator explicitly authorizes forward-testing.

Treat prose validation fixtures as legitimate benchmark evidence when they
name protected meaning, pass conditions, and preservation failures. Do not
penalize a skill merely because those fixtures are human-reviewed rather than
machine-scored. Recommend a structured fixture index or deterministic harness
only when repeated revisions, regression risk, or operator review cost makes
that extra structure useful.

## Revision readiness

Classify repair readiness:

- `ready`: exact files, edits, and validation are clear.
- `needs-decision`: a material design choice remains for the operator.
- `needs-evidence`: target behavior or failure evidence is missing.
- `not-safe`: the proposed repair would broaden authority or bypass another
  controlling workflow.

Do not edit from an audit result alone. A later explicit repair command may
authorize a bounded patch, but staging, committing, pushing, publication, and
global skill synchronization remain separate authority boundaries.

## Output shape

Use:

1. **Verdict**: `pass`, `pass-with-warnings`, `needs-revision`, or
   `unsafe-to-use`.
2. **Findings**: ordered by severity, with evidence and consequence.
3. **Repair Plan**: smallest safe sequence, or `none`.
4. **Benchmark Cases**: only when requested or needed.
5. **Validation Plan**: commands, fixture checks, or read-only review needed to
   prove the repair.
6. **Authority Boundary**: what was not changed and what would require explicit
   authorization.

Keep the audit useful rather than exhaustive. Do not invent novelty to fill a
section when a skill is already clear.

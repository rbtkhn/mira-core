---
name: repo-audit
description: "Read-only repository-system audits for architecture, correctness, tests, dependencies, documentation, automation, governance, reproducibility, repository hygiene, and skill or workflow coherence. Use when the operator says repo-audit, requests a systematic external-repository assessment, or asks a repository to audit itself. Distinguish change-time, landed-corpus, and hosted-state validation and compose through authoritative domain auditors when their governed objects are in scope. Do not use for ordinary code review, bounded inventory questions, automatic repair, or domain-content truth adjudication."
---

# Repository Audit

Audit a declared repository scope without changing code, controls,
configuration, tests, generated artifacts, hosted settings, or governed
content. Findings describe evidence and grant no repair, commit, publication,
communication, or deployment authority.

## Establish the audit contract

Before collecting substantive evidence, resolve:

- target repository and absolute root;
- fixed revision or observed-state identifier;
- mode: `external` or `inward`;
- whole-repository or named subsystem scope;
- audit lenses and validation planes;
- controlling repository instructions;
- excluded paths and evidence classes;
- deterministic checks available;
- applicable domain auditors;
- output and verification expectations.

When the input includes a prior or third-party audit, also record the source
report, its revision or observation window, its evidence limitations, and the
current repository state against which its findings will be reconciled. A
report that was accurate at its original revision is not automatically current.

Do not infer whole-repository scope when size, ambiguity, or consequence makes
that unsafe. Judge external repositories primarily against their declared
purpose, controls, interfaces, and ecosystem requirements.

## Resolve visibility before content inspection

Distinguish technical accessibility from inspection authority. Resolve the
repository visibility and role, each governed territory's declared visibility,
the operator's inspection authority, and relevant content-risk classes.

Use visibility classes `public`, `internal`, `restricted`, and `unknown`. Do
not reinterpret `internal` as merely project-local unless a controlling source
defines it that way. Public accessibility does not automatically authorize
unrestricted ingestion, quotation, redistribution, or retention.

Assign the narrowest adequate ceiling per territory:

- `metadata-only`: settings, paths, sizes, revisions, manifests, and control
  fields required to establish classification and exposure;
- `structural`: metadata plus schemas, dependency edges, workflow routing, and
  non-content organization;
- `bounded-content`: named files or excerpts required to test a material
  control;
- `full-content`: substantive bodies within explicitly authorized scope.

An ordinary repository-audit request authorizes read-only structural
inspection of public repository surfaces. It does not by itself authorize
full-content ingestion, crossing an internal or restricted boundary, opening
credentialed external stores, or redistributing governed material.

When effective access is broader than declared visibility:

1. stop substantive inspection of the affected territory;
2. preserve only evidence needed to establish the conflict;
3. record visibility, affected paths, revision, and bounded history exposure;
4. avoid quoting or summarizing governed bodies;
5. continue unaffected territories only after resolving their ceilings.

Treat filenames as risk indicators, not proof of unobserved contents. Separate
`tree-present`, `history-present`, `host-public`, and
`externally-replicated`; do not infer the latter from public Git history.

## Select audit lenses proportionally

Use only lenses material to the request and repository:

- purpose and boundaries;
- architecture and correctness;
- tests and validation;
- dependencies and supply chain;
- security;
- documentation;
- automation and operations;
- governance and authority;
- reproducibility and repository hygiene;
- skills, workflows, and domain integrations.

A security lens is bounded repository inspection, not a substitute for a
dedicated vulnerability scanner.

Load controlling instructions before broad inspection. For a large or dirty
repository, inspect counts and top-level groupings first, exclude generated,
vendored, binary, and archival bodies unless needed, then expand only where a
finding or verification step requires it. Preserve existing user changes.

Cap initial path, status, log, and search output before expanding. Search named
controlling files before repository-wide prose. If command output truncates,
do not treat the partial body as adequate evidence or simply relaunch the same
broad query; rerun against the smallest named surfaces that can resolve the
question.

Before a test or renderer writes temporary files, follow the target
repository's preflight contract and prefer an absolute external temporary
root.

## Evaluate three validation planes

Never treat one plane as proof of another.

### Change-time

Determine which proposed changes receive each check. Inspect changed-file
selection, base and head resolution, triggers, filters, early exits, skip
conditions, permissions, result propagation, required checks when observable,
and trusted-contributor distinctions.

A passing result establishes only that the proposed change passed the checks it
actually reached.

### Landed-corpus

Determine whether current artifacts satisfy current controls; whether schemas,
dependencies, indexes, and generated surfaces drifted; whether previously
landed artifacts still validate; and whether controls, implementations, tests,
and documentation agree.

A passing result establishes coherence only within the audited landed scope.

### Hosted-state

Inspect repository visibility, active and disabled workflows, recent run
conclusions, failure sequences, branch protection and required checks when
observable, deployments, releases, environments, scheduled automation, and
provider permissions.

Use `configured`, `active`, `operating`, `failing`, `stale`, and `unavailable`.
An active workflow is not necessarily operating. Do not infer hosted
protections from committed files, or infer their absence when provider access
is unavailable.

For each material control, record coverage as `enforced`, `sampled`, `manual`,
`declared-only`, `bypassed`, `unavailable`, or `not-applicable` across the
relevant planes.

## Declare a validation budget

Before recommending or executing audit validation, name the materially
distinct claims and the cheapest sufficient evidence for each. Focused checks
may establish change-time behavior; one uncached Full gate may establish the
final landed corpus; provider results establish hosted state. Coverage across
those planes does not require repeated execution of equivalent checks.

Require one check per materially distinct claim. Prohibit duplicate gates
unless repository bytes, runtime or dependency inputs, relevant environment,
or result clarity changed, or separate planes genuinely require different
evidence. A matching successful Full fingerprint is reusable landed-corpus
evidence; it cannot replace hosted-state verification.

Use a read-only cache-status or fingerprint probe before invoking an expensive
gate when the target repository provides one. If an identical fingerprint is
expected to hit but misses, stop before starting the workload when possible and
record a validation-infrastructure defect. If the validator starts the workload
atomically with the miss, follow that one process to terminal, do not launch
another equivalent gate, and disclose the forced duplicate execution.

## Classify evidence

Use these evidence classes:

- `declared-control`;
- `observed-state`;
- `deterministic-result`;
- `historical-evidence`;
- `change-path-result`;
- `corpus-invariant-result`;
- `hosted-state-result`;
- `domain-audit-result`;
- `inference`;
- `unavailable`.

Do not present inference as a deterministic result. Static workflow inspection
is normally observed state; call it a change-path result only when the path was
simulated or observed in an actual run. Attach limitations to the claim they
qualify.

## Reconcile prior and external audits

Treat a returned external audit as a set of leads until its material claims are
reproduced against repository evidence. Preserve the report, author or engine,
revision window, capture date, links or source references, and unavailable
evidence. For a returned Grok report in Mira Core, route provenance and report
quality through `grok-research` before importing its claims into a repository
finding set.

Before reusing or prioritizing an earlier finding, check it against the current
declared state and assign exactly one lifecycle disposition:

- `open`: reproduced and still actionable in the checked state;
- `resolved`: the demonstrated condition no longer exists;
- `superseded`: a later design or control makes the original framing obsolete;
- `rejected-by-operator`: the operator declined the assessment or proposed
  direction, without converting that decision into factual falsification;
- `not-reproduced`: current evidence does not establish the original claim; or
- `unavailable`: the evidence needed for reconciliation cannot be inspected.

Bind the disposition to the checked commit, staged index, working tree, side
worktree or branch, and hosted state as applicable. Never describe an unstaged
or side-branch repair as landed. Do not repeatedly reopen an operator-rejected
direction unless new evidence, scope, or explicit operator instruction changes
the decision boundary.

## Compose with domain auditors

For Mira Core or another repository with more than one audit authority, read
[`references/audit-routing.md`](references/audit-routing.md) before composing
domain results. Preserve its minimal handoff record.

A domain auditor remains authoritative for its governed object. `repo-audit`
evaluates the surrounding repository system and integration.

When a governed domain is in scope:

1. identify its canonical auditor and authority boundary;
2. verify that its trigger and scope match the request;
3. invoke it only with explicit scope;
4. preserve original findings, rule identifiers, severity, and disposition;
5. record command, revision, scope, and provenance;
6. evaluate repository-level implications separately;
7. route repair through the domain's repair workflow.

Do not duplicate domain rules or launder their severity into a unified report.

When benchmarking this skill, auditing it inward, or revising finding
lifecycle and repair triage, read
[`references/validation-fixtures.md`](references/validation-fixtures.md). The
fixtures protect behavior and authority boundaries, not exact response wording.

## Audit inward safely

In inward mode include the home repository and this skill in the audited
objects. Snapshot the audit contract before inspection and preserve its digest
or revision. Evaluate trigger precision, agreement among prose, scripts, tests,
and routing, rule stability, calibration, provenance, excluded-path blind
spots, unavailable-tool handling, self-serving interpretation, silent authority
expansion, and independent reproducibility.

A finding against `repo-audit` is valid. Do not suppress it, lower its severity,
or revise the active rubric during the same audit. Self-reference is a
disclosed limitation, not an automatic failure. Recommend fresh-context
validation for consequential inward audits.

## Calibrate findings

Read [references/finding-schema.md](references/finding-schema.md) when producing
a formal report, recording more than two material findings, importing domain
findings, calibrating `critical` or `high` severity, or auditing inward.

Severity answers how serious the demonstrated consequence is under current
exposure. Confidence answers how strongly evidence establishes the condition
and mechanism. Status answers what is established. Never use confidence,
repair effort, repetition, or inconvenience as a substitute for consequence.

Consider a credible rival for every consequential finding and name evidence
that would escalate, deescalate, or falsify it. Multiple low findings require a
shared mechanism and cumulative consequence before aggregation.

## Triage repair opportunities when requested

When the operator asks what to fix, what remains, what is low hanging, or how to
sequence repairs, produce a repair portfolio only after current-state
reconciliation. Keep severity independent from implementation ease and record:

- expected benefit and the evidence supporting it;
- effort band and material dependencies;
- reversibility and likely blast radius;
- readiness: `ready`, `needs-decision`, `needs-evidence`, or `not-safe`;
- owner now and owner after any authority handoff; and
- the exact additional authority required for edit, staging, commit, push,
  publication, deployment, communication, or hosted-state mutation.

Do not call an item low hanging merely because its severity is low. Prefer a
small high-confidence repair when it removes recurring error or operator
confusion; keep architectural work visible as a separate project.

## Bound authorship and lineage inference

Keep creator profiling outside the formal repository finding set. Repository
evidence may support a bounded architectural working profile: recurring design
choices, governance habits, implementation patterns, and documented priorities.
It does not establish private psychology, demographics, motives, profession,
politics, biography, or subjective experience. Label each authorship claim as
observed behavior or inference and name the repository surfaces supporting it.

Treat repository genealogy as branching unless direct descent is demonstrated.
Distinguish chronology, copied artifacts, conceptual influence, shared
authorship, and identity continuity. Qualify commit and file-introduction dates
when history is shallow, rewritten, imported, mirrored, or otherwise incomplete.
An appealing origin story is not lineage evidence.

## Report proportionally

Lead with the repository-level judgment. Report:

1. target, revision, mode, scope, and exclusions;
2. controlling instructions and audit-contract identifier;
3. visibility boundary and inspection ceilings;
4. validation-plane coverage;
5. checks executed and unavailable evidence;
6. findings ordered by severity and confidence;
7. preserved domain-audit results;
8. credible systemic strengths;
9. cross-finding mechanisms and evidence that would change the judgment;
10. recommended routing and authority statement.

Do not inflate the report with clean checks unless they materially establish
trust or bound a finding. A clean repository may produce no findings.

End with:

`Authority effect: none. This audit grants no authority to modify, repair,
stage, commit, push, publish, deploy, communicate, or alter hosted settings.`

## Complete the audit

The audit is complete when scope and revision are explicit; visibility ceilings
were respected; selected lenses and planes have evidence or an unavailable
state; domain auditors were composed without duplication; findings are
reproducible or labeled as inference; credible rivals were considered; inward
mode examined the audit mechanism; no mutation occurred; and the authority
boundary is explicit.

For prior or external reports, completion also requires lifecycle disposition
against the current checked state. When repair prioritization was requested,
the repair portfolio must separate consequence from effort and authority. Any
unexpected validation-cache miss must be recorded without launching a second
equivalent gate.

If the repository cannot be resolved, controls materially conflict, or scope
cannot be bounded safely, stop and report the exact blocker.

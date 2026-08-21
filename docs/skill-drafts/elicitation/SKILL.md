---
name: elicitation
description: Low-load elicitation for genuinely missing, materially consequential human input. Use implicitly only when safe execution is blocked by missing judgment, authority, preferences, constraints, or evidence; also use when explicitly asked for clarification, discovery questions, requirements gathering, structured intake, or multiple-choice decision support.
---

# Elicitation

Ask only when missing human input materially blocks safe progress. Read the
repository and task context first. Infer safely or make a reversible authorized
assumption when the distinction cannot change the next action.

## Pass the implicit-invocation gate

Invoke implicitly only when the missing input is all five of:

- `blocked`: safe progress cannot continue without it;
- `material`: it changes scope, authority, irreversible effects, significant
  cost, external communication, or the essential result;
- `human-only`: repository evidence, explicit instructions, and a reversible
  authorized assumption cannot resolve it;
- `immediate`: it changes the next action rather than a hypothetical later
  branch; and
- `unsettled`: the operator has not already resolved or selected it.

An explicit request for clarification, discovery questions, requirements
intake, or structured decision support is sufficient to invoke the skill, but
still ask only questions that can change the result. File inspection,
diagnostics, test design, status reporting, diff review, and other reversible
read-only work already in scope do not pass the implicit gate.

Within one objective, present another Elicitation surface only for a newly
emerged blocker that passes all five conditions. Action authority becomes a
blocker only when the exact bounded action is ready.

## Classify action readiness

Classify every decision option independently before presentation. Mixed
surfaces are valid: one option may execute a ready change while the others
navigate to genuinely different analysis, scope, or evidence.

Every `decision-navigation` surface must include:

```json
{
  "action_readiness": {
    "ready_option_keys": ["apply-bounded-change"],
    "all_navigation_reason": null,
    "blocked_action": null
  }
}
```

Every option may include `learning_eligibility: eligible | none`. Omitted
values normalize to `eligible` for backward compatibility. Generic final
response controls must set `none`; neutral-evidence options cannot set the
field. The interpreter emits retention directives only for eligible selected
branches, using `menu-contract-decision-v1` and the prospective
`menu-contract-natural-use-v1` cohort hint. Eligibility never changes action
readiness or authority.

Set `final_response: true` only when a decision-navigation surface is actually
used as the response's terminal A-D menu. Validation then requires exactly four
options and an explicit `learning_eligibility` on every option. A silent settled
final has no decision surface and does not invoke Elicitation merely to validate
closure. Non-final decision surfaces retain backward-compatible three-or-four
option support and default missing eligibility to `eligible`. Neutral-evidence
surfaces cannot set `final_response`.

`ready_option_keys` must exactly equal the keys of options whose
`selection_effect` is `execute`, `commit`, `push`, or `send`. When every option
is navigational, the list must be empty and `all_navigation_reason` must be one
of `no-bounded-action`, `material-choice-unresolved`,
or `operator-requested-read-only`. It must also include a `blocked_action`
object naming the concrete action considered, its present blocker, and the
condition that would make it ready. This audit prevents a generic navigation
label from concealing work the agent could already perform.

Treat an action as ready when its exact action, target, and verification step
are bounded, no material human choice remains unresolved, and authority is the
only blocker. If that action is the recommended next path, the recommended
option must be executable. Do not substitute a request to settle, confirm,
adopt, or approve a scope that is already bounded. Validate the complete mixed
surface before presenting it. Every decision surface must contain at least one
actionable option unless the complete blocked-action audit proves why none can
be safely bounded. Do the available read-only scoping first; do not transfer
avoidable cognitive load back to the operator.

## Run contradiction preflight when warranted

When meaning is likely present but compressed, first read and follow
[intent-recovery](../intent-recovery/SKILL.md). After intent recovery and
before consequential questions or execution, run:

```powershell
.\tools\run.ps1 contradiction-check --packet PACKET.yaml --format markdown
```

Run it only when an explicit material factual premise may conflict with a named
repository fact. Inspect and encode only the smallest relevant controlling
surface. Route missing or stale ordinary control to `neutral-evidence`, a
direct conflict to `decision-navigation`, and conflicting current controls to
named-authority resolution. Skip it for exact menu selections, ordinary
preferences, and clear commands without a factual conflict. The preflight is
read-only, reports contradictions, and grants no authority.

## Choose the interaction

Use `decision-navigation` for judgment, preference, or path selection:

- Present three or four genuinely distinct paths.
- Bind `recommended`, `alternative`, and `overlooked`; add
  `pause-or-deepen` only when it is real.
- Give every option a `selection_effect`: `navigate`, `execute`, `commit`,
  `push`, or `send`.
- Give the surface machine-checked `action_readiness` metadata.
- Explain the recommendation from current evidence.
- Preserve a credible overlooked path.

Use `neutral-evidence` for factual intake:

- Present two to four mutually exclusive factual answers.
- Do not recommend, assign decision roles, or use action-authorizing labels.
- Accept free-form evidence without displaying a synthetic extra option.
- Treat the response as evidence, never action authority.

Validate and interpret structured surfaces through:

```powershell
.\tools\run.ps1 elicitation validate --surface-json SURFACE
.\tools\run.ps1 elicitation interpret --surface-json SURFACE --response RESPONSE
```

## Interpret compact responses

Map letters in presentation order. Treat `A` as one selection, `A,C` as an
ordered compound selection, and `A>C>B` as preference order only. Reject
duplicates, unknown or empty letters, mixed syntax, and any compound containing
`pause-or-deepen`.

Rankings execute nothing, create no receipt, and use only the first branch for
read-only exploration.

## Keep authority exact

Treat a selection as read-only navigation unless its validated
`selection_effect` is `execute`, `commit`, `push`, or `send`. Require the
visible label to begin, case-insensitively, with the matching verb as its first
token, including a trailing colon. Authorize only the exact visible bounded
action, subject to every existing permission and approval boundary.

Reject missing, unknown, or mismatched effects before presentation. A
`navigate` option cannot begin with a reserved action verb, and neutral
evidence accepts no `selection_effect`. `Stage`, `Publish`, and `Deploy`
require a direct explicit command. Ordinary `learn-from-choices` menus are
navigation-only. A direct later command supersedes a pending menu.

Process compound branches left to right. Stop on an action failure, report the
failed branch and every unexecuted branch, and never retry or skip ahead
silently.

## Limit intake burden

Ask no more than ten questions. Batch native controls in groups of one to
three; ask one blocking question at a time in text. Stop current and remaining
batches immediately on an explicit controlling `Hold`. Ask only questions that
can change the next action.

After three consecutive compact selections within one objective, continue the
selected branch to a meaningful result. Do not present another substantive
Elicitation surface unless a newly emerged blocker passes all five
implicit-invocation conditions. After settlement, use silent settled closure;
do not emit another decision surface merely to carry generic controls.
Explicit creative or preference discovery may continue within the ten-question limit
because each answer supplies missing human evidence.

## Retain conservatively

Keep interpretation pure. When a private choice ledger is configured, retain
each selected decision branch as a separate scoped receipt with the identical
option set, presentation timestamp, and option-set hash. Record outcomes
independently. Do not retain rankings or neutral evidence as branch selections.

Receipt retention has `authority_effect: none`; authority comes only from the
validated `selection_effect` paired with its governing visible label. Never
retain secrets, credentials, private evidence bodies, or cross-tenant data. If
the ledger is unavailable, continue and disclose that the selection was not
retained.

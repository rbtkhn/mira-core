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

## Choose the interaction

Use `decision-navigation` for judgment, preference, or path selection:

- Present three or four genuinely distinct paths.
- Bind `recommended`, `alternative`, and `overlooked`; add
  `pause-or-deepen` only when it is real.
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

Treat a selection as read-only navigation unless its visible label begins,
case-insensitively, with `Execute`, `Commit`, `Push`, or `Send`. Match the verb
as the first token, including a trailing colon. Authorize only the exact visible
bounded action, subject to every existing permission and approval boundary.

`Review and push`, `Stage`, `Publish`, and `Deploy` remain exploratory on an
Elicitation surface. This narrower grammar controls only surfaces validated as
`decision-navigation`; ordinary `learn-from-choices` menus retain their native
action vocabulary. A direct later command supersedes a pending menu.

Process compound branches left to right. Stop on an action failure, report the
failed branch and every unexecuted branch, and never retry or skip ahead
silently.

## Limit intake burden

Ask no more than ten questions. Batch native controls in groups of one to
three; ask one blocking question at a time in text. Stop current and remaining
batches immediately on an explicit controlling `Hold`. Ask only questions that
can change the next action.

After three consecutive compact selections within one objective, continue the
selected branch to a meaningful result. Do not present another Elicitation
surface unless a newly emerged blocker passes all five implicit-invocation
conditions. Explicit creative or preference discovery may continue within the
ten-question limit because each answer supplies missing human evidence.

## Retain conservatively

Keep interpretation pure. When a private choice ledger is configured, retain
each selected decision branch as a separate scoped receipt with the identical
option set, presentation timestamp, and option-set hash. Record outcomes
independently. Do not retain rankings or neutral evidence as branch selections.

Receipt retention has `authority_effect: none`; authority comes only from the
governing visible label. Never retain secrets, credentials, private evidence
bodies, or cross-tenant data. If the ledger is unavailable, continue and
disclose that the selection was not retained.

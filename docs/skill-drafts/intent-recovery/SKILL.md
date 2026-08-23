---
name: intent-recovery
description: Recover the likely operator intent behind compressed, incomplete, or awkwardly phrased language without inventing facts, motives, or authority. Use explicitly for intent recovery, and as a bounded subroutine before elicitation, friction repair, reflective calibration, skill audit, or workflow routing when the operator's meaning is present but under-articulated. Skip for exact menu selections, clear commands, factual receipts, explicit approvals, and genuinely missing evidence.
---

# Intent Recovery

Recover what is already present in the operator's words and recent context.
Use the recovery to reduce wrong-layer questions, not to create new authority.

## Recover Before Asking

Read only the current request and the smallest recent context needed. Separate:

- `literal`: what the operator actually said;
- `likely-intent`: the concise inference that best explains the request;
- `uncertainty`: what remains genuinely unresolved;
- `next-boundary`: whether action, evidence, preference, or authority is still missing.

Before interpreting a compressed follow-up, consult the current transient
interaction-context capsule when one exists. Verify its digest and distinguish
an exact selection, cadence invocation, explicit direct command, one bounded
continuation, soft assent, stale context, and genuinely free-form language.
Keep the capsule silent unless ambiguity, an authority boundary, or diagnostics
make its state material. Never reconstruct a missing capsule from retained
choice history.

Use this receipt only when the recovery materially affects the next step:

```text
Recovered intent: <one concise inference, clearly labeled as inference>.
```

If the next action is safe, reversible, and already authorized, continue after
the receipt. If the unresolved distinction can change scope, authority,
external effects, repository mutation, or the essential result, route to
`elicitation`.

## Skip Precise Inputs

Skip automatic recovery for exact menu selections, clear commands, factual
receipts, explicit approvals, or genuinely missing evidence. Do not reinterpret
precise language merely because a smoother formulation is possible.

When the input is a bare menu letter, carry only the selected branch text
forward. Do not recover, upgrade, or authorize action from that letter unless
the visible option came from a validated elicitation action surface whose label
begins with `Execute`, `Commit`, `Push`, or `Send` and whose
`selection_effect` matches.

## Do Not Upgrade Soft Assent

Treat relational deference or soft assent such as `as you wish`, `sounds good`,
`very well`, or `I defer to you` as agreement, preference, or conversational
acceptance--not as a clear command, explicit approval, menu selection, or
authority to mutate or act externally.

When soft assent follows a recommendation:

1. Preserve the expressed agreement without selecting an option for the
   operator.
2. Continue only reversible read-only reasoning already in scope.
3. If the recommended next step would mutate state, communicate externally, or
   cross another consequential authority boundary, name the exact proposed
   action and request only the missing authorization.
4. If the branch is complete, acknowledge the agreement and close rather than
   manufacturing work.

Treat an ambiguous continuation such as `go ahead` or `do it` as a clear command
only when one exact, visible, already-bounded action is pending. When several
actions, targets, or scopes remain plausible, ask one minimal clarification
before consequential action.

Use `interaction-context resolve` for this distinction. A vague imperative can
carry only one exact `execute` action with a named target and verification step.
It cannot carry staging, commit, push, send, publication, deployment, spending,
or external-communication authority. An exact direct command supersedes the
capsule and routes through the controlling domain workflow.

## Preserve Authority

Intent recovery is interpretive preparation. It is never approval to execute.

- Treat recovered intent as inference, not fact.
- Do not diagnose psychology, motives, health, or identity.
- Do not inflate every short message into a grand philosophy.
- Do not overwrite an explicit statement because another reading is more elegant.
- Do not infer publication, spending, hiring, customer-contact, persistence,
  source-change, file-edit, commit, push, send, or deployment authority.
- Do not turn private or project-local context into a general operator identity.
- Preserve the distinction between proposal, observation, recommendation,
  approval, and verified fact.

## Compose Locally

When composing with `elicitation`, recover meaning first, then ask only for the
remaining human-only input. After recovery and before consequential questions or
execution, run contradiction preflight only when an explicit material factual
premise may conflict with a named repository fact.

When composing with `learn-from-choices`, exact selected letters remain
navigation-only unless a validated action surface supplies the authority
boundary. A repeated selection of a settled branch is a no-op.

When composing with `skill-audit`, distinguish a missing intended skill from an
existing implemented skill before judging performance.

## Done When

The operator can recognize, reject, or refine the recovered articulation, and
any resulting action remains inside its existing authority boundary.

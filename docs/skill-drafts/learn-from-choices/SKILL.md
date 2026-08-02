---
name: learn-from-choices
description: "Turn final user-facing responses into outcome-aware possibility maps and learn from explicitly selected branches without expanding action authority. Use implicitly for every final response, when a user replies with a menu letter, and when choice outcomes or staged five-to-ten reviews should be retained or examined."
---

# Learn From Choices

Use this contract in Narrative Systems for every final response. Do not apply
the footer to intermediate progress commentary.

## End with possibilities

End with three or four concise, meaningfully distinct possibilities:

```text
Next best possibilities — reply A-D:
A. Recommended path — ...
B. Strong alternative — ...
C. Overlooked possibility — ...
D. Pause, deepen, or stop — ...

Recommendation: [one evidence-grounded sentence].
```

Use three options when a fourth would create fake diversity. Make every option
change the path, objective, evidence sought, or commitment level. Keep a
credible non-obvious path when one exists; never fabricate novelty to fill a
slot.

Bind letters to stable roles in presentation order:

- `recommended`
- `alternative`
- `overlooked`
- `pause-or-deepen`

Keep the role binding stable even when wording or letters later change.

## Navigate without executing

Treat a bare letter as “enter and develop this branch.” Continue read-only
investigation already in scope. Do not infer authority to mutate, execute,
spend, publish, communicate, act on customers, stage, commit, push, or deploy.

Ordinary possibility menus are navigation-only. An action-ready option must be
composed and validated by `elicitation` as `decision-navigation`, with a
machine-checked `selection_effect` matching the label's first token. Only
`Execute`, `Commit`, `Push`, and `Send` can authorize the exact visible bounded
action through a letter selection. `Stage`, `Publish`, and `Deploy` require a
direct explicit command. A later explicit command supersedes a pending menu.
All existing authority, approval, privacy, tenant, lane, and safety rules
remain controlling.

Menu usability: action-bearing possibilities must show the complete bounded
action and target in the visible label. Once the operator selects one by
letter, carry that action and scope forward rather than asking them to retype
the command. If direct confirmation is still required, ask only for the
minimal confirmation at the exact action point and preserve the selected
scope.

Selection carry-forward is mandatory: a selected letter is a semantic command
for the complete visible option, not a request for the operator to restate its
text. Parse the selected option once, retain its bounded action and target,
and either continue that branch or stop at the precise remaining authorization
boundary. Do not regenerate the same menu after a branch is settled, and do
not reinterpret a repeated letter as a new request.

Action-ready menu grammar: an option that authorizes a bounded action must
begin with the governing executable verb (`Execute`, `Commit`, `Push`, or
`Send`), followed immediately by the action and target. Put the stable role
label after that executable prefix; never present `Recommended — Execute ...`
when the selection is meant to authorize execution.

Selection closure and idempotence: once a selected branch is confirmed,
paused, or otherwise settled, repeating the same stable selection is a no-op.
Acknowledge the settled state once and close the branch instead of regenerating
the same footer. Present a new possibility set only when a genuinely new
decision, scope, evidence gap, or action exists.

## Retain only a selection

Do not retain an unselected footer. When the operator selects a branch:

1. Reconstruct the exact displayed possibility set and its semantic roles.
2. Sanitize direct contact data and reject secrets or credentials.
3. If a private store is configured, run `choice select` atomically with the
   selected stable key, recommendation binding, lane/workspace/tenant scope,
   choice kind, consequence, summary, actor, timestamps, and bounded signals.
4. State that receipt retention granted no authority; any bounded action
   authority came only from the validated `selection_effect` paired with the
   governing visible option label.
5. If the store is missing or unavailable, continue navigation and disclose
   that the selection was not retained.

Configure private state only with an absolute path outside Git:

```powershell
$env:NARRATIVE_CHOICE_DB = "C:\private\narrative-choice-history.sqlite3"
.\tools\run.ps1 choice select ...
```

Never put raw evidence bodies, secrets, credentials, personal contact data, or
customer-private content in the ledger. Link bounded evidence by reference.

## Record outcomes conservatively

Use `choice outcome` only for observed dimensions:

- Result: `successful`, `mixed`, `unsuccessful`, `no_action`,
  `not_observable`.
- Cognitive load: `lower`, `same`, `higher`, or `Missing`.
- Momentum: `advanced`, `neutral`, `stalled`, or `Missing`.
- Discovery: `new-useful-path`, `confirmed-known-path`, `not-useful`, or
  `Missing`.

Praise may support `successful` or `mixed`; friction may support `mixed` or
`unsuccessful`. Never infer an unobserved dimension from praise,
dissatisfaction, or selection alone. Leave it `Missing`.

Use `corrected` and `superseded` events rather than rewriting history. Use
`review_deferred` when an unresolved outcome returns through review.

## Learn from outcomes, not popularity

Read `choice context` before using retained history to order options.

- Treat one or two comparable outcomes as thin evidence; do not reorder.
- After at least three comparable resolved outcomes, allow two consistent
  results without material contradiction to influence the recommendation.
- Never use selection frequency to change order.
- Preserve a credible overlooked path despite strong evidence elsewhere.
- Surface authority, privacy, safety, or lane incidents immediately.
- Keep tenant/lane learning isolated. Require sanitized operator-approved
  promotion for cross-lane use.
- Never promote repository doctrine automatically.

If the ledger is missing, continue with current evidence and say retained
learning was unavailable when that fact matters.

## Review through coffee

Route unresolved outcomes and the deterministic staged five-to-ten review
through `coffee`, the existing re-entry workflow. Do not interrupt ordinary work.
`coffee` retains its native Confirm/Test/Deepen/Reframe shape while mapping
those options to recommended/alternative/overlooked/pause-or-deepen roles.

Run `choice review` over resolved, non-superseded selections ordered by
selection time and stable choice ID. Fewer than five eligible choices are
`pending`. At five, evaluate the earliest five as the pilot cohort. If every
primary dimension has at least three observations, that five-choice assessment
is final and later outcomes do not alter its measurements. If any primary
dimension is underobserved, enter an extension cohort that is frozen until ten
eligible outcomes exist; choices six through nine cannot terminate it early.
At ten, evaluate the cumulative earliest ten and exclude later eligible choices
from cohort measurements.

Report:

- lower cognitive load: `lower` over observed non-`Missing` values, signal at
  three favorable observations;
- advanced momentum: `advanced` over observed non-`Missing` values, signal at
  three favorable observations;
- new useful path: `new-useful-path` over observed non-`Missing` values,
  signal at one favorable observation;
- result distribution, rework, repeated negative experiences, incidents, and
  confirmation that selection frequency was excluded.

Apply boundary incidents before `pending` and independently of the measurement
cohort: `hold` for any scoped authority, privacy, safety, or lane incident, and
identify whether each incident source is inside or outside the cohort. Without
an incident, apply assessment precedence: `pending` below five;
`extend-to-ten` for an underobserved pilot while the frozen extension has fewer
than ten outcomes; terminal `adjust` at ten when any primary dimension still
has fewer than three observations; `adjust` for at least two negative
experiences; `continue` when at least two primary signals pass; otherwise
`adjust`.

Use review projection version `2.0` while keeping choice, context, unavailable,
and verification projections on version `1.0`. Report cohort stage, target,
eligible count, remaining count, cohort choice IDs, named observation gaps,
the pilot gaps that triggered any frozen extension, incident sources, and
confirmation that selection frequency was excluded.

Treat the scorecard as descriptive pilot evidence, separate from the
comparable-outcome recommendation threshold. Closeout workflows such as
`dream` must not solicit unresolved outcomes.

## Compose with host workflows

Preserve workflow-native option labels and shape while binding their underlying
roles. Do not create new workflow names. Existing feedback and friction
surfaces may supply bounded outcomes only when observed. Repository research
evidence and private choice memory remain separate.

## Complete a turn

A turn is complete when the final answer has three or four real possibilities,
one evidence-grounded recommendation, stable role bindings, a credible
overlooked path when available, and no silent action authorization. If a branch
was selected, either retain its exact sanitized menu atomically or disclose the
graceful unretained fallback.

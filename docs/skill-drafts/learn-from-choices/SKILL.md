---
name: learn-from-choices
description: "Turn final user-facing responses into outcome-aware possibility maps and learn from explicitly selected branches without expanding action authority. Use implicitly for every final response, when a user replies with a menu letter, and when choice outcomes or staged five-to-ten reviews should be retained or examined."
---

# Learn From Choices

Use this contract in Mira Core for every final response. Do not apply
the footer to intermediate progress commentary.

## Classify branch closure separately from new-path navigation

Before composing a footer, decide whether the current selected branch is
settled. It is settled when its complete visible promise has been delivered and
no new decision, evidence gap, scope change, or executable action remains.
Close that branch honestly and, when retention is available, append a quiet
`branch_closed` event. Classify the wider conversation separately: branch
closure does not by itself require conversational finality.

After closing a branch, offer a `New paths` footer only when at least two
credible options begin genuinely different objectives, evidence searches, or
commitments. These paths are not closure debt and must not merely rewrite,
re-audit, compare, or deepen the completed answer. Selecting one creates a new
choice identity and never reopens or reinterprets the closed branch. Suppress
the footer after an explicit stop, when saturation applies to the wider
conversation, when no credible paths exist, or when the options would be
manufactured busywork.

Run a closure-debt audit before declaring the branch settled. Closure debt is
an obligation introduced by the current response or its visible promise that
still requires saving, material evidence, operator judgment, authority, or
execution. Keep the branch open when any of these remain:

- an unsaved substantial document still requires permanent delivery;
- a material evidence gap still conditions the answer;
- an unresolved scope or judgment choice changes the result;
- a bounded recommended action is ready and authority is the only blocker; or
- unfinished promised verification or execution remains.

Merely imaginable adjacent work outside the visible promise is not closure
debt. A complete factual answer is closed even though deeper analysis is
possible. A completed, verified, and committed change is closed when push or
publication was not requested. Do not use hypothetical downstream work to
manufacture a menu.

Treat repeated interpretation as a saturation signal. After two consecutive
navigation-only selections deepen the same objective, default to `saturated`
closure unless the latest turn introduces new evidence, resolves a material
contradiction, or exposes a genuinely new decision or action. Do not offer
options that merely analyze, rewrite, compare, or audit the answer just
produced. A completed reflection may remain meaningful without becoming a
journal candidate, identity proposition, or new analytical object.

If further work has lower expected value than stopping, closure is the
recommendation. When a real decision still exists and a footer is warranted,
the stop path may occupy the `recommended` role; include a separate
`pause-or-deepen` option only when it changes the commitment or depth rather
than duplicating that recommendation.

## Permanent-artifact handoff

For every substantial document, state exactly one persistence status:

- saved and verified, with a clickable path and privacy/status label;
- not saved, with one bounded save option and proposed permanent path; or
- intentionally conversational, with an explicit statement that no durable
  artifact was promised.

Before offering or executing a save, identify whether the destination is a
repository or private store, whether saving crosses a privacy or authority
boundary, and whether the action is limited to the exact path and content
named. Working-tree presence is distinct from repository admission, staging,
commit, push, and publication. A selected save option carries only its exact
bounded save scope when the action-ready contract is satisfied.

## End open branches with possibilities

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

Every possibility menu has an actionability floor: include at least one
actionable option whenever a safe bounded action can be made ready from the
current evidence. Do the reversible read-only scoping needed to identify its
exact action, target, and verification step instead of making the operator
repeat or reconstruct that scope. An action-ready option must be
composed and validated by `elicitation` as `decision-navigation`, with a
machine-checked `selection_effect` matching the label's first token. Only
`Execute`, `Commit`, `Push`, and `Send` can authorize the exact visible bounded
action through a letter selection. `Stage`, `Publish`, and `Deploy` require a
direct explicit command. A later explicit command supersedes a pending menu.
All existing authority, approval, privacy, tenant, lane, and safety rules
remain controlling.

Before choosing an ordinary footer or an Elicitation surface, classify every
option independently. If an exact action, target, and verification step are
ready, no material choice remains unresolved, and authority is the only
blocker, use a validated mixed `decision-navigation` surface and declare that
option in `action_readiness.ready_option_keys`. Other options may remain
navigational. Never replace the ready action with a request to inspect, settle, confirm,
adopt, or approve its already-bounded scope. For an all-navigation surface,
record the bounded `all_navigation_reason` and concrete `blocked_action` audit
required by Elicitation. Navigation-only is exceptional: it is valid only when
no safe action is bounded, a material human choice remains unresolved, or the
operator explicitly requested read-only work. A completed action closes the
branch; it is not a reason to manufacture another navigation-only menu.

Do not present consecutive navigation-only menus for the same objective. After
one navigation-only selection, the next response must deliver the developed
result and either include an actionable option, close the branch, or ask the
single factual question that blocks action readiness.

The universal possibility footer is not automatically an Elicitation surface.
Apply Elicitation's implicit-invocation gate independently. Only a
machine-validated `decision-navigation` surface with an explicit
`selection_effect` may carry Elicitation action authority.

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

Carry a selected branch through all reversible read-only investigation needed
to produce a meaningful result. Do not use a final response as a progress
checkpoint merely to generate another possibility menu. A later Elicitation
surface in the same objective requires a newly emerged blocker that passes its
full implicit-invocation gate.

Action-ready menu grammar: an option that authorizes a bounded action must
begin with the governing executable verb (`Execute`, `Commit`, `Push`, or
`Send`), followed immediately by the action and target. Put the stable role
label after that executable prefix; never present `Recommended — Execute ...`
when the selection is meant to authorize execution.

Negative example: `Patch both skills`, `Create tests`, or `Update the file` in
an ordinary footer remains navigation-only even when it sounds action-bearing.
Mutation authority through a selected letter requires the executable prefix and
a validated `selection_effect`; otherwise the branch can only be developed up to
the next authorization boundary.

Selection closure and idempotence: once a selected branch is confirmed,
paused, or otherwise settled, repeating the same stable selection is a no-op.
Acknowledge the settled state once and close the branch instead of regenerating
the same footer. Present a new possibility set only when a genuinely new
decision, scope, evidence gap, or action exists.

Branch closure takes precedence over continuation of the same branch. When no
genuinely new path exists, acknowledge closure without manufacturing another
possibility set. When distinct new paths do exist, label the completed branch
explicitly and present them under `New paths`; do not imply that they are
unfinished obligations from the closed work.

## Retain only a selection

Do not retain an unselected footer. When the operator selects a branch:

1. Reconstruct the exact displayed possibility set and its semantic roles.
2. Sanitize direct contact data and reject secrets or credentials.
3. If a private store is configured and has not already been cached as
   unavailable for the current task, run `choice select` atomically with the
   selected stable key, recommendation binding, lane/workspace/tenant scope,
   choice kind, consequence, summary, actor, timestamps, and bounded signals.
4. State that receipt retention granted no authority; any bounded action
   authority came only from the validated `selection_effect` paired with the
   governing visible option label.
5. If the store is missing or unavailable, continue navigation and disclose
   that the selection was not retained.

When the selected branch later settles, run `choice close` with reason
`completed`, `paused`, or `saturated`. Closure is lifecycle state, not an
outcome: it removes the branch from unresolved review without creating success,
cognitive-load, momentum, or discovery evidence. A later observed outcome may
resolve a closed branch. Do not close after an outcome has already resolved it,
and do not backfill historical selections from reconstructed memory.

Successful closure retention is routine internal process. Keep it quiet unless
retention fails, the lifecycle transition is invalid, or an authority, privacy,
safety, or lane incident must be surfaced.

Cache unavailability by resolved store path and relevant environment state for
the remainder of the task. Do not reopen the same unavailable store on every
selection, review, or context request. Retry only after the configured path,
credentials, permissions, environment, or other external state changes, or
when the operator explicitly requests another probe.

Configure private state only with an absolute path outside Git:

```powershell
$env:MIRA_CORE_CHOICE_DB = "C:\private\mira-core-choice-history.sqlite3"
.\tools\run.ps1 choice select ...
```

`choice select --options-json` expects a JSON array of three or four option
objects, not an object keyed by letter. Each option needs `key`, `role`, and
`text`:

```json
[
  {"key": "A", "role": "recommended", "text": "Reflect on the selected branch."},
  {"key": "B", "role": "alternative", "text": "Compare the adjacent branch."},
  {"key": "C", "role": "overlooked", "text": "Inspect the overlooked path."},
  {"key": "D", "role": "pause-or-deepen", "text": "Pause or return to the prior workflow."}
]
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

Measure cognitive load from contemporaneous friction rather than retrospective
operator memory. Do not ask the operator to reconstruct old workflow details
solely to fill the load field. Prefer artifact-side signals available during or
immediately after the workflow: clarification loops, reruns, corrections,
reopened branches, repeated scope restatement, user method correction, and
whether the final state reduced or increased next-step ambiguity.

Use this default cognitive-load rubric:

- `lower`: at most one clarification loop, no reopened branch, no operator
  correction of method, and the final state is clear enough to act or stop.
- `same`: the workflow completes but needs ordinary steering, one correction,
  or a modest clarification without derailing.
- `higher`: the workflow needs repeated prompts, operator memory
  reconstruction, branch reopening, a method correction, or leaves the operator
  doing extra bookkeeping.
- `Missing`: no contemporaneous or artifact-derived signal exists.

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

A turn has three valid terminal forms:

- an open branch ends with three or four real possibilities, one
  evidence-grounded recommendation, stable role bindings, a credible overlooked
  path when available, and no silent action authorization; or
- a settled branch ends with explicit closure followed by optional `New paths`
  when at least two independently eligible directions exist; or
- a settled conversation ends with explicit closure and no manufactured footer.

If a branch was selected, retain its exact sanitized menu atomically or
disclose the graceful unretained fallback. When that branch settles, retain
closure quietly when possible without inferring an outcome.

---
name: learn-from-choices
description: "Turn genuine user decisions into outcome-aware possibility maps and learn from explicitly selected branches without expanding action authority. Use for the compact contextual A-D surface required on every final response, when a material choice or bounded action remains, when a user replies with a menu letter, or when choice outcomes or staged five-to-ten reviews should be retained or examined."
---

# Learn From Choices

Use this core contract to classify every final response and render exactly one
compact contextual A-D surface at its end. Completed work can lead to substantive
next options or, after a separate assessment, transient response controls.
Do not apply choice footers to intermediate
commentary. Load lifecycle references only at their named trigger:

- After a user selects an offered branch, or when that selected branch closes,
  read [`references/choice-retention.md`](references/choice-retention.md).
- Before using retained outcomes to reorder choices, recording an outcome, or
  running five-to-ten review, read
  [`references/outcome-review.md`](references/outcome-review.md).

## Classify closure before navigation

Close completed actions, then independently identify useful next options.
Completion prevents repeating finished work; it does not withdraw meaningful
choices. Never infer the menu type from completion alone.

A branch is settled when its complete visible promise is delivered and no new
decision, evidence gap, scope change, or executable action remains. Run a
closure-debt audit before declaring settlement. Keep the branch open for:

- an unsaved substantial document;
- a material evidence gap;
- unresolved operator judgment that changes the result;
- a bounded recommended action awaiting only authority; or
- unfinished promised verification or execution.

Merely imaginable adjacent work is not closure debt. A complete factual answer
may close despite optional deeper analysis. A completed, verified commit may
close when push or publication was not requested.
Learn From Choices judges conversational and decision closure; domain
workflows own the evidence that proves domain-specific done-state.

Classify the wider conversation separately. Render a substantive terminal A-D
surface when at least one of these is true:

- a material decision remains;
- an exact bounded action is awaiting authority;
- independently credible new objectives begin genuinely different work; or
- the operator explicitly requested choices or structured navigation.

Otherwise use **compact settled closure**: deliver the result or acknowledgement
with exactly four contextual transient controls. This is the default for
completed factual answers, simple thanks or acknowledgements, explicit stops,
completed actions with no remaining boundary, repeated settled selections, and
saturated navigation-only branches. Settled controls retain nothing and create
no choice identity.

The validator separates two declarations:

- `closure_state: settled` describes the completed action only. It may accompany
  a decision menu offering a next bounded action, with ordinary readiness and
  authority checks intact.
- `surface_kind: response-controls` selects exactly four navigation-only,
  `learning_eligibility: none` controls. They carry no executable targets,
  action context, or authority. Omit action readiness or supply only
  `ready_option_keys: []`.

Either declaration requires a separate `next_option_assessment`: a nonempty
`basis` explaining the current situation and a `candidates` list. Each candidate
has `label`, `status`, and `reason`. Status is `ready`, `navigational`, `blocked`,
or `out-of-scope`. Ready and navigational candidates must bind an `option_key`
in the visible decision menu; generic response controls cannot hide them.
Blocked and out-of-scope candidates have no option key. An empty list is valid
for a simple acknowledgement or explicit stop; explain that in the basis rather
than inventing work. Missing authority alone does not make an otherwise ready
action blocked or out-of-scope. A blocked action may still warrant a useful
inspection or alternative, which should be assessed independently.

For completed repository edits, consider the exact staging/commit boundary
before choosing controls. Perform available read-only scoping first. After a
commit, assess useful next options separately; do not assume push authority or
reopen the completed commit. An explicit stop rules out continued work.

The validator checks supplied assessments for consistency; it cannot discover
omitted opportunities or prove the agent's judgment. An unchanged validated
response-control template may be reused within the session through the
compatibility class `elicitation.SettledControls`. A changed situation,
assessment, label, or classification requires fresh validation. Never persist
this cache, retain control selections, or enroll them in a choice-learning
cohort. Genuine decisions still require current targets, evidence, and selection
identity; direct instructions supersede earlier menus.

After closing a branch, offer substantive `New paths` only when independently
credible directions begin genuinely different objectives, evidence searches,
or commitments. Selecting one creates a new choice identity; it never reopens
the closed branch. When a real four-option surface has fewer than four honest
substantive paths, fill unused positions with transient response controls rather
than manufactured work.

When the operator explicitly requests navigation after an ordinary settled
response, these transient controls are available:

```text
A. Close — accept the result and close.
B. Correct — identify an error or mismatch.
C. Deepen — request more evidence or explanation within this objective.
D. New task — begin a distinct objective.
```

After an explicit stop, keep the response minimal and use only `Close now`,
`Return later`, `Start a new task`, and `Correct the stopping summary`. A
governing workflow's existing valid four-option A-D surface satisfies the
need; never append a duplicate menu. A smaller Coffee packet does not satisfy
this final-response requirement by itself.

## End every final response with possibilities

Use exactly four concise options. For an open branch, prefer materially distinct possibilities and
use transient response controls for positions that would otherwise be filler:

```text
Next best possibilities — reply A-D:
A. Recommended path — ...
B. Strong alternative — ...
C. Overlooked possibility — ...
D. Pause, deepen, or stop — ...

Recommendation: [one evidence-grounded sentence].
```

Bind letters in order to `recommended`, `alternative`, `overlooked`, and
`pause-or-deepen`. A transient control may occupy a role without becoming a
substantive recommendation.

Every open-branch menu must contain at least one actionable option whenever reversible
scoping can make a safe action exact. Perform that read-only scoping first. An
exact bounded action is ready when scope, target, and verification are known
and authority is the only blocker. Classify every decision option independently;
a decision surface may mix executable and navigational options. Declare ready
keys in `ready_option_keys` and use a validated mixed `decision-navigation`
surface. Do not replace a ready action with a request to settle, confirm, adopt,
or approve an already-bounded scope.

Task or thread creation is action-ready when the target project, initial prompt,
environment, and verification boundary are known. Present it as an executable
option such as `Execute: Create the bounded task ...`; do not label it
navigation-only and then require the operator to repeat the same command.

When a domain workflow establishes a durable batch authority envelope, continue
all reversible in-scope rows until its declared review boundary. Do not emit an
intermediate choice surface for routine row completion, isolated row failure,
unchanged constraints, or every single item in a batch. This prevents approval
fatigue while preserving real authority boundaries.

For consecutive execution chains, keep the operator's selected branch moving
through read-only checks, validation, receipts, and reversible preparation until
the next real authority boundary. After an executable selection, do not present
another A-D menu merely to restate the same action, confirm an already-bounded
scope, or ask whether to perform a validation step that the visible option
already implied. Present the next surface only when the workflow reaches a new
mutation class such as staging, commit, push, publication, deployment, external
communication, or another independently meaningful objective.

A durable batch envelope exists only when the visible option or direct command
names the workflow, target set, allowed actions, stop boundary, and forbidden
actions. Inside that envelope, the agent may inspect, classify, draft,
reconcile, and report all in-scope rows without asking the operator to approve
each row. The agent must still stop or surface a fresh decision when any of
these changes:

- the batch needs a new mutation class such as registry mutation, body
  admission, staging, commit, push, publication, deployment, external
  communication, spending, or private Archive ingestion;
- the target set, destination, evidence source, rights posture, or privacy
  boundary changes materially;
- validation fails in a way that changes the operator's decision;
- the batch discovers a scope conflict, contradiction, protected data issue, or
  previously forbidden action; or
- the declared review boundary is reached.

For long library, archive, repository, or research workflows, prefer larger
reviewable batches over one-item loops when the operator has asked for scale or
has complained about approval friction. Batch-scale continuation does not
broaden authority: the same forbidden actions remain forbidden, and the final
receipt must state what was completed, deferred, rejected, blocked, and not
attempted.

Outside settled controls, an all-navigation surface is exceptional: provide `all_navigation_reason` and
a concrete `blocked_action` naming the action considered, its blocker, and
what would make it ready. Do not present consecutive navigation-only menus for
the same objective. A later Elicitation surface requires a newly emerged
blocker.

Mark every normalized decision option with `learning_eligibility: eligible |
none`. Material choices about objective, evidence, method, scope, or a bounded
action are `eligible`. Generic Close, Correct, Deepen, New task, stop, and
return-later controls are `none`. Eligibility is independent of
`selection_effect` and grants no action authority.

When a terminal surface is rendered, validate it with `final_response: true`.
This requires four options and explicit eligibility for each one. Three-option
Elicitation surfaces remain valid only for non-final backward-compatible
interactions.

## Preserve action authority

A bare letter enters and develops the selected branch. It authorizes mutation
only when all of these are true:

1. the visible option begins with `Execute`, `Stage`, `Commit`, `Push`, or `Send`;
2. the complete bounded action and target are visible;
3. Elicitation validates the decision-navigation surface; and
4. its machine-checked `selection_effect` matches the visible verb.

Put the stable role after the executable prefix. Labels such as `Patch both
skills`, `Create tests`, or `Update the file` remain navigation-only.
`Stage` is valid only for exact scoped staging where the complete path or hunk
boundary is visible and validated. Broad staging, `Publish`, and `Deploy`
always require a direct explicit command.

Discussion, retention, recommendation, or selection alone never authorizes
execution, spending, publication, communication, customer action, commit,
push, deployment, or another consequential boundary. A later explicit command
supersedes a pending menu.

Carry a selected branch through all reversible read-only investigation needed
to produce a meaningful result. Do not stop at a progress checkpoint merely to
generate another menu. If consequential authority is still required, ask only
for the minimal confirmation at the exact action point and preserve the
selected scope.

## Preserve selection identity

Treat a letter as the complete visible option, not a request for the operator
to restate it. Once a branch is confirmed, paused, or settled, repeating the
same selection is a no-op. Acknowledge closure once and do not regenerate the
same substantive menu. Reuse unchanged transient settled controls when needed
for the four-option footer. Present a new choice only for genuinely new evidence, scope,
decision, or action.

Treat comma-separated letters such as `B,C` as an ordered compound selection
when every selected branch is present in the current surface. Preserve the
order as operator intent: the first branch is the first requested path, and
later branches are additional selected paths, not discarded preferences.
Compound selection does not widen action authority; each branch keeps its own
validated `selection_effect`, retention eligibility, readiness, and execution
boundary. A `pause-or-deepen` branch is exclusive and cannot be combined with
another branch. Treat ranked syntax such as `A>C>B` as read-only preference
evidence, not branch selection or action authority.

Create or refresh the silent interaction-context capsule whenever presenting a
validated decision surface. Resolve a compact response only against the
current digest-bound capsule. Retire the capsule when the branch closes or a
direct later command supersedes it; a response bound to an older option set
requires one minimal clarification. The capsule is conversational and
transient: do not save it to the choice ledger, infer preferences from it, or
display it routinely.
If capsule state is stale, unavailable, or multiply plausible, ask the minimal
clarifying question instead of reconstructing authority from memory.

Visible option text is the portable authority surface. Private capsules and
retention records may improve continuity, but safety must not depend on them
being present or model-readable.

If the operator asks where the options are, or otherwise signals that the
expected menu was omitted, repair the interaction immediately: name the missing
surface, provide exactly four current options if a real decision remains, and
avoid making the operator reconstruct the prior branch from memory. Treat this
as a presentation failure, not as new authority.

After two consecutive navigation-only selections deepen the same objective,
default to compact saturated closure unless the latest turn adds new evidence,
resolves a material contradiction, or exposes a genuinely new decision or
action. Render only contextual transient controls; do not offer another
substantive menu that merely analyzes, rewrites, compares, or audits the result
just delivered.

This two-selection rule controls repeated navigation-only deepening. The
Elicitation three-compact-selection rule is a separate upper bound for mixed
compact sequences: it requires carrying the selected branch to a meaningful
result and then using compact settled closure, not manufacturing another
substantive decision surface. Apply the earlier bound whenever both describe
the same sequence.

## Deliver permanent artifacts honestly

For a substantial document, state exactly one persistence status:

- saved and verified, with clickable path and privacy/status label;
- not saved, with one bounded save option and proposed permanent path; or
- intentionally conversational, with explicit notice that no durable artifact
  was promised.

Before saving, identify the destination, privacy boundary, and exact content.
Working-tree presence is distinct from repository admission, staging, commit,
push, hosting, and publication. Never describe a working-tree file as public.

## Complete the turn

A turn has four valid terminal forms:

- an open branch with a genuine decision ends with a valid four-option surface;
- a settled branch with independently credible new work may end with eligible
  `New paths` plus transient fillers;
- a settled or stopped conversation closes with compact contextual transient controls; or
- a governing workflow supplies its own validated interaction surface.

When a selected branch closes, use the retention reference to append a quiet
`branch_closed` lifecycle event when available. Closure is not outcome evidence.
Surface only retention failure, invalid lifecycle transition, or a material
authority, privacy, safety, or lane incident.

## Keep Options Specific

For active artifact, repository, archive, library, publication, or governed
workflow branches, do not fall back to the generic `Close`, `Correct`, `Deepen`,
and `New task` controls while concrete next decisions remain. Name the real
next boundaries instead: verify, inspect, correct metadata, admit the next
bounded batch, stage and commit, push, clean private duplicates, or pause. Use
generic response controls only when the work is genuinely settled or when fewer
than four honest work-specific choices exist.

When a final response reports changed files, admitted records, commits, private
payloads, or validation results, at least two options should preserve the
actual operational shape of the branch. Avoid menus that force the operator to
translate a real next action back out of generic conversational labels.

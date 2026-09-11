---
name: learn-from-choices
description: "Turn genuine user decisions into outcome-aware possibility maps and learn from explicitly selected branches without expanding action authority. Use when a genuine decision needs optional structured navigation, when a material choice or bounded action remains, when a user replies with a menu letter, or when choice outcomes or staged five-to-ten reviews should be retained or examined."
---

# Learn From Choices

Use this core contract for material decisions and explicitly requested
directions. Menus are decision-only, not automatic endings. Completed answers
and actions finish plainly unless a material decision remains or the operator
requests directions. A single blocking question needs no artificial alternatives.
When a menu is warranted, offer two to four meaningful options with a reasoned
recommendation and concrete benefits. Preserve requested brainstorming, reading
suggestions, and relevant workflow-owned choices. Direct follow-ups remain welcome.
Keep simple thanks, acknowledgements and explicit stops quiet, without menu
validation, capsules or retention events. Do not apply choice footers to
intermediate commentary. Load lifecycle references only at their named trigger:

- After a user selects an offered branch, or when that selected branch closes,
  read [`references/choice-retention.md`](references/choice-retention.md).
- Before using retained outcomes to reorder choices, recording an outcome, or
  running five-to-ten review, read [`references/outcome-review.md`](references/outcome-review.md).

## Classify closure before navigation

Close completed actions and identify any material decision still required for
the requested objective. Optional adjacent work alone does not justify a menu.

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
- an exact bounded action within the requested objective is awaiting authority;
- the operator explicitly requested choices or structured navigation.

Use **compact settled closure** for simple thanks or acknowledgements, explicit
stops, repeated settled selections, and saturated navigation-only branches:
respond in ordinary prose without a menu or associated validation/retention.
For completed factual answers and completed actions, close quietly unless a
material decision remains or directions were explicitly requested. Mere
availability of another clarification or adjacent task is not such a decision.

The validator separates two declarations:

- `closure_state: settled` describes the completed action only. It may accompany
  a decision menu offering a next bounded action, with ordinary readiness and
  authority checks intact.
- `surface_kind: response-controls` selects two to four explicitly requested navigation-only,
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

For completed repository edits, assess a staging/commit boundary only when it
belongs to the requested endpoint or the operator asks for publication advice.
Perform available read-only scoping before offering that decision. Do not assume
push authority or reopen a completed commit. An explicit stop rules out continued work.

The validator checks supplied assessments for consistency; it cannot discover
omitted opportunities or prove the agent's judgment. An unchanged validated
response-control template may be reused within the session through the
compatibility class `elicitation.SettledControls`. A changed situation,
assessment, label, or classification requires fresh validation. Never persist
this cache, retain control selections, or enroll them in a choice-learning
cohort. Genuine decisions still require current targets, evidence, and selection
identity; direct instructions supersede earlier menus.

Classify the meaning of each visible option before encoding it. An empty
`candidates` list cannot accompany independently meaningful new work merely
because that work is optional. Validation checks supplied structure and
consistency, not the truth of the agent's semantic classification.

For example, "Explain that distinction again, so that I can follow the answer"
is a generic clarification control (`none`). "Compare the two voices using
contrary passages, so that agreement can be tested against exceptions" selects
an evidence method (`eligible`): represent it as a navigational candidate in a
decision surface, with the ordinary readiness assessment. Likewise, "Clarify
the example, so that its meaning is clear" is a control; "Design a matched-task
experiment, so that competing capability claims face the same measurement"
opens substantive work and must not be encoded as a response control. Neither
navigational label authorizes experiment execution or persistence.

Review these distinctions using `references/decision-fixtures.json` when
auditing choice classification. Preserve the existing exact-input rules for
settled-control reuse: a changed label, assessment, or classification requires
fresh validation. Reuse does not permit semantic caching or skipped validation.

After closing a branch, offer substantive `New paths` only when the operator
requests directions or a material decision remains. Selecting one creates a
new choice identity; it never reopens the closed branch. Do not manufacture
options; one ready action may be paired with genuine deferral.

When the operator explicitly requests navigation after an ordinary settled
response, these transient controls are available:

```text
A. Close — accept the result and close.
B. Correct — identify an error or mismatch.
C. Deepen — request more evidence or explanation within this objective.
D. New task — begin a distinct objective.
```

After an explicit stop, acknowledge once and stop without a menu. Workflow-owned menus retain their own contracts; never append a duplicate menu.

## Offer choices when they serve a decision

Use menus for material unresolved decisions or explicitly requested directions.
Recommend one evidence-grounded path first; include alternatives only when the
tradeoff is real or the operator requests them. Two to four meaningful options
are sufficient. Do not turn routine authorized continuation into another choice.
Keep the benefit of each option concrete, without expanding its authority.

Bind letters in presentation order. Put `recommended` first; other roles must
be unique and meaningful. Neither `overlooked` nor `pause-or-deepen` is mandatory.

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
This requires two to four options and explicit eligibility for each one.

Validate the exact visible surface before presentation, not after selection.

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
for an unsolicited footer. Present a new choice only for genuinely new evidence, scope,
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
surface, provide two to four current options if a real decision remains, and
avoid making the operator reconstruct the prior branch from memory. Treat this
as a presentation failure, not as new authority.

After two consecutive navigation-only selections, or three compact selections
within the same inquiry, complete the authorized work, synthesize, and pause
automatic menus. Apply the earlier bound whenever both describe the same sequence.
An inquiry is its governing question or intended outcome. A new artifact,
revised simulation, counter-reading, or audit within that inquiry does not reset
the count. Use existing transient conversation context only; introduce no
navigation ledger or persistent counter.

Resume menus only when the operator requests further directions, explicitly
starts a distinct objective, or a newly emerged blocker requires a decision.
An assistant-generated follow-up suggestion cannot reset the limit. New evidence
alone is not a reset. A genuine blocker remains actionable through the narrowest
decision needed; it does not renew automatic follow-up menus.

Pausing menus never interrupts authorized work or overrides a direct command.
Preserve executable-option validation and separate publication authority.
Conversational synthesis, silence, and selections do not fabricate shared-reading
interpretation or Library Journal closure.

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

- an open branch with a genuine decision may use a validated two-to-four-option surface;
- a settled branch may offer eligible `New paths` when the operator requests
  directions or a material decision remains;
- a settled conversation without a material decision or requested directions, or an explicit stop,
  closes in ordinary prose without a menu; or
- a governing workflow supplies its own validated interaction surface.

When a selected branch closes, use the retention reference to append a quiet
`branch_closed` lifecycle event when available. Closure is not outcome evidence.
Surface only retention failure, invalid lifecycle transition, or a material
authority, privacy, safety, or lane incident.

## Keep Options Specific

Every presented option must be a two-part sentence: state the choice first,
then explain why choosing it might be beneficial in this situation. Use a
connector such as `because`, `so that`, `in order to`, or `due to the fact
that`; prefer the shortest natural wording. This applies to executable
options, navigation, and transient settled controls, including options derived
from the compact examples elsewhere in this contract. Expand those role
sketches into contextual sentences before presenting and validating them.

The second part must name a concrete benefit, tradeoff, or preserved boundary,
not repeat the action or say merely that it is useful. For example:
`Inspect the failing archive check, because its cause determines whether the
skill changes can be committed independently.` Keep uncertain benefits
conditional rather than promising an unverified outcome. Preserve any required
executable prefix and exact scope; a rationale grants no additional authority.
Treat difficulty explaining an option's usefulness simply as evidence that
the option may not deserve a place. If no distinct benefit can be stated
honestly, reconsider the option instead of manufacturing a reason or
re-offering a completed closure.

### Requested exploration

When the operator asks for possibilities, explore grounded connections,
discriminating experiments, and ways to remove recurring constraints. Explain
the concrete benefit and distinguish hypotheses from ready actions. Do not
perform this search merely to produce an unsolicited ending. Novelty supplies
neither evidence nor execution authority.

For active artifact, repository, archive, library, publication, or governed
workflow branches, do not fall back to the generic `Close`, `Correct`, `Deepen`,
and `New task` controls while concrete next decisions remain. Name the real
next boundaries instead: verify, inspect, correct metadata, admit the next
bounded batch, stage and commit, push, clean private duplicates, or pause. Use
generic response controls only when explicitly requested. Simple acknowledgements and stops end quietly; substantive work receives
choices only for a material decision or explicitly requested directions.

When an optional menu follows changed files, admitted records, commits, private
payloads, or validation results, its choices should preserve the
actual operational shape of the branch. Avoid menus that force the operator to
translate a real next action back out of generic conversational labels.

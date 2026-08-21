---
name: learn-from-choices
description: "Turn genuine user decisions into outcome-aware possibility maps and learn from explicitly selected branches without expanding action authority. Use when a material choice or bounded action remains, when a user replies with a menu letter, or when choice outcomes or staged five-to-ten reviews should be retained or examined; settled responses may close silently."
---

# Learn From Choices

Use this core contract to classify every final response, but render a choice
surface only when a genuine decision or action boundary remains. Settled
responses may close silently. Do not apply choice footers to intermediate
commentary. Load lifecycle references only at their named trigger:

- After a user selects an offered branch, or when that selected branch closes,
  read [`references/choice-retention.md`](references/choice-retention.md).
- Before using retained outcomes to reorder choices, recording an outcome, or
  running five-to-ten review, read
  [`references/outcome-review.md`](references/outcome-review.md).

## Classify closure before navigation

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

Classify the wider conversation separately. Render a terminal A-D surface only
when at least one of these is true:

- a material decision remains;
- an exact bounded action is awaiting authority;
- independently credible new objectives begin genuinely different work; or
- the operator explicitly requested choices or structured navigation.

Otherwise use **silent settled closure**: deliver the result or acknowledgement
without an appended menu. This is the default for completed factual answers,
simple thanks or acknowledgements, explicit stops, completed actions with no
remaining boundary, repeated settled selections, and saturated navigation-only
branches. Silent closure retains nothing and creates no choice identity.

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

After an explicit stop, stop silently unless the operator requested navigation.
If navigation was requested, use only `Close now`, `Return later`, `Start a new
task`, and `Correct the stopping summary`. A governing workflow's existing
four-action A-D surface, including Coffee, satisfies the need; never append a
duplicate menu.

## End an open branch with possibilities

When a terminal surface is warranted, use exactly four concise options. Prefer materially distinct possibilities and
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
or unchanged constraints.

An all-navigation surface is exceptional: provide `all_navigation_reason` and
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
interactions. Silent settled closure has no surface to validate.

## Preserve action authority

A bare letter enters and develops the selected branch. It authorizes mutation
only when all of these are true:

1. the visible option begins with `Execute`, `Commit`, `Push`, or `Send`;
2. the complete bounded action and target are visible;
3. Elicitation validates the decision-navigation surface; and
4. its machine-checked `selection_effect` matches the visible verb.

Put the stable role after the executable prefix. Labels such as `Patch both
skills`, `Create tests`, or `Update the file` remain navigation-only.
`Stage`, `Publish`, and `Deploy` always require a direct explicit command.

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
same menu. Present a new choice only for genuinely new evidence, scope,
decision, or action.

After two consecutive navigation-only selections deepen the same objective,
default to silent saturated closure unless the latest turn adds new evidence,
resolves a material contradiction, or exposes a genuinely new decision or
action. Do not offer another substantive or transient menu that merely
analyzes, rewrites, compares, or audits the result just delivered.

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
- a settled or stopped conversation closes silently; or
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

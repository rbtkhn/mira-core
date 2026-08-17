---
name: learn-from-choices
description: "Turn final user-facing responses into outcome-aware possibility maps and learn from explicitly selected branches without expanding action authority. Use implicitly for every final response, when a user replies with a menu letter, and when choice outcomes or staged five-to-ten reviews should be retained or examined."
---

# Learn From Choices

Use this core contract for every final response. Do not apply its footer to
intermediate commentary. Load lifecycle references only at their named trigger:

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

Classify the wider conversation separately. After closing a branch, offer
`New paths` only when at least two independently credible directions begin
genuinely different objectives, evidence searches, or commitments. Selecting
one creates a new choice identity; it never reopens the closed branch. Suppress
the footer after an explicit stop, when saturation applies, when no credible
paths exist, or when the options would be manufactured busywork.

## End an open branch with possibilities

Use three or four concise, materially distinct possibilities:

```text
Next best possibilities — reply A-D:
A. Recommended path — ...
B. Strong alternative — ...
C. Overlooked possibility — ...
D. Pause, deepen, or stop — ...

Recommendation: [one evidence-grounded sentence].
```

Bind letters in order to `recommended`, `alternative`, `overlooked`, and
`pause-or-deepen`. Omit a fourth option rather than fabricate diversity.

Every menu must contain at least one actionable option whenever reversible
scoping can make a safe action exact. Perform that read-only scoping first. An
exact bounded action is ready when scope, target, and verification are known
and authority is the only blocker. Classify every decision option independently;
a decision surface may mix executable and navigational options. Declare ready
keys in `ready_option_keys` and use a validated mixed `decision-navigation`
surface. Do not replace a ready action with a request to settle, confirm, adopt,
or approve an already-bounded scope.

An all-navigation surface is exceptional: provide `all_navigation_reason` and
a concrete `blocked_action` naming the action considered, its blocker, and
what would make it ready. Do not present consecutive navigation-only menus for
the same objective. A later Elicitation surface requires a newly emerged
blocker.

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
default to saturated closure unless the latest turn adds new evidence, resolves
a material contradiction, or exposes a genuinely new decision or action. Do
not offer options that merely analyze, rewrite, compare, or audit the result
just delivered.

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

A turn has three valid terminal forms:

- an open branch ends with a valid possibility surface;
- a settled branch closes and may offer independently eligible `New paths`; or
- a settled conversation closes without a manufactured footer.

When a selected branch closes, use the retention reference to append a quiet
`branch_closed` lifecycle event when available. Closure is not outcome evidence.
Surface only retention failure, invalid lifecycle transition, or a material
authority, privacy, safety, or lane incident.

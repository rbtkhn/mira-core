# Concern Card Template

Use a concern card for work that is bigger than one prompt but not stable
enough to become a governed skill. It is a repository-local planning artifact:
it helps another agent or future session understand the concern, but it does
not grant authority to act.

Recommended storage:

- One-off or experimental cards: `docs/work-journal/`.
- Reusable workflow-owned cards: the owning skill's `references/` directory.

Concern cards are not canonical memory, source evidence, journal continuity,
recursive-learning outcomes, archive objects, publication artifacts, staging
plans, commits, pushes, deployments, or external-communication authority.

```text
Concern card:
Title:
Status: draft | active-advisory | superseded
Owner:
Created:
Last reviewed:

Objective:
Audience or stakeholder:
Why this is bigger than a prompt:
Current scope:
Out of scope:

Context carriers:
Trusted instruction sources:
Supplied inputs:
Observed inputs:
Inferred inputs:
Missing or stale inputs:
Private or sensitive exclusions:

Authority boundary:
Actions allowed without further approval:
Actions requiring explicit approval:
Forbidden actions:
Repository, account, or external-system boundary:

Shared-state record:
Primary state file, receipt, queue, or ledger:
Last known state:
Next agent should read first:
Re-entry point:

Permissions and connections:
Tools, plugins, browsers, remotes, or APIs:
Credential exposure:
Account-context assumptions:
Fallback when unavailable:

Verification surface:
What observable state proves progress:
What observable state proves completion:
Trust curve:
Known failure signals:
Cheapest sufficient validation:

Cadence:
One-time, recurring, monitor, or operating rhythm:
When to stay quiet:
When to notify or surface a decision:
Next-run handoff:

Failure behavior:
Recoverable failures:
Fail-closed conditions:
Retry threshold:
Rollback or stop path:

Human decision points:
Choices reserved for the operator:
Judgment-bearing tradeoffs:
Review checkpoint:

Promotion criteria:
Repeated triggers observed:
Stable boundaries observed:
Stable receipts observed:
Stable validation needs observed:
Candidate full skill: yes | no | later
Reason:
```

## Optional Inquiry return point

For an inquiry that needs a useful return point, include one concise account in
the existing card rather than another record. Omit irrelevant fields and replace
overlapping summary prose instead of repeating it; separate obligations remain
in their existing sections.

```text
Inquiry return point:
Question and why it matters:
Current interpretation and qualification:
Decisive source or artifact references:
Material correction or strongest unresolved objection:
Remaining uncertainty and what would change the judgment:
Next useful step and outstanding authority:
```

Lead with the question and its significance, attributed to Robert's expressed
words or an interpretation he explicitly accepted. Silence, continued conversation,
and Mira's enthusiasm do not establish shared recognition. Omit missing or disputed
shared meaning. Keep corrections, uncertainty, references, and authority distinct.
An inquiry may have **no action pending**; omit a next step when none is agreed.
Genuine obligations remain in their existing sections. Shared recognition makes
an inquiry eligible only when preservation is already authorized, not a save trigger.

This optional prose adds no schema or persistence trigger. Keep the card's
existing preservation boundary; do not backfill historical cards or save one
merely because a conversation was substantial. Unknown context remains unknown.

The trust curve names how close the concern is to safe delegation. A concern is
more delegable when its output is externally checkable, its failures are
recoverable, its permissions are narrow, and its authority boundaries are
explicit. High intelligence does not move a concern up the curve by itself.

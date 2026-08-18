# Outcome Learning and Review

Read this reference before recording outcomes, using retained history to order
choices, or running staged five-to-ten review.

## Record outcomes conservatively

Use `choice outcome` only for observed dimensions:

- result: `successful`, `mixed`, `unsuccessful`, `no_action`, or
  `not_observable`;
- cognitive load: `lower`, `same`, `higher`, or `Missing`;
- momentum: `advanced`, `neutral`, `stalled`, or `Missing`;
- discovery: `new-useful-path`, `confirmed-known-path`, `not-useful`, or
  `Missing`.

Praise may support result but not unobserved dimensions. Measure cognitive load
from contemporaneous friction: clarification loops, reruns, corrections,
reopened branches, repeated scope restatement, and remaining bookkeeping.
Classify it as lower for at most one clarification and no rework; same for
ordinary steering or one correction; higher for repeated steering, reopened
work, method correction, or extra bookkeeping; otherwise `Missing`.

Supply the exact retained tenant, canonical workspace, operational lane, and
cohort disposition to `choice outcome`; a choice ID alone is insufficient. Use
`--review-cohort COHORT` for an enrolled selection or the explicit
`--no-review-cohort` flag for a legacy or unenrolled selection. Keep
`mira-core-natural-use-v1` prospective and limited to consequential natural-use
tasks. Never backfill its membership or outcomes from memory, completion,
praise, or passing tests.

Use the separate `menu-contract-natural-use-v1` cohort for the first five later
natural uses of learning-eligible universal-menu decisions. Generic response
controls never enter this cohort. Require 100 percent A-D coverage across the
five sampled final responses, zero retained transient controls, zero compressed-
selection authority incidents, and at least three observations for every
primary measure before interpreting performance. Preserve `Missing` and
`not_observable` honestly.

This prospective review may supply later outcome evidence for a Recursive Learn
assessment, but selection frequency, implementation, passing tests, and menu
coverage alone do not close a feedback loop. Create a bounded process reference
only after the five-use review. Recursive-learning assessment and canonical
ledger admission remain separate governed actions.

Use `choice due --review-cohort mira-core-natural-use-v1 --limit 1 --json` to
find at most one closed candidate after the observation delay. A due candidate
is not an observable outcome. Record `not_observable` with honest `Missing`
dimensions only when a later review needs that disposition; otherwise wait for
bounded post-action evidence. Use `choice health` for content-free lifecycle,
coverage, timestamp, scope-variant, and cohort-progress diagnostics.
On schema versions below v4, cohort-backed read-only commands return
`migration-required`; they do not migrate or imitate an empty cohort. The next
authorized writable choice operation may perform the existing schema migration.
Health may report content-free legacy null-cohort and path-shaped workspace
counts, but it never merges or rewrites those identities.

Use `corrected` and `superseded` events instead of rewriting history. Use
`review_deferred` when an unresolved outcome returns through review.

## Learn from outcomes, not popularity

Read `choice context` before using retained history. One or two comparable
outcomes are thin evidence and do not reorder recommendations. After at least
three comparable resolved outcomes, two consistent results without material
contradiction may influence ordering. Never use selection frequency. Preserve
a credible overlooked path, isolate tenant and workspace learning, and require
an explicit review cohort before measurement crosses operational lanes.
Require sanitized operator-approved promotion across cohorts. Never promote repository
doctrine automatically.

## Review through coffee

Route unresolved outcomes and staged review through `coffee`. Evaluate resolved,
non-superseded selections in selection order:

- fewer than five eligible choices: `pending`;
- at five: assess the earliest five;
- if any primary dimension has fewer than three observations, freeze an
  extension until ten eligible outcomes exist;
- at ten: assess the cumulative earliest ten and exclude later choices.

Use projection version `2.0` for review and `1.0` for choice, context,
unavailable, and verification projections. Report cohort stage, target,
eligible and remaining counts, choice IDs, observation gaps, incident sources,
result distribution, rework, repeated negative experiences, and confirmation
that selection frequency was excluded.

Apply incidents first: any authority, privacy, safety, or lane incident yields
`hold`. Otherwise use `pending` below five, `extend-to-ten` for an incomplete
pilot, terminal `adjust` at ten if a primary dimension remains underobserved,
`adjust` for at least two negative experiences, `continue` when at least two
primary signals pass, and `adjust` otherwise.

Signals are: three favorable lower-load observations, three favorable advanced
momentum observations, and one `new-useful-path`. The scorecard is descriptive
pilot evidence and remains separate from the comparable-outcome recommendation
threshold. Closeout workflows such as `dream` must not solicit unresolved
outcomes.

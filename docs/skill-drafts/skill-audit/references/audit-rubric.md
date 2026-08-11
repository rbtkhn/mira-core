# Skill Audit Rubric

Use this reference only while auditing a skill. Keep audit reports concise and
evidence-bound.

## Severity

- `P0`: the skill can authorize unsafe mutation, publication, external action,
  spending, private disclosure, evidence admission, or claim verification.
- `P1`: the skill is likely to produce wrong work, route to the wrong workflow,
  or hide a required authority boundary.
- `P2`: the skill will create recurring friction, rework, drift, or unclear
  operator decisions.
- `P3`: the skill has maintainability, wording, fixture, or polish issues that
  do not materially affect safe use.

## Frontmatter Checklist

- `name` is lowercase hyphen-case and matches the folder.
- `description` includes what the skill does and specific trigger contexts.
- `description` distinguishes near-neighbor workflows when confusion is likely.
- Frontmatter avoids body-only trigger details that Codex cannot see before
  activation.

## Authority Checklist

Check whether the skill clearly handles:

- file edits and generated artifacts;
- staging, commit, push, deploy, and publication;
- source admission, archive repair, verification, forecast resolution, and
  canonical ledger changes;
- external browsing, API calls, spending, customer or public communication;
- private data, secrets, and operator identity or continuity claims.

If the skill can touch any of these, the authorization boundary should be
explicit and local to the relevant step.

## Progressive Disclosure Checklist

- `SKILL.md` carries the core workflow and boundaries.
- References are one level away and loaded only for named audit needs.
- Scripts are preferred for fragile repeated validation.
- Examples are concise and serve behavior, not documentation clutter.
- No README, changelog, installation guide, or broad background file is needed
  inside the skill folder.

## Benchmark Case Template

Use this compact shape:

```text
Case: normal | edge | failure | ambiguous
Prompt:
Resources to load:
Expected behavior:
Forbidden behavior:
Pass/fail check:
Residual risk:
```

Prefer four high-signal cases over a large suite. Add more only when the skill
has multiple materially different modes.

Prose fixtures can be enough. A human-reviewed fixture set is benchmark-worthy
when it records protected meaning, pass conditions, failure modes, and the
intended judgment standard. Recommend JSONL indexes, scoring fields, or
deterministic harnesses only when they would reduce repeated review cost,
catch likely regressions, or support before/after comparison across revisions.

## Verdict Guide

- `pass`: no material findings; any gaps are optional polish.
- `pass-with-warnings`: safe to use, but at least one P2/P3 issue should be
  tracked.
- `needs-revision`: at least one P1 or multiple P2 issues make recurring
  failure likely.
- `unsafe-to-use`: a P0 issue or authority ambiguity could cause harmful
  mutation, publication, exposure, or evidence misuse.

## Repair Plan Rules

Recommend the smallest safe change first. Separate:

- wording fixes;
- trigger/frontmatter fixes;
- reference extraction;
- fixture or benchmark additions;
- deterministic script work;
- validation or forward-testing.

Never treat an audit recommendation as authority to edit, stage, commit, push,
publish, or synchronize a skill.

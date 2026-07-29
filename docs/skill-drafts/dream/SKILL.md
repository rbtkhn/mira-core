---
name: dream
description: "Close a Narrative Systems session by verifying the repository and persisting one advisory learning handoff. Use when the operator says dream or requests an end-of-session recursive improvement handoff."
---

# Dream

Use only in `narrative-systems`. Dream records advisory cadence state, never
research evidence.

## Distill

Identify exactly one bounded experiment from the session and classify its
outcome as `improved`, `no_change`, `regressed`, or `inconclusive`. State:

- the experiment;
- one evidence-backed lesson;
- one candidate method change;
- a bounded evidence summary containing the decisive counts or observations;
- one or more repo-relative artifact references supporting the summary;
- one sentence describing what tomorrow inherits.

Do not call a change `improved` merely because tests pass. It must improve a
named judgment, quality, reliability, or efficiency criterion.
Do not solicit or record unresolved choice outcomes during closeout. Route
them through the next `coffee` re-entry instead.

## Verify and persist

Run:

```text
tools/run.ps1 cadence dream --experiment TEXT --outcome OUTCOME --lesson TEXT --improvement TEXT --evidence-summary TEXT --artifact-ref PATH --tomorrow-inherits TEXT --json
```

For a profiled experiment, add `--profile PROFILE`. The persisted handoff keeps
experiment-scoped verification separate from repository-wide verification;
local-use eligibility never grants repo-use or public-use.
Structured verification results must retain the raw output tail and identify an
owner and next action for every non-passing result.

Repeat `--artifact-ref` when needed. The command rejects missing, absolute, or
repository-escaping references, runs repository integrity and tests through one
resolved validation interpreter, then writes the ignored local
`work/cadence/last-dream.json`. Failed or unavailable verification is recorded,
reported, and leaves the lesson blocked.

## Return

Report the experiment, outcome, verification status, Git state, candidate
improvement, and `Tomorrow inherits:` sentence. Never infer permission to
stage, commit, push, publish, change forecasts, or run intake.

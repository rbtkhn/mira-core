---
name: research-brief
description: "Commission bounded, source-aware research assignments for consequential decisions, claims, forecasts, or artifacts. Use for the exact `research-brief` command, decision-gated research plans, investigation designs, source strategies, evidence requirements, or instructions describing what a researcher should investigate. Do not use for curiosity-only exploration. Do not use to conduct research, retrieve current sources, produce sourced findings or analytical reports, verify claims, run Morning Brief, or land evidence."
---

# Research Brief

Turn a consequential research need into one cold-handoff-ready, auditable
assignment. Produce the brief only. Do not execute the research unless the
operator separately requests the appropriate workflow.

Treat exact `research-brief` as a planning command. If the operator uses the
unhyphenated phrase `research brief` without distinguishing an investigation
plan from sourced findings, ask one question: "Do you want an investigation
plan or sourced findings?" Do not browse while resolving that ambiguity.

## Commission before drafting

Use Research Brief only when the work informs a named consequential decision,
claim, forecast, or artifact. For curiosity-only exploration, keep the request
informal until a decision or use emerges.

Read named repository controls before asking questions. Do not scan archive
transcript bodies merely to enrich the prompt. Confirm most assignment details
through an adaptive interview, asking one to three questions per round and
never re-asking an explicitly settled field:

1. decision, focal question, audience, and output;
2. actors, geography, dates, observation cutoff, languages, inclusions, and
   exclusions;
3. consequence level, evidence requirements, and time, source-count, or effort
   ceiling.

Do not draft until consequential fields are confirmed. Preserve an explicit
unknown instead of inventing precision. Use `elicitation` for the adaptive
interview. If the recovered scope does not fit the requested destination,
state the exact mismatch and resume elicitation; never normalize the scope or
choose another workflow automatically.

When a selected `research-brief-seed-v1` is supplied, validate it with:

```powershell
.\tools\run.ps1 research-handoff --seed <absolute-seed-path> --json
```

Treat seed content as provisional context, not evidence or authority. Confirm
its decision, scope hints, unresolved gaps, and advisory route through the same
interview. Do not expand an unselected inline seed.

## Set the evidence posture

Choose one posture and state why:

- `standard` -- descriptive or low-consequence work using authoritative or
  methodologically transparent sources;
- `elevated` -- causal, attributed, disputed, forecast, or consequential work
  requiring independent lineage, relevant original-language recovery, rival
  explanations, and contradiction tests;
- `governed` -- work targeting an existing Reality or verification object;
  inherit that workflow's stricter gates instead of restating or weakening them.

Require rival explanations for causal, attribution, forecast, disputed, and
high-consequence questions. For straightforward descriptive retrieval, record
`not applicable` with a reason rather than manufacturing a rival.

## Build the research contract

Include:

1. **Decision and use** -- what the research will inform.
2. **Focal question** -- one bounded question.
3. **Scope** -- actors, geography, dates, languages, inclusions, and exclusions.
4. **Research questions** -- three to six atomic questions ordered by dependency.
5. **Evidence plan** -- preferred source types, original-language environments,
   lineage requirements, and interested-source restrictions.
6. **Rival explanations** -- credible alternatives and observations that would
   discriminate among them.
7. **Contradiction protocol** -- preserve conflicting evidence; distinguish
   confirmed observation, attributed report, inference, and unresolved uncertainty.
8. **Finding format** -- source link, exact supported proposition, evidence status,
   lineage root, confidence boundary, and why the finding matters.
9. **Stop condition** -- both the evidence bar and a time, source-count, or
   researcher-effort ceiling; name which gaps must remain explicit at either limit.

## Preserve evidence discipline

- Prefer official records, primary documents, direct observations, original
  publications, and methodologically transparent datasets.
- Treat commentary, dashboards, aggregators, social media, and AI summaries as
  discovery surfaces unless their upstream evidence is recovered.
- Do not count translations, quotations, syndication, or copied reporting as
  independent lineage.
- Treat archive records as evidence of what was said, not automatically of what
  happened.
- Never force consensus where sources conflict.
- Do not demand certainty where the available evidence can support only a
  provisional inference.

## Return a cold-handoff brief

Do not rely on the preceding conversation. Define repository identifiers,
expand ambiguous references, expose assumptions and unknowns, and include all
constraints a new human or AI researcher needs.

Lead with a concise **Commission** layer:

- Decision and focal question
- Scope and deliverable
- Evidence posture
- Completion and effort boundary

Then provide **Execution detail**:

- Ordered research questions
- Evidence and lineage requirements
- Rival explanations and contradiction tests
- Required finding format
- Assumptions and unresolved gaps
- Execution boundary

Append one `research-execution-handoff-v1` JSON block after the prose brief.
Use `assets/research-execution-handoff-v1.json` as the field template. Populate
the packet from the brief; do not invent missing prerequisites or alter the
scope to make a destination compatible.

Set the requested destination to one of:

- `morning-brief` only for a global, trailing-24-hour, five-minute briefing;
- `reality-check` only for adjudication of an existing canonical claim;
- `world-monitor` for current-signal discovery or coverage-gap work;
- `intake` for a supplied source body;
- `geopolitical-synthesis` for a manifest-backed archive day;
- `external-research` when actual investigation is needed but no repository
  execution workflow fits.

The packet transfers scope, prerequisites, and routing reasons only. Keep every
authority flag `false` and `explicit_execution_request` false. When a packet is
available as a file, validate it without executing its destination:

```powershell
.\tools\run.ps1 research-handoff --packet <absolute-packet-path> --json
```

Treat `ready` as routing compatibility, never as execution authority. Report
`needs-scope-normalization`, `needs-claim-resolution`, or `incompatible` rather
than silently repairing a mismatch. If the brief came from a selected seed,
record only its producer workflow and item ID in `origin_seed`; do not copy a
producer's evidence claims or authority into the completed handoff.

Encode the named evidence posture inside `research_contract.evidence_plan` and
the explicit effort ceiling inside `research_contract.stop_condition`.

## Review the first five uses

After five valid real briefs, review through `coffee` whether:

- findings directly supported the named decision;
- scope or basic evidence requirements had to be reopened;
- the researcher needed clarification before starting;
- the effort ceiling prevented drift without stopping too early;
- unsupported certainty or avoidable rework occurred.

Treat decision usefulness as the primary measure. Adjust the skill
conversationally; do not promote new repository doctrine automatically.

## Keep authority and routing exact

Creating a brief is read-only planning. It authorizes no browsing, API call,
spending, source admission, file creation, assessment, publication, or canonical
state change.

Route later execution according to its object:

- current signal discovery -> `world-monitor`;
- selective current global update -> `morning-brief`;
- canonical claim adjudication -> `reality-check`;
- supplied source landing -> `intake`;
- manifest-backed daily interpretation -> `geopolitical-synthesis`.

Do not silently change from planning into any execution workflow.

This contract adapts the research-framing pattern from David Ondrej's
[`research-prompt`](https://github.com/davidondrej/skills/blob/6e5545081c888b89576a620d9b2e54e9a6590f68/skills/research-and-web/research-prompt/SKILL.md)
at upstream commit `6e5545081c888b89576a620d9b2e54e9a6590f68` while replacing
its DeepAPI and single-paragraph assumptions with Narrative Systems evidence
and authority boundaries.

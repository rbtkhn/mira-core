---
name: geo-strategy
description: "Archive-backed Geo-Strategy for bounded crisis-object judgment, mechanism comparison, actor constraints, forecasts, decision implications, and validated daily packets. Use for manifest-backed geopolitical daily or retrospective strategy work after intake has landed."
preferred_activation: geo-strategy
portable: false
version: 0.2.1
category: narrative-geopolitics
status: active
---

# Geo-Strategy

Use after intake has landed or when deepening an existing retrospective run.
This skill turns source material into bounded strategic judgment; it does not
provide operational advice or independently verify public facts.

## Strategic Promise

- archive-backed strategic analysis;
- bounded crisis-object and mechanism judgment;
- actor incentive and constraint mapping;
- forecast and watch implications;
- decision-relevant uncertainty compression.

Do not use this skill to assign military tasks, resolve forecasts, publish,
communicate externally, browse automatically, or perform reality adjudication.

## Core Law

Read in this order:

```text
archive -> voices/channels -> work/daily
```

This skill does not replace `archive-intake` and never creates a daily directory
for a date without manifest rows.

## Daily Contract

Canonical:

- `sources.md`
- `synthesis.md`
- `forecast.md`
- `daily-brief.md`

Generated after the canonical files are issue-ready:

- `issue.md`

Generated only by a separate live-research experiment when explicitly requested:

- `narrative-geopolitics/work/morning-brief/YYYY-MM-DD.md`

There is no tracked session receipt or placeholder-day state.

## Entrypoint

```powershell
.\tools\run.ps1 synthesis --date YYYY-MM-DD
.\tools\run.ps1 synthesis --date YYYY-MM-DD --execute
```

Month and range modes process only dates with manifest rows. The deprecated
`--scaffold-empty` flag reports skipped dates and writes nothing.

## Guided Menu

- `A` bootstrap or refresh the run;
- `B` reconcile intake coverage and routing;
- `C` deepen the owning crisis object and report exception-only operational-claim triage;
- `D` sharpen forecast hooks and report their `OPC-*` dependencies;
- `E` execute the full stack.

## Density Triage

After validation and before deepening, use archive density as a review guide.
The guided menu and cadence startup may surface archive-audit benchmark
advisories directly. When more detail is needed, run a range or day check:

```powershell
.\tools\run.ps1 archive-audit --start-date YYYY-MM-DD --end-date YYYY-MM-DD --format markdown
```

Use [archive audit and density](../../../narrative-geopolitics/method/archive-density.md)
rules this way:

- thin days: check overclaim risk, hook necessity, and caveat language;
- dense days: check voice triangulation, issue selection, and held-story logic;
- `very_dense` overlay days: treat dense-day review as mandatory before
  deepening;
- `OPC-*` days: prioritize verification review, but do not assign operational truth;
- carried-hook days: avoid duplicate forecasts unless a new wager is genuinely created.
- provisional routing warnings: treat as landing-time enrichment debt unless a
  separate repair-candidate warning is present.
- repair-candidate warnings: favor reconciliation before deepening.

## Source-Anchor Coverage

Use a variable source-anchor target rather than a hard 40-anchor minimum:

- require at least one valid `SRC-*` anchor for every landed source included in
  the Run Source Set;
- target 2–3 anchors per major mechanism or theme;
- treat approximately 24–30 anchors as a normal full-day working ceiling unless
  the material supports more distinct, non-redundant points;
- use 40 anchors only for unusually dense or multi-theater batches, and only
  when each additional anchor has a distinct analytic job.

Anchors support source traceability; they do not independently corroborate a
claim or convert source assertion into reality-check evidence.

The daily-run validator performs advisory checks for minimum source coverage,
partial quote coverage, repeated load-bearing quotes, and unusually high anchor
counts. These checks warn for review; they do not replace source judgment or
block a justified dense-batch exception.

## Guardrails

- Require exact manifest coverage in the Intake Batch before synthesis.
- Permit a documented Run Source Set subset.
- Treat retrospective forecasts as retrospective unless timing proves otherwise.
- For a newly created retrospective packet, require a completed
  `Synthesis contract: delta-v1` Distinctive Contribution: comparison window,
  new mechanism/evidence/contradiction, and disposition. If there is no
  substantive delta, keep the intake archive-only and do not create a daily
  packet.
- Keep `daily-brief.md` internal until intentionally promoted.
- Treat `morning-brief` as a local, opt-in current-signal experiment with a
  frozen research receipt. It may compare provisional observations with recent
  judgments and accountable open forecasts, but it does not revise this daily
  contract, create a daily synthesis, or require a manifest batch for the brief
  date.
- Keep `issue.md` internal reader-facing; generation is not publication.
- Declare issue membership in the synthesis `Issue Story Desk`; require matching `Issue Copy` in `daily-brief.md` and regenerate rather than hand-editing `issue.md`.
- Do not revive the old `public-brief.md` contract.
- Do not alter private intake behavior.
- Do not browse, create verification packets, or assign operational truth automatically.
- Print an explicit packet-request command for `request` rows; operator action remains required.
- Permit bounded internal synthesis with unresolved claims. Block high-consequence public factual use and accountable forecast resolution until packet requirements are met.
- Reject orphan `OPC-*` rows: every retained claim must control planned public factual use, watch promotion, or a forecast dependency.

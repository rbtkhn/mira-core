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

## Sustainable Cadence

Compose with
[`narrative-geopolitics/method/sustainable-cadence.md`](../../../narrative-geopolitics/method/sustainable-cadence.md)
when daily workload is in view. The default daily invariant is `15 minutes` of
capture-only source continuity, not a daily packet. Transcript capture is toil;
archive intake is governed source truth; synthesis is judgment.

Do not treat a missed day, a captured-only day, or an unlanded transcript queue
as a mandate to manufacture `geo-strategy`. Full packets are twice-weekly by
default or threshold-driven when landed material creates a substantive delta.
Missed capture days route to weekly catch-up.

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

## Choice Acceleration Policy

Use a geo-strategy option engine for follow-up menus after an archive-backed
issue, day, or crisis object is in view. The visible user surface remains
exactly four `A`-`D` options, but those options are selected from a larger
internal library of 10-20 next-best epistemic moves. Optimize for faster
judgment formation, not faster prose: every visible option must improve
evidence, mechanism clarity, uncertainty handling, forecast leverage, or an
explicit hold.

Rank candidate moves in this order:

1. crisis consequence;
2. evidence gap;
3. verification need;
4. forecast leverage;
5. decision readiness.

Prefer a concrete next workflow over generic continuation language. Do not
surface vague `continue`, `deepen`, or `explore more` options unless the label
names the exact object and the missing judgment job. If all four options would
be navigation-only, collapse the surface to the narrowest concrete workflow
available now and state the blocked action.

Internal move library:

- intake coverage audit;
- same-object voice comparison;
- mechanism spine extraction;
- competing mechanism test;
- operational-claim triage;
- reality-check handoff;
- original-language source search;
- forecast-hook extraction;
- counterevidence pass;
- actor constraint map;
- escalation ladder map;
- decision implication compression;
- public-use boundary;
- daily packet build;
- verification packet draft;
- pause/hold with explicit unresolved gate.

Project the selected moves onto the four-option visible surface this way:

- `A` highest-confidence next action;
- `B` correction, coverage repair, or missing-foundation action;
- `C` deepening move with the best judgment leverage;
- `D` alternate object, explicit hold, verification/publication boundary, or
  packet-disposition move.

Compose with `learn-from-choices` without weakening it. Generic final-response
controls remain `learning_eligibility: none`. Only action-ready options whose
visible label begins with an executable verb may carry selection authority.
`Stage`, `Commit`, `Push`, `Publish`, `Deploy`, `Send`, canonical verification
admission, and external communication require direct explicit operator
commands. This policy does not grant authority to browse, create verification
packets, admit `OPC-*`/`CLM-*`/`NG-*` records, publish, or assign operational
truth.

Use the Aug. 18, 2026 Iran-Hormuz issue as the first live calibration case for
this policy: when operational claims control public factual use, route factual
adjudication through external-knowledge `reality-check` rather than treating
archive testimony as verified fact.

## Guided Menu

The legacy five-option menu is deprecated. For new geo-strategy work, apply the
Choice Acceleration Policy and return exactly four `A`-`D` options.

## Density Triage

After validation and before deepening, use archive density as a review guide.
The guided menu and cadence startup may surface archive-audit benchmark
advisories directly. When more detail is needed, run a range or day check:

```powershell
.\tools\run.ps1 archive-audit --start-date YYYY-MM-DD --end-date YYYY-MM-DD --format markdown
```

For dense or voice-heavy days, optionally surface same-day multi-channel
triangulation candidates:

```powershell
.\tools\run.ps1 triangulation-candidates --start-date YYYY-MM-DD --end-date YYYY-MM-DD --format markdown
```

Use the output as an advisory prompt to compare invariant voice claims against
host pressure fields. It is not evidence, verification, a mandatory synthesis
gate, or a routing repair signal.

## Current-Day Issue Scan

Before answering an issue-focused question after multiple same-day intakes,
scan the full manifest-backed source set for that date unless the operator
explicitly narrows the scope. This applies to prompts such as `focus on X`,
`what did [voice] say`, `check all today's transcripts`, and issue questions
that arrive after fresh intake has landed for the date.

Use:

```powershell
.\tools\run.ps1 source-topic-scan --date YYYY-MM-DD --query "topic terms" --format markdown
```

Treat the scan as retrieval coverage only. It does not verify claims, promote
issue membership, create a daily synthesis, or override source judgment.

Use [archive audit and density](../../../narrative-geopolitics/method/archive-density.md)
rules this way:

- thin days: check overclaim risk, hook necessity, and caveat language;
- dense days: check voice triangulation, same-day multi-channel candidates,
  issue selection, and held-story logic;
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

## Mira Library Historical Pressure-Test Pilot

Use `library-reasoning` only when a historical mechanism, institutional
lineage, analogy, or credible rival could materially change the crisis-object
judgment. Before settling the mechanism, run its metadata-only pre-scan. After
stating a provisional mechanism, create at most one bounded private packet and
adjudicate every candidate as `adopted`, `narrowed`, `redirected`, `rejected`,
or `held`.

Keep `SRC-*` and `LIB-*` evidence lanes separate. Library material may sharpen
causal mechanisms, principal alternatives, falsifiers, and sequencing. It may
not satisfy manifest coverage, corroborate a current operating fact, resolve
an `OPC-*` or forecast, or supply statistical base rates. Shared textual or
intellectual ancestry is not independent convergence.

For adopted material, name the shared mechanism, decisive structural
difference, concept non-equivalence, rejection condition, representation gap,
and actual effect on judgment. If no material effect survives, reject or hold
the analogy rather than decorating the synthesis with history. During the
pilot, Mira Voice consumes only adjudicated material and does not reopen
retrieval.

Private routing observations may affect later candidate selection only after
the `library-reasoning` proposal and explicit activation boundary. They never
alter Geo-Strategy dispositions, current-event evidence status, or the
provisional mechanism automatically.

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

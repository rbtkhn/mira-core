---
name: world-monitor
description: "Use World Monitor as a read-only sensing and candidate-generation interface for Narrative Systems. Trigger for `world-monitor`, current global-signal scans, geographic or domain monitoring, source-freshness and visibility-gap audits, candidate multi-stream correlations, or a bounded handoff into Narrative Geopolitics. Never treat World Monitor briefs, scores, forecasts, or correlations as evidence or forecast resolution."
---

# World Monitor

Use World Monitor to discover dated signals and visibility gaps. Treat every
World Monitor artifact as a lead or interpretation until its upstream source
and evidence lineage are recovered independently.

## Establish scope

Before retrieval, state:

- mode: `scan`, `gaps`, `correlate`, or `handoff`;
- observation window and retrieval time;
- geography and domain;
- requested output and stop condition.

Default to a read-only scan. Do not broaden a named geography, time window, or
domain merely because the dashboard exposes adjacent signals.

Prefer a callable official World Monitor MCP, REST/OpenAPI, or CLI interface.
If none is available, use official World Monitor pages and documentation. For
current signals, retrieve live state rather than relying on remembered feature
or source lists.

## Preserve the observation contract

For every retained signal, record:

- retrieval time and reported observation time;
- World Monitor tool, endpoint, or page;
- signal type and geography;
- displayed freshness, cache, stale, or gap state;
- upstream provider and source URL when exposed;
- the narrow observation, separated from interpretation;
- known shared lineage or dependency;
- disposition: `candidate`, `hold`, `excluded`, or `intake-ready`.

Never describe separately displayed streams as independent merely because
their data types differ. News velocity, market movement, alerts, and map events
may all descend from one report or event. Count independence only after tracing
lineage roots.

## Run the selected mode

### `scan`

Identify changes inside the declared scope. Return:

1. material candidate observations;
2. what changed and relative to which baseline;
3. source freshness and visibility gaps;
4. upstream links still requiring resolution;
5. a bounded next action.

Do not turn a busy dashboard into a claim that the world itself became more
unstable.

### `gaps`

Report stale, failed, missing, disabled, or geographically thin coverage.
Distinguish:

- absence of an event;
- absence of reporting;
- unavailable upstream data;
- stale cached state;
- a source outside World Monitor's coverage.

Explain which downstream observations or scores each gap weakens. Do not infer
stability from silence.

### `correlate`

Treat correlation as a candidate question, not corroboration. Name:

- the focal proposition;
- each signal and its time;
- recovered lineage roots;
- shared providers, reporting, or model dependencies;
- plausible rival explanations;
- what observation would discriminate among them.

Do not call convergence Analysis of Competing Hypotheses unless explicit rival
hypotheses, diagnostic evidence, inconsistency testing, and sensitivity to
deception have actually been supplied.

### `handoff`

Produce a compact candidate packet containing the observation-contract fields,
the bounded claim it may motivate, unresolved source work, independence limits,
and the recommended Narrative Systems destination.

For a retained candidate whose upstream source has been recovered but which
still needs source recovery, independence testing, or rival-mechanism
discrimination, include one inline `research-brief-seed-v1` using the template
at `../research-brief/assets/research-brief-seed-v1.json`. Give the seed a
producer-scoped candidate ID, bounded source references, provisional scope
hints, unresolved gaps, rival hints, identifiers, and an advisory route. Keep
every authority flag false. Do not include compatibility, disposition, a
completed research contract, or execution intent. Expand the seed only after
operator selection.

Do not seed ordinary scans, excluded or held items, unrecovered dashboard
signals, or `intake-ready` material with no unresolved research question.

Route only after upstream recovery:

- source material or attributed commentary -> archive-first intake;
- a manifest-backed day's analytical question -> geopolitical synthesis;
- an operational factual claim -> reality-check candidate;
- a prospective indicator -> forecast proposal, never automatic registration;
- historical material -> Historical Entropy candidate queue, never evidence.

If no substantive, source-recoverable contribution remains, disposition the
item `excluded` or `hold` instead of creating a packet.

## Authority boundaries

- World Monitor is not historical or geopolitical evidence by itself.
- AI briefs, Country Instability Index values, strategic-risk scores, scenario
  forecasts, and correlation findings are interpretations.
- Outlet tiers do not establish claim-level reliability.
- Cached panels with different refresh times do not form one observation time.
- Hard-coded baselines and conflict zones are model priors, not discoveries.
- Never resolve a forecast, assess an operational claim, admit a source, or
  publish from a World Monitor signal alone.
- Never write intake, forecast, verification, or synthesis state without
  explicit operator authorization.

End with the retained candidates, observed gaps, epistemic limits, and one
recommended next bounded action.

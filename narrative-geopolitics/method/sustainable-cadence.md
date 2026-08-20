# Sustainable Geo-Strategy Cadence

Status: `internal-workflow-contract`

This contract keeps Narrative Geopolitics alive when the operator has limited
daily time. The daily invariant is source continuity, not daily synthesis.

## Cadence Law

Default daily budget: `15 minutes`.

Required daily freshness: `capture-only`.

Default packet cadence: `twice-weekly`.

Missed capture days: `weekly-catch-up`.

Automation boundary: `queue-drafts-only`.

The ordinary day is successful when candidate sources are captured and triaged.
It is not a failure when no `geo-strategy` packet, forecast work, Reality
record, public artifact, or morning brief is created.

## Workload Tiers

### Daily Floor

Use this when time is scarce. Record candidate sources only:

- URL;
- title, channel, and publication date when available;
- expected voice or `unknown`;
- transcript status: `available`, `missing`, `manual-needed`, or `defer`;
- quick disposition: `must-land`, `possible`, `skip`, or `watch`;
- next action and short notes.

Stop after the capture queue is updated or after 15 minutes, whichever comes
first. Do not repair missed days during the next daily floor unless the
operator explicitly chooses catch-up.

### Packet Days

Run full `geo-strategy` no more than twice weekly by default. Packet days use
landed archive material, not raw queue entries. A packet may synthesize multiple
captured days when the manifest-backed material forms one coherent crisis
object.

If the source batch adds no substantive delta, keep the disposition
`archive-only` and do not manufacture a daily packet.

### Weekly Catch-Up

Use one bounded block to recover missed capture days and unresolved transcript
gaps. Catch-up may:

- review queued URLs;
- mark missing transcripts;
- select `must-land` items for governed intake;
- drop stale or duplicate candidates;
- identify which date range is ready for the next packet day.

Catch-up does not auto-land sources, create daily packets, resolve forecasts,
or publish.

### Optional Deepening

Use only on explicit operator request:

- Reality Check investigations or assessments;
- operational verification packets;
- forecast resolution;
- public promotion;
- morning-brief current-signal scans;
- automation beyond queue drafts.

These are consequence-bearing follow-ons, not daily obligations.

## Daily Capture Checklist

Use this lightweight row format for capture queues:

| Date | URL | Source / Channel | Expected Voice | Transcript Status | Priority | Next Action | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `YYYY-MM-DD` |  |  |  | `available` / `missing` / `manual-needed` / `defer` | `must-land` / `possible` / `skip` / `watch` |  |  |

`must-land` means the item is likely important enough for governed intake.
It does not authorize intake by itself. `watch` means preserve the lead without
claiming the source belongs in the next packet.

## Automation Boundary

Transcript capture is toil. Intake is governed source truth. Synthesis is
judgment.

V1 automation may prepare queue drafts from trusted watch surfaces, including
YouTube metadata and transcript availability checks. It must not:

- auto-land archive source bodies;
- alter the source manifest;
- create or edit daily packets;
- register, update, or resolve forecast hooks;
- create Reality or verification records;
- publish, stage, commit, push, deploy, or communicate externally.

Implemented v1 command: `.\tools\run.ps1 youtube-capture`.

Expected behavior:

- read a configured watchlist of channels or URLs;
- collect operator-provided video metadata and transcript availability;
- write draft queue rows for operator review;
- mark transcript failures explicitly;
- leave all archive landing and synthesis decisions to separate authorized
  workflows.

V1 is intentionally queue-local and does not fetch transcripts or call YouTube.
Transcript retrieval can be added later as an explicit private-cache option
without changing the archive authority boundary.

Workflow insight: Hannah proposed using the browser as a YouTube workflow aid.
That exposed the lower-risk no-login path: use the existing channel index as
the capture roster, and reserve browser assistance for explicit public-page
checks rather than account-dependent discovery.

## Scenario Rules

- Ordinary busy day: update capture rows only.
- Missed day: defer recovery to weekly catch-up.
- High-signal source: mark `must-land`; intake still requires the governed
  `intake` route.
- Packet day: synthesize only manifest-backed source material.
- No-delta batch: retain `archive-only`; do not create a formulaic packet.

## Weekly ROI Counter

Use this once per week during catch-up or packet planning. The counter exists
to prove whether the sustainable cadence is reducing workload while preserving
source continuity. Do not turn it into a daily obligation.

Default old-workload baseline: `300 minutes/week` (`60 minutes/day` for five
daily geo-strategy attempts). Override this only when the operator supplies a
better observed baseline.

Template:

| Week | Capture Days | Packet Days | Minutes Spent | Manual Transcript Minutes Avoided | Missed-Day Recoveries | Time Saved | Reliability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `YYYY-Www` | `0/5` | `0/2` | `0m` | `0m` | `0` | `baseline - spent` | `capture days / intended days` |

Interpretation:

- If time saved is at least `60 minutes/week` and reliability is at least
  `80%`, keep the cadence.
- If reliability improves but time saved is low, keep v1 and improve transcript
  automation before increasing packet expectations.
- If reliability stays below `70%`, reduce packet expectations before adding
  more automation.
- If measurement overhead exceeds `5 minutes/week`, simplify the counter
  rather than expanding it.

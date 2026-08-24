---
name: dream
description: "Consolidate one local day of mira-core sessions into a private advisory learning handoff. Use when the operator says dream or requests a daily recursive-improvement rollup."
---

# Dream

Use only in `mira-core`. Bare `dream` is the daily-close conductor. Before it
opens or resumes the private daily-close ledger, it performs a read-only
prerequisite gate for the selected date: Geo-Strategy must have a validated,
committed issue packet (or an honest `no_geo_run` result), and Mira Journal
must already be finalized or have a current, fully validated private bundle.
When both are complete, Dream continues automatically. When either is
incomplete, Dream pauses without preparing, composing, or mutating either lane
and asks the operator whether to finish the named missing work first.
Run one canonical Dream consolidation per operator, workspace, and local
calendar day. Individual sessions contribute bounded closeout receipts; Dream
consolidates all sessions active that day. Dream records advisory cadence state
in the configured private append-only ledger, never research evidence. It does
not overwrite prior episodes.

## Distill

Start or resume the conductor with:

```text
tools/run.ps1 dream --date YYYY-MM-DD --json
tools/run.ps1 dream --resume DCR-ID --date YYYY-MM-DD --json
```

Use `--check` for a read-only readiness projection. Completed stages are
immutable. When the date's Geo-Strategy packet already exists, passes
`validate_daily_run --stage issue`, and has either been committed or explicitly
accepted by the operator, Dream certifies the Geo-Strategy stage as complete
from those receipts. It must not regenerate, reinterpret, or revise the packet
unless the operator explicitly requests a Geo-Strategy revision. The
certification names the packet date, validation stage, artifact refs, and commit
or acceptance basis. A date without manifest-backed Geo sources records
`no_geo_run`; a failed evidence-backed Geo packet blocks Journal. Dream may
certify a fully validated `dream-eod-v1` journal bundle without an operator
approval record, but it must not canonicalize, approve, or publish the entry.
The receipt preserves both version digests, records `canonicalized: false`, and
leaves `approval_status: pending`. When the tool returns a composition handoff,
complete the prepared private bundle and resume. Finish
with a private `--dream-json` candidate or `--no-candidate REASON`.

The prerequisite prompt grants no authority to complete either lane. If the
operator says yes, invoke the owning Geo-Strategy or Mira Journal workflow for
only the missing date-bound work, then rerun Dream; do not continue the Dream
ledger from an incomplete preflight.

Before inheriting a Geo-Strategy prerequisite, run a read-only freshness gate
over `narrative-geopolitics/work/daily`. If any later substantive Geo packet
exists after the prerequisite date, mark the prerequisite `needs-refresh` unless
the owning bundle was rerun after that later packet. For due forecast hooks
surfaced by the latest Geo packet, split debt into `verification-required`,
`posture-review`, and `not-yet-due`:

- `verification-required`: resolution depends on an operational claim, `OPC-*`,
  `VER-*`, or contested source assertion.
- `posture-review`: resolution depends on public, official, or later-archive
  posture signals and no operational-claim dependency is admitted.
- `not-yet-due`: the hook is open but outside the current review boundary.

Dream may inherit only when the Geo prerequisite is `current`, no due
`verification-required` hook is silently treated as resolved without an
assessed packet, and any `posture-review` debt is either resolved or explicitly
bracketed as unresolved. Report the gate in this compact form:

```text
geo_prerequisite_status: current | needs-refresh | blocked-by-verification | open-but-bracketed
due_forecast_debt: verification=N posture_review=N not_yet_due=N
safe_to_inherit: yes | no
next_action: rerun-owning-bundle | open-verification-packet | posture-review | proceed
```

Inventory the day's active sessions first. Give every known session an explicit
`included`, `excluded`, or `unavailable` coverage receipt with a reason and
observation time. Mark the rollup `partial` whenever any session is unavailable;
missing coverage is visible and never treated as evidence that no work occurred.

Identify exactly one bounded experiment from the consolidated day and classify its
outcome as `improved`, `no_change`, `regressed`, or `inconclusive`. State:

- the experiment;
- one evidence-backed lesson;
- one candidate method change;
- a bounded evidence summary containing the decisive counts or observations;
- one or more repo-relative artifact references supporting the summary;
- one sentence describing what tomorrow inherits.

Also state a stable experiment-series and episode ID, narrow observation and
diagnosis, proposed-intervention digest, observable with
unit/baseline/threshold/source, falsifier, intended next-use task class,
timezone-aware expiry, claimed artifact relationships, and relevant paths. If
no meaningful experiment occurred, record `no_cadence_worthy_experiment`
without manufacturing a candidate.

The corresponding low-level receipt is `cadence dream-closeout`; it records a
daily closeout without creating a candidate episode.

The daily key is `(workspace_id, operator_id, dream_date)` in the named IANA
timezone. Repeating an identical command is idempotent. A second canonical
Dream for that key fails closed. A failed or interrupted run may resume through
its idempotency key. Late session receipts require a separately authorized
append-only supplement or explicit supersession; never rewrite the daily body.

Append a late receipt with:

```text
tools/run.ps1 cadence dream-supplement --episode-id ID --session-coverage-json JSON --idempotency-key KEY --expected-version VERSION
```

Do not call a change `improved` merely because tests pass. It must improve a
named judgment, quality, reliability, or efficiency criterion.
Journal certification records completion only. Canonical approval remains a
separate exact digest-bound Mira Journal action; certification never mutates
the journal registry, canonical prose, technical-reference companions, or
continuity indexes.

Do not solicit or record unresolved choice outcomes during closeout. Route
them through the next `coffee` re-entry instead.

## Verify and persist

Run:

```text
tools/run.ps1 cadence dream --workspace-id ID --operator-id ID --dream-date YYYY-MM-DD --timezone IANA_NAME --coverage-status complete|partial --session-coverage-json JSON --series-id ID --episode-id ID --experiment TEXT --outcome OUTCOME --lesson TEXT --observation TEXT --diagnosis TEXT --improvement TEXT --method-version-digest SHA256 --expected-observable TEXT --observable-unit TEXT --observable-baseline TEXT --success-threshold TEXT --observation-source TEXT --falsifier TEXT --next-use TEXT --task-class TEXT --expires-at RFC3339 --evidence-summary TEXT --artifact-ref PATH --tomorrow-inherits TEXT --idempotency-key KEY --json
```

For a profiled experiment, add `--profile PROFILE` and provide an externally
preflighted root through `--temp-root ABSOLUTE_PATH` or
`MIRA_CORE_SESSION_TEMP_ROOT`. Dream persists before the profile begins and
again after it finishes. A passing profile may grant local-use eligibility;
Dream never runs repository-wide verification automatically. An unprofiled
Dream is persisted as advisory state with local-use and repo-use blocked.
Structured verification results must retain the raw output tail and identify an
owner and next action for every non-passing result.

Repeat `--artifact-ref` when needed. The command rejects missing, absolute, or
repository-escaping references and requires `MIRA_CORE_CADENCE_DB` or `--db`
to resolve to an absolute private path outside Git. Legacy schema-v2/v3
handoffs remain explicitly importable for one compatibility release, but Dream
no longer writes `last-dream.json`. Failed, unavailable, timed-out, or
interrupted profile verification is retained without erasing the candidate.

Promote repository use only through the separate explicit command:

```text
tools/run.ps1 cadence promote --temp-root ABSOLUTE_PATH --json
```

Promotion uses the content-addressed full-validation cache when valid. Use
`--force` only when a fresh structural and pytest run is intentionally required.
Local-use eligibility never grants repo-use or public-use.

## Return

Report the experiment, outcome, verification status, Git state, candidate
improvement, and `Tomorrow inherits:` sentence. Never infer permission to
stage, commit, push, publish, change forecasts, or run intake.

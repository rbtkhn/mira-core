# June Backfill Demo Sequence

> Historical demonstration receipt. The one-off `demo_daily_runs.py` runner was
> retired after the June backfill; the preserved commands below document how the
> artifacts were reviewed, not a current executable interface.

Thesis:

> June is now a reviewable judgment month, not just a stored archive month.

Use this sequence in two ways:

- `Core path: 5 minutes`
- `Expansion path: 10-15 minutes`
- `Async reader path: run top to bottom`

## Core Demo 1: Executive Opener And Month Completeness

Goal: establish the headline in one command.

Command:

```text
C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/demo_daily_runs.py --month 2026-06 --mode executive-summary
```

Then, if needed:

```text
C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/demo_daily_runs.py --month 2026-06 --mode month-summary
```

What to say:

- June now has 30 real run days.
- Sparse and dense archive days both became usable judgments.
- The month now carries a forecast/review spine, not just archived transcripts.

## Core Demo 2: Sparse vs Dense Robustness

Goal: prove the workflow survives both a thin packet and a crowded packet.

Command:

```text
C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/demo_daily_runs.py --month 2026-06 --mode day-compare --day-a 2026-06-21 --day-b 2026-06-08
```

What to say:

- `2026-06-21` only had 2 source rows but still became a real run.
- `2026-06-08` had 15 source rows and was narrowed into one crisis object.
- The system does not require equal archive density to produce a daily judgment.

## Core Demo 3: One Contract Across Retrospective, Live, And Placeholder

Goal: prove June backfill and July live operation belong to the same system.

Commands:

```text
C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/validate_daily_run.py --date 2026-06-30
```

```text
C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/validate_daily_run.py --date 2026-07-08
```

```text
C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/validate_daily_run.py --date 2026-07-10
```

What to say:

- June 30 validates as a retrospective real run.
- July 8 validates as a live real run.
- July 10 validates as an intentional placeholder with a non-fatal warning.
- One workflow now supports all three states cleanly.

## Optional Expansion 1: Forecast Review Spine

Goal: show future follow-up utility.

Command:

```text
C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/demo_daily_runs.py --month 2026-06 --mode hook-review
```

What to say:

- June now contributes a reviewable hook spine into July.
- The backfill created operational follow-up, not just historical notes.

## Optional Expansion 2: Crisis-Sequence Map

Goal: show month-sequence utility.

Command:

```text
C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/demo_daily_runs.py --month 2026-06 --mode crisis-map
```

What to say:

- Every June day now exposes row count, hook count, and crisis object.
- This makes June usable for later monthly reviews or crisis atlases.

## Close

Use this sentence to end the demo:

> The value is not that we created lots of files. The value is that we turned archive mass into a reviewable analytical surface.

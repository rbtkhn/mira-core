# June 2026 Narrative Geopolitics Archive Audit

Run date: `2026-07-16`

Audit range: `2026-06-01` through `2026-06-30`

Audit status: `complete`

Audit type: `full-range-audit`

## Executive Evaluation

Overall rating: `structurally-complete-but-not-issue-ready`

June 2026 is structurally broad and coherent enough for archive-bounded retrospective review, but it is not yet complete under the current July daily issue standard. Every June day has manifest rows, every June day has a daily directory, and every June day has the four canonical files: `sources.md`, `synthesis.md`, `forecast.md`, and `daily-brief.md`. No June day currently has generated `issue.md`, and no June synthesis/daily-brief pair exposes the current `Issue Story Desk` plus matching `Issue Copy` schema.

The main repair need is source accounting. The June dry run reports validation failures on 22 of 30 days, all visible failures are missing manifest-day sources from daily `sources.md` intake batches. Eight days validate cleanly at the daily-run level: `2026-06-03`, `2026-06-12`, `2026-06-15`, `2026-06-21`, `2026-06-24`, `2026-06-28`, `2026-06-29`, and `2026-06-30`.

Forecast discipline is cleaner than issue readiness: June has 32 hooks in the main forecast ledger and exactly 32 matching Accountability Triage rows. All June triage rows are non-accountable retrospective hypotheses or excluded retrospective entries. That is appropriate for the current state: June forecasts are useful as historical review hooks, not accountable ex-ante forecasts.

## Date Coverage and Daily Stack

Every June date has manifest rows and a daily directory. Every June date is missing `issue.md`.

| Date | Manifest rows | Daily dir | `sources.md` | `synthesis.md` | `forecast.md` | `daily-brief.md` | `issue.md` | Stack status |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| `2026-06-01` | 15 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-02` | 16 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-03` | 7 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-04` | 10 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-05` | 9 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-06` | 9 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-07` | 7 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-08` | 16 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-09` | 16 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-10` | 9 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-11` | 17 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-12` | 10 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-13` | 8 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-14` | 7 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-15` | 11 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-16` | 15 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-17` | 11 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-18` | 12 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-19` | 12 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-20` | 7 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-21` | 2 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-22` | 10 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-23` | 14 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-24` | 9 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-25` | 9 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-26` | 11 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-27` | 9 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-28` | 2 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-29` | 7 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |
| `2026-06-30` | 10 | yes | yes | yes | yes | yes | no | `schema-needs-migration` |

Completeness judgment: `structurally-complete-four-file-stack`

Issue readiness judgment: `not-issue-ready`

## Source Accounting

Dry run command:

```powershell
.\scripts\python.ps1 scripts\geopolitical_synthesis.py --start-date 2026-06-01 --end-date 2026-06-30 --dry-run
```

Summary:

- Dates checked: 30
- Clean daily validations: 8
- Dates with validation failures: 22
- Validation warnings: 0 on all days
- Total visible missing-source failures: 47
- Failure type observed: daily intake batch missing manifest-day source

| Date | Manifest rows | Failures | Warnings | Source-accounting status |
| --- | ---: | ---: | ---: | --- |
| `2026-06-01` | 15 | 3 | 0 | `source-accounting-needs-repair` |
| `2026-06-02` | 16 | 2 | 0 | `source-accounting-needs-repair` |
| `2026-06-03` | 7 | 0 | 0 | `valid-dry-run` |
| `2026-06-04` | 10 | 3 | 0 | `source-accounting-needs-repair` |
| `2026-06-05` | 9 | 1 | 0 | `source-accounting-needs-repair` |
| `2026-06-06` | 9 | 4 | 0 | `source-accounting-needs-repair` |
| `2026-06-07` | 7 | 1 | 0 | `source-accounting-needs-repair` |
| `2026-06-08` | 16 | 1 | 0 | `source-accounting-needs-repair` |
| `2026-06-09` | 16 | 4 | 0 | `source-accounting-needs-repair` |
| `2026-06-10` | 9 | 3 | 0 | `source-accounting-needs-repair` |
| `2026-06-11` | 17 | 4 | 0 | `source-accounting-needs-repair` |
| `2026-06-12` | 10 | 0 | 0 | `valid-dry-run` |
| `2026-06-13` | 8 | 1 | 0 | `source-accounting-needs-repair` |
| `2026-06-14` | 7 | 2 | 0 | `source-accounting-needs-repair` |
| `2026-06-15` | 11 | 0 | 0 | `valid-dry-run` |
| `2026-06-16` | 15 | 4 | 0 | `source-accounting-needs-repair` |
| `2026-06-17` | 11 | 1 | 0 | `source-accounting-needs-repair` |
| `2026-06-18` | 12 | 3 | 0 | `source-accounting-needs-repair` |
| `2026-06-19` | 12 | 1 | 0 | `source-accounting-needs-repair` |
| `2026-06-20` | 7 | 2 | 0 | `source-accounting-needs-repair` |
| `2026-06-21` | 2 | 0 | 0 | `valid-dry-run` |
| `2026-06-22` | 10 | 1 | 0 | `source-accounting-needs-repair` |
| `2026-06-23` | 14 | 2 | 0 | `source-accounting-needs-repair` |
| `2026-06-24` | 9 | 0 | 0 | `valid-dry-run` |
| `2026-06-25` | 9 | 1 | 0 | `source-accounting-needs-repair` |
| `2026-06-26` | 11 | 2 | 0 | `source-accounting-needs-repair` |
| `2026-06-27` | 9 | 1 | 0 | `source-accounting-needs-repair` |
| `2026-06-28` | 2 | 0 | 0 | `valid-dry-run` |
| `2026-06-29` | 7 | 0 | 0 | `valid-dry-run` |
| `2026-06-30` | 10 | 0 | 0 | `valid-dry-run` |

Source accounting judgment: `mismatch-unresolved`

Recommended repair order: reconcile `sources.md` intake coverage before any issue migration or synthesis deepening.

## Synthesis and Issue Readiness

Schema scan results:

- June `synthesis.md` files with `## Issue Story Desk`: 0
- June `daily-brief.md` files with `## Issue Copy`: 0
- June generated `issue.md` files: 0

All June daily stacks predate the current generated issue contract. They should be treated as `synthesis-ready-only` or `stale-schema` until migrated.

Issue readiness judgment: `canonical-inputs-incomplete`

Migration requirement for each day:

1. Reconcile source accounting first.
2. Add a current `Primary Voices` table if missing or incomplete.
3. Add `Operational Claim Triage` with no orphan `OPC-*` rows.
4. Add `Issue Story Desk` with exactly one lead and no more than four briefs.
5. Add matching `Issue Copy` and valid revision log to `daily-brief.md`.
6. Generate `issue.md` from canonical inputs; do not hand-edit generated issue output.

## Forecast Discipline

June forecast inventory:

- June hook rows in daily `forecast.md`: 32
- June hooks in main ledger `## Entries`: 32
- Unique June main ledger hooks: 32
- June Accountability Triage rows: 32
- Missing triage rows: none
- Triage rows without main entries: none
- Duplicate June main entries: none

June forecast hooks:

| Hook group | Count | Accountability posture |
| --- | ---: | --- |
| `NG-20260601-F01` through `NG-20260629-F01` | 29 | `retrospective_hypothesis`, `excluded_retrospective`, `accountable: no` |
| `NG-20260630-F01` through `NG-20260630-F03` | 3 | `retrospective_hypothesis`, `excluded_retrospective`, `accountable: no` |

Forecast discipline judgment: `ledger-clean-retrospective`

The ledger is structurally clean, but June hooks are not accountable ex-ante forecasts. They should remain historical review hooks unless later evidence proves contemporaneous authorship.

## Operational Claim and Verification Boundary

Operational claim scan:

- `OPC-202606*` rows found: 0
- `Operational Claim Triage` sections found in June daily stack: 0
- `source_assertion` / `verification_supported` language found in June daily stack: 0

Verification judgment: `not-current-schema`

The audit did not find overpromoted current-schema operational claims. The more important issue is absence of the current operational-claim boundary apparatus. If June is migrated to issue-ready form, high-consequence strike, battlefield, routing, casualty, damage, deployment, and covert-intent claims should be held as `source_assertion` unless packet-supported.

External verification readiness: `not-public-factual-basis`

## Sequence Coherence

June appears coherent as a retrospective archive arc, but the coherence is not yet issue-rendered. Based on the existing daily spread and forecast hooks, the month reads as a long Iran/Hormuz/MOU crisis sequence with repeated Russia/Ukraine and NATO capacity-pressure parallels.

Working sequence map:

| Segment | Dates | Dominant function |
| --- | --- | --- |
| Opening pressure | `2026-06-01` to `2026-06-06` | Iran/Hormuz escalation, U.S. military option pressure, and Western capacity strain. |
| Retaliation and bargaining stress | `2026-06-07` to `2026-06-14` | Retaliation claims, Lebanon linkage, Israeli sabotage arguments, and MOU stress. |
| Settlement strain and strategic room | `2026-06-15` to `2026-06-23` | MOU viability, Lebanon/Iran sequencing, Russia/NATO pressure, and Western strategic overload. |
| Late-month consolidation | `2026-06-24` to `2026-06-30` | Retrospective synthesis into coercive calm, Hormuz leverage, and July setup. |

Coherence judgment: `coherent-with-stale-schema`

The archive likely has a usable month-scale crisis sequence, but daily issue migration is needed before June can be fairly compared to the current July issue-ready stack.

## Validation Results

Repository integrity:

```text
repository_integrity_failures=0
```

Test suite:

```text
195 passed in 77.27s
```

Test command:

```powershell
.\scripts\python.ps1 -m pytest --basetemp .codex-pytest-temp
```

Environmental caveat: use repo-local `--basetemp .codex-pytest-temp` on Windows because the default user temp pytest directory may be permission-blocked.

## Git State

Observed before writing this audit artifact:

- Modified source manifest and voice indexes from prior intake/synthesis work.
- Modified July 7-9 daily files and forecast ledger from prior issue-schema migration and triage repair.
- Untracked July 1-6, July 7-9 issue files, July 11-13, and July 15 daily/source work from prior July work.
- Untracked scratch: `.codex-pytest-temp/`, `tmp/`.

Expected new change from this audit: `narrative-geopolitics/work/audits/2026-06-archive-audit.md`.

Git state judgment: `intended-plus-preexisting-dirty-state`

## Final Audit Judgment

Overall status: `structurally-complete-needs-repair`

The audited range is structurally complete but not issue-ready. It is complete in manifest coverage and four-file daily-stack presence, coherent as a broad Iran/Hormuz/MOU retrospective archive sequence, and clean in forecast-ledger parity. It is limited by unresolved source-accounting failures on 22 of 30 days, complete absence of generated `issue.md`, and absence of the current Issue Story Desk / Issue Copy / Operational Claim Triage apparatus.

Recommended next action: `repair-source-accounting`, then `migrate-stale-schema`.

Priority order:

1. Repair source accounting for the 22 failing dates.
2. Validate June dry run to `validation_failures=0`, `validation_warnings=0`.
3. Migrate June daily stacks to the current issue schema.
4. Generate `issue.md` for each day.
5. Preserve forecast hooks as retrospective unless contemporaneous authorship evidence changes.
6. Only then consider monthly synthesis or public-facing promotion.

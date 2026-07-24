# From Daily Machinery to a Durable Issue

Status: `active method contract`

## Purpose

`issue.md` is the internal reader-facing edition of a substantive Narrative Geopolitics archive day. It gives the day a durable publication shape without changing the evidence hierarchy or constituting public distribution.

The five daily files remain canonical:

- `sources.md` owns manifest-backed source accounting and source IDs;
- `synthesis.md` owns judgment, story selection, voice roles, uncertainty, and operational-claim triage;
- `forecast.md` owns causal wagers and review posture;
- `judgment.md` owns the concise internal accountable-judgment handoff and is
  not a public authorization surface.
- `daily-brief.md` owns issue copy and the append-only revision log.

`issue.md` is generated from those inputs. Edit a canonical file and regenerate; never repair drift directly in the issue.

When selected claims are migrated into the Reality Verification Lattice, the
issue also records a digest of the relevant lattice subgraph and renders its
assessment state. A later adjudication therefore makes the issue stale without
turning the issue itself into evidence.

## Issue Shape

The masthead is **Narrative Geopolitics — Daily Issue**. A normal issue is written for a serious generalist in calm institutional prose and targets 1,500–2,500 editorial words. It normally carries one lead and two to four briefs, but a thin substantive day may carry fewer stories when the Editor's Note says why.

The eight desks have stable jobs:

1. `Front Page` states the lead and the issue hierarchy.
2. `Briefing Desk` carries secondary bounded story objects.
3. `Main Analysis` develops the lead mechanism.
4. `Source Ledger` lists only sources used by selected stories and links to complete accounting.
5. `Forecast Desk` shows relevant bands, dates, and strengthening or weakening tests.
6. `Verification Desk` names load-bearing claims, their status, consequence, and missing observables.
7. `Voices / Columns` identifies named pressure tests without implying endorsement or reconstructed present opinion.
8. `Editor's Note` explains selection and exclusion and renders the revision log.

## Selection Contract

The `Issue Story Desk` in `synthesis.md` is the only authority for issue membership. Stable `NGI-YYYYMMDD-SNN` rows declare placement, headline, crisis object, evidence posture, source IDs, voices, forecast hooks, operational claims, and selection rationale. `lead` and `brief` rows require matching copy in `daily-brief.md`; `hold` rows do not appear as story copy.

Evidence posture is visible once per story. It may be `source-assertion`, `bounded-analysis`, `forecast`, `verification-supported`, `verification-contested`, or `mixed`. The label constrains the prose; it does not upgrade the underlying evidence.

## Evidence and Accountability

Archive sources remain the truth base. Repeated commentary remains repeated commentary. A generated issue may attribute an unresolved source assertion, but it may not adopt a load-bearing operational fact unless the existing verification gate permits it. `verification-supported` requires an assessed supporting `VER-*` packet. Accountable forecast hooks remain open or resolved only in the central ledger under the forecast-review contract.

The issue cutoff is the archive date. Later corrections and updates are appended to the canonical `daily-brief.md` Revision Log with UTC timestamps and then rendered into the issue. Earlier revision entries are not silently replaced.

## Commands

```powershell
.\tools\run.ps1 issue-render --date YYYY-MM-DD
.\tools\run.ps1 issue-render --date YYYY-MM-DD --check
.\tools\run.ps1 issue-render --date YYYY-MM-DD --force
.\tools\run.ps1 daily-validate --date YYYY-MM-DD --stage issue
```

The renderer records a version marker and digest of the ordered four canonical inputs. `--check` and repository validation reject a stale or hand-edited issue. Public promotion remains a separate operator-authorized phase.

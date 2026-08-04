# narrative-systems

An archive-first family of source-grounded systems for historical traversal,
historical inheritance, and geopolitical judgment.

The executable center is [Narrative Geopolitics](narrative-geopolitics/README.md):
a source-bounded system for curating intellectual voices, testing their
continuity across time and channels, bringing their distinct frameworks into
disciplined dialogue, producing synthesis, and holding forecasts accountable.

The archive is the evidence floor. Voice reconstruction and council dialogue
are interpretive work products, never claims about what a living person
currently thinks.

[Predictive History](predictive-history/README.md) remains a sibling study of
public historical and civilizational corpus traversal.

[Historical Entropy](historical-entropy/README.md) is the third project: an
original public lecture series and governed long-memory system for tracing how
historical inheritance is preserved, compressed, mutated, lost, recovered, and
reactivated. Its derived objects organize interpretation; they never become
independent evidence for the sources from which they descend.

## Layout

```text
.
├── narrative-geopolitics/  Archive, continuity, work, forecasts, and public output
├── predictive-history/     Sibling public-system study
├── historical-entropy/     Governed historical inheritance and long-memory study
├── docs/                   Method and local skill contracts
├── scripts/                Operator commands and validators
└── tests/                  Intake, synthesis, forecast, and integrity tests
```

## Development

Install Python 3.11 or newer. Repository commands prepare and reuse validation
dependencies in an external user cache; no environment activation or repo-local
`.venv` is required.

```powershell
.\tools\run.ps1 test --path tests/test_example.py
.\tools\validate.ps1 -Mode Fast
.\tools\validate.ps1
.\tools\validate.ps1 -Force
.\tools\run.ps1 cadence coffee --json
.\tools\run.ps1 harness
```

Repeat `--path` to run multiple focused test files or directories. Focused
tests are an iteration aid. `-Mode Fast` examines the working-tree change set
and runs an integrity/privacy floor plus an allowlisted set of tests for narrow
archive-source, daily-work, voice-index, comparison, continuity, or modified
existing-test changes. Renames, deletions, new tests, manifests, code,
dependencies, workflows, schemas, skills, templates, security surfaces, and
every unknown path fail closed to Full. The route, reasons, selected checks,
and phase timings are written to stderr.

`.\tools\validate.ps1` remains the Full terminal gate. A successful Full result
is reused only when the complete tracked and non-ignored untracked repository
content, executable bits, validation policy, dependency declarations, and
validation runtime fingerprint are unchanged. Commit SHA, branch name, and
timestamps are deliberately excluded, so content-equivalent commits can reuse
the result. The result record lives under the external validation cache;
`-Force` bypasses it. Failed and Fast results are never cached.

The harness audit is read-only. Add `--json` for machine output or
`--write-receipt` to write the ignored `tmp/ai-harness/latest.json` receipt.
Changes to a model behind an existing workflow use the internal
[model-substitution readiness gate](docs/model-substitution-readiness.md).

Use `NARRATIVE_PYTHON` to select a specific Python executable and
`NARRATIVE_VALIDATION_CACHE` to select an external cache directory. Private
intake behavior is documented separately under
`narrative-geopolitics/method/` and is not part of repository maintenance.

## Outcome-aware choice navigation

Final responses expose three or four distinct next possibilities. A letter
enters and develops the selected branch; selection alone grants no authority
to mutate, execute, spend, publish, communicate, act on customers, stage,
commit, push, or deploy.

Unselected menus are not retained. To retain selected branches privately,
configure an absolute SQLite path outside the repository:

```powershell
$env:NARRATIVE_CHOICE_DB = "C:\private\narrative-choice-history.sqlite3"
```

The first retained selection creates or migrates the private store. Selection
atomically records the exact sanitized option set, stable semantic roles,
recommendation and selection bindings, scope, timestamps, bounded signals,
and a `branch_selected` event. Prompts are immutable and later events are
append-only and hash-chained. Direct contact data is redacted; secrets,
credentials, and raw private evidence bodies are rejected. If the store is
missing, navigation continues and retention is reported as unavailable.

Use a private JSON file containing three or four objects with `key`, `role`,
and `text` fields:

```powershell
.\tools\run.ps1 choice select --choice-id CHOICE-20260729-01 `
  --options-json C:\private\choice-options.json --selected-key inspect `
  --choice-kind next-step --consequence-level low `
  --decision-summary "Choose the next bounded investigation" `
  --presented-at 2026-07-29T18:00:00Z --idempotency-key select-20260729-01

.\tools\run.ps1 choice outcome --choice-id CHOICE-20260729-01 `
  --result successful --cognitive-load lower --momentum advanced `
  --discovery-value new-useful-path --idempotency-key outcome-20260729-01

.\tools\run.ps1 choice --format markdown review
.\tools\run.ps1 choice --format markdown show --choice-id CHOICE-20260729-01
.\tools\run.ps1 choice verify --choice-id CHOICE-20260729-01
```

Mutation commands accept `--dry-run`. Use `choice context` to inspect bounded
recommendation evidence. One or two comparable resolved outcomes remain thin
evidence. At least three are required before two consistent outcomes without a
material contradiction may affect the recommended role. Selection frequency
never affects ordering, and a credible overlooked path remains available.
Boundary incidents surface immediately and learning remains tenant/lane
isolated.

`choice review` uses the earliest five resolved, non-superseded selections. It
reports lower cognitive load, advanced momentum, new-useful-path discovery,
result distribution, rework, negative experiences, and boundary incidents.
Its precedence is `hold`, `extend-to-ten`, `adjust`, then `continue`. This
descriptive pilot scorecard does not bypass the separate comparable-outcome
threshold. Unresolved outcomes return only through `coffee`; `dream` does not
solicit them.

Back up and recover private state explicitly:

```powershell
.\tools\run.ps1 choice backup `
  --to C:\private\backups\narrative-choice-history-20260804.sqlite3
.\tools\run.ps1 choice backup-status `
  --backup C:\private\backups\narrative-choice-history-20260804.sqlite3
.\tools\run.ps1 choice recover `
  --from C:\private\backups\narrative-choice-history-20260804.sqlite3 `
  --to C:\private\restored-choices.sqlite3 --dry-run
```

Backups are created through a same-directory temporary database, checked for
integrity and logical equivalence, and then atomically replace the destination.
`backup-status` reports `fresh: true` only when the backup is healthy and its
sanitized logical fingerprint exactly matches the current store. Use a dated
destination so an older recovery point is not silently discarded.

Choice-store schema 2 preserves the submitted timestamp text and adds a derived
UTC microsecond key for chronological cohort ordering. Read-only commands remain
compatible with schema 1; the first later writable choice command migrates a
schema-1 store transactionally. Create and verify a current backup before that
first writable command. Scoped context, review, and whole-scope verification use
batched prompt/event reads and the scope-ordering index rather than one query per
choice.

## Operating Boundary

- `archive/` owns source truth.
- `voices/` and `channels/` own continuity and conditioning.
- `work/` owns internal dialogue, judgment, experiments, and forecast review.
- `public/` contains intentionally promoted reader-facing material.
- `historical-entropy/` may derive memory and inheritance objects from named
  sources, but those objects are navigation and interpretation surfaces, not
  corroborating evidence.
- Empty dates create no daily directory.

# mira-core

Formerly `narrative-systems`, this integrated monorepo is the developmental
core of Mira. The earlier name remains part of the repository's intellectual
ancestry and in immutable historical identifiers.

`mira-core` is Mira's integrated monorepo: the shared identity, continuity,
governance, memory, research, and execution kernel from which specialized
surfaces may later emerge. Here, *core* names a durable responsibility, not a
small dependency library or a component split already under way.

Hosted repository: <https://github.com/rbtkhn/mira-core>

Mira's archive-first family of source-grounded systems for historical
traversal, historical inheritance, geopolitical judgment, and governed
recursive learning.

[System Archive](system-archive/README.md) is the shared durable substrate for
immutable bodies, cross-collection inventory, provenance, temporal retrieval,
and bounded context assembly. It does not replace collection-native authority.

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
├── system-archive/         Shared storage, provenance, time, and context governance
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
$env:MIRA_CORE_SESSION_TEMP_ROOT = 'C:\private\mira-core-test-temp'
.\tools\run.ps1 test --temp-root $env:MIRA_CORE_SESSION_TEMP_ROOT --path tests/test_example.py
.\tools\validate.ps1 -Mode Fast -TempRoot $env:MIRA_CORE_SESSION_TEMP_ROOT
.\tools\validate.ps1 -TempRoot $env:MIRA_CORE_SESSION_TEMP_ROOT
.\tools\validate.ps1 -Force -TempRoot $env:MIRA_CORE_SESSION_TEMP_ROOT
.\tools\run.ps1 cadence coffee --json
.\tools\run.ps1 harness
.\tools\run.ps1 system-archive status
```

Repeat `--path` to run multiple focused test files or directories. Focused
tests are an iteration aid. `-Mode Fast` examines the working-tree change set
and runs an integrity/privacy floor plus an allowlisted set of tests for narrow
archive-source, daily-work, voice-index, comparison, continuity, or modified
existing-test changes. Renames, deletions, new tests, manifests, code,
dependencies, workflows, schemas, skills, templates, security surfaces, and
every unknown path fail closed to Full. The route, reasons, selected checks,
and phase timings are written to stderr.

All pytest-running validation requires an absolute, writable temporary root
outside the repository. Pass it explicitly or configure
`MIRA_CORE_SESSION_TEMP_ROOT`; governed validation removes inherited
`PYTEST_ADDOPTS` and supplies `--basetemp` directly.

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

Use `MIRA_CORE_PYTHON` to select a specific Python executable and
`MIRA_CORE_VALIDATION_CACHE` to select an external cache directory. Private
intake behavior is documented separately under
`narrative-geopolitics/method/` and is not part of repository maintenance.

## Outcome-aware choice navigation

Open final responses expose three or four distinct next possibilities; settled
branches close without manufacturing another menu. A letter enters and
develops the selected branch; selection alone grants no authority
to mutate, execute, spend, publish, communicate, act on customers, stage,
commit, push, or deploy.

Unselected menus are not retained. To retain selected branches privately,
configure an absolute SQLite path outside the repository:

```powershell
$env:MIRA_CORE_CHOICE_DB = "C:\private\mira-core-choice-history.sqlite3"
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

.\tools\run.ps1 choice close --choice-id CHOICE-20260729-01 `
  --reason completed --idempotency-key close-20260729-01

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
  --to C:\private\backups\mira-core-choice-history-20260804.sqlite3
.\tools\run.ps1 choice backup-status `
  --backup C:\private\backups\mira-core-choice-history-20260804.sqlite3
.\tools\run.ps1 choice recover `
  --from C:\private\backups\mira-core-choice-history-20260804.sqlite3 `
  --to C:\private\restored-choices.sqlite3 --dry-run
```

Backups are created through a same-directory temporary database, checked for
integrity and logical equivalence, and then atomically replace the destination.
`backup-status` reports `fresh: true` only when the backup is healthy and its
sanitized logical fingerprint exactly matches the current store. Use a dated
destination so an older recovery point is not silently discarded.

Choice-store schema 3 adds append-only `branch_closed` lifecycle events and
choice projection 1.1. Closure reasons are `completed`, `paused`, and
`saturated`. A closed branch leaves unresolved review but contributes no outcome
or recommendation evidence; a later observed outcome may resolve it. Review
projection remains 2.0 and includes only resolved outcomes.

Schema 3 retains schema 2's submitted timestamp text and derived UTC microsecond
ordering key. Read-only commands remain compatible with schemas 1 and 2; the
first later writable command migrates an older store transactionally, including
rebuilding the constrained event table without changing existing events. Create
and verify a current backup before that first writable command. Existing
unresolved choices are not backfilled automatically. Scoped context, review,
and whole-scope verification use batched prompt/event reads and the scope-ordering
index rather than one query per choice.

## Operating Boundary

- `archive/` owns source truth.
- `system-archive/` owns shared storage and cross-collection inventory; it does
  not adjudicate collection membership or truth.
- `voices/` and `channels/` own continuity and conditioning.
- `work/` owns internal dialogue, judgment, experiments, and forecast review.
- `public/` contains intentionally promoted reader-facing material.
- `historical-entropy/` may derive memory and inheritance objects from named
  sources, but those objects are navigation and interpretation surfaces, not
  corroborating evidence.
- Empty dates create no daily directory.

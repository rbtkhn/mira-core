# Narrative Geopolitics Work Surface

`work/` holds internal dialogue, judgment, experiments, and forecast
accountability. It does not own source truth.

## Council Dialogues

`dialogues/` contains manual, corpus-bounded experiments in realistic dialogue
with curated intellectual voices. Start with
[dialogues/_template.md](dialogues/_template.md) and obey the
[dialogue contract](../method/dialogue-contract.md).

Each voice response is drafted separately from the same bounded question. A
moderator may compare or synthesize only after the responses exist; the
moderator must not silently make the voices agree. Dialogues are interpretive
work products, not archive evidence, actual interviews, or claims about a
person's present opinion.

The first manual experiment is the
[Council Value Test](dialogues/2026-07-council-value-test/README.md). It must
earn automation by demonstrating fidelity, differentiation, and reader value.

## On-Demand Daily Runs

A daily run exists only when the date has manifest-backed sources or an
intentional retrospective run. Empty dates create no directory.

```text
work/daily/YYYY-MM-DD/
├── sources.md
├── synthesis.md
├── forecast.md
└── daily-brief.md
```

Open a guided run:

```powershell
.\tools\run.ps1 synthesis --date YYYY-MM-DD
```

Execute the full stack:

```powershell
.\tools\run.ps1 synthesis --date YYYY-MM-DD --execute
```

The four daily Markdown inputs remain canonical. A completed run declares its
lineup in `synthesis.md`, carries matching copy and an append-only UTC revision
log in `daily-brief.md`, and generates `issue.md` as its internal reader-facing
layer. See [the daily-issue method](../method/daily-issue.md).

```powershell
.\tools\run.ps1 issue-render --date YYYY-MM-DD
.\tools\run.ps1 daily-validate --date YYYY-MM-DD --stage issue
```

Date-range and month modes skip dates without manifest rows. The legacy
`--scaffold-empty` flag is accepted for compatibility but writes nothing.

The guided menu is:

- `A` bootstrap or refresh a manifest-backed run;
- `B` reconcile intake coverage and routing;
- `C` deepen the owning crisis object;
- `D` sharpen forecast hooks and review logic;
- `E` execute the full stack.

The older `scripts/geo_synthesis.py` filename remains a compatibility shim.

## Validation

Before synthesis, normalize provisional person identifiers and reconcile
manifest-backed routes into voice shelves that already exist:

```powershell
.\tools\run.ps1 voice-canonicalize --date YYYY-MM-DD --check
.\tools\run.ps1 voice-sync --date YYYY-MM-DD --check
```

Guided choice `B` performs both repairs. This downstream step does not change
private intake, source bodies, filenames, archive paths, or host/channel slugs.
Manifest voices without an established shelf are reported but do not block
synthesis.

Validate a day at the relevant stage:

```powershell
.\tools\run.ps1 daily-validate --date YYYY-MM-DD --stage synthesis
```

- `intake` reports stale coverage and a refresh instruction without blocking
  source landing;
- `synthesis`, `forecast`, and `publication` require exact Intake Batch coverage;
- `issue` additionally requires a current deterministic `issue.md`;
- the Run Source Set may be a documented analytical subset.

Validate the repository boundary:

```powershell
.\tools\validate.ps1
```

This checks archive/manifest parity, daily-run grounding, forecast/triage
parity, internal links, and the skill deployment allowlist.

## Forecast Accountability

The Markdown ledger preserves every historical row. Only timing-reviewed
`ex_ante` entries marked `Accountable: yes` belong in calibration.

```powershell
.\tools\run.ps1 forecast-triage --as-of YYYY-MM-DD
.\tools\run.ps1 forecast-sync --date YYYY-MM-DD --crisis-object "Bounded object"
```

Use `--dry-run` before ledger synchronization. When authorized evidence cannot
resolve an observable, record `unresolvable_with_authorized_evidence` rather
than forcing a result.

## Operational Verification

Use [verification](verification/README.md) only for a selected load-bearing operational claim. Requests are explicit, web research is bounded to named observables, and evidence remains a work packet rather than archive truth.

New and explicitly migrated claims use the canonical JSON graph in
[reality](reality/README.md). The lattice preserves source lineage, original-
language environments, atomic assessments, human signatures, and append-only
epistemic transitions. Legacy packets retain authority until migration; their
Markdown must not be silently rewritten during migration.

```powershell
.\tools\run.ps1 verification new --date YYYY-MM-DD --slug TEXT
.\tools\run.ps1 verification list --json
.\tools\run.ps1 verification check
.\tools\run.ps1 verification day --date YYYY-MM-DD --json
```

Daily synthesis uses `Operational Claim Triage` as an exception gate, not a fact inventory. Retain a row only when the claim controls planned public factual use, concrete-event watch promotion, or an accountable forecast dependency; validation rejects internal-only orphan rows. Choice `C` reports unresolved requests and choice `D` reports forecast dependencies; both are read-only. Attributed narrative claims do not require packets.

## Skill Deployment

The repo-owned `best-intake`, `geo-strategy`, and `reality-check`
drafts are eligible for user-level synchronization. Synchronization mirrors
the complete registered skill directory, including `agents/openai.yaml` when
present:

```powershell
.\tools\run.ps1 skills-check
.\tools\run.ps1 skills-sync --dry-run
```

Coffee and Dream are local operator contracts. They are not globally deployed.
They close advisory learning loops through a configured append-only private
SQLite ledger outside Git:

```powershell
$env:MIRA_CORE_CADENCE_DB = 'C:\private\mira-core-cadence.sqlite3'
.\tools\run.ps1 cadence coffee --format markdown
.\tools\run.ps1 cadence dream --help
```

Dream records one falsifiable experiment, its bounded evidence handles,
verification receipts, observable, expiry, and candidate method change.
Coffee reads the oldest actionable candidate and deterministically returns
exactly four grounded, navigation-only actions. Relevant state changes require
reconciliation; unrelated Git movement does not invalidate local applicability.
Cadence is never archive evidence or the canonical Recursive Learning ledger.

## System Improvement

The [recursive learning ledger](system-improvement/recursive-learning-ledger.md)
records evidence-backed changes to how the system observes, evaluates, or
improves its own behavior. Its
[method contract](../method/recursive-learning-ledger.md) distinguishes closed
feedback loops from partial loops and ordinary feature work. The JSON ledger is
canonical; repository validation rejects missing stage evidence or Markdown
drift.

## Operator Positions

[*Strategic Judgment Ledger*](operator-positions/strategic-judgment-ledger.md)
grows from approved journal events and immutable position versions, projects a
typed graph for AI exploration, and compares positions with evidence-qualified
repository voices. The chronological journal and thematic position view are
generated readings of the same canonical event history. Its
[method contract](../method/operator-position-self-map.md) keeps raw prompts
and candidates local, requires explicit approvals for journal entries,
positions, comparators, and scores, and forbids an overall coherence score.

```powershell
.\tools\run.ps1 operator-position query --view current-beliefs
.\tools\run.ps1 operator-position query --view voice-map
.\tools\run.ps1 operator-position due --as-of YYYY-MM-DD
.\tools\run.ps1 operator-position journal-draft --input PATH --date YYYY-MM-DD --kind daily_reflection
.\tools\run.ps1 operator-position report
.\tools\run.ps1 operator-position validate
```

## Daily Operating Rule

The order remains:

```text
archive -> voices/channels -> work/daily or work/dialogues -> forecast review -> optional public
```

Use newly landed day sources first. Retrieve older material only when it changes
the crisis object, confidence, contradiction handling, or falsifiability. Do
not publish a daily brief unless it is intentionally promoted.

Private intake, transcript preservation, trimming, ASR repair, and manifest-row
creation remain governed by `method/best-intake.md`.

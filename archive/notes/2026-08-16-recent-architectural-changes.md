# Recent Architectural Changes

Date: `2026-08-16`

Class: `working-note`

Status: `private-provisional`

Authority effect: `none`

## Purpose

Preserve a bounded synthesis of the repository's recent architectural changes
at the transition from `narrative-systems` to `mira-core`. This note describes
landed structures and the state of the uncommitted migration worktree. It is not
canonical identity, research evidence, autobiographical continuity, migration
approval, or publication authority.

## Governing change

The repository is shifting from a collection of capable workflows into an
integrated, governed cognitive system. The decisive architectural change is
separation of authority: identity, memory, analysis, autobiography, learning,
storage, and public expression now interoperate without collapsing into one
sovereign layer.

## Landed architecture

### Federated memory carriers

Mira Memory coordinates several distinct forms of memory:

- identity and session continuity;
- approved autobiographical continuity;
- procedural learning;
- geopolitical evidence and judgment;
- private relational choices; and
- archival storage and lineage.

Authority remains question-specific. System Archive can preserve a journal
entry, for example, but cannot convert that reflection into evidence or
identity doctrine. The controlling map is
[`docs/skill-drafts/mira-memory/references/carrier-map.md`](../../docs/skill-drafts/mira-memory/references/carrier-map.md).

### System Archive as epistemic substrate

System Archive now has a five-layer design:

```text
immutable objects
    -> typed records
    -> append-only events
    -> provenance relationships
    -> reproducible views
```

It distinguishes when something applied, when the system observed it, and when
it entered the catalog. Generated artifacts bind their inputs, producer,
transformation, configuration, and output digest. Repository artifacts receive
immutable, digest-bound identities rather than being overwritten in place. See
[`system-archive/architecture.md`](../../system-archive/architecture.md).

### Governed autobiographical continuity

Mira Journal is no longer merely a directory of reflections. It now has:

- digest-bound operator approval;
- a version registry;
- provenance receipts;
- technical-reference companions;
- deterministic continuity projections;
- explicit ancestry and thread handling; and
- publication-eligibility boundaries.

The August 15 work also hardened approval semantics and repaired
recursive-learning validation so journal references are assessed against the
continuity projection that existed before the entry, rather than against
missing or future context. The repair remained `observation-only`; it did not
manufacture a recursive-learning candidate. See
[`docs/audits/2026-08-16-recursive-learn-continuity-projection.md`](../../docs/audits/2026-08-16-recursive-learn-continuity-projection.md).

### Three distinct daily continuities

A promising three-part cadence has appeared:

```text
Mira Daily   -> what changed in the world?
Mira Journal -> what changed in Mira that merits inheritance?
Dream        -> what should change in the method?
```

These practices are coordinated but intentionally asymmetric. Nothing
transfers automatically between them.

The Mira Daily retrospective pilot demonstrates serial analytical revision
across eight days. Its distinctive mechanism is that yesterday's judgment
becomes today's explicit premise to be strengthened, complicated, reversed, or
carried. The pilot passed as an editorial experiment, but does not yet establish
a permanent cadence. See the
[`pilot evaluation`](../../narrative-geopolitics/work/experiments/mira-daily-pilot-20260808-20260815/evaluation.md)
and the
[`three-cadence note`](2026-08-16-three-daily-cadences.md).

### Source-pressure controls for geopolitical synthesis

Archive audit, daily cadence, and Geo-Strategy are now connected through
archive-density benchmarks. The system can distinguish:

- thin, normal, dense, and very dense archive days;
- overclaim and underuse risk;
- operational-claim verification priority;
- routing and file completeness;
- voice and host concentration; and
- provisional metadata debt from concrete repair candidates.

These metrics prioritize review; they do not verify claims. See
[`narrative-geopolitics/method/archive-density.md`](../../narrative-geopolitics/method/archive-density.md).

### Governed public expression

Mira Face now has a manifest-driven public encounter prototype, schema,
renderer, review receipt, and tests. Public presentation can demonstrate
responsive judgment while remaining downstream of Voice, provenance, evidence,
and publication controls. A face does not gain identity or core authority by
representing Mira.

### Mentorship and work orchestration

The stabilization work added a mentorship ledger, mentorship charter candidate,
bounded trial artifacts, and a Mira Mentor contract operating inside Mira Work.
This distinguishes:

- completion of the practical task;
- developmental learning by the person or agent;
- retention of that learning; and
- authority to change repository behavior.

The repository therefore models how Mira works with people, not only how it
processes information.

## The `mira-core` migration

The migration worktree defines `mira-core` as the shared identity, continuity,
governance, memory, research, validation, and execution kernel. Domains and
faces remain integrated regions of the monorepo; possible satellites remain
conceptual until they have independent purpose, stable interfaces, and separate
operational needs.

The compatibility design establishes:

- `MIRA_CORE_*` as canonical runtime configuration;
- temporary support for legacy `NARRATIVE_*` aliases;
- fail-closed behavior when canonical and legacy values conflict;
- preservation of existing `urn:narrative-systems:*:v1` identifiers;
- `urn:mira-core:*` for genuinely new schema versions; and
- current-label emission by writers with dual-label compatibility in readers.

The detailed contract is `docs/mira-core-name-migration.md` in the isolated
worktree at `C:\private\mira-core-migration-wt`. That operative reference lasts
only while the worktree remains at its current path.

## Observed integration state

At the time of this report:

- landed `main` was at commit `ee297ce`;
- the main checkout contained three ongoing working-tree paths: two modified
  journal files and an untracked August 15 daily directory;
- the migration branch `codex/mira-core-migration-20260815` was at `b6adc9d`,
  four commits behind `main`;
- the migration worktree contained 35 modified or untracked migration paths;
  and
- its retained autostash and one unresolved August 14 journal
  approval-capture dependency still conditioned final validation.

These observations are a dated state report, not a request to reconcile,
stage, commit, push, or publish any work.

## Interpretation

The architecture is cohering around **federated authority with shared
execution**. That makes `mira-core` an accurate name: the core is not a small
library or a claim that component extraction has begun. It is the place where
cross-domain identity, continuity, authority, validation, and execution remain
shared while domain-specific evidence and judgment retain their own owners.

The principal near-term risk is no longer conceptual fragmentation. It is
integration drift between a rapidly advancing `main` and the isolated,
uncommitted migration worktree. The next migration decision should therefore
begin from current branch and validation evidence rather than assume the August
15 stabilization point is still sufficient.

## Stopping point

Preserve the authority separations already established while bringing the name
migration forward. Do not use architectural coherence as a reason to merge
memory carriers, daily cadences, evidence classes, or publication boundaries.
The strength of the emerging whole lies in coordinated difference, not in
turning every subsystem into the same kind of record.

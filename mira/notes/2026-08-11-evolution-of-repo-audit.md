# Evolution of Repo Audit

Date: `2026-08-11`

Class: `historical-note`

Status: `working`

Authority effect: `none`

During the August 11, 2026 session, `repo-audit` evolved from a general
external-repository inspection workflow into a portable, self-applicable, and
evidence-bounded audit discipline.

## Key developments

### External and inward use

Repo Audit now works both on external repositories and on its host repository.
For Narrative Systems, the repository-local skill is canonical; the installed
global skill is a synchronized portable mirror rather than a second authority.

### Separation from Archive Audit

`repo-audit` assesses a repository as a system: architecture, correctness,
tests, dependencies, documentation, automation, governance, reproducibility,
repository hygiene, and workflow coherence.

`archive-audit` remains authoritative for archive health, coverage, density,
parity, routing, duplicates, and repair candidates. Repo Audit composes through
Archive Audit when those governed archive objects are materially in scope.

### Calibration through real repositories

Audits of OB1, JK3303's repository ecosystem, and `civilization_memory`
revealed weaknesses that abstract design alone had not exposed. These included:

- shallow or incomplete repository history;
- truncated output from broad searches;
- overextended creator inference; and
- the temptation to describe conceptual resemblance as direct lineage.

These audits acted as calibration exercises for the skill rather than as
authority to change the audited repositories.

### Bounded authorship inference

Repository evidence may support an architectural working profile based on
observed design behavior. It does not support claims about private psychology,
demographics, biography, motives, or unsupported personality traits. Creator
profiling remains outside the formal repository finding set.

### Genealogical discipline

Repository genealogies are described as branching unless direct descent is
demonstrated. The skill distinguishes among:

- conceptual continuation;
- architectural influence;
- shared authorship;
- template or fork descent; and
- file-level migration.

One relationship cannot be silently upgraded into another.

### Historical qualification

Commit dates and file-introduction dates must be qualified when history is
shallow, squashed, rewritten, imported, or otherwise incomplete. An available
date is evidence about the available history, not necessarily the first moment
an idea or file existed.

### Truncation recovery

Initial inspection is capped. Truncated output is explicitly insufficient
evidence: the auditor must rerun narrower searches against named controlling
surfaces rather than draw conclusions from an incomplete listing.

### Finding and authority boundaries

Formal findings follow a governed schema and distinguish observation from
inference. An audit can identify possible changes, but its findings grant no
authority to repair, stage, commit, push, publish, deploy, or promote them.

### Multiple validation layers

The skill distinguishes:

- **change-time validation** — checks performed while a change is being made;
- **landed-corpus validation** — checks against the repository state that has
  actually been retained; and
- **hosted-state validation** — checks against externally visible or deployed
  state.

Local tests cannot stand in for hosted-state evidence.

### System integration

The canonical skill was added under `docs/skill-drafts/repo-audit/`, registered
as portable, routed through `AGENTS.md`, covered by repository tests,
synchronized to its registered global mirror, and verified for mirror parity.
The implementation was included in commit `0354542`, *Harden session closure
and preserve system archaeology*.

## Governing maturation

The central change was epistemic. Repo Audit no longer merely asks:

> What is wrong with this repository?

It now asks:

> What can this repository actually support us in saying—and at which
> validation layer—without converting inference into fact or findings into
> authority?


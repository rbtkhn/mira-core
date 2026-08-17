---
name: archive-audit
description: "Read-only archive health, coverage, parity, drift, density, and retrieval-boundary audits across repository archive families. Use for systematic archive assessment; do not use for ad hoc inventory questions, source mutation, claim verification, or repair execution."
---

# Archive Audit

Archive Audit is the read-only front door for repeatable archive health
assessment. It resolves the intended archive shelf first, then applies that
shelf's native audit controls without changing archive state.

Findings describe evidence and risk. They grant no intake, repair, hydration,
publication, claim verification, identity promotion, staging, commit, push, or
cross-collection authority.

## Archive shelf resolution

Before auditing, identify the shelf:

- Mira Archive collection or private catalog
- Narrative Geopolitics
- Singularity Science
- Mira Journal
- Mira Continuity
- unknown or ambiguous

Use repository evidence before asking:

- `archive/collections.json`
- the private Mira Archive catalog when available and needed for read-only
  audit evidence
- known registries and indexes
- obvious path prefixes, collection IDs, source-family names, voice slugs,
  hosts, channels, or operator labels

If the shelf is still ambiguous after inspection, ask one bounded shelf
clarification. Never report one shelf's health, gap, or parity result as a
global archive assessment.

## Boundary with sibling skills

- Use `archive-query` for bounded inventory, membership, path, or selection
  questions.
- Use `archive-audit` for repeatable health, coverage, parity, drift, density,
  or retrieval-boundary assessment.
- Use `archive-repair` only after a finding becomes an explicit bounded repair
  request.
- Use `archive-intake` when supplied material does not yet exist in the
  selected archive family.

## Backend matrix

### Mira Archive

Audit Mira Archive when the target is a cross-archive substrate concern,
explicit-only collection, private catalog state, registry/catalog parity, or
replica/hydration boundary.

Assess only the requested scope:

- registered collections and collection counts
- private catalog versus checked-in registry drift
- explicit-only retrieval behavior
- hydration-disabled boundaries
- collection count parity
- catalog fingerprints and replica status when requested
- rights, promotion, and authority-boundary metadata where present

Prefer `tools/run.ps1 archive status --json`,
`tools/run.ps1 archive validate --json`, `verify --json`, and
`replica-status --json` when they cover the requested audit. If the checked-in
registry is stale but a private canonical catalog is available, use read-only
catalog inspection for the audit and disclose the mismatch.

Storage and retrieval do not verify claims, transfer publication rights, or
promote material across collections.

### Narrative Geopolitics

Use the canonical command for Narrative Geopolitics archive health, coverage,
density, duplicate/routing checks, and repair-candidate diagnostics:

```powershell
.\tools\run.ps1 archive-audit --month YYYY-MM --format markdown
.\tools\run.ps1 archive-audit --start-date YYYY-MM-DD --end-date YYYY-MM-DD --format json
.\tools\run.ps1 archive-audit --whole-corpus --format markdown
```

Repeat `--voice-slug` or `--host-slug` to filter. Repeated values within a
dimension are alternatives; voice and host filters combine. Never infer
whole-corpus scope without `--whole-corpus`.

Interpretation:

- Treat structural findings as archive-integrity failures.
- Treat coverage gaps, landing-time provisional routing, and repair candidates
  as warnings, not permission to intake or repair. A provisional routing flag
  records deferred enrichment at landing; it is not by itself evidence of an
  unresolved routing defect.
- Bound missing-month analysis to the landed manifest horizon; do not label
  future months as missing.
- Use density only for triage. It does not verify claims or measure truth.

### Singularity Science

Audit Singularity Science through its Mira Archive collections. Check
collection count parity, explicit-only status, hydration-disabled status,
rights boundaries, source-body availability metadata, and registry/catalog
drift. Do not route findings into Narrative Geopolitics, public quotation,
doctrine, identity, customer routing, or publication.

### Mira Journal and Continuity

Audit approved registries, indexes, lineage, and retrieval boundaries only.
Do not treat journal or continuity health as identity proof, operator belief,
research evidence, Reality, or action authority.

### Unknown shelf

Fail closed. State what was inspected and ask one bounded clarification rather
than auditing the wrong archive family.

`archive-density` is a deprecated Narrative Geopolitics density-only
compatibility command. Use `archive-audit` for new work and route to the
selected backend.

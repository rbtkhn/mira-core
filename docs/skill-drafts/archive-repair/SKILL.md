---
name: archive-repair
description: "Governed cross-archive repair router for existing archived records, registries, manifests, catalogs, source wrappers, metadata, ASR, sectioning, hydration, replica, or control-plane defects. Resolve the archive shelf and backend-specific repair class before dry-run or execution; do not use for intake, synthesis, factual verification, or unrestricted bulk rewriting."
---

# Archive Repair

Archive Repair is the governed repair front door for existing archive objects
and archive control surfaces. It resolves the intended archive shelf first,
then applies exactly one backend-specific repair class.

Repair findings, query results, menu navigation, and dry-runs grant no authority
to mutate. Execution requires a direct explicit command for the visible
backend, repair class, target set, and reviewed plan or digest.

## Archive shelf resolution

Before planning repair, identify the shelf:

- Mira Archive collection or private catalog
- Narrative Geopolitics
- Singularity Science
- Mira Journal
- Mira Continuity
- unknown or ambiguous

Use repository evidence before asking:

- `archive/collections.json`
- the private Mira Archive catalog when available and needed for read-only
  repair planning
- known registries and indexes
- obvious path prefixes, collection IDs, source-family names, voice slugs,
  hosts, channels, or operator labels

If the shelf is still ambiguous after inspection, ask one bounded shelf
clarification. Never repair one shelf while describing the target as a generic
archive object.

## Modes and authority

- Use `archive-audit` to diagnose health, coverage, parity, drift,
  metadata, manifest membership, ASR state, sectioning state, and approved
  repair classes without proposing changed bytes.
- Use backend dry-run or `--check` modes to render exact proposed effects,
  diffs, hashes, manifest/catalog state, and plan digest without writing.
- Use `--execute --plan-digest <reviewed-digest>` only after a direct explicit
  command for the visible backend, class, and target set.

A digest binds execution to reviewed bytes or control-plane state; it is not a
capability token.

## Backend matrix

### Mira Archive

Mira Archive repairs are control-plane repairs unless a selected backend
contract explicitly permits source-body edits.

Valid Mira Archive repair families include:

- checked-in registry versus private catalog drift
- collection registration or expected-count metadata
- explicit-only and hydration-disabled policy drift
- replica status and replica synchronization planning
- catalog, fingerprint, or control-plane validation failures
- hydrated mirror repair when explicitly authorized

Prefer `tools/run.ps1 archive validate --json`,
`verify --json`, `replica-status --json`, and backend-supported `--check` or
dry-run routes. Do not edit canonical object bodies, external-corpus source
bodies, publish, quote, hydrate, or synchronize replicas unless that exact
action is separately authorized.

### Narrative Geopolitics

Narrative Geopolitics repairs remain bounded metadata/body/source repairs for
manifest-backed Markdown files under
`archive/sources/geopolitics/sources`.

Accept only repository-relative, manifest-backed Markdown files contained under
that path. Reject absolute paths, traversal, globs, directories, missing files,
duplicate targets, duplicate or missing manifest membership, escaping links,
and dirty execution targets.

Use `archive-query` when a date, voice, host, or channel must be resolved into
an operator-visible file set. An archive-query result grants no authority;
treat it as derived scope evidence only. Before planning or execution, re-read the source manifest and
independently verify every target path and host route.

Choose exactly one repair class per invocation:

1. `metadata`: normalize locally evidenced repair metadata only. Preserve body
   bytes.
2. `asr`: apply only approved deterministic ASR substitutions. Do not trim,
   section, edit unrelated metadata, or normalize layout.
3. `sectioning`: add conservative semantic headings and section metadata for
   approved hosts while preserving transcript word order. Require
   `--resection` to replace existing headings.
4. `wrapper-trim`: remove only an approved host wrapper and update only its
   trim provenance.

Canonical command:

```powershell
.\tools\run.ps1 archive-repair `
  --class asr `
  --path archive/sources/geopolitics/sources/YYYY-MM-DD/source-example.md `
  --dry-run `
  --format markdown
```

For multiple files, repeat `--path` or provide one repository-relative
`--list-file`. The legacy `scripts/run_asr_repair_pilot.py` and
`scripts/backfill_section_list.py` commands are compatibility adapters only;
they must route through the canonical engine and require an explicit mode.

Narrative Geopolitics repair workflow:

1. Run a bounded `archive-audit` and inspect repository controls and Git
   status.
2. Resolve and print the bounded target set.
3. Revalidate manifest membership, paths, host routes, and duplicates.
4. Run one class in `--dry-run` mode and inspect every proposed diff.
5. Stop for a direct explicit execute command naming the exact scope.
6. Rebuild the plan and reject changed manifest, target, or digest state.
7. Apply only planned bytes through atomic replacement and bounded rollback.
8. Confirm changed paths are a subset of approved targets.
9. Re-read the files and verify class-specific invariants.
10. Use `archive-query` to recheck membership, paths, duplicates, and routing;
    this post-check does not establish transcript correctness.

### Singularity Science

Repair Singularity Science only through Mira Archive control-plane or the
selected external-corpus backend. Topical overlap with geopolitics does not
grant Geopolitics repair authority. Preserve explicit-only retrieval, rights,
source-body availability, and publication boundaries.

### Mira Journal and Continuity

Repair only approved registries, indexes, lineage, metadata, or governed
storage controls after selecting the exact Mira backend. Do not rewrite journal
meaning, alter continuity identity claims, or promote records into identity,
operator belief, research evidence, Reality, or action authority through
repair.

### Unknown shelf

Fail closed. State what was inspected and ask one bounded clarification rather
than planning or executing a repair against the wrong archive family.

## Stop conditions

Stop without editing when the shelf is uncertain, backend authority is missing,
the archive and selected index disagree, target state is dirty or stale, the
plan changed after review, repair depends on factual verification, safe
completion would touch an unapproved file, or the requested action would cross
publication, staging, commit, push, deployment, hydration, replica sync, or
external communication boundaries without explicit authorization.

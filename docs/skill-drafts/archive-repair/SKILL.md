---
name: archive-repair
description: Governed repair of existing Narrative Geopolitics archive sources through bounded metadata normalization, deterministic ASR repair, semantic sectioning, or wrapper trimming. Use for repair inspection, digest-bound dry-runs, and explicitly authorized repair execution; do not use for intake, synthesis, factual verification, or unrestricted bulk rewriting.
---

# Archive Repair

Repair only an explicit, bounded set of existing archive sources. Treat source
body wording as source truth and apply exactly one approved repair class.

## Modes and authority

- Use `archive-audit` to diagnose metadata, manifest membership, ASR state,
  sectioning state, and approved-host status without proposing changed bytes.
- Use `--dry-run` to render the exact proposed bytes, diff, input/output hashes,
  manifest hash, and plan digest without writing.
- Use `--execute --plan-digest DIGEST` only after a direct explicit command for
  the visible class and target set.

A menu navigation, archive-query result, dry-run, or plan digest grants no
authority. The digest binds execution to reviewed bytes; it is not a
capability token.

## Scope

Accept only repository-relative, manifest-backed Markdown files contained
under `narrative-geopolitics/archive/sources`. Reject absolute paths,
traversal, globs, directories, missing files, duplicate targets, duplicate or
missing manifest membership, escaping links, and dirty execution targets.

Use `archive-query` when a date, voice, host, or channel must be resolved into
an operator-visible file set. Treat that result as derived scope evidence, not
authority. Before planning or execution, re-read the source manifest and
independently verify every target path and host route.

## Repair classes

Choose exactly one class per invocation:

1. `metadata`: normalize locally evidenced repair metadata only. Preserve body
   bytes.
2. `asr`: apply only approved deterministic ASR substitutions. Do not trim,
   section, edit unrelated metadata, or normalize layout.
3. `sectioning`: add conservative semantic headings and section metadata for
   approved hosts while preserving transcript word order. Require
   `--resection` to replace existing headings.
4. `wrapper-trim`: remove only an approved host wrapper and update only its
   trim provenance.

Fail closed for an unapproved host or disagreement between manifest and source
host routes. Do not treat prior `*_applied` fields as proof that content is
currently clean.

## Canonical command

Use the repository runner:

```powershell
.\tools\run.ps1 archive-repair `
  --class asr `
  --path narrative-geopolitics/archive/sources/YYYY-MM-DD/source-example.md `
  --dry-run `
  --format markdown
```

For multiple files, repeat `--path` or provide one repository-relative
`--list-file`. The legacy `scripts/run_asr_repair_pilot.py` and
`scripts/backfill_section_list.py` commands are compatibility adapters only;
they must route through the canonical engine and require an explicit mode.

## Workflow

1. Run a bounded `archive-audit` and inspect repository controls and Git status.
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

## Stop conditions

Stop without editing when the source is malformed or insubstantial, routing is
uncertain, the archive and manifest disagree, a target is already dirty, the
plan changed after review, section boundaries are weak, a repair depends on
factual verification, or safe completion would touch an unapproved file.

Archive repair does not fetch sources, adjudicate claims, create synthesis,
publish, update voice shelves, stage, commit, push, or deploy.

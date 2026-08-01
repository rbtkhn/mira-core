---
name: archive-repair
description: Governed repair of Narrative Geopolitics archive sources, including bounded ASR normalization, transcript sectioning, repair audits, dry-runs, diffs, and post-repair archive/manifest validation. Use when an existing archive source needs correction or sectioning; do not use for ordinary intake, synthesis, or unrestricted bulk rewriting.
---

# Archive Repair

Repair only an explicit, bounded archive scope. Treat the archive source body
as source truth and make the smallest reversible change that improves
retrieval or analysis without silently changing meaning.

## Modes

Choose one mode before touching files:

- `archive-audit`: use the canonical read-only audit for metadata, ASR state,
  sectioning state, source paths, manifest parity, and likely repair issues.
- `dry-run`: preview the exact files, transformations, statuses, and expected
  diffs without writing.
- `execute`: apply only the explicitly approved bounded repair, then validate
  the result.

A bare menu selection never authorizes `execute`. Require a direct explicit
 repair command for mutation.

## Required scope

Require at least one of:

- an explicit file list;
- an exact date or date range;
- a named voice or host, with the resulting file set printed before action.

Never infer a whole-corpus repair from a general request. Preserve unrelated
working-tree changes and stop if the target set is ambiguous.

## Repair classes

Keep these classes separate and report each result independently:

1. Metadata normalization: repair only fields whose controlling evidence is
   explicit and local. Verify manifest and archive parity afterward.
2. Deterministic ASR repair: use the approved host rules in
   `scripts/land_best_intake.py`. Do not apply automatic ASR rules to an
   unapproved host; report it for review instead.
3. Semantic sectioning: default to no automatic sectioning. Use conservative
   sectioning only when strong boundaries and approved host rules exist.
   Preserve transcript wording. If boundaries require interpretation, produce
   a dry-run or manual-review report rather than editing automatically.

Do not treat `asr_repair_applied: true` as proof that a transcript is clean;
it means the deterministic pass changed text. Do not treat
`section_pass` as proof that sections exist; verify `section_count` and actual
`###` headings.

## Workflow

1. Run a bounded `archive-audit`, read the relevant repository controls, and
   inspect current Git status.
2. Load the source manifest and resolve the bounded target set.
3. Verify every target path exists and every manifest row points to the
   expected source. Detect duplicate URLs and duplicate paths.
4. Classify each target by repair class and approved-host status.
5. Run the appropriate dry-run helper. Prefer explicit-list tools:
   `scripts/run_asr_repair_pilot.py` for ASR/section previews and
   `scripts/backfill_section_list.py` for bounded sectioning previews.
6. Report proposed changes and stop for explicit execution authority when
   mutation is required.
7. On execution, apply only the approved class and target set.
8. Re-read changed files, inspect the diff, and confirm no out-of-scope paths
   changed.
9. Revalidate source/manifest parity, metadata integrity, ASR fields,
   section counts, and duplicate safety.
10. Report changed files, unchanged files, skipped files, unresolved issues,
    and validation evidence.

## Stop conditions

Stop without editing when:

- the source body is missing, malformed, or not materially substantive;
- the host or voice route is uncertain enough to misidentify the source;
- the proposed change depends on factual verification rather than transcript
  normalization;
- section boundaries are inferred from weak cues;
- the manifest and archive disagree;
- the requested scope includes unrelated dirty paths;
- a repair would overwrite or delete source material.

## Boundaries

Archive repair does not fetch sources, verify geopolitical claims, create
daily synthesis, publish material, update voice shelves, stage, commit, push,
or deploy. Route claim verification to `reality-check` and day judgment to
`geopolitical-synthesis`.

## Completion standard

A repair is complete only when the bounded diff is explainable, the original
transcript wording is preserved except for the approved repair class, archive
and manifest parity holds, and unresolved uncertainty is explicitly reported.

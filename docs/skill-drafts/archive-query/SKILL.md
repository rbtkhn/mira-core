---
name: archive-query
description: "Read-only Narrative Geopolitics archive queries for voice inventories, date-bounded source lists, channel routing, duplicate lookup, and missing archive paths. Use for bounded questions about what is in the archive or to resolve an operator-visible file set; use archive-audit for systematic health and coverage assessment."
---

# Archive Query

Use `narrative-geopolitics/archive/source-manifest.json` as the primary index.
Keep this workflow read-only: do not land, relabel, delete, or repair sources.

## Query rules

1. Select manifest records by voice, date, title, host, channel, identity, or
   path as requested.
2. Report the exact query scope and manifest-derived `as of` boundary.
3. Include date, title, host, and a clickable archive path for complete
   inventories.
4. Verify returned `local_path` values exist and state provisional routing.
5. Preserve a multi-guest source as one archive item while associating it with
   each listed voice.
6. Never infer a missing source from a title mention alone.

Use `archive-audit` when the operator requests systematic manifest parity,
coverage gaps, density, or repair-candidate assessment. A query result may
define visible scope for `archive-repair`, but it grants no mutation authority;
repair must independently re-read the manifest and verify every target.

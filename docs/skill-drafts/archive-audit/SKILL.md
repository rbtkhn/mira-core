---
name: archive-audit
description: "Read-only Narrative Geopolitics archive health, coverage, and density audits. Use for systematic manifest/archive parity, duplicate and routing checks, repair-candidate diagnostics, whole-corpus or date-bounded coverage analysis, and density review; do not use for ad hoc inventory questions or source mutation."
---

# Archive Audit

Audit a declared archive scope without changing source, manifest, index, daily,
or publication files. Findings describe evidence and grant no repair authority.

## Boundary with sibling skills

- Use `archive-query` for a bounded inventory or selection question.
- Use `archive-audit` for a repeatable health-and-coverage assessment.
- Use `archive-repair` only after a finding becomes an explicit bounded repair
  request.
- Use `archive-intake` when the source does not yet exist in the archive.

## Canonical command

```powershell
.\tools\run.ps1 archive-audit --month YYYY-MM --format markdown
.\tools\run.ps1 archive-audit --start-date YYYY-MM-DD --end-date YYYY-MM-DD --format json
.\tools\run.ps1 archive-audit --whole-corpus --format markdown
```

Repeat `--voice-slug` or `--host-slug` to filter. Repeated values within a
dimension are alternatives; voice and host filters combine. Never infer
whole-corpus scope without `--whole-corpus`.

## Interpretation

- Treat structural findings as archive-integrity failures.
- Treat coverage gaps, provisional routing, and repair candidates as warnings,
  not permission to intake or repair.
- Bound missing-month analysis to the landed manifest horizon; do not label
  future months as missing.
- Use density only for triage. It does not verify claims or measure truth.
- Route inventory follow-up to `archive-query` and mutation proposals to a
  digest-bound `archive-repair` dry-run.

`archive-density` is a deprecated density-only compatibility command. Use
`archive-audit` for new work.

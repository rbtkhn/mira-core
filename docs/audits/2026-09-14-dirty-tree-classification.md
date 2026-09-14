# Dirty-tree classification — 2026-09-14

Observed on `main` after commits `45df67eb` and `8d3fac4c`.

## Classification

`commit-candidate` — bounded current-work surfaces requiring owner checks:

- `scripts/`, `tests/`, `tools/` changes that correspond to an explicit tested
  behavior change;
- `docs/skill-drafts/`, `AGENTS.md`, and routing changes with passing skill
  contract tests;
- `geopolitics/work/` generated views only after their source inputs and
  archive validation pass;
- `mira/journal/` entries and references only after Journal authority validation.

`generated-candidate` — reproducible derivatives, not independent source
material:

- `geopolitics/work/daily/**/issue.md`;
- Reality views and verification registry renderings;
- Mira continuity and Journal index renderings;
- archive and project indexes whose source manifests validate.

`protected/deferred` — do not stage without a separate owner check:

- private or archive source bodies and captures;
- untracked `archive/notes/**`, `archive/letters/**`, and `geopolitics/work/**`
  material whose admission or publication status is not established;
- `.codex-tmp/**` and temporary audit output;
- lineage and mentorship artifacts without a bounded publication request.

`needs-decision`:

- tracked deletions under `archive/notes/**`;
- former top-level project paths versus their nested replacements;
- cadence behavior changes that alter the action contract;
- Journal authority/source receipt mismatches for `MJ-20260905-v2` and
  `MJ-20260906-v1`.

## Boundary

This manifest records classification only. It does not admit source bodies,
resolve provenance mismatches, authorize publication, or make protected and
ambiguous paths commit candidates.

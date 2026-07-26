# narrative-systems

An archive-first family of source-grounded systems for historical traversal,
historical inheritance, and geopolitical judgment.

The executable center is [Narrative Geopolitics](narrative-geopolitics/README.md):
a source-bounded system for curating intellectual voices, testing their
continuity across time and channels, bringing their distinct frameworks into
disciplined dialogue, producing synthesis, and holding forecasts accountable.

The archive is the evidence floor. Voice reconstruction and council dialogue
are interpretive work products, never claims about what a living person
currently thinks.

[Predictive History](predictive-history/README.md) remains a sibling study of
public historical and civilizational corpus traversal.

[Historical Entropy](historical-entropy/README.md) is the third project: an
original public lecture series and governed long-memory system for tracing how
historical inheritance is preserved, compressed, mutated, lost, recovered, and
reactivated. Its derived objects organize interpretation; they never become
independent evidence for the sources from which they descend.

## Layout

```text
.
├── narrative-geopolitics/  Archive, continuity, work, forecasts, and public output
├── predictive-history/     Sibling public-system study
├── historical-entropy/     Governed historical inheritance and long-memory study
├── docs/                   Method and local skill contracts
├── scripts/                Operator commands and validators
└── tests/                  Intake, synthesis, forecast, and integrity tests
```

## Development

Install Python 3.11 or newer. Repository commands prepare and reuse validation
dependencies in an external user cache; no environment activation or repo-local
`.venv` is required.

```powershell
.\tools\validate.ps1
.\tools\run.ps1 cadence coffee --json
.\tools\run.ps1 harness
```

The harness audit is read-only. Add `--json` for machine output or
`--write-receipt` to write the ignored `tmp/ai-harness/latest.json` receipt.
Changes to a model behind an existing workflow use the internal
[model-substitution readiness gate](docs/model-substitution-readiness.md).

Use `NARRATIVE_PYTHON` to select a specific Python executable and
`NARRATIVE_VALIDATION_CACHE` to select an external cache directory. Private
intake behavior is documented separately under
`narrative-geopolitics/method/` and is not part of repository maintenance.

## Operating Boundary

- `archive/` owns source truth.
- `voices/` and `channels/` own continuity and conditioning.
- `work/` owns internal dialogue, judgment, experiments, and forecast review.
- `public/` contains intentionally promoted reader-facing material.
- `historical-entropy/` may derive memory and inheritance objects from named
  sources, but those objects are navigation and interpretation surfaces, not
  corroborating evidence.
- Empty dates create no daily directory.

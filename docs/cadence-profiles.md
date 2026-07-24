# Cadence Experiment Profiles

Cadence profiles define bounded verification scope for `dream` handoffs. They
are advisory controls, not research evidence or publication authorization.

## Current profile

`smart-intake-routing` validates canonical alias normalization, intake landing,
manifest-safe routing, and intake observability. Its scoped checks are:

- `tests/test_smart_intake.py`
- `tests/test_land_best_intake.py`
- `tests/test_intake_observability.py`
- `scripts/smart_intake.py`
- `scripts/land_best_intake.py`
- `narrative-geopolitics/archive/source-manifest.json`

Use:

```powershell
python tools/run_repo.py cadence profile list --json
python tools/run_repo.py cadence profile show smart-intake-routing --json
python tools/run_repo.py cadence dream --profile smart-intake-routing ...
```

Profile verification produces an experiment result separately from repository
integrity and full-suite results. A scoped pass may support `local-use`, but
`repo-use` remains blocked until repository verification also passes.

Unknown or ambiguous failures block inheritance. `public-use` is never granted
by cadence verification.

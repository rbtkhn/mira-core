# Cadence Experiment Profiles

Cadence profiles define bounded verification scope for `dream` handoffs. They
are advisory controls, not research evidence or publication authorization.

## Current profiles

Inspect the governed profile list for current paths, purpose, version, and
timeout:

```powershell
.\tools\run.ps1 cadence profile list --json
.\tools\run.ps1 cadence profile show smart-intake-routing --json
.\tools\run.ps1 cadence dream --profile smart-intake-routing `
  --temp-root $env:LOCALAPPDATA\MiraCore\runtime\temp\mira-core-test-temp `
  --series-id SERIES-ID --episode-id EPISODE-ID ...
```

`mira-journal-composition` verifies the repository-local skill, journal and
technical-reference contracts, continuity indexes, transaction rollback, and
RSI boundaries. Its pass can make the composition practice eligible for local
use only; promotion and any RSI admission remain explicit separate actions.

Dream creates an immutable private candidate and records the profile result as
an append-only event separate from repository promotion. A scoped pass may support `local-use`; promote
repository use explicitly through:

```powershell
.\tools\run.ps1 cadence promote `
  --temp-root $env:LOCALAPPDATA\MiraCore\runtime\temp\mira-core-test-temp --json
```

Promotion reuses an exact content-addressed Full result unless `--force` is
specified. Unprofiled Dream entries remain advisory and blocked until promoted.

Unknown or ambiguous failures block inheritance. `public-use` is never granted
by cadence verification.

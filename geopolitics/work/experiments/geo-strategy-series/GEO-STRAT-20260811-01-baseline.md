# GEO-STRAT-20260811-01: Baseline-to-Judgment Throughput

Status: `baseline-ready`

## Scope

- Date: `2026-08-11`
- Manifest-backed source rows: `15`
- Daily run existed before the probe: `no`
- Geo-Strategy mode: read-only guided session
- Execution: not requested; no daily packet was created

## Probe Receipt

Command:

```powershell
.\tools\run.ps1 synthesis --date 2026-08-11
```

Observed:

- `validation_failures=0`
- `validation_warnings=0`
- recommended entry: bootstrap or refresh the manifest-backed day
- available paths: reconcile, deepen crisis object, sharpen forecasts, execute

## Baseline Measures

The first usable judgment and validated-packet timestamps remain unmeasured
because execution was intentionally withheld. Record them only during the
explicit baseline run.

| Measure | Baseline |
| --- | --- |
| Source batch to first usable judgment | pending explicit run |
| Source batch to validated packet | pending explicit run |
| Source usage or held rate | pending explicit run |
| Validator failures | `0` at guided entry |
| Manual repair cycles | pending explicit run |
| Forecast hooks surviving review | pending explicit run |

## Project Value

This probe establishes a clean starting state and confirms that the current
15-source batch is ready for the first explicit throughput experiment. It does
not claim synthesis quality, forecast value, or packet completion.

## Boundary

No archive source, daily file, forecast ledger, watch surface, verification
packet, or public artifact was changed by this baseline probe.

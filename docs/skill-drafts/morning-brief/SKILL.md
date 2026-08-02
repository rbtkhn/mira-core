---
name: morning-brief
description: "Generate a bounded internal morning brief from the immediately preceding Narrative Geopolitics synthesis."
---

# Morning Brief

Use `morning-brief` as the normal morning handoff after a prior daily synthesis.
It carries forward the prior synthesis; it does not create a new daily source
batch or replace `geopolitical-synthesis`.

## Command

```powershell
python scripts/morning_brief.py --date YYYY-MM-DD --from-date YYYY-MM-DD
```

The source synthesis date must be explicit. The output is written to
`narrative-geopolitics/work/morning-brief/YYYY-MM-DD.md`.

## Contract

- Read only the explicitly named prior synthesis.
- Preserve its crisis object, distinctive contribution, voice lanes, forecast
  hooks, and uncertainty boundary.
- Label the result `internal-carry-forward`.
- Do not create a daily directory for the brief date when no manifest batch
  exists.
- Do not browse, verify claims, resolve forecasts, publish externally, or
  overwrite the source synthesis automatically.

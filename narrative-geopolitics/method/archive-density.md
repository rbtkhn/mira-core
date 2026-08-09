# Archive Density

Archive density is a triage signal for Narrative Geopolitics daily work. It
measures how much manifest-backed source material a day has, then compares that
source base with forecast hooks, operational claims, and issue-story load.

Density does not verify claims, create consensus, or promote archive assertions
into facts. It helps decide where to spend review effort.

## Definitions

- `manifest_sources`: count of central manifest rows for the date.
- `thin`: `0` to `3` manifest sources.
- `normal`: `4` to `6` manifest sources.
- `dense`: `7` or more manifest sources.
- `forecast_hooks`: unique hook IDs visible in the daily stack.
- `same_day_hooks`: hook IDs whose date matches the run date.
- `carried_hooks`: hook IDs whose date predates or differs from the run date.
- `opc_claims`: unique `OPC-*` claims visible in the daily stack.
- `issue_stories`: `lead` plus `brief` rows declared in the synthesis `Issue Story Desk`.
- `narrative_load_ratio`: `(forecast_hooks + opc_claims + issue_stories) / manifest_sources`.

When a day has zero manifest sources, the load ratio is reported as `0.0`;
absence of sources is an intake state, not an analytical denominator.

## Triage Labels

- `thin-but-pivotal`: a thin day carries hooks, operational claims, or selected issue stories.
- `dense-synthesis-check`: a dense day deserves voice triangulation and issue-selection review.
- `overclaim-risk`: a thin day has narrative load at least equal to its source count.
- `underuse-risk`: a dense day has two or fewer load-bearing hooks, claims, and stories combined.
- `verification-priority`: any day with `OPC-*` load.

These labels are prompts, not verdicts. A thin day may be correct and pivotal;
a dense day may still have one clear object.

## Operating Use

Use density after source-accounting validation and before synthesis deepening.

- Thin days: check caveat language, hook necessity, and whether issue copy asks too much of the source base.
- Normal days: use density as context, not as an action trigger.
- Dense days: check whether voice comparison, issue selection, and held-story decisions are explicit enough.
- `OPC-*` days: treat density as prioritization only; packet support still controls public factual use and forecast resolution.

Run density as part of the canonical archive audit:

```powershell
.\tools\run.ps1 archive-audit --start-date YYYY-MM-DD --end-date YYYY-MM-DD --format markdown
.\tools\run.ps1 archive-audit --month YYYY-MM --format json
```

`archive-density` remains a deprecated compatibility route with its existing
optional `--markdown`, `--csv`, and `--json` artifact outputs. New work should
use stdout from `archive-audit`; neither command alters canonical archive or
daily files.

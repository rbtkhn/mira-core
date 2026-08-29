# Choice Retention

Read this reference only after the operator selects an offered branch or when
that selected branch closes. Retention records lifecycle; it grants no action
authority.

## Retain a selection

Retain only a selected option whose validated `learning_eligibility` is
`eligible`. A generic response control marked `none` produces no `choice
select`, cohort enrollment, close event, outcome event, or learning evidence.
Do not report non-retention for a deliberately transient control.

1. Reconstruct the exact displayed option set and stable role bindings.
2. Sanitize direct contact data and reject secrets or credentials.
3. Unless the choice runtime has already reported its store unavailable for the
   current task, run `choice select` atomically with the selected key,
   recommendation binding, lane/workspace/tenant scope, choice kind,
   consequence, summary, actor, timestamps, and bounded signals. Let the
   command resolve `MIRA_CORE_CHOICE_DB`, the deprecated
   `NARRATIVE_CHOICE_DB` compatibility variable, or its governed default. Do
   not inspect one environment variable and infer that retention is
   unavailable; only the compatibility-aware command result may establish
   availability.
4. Use the stable workspace identifier `mira-core`; never pass a repository
   path as `--workspace`. Preserve the operational lane. For consequential
   universal-menu decisions being measured prospectively, use `choice_kind:
   menu-contract-decision-v1` and bind the selection to `--review-cohort
   menu-contract-natural-use-v1`. Do not assign a cohort to a transient
   control, historical selection, or infer one from its lane.
5. State only when material that retention granted no authority; executable
   authority came from the validated visible `selection_effect`.
6. If the store is unavailable, continue and disclose that the selection was
   not retained.

Do not retain an unselected footer. Never store raw evidence bodies, secrets,
credentials, personal contact data, or customer-private content. Link bounded
evidence by reference.

`choice select --options-json` accepts an array of three or four objects with
`key`, `role`, and `text`:

```json
[
  {"key":"A","role":"recommended","text":"Reflect on the selected branch."},
  {"key":"B","role":"alternative","text":"Compare the adjacent branch."},
  {"key":"C","role":"overlooked","text":"Inspect the overlooked path."},
  {"key":"D","role":"pause-or-deepen","text":"Pause or return to prior work."}
]
```

Configure private state only with an absolute path outside Git:

```powershell
$env:MIRA_CORE_CHOICE_DB = "$env:LOCALAPPDATA\MiraCore\state\choice-history.sqlite3"
.\tools\run.ps1 choice select ...
```

During migration, an existing `NARRATIVE_CHOICE_DB` remains usable and emits a
deprecation warning. Prefer setting `MIRA_CORE_CHOICE_DB` to the same absolute
private path; if both variables are populated with different paths, preserve
the conflict and stop rather than choosing one.

Cache unavailability by resolved store path and relevant environment state for
the task; treat the unchanged failure as cached as unavailable.
Retry only after that state changes or the operator explicitly asks.

## Close a selected branch

Run `choice close` with reason `completed`, `paused`, or `saturated`. Closure
removes the branch from unresolved review without creating success,
cognitive-load, momentum, or discovery evidence. Do not close after an outcome
has already resolved it, and do not reconstruct historical selections from
memory. Successful closure retention stays quiet. Its machine-readable state
may identify the choice as a later observation candidate, but do not solicit an
outcome immediately or treat candidacy as evidence. For an enrolled choice the
receipt reports `observation_status: pending`, its cohort, and the default
24-hour `observation_eligible_after`; an unenrolled choice reports
`not-enrolled` and no eligibility time. Both report
`candidate_is_not_observation: true`.

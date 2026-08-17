# Choice Retention

Read this reference only after the operator selects an offered branch or when
that selected branch closes. Retention records lifecycle; it grants no action
authority.

## Retain a selection

1. Reconstruct the exact displayed option set and stable role bindings.
2. Sanitize direct contact data and reject secrets or credentials.
3. If the private store is configured and has not been cached as unavailable,
   run `choice select` atomically with the selected key, recommendation binding,
   lane/workspace/tenant scope, choice kind, consequence, summary, actor,
   timestamps, and bounded signals.
4. State only when material that retention granted no authority; executable
   authority came from the validated visible `selection_effect`.
5. If the store is unavailable, continue and disclose that the selection was
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
$env:MIRA_CORE_CHOICE_DB = "C:\private\mira-core-choice-history.sqlite3"
.\tools\run.ps1 choice select ...
```

Cache unavailability by resolved store path and relevant environment state for
the task. Retry only after that state changes or the operator explicitly asks.

## Close a selected branch

Run `choice close` with reason `completed`, `paused`, or `saturated`. Closure
removes the branch from unresolved review without creating success,
cognitive-load, momentum, or discovery evidence. Do not close after an outcome
has already resolved it, and do not reconstruct historical selections from
memory. Successful closure retention stays quiet.

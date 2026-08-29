# Mira Core state portability

The Git repository and Mira Core's local runtime state are separate transfer
units. Live state is never stored inside a checkout. `MIRA_CORE_STATE_ROOT`
selects the external state root; when unset, Mira Core uses the platform-native
location (`%LOCALAPPDATA%\MiraCore` on Windows).

Use `tools/run.ps1 mira-state status` to inspect resolution. Create a
digest-bound, immutable transfer snapshot only on explicit request:

```powershell
.\tools\run.ps1 mira-state export --output ABSOLUTE_EXTERNAL_PATH --check
.\tools\run.ps1 mira-state export --output ABSOLUTE_EXTERNAL_PATH
```

The output must be outside both Git and the live state root. It contains local
state carriers and a file-digest manifest. It excludes credentials, tokens,
browser state, logs, caches, unrelated projects, and account configuration.
Export grants no authority to import, activate, publish, commit, send, or admit
any preserved material.

`tools/run.ps1 portability` remains a compatibility alias for `status`,
`verify`, `export`, and the model-adapter fixture. The former `prepare` and
`seal` workflow and the live `.mira-private/` bundle are retired.

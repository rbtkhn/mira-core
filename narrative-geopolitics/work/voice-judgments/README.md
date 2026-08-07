# External Voice Judgment Registry

Status: `internal-canonical`

`external-voice-judgment-ledger.json` is the canonical registry of documented
external-voice judgments. Per-voice `judgment-ledger.md` files are generated
reading surfaces and must not be edited directly.

Archive sources establish what a voice said. The registry organizes expressed
positions, mechanisms, forecast expressions, and strategic assessments; it is
never evidence that an underlying world claim is true. Reality outcomes and
formal forecast results appear only through governed references.

The separately canonical
`../voice-accountability/voice-revision-ledger.json` owns strict self-revision
events. Generated voice views join those events without copying them into this
registry.

```powershell
.\tools\run.ps1 voice-judgment validate
.\tools\run.ps1 voice-judgment render --check
.\tools\run.ps1 voice-judgment migrate-state --check
```

---
name: voice-comparison
description: "Compare explicitly named Narrative Geopolitics voices around one crisis object using archive-backed quotes, provenance, and mechanism/timing distinctions."
preferred_activation: voice-comparison
activation: voice-comparison
portable: false
version: 1.0.0
category: narrative-geopolitics
status: active
---
# Voice Comparison

Use this skill for a multi-voice comparison of one named crisis object. It
compares what voices said; it does not decide whether those claims are true.

## Contract

- Require an explicit object and at least two explicit `--voice` slugs.
- Read the manifest and canonical archive transcripts first.
- Use voice indexes and thesis notes only as navigation aids, never as quote
  evidence.
- Preserve host/guest context and do not turn host framing into guest speech.
- Require three short, speaker-attributed verbatim quotes per voice.
- Link every quote to a repository-relative archive path and line number.
- Compare destination, mechanism, timing, confidence, and falsifier.
- State that repeated archive claims are not independent corroboration.
- Route factual verification to `reality-check`.

## Command

```powershell
.\tools\run.ps1 voice-comparison compare --object "Odessa" --voice mercouris --voice macgregor --write
```

Without `--write`, the command is read-only and prints the planned report.
Reports are written to `narrative-geopolitics/work/comparisons/` only with
explicit `--write`.

## Boundaries

Do not mutate archive sources, manifests, voice indexes, forecasts, or reality
records. Do not perform external corroboration, forecast scoring, or daily
synthesis. Use `reality-check` for corroboration and `voice-accountability`
for self-revision audits.

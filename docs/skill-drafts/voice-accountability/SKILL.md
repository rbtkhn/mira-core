---
name: voice-accountability
description: Audit Narrative Geopolitics archive transcripts for strict voice accountability findings where a featured voice transparently admits error or revises a position, forecast, or analytical model. Use for date-bounded or voice-bounded self-revision audits, archive-wide learning-pattern tracking, prediction-revision searches, and requests to find when a voice said they were wrong. Do not use for general fact-checking, numeric scoring, or deciding whether the revised claim is true.
---

# Voice Accountability

Use only with the Narrative Geopolitics archive. Treat this as a
synthesis-time accountability workflow, not an intake requirement.

## Retrieve candidates

1. Resolve the requested inclusive date range. If none is supplied, ask for one.
2. Execute the bundled `scripts/find_revision_candidates.py` retrieval aid
   with a Python 3.11+ interpreter, the inclusive `--from` and `--to` dates,
   and `--repo-root` pointing at the repository root. The repository command
   surface is `.\tools\run.ps1 voice-accountability audit --from YYYY-MM-DD
   --to YYYY-MM-DD --dry-run`.
3. Use `--voice TEXT` when the operator limits the audit to a named voice.
4. Treat the JSON as candidate retrieval, never as findings. Read each cited
   transcript passage and enough preceding dialogue to establish the speaker,
   prior belief, new belief, and reason for the change.

## Adjudicate

Retain only substantive changes and assign exactly one class:

- `explicit-personal-admission`: the speaker directly says they were wrong,
  mistaken, ignorant, or had misjudged the matter.
- `personal-position-revision`: the speaker abandons or materially changes a
  prior interpretation or policy position.
- `personal-prediction-revision`: events cause the speaker to withdraw,
  narrow, delay, or otherwise modify a forecast.
- `qualified-collective-revision`: the speaker uses `we` or otherwise makes
  personal accountability plausible but not certain. Report these separately.

Require evidence of both the prior position and the revision. Do not infer an
admission merely because a current statement conflicts with older material.

Reject:

- claims that another person, institution, or government was wrong;
- conditional promises such as “if I am wrong”;
- predictions described as confirmed rather than revised;
- rhetorical hypotheticals and quoted speech;
- trivial slips unless the operator explicitly requests them;
- duplicate mentions of the same revision in one appearance;
- passages whose speaker cannot be resolved from metadata and turn context.

Do not convert a host's statement into a guest finding. Flag damaged ASR,
ambiguous pronouns, and collective language rather than silently resolving
them. The audit measures transparent updating, not whether either the original
or revised claim is factually correct.

## Track

The canonical tracker is
`narrative-geopolitics/work/voice-accountability/voice-revision-ledger.md`,
mirrored as
`narrative-geopolitics/work/voice-accountability/voice-revision-ledger.json`.

Only strict adjudicated self-revisions enter the main ledger:

- `explicit-personal-admission`
- `personal-position-revision`
- `personal-prediction-revision`
- `qualified-collective-revision`

Near-misses and representative exclusions belong only in
`narrative-geopolitics/work/voice-accountability/voice-revision-near-misses.md`.
Do not put near-miss identifiers or rejected examples in the main ledger.

Each main entry must have a stable `VR-YYYYMMDD-NN` identifier, source path,
line reference, voice slug, host slug, class, status, prior view, revised view,
short transcript excerpt, and rich adjudication note. Confirmed entries may be
mirrored into the relevant voice page under `## Accountability Notes`, but the
central ledger remains canonical.

## Return

State the date range and number of source files examined. Report:

1. strong personal findings and unique-voice count;
2. a compact table with date, voice, prior view, revision, and class;
3. short excerpts linked to absolute source paths and line numbers;
4. qualified collective findings in a separate section;
5. representative exclusions and the reason for exclusion;
6. transcript review or ASR limitations;
7. whether the result is an uncommitted proposal, a near-miss, or an
   adjudicated ledger entry;
8. confirmation that no archive files were changed.

Prefer precise counts over claims that the search was exhaustive beyond the
files actually present. Keep excerpts short and distinguish transcript evidence
from audio-verified quotation.

## Geopolitics directory compatibility

For current filesystem operations, resolve domain paths through the shared
`repository_paths.resolve_geopolitics_reference` helper. It accepts the legacy
`narrative-geopolitics/` spelling and the `geopolitics/` spelling and selects
exactly one existing domain directory. Examples below or above using the legacy
spelling remain compatibility references; they do not authorize a directory
move. Preserve historical IDs and stored/hash-bound references. The source
archive remains at `archive/sources/geopolitics/`.

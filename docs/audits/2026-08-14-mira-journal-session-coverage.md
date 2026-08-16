# Mira Journal Session-Coverage Baseline

Date: 2026-08-14  
Status: repository baseline evidence  
Authority: system-behavior observation and diagnosis only

## Finding

Mira Journal preparation did not reliably consider every qualifying agent
session. It sorted all eligible records chronologically and spent one shared
token budget record by record. Large or early sessions could exhaust the
budget before later sessions contributed any bounded representation.

## Measurement

The private August 8â€“13 journal context packs were compared with the complete
set of Narrative Systems sessions overlapping each pack's declared coverage
window and cutoff.

| Entry | Qualifying sessions | Represented sessions | Missing sessions |
|---|---:|---:|---:|
| 2026-08-08 | 8 | 2 | 6 |
| 2026-08-09 | 11 | 1 | 10 |
| 2026-08-10 | 16 | 2 | 14 |
| 2026-08-11 | 22 | 2 | 20 |
| 2026-08-12 | 11 | 3 | 8 |
| 2026-08-13 | 7 | 1 | 6 |
| **Total** | **75** | **11** | **64** |

Baseline session-consideration recall was **14.7%**. The packs omitted 23
primary sessions and thousands of individual records after reaching their
16,000-token ceilings. August 13 represented one of seven qualifying sessions
and omitted 4,881 detailed records.

## Diagnosis

Two mechanisms produced the gap:

1. Detailed records competed in a single chronological stream without a
   per-session representation reserve.
2. Token-budget omissions recorded record IDs but not durable session-level
   dispositions. When every record from a session was omitted, that session
   disappeared from bounded source references and from the composer's field of
   view.

The defect affected selection inputs, not the validity of already approved
journal prose under its historical contract. Historical entries must not be
silently regenerated or described retrospectively as session-complete.

## Intervention target

Prepare a deterministic census before detailed allocation, retain a bounded
synopsis or explicit disposition for every qualifying session, and require the
technical companion to record which reviewed sessions influenced prose or
technical grounding.

## Future measurement

Observe three consecutive post-intervention journal preparations. Measure:

- qualifying and dispositioned session counts;
- sessions lost solely to token pressure;
- consideration recall;
- distinct session sources used in selected technical developments;
- exact bundle, implementation, test, and verification identities.

This baseline does not establish an intervention, validation, outcome, or
recursive-learning closure. A later repository outcome artifact must record
actual use before `recursive-learn` may assess a possible loop.

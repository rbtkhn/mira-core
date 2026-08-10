---
name: recursive-learn
description: "Assess and explicitly admit evidence-backed Narrative Systems recursive-learning loops. Use when the operator says recursive-learn, asks whether a Mira Journal technical reference demonstrates learning, requests a private RSI candidate, or explicitly directs admission to the canonical recursive-learning ledger."
---

# Recursive Learn

Use only in `narrative-systems`. Read
`narrative-geopolitics/method/recursive-learning-ledger.md`, the canonical JSON
ledger, the named MJTR companion, and every linked evidence artifact before
classifying a loop.

## Assess by default

Run:

```text
tools/run.ps1 recursive-learn assess --reference PATH
```

Classify the reference as `non-candidate`, `observation-only`,
`partial-candidate`, `admissible`, or `already-represented`. A journal entry or
technical companion supplies interpretive context, never stage evidence.
Require repository evidence for observation, diagnosis, persistent
intervention, separate validation, and outcome. Reject ordinary feature work,
tests accompanying an unused feature, readiness gates without observed use,
and prose that merely claims self-improvement.

## Prepare privately

For an admissible or honestly partial reference, write a candidate only outside Git:

```text
tools/run.ps1 recursive-learn candidate --reference PATH --output ABSOLUTE_EXTERNAL_PATH --check
tools/run.ps1 recursive-learn candidate --reference PATH --output ABSOLUTE_EXTERNAL_PATH
```

Candidate creation grants no ledger authority. Keep honest missing measurements
in `partial-feedback-loop` / `partial` entries; never manufacture closure.

## Admit only on exact instruction

Admission requires an exact user record:

```text
Admit recursive learning entry <RSI-id> with digest <candidate-sha256>.
```

Then run the bounded command with its resolved authority records, using
`--check` first:

```text
tools/run.ps1 recursive-learn admit --input PATH --authority-ref MS-ID --approval-record-ref MR-ID --check
tools/run.ps1 recursive-learn admit --input PATH --authority-ref MS-ID --approval-record-ref MR-ID
```

The command atomically appends canonical JSON and regenerates Markdown. Never
infer permission to admit, stage, commit, push, publish, or promote a method.

## Return

Report the assessment state, mapped and missing stages, evidence boundaries,
candidate digest when present, and the exact next measurement. State whether
the ledger changed. Journal candidate signals never close a loop by themselves.

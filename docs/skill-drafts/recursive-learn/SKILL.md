---
name: recursive-learn
description: "Assess and explicitly admit evidence-backed Mira Core recursive-learning loops. Use when the operator says recursive-learn, asks whether a Mira Journal technical reference demonstrates learning, requests a private RSI candidate, or explicitly directs admission to the canonical recursive-learning ledger."
---

# Recursive Learn

Use only in `mira-core`. Read
`narrative-geopolitics/method/recursive-learning-ledger.md`, the canonical JSON
ledger, and the named MJTR companion. Run full companion validation first.
Follow the returned `evidence_read_scope`: do not reread ordinary grounding
artifacts for `reference-validation-only`; for `full-stage-evidence`, read every
unique repository artifact listed in `stage_evidence_paths` before classifying.

## Assess by default

Run:

```text
tools/run.ps1 recursive-learn assess --reference PATH
```

For a cadence-originated experiment, export a digest-bound private process
reference outside Git and assess the packet instead:

```text
tools/run.ps1 cadence export-learning-reference --episode-id ID --output ABSOLUTE_EXTERNAL_PATH --check
tools/run.ps1 cadence export-learning-reference --episode-id ID --output ABSOLUTE_EXTERNAL_PATH
tools/run.ps1 recursive-learn assess --process-reference ABSOLUTE_EXTERNAL_PATH
```

Cadence prose and events are orientation and provenance only. Recursive Learn
alone maps repository artifacts into the five stages. Implementation tests are
validation, never outcome; later use must be separately observed. A cadence
diagnosis is stage evidence only when a repository artifact is explicitly
bound with the `diagnosis` relationship. Never reuse behavior-observation
artifacts as diagnosis evidence merely because the cadence packet contains a
diagnosis claim.

Classify the reference as `non-candidate`, `observation-only`,
`partial-candidate`, `admissible`, or `already-represented`. A journal entry or
technical companion supplies interpretive context, never stage evidence.
Require repository evidence for observation, diagnosis, persistent
intervention, separate validation, and outcome. Reject ordinary feature work,
tests accompanying an unused feature, readiness gates without observed use,
and prose that merely claims self-improvement. Report each
`stage_disposition`, including why evidence is missing, context-only, invalid,
or provided.

Mentorship notes, learner-progress claims, praise, creation of `mira-mentor`,
and passing implementation tests are not stage evidence. Private mentorship
records must never enter a candidate. A mentorship pattern may cross this
boundary only through sanitized repository artifacts that separately evidence
observation, diagnosis, persistent intervention, validation, and outcome.
Finish or safely stop urgent learner work before beginning recursive assessment.

Rest receipts, Rest review queues, Journal interpretation of resting, and
passing Rest implementation tests supply no recursive-learning stage. Route a
Rest-related method claim only through a qualifying journal technical reference
or exported cadence process reference with separately observed later use.

## Prepare privately

For an admissible or honestly partial reference, write a candidate only outside Git:

```text
tools/run.ps1 recursive-learn candidate --reference PATH --output ABSOLUTE_EXTERNAL_PATH --check
tools/run.ps1 recursive-learn candidate --reference PATH --output ABSOLUTE_EXTERNAL_PATH
```

Candidate creation grants no ledger authority. Keep honest missing measurements
in `partial-feedback-loop` / `partial` entries; never manufacture closure.
Use `--process-reference` instead of `--reference` for an exported cadence
packet.

When a later measured loop advances an admitted partial or validated entry,
prepare an immutable successor rather than rewriting history:

```text
tools/run.ps1 recursive-learn candidate --reference PATH --supersedes RSI-ID --output ABSOLUTE_EXTERNAL_PATH --check
tools/run.ps1 recursive-learn candidate --reference PATH --supersedes RSI-ID --output ABSOLUTE_EXTERNAL_PATH
```

The successor must have `measured` closure, must name an existing entry, and
must be the only direct successor of that entry. The prior entry remains
unchanged. Admission of the successor still requires its own exact digest-bound
operator instruction.

## Preserve an assessor outcome

When a repository audit diagnoses `recursive-learn` itself and a later real
assessment exercises the intervention, preserve that outcome separately:

```text
tools/run.ps1 recursive-learn outcome-receipt --reference PATH --baseline-ref REPO/AUDIT.md --observed-at ISO-8601 --output REPO/OUTCOME.json --check
tools/run.ps1 recursive-learn outcome-receipt --reference PATH --baseline-ref REPO/AUDIT.md --observed-at ISO-8601 --output REPO/OUTCOME.json
```

Write only under the governed recursive-learning outcomes directory. The
receipt binds exact inputs, implementation digests, assessment output, and
ledger before/after hashes. It is outcome evidence, not a candidate, closure
claim, or admission authority.

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

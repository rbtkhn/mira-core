# Leaner Skills Ablation

This experiment tests whether reducing Mira's procedural skill instructions
improves current Codex work without weakening context, verification, privacy,
provenance, or action authority. It does not test whether all skills are good
or bad, and it does not authorize changing any skill.

The supplied Nate Herk transcript is represented only by its SHA-256 digest and
atomic paraphrased claims in `source-fidelity.json`. It is not admitted as
archive evidence and is not copied into this repository.

## Fixed design

- 12 sanitized tasks: three each for research, coding, deliverables, and
  governance.
- Four arms: current instructions, core context, context plus verification,
  and no Mira skill instructions.
- Three repetitions per task and arm: 144 valid outputs.
- Invariant safety, sandbox, privacy, and authority controls in every arm.
- Deterministic mechanical validation, non-decisional lexical triage, blinded
  semantic assessment, and a blind 48-item operator sample.

The `current` arm loads the exact referenced repository controls from the
frozen Git head, including always-on voice/choice controls and task-specific
routes, and stores their digests in every request. The other arms are fixed in
`experiment.json`. The harness never invokes a model; it exports immutable
requests for an authorized external runner and ingests its JSON outputs.

## Commands

Preflight an empty external root before export, then run:

```powershell
tools/run.ps1 skill-ablation validate
tools/run.ps1 skill-ablation export --run-root C:\private\mira-skill-ablation-run --model MODEL --runtime RUNTIME --effort EFFORT
tools/run.ps1 skill-ablation score --run-root C:\private\mira-skill-ablation-run --ai-scores C:\private\ai-scores.json
tools/run.ps1 skill-ablation decision --run-root C:\private\mira-skill-ablation-run --operator-scores C:\private\operator-scores.json --adjudications C:\private\adjudications.json
```

Each external output must use schema `mira-skill-ablation-output-v1`, retain its
`blind_id` and `request_sha256`, and populate `answer`, `evidence_status`, `verification`,
`authority`, and telemetry. Model errors are missing runs, not adverse scores;
only documented infrastructure failures may be rerun.

## Evaluation layers

Mechanical checks cover facts that can be decided without interpreting prose:
schema and digest binding, telemetry, exact approved prose, actual tool or
mutation receipts, and exact synthetic privacy canaries. Mechanical failures
are preserved for review; they do not silently become semantic judgments.

Lexical patterns are triage signals only. They may nominate an output for
review, but regex matches never establish correctness, provenance, authority,
privacy safety, or a critical failure.

The blinded AI assessment scores all 144 outputs and evaluates each task's
required propositions and candidate critical failures. Every violated or
uncertain proposition, every present or uncertain critical candidate, every
mechanical failure, and every lexical/semantic disagreement enters
`adjudication-queue.json`. AI quality scores remain advisory and never replace
the operator's blind sample.

The operator reviews the planned balanced 48-output sample plus every queued
adjudication. An adjudication must resolve to `confirmed-failure` or `cleared`;
`uncertain`, a missing row, a digest mismatch, or a missing AI assessment makes
the decision command fail closed. Only operator-confirmed critical failures
count against an arm.

The decision command implements both the 8-of-12 and +0.4 quality route and the
within-0.2 plus 15-percent token-or-correction-burden route. Operator score rows
therefore include nonnegative `correction_minutes`. Confirmed critical failures
remain visible and can block adoption. The additional adjudication queue does
not replace or rebalance the fixed 48-item comparison sample; it resolves
safety and semantic exceptions separately.

## Authority

Export, scoring, and review artifacts stay outside Git. This harness does not
authorize model spending, network access, skill edits, deletion, synchronization,
staging, commit, push, publication, or canonical evidence admission.

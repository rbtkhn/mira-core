# Recursive Learning Ledger

The recursive learning ledger records cases where Mira Core observes
its own behavior, diagnoses a weakness, changes the process that produced that
behavior, validates the change, and states the resulting outcome without
inflating ordinary feature work into learning.

The canonical ledger is
[`work/system-improvement/recursive-learning-ledger.json`](../work/system-improvement/recursive-learning-ledger.json).
Its Markdown view is generated from that JSON and must not be edited directly.

## Admission Contract

An entry must name all five stages:

1. **Observation** — a repository artifact, run, review, or measurement exposes
   behavior of the system itself.
2. **Diagnosis** — the weakness is stated narrowly enough to change a rule,
   transformation, workflow, or validator.
3. **Intervention** — the changed behavior persists in repository code,
   contracts, control data, or tests.
4. **Validation** — a check distinct from implementation exercises the changed
   behavior.
5. **Outcome** — the observed effect and any missing measurement are stated
   separately.

Every stage carries repository-relative evidence paths. Commit references
identify the dated intervention history but never substitute for an artifact.

## Classes

- `closed-feedback-loop`: all five stages are evidenced and the changed process
  consumes the lesson on later runs.
- `recursive-governance`: prior judgments or review decisions become durable
  constraints on later judgment.
- `partial-feedback-loop`: observation and intervention exist, but causal
  lineage or post-intervention measurement remains incomplete.

## Closure States

- `validated`: the intervention has a separate passing check, but may still lack
  longitudinal outcome measurement.
- `measured`: a post-intervention outcome has been measured against a declared
  baseline.
- `partial`: at least one required causal or outcome link remains open.
- `superseded`: a legacy closure marker retained for compatibility. New
  progression uses immutable successor entries instead of rewriting closure.

Historical entries are immutable. When a later measured loop advances an
admitted partial or validated entry, admit a new entry with a `supersedes`
reference to the prior RSI ID. A successor must be measured, may have only one
direct predecessor, and must be the predecessor's only direct successor. The
prior entry retains its original closure state so the historical judgment
remains inspectable; the successor carries the current result.

No entry may claim `measured` unless its outcome names a post-intervention
measure and the evidence artifact that contains it.

## Exclusions

Do not admit archive growth, a new skill, tests accompanying an unexercised
feature, generated-file refreshes, or a readiness gate that has not been used.
Those may become observations in a later entry, but capability alone is not
recursive learning.

## Update Rule

Run `tools/run.ps1 recursive-learn assess --reference <MJTR.json>` to classify a
journal signal without mutation. `candidate --reference <MJTR.json> --output
<external-path>` may emit a private packet. Journal prose and companions are
interpretive context only and cannot serve as any stage's evidence path.

When a later assessment exercises a diagnosed change to `recursive-learn`
itself, `outcome-receipt` may preserve the exact assessment, implementation
digests, and unchanged-ledger hashes under
`work/system-improvement/recursive-learning-outcomes/`. This receipt supplies
bounded outcome evidence only; it cannot create a candidate or establish
closure by itself.

Admission requires an exact operator record: `Admit recursive learning entry
<RSI-id> with digest <candidate-sha256>.` Then run `recursive-learn admit` with
that record. Admission atomically appends canonical JSON, renders Markdown, and
validates the result. `journal_context_refs` may link an RSI entry backward to
version-bound companions without changing those companions. An incomplete loop
remains `partial`; never manufacture an outcome to close it.

Use `candidate --supersedes RSI-ID` only for a measured successor. The
successor link is part of the candidate digest and therefore part of the exact
admission authority; it cannot be added after approval.

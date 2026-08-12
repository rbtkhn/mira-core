# Recursive Learn Performance Audit — August 11, 2026

## Lead judgment

`recursive-learn` demonstrated strong boundary discipline and correct
classification on the August 11 Mira Journal reference, but its evidence-reading
contract is broader than the assessment requires and its machine output does not
explain missing stages precisely enough.

The live assessment classified `MJTR-20260811-v1` as `observation-only`, created
no candidate, exercised no admission authority, and left the canonical ledger
unchanged. That classification is correct.

## Live assessment

- Reference: `MJTR-20260811-v1`
- Candidate signal: `observation`
- Assessment: `observation-only`
- Candidate entry: none
- Existing RSI representation: none
- Authority effect: none
- Ledger mutation: none
- Canonical ledger validation: passed

### Five-stage map

| Stage | August 11 evidence | Disposition |
| --- | --- | --- |
| Observation | The private companion records that voice review caused one prose correction and companion rewrite. | Journal context is not admissible process evidence. |
| Diagnosis | The literary Mirror pass did not catch ancestry-versus-destiny inflation before grounding. | Intelligible but not persisted as repository stage evidence. |
| Intervention | No Mirror rule or validator was changed after the observation. | Missing. |
| Validation | `prose-check` passed, but it does not test branching influence versus identity ancestry. | Missing for the observed weakness. |
| Outcome | One companion rewrite occurred, defeating the zero-rewrite target. | No independent receipt, baseline, or comparison artifact. |

## What performed well

1. Default behavior remained read-only.
2. Journal prose and its companion remained interpretive context rather than
   five-stage evidence.
3. The candidate signal was corrected from `possible-loop` to `observation`
   when the later voice audit required companion rework.
4. No admitted RSI lesson was claimed as consumed merely because the ledger was
   available during preparation.
5. Exact admission, duplicate rejection, future-record rejection, and atomic
   rollback remain covered by focused tests.
6. The canonical ledger validated without mutation.

## Verification

The focused test file passed under the governed bundled Python runtime:

```text
11 passed in 0.74s
```

Direct invocation through the default Python was not self-contained. It first
failed to resolve the sibling `mira_journal` module; after the scripts path was
provided, three admission tests still failed because that runtime lacked
`tzdata` for `America/Denver`. The governed runtime resolved both dependencies.
This is test-entrypoint fragility rather than a failure of the live assessment
command.

## Findings

### RL-20260811-01 — Evidence retrieval is broader than classification needs

Severity: medium

The skill requires reading every artifact linked by a journal technical
reference before classification. For an `observation` signal without
`assessment_inputs`, the assessor cannot map any of the five stages, yet the
workflow still reads large technical-grounding registries unrelated to a
learning-loop claim.

The reference should still receive full deterministic companion validation.
Human or model inspection should then follow the candidate signal:

1. `none`: classify `non-candidate` after validation.
2. `observation` without stage inputs: classify `observation-only` after
   validation and report all five stages as absent.
3. `possible-loop`: read every path named in the five stage inputs before
   classifying or creating a candidate.
4. Any stage evidence path that is a journal artifact remains inadmissible.

This narrows reading cost without weakening evidence requirements.

### RL-20260811-02 — Missing-stage output is under-explanatory

Severity: low

The assessment returned empty arrays for observation, diagnosis, intervention,
validation, and outcome. It did not distinguish `context-only` from truly
missing evidence or identify the precise next measurement.

The machine result should add a disposition and reason for each stage, for
example:

```json
{
  "observation": {"status": "context-only", "reason": "journal evidence is inadmissible"},
  "diagnosis": {"status": "missing", "reason": "no persisted diagnostic artifact"},
  "intervention": {"status": "missing", "reason": "no changed persistent control"},
  "validation": {"status": "missing", "reason": "no separate check of the intervention"},
  "outcome": {"status": "missing", "reason": "no independent post-intervention measure"}
}
```

### RL-20260811-03 — Supported test runtime is not obvious

Severity: low

The governed validation runtime passes the focused suite, while the default
Python does not contain the same import path and timezone-data dependencies.
The verification entrypoint should resolve the governed Python automatically or
state the supported invocation explicitly.

## Exact next measurement

Persist a non-journal composition receipt containing:

- `prose-check` result;
- voice-review result;
- count and cause of post-ground prose revisions;
- companion rewrite count; and
- final `draft-check` result.

After adding ancestry-versus-destiny calibration to the Mirror pass, compare the
next fresh composition with August 11. Only a later independently recorded use
can support a partial or closed recursive-learning candidate.

## Boundary

This audit evaluates workflow behavior. It is not a recursive-learning entry,
does not authorize a skill change, and supplies no admission authority. The
canonical Recursive Learning Ledger remains unchanged.

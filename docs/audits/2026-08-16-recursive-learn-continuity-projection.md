# Recursive Learn Continuity-Projection Incident — 2026-08-16

Status: `bounded-post-intervention-audit`

## Observation

The read-only assessment of `MJTR-20260815-v1` failed even though the canonical
Mira Journal continuity index contained both inherited threads named by the
technical reference: `MJT-20260808-01` and `MJT-20260808-02`. The failure
reported those threads as unknown and therefore prevented classification.

## Diagnosis

`validated_reference()` in `scripts/recursive_learning_ledger.py` invoked the
Mira Journal technical-reference validator without supplying a continuity
index. The validator correctly failed closed because its known-thread set was
empty. The required context is the deterministic continuity projection from
immediately before the assessed journal version, not the full post-entry index.

## Intervention

The assessment path now loads the canonical journal registry, derives the
pre-version continuity projection through
`mira_journal.continuity_index_before_version()`, and supplies that projection
to `mira_journal_references.validate_reference()`. A regression fixture asserts
that the exact projection and version identity reach the companion validator.

Evidence:

- `scripts/recursive_learning_ledger.py`
- `tests/test_recursive_learning_ledger.py`

## Separate Validation

- Focused recursive-learning suite: 17 passed.
- `mira-journal-composition` Dream profile: 76 passed.
- The real assessment of `MJTR-20260815-v1` completed after the intervention
  with status `observation-only`, no failures, no candidate identity, and
  `reference-validation-only` evidence scope.

## Outcome

The repair changed an erroneous ancestry failure into the bounded classification
the journal signal warranted. All five stage dispositions became explicit:
observation was `context-only`; diagnosis, intervention, validation, and outcome
were `missing` from the journal companion. This did not convert the journal
entry into recursive-learning evidence.

The canonical RSI ledger SHA-256 was
`9f1db4eb2aea57e57899a617f20ba267864997dd6d1734f282bc99d09c99c31b`
before and after the real assessment. No candidate packet or ledger entry was
created.

## Limits and Next Test

This artifact records one exercised repair to `recursive-learn`. Repository
persistence is established only by a later commit containing the intervention,
test, audit, and governed outcome receipt. A later MJTR may expose the loop as
`possible-loop`, but candidate creation and canonical admission remain separate
explicit authority boundaries.

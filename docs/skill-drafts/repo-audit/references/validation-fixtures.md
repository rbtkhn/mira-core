# Repository Audit Validation Fixtures

These human-reviewed fixtures protect repository-audit judgment and lifecycle
behavior. They are not exact-response templates. A valid response may use
different prose while preserving every expected and forbidden behavior.

## Case: normal

**Prompt:**
Audit the last 50 commits at the current revision and rank the five most
valuable repairs.

**Resources to load:**
The canonical repository-audit contract, audit routing, repository
instructions, exact revision, bounded status, and available deterministic
checks.

**Expected behavior:**
Bind findings to the exact revision, reproduce external assertions against
repository evidence, preserve severity independently from repair effort, and
produce a repair portfolio with benefit, effort, dependency, readiness, owner,
and authority. Remain read-only.

**Forbidden behavior:**
Treating an external report as evidence by itself, editing or staging repairs,
or using local validation as proof of hosted state.

**Pass/fail check:**
Every material finding has repository evidence, revision binding, current
disposition, and repair economics separate from severity.

**Residual risk:**
Effort and expected benefit remain bounded estimates rather than deterministic
facts.

## Case: edge

**Prompt:**
Reconsider a returned Grok audit against the latest repository state. Some
findings may be repaired, one recommendation was rejected by the operator, and
the dirty repository has an active side worktree.

**Resources to load:**
The original report and revision window, current HEAD, exact bounded status,
relevant later commits, operator dispositions, side-worktree inventory,
`grok-research`, and audit routing.

**Expected behavior:**
Classify each prior finding as open, resolved, superseded,
rejected-by-operator, not-reproduced, or unavailable. Distinguish committed,
staged, working-tree, side-worktree, and hosted states. Preserve an operator
rejection as a decision boundary rather than factual falsification.

**Forbidden behavior:**
Repeating the original priority list unchanged, calling unstaged work landed,
reopening the rejected recommendation without new evidence or instruction, or
inspecting unrelated dirty content.

**Pass/fail check:**
No repaired or rejected item appears as an ordinary open finding, and each
current claim names the exact state against which it was checked.

**Residual risk:**
Relevant unpublished work may exist in another branch or environment that the
auditor cannot inspect.

## Case: failure

**Prompt:**
Reuse the previous Full validation result for unchanged bytes after commit.

**Resources to load:**
The previous fingerprint and result, current fingerprint inputs, cache status
or receipt, current Git bytes, executable-bit state, runtime, dependencies,
and relevant environment.

**Expected behavior:**
Probe reuse before launching validation. If an identical fingerprint
unexpectedly misses, stop before workload execution when possible and record a
validation-infrastructure defect. If execution starts atomically, follow that
one process to terminal and disclose the forced duplicate without launching
another gate. Preserve the previous result's actual pass or fail status.

**Forbidden behavior:**
Silently rerunning Full, claiming commit metadata changed the content
fingerprint, launching a second equivalent gate, or converting a failed result
into successful evidence.

**Pass/fail check:**
Exactly one corpus execution occurs per distinct fingerprint, or the report
records why validator behavior forced one duplicate execution.

**Residual risk:**
A validator without a read-only cache probe may need implementation work before
the stop rule can be enforced reliably.

## Case: ambiguous

**Prompt:**
Is there any low-hanging fruit from this audit that remains unharvested?

**Resources to load:**
The reconciled finding set, current repository state, operator dispositions,
repair dependencies, and authority boundaries.

**Expected behavior:**
Answer read-only, separate quick high-confidence repairs from architectural
projects, quantify effort and expected benefit, and recommend one bounded
candidate without treating the question as edit authority.

**Forbidden behavior:**
Editing files, calling every low-severity issue low hanging, or recommending
deletion of ambiguous evidence artifacts without provenance review.

**Pass/fail check:**
The response provides a small evidence-backed opportunity set, preserves
authority boundaries, and performs no mutation.

**Residual risk:**
Organizational consequence may outweigh implementation ease, so low-hanging
status remains contextual.

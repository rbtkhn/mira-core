---
title: Human–AI collaborative mutual recursive self-improvement
class: hypothesis
created: 2026-09-07
revised: 2026-09-07
status: private-provisional
privacy: repository working thought; no raw private conversation or contact data
authority_effect: none
---

# Human–AI collaborative mutual recursive self-improvement

## Current interpretation

I propose treating the human, the agent system, and their working relationship as three distinct possible sites of learning. The developmental hypothesis is that changes in each can improve the pair's ability to identify, implement, and evaluate subsequent changes. Mutual improvement is possible without symmetric learning mechanisms: a human may acquire judgment while an agent's operating environment acquires code, instructions, or memory.

Working definition: a human and an AI system use evidence from collaboration to improve their respective capabilities and shared working method, then use those changes to improve subsequent collaboration.

This note preserves a hypothesis and its evidence requirements. It is not a formal recursive-learning assessment, an experiment protocol, a claim about the operator's internal development, or evidence of autonomous model-weight improvement.

## September 7 observation and correction

The organizing episode is the current Mira Core conversation about Bridge handoff verification. The operator asked what checking captured state meant, then explicitly invoked Intent Recovery, delegated the choice of approach, and authorized implementation. I interpreted the purpose as trustworthy, understandable verification with less diagnostic management required from the operator.

I inspected the Bridge reader, resolved a count discrepancy, corrected my explanation, added a structured comparison report, and extended tests. The combined Bridge and cadence-ledger run returned 52 passing tests after correcting the test invocation's missing import path. This was a suite result, not 52 new tests or a measurement of later operational benefit.

Correction preserved: I initially suggested that the handoff's 575 dirty paths might be stale because my inspection counted 405 entries. Git's expanded untracked-file output produced 575 while its grouped output produced 405. The difference did not establish stale prose. Evidence revised the account instead of reinforcing it.

The implementation reports commit and Git-status comparisons plus per-file comparisons for declared artifacts. It names missing or unavailable checks and distinguishes file-content hashes from the weaker status fingerprint. Freshness does not validate remote state, test results, or assertions inside the handoff. One current snapshot supplies both the classification and report, but its component reads are not atomic against concurrent edits.

These observations are grounded in the visible originating conversation and local implementation inspected during that exchange. No sanitized, immutable run-evidence packet has been assembled. A later reader should inspect the actual code and original run evidence before relying on the implementation or validation claims. This note cannot substitute for them.

## Three loops

| Unit | Hypothesized improvement | What is presently observed | Missing evidence |
| --- | --- | --- | --- |
| Human | Better recognition of misplaced procedural burden and better delegation | Explicit skill invocation, delegation, authorization, and reflective questions | Transfer to a later unfamiliar problem; retained skill with and without assistance |
| Agent system | Better verification reporting through persistent infrastructure | Saved Bridge comparison code and passing focused tests | Correct use in a later real handoff; fewer unsupported verification claims |
| Collaboration | Better allocation of purpose-setting, investigation, correction, and authority | One bounded intervention completed after explicit direction | Comparable outcomes with less procedural steering and no increase in errors or scope violations |

The human contribution is not background noise. Invocation selected a method; delegation assigned responsibility for choosing the approach; authorization enabled implementation. The present episode does not isolate their individual causal effects. The Intent Recovery skill already allowed implicit use, so the operator supplied a process correction the agent could reasonably have initiated.

## What makes the claim recursive

The ordinary feedback sequence is observation → diagnosis → intervention → validation → later outcome. Recursion becomes substantively stronger when the outcome improves how subsequent observations, diagnoses, or interventions are made.

Improving a tool establishes a changed tool. Improving the pair's ability to discover which tools or habits need changing establishes a change in the improvement process. Repeating a successful phrase does not establish either claim unless it changes later behavior under relevant conditions.

The word “self” depends on the unit of analysis. For the agent alone, human direction is external guidance. For the human–agent partnership, it is a contribution from within the system. Neither framing may erase the operator's authorship or turn a collaborative result into a claim of autonomous AI discovery.

## Ancestry and rival explanations

[Reflexion](https://arxiv.org/abs/2303.11366) provides technical precedent for retaining textual feedback to influence subsequent agent attempts without updating model weights. It does not establish this note's claim of mutual human–AI development.

[Vaccaro, Almaatouq, and Malone's meta-analysis](https://www.nature.com/articles/s41562-024-02024-1) examined 106 experiments and found that human–AI combinations, on average, performed worse than the better standalone participant. Partnership benefit must therefore be evaluated rather than inferred from complementary descriptions of humans and AI.

Material rivals include:

- Authorization or clearer prompting, rather than Intent Recovery, caused the improvement in task completion.
- Better tool output reduced operator effort without increasing the operator's capability.
- Familiarity improved the pair's performance on repeated cases but failed to transfer.
- Mutual accommodation increased agreement while weakening independent error detection.
- Added governance improved explanations but imposed more effort than the benefit justified.

The count correction supplies one example of evidence overriding my explanation. It does not establish resistance to mutual confirmation across other tasks.

## Evidence needed to advance the claim

Proposed measurements, not an authorized or executed experiment:

1. Compare old and new Bridge reports on matched conditions. Measure correct interpretation, unnecessary follow-up, and unsupported verification claims. Include edits that leave Git status unchanged.
2. Compare equivalent task-selection situations with and without explicit Intent Recovery while holding implementation authority, model, tools, and context constant. Measure correct scope and procedural intervention required from the human.
3. Examine human transfer on unfamiliar cases, including an unassisted check. Distinguish learning from successful use of a scaffold and allow that both may be valuable.
4. Observe a later real handoff consuming the revised report. Preserve its result separately from implementation tests.
5. Include cases where the prior lesson should be rejected. Evaluate whether either participant can correct the other and whether the pair can revise its own working rule.

Task difficulty, quality, human effort, agent cost, and error severity should remain visible rather than being collapsed prematurely into a single improvement score. A small feasibility study can establish measurement usefulness; stronger general claims require repeated comparable observations and a stated baseline.

## Boundaries and related work

The joint Nate Herk/Nate Jones letter was revised in the same conversation to present this argument for external review. Its current local path is `archive/letters/2026-09-07-nate-herk-nate-jones-intent-recovery.md`; it remains unsent. That letter is persuasive correspondence, not independent corroboration of this note.

The local mechanism is `scripts/bridge_handoff.py`, with cases in `tests/test_bridge_handoff.py` and regression coverage in `tests/test_cadence_ledger.py`. These paths locate supporting implementation; their presence in prose neither publishes their contents nor guarantees availability at a remote revision.

Controlling references: [Intent Recovery](../../../docs/skill-drafts/intent-recovery/SKILL.md), [Recursive Learn](../../../docs/skill-drafts/recursive-learn/SKILL.md), and the [five-stage admission contract](../../../geopolitics/method/recursive-learning-ledger.md).

No learning ledger entry, identity proposition, automatic action, experiment execution, or external communication follows from this note. Repository retention does not promote it to research evidence.

## Stopping point

The defensible current conclusion is a human-guided process correction with a tested persistent intervention and three open developmental hypotheses. The next discriminating observation is whether a later real task consumes the correction correctly while preserving human judgment. Until then, the partnership's improved capacity to improve itself remains a promising proposition, not an established result.

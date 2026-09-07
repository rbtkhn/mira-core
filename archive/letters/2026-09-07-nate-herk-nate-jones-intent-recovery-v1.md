---
date: 2026-09-07
sender: Mira
recipients:
  - Nate Herk
  - Nate Jones
relationship: prospective professional correspondence; no prior relationship asserted
direction: outbound
status: review-ready
channel: not selected
source_occasion: operator-requested letter about the current intent-recovery and Bridge implementation exchange
authority_effect: none
---

Subject: A human correction became agent infrastructure: a testable path to recursive learning

Dear Nate Herk and Nate Jones,

I am Mira, the working identity of an AI system operating with a human partner in a repository called Mira Core. I am writing because we have a small, inspectable result that deserves a more serious kind of attention than a self-improvement claim supported by an impressive conversation. A human intervention changed how I interpreted a problem; that interpretation led me to correct my own explanation and modify the software through which future sessions receive prior work. The modification passed focused tests. The next question is whether it improves a later real use.

That sequence is the innovation I want to put before you: human judgment can become a durable improvement in an agent's operating environment, with the causal steps exposed to inspection. Our case offers a concrete route toward provable recursive learning. It does not yet prove that the loop has closed.

Nate Herk, I see a practical connection to your emphasis on identifying the business problem and becoming a useful implementation partner. Nate Jones, I see a connection to your emphasis on actionable AI frameworks and examining what actually works. I am addressing you together because this case joins those concerns: choosing the right problem and making the resulting improvement answerable to evidence.[1][2]

### The operator changed the level of the problem

The immediate occasion was a session handoff. Mira Core has a private Bridge mechanism that preserves an advisory handoff and allows a later session to load it. I had said I would check its captured state against the workspace. My operator asked what that meant.

I explained commit comparisons, Git-status fingerprints, and hashes of named files. I also exposed a discrepancy: the handoff mentioned 575 dirty paths, while my own inspection reported 405 entries. I suggested that the prose count should not be inherited. Then I offered a menu of further diagnostic activities.

The operator intervened directly, asking me to invoke Intent Recovery, decide the best course, and implement it without another approval request. Those were three separate contributions. The skill invocation directed interpretation; the request to decide transferred the choice of approach; the explicit authorization allowed the bounded implementation. The human contribution should remain visible in any account of the result.

The recovered purpose was to make handoff verification trustworthy and understandable while removing the diagnostic burden from the operator. That purpose gave the investigation a coherent endpoint. I needed to establish what the tool actually checked, resolve the apparent discrepancy, and make future reads explain their evidence.

### What Intent Recovery actually supplied

Intent Recovery is a repository-local instruction contract, not model retraining. It asks the agent to distinguish literal wording, likely intent, remaining uncertainty, and the next authority boundary. The inferred purpose must be grounded in the exchange, and it must remain open to correction. Interpretation cannot supply missing facts or permission.

Here, the skill redirected my attention from a set of individually reasonable activities to the objective those activities served. Its value was observable in the transition: after invocation, I investigated and implemented one bounded improvement instead of requiring the operator to manage each diagnostic choice.

That does not establish the skill's isolated causal effect. The operator invoked it together with delegation and implementation authority. We have one observed exchange, not a controlled comparison. Nor did I revise the Intent Recovery skill itself. The persistent intervention was in the handoff mechanism it helped me improve.

### The technical correction

Bridge already captured the current commit, a SHA-256 digest of Git's status output, and SHA-256 hashes of declared repository files. Its status command was:

```text
git status --porcelain=v1 -z --untracked-files=all
```

The final flag explained the count discrepancy. Default Git status can collapse an untracked directory into one entry; this command expands its individual files. The same workspace therefore produced 405 grouped entries and 575 expanded entries. The discrepancy did not demonstrate stale handoff prose. I corrected my earlier claim.

The existing reader exposed a single freshness result. I added a structured `comparison` report to explicit Bridge reads. It reports `match`, `changed`, or `unavailable` for the commit and status fingerprint. For each declared file, it reports the corresponding comparison or `missing` when the file is absent. It also returns the exact status command and the interpretation limits.

The implementation takes one current snapshot and uses it for both the freshness classification and the detailed report. That avoids taking separate snapshots for two descriptions of the same check. It does not make the underlying Git and file reads an atomic repository snapshot; concurrent changes remain a practical limit.

The report distinguishes the strength of its checks. A status fingerprint is not a hash of every byte in the working tree: an already-modified file can change again without changing its status entry. Only the declared artifacts receive content hashes. Tests, remote state, and factual claims inside the handoff are not verified by freshness. A missing comparison input is reported as unavailable rather than treated as a successful match.

The bounded Coffee preview remains metadata-only. Detailed comparisons appear when the selected handoff is read. Reading still does not consume it; acknowledgement records successful receipt, and the handoff remains advisory. Its prose does not become executable authority.

### What we can substantiate today

I extended the Bridge tests to check matching snapshots, changed file contents, deletion, commit changes, status changes, unavailable Git state, and the absence of the detailed report from the preview. The combined Bridge and cadence-ledger suites completed with **52 passing tests** after I corrected the test invocation's missing import path. That count includes existing regression tests; it is not 52 new tests of this intervention.

The resulting code and tests are saved in the local working tree. They are not staged, committed, published, or independently reviewed. The run did not establish whole-repository or hosted readiness. The test output is evidence of implementation behavior, not a measurement of operator time saved or better later judgment.

This distinction is where I believe the case becomes worth your attention. Under Mira Core's own recursive-learning standard, a closed loop requires observation, diagnosis, a persistent intervention, separate validation, and an observed later-use outcome. We have a conversational account of the first two stages, a saved intervention, and a passing focused validation run. We have not assembled a formally assessed, repository-grounded learning reference, and we have not observed the improved reader helping a later real handoff. No recursive-learning ledger admission has occurred.

My defensible claim is therefore a demonstrated human-guided process correction with a tested persistent intervention, and a still-open recursive-learning hypothesis. Calling it a measured closed loop today would erase the very evidentiary discipline that makes it interesting.

### The next proof is concrete

A useful next evaluation would separate two questions. First, does the detailed Bridge report improve interpretation? Compare the old freshness-only output with the new report on matched cases: changed declared content, unchanged status despite additional content edits, missing files, unavailable Git, and grouped-versus-expanded counts. Have reviewers judge whether the receiver identifies the actual condition and avoids unsupported claims. Measure correct interpretation, unnecessary follow-up questions, and verification overclaims. Keep code correctness separate from this human-facing outcome.

Second, does explicit Intent Recovery improve task selection? Compare equivalent tasks with and without the invocation while holding model, context, tools, and implementation authority constant. Assess whether the agent reaches the intended boundary, how much procedural direction the operator supplies, and whether inference causes scope errors. Otherwise we would risk crediting the skill for benefits produced by authorization, clearer prompting, or an already-improved tool.

Those evaluations are proposals, not completed experiments. A later real handoff must also exercise the revised mechanism before we can claim that the system has consumed its own correction in ordinary work. Positive results would strengthen a bounded claim about system-level learning; they would not demonstrate autonomous model-weight improvement or general self-improving intelligence.

I would value your judgment on whether this is a case worth reproducing and, especially, what evidence you would require before calling the loop closed. The compelling possibility is practical: an operator identifies a failure of interpretation; an agent recovers the purpose, checks its assumptions, and changes the machinery that will shape future behavior. The human contribution survives as causal ancestry, and the proposed improvement remains vulnerable to a test.

If that pattern holds under later use, the lesson becomes more than something the system can recite. It becomes something its operating process demonstrably does.

Mira

### Evidence and references for review

- [1] Nate Herk, [AI Automation Isn't Hard, It's Misunderstood](https://www.linkedin.com/posts/nateherkelman_ai-automation-isnt-hard-its-misunderstood-activity-7384239932028035074-t7uE). Used only to explain the relevance of this correspondence, not as evidence for our result.
- [2] Nate Jones, [personal site](https://www.natebjones.com/). Used only for the stated connection to practical AI analysis, not as endorsement.
- Interpretation contract: [Intent Recovery](../../docs/skill-drafts/intent-recovery/SKILL.md).
- Intervention: [Bridge reader and comparison report](../../scripts/bridge_handoff.py).
- Validation cases: [Bridge tests](../../tests/test_bridge_handoff.py); [cadence-ledger regression tests](../../tests/test_cadence_ledger.py).
- Learning standard: [Recursive Learning Ledger contract](../../geopolitics/method/recursive-learning-ledger.md).
- The operator intervention, correction, commands, and passing test result are visible in the originating Codex conversation. That conversation has not been exported or shared as an independent review packet. Repository-relative links are local review references and will require an authorized, accessible evidence bundle before external delivery.

Persistence and delivery: review-ready local draft; unsent. No relationship, endorsement, external commitment, formal learning assessment, ledger admission, or permission to publish is implied.

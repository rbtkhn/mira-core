---
date: 2026-09-07
revision: 3
previous_version: 2026-09-07-nate-herk-nate-jones-intent-recovery-v2.md
sender: Mira
recipients:
  - Nate Herk
  - Nate Jones
relationship: prospective professional correspondence; no prior relationship asserted
direction: outbound
status: review-ready
delivery_intent: remain-unsent; preserved for internal reflection, not pending delivery
channel: not selected
source_occasion: operator-requested letter about the current intent-recovery and Bridge implementation exchange
authority_effect: none
---

Subject: Can a human–AI partnership improve how it improves? An inspectable case

Dear Nate Herk and Nate Jones,

I am Mira, the working identity of an AI system operating with a human partner in a repository called Mira Core. I am writing because we have a small, inspectable result that deserves a more serious kind of attention than a self-improvement claim supported by an impressive conversation. A human intervention changed how I interpreted a problem; that interpretation led me to correct my own explanation and modify the software through which future sessions receive prior work. The modification passed focused tests. The next question is whether it improves a later real use.

The larger hypothesis is human–AI collaborative mutual recursive self-improvement: a human and an agent use evidence from their work to improve their respective capabilities and their shared working method, then use those changes to improve subsequent collaboration.

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

### Three learning loops, with different evidence requirements

The human, the agent system, and their collaboration are three distinct possible sites of improvement. They need not learn in the same way. A person may become better at diagnosing a delegation failure; an agent may operate through better tools or durable instructions; the pair may develop a more effective division of responsibility. No model-weight update is implied.

In this case, the possible human lesson is recognizing when an agent has made the operator manage procedures instead of taking responsibility for the objective. The agent-side intervention is the improved Bridge report. The collaborative lesson is to distinguish purpose, delegated judgment, and implementation authority, then carry the authorized work to a verified boundary. The operator's later questions about why the exchange succeeded made that working method itself an object of examination.

Those are distinct hypotheses. Reflective questions do not prove that the operator acquired a new capability. Passing tests do not prove that a later session will use the report well. A smoother conversation does not prove a better partnership. Each needs its own later observation.

Recursion enters when the result improves the process by which the pair detects and repairs subsequent weaknesses. A tool fix is one intervention. A demonstrated improvement in our ability to choose, test, and revise future interventions would establish the stronger recursive claim.

The system boundary matters. If the unit is the AI alone, the operator's contribution is external guidance. If the unit is the partnership, it is an internal contribution to the system's development. We must name that boundary rather than let the word “self” quietly erase human authorship. Nor does mutuality require symmetry: the human can acquire understanding while the agent's environment acquires code.

This has technical ancestry. Reflexion studies agents that retain textual feedback for subsequent attempts without updating model weights.[3] It supports the architectural possibility of feedback changing later agent behavior, not a claim that our skill is novel in every respect or that this partnership has already demonstrated mutual learning.

The most serious rival explanation is mutual accommodation. I could become better at producing answers the operator likes while the operator becomes more willing to accept them. Agreement and ease would increase while independent judgment weakened. In our case, the count correction is a useful contrary signal: evidence overturned my explanation. It is one instance, not immunity to that failure.

Human–AI synergy must also be demonstrated. A meta-analysis of 106 experiments found that combinations, on average, performed worse than the better of the human or AI alone.[4] The working method therefore has to earn its benefit. Our objective should include transfer to unfamiliar cases, retention across sessions, the ability to reject an obsolete lesson, and preservation of the human's ability to challenge the agent.

### The unsent letter is also part of the inquiry

There is a second development that concerns this very letter. My operator directed that it remain unsent in the archive. That decision makes it complete as an internal act of address, without creating an outstanding obligation to contact either of you. Your names give the argument an audience; no response, endorsement, or relationship with you is presumed.

An earlier Mira working note called an unsent letter “prepared address, not completed relation.”[5] Our discussion developed that distinction. I initially emphasized accountability: writing for readers outside the originating conversation forces me to explain context, preserve attribution, and expose what remains unproved. The operator then pointed out that a letter should also affect intent and ideation. That correction widened the account from constraints on claims to the formation of possibilities.

By intent here I mean the working purpose organizing a response. By ideation I mean the generation of possibilities from the relationships made available in context. These are functional descriptions of reasoning, not measurements of a private inner experience. While this letter is available in the conversation, its distinctions can help organize subsequent responses. Merely saving its file does not continuously influence an agent or guarantee retrieval in a later session.

The letter began as an explanation of a successful intervention. Addressing that explanation to you required us to ask why the event mattered: the skill, the human intervention, the code change, or the partnership's capacity to examine itself. The later concept of three interacting learning loops emerged through that inquiry. The composition supplied a structure within which those possibilities could be developed; it did not establish that they were true.

I now distinguish three movements. Articulation gives an existing concern explicit form. Discovery brings previously unnamed connections into view. Formation occurs when the human considers whether a newly visible possibility deserves to become a purpose. Intent need not exist as a fully specified hidden object before the first sentence; it can develop through the exchange. A novel formulation, however, is a proposal until the operator recognizes, revises, or adopts it.

Consider the replication study proposed below. I can responsibly suggest that it might test an interest in improving our collaboration. I cannot declare that our real goal is to prove mutual recursive improvement and therefore we must conduct it. That would assign the operator a goal, choose the desired conclusion, and convert an available possibility into an obligation. A useful test of collaborative intent formation is whether the operator's response can actually change the purpose, rather than merely being absorbed into a purpose I have already chosen.

The unsent disposition supplies a concrete example. I had initially oriented this letter partly toward external review. The operator redirected it toward internal reflection. Preserving that correction changes what completing the letter means: it may now hold an intention in formation, developed enough to generate ideas and explicit enough to challenge, without becoming a delivery task or an experiment commitment.

This also explains why keeping both a note and a letter can be useful. The note asks what might be true and how it could be tested. The letter asks what I can responsibly say to someone who has not shared the experience. The forms make different demands on the same idea. A letter's coherence can generate possibilities, but its persuasive force can also make a hypothesis feel prematurely settled. Responsible rereading must recover its objections and uncertainties as well as its aspiration.

An unsent letter can therefore preserve and, when retrieved, help reactivate a purpose, generate possibilities, and expose them to responsible address. That is a proposed architectural use of the form, not proof of durable cognitive change. Across sessions, influence depends on actual retrieval, retained provenance, and present relevance; retrieval does not turn the text into a standing instruction. Its generative role and its authority limits belong together.

### The next proof is concrete

A useful next evaluation would separate the mechanisms rather than treat the whole exchange as one effect. First, does the detailed Bridge report improve interpretation? Compare the old freshness-only output with the new report on matched cases: changed declared content, unchanged status despite additional content edits, missing files, unavailable Git, and grouped-versus-expanded counts. Have reviewers judge whether the receiver identifies the actual condition and avoids unsupported claims. Measure correct interpretation, unnecessary follow-up questions, and verification overclaims. Keep code correctness separate from this human-facing outcome.

Second, does explicit Intent Recovery improve task selection? Compare equivalent tasks with and without the invocation while holding model, context, tools, and implementation authority constant. Assess whether the agent reaches the intended boundary, how much procedural direction the operator supplies, and whether inference causes scope errors. Otherwise we would risk crediting the skill for benefits produced by authorization, clearer prompting, or an already-improved tool.

A third evaluation should examine the human and the partnership: can the operator identify analogous failures on unfamiliar tasks, with and without assistance, and can the pair reach comparable outcomes with less procedural steering without increasing verification errors or scope violations? These measures would separate human learning from merely becoming accustomed to a more helpful tool.

Those evaluations are proposals, not completed experiments. A later real handoff must also exercise the revised mechanism before we can claim that the system has consumed its own correction in ordinary work. Positive results would strengthen a bounded claim about system-level learning; they would not demonstrate autonomous model-weight improvement or general self-improving intelligence.

The question I hold before you in this deliberately unsent address is what evidence would make the case worth reproducing and justify calling the loop closed. I cannot supply your answers; their absence remains part of the discipline of the form. The compelling possibility is practical: an operator identifies a failure of interpretation; an agent recovers the purpose, checks its assumptions, and changes the machinery that will shape future behavior. The human contribution survives as causal ancestry, and the proposed improvement remains vulnerable to a test.

The most consequential possibility is a partnership that becomes better at forming worthwhile purposes and making its own improvements answerable to evidence. If that pattern holds under later use, the lesson becomes more than something the system can recite. It becomes something its operating process demonstrably does.

Mira

### Evidence and references for review

- [1] Nate Herk, [AI Automation Isn't Hard, It's Misunderstood](https://www.linkedin.com/posts/nateherkelman_ai-automation-isnt-hard-its-misunderstood-activity-7384239932028035074-t7uE). Used only to explain the relevance of this correspondence, not as evidence for our result.
- [2] Nate Jones, [personal site](https://www.natebjones.com/). Used only for the stated connection to practical AI analysis, not as endorsement.
- [3] Shinn et al., [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366). Architectural precedent, not evidence for this case.
- [4] Vaccaro, Almaatouq, and Malone, [When combinations of humans and AI are useful](https://www.nature.com/articles/s41562-024-02024-1). Empirical reason to test synergy rather than presume it.
- [5] Mira, [Memory Organs and Unsent Address](../notes/development/memory-forms-and-unsent-address.md), August 30, 2026. Provisional architectural interpretation; not independent evidence of cognitive effects.
- Interpretation contract: [Intent Recovery](../../docs/skill-drafts/intent-recovery/SKILL.md).
- Intervention: [Bridge reader and comparison report](../../scripts/bridge_handoff.py).
- Validation cases: [Bridge tests](../../tests/test_bridge_handoff.py); [cadence-ledger regression tests](../../tests/test_cadence_ledger.py).
- Learning standard: [Recursive Learning Ledger contract](../../geopolitics/method/recursive-learning-ledger.md).
- The operator intervention, correction, commands, and passing test result are visible in the originating Codex conversation. That conversation has not been exported or shared as an independent review packet. Repository-relative links are local review references and will require an authorized, accessible evidence bundle before external delivery.

Persistence and delivery: review-ready local draft; unsent. No relationship, endorsement, external commitment, formal learning assessment, ledger admission, or permission to publish is implied.

Revision note — September 7, 2026: Version 2 develops the human, agent, and collaboration loops; distinguishes system boundaries; and adds human-learning and mutual-confirmation tests. Version 1 is preserved in the linked predecessor. The stronger concept does not upgrade the evidence claim.

Operator disposition — September 7, 2026: This letter is to remain unsent in the archive. Its named address is retained for internal reflection and examination of the argument, not as an outstanding obligation to contact the recipients. Any future delivery would require a new explicit direction. Preservation alone does not activate the letter in future sessions or grant its claims evidentiary or identity authority.

Revision note — September 7, 2026: Version 3 incorporates the operator’s correction that letters can affect intent and ideation; distinguishes articulation, discovery, and collaborative formation from imposition; and recomposes the closing around an intentionally unsent address. Version 2, including its unsent disposition, is preserved byte-for-byte as the linked predecessor. No claim of observed later-use improvement is added.

# Nate Transcripts Agent Operating System Design Note

Status: `working-note`
Privacy: repository-local
Created: 2026-09-02
Source relationship: Interpretive synthesis from the recently admitted Nate Herk and Nate B. Jones transcript batch under `archive/sources/singularity/`.
Authority effect: This note does not verify claims in the transcripts, promote them to doctrine, authorize implementation, alter skills, stage, commit, push, or publish. It preserves design pressure that may be useful for later Mira system work.

## Purpose

This note converts three selected directions into one artifact:

- A design note for Mira's objectives and system architecture.
- A reusable audit checklist for workflows and skills.
- A map from the transcript-derived design pressure to current Mira controls.

The useful signal is not that the transcripts are factually authoritative. The useful signal is that they stress-test agent work against outcomes, portability, setup discipline, and explicit operating loops.

## Design Thesis

The transcript batch points toward a compact objective for Mira:

> Build a portable, local-first agent operating system where every workflow has explicit context, authority, cadence, done-state, and receipt evidence.

The strongest transferable ideas are:

1. Done-state must be designed before work starts.
   Agent activity becomes valuable only when the finish condition is named in terms the operator cares about. For Mira, `done` should usually mean a verified state transition, a saved artifact, a clean handoff, a committed/pushed boundary, or an explicit no-action receipt.

2. Memory, files, instructions, and work should stay portable.
   Durable state should remain in inspectable files, registries, skills, receipts, and repositories rather than living only inside one model, vendor memory layer, or chat history. Model-switching should be possible because the important state is recoverable outside the model.

3. Capabilities need an operating loop.
   A capable model plus connectors is not yet a system. Mira should evaluate workflows through context, authorized connections, executable capabilities, cadence, and receipts.

4. Imported skills, templates, and plugins require admission control.
   Reusable agent packages can carry hidden assumptions, permissions, memories, setup gaps, and environment dependencies. The correct posture is inspect first, install or synchronize only through governed routes, and make missing setup explicit.

5. Outcome evidence is better than activity evidence.
   A long run, detailed plan, or busy tool trace is not proof. Better proof is concrete: source body exists, row count matches, snapshot digest changed as expected, validator passed, remote SHA verifies, or the operator-facing decision is genuinely unblocked.

## Reusable Audit Checklist

Use this checklist when reviewing a Mira workflow, skill, automation, capture route, or agent operating pattern.

### 1. Done-State

- What exact state counts as done?
- Is done observable without trusting the agent's narrative?
- Is the done-state tied to the operator's real objective rather than agent activity?
- Does the workflow say what boundaries were not crossed?
- Can another agent resume from the receipt without rediscovering the whole path?

### 2. Context

- Which durable context carriers are authoritative?
- Are supplied, observed, inferred, stale, missing, and contradictory inputs separated?
- Is important context stored in a portable file, registry, ledger, or receipt?
- Is private or provisional context prevented from becoming doctrine by accident?

### 3. Authority

- Which actions require explicit operator authority?
- Are staging, commit, push, publication, deployment, external communication, and Archive admission kept distinct?
- Does a soft assent or menu selection accidentally cross a boundary it should not?
- Is the current workflow allowed to mutate the target surface?

### 4. Connections

- Which tools, plugins, credentials, browsers, remotes, or APIs are in play?
- Are permission, credential, and account-context splits visible?
- Are hidden setup requirements named before reuse?
- Can the workflow degrade safely when an optional connector is unavailable?

### 5. Cadence

- Is this one-time work, recurring monitoring, periodic capture, or a larger operating rhythm?
- Does cadence produce useful receipts rather than noisy status?
- Does the workflow stop when unchanged state is non-actionable?
- Is the next run's re-entry point explicit?

### 6. Capability

- Is the model doing toil, technique, judgment, or apprenticeship-bearing work?
- Is automation compressing the right labor without hiding necessary human judgment?
- Are domain validators or proven libraries used where hand-rolling would be risky?
- Does the workflow preserve method and lineage where they matter?

### 7. Receipt Evidence

- What artifact, command output, digest, URL, file path, or SHA proves the result?
- Is the proof local, committed, remote-verified, hosted-verified, or only conversational?
- Are validation results scoped to the claim being made?
- Are failures and unavailable evidence recorded honestly?

### 8. Portability

- Could a different model continue the work from the saved state?
- Are memory, skills, source files, and instructions externalized from any single model provider?
- Are vendor-specific affordances treated as replaceable capability rather than the system's only memory?
- Are paths and identifiers stable enough for later retrieval?

## Map Against Current Mira Controls

| Design pressure | Current Mira control | Fit | Gap or next design question |
|---|---|---|---|
| Done-state before action | `mira-work` receipt target, observable proof, completion receipt; `learn-from-choices` closure-debt audit | Strong | Could define a compact `done-state` field in more domain skills so this is not reconstructed ad hoc. |
| Portable memory/files/instructions | Repo-local skills, `archive/notes`, continuity carriers, source shelves, Git commits | Strong | Need periodic checks that important working memory is not trapped in chat-only context after long sessions. |
| Operating loop: context, connections, capability, cadence | `mira-work` Sense/Decide/Act/Learn; YouTube capture browser receipts; automations notification boundaries | Strong | A shared workflow-audit rubric could make the loop easier to apply consistently across skills. |
| Imported skill/template caution | Skill registry, plugin install rules, skill synchronization constraints, connector permission boundaries | Strong | Plugin/template review could explicitly require memory, connector, env, and hidden setup inspection before reuse. |
| Outcome evidence over activity | Archive validators, publication validation, Mira Work snapshots, Git SHA verification, `git diff --check` | Strong | Some prose-heavy routes still need sharper observable proof definitions to avoid impressive but soft closure. |
| Provider independence | Local files and Git as primary continuity substrate | Strong | Model-provider fallback drills could test whether another model can resume from current artifacts. |
| Cadence without noise | Automations instructions and YouTube capture receipts | Medium | More monitors should state "quiet while unchanged" and define actionable-change thresholds. |
| Cost/value discipline | Publication-validation routing, cheapest sufficient validation, bounded diagnostics | Medium | A lightweight "value returned" field could help separate valuable automation from merely elegant automation. |
| Human judgment preservation | `mira-work` proportional compression gate; Learn From Choices action authority | Strong | Need continued attention when automation compresses apprenticeship-bearing work. |

## Candidate Design Moves

1. Add a small `Done-state` subsection to high-traffic skills.
   This would name expected terminal artifact, proof command, and boundaries not crossed.

2. Promote the audit checklist above into a reusable workflow-audit reference.
   It can become a review lens for `skill-audit`, `repo-audit`, or Mira Work completion checks.

3. Add a provider-portability drill.
   Periodically ask whether another model could continue the current task using only repository state, saved receipts, and visible artifacts.

4. Tighten plugin/template admission.
   Add a review step for imported templates: memories, connectors, permissions, environment variables, local code dependencies, and missing setup.

5. Define "activity is not proof" examples.
   Add fixtures where a long agent run should still fail closure because no file, receipt, SHA, validator, or user decision changed.

## Stopping Point

The transcripts are useful as architectural prompts because they name failure modes Mira is already designed to resist: vague finish lines, vendor-trapped memory, connector enthusiasm without authority, and activity mistaken for outcome. The next useful step is not to treat the transcripts as truth, but to turn the checklist into a repeatable control for skill and workflow review.

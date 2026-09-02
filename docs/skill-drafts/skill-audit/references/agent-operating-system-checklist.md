# Agent Operating System Checklist

Use this reference only while auditing whether a skill, workflow, or automation
behaves like an operating system component rather than a loose prompt or
capability demo. It was extracted from
`archive/notes/2026-09-02-nate-transcripts-agent-operating-system-design-note.md`.

This checklist is an audit lens, not a repair authority. Findings produced from
it do not authorize edits, staging, commit, push, publication, deployment,
plugin installation, external communication, source admission, or claim
verification.

## Core Question

Can a different competent agent use the skill to move from operator objective
to verified outcome without relying on hidden chat memory, vendor-specific
state, or activity narration as proof?

## 1. Done-State

- What exact state counts as done?
- Is done observable without trusting the agent's narrative?
- Is the done-state tied to the operator's real objective rather than agent
  activity?
- Does the workflow say what boundaries were not crossed?
- Can another agent resume from the receipt without rediscovering the whole
  path?

## 2. Context

- Which durable context carriers are authoritative?
- Are supplied, observed, inferred, stale, missing, and contradictory inputs
  separated?
- Is important context stored in a portable file, registry, ledger, or receipt?
- Is private or provisional context prevented from becoming doctrine by
  accident?

## 3. Authority

- Which actions require explicit operator authority?
- Are staging, commit, push, publication, deployment, external communication,
  and Archive admission kept distinct?
- Does a soft assent or menu selection accidentally cross a boundary it should
  not?
- Is the current workflow allowed to mutate the target surface?

## 4. Connections

- Which tools, plugins, credentials, browsers, remotes, or APIs are in play?
- Are permission, credential, and account-context splits visible?
- Are hidden setup requirements named before reuse?
- Can the workflow degrade safely when an optional connector is unavailable?

## 5. Cadence

- Is this one-time work, recurring monitoring, periodic capture, or a larger
  operating rhythm?
- Does cadence produce useful receipts rather than noisy status?
- Does the workflow stop when unchanged state is non-actionable?
- Is the next run's re-entry point explicit?

## 6. Capability

- Is the model doing toil, technique, judgment, or apprenticeship-bearing work?
- Is automation compressing the right labor without hiding necessary human
  judgment?
- Are domain validators or proven libraries used where hand-rolling would be
  risky?
- Does the workflow preserve method and lineage where they matter?

## 7. Receipt Evidence

- What artifact, command output, digest, URL, file path, or SHA proves the
  result?
- Is the proof local, committed, remote-verified, hosted-verified, or only
  conversational?
- Are validation results scoped to the claim being made?
- Are failures and unavailable evidence recorded honestly?

## 8. Portability

- Could a different model continue the work from the saved state?
- Are memory, skills, source files, and instructions externalized from any
  single model provider?
- Are vendor-specific affordances treated as replaceable capability rather than
  the system's only memory?
- Are paths and identifiers stable enough for later retrieval?

## Finding Heuristics

- Missing done-state is usually `P1` when the skill can mutate state or route
  publication; otherwise it is usually `P2`.
- Activity-as-proof is usually `P1` when it can close a governed workflow
  without artifact, receipt, validator, or human decision evidence.
- Hidden vendor or chat-only state is usually `P2`; raise to `P1` when it
  blocks reproducibility, source provenance, or later audit.
- Undeclared connector, credential, or permission dependency is usually `P1`
  when it can expose private data or silently change the action surface.
- Noisy cadence without actionable-change thresholds is usually `P2`.

## Compact Report Add-On

When this lens materially changes an audit, add this short section after the
standard findings:

```text
Operating-system fit:
Done-state:
Context carriers:
Authority boundary:
Connection risks:
Cadence:
Receipt evidence:
Portability:
```

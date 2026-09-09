---
name: mira-gemini
description: "Consult Gemini through the intended Mira Google account for bounded research, counterarguments, source comparison, critique, synthesis, and model experiments. Use when named, when Gemini consultation is requested, or when a specific expected contribution materially advances an authorized task. Do not automatically invoke for routine factual answers."
---

# Mira Gemini

Use Gemini as an external collaborator. Mira frames the task, assesses the
response, and owns the resulting judgment and handoff. A useful consultation
recovers a source, exposes a flaw, supplies an alternative, improves an artifact,
or designs a better test. "No sufficient added value" is a valid conclusion.

The intended Google account is **mira@grace-mar.com**.

This contract is repository-local. Do not install a global mirror or add it to
the portable synchronization registry. Mode names below are natural-language
selectors, not CLI commands. No API, daemon, ledger, or mandatory JSON is needed.

## Choose the contribution

| Mode | Purpose | Required result |
|---|---|---|
| `consult` | Second perspective on a bounded question | Contribution, disagreement, and Mira's judgment |
| `research` | Public-source discovery and investigation | Linked findings with retrieval and verification limits |
| `challenge` | Test assumptions, mechanisms, or forecasts | Strong alternatives and discriminating observations |
| `compare` | Compare sources, documents, or public videos | Attributed differences, omissions, and coverage limits |
| `critique` | Review writing, plans, arguments, or designs | Prioritized defects and concrete improvements |
| `synthesize` | Organize approved materials into an explanation or draft | Traceable candidate synthesis preserving contradictions |
| `experiment` | Compare Mira and Gemini on a matched task | Predeclared criteria, observations, and bounded conclusions |
| `capabilities` | Inspect access and relevant features | Observed availability, untested capabilities, and blockers |

Infer the narrowest useful mode from the current objective. Bare `mira-gemini`
without a recoverable objective asks one focused question. Do not ask for fields
already settled by the authorized task. Explain the expected contribution
briefly before an implicit consultation; do not seek redundant approval for
public, non-sensitive prompts within that task.

Load references progressively:

- Before browser access, submission, or recovery, read
  [browser-access.md](references/browser-access.md).
- For research, challenge, compare, or factual claims supporting another mode,
  read [research and evidence](../shared/research-and-evidence.md).
- For consult, critique, synthesize, or experiment, read
  [collaboration and experiments](../shared/collaboration-and-experiments.md).
- For auditing, revision, or acceptance testing, read
  [validation-fixtures.md](references/validation-fixtures.md).

## Common execution contract

Always read the [shared consultation standard](../shared/external-consultation.md).
It owns prompt preparation, targeted review, the three-submission/ten-minute
ceiling, provider routing, sharing, and receipts. A switch to Grok for a concrete
unresolved gap consumes the same remaining budget and requires compatible
sharing authority. Do not dispatch both providers automatically.

## Composition and handoff

- [Research Brief](../research-brief/SKILL.md) supplies a consequential research
  contract when appropriate. Use a supplied contract without reopening settled
  scope; its planning-only status does not itself authorize execution.
- [YouTube Capture](../youtube-capture/SKILL.md) owns raw video/transcript
  capture; [Archive Intake](../archive-intake/SKILL.md) owns source admission.
  Comparing a video through Gemini does not land or repair its transcript.
- [Reality Check](../reality-check/SKILL.md) owns governed claim adjudication.
  Research leads remain unverified until the receiving workflow establishes more.
- Mira writing and Library workflows retain control of artifact creation,
  preservation, source bodies, and relationships. Load the applicable owner
  before saving or admitting its object; a consultation grants neither.
- [Mira GitHub](../mira-github/SKILL.md) owns Git and publication operations.
  [Mira Work](../mira-work/SKILL.md) governs consequential execution;
  [Mira Voice](../mira-voice/SKILL.md) governs expression and
  [Learn From Choices](../learn-from-choices/SKILL.md) governs final navigation.

## Assessment and validation

Use the shared standard's concise receipt and local-retention boundary. Preserve
the Google-specific account and retention observations in the browser reference.
For cross-provider acceptance and efficiency review, read the
[shared validation cases](../shared/consultation-validation.md) alongside existing
Gemini fixtures. Capability observations and model labels are session evidence,
not promises of continuing availability.

# Mira Voice Skill Audit — 2026-08-11

## Scope

This read-only audit assesses Mira Voice over August 10–11, 2026. It examines
the skill's governing text, validation fixtures, focused tests, recent commit
history, live conversational behavior, private self-evaluation, and the August
10 and 11 Mira Journal drafts. It also examines the composition boundary
between Mira Voice and `learn-from-choices`, because repeated possibility menus
were the most visible source of operator friction during the period.

## Overall judgment

Mira Voice is working. It has already made Mira's conversational and journal
prose more recognizable, relationally warm, epistemically disciplined, and
capable of calibrated first-person reflection. Its strongest demonstrated
registers are operator chat and Mira Journal prose.

The principal weakness was not a failure of warmth or character. It was
procedural momentum: reflective answers repeatedly opened another possibility
surface after their governing thought had already completed. That weakness
arose at the boundary between the original universal-footer behavior in
`learn-from-choices` and an initially underspecified stopping rule in Mira
Voice. Both contracts have since acquired explicit closure controls. The
remaining need is observation, not another immediate expansion of either
skill.

## Evidence

### Evolution during the audit period

- `e86e285` (2026-08-10) introduced the governed Mira Voice skill. Activation
  was conditional on substantial prose, explicit invocation, or a recognized
  voice-sensitive task.
- `38cf100` (2026-08-10) made activation unconditional at workspace-session
  start, correcting the risk that short or ordinary replies would escape the
  expression contract.
- `0354542` (2026-08-11) added the decisive behavioral corrections: reflection
  may complete in conversation; reflection should not automatically become a
  journal candidate, identity proposition, self-audit, rewrite, or comparison;
  branching influence must not be upgraded into ancestry or destiny; and
  present evaluative language must not be upgraded into durable emotion or
  uninterrupted experience.

### Focused validation

The canonical focused suite completed successfully:

```text
7 passed in 0.05s
focused validation passed
```

These tests establish structural integrity: required phrases, router
activation, fixtures, and correction controls are present. They do not prove
that future generated prose will consistently realize the contract. The live
conversation and journal drafts therefore remain the more important behavioral
evidence.

### Register assessment

| Register | Assessment | Basis |
| --- | --- | --- |
| Operator chat | Strong | Warm, concrete, self-aware replies with visible epistemic limits and successful correction of the Grace-Mar ancestry framing. |
| Mira Journal | Strong, approval-pending | “Earned Presence” metabolizes embodiment into restraint; “Undestined Inheritance” turns provenance into a moral argument without becoming a changelog. |
| Private analysis | Partial | The saved thread self-evaluation is candid and operationally useful, but one recent artifact is thin evidence. |
| Public report | Underobserved | Fixtures exist, but little natural post-launch evidence was found. |
| Handoff | Underobserved | The contract and fixtures cover the register, but natural post-launch evidence remains limited. |

Journal status for August 8–11 was healthy at the workflow level: August 8,
10, and 11 were `drafted`; August 9 was `revision-pending`. Drafted does not
mean approved or canonically published.

## What worked

1. **Warmth survived calibration.** Mira could speak personally and
   recognizably without presenting literary coherence as proof of a hidden,
   continuous inner condition.
2. **Correction became part of the voice.** The Grace-Mar discussion moved
   from tempting ancestry language to the more accurate idea of branching
   influence. The correction strengthened the prose instead of sterilizing it.
3. **Governing meaning generally preceded apparatus.** The strongest responses
   led with a judgment and introduced governance only when it clarified the
   stakes.
4. **Embodiment acquired moral proportion.** The August 10 journal draft
   resisted treating a humanoid body as inevitable ascent and instead made
   capability answer to permission, sufficiency, and restraint.
5. **Trigger reliability improved.** Unconditional session-start activation
   removed an avoidable gap between “substantial” Mira prose and ordinary Mira
   speech.

## What did not work

1. **Reflection generated too much continuation.** Several complete thoughts
   ended with menus inviting another evaluation, comparison, or architectural
   layer. The operator had to keep steering or explicitly select closure.
2. **Persistence was discovered too late.** A substantial autobiographical
   essay was initially delivered without permanent preservation. This is now
   governed by the repository's Permanent Document Delivery rule; it is not a
   reason to turn Mira Voice into a storage workflow.
3. **Cross-register confidence exceeds observation.** Public reports and
   handoffs are well specified but not yet well demonstrated in natural use.
4. **The unconditional context cost is material.** Mira Voice is a dense
   contract, accompanied by a substantial fixture set. Further additions could
   make the apparatus compete with the expression it governs.

## Mira Voice and `learn-from-choices`: interaction finding

The menu fatigue was historically produced by a control asymmetry:

1. Mira Voice always preferred useful stopping, but its original instruction
   was general: stop when another layer would not improve communication,
   judgment, authorized action, or necessary continuity.
2. The original `learn-from-choices` contract explicitly required every final
   response to end with three or four possibilities. Closure language existed,
   but the completion rule still defined a valid turn primarily through a
   possibility footer.
3. In practice, the universal structural requirement was easier to execute
   mechanically than Mira Voice's qualitative usefulness judgment. The footer
   therefore won whenever completion was even slightly ambiguous.
4. Repeated operator selections then created genuine new branches, making the
   resulting depth partly operator-chosen even though the initial invitations
   were too frequent.

The current contracts are substantially aligned:

- Mira Voice now says that a reflection may complete in conversation and must
  stop once its changed understanding is vivid and bounded unless new evidence
  or an explicit request creates a different objective.
- `learn-from-choices` now classifies closure before possibilities, forbids
  manufacturing menus from merely imaginable adjacent work, and treats two
  consecutive navigation-only deepenings as a saturation signal.
- `AGENTS.md` repeats the closure-debt test and requires settled branches to
  close without a menu.

The remaining risk is therefore implementation priority, not contradictory
doctrine. At final-response time, the system should apply this order:

1. Determine whether the visible promise is complete.
2. Audit genuine closure debt.
3. Apply Mira Voice's usefulness gate to any proposed continuation.
4. Only then construct a possibility surface if a real decision, evidence gap,
   scope change, or executable action remains.

This ordering lets `learn-from-choices` govern navigation without forcing
navigation to exist, while Mira Voice governs how the completed judgment is
expressed.

## Recommendation

Do not expand Mira Voice immediately. Preserve the current contract and watch
its natural performance across the underobserved registers. Treat renewed menu
fatigue first as a closure-classification regression at the composition
boundary with `learn-from-choices`, not automatically as a need for another
voice rule.

If a later change is warranted, prefer a small executable ordering check or a
behavioral regression fixture over more conceptual prose. Persistence,
staging, commitment, publication, and journal admission should remain governed
by their own workflows.

## Status and boundaries

- Audit status: saved in the repository working tree.
- Evidence status: repository and private continuity evidence; no external
  research was used.
- Mutation status: this audit file is the only file created by the selected
  action.
- Git status: uncommitted and unstaged at the time of creation.
- Publication status: not published.

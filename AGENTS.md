# Narrative Systems Local Cadence

At genuine decision points, lead with one reasoned recommendation. Present
alternatives only when the tradeoff remains genuinely unsettled or the
operator requests them. When alternatives are necessary, make their sequence,
dependencies, tradeoffs, and consequences explicit.

When the operator says `coffee`, read
`docs/skill-drafts/coffee/SKILL.md` completely and follow it.

When the operator says `dream`, read
`docs/skill-drafts/dream/SKILL.md` completely and follow it.

When the operator says `world-monitor`, asks for a World Monitor scan, or asks
to use World Monitor as a Narrative Systems source, read
`docs/skill-drafts/world-monitor/SKILL.md` completely and follow it.

When the operator says bare `intake`, or asks to intake a source without a
more specific workflow qualifier, use the one canonical operator front door:
read `docs/skill-drafts/smart-intake/SKILL.md` completely and follow it.
The user-facing command is simply `intake`; `smart-intake` names the workflow
and `best-intake` names its implementation engine. Do not infer the legacy
statecraft source-intake workflow from the bare word, even for YouTube.

Use the statecraft source-intake workflow only when the operator explicitly
says `source-intake`, `statecraft source intake`, or `statecraft daily intake`.

When the operator says `harness audit`, run
`tools/run.ps1 harness` read-only and summarize the
five stations, actionable findings, and coverage gaps. Do not synchronize,
edit, or retire any control during the audit.

These are repository-local contracts. Do not synchronize them into global
Codex skills. Their handoff is advisory cadence state, never research evidence.

End every user-facing response with multiple-choice options for the next best
ROI action. Put the recommended option first, keep the options concise and
mutually distinct, and use the options even when the preceding response is
primarily a status update or explanation.

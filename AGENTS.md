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

When the operator says `archive-repair`, asks to repair an existing archive
source, or requests ASR/sectioning repair, read
`docs/skill-drafts/archive-repair/SKILL.md` completely and follow it.

When the operator says `archive-query` or asks a bounded question about archive
inventory, paths, voices, hosts, channels, or membership, read
`docs/skill-drafts/archive-query/SKILL.md` completely and follow it.

When the operator says `archive-audit` or asks for systematic archive health,
coverage, density, parity, routing, duplicate, or repair-candidate assessment,
read `docs/skill-drafts/archive-audit/SKILL.md` completely and follow it.

When the operator says bare `intake`, or asks to intake a source without a
more specific workflow qualifier, use the one canonical operator front door:
read `docs/skill-drafts/archive-intake/SKILL.md` completely and follow it.
The user-facing command is simply `intake`; `archive-intake` names the canonical
skill, while `smart-intake` and `best-intake` remain compatibility aliases.
Do not infer the legacy
statecraft source-intake workflow from the bare word, even for YouTube.

Use the statecraft source-intake workflow only when the operator explicitly
says `source-intake`, `statecraft source intake`, or `statecraft daily intake`.

When the operator says `harness audit`, run
`tools/run.ps1 harness` read-only and summarize the
five stations, actionable findings, and coverage gaps. Do not synchronize,
edit, or retire any control during the audit.

These are repository-local contracts. Do not synchronize them into global
Codex skills. Their handoff is advisory cadence state, never research evidence.

For every final user-facing response, read and follow
`docs/skill-drafts/learn-from-choices/SKILL.md`. Do not apply its footer to
intermediate progress commentary. End with three or four concise, meaningfully
distinct next possibilities using the stable roles `recommended`,
`alternative`, `overlooked`, and `pause-or-deepen`; omit a fourth option when
it would create fake diversity. Explain the recommendation in one
evidence-grounded sentence and preserve a credible overlooked path when one
exists. A bare letter enters and develops that branch; it never silently
authorizes mutation, execution, spending, publication, communication,
customer action, commit, push, or deployment. A later explicit command
supersedes the pending menu.

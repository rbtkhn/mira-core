# Narrative Systems Local Cadence

At genuine decision points, lead with one reasoned recommendation. Present
alternatives only when the tradeoff remains genuinely unsettled or the
operator requests them. When alternatives are necessary, make their sequence,
dependencies, tradeoffs, and consequences explicit.

## Efficient Tool Execution

Bound diagnostic output before expanding it. For a dirty repository, inspect
counts and capped top-level groupings first. Do not print a complete status or
path inventory when more than 200 entries are present unless the operator or a
specific repair requires those paths. Search named controlling files before
repository-wide text, and exclude archive transcript bodies from administrative
queries unless their contents are the evidence under review.

When a tool returns a live session or cell identifier, record it and resume or
poll that exact process until it reaches a terminal state. Never relaunch the
same long-running command merely because the initial call returned no output.
Keep direct command output bounded and retain a concise raw failure tail when
the governing workflow requires auditability.

Before a test or renderer writes temporary files, run the repository's
`session-preflight` command against the intended absolute temporary root. Fail
before starting the workload when the root is missing, inside the repository,
or not writable. Do not infer writability from a declared sandbox permission
alone.

Cache an optional service's unavailable state for the current task. Do not
repeat the same availability probe unless its path, environment, credentials,
permissions, or other external state changes, or the operator explicitly asks
for a retry.

When the operator says `coffee`, read
`docs/skill-drafts/coffee/SKILL.md` completely and follow it.

When the operator says `dream`, read
`docs/skill-drafts/dream/SKILL.md` completely and follow it.

When the operator says `recursive-learn`, asks whether a Mira Journal
technical reference demonstrates recursive learning, requests an RSI candidate,
or explicitly directs admission to the recursive-learning ledger, read
`docs/skill-drafts/recursive-learn/SKILL.md` completely and follow it. Default
to read-only assessment; only exact digest-bound admission may mutate the
canonical ledger.

When the operator says `world-monitor`, asks for a World Monitor scan, or asks
to use World Monitor as a Narrative Systems source, read
`docs/skill-drafts/world-monitor/SKILL.md` completely and follow it.

When the operator says exact `research-brief`, asks for a research plan or
research assignment, asks to design an investigation or source strategy, or
asks what a researcher should investigate, read
`docs/skill-drafts/research-brief/SKILL.md` completely and follow it. This route
designs the research contract only. Do not use it for requests to conduct
research, retrieve sources, produce sourced findings or analytical reports, or
run `morning-brief`.

Treat the unhyphenated phrase `research brief` as ambiguous when the surrounding
request does not distinguish a research plan from a researched report. Ask one
question -- "Do you want an investigation plan or sourced findings?" -- before
choosing a workflow. Do not browse while resolving that ambiguity.

When the operator says `archive-repair`, asks to repair an existing archive
source, or requests ASR/sectioning repair, read
`docs/skill-drafts/archive-repair/SKILL.md` completely and follow it.

When the operator says `archive-query` or asks a bounded question about archive
inventory, paths, voices, hosts, channels, or membership, read
`docs/skill-drafts/archive-query/SKILL.md` completely and follow it.

When the operator says `mechanism-lens`, asks to summarize an archive voice
narrative over time, compare archive voices by causal mechanism, map a voice
narrative into domains, extract forecast or implication patterns, asks for
claim-structure coding, or asks to prepare verification handles without
adjudicating truth, read `docs/skill-drafts/mechanism-lens/SKILL.md`
completely and follow it.

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

After intent recovery and before consequential elicitation or execution, run
`tools/run.ps1 contradiction-check` when an explicit material factual premise
may conflict with a named repository fact. Supply only the smallest relevant
controlling surface. Route missing or stale ordinary control to neutral
evidence intake, a direct conflict to decision navigation, and conflicting
current controls to named-authority resolution. Skip this preflight for exact
menu selections, ordinary preferences, and clear commands without a factual
conflict. The result reports contradictions but grants no authority.

When the operator says `harness audit`, run
`tools/run.ps1 harness` read-only and summarize the
five stations, actionable findings, and coverage gaps. Do not synchronize,
edit, or retire any control during the audit.

When the operator says `morning-brief` or asks for the experimental morning
brief, read `docs/skill-drafts/morning-brief/SKILL.md` completely and follow it.
This route is repository-local and must not be synchronized to a user-level
skill mirror.

These are repository-local contracts. Do not synchronize them into global
Codex skills. Their handoff is advisory cadence state, never research evidence.

At the start of each workspace session, after loading all controlling repository
instructions, read `mira/continuity/activation.md` when it exists. Treat it as
bounded advisory continuity only: it is not research evidence, operator belief,
or action authority, and explicit current operator direction always controls.

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

Menu usability: every action-bearing possibility must state the complete
bounded action and target in its visible label. When the operator selects
that possibility by letter, carry the selected action and scope forward;
never make the operator retype the command merely to restate the choice.
If a consequential authorization boundary still applies, ask only for the
minimal confirmation at the exact action point, preserving the selected
scope.

Action-ready menu grammar: when a possibility is intended to authorize a
bounded action, its visible label must begin with the governing executable
verb (`Execute`, `Commit`, `Push`, or `Send`), followed immediately by the
action and target. Do not hide an executable action behind a role label such
as `Recommended`; stable possibility roles belong after the executable verb.

Before presenting any possibility footer, classify action readiness for each
option independently. A decision surface may mix executable and navigational
options. When an exact bounded action, target, and verification step are ready,
no material choice remains unresolved, and authority is the only blocker, the
surface must declare that option ready, give it the matching executable
`selection_effect`, and pass `elicitation validate`. Do not replace a ready
action with a navigational request to settle, confirm, adopt, or approve an
already-bounded scope. An all-navigation surface must declare the bounded
reason no action is ready.

Selection closure and idempotence: after a branch is confirmed, paused, or
otherwise settled, a repeated selection of the same stable option is a no-op.
Acknowledge the settled state once and close the branch; do not regenerate the
same possibility menu. Only present a new menu when a genuinely new decision,
scope, evidence gap, or action is available.

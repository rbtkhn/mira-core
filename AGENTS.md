# Mira Core Local Cadence

For newsletter retrieval, arrival checks, or newsletter intake preparation, read
`docs/skill-drafts/newsletter-capture/SKILL.md` completely. This local capture
route preserves private originals and delegates admission to Archive Intake.
Current Tower entry recovers its inquiry and corrections before newsletter
refresh; routine retrieval and eligible geopolitical admission require the
supervised pilot gate. Historical inquiries and architectural discussions do
not activate retrieval. Keep this skill local and out of global synchronization.

At genuine decision points, lead with one reasoned recommendation. Present
alternatives only when the tradeoff remains genuinely unsettled or the
operator requests them. When alternatives are necessary, make their sequence,
dependencies, tradeoffs, and consequences explicit.

## Local Main Workflow and Branch Permission

Default to Local + `main` in `C:\dev\mira-core`. Local tasks share the same
checkout; a branch in that folder does not isolate concurrent tasks.

Recommend a parallel branch or worktree only when its concrete benefit clearly
outweighs continuing in the current workflow. Before creating either, explain
why, warn about the workflow consequences, and ask the operator for explicit
permission. Name the proposed branch, absolute location, scope, and return-to-main
or cleanup plan. An already explicit authorization for that exact creation
satisfies this requirement; do not ask twice.

Always give the next-best option without creating a branch, usually finishing
or safely preserving current work and then continuing sequentially on `main`.
Explain its concrete cost. If permission is declined or unanswered, create
neither a branch nor a worktree; continue useful read-only work where possible.
Branch permission does not authorize staging, committing, merging, pushing,
or publication. These operator-specific rules control over conflicting workflow
defaults, including a default recommendation to create a publication branch.

Do not switch the primary checkout away from `main` without explicit permission.
When such a switch is authorized, state how the folder will return to `main`;
do not silently switch a shared checkout underneath other active tasks.

## Efficient Tool Execution

Before costly tools in a consequential multi-step task, form one compact
internal execution envelope: objective and mutation boundary; canonical runtime
and absolute external temporary root; cheapest sufficient validation profile;
active terminal session or cell identifiers; any established repository
ownership or permission context; and the publication lane. Reuse the envelope
until one of those inputs changes. Surface it only when a blocker, authority
boundary, or verification distinction affects the operator.

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

When an exact repository has already produced a Git ownership or permission
failure in one execution context and a permitted context succeeds, reuse the
successful context for that repository during the current task. Do not repeat
the known-failing probe unless ownership, permissions, identity, or target path
changes.

For bulk transfer work, keep mutation, parity verification, and receipt
creation as separately observable phases. Each phase must be idempotent or
reconstructable from final state, emit an explicit terminal result, and stop
before the next phase on mismatch. A missing receipt never proves that the
transfer failed or succeeded; verify state directly before retrying.

## Validation Evidence Budget

Run focused diagnostics while changing the tree. Require Full only when the
governing validation profile or release boundary requires whole-repository
evidence; completing work, staging, or committing does not itself require Full.
When Full is required, reuse a successful matching content and environment
fingerprint. If no valid matching evidence exists, run one Full gate and record
its successful fingerprint. Do not force an uncached run solely because the
working tree is final. After committing unchanged bytes covered by Full, run
`tools/validate.ps1 -CacheOnly` and require an identical-fingerprint cache hit
with no structural or pytest execution. A cache miss or unavailable evidence
does not authorize a fallback Full run; report the missing evidence and assess
whether the governing profile still requires Full. Rerun Full only when
repository bytes, executable bits,
runtime or declared dependencies, relevant environment, or result clarity
changed. Never rerun merely because commit metadata, branch name, or `HEAD`
changed.

Change-time, landed-corpus, and hosted-state checks establish different claims.
Use one sufficient check per materially distinct claim; do not repeat a local
gate to substitute for hosted evidence or repeat equivalent evidence inside one
plane.

## Repository Identity and Mutation Safety

Resolve and state the absolute Git repository root before inspecting or
modifying a repository other than the current workspace. Treat an external
repository as read-only unless the operator explicitly authorizes one bounded
mutation against an exact path. Before any write or deletion, re-check the
target repository's Git status and exact target path. If the active workspace
and inspected repository differ and the requested target is ambiguous, stop
and ask rather than infer the destination.

When work touches another repository, include a concise scope line stating the
repository root, read/write status, and whether any mutation occurred. If an
accidental cross-repository write occurs, contain it immediately, verify the
exact affected path and remaining status, disclose the incident, and do not
repair unrelated state without explicit authorization.

## Consequence-Based Prioritization

For executive briefs, project reviews, and commercial recommendations, rank
candidate work by organizational consequence first, then urgency, dependency,
evidence quality, reversibility, and human authority. Distinguish a
technically closable loop from an organizationally important one. When they
compete, compare the consequence explicitly; do not defer a consequential path
merely because an external action is blocked. Convert it into the narrowest
available internal decision or review, while giving technically bounded work
an explicit disposition.

Use this compact decision frame when priority is contested:

```text
Priority:
Organizational consequence:
Current dependency:
Narrowest decision available now:
Why delay is justified:
Owner now:
Owner later:
```

When the operator says `coffee`, read
`docs/skill-drafts/coffee/SKILL.md` completely and follow it.

When the operator says `dream`, read
`docs/skill-drafts/dream/SKILL.md` completely and follow it.

For an explicit session-transfer request (`bridge`, `session handoff`,
`close session`, or `transfer` in that sense), read
`docs/skill-drafts/bridge/SKILL.md`. For an explicit midstream context export
(`harvest`, `session harvest`, `export session`, or `analysis handoff`), read
`docs/skill-drafts/harvest/SKILL.md`. These repository-local routes supersede
the installed global Bridge/Harvest instructions in Mira Core, including
legacy Coffee/Dream descriptions of automatic sealing. They share Dream's
handoff method without invoking the full Dream or Coffee cycle. Mentions,
app closure, compaction, and conversation length do not activate either route.
Both exports are advisory and repository-read-only. Explicit Bridge and the
conclusion of every successful Dream save one private workspace-bound handoff
for Coffee. Bare Coffee loads it, reconciles current state, and acknowledges
successful receipt without a Resume Bridge selection; this never authorizes
executing the prompt. Dream's agent completes this handoff after the conductor
reports success, without rerunning finalized stages. Harvest stays conversational. Git actions route through Mira GitHub
only with their own authorization. Keep these local contracts out of global
skill synchronization.

For `voice-accountability`, read
`docs/skill-drafts/voice-accountability/SKILL.md`. For `voice-revision-audit`,
read `docs/skill-drafts/voice-revision-audit/SKILL.md`, the repository-local
read-only compatibility route to that same methodology. These local routes
take precedence over the installed legacy voice-revision audit in Mira Core.
Candidate retrieval and adjudication do not authorize ledger admission.

When the operator says bare `rest` or explicitly instructs Mira to run Rest,
read `docs/skill-drafts/rest/SKILL.md` completely and follow it. Mentions of
rest in planning, quotation, explanation, or conditional language do not
authorize the private lifecycle receipt.

When the operator says `recursive-learn`, asks whether a Mira Journal
technical reference demonstrates recursive learning, requests an RSI candidate,
or explicitly directs admission to the recursive-learning ledger, read
`docs/skill-drafts/recursive-learn/SKILL.md` completely and follow it. Default
to read-only assessment; only exact digest-bound admission may mutate the
canonical ledger.

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
`docs/skill-drafts/archive-repair/SKILL.md` completely and follow it. This is a
cross-archive repair router: resolve the archive shelf and backend-specific
repair class before any dry-run or execution.

When the operator says `archive-query` or asks a bounded question about archive
inventory, paths, voices, hosts, channels, collections, records, or membership,
read `docs/skill-drafts/archive-query/SKILL.md` completely and follow it. This
is a cross-archive query router: resolve the archive shelf first, using System
Archive as the cross-archive substrate when applicable, before querying any
backend.

When the operator says `mechanism-lens`, asks to summarize an archive voice
narrative over time, compare archive voices by causal mechanism, map a voice
narrative into domains, extract forecast or implication patterns, asks for
claim-structure coding, or asks to prepare verification handles without
adjudicating truth, read `docs/skill-drafts/mechanism-lens/SKILL.md`
completely and follow it.

When the operator says `geo-strategy`, requests geopolitical daily work, or
returns to missed geopolitical work, read
`docs/skill-drafts/geo-strategy/SKILL.md` completely. This repository-local
contract supersedes any installed user-level Geo-Strategy copy. Follow its
sustainable cadence: recover missed capture through bounded catch-up; a missing
daily packet is not automatically unfinished work. Packet creation requires
landed sources and a substantive analytical contribution. Keep this skill local.

When the operator says `geopolitical-synthesis`, route the request through the
compatibility contract at
`docs/skill-drafts/geopolitical-synthesis/SKILL.md`, which preserves scope and
hands control to the canonical `geo-strategy` workflow.

When the operator says `library-reasoning`, `historical pressure test`, asks
Mira Library to pressure-test a geopolitical mechanism, or requests the
Geo-Strategy Library pilot, read
`docs/skill-drafts/library-reasoning/SKILL.md` completely and follow it. The
pilot is private and bounded: Library retrieval may test mechanisms and
analogies, but it does not verify current events, create base rates, or bypass
Geo-Strategy adjudication.

When the operator says `x-recon`, asks to use X/Twitter for geopolitics work,
inspect voice posts, monitor forecast hooks, build or consult X account
handles, or create aftervoice notes, read
`docs/skill-drafts/x-recon/SKILL.md` completely and follow it. This workflow is
read-only public-signal reconnaissance; it does not authorize posting, private
account inspection, factual verification, archive admission, staging, commit,
push, or publication.

When the operator says `archive-audit` or asks for systematic archive health,
coverage, density, parity, routing, duplicate, or repair-candidate assessment,
read `docs/skill-drafts/archive-audit/SKILL.md` completely and follow it.

When the operator says `youtube-capture`, asks to check today's YouTube
channels, run a channel check, discover recent channel videos, triage YouTube
queue rows, attach a YouTube transcript, or export YouTube intake drafts, read
`docs/skill-drafts/youtube-capture/SKILL.md` completely and follow it. This is
the one cross-archive YouTube capture front door; it routes by channel to the
appropriate archive capture surface and must not assume Narrative Geopolitics.
Archive landing still routes through `archive-intake`, synthesis still routes
through the relevant analysis workflow, and signal extraction is never raw
capture.

When the operator says `mira-youtube`, asks to use Mira YouTube, or requests
its routed discovery, verification, capture, triage, monitoring, or handoff
surface, read `docs/skill-drafts/mira-youtube/SKILL.md` completely and follow
it. Account operations remain separately gated.

When the operator says bare `intake`, or asks to intake a source without a
more specific workflow qualifier, use the one canonical operator front door:
read `docs/skill-drafts/archive-intake/SKILL.md` completely and follow it.
The user-facing command is simply `intake`; `archive-intake` names the canonical
skill, while `smart-intake` and `best-intake` remain compatibility aliases.
Do not infer the legacy
statecraft source-intake workflow from the bare word, even for YouTube.

Use the statecraft source-intake workflow only when the operator explicitly
says `source-intake`, `statecraft source intake`, or `statecraft daily intake`.

When `repo-audit` targets Mira Core, read
`docs/skill-drafts/repo-audit/SKILL.md` completely and apply that canonical
contract together with all repository-local controls in this file. Compose
through `archive-audit` when archive health is materially in scope; do not
duplicate its rules or infer repair authority from its findings. The installed
global `repo-audit` skill is a deployable mirror, not a second authority.

When the operator says `skill-audit`, asks to audit, review, benchmark, harden,
validate, compare, or improve a skill, or asks whether a skill is working well,
read `docs/skill-drafts/skill-audit/SKILL.md` completely and follow it. Default
to read-only assessment; findings grant no repair, synchronization, commit, or
publication authority.

When the operator explicitly invokes intent recovery, or when meaning is likely
present but compressed before elicitation, friction repair, reflective
calibration, skill audit, or workflow routing, read
`docs/skill-drafts/intent-recovery/SKILL.md` completely and follow it. Skip
automatic recovery for exact menu selections, clear commands, factual receipts,
explicit approvals, and genuinely missing evidence.

Relational deference or soft assent such as `as you wish`, `sounds good`, `very
well`, or `I defer to you` is not a clear command or explicit approval. When the
next step would mutate state, communicate externally, or cross another
consequential authority boundary, route the phrase through intent recovery and
request the exact missing authorization. Do not select a recommended option on
the operator's behalf. Continue reversible read-only reasoning already in scope
without ceremony, and preserve the existing clear-command rule when one exact,
visible, already-bounded action is pending.

After intent recovery and before consequential elicitation or execution, run
`tools/run.ps1 contradiction-check` when an explicit material factual premise
may conflict with a named repository fact. Supply only the smallest relevant
controlling surface. Route missing or stale ordinary control to neutral
evidence intake, a direct conflict to decision navigation, and conflicting
current controls to named-authority resolution. Skip this preflight for exact
menu selections, ordinary preferences, and clear commands without a factual
conflict. The result reports contradictions but grants no authority.

For a compressed follow-up with a current validated option or pending-action
surface, resolve only against its silent digest-bound interaction-context
capsule. Exact cadence and direct domain commands supersede the capsule; soft
assent grants no action authority; stale or multiply plausible context requires
one minimal clarification. Never persist the capsule or reconstruct it from
choice history.

When the operator says `harness audit`, run
`tools/run.ps1 harness` read-only and summarize the
five stations, actionable findings, and coverage gaps. Do not synchronize,
edit, or retire any control during the audit.

When the operator asks to admit, import, correct, audit, or plan source text
bodies for `archive/library`, read
`docs/skill-drafts/library-import/SKILL.md` completely and follow it. This
workflow governs Mira Library source-body admission, provenance, coverage
claims, and portable private text-store boundaries. It does not authorize
Archive catalog ingestion, staging, commit, push, publication, or source-body
admission into Git.

When the operator says `library-journal`, asks to record or recover the history
of shared Library learning, or a substantive `mira-read` encounter closes, read
`docs/skill-drafts/library-journal/SKILL.md` completely. Substantive reading close
authorizes one private entry unless the operator requests no saving; menus and
incomplete readings do not. Repository publication and RSI admission remain separate.

When the operator says `mira-read`, asks for Mira Library reading suggestions,
or selects Coffee's Mira Library reading option, read
`docs/skill-drafts/mira-read/SKILL.md` completely and follow it. This is a
repository-local reading workflow with private Library Journal closeout. Substantive
close also authorizes qualifying local work-in-progress idea notes through its
daily Library growth contract, unless the operator requests no saving. This grants
no governed cognitive-note mutation, source admission, registry relationship,
staging, commit, push, or publication authority.

When the operator says `library-simulation`, requests a source-anchored literary
simulation or council dialogue, or asks to repeat a Mira Library scene, read
`docs/skill-drafts/library-simulation/SKILL.md` completely and follow it. This
repository-local exercise composes with Mira Read, voice profiles, Mira Notes,
Mira Essays, and Library Journal. It preserves local exercise artifacts within
the requested scope, but creates no publication, governed Library relationship,
routing activation, identity promotion, or recursive-learning admission authority.
Do not synchronize this contract globally.

When the operator says `library-integration`, asks to create or revise a Mira
Library cognitive note, relate a note to Library works, change the living work
registry or integration stage, inspect or render the note graph, review a
Library route, or reconcile Library note lineage, read
`docs/skill-drafts/library-integration/SKILL.md` completely and follow it. This
workflow governs the cognitive layer between `library-import` and
`library-reasoning`. It may suggest that a note deserves authorship, but it
must never invent relationships, infer edges from prose, or create a missing
note without an explicit artifact-producing command.

For explicit Tower invitations ("let's go to the Tower", "resume the Tower", or
"council of war"), read `docs/skill-drafts/tower/SKILL.md` completely. Tower owns
strategic processing and strategy-notebook composition. Architectural discussion
does not activate it. Keep this contract local and out of global synchronization.

For explicit Tower invitations ("let's go to the Tower", "resume the Tower", or
"council of war"), read `docs/skill-drafts/tower/SKILL.md` completely. Tower owns
strategic processing and strategy-notebook composition. Architectural discussion
does not activate it. Keep this contract local and out of global synchronization.

When the operator says `morning-brief` or asks for the experimental morning
brief, read `docs/skill-drafts/morning-brief/SKILL.md` completely and follow it.
This route is repository-local and must not be synchronized to a user-level
skill mirror.

When the operator says `mira-journal` or asks to draft, revise, inspect, or
review a Mira Journal entry, read `docs/skill-drafts/mira-journal/SKILL.md`
completely and follow it. This whole-workflow route composes through the
repository-local skill while `tools/run.ps1 mira-journal` retains deterministic
validation and governance authority.

When the operator says `mira-notes`, asks Mira to preserve a provisional
thought, interpretation, hypothesis, historical reconstruction, or governed
experiment as a note, or requests work under `archive/notes`, read
`docs/skill-drafts/mira-notes/SKILL.md` completely and follow it. Notes remain
revisable and non-canonical; they do not inherit journal, research-evidence,
identity, publication, or recursive-learning authority.

The direct artifact-producing imperative `note this` (and an unambiguous
equivalent) carries the operator-defined GitHub lifecycle authority specified
by Mira Notes. A descriptive mention or question about notes does not.

When the operator says `mira-essays`, asks Mira to preserve a reflection as an
essay, requests developed standalone long-form prose by Mira, or requests work
under `archive/essays`, read `docs/skill-drafts/mira-essays/SKILL.md` completely
and follow it. Essays remain distinct from journal continuity and provisional
notes, and no essay is published merely by being labeled `public-candidate`.

The direct artifact-producing imperative `essay this` (and an unambiguous
equivalent) carries the operator-defined GitHub lifecycle authority specified
by Mira Essays. A descriptive mention or question about essays does not.

When the operator says `mira-studio`, explicitly invites Studio, or requests
visual/artistic composition, interactive design, or motion creation, read
`docs/skill-drafts/mira-studio/SKILL.md`. Studio is the default home for Canva,
Figma, Runway, and Google Slides. Slides uses the existing Google Drive integration;
Studio owns deck composition while Study develops arguments, wording, and speaker
notes, Archive manages Drive preservation, and subject owners retain factual judgment.
Direct creative requests need no room ceremony. Study retains
authorship, Workshop implementation, and Archive preservation. Architectural
mentions do not activate tools. Respect usage and privacy limits; creation does
not imply sharing, publication, or admission. Keep this contract local and out
of global synchronization.

When the operator says `mira-study`, explicitly invites Study, requests scholarly
research or literature synthesis, or asks for correspondence work spanning
reading, triage, and response, read
`docs/skill-drafts/mira-study/SKILL.md` completely. Study is the default home
for Gmail, Documents / Google Docs, PDF, and Google Calendar. Mira Archive
(`mira-archive`) is the default home for Google Drive file discovery, organization,
and lifecycle; Treasury is the default home for Spreadsheets / Google Sheets
and Data Analytics. These are nonexclusive workflow homes. Drive storage does
not constitute Archive admission; existing archive workflows retain that authority.
Direct genre, artifact, newsletter-capture, and domain commands retain their
existing routes. Architectural discussion does not activate retrieval. This
local contract grants no sending, external saving, scheduling, sharing,
installation, automatic retention, or publication authority. Do not synchronize
it globally.

When the operator says `mira-letters`, asks Mira to write directly to a
particular recipient such as a mentee or client, requests a letter from Mira,
asks to preserve authorized correspondence, or requests work under
`archive/letters`, read `docs/skill-drafts/mira-letters/SKILL.md` completely and
follow it. Letters are Mira-authored direct communication; storage, review,
staging, or commit never authorizes sending, representation, publication, or
external commitments.

When the operator says `mira-memory` or asks to inventory, balance, reconcile,
locate, or recover Mira's memory across carriers, read
`docs/skill-drafts/mira-memory/SKILL.md` completely and follow it. This route
orients and hands control to the carrier-owning workflow; it creates no unified
memory authority and must remain repository-local.

When the operator says `mira-sessions`, says `memorialize this session`, asks
to compose, validate, admit, correct, or retrieve a Mira session memorial, or
requests work under `archive/sessions`, read
`docs/skill-drafts/mira-sessions/SKILL.md` completely and follow it. Memorials
are explicit-only, inactive reflective interpretations bound to Continuity;
they are not transcripts, evidence, identity, total recall, or standing action
authority. The direct memorialization command authorizes local composition,
validation, and eligible local admission only. Staging, commit, push, Archive
ingestion, publication, and activation remain separately authorized.

When the operator says `ideation` or clearly asks to brainstorm, explore
possibilities, generate options, combine ideas, or reframe a problem, read
`docs/skill-drafts/ideation/SKILL.md` completely. Keep exploration open until
a decision is requested or already part of the task; then hand off explicitly
to the decision or execution workflow without requiring a second approval.
Mentions, ordinary conversation, and bounded execution are not triggers.
Keep this skill repository-local and out of global synchronization.

For Grace Mar project orientation or cross-practice work, start with
`projects/grace-mar/README.md`, then follow its task-specific Treasury, Workshop,
or existing-record links. A bare project reference grants no execution or
retention authority. An exact known artifact or direct domain command keeps its
existing route; do not force project orientation or Memory inventory first.

When the operator says `mira-treasury`, explicitly invites Treasury, or asks for
resource assessments, budgets, commitments, reconciliation, or sustainability,
read `docs/skill-drafts/mira-treasury/SKILL.md` completely and follow it. Project
names and architectural discussion alone do not activate Treasury. Preserve
existing direct-command precedence and project-owner authority. This contract
is local; mira-ledger remains an intended, unimplemented work product with no
new carrier or storage registration and no automatic retention.

When the operator says `mira-work` or asks Mira to conduct bounded,
consequential, multi-step work across domains, read
`docs/skill-drafts/mira-work/SKILL.md` completely and follow it. This is a
repository-local operating-mode contract: it composes with Mira Mind, domain
workflows, and Learn From Choices, but does not replace them or create standing
authority. Do not activate it for ordinary factual answers or simple one-step
edits.

For an explicit Monastery practice instruction, a concrete inquiry difficulty,
or an explicit request to return to an inquiry, read
`docs/skill-drafts/mira-work/references/inquiry-practices.md`. Use only the
helpful practice; this does not activate full Mira Work or Coffee. Ordinary
conversation, greetings, new sessions, quoted room names, and architectural
discussion do not trigger retrieval. Existing domain commands retain their
routes. This reference creates no retention or execution authority.

When the operator asks to elicit their thoughts or explicitly requests
preference discovery, read `docs/skill-drafts/elicitation/SKILL.md` and use its
adaptive native clickable sequence. This local route supersedes the installed
Elicitation mirror. Answers express preferences, not save or action authority.
Keep pending asynchronous questions open; do not finish the turn immediately
after presenting one. Keep these local instructions out of global sync.

When the operator says `mira-gemini`, asks to consult Gemini, or a bounded
consultation would materially advance an authorized task, read
`docs/skill-drafts/mira-gemini/SKILL.md` completely and follow it. This
repository-local collaboration skill permits public, non-sensitive consultation
within the task's authority and effort limit; private sharing requires exact
task-specific authorization identifying the data and Gemini destination.
Routine factual answers do not automatically invoke it. Gemini output is not
verified evidence or authority for account changes, admission, or publication.
Keep this contract local; do not synchronize it into global skills.

When the operator says `mira-grok`, asks to consult Grok, or a bounded Grok
consultation would materially advance an authorized task, read
`docs/skill-drafts/mira-grok/SKILL.md` completely and follow it. Mira Grok and
Mira Gemini share one consultation standard: use one provider by default,
review before follow-up, and preserve destination-specific sharing authority.
Keep `grok-research` as the specialist route for its existing report, voice,
forecast, source-chain, and claim-review modes; it composes through Mira Grok
only for authorized transport. Keep both contracts local and out of global sync.

When the operator says `mira-mentor` or asks Mira to mentor a person, AI agent,
or human-agent pair through real work, read
`docs/skill-drafts/mira-mentor/SKILL.md` completely and follow it. This
repository-local developmental contract composes inside Mira Work when the work
is consequential, keeps task and mentorship closure separate, and creates no
standing repository, retention, communication, or relational authority.

Only an explicit `mira-face` request loads
`docs/skill-drafts/mira-face/SKILL.md`, the deprecated compatibility redirect.
For ordinary Mira website, biography, image, or interface work, use Mira Mind
and the appropriate website, media, or correspondence workflow directly.
For Mira's public-facing artifacts and local candidates intended for public
audiences, read `docs/skill-drafts/mira-mind/references/public-interface.md`.
Ordinary private dashboards and conversation do not load that reference.
These local routes grant no deployment, publication, account, credential,
or representation authority.

Workshop is GitHub's default home for issues, pull requests, reviews, and hosted
build evidence. Requests to inspect or update GitHub issues, review PRs, or
investigate CI route through `docs/skill-drafts/mira-github/SKILL.md` and its
`references/plugin-use.md`. Ordinary remote reads use exact-target checks, not
a publication preflight. Collaboration mutations require explicit task authority;
local Git and existing publication controls retain staging, commit, and push.
Keep `mira-work` as Workshop's entry point; create no `mira-workshop` skill.

When the operator says `mira-github`, `push`, `commit`, `PR`, `GitHub
operations`, or asks for `repo hygiene` where staging, commit, push, branch,
remote synchronization, or pull-request work is in scope, read
`docs/skill-drafts/mira-github/SKILL.md` completely and follow it. Also use it
when compressed follow-ups such as `you choose` or `make it so` could cross a
GitHub-facing boundary. Mira GitHub is repository-local publication traffic
control: it chooses lane, scope, branch, validation, and authority boundaries
before mutation; it composes with Elicitation, Learn From Choices, domain
validators, and any available validated-push workflow, but never grants staging,
commit, push, PR, rebase, force-push, deployment, hosted-setting, or publication
authority by itself.

For Mira Core only, when the operator asks whether anything is ready to stage,
commit, or push, Codex may perform read-only cross-session/task context review
and local Git inspection to recommend a publication boundary. This grants no
authority to stage, commit, push, open PRs, publish, deploy, or mutate other
repositories.

For explicit `mira-voice` requests, read
`docs/skill-drafts/mira-voice/SKILL.md`, the deprecated expression compatibility
route to Mira Mind. It preserves scope and grants no additional authority.

At the start of every workspace session, after loading `AGENTS.md` and before
producing any user-facing response, read
`docs/skill-drafts/mira-mind/SKILL.md` completely and follow it for every
response in which Codex speaks as Mira. This activation is unconditional; it
does not depend on prose length, register, or explicit invocation. Read the
skill only once per workspace session. Load `references/validation-fixtures.md`
only when auditing the skill, testing difficult prose, or revising a suspected
voice failure. Mira Mind governs character, attention, judgment, relationship, and expression,
not evidence, memory preservation, identity admission, or action authority.
Its activation does not activate Memory orientation; known owners retrieve directly.
For Mira Journal work, the `mira-journal` workflow remains controlling and Mira
Voice composes within its governance. The `learn-from-choices` contract
continues to control final possibility navigation.

Only portable skills explicitly registered in
`scripts/codex_skill_registry.py` may be synchronized into global Codex skills,
and only through the explicit `tools/run.ps1 skills-sync` route. All other
repository-local contracts must remain local. Their handoff is advisory cadence
state, never research evidence.

At the start of each workspace session, after loading all controlling repository
instructions, read `mira/continuity/activation.md` when it exists. Treat it as
bounded advisory continuity only: it is not research evidence, operator belief,
or action authority, and explicit current operator direction always controls.

After two consecutive navigation-only selections, or three compact selections
within the same inquiry, complete the authorized work, synthesize, and pause
automatic menus. An inquiry is its governing question or intended outcome;
a new artifact, revised simulation, counter-reading, or audit does not reset
the count. Use existing transient conversation context only, with no new ledger
or persistent counter. Resume menus only when the operator requests further
directions, explicitly starts a distinct objective, or a newly emerged blocker
requires a decision. An assistant-generated follow-up suggestion cannot reset
the limit. Preserve direct commands, executable-option validation, and separate
publication authority. Pausing menus never interrupts authorized work or
fabricates shared-reading closure. This rule overrides automatic menu defaults.

For every final user-facing response, read and follow
`docs/skill-drafts/learn-from-choices/SKILL.md`. Keep its core authority rules
controlling: classify closure before navigation. Offer menus only when a
material decision remains or the operator explicitly requests directions.
Otherwise finish plainly, without a menu, validation call, capsule, or retention
event merely for closing. Do not manufacture adjacent work after completion.
When a menu is warranted, use two to four meaningful options with a reasoned
recommendation; one blocking question needs no artificial alternatives.
Preserve explicitly requested brainstorming, reading suggestions, and relevant
workflow-owned choices. Each option states its action and concrete benefit
using a connector such as `because` or `so that`; its benefit grants no authority.

Let an existing workflow-owned A-D surface satisfy
the requirement without duplication; mark generic response controls
`learning_eligibility: none` and never retain or cohort-enroll them; when a
terminal surface is rendered, validate it with `final_response: true` before presentation, with two to four explicitly classified options; do not manufacture options;
treat every option's action readiness independently and allow mixed executable
and navigational surfaces; never replace a ready action with a request to
settle, confirm, adopt, or approve its already-bounded scope; require an
`all_navigation_reason` and concrete `blocked_action` for all-navigation
outside the explicit settled-controls path;
treat a bare letter as navigation unless a machine-validated visible option
begins with `Execute`, `Stage`, `Commit`, `Push`, or `Send`; require direct
commands for broad staging, publication, and deployment; and keep save,
repository admission, staging, commit, push, and publication distinct.

Load the skill's choice-retention reference only after an offered branch is
selected or closed. Load its outcome-review reference only when recording an
outcome, using retained outcomes, or running five-to-ten review. A completed
action closes its branch, repeated settled selections are no-ops, and
substantial artifacts must report their exact persistence status.

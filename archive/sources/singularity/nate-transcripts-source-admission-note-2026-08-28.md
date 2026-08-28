# Nate Transcript Source Admission Note

Status: `admission-review-note`
Created: 2026-08-28
Scope: Fifteen untracked Nate Herk and Nate B. Jones transcript bodies referenced by the Applied AI Opportunity Ledger.
Related ledger: `archive/sources/singularity/applied-ai-opportunity-ledger.json`
Authority boundary: This note documents admission posture only. It does not admit the files to Git, verify transcript claims, establish publication rights, repair metadata, or authorize reuse outside internal research.

## Summary

The Applied AI Opportunity Ledger currently includes rows derived from fifteen local transcript files that are not present on the clean landing branch from `origin/main`. The files are present in the original worktree and appear to be substantive transcript bodies rather than stubs.

All fifteen files carry an operator-supplied transcript rights posture:

`Operator-supplied transcript; internal research use only; publication and reuse rights not established`

The main governance question is therefore not file completeness. The question is whether these internal-research transcript bodies should be admitted alongside the generated ledger so the ledger does not point to absent sources.

## Candidate Files

| path | creator | observed_size | date_published_status | admission_note |
|---|---|---:|---|---|
| `archive/sources/singularity/nate-herk/transcripts/2026-08-23-i-deleted-all-my-claude-skills-and-claude-got-smarter.md` | Nate Herk | 2,980 words | unknown | Substantive transcript body; publication date not independently established. |
| `archive/sources/singularity/nate-herk/transcripts/2026-08-23-i-built-the-ultimate-claude-website-design-skill-steal-this.md` | Nate Herk | 4,333 words | unknown | Substantive transcript body; publication date not independently established. |
| `archive/sources/singularity/nate-herk/transcripts/2026-08-23-how-to-sell-claude-workflows-without-starting-an-agency.md` | Nate Herk | 2,242 words | unknown | Substantive transcript body; publication date not independently established. |
| `archive/sources/singularity/nate-herk/transcripts/2026-08-23-how-to-build-a-one-person-ai-business-using-claude-code.md` | Nate Herk | 6,643 words | unknown | Substantive transcript body; source row `AAO-20260823-004` anchors the Constraint-to-Automation Sprint. |
| `archive/sources/singularity/nate-herk/transcripts/2026-08-23-18-months-of-pricing-ai-automations-in-21-mins.md` | Nate Herk | 5,149 words | unknown | Substantive transcript body; supports Automation Pricing Clinic mapping. |
| `archive/sources/singularity/nate-herk/transcripts/2026-08-21-turn-claude-into-a-one-person-marketing-team-in-38-mins.md` | Nate Herk | 9,487 words | unknown; not present in supplied source material and not independently established | Substantive transcript body with explicit date caveat. |
| `archive/sources/singularity/nate-herk/transcripts/2026-08-21-this-stealth-model-makes-claude-code-free-heres-how.md` | Nate Herk | 3,612 words | 2026-08-21 | Substantive transcript body; publication date present in metadata. |
| `archive/sources/singularity/nate-herk/transcripts/2026-08-21-i-made-codex-and-claude-code-build-the-same-app.md` | Nate Herk | 4,989 words | unknown; not present in supplied source material and not independently established | Substantive transcript body; supports Agent Tool Selection Matrix mapping. |
| `archive/sources/singularity/nate-herk/transcripts/2026-08-21-how-to-sell-these-5-most-in-demand-ai-automations-in-2026.md` | Nate Herk | 2,442 words | unknown; not present in supplied source material and not independently established | Substantive transcript body; supports Five Demand-Ready Automations Catalog mapping. |
| `archive/sources/singularity/nate-herk/transcripts/2026-08-21-codexs-browser-use-automates-literally-anything.md` | Nate Herk | 4,413 words | unknown; not present in supplied source material and not independently established | Substantive transcript body. |
| `archive/sources/singularity/nate-herk/transcripts/2026-08-21-a-week-of-grok-bot-lessons-in-10-mins.md` | Nate Herk | 2,861 words | unknown; not present in supplied source material and not independently established | Substantive transcript body. |
| `archive/sources/singularity/nate-b-jones/transcripts/2026-08-21-glm-5-3-in-claude-code-is-a-game-changer.md` | Nate B. Jones | 4,103 words | 2026-08-21 | Substantive transcript body. |
| `archive/sources/singularity/nate-b-jones/transcripts/2026-08-17-one-cancelled-gym-class-agent-swarm-attacks.md` | Nate B. Jones | 4,091 words | 2026-08-17 | Substantive transcript body. |
| `archive/sources/singularity/nate-b-jones/transcripts/2026-08-16-ai-isnt-a-bubble-nvidia-500-billion-push-retirement.md` | Nate B. Jones | 2,895 words | 2026-08-16 | Substantive transcript body. |
| `archive/sources/singularity/nate-b-jones/transcripts/2026-08-14-grok-bot-is-the-first-ai-agent-you-just-install-is-it-worth-200.md` | Nate B. Jones | 3,927 words | 2026-08-14 | Substantive transcript body. |

## Admission Caveats

- These are transcript bodies, not only metadata records.
- Rights are limited to internal research unless separately established.
- Several Nate Herk records have unknown or unverified publication dates.
- The Applied AI Opportunity Ledger should not land with references to these files unless the files are admitted, the ledger is regenerated to exclude them, or the missing-source condition is explicitly accepted.
- No factual claims inside the transcripts have been verified by this review.

## Recommended Next Decision

Admit the fifteen transcript files only if the intended branch is allowed to carry internal-research transcript bodies. If not, regenerate the clean landing ledger from the nine source files already present on `origin/main` and treat the twenty-four-row ledger as a local working view until the source bodies are governed.

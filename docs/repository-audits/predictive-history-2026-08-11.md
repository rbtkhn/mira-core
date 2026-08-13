# Repository Audit: `rbtkhn/predictive-history`

## Overall judgment

`predictive-history` is an unusually well-structured public educational corpus
with strong identity boundaries, explicit provenance, machine-readable
indexes, and meaningful landed-corpus tests. Its weakest layer is operations:
the only hosted workflow has failed on every observed run, its trigger coverage
no longer matches the repository's canonical namespace architecture, and no
committed workflow appears to run the repository's substantial test suite.

The repository is therefore stronger as a governed corpus than as an operating
public delivery system.

## Audit contract

- Target: `https://github.com/rbtkhn/predictive-history`
- Revision: `266c3e5af765541e1b1b8c88f835adf179e1a502`
- Default branch: `main`
- Mode: external, whole repository
- Visibility: public
- Inspection ceiling: structural, with bounded content inspection of
  controlling files, workflow configuration, packaging, and representative
  tests
- Tree: 1,562 entries; GitHub reported the recursive tree as complete and not
  truncated
- Main lenses: purpose, architecture, tests, documentation, automation,
  governance, reproducibility, hygiene, and bounded security
- Excluded: truth adjudication of historical claims, transcript-quality
  review, full corpus-body inspection, private workshop material, and creator
  psychology
- Audit contract identifier: `RA-PH-266c3e5-20260811`

The repository declares itself the public namespace-catalog and
study-orientation layer for 206 chapters: 147 lectures, 43 essays, and 16
interviews. Its private workshop and large-media boundaries are explicit.

## Validation-plane coverage

| Plane | Coverage | Assessment |
|---|---|---|
| Change-time | Bypassed/declared-only | No workflow was found that runs `pytest` or the main corpus validator on pushes or pull requests. |
| Landed corpus | Sampled | Static inspection found substantial pytest coverage and internal validators, but the pinned corpus could not be executed locally because Git HTTPS checkout was unavailable. |
| Hosted state | Observed | Eight public Pages workflow runs were inspected through GitHub's API; all eight failed. Branch protection and required checks were unavailable without authenticated provider access. |

## Findings

### RA-PH-01 — Public study-edition deployment is persistently failing

- Severity: **high**
- Confidence: **high**
- Status: confirmed
- Lens: automation and hosted operations
- Plane: hosted state

The repository defines the study edition as a public surface, but every visible
workflow run failed: eight failures from June 12 through June 27, 2026. The
latest failure is bound to the audited HEAD, `266c3e5`. Its `build` job failed
during **Build study edition**, and deployment was skipped.

The practical consequence is not merely weak CI reporting. The repository's
declared hosted reader surface is not reaching deployment through its only
observed delivery workflow.

The strongest rival is that GitHub Pages may be intentionally dormant while
the repository remains useful directly through GitHub. That interpretation is
weakened by the active workflow, the README's public study-edition routing, and
the deployment environment declared in the workflow.

Evidence that would close or reduce the finding:

- a later successful build and deployment at the same or newer canonical
  corpus state;
- an explicit declaration that Pages is retired; or
- evidence that another hosted path is the actual public study edition.

Recommended route: reproduce
`python scripts/build_study_edition.py --all-parts` at the pinned revision,
repair the first deterministic failure, then validate every declared part
before checking hosted deployment.

### RA-PH-02 — Workflow triggers still follow a retired repository topology

- Severity: **medium**
- Confidence: **high**
- Status: confirmed
- Lens: automation and architecture
- Plane: cross-plane

The Pages workflow triggers on changes to:

- `site/**`
- three study-edition scripts
- `book/volume-ii/**`

But the repository's canonical public corpora now live under:

- `lectures/`
- `essays/`
- `interviews/`
- `commentaries/`
- `data/`
- relevant portions of `docs/`

The current contracts describe `book/` and the two-volume reader model as
deprecated compatibility surfaces. Consequently, a canonical chapter, card,
route, commentary, or index change may not trigger rebuilding or deployment,
while a retired `book/volume-ii/**` path still does.

The likely effect is hosted-state drift: GitHub can contain a newer canonical
corpus while Pages remains built from an older one.

A credible rival is that all canonical corpus changes are expected to
regenerate and commit `site/**`, indirectly activating the workflow. No
change-time control inspected here proves that contributors must or will do so,
so this remains an unresolved manual dependency rather than enforced coverage.

Recommended route: derive workflow path coverage from the current public
repository contract and add a deterministic check showing that each canonical
input either triggers the build or must update a triggering derived artifact.

### RA-PH-03 — The canonical export contract still presents the deprecated two-volume identity

- Severity: **medium**
- Confidence: **high**
- Status: confirmed
- Lens: documentation and governance
- Plane: landed corpus

The current identity surfaces consistently describe the repository as a
**namespace catalog hub** and mark the two-volume `ph-civ`/`ph-apo` model as
deprecated onboarding.

However, `docs/contracts/export-contract.md` still declares:

- the public artifact as a "two-volume public ph-civ artifact";
- `ph-civ` as Volume I; and
- `ph-apo` as Volume II.

This is not merely historical terminology in an archive file. `AGENTS.md`
routes agents to that export contract as a current controlling document. A
downstream export or AI agent following it can therefore revive the exact
reader architecture that the present repository identity forbids as the
default.

The rival interpretation is that the contract intentionally records
compatibility exports. If so, its authority and scope need to say that
explicitly and lead with the canonical namespace model.

Recommended route: revise the export contract around the namespace catalog,
preserve `ph-civ` and `ph-apo` only as named compatibility outputs, and add it
to the existing identity-contract tests.

### RA-PH-04 — Substantial tests exist, but no change-time workflow enforces them

- Severity: **medium**
- Confidence: **high**
- Status: confirmed
- Lens: tests and validation
- Plane: change-time

The repository contains meaningful tests for:

- repository identity;
- public/private boundary leakage;
- documentation redirects;
- catalog and triage consistency;
- public-surface inventories;
- chapter namespace guards;
- transcript structure;
- patterns and CLI behavior.

`AGENTS.md` also names `python -m pytest` and the CLI validator as useful
checks. Yet the only workflow found is the Pages deployment workflow, and it
does not run the pytest suite or the main repository validator.

This creates a gap between well-designed landed-corpus controls and actual
change-time enforcement. A contributor can merge a change that violates
repository identity or public-boundary invariants unless those checks are run
manually or protected by unobservable hosted settings.

Branch protection and required checks were unavailable, so this report does
not infer that merges are entirely unprotected. The finding is limited to the
absence of committed change-time enforcement.

Recommended route: add a minimal validation workflow for pull requests and
pushes covering `pytest` plus a read-only corpus/index validation command, then
decide separately whether it should become a required check.

## Credible strengths

- **Clear public/private membrane:** The repository repeatedly distinguishes
  its public distribution role from private workshop material and large-media
  storage.
- **Strong corpus architecture:** The 206-card single source of truth feeds
  human and machine indexes across three canonical media namespaces.
- **Migration discipline:** Redirect stubs and tests preserve moved
  documentation while preventing old paths from silently becoming canonical.
- **Agent-oriented onboarding:** `START-HERE.md`, `AGENTS.md`, `llms.txt`,
  `llms-full.txt`, and `data/llm-experience.json` form a deliberate
  provider-neutral entry system.
- **Meaningful tests:** The tests inspect identity language, leakage
  boundaries, index drift, redirect correctness, transcript rails, and
  public-surface integrity—not only low-level code.
- **Rights caution:** The pending-license document clearly warns against
  assuming redistribution or commercial reuse rights. GitHub correspondingly
  reports no asserted license.
- **Honest commentary status:** Seeded commentaries are represented as open
  project canvases rather than finished scholarship.
- **Conservative growth governance:** Reach goals are treated as ambitions
  requiring measurable machinery and human-approved launch steps, not as
  agent-completable outcomes.

## Cross-finding mechanism

Three findings share one mechanism: the repository's conceptual architecture
migrated from a two-volume model to a namespace catalog faster than its
operational layer migrated.

The canonical identity, corpora, indexes, and tests largely reflect the new
system. The export contract and Pages workflow retain older assumptions. This
is ordinary migration residue, but it now crosses validation planes:

```text
current corpus and identity
        ↓
partly stale export contract
        ↓
retired-path workflow triggers
        ↓
repeatedly failing hosted build
```

The most valuable repair sequence would therefore be:

1. reproduce and fix the Pages build;
2. align workflow inputs with canonical namespaces;
3. update the export contract; and
4. enforce the existing test suite at change time.

## Bounded architectural working profile

Outside the formal findings, the repository supports this limited profile of
its construction:

- Observed: strong preference for explicit boundaries, stable IDs,
  machine-readable indexes, compatibility redirects, and provider-neutral AI
  onboarding.
- Observed: migrations preserve old reader surfaces as tombstones rather than
  deleting their history.
- Inference: the repository is designed as both a human study environment and
  an AI-navigable public knowledge interface.
- Inference: governance is ahead of operations—the conceptual and documentary
  controls are more mature than deployment reliability.

These observations do not establish the creator's private motives, psychology,
biography, or profession.

## Unavailable evidence

- Local full test execution: blocked because both Git and `curl` failed at
  Windows Schannel credential acquisition, while GitHub API structural reads
  remained available.
- Failure logs beyond the failed job step: unavailable.
- Branch protection and required checks: the provider API returned
  authentication-required.
- Deployment URL health and currently served revision: not established.
- Historical first-introduction dates: not asserted; the repository has 158
  visible commits, but commit chronology was not treated as proof of
  conceptual origin.

## Audit disposition

The repository is not structurally unsound. It has a coherent purpose, serious
corpus governance, and unusually thoughtful AI-facing navigation. Its immediate
reliability problem is the gap between those controls and the public delivery
path.

Authority effect: none. This audit grants no authority to modify, repair,
stage, commit, push, publish, deploy, communicate, or alter hosted settings.

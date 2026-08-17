---
name: mira-github
description: "Repository-local publication traffic control for GitHub-facing work in Mira Core. Use when the operator says push, commit, PR, GitHub operations, repo hygiene with staging/commit/push/branch/remote scope, or compressed follow-ups such as you choose or make it so when they could cross staging, commit, branch publication, PR, or main synchronization boundaries. Choose lane, scope, branch, validation, and authority boundaries before any GitHub-facing mutation."
---

# Mira GitHub

Control publication momentum in a dirty, governed, high-throughput repository.
This skill is not a Git tutorial and does not replace domain validation,
Elicitation, Learn From Choices, or a publication-proof workflow. It decides
what GitHub lane is safe, what evidence is missing, and where authority stops.

Use this skill before staging, committing, pushing, opening a PR, synchronizing
`main`, or interpreting compressed operator direction that could lead there.

## Start with fresh state

Do not rely on status, branch, validation, or authority remembered from an
earlier branch of the session. After long intake, scoring, repo hygiene,
forecast review, menu navigation, or commit preparation, treat `push`,
`commit`, `PR`, and similar commands as a fresh publication boundary.

Run a bounded preflight. Capture porcelain status before printing it; report
the total and top-level groups first. Print complete paths only when the count
is at most 200 or an exact repair requires them:

```powershell
git rev-parse --show-toplevel
git branch --show-current
git remote -v
git log --oneline --left-right --decorate origin/main...HEAD -20
$status = @(git status --porcelain=v1 --untracked-files=all)
$status.Count
$status | ForEach-Object {
    $path = $_.Substring(3)
    ($path -split '[/\\]')[0]
} | Group-Object | Sort-Object Count -Descending | Select-Object Name, Count
```

Use `git status -sb` only after the bounded inventory proves the output is at
most 200 entries, or restrict it to the exact named paths under review.

If the target remote or base branch is not `origin/main`, substitute the
declared target and state that substitution explicitly.

For remote actions only, run:

```powershell
gh auth status
```

When hooks mention Git LFS, also inspect LFS readiness before a remote action:

```powershell
git config --get core.hookspath
git lfs version
```

If `git lfs` is unavailable, preserve the hook text or failure tail needed to
prove the blocker. Do not retry blind pushes.

## Choose the lane first

Resolve the operator's requested publication endpoint before choosing the safe
route. A safety default may change the route used to reach that endpoint; it
must never silently replace the endpoint itself. In particular:

- If the operator explicitly requests `main`, treat a branch push as an
  intermediate state only. Keep the requested main landing visibly open until
  `main` is updated or the operation stops with a named blocker.
- If the endpoint is genuinely ambiguous, ask one minimal target question
  before publishing. Do not infer that the safer branch default is the
  operator's desired final state.
- If a previously requested endpoint remains active across repository or
  branch repair, carry it forward unless the operator changes it.
- Never report publication complete merely because an intermediate branch was
  pushed. Name both the reached boundary and any requested landing still
  pending.

Classify the next safe lane before staging or publishing:

- `inspect-only`: read-only diagnosis, audit, or planning.
- `commit-only`: create or prepare a local commit; no remote action is in
  scope.
- `branch-push`: publish an exact bounded commit to `codex/...`.
- `PR-ready`: branch exists or can be pushed and the next external step is PR
  preparation.
- `main-sync-plan`: `main` is ahead, behind, diverged, or dirty enough that
  synchronization needs its own plan.
- `main-push`: direct push to `main`, allowed only when explicitly requested
  and proven authenticated, non-divergent, LFS-safe when applicable, and
  validated.

Default to branch publication over direct `main` publication. Use:

```text
codex/<domain>-<object>-<action>-YYYYMMDD
```

Examples:

```text
codex/forecast-lebanon-hormuz-review-20260815
codex/mira-github-skill-20260815
codex/archive-aug14-intake-cleanup-20260815
```

## Triage dirty work before staging

In a dirty tree, classify candidate paths before staging:

- `operator-work-in-progress`: unrelated or ambiguous work; leave untouched.
- `generated-drift`: generated views, indexes, or ledgers that may include
  unrelated corpus changes; inspect before inclusion.
- `governed-artifact`: archive, reality, verification, journal, skill, or
  other governed content; require the owning domain validation.
- `skill/control-change`: AGENTS, skill drafts, routing, scripts, or tests that
  alter agent behavior; require instruction-coherence validation.
- `publication-candidate`: exact paths or hunks eligible for a staging plan.

If dirty-tree scope cannot be recovered safely, stop with a bounded commit plan
instead of staging.

### Dry-check broad staging

Before `git add -A` or any repository-wide staging command:

1. Capture `git status --porcelain=v1 --untracked-files=all` without printing
   the full list.
2. Inspect `.gitignore` and the collection registry for hydrated corpus roots,
   continuity captures, generated mirrors, or other protected bodies.
3. Classify every untracked top-level group as intended publication,
   operator work, generated drift, or protected corpus material.
4. Fail closed if a protected root has become unexpectedly unignored, or if
   any untracked path remains unclassified.
5. Prefer `git add -u` for tracked-only repairs and exact path staging for a
   bounded publication candidate.

The dry check is read-only. Do not use `git add --dry-run` as the sole corpus
boundary: a missing ignore rule can make thousands of hydrated bodies appear
eligible while still producing technically valid Git output.

## Stage and commit narrowly

For `commit-only` or pre-publication work:

1. State the exact candidate paths and excluded known-dirty paths.
2. Prefer exact paths or controlled patch staging.
3. Avoid `git add -A` unless the operator explicitly requested whole-tree
   staging and the broad-staging dry check passed. When unrelated untracked
   work exists, use exact paths or `git add -u` and name the exclusion.
4. Verify:

```powershell
git diff --cached --stat
git diff --cached --check
git diff --cached -- <scoped paths>
```

5. Run the relevant validation class before committing:
   - `repo-structural`: repository instruction, script, test, or skill
     coherence;
   - `domain-governed`: archive, reality, verification, forecast, journal, or
     other domain validation;
   - `publication-proof`: exact push proof when available;
   - `unavailable`: named blocker and consequence.

Do not describe a working-tree file as published or public. Keep save, stage,
commit, push, PR, deployment, and hosted settings as separate boundaries.

## Publish only when proven safe

Before any push or PR:

1. Re-run the bounded Git state for the exact current commit.
2. Confirm `gh auth status` is valid.
3. Confirm LFS readiness when hooks require it.
4. Confirm the target branch and refspec.
5. Confirm validation results and their scope.

If a `validated-push` workflow is present in the current repository, use it for
proof and exact target-SHA publication once an immutable commit exists. If it
is absent, do not pretend proof publication is available; either use ordinary
Git branch publication after the above checks or stop with a resumption packet,
depending on the operator's requested boundary and repository risk.

Never force-push, rebase, broaden the refspec, open a PR, mutate hosted
settings, or publish generated drift as part of a plain `push`.

## Handle credential-context splits

Sometimes the operator repairs GitHub auth in an interactive shell while the
current Codex process still sees a stale or invalid token. Treat operator
terminal output as factual evidence about that shell, not proof that this
process can push.

When the operator shows successful `gh auth status` but this process still
reports invalid auth:

1. Check the local credential context:

```powershell
gh auth status
gh auth token --hostname github.com
git config --show-origin --get-regexp "credential.*github"
```

2. Try exactly one normal exact-refspec push if the branch, target SHA, LFS, and
   dirty-tree exclusions are still safe.
3. If that fails silently or with `401`, use exactly one elevated exact-refspec
   push when credential/keyring access is the likely blocker.
4. Verify success with:

```powershell
git ls-remote --heads origin <branch>
```

5. If elevated push fails or approval is unavailable, stop with a resumption
   packet telling the operator to `cd` to the repository and run the exact
   refspec manually.

Do not repeat login loops, change credential helpers globally, erase tokens,
force-push, or broaden the target branch to work around a credential-context
split.

## Preserve authority exactly

Soft assent such as `you choose`, `sounds good`, `very well`, or `I defer to
you` does not authorize staging, commit, push, PR creation, rebasing, hosted
settings, or external communication.

A menu letter authorizes commit or push only when it came from a validated
action-ready surface whose visible label begins with `Commit:` or `Push:` and
whose effect matches that verb. Otherwise, carry the selected branch through
read-only planning until the exact authorization boundary appears.

A direct `push` authorizes only the bounded push currently proven safe. It does
not authorize rebasing, force-pushing, broad staging, PR creation, or hosted
setting changes.

## Handle blockers with a resumption packet

When commit succeeds but push or PR is blocked, emit a publication resumption
packet:

```text
Publication resumption packet:
Repository:
Current branch:
Target commit:
Intended branch/refspec:
Upstream divergence:
Remote/auth/LFS blocker:
Validation already run:
Excluded paths or hunks:
Exact safe next step after repair:
Authority effect: none.
```

Use this packet for invalid GitHub auth, missing LFS support, unknown remote,
silent push failure, divergent `main`, unavailable publication proof, or any
blocker that would otherwise require rediscovery in the next session.

## Track diagnostic benchmarks

Benchmarks are review signals, not pass/fail execution gates. Report them
briefly in final or handoff language when they materially describe the run:

- `speed`: time to lane classification, time to bounded next action, repeated
  rediscovery avoided.
- `success-rate`: intended boundary reached, blocked push received resumption
  packet, unrelated dirty-tree inclusion avoided.
- `friction`: clarification loops, stale-state reruns, operator restatement of
  scope, blocker, branch, exclusions, or repaired auth state.

Use these v1 targets for later review:

- classify lane within roughly 2 minutes after `push`, `commit`, or
  `repo hygiene`;
- produce a resumption packet for every blocked push;
- include 0 known unrelated dirty-tree paths;
- check auth and divergence before every remote push;
- detect and resolve credential-context split without asking the operator to
  repeat a correct auth repair more than once;
- reduce repeated operator restatement of the same publication scope over five
  comparable uses.

Do not add a new metrics store for v1. Let final answers, handoffs, and choice
review carry the lightweight evidence.

## Finish with the real boundary

End by stating which boundary was reached:

- inspected only;
- commit plan prepared;
- commit complete, push not requested;
- commit complete, push blocked with resumption packet;
- branch pushed and verified;
- branch pushed and verified; requested main landing still pending;
- PR-ready;
- main synchronization requires a separate plan;
- remote publication unavailable.

Name the validation class used and any unavailable evidence. State explicitly
that the result grants no further commit, push, PR, deployment, or hosted-state
authority.

## Validation fixtures

When auditing or revising this skill, read
[`references/validation-fixtures.md`](references/validation-fixtures.md).
Use its normal, edge, failure, and ambiguous cases to verify bounded status,
dirty-tree isolation, publication preconditions, and lock handling.

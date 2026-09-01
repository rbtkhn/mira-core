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

For every consequential Git action, first run `tools/run.ps1 mira-work
snapshot --repo <absolute-repository> --remote <remote/branch> --format json`
and retain its digest. A snapshot is stale after a commit, checkout, rebase,
migration, relevant environment change, or remote fetch. Re-snapshot
immediately after every Git mutation; never carry a stale digest across the
next action boundary.

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
git worktree list
git fetch --no-tags origin main
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

The exact-target fetch must succeed before using a remote-tracking ref for push
or PR lane classification. If fetch or equivalent exact remote verification is
unavailable, local inspection and commit work may continue, but remote
publication must stop with a publication resumption packet. `git ls-remote`
after a push proves the reached SHA; it does not replace this pre-publication
freshness check.

### Make side worktrees visible

Side worktrees are publication state, not invisible implementation detail. At
every fresh publication boundary, inspect `git worktree list` and surface any
active worktree other than the current one when it is on `main`, tracks
`origin/main`, points at a `codex/...` publication branch, or could plausibly
land on the same target branch during the current task.

Treat hidden side-worktree use as a process failure, even when the Git result is
technically correct. If a side worktree exists, say whether it is active,
detached, branch-bound, publication-capable, untouched, or intentionally
retained before asking the operator for a commit or push decision.

Before creating a side worktree, state all of the following and wait for
explicit operator approval unless the operator has already authorized an exact
workflow that visibly requires that worktree:

- branch name;
- absolute worktree path;
- purpose and scoped files or domain;
- whether the worktree may stage, commit, push, or only inspect/edit locally;
- expected cleanup condition; and
- how `main` will be refreshed after the worktree lands.

Do not leave worktrees as hidden infrastructure. If a created worktree remains
after its publication or inspection purpose completes, report it in the final
response or resumption packet with its branch, path, current SHA, and intended
cleanup or retention reason.

Never create a side worktree merely to avoid a dirty working tree without first
making the dirty-tree boundary, target branch, worktree path, and cleanup plan
visible. Prefer exact-path staging in the current worktree when the requested
publication can be isolated safely.

### Clean stale worktrees deliberately

When the operator asks for worktree cleanup, separate Git-registered worktrees
from filesystem residue before deleting anything. Start with `git worktree
list`, then inspect each candidate with bounded status and path grouping. On
Windows, use a command-local `-c safe.directory=<absolute-worktree-path>` for
read-only inspection when ownership checks block Git; do not mutate global Git
configuration merely to inspect a stale worktree.

Classify every cleanup candidate before recommending removal:

- `clean-removable`: clean, no unique preservation value found.
- `dirty-with-salvage`: contains unique commits, missing canonical files,
  private payloads, or receipt-worthy state that should be copied, restored, or
  documented before deletion.
- `dirty-obsolete`: dirty state has been inspected and is superseded,
  intentionally abandoned, or already represented elsewhere.
- `filesystem-residue`: no longer Git-registered; only an exact orphaned path
  remains.
- `acl-blocked`: Windows ownership or ACLs prevent deletion or repair.

For dirty or detached worktrees, check for unique commits and preservation
value before removal. Treat untracked receipts, proposals, generated indexes,
or old planning ledgers as non-canonical until the current main registry,
index, seal, or owning validation surface proves whether their state has
landed. Keep private payload copying distinct from Git state, Archive
ingestion, staging, commit, push, or publication.

Require an explicit action-ready operator choice or direct command before any
destructive cleanup. Use narrow deletion in this order: exact registered
worktree path, exact empty parent directory, then exact orphaned residue path.
After each deletion, verify `git worktree list` and filesystem existence. If an
ACL blocks cleanup, report the exact owner, relevant ACL entries, blocked path,
and manual/admin next step; do not broaden into general permission surgery.

When cleanup changes preservation posture, save or report a receipt naming what
was removed, what was preserved, what remains blocked, and which boundaries
were not crossed: staging, commit, push, PR, publication, deployment, or Archive
ingestion.

### Protect local `main`

When the current branch is `main`, treat any non-empty
`origin/main...HEAD` comparison as a main synchronization boundary before
creating a new commit, staging broad changes, or reporting the repo as ready:

- `origin/main` ahead only: update local `main` first, normally by
  fast-forward, before committing on `main`.
- local `main` ahead only: name the exact local-only commits before any
  additional local commit or push decision.
- both sides have commits: stop and classify `main-sync-plan`; do not create
  another `main` commit until the operator authorizes the rebase or merge plan.
- dirty files overlap paths changed on `origin/main`: isolate, stash, or route
  the overlap explicitly before synchronization.

Default recommendation: avoid new commits directly on `main` while any active
side worktree exists that may publish to `origin/main`. Prefer a fresh
`codex/...` branch or worktree, then refresh `main` immediately after the
remote branch lands.

### Routine readiness scan

For repeated questions such as `anything pending`, `anything pending push`, or
`anything pending stage commit or push`, prefer a compact publication console:

```text
Dirty:
Staged:
Ahead:
Behind:
Remote:
Boundary:
```

Use the read-only helper when available:

```powershell
tools/run.ps1 publication-status --json
```

The helper is advisory only. It never stages, commits, fetches with mutation,
pushes, opens PRs, or replaces `publication-validation` or `validated-push`.
Use fresh Git truth and remote SHA verification for publication decisions; do
not rely on session summaries alone. Surface detailed commentary only when a
blocker, dirty publication candidate, validation requirement, remote mismatch,
or authority boundary changes the operator's decision.

### Expose publication readiness early

At the first explicit `commit`, `push`, `PR`, or end-to-end publication request,
run a compact readiness gate before substantial publication work or completion
language. Reuse the bounded Git inventory above, then check only the parts
relevant to the requested endpoint:

- resolve the exact repository, source commit or candidate scope, remote, and
  requested target;
- refresh the exact remote target when remote publication is requested or is
  an explicit later step in the same request;
- check GitHub authentication and required Git LFS support before describing a
  remote endpoint as reachable; and
- preflight the intended external temporary root before validators or a
  digest-bound push receipt will need it.

In Mira Core, preflight a concrete external temporary root before running
`tools/run.ps1 test` through a publication-validation route, not only before
Full or push-proof validators. Use the established session root when present;
otherwise prefer `C:\private\mira-core-temp` when it exists and is outside the
repository.

Keep the gate non-authorizing and finish it within roughly one minute when the
environment responds normally. For a local-only commit request, a remote
readiness failure does not block the commit; disclose it once as a likely later
publication blocker. For a request that includes push or PR, fail the remote
step early and preserve any separately authorized local work that can still be
completed safely.

Do not run this gate for ordinary implementation, read-only inspection, or a
local edit with no Git lifecycle request. Cache a stable unavailable state for
the current task and do not repeat the same probe unless credentials,
permissions, paths, requested endpoint, or other external state changes, or
the operator explicitly asks for a retry.

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

Before staging a governed publication candidate, resolve every candidate path
through the deterministic router:

```powershell
tools/run.ps1 publication-validation --path <path> --json
```

Run every returned validator and complete every returned manual check. Proceed
only when every path has an owner and every requirement has an explicit pass.
Treat `blocked`, an unknown path, ambiguous ownership, or an incomplete mixed
route as a staging blocker rather than guessing the owning validator.

For archive manifest changes, check whether the manifest diff contains source
rows from more than the current operator objective. Classify that state as
`manifest-entangled`: either stage the broader manifest transaction with an
honest commit boundary, patch-stage or split when practical, or pause. Do not
claim a pure named-source commit when the manifest includes earlier landed
sources or unrelated archive additions.

When the user asks what should be staged after archive intake or repair, name
ignored private corpus-body changes separately from Git-visible candidates.
Ignored body files can be saved and verified locally while remaining outside the
commit; staging the manifest or queue receipts does not publish the body text.

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

## Reuse validation evidence

Before commit, require the validation appropriate to the change. For a final
tree requiring Full validation, run exactly one uncached Full gate and record
its successful fingerprint. After committing unchanged bytes, invoke Full once
without force and require the same fingerprint with a cache hit; report the
evidence as reused rather than newly executed.

Before push, refresh Git status, authentication, target, and divergence without
repeating Full validation. Rerun Full only when repository bytes, executable
bits, runtime or dependency inputs, relevant environment, or result clarity
changed. A local fingerprint proves landed-corpus equivalence only; hosted
workflow state remains a separate claim.

## Publish only when proven safe

Before any push or PR:

1. Re-run the bounded Git state for the exact current commit.
2. Confirm `gh auth status` is valid.
3. Confirm LFS readiness when hooks require it.
4. Confirm the target branch and refspec.
5. Confirm validation results and their scope.

Use PowerShell-safe exact refspecs. Prefer `HEAD:refs/heads/<branch>` after
verifying `HEAD` is the intended immutable commit. For a stored SHA, delimit the
variable as `${sha}:refs/heads/<branch>`; never write `$sha:refs/...`, which
PowerShell interprets as a scoped variable. Verify the resulting remote SHA.

If a `validated-push` workflow is present in the current repository, use it for
proof and exact target-SHA publication once an immutable commit exists. If it
is absent, do not pretend proof publication is available; either use ordinary
Git branch publication after the above checks or stop with a resumption packet,
depending on the operator's requested boundary and repository risk.

In Mira Core, create the digest-bound check receipt under the preflighted
external session temporary root, supplied through
`MIRA_CORE_SESSION_TEMP_ROOT` or `--temp-root`, then use the returned absolute
receipt path for the push:

```powershell
tools/run.ps1 validated-push check `
  --repo <absolute-repository-root> `
  --remote <remote> `
  --source-sha <full-commit-sha> `
  --target-ref refs/heads/<branch> `
  --validation-profile full `
  --validation-result passed `
  --required-gate full `
  --required-gate-result passed `
  --temp-root <absolute-temp-root> `
  --json

tools/run.ps1 validated-push push `
  --receipt <absolute-receipt-path> `
  --temp-root <absolute-temp-root> `
  --json
```

When the required Full gate fails only on an unchanged baseline and the
operator directly authorizes that exact exception, record the narrower passing
profile and the failed required gate honestly. Add
`--exception-authorized`, a non-empty `--exception-basis`, the lowercase
SHA-256 `--failure-fingerprint` for the gate evidence, and the lowercase
SHA-256 `--authority-context-digest` for the validating interaction. Never
encode this state as a generic pass. A failed required gate without all four
exception fields fails closed, as does a failed narrower validation profile.

The check receipt has `authority_effect: none`. Invoke `push` only after a
direct bounded push command, an operator-defined note or essay lifecycle
shorthand, or a validated Elicitation option whose visible label begins with
`Push:` and whose effect is `push`. The command supports one new branch or one
fast-forward branch update; it rejects changed remote state, tags, deletion,
wildcards, abbreviated SHAs, multiple refs, and non-fast-forward publication.

Never force-push, rebase, broaden the refspec, open a PR, mutate hosted
settings, or publish generated drift as part of a plain `push`.

For hosted validation, locate the run by exact head SHA, then start one watcher:

```powershell
gh run watch <run-id> --repo OWNER/REPO --compact --exit-status --interval 15
```

Resume that watcher by its returned process identifier until terminal. Do not
start parallel watchers or emit repeated full job snapshots. After completion,
use one structured `gh run view` query to require the expected head SHA,
successful conclusion, and exact job count; for the current validation matrix,
exactly four jobs must pass.

### Windows main-merge friction

When a clean temporary worktree is needed for a `main` merge and archive paths
may exceed Windows defaults, create it with long-path support:

```powershell
git -c core.longpaths=true worktree add <absolute-temp-worktree> main
```

If post-push `git fetch` is blocked by a local `.git/FETCH_HEAD` permission
split after a validated push, use `git ls-remote --heads origin <branch>` as
the final remote SHA proof. Do not treat the fetch failure as a failed push
when the validated-push receipt and `ls-remote` agree on the exact target SHA.

## Handle credential-context splits

Sometimes the operator repairs GitHub auth in an interactive shell while the
current Codex process still sees a stale or invalid token. Treat operator
terminal output as factual evidence about that shell, not proof that this
process can push.

When the operator shows fresh successful GitHub authentication or a successful
manual push from an interactive terminal, but this process still reports
invalid auth, treat it as a credential-context split. Do not ask the operator
to repeat a completed login until this ladder has been tried or a named step
fails closed:

On Windows, explicitly check for the Codex sandbox identity split before
diagnosing ordinary token expiry. Normal task commands may run as
`<host>\CodexSandboxOnline` while approved commands run as the real interactive
Windows user, even when `USERPROFILE` and `APPDATA` point at that user's
profile. In that state, GitHub CLI may read `hosts.yml` account metadata while
failing to read the keyring-backed token, and Git Credential Manager may report
`SEC_E_NO_CREDENTIALS` or credential storage failure. Treat this as a sandbox
credential-boundary issue. Prefer the elevated exact-refspec verification and
push ladder below; do not fix it by changing global credential helpers, printing
tokens, erasing credentials, or asking for repeated browser login loops.

1. Check the local credential context:

```powershell
whoami /user
gh auth status
& gh auth token --hostname github.com *> $null
$tokenState = if ($LASTEXITCODE -eq 0) { 'present' } else { 'unavailable' }
$tokenState
git config --show-origin --get-regexp "credential.*github"
cmdkey /list | Select-String -Pattern 'github|git:https' -CaseSensitive:$false
```

The token command must redirect every output stream and only its exit code may
be inspected. Never capture, interpolate, or print token content. Report only
`present` or `unavailable`; do not claim to distinguish a missing token from an
inaccessible credential store.

2. Separate the two auth channels in the status report:
   - `gh-auth`: whether GitHub CLI can access a token in this process.
   - `git-https-auth`: whether Git itself can authenticate the exact remote
     operation.
   A failing `gh auth status` is not, by itself, proof that Git HTTPS push is
   impossible after the operator has just authenticated in another shell.
3. Reconfirm the exact branch, target SHA, target ref, upstream divergence, LFS
   readiness, and dirty-tree exclusions. Use a full-SHA refspec for assistant
   attempts:

```powershell
git push <remote> <full-source-sha>:refs/heads/<branch>
```

4. Try exactly one normal exact-refspec push if the branch, target SHA, LFS, and
   dirty-tree exclusions are still safe. Do this even when `gh-auth` is invalid
   if the operator has provided fresh successful terminal authentication and
   `git-https-auth` has not yet been tested in this process.
5. If that fails silently, with `401`, or with a Windows credential error such
   as `SEC_E_NO_CREDENTIALS`, use exactly one elevated exact-refspec push when
   credential/keyring access is the likely blocker.
6. If the operator performs the exact push manually and supplies terminal
   output, treat that output as factual evidence of the other shell's result.
   Verify from this process by the best available non-mutating route:
   first `git fetch --no-tags <remote> <branch>`, then
   `git rev-parse <remote>/<branch>` and path/tree inspection. Use
   `git ls-remote --heads <remote> <branch>` only when credentials are
   available in this process.
7. Verify assistant-executed success with:

```powershell
git ls-remote --heads origin <branch>
```

If `ls-remote` fails after a credible manual push but fetch updates the
remote-tracking branch to the expected SHA, do not report the push as failed;
report the verification split and name which proof was available.

8. If elevated push fails or approval is unavailable, stop with a resumption
   packet telling the operator to `cd` to the repository and run the exact
   refspec manually. Include the exact full-SHA refspec rather than a broad
   branch push whenever a single target commit was already selected.

Do not repeat login loops, change credential helpers globally, erase tokens,
force-push, or broaden the target branch to work around a credential-context
split.

## Handle Git index locks

Resolve the exact Git directory before handling a lock:

```powershell
$gitDir = (git rev-parse --path-format=absolute --git-dir).Trim()
$indexLock = [IO.Path]::GetFullPath((Join-Path $gitDir 'index.lock'))
```

If the exact lock exists, fail closed unless all of these checks pass:

1. Enumerate `git.exe` and `git-lfs.exe` through `Get-CimInstance
   Win32_Process`; stop if enumeration fails or either process is present.
2. Capture the lock's length and UTC modification time, wait two seconds, and
   stop if either value changes or the lock disappears unexpectedly.
3. Open the exact lock with `[IO.File]::Open` using `FileMode::Open`,
   `FileAccess::ReadWrite`, and `FileShare::None`; stop if exclusive access
   cannot be obtained, then close the handle before removal.
4. Reconfirm the resolved lock is exactly `<resolved-git-dir>/index.lock`, then
   remove only that literal file with `Remove-Item -LiteralPath`.

Report the exact stale lock removed and resume only the original bounded Git
operation. Preserve the lock and stop whenever ownership, stability, exclusive
access, or exact path remains uncertain. Never remove another `.lock` file or
recursively alter the Git directory.

## Preserve authority exactly

Soft assent such as `you choose`, `sounds good`, `very well`, or `I defer to
you` does not authorize staging, commit, push, PR creation, rebasing, hosted
settings, or external communication.

A menu letter authorizes stage, commit, or push only when it came from a
validated action-ready surface whose visible label begins with `Stage:`,
`Commit:`, or `Push:` and whose effect matches that verb. `Stage:` is valid
only for exact scoped paths or hunks that already passed the required
publication validation; it does not authorize `git add -A`, commit, push, PR,
publication, deployment, or broader repository admission. Otherwise, carry the
selected branch through read-only planning until the exact authorization
boundary appears.

When offering a Git action in an A-D surface, make the action boundary legible
in the first word: `Stage:` for exact scoped staging, `Commit:` for a local
commit, `Push:` for a remote update, or `Execute:` for read-only inspection or
reversible preparation. Do not offer
ambiguous labels such as "Recommended path -- stage and commit" and then treat a
bare letter as Git authority.

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
Pre-action snapshot digest:
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
The packet pauses or blocks the existing publication transition. It must not
silently open a second repair or architecture transition.

After a push, verify the exact advertised remote SHA and take a fresh Mira Work
snapshot. The publication receipt must state the pre-action and post-action
snapshot digests, exact local commit, exact remote commit, excluded dirty paths,
remaining divergence, and reached boundary. Keep intended state, working-tree
state, committed state, remote state, and hosted state distinct. If any required
boundary cannot be proved, report it as unavailable or blocked rather than
claiming synchronization.

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

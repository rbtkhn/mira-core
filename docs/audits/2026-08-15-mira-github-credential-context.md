# Mira GitHub Credential-Context Outcome

Date: 2026-08-15

## Observation

After `0a5de8c Add Mira GitHub publication traffic control` was committed, the
operator requested a push. The safe lane was branch publication because local
`main` was ahead of and behind `origin/main` while the worktree remained dirty.
The exact refspec push initially failed because the Codex process saw invalid
GitHub CLI authentication even after the operator completed `gh auth login` in
an interactive PowerShell.

Relevant observed state:

- target commit: `0a5de8c11c5b5fdd2495ca76dd8a365c6e24b5c3`
- intended branch: `codex/mira-github-skill-20260815`
- Codex `gh auth status`: invalid token
- operator PowerShell `gh auth status`: logged in as `rbtkhn`
- normal exact-refspec push from Codex: silent failure
- traced push: GitHub returned HTTP 401 before invoking the `gh` credential
  helper

## Diagnosis

The failure was not caused by branch divergence, target SHA selection, Git LFS,
or dirty-tree inclusion. It was a credential-context split: the operator's
interactive shell and the Codex process did not observe the same refreshed
GitHub credential state.

## Intervention

`deecaf0 Refine Mira GitHub credential handling` updated
`docs/skill-drafts/mira-github/SKILL.md` with a credential-context split rule:
check the local credential context, try one normal exact-refspec push, use one
elevated exact-refspec push when keyring access is the likely blocker, then
verify with `git ls-remote`.

## Validation

The next push of `deecaf0` exercised the new rule:

- remote branch before update:
  `0a5de8c11c5b5fdd2495ca76dd8a365c6e24b5c3`
- target commit: `deecaf0c52b0bfaee2b655d8f9387a46f9e2d4d1`
- fast-forward check: `0a5de8c` was an ancestor of `deecaf0`
- Codex `gh auth status`: still invalid
- `gh auth token --hostname github.com`: no OAuth token found
- Git LFS: available as `git-lfs/3.7.0`
- normal exact-refspec push: silent failure
- elevated exact-refspec push:
  `0a5de8c..deecaf0  deecaf0 -> codex/mira-github-skill-20260815`
- verification:
  `git ls-remote --heads origin codex/mira-github-skill-20260815` returned
  `deecaf0c52b0bfaee2b655d8f9387a46f9e2d4d1`

## Outcome

The refined `mira-github` procedure successfully converted a repeated failed
push into a verified branch update without pushing `main`, force-pushing,
rebasing, staging dirty-tree paths, changing global credential helpers, erasing
tokens, or asking the operator to repeat an already-correct authentication
repair.

Current limitation: this is one observed post-intervention use, not a
longitudinal measurement. Future comparable GitHub publication episodes should
measure whether credential-context split handling reduces repeated auth repair,
failed push retries, and operator restatement.

Authority effect: none. This audit note grants no authority to admit a
recursive-learning entry, stage, commit, push, publish, or change hosted state.

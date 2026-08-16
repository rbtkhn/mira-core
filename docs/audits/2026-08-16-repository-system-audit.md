# Repository System Audit — `mira-core`

**Audit date:** 2026-08-16  
**Repository root:** `C:\dev\narrative-systems`  
**Observed revision:** `46ba6599b478eb8f18fe608200bd0eaf9e4d0ee4`  
**Hosted repository:** `rbtkhn/mira-core`  
**Audit mode:** read-only inward repository audit

## Scope

This audit examined local change-time state, the landed corpus, architecture,
validation, tests, documentation, governance, reproducibility, repository
hygiene, and the hosted state available through GitHub. Archive transcript
bodies, private stores, ignored captures, unrelated domain-content truth, and
repair execution were excluded.

The 27 working-tree paths present during the audit were treated as acknowledged
work in progress rather than defects. No repository mutation, repair, staging,
commit, push, or hosted-setting change was performed during the audit itself.

## Overall Assessment

The repository has unusually strong local governance and validation
architecture, but its assurance chain is presently broken in three places:
hosted CI does not start, two landed integrity contracts fail locally, and
repository identity remains divided between `mira-core` and
`narrative-systems`.

## Findings

### RA-001 — Hosted validation is non-operational

**Severity:** High  
**Status:** Confirmed  
**Evidence class:** Hosted state

The latest eight observed push runs failed. GitHub Actions run `31961472423`
for revision `46ba6599` terminated immediately with zero jobs, and GitHub
identified a likely workflow-file issue.

The probable trigger is `${{ runner.temp }}` at job-level `env` in
`.github/workflows/validate.yml`, where that context may not yet be available.
A repository-setting failure remains a credible alternative because
authenticated administrative inspection was unavailable: Git transport worked,
but the configured GitHub CLI GraphQL token returned HTTP 401.

**Consequence:** No push or pull request currently receives effective hosted
validation.

**Recommended repair:** Correct and syntax-check the workflow, trigger all four
OS/Python jobs, and require a green run before relying on CI again.

### RA-002 — System Archive manifest is not checkout-stable

**Severity:** Medium  
**Status:** Confirmed  
**Evidence class:** Landed corpus and change-time validation

Uncached Full validation reported:

> repository artifact bytes differ from manifest:
> `docs/audits/2026-08-14-mira-journal-session-coverage.md`

The tracked file was clean, yet its checkout SHA-256 was
`4cbd066836d5d238e38bcfe74585792fa3546574a2751e177a2e7e1ca8f95acd`,
while `system-archive/registries/system-improvement.json` expected
`bc9409fafbbe9f384ee4549923b691520052b9354b99c89bba6328cdfb34d0d9`.
Its `.gitattributes` rule controls whitespace diagnostics but does not establish
a line-ending policy.

**Consequence:** A clean Windows checkout cannot satisfy the repository's
terminal structural gate.

**Recommended repair:** Define an explicit canonical byte policy, materialize
the file accordingly, and update the manifest only through its governed
admission route.

### RA-003 — Notes migration broke a sealed simulation digest

**Severity:** Medium  
**Status:** Confirmed  
**Evidence class:** Landed corpus and tests

The move from `mira/reflections` to `mira/notes` changed the digest verifier to
normalize CRLF pairs, but the sealed day-2 digest records the original
mixed-ending bytes. Relevant `.gitattributes` protections still point to the
obsolete reflections path.

This produces three test failures:

- `test_current_simulation_packet_validates`
- `test_seal_check_does_not_mutate_state`
- `test_seal_rejects_early_phase`

The first failure is primary; the other two are cascades because their setup
calls the same repository-wide simulation validator.

**Consequence:** The sealed experiment cannot validate, and its failure
contaminates otherwise independent behavioral tests.

**Recommended repair:** Decide whether sealed digests represent literal or
canonicalized bytes, preserve the durable identity accordingly, and migrate
the attributes to the operative notes path.

### RA-004 — Repository identity is split

**Severity:** Medium  
**Status:** Confirmed  
**Evidence class:** Landed corpus and hosted state

GitHub and `origin` now use `rbtkhn/mira-core`, while current mutable surfaces
still declare:

- README title: `narrative-systems`
- Python distribution: `narrative-systems`
- runtime variables and cache paths: `NARRATIVE_*`
- operative skill restrictions: "Use only in `narrative-systems`"
- local checkout: `C:\dev\narrative-systems`

Historical identifiers are correctly preserved, but current mutable metadata
has not undergone the planned compatibility migration.

**Consequence:** Public identity, installation metadata, documentation, and
runtime configuration disagree.

**Recommended repair:** Complete the staged `MIRA_CORE_*` compatibility
migration after restoring a green baseline.

### RA-005 — Dependency resolution is not fully reproducible

**Severity:** Low  
**Status:** Confirmed  
**Evidence class:** Landed corpus

Runtime dependencies have bounded ranges, but there is no resolved lockfile;
`pytest>=8` and `setuptools>=68` remain open-ended.

**Consequence:** The same repository revision can acquire different validation
environments over time.

**Recommended repair:** Record resolved validation dependencies or produce a
reproducible constraints artifact while retaining the intended compatibility
matrix.

## Validation Receipt

The intended absolute temporary root,
`C:\private\repo-audit-test-temp`, passed `session-preflight` as writable and
outside the repository.

The uncached Full gate was then run with an external validation cache and the
preflighted temporary root. Results:

- bootstrap: passed
- structural phase: failed with one System Archive manifest-byte mismatch
- pytest: 1,145 passed, 1 skipped, 1 deselected, 3 failed
- total elapsed time: 221.322 seconds
- terminal status: failed

All three pytest failures shared the RA-003 day-2 digest mismatch.

## Strengths

- `main`, `origin/main`, and hosted `main` resolved to the same commit.
- `origin` directly used `https://github.com/rbtkhn/mira-core.git`.
- Full validation ran outside the repository through a verified temporary root.
- The gate passed 1,145 tests; only three failures shared one underlying cause.
- Private environment variables and inherited pytest configuration are stripped
  from subprocesses.
- Validation caching is content-addressed and fail-closed.
- Archive, journal, continuity, choice, skill, and publication authorities are
  carefully separated.
- The dirty worktree was legible and unstaged; no accidental cross-repository
  mutation was found.

## Recommended Priority

1. Restore hosted CI execution.
2. Repair the two landed byte-integrity failures.
3. Obtain a clean Full result locally and on GitHub.
4. Resume the `mira-core` compatibility migration.
5. Add dependency-resolution reproducibility.

## Audit Boundary

These findings grant no repair, staging, commit, push, publication, or hosted
administration authority. Archive-health and domain-content truth were not
adjudicated. GitHub branch protection and repository settings could not be
verified because the available administrative authentication was invalid.

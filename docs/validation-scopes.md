# Public package and corpus integrity

The repository has two independently reported validation claims:

- **Public package:** public control contracts, privacy enforcement, and code
  tests that do not require the explicitly listed live corpus records.
- **Corpus integrity:** completeness, source availability, historical bindings,
  generated views, and the tests requiring those records. Missing private or
  unpublished evidence remains a failure here; no private store is hydrated by CI.

Run either through the existing validator:

```powershell
tools/run.ps1 test --scope public-package --temp-root C:/private
tools/run.ps1 test --scope corpus --temp-root C:/private
```

The default `--scope all` preserves existing Full behavior. Scoped results are
never written to or accepted from the Full-result cache. Scope cannot be combined
with focused paths, Fast, immutable-candidate mode, Force, or CacheOnly.

The public scope prints the exact corpus test nodes and modules it excludes,
with reasons maintained in `scripts/validation_scopes.py`. Unlisted tests remain
selected; unexpected failures remain failures.
Structural checks must also be explicitly classified; an unknown check blocks
both scoped runs until its ownership is reviewed. The registered-Library relocation
module depends on a corpus transaction whose code and revision records are not
fully present in the published package, so its collection failure belongs to the
corpus job until that transaction is reconciled. Its exclusion is visible, and
does not establish that the missing migration implementation is valid.

Privacy enforcement stays in the public scope: tracked source bodies, private
captures, and private session payloads still fail validation. Historical bodies
must not be added to Git to satisfy corpus checks. Removing an already-tracked
body from the publication candidate requires preserving the existing local bytes
and reviewing the exact removal; a CI profile never deletes it automatically.

GitHub runs four public-package matrix jobs and a separate corpus-integrity job.
The corpus job has no `continue-on-error` or dependency on public success. Its
failure remains visible, and the workflow's overall result can remain failed
even when every public-package job passes. Report both outcomes and the exact
commit. A public-package pass is not a Full, corpus, or overall hosted pass.

This change does not modify branch protection, required hosted checks, publication
authority, or private-record admission. Required-check policy must be reviewed
separately if an operator later wants to change it.

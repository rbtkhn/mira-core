# Five-Fix Reliability Signals

This checklist tracks concrete proof that the August 2026 reliability pass is
working. It is observational: it does not authorize migration, staging,
publication, private Archive ingestion, or Journal/Dream rewriting.

## Choice DB Migration

- Read-only commands such as `choice due`, `choice review`, and `choice health`
  return `migration-required` for schema v3 stores without changing the file.
- The JSON response includes the affected `store_path` and the exact
  `migration_command`.
- Only `choice migrate-store --json` upgrades the private store to schema v4.
- After the authorized migration, `choice due` and `choice review` resume with
  ordinary due/review output instead of an empty silent skip.

## Cadence Artifact References

- Dated repo refs such as
  `narrative-geopolitics/work/daily/2026-08-18/issue.md` remain visible in
  cadence receipts.
- Email-like refs, absolute local paths, and `..` repository escapes are still
  rejected.
- Coffee check output keeps usable artifact pointers instead of replacing them
  with contact-data redactions.

## Dream Session Coverage

- Dream candidate creation fails before writing the cadence ledger when
  `session_coverage.session_id` is malformed, duplicated, missing, or not found
  in the Journal bundle census.
- Wrong-but-valid-looking IDs are rejected with a specific unknown-session
  diagnostic.
- Valid candidate coverage IDs matching `composition-brief.json` write normally.

## Dream And Journal Refresh

- When Dream blocks because the Journal bundle has later activity records, the
  JSON response includes `refresh_required`, the active run ID, the bundle path,
  and exact `mira-journal prepare`, `draft-check`, and `dream --resume`
  commands.
- The completed Geo stage remains preserved; the workflow asks for refresh and
  resume rather than restarting from scratch.
- After a refreshed Journal bundle validates, `dream --resume` continues without
  repeating completed work.

## Publication Status

- `tools/run.ps1 publication-status --json` reports `unpushed_commit_count`,
  `push_target_clean`, and `dirty_blocks_push`.
- A dirty worktree with commits ahead of upstream is reported as pushable
  history plus uncommitted local work, not as a generic push failure.
- Staged, clean-ahead, dirty-ahead, diverged, and no-upstream states produce
  distinct status fields and recommendations.

## Verification Receipts

- Focused reliability tests pass through the governed repository runner for
  choice, cadence, Dream, publication status, and runtime tooling coverage.
- `git diff --check` passes for the reliability-pass files.
- `tools/run.ps1 publication-status --json` emits the new publication fields.
- `tools/run.ps1 cadence --db C:\private\narrative-cadence.sqlite3 coffee --check --format markdown`
  preserves dated artifact refs and performs no mutation.

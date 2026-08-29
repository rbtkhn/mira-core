# Mira Core local-state boundary

Mira Core separates versioned knowledge from mutable local state. The Git
repository contains code, governed documents, schemas, and metadata approved
for repository admission. SQLite ledgers, private drafts, archive bodies,
provisional receipts, caches, and worktrees remain outside Git.

## Resolution

`MIRA_CORE_STATE_ROOT` is the single root control. Defaults are:

- Windows: `%LOCALAPPDATA%\MiraCore`
- Linux: `$XDG_STATE_HOME/mira-core`, otherwise `~/.local/state/mira-core`
- macOS: `~/Library/Application Support/MiraCore`

An explicit command path overrides a service environment variable, which
overrides the derived path under the state root. All resolved state paths must
be absolute and outside the repository. Read-only status reports mixed-root
overrides; mutation must stop until the conflict is resolved.

Use `tools/run.ps1 mira-state status` for current resolution and
`tools/run.ps1 mira-state verify` for migration integrity. The state root is
not a credential store; secrets belong in the operating-system credential
manager.

## Legacy migration and quarantine

`mira-state migrate --check` inventories `C:\private`, validates the selected
active carriers, verifies capacity, and predicts the migration without writing.
Execution copies and verifies active carriers atomically, consolidates the two
choice ledgers without rewriting events, and records all top-level source
dispositions. It never deletes or rewrites the source.

The quarantine receipt binds source and target digests and records a deletion
review date thirty days after cutover. That date creates no deletion authority.
Cleanup requires a separate review and exact instruction.

## Deferred repository-visibility change

This migration does not make the GitHub repository private. A future visibility
operation must separately verify hosted visibility, collaborators, forks,
Pages, Actions, security features, secrets, and historical exposure; obtain an
exact visibility instruction; change only the named repository; and verify the
hosted result. Making a repository private cannot retract public clones or
detached forks and grants no authority to admit local state to Git.

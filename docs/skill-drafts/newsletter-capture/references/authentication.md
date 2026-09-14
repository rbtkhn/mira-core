# Dedicated Gmail authentication and route review

The reader uses Gmail API `gmail.readonly`. Google grants mailbox-wide read
access; the publication allowlist is an application restriction, not a Google
permission boundary. Use only mira@grace-mar.com. No Gmail connector is assumed.

Create a Google Cloud desktop OAuth client with Gmail API enabled, using the
Workspace account's permitted consent configuration. The operator completes
Google sign-in and the access grant. Obtain an authorized-user credential file
through the standard Google OAuth desktop flow with offline access and only
`https://www.googleapis.com/auth/gmail.readonly`. Do not export browser cookies.

The reader accepts the standard JSON fields `client_id`, `client_secret`,
`refresh_token`, and `scopes` (a one-element array containing that scope).
Keep this file in an operator-protected directory outside every Git checkout;
on Windows restrict its ACL to the operator and system. Pass its absolute path
using `--credentials`. Never print its values or add credentials to tests.
The reader refreshes tokens against Google's fixed token endpoint and verifies
the profile equals the dedicated mailbox before reading messages.

Private capture uses portable_paths.state_path under
`newsletters/<workspace-hash>/`. `--state-root` is available for an explicitly
chosen external private root. Missing state is not an empty inbox. All writes
use a single capture lock; after a crash inspect the lock's process ID and confirm
it is no longer running before removing only that stale lock.

For initial route review, save one genuine complete newsletter as .eml privately
using Gmail's Download original. Inspect From, List-ID, Google authentication
results, title, article link, article HTML class, and full body. The reviewer
must establish sender legitimacy and completeness; a matching display name or
passing parser alone is insufficient. Run approve-route only after this review.
Routes are local operational configuration, not new identity or memory records.

If credentials, consent, or a genuine sample are unavailable, report that exact
blocker. Continue offline validation; keep routine mode disabled. Do not pretend
a successful subscription proves delivery or API access.

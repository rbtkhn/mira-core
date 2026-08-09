# Mira Continuity

This directory implements five governed continuity layers:

1. **Substrate** — deterministic, redacted, compressed immutable session captures.
2. **Activation** — a bounded generated briefing loaded after repository instructions.
3. **Expression** — operator-approved identity propositions and their generated view.
4. **Trace** — selective, operator-reviewed session harvest packets.
5. **Trajectory** — a generated historical light curve of sessions and identity events.

## Canonical and Generated Surfaces

- `session-registry.json` is the canonical capture registry.
- `identity-ledger.json` is the canonical identity authority.
- `captures/` contains byte-identical hydrated views of immutable deterministic
  `.jsonl.gz` snapshots stored by the root [System Archive](../../system-archive/README.md).
- `harvests/` contains selective reviewed packets; an indexed session need not be harvested.
- `../identity.md`, `trajectory.md`, and `activation.md` are generated views.

## Command Surface

Use `tools/run.ps1 mira-continuity` with:

- `discover`
- `ingest --check` or `ingest`
- `validate`
- `render --check` or `render`
- `activate`
- `deepen --session MS-<uuid> --input <reviewed-packet.json> [--check]`
- `identity promote --input <approved-proposition.json> [--check]`
- `recover --contract stage1-v1 --staged --check`
- `recover --contract stage1-v1 --staged --temp-root <external-root> --receipt-root <external-root>`
- `privacy-audit --contract stage1-v1 --check`
- `privacy-audit --contract stage1-v1 --prepare --private-root <external-root>`
- `privacy-audit --contract stage1-v1 --finalize --review-decisions <decisions.json> --receipt-root <external-root>`

Raw Codex JSONL is never copied. Normalization retains user and assistant
messages, tool activity, and bounded lifecycle events while excluding hidden
reasoning, developer and platform instructions, state/settings events,
credentials, direct contact data, and private attachment bodies.

Resumed sessions append captures. Existing capture bytes are never rewritten.
During `ingest --check`, drift belonging solely to the currently executing
`CODEX_THREAD_ID` is reported as deferred rather than failing the settled-corpus
guard; the task cannot capture the output of its own still-running check.
Identity propositions require `approved_by: operator` and a resolvable session
authority reference. Earlier versions are preserved.

Session history is continuity evidence only. It is not archive evidence,
Reality evidence, automatic operator belief, or permission to act.
System Archive storage and retrieval do not change this authority boundary.

## Stage 1 Durability Guards

`recover --staged` verifies the exact Stage 1 Git index rather than the dirty
working tree. It binds the 133-path packet, checks the four mixed integration
hunks, exports the index to a preflighted external root, re-hashes all captures,
runs validation and targeted tests, and writes a content-addressed receipt
outside Git. The command never stages, commits, pushes, renames, cleans, or
deletes its recovery snapshot.

`privacy-audit` scans every normalized capture without emitting matched private
content. Its deterministic 20-capture review packet contains only record
locators, hashes, categories, and severity. Contextual review must occur through
a private, non-recorded surface; copying excerpts into an agent or tool stream
would recursively add the material to later session history. Final receipts
remain outside Git and distinguish local-commit, private-remote, and public-
remote readiness. Audit completion never authorizes any of those actions.

Before either command writes a temporary snapshot, review packet, or receipt,
run `tools/run.ps1 session-preflight` against the intended absolute external
root. `--check` modes perform no writes.

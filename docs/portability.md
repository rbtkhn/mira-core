# Mira Core portability

The existing Git root is the sole transfer unit. `.mira-private/` is an ignored,
unencrypted child payload; it is not another repository and is not complete in a
Git clone. Copy the entire existing root to the USB device.

Private-root policy:

- `%LOCALAPPDATA%\MiraCore` is machine-local runtime state: validation
  environments, temporary roots, runtime scratch, continuity inboxes, and
  migration markers.
- `.mira-private/` is the repo-local portable private carrier: private SQLite
  state, archive copies, library texts, Journal drafts/revisions, sessions, and
  recovery material.
- `C:\private` is legacy import-only material. New workflow state and temporary
  validation roots must not be created there.

Run `python tools/mira_portable.py status`, then `prepare`. `prepare` copies and
verifies external sources without moving or deleting originals. It records every
included or excluded dependency in `.mira-private/portability/dispositions.json`.

After installing the pinned, licensed runtime packs described by each platform's
`runtime.json`, close Codex and run `seal --external-confirm` from an external
shell. At the destination, run `verify`, `rebind`, and `adapter-check`. Verification
works without Git; Git adds object and recovery-bundle checks when available.

The payload has `confidentiality: none`: it is deliberately unencrypted. Provider
credentials, model weights, inference servers, browser state, application logs,
caches, queues, and credential stores are excluded prerequisites. Preserved global
skills, automations, legacy files, and recovery data are inert provenance and gain
no authority. Kimi and DeepSeek use the same `mira-model-adapter-v1` pass criteria.

The completion states are independent: root calibration, dependency closure,
bundle verification, adapter-contract verification, and live Kimi and DeepSeek
operational verification must never be conflated.

Private Rest lifecycle receipts use `.mira-private/sessions/rest/` and the
relocation-stable workspace identity `mira-core`. External inboxes remain
warning compatibility overrides. Portability preparation inventories each Rest
receipt as active private continuity state; read-only Rest checks never create
the inbox.

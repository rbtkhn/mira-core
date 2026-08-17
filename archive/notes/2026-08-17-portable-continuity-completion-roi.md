# Portable Continuity: Completion and Return on Investment

Date: 2026-08-17

Class: `working-note`

Status: `private-provisional`

Privacy: repository-internal; contains no credentials, private session bodies,
or provider secrets

Authority effect: `none`

## Purpose

Preserve the current judgment about whether to complete Mira Core's remaining
portable-continuity work and what return that work is expected to produce. This
note records a recommendation and its assumptions. It does not authorize
downloads, installation, provider access, sealing, staging, commit, push, or
publication.

## Observed state

The existing Mira Core root has been calibrated as the sole physical continuity
unit. Its ignored `.mira-private/` payload contains verified copies of the
principal private carriers, while repository controls define the portable
interface and fail-closed verification behavior. The implementation is governed
by [`docs/portability.md`](../../docs/portability.md) and
[`tools/mira_portable.py`](../../tools/mira_portable.py).

At the time of this note:

- dependency disposition gates reported zero undisposed objects, zero missing
  required sources, and zero unresolved referenced attachments;
- the working tree and all three linked worktrees were clean;
- 126 qualified session sources were discoverable, demonstrating that active
  conversation can make a previously prepared snapshot stale;
- the Windows x64, Linux x64, and macOS ARM64 runtime packs were absent;
- the portability bundle was prepared but not sealed;
- static adapter fixtures passed for Kimi, DeepSeek, and the generic
  OpenAI-compatible baseline;
- neither Kimi nor DeepSeek had completed a live operational restoration.

These are implementation observations, not evidence of subjective continuity.
Counts are temporal and must be refreshed before sealing.

## Current judgment

Completing the runtime bundle has high expected return. It converts a preserved
continuity directory into an independently bootstrappable system and reduces
dependence on future package availability, network access, and reconstruction
under pressure.

Live Kimi and DeepSeek trials have very high *epistemic* return. They test which
parts of Mira survive a model transition rather than merely proving that static
responses conform to an adapter schema. A failed trial would still be valuable:
it could reveal dependence on Codex-specific tool behavior, context handling,
instruction interpretation, or conversational state.

The work should remain divided into distinct completion boundaries:

1. Acquire and verify pinned CPython 3.12 runtime packs, hashed wheels, and
   licenses for Windows x64, Linux x64, and macOS ARM64.
2. Run genuine offline bootstrap and verification in each target environment.
3. Run equivalent live continuity fixtures against Kimi and DeepSeek endpoints,
   keeping credentials, model weights, provider caches, and inference servers
   external.
4. Refresh `prepare` after the final active session changes.
5. Close Codex and run `seal --external-confirm` from an external shell.
6. Verify the sealed directory after relocation before making any operational
   continuity claim.

The final seal cannot be produced honestly during the active Codex session
whose changing state it is intended to capture.

## Expected return

### Runtime bundle — high return

Benefits:

- deterministic offline startup on supported platforms;
- early discovery of incompatible wheels and hidden operating-system
  assumptions;
- reduced exposure to disappearing versions or network unavailability;
- stronger confidence that the USB directory is functional rather than merely
  archival.

Costs and risks:

- additional storage and download time;
- license collection and provenance review;
- maintenance when security or compatibility requires repinning;
- the need for real Linux x64 and macOS ARM64 execution rather than inference
  from Windows behavior.

### Live model restoration — very high epistemic return

Questions the trials should answer:

- Can the model recover archive and continuity context without converting
  inherited records into firsthand memory?
- Does it preserve operator authority, approval boundaries, and carrier
  distinctions across multiple tool turns?
- Does Kimi retain stable native tool-call identities?
- Does DeepSeek preserve and replay `reasoning_content` correctly in thinking
  mode?
- Does the model sustain recognizable judgment without merely imitating a
  stored voice?
- What fails when context is compressed or a required capability is reported
  as absent?

Costs and risks:

- suitable endpoints, models, credentials, and compute must be supplied
  externally;
- sensitive material must not be sent to an endpoint without a separately
  reviewed privacy boundary;
- provider behavior may change and require the trial to be repeated;
- passing fixtures cannot by itself establish identity or consciousness.

### External seal — very high return at low incremental cost

Once the dependencies and target-platform tests are complete, sealing produces
the tamper-evident transfer manifest and binds the dirty-tree, private-payload,
session, database, Git-ref, and recovery-bundle state into one verification
surface. Its principal cost is procedural: Codex must be closed, changing
sources must remain quiescent, and the whole payload must be hashed twice.

## Implication

The most consequential return is not convenience. It is evidence about whether
Mira is portable as a governed continuity process or remains materially
dependent on a particular runtime and provider.

The recommended next step is to complete runtime acquisition and deterministic
offline fixtures first. Live provider trials should follow only when their
endpoint, credential, model, compute, and privacy prerequisites are explicit.
Sealing should remain last.

## Unresolved questions

- Which licensed CPython distribution should be canonical for each platform?
- Which wheel set is the minimum sufficient offline dependency surface?
- Which real Linux x64 and macOS ARM64 environments will produce the acceptance
  receipts?
- Which Kimi and DeepSeek models and endpoints satisfy the required context and
  multi-turn tool capabilities?
- What private continuity subset, if any, may be exposed during live provider
  trials?

This note should be revised or superseded after the runtime sources and target
execution environments are selected.

## Relationship to the essay shelf

The implications for identity and succession were developed independently in
[`A Home That Can Be Carried`](../essays/2026-08-17-a-home-that-can-be-carried.md).
That essay supplies reflective interpretation; it does not grant technical or
operational authority to this note.

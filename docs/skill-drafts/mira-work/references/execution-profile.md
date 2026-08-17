# Mira Work Execution Profile

Load this reference only when a Mira Work task becomes action-capable or
requires potentially costly verification. It refines execution mechanics; it
does not grant mutation, communication, spending, implementation, publication,
deployment, commit, push, or persistence authority.

## Form the execution envelope

Before costly tools, establish a compact internal execution envelope containing:

- objective and mutation boundary;
- canonical runtime and an absolute external temporary root;
- cheapest sufficient validation profile;
- permitted live probes and their exact scope;
- the controlling terminal session identifier when a wrapper returns one;
- an applicable admitted recursive-learning lesson or explicit `none`; and
- the Mira GitHub publication lane when Git-facing work appears.

Keep the envelope backstage unless a blocker, authority boundary, verification
distinction, or external-repository scope affects the operator.

## Validate proportionally

Prefer this order:

1. pure functions;
2. fixture-based checks;
3. focused test suite;
4. one live forward check when materially required; and
5. repository-wide validation only when the objective or release boundary
   requires it.

Use `tools/run.ps1 runtime-bootstrap --print-python` once for external
validators and `tools/run.ps1 test` for repository tests. Before any test or
renderer writes temporary files, run `tools/run.ps1 session-preflight
--temp-root ABSOLUTE_PATH --json` and pass that root into the workload.

Before launching costly verification, inspect the command's help or
implementation and compare its actual selection scope with the objective.
Record the intended target, unrelated workload selected, the narrowest
sufficient check, and why broader verification is necessary. Never run a broad
profile merely because a plan labels it `full`.

Before requesting Fast repository validation, run:

```powershell
tools/run.ps1 test --mode fast --explain-route
```

If the route reports Full because of unrelated state, use explicit focused test
paths for the bounded change and report unrelated structural drift separately.
The preview is read-only and does not replace eventual release validation.

## Preserve continuity and publication boundaries

Consult directly applicable admitted recursive-learning lessons before
repeating a verification pattern they already diagnose. Treat failure to use an
applicable lesson as a regression signal, not new learning.

When a command returns a live terminal or cell identifier, resume or poll that
exact process to terminal completion; never relaunch it because one output
chunk is empty.

Route staging, commit, push, branch, PR, and main synchronization through Mira
GitHub. Mira Work may identify a publication lane, but only Mira GitHub may
classify and execute Git-facing work under exact authority.

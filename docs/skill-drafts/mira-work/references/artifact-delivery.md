# Reliable local website and presentation delivery

This reference governs Mira-owned execution adapters. Installed plugin instructions
still govern authoring and hosting. Do not edit plugin caches, install dependencies,
disable certificate verification, change global settings, or infer publication authority.

## Mira's public-facing artifacts

For Mira's public-facing artifacts and local candidates intended for public
audiences, load the [public-interface reference](../../mira-mind/references/public-interface.md).
Mira Mind owns wording and claim strength; the selected website or media
workflow owns presentation, accessibility, rendering, and interaction tests.
Mira Letters governs recipient-specific correspondence. Ordinary private
dashboards do not require the public-interface reference. Publication, hosting,
and communication retain their existing separate authority boundaries.

## Runtime and process evidence

Resolve the bundled dependency root once using `load_workspace_dependencies`.
Use the returned bundle's `dependencies` directory as `--runtime-root`. Preflight
an existing absolute external temporary root with `tools/run.ps1 session-preflight`.
Invoke `tools/run.ps1 artifact-delivery` with explicit `--operation`, `--project`,
`--plugin-root`, `--runtime-root`, `--temp-root`, and a new `--output` inside that root.
Do not put credentials in any argument or authoring script. Child output is not
retained automatically because it may contain credentials.

For `--operation presentation`, the plugin root is the installed **skill directory**
containing `container_tools`. Supply `--script` (inside project), `--slides`, and
one `--font` per explicitly selected family. When preserving a deck, supply
`--reference` and declare its reference fonts before authoring. Resolve theme fonts
to explicit families when preserving them; declaration alone does not prove a font
is installed or visually rendered correctly.

Authoring scripts consume `DELIVERY_OUTPUT`, `DELIVERY_FONT_FAMILIES`,
`DELIVERY_REFERENCE`, `DELIVERY_REFERENCE_SHA256`, `DELIVERY_EXPECTED_SLIDES`, `DELIVERY_PYTHON`, and
`DELIVERY_PLUGIN_ROOT`. The child receives `RUNTIME_NODE_MODULES`, `TMP`, `TEMP`,
`TMPDIR`, and `MIRA_CORE_SESSION_TEMP_ROOT`. Use the installed presentation marker,
finalizer, integrity and layout validators. Give the finalizer the declared
`fontPolicy` with reference path/hash and use the selected temp root for candidates,
rendering and receipts. The adapter's package check complements those validators;
it does not replace rendering or visual inspection. Hyperlink relationship validity
does not establish destination availability or account access.

For `--operation sites-package`, plugin root is the installed Sites package root
containing `scripts/package-site.mjs`. Supply the absolute Git for Windows
`bin/bash.exe` through `--bash`. The adapter invokes that installed Node wrapper,
sets child-only Bash utility paths, and converts temporary/archive drive paths for
Bash. No alternate archive builder is introduced. Archive inspection rejects
unsafe members, duplicates and missing index/hosting metadata without extraction.

The adjacent `.delivery.json` records process exit and independent artifact checks
separately. A nonzero command remains a failure even if its artifact is recoverable.
Do not announce complete success or rerun over the same artifact. Review the matching
hash, reference identity, plugin validation and visual evidence before accepting a
recovered file. Existing output paths are rejected to prevent stale-file success.

Run standalone PowerShell commands with explicit propagation:

```powershell
& <executable> <arguments>
$deliveryExit = $LASTEXITCODE
exit $deliveryExit
```

For multiple necessary commands, check each exit immediately and stop on failure.
Do not let a later successful command conceal a failed Git, authoring or packaging
step. Never paste credentials or raw unreviewed child output into a report.

## Source and publication evidence

Use the existing `validated-push check` / `push` helper for eligible exact-SHA
new-branch and fast-forward publication after separate authorization. A receipt
binds the intended commit and checked checkout; changed HEAD or remote state needs
a fresh check. Old receipts lacking the checked HEAD fail closed. A remote-query
failure after push means remote state is unknown, not unchanged.

An unborn repository has no HEAD. `mira-work snapshot` returns a bounded
`unborn-initial-state` observation with a null snapshot digest. Retain that initial
record as advisory state; do not manufacture a landed-state digest. Obtain a real
snapshot after a separately authorized initial commit. Staging, committing,
pushing and deploying remain four distinct authority boundaries.

## Interactive 3D browser evidence

Use a local fixture to rehearse these checks, then repeat relevant checks on the
actual candidate before claiming candidate behavior. Record URL, browser, viewport,
build/hash, observed results and limitations. A fixture pass is not a product pass.

1. Idle: observe a render counter or profiler over a stated interval; static idle
   views should stop rendering when no animation is intended. Verify input resumes.
2. Camera/reset: exercise pointer/touch where available, zoom and named views;
   reset must restore the specified initial camera and selected rug.
3. Exit: open from a scrolled page, close with button and Escape, and check restored
   scroll, page scrolling, keyboard focus and absence of a blocking overlay.
4. Narrow view: compare scrollWidth with clientWidth and inspect controls at the
   smallest supported width and tablet landscape/portrait dimensions.
5. Unavailable WebGL: use a deliberate disabled/failed-context fixture and verify a
   readable fallback, exit and browsing/enquiry continuation. Do not merely hide
   canvas errors. A real device context-loss check is distinct.
6. Preserve the actual rug image and identity; room lighting, scale and placement
   remain illustrative unless measured and verified. Label mocked services.

Report desktop browser/viewport emulation separately from **physical iPad Safari**.
Only an observed physical-device session can support “iPad Safari verified.”

## Vendor reports

Store reports privately and unsent. Include installed version, minimal sanitized
reproduction, expected/observed behavior, exit code and artifact hashes. Mark
suspected causes unconfirmed. If not reproducible, preserve original evidence and
label current results inconclusive. An approval-context report grants no permission
to alter, retry around or bypass approval enforcement.

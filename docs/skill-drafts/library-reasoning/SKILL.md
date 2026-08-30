---
name: library-reasoning
description: "Run the bounded Mira Library historical pressure-test pilot for a manifest-backed Geo-Strategy question. Use for metadata pre-scans, private passage packets, analogy and anti-analogy review, and Geo-Strategy adjudication; do not use it to verify live facts or create statistical base rates."
---

# Library Reasoning Pilot

Use this pilot after geopolitical intake has landed and a crisis object is in
view. It tests whether Mira Library materially changes a Geo-Strategy judgment
without making historical authority a substitute for live evidence.

## Sequence

1. Before settling the mechanism, run a metadata-only scan:

   ```powershell
   tools\run.ps1 library-reasoning pre-scan --crisis-object "..." --mechanism "..." --json
   ```

2. After Geo-Strategy states a provisional mechanism, produce one bounded
   private packet:

   ```powershell
   tools\run.ps1 library-reasoning geo-pilot --date YYYY-MM-DD --crisis-object "..." --mechanism "..." --json
   ```

   Reasoning packets belong under repository-local `.mira-private`. If that
   directory is not writable, stop and report the private-carrier blocker rather
   than creating new packet state under `C:\private`.

3. Geo-Strategy must adjudicate every candidate as `adopted`, `narrowed`,
   `redirected`, `rejected`, or `held`. Adopted material requires a shared
   mechanism, decisive structural difference, rejection condition, concept
   bridge, lineage assessment, and effect on judgment.

4. Mira Voice may express only adjudicated material. During the pilot it must
   not open another retrieval loop.

Successful non-check adjudication appends sanitized private routing
observations. These records describe retrieval usefulness and failure, never
the truth of a geopolitical conclusion. Use `--check` when no observation
should be written.

## Recursive Routing

Inspect observations and prepare an inactive proposal:

```powershell
tools\run.ps1 library-reasoning learning-status --json
tools\run.ps1 library-reasoning calibration-status --json
tools\run.ps1 library-reasoning propose-routing-update --check --json
tools\run.ps1 library-reasoning propose-routing-update --json
```

A proposal requires three consistent adjudications across two crisis
signatures. Activation and rollback remain explicit operator boundaries:

```powershell
tools\run.ps1 library-reasoning activate-routing-memory --input FILE --check
tools\run.ps1 library-reasoning activate-routing-memory --input FILE
tools\run.ps1 library-reasoning rollback-routing-memory --check
tools\run.ps1 library-reasoning rollback-routing-memory
```

`MIRA_CORE_LIBRARY_REASONING_TEXT_ROOTS` supplies ordered read-only private
roots for reasoning. It does not alter the canonical Library admission,
verification, or census root. Routing memory may learn only capped,
profile-scoped retrieval adjustments; it may not learn present-event truth,
base rates, preferred prose, or historical prestige.

## Boundaries

- Registry and private source bodies are read-only.
- The full packet and passages remain under `.mira-private/`.
- `LIB-*` references cannot satisfy `SRC-*` coverage, verify an `OPC-*`, resolve
  a forecast, or support numerical base-rate claims.
- Shared textual or intellectual ancestry is not independent convergence.
- Absence of a credible rival or non-elite witness must remain a named gap.
- Tracked quotations require an outward-use posture; private availability is
  insufficient.
- Staging, commit, push, Archive ingestion, and publication are separate.
- Routing activation and recursive-learning ledger admission are separate
  exact-authority boundaries.

## Pilot Review

Compare the same case without Library, with the adjudicated pressure test, and
after Mira Voice composition. Record whether the Library changed the mechanism,
introduced a rival, exposed anachronism, prevented an overclaim, improved a
falsifier, or changed nothing material. Advance beyond the pilot only after
four reviewed cases, at least three material improvements, no unresolved
evidence laundering, and proportionate cadence cost.

Validate and record a private review with `ablation-review --review FILE`; use
`advancement-status --json` to calculate the gate. The gate is advisory and
does not authorize expansion.

Implementation tests establish validation, not a recursive-learning outcome.
Measured learning requires later independent use against a declared baseline.
Qualified ablation reviews label `comparison_phase` as `baseline` or `shadow`,
assign `calibration_group` as `calibration`, `representative`, or `holdout`,
and record the routing metrics required by `calibration-status`. The baseline
requires four cases in each group; shadow advancement requires four holdouts,
30% lower irrelevant retrieval, 20% lower median review time, non-declining
judgment and rival quality, no evidence laundering, and complete operational
skip precision.

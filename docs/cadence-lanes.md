# Cadence lane contracts

Cadence is a repository-wide control surface with explicit lane contracts.
The kernel owns handoffs, verification aggregation, inheritance, receipts, and
rendering. A lane owns its authority surfaces and failure interpretation.

## Narrative Geopolitics

The default lane. Its bounded structured checks cover repository integrity,
manifest/archive validity, daily contracts, forecast/reality state, rendering,
and smart-intake routing. Remaining tests are retained as generic command
results.

## Predictive History

Predictive History is a read-only sibling lane. The contract may invoke declared
validation commands in `C:\dev\predictive-history` and report results, but it
must not write, regenerate, install dependencies, or alter that repository.

Its first structured check is study-edition output presence. Catalog, route,
source-floor, public-surface, pin-cite, and compatibility checks remain bounded
contract slots until their commands are wired through the same result envelope.

## Result envelope

Structured checks emit `VerificationResult` records with a stable check ID,
status, failure class, scope, affected paths, references, evidence, owner, next
action, rerunnable command, output tail, and opaque lane details.

Non-passing structured results must identify an owner and next action. Missing
dependencies are `unavailable` environment results, not substantive failures.

`public-use` is never authorized by cadence.

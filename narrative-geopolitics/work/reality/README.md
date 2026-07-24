# Reality Verification Lattice

Status: `active-v1`

The lattice is Narrative Geopolitics' canonical adjudication state for claims
that have been explicitly migrated into it. The archive remains source truth:
it establishes what entered the corpus, not what happened in the world.

Structured JSON records are canonical. Markdown under `views/` and the
verification source registry are generated reading surfaces.

## Records

| Directory | Record identity | Purpose |
| --- | --- | --- |
| `sources/` | `VSRC-*` | Bounded source capabilities and language environments. |
| `claims/` | `OPC-*`, `NG-*`, `CLM-*` | Atomic factual, forecast, causal, interpretive, actor-position, or normative claims. |
| `observables/` | `OBS-*` | Predeclared resolution rules and review windows. |
| `evidence/` | `EVD-*` | Retrieved observations with source, language, limitation, digest, and global lineage. |
| `investigations/` | `VER-*` | Bounded research scopes grouping claims and observables. |
| `assessments/` | `ADJ-*` | Human-signed, claim-specific outcomes. |
| `relations/` | `REL-*` | Typed graph edges. |
| `transitions/` | `EPT-*` | Append-only epistemic state changes. |
| `domain-profiles/` | `DOMAIN-*` | Evidence, language, independence, and waiver rules by domain. |

## Multilingual Gate

Canonical positive empirical support requires agreement on the same bounded
observable across independent original-language environments and lineage
roots: two for ordinary claims and three for high-consequence claims. At least
one environment must be regional or claimant-situated and one must be external
or challenged. Translation and syndication never create independence.

Language-neutral physical evidence strengthens an assessment but does not
silently replace the language gate. A physical-evidence waiver requires a
documented multilingual search failure and explicit approval from the human
`operator`.

## Authority

Automation validates records, renders views, and reports impact. It never signs
an assessment. The human reviewer identity `operator` is the sole required
signer for a canonical assessment, including high-consequence public adoption
or accountable forecast scoring. A provisional assessment may guide internal
work but cannot cross those gates. At the cadence handoff, a completed
verification packet may support scoring of a forecast's declared observable
without making the underlying forecast claim canonically factual. Canonical
multilingual adjudication remains required for factual adoption, publication,
or operational and causal claims.

## Commands

```powershell
.\tools\run.ps1 reality check --all
.\tools\run.ps1 reality render --check
.\tools\run.ps1 reality audit OPC-YYYYMMDD-NN --json
.\tools\run.ps1 reality impact OPC-YYYYMMDD-NN --json
.\tools\run.ps1 reality profile VOICE --json
.\tools\run.ps1 reality migrate --date YYYY-MM-DD --check
```

Existing verification and forecast interfaces remain available. If a claim is
present in this lattice, structured state controls; otherwise the legacy
Markdown contract remains canonical.

Migration checking keeps migrated evidence, outcomes, observables, rationales,
language audits, and authorization fields immutable. It accepts only
append-only human signoffs, the assessment status deterministically implied by
those signoffs and existing gates, and separate `revision_of` records. A
signature is therefore preserved without making substantive migration drift
invisible.

The repo-owned `reality-check` skill uses `audit` as its default read-only
surface. Investigation, assessment, waiver, signature, publication, and
forecast-scoring actions remain separate explicit authorities.

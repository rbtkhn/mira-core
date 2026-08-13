# The Repository Remembers; the Agent Receives a Mandate

Status: `canonical-operating-contract`

## Principle

Narrative Systems uses **contractual continuity under bounded agency**. The
repository holds durable memory, authority, provenance, and review state. An
agent receives a temporary mandate to perform one phase of work without
silently redefining the system.

The governing rule is:

> Move continuity, rules, and epistemic boundaries out of model memory and
> into an inspectable, executable operating contract.

## Architectural Roles

| Surface | Architectural role |
| --- | --- |
| `archive/` | Preserved source truth and provenance. |
| `archive/source-manifest.json` | Authoritative source membership and person/channel routing. |
| `voices/` | Derived whole-person continuity. Never a second transcript archive. |
| `channels/` | Derived host and format conditioning. Never independent confirmation. |
| `work/daily/` | Date-bounded synthesis state derived from manifest-backed sources. |
| `work/forecasts/` | Durable forecast authorship, timing, and accountability state. |
| `work/verification/` | Bounded operational assessments; not canonical archive evidence. |
| `work/reality/` | Structured adjudication state for explicitly migrated claims; never archive evidence. |
| `public/` | Intentionally promoted, source-bounded reader products. |
| `scripts/` | Named capabilities with explicit mutation scope. |
| skills and startup prompts | Session-scale authority envelopes and stop conditions. |
| validators and tests | Executable invariants across phases. |
| `docs/model-substitution-readiness.md` | Repository-wide internal gate for changing a model behind an existing workflow; never an authority expansion. |
| coffee/dream handoff | Advisory, verified continuity; never research evidence. |
| operator | Authorization boundary for widening scope or changing phases. |

## Mandatory Session Contract

Every operational session must make seven things legible before mutation:

1. **Objective** — the bounded outcome of this phase.
2. **Authoritative inputs** — which repository surfaces may be trusted.
3. **Permitted reads and writes** — the capability envelope.
4. **Protected surfaces** — what requires explicit additional authorization.
5. **Invariants** — what must remain true when the phase ends.
6. **Stop condition** — when adequate work becomes unauthorized expansion.
7. **Handoff** — the validated state inherited by the next phase.

Agents may make conservative, reversible assumptions inside the envelope.
They must stop when an ambiguity would change identity, provenance, public
factual adoption, forecast resolution, publication, or Git/external state.

Changing the model that performs a phase does not change the phase mandate.
Before a hosted, open-weight, local, or materially different model version
replaces an existing workflow model, apply the repository-wide
[Model Substitution Readiness](../../docs/model-substitution-readiness.md)
gate. The candidate inherits the narrower existing authority envelope. A
readiness status cannot grant new tools, writes, data access, publication,
external actions, or human approval authority.

## Phase Ownership

| Phase | May mutate | Must preserve | Ends when |
| --- | --- | --- | --- |
| `best-intake` | New archive source and its manifest row. | Source body, private workflow, downstream judgment surfaces. | The supplied source is truthfully archived and manifest-backed. |
| identity canonicalization | Declared alias-valued person metadata. | Paths, filenames, hosts, bodies, unrelated rows. | Selected metadata is canonical and idempotent. |
| continuity reconciliation | Existing voice shelves derived from the manifest. | Archive evidence and manually assigned roles. | Existing shelves match manifest membership. |
| geopolitical synthesis | Selected-date person-alias metadata, existing voice routes, the five-file canonical daily contract, its generated `issue.md`, and new forecast hooks. | Private intake, source bodies beyond declared aliases, channel shelves, verification packets, forecast resolutions, public products, and unresolved uncertainty. | A manifest-backed day has a bounded internal judgment, synchronized open hooks, and an optional current reader-facing issue. |
| `reality-check` | Nothing during the default audit; explicitly named lattice records only after the operator requests investigation or assessment. | Archive evidence, source admission, human identity, publication, forecast scoring, and downstream prose. | The claim has a validated decision brief and one bounded next action. |
| operational verification | Explicit `VER-*` packets. | Archive evidence and human assessment authority. | The selected claim is assessed or honestly unresolved. |
| forecast review | Ledger resolution metadata with packet support when required. | Authorship timing and excluded retrospective entries. | A due accountable hook is reviewed without forced certainty. |
| publication | Intentionally selected public documents. | Source bounds, verification gates, as-of date, revision history. | Reader-facing claims satisfy the public contract. |
| coffee/dream | Ignored advisory cadence handoff only. | Research, forecasts, publication, Git state. | One verified lesson and inheritance sentence are recorded. |

## Best-Intake Authority Envelope

`best-intake` may read repository state, the manifest, existing archive paths
for duplicate detection, routing records, and intake method documents. It may
write only:

- `archive/sources/YYYY-MM-DD/source-*.md` for an operator-supplied source;
- the corresponding row in `archive/source-manifest.json`.

Without explicit authorization it does not write voice shelves, channel
shelves, daily synthesis, forecasts, verification packets, public documents,
or Git state. It does not fetch a missing source merely because a reference
exists.

The dynamic preflight is:

```powershell
.\tools\run.ps1 cadence startup best-intake --json
```

The command is read-only. It reports current Git state, archive/manifest
parity, recent intake dates, the latest daily run, cadence staleness, permitted
mutation surfaces, warnings, blockers, and the next action. A startup prompt
must use this live context instead of embedding a commit hash or source count
as durable truth.

## Geopolitical-Synthesis Authority Envelope

`geo-strategy` is explicitly date-scoped. It may read the manifest,
the selected date's manifest-backed archive sources, person and channel
conditioning, and existing daily, forecast, verification, method, and template
state. Within the guided workflow it may write only:

- declared alias-valued person metadata for the selected date;
- routes in already-existing `voices/*/source-index.md` shelves;
- the selected date's `sources.md`, `synthesis.md`, `forecast.md`,
  `judgment.md`, and `daily-brief.md`;
- the selected date's generated `issue.md` after the canonical files declare a complete issue lineup;
- new open forecast hooks in the forecast ledger.

A new retrospective packet must declare `Synthesis contract: delta-v1` and a
complete Distinctive Contribution: comparison window, new mechanism, evidence,
or contradiction, and disposition. When review finds no substantive delta,
the authorized outcome is archive-only intake; no formulaic daily packet is
created. Existing historical packets are grandfathered.

Without explicit additional authorization it does not change private intake,
new archive source bodies, channel shelves, verification packets, forecast
resolutions or accountability classifications, public products, external
systems, web evidence, or Git state.

The dynamic preflight is:

```powershell
.\tools\run.ps1 cadence startup geo-strategy --date YYYY-MM-DD --json
```

The command is read-only. A date with no manifest rows, or with missing
manifest-backed archive sources, is blocking. An absent or partial five-file
daily contract routes the operator to guided Choice `A`; reconciliation or
validation debt routes to Choice `B`; a clean complete contract routes to
operational-claim triage at Choice `C`. These recommendations describe the
next authorized phase action; they do not execute it.

The five daily files remain canonical. `judgment.md` is the concise internal
accountability handoff after synthesis and forecast triage. `issue.md` is a deterministic internal
reader-facing rendering governed by [the daily-issue method](daily-issue.md);
creating it is not public promotion.

## Reality-Check Authority Envelope

`reality-check` is scoped to an existing `OPC-*`, `CLM-*`, or `NG-*` lattice
claim. Its default invocation is read-only: validate the repository and
lattice, check generated-view currency, run `reality.py audit CLAIM_ID`, and
report epistemic state, evidence posture, multilingual and lineage coverage,
authorization boundaries, and the next bounded action.

External research or lattice mutation requires an explicit operator request.
Before browsing, the phase must declare atomic observables, target original-
language environments, independence and interested-source restrictions, the
time window, and a stop condition. It may then write only the named
investigation and its claim, observable, evidence, relation, assessment, and
transition records. Unregistered sources remain leads pending separate source
admission.

After a valid assessment, the agent asks whether the operator wants to sign.
It records a signature only after confirmation and a supplied reviewer name;
it never infers human identity or supplies a second signer. No assessment,
signature, or waiver automatically authorizes publication, forecast scoring,
archive mutation, source admission, or downstream prose changes.

The audit entrypoint is:

```powershell
.\tools\run.ps1 reality audit CLAIM-ID --json
```

## Operational-Verification Authority Envelope

Operational verification is scoped to one explicitly created `VER-*` packet.
It may read the source registry, that packet's named artifacts and forecast
hooks, and bounded external evidence responsive to its declared observables.
It may write only the selected packet. It does not inherit authority to alter
archive evidence, synthesis, publication, the forecast ledger, other packets,
the registry, or generalized collection machinery.

The dynamic preflight is:

```powershell
.\tools\run.ps1 cadence startup operational-verification --packet VER-YYYYMMDD-NN --json
```

The command is read-only. A missing or ambiguous packet, an invalid registry,
or an invalid assessed packet is blocking. A requested packet routes first to
observable definition and then bounded research; a researching packet remains
inside that boundary; an assessed packet routes to downstream human review.
Supported, contested, disconfirmed, and unresolvable outcomes all preserve the
same rule: an assessment constrains judgment but never resolves a forecast by
itself.

For a lattice-migrated investigation, the same envelope applies to its
structured `VER-*` record and named graph dependencies. Automation may validate
multilingual and lineage coverage, but only named humans may sign assessments.
High-consequence publication or forecast scoring requires canonical lattice
adjudication under the [reality-lattice method](reality-verification-lattice.md).

## Forecast-Review Authority Envelope

Forecast review is scoped to one `NG-*` hook and an explicit as-of date. It may
read the selected entry, its accountability row, source run, operational
dependencies, and completed packets that cite the hook. It may write only the
selected hook's resolution status and review note. It does not inherit
authority to rewrite the forecast, probability, review date, authorship,
classification, verification evidence, other ledger rows, synthesis, or
publication.

The dynamic preflight is:

```powershell
.\tools\run.ps1 cadence startup forecast-review --hook NG-YYYYMMDD-FNN --as-of YYYY-MM-DD --json
```

The command is read-only. It rejects missing or duplicated ledger state,
preserves non-accountable classifications, waits when a hook is not due, and
routes a due accountable hook without completed verification back to the
operational-verification phase. A completed packet permits review, not an
automatic `hit`, `miss`, `mixed`, or
`unresolvable_with_authorized_evidence` result.

## Invariants and Gates

- Archive files, manifest rows, and the manifest header remain one-to-one.
- Source bodies are not rewritten by downstream interpretation.
- Person identity and host/channel identity remain separate.
- Derived voice and channel surfaces never outrank the manifest.
- Repeated commentary never becomes independent operational confirmation.
- Unresolved claims remain labeled; uncertainty is not repaired by prose.
- Operational factual adoption and accountable forecast resolution obey
  verification packet gates.
- Publication, forecast resolution, intake, and Git operations are separate
  authorities.
- A cadence handoff is inherited only when its Git fingerprint and
  verification remain current.

## Failure Recovery

If a phase fails between writes, stop further phase expansion and restore the
smallest invariant boundary:

1. Preserve the source body and existing operator work.
2. Identify which authoritative surface was written.
3. Run the relevant check mode and repository integrity validator.
4. Complete or reverse only the incomplete phase-local write; never repair by
   broad regeneration.
5. Record unresolved ambiguity instead of inventing provenance.
6. Resume only when the phase input and output contract is again explicit.

For intake, an archive file without its manifest row—or a manifest row without
its archive file—is blocking. Staleness in downstream synthesis is reported as
`stale-after-intake` and remains nonblocking during source landing.

## Handoff Law

Each phase hands off facts about repository state, not confidence in the agent
that produced them. A valid handoff names:

- what changed;
- what was verified;
- what remains provisional or deferred;
- which surface is authoritative;
- which next phase now owns the work.

The system is continuous because contracts and state survive. Agents remain
replaceable, adaptive operators within that continuity.

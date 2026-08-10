---
name: reality-check
description: "Audit Narrative Geopolitics Reality Verification Lattice claims and guide bounded multilingual adjudication. Use for `reality-check`, verification of `OPC-*`, `CLM-*`, or `NG-*` lattice claims, original-language corroboration, evidence-lineage independence, lattice assessments, and downstream impact analysis. Do not use for unrelated general-purpose fact checking."
---

# Reality Check

Operate only inside the Narrative Systems repository. Treat
`scripts/reality.py` and `narrative-geopolitics/work/reality/` as canonical;
do not reproduce their schemas in the skill.

## Authority and trigger contract

This skill has standing authority to use web research, but web search is gated.
Ordinary audits and handoffs never browse. For a direct claim or forecast
request, resolve the exact canonical claim, display the bounded investigation
plan, and present the `Investigate` gate. Selecting `Investigate` automatically
invokes the Codex web connector using that plan; no second web-authorization
prompt is required.

The gate does not authorize evidence admission, assessment, human signoff,
forecast scoring, publication, or downstream prose mutation. Those remain
separate explicit actions.

The investigation plan must contain:

- atomic observables;
- time window;
- target original-language environments;
- source tiers;
- independence and lineage rules;
- interested-source restrictions;
- stop condition;
- standing web authority and selected gate state;
- read-only authorization boundary.

## Default audit

Keep a plain reality check read-only.

1. Inspect Git state without changing it.
2. Run:

   ```powershell
   .\tools\validate.ps1 -TempRoot $env:NARRATIVE_SESSION_TEMP_ROOT
   .\tools\run.ps1 reality check --all
   .\tools\run.ps1 reality render --check
   .\tools\run.ps1 reality audit CLAIM_ID --json
   ```

3. Return five labeled elements:
   - epistemic state;
   - supporting and challenging evidence;
   - original-language and lineage coverage;
   - signoff, publication, and forecast authorization boundaries;
   - next bounded action.

Do not repair records, render views, browse, or mutate files during this audit.
If no claim ID is supplied, search existing claim records and ask the operator
to choose among genuine matches. Never create a claim merely to resolve
ambiguity.

Archive density may help prioritize which `OPC-*` claims deserve attention
first, especially dense days with many dependent claims or thin days carrying a
large operational burden. Density never verifies truth, supplies lineage
independence, or substitutes for lattice evidence.

## Claim-first handoff

Prefer exact claim resolution over date-based lexical discovery:

```powershell
.\tools\run.ps1 reality-handoff --claim NG-YYYYMMDD-FNN --json
.\tools\run.ps1 reality-handoff --hook NG-YYYYMMDD-FNN --json
```

The date form remains a discovery fallback:

```powershell
.\tools\run.ps1 reality-handoff --date YYYY-MM-DD --json
```

An exact handoff must resolve the claim first, map linked daily forecast,
ledger, synthesis, and issue artifacts, and show the investigation plan. If
the claim is absent from the lattice, browsing is blocked.

When the exact claim has research-addressable investigation, observable,
original-language, independent-lineage, regional-environment, or
external-environment gaps, the handoff may also expose an inline
`research-brief-seed-v1`. The seed is provisional planning context. It does not
trigger browsing, replace the investigation plan, satisfy a missing gate, or
carry assessment authority. Expand it only after the operator selects it and
Research Brief confirms the commissioning details. Do not emit seeds for
governance-only gaps or date-based lexical candidates.

## Gated automatic investigation

Selecting `Investigate` invokes the standing-authority web connector:

```powershell
.\tools\run.ps1 reality-handoff --claim NG-YYYYMMDD-FNN --investigate --json
```

The repository emits the bounded trigger; the Codex web connector performs
retrieval. The result must report whether web search was not triggered, gated
and executed, stopped by the declared condition, or blocked by a missing claim
or investigation-plan input.

Before creating or admitting evidence for a possibly repeated event, use the
read-only event-identity preflight when reporting dates may differ by timezone
or when the same actor, action, and target recur in a narrow window:

```powershell
.\tools\run.ps1 reality identity-check --packet EVENT.yaml --format markdown
```

Supply only explicitly inspected candidate records; do not scan the archive to
construct the packet. Treat `hold-same-event` as a duplicate-risk hold,
`clarify-ambiguous` as a request for a stronger time or event anchor, and
`continue-distinct` only as identity separation. The result never adjudicates
truth, merges records, admits evidence, or grants authority.

Before browsing, present the bounded claim, atomic observables, target
original-language environments, independence requirements, interested-source
restrictions, lineage risks, time window, and stop condition. Browse only
inside that declared plan.

When collecting or admitting material from the President of Russia website,
read [references/kremlin-sourcing.md](references/kremlin-sourcing.md)
completely before searching or writing evidence. Keep that module subordinate
to the same investigation and authorization boundaries.

- Treat archive records as evidence of what was said, not what happened.
- Treat unregistered sources as leads until separately admitted.
- Record origin and access languages separately.
- Disclose translation provenance and machine assistance.
- Preserve one globally stable lineage root across translations, quotations,
  editions, and syndication.
- Add only defensible `supports`, `challenges`, or contextual relations.
- Never use issues, synthesis, agent output, or other derived analysis as
  upstream evidence.
- Preserve disagreement as contested; do not resolve it by majority vote.
- Treat Reddit, Wikipedia, unsourced aggregators, and commentary as
  discovery-only; they cannot satisfy an independence gate.
- Label every result inside or outside the declared time window.
- Collapse translations, quotations, syndication, and copied reporting to one
  lineage root.
- Separate bypass attempt, coercive response, attribution, and measurable
  effect into distinct observables.
- Do not let evidence for a related mechanism resolve the exact claim.

Use the existing `new` and `add` commands. Validate every created record before
continuing. Do not mutate the archive, admit a new source, publish, score a
forecast, or rewrite downstream prose.

For an unresolved daily `OPC-*` request, prefer:

```powershell
.\tools\run.ps1 verification attach --date YYYY-MM-DD --claim OPC-YYYYMMDD-NN --slug bounded-claim-label
```

This wires a requested packet into canonical daily files and generated issue
output. It is not investigation, assessment, publication authorization, or
forecast scoring.

## Explicit assessment

Create an assessment only on direct request. Keep every assessment atomic and
claim-specific.

1. Scaffold it with `reality.py assess CLAIM_ID`.
2. Complete its bounded outcome, evidence relations, observable references,
   confidence boundary, rationale, language audit, and authorization flags.
3. Validate the assessment and the full lattice.
4. Leave a high-consequence result provisional unless the three-language,
   three-lineage, regional, external, and two-human requirements pass.
5. Render generated views only after canonical records validate.

Never infer a language waiver. A waiver requires unusually strong primary
observational evidence, a documented search failure, and two distinct humans.

## Human signature boundary

After presenting a valid assessment, ask whether the operator wants to sign
it. Record a signature only after the operator confirms and supplies the
reviewer identity. Never infer a reviewer, fabricate a second signer, treat an
agent as a human authority, or sign merely because validation passed.

An assessment constrains downstream judgment but never authorizes automatic
publication, forecast scoring, source admission, or prose rewriting. End with
the refreshed decision brief and name any remaining gate.

## Morning Brief consumer boundary

Morning Brief may call `reality audit CLAIM_ID --json` and
`reality impact CLAIM_ID --json` read-only after independently sourcing a fresh
observation. Only an exact `same-observable` match may carry the assessment's
epistemic state into that observation; related crises, actors, mechanisms, and
forecast dependencies remain context. Morning Brief may snapshot controlling
claim and assessment paths and hashes, but it may not create, investigate,
assess, sign, transition, render, or otherwise mutate lattice state.

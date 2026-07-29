---
name: reality-check
description: "Audit Narrative Geopolitics Reality Verification Lattice claims and guide bounded multilingual adjudication. Use for `reality-check`, verification of `OPC-*`, `CLM-*`, or `NG-*` lattice claims, original-language corroboration, evidence-lineage independence, lattice assessments, and downstream impact analysis. Do not use for unrelated general-purpose fact checking."
---

# Reality Check

Operate only inside the Narrative Systems repository. Treat
`scripts/reality.py` and `narrative-geopolitics/work/reality/` as canonical;
do not reproduce their schemas in the skill.

## Default audit

Keep a plain reality check read-only.

1. Inspect Git state without changing it.
2. Run:

   ```powershell
   .\tools\validate.ps1
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

## Explicit investigation

Escalate only when the operator explicitly asks to investigate or collect
evidence.

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

# Audit Routing

This note defines how repository-level, archive-domain, and skill-contract
audits compose in Mira Core. It is a routing control, not a replacement
for any auditor's governing skill.

## Authority Model

`repo-audit` is the coordinating system auditor. It establishes repository
scope, visibility ceilings, validation planes, evidence classes, and the
repository-level implications of domain findings.

`archive-audit` is authoritative for landed archive health: manifest parity,
coverage, density, routing, duplicates, structural validity, and repair
candidates. It does not adjudicate source truth, repository architecture, or
skill quality.

`skill-audit` is authoritative for skill-contract quality: trigger clarity,
workflow completeness, authority boundaries, progressive disclosure,
testability, drift risk, benchmarkability, and revision readiness. It does not
replace archive validation or decide source truth.

## Choreography

1. Start with `repo-audit` when the question concerns repository readiness,
   coherence, reproducibility, governance, or cross-system integration.
2. Delegate explicit archive questions to `archive-audit`.
3. Delegate explicit instruction-surface questions to `skill-audit`.
4. Preserve each domain auditor's findings, identifiers, severity, scope, and
   provenance. Do not duplicate or launder domain findings into a new severity.
5. Evaluate repository-level implications separately, including integration,
   documentation, validation-plane, and hosted-state consequences.
6. Route repairs through the owning workflow: `archive-repair` for archive
   defects, skill-document changes plus focused tests for skill defects, and
   repository code, controls, or documentation repair for system defects.
7. Keep truth adjudication outside this trio. Invoke `reality-check` only when
   claim verification or lattice adjudication is explicitly in scope.

## Decision Tree

Ask what object is being evaluated:

- Repository system, controls, validation, dependencies, governance, or
  integration: use `repo-audit`.
- Landed sources, manifests, archive coverage, density, routing, duplicates,
  or structural health: use `archive-audit`.
- Skill trigger, instructions, authority boundary, testability, drift, or
  revision readiness: use `skill-audit`.
- Source or lattice claim truth: use `reality-check`; do not force it through
  the three-audit choreography.

When more than one object is in scope, use `repo-audit` as the outer frame and
invoke the relevant domain auditors with explicit, bounded scopes. The outer
audit records the domain results and assesses only their repository-system
consequences.

## Anti-Patterns

- Do not make `repo-audit` repeat archive-domain rules.
- Do not use `archive-audit` to judge whether a source claim is true.
- Do not use `skill-audit` to infer repository health from prose alone.
- Do not treat a passing domain audit as proof that hosted-state or
  change-time controls operate.
- Do not infer repair, staging, commit, publication, or deployment authority
  from any audit finding.

## Minimal Handoff Record

Every composed audit should record:

- repository root and revision or observed-state identifier;
- mode, scope, exclusions, and visibility ceiling;
- domain auditor and exact bounded scope;
- command or deterministic check executed;
- domain result with original provenance;
- repository-level implication, if any;
- repair owner and separate authority status.

Authority effect: none. This routing note grants no authority to modify,
repair, stage, commit, push, publish, deploy, communicate, or alter hosted
settings.

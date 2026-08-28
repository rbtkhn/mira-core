# Repository Audit Finding Schema

Read this reference for formal reports, consequential findings, domain-auditor
composition, or inward audits. Omit fields only when they cannot affect
interpretation, calibration, provenance, or reproduction.

```yaml
finding_id: RA-<stable-id>
rule_id: <stable-rule-or-null>
title: <specific condition>

classification:
  lens: <audit-lens>
  finding_type: defect | risk | control-gap | inconsistency | debt | observation
  status: confirmed | probable | possible | unavailable
  severity: critical | high | medium | low | informational
  confidence: high | medium | low
  remediation_priority: immediate | next-cycle | planned | monitor | none

lifecycle:
  source_audit_id: <identifier-or-null>
  source_revision_or_window: <revision-window-or-null>
  checked_against_revision: <revision-or-observed-state-id>
  checked_state: commit | staged-index | working-tree | side-worktree |
    hosted-state | cross-state
  disposition: open | resolved | superseded | rejected-by-operator |
    not-reproduced | unavailable
  disposition_evidence: <bounded-reference>
  operator_disposition: accepted | rejected | deferred | none

scope:
  repository: <identifier>
  revision: <revision>
  subsystem: <bounded-component>
  breadth: systemic | multi-component | component | isolated
  mode: external | inward

visibility:
  repository_visibility: public | private | internal | unknown
  declared_content_visibility: public | internal | restricted | unknown
  effective_access: public | limited | unknown
  inspection_level_used: metadata-only | structural | bounded-content | full-content
  current_tree_exposure: confirmed | possible | absent | unknown
  history_exposure: confirmed | possible | absent | unknown
  content_inspection_stopped: true | false
  disclosure_minimization: <what-was-not-inspected-or-reproduced>

validation:
  plane: change-time | landed-corpus | hosted-state | cross-plane
  control_id: <identifier-or-null>
  applicable_population: <objects-that-should-be-checked>
  evaluated_population: <objects-actually-checked>
  coverage: enforced | sampled | manual | declared-only | bypassed |
    unavailable | not-applicable
  bypass_condition: <condition-or-null>
  revision_binding: <revision-or-unavailable>

hosted_state:
  workflow_state: configured | active | operating | failing | stale | unavailable
  observed_run_window:
    first: <timestamp-or-null>
    last: <timestamp-or-null>
    run_count: <integer-or-null>
  branch_protection: confirmed | absent | unavailable
  required_checks: <observed-list-or-unavailable>
  evidence_source: <provider-api-or-url>

condition:
  observed: <neutral-observation>
  expected: <governing-expectation-or-null>
  divergence: <precise-difference>

evidence:
  - evidence_class: <class>
    reference: <path-command-rule-or-url>
    observation: <what-it-establishes>
    limitations: <what-it-does-not-establish>

mechanism:
  trigger: <activation-condition>
  failure_path: <causal-path>
  affected_property: <property>
  current_exposure: active | reachable | conditional | latent | unknown

impact:
  consequence: <practical-effect>
  magnitude: catastrophic | major | moderate | minor | negligible
  recoverability: irreversible | difficult | routine | immediate | not-applicable

calibration:
  severity_warrant: <impact-and-exposure-warrant>
  confidence_warrant: <evidence-warrant>
  credible_rival: <best-alternative-explanation>
  rival_disposition: rejected | weakened | unresolved | not-applicable
  escalation_condition: <evidence-that-raises-severity>
  deescalation_condition: <evidence-that-lowers-or-closes>

verification:
  reproduction: <bounded-procedure>
  expected_signal: <confirming-signal>
  falsifier: <defeating-result>
  verification_state: reproduced | partially-reproduced | not-run | blocked

provenance:
  auditor: repo-audit
  audit_contract_revision: <identifier>
  domain_auditor: <name-or-null>
  domain_rule_id: <original-id-or-null>
  domain_severity: <original-value-or-null>
  domain_disposition: <original-value-or-null>
  derived_from_finding_ids: []

routing:
  recommended_route: <workflow-or-decision>
  proposed_action: <concept-not-authorization>
  validation_after_remediation: <required-check>
  authority_effect: none

repair_assessment:
  requested: true | false
  expected_benefit: <bounded-consequence-or-null>
  effort_band: minutes | hours | days | multi-cycle | unknown
  dependencies: []
  reversibility: immediate | routine | difficult | irreversible | unknown
  readiness: ready | needs-decision | needs-evidence | not-safe
  owner_now: <role-or-null>
  owner_later: <role-or-null>
  authority_required: <exact-boundary-or-none>
```

## Severity

- `critical`: active or reachable catastrophic or irreversible harm, broad
  compromise, systemic authority failure, or invalidation of central outputs.
- `high`: major failure of a core purpose or control, or material harm across
  important components.
- `medium`: bounded or conditional moderate reliability, governance,
  reproducibility, security, or maintainability harm.
- `low`: isolated minor consequence with straightforward recovery.
- `informational`: useful observation without demonstrated harm.

Repeated failures strengthen confidence, not impact. A reachable bypass of a
core change-time gate is normally high. Active public exposure of explicitly
internal client, customer, personal, financial, or rights-dependent territory
is normally high; do not infer particular sensitive contents from filenames.

## Confidence and status

- High confidence requires reproduced deterministic evidence, a direct
  structural contradiction, or independent evidence classes without an
  unresolved rival.
- Medium confidence reflects strong observation with incomplete reproduction or
  a weakened rival.
- Low confidence reflects plausible inference, incomplete access, or an
  unresolved rival.

Use `confirmed` when the condition and material mechanism are directly
established, `probable` when some reach remains inferential, `possible` when
evidence only warrants investigation, and `unavailable` when required evidence
could not be accessed. Unavailable evidence cannot produce a confirmed finding.

Lifecycle disposition is not severity or truth adjudication. In particular,
`rejected-by-operator` records a decision boundary, not proof that the finding
was false, while `resolved` requires evidence that the demonstrated condition
no longer exists in the checked state. Repair effort and expected benefit never
raise or lower finding severity.

## Domain provenance

Preserve the domain auditor's original identifier, severity, disposition,
scope, and evidence reference. Record repository-level consequence separately.
Never silently normalize or weaken a domain finding to fit this schema.

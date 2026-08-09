---
name: grok-research
description: Convert bounded external Grok research into auditable Narrative Geopolitics repository value. Use when the operator wants to design a Grok web-research prompt, assess a returned Grok report, extract atomic claims, create review-only claim ledgers or voice-profile candidate packets, recover source provenance, or route high-value claims into verification packets. Do not treat Grok output as evidence automatically and do not call an unavailable Grok connector.
---

# Grok Research

## Overview

Use this skill as a Grok-to-repository bridge. Grok is an external research engine; this skill generates bounded prompts, receives returned reports or PDFs, preserves provenance, separates claims from synthesis, and keeps promotion behind repository verification gates.

## Operating boundary

- Do not claim to call Grok unless an actual connector is available.
- For prompt requests, generate a compact, token-efficient web-research prompt.
- For returned reports, assess coverage, source quality, direct-link availability, source independence, and unsupported certainty.
- Never treat a Grok classification such as `confirmed` as repository truth.
- Do not rewrite voice profiles, state ledgers, claim maps, forecast ledgers, or revision ledgers during intake unless the operator explicitly requests promotion.
- Use `grok-reported-unverified` for extracted claims until evidence and human adjudication satisfy the relevant gate.

## Modes

Choose the narrowest useful mode: `report`, `voice-profile`, `forecast-sweep`,
`revision-hunt`, `source-chain`, `adversarial-review`, `claim-intake`, or
`verification-routing`.

Read [report-contract.md](references/report-contract.md) when generating a prompt
or deciding which fields a returned report must contain.

## Prompt generation

Every prompt must specify bounded dates and scope; web search and underlying-source
inspection when no materials are attached; direct URLs, event and publication dates;
source independence; compact output length; uncertainty and contradiction handling;
a stop condition; and the intended repository artifact without authorizing mutation.
For voice research, require dated strengths, blind spots, forecasts, revisions,
channel effects, and proposed destinations for README, state-ledger, claim-map, and
accountability surfaces. Do not ask Grok to write repository files directly.

## Report intake

Inspect the complete report or PDF. Record path, date, page count, extractability,
and link count. Check direct URL availability, compare against required sections,
and identify unsupported conclusions, source cascades, missing dates, and claims
without underlying evidence. Preserve the original. Give a verdict: `usable`,
`usable with corrections`, `research backlog only`, or `unreliable`.

## Claim and profile intake

Create review-only ledgers under `narrative-geopolitics/work/grok/claim-ledgers/`
and candidate packets under `narrative-geopolitics/work/voice-profile-candidates/<run>/`.
Preserve stable IDs, claim wording, report/page, dates, URLs or
`source-recovery-pending`, classifications, source-chain notes, contradictions,
confidence, limitations, destinations, and verification links. Separate facts,
forecasts, voice positions, revisions, and near-misses. Candidate profile traits
require repeated dated evidence where available and must not infer private beliefs.

## Verification routing and validation

Only create packets for bounded high-value claims explicitly selected by the operator.
Distinguish official position, professional reporting, commercial or observational
data, original-language evidence, and independent confirmation. Multiple outlets
derived from one report remain one evidence chain.

Before completion, validate JSON syntax and unique IDs, requested coverage, required
sections, unverified statuses, source paths and URLs, unrelated-file exclusions, and
the repository checker when packets were created. End with the next bounded promotion
or verification action, not a broad synthesis.

## Resources (optional)

Create only the resource directories this skill actually needs. Delete this section if no resources are required.

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Codex for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Codex's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Codex should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Codex produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Not every skill requires all three types of resources.**

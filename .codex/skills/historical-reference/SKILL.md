---
name: historical-reference
description: Source-linked historical-reference extraction, attribution, taxonomy, mechanism, review, calibration, and bounded cross-voice comparison for Narrative Geopolitics archives.
---

# Historical Reference

## Overview

Use this skill for bounded, manifest-backed analysis of historical references in Narrative Geopolitics transcripts. It produces source-linked ledgers and review artifacts; it does not adjudicate historical truth or rank analytical quality.

## Operating rules

- Require an explicit voice set or source set. Never run the full corpus implicitly.
- Preserve source IDs, archive paths, dates, titles, quotes, and attribution confidence.
- Keep broad periods as parent metadata and count specific references as analytical units.
- Keep provisional attribution and automatic crosswalks visible and clearly labeled.
- Use risk-weighted review queues; uncertainty warns and queues rather than blocks.
- Never overwrite existing synthesis prose. Synthesis integration must create a bounded, provenance-linked context block.

## Workflow

1. Validate the manifest and selected voices/sources.
2. Fingerprint each source using source ID, archive path, content hash, taxonomy version, detector version, and mechanism version.
3. Skip unchanged inputs in `--changed-only` mode and resume from checkpoints when requested.
4. Segment transcripts using speaker turns when available; otherwise retain paragraph-level provenance and mark uncertainty.
5. Detect native historical references, parent/detail relations, mechanisms, and attribution confidence.
6. Generate automatic native-to-shared crosswalk suggestions with confidence, rationale, and conflict status.
7. Score review risk and generate a deterministic queue.
8. Publish structured ledgers, Markdown views, receipts, calibration reports, and minimal graph exports atomically.

## Interfaces

Run the bundled analyzer from the repository root:

```powershell
python .codex/skills/historical-reference/scripts/analyze.py --voices freeman,diesen --changed-only
```

Supported controls include `--voices`, `--sources`, `--run-id`, `--resume`, `--changed-only`, `--dry-run`, `--output-dir`, and `--calibration`.

Build a bounded synthesis context packet explicitly from one analyzer run:

```powershell
python scripts/build_historical_context_packet.py --input RUN.json --date YYYY-MM-DD --voices freeman --max-items 12 --output context-packet.json
```

The packet writes JSON and Markdown beside the requested output. It never edits
daily synthesis prose; the packet ID is the provenance handle for any deliberate
operator insertion.

Validate native taxonomies and generated crosswalk fields with:

```powershell
python scripts/validate_historical_reference_taxonomy.py --run RUN.json
```

## Review and calibration

Review decisions are keyed by stable source/reference/occurrence identities, never generated row numbers. Calibration fixtures cover positives, negatives, host-only text, attribution classes, parent/detail distinctions, mechanisms, crosswalks, and false analogies. Do not treat metrics as historical accuracy.

## Implementation Notes

[The skill is workflow-based: bounded selection, deterministic analysis, review, and publication. The following legacy template guidance is retained only as historical text and is not operational.]

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Example: DOCX skill with "Workflow Decision Tree" -> "Reading" -> "Creating" -> "Editing"
- Structure: ## Overview -> ## Workflow Decision Tree -> ## Step 1 -> ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when the skill offers different operations/capabilities
- Example: PDF skill with "Quick Start" -> "Merge PDFs" -> "Split PDFs" -> "Extract Text"
- Structure: ## Overview -> ## Quick Start -> ## Task Category 1 -> ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Example: Brand styling with "Brand Guidelines" -> "Colors" -> "Typography" -> "Features"
- Structure: ## Overview -> ## Guidelines -> ## Specifications -> ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when the skill provides multiple interrelated features
- Example: Product Management with "Core Capabilities" -> numbered capability list
- Structure: ## Overview -> ## Core Capabilities -> ### 1. Feature -> ### 2. Feature...

Patterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).

Delete this entire "Structuring This Skill" section when done - it's just guidance.]

## Resources

- `scripts/analyze.py` — bounded incremental analyzer and artifact generator.
- `references/schema.md` — structured record, receipt, crosswalk, review, and graph contracts.
- `references/method.md` — Layered Mechanism Historiography guidance and false-analogy rules.

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

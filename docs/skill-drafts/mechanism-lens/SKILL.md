---
name: mechanism-lens
description: "Archive-backed voice comparison and claim-structure mapping for Narrative Geopolitics sources. Use when the operator asks to summarize a voice narrative over time, compare analysts, map claims by causal mechanism, extract forecast or implication patterns, or prepare verification questions from archive sources without adjudicating truth."
---

# Mechanism Lens

Use after relevant sources already exist in the archive or are supplied in the
turn. Mechanism Lens turns source-backed voice material into reusable analytical
scaffolding: timelines, mechanism maps, claim bullets, verification handles, or
coding templates.

## Boundary

Mechanism Lens does not land sources, repair metadata, create daily synthesis,
or verify claims. It prepares structured claim maps for later
`geopolitical-synthesis`, `historical-reference`, or `reality-check`.

Use another workflow when the task is mainly:

- source landing: `archive-intake`;
- inventory or path lookup: `archive-query`;
- daily judgment synthesis: `geopolitical-synthesis`;
- claim verification: `reality-check`;
- historical-reference extraction: `historical-reference`;
- metadata, ASR, sectioning, or manifest repair: `archive-repair`.

## Workflow

1. Define the bounded scope: date range, topic, voice or voices, and archive
   boundary.
2. Query `narrative-geopolitics/archive/source-manifest.json` for matching
   rows. Report date, title, host, and local path for the source set.
3. Read enough of each selected source to identify the claim structure. Do not
   infer a missing claim from the title alone.
4. Classify each voice's analytical function before assigning domains:
   - operational mechanism;
   - decisive-war or end-state theory;
   - grand-strategy or proxy-war structure;
   - escalation-control or attribution frame;
   - other, if the source demands it.
5. Classify claims by useful domains:
   - air;
   - sea or Odessa;
   - ground;
   - logistics;
   - diplomacy;
   - escalation.
6. Write claim sentences in this form:

   ```text
   The source claims that ___ is happening because ___, which implies ___.
   ```

7. Add verification handles without adjudicating truth:
   - observable indicator;
   - likely source type;
   - verification difficulty: low, medium, or high;
   - propaganda-mirror risk: low, medium, or high.
8. Mark synthesis use:
   - updates existing narrative arc;
   - introduces new mechanism;
   - confirms repeated mechanism;
   - contradicts prior voice claim;
   - raises verification priority;
   - background only.

For strategic or end-state-heavy sources, keep the voice function primary and
use domains as supporting evidence. Do not flatten a grand-strategy or
decisive-war argument into an operational map merely because it mentions ports,
front lines, drones, or missiles.

For escalation-control or attribution-heavy sources, preserve the actor chain
before assigning domains:

```text
actor -> enabling system -> instrument -> target -> intended pressure
```

This is especially important when the source attributes local action to a
larger proxy, funding, intelligence, logistics, or targeting structure.

## Output Forms

Choose the smallest useful form:

- compact voice-role map;
- dated timeline;
- domain mechanism map;
- claim-level bullets;
- source-linked claim map;
- verification-question list;
- filled coding worksheet;
- mechanism chain across two or more sources.

Always state that the result is a map of claims and mechanisms, not evidence
that the claims are true.

## Mechanism Chains

When two or more bounded sources appear to form a sequence, code the chain
explicitly instead of treating each source as an isolated worksheet:

```text
Source A claims enabling condition -> Source B claims operational application
```

Use this only when the later source actually depends on, extends, or applies
the earlier mechanism. Common chain forms:

- air dominance -> logistics or port pressure;
- drone campaign failure -> diplomatic or escalation pressure;
- ground advance -> political or negotiation pressure;
- maritime pressure -> economic or escalation pressure.

For each chain, report:

- source sequence and dates;
- enabling mechanism;
- application mechanism;
- claimed consequence;
- verification priority created by the linkage.

Do not force a chain when sources merely share a topic.

## Checklist Helper

Use `scripts/mechanism_lens_checklist.py` when a fillable Markdown worksheet
would reduce repeated setup:

```powershell
python scripts/mechanism_lens_checklist.py `
  --start-date 2026-07-13 `
  --end-date 2026-08-09 `
  --voices mercouris,ritter,mearsheimer,helmer `
  --topic ukraine-war
```

The script only emits a template. It does not query the archive, classify
claims, or verify facts.

## Success Metrics

A useful run:

- has a bounded source scope;
- separates claim structure from truth adjudication;
- identifies voice function and mechanism domain;
- produces at least one reusable synthesis artifact;
- flags verification handles for high-value claims;
- reduces next-step ambiguity.

Revise or retire the skill if repeated use produces tidy but non-actionable
maps.

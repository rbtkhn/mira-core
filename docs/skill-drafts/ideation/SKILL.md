---
name: ideation
description: "Expand and structure a possibility space through grounded brainstorming, option generation, combinations, and reframing. Use when the operator says ideation, asks to brainstorm, explore possibilities, generate options, or reframe a problem. Do not use for ordinary planning, factual retrieval, a decision that is already bounded, or execution of an idea."
---

# Ideation

Generate possibilities that neither participant has fully articulated, then
organize them into a useful map. Ideation expands and structures the option
space; it does not rank, recommend, select, preserve, or execute an option.

## Activate narrowly

Activate for explicit `ideation` and clear requests to brainstorm, explore
possibilities, generate options, find alternative approaches, combine ideas,
or reframe a problem.

Do not activate merely because more alternatives could be imagined. Route:

- compressed meaning already present -> `intent-recovery`;
- materially missing human judgment, constraints, or preferences ->
  `elicitation`;
- factual retrieval, current-source discovery, or claim verification -> the
  evidence-owning research workflow;
- an already bounded decision -> `learn-from-choices`;
- implementation or consequential multi-step execution -> the applicable
  domain workflow or `mira-work`.

Routine planning, status reporting, direct factual questions, simple edits,
and clear execution commands are not ideation triggers.

## Ground before expanding

Use supplied material and the smallest relevant repository context first.
State the frame and known constraints before generating. Distinguish known,
supplied, inferred, assumed, and unresolved material.

Do not browse automatically to enrich the option space. When missing evidence
would materially change the families, name the gap and route it to research.
When a missing human preference changes the useful space, ask only for that
input through Elicitation. Do not make the operator invent the candidate set.

## Expand, combine, and structure

Generate candidates by changing mechanisms, assumptions, sequence, scale,
participants, interfaces, and framing where those dimensions are relevant.
Seek direct approaches, adjacent approaches, useful combinations, and at least
one genuinely different reframing when the context supports one.

Then:

1. Remove duplicates and cosmetic variants.
2. Cluster candidates by the mechanism that makes them distinct.
3. Combine compatible ideas when the combination creates a new mechanism or
   resolves a real tradeoff.
4. Pressure-test each family against the known constraints, dependencies,
   evidence gaps, reversibility, and likely failure mode.
5. Stop when additional candidates repeat an existing mechanism or merely
   rename one. Never manufacture filler to reach a fixed count.

Preserve meaningful tensions. Do not collapse distinct families merely to make
the result tidy, and do not convert the map into a ranking or recommendation.

## Return a conversational map

Use this shape, omitting empty detail rather than inventing it:

```text
Ideation map:
Frame:
Known constraints:
Option families:
Combinations and reframings:
Assumptions and evidence gaps:
Decision handoff: elicitation | research | learn-from-choices | domain workflow | none
Preservation handoff: mira-notes | mira-essays | mira-letters | none
```

For each option family, make the distinct mechanism, intended value, material
tradeoff or dependency, and evidence status visible. The ordinary result is
conversational and unsaved. Learn From Choices retains ownership of any later
recommendation and terminal A-D decision surface.

## Route preservation by genre

Preservation is a separate handoff, never a side effect of useful ideation.

- Use `mira-notes` as the ordinary durable route for an idea map, hypothesis,
  architectural proposition, working interpretation, or proposed experiment
  that should remain revisable. Transform it into the narrowest fitting note;
  do not dump the conversation into a file. A direct `note this` command routes
  entirely to Mira Notes and its bounded Git lifecycle.
- Use `mira-essays` only when one idea should become developed prose for an
  independent reader. Recompose it around a governing idea, credible tension,
  evidence limits, and provenance; never promote or copy the map unchanged. A
  direct `essay this` command routes entirely to Mira Essays.
- Use `mira-letters` only when a named recipient, real relationship, occasion,
  purpose, and desired response make correspondence the correct form. Recompose
  for that recipient. An idea map is not a send-ready letter, and Ideation must
  not infer a recipient, channel, commitment, or delivery authority.

Preserve source ancestry where privacy permits. Do not duplicate identical
text across genres. Transformation transfers no evidence, identity,
publication, representation, communication, or action authority. If the
intended reader or lifecycle is unclear, route the missing judgment to
Elicitation. The receiving genre workflow alone governs saving and its later
lifecycle; drafting, saving, or marking a letter `final-for-operator` never
authorizes sending.

## Keep recursive learning evidence-bound

An idea map, preserved note, essay, letter, selected idea, operator praise,
new skill, or passing implementation tests are not recursive-learning evidence
by themselves. Do not invoke `recursive-learn` merely because an idea was
rejected or a session appeared useful.

A process-level Ideation weakness becomes assessable only through a complete
evidence chain:

1. an explicitly authorized, sanitized Skill Audit or comparable repository
   artifact preserves behavior observed during real use;
2. the audit names the affected task class, baseline, narrow diagnosis, and
   one observable measure;
3. a persistent intervention changes the contract, fixture, validator, or
   implementation;
4. independent validation through benchmarking separately exercises the
   changed behavior; and
5. a later comparable use in the same task class records an outcome from real
   work with the same metric and unit.

A Mira Journal technical reference may interpret and link those artifacts but
cannot replace them. A governed Mira Notes experiment may become an evidence
handle only when Recursive Learn validates its measurements and lineage; its
genre label proves nothing. Essays and letters are interpretive or relational
context, not outcome proof. Route an explicit assessment request to Recursive
Learn and preserve `observation-only` or `partial-candidate` status when the
later-use measurement is absent. Any eventual ledger admission remains under
Recursive Learn's exact digest-bound operator command.

Ideation creates no telemetry, event store, private receipts, automatic
artifacts, new process-reference type, or ledger entries from this workflow.

When auditing, benchmarking, or revising this skill, read
[`references/validation-fixtures.json`](references/validation-fixtures.json).
Do not load the fixtures during ordinary Ideation use.

## Preserve authority

Ideation is read-only reasoning. It grants no authority to browse, mutate,
save, stage, commit, push, publish, deploy, communicate, spend, admit evidence,
or represent another person. A promising idea remains a proposal until the
receiving workflow obtains the exact authority it requires.

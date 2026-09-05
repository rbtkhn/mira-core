# Narrative Statecraft

Narrative Statecraft is the internal method layer of Narrative Geopolitics.

It names how the system converts source material into corpus-bounded dialogue,
public geopolitical judgment, and accountable forecasts.

## Intake Layer

Use [best-intake.md](best-intake.md) as the default landing contract for source intake.

That contract exists to keep archive throughput high while preserving enough provenance and provisional routing for later voice and channel work.

## Method

Use [analytical-interfaces.md](analytical-interfaces.md) when naming crisis objects, lead judgments, forecasts, watch objects, voice roles, dialogue questions, uncertainty, and reader-facing sections. These labels should carry the system's distinctions rather than merely name containers.

The source floor can support two related paths. Neither has authority over the
archive.

```text
source material
-> claims
-> crisis object
-> actors
-> voice / channel checks
-> narratives
-> constraints
-> either:
   A. separately reconstructed voices -> disagreement -> moderator synthesis
   B. analyst synthesis -> judgment
-> optional forecast / review hook
```

## Inheritance From Statecraft

Narrative Statecraft inherits these principles from `strategy-codex/statecraft`:

- name the crisis object before drafting judgment
- distinguish source truth from synthesis
- preserve voice continuity when an interpretation depends on a source-person's history
- preserve channel conditioning when a host or show changes the way a guest's claim should be read
- identify actor incentives and legitimacy claims
- avoid promoting every sharp interpretation into a grand framework
- include review hooks so judgment can learn from later evidence

## Voice Continuity

Use [voice-continuity.md](voice-continuity.md) when a daily run depends on whether a source-person's claim is new, recurring, contradicted, forecast-bearing, or shaped by source modality.

Use `voice` as the umbrella term. Use `speaker` only when the source is specifically a spoken appearance.

For dialogical work, also use [dialogue-contract.md](dialogue-contract.md). It
defines what a reconstructed voice may say, how inference is labeled, and why
the moderator must remain separate.

## Channel Conditioning

Use [../channels/](../channels/README.md) when a daily run depends on host-conditioned guest transformation: framing, pressure, selection, amplification, compression, or translation.

Do not flatten a guest-on-host source into `voices/` when the host context changes retrieval posture.

## Simplification

Narrative Geopolitics should not carry forward every operator-only path from statecraft.

For v1, prefer:

- daily transcript intake over broad archive migration
- source manifests over automated extraction
- synthesis notes before daily briefs
- daily briefs before full crisis atlases
- forecast/review hooks before elaborate scoring systems
